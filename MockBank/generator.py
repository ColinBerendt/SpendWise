"""
MockBank Transaction Generator - Creates random transactions
"""

import random
from datetime import date
from config import CATEGORIES, AMOUNT_RANGES, CITIES, NO_LOCATION_MERCHANTS


def create_random_transactions(count: int = 5) -> list[dict]:
    """
    Generate random transactions.
    
    Args:
        count: Number of transactions to generate
        
    Returns:
        List of transaction dictionaries (not yet in DB)
    """
    transactions = []
    today = date.today()
    
    for _ in range(count):
        # Random category (Income is less likely)
        if random.random() < 0.1:  # 10% chance of income
            category = "Income"
        else:
            category = random.choice([c for c in CATEGORIES.keys() if c != "Income"])
        
        # Random merchant from category
        merchant = random.choice(CATEGORIES[category])
        
        # Random amount within range
        min_amt, max_amt = AMOUNT_RANGES[category]
        amount = round(random.uniform(min_amt, max_amt), 2)
        
        # Build description - only add city for physical locations
        if category == "Income" or merchant in NO_LOCATION_MERCHANTS:
            description = f"{merchant.upper()}"
        else:
            city = random.choice(CITIES)
            description = f"{merchant.upper()} {city}"
        
        # Always use today's date
        transactions.append({
            "date": today.isoformat(),
            "description": description,
            "amount": amount,
            "currency": "CHF",
        })
    
    return transactions

