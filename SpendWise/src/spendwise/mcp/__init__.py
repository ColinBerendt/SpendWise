"""
MCP Server configuration for SpendWise

Provides sandboxed MCP servers for:
- SQLite: Database access (readonly/readwrite)
- SMS: Twilio SMS via custom mcp-server-sms (Docker)
- Travel: Combined server for Flights, Hotels, Weather, Attractions (Docker)
- Stock: FMP stock data + MockBank trading (Docker)
"""

from .sqlite_server import create_sqlite_mcp_server
from .sms_server import create_sms_mcp_server
from .travel_server import create_travel_mcp_server
from .stock_server import create_stock_mcp_server

__all__ = [
    "create_sqlite_mcp_server",
    "create_sms_mcp_server",
    "create_travel_mcp_server",
    "create_stock_mcp_server",
]
