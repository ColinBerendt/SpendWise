"""
MockBank Server - FastAPI Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
import json

import database as db
from generator import create_random_transactions
from scheduler import start_scheduler, stop_scheduler, check_recurring_transactions
from config import CATEGORIES, RECURRING_TYPES, DAYS_OF_WEEK, MONTHS
from models import TransactionCreate, RecurringCreate, StockModify
from stock_prices import enrich_stocks_with_prices, clear_cache as clear_price_cache, get_total_portfolio_value


# ═══════════════════════════════════════════════════════════════
# APP SETUP
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    db.init_databases()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title="MockBank",
    description="Simulated bank for SpendWise testing",
    version="0.1.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory staging area for transactions
staging: list[dict] = []


# ═══════════════════════════════════════════════════════════════
# UI ROUTES - HTML Pages
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def bank_statement(request: Request):
    """Bank Statement page - transactions management."""
    transactions = db.get_all_transactions()
    balance = db.get_balance()
    stocks = db.get_all_stocks()
    portfolio_value = get_total_portfolio_value(stocks)
    net_worth = round(balance + portfolio_value, 2)
    return templates.TemplateResponse("bank_statement.html", {
        "request": request,
        "transactions": transactions,
        "staging": staging,
        "categories": CATEGORIES,
        "active_tab": "bank_statement",
        "balance": balance,
        "net_worth": net_worth,
    })


@app.get("/stocks")
async def stock_portfolio(request: Request):
    """Stock Portfolio page - view only with live prices."""
    stocks = db.get_all_stocks()
    balance = db.get_balance()
    # Enrich with current prices from Yahoo Finance
    stocks_with_prices = enrich_stocks_with_prices(stocks)
    # Calculate portfolio value from enriched data
    portfolio_value = sum(s.get("market_value") or 0 for s in stocks_with_prices)
    net_worth = round(balance + portfolio_value, 2)
    return templates.TemplateResponse("stock_portfolio.html", {
        "request": request,
        "stocks": stocks_with_prices,
        "active_tab": "stocks",
        "balance": balance,
        "net_worth": net_worth,
    })


@app.get("/recurring")
async def recurring_page(request: Request):
    """Recurring Transactions page."""
    # Auto-check recurring transactions when page is loaded
    check_recurring_transactions()
    
    recurring = db.get_all_recurring()
    balance = db.get_balance()
    stocks = db.get_all_stocks()
    portfolio_value = get_total_portfolio_value(stocks)
    net_worth = round(balance + portfolio_value, 2)
    return templates.TemplateResponse("recurring.html", {
        "request": request,
        "recurring": recurring,
        "recurring_types": RECURRING_TYPES,
        "days_of_week": DAYS_OF_WEEK,
        "months": MONTHS,
        "active_tab": "recurring",
        "balance": balance,
        "net_worth": net_worth,
    })


# ═══════════════════════════════════════════════════════════════
# UI ACTIONS - Form Submissions
# ═══════════════════════════════════════════════════════════════

@app.post("/staging/add")
async def add_to_staging(
    category: str = Form(...),
    merchant: str = Form(...),
    amount: float = Form(...),
):
    """Add a manual transaction to staging."""
    from datetime import date
    
    staging.append({
        "date": date.today().isoformat(),
        "description": merchant.upper(),
        "amount": amount,
        "currency": "CHF",
    })
    return RedirectResponse("/", status_code=303)


@app.post("/staging/generate")
async def generate_to_staging(count: int = Form(5)):
    """Generate random transactions to staging."""
    count = min(max(1, count), 50)  # Limit 1-50
    new_transactions = create_random_transactions(count)
    staging.extend(new_transactions)
    return RedirectResponse("/", status_code=303)


@app.post("/staging/edit/{index}")
async def edit_staging(
    index: int,
    date: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
):
    """Edit a transaction in staging."""
    if 0 <= index < len(staging):
        staging[index] = {
            "date": date,
            "description": description,
            "amount": amount,
            "currency": "CHF",
        }
    return RedirectResponse("/", status_code=303)


@app.post("/staging/delete/{index}")
async def delete_from_staging(index: int):
    """Remove a transaction from staging."""
    if 0 <= index < len(staging):
        staging.pop(index)
    return RedirectResponse("/", status_code=303)


@app.post("/staging/commit")
async def commit_staging():
    """Save all staging transactions to database."""
    for tx in staging:
        db.create_transaction(tx)
    staging.clear()
    return RedirectResponse("/", status_code=303)


@app.post("/staging/clear")
async def clear_staging():
    """Clear all staging transactions."""
    staging.clear()
    return RedirectResponse("/", status_code=303)


@app.post("/transactions/delete/{reference}")
async def delete_transaction(reference: str):
    """Delete a transaction from database."""
    db.delete_transaction(reference)
    return RedirectResponse("/", status_code=303)


# ═══════════════════════════════════════════════════════════════
# RECURRING UI ACTIONS
# ═══════════════════════════════════════════════════════════════

@app.post("/recurring/add")
async def add_recurring(
    description: str = Form(...),
    amount: float = Form(...),
    frequency: str = Form(...),
    day_of_week: Optional[int] = Form(None),
    day_of_month: Optional[int] = Form(None),
    month: Optional[int] = Form(None),
    day_of_year: Optional[int] = Form(None),
):
    """Add a new recurring transaction."""
    # Validate required fields based on frequency
    if frequency == "weekly" and day_of_week is None:
        raise HTTPException(status_code=400, detail="day_of_week is required for weekly frequency")
    if frequency == "monthly" and day_of_month is None:
        raise HTTPException(status_code=400, detail="day_of_month is required for monthly frequency")
    if frequency == "yearly" and (month is None or day_of_year is None):
        raise HTTPException(status_code=400, detail="month and day_of_year are required for yearly frequency")
    
    rec = {
        "description": description,
        "amount": amount,
        "currency": "CHF",
        "frequency": frequency,
        "day_of_week": day_of_week if frequency == "weekly" else None,
        "day_of_month": day_of_month if frequency == "monthly" else None,
        "month": month if frequency == "yearly" else None,
        "day_of_year": day_of_year if frequency == "yearly" else None,
    }
    db.create_recurring(rec)
    return RedirectResponse("/recurring", status_code=303)


@app.post("/recurring/edit/{id}")
async def edit_recurring(
    id: int,
    description: str = Form(...),
    amount: float = Form(...),
    frequency: str = Form(...),
    day_of_week: Optional[int] = Form(None),
    day_of_month: Optional[int] = Form(None),
    month: Optional[int] = Form(None),
    day_of_year: Optional[int] = Form(None),
):
    """Edit a recurring transaction."""
    # Validate required fields based on frequency
    if frequency == "weekly" and day_of_week is None:
        raise HTTPException(status_code=400, detail="day_of_week is required for weekly frequency")
    if frequency == "monthly" and day_of_month is None:
        raise HTTPException(status_code=400, detail="day_of_month is required for monthly frequency")
    if frequency == "yearly" and (month is None or day_of_year is None):
        raise HTTPException(status_code=400, detail="month and day_of_year are required for yearly frequency")
    
    rec = {
        "description": description,
        "amount": amount,
        "currency": "CHF",
        "frequency": frequency,
        "day_of_week": day_of_week if frequency == "weekly" else None,
        "day_of_month": day_of_month if frequency == "monthly" else None,
        "month": month if frequency == "yearly" else None,
        "day_of_year": day_of_year if frequency == "yearly" else None,
    }
    db.update_recurring(id, rec)
    return RedirectResponse("/recurring", status_code=303)


@app.post("/recurring/delete/{id}")
async def delete_recurring(id: int):
    """Delete a recurring transaction."""
    db.delete_recurring(id)
    return RedirectResponse("/recurring", status_code=303)


@app.post("/stocks/refresh")
async def refresh_stock_prices():
    """Clear price cache and refresh stock prices."""
    clear_price_cache()
    return RedirectResponse("/stocks", status_code=303)


# ═══════════════════════════════════════════════════════════════
# API ROUTES - JSON (for SpendWise)
# ═══════════════════════════════════════════════════════════════

@app.get("/api/transactions")
async def api_get_transactions(since: Optional[str] = None):
    """Get all transactions (API)."""
    transactions = db.get_all_transactions(since=since)
    return {
        "transactions": transactions,
        "count": len(transactions)
    }


@app.post("/api/transactions")
async def api_create_transaction(tx: TransactionCreate):
    """Create a new transaction (API)."""
    result = db.create_transaction(tx.model_dump())
    return result


@app.get("/api/stocks")
async def api_get_stocks():
    """Get all stocks (API)."""
    stocks = db.get_all_stocks()
    return {
        "portfolio": stocks,
        "total_positions": len(stocks)
    }


@app.get("/api/stocks/{ticker}")
async def api_get_stock(ticker: str):
    """Get a single stock (API)."""
    stock = db.get_stock(ticker)
    return {
        "ticker": ticker.upper(),
        "quantity": stock["quantity"] if stock else 0,
        "invested": stock["invested"] if stock else 0,
        "exists": stock is not None
    }


@app.post("/api/stocks/{ticker}/add")
async def api_add_stock(ticker: str, body: StockModify):
    """Buy stocks (API). Creates a transaction automatically."""
    result = db.add_stock(ticker, body.quantity, body.price)
    return result


@app.post("/api/stocks/{ticker}/remove")
async def api_remove_stock(ticker: str, body: StockModify):
    """Sell stocks (API). Creates a transaction automatically."""
    result = db.remove_stock(ticker, body.quantity, body.price)
    return result


# ═══════════════════════════════════════════════════════════════
# HELPER ENDPOINT
# ═══════════════════════════════════════════════════════════════

@app.get("/api/balance")
async def api_get_balance():
    """Get current account balance (API)."""
    balance = db.get_balance()
    return {"balance": balance, "currency": "CHF"}


@app.get("/api/categories")
async def api_get_categories():
    """Get all categories with merchants (for frontend JS)."""
    return CATEGORIES


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

