## Setup

- Create a service account for the application in Google Cloud IAM
- Add the Log Writer role to the service account
- Add the Monitoring Metric Writer role to the service account

### Outside of Google Cloud

- Generate a new JSON key
- Confgiure the client library project with the GOOGLE_CLOUD_PROJECT environment variable
- Make the key available to the application with the GOOGLE_APPLICATION_CREDENTIALS environment variable

## Start-up Script

In the main folder of the tool, execute

`python main.py [config-file]`

If a file is not specified, the tool will look for `config.yaml` in the current folder.

### Environment Variables

You can use the following environment variables when running the tool

`ADVOBS_DEBUG=True` enables more detailed logging to stdout
`ADVOBS_NO_GCE_METADATA=True` disables execution of GCE metadata endpoint when outside of a GCE VM instance
`ADVOBS_DRY_RUN=True` executes the whole script without sending requests to Google Cloud, but logging to stdout instead

## Configuration File

- `cloudConfig`
  - `project`
  - `credentials`

- `dataSources`[]
  - `type` one of "env", "list", "random", "gce-metadata", "fixed"
  - `value`
  - `range` for "random"

- `loggingJobs`
  - `live`
  - timings
  - `textPayload` or `jsonPayload`
  - `level`
    - one of `DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY` 
      for Cloud logging
    - one of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET` for native Python logging
  - variables

- `metricDescriptors`

- `monitoringJobs`
  - `live`
  - timings
  - variables


Timing definitions are as follows

- `frequency`
- `startTime`
- `startOffset`
- `endTime`
- `endOffset`

Variable definitions are a list of the following

- `name`
- `dataSource`
- `selector`
- `extractor`
- `index`

