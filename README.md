# Observability Testing Tool for Google Cloud

A Python script to generate large quantities of log entries and metrics into
the Google Cloud Observability Suite. It can be used for

- **Training and education**
  
  It was successfully used in the _Advanced
Observability Querying in Google Cloud_ course in order to create the logs and
metrics used in the lab exercises.

- **Testing**
  
  It could be used to generate logs and metrics when testing expressions in LQL
  (Logging Query Language) for Logs Explorer, SQL for Log Analytics, and PromQL
  for Cloud Monitoring, as well as for generating live metrics and logs to test 
  Cloud Monitoring alerts and notifications. 

It can generate historical logs and metrics as well as live logs and metrics.

**Historical logs and metrics** are generated at a given frequency in bulk given
a start point and end point in time.
The timestamps of historical logs are limited to 30 days in the past and 1 day in the future (this is due
to [Google Logging infrastructure quotas and limits](https://cloud.google.com/logging/quotas#log-limits)). As far as the timestamps of historical metrics go, they are limited to max 25 hours in the past and 5 minutes in the future (also
due to [Google Monitoring infrastructure limits](https://cloud.google.com/monitoring/custom-metrics/creating-metrics#writing-ts)).

**Live logs and metrics** are instead generated between a given start point and end 
point in the future at the specified frequency. The application will keep on running until the 
given end time and generate logs and metrics live as specified at the configured intervals. 
This is particularly useful when testing alert and notification triggers.

## Set-up and Execution

- For set-up information and how to run the tool, [read here](SETUP.md).

## Getting Started

- For a guide on how to start using the tool quickly, [read here](GETSTARTED.md).

## Configuration Reference

- For a full reference to the configuration options, [read here](REFERENCE.md).

