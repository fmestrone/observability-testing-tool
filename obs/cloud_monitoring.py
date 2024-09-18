from google.cloud import monitoring_v3

import time

from os import getenv


client = monitoring_v3.MetricServiceClient()


def prepare_time_interval_gauge(start_time: None):
    if start_time is None:
        start_time = time.time()
    seconds = int(start_time)  # Integer part of time() is the number of seconds
    nanos = int((start_time - seconds) * 10 ** 9)
    return monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )


def prepare_time_interval(start_time: None, delta: None):
    if start_time is None:
        start_time = time.time()
    seconds = int(start_time)  # Integer part of time() is the number of seconds
    nanos = int((start_time - seconds) * 10 ** 9)
    if delta is None:
        delta = 1 # Deafult interval of one second
    delta_seconds = int(delta)
    delta_nanos = int((delta - delta_seconds) * 10 ** 9)
    return monitoring_v3.TimeInterval({
        "start_time": {"seconds": seconds, "nanos": nanos},
        "end_time": {"seconds": seconds + delta_seconds, "nanos": nanos + delta_nanos},
    })


def submit_gauge_metric(value, metric_name, when = None, project_name = None, metric_labels = None, resource_type = None, resource_labels = None):
    # Create a data point for the timestamp interval
    point = monitoring_v3.Point({"interval": prepare_time_interval_gauge(when), "value": {"double_value": value}})

    # Prepare a time series and all its attributes
    series = monitoring_v3.TimeSeries()
    series.metric_kind = "GAUGE"
    series.metric.type = f"custom.googleapis.com/{metric_name}"
    series.metric.labels.update(metric_labels if metric_labels is not None else {})
    series.resource.type = resource_type if resource_type is not None else "global"
    series.resource.labels.update(resource_labels if resource_labels is not None else {})

    # Add the data point to the series
    series.points = [point]

    # Submit the time series data
    project_name = f"projects/{project_name if project_name is not None else getenv('GOOGLE_CLOUD_PROJECT')}"
    client.create_time_series(request={"name": project_name, "time_series": [series]})

