import logging
import json
import re
from os import getenv

import google.cloud.logging

from logging import getLevelName

from google.cloud.logging_v2 import Resource

__ADVOBS_DRY_RUN = (getenv("ADVOBS_DRY_RUN") == "True")

_regex_logname_format = re.compile(r"^projects/.+/logs/.+$")

loggingClient = None
usePythonLogging = False
logger = None

def setup_logging_client():
    if __ADVOBS_DRY_RUN: return
    global loggingClient, logger
    loggingClient = google.cloud.logging.Client()
    if usePythonLogging:
        loggingClient.setup_logging(log_level=logging.DEBUG)
        logger = logging.getLogger("googlecloud_adv_obs_logger")
        logger.addFilter(TimestampFilter())
    else:
        logger = loggingClient.logger("googlecloud_adv_obs_logger")


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


def submit_log_entry(level, message, when = None, labels = None, resource_type = None, resource_labels = None, log_name = None, other = None, payloadStyle = "text"):
    global logger

    if other is None:
        # otherwise default argument is mutable
        # https://stackoverflow.com/questions/41686829
        other = {}

    if usePythonLogging:

        # NB protoBuffer not supported in native logging
        if payloadStyle == "json" and isinstance(message, dict):
            message = json.dumps(message)
        elif (payloadStyle == "text") and not isinstance(message, str):
            message = str(message)
        if not isinstance(message, str):
            raise ValueError("Invalid message payload")

        extra = {
            "labels": labels if labels is not None else {},
            "resource": Resource(
                resource_type if resource_type is not None else "global",
                resource_labels if resource_labels is not None else {},
            ),
            **other
        }

        if when is not None:
            extra["logger__timestamp"] = when.timestamp()

        if not __ADVOBS_DRY_RUN:
            logger.log(getLevelName(level), message, extra=extra)

    else:

        if payloadStyle == "json" and not isinstance(message, dict):
            raise ValueError("Invalid JSON payload")
        if payloadStyle == "text" and not isinstance(message, str):
            raise ValueError("Invalid text payload")
        if payloadStyle == "proto" and not isinstance(message, dict) and message.get("@type") is None:
            raise ValueError("Invalid ProtoBuf payload")

        if log_name is None:
            log_name = "python"
        if not __ADVOBS_DRY_RUN and not _regex_logname_format.match(log_name):
            log_name = f"projects/{logger.project}/logs/{log_name}"

        metadata = {
            "log_name": log_name,
            "labels": labels,
            "severity": level.upper(),
            "timestamp": when,
            "resource": Resource(
                resource_type if resource_type is not None else "global",
                resource_labels if resource_labels is not None else {}
            ),
            **other
        }
        if not __ADVOBS_DRY_RUN:
            match payloadStyle:
                case "json":
                    logger.log_struct(message, **metadata)
                case "text":
                    logger.log_text(message, **metadata)
                case "proto":
                    logger.log_proto(message, **metadata)
                case _:
                    raise ValueError(f"Invalid payload type {payloadStyle}")


def submit_log_entry_json(level, payload, when = None, labels = None, resource_type = None, resource_labels = None, log_name = None, other = None):
    submit_log_entry(level, payload, when, labels, resource_type, resource_labels, log_name, other, payloadStyle="json")


def submit_log_entry_proto(level, payload, when = None, labels = None, resource_type = None, resource_labels = None, log_name = None, other = None):
    submit_log_entry(level, payload, when, labels, resource_type, resource_labels, log_name, other, payloadStyle="proto")
