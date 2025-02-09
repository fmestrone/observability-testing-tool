## Setup

- Make sure you are inside the top-level folder where the tool was downloaded

```bash
cd advobs-tool
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

- Create a service account for the application in Google Cloud IAM
- Add the Log Writer role to the service account
- Add the Monitoring Metric Writer role to the service account
- Generate a new JSON key for the service account

> [!TIP]
> The following two steps are not need if you set the `cloudConfig.project` and 
> `cloudConfig.credentials` properties in the configuration file for the tool.

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

## Configuration File

- `cloudConfig`
  - `project` the Google Cloud project that the tool will run against.
  - `credentials` the Google Cloud service account key used to authenticate and authorize the tool to send logs and metrics.

- `dataSources[]`
  - `type` one of "env", "list", "random", "gce-metadata", "fixed"
  - `value`
  - `range` for "random"

- `loggingJobs`
  - `live`
  - [timing](#timing-definition)
  - `textPayload` or `jsonPayload`
  - `level`
    - one of `DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY` for Cloud logging
    - one of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET` for native Python logging
  - variables

- `metricDescriptors`

- `monitoringJobs`
  - `live`
  - [timing](#timing-definition)
  - [variables](#variable-definition)`[]`

### Timing Definition

- `frequency`
- `startTime`
- `startOffset`
- `endTime`
- `endOffset`

### Variable Definition

- `name`
- `dataSource`
- `selector`
- `extractor`
- `index`
