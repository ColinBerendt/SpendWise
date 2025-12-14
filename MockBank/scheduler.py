"""
MockBank Scheduler - Checks and executes recurring transactions
"""

from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
import database as db


scheduler = BackgroundScheduler()


def should_execute_today(recurring: dict, today: date) -> bool:
    """Check if a recurring transaction should execute today."""
    freq = recurring["frequency"]
    
    if freq == "weekly":
        # day_of_week: 0=Monday, 6=Sunday
        return today.weekday() == recurring["day_of_week"]
    
    elif freq == "monthly":
        # day_of_month: 1-31
        target_day = recurring["day_of_month"]
        if target_day is None:
            return False
        return today.day == target_day
    
    elif freq == "yearly":
        # month: 1-12, day_of_year: 1-31
        return today.month == recurring["month"] and today.day == recurring["day_of_year"]
    
    return False


def already_executed_today(recurring: dict, today: date) -> bool:
    """Check if recurring transaction was already executed today."""
    last = recurring.get("last_executed")
    if not last:
        return False
    return last == today.isoformat()


def check_recurring_transactions():
    """Check all active recurring transactions and execute due ones."""
    today = date.today()
    
    recurring_list = db.get_all_recurring(active_only=True)
    executed_count = 0
    
    for recurring in recurring_list:
        
        if should_execute_today(recurring, today):
            if not already_executed_today(recurring, today):
                # Create the transaction (reference will be auto-generated)
                tx = {
                    "date": today.isoformat(),
                    "description": recurring["description"],
                    "amount": recurring["amount"],
                    "currency": recurring["currency"],
                }
                
                result = db.create_transaction(tx)
                
                # Update last executed
                db.update_recurring_last_executed(recurring["id"], today)
                
                executed_count += 1
    
    if executed_count > 0:
        print(f"Executed {executed_count} recurring transaction(s)")


def start_scheduler():
    """Start the background scheduler."""
    # Check every 10 seconds
    scheduler.add_job(
        check_recurring_transactions,
        'interval',
        seconds=10,
        id='recurring_check',
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started (checking recurring transactions every 10 seconds)")
    
    # Also check immediately on startup
    check_recurring_transactions()


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    print("Scheduler stopped")
