# Observability Testing Tool for Google Cloud <sup>[📖](README.md)</sup>

## 🚀 Getting Started  

The **configuration file** defines the **jobs** that generate logs and metrics.  
Each **job** specifies:  
- **What** log entries or metric values to send  
- **How many** entries/values to generate  
- **How often** to submit them  

A **logging job** generates log entries, while a **monitoring job** generates metric values.  
You can also define **metric descriptors** to explicitly create new metrics before submitting data.  

Additionally, jobs can use **variables**, which are derived from **data sources** defined in the configuration.  

---

### 📄 Example Configurations  

> [!NOTE]
> Copy and paste the following snippets into a file called  
> `config.obs.yaml` in the same folder where the **Observability Testing Tool** is located.  

To execute these examples **without sending data** to Google Cloud, enable **dry-run mode** and **info logging**:

```shell
# Using the installed CLI
obs-tool -v --dry-run config.obs.yaml

# Or using the script directly and environment variables
OBSTOOL_DRY_RUN=True OBSTOOL_DEBUG=1 python src/observability_testing_tool/main.py config.obs.yaml
```

- `--dry-run` prevents actual log/metric submission and logs the intended actions instead.  
- `-v` (info logging) or `-vv` (debug logging) ensures that logs are displayed — without it, no output would be shown for errors, making the execution less informative.

---

## ⏳ Logging in the Past  

### Issue a warning log entry every 5 seconds for 1 minute (starting 61 minutes ago)  

```yaml
loggingJobs:
  - frequency: "5s"
    startOffset: "- 1h 1m"
    endOffset: "-1h"
    logName: "application.log"
    level: "WARNING"
    textPayload: "Something bad is happening here"
```

### Issue error logs every 30 seconds to 1 minute (starting on 1/1/2025 for 5 mins)  

```yaml
loggingJobs:
  - frequency: "30s ~ 1m"
    startTime: "2025-01-01T00:00:00"
    endOffset: "5m"
    logName: "application.log"
    level: "ERROR"
    textPayload: "An error has occurred"
```

### Bulk logs can also be scheduled in the future (up to 24 hours ahead)  

```yaml
loggingJobs:
  - frequency: "10m~50m"
    startOffset: "1h"
    endOffset: "7h"
    logName: "application.log"
    level: "INFO"
    textPayload: "A log starting an hour from now for the following 6 hours"
```

---

## 🔴 Logging Live  

### Issue a critical log entry every 5 seconds for the next 2 minutes  

```yaml
loggingJobs:
  - live: true
    frequency: "5s"
    endOffset: "2m"
    logName: "application.log"
    level: "CRITICAL"
    textPayload: "Critical log generated in real-time"
```

### Issue a log entry with a random frequency between 45 secs and 90 secs starting in 5 minutes for 10 minutes

```yaml
loggingJobs:
  - live: true
    frequency: "45s ~ 1m30s"
    startOffset: "5m"
    endOffset: "15m"
    logName: "application.log"
    level: "CRITICAL"
    textPayload: "Critical log generated in real-time"
```

---

## 📦 Data Sources and Variables  

### Get the instance ID from GCE metadata, then use it within the JSON payload 

```yaml
dataSources:
  vmId:
    sourceType: "gce-metadata"
    value: "instance/id"
loggingJobs:
  - startOffset: "-5h"
    frequency: "45s"
    jsonPayload: {
      # Variable reference with {vmId}
      "message": "Invalid connection request to GCE instance {vmId}."
    }
    level: WARNING
    variables:
      # A variable with the same name as the data source and no config
      - "vmId"
```

### Generate a randon float value between 10 and 99, then use it as a simulated CPU load for a metric

```yaml
dataSources:
  cpuUsageValue:
    sourceType: "random"
    value: "float"
    range: "10.0~99.0"
monitoringJobs:
  - live: false
    startOffset: "-5h"
    frequency: "15s"
    metricType: "advobv/queries/python_app_count"
    resourceType: "gce_instance"
    resourceLabels:
      instance_id: "1234567890"
      zone: "us-central1-a"
    metricValue: "{cpuUsageValue}"
    variables:
      # A variable with the same name as the data source and no config
      - "cpuUsageValue"
```

### Provide a list of IP addresses, then use them at random in your log entries

```yaml
dataSources:
  someIpAddresses:
    sourceType: "list"
    value:
      - 192.168.0.1
      - 192.168.0.12
      - 192.168.0.13
      - 192.168.0.14
      - 192.168.0.15
      - 192.168.0.17
      - 192.168.0.19
      - 192.168.0.3
      - 192.168.0.31
      - 192.168.0.33
      - 192.168.0.35
      - 192.168.0.39
loggingJobs:
  - startOffset: "-5h"
    frequency: "45s"
    jsonPayload: {
      # Variable reference with {ip}
      "message": "Invalid connection request from {ip}."
    }
    level: WARNING
    variables:
      # A variable called "ip" that gets data from the "someIpAddress" source and picks any random item from the list
      - name: "ip"
        dataSource: "someIpAddresses"
        selector: "any"
```

### Get the fully qualified metadata for the GCE instance zone, then extract the simple name in the variable

The GCE metadata for the instance zone is in the format _/projects/\<project-id\>/zones/\<zone-id\>_, but in resource labels for log entries and metrics, only the simple name is expected. We can use the `extract` attribute of a variable to apply a regular expression to it with a single capturing group to extract the desired information. 

```yaml
dataSources:
  vmZone:
    sourceType: "gce-metadata"
    value: "instance/zone"
loggingJobs:
  - startOffset: "-5h"
    frequency: "45s"
    textPayload: "Critical log generated in real-time"
    level: WARNING
    variables:
      # A variable called "vmZone" that gets data from a source with the same name and extracts a part of it
      - name: "vmZone"
        extractor: "/zones/([a-z0-9\\-]+)$"
```

### Send a selection of log entries from a list of levels and messages

```yaml
dataSources:
  cnxlogs:
    sourceType: "list"
    value:
      - ["CRITICAL", "Too many denied attempts from"]
      - ["INFO", "Access succeeded from"]
      - ["WARNING", "Access failed from"]
  ips:
    sourceType: "list"
    value:
      - "111.144.187.212"
      - "233.142.26.173"
      - "65.44.51.196"
      - "229.15.109.233"
      - "210.34.246.74"
      - "136.250.243.161"
      - "83.8.35.71"
loggingJobs:
  - startOffset: "-5h"
    frequency: "45s"
    # if variable value is an array or object, you can use square bracket to access a key or index
    textPayload: "{cnxlogs[1]} {ip}"
    level: "{cnxlogs[0]}"
    variables:
      - name: "ip"
        # if variable name is different to data source name, specify the data source name
        dataSource: "ips"
        selector: "any"
      - name: "cnxlogs"
        selector: "any"
```
