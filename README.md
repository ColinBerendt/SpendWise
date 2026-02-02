# SpendWise

> **AI-Powered Personal Finance System with Multi-Agent Architecture**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-Agents_SDK-412991?logo=openai)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![Docker](https://img.shields.io/badge/Docker-Sandbox-2496ED?logo=docker)
![SQLite](https://img.shields.io/badge/SQLite-MCP-003B57?logo=sqlite)


---

## Authors

**Colin Berendt, Yannik Holenstein, Robin Sutter**  
University of St.Gallen (HSG)
Course: Coding with AI

---

This repository contains a complete personal finance application with:

- **SpendWise** - AI-powered finance assistant with multiple specialized agents
- **MockBank** - Simulated bank API for testing
- **python-mcp-sandbox-openai-sdk** - MCP sandbox SDK for secure agent execution

---

## Quick Start (4 Terminals)

### Prerequisites

- **Python 3.10+** with [uv](https://github.com/astral-sh/uv)
- **Node.js 18+** with npm
- **Docker Desktop** (must be running!)
- **OpenAI API Key**

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd SpendWise

# 2. Install SpendWise dependencies
cd SpendWise
uv sync
cd web && npm install && cd ..

# 3. Install MockBank dependencies
cd ../MockBank
uv sync

# 4. Configure environment
cd ../SpendWise
cp .env.example .env   # Then edit with your API keys
```

### Environment Variables

Create `SpendWise/.env`:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional: SMS Alerts (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
NOTIFICATION_PHONE=+41791234567

# Optional: Travel Planning
AMADEUS_API_KEY=...
AMADEUS_API_SECRET=...
OPENWEATHER_API_KEY=...

# Optional: Stock Analysis
FMP_API_KEY=...
```

### Seed Test Data (Optional)

```bash
# MockBank: Seed sample transactions
cd MockBank/testing
uv run python seed_data.py

# SpendWise: Seed sample data
cd ../../SpendWise
uv run testing/seed_data.py
```

---

## Start the Application (4 Terminals)

```
┌─────────────────────────────────────────────────────────────────┐
│  TERMINAL 1: MockBank API (Port 8080)                           │
│  ─────────────────────────────────────────────────────────────  │
│  cd MockBank                                                    │
│  uv run uvicorn server:app --reload --port 8080                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TERMINAL 2: SpendWise API (Port 8000)                          │
│  ─────────────────────────────────────────────────────────────  │
│  cd SpendWise                                                   │
│  uv run uvicorn api.main:app --reload --port 8000               │
│                                                                 │
│  Note: Confirm Docker sandbox permissions when prompted:        │
│  [?] Allow SQLite (RO) access to /data? [y/n]: y                │
│  [?] Allow SQLite (RW) access to /data? [y/n]: y                │
│  [?] Allow Travel MCP network access? [y/n]: y                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TERMINAL 3: Frontend (Port 3000)                               │
│  ─────────────────────────────────────────────────────────────  │
│  cd SpendWise/web                                               │
│  npm run dev                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  TERMINAL 4: Bank Sync (Background)                             │
│  ─────────────────────────────────────────────────────────────  │
│  cd SpendWise                                                   │
│  uv run scripts/bank_sync.py                                    │
│                                                                 │
│  This syncs transactions from MockBank every 5 seconds          │
│  and triggers SMS alerts for suspicious transactions            │
└─────────────────────────────────────────────────────────────────┘
```

### Open in Browser

```
http://localhost:3000
```

---

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| MockBank | 8080 | Simulated bank with transactions & portfolio |
| SpendWise API | 8000 | FastAPI backend with AI agents |
| Frontend | 3000 | Next.js web interface |
| Bank Sync | - | Background script, syncs every 5 seconds |

---

## What Can You Do?

### Chat with AI Agents

```
"Show my spending this month"     -> Spending Agent (read-only)
"Set food budget to 200 CHF"      -> Budget Agent (read-write)
"Plan a weekend in Barcelona"     -> Travel Agent (external APIs)
"Analyze NVDA - should I buy?"    -> Stock Agent (FMP API)
"Any suspicious transactions?"    -> Insights Agent (+ SMS alerts)
```

### MockBank Web UI

Open `http://localhost:8080` to:
- View and create transactions manually
- Generate random transactions
- Manage stock portfolio
- Set up recurring transactions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           FRONTEND                              │
│                      Next.js (localhost:3000)                   │
│   Dashboard | Transactions | Budgets | Stocks | Chat Panel      │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SPENDWISE API                             │
│                     FastAPI (localhost:8000)                    │
│                                                                 │
│              ┌──────── ORCHESTRATOR AGENT ────────┐             │
│              │                                    │             │
│     ┌────────┼────────┬────────────┬─────────────┼────────┐     │
│     ▼        ▼        ▼            ▼             ▼        │     │
│  Spending  Budget  Insights    Travel       Stock     Import    │
│   Agent    Agent    Agent      Agent        Agent     Agent     │
│  (RO DB)  (RW DB)  (RO+SMS)   (APIs)      (RO+FMP)  (RW DB)     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER SANDBOXES (MCP)                       │
│                                                                 │
│  SQLite(RO) | SQLite(RW) | SMS | Travel | Stock                 │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
   SQLite DB              External APIs            MockBank
    (local)          (Amadeus, Twilio, FMP)    (localhost:8080)
```

---

## Project Structure

```
SpendWise/
│
├── SpendWise/                  # Main AI Finance Application
│   ├── api/                    # FastAPI Backend
│   │   ├── main.py             # App entry, MCP initialization
│   │   └── routes/             # API endpoints
│   │
│   ├── src/spendwise/          # Core Library
│   │   ├── agents/             # AI Agent definitions
│   │   └── mcp/                # MCP Server configs
│   │
│   ├── web/                    # Next.js Frontend
│   │   └── src/
│   │       ├── app/            # Pages
│   │       └── components/     # React components
│   │
│   ├── scripts/
│   │   └── bank_sync.py        # Continuous sync with MockBank
│   │
│   ├── testing/                # Demo & test scripts
│   │   ├── seed_data.py        # Create test database
│   │   └── *_demo.py           # Agent demo scripts
│   │
│   ├── mcp-server-sms/         # Custom MCP: Twilio SMS
│   ├── mcp-server-travel/      # Custom MCP: Travel APIs
│   └── mcp-server-stock/       # Custom MCP: Stock data
│
├── MockBank/                   # Simulated Bank API
│   ├── server.py               # FastAPI server (port 8080)
│   ├── database.py             # SQLite CRUD operations
│   ├── testing/
│   │   ├── seed_data.py        # 430+ demo transactions
│   │   └── test_api.py         # API tests
│   └── data/                   # SQLite databases
│
└── python-mcp-sandbox-openai-sdk/  # MCP Sandbox SDK
    └── src/                    # SDK source code
```

---

## Detailed Documentation

| Component | README |
|-----------|--------|
| SpendWise | [SpendWise/README.md](./SpendWise/README.md) |
| MockBank | [MockBank/README.md](./MockBank/README.md) |
| MCP Sandbox SDK | [python-mcp-sandbox-openai-sdk/README.md](./python-mcp-sandbox-openai-sdk/README.md) |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Agents | OpenAI Agents SDK |
| Sandboxing | Docker + mcp-sandbox-openai-sdk |
| Database | SQLite via MCP |
| Backend | FastAPI |
| Frontend | Next.js 15 + TailwindCSS |
| Package Manager | uv (Python), npm (JS) |

---

## Troubleshooting

### Docker not running
```
Error: Cannot connect to Docker daemon
```
Solution: Start Docker Desktop

### Port already in use
```
Error: Address already in use
```
Solution: Kill the process using the port or use a different port

### MCP permission denied
```
Error: Permission denied for MCP server
```
Solution: Answer "y" to all permission prompts when starting the API

### MockBank unreachable
```
Error: MockBank HTTP error
```
Solution: Make sure Terminal 1 (MockBank) is running

