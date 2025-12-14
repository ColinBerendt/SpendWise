"""
Transactions API Routes (Read-Only for Display)

GET /api/transactions          - List all transactions
GET /api/transactions/summary  - Get spending summary
GET /api/transactions/categories - List categories
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

DB_PATH = Path(__file__).parent.parent.parent / "data" / "spendwise.db"


def get_db():
    """Get database connection."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Database not found")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
async def list_transactions(
    category_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """List all transactions with optional filters."""
    conn = get_db()
    try:
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []
        
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        
        if start_date:
            query += " AND t.date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND t.date <= ?"
            params.append(end_date)
        
        query += " ORDER BY t.date DESC, t.id DESC"
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        return {
            "transactions": [dict(row) for row in rows],
            "count": len(rows),
        }
    finally:
        conn.close()


@router.get("/summary")
async def get_summary(
    period: str = Query("month", regex="^(week|month|year)$"),
):
    """Get spending summary for period."""
    conn = get_db()
    try:
        today = date.today()
        if period == "week":
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
        elif period == "month":
            start_date = today.replace(day=1)
        else:
            start_date = today.replace(month=1, day=1)
        
        # Total income and expenses
        cursor = conn.execute("""
            SELECT 
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as expenses
            FROM transactions
            WHERE date >= ?
        """, (start_date.isoformat(),))
        totals = dict(cursor.fetchone())
        
        # By category (expenses only)
        cursor = conn.execute("""
            SELECT c.name, c.id, c.color, c.icon, SUM(t.amount) as total, COUNT(*) as count
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date >= ? AND t.amount < 0
            GROUP BY c.id
            ORDER BY total ASC
        """, (start_date.isoformat(),))
        by_category = [dict(row) for row in cursor.fetchall()]
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "income": totals["income"] or 0,
            "expenses": abs(totals["expenses"] or 0),
            "net": (totals["income"] or 0) + (totals["expenses"] or 0),
            "by_category": by_category,
        }
    finally:
        conn.close()


@router.get("/categories")
async def list_categories():
    """List all categories."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT * FROM categories ORDER BY id")
        return {"categories": [dict(row) for row in cursor.fetchall()]}
    finally:
        conn.close()
