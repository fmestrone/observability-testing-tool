# Observability Testing Tool for Google Cloud <sup>[📖](README.md)</sup>

## 🚀 Getting Started  

The **configuration file** defines the **jobs** that generate logs and metrics.  
Each **job** specifies:  
- **What** log entries or metric values to send  
- **How many** entries/values to generate  
- **How often** to submit them  

A **logging job** generates log entries, while a **monitoring job** generates metric values.  
You can also define **metric descriptors** to create new metrics before submitting data.  

Additionally, jobs can use **variables**, which are derived from **data sources** defined in the configuration.  

---

### 📄 Example Configurations  

> [!NOTE]
> Copy and paste the following snippets into a file called  
> `config.obs.yaml` in the same folder where the **Observability Testing Tool** is located.  

To execute these examples **without sending data** to Google Cloud, enable **dry-run mode** and **info logging**:

```shell
OBSTOOL_DEBUG=1 OBSTOOL_DRY_RUN=True python main.py
```

- `OBSTOOL_DRY_RUN=True` prevents actual log/metric submission and logs the intended actions instead.  
- `OBSTOOL_DEBUG=1` ensures that info logs are displayed — without it, no output would be shown, making the dry-run execution useless.

---

## ⏳ Logging in the Past  

### ⚠️ Issue a warning log entry every 5 seconds for 1 minute (starting 61 minutes ago)  

```yaml
loggingJobs:
  - frequency: "5s"
    startOffset: "- 1h 1m"
    endOffset: "-1h"
    logName: "application.log"
    level: "WARNING"
    textPayload: "Something bad is happening here"
```

### ❌ Issue error logs every 30 seconds to 1 minute (starting on 1/1/2025 for 5 mins)  

```yaml
loggingJobs:
  - frequency: "30s ~ 1m"
    startTime: "2025-01-01T00:00:00"
    endOffset: "5m"
    logName: "application.log"
    level: "ERROR"
    textPayload: "An error has occurred"
```

### 📅 Bulk logs can also be scheduled in the future (up to 24 hours ahead)  

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

### 🚨 Issue a critical log entry every 5 seconds for the next 2 minutes  

```yaml
loggingJobs:
  - live: true
    frequency: "5s"
    endOffset: "2m"
    logName: "application.log"
    level: "CRITICAL"
    textPayload: "Critical log generated in real-time"
```

