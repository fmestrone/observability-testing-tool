import logging
import json

import google.cloud.logging

from logging import getLevelName

from google.cloud.logging_v2 import Resource

client = google.cloud.logging.Client()
client.setup_logging(log_level=logging.DEBUG)

logger = logging.getLogger("googlecloud_adv_obs_queries")

def submit_log_entry_text(level, message, labels = None, resource_type = None, resource_labels = None, other = None):
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

    logger.log(getLevelName(level), message, extra=extra)

def submit_log_entry_json(level, payload, metrics_labels = None, resource_type = None, resource_labels = None, other = None):
    submit_log_entry_text(level, json.dumps(payload), metrics_labels, resource_type, resource_labels, other)

