# https://cloud.google.com/monitoring/docs/reference/libraries

# Imports the Cloud Monitoring client library
from google.cloud import monitoring_v3
from google.api import metric_pb2
from google.api import label_pb2

# Import getenv for access to environment variables, from where we will get
# the project ID for this application, stored in GOOGLE_CLOUD_PROJECT for the
# client libraries and used here to set up the metric
from os import getenv

# Import the standard Python time library to format timestamps in metrics
import time

# Retrieve an instance of the Metrics Service Client
client = monitoring_v3.MetricServiceClient()

# Prepare the timestamp interval
now = time.time()
seconds = int(now) # Integer part of time() is the number of seconds
nanos = int((now - seconds) * 10**9)
interval = monitoring_v3.TimeInterval(
    {"end_time": {"seconds": seconds, "nanos": nanos}}
)

# Create a data point for the timestamp interval
point = monitoring_v3.Point({"interval": interval, "value": {"double_value": 3.99}})

# Prepare a time series and all its attributes
series = monitoring_v3.TimeSeries()
series.metric.labels["store_id"] = "Pittsburgh"
series.resource.type = "gce_instance"
series.resource.labels["instance_id"] = "1234567890123456789"
series.resource.labels["zone"] = "us-central1-f"

# Add the data point to the series
series.points = [point]

# Submit the time series data
project_name = f"projects/{getenv('GOOGLE_CLOUD_PROJECT')}"
client.create_time_series(request={"name": project_name, "time_series": [series]})


# You need to create metric descriptors in order to provide details about metrics
# https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.metricDescriptors
# https://cloud.google.com/monitoring/api/ref_v3/rest/v3/LabelDescriptor
# https://cloud.google.com/monitoring/custom-metrics/creating-metrics#create-metric-desc
# Otherwise the metric will have a standard auto-inferred descriptor
# https://cloud.google.com/monitoring/custom-metrics/creating-metrics#auto-creation
# Not all combinations of kind and value type are possible in custom metrics
# https://cloud.google.com/monitoring/api/v3/kinds-and-types#kind-type-combos

descriptor = metric_pb2.MetricDescriptor()
descriptor.name = "my_metric"
descriptor.type = "custom.googleapis.com/advobv/queries/my_metric"
descriptor.metric_kind = "GAUGE"
descriptor.value_type = "DOUBLE"
descriptor.unit = "ms"
descriptor.description = "This is a my metric for the Advanced Observability Querying course."
descriptor.display_name = "My Metric"
# descriptor.launch_stage = "GA"
descriptor.monitored_resource_types.append("GA")

label = label_pb2.LabelDescriptor()
label.key = "my_label"
label.value_type = "STRING" # STRING, BOOL, INT64
label.description = "This is my label for the Advanced Observability Querying course."
descriptor.labels.append(label)

print()
