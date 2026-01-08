# Observability Testing Tool for Google Cloud  

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=yellow)  ![License](https://img.shields.io/github/license/fmestrone/observability-testing-tool)  ![GitHub Stars](https://img.shields.io/github/stars/fmestrone/observability-testing-tool?style=social)  ![GitHub Issues](https://img.shields.io/github/issues/fmestrone/observability-testing-tool)

Easily generate bulk logs and metrics in Google Cloud Operations Suite to test alerts, validate queries, and simulate real-world observability scenarios.

## 🚀 Use Cases  

This Python-based tool is designed for:  

### **Training & Education**

Successfully used in the _Advanced Observability Querying in Google Cloud_ course, it helps create logs and metrics for hands-on labs and classroom demos.  

### **Testing & Validation**  

Use it to:  

- Simulate logs and metrics when testing expressions for Logs Explorer with **Logging Query Language** (LQL), for **Log Analytics** with SQL, and for Cloud Monitoring with **PromQL**.

- Generate real-time live data to test Cloud Monitoring **alerts and notifications**. 

---

## ⚡ Generate Historical or Live Data  

The tool supports two data generation modes, that can be mixed within the same run.

### 📜 **Historical Logs & Metrics**  

- Bulk-generate logs and metrics for a past time window.  


- **Limits:**  
  - _Google Cloud quotas apply: [Logging Limits](https://cloud.google.com/logging/quotas#log-limits), [Monitoring Limits](https://cloud.google.com/monitoring/custom-metrics/creating-metrics#writing-ts)_.
  
  - Logs: Up to **30 days in the past** and **1 day in the future**.  

  - Metrics: Up to **25 hours in the past** and **5 minutes in the future**.  
  

### ⏳ **Live Logs & Metrics**  

- Continuously generate logs and metrics between a **future start and end time**.

- The tool runs **until the specified end time**, creating data at the configured intervals.  

- **Ideal for testing alerts and notifications** in real-time.  

---

## 📖 Documentation  

🔹 **[Set Up & Install](SETUP.md)** – Installation guide.  
🔹 **[Quick Start](START.md)** – Jump into usage examples.  
🔹 **[Configuration Reference](REFERENCE.md)** – Full list of options.  

---

### 🛠 Contributing 

Feel free to open an issue or submit a PR if you have ideas for improvement!  

---
