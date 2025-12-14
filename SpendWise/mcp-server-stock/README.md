# MCP Server - Stock

Custom MCP server for stock market data and trading.

## Features

- **FMP API**: Real-time stock market data
- **MockBank API**: Portfolio management and trading

## Tools

### Market Data (FMP)

| Tool | Description |
|------|-------------|
| `get_quote` | Real-time stock quote (price, change, volume) |
| `get_profile` | Company profile (sector, industry, CEO) |
| `get_key_metrics` | Financial metrics (P/E, ROE, margins) |
| `get_price_target` | Price target summary |
| `get_market_movers` | Gainers, losers, most active |
| `search_symbol` | Search for stock symbols |

### Trading (MockBank)

| Tool | Description |
|------|-------------|
| `get_balance` | Current cash balance (CHF) |
| `get_portfolio` | All stock holdings |
| `buy_stock` | Buy shares (ticker, quantity, price) |
| `sell_stock` | Sell shares (ticker, quantity, price) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FMP_API_KEY` | Yes | Your FMP API key |
| `MOCKBANK_URL` | No | MockBank URL (default: `http://host.docker.internal:8080`) |

Get a free FMP API key at: https://site.financialmodelingprep.com/developer

## Docker Sandbox

This server runs in a Docker sandbox with:
- Network access to `financialmodelingprep.com` (FMP API)
- Network access to `host.docker.internal:8080` (MockBank)
- Environment variable for API key

## Usage

```python
from spendwise.mcp import create_stock_mcp_server

stock_mcp = create_stock_mcp_server()
```

## Development

```bash
cd SpendWise/mcp-server-stock
pip install -e .
python -m mcp_server_stock
```
