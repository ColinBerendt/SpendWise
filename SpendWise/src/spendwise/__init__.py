"""
SpendWise - AI-powered spending analysis with MCP sandbox

A modular library for building AI agents that can interact with
financial data through sandboxed MCP servers.
"""

__version__ = "0.1.0"

# Agents
from .agents import (
    create_spending_agent,
    create_import_agent,
    create_budget_agent,
    create_insights_agent,
    SPENDING_INSTRUCTIONS,
    IMPORT_INSTRUCTIONS,
    BUDGET_INSTRUCTIONS,
    INSIGHTS_INSTRUCTIONS,
)

# MCP Servers
from .mcp import create_sqlite_mcp_server, create_sms_mcp_server

# Config
from .config import Settings, get_settings

# Utils
from .utils import (
    CSVParser,
    ParsedTransaction,
    ParseResult,
    CSVFormat,
)

__all__ = [
    # Agents
    "create_spending_agent",
    "create_import_agent",
    "create_budget_agent",
    "create_insights_agent",
    "SPENDING_INSTRUCTIONS",
    "IMPORT_INSTRUCTIONS",
    "BUDGET_INSTRUCTIONS",
    "INSIGHTS_INSTRUCTIONS",
    # MCP
    "create_sqlite_mcp_server",
    "create_sms_mcp_server",
    # Config
    "Settings",
    "get_settings",
    # Utils
    "CSVParser",
    "ParsedTransaction",
    "ParseResult",
    "CSVFormat",
]
