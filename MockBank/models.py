"""
MockBank Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional


class TransactionCreate(BaseModel):
    """Model for creating a new transaction."""
    date: str
    description: str
    amount: float
    currency: str = "CHF"
    reference: Optional[str] = None


class Transaction(TransactionCreate):
    """Full transaction model with ID."""
    id: int


class RecurringCreate(BaseModel):
    """Model for creating a recurring transaction."""
    description: str
    amount: float
    currency: str = "CHF"
    frequency: str  # 'weekly', 'monthly', 'yearly'
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    month: Optional[int] = None  # 1-12 for yearly
    day_of_year: Optional[int] = None  # 1-31 for yearly


class Recurring(RecurringCreate):
    """Full recurring transaction model."""
    id: int
    is_active: bool = True
    last_executed: Optional[str] = None


class Stock(BaseModel):
    """Stock portfolio model."""
    ticker: str
    quantity: int
    invested: float = 0


class StockModify(BaseModel):
    """Model for adding/removing stocks with price."""
    quantity: int
    price: float  # CHF amount for buy/sell

