# https://cloud.google.com/monitoring/docs/reference/libraries

# Imports the Cloud Monitoring client library
from google.cloud import monitoring_v3

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
series.metric_kind = "GAUGE"
series.metric.type = "custom.googleapis.com/my_metric"
series.metric.labels["store_id"] = "Pittsburgh"
series.resource.type = "gce_instance"
series.resource.labels["instance_id"] = "1234567890123456789"
series.resource.labels["zone"] = "us-central1-f"

# Add the data point to the series
series.points = [point]

# Submit the time series data
project_name = f"projects/{getenv('GOOGLE_CLOUD_PROJECT')}"
client.create_time_series(request={"name": project_name, "time_series": [series]})
