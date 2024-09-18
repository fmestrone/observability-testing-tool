# https://cloud.google.com/python/docs/reference/logging/latest/std-lib-integration

# Imports the Cloud Logging client library
import google.cloud.logging

# Uses the standard Python logging library to generate logs
import logging
# Uses the standard Python JSON library to prepare JSON payloads
import json

from google.cloud.logging_v2 import Resource

# Instantiates a Cloud Logging client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the Python
# logging module. By default, this captures all logs at INFO
# level and higher, but here we set it to DEBUG and higher
client.setup_logging(log_level=logging.DEBUG)

# Emits the data using the standard logging module and
# will generate a textPayload in Cloud Logging
logging.warning("Hello, world!")

# To write JSON logs using the standard library integration, do one of the following:

# - Use the json_fields extra argument
logging.info("message field", extra={"json_fields": {"hello": "world"}})

# - Log a JSON-parsable string:
logging.info(json.dumps({"hello": "world"}))

# The Cloud Logging library attempts to detect and attach the
# following additional LogEntry fields:
# - labels
# - trace
# - span_id
# - trace_sampled
# - http_request
# - source_location
# - resource
# - json_fields

# You can set LogEntry fields manually with the extra parameter in the logging methods
my_labels = {"foo": "bar"}
res_labels = {"instance_id":"1234567890123456789", "zone":"us-central1-f"}
my_http = {"requestUrl": "localhost"}
my_trace = "01234"

logging.debug(
    "hello", extra={
        "labels": my_labels,
        "http_request": my_http,
        "trace": my_trace,
        "resource": Resource(type="gce_instance", labels=res_labels),
    }
)
