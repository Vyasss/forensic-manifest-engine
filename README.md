# Forensic Manifest: Verifiable AI-Generated Content (AIGC) Forensics Engine

([https://img.shields.io/badge/Status-Developing-yellow.svg](https://www.google.com/search?q=https://img.shields.io/badge/Status-Developing-yellow.svg))]([https://github.com/Vyasss/forensic-manifest-engine](https://github.com/Vyasss/forensic-manifest-engine))
([https://img.shields.io/badge/License-MIT-blue.svg](https://www.google.com/search?q=https://img.shields.io/badge/License-MIT-blue.svg))](LICENSE)

**Forensic Manifest** is an advanced, multi-modal digital evidence platform engineered to solve the rapidly escalating threat of AI-driven financial fraud across high-volume commerce sectors. Our core mission is to move beyond simple, vulnerable classification models to establish a **verifiable forensic reasoning engine** that generates high-integrity proof necessary for automated, high-stakes commercial decision-making.

The system is designed to serve as a crucial, trusted oracle, generating cryptographically durable evidence that ensures financial integrity and prevents fraudulent refund claims across e-commerce, food delivery, and logistics platforms.

## Problem Solved: Mitigating Refund Fraud in High-Volume Commerce

E-commerce and delivery companies face significant financial losses due to malicious actors leveraging generative AI to submit fraudulent refund requests. This fraud is executed through two sophisticated methods:

1.  **Fabricated Evidence:** Using AI to generate highly realistic, synthetic images of damaged goods, broken packaging, or spoiled food, mimicking genuine proof of loss.
2.  **Forensic Trace Destruction:** Submitting these fraudulent images through highly lossy compression channels (e.g., low-resolution uploads, messaging apps) to intentionally obscure the subtle forensic artifacts left by the generative process.

Current reactive detection systems, which rely on single-point analysis, are consistently defeated by this combination of high-quality synthesis and malicious degradation. **Forensic Manifest** directly counters this threat by providing an indisputable, evidence-based assessment of the media's authenticity.

## Unique Innovation: Architecting Verifiable Trust

To counter sophisticated, AI-driven fraud, **Forensic Manifest** leverages a convergence of state-of-the-art AI and forensic science. We prioritize transparency and reliability to ensure every piece of evidence is justifiable and auditable.

| Feature | Scientific Mechanism | Strategic Value for E-commerce |
| :--- | :--- | :--- |
| **VLM-Driven Interpretability** | Integration of **Vision-Language Models (VLMs)** (e.g., `gemini_vlm.py`) to generate contextual, natural-language explanations of forgery traces.[1, 2] | Converts a technical finding into a definitive, auditable, and human-readable reason for justifying a refund decision. |
| **Multi-Modal Forensic Fusion** | Combines both classical and modern forensic techniques (PRNU analysis, ELA, and Frequency Analysis) to identify a wider spectrum of manipulation artifacts.[1, 3] | Enhances the system's ability to resist common adversarial compression and destruction of forensic signals.[4] |
| **Semantic Grounding & Traceability** | A VLM-guided mechanism that maps localized, machine-detected anomalies to human-interpretable concepts (e.g., "Implausible texture consistency" or "Unnatural edge transitions").[5, 6] | Provides the transparent traceability required for internal auditing, policy enforcement, and formal dispute resolution. |
| **C2PA Assertion Generation** | Designed to package forensic findings into a cryptographically signed **C2PA Assertion**, ensuring the evidence of forgery is tamper-evident.[7, 8] | Creates legally durable evidence, reducing corporate liability and building trust in automated refund decisions. |

## Project Status: Developing (Focus on Robustness)

**Forensic Manifest** is currently in the active development phase. The architectural core, which includes multi-modal forensic fusion and VLM-based reasoning, is established and being optimized.

The immediate roadmap is heavily focused on achieving **extreme robustness** and scientific generalizability. We are actively refining the feature extraction and reasoning protocols to ensure the system can reliably distinguish subtle AI artifacts from the common noise introduced by low-resolution uploads and lossy compression—the primary challenge for this high-volume fraud detection scenario.[5]

## Technology Stack and File Structure

The project utilizes a high-performance Python environment structured for scalability and maintainability, separating core logic into distinct service and analysis layers.

| Category | Module/Tool | Purpose |
| :--- | :--- | :--- |
| **AI Reasoning Core** | `ai/gemini_vlm.py` | Implementation of the Vision-Language Model (VLM) for semantic grounding and transparent reasoning generation. |
| **Forensic Fusion** | `forensics/prnu_analyzer.py` | Photo Response Non-Uniformity (PRNU) analysis module. |
| **Forensic Fusion** | `forensics/ela_analyzer.py` | Error Level Analysis (ELA) module for detecting re-saving and tampering. |
| **Forensic Fusion** | `forensics/frequency_analyzer.py` | High-frequency signal analysis to detect generative model artifacts. |
| **API Framework** | `main.py`, `schemas.py`, `services.py` | FastAPI application for high-throughput, asynchronous service hosting (ASGI). |
| **Interface/Deployment** | Uvicorn, Gradio, Python `venv` | High-performance ASGI server, rapid prototyping UI, and isolated environment management. |

### File Structure Overview

.
├──.gitignore
├── requirements.txt
├── app/
│   ├── ai/
│   │   └── forensics/
│   │       ├── ela\_analyzer.py
│   │       ├── frequency\_analyzer.py
│   │       ├── prnu\_analyzer.py
│   │   └── gemini\_vlm.py
│   ├── main.py
│   ├── schemas.py
│   └── services.py
├── Frontend/
├── data/
└── venv/

````

-----

## About the Author

**Forensic Manifest** was conceptualized and developed by:

**Chetan Vyas**

[Connect with me on LinkedIn]

-----

## Getting Started

### Prerequisites

*   Python 3.9+
*   Uvicorn (ASGI server)

### 1\. Environment Setup

```bash
# 1. Create and activate the virtual environment
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# 2. Install dependencies (requires Uvicorn for deployment)
pip install -r requirements.txt
pip install "uvicorn[standard]"
````

### 2\. Running the Server

To run the application and expose it to your local network for internal testing and rapid iteration, use the `0.0.0.0` host binding:

```bash
# Run the application:
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Accessing the Application:**

To test on a mobile device or separate machine (on the same Wi-Fi network):

1.  Determine your computer's local IP address (e.g., `192.168.1.100`).
2.  Open the browser on the testing device:
      * **Frontend:** `http://<Your_Local_IP>:8000`
      * **API Docs:** `http://<Your_Local_IP>:8000/docs`

<!-- end list -->

```
```