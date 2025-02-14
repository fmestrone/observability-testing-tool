# Observability Testing Tool for Google Cloud <sup>[📖](README.md)</sup>

> ⚠️ **Work in Progress**  
> This section is still being written. Check back soon for a complete reference on all configuration options!  

## Configuration File Reference

### Google Cloud Settings

- `cloudConfig` allows you to specify project and service account to use in Google Cloud.
  - `project` the Google Cloud project that the tool will run against.
  - `credentials` the Google Cloud service account key used to authenticate and authorize the tool to send logs and metrics.

### Data Sources

- `dataSources[]` lists the sources of data that can be used when generating log entries
or metric values. See the section on [data sources and variables](#data-sources-and-variables)
for more information.
  - `type` the type of data source. Can be one of "env", "list", "random", "gce-metadata", "fixed". Find out more in [this section](#data-source-types).
  - `value` represents the value that the data source will offer, but its meaning depends on the type of data source.
  - `range` for "random"

### Logging Jobs

- `loggingJobs[]`
  - `live`
  - [timing](#timing-definition)
  - `textPayload` or `jsonPayload`
  - `level`
    - one of `DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY` for Cloud logging
    - one of `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET` for native Python logging
  - [variables](#variable-definition)`[]`

### Metric Descriptors

- `metricDescriptors`

### Monitoring Jobs

- `monitoringJobs[]`
  - `live`
  - [timing](#timing-definition)
  - [variables](#variable-definition)`[]`

## Timing Definition

- `frequency`
- `startTime`
- `startOffset`
- `endTime`
- `endOffset`

## Data Sources and Variables

### Data Source Types

### Variable Definition

- `name`
- `dataSource`
- `selector`
- `extractor`
- `index`
