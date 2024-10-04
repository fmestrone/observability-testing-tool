import random
import re
import sched
import sys
from multiprocessing import Process
from collections.abc import Callable

from datetime import datetime
from os import environ
from random import randrange
from time import sleep, time

from config.common import debug_log, info_log, error_log
from config.parser import parse_config, prepare_config, next_timedelta_from_interval

from obs.cloud_logging import setup_logging_client, submit_log_entry, submit_log_entry_json, submit_log_entry_proto, logger
from obs.cloud_monitoring import setup_monitoring_client, submit_gauge_metric, submit_metric_descriptor


_config = {}


def prepare():
    global _config
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = None
    try:
        _config = parse_config(filename)
        if _config is None:
            info_log("No config information was found. Is the file empty?")
            exit(1)
        prepare_config(_config)
    except Exception as e:
        info_log("There was an error parsing the configuration file", _config, e)
        exit(1)

    if _config.get("cloudConfig") is not None:
        environ["GOOGLE_CLOUD_PROJECT"] = _config["cloudConfig"]["project"]
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = _config["cloudConfig"]["credentials"]

    # these calls need to happen AFTER the environment variables have been set
    setup_logging_client()
    setup_monitoring_client()

    debug_log("Final configuration settings", _config)


def expand_list_variable(selector, value):
    if selector == "any":
        return random.choice(value)
    elif selector == "first":
        return value[0]
    elif selector == "last":
        return value[-1]
    elif selector == "all":
        return value
    else:
        try:
            return value[int(selector)]
        except ValueError:
            # TODO allow range selection (sublist/slice)
            raise ValueError(f"Variable '{value}' uses an invalid list selector '{selector}'")

_regex_var_name_index = re.compile(r'^(?P<name>.+?)(\[(?P<index>.+)])?$')

def _split_var_name_index(var_name):
    parts = _regex_var_name_index.match(var_name)
    if parts is None:
        return (var_name, None)
    else:
        return (parts.groupdict("name"), parts.groupdict("index"))


# need the data sources for testability
def expand_variables(variables: list, data_sources: dict) -> dict:
    debug_log("Received request to expand variables", variables)
    variables_expanded = {}
    for idx, var_config in enumerate(variables, start=1):
        if isinstance(var_config, str):
            data_source_name = var_config
            var_name = var_config
            var_config = {} # so it does not fail when looking up the config further down, e.g. var_config.get("extractor")
        elif isinstance(var_config, dict):
            var_name = var_config["name"]
            data_source_name = var_config.get("dataSource", var_name)
        else:
            raise ValueError(f"Variable {idx} is not configure correctly")
        data_source = data_sources.get(data_source_name)
        if data_source is None:
            raise ValueError(f"Data source for '{var_name}' does not exist")

        data_source_value = data_source["value"]
        match data_source["type"]:
            case "list":
                var_list_selector = var_config.get("selector", "any")
                variables_expanded[var_name] = expand_list_variable(var_list_selector, data_source_value)
            case "random":
                rand_range = data_source["range"]
                if data_source_value == "int":
                    variables_expanded[var_name] = randrange(
                        rand_range.get("from", 0),
                        rand_range.get("to", 2147483647),
                        rand_range.get("step", 1)
                    )
                elif data_source_value == "float":
                    variables_expanded[var_name] = random.uniform(
                        rand_range.get("from", 0.0),
                        rand_range.get("to", 2147483647.0),
                    )
            case "env" | "gce-metadata":
                variables_expanded[var_name] = data_source["__value__"]
            case "fixed":
                # This type is mostly needed for testing and debugging
                variables_expanded[var_name] = data_source["value"]

        var_index = var_config.get("index")
        if var_index is not None:
            expanded_value = variables_expanded[var_name]
            if not isinstance(expanded_value, dict) and not isinstance(expanded_value, list):
                error_log(f"Could not get indexed value from '{expanded_value}' in variable '{var_name}' with index '{var_index}'", "Make sure the value is a JSON object or array")
            else:
                variables_expanded[var_name] = expanded_value[var_index]

        var_extractor = var_config.get("extractor")
        if var_extractor is not None:
            expanded_value = variables_expanded[var_name]
            if not isinstance(expanded_value, str):
                expanded_value = str(expanded_value)
            matches = re.search(var_extractor, expanded_value)
            if matches is None or matches.group(1) is None:
                error_log(f"Could not extract from '{expanded_value}' in variable '{var_name}' with regex '{var_extractor}'", "Did you include a group in the regex?")
            else:
                variables_expanded[var_name] = matches.group(1)

    debug_log("Returning expanded variables", variables_expanded)
    return variables_expanded


def format_str_payload(vars_dict: dict, text: str):
    if text is None: return None
    # TODO need to verify that text is valid
    # - only {varname} or {varname[index]} syntax is allowed
    # - varname must exist in vars_dict
    # - for everything else, token is returned verbatim
    # can use _split_var_name_index function to help
    return text.format(**vars_dict)


def format_dict_payload(vars_dict: dict, obj: dict):
    if obj is None: return None
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
    global _config
    # https://docs.python.org/3/library/multiprocessing.html
    if _config["hasLiveLoggingJobs"]:
        p = Process(target=_run_live_jobs, args=("loggingJobs", handle_logging_job, _config))
        p.start()
    else:
        p = None
    _run_batch_jobs("loggingJobs", handle_logging_job)
    return p


def run_monitoring_jobs() -> Process:
    global _config
    # https://docs.python.org/3/library/multiprocessing.html
    # https://docs.python.org/3/library/multiprocessing.html
    if _config["hasLiveMonitoringJobs"]:
        p = Process(target=_run_live_jobs, args=("monitoringJobs", handle_monitoring_job, _config))
        p.start()
    else:
        p = None
    _run_batch_jobs("monitoringJobs", handle_monitoring_job)
    return p


def _run_live_jobs(jobs_key: str, handler: Callable, config: dict):
    setup_logging_client()
    schedule = sched.scheduler(time, sleep)
    for job in config[jobs_key]:
        if not job["live"]: continue
        job_key = f"LiveJob [{job['id']}]"
        debug_log(f"{job_key}: Queuing into scheduler", job)
        if job["startTime"] > datetime.now():
            schedule.enter(0, 1, _handle_live_job, (schedule, job, config["dataSources"], handler))
        else:
            schedule.enterabs(job["startTime"].timestamp(), 1, _handle_live_job, (schedule, job, config["dataSources"], handler))
    schedule.run(True)
    debug_log(f"Initial Scheduler Queue for [{jobs_key}]", schedule.queue)
    exit(0)


def _handle_live_job(schedule: sched.scheduler, job: dict, data_sources: dict, handler: Callable):
    job_key = job["id"]
    debug_log(f"{job_key}: Running scheduled job", job)
    if datetime.now() >= job["endTime"]: return
    if job.get("variables") is not None:
        vars_dict = expand_variables(job["variables"], data_sources)
    else:
        vars_dict = None
    handler(datetime.now(), job, vars_dict)
    next_time = next_timedelta_from_interval(job["frequency"])
    debug_log(f"{job_key}: Next Execution for in {next_time}")
    schedule.enter(next_time.total_seconds(), 1, _handle_live_job, (schedule, job, data_sources, handler))


def _run_batch_jobs(jobs_key: str, handler: Callable):
    for job in _config[jobs_key]:
        if job["live"]: continue
        sleep(0.5)
        jobConfig = dict(job)
        del jobConfig["loggingEntries"]
        for entry in job["loggingEntries"]:
            entry = jobConfig | entry
            submit_time = entry["startTime"]
            end_time = entry["endTime"]
            frequency = entry["frequency"]
            info_log(f"{entry['id']}: Starting job from {submit_time} to {end_time} every {frequency}")
            while submit_time <= end_time: # use "<=" because same value means execute once!
                sleep(0.05) # avoid exceeding burn rate of API
                if entry.get("variables") is not None:
                    vars_dict = expand_variables(entry["variables"], _config["dataSources"])
                else:
                    vars_dict = None

                handler(submit_time, entry, vars_dict)

                submit_time += next_timedelta_from_interval(frequency)


def handle_logging_job(submit_time: datetime, job: dict, vars_dict: dict):
    job_key = job["id"]
    labels = job.get("labels")
    resource_type = job.get("resourceType")
    resource_labels = job.get("resourceLabels")
    other = job.get("other")
    severity = job.get("level")
    log_name = job.get("logName")
    if vars_dict is not None:
        labels = format_dict_payload(vars_dict, labels)
        resource_type = format_str_payload(vars_dict, resource_type)
        resource_labels = format_dict_payload(vars_dict, resource_labels)
        other = format_dict_payload(vars_dict, other)
        severity = format_str_payload(vars_dict, severity)
        log_name = format_str_payload(vars_dict, log_name)

    kw = {
        "log_name": log_name,
        "resource_type": resource_type,
        "resource_labels": resource_labels,
        "labels": labels,
        "other": other,
        "when": submit_time
    }

    if job.get("jsonPayload") is not None:
        if vars_dict is None:
            json_payload = job["jsonPayload"]
        else:
            json_payload = format_dict_payload(vars_dict, job["jsonPayload"])
        info_log(f"{job_key}: Sending log with JSON Payload", json_payload)
        submit_log_entry_json(severity, json_payload, **kw)

    elif job.get("textPayload") is not None:
        if vars_dict is None:
            text_payload = job["textPayload"]
        else:
            text_payload = format_str_payload(vars_dict, job["textPayload"])
        info_log(f"{job_key}: Sending log with text Payload", text_payload)
        submit_log_entry(severity, text_payload, **kw)

    elif job.get("protoPayload") is not None:
        if vars_dict is None:
            proto_payload = job["protoPayload"]
        else:
            proto_payload = format_dict_payload(vars_dict, job["protoPayload"])
        info_log(f"{job_key}: Sending log with ProtoBuf Payload", proto_payload)
        submit_log_entry_proto(severity, proto_payload, **kw)


def create_metrics_descriptors():
    for metric_descriptor in _config["metricDescriptors"]:
        sleep(0.01)

        project_id = metric_descriptor.get("projectId")
        if metric_descriptor.get("variables") is not None:
            vars_dict = expand_variables(metric_descriptor["variables"], _config["dataSources"])
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


def handle_monitoring_job(submit_time: datetime, job: dict, vars_dict: dict):
    metric_labels = job.get("metricLabels")
    resource_labels = job.get("resourceLabels")
    project_id = job.get("projectId")
    if vars_dict is None:
        metric_value = float(job["metricValue"])
    else:
        metric_value = float(format_str_payload(vars_dict, job["metricValue"]))
        metric_labels = format_dict_payload(vars_dict, metric_labels)
        resource_labels = format_dict_payload(vars_dict, resource_labels)
        project_id = format_str_payload(vars_dict, project_id)
    submit_gauge_metric(
        metric_value, job["metricType"], submit_time,
        project_id=project_id,
        metric_labels=metric_labels,
        resource_type=job.get("resourceType"),
        resource_labels=resource_labels
    )
