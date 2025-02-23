# Observability Testing Tool for Google Cloud <sup>[📖](README.md)</sup>

## ⚙️ Setup

### 1️⃣ Clone the Repository

First, clone the project and navigate to the tool's top-level folder:  

```bash
git clone https://github.com/fmestrone/observability-testing-tool.git
cd observability-testing-tool
```
### 2️⃣ Create a Virtual Environment

Set up a Python virtual environment for the tool and activate it:

```bash
python3 -m venv .venv
source ./.venv/bin/activate
```

> [!IMPORTANT]
> Ensure your system is running Python 3.12 or later.

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
python main.py [config-file]
```

> [!NOTE]
> If no configuration file is specified, the tool defaults to using `config.obs.yaml` in the current folder.

## 🛠 Environment Variables  

You can customize execution with the following environment variables:  

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
OBSTOOL_DEBUG=2 python main.py config.obs.yaml
```

```bash
OBSTOOL_DEBUG=1 OBSTOOL_DRY_RUN=True python main.py config.obs.yaml
```

## 📌 Notes  
- Make sure your **Google Cloud project is set correctly** before running the tool.  
- For advanced configuration options, check the **[Configuration Reference](REFERENCE.md)**.  

---

📖 **Next Steps:**  
➡️ Follow the **[Quick Start Guide](START.md)** to begin using the tool right away!

---
