"""
MockBank Database - SQLite CRUD Operations
"""

import sqlite3
import uuid
from pathlib import Path
from datetime import date, datetime
from typing import Optional

# Database directory
DATA_DIR = Path(__file__).parent / "data"


def get_transactions_db() -> sqlite3.Connection:
    """Get connection to transactions database."""
    conn = sqlite3.connect(DATA_DIR / "transactions.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_stocks_db() -> sqlite3.Connection:
    """Get connection to stocks database."""
    conn = sqlite3.connect(DATA_DIR / "stocks.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_recurring_db() -> sqlite3.Connection:
    """Get connection to recurring database."""
    conn = sqlite3.connect(DATA_DIR / "recurring.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_databases():
    """Initialize all databases and create tables."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Transactions table
    with get_transactions_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                reference TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'CHF'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
        conn.commit()
    
    # Stocks table
    with get_stocks_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                ticker TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0,
                invested REAL NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    # Recurring transactions table
    with get_recurring_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'CHF',
                frequency TEXT NOT NULL,
                day_of_week INTEGER,
                day_of_month INTEGER,
                month INTEGER,
                day_of_year INTEGER,
                is_active INTEGER DEFAULT 1,
                last_executed TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    print("Databases initialized")


# ═══════════════════════════════════════════════════════════════
# TRANSACTIONS CRUD
# ═══════════════════════════════════════════════════════════════

def create_transaction(tx: dict) -> dict:
    """Create a new transaction."""
    ref = tx.get("reference") or f"TXN-{uuid.uuid4().hex[:8].upper()}"
    
    with get_transactions_db() as conn:
        conn.execute(
            """INSERT INTO transactions (reference, date, description, amount, currency)
               VALUES (?, ?, ?, ?, ?)""",
            (ref, tx["date"], tx["description"], tx["amount"], tx.get("currency", "CHF"))
        )
        conn.commit()
        return {
            "reference": ref,
            "created": True
        }


def get_all_transactions(since: Optional[str] = None) -> list[dict]:
    """Get all transactions, optionally filtered by date."""
    with get_transactions_db() as conn:
        if since:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE date >= ? ORDER BY date DESC, reference DESC",
                (since,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM transactions ORDER BY date DESC, reference DESC"
            ).fetchall()
        return [dict(row) for row in rows]


def get_transaction(reference: str) -> Optional[dict]:
    """Get a single transaction by reference."""
    with get_transactions_db() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE reference = ?", (reference,)).fetchone()
        return dict(row) if row else None


def delete_transaction(reference: str) -> bool:
    """Delete a transaction."""
    with get_transactions_db() as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE reference = ?", (reference,))
        conn.commit()
        return cursor.rowcount > 0


def get_balance() -> float:
    """Calculate current account balance from all transactions."""
    with get_transactions_db() as conn:
        cursor = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions")
        balance = cursor.fetchone()[0]
        return round(balance, 2)


# ═══════════════════════════════════════════════════════════════
# STOCKS CRUD
# ═══════════════════════════════════════════════════════════════

def get_all_stocks() -> list[dict]:
    """Get all stocks in portfolio."""
    with get_stocks_db() as conn:
        rows = conn.execute(
            "SELECT ticker, quantity, invested FROM stocks WHERE quantity > 0 ORDER BY ticker"
        ).fetchall()
        return [dict(row) for row in rows]


def get_stock(ticker: str) -> Optional[dict]:
    """Get a single stock by ticker."""
    ticker = ticker.upper()
    with get_stocks_db() as conn:
        row = conn.execute(
            "SELECT ticker, quantity, invested FROM stocks WHERE ticker = ?", (ticker,)
        ).fetchone()
        return dict(row) if row else None


def add_stock(ticker: str, quantity: int, price: float) -> dict:
    """Add stocks (buy). Creates a transaction automatically."""
    ticker = ticker.upper()
    total_cost = quantity * price  # Total cost = quantity * price per share
    
    with get_stocks_db() as conn:
        # Upsert stock with invested amount
        conn.execute("""
            INSERT INTO stocks (ticker, quantity, invested, updated_at) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ticker) DO UPDATE SET 
                quantity = quantity + excluded.quantity,
                invested = invested + excluded.invested,
                updated_at = CURRENT_TIMESTAMP
        """, (ticker, quantity, total_cost))
        conn.commit()
        
        row = conn.execute("SELECT quantity, invested FROM stocks WHERE ticker = ?", (ticker,)).fetchone()
    
    # Create transaction for the buy
    tx = {
        "date": date.today().isoformat(),
        "description": f"STOCK: +{quantity} {ticker} @{price:.2f}",
        "amount": -total_cost,  # Negative because money goes out
        "currency": "CHF"
    }
    create_transaction(tx)
    
    return {
        "ticker": ticker,
        "added": quantity,
        "price": price,
        "total_cost": total_cost,
        "new_quantity": row["quantity"],
        "total_invested": row["invested"]
    }


def remove_stock(ticker: str, quantity: int, price: float) -> dict:
    """Remove stocks (sell). Creates a transaction automatically."""
    ticker = ticker.upper()
    
    with get_stocks_db() as conn:
        row = conn.execute("SELECT quantity, invested FROM stocks WHERE ticker = ?", (ticker,)).fetchone()
        
        if not row:
            return {"ticker": ticker, "error": "Stock not found", "removed": 0, "new_quantity": 0}
        
        current_qty = row["quantity"]
        current_invested = row["invested"]
        
        new_quantity = max(0, current_qty - quantity)
        actually_removed = current_qty - new_quantity
        
        # Calculate proportional invested reduction
        if current_qty > 0:
            invested_per_share = current_invested / current_qty
            invested_reduction = invested_per_share * actually_removed
        else:
            invested_reduction = 0
        
        new_invested = max(0, current_invested - invested_reduction)
        
        conn.execute(
            "UPDATE stocks SET quantity = ?, invested = ?, updated_at = CURRENT_TIMESTAMP WHERE ticker = ?",
            (new_quantity, new_invested, ticker)
        )
        conn.commit()
    
    # Create transaction for the sell (total = quantity * price)
    total_sale = actually_removed * price
    if actually_removed > 0:
        tx = {
            "date": date.today().isoformat(),
            "description": f"STOCK: -{actually_removed} {ticker} @{price:.2f}",
            "amount": total_sale,  # Positive because money comes in
            "currency": "CHF"
        }
        create_transaction(tx)
    
    return {
        "ticker": ticker,
        "removed": actually_removed,
        "price": price,
        "total_sale": total_sale,
        "new_quantity": new_quantity,
        "total_invested": new_invested
    }


# ═══════════════════════════════════════════════════════════════
# RECURRING TRANSACTIONS CRUD
# ═══════════════════════════════════════════════════════════════

def create_recurring(rec: dict) -> dict:
    """Create a new recurring transaction."""
    with get_recurring_db() as conn:
        cursor = conn.execute("""
            INSERT INTO recurring_transactions 
            (description, amount, currency, frequency, day_of_week, day_of_month, month, day_of_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec["description"],
            rec["amount"],
            rec.get("currency", "CHF"),
            rec["frequency"],
            rec.get("day_of_week"),
            rec.get("day_of_month"),
            rec.get("month"),
            rec.get("day_of_year"),
        ))
        conn.commit()
        return {"id": cursor.lastrowid, "created": True}


def get_all_recurring(active_only: bool = False) -> list[dict]:
    """Get all recurring transactions."""
    with get_recurring_db() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM recurring_transactions WHERE is_active = 1 ORDER BY id"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM recurring_transactions ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]


def get_recurring(id: int) -> Optional[dict]:
    """Get a single recurring transaction."""
    with get_recurring_db() as conn:
        row = conn.execute(
            "SELECT * FROM recurring_transactions WHERE id = ?", (id,)
        ).fetchone()
        return dict(row) if row else None


def update_recurring(id: int, rec: dict) -> bool:
    """Update a recurring transaction."""
    with get_recurring_db() as conn:
        cursor = conn.execute("""
            UPDATE recurring_transactions SET
                description = ?,
                amount = ?,
                currency = ?,
                frequency = ?,
                day_of_week = ?,
                day_of_month = ?,
                month = ?,
                day_of_year = ?
            WHERE id = ?
        """, (
            rec["description"],
            rec["amount"],
            rec.get("currency", "CHF"),
            rec["frequency"],
            rec.get("day_of_week"),
            rec.get("day_of_month"),
            rec.get("month"),
            rec.get("day_of_year"),
            id,
        ))
        conn.commit()
        return cursor.rowcount > 0


def delete_recurring(id: int) -> bool:
    """Delete a recurring transaction."""
    with get_recurring_db() as conn:
        cursor = conn.execute("DELETE FROM recurring_transactions WHERE id = ?", (id,))
        conn.commit()
        return cursor.rowcount > 0


def update_recurring_last_executed(id: int, executed_date: date) -> bool:
    """Update the last executed date of a recurring transaction."""
    with get_recurring_db() as conn:
        cursor = conn.execute(
            "UPDATE recurring_transactions SET last_executed = ? WHERE id = ?",
            (executed_date.isoformat(), id)
        )
        conn.commit()
        return cursor.rowcount > 0

