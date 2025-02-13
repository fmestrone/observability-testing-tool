# Observability Testing Tool for Google Cloud

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

To execute these scripts


```yaml
loggingJobs:

```

