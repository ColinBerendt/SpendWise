"""
MCP Server for Stock Market Data and Trading

A Model Context Protocol server that provides:
- Stock market data from Financial Modeling Prep API
- Portfolio management via MockBank API
- Buy/Sell stock functionality

Enables AI agents to analyze stocks, check prices, and make investment decisions.
"""

from .server import serve
import asyncio


def main():
    """MCP Stock Server - Market data and trading for AI agents"""
    asyncio.run(serve())


__all__ = ["main", "serve"]
