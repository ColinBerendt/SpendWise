"""
SpendWise Agents - AI agents for personal finance management
"""

from .spending_agent import create_spending_agent, SPENDING_INSTRUCTIONS
from .import_agent import create_import_agent, IMPORT_INSTRUCTIONS
from .budget_agent import create_budget_agent, BUDGET_INSTRUCTIONS
from .travel_agent import create_travel_agent, TRAVEL_INSTRUCTIONS
from .insights_agent import create_insights_agent, INSIGHTS_INSTRUCTIONS
from .orchestrator_agent import create_orchestrator_agent, ORCHESTRATOR_INSTRUCTIONS
from .stock_agent import create_stock_agent, STOCK_INSTRUCTIONS

__all__ = [
    # Orchestrator (main entry point)
    "create_orchestrator_agent",
    "ORCHESTRATOR_INSTRUCTIONS",
    # Spending Agent (read-only)
    "create_spending_agent",
    "SPENDING_INSTRUCTIONS",
    # Import Agent (read-write, categorizes internally)
    "create_import_agent",
    "IMPORT_INSTRUCTIONS",
    # Budget Agent (read-write)
    "create_budget_agent",
    "BUDGET_INSTRUCTIONS",
    # Travel Agent (external APIs)
    "create_travel_agent",
    "TRAVEL_INSTRUCTIONS",
    # Insights Agent (read-only + SMS alerts)
    "create_insights_agent",
    "INSIGHTS_INSTRUCTIONS",
    # Stock Agent (read-only + FMP + MockBank)
    "create_stock_agent",
    "STOCK_INSTRUCTIONS",
]
