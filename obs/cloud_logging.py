import logging
import json

import google.cloud.logging

from logging import getLevelName

from google.cloud.logging_v2 import Resource

loggingClient = None

def setup_logging_client():
    global loggingClient
    loggingClient = google.cloud.logging.Client()
    loggingClient.setup_logging(log_level=logging.DEBUG)


class TimestampFilter(logging.Filter):
    """
    This is a logging filter which will check for a `timestamp` attribute on a
    given LogRecord, and if present it will override the LogRecord creation time
    (and msecs) to be that of the timestamp (specified as a time.time()-style
    value).
    This allows one to override the date/time output for log entries by specifying
    `timestamp` in the `extra` option to the logging call.
    """
    def filter(self, record):
        if hasattr(record, "logger__timestamp"):
            record.created = record.logger__timestamp
            record.msecs = (record.logger__timestamp % 1) * 1000
            del record.logger__timestamp
        return True


logger = logging.getLogger("googlecloud_adv_obs_queries")
logger.addFilter(TimestampFilter())


def submit_log_entry_text(level, message, when = None, labels = None, resource_type = None, resource_labels = None, other = None):

    if other is None:
        # otherwise default argument is mutable
        # https://stackoverflow.com/questions/41686829
        other = {}

    extra = {
        "labels": labels if labels is not None else {},
        "resource": Resource(
            resource_type if resource_type is not None else "global",
            resource_labels if resource_labels is not None else {},
        ),
        **other
    }

    if when is not None:
        extra["logger__timestamp"] = when

    logger.log(getLevelName(level), message, extra=extra)


def submit_log_entry_json(level, payload, when = None, labels = None, resource_type = None, resource_labels = None, other = None):
    submit_log_entry_text(level, json.dumps(payload), when, labels, resource_type, resource_labels, other)

