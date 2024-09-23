import random
from collections.abc import Callable

from datetime import timedelta, datetime
from os import environ, getenv
from random import randrange
from time import sleep

from config.parser import parse_config, prepare_config


try:
    _config = parse_config()
    prepare_config(_config)
except Exception as e:
    print(e)
    exit(1)


if _config.get("cloudConfig") is not None:
    environ["GOOGLE_CLOUD_PROJECT"] = _config["cloudConfig"]["project"]
    environ["GOOGLE_APPLICATION_CREDENTIALS"] = _config["cloudConfig"]["credentials"]

# these imports need to happen AFTER the environment variables have been set

from obs.cloud_logging import submit_log_entry_text, submit_log_entry_json
from obs.cloud_monitoring import submit_gauge_metric, submit_metric_descriptor

if getenv("DEBUG") is not None: print(_config)

_datasource_list_selectors = ["any", "first", "last", "all"]


def expand_list_variable(selector, value):
    if selector == "any":
        return random.choice(value)
    elif selector == "first":
        return value[0]
    elif selector == "last":
        return value[-1]
    elif selector == "all":
        return " ".join(value)
    elif isinstance(selector, int) and 0 < selector < len(value):
        return value[selector]
    else:
        return None


def expand_variables(variables: dict) -> dict:
    variables_expanded = {}
    for var_name, var_config in variables.items():
        if not isinstance(var_config, dict) or var_config.get("dataSource") is None:
            raise ValueError(f"Variable {var_name} is not configure correctly")
        data_source = _config["dataSources"].get(var_config["dataSource"])
        if data_source is None:
            raise ValueError(f"Data source for {var_name} does not exist")
        data_source_value = data_source["value"]
        match data_source["type"]:
            case "env":
                variables_expanded[var_name] = getenv(data_source_value)
            case "list":
                var_list_selector = var_config.get("selector")
                if var_list_selector is None or var_list_selector not in _datasource_list_selectors:
                    raise ValueError(f"Variable {var_name} uses an invalid list selector")
                variables_expanded[var_name] = expand_list_variable(var_list_selector, data_source_value)
            case "random":
                rand_range = var_config.get("range")
                if data_source_value == "int":
                    variables_expanded[var_name] = randrange(
                        rand_range.get("from"),
                        rand_range.get("to"),
                        rand_range.get("step")
                    )
                elif data_source_value == "float":
                    variables_expanded[var_name] = random.uniform(
                        rand_range.get("from"),
                        rand_range.get("to")
                    )
    return variables_expanded


def format_str_payload(vars_dict: dict, text: str):
    return text.format(**vars_dict)


def format_dict_payload(vars_dict: dict, obj: dict):
    new_payload = {}
    for key, value in obj.items():
        if isinstance(value, str):
            new_payload[key] = format_str_payload(vars_dict, value)
        elif isinstance(value, dict):
            new_payload[key] = format_dict_payload(vars_dict, value)
        else:
            new_payload[key] = value
    return new_payload


def run_logging_jobs():
    _run_jobs("loggingJobs", handle_logging_job)


def run_monitoring_jobs():
    _run_jobs("loggingJobs", handle_monitoring_job)


def _run_jobs(jobs_key: str, handler: Callable):
    for job in _config[jobs_key]:
        sleep(0.5)
        submit_time = job["startTime"]
        end_time = job["endTime"]
        frequency = job["frequency"]
        while submit_time < end_time:
            sleep(0.05) # avoid exceeding burn rate of API
            if job.get("variables") is not None:
                vars_dict = expand_variables(job["variables"])
            else:
                vars_dict = None

            handler(submit_time, job, vars_dict)

            if isinstance(frequency, timedelta):
                submit_time += frequency
            elif isinstance(frequency, dict):
                rand_num_secs = random.uniform(frequency["from"].seconds, frequency["to"].seconds)
                next_frequency = timedelta(seconds=rand_num_secs)
                submit_time += next_frequency


def handle_logging_job(submit_time: datetime, job: dict, vars_dict: dict):
    if job.get("jsonPayload") is not None:
        if vars_dict is None:
            json_payload = job["jsonPayload"]
        else:
            json_payload = format_dict_payload(vars_dict, job["jsonPayload"])
        submit_log_entry_json(
            job["level"], json_payload,
            resource_type=job.get("resourceType"),
            resource_labels=job.get("resourceLabels"),
            labels=job.get("labels"),
            other=job.get("other"),
            when=submit_time.timestamp()
        )
    elif job.get("textPayload") is not None:
        if vars_dict is None:
            text_payload = job["textPayload"]
        else:
            text_payload = format_str_payload(vars_dict, job["textPayload"])
        submit_log_entry_text(
            job["level"], text_payload,
            resource_type=job.get("resourceType"),
            resource_labels=job.get("resourceLabels"),
            labels=job.get("labels"),
            other=job.get("other"),
            when=submit_time.timestamp()
        )


def create_metrics_descriptors():
    for metric_descriptor in _config["metricDescriptors"]:
        sleep(0.01)

        # cannot think of a useful use case for variables in descriptor, so leaving them out

        submit_metric_descriptor(
            metric_descriptor["type"], metric_descriptor["metricKind"], metric_descriptor["valueType"],
            name=metric_descriptor.get("name"),
            project_id=metric_descriptor.get("projectId"),
            unit=metric_descriptor.get("unit"),
            description=metric_descriptor.get("description"),
            display_name=metric_descriptor.get("displayName"),
            launch_stage=metric_descriptor.get("launchStage"),
            labels=metric_descriptor.get("labels"),
            monitored_resource_types=metric_descriptor.get("monitoredResourceTypes")
        )


def handle_monitoring_job(submit_time: datetime, job: dict, vars_dict: dict):
    metric_labels = job.get("metricLabels")
    resource_labels = job.get("resourceLabels")
    if vars_dict is None:
        metric_value = job["metricValue"]
    else:
        metric_value = format_str_payload(vars_dict, job["metricValue"])
        if metric_labels is not None:
            metric_labels = {k: format_str_payload(vars_dict, v) for k, v in job["metricLabels"].items()}
        if resource_labels is not None:
            resource_labels = {k: format_str_payload(vars_dict, v) for k, v in job["resource_labels"].items()}
    submit_gauge_metric(
        metric_value, job["metricType"], submit_time,
        project_id=job.get("projectId"),
        metric_labels=metric_labels,
        resource_type=job.get("resourceType"),
        resource_labels=resource_labels
    )
