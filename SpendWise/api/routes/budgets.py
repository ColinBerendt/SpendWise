"""
Budgets API Routes (Read-Only for Display)

GET /api/budgets        - List all budgets with status
GET /api/budgets/status - Get budget status overview
"""

import sqlite3
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException

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
async def list_budgets():
    """List all budgets with current week spending."""
    conn = get_db()
    try:
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        cursor = conn.execute("""
            SELECT 
                b.id,
                b.category_id,
                c.name as category_name,
                c.color,
                c.icon,
                b.amount_weekly as budget,
                b.alert_threshold,
                COALESCE(ABS(SUM(CASE WHEN t.amount < 0 THEN t.amount ELSE 0 END)), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON t.category_id = b.category_id
                AND t.date >= ?
            WHERE b.is_active = 1
            GROUP BY b.id
            ORDER BY c.id
        """, (week_start.isoformat(),))
        
        budgets = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            budget = row_dict["budget"]
            spent = row_dict["spent"]
            remaining = budget - spent
            usage_percent = (spent / budget * 100) if budget > 0 else 0
            
            if usage_percent >= 100:
                status = "over"
            elif usage_percent >= row_dict["alert_threshold"] * 100:
                status = "warning"
            else:
                status = "ok"
            
            budgets.append({
                **row_dict,
                "remaining": remaining,
                "usage_percent": round(usage_percent, 1),
                "status": status,
            })
        
        return {
            "budgets": budgets,
            "week_start": week_start.isoformat(),
            "week_end": (week_start + timedelta(days=6)).isoformat(),
        }
    finally:
        conn.close()


@router.get("/status")
async def get_budget_status():
    """Get budget status overview."""
    conn = get_db()
    try:
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        
        cursor = conn.execute("""
            SELECT 
                c.name as category_name,
                b.amount_weekly as budget,
                COALESCE(ABS(SUM(CASE WHEN t.amount < 0 THEN t.amount ELSE 0 END)), 0) as spent,
                b.alert_threshold
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON t.category_id = b.category_id
                AND t.date >= ?
            WHERE b.is_active = 1
            GROUP BY b.id
        """, (week_start.isoformat(),))
        
        ok_count = 0
        warning_count = 0
        over_count = 0
        total_budget = 0
        total_spent = 0
        
        for row in cursor.fetchall():
            budget = row["budget"]
            spent = row["spent"]
            usage = spent / budget if budget > 0 else 0
            
            total_budget += budget
            total_spent += spent
            
            if usage >= 1.0:
                over_count += 1
            elif usage >= row["alert_threshold"]:
                warning_count += 1
            else:
                ok_count += 1
        
        return {
            "week_start": week_start.isoformat(),
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": total_budget - total_spent,
            "overall_usage_percent": round(total_spent / total_budget * 100, 1) if total_budget > 0 else 0,
            "counts": {
                "ok": ok_count,
                "warning": warning_count,
                "over": over_count,
            },
        }
    finally:
        conn.close()
