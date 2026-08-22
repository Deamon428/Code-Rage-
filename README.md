# 🔥 CodeRage: Multi-Agent Code Review & Debugger

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini SDK](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Judge0 API](https://img.shields.io/badge/Judge0-Self--Healing-green.svg)](https://ce.judge0.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

> **"Your bugs aren't ready for this review."**

An intelligent, multi-agent web application designed for students and developers to **debug code**, extract root causes, compile-test and self-heal patches via **Judge0 API**, and receive **savage code roasts** alongside **strict 3-bullet-point pedagogical breakdowns**.

Built with **Python**, **Streamlit**, and **Google Gemini SDK**, supporting **Python**, **C++**, and **Java**.

---

## ⚡ The 5-Step CodeRage Pipeline

1. 🔍 **Diagnose (Parser Agent)**: Localizes exact bug lines, classifies error types (Runtime, Logic, Memory Safety, Syntax), and analyzes syntax/AST patterns.
2. 🔧 **Repair (Fixer Agent)**: Produces clean, idiomatic, and production-grade code patches with unified diff comparisons and complexity analysis.
3. 🧪 **Verify (Judge0 Self-Healing)**: Automatically compiles and executes candidate code patches on the free public Judge0 API (`MAX_RETRIES = 2`) with iterative error feedback.
4. 🔥 **Roast (Tutor Agent)**: Brutally roasts $O(n^2)$ complexity, memory leaks, terrible variable names (`x`, `temp`), and missing edge cases.
5. 🧠 **Learn (Tutor Agent)**: Formulates a **strict 3-bullet-point root cause explanation** (Trigger, Mechanism, Golden Rule), Core CS Concept card, and an Interactive Concept Quiz.

---

## 🌟 Key Features

- 🐙 **GitHub Ingestion Engine**:
  - Ingest code directly from GitHub URLs (direct file links or repository root exploration via GitHub REST API).
  - Strict HTTP 404 (Not Found) & HTTP 403 (Rate Limit) exception handling rendered cleanly in the UI.
  - Automatic language detection from file extensions (`.py`, `.cpp`, `.java`).

- 🧪 **Self-Healing Compiler Loop (Judge0 API)**:
  - Free public **Judge0 API** integration (`https://ce.judge0.com`).
  - Iterative self-healing error correction loop up to `MAX_RETRIES = 2`.

- 🔥 **"Roast My Code" Tutor Mode**:
  - Gordon Ramsay / Linus Torvalds CS reviewer persona.
  - Savage, witty roasts followed by structured 3-bullet educational feedback.

- 🎨 **Modern Dark-Mode UI**: Sleek glassmorphism cards, glowing status pills, neon accents, unified diff viewer, and responsive layout.
- 🧪 **1-Click Bug Presets**: Pre-loaded real-world student bugs across Python, C++, and Java for instant demo and evaluation.
- 💾 **Exportable Reports**: Download full debug and code review reports in structured Markdown (`.md`) or JSON (`.json`).

---

## 🤖 Multi-Agent Architecture

```mermaid
flowchart TD
    subgraph Ingestion [Code Ingestion Stage]
        GH[🐙 GitHub URL Ingestion] --> Editor[Code Text Area]
        Preset[🧪 1-Click Presets] --> Editor
        Manual[💻 Manual Input] --> Editor
    end

    subgraph Pipeline [5-Step Multi-Agent Self-Healing Loop]
        Editor --> P[🔍 1. Diagnose: Parser Agent AST & Scope Localization]
        P --> F[🔧 2. Repair: Fixer Agent Code Synthesis]
        F --> J[🧪 3. Verify: Judge0 Compilation & Test Execution]
        J -->|Compilation / Runtime Error & Retries < 2| Retry[Feed error back to Fixer]
        Retry --> F
        J -->|Passed OR Retries >= 2| T1[🔥 4. Roast: Savage Code Roast]
        T1 --> T2[🧠 5. Learn: 3-Bullet Root Cause & Concept Check]
    end

    subgraph Dashboard [Interactive Dark Dashboard]
        T2 --> Tab1[🔥 Savage Roast & 🎓 3-Bullet Tutor Review]
        J --> Tab2[🛠️ Fixed Code & 🧪 Judge0 Timeline & Diff]
        P --> Tab3[🔍 Parser AST Diagnostics]
        Dashboard --> Tab4[📥 Markdown / JSON Export]
    end

    Ingestion --> Pipeline
    Pipeline --> Dashboard
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/coderage.git
cd coderage
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Gemini API Key (Optional)
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash
```
> **Note:** If no API key is provided, the app runs in built-in offline simulation mode with rich diagnostic presets.

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment

```bash
docker-compose up --build -d
```
Access the app at `http://localhost:8501`.

---

## 📂 Project Structure

```
.
├── .streamlit/
│   └── config.toml          # Streamlit theme & dark mode configuration
├── agents/
│   ├── __init__.py          # Agent exports
│   ├── base.py              # Base Gemini SDK client & error fallback
│   ├── parser.py            # 🔍 Diagnose: Parser Agent (Bug extraction & classification)
│   ├── fixer.py             # 🔧 Repair: Fixer Agent (Clean patches & self-healing feedback)
│   ├── tutor.py             # 🔥 Roast & 🧠 Learn: Tutor Agent (Savage Roast & 3-bullet root cause)
│   └── orchestrator.py      # Multi-agent orchestrator with Judge0 verification (MAX_RETRIES = 2)
├── data/
│   └── sample_presets.py    # Pre-configured buggy codes across Python, C++, Java
├── utils/
│   ├── __init__.py          # Utils exports
│   ├── github_fetcher.py    # GitHub file & repo contents ingestion with 404/403 guards
│   ├── judge0_client.py     # 🧪 Verify: Free Judge0 API compilation client & test runner
│   └── ui_helpers.py        # Dark mode CSS, diff renderer, roast cards & report exporters
├── .env.example             # Environment variables template
├── Dockerfile               # Production Docker container definition
├── docker-compose.yml       # Docker compose setup
├── requirements.txt         # Project dependencies
├── app.py                   # Main Streamlit web application
└── README.md                # Comprehensive documentation
```

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.
