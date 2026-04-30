# 🚀 Financial Agents Project

**Lightweight Research-to-Execution AI System for Financial Simulations**

---

## 🧠 What Is This?

Imagine a **mini AI trading firm** running on your laptop.

This project builds a **multi-agent system** where each AI agent has a role:

- 🔍 **Research** stocks
- 📊 **Analyze** signals
- 🧮 **Manage** portfolios
- 🤝 **Reach** consensus
- ⚙️ **Execute** trades (simulated)

All coordinated through a central **orchestrator** and visualized in a real-time **dashboard**.

---

## ✨ Key Features

- 🧩 **Modular** multi-agent architecture
- 🧠 **Specialized** agents (research, analysis, execution)
- 🔄 **Orchestrated** end-to-end workflow
- 📈 **Live** market simulation (Observer agent)
- 🖥️ **Interactive** Streamlit dashboard
- 🔌 **API-ready architecture** (FastAPI can be integrated as a backend layer)
- 🛡️ **Built-in** guardrails & audit logging

---

## 🏗️ Architecture Overview

```
                 ┌──────────────────────────────┐
                 │     Streamlit Dashboard      │
                 │   (Interactive UI Layer)     │
                 └──────────────┬───────────────┘
                                │
               ┌────────────────┴───────────────┐
               │                                │
        ┌───────────────┐              ┌────────────────┐
        │    Agents     │              │ Orchestrators  │
        │───────────────│              │────────────────│
        │ Researcher    │              │ Base Orchestrator
        │ Analyst       │              │ Extended (HITL)
        │ Portfolio     │              └────────────────┘
        │ Observer      │
        │ Consensus     │
        └───────────────┘
                │
        ┌──────────────────────────────┐
        │ Data • Tools • Guardrails    │
        │ Market APIs • Execution      │
        └──────────────────────────────┘
```

---

## 🧩 Core Components

### 🤖 Agents (`agents/`)

| Agent | Role |
|-------|------|
| `analyst.py` | Generates trading signals |
| `researcher.py` | Deep company + risk analysis |
| `portfolio.py` | Portfolio rebalancing |
| `observer_agent.py` | Live market streaming |
| `consensus.py` | Multi-agent decision making |

### ⚙️ Orchestrators

| File | Description |
|------|-------------|
| `orchestrator.py` | Core execution pipeline |
| `orchestrator_extended.py` | HITL + MCP-ready orchestration |

### 🖥️ UI & API

| File | Description |
|------|-------------|
| `streamlit_app.py` | Interactive dashboard |
| `demos/start_api.py` | Alternative Streamlit-based interface (API-style demo) |

### 🧱 Supporting Layers

- `modules/` → Data feeds & signals
- `tools/` → Execution + market APIs
- `security/` → Guardrails
- `audit/` → Full audit trail

### 📂 Data & Demos

- `data/` → Sample datasets
- `demos/` → Pre-built workflows

---

## 🎯 How It Works

### 3-Step Flow

**1️⃣ Choose an Agent**

Pick from sidebar:
- Analyst
- Researcher
- Portfolio Manager
- Consensus
- Orchestrator

**2️⃣ Enter Prompt**

Example:
```
Analyze AAPL stock and generate a trading signal
```

**3️⃣ Click Run**

Get:
- ✅ Response
- 🔍 Debug logs (optional)
- 📊 Structured output

---

## ⚡ Example Prompts

### 🔍 Researcher
```
Research AAPL. Summarize performance, list risks, give BUY/HOLD/SELL with confidence.
```

### 📊 Analyst
```
Analyze AAPL price data. Return signal + rule + confidence.
```

### 🧮 Portfolio Manager
```
Portfolio: AAPL 40%, MSFT 30%, CASH 30%.
Rebalance to equal weights.
```

### ⚙️ Orchestrator (Full Pipeline)
```
Run full pipeline for AAPL with $1000 limit and return summary.
```

### 📡 Observer (Live Stream)
1. Enter symbol → `AAPL`
2. Click **Start Observer**
3. Click **Show Observations**

---

## ⚡ Quick Start (5 Minutes)

### ✅ Prerequisites
```powershell
python --version  # >= 3.8
```

### 🧱 Setup
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 📦 Install
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 🚀 Run Dashboard
```powershell
streamlit run streamlit_app.py
```

👉 Open: http://localhost:8501

---

## 🔌 Other Ways to Run

### CLI Execution
```powershell
python orchestrator.py
define something like below in the file
if __name__ == "__main__":
    o = Orchestrator()
    order = {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 10,
        "price": 100
    }
    print(o.execute(order))
```

### Streamlit UI (another dashboard)
```powershell
streamlit run demos/start_api.py
```

### Demo Scripts
```powershell
python demos/run_full_demo.py
python demos/run_execution_demo.py
```

---

## 🧠 Why This Project Matters

This isn't just a demo.

It teaches:
- Multi-agent system design
- Orchestration patterns
- Real-world AI workflows
- Financial system simulation
- UI + API integration

---

## ⚠️ Disclaimer

**This is a simulated trading system for learning.**
**Do not use it for real financial trading.**

---

## 📌 Future Improvements

- 🔥 Real-time market APIs (instead of simulated)
- 🧠 LLM-powered reasoning
- 📊 Advanced visualization (charts, dashboards)
- ☁️ Deployment (Docker + Cloud)
- 🤝 Multi-user collaboration
