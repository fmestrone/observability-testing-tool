# [Observability Testing Tool for Google Cloud](README.md)

## Setup

- Clone the Git project and make sure you are inside the top-level folder where the tool was downloaded

```bash
git clone https://github.com/fmestrone/observability-testing-tool.git
cd observability-testing-tool
```

- Create a python virtual environment for the tool and activate it

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

> [!IMPORTANT]
> Make sure your system is running Python v3.12 or later.

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

## Start-up Script

In the main folder of the tool, execute

`python main.py [config-file]`

If a file is not specified, the tool will look for `config.obs.yaml` in the current folder.

### Environment Variables

You can use the following environment variables when running the tool

- `OBSTOOL_DEBUG=n` enables more detailed logging to `stdout`
  - `0` means no logging apart from errors
  - `1` means `INFO` logs and errors
  - `2` means `DEBUG`, `INFO` and error logs

- `OBSTOOL_NO_GCE_METADATA=True` disables execution of GCE metadata endpoint when outside a GCE VM instance

- `OBSTOOL_DRY_RUN=True` executes the whole script without sending requests to Google Cloud, but logging to `stdout` instead - note that this also implies `OBSTOOL_NO_GCE_METADATA=True`, so metadata will not be queried in dry-run mode.

For example,

```shell
OBSTOOL_DEBUG=2 python main.py config.obs.yaml
```

```shell
OBSTOOL_DEBUG=1 OBSTOOL_DRY_RUN=True python main.py config.obs.yaml
```
