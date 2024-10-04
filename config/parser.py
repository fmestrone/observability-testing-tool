import random
import re
from os import getenv

import yaml

from datetime import timedelta
from datetime import datetime

import requests

__ADVOBS_NO_GCE_METADATA = (getenv("ADVOBS_NO_GCE_METADATA") == "True" or getenv("ADVOBS_DRY_RUN") == "True")

_regex_duration = re.compile(r'^ *(-?) *((?P<days>[.\d]+?)d)? *((?P<hours>[.\d]+?)h)? *((?P<minutes>[.\d]+?)m)? *((?P<seconds>[.\d]+?)s)? *((?P<milliseconds>\d+?)ms)? *$')

_datasource_types = ["env", "list", "random", "gce-metadata", "fixed"]
_datasource_random_values = ["int", "float"]


def next_timedelta_from_interval(interval_or_range) -> timedelta:
    if isinstance(interval_or_range, timedelta):
        return interval_or_range
    elif isinstance(interval_or_range, dict):
        rand_num_secs = random.uniform(interval_or_range["from"].total_seconds(), interval_or_range["to"].total_seconds())
        next_frequency = timedelta(seconds=rand_num_secs)
        return next_frequency
    else:
        raise ValueError(f"Invalid interval value")


def parse_float_range(range_cfg: str) -> dict:
    """
    Parses a floating point range (e.g. "13.9~39.3") into a dict object, with `from`
    and `to` keys.

    If only one value is provided (e.g. "15.3937"), that will be the end of the range, with the
    beginning of the range set to 0.0.

    :param range_cfg: A string identifying a floating point range (e.g. "13.9~39.3")
    :return dict: A dictionary object with `from` and `to` keys
    """
    values = range_cfg.split('~') # otherwise cannot have negative values
    if len(values) <= 0 or len(values) > 2:
        raise ValueError("Range string is not formatted correctly")
    elif len(values) == 1:
        return { "from": 0.0, "to": float(values[0]) }
    else:
        return { "from": float(values[0]), "to": float(values[1]) }


def parse_int_range(range_cfg: str) -> dict:
    """
    Parses an integer range (e.g. "13~39") into a dict object, with `from`
    and `to` keys.

    If only one value is provided (e.g. "15"), that will be the end of the range, with the
    beginning of the range set to 0.

    :param range_cfg: A string identifying an integer range (e.g. "13~39")
    :return dict: A dictionary object with `from` and `to` keys
    """
    values = range_cfg.split('~') # otherwise cannot have negative values
    if len(values) <= 0 or len(values) > 3:
        raise RuntimeError("Range string is not formatted correctly")
    elif len(values) == 1:
        return { "from": 0, "to": int(values[0]) }
    elif len(values) == 2:
        return { "from": int(values[0]), "to": int(values[1]) }
    else:
        return { "from": int(values[0]), "to": int(values[1]), "step": int(values[2]) }


def parse_timedelta_interval(duration_cfg: str) -> timedelta | dict:
    durations = duration_cfg.split('~') # for consistency with int/float range parsers
    if len(durations) <= 0 or len(durations) > 2:
        raise ValueError("Duration string is not formatted correctly")
    elif len(durations) == 1:
        return parse_timedelta_value(durations[0])
    else:
        return {
            "from": parse_timedelta_value(durations[0]),
            "to": parse_timedelta_value(durations[1]),
        }


def parse_timedelta_value(duration_val: str) -> timedelta:
    """
    Parses a time string (e.g. 2h13m) into a timedelta object.

    Modified from virhilo's answer at https://stackoverflow.com/a/4628148/851699

    :param duration_val: A string identifying a duration.  (e.g. 2h13m)
    :return datetime.timedelta: A datetime.timedelta object
    """
    parts = _regex_duration.match(duration_val)
    if parts is None:
        raise ValueError(f"Could not parse any duration information from '{duration_val}'.  Examples of valid strings: '8h', '2d8h5m20s', '2m4s'")
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    if parts.group(1) == "-":
        return -timedelta(**time_params)
    else:
        return timedelta(**time_params)


def parse_datetime(datetime_str: str) -> datetime:
    return datetime.fromisoformat(datetime_str)


def configure_entry_timings(entry_config: dict, logging_job: dict):
    current_timestamp = datetime.now() # create now so the default startTime is later than this point

    entry_config["frequency"] = entry_config.get("frequency", logging_job.get("frequency"))

    if entry_config.get("frequency") is None:
        raise ValueError("Frequency must be specified either in the job config or in the entry config")

    entry_config["startTime"] = entry_config.get("startTime", logging_job.get("startTime"))
    entry_config["endTime"] = entry_config.get("endTime", logging_job.get("endTime"))
    entry_config["startOffset"] = entry_config.get("startOffset", logging_job.get("startOffset"))
    entry_config["endOffset"] = entry_config.get("endOffset", logging_job.get("endOffset"))

    if entry_config.get("startTime") is None and entry_config.get("endTime") is None:
        entry_config["startTime"] = datetime.now()
        entry_config["endTime"] = entry_config["startTime"]
    elif entry_config.get("startTime") is None:
        entry_config["endTime"] = parse_datetime(entry_config["endTime"])
        entry_config["startTime"] = entry_config["endTime"]
    elif entry_config.get("endTime") is None:
        entry_config["startTime"] = parse_datetime(entry_config["startTime"])
        entry_config["endTime"] = entry_config["startTime"]
    else:
        entry_config["startTime"] = parse_datetime(entry_config["startTime"])
        entry_config["endTime"] = parse_datetime(entry_config["endTime"])

    if entry_config.get("startOffset") is not None:
        entry_config["originalStartTime"] = entry_config["startTime"]
        entry_config["startOffset"] = parse_timedelta_interval(entry_config["startOffset"])
        entry_config["startTime"] = entry_config["originalStartTime"] + next_timedelta_from_interval(entry_config["startOffset"])

    if entry_config.get("endOffset") is not None:
        entry_config["originalEndTime"] = entry_config["endTime"]
        entry_config["endOffset"] = parse_timedelta_interval(entry_config["endOffset"])
        entry_config["endTime"] = entry_config["originalEndTime"] + next_timedelta_from_interval(entry_config["endOffset"])

    if entry_config["frequency"] == "once":
        entry_config["frequency"] = "1d"
        entry_config["endTime"] = entry_config["startTime"] + timedelta(hours=1)

    entry_config["frequency"] = parse_timedelta_interval(entry_config["frequency"])

    if logging_job["live"] and entry_config["startTime"] < current_timestamp:
        raise ValueError("Live job must start now or later")

    if entry_config["startTime"] >= entry_config["endTime"]:
        raise ValueError("End time of job must be later than start time")


def _get_variable_name(var_config: dict | str):
    if isinstance(var_config, dict):
        return var_config.get("name")
    elif isinstance(var_config, str):
        return var_config
    else:
        raise ValueError("Variable config must be dict or str")


def configure_variables(entry: dict, logging_vars: dict):
    entry_vars = {_get_variable_name(var): var for var in entry.get("variables", [])}
    entry_vars.update(logging_vars)
    entry["variables"] = [var for var in entry_vars.values()]


def parse_config(file: str = None) -> dict:
    if file is None: file = "config.yaml" # makes it easier to pass None at point of call
    with open(file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def prepare_config(config: dict):
    if config.get("dataSources") is None:
        config["dataSources"] = []
    if config.get("loggingJobs") is None:
        config["loggingJobs"] = []
    if config.get("metricDescriptors") is None:
        config["metricDescriptors"] = []
    if config.get("monitoringJobs") is None:
        config["monitoringJobs"] = []

    for datasource in config["dataSources"].values():
        configure_data_source(datasource)

    config["hasLiveLoggingJobs"] = False
    for job_id, job in enumerate(config["loggingJobs"], start=1):
        temp_id = job.get("id", f"{job_id:03}")
        job["id"] = f"log#{temp_id}"
        if configure_logging_job(job) and not config.get("hasLiveLoggingJobs"):
            config["hasLiveLoggingJobs"] = True

    config["hasLiveMonitoringJobs"] = False
    for job_id, job in enumerate(config["monitoringJobs"], start=1):
        temp_id = job.get("id", f"{job_id:03}")
        job["id"] = f"mon#{temp_id}"
        if configure_monitoring_job(job) and not config.get("hasLiveLoggingJobs"):
            config["hasLiveMonitoringJobs"] = True


def get_gce_metadata(metadata_key: str) -> str:
    # This will only work from inside a GCE instance
    # See https://cloud.google.com/compute/docs/metadata/predefined-metadata-keys
    if __ADVOBS_NO_GCE_METADATA: return "Dummy GCE Metadata"
    metadata_server = "http://metadata.google.internal/computeMetadata/v1/"
    metadata_flavor = {"Metadata-Flavor" : "Google"}
    return requests.get(metadata_server + metadata_key, headers = metadata_flavor).text


def configure_logging_job(logging_job: dict):
    logging_job["live"] = isinstance(logging_job.get("live"), bool) and logging_job["live"] == True

    if logging_job.get("logEntries") is None:
        logging_job["logEntries"] = [{}]

    if logging_job.get("variables") is None:
        logging_job["variables"] = []

    logging_job_vars = {_get_variable_name(var): var for var in logging_job["variables"]}

    for logging_entry_id, logging_entry in enumerate(logging_job["logEntries"], start=1):
        temp_id = logging_entry.get("id", f"{logging_entry_id:03}")
        logging_entry["id"] = f"{logging_job["id"]}/{temp_id}"
        configure_entry_timings(logging_entry, logging_job)
        configure_variables(logging_entry, logging_job_vars)

    del logging_job["variables"]
    del logging_job_vars

    return logging_job["live"]


def configure_monitoring_job(monitoring_job: dict):
    monitoring_job["live"] = isinstance(monitoring_job.get("live"), bool) and monitoring_job["live"] == True

    if monitoring_job.get("metricEntries") is None:
        monitoring_job["metricEntries"] = [{}]

    if monitoring_job.get("variables") is None:
        monitoring_job["variables"] = []

    monitoring_job_vars = {_get_variable_name(var): var for var in monitoring_job["variables"]}

    for metric_entry_id, metric_entry in enumerate(monitoring_job["metricEntries"], start=1):
        temp_id = metric_entry.get("id", f"{metric_entry_id:03}")
        metric_entry["id"] = f"{monitoring_job["id"]}/{temp_id}"
        configure_entry_timings(metric_entry, monitoring_job)
        configure_variables(metric_entry, monitoring_job_vars)

    del monitoring_job["variables"]
    del monitoring_job_vars

    return monitoring_job["live"]


def configure_data_source(data_source: dict):
    data_source_type = data_source.get("type")
    if data_source_type is None or data_source_type not in _datasource_types:
        raise RuntimeError("Data source type '{}' not supported".format(data_source_type))
    else:
        data_source_value = data_source.get("value")
        match data_source_type:
            case "list":
                if not isinstance(data_source_value, list):
                    raise RuntimeError("Data source value for 'list' must be a list")
            case "env":
                if not isinstance(data_source_value, str):
                    raise RuntimeError("Data source value for 'env' must be a string")
                data_source["__value__"] = getenv(data_source_value)
            case "random":
                if data_source_value not in _datasource_random_values:
                    raise RuntimeError("Random value must be a float or an int")
                data_source_range = data_source.get("range")
                if data_source_value == "int":
                    data_source["range"] = parse_int_range(data_source_range)
                elif data_source_value == "float":
                    data_source["range"] = parse_float_range(data_source_range)
            case "gce-metadata":
                data_source["__value__"] = get_gce_metadata(data_source_value)

