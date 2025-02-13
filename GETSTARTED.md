# [Observability Testing Tool for Google Cloud](README.md)

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

Let's take a look at a couple of examples.

> [!NOTE]
> Copy and paste the following snippets in a file called `config.obs.yaml` in the same
> folder where the Observability Testing Tool is.

To execute these scripts without consequence, add the `OBSTOOL_DRY_RUN=True` environment variable,
and also `OBSTOOL_DEBUG=1`, so that you can see the logs generated instead of the actual actions.

```shell
OBSTOOL_DEBUG=1 OBSTOOL_DRY_RUN=True python main.py
```

### Logging in the past

- Issue a warning log entry every 5 seconds for one minute starting 61 minutes ago.

    ```yaml
    loggingJobs:
      - frequency: "5s"
        startOffset: "- 1h 1m"
        endOffset: "-1h"
        logName: "application.log"
        level: "WARNING"
        textPayload: "Something bad is happening here"
    ```

- Issue error logs every 30 seconds to a minute starting on 1/1/2025 for 5 mins.

    ```yaml
    loggingJobs:
      - frequency: "30s ~ 1m"
        startTime: "2025-01-01T00:00:00"
        endOffset: "5m"
        logName: "application.log"
        level: "ERROR"
        textPayload: "An error has occurred"
    ```

- Bulk logs can also be in the future (max 24 hours)

    ```yaml
    loggingJobs:
      - frequency: "10m~50m"
        startOffset: "1h"
        endOffset: "7h"
        logName: "application.log"
        level: "INFO"
        textPayload: "A log starting an hour from now for the following 6 hours"
    ```

### Logging live

- Issue a critical log entry every 5 seconds for the next 2 minutes.

    ```yaml
    loggingJobs:
      - live: true
        frequency: "5s"
        endOffset: "2m"
        logName: "application.log"
        level: "CRITICAL"
        textPayload: "Critical log generated in real-time"
    ```
