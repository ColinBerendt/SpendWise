# SpendWise Testing

**This directory contains testing and demo scripts for development purposes.**

These scripts are used to:
- Test individual agents in isolation
- Demonstrate agent capabilities
- Seed sample data for development
- Verify MCP server configurations
- Debug agent behavior

**Note:** These are development/testing tools, not part of the production application.

## Quick Start

```bash
cd SpendWise

# 1. Seed the database
uv run testing/seed_data.py

# 2. Run any demo
uv run testing/spending_demo.py
uv run testing/budget_demo.py
uv run testing/import_demo.py
uv run testing/travel_demo.py
uv run testing/stock_demo.py
```

## Agent Demos

| Agent | Demo | Access | Can Do |
|-------|------|--------|--------|
| **SpendingAgent** | `spending_demo.py` | READ-ONLY | Query transactions |
| **BudgetAgent** | `budget_demo.py` | READ-WRITE | Create/update budgets |
| **ImportAgent** | `import_demo.py` | READ-WRITE | Import & categorize from CSV |
| **TravelAgent** | `travel_demo.py` | External APIs | Plan trips (flights, hotels, weather) |
| **StockAgent** | `stock_demo.py` | READ + FMP + MockBank | Analyze stocks, trade |

## Stock Agent Demo

Requires MockBank running:
```bash
# Terminal 1: Start MockBank
cd MockBank && uv run python server.py

# Terminal 2: Run demo
cd SpendWise && uv run testing/stock_demo.py
```

## Files

```
testing/
├── README.md              # This file
├── seed_data.py           # Testing: Create database with sample data
├── import_mockbank_data.py # Testing: Import 430+ transactions from MockBank
├── spending_demo.py       # Demo: SpendingAgent (read-only)
├── budget_demo.py         # Demo: BudgetAgent (read-write)
├── import_demo.py         # Demo: ImportAgent (read-write, categorizes)
├── travel_demo.py         # Demo: TravelAgent (external APIs)
├── stock_demo.py          # Demo: StockAgent (FMP + MockBank)
├── mcp_sms_demo.py        # Demo: SMS Agent with Twilio
├── test_fmp_api.py        # Testing: Verify FMP API connectivity
├── discover_amadeus_ips.py # Testing: Discover Amadeus API IP addresses
└── data/
    └── bank_export.csv    # Sample CSV for import testing
```

## Purpose

### Testing Scripts
- `seed_data.py` - Creates test database with sample transactions and budgets
- `import_mockbank_data.py` - Imports test data from MockBank for development
- `test_fmp_api.py` - Verifies FMP API key and connectivity
- `discover_amadeus_ips.py` - Discovers Amadeus API IP addresses for MCP permissions

### Demo Scripts
- `spending_demo.py` - Demonstrates Spending Agent capabilities
- `budget_demo.py` - Demonstrates Budget Agent capabilities
- `import_demo.py` - Demonstrates Import Agent with CSV parsing
- `travel_demo.py` - Demonstrates Travel Agent with real APIs
- `stock_demo.py` - Demonstrates Stock Agent with market data
- `mcp_sms_demo.py` - Demonstrates SMS alerts via Twilio

**These scripts are for development and testing only.**

## How Access Control Works

```python
# Read-only access (SpendingAgent, InsightsAgent)
sqlite_mcp = create_sqlite_mcp_server(db_path, readonly=True)

# Read-write access (BudgetAgent, ImportAgent)
sqlite_mcp = create_sqlite_mcp_server(db_path, readonly=False)
```
