# Google Cloud Advanced Observability Testing Tool

A Python script to generate large quantities of log entries and metrics into
the Google Cloud Observability Suite. It can be used for


- **Training and education**
  
  It was successfully used in the _Advanced
Observability Querying in Google Cloud_ course in order to create the logs and
metrics used in the lab exercises.


- **Testing**
  
  It could be used to generate logs and metrics when testing expressions in LQL
  (Logging Query Language) for Logs Explorer, SQL for Log Analytics, and PromQL
  for Cloud Monitoring, as well as testing notifications and alerting conditions. 


It can generate historical logs and metrics as well as live logs and metrics.

**Historical logs and metrics** are generated at a given frequency in bulk given
a start point and end point in time.
The timestamps of historical logs are limited to 30 days in the past and 1 day in the future (this is due
to [Google Logging infrastructure quotas and limits](https://cloud.google.com/logging/quotas#log-limits)). As far as the timestamps of historical metrics go, they are limited to max 25 hours in the past and 5 minutes in the future (also
due to [Google Monitoring infrastructure limits](https://cloud.google.com/monitoring/custom-metrics/creating-metrics#writing-ts)).

**Live logs and metrics** are instead generated between a given start point and end 
point in time in the future at the specified frequency, but they are generated at the time when 
they are due to be sent and will bear the timestamp of generation. Live 
configurations are particularly useful when testing alerts and triggers.

## Setup

- Clone the Git project and make sure you are inside the top-level folder where the tool was downloaded

```bash
git clone https://github.com/fmestrone/advanced-observability-testing-tool.git
cd advanced-observability-testing-tool
```

- Create a python virtual environment for the tool and activate it

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

- Install the application requirements

```bash
pip install -r requirements.txt
```

## Google Cloud Setup

If running the tool in the Cloud Shell, make sure that you are authorized
to write logs and metrics (you must have the Logs Writer and Monitoring Metric Writer 
roles or equivalent permissions).

If running the tool inside GCE or GKE, make sure that those roles (or
equivalent permissions) are available to the identity running your
GCE instance on the environment.

Alternatively, you can use service account keys:

- Create a service account for the application in Google Cloud IAM
- Add the Logs Writer role to the service account
- Add the Monitoring Metric Writer role to the service account
- Generate a new JSON key for the service account
- Configure the client library project with the `GOOGLE_CLOUD_PROJECT` environment variable
- Make the key available to the application with the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## Python Version

Please make sure you use Python v3.12 - this solves an issue with formatted strings that contain
quotes inside quotes of the same type in a formatted field. The code can easily be adjusted to work
with older versions, but for now just make sure that you use a version from 3.12 onwards.

## Start-up Script

In the main folder of the tool, execute

`python main.py [config-file]`

If a file is not specified, the tool will look for `config.yaml` in the current folder.

### Environment Variables

You can use the following environment variables when running the tool

`ADVOBS_DEBUG=n` enables more detailed logging to stdout - 0 means no logging apart from errors, 1 means INFO logs, and 2 means DEBUG logs
`ADVOBS_NO_GCE_METADATA=True` disables execution of GCE metadata endpoint when outside a GCE VM instance
`ADVOBS_DRY_RUN=True` executes the whole script without sending requests to Google Cloud, but logging to `stdout` instead

## Getting Started

The configuration file describes the jobs that will generate logs and metrics. Each
**job** describes what and how many log entries or metrics values should be
submitted to Google Cloud and with what frequency.

A **logging job** specifies logging entries, while a **monitoring job** 
specifies metrics. You can also provide a metric description to define
new metrics before monitoring jobs submit time series values for them.

When configuring your jobs and the values that they submit, you can also
use **variables**. Variables are taken from the **data sources** that you can
declare in your configuration.

Let's take a look at a couple of examples - call these files `config.yaml` in
the same folder where the tool is installed.

```yaml
loggingJobs:

```

### Configuration File Reference

#### Google Cloud Settings

- `cloudConfig` allows you to specify project and service account to use in Google Cloud.
  - `project` the Google Cloud project that the tool will run against.
  - `credentials` the Google Cloud service account key used to authenticate and authorize the tool to send logs and metrics.

#### Data Sources

- `dataSources[]` lists the sources of data that can be used when generating log entries
or metric values. See the section on [data sources and variables](#data-sources-and-variables)
for more information.
  - `type` the type of data source. Can be one of "env", "list", "random", "gce-metadata", "fixed". Find out more in [this section](#data-source-types).
  - `value` represents the value that the data source will offer, but its meaning depends on the type of data source.
  - `range` for "random"

#### Logging Jobs

- `loggingJobs[]`
  - `live`
  - [timing](#timing-definition)
  - `textPayload` or `jsonPayload`
  - `level`
    - one of `DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY` for Cloud logging
    - one of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET` for native Python logging
  - [variables](#variable-definition)`[]`

#### Metric Descriptors

- `metricDescriptors`

#### Monitoring Jobs

- `monitoringJobs[]`
  - `live`
  - [timing](#timing-definition)
  - [variables](#variable-definition)`[]`

### Timing Definition

- `frequency`
- `startTime`
- `startOffset`
- `endTime`
- `endOffset`

### Data Sources and Variables

#### Data Source Types

#### Variable Definition

- `name`
- `dataSource`
- `selector`
- `extractor`
- `index`
