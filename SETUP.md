# Observability Testing Tool for Google Cloud <sup>[📖](README.md)</sup>

## ⚙️ Setup

### 1️⃣ Create a Virtual Environment

Set up a Python virtual environment for the tool and activate it:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

> [!IMPORTANT]
> Ensure your system is running Python 3.12 or later.

### 2️⃣ Install the Observability Testing Tool



### 3️⃣ Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## ☁️ Google Cloud Setup  

To send logs and metrics to Google Cloud, ensure proper authentication and provide adequate permissions.  

### 🔹 Cloud Shell

If running in **Google Cloud Shell**, verify that your account has the necessary roles:  
- **Logs Writer** (`roles/logging.logWriter`)  
- **Monitoring Metric Writer** (`roles/monitoring.metricWriter`)  

### 🔹 Compute Engine (GCE) / Kubernetes Engine (GKE)  

If running inside **GCE or GKE**, ensure the instance or pod identity has the required permissions.

### 🔹 Using a Service Account

Alternatively, you can authenticate using a **service account key**:  

1. **Create a service account** in **Google Cloud IAM**.  
2. **Assign roles**:  
   - `Logs Writer` (`roles/logging.logWriter`)
   - `Monitoring Metric Writer` (`roles/monitoring.metricWriter`)
3. **Generate a JSON key** for the service account.  
4. **Set environment variables**:

    ```bash
    export GOOGLE_CLOUD_PROJECT=<your-project-id>
    export GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account-key.json>
    ```

## 🚀 Running the Tool  

Run the tool from the main directory:  

```bash
# Using the installed CLI
obs-tool [config-file]

# Or using the script directly
python src/observability_testing_tool/main.py [config-file]
```

> [!NOTE]
> If no configuration file is specified, the tool defaults to using `config.obs.yaml` in the current folder.

## 🛠 Command-Line Options

The tool supports several command-line arguments:

- `-v`, `--verbose`: Increase output verbosity. Use `-v` for `INFO` logs and `-vv` for `DEBUG` logs.
- `--version`: Show the version of the tool.
- `-h`, `--help`: Show the help message.

## ⚙️ Environment Variables  

You can also customize execution with the following environment variables (command-line options take precedence):  

### 🔍 **Debug Logging**  

Enable different log levels for troubleshooting:  

- `OBSTOOL_DEBUG=0` → Errors only (default)  
- `OBSTOOL_DEBUG=1` → `INFO` logs + errors  
- `OBSTOOL_DEBUG=2` → `DEBUG` and `INFO` logs + errors  

### 🏗️ **Metadata & Dry-Run Mode**  

- `OBSTOOL_NO_GCE_METADATA=True` → Disables GCE metadata API checks (useful outside GCE)  
- `OBSTOOL_DRY_RUN=True` → Simulates execution without sending logs/metrics to Google Cloud  
  - _(Also implies `OBSTOOL_NO_GCE_METADATA=True`, so no metadata requests are sent in dry-run mode)_.  

#### ✅ Example Usage:

```bash
# Debug mode via CLI flag
obs-tool -vv config.obs.yaml
```

```bash
# Dry-run mode with info logging
OBSTOOL_DRY_RUN=True obs-tool -v config.obs.yaml
```

## 📌 Notes  
- Make sure your **Google Cloud project is set correctly** before running the tool.  
- For advanced configuration options, check the **[Configuration Reference](REFERENCE.md)**.  

---

📖 **Next Steps:**  
➡️ Follow the **[Quick Start Guide](START.md)** to begin using the tool right away!

---
