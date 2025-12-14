# MockBank

Simulated bank for SpendWise testing. Provides a web UI for managing transactions and a REST API for SpendWise integration.

## Features

- **Bank Statement**: Create transactions manually or generate random ones
- **Stock Portfolio**: View stock holdings (modifiable via API only)
- **Recurring Transactions**: Set up weekly/monthly/yearly recurring transactions
- **REST API**: Full API for SpendWise integration

## Quick Start

```bash
cd MockBank
uv venv && uv sync
uv run uvicorn server:app --reload --port 8080
```

Open: **http://localhost:8080**

## Databases

| File | Content |
|------|---------|
| `data/transactions.db` | All bank transactions |
| `data/stocks.db` | Stock portfolio |
| `data/recurring.db` | Recurring transaction definitions |

## API Endpoints

### Transactions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/transactions` | GET | Get all transactions |
| `/api/transactions?since=2025-01-01` | GET | Get transactions since date |
| `/api/transactions` | POST | Create new transaction |

### Stocks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stocks` | GET | Get all stocks |
| `/api/stocks/{ticker}` | GET | Get single stock |
| `/api/stocks/{ticker}/add` | POST | Buy stocks `{"quantity": 5}` |
| `/api/stocks/{ticker}/remove` | POST | Sell stocks `{"quantity": 2}` |

### Other

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/categories` | GET | Get categories with merchants |
| `/docs` | GET | OpenAPI documentation |

## Example Usage

### Get all transactions
```bash
curl http://localhost:8080/api/transactions
```

### Create a transaction
```bash
curl -X POST http://localhost:8080/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-12-07", "description": "MIGROS ZURICH", "amount": -45.80}'
```

### Buy stocks
```bash
curl -X POST http://localhost:8080/api/stocks/AAPL/add \
  -H "Content-Type: application/json" \
  -d '{"quantity": 10}'
```

## Integration with SpendWise

SpendWise can fetch transactions from MockBank:

```python
import httpx

async def fetch_bank_transactions():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/api/transactions")
        data = response.json()
        return data["transactions"]
```

