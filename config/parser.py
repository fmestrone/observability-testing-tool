import re
from os import getenv

import yaml

from datetime import timedelta
from datetime import datetime

import requests

_regex_duration = re.compile(r'^ *((?P<days>[.\d]+?)d)? *((?P<hours>[.\d]+?)h)? *((?P<minutes>[.\d]+?)m)? *((?P<seconds>[.\d]+?)s)? *((?P<millis>\d+?)ms)? *$')

_datasource_types = ["env", "list", "random", "gce-metadata"]
_datasource_random_values = ["int", "float"]


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
        raise RuntimeError("Duration string is not formatted correctly")
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
        raise RuntimeError("Could not parse any duration information from '{}'.  Examples of valid strings: '8h', '2d8h5m20s', '2m4s'".format(parts))
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)


def configure_job_timings(job_config: dict):
    job_config["frequency"] = parse_timedelta_interval(job_config["frequency"])
    if job_config.get("startOffset") is not None:
        job_config["startOffset"] = parse_timedelta_interval(job_config["startOffset"])
    if job_config.get("endOffset") is not None:
        job_config["endOffset"] = parse_timedelta_interval(job_config["endOffset"])

    if job_config.get("live", False):
        job_config["startTime"] = datetime.strptime(job_config["startTime"], "%d/%m/%YT%H:%M:%S.%f")
        if job_config.get("endTime") is None:
            job_config["endTime"] = datetime.today()
        else:
            job_config["endTime"] = datetime.strptime(job_config["endTime"], "%d/%m/%YT%H:%M:%S.%f")
    else:
        job_config["endTime"] = datetime.strptime(job_config["endTime"], "%d/%m/%YT%H:%M:%S.%f")
        if job_config.get("startTime") is None:
            job_config["startTime"] = datetime.today()
        else:
            job_config["startTime"] = datetime.strptime(job_config["startTime"], "%d/%m/%YT%H:%M:%S.%f")
    if job_config["startTime"] >= job_config["endTime"]:
        raise RuntimeError("End time of job must be later than start time")


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
    if config.get("monitoringJobs") is None:
        config["monitoringJobs"] = []

    for datasource in config["dataSources"].values():
        configure_data_source(datasource)

    for job in config["loggingJobs"]:
        configure_logging_job(job)

    for job in config["monitoringJobs"]:
        configure_monitoring_job(job)


def get_gce_metadata(metadata_key: str) -> str:
    # This will only work from inside a GCE instance
    metadata_server = "http://metadata.google.internal/computeMetadata/v1/"
    metadata_flavor = {"Metadata-Flavor" : "Google"}
    return requests.get(metadata_server + metadata_key, headers = metadata_flavor).text


def configure_logging_job(logging_job: dict):
    if logging_job.get("textPayload") is None and logging_job.get("jsonPayload") is None:
        raise RuntimeError("Missing 'textPayload' or 'jsonPayload' in config")
    configure_job_timings(logging_job)


def configure_monitoring_job(monitoring_job: dict):
    configure_job_timings(monitoring_job)


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

