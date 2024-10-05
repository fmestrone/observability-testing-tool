import google
from google.cloud import monitoring_v3
from google.api import metric_pb2
from google.api import label_pb2

import datetime

from os import getenv

__ADVOBS_DRY_RUN = (getenv("ADVOBS_DRY_RUN") == "True")


monitoringClient = None


def setup_monitoring_client():
    if __ADVOBS_DRY_RUN: return
    global monitoringClient
    monitoringClient = monitoring_v3.MetricServiceClient()


def prepare_time_interval_gauge(start_time = None):
    if start_time is None:
        start_time = datetime.datetime.today()
    seconds = int(start_time.timestamp())  # Integer part of time() is the number of seconds
    nanos = int((start_time.timestamp() - seconds) * 10 ** 9)
    return monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )


def prepare_time_interval(start_time = None, delta = None):
    if start_time is None:
        start_time = datetime.datetime.today()
    seconds = int(start_time.timestamp())  # Integer part of time() is the number of seconds
    nanos = int((start_time.timestamp() - seconds) * 10 ** 9)
    if delta is None:
        delta = 1 # Deafult interval of one second
    delta_seconds = int(delta)
    delta_nanos = int((delta - delta_seconds) * 10 ** 9)
    return monitoring_v3.TimeInterval({
        "start_time": {"seconds": seconds, "nanos": nanos},
        "end_time": {"seconds": seconds + delta_seconds, "nanos": nanos + delta_nanos},
    })


def submit_gauge_metric(value, metric_type, when = None, project_id = None, metric_labels = None, resource_type = None, resource_labels = None):
    interval = prepare_time_interval_gauge(when)
    submit_metric(value, metric_type, interval, project_id, metric_labels, resource_type, resource_labels)


def submit_delta_metric(value, metric_type, when = None, project_id = None, metric_labels = None, resource_type = None, resource_labels = None):
    # interval = prepare_time_interval_gauge(when)
    # submit_metric(value, "GAUGE", metric_type, interval, project_id, metric_labels, resource_type, resource_labels)
    pass


def submit_metric(value: float, metric_type, interval, project_id = None, metric_labels = None, resource_type = None, resource_labels = None):
    # Create a data point for the timestamp interval
    point = monitoring_v3.Point({"interval": interval, "value": {"double_value": value}})

    # Prepare a time series and all its attributes
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_type}"
    series.metric.labels.update(metric_labels if metric_labels is not None else {})
    series.resource.type = resource_type if resource_type is not None else "global"
    series.resource.labels.update(resource_labels if resource_labels is not None else {})

    # Add the data point to the series
    series.points = [point]

    # Submit the time series data
    project_name = f"projects/{project_id if project_id is not None else getenv('GOOGLE_CLOUD_PROJECT')}"

    if not __ADVOBS_DRY_RUN:
        monitoringClient.create_time_series(request={"name": project_name, "time_series": [series]})


def submit_metric_descriptor(metric_type, kind, value_type, name = None, project_id = None, unit = None, description = None, display_name = None, launch_stage = None, labels = None, monitored_resource_types = None):
    project_id = project_id if project_id is not None else getenv('GOOGLE_CLOUD_PROJECT')

    descriptor = metric_pb2.MetricDescriptor()
    if name is not None: descriptor.name = name
    descriptor.type = f"custom.googleapis.com/{metric_type}"

    descriptor_path = monitoringClient.metric_descriptor_path(project_id, descriptor.type)
    try:
        monitoringClient.get_metric_descriptor(name=descriptor_path)
    except google.api_core.exceptions.NotFound:
        descriptor.metric_kind = kind
        descriptor.value_type = value_type
        if unit is not None: descriptor.unit = unit
        if description is not None: descriptor.description = description
        if display_name is not None: descriptor.display_name = display_name
        if launch_stage is not None: descriptor.launch_stage = launch_stage

        if labels is not None:
            for label_dict in labels:
                label = label_pb2.LabelDescriptor()
                label.key = label_dict["key"]
                label.value_type = label_dict["valueType"]
                label.description = label_dict["description"]
                descriptor.labels.append(label)

        # for monitored_resource_type in monitored_resource_types:
        #     descriptor.monitored_resource_types.append(monitored_resource_type)
        if monitored_resource_types is not None:
            descriptor.monitored_resource_types.extend(monitored_resource_types)

        project_name = f"projects/{project_id}"

        if not __ADVOBS_DRY_RUN:
            monitoringClient.create_metric_descriptor(
                name=project_name, metric_descriptor=descriptor
            )
