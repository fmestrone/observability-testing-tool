# 🚀 TODO  

This page tracks planned features, improvements, and completed tasks for the **Observability Testing Tool**.  
Although primarily for internal use, it is publicly accessible.  

---

## 📝 Planned Features  

### ➤ **Add step in float range**  
🔹 Float ranges do not exist in core Python, so this functionality would need to be implemented manually.  
🔹 Currently, the only use of float ranges in **Obs Test Tool** is for generating a **random float** between a start and end value — this does not support steps.  

### ➤ **Add step in duration**  
🔹 Define values at regular intervals between **Time A and Time B**.  
🔹 This is **already possible** using `startOffset`, `endOffset`, and `frequency`, so it would mainly serve as a shortcut when **random frequency** is **not** needed.  

### ➤ **Conform to Schema Store requirements**  
🔹 Ensure compliance with [Schema Store Contribution Guidelines](https://github.com/SchemaStore/schemastore/blob/master/CONTRIBUTING.md).  

### ➤ **Package for PIP**  
🔹 Package the tool for **easier installation via PIP**.  
🔹 If possible, provide an **executable** to minimize setup effort.  

### ➤ **Add a fallback property for GCE metadata data source**  
🔹 When running without metadata connection () or in dry-run mode (`OBSTOOL_DRY_RUN=True`), this property allows to specify a fallback value to provide.

### ➤ **Add Error Reporting support to logging**

🔹 Simplify the creation of log entries that would be picked up by Error Reporting. Follow [these guidelines](https://cloud.google.com/error-reporting/docs/formatting-error-messages)

---

## 🚧 In Progress  

🔹 _Nothing here at the moment._  

---

## ✅ Completed  

### **➤ Add schema information for `config.obs.yaml`**  
🔹 Implemented schema definitions for improved validation and autocompletion.  

🔗 **References:**  
- [Boost your YAML with autocompletion and validation](https://medium.com/@alexmolev/boost-your-yaml-with-autocompletion-and-validation-b74735268ad7)  
- [JSON Schema: Getting Started](https://json-schema.org/learn/getting-started-step-by-step)  
- [JSON Schema Examples](https://json-schema.org/learn/json-schema-examples#device-type) _(useful for defining "timings" in both logging and monitoring jobs)_  
