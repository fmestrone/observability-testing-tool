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

from observability_testing_tool.config.common import debug_log, info_log, error_log
from observability_testing_tool.config.parser import parse_config, prepare_config, next_timedelta_from_interval

from observability_testing_tool.obs.cloud_logging import setup_logging_client, submit_log_entry, submit_log_entry_json, submit_log_entry_proto, logger
from observability_testing_tool.obs.cloud_monitoring import setup_monitoring_client, submit_gauge_metric, submit_metric_descriptor


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
            error_log("No config information was found. Is the file empty?")
            exit(1)
        prepare_config(_config)
    except ValueError as e:
        error_log(str(e))
        exit(1)
    except Exception as e:
        error_log("There was an error parsing the configuration file", _config, e)
        exit(1)

    if _config.get("cloudConfig") is not None:
        environ["GOOGLE_CLOUD_PROJECT"] = _config["cloudConfig"]["project"]
        environ["GOOGLE_APPLICATION_CREDENTIALS"] = _config["cloudConfig"]["credentials"]

    # these calls need to happen AFTER the environment variables have been set
    setup_logging_client()
    setup_monitoring_client()

    debug_log("Final configuration settings", _config)


def expand_list_variable(selector, value):
    # TODO selector chooses item, range allows to limit values that selector acts on
    # E.g. range: None, selector: any = random value from full list
    # E.g. range: 5-9, selector: any = random value from sublist/slice
    # E.g. range: None, selector: all = the full list
    # E.g. range: 5-9, selector: all = the entire sublist/slice
    # In this case range would have to be ALSO at the variable level, used for a list

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
            raise ValueError(f"Variable '{value}' uses an invalid list selector '{selector}'")


_regex_var_name_index = re.compile(r'^(?P<name>.+?)(\[(?P<index>.+)])?$')


def _split_var_name_index(var_name):
    parts = _regex_var_name_index.match(var_name)
    if parts is None:
        return var_name, None
    else:
        return parts.groupdict("name"), parts.groupdict("index")


# need the data sources for testability
def expand_variables(variables: list, data_sources: dict) -> dict | None:
    if variables is None: return None
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
            raise ValueError(f"Variable {idx} is not configured correctly")
        data_source = data_sources.get(data_source_name)
        if data_source is None:
            raise ValueError(f"Data source for '{var_name}' does not exist")

        data_source_value = data_source["value"]
        match data_source["sourceType"]:
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
        p = Process(target=_run_live_jobs, args=("loggingJobs", "logEntries", handle_logging_job, _config))
        p.start()
    else:
        p = None
    _run_batch_jobs("loggingJobs", "logEntries", handle_logging_job)
    return p


def run_monitoring_jobs() -> Process:
    global _config
    # https://docs.python.org/3/library/multiprocessing.html
    if _config["hasLiveMonitoringJobs"]:
        p = Process(target=_run_live_jobs, args=("monitoringJobs", "metricEntries", handle_monitoring_job, _config))
        p.start()
    else:
        p = None
    _run_batch_jobs("monitoringJobs", "metricEntries", handle_monitoring_job)
    return p

# NOT IN USE - FUTURE IDEA
def _run_jobs(config: dict):
    # https://docs.python.org/3/library/multiprocessing.html
    has_live_jobs = bool(config["hasLiveJobs"])
    job_config = config["jobConfig"]
    data_sources = job_config["dataSources"]
    handler = job_config["handler"]
    if has_live_jobs:
        p = Process(target=_run_live_jobs, args=(job_config, data_sources, handler))
        p.start()
    else:
        p = None
    _run_batch_jobs(job_config, data_sources, handler)
    return p

# NOT IN USE - FUTURE IDEA
def _run_live_jobs2(jobs_config: dict, data_sources: dict, handler: Callable):
    setup_logging_client()
    schedule = sched.scheduler(time, sleep)
    jobs = jobs_config["jobs"]
    job_entries = jobs_config["entries"]
    for job in jobs:
        if not job["live"]: continue
        job_key = f"LiveJob [{job['id']}]"
        job_config = dict(job)
        for entry in job_entries:
            entry = job_config | entry
            start_time = entry["startTime"]
            debug_log(f"{job_key}: Queuing into scheduler", job)
            if start_time > datetime.now():
                schedule.enter(0, 1, _handle_live_job, (schedule, entry, data_sources, handler))
            else:
                schedule.enterabs(start_time.timestamp(), 1, _handle_live_job, (schedule, entry, data_sources, handler))
    # info_log(f"Initial Scheduler Queue for [{jobs_key}]", schedule.queue)
    schedule.run(True)
    exit(0)


def _run_live_jobs(jobs_key: str, entries_key: str, handler: Callable, config: dict):
    setup_logging_client()
    setup_monitoring_client()
    schedule = sched.scheduler(time, sleep)
    for job in config[jobs_key]:
        if not job["live"]: continue
        job_key = f"LiveJob [{job['id']}]"
        job_config = dict(job)
        del job_config[entries_key]
        for entry in job[entries_key]:
            entry = job_config | entry
            start_time = entry["startTime"]
            debug_log(f"{job_key}: Queuing into scheduler", job)
            if start_time <= datetime.now():
                schedule.enter(0, 1, _handle_live_job, (schedule, entry, config["dataSources"], handler))
            else:
                schedule.enterabs(start_time.timestamp(), 1, _handle_live_job, (schedule, entry, config["dataSources"], handler))
    info_log(f"Initial Scheduler Queue for [{jobs_key}]", schedule.queue)
    schedule.run(True)
    exit(0)


def _handle_live_job(schedule: sched.scheduler, job: dict, data_sources: dict, handler: Callable):
    job_key = job["id"]
    debug_log(f"{job_key}: Running scheduled job", job)
    if datetime.now() >= job["endTime"]:
        info_log(f"{job_key}: Job has completed (past end time)")
        return
    vars_dict = expand_variables(job.get("variables"), data_sources)
    handler(datetime.now(), job, vars_dict)
    next_time = next_timedelta_from_interval(job["frequency"])
    info_log(f"{job_key}: Next Execution in {next_time}")
    schedule.enter(next_time.total_seconds(), 1, _handle_live_job, (schedule, job, data_sources, handler))


def _run_batch_jobs(jobs_key: str, entry_key: str, handler: Callable):
    for job in _config[jobs_key]:
        if job["live"]: continue
        sleep(0.5)
        job_config = dict(job)
        del job_config[entry_key]
        for entry in job[entry_key]:
            entry = job_config | entry
            submit_time = entry["startTime"]
            end_time = entry["endTime"]
            frequency = entry["frequency"]
            info_log(f"{entry['id']}: Starting job from {submit_time} to {end_time} every {frequency}")
            while submit_time < end_time:
                sleep(0.05) # avoid exceeding burn rate of API
                vars_dict = expand_variables(entry["variables"], _config["dataSources"])

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
        log_payload_type = "JSON"
        if vars_dict is None:
            payload = job["jsonPayload"]
        else:
            payload = format_dict_payload(vars_dict, job["jsonPayload"])
        submit_log_entry_json(severity, payload, **kw)

    elif job.get("textPayload") is not None:
        log_payload_type = "text"
        if vars_dict is None:
            payload = job["textPayload"]
        else:
            payload = format_str_payload(vars_dict, job["textPayload"])
        submit_log_entry(severity, payload, **kw)

    elif job.get("protoPayload") is not None:
        log_payload_type = "ProtoBuf"
        if vars_dict is None:
            payload = job["protoPayload"]
        else:
            payload = format_dict_payload(vars_dict, job["protoPayload"])
        submit_log_entry_proto(severity, payload, **kw)

    else:
        raise ValueError(f"{job_key}: No payload available for log")

    info_log(f"{job_key}: Sending {severity} log to {log_name} with {log_payload_type} payload at {submit_time}", payload)


def create_metrics_descriptors():
    for metric_descriptor in _config["metricDescriptors"]:
        sleep(0.01)

        project_id = metric_descriptor.get("projectId")
        metric_type = metric_descriptor.get("metricType")
        metric_kind = metric_descriptor.get("metricKind")
        value_type = metric_descriptor.get("valueType")
        metric_name = metric_descriptor.get("name")
        vars_dict = expand_variables(metric_descriptor.get("variables"), _config["dataSources"])
        if vars_dict is not None:
            project_id = format_str_payload(vars_dict, project_id)

        info_log(f"Metrics Descriptor: Creating {metric_name} ({metric_type}, {metric_kind}, {value_type}) in {project_id}")
        submit_metric_descriptor(
            metric_type, metric_kind, value_type,
            name=metric_name,
            project_id=project_id,
            unit=metric_descriptor.get("unit"),
            description=metric_descriptor.get("description"),
            display_name=metric_descriptor.get("displayName"),
            launch_stage=metric_descriptor.get("launchStage"),
            labels=metric_descriptor.get("labels"),
            monitored_resource_types=metric_descriptor.get("monitoredResourceTypes")
        )


def handle_monitoring_job(submit_time: datetime, job: dict, vars_dict: dict):
    job_key = job["id"]
    metric_type = job["metricType"]
    if vars_dict is None:
        metric_value = float(job["metricValue"])
        metric_labels = job.get("labels")
        resource_type = job.get("resourceType")
        resource_labels = job.get("resourceLabels")
        project_id = job.get("projectId")
    else:
        metric_value = float(format_str_payload(vars_dict, job["metricValue"]))
        metric_labels = format_dict_payload(vars_dict, job.get("metricLabels"))
        resource_type = format_str_payload(vars_dict, job.get("resourceType"))
        resource_labels = format_dict_payload(vars_dict, job.get("resourceLabels"))
        project_id = format_str_payload(vars_dict, job.get("projectId"))

    info_log(f"{job_key}: Sending {metric_type} in {project_id} = {metric_value}")
    submit_gauge_metric(
        metric_value, metric_type, submit_time,
        project_id=project_id,
        metric_labels=metric_labels,
        resource_type=resource_type,
        resource_labels=resource_labels
    )
