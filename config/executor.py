import random
import sched
import sys
from multiprocessing import Process
from collections.abc import Callable

from datetime import datetime
from os import environ
from random import randrange
from time import sleep, time

from config.common import debug_log
from config.parser import parse_config, prepare_config, next_timedelta_from_interval

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = None

_config = {}
try:
    _config = parse_config(filename)
    if _config is None:
        debug_log("No config information was found. Is the file empty?")
        exit(1)
    prepare_config(_config)
except Exception as e:
    debug_log("There was an error parsing the configuration file", _config, e)
    exit(1)


if _config.get("cloudConfig") is not None:
    environ["GOOGLE_CLOUD_PROJECT"] = _config["cloudConfig"]["project"]
    environ["GOOGLE_APPLICATION_CREDENTIALS"] = _config["cloudConfig"]["credentials"]

# these imports need to happen AFTER the environment variables have been set

from obs.cloud_logging import submit_log_entry_text, submit_log_entry_json
from obs.cloud_monitoring import submit_gauge_metric, submit_metric_descriptor

debug_log("Final configuration settings", _config)

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
            case "list":
                var_list_selector = var_config.get("selector")
                if var_list_selector is None or var_list_selector not in _datasource_list_selectors:
                    raise ValueError(f"Variable {var_name} uses an invalid list selector")
                variables_expanded[var_name] = expand_list_variable(var_list_selector, data_source_value)
            case "random":
                rand_range = data_source.get("range")
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
            case "env" | "gce-metadata":
                variables_expanded[var_name] = data_source["__value__"]

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


def run_logging_jobs() -> Process:
    # https://docs.python.org/3/library/multiprocessing.html
    if _config["hasLiveLoggingJobs"]:
        p = Process(target=_run_live_jobs, args=("loggingJobs", handle_logging_job))
        p.start()
    else:
        p = None
    _run_batch_jobs("loggingJobs", handle_logging_job)
    return p


def run_monitoring_jobs() -> Process:
    # https://docs.python.org/3/library/multiprocessing.html
    # https://docs.python.org/3/library/multiprocessing.html
    if _config["hasLiveMonitoringJobs"]:
        p = Process(target=_run_live_jobs, args=("monitoringJobs", handle_monitoring_job))
        p.start()
    else:
        p = None
    _run_batch_jobs("monitoringJobs", handle_monitoring_job)
    return p

def _run_live_jobs(jobs_key: str, handler: Callable):
    schedule = sched.scheduler(time, sleep)
    for idx, job in enumerate(_config[jobs_key], start=1):
        if not job["live"]: continue
        job_key = f"LiveJob [{jobs_key}/{idx}]"
        debug_log(f"{job_key}: Queuing into scheduler", job)
        if job["startTime"] > datetime.now():
            schedule.enter(0, 1, _handle_live_job, (job_key, schedule, job, handler))
        else:
            schedule.enterabs(job["startTime"].timestamp(), 1, _handle_live_job, (job_key, schedule, job, handler))
    schedule.run(True)
    debug_log(f"Initial Scheduler Queue for [{jobs_key}]", schedule.queue)
    exit(0)


def _handle_live_job(job_key: str, schedule: sched.scheduler, job: dict, handler: Callable):
    debug_log(f"{job_key}: Running scheduled job", job)
    if datetime.now() >= job["endTime"]: return
    if job.get("variables") is not None:
        vars_dict = expand_variables(job["variables"])
    else:
        vars_dict = None
    handler(job_key, datetime.now(), job, vars_dict)
    next_time = next_timedelta_from_interval(job["frequency"])
    debug_log(f"{job_key}: Next Execution for in {next_time}")
    schedule.enter(next_time.total_seconds(), 1, _handle_live_job, (job_key, schedule, job, handler))


def _run_batch_jobs(jobs_key: str, handler: Callable):
    for idx, job in enumerate(_config[jobs_key], start=1):
        if job["live"]: continue
        sleep(0.5)
        job_key = f"BatchJob [{jobs_key}/{idx}]"
        submit_time = job["startTime"]
        end_time = job["endTime"]
        frequency = job["frequency"]
        while submit_time < end_time:
            sleep(0.05) # avoid exceeding burn rate of API
            if job.get("variables") is not None:
                vars_dict = expand_variables(job["variables"])
            else:
                vars_dict = None

            handler(job_key, submit_time, job, vars_dict)

            submit_time += next_timedelta_from_interval(frequency)


def handle_logging_job(job_key: str, submit_time: datetime, job: dict, vars_dict: dict):
    labels = job.get("labels")
    resource_labels = job.get("resourceLabels")
    other = job.get("other")
    if vars_dict is not None:
        if labels is not None:
            labels = format_dict_payload(vars_dict, labels)
        if resource_labels is not None:
            resource_labels = format_dict_payload(vars_dict, resource_labels)
        if other is not None:
            other = format_dict_payload(vars_dict, other)

    if job.get("jsonPayload") is not None:
        if vars_dict is None:
            json_payload = job["jsonPayload"]
        else:
            json_payload = format_dict_payload(vars_dict, job["jsonPayload"])
        submit_log_entry_json(
            job["level"], json_payload,
            resource_type=job.get("resourceType"),
            resource_labels=resource_labels,
            labels=labels,
            other=other,
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
            resource_labels=resource_labels,
            labels=labels,
            other=other,
            when=submit_time.timestamp()
        )


def create_metrics_descriptors():
    for metric_descriptor in _config["metricDescriptors"]:
        sleep(0.01)

        project_id = metric_descriptor.get("projectId")
        if metric_descriptor.get("variables") is not None:
            vars_dict = expand_variables(metric_descriptor["variables"])
        else:
            vars_dict = None
        if vars_dict is not None:
            if project_id is not None:
                project_id = format_str_payload(vars_dict, project_id)

        submit_metric_descriptor(
            metric_descriptor["type"], metric_descriptor["metricKind"], metric_descriptor["valueType"],
            name=metric_descriptor.get("name"),
            project_id=project_id,
            unit=metric_descriptor.get("unit"),
            description=metric_descriptor.get("description"),
            display_name=metric_descriptor.get("displayName"),
            launch_stage=metric_descriptor.get("launchStage"),
            labels=metric_descriptor.get("labels"),
            monitored_resource_types=metric_descriptor.get("monitoredResourceTypes")
        )


def handle_monitoring_job(job_key: str, submit_time: datetime, job: dict, vars_dict: dict):
    metric_labels = job.get("metricLabels")
    resource_labels = job.get("resourceLabels")
    project_id = job.get("projectId")
    if vars_dict is None:
        metric_value = float(job["metricValue"])
    else:
        metric_value = float(format_str_payload(vars_dict, job["metricValue"]))
        if metric_labels is not None:
            metric_labels = format_dict_payload(vars_dict, metric_labels)
        if resource_labels is not None:
            resource_labels = format_dict_payload(vars_dict, resource_labels)
        if project_id is not None:
            project_id = format_str_payload(vars_dict, project_id)
    submit_gauge_metric(
        metric_value, job["metricType"], submit_time,
        project_id=project_id,
        metric_labels=metric_labels,
        resource_type=job.get("resourceType"),
        resource_labels=resource_labels
    )
