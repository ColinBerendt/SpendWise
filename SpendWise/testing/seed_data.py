#!/usr/bin/env python3
"""
Seed Demo Data - Populates SQLite database with sample data

Usage:
    cd SpendWise
    uv run testing/seed_data.py
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path


# Database path
PROJECT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = PROJECT_DIR / "data" / "spendwise.db"


# Categories
CATEGORIES = [
    (1, "Food & Dining", "Restaurants, groceries, cafes", "utensils", "#FF6B6B"),
    (2, "Transportation", "Public transport, fuel, parking", "car", "#4ECDC4"),
    (3, "Shopping", "Clothing, electronics, general shopping", "shopping-bag", "#45B7D1"),
    (4, "Entertainment", "Movies, games, subscriptions", "film", "#96CEB4"),
    (5, "Bills & Utilities", "Rent, electricity, phone, internet", "file-text", "#FFEAA7"),
    (6, "Health", "Pharmacy, doctor, gym", "heart", "#DDA0DD"),
    (7, "Education", "Books, courses, university fees", "book", "#98D8C8"),
    (8, "Income", "Salary, transfers received", "dollar-sign", "#7ED321"),
    (9, "Stocks & Investments", "Stock purchases, ETFs, crypto, dividends", "trending-up", "#9B59B6"),
    (10, "Other", "Uncategorized transactions", "help-circle", "#95A5A6"),
]

# Weekly budgets: (category_id, amount_weekly)
BUDGETS = [
    (1, 150.00),   # Food: 150 CHF/week
    (2, 100.00),   # Transportation: 100 CHF/week
    (3, 80.00),    # Shopping: 80 CHF/week
    (4, 50.00),    # Entertainment: 50 CHF/week
]


def create_tables(conn: sqlite3.Connection):
    """Create all database tables"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            icon TEXT,
            color TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'CHF',
            category_id INTEGER REFERENCES categories(id),
            merchant TEXT,
            source TEXT DEFAULT 'manual',
            reference TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER REFERENCES categories(id),
            amount_weekly REAL NOT NULL,
            alert_threshold REAL DEFAULT 0.8,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            filename TEXT,
            transactions_count INTEGER,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()


def insert_data(conn: sqlite3.Connection):
    """Insert sample data with predictable spending for current week"""
    cursor = conn.cursor()
    today = date.today()
    
    # Calculate start of current week (Monday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    
    # Categories
    for cat in CATEGORIES:
        cursor.execute("""
            INSERT OR REPLACE INTO categories (id, name, description, icon, color)
            VALUES (?, ?, ?, ?, ?)
        """, cat)
    
    # Budgets
    cursor.execute("DELETE FROM budgets")
    for cat_id, amount in BUDGETS:
        cursor.execute("""
            INSERT INTO budgets (category_id, amount_weekly, alert_threshold, is_active)
            VALUES (?, ?, 0.8, 1)
        """, (cat_id, amount))
    
    # Clear old transactions
    cursor.execute("DELETE FROM transactions")
    
    # Current week transactions (Monday to Sunday)
    # Food: Budget 150, spending 135 = 90% (WARNING)
    this_week_txs = [
        (week_start, "Migros Shopping", -65.00, 1, "Migros"),
        (week_start + timedelta(days=1), "Restaurant", -35.00, 1, "Restaurant"),
        (week_start + timedelta(days=2), "Coop", -35.00, 1, "Coop"),
        # Total Food: 135 CHF / 150 CHF = 90% -> WARNING
        
        # Transport: Budget 100, spending 45 = 45% (OK)
        (week_start, "SBB Ticket", -25.00, 2, "SBB"),
        (week_start + timedelta(days=1), "Bus", -20.00, 2, "ZVV"),
        # Total Transport: 45 CHF / 100 CHF = 45% -> OK, no SMS
        
        # Shopping: Budget 80, spending 95 = 119% (OVER BUDGET)
        (week_start, "Zalando", -55.00, 3, "Zalando"),
        (week_start + timedelta(days=2), "Amazon", -40.00, 3, "Amazon"),
        # Total Shopping: 95 CHF / 80 CHF = 119% -> OVER BUDGET
        
        # Entertainment: Budget 50, spending 15 = 30% (OK)
        (week_start + timedelta(days=1), "Netflix", -12.90, 4, "Netflix"),
        (week_start + timedelta(days=1), "Spotify", -2.10, 4, "Spotify"),
        # Total Entertainment: 15 CHF / 50 CHF = 30% -> OK, no SMS
        
        # Income
        (week_start, "Salary", 2500.00, 8, "Employer"),
    ]
    
    for i, (tx_date, desc, amount, cat_id, merchant) in enumerate(this_week_txs):
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, category_id, merchant, source, reference)
            VALUES (?, ?, ?, ?, ?, 'seed', ?)
        """, (tx_date.isoformat(), desc, amount, cat_id, merchant, f"SEED-{i:04d}"))
    
    conn.commit()
    
    # Show expected results
    print("\n--- EXPECTED RESULTS ---")
    print("| Category       | Budget | Spent  | Usage | Status      | SMS? |")
    print("|----------------|--------|--------|-------|-------------|------|")
    print("| Food           | 150    | 135    | 90%   | WARNING     | YES  |")
    print("| Transportation | 100    | 45     | 45%   | OK          | NO   |")
    print("| Shopping       | 80     | 95     | 119%  | OVER BUDGET | YES  |")
    print("| Entertainment  | 50     | 15     | 30%   | OK          | NO   |")
    print("-----------------------------")
    print("-> Expected SMS: 2 (Food + Shopping)")


def show_summary(conn: sqlite3.Connection):
    """Show database summary"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM budgets WHERE is_active = 1")
    budget_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount > 0")
    income = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE amount < 0")
    expenses = cursor.fetchone()[0] or 0
    
    print(f"\nDatabase Summary:")
    print(f"  Transactions: {tx_count}")
    print(f"  Budgets:      {budget_count}")
    print(f"  Income:       CHF {income:,.2f}")
    print(f"  Expenses:     CHF {abs(expenses):,.2f}")


def main():
    print("\n" + "=" * 50)
    print("SpendWise - Seed Data")
    print("=" * 50)
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("\n[OK] Deleted existing database")
    
    print(f"\nDatabase: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        print("[OK] Tables created")
        
        insert_data(conn)
        print("[OK] Data inserted")
        
        show_summary(conn)
        
        print("\n" + "=" * 50)
        print("Test with:")
        print("  uv run scripts/weekly_check.py --dry-run")
        print("=" * 50 + "\n")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
