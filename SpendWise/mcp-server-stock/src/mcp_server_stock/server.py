"""
MCP Server for Stock Market Data and Trading

Provides stock market data tools for AI agents:
- Real-time quotes (FMP API)
- Company profiles (FMP API)
- Key metrics and ratios (FMP API)
- Price targets (FMP API)
- Market movers (FMP API)
- Portfolio management (MockBank)
- Buy/Sell stocks (MockBank)
"""

import os
import json
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-stock")

# Create MCP server
server = Server("mcp-server-stock")

# FMP API configuration
FMP_API_KEY = os.environ.get("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"

# MockBank API configuration
MOCKBANK_URL = os.environ.get("MOCKBANK_URL", "http://host.docker.internal:8080")


async def fmp_request(endpoint: str, params: dict = None) -> Any:
    """
    Make a request to the FMP API.
    
    Args:
        endpoint: API endpoint (e.g., "/quote")
        params: Query parameters (apikey added automatically)
    
    Returns:
        JSON response from FMP
    """
    if not FMP_API_KEY:
        raise ValueError("FMP_API_KEY environment variable not set")
    
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params["apikey"] = FMP_API_KEY
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def mockbank_request(method: str, endpoint: str, json_data: dict = None) -> Any:
    """
    Make a request to the MockBank API.
    
    Args:
        method: HTTP method (GET, POST)
        endpoint: API endpoint (e.g., "/api/balance")
        json_data: JSON body for POST requests
    
    Returns:
        JSON response from MockBank
    """
    url = f"{MOCKBANK_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        if method == "GET":
            response = await client.get(url)
        else:
            response = await client.post(url, json=json_data)
        response.raise_for_status()
        return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available FMP tools."""
    return [
        Tool(
            name="get_quote",
            description="Get real-time stock quote (price, change, volume)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="get_profile",
            description="Get company profile (sector, industry, description, CEO)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol",
                    },
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="get_key_metrics",
            description="Get key financial metrics (P/E ratio, ROE, profit margin, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol",
                    },
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="get_price_target",
            description="Get analyst price target summary (average, high, low)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol",
                    },
                },
                "required": ["symbol"],
            },
        ),
        Tool(
            name="search_symbol",
            description="Search for stock symbols by company name",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (company name or partial symbol)",
                    },
                },
                "required": ["query"],
            },
        ),
        # MockBank Tools
        Tool(
            name="get_balance",
            description="Get the current cash balance from MockBank account",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_portfolio",
            description="Get the current stock portfolio from MockBank (all holdings)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="buy_stock",
            description="Buy stocks via MockBank. Creates a transaction and updates portfolio.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL)",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares to buy",
                    },
                    "price": {
                        "type": "number",
                        "description": "Price per share in CHF",
                    },
                },
                "required": ["ticker", "quantity", "price"],
            },
        ),
        Tool(
            name="sell_stock",
            description="Sell stocks via MockBank. Creates a transaction and updates portfolio.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL)",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares to sell",
                    },
                    "price": {
                        "type": "number",
                        "description": "Price per share in CHF",
                    },
                },
                "required": ["ticker", "quantity", "price"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name}")
    
    try:
        if name == "get_quote":
            symbol = arguments["symbol"].upper()
            data = await fmp_request("/quote", {"symbol": symbol})
            
            if data and isinstance(data, list) and len(data) > 0:
                quote = data[0]
                result = {
                    "symbol": quote.get("symbol"),
                    "name": quote.get("name"),
                    "price": quote.get("price"),
                    "change": quote.get("change"),
                    "changePercent": quote.get("changePercentage"),
                    "dayHigh": quote.get("dayHigh"),
                    "dayLow": quote.get("dayLow"),
                    "yearHigh": quote.get("yearHigh"),
                    "yearLow": quote.get("yearLow"),
                    "volume": quote.get("volume"),
                    "marketCap": quote.get("marketCap"),
                    "priceAvg50": quote.get("priceAvg50"),
                    "priceAvg200": quote.get("priceAvg200"),
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "No quote data found"}))]
        
        elif name == "get_profile":
            symbol = arguments["symbol"].upper()
            data = await fmp_request("/profile", {"symbol": symbol})
            
            if data and isinstance(data, list) and len(data) > 0:
                profile = data[0]
                result = {
                    "symbol": profile.get("symbol"),
                    "companyName": profile.get("companyName"),
                    "sector": profile.get("sector"),
                    "industry": profile.get("industry"),
                    "ceo": profile.get("ceo"),
                    "country": profile.get("country"),
                    "exchange": profile.get("exchange"),
                    "marketCap": profile.get("mktCap"),
                    "description": profile.get("description", "")[:500],
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "No profile data found"}))]
        
        elif name == "get_key_metrics":
            symbol = arguments["symbol"].upper()
            data = await fmp_request("/key-metrics", {"symbol": symbol, "limit": 1})
            
            if data and isinstance(data, list) and len(data) > 0:
                metrics = data[0]
                # Calculate P/E from earnings yield (P/E = 1 / earningsYield)
                earnings_yield = metrics.get("earningsYield")
                pe_ratio = round(1 / earnings_yield, 2) if earnings_yield and earnings_yield > 0 else None
                # Convert ROE/ROA to percentage
                roe = metrics.get("returnOnEquity")
                roa = metrics.get("returnOnAssets")
                result = {
                    "symbol": metrics.get("symbol"),
                    "date": metrics.get("date"),
                    "peRatio": pe_ratio,
                    "roe": round(roe * 100, 2) if roe else None,
                    "roa": round(roa * 100, 2) if roa else None,
                    "currentRatio": round(metrics.get("currentRatio", 0), 2),
                    "netDebtToEBITDA": round(metrics.get("netDebtToEBITDA", 0), 2),
                    "marketCap": metrics.get("marketCap"),
                    "enterpriseValue": metrics.get("enterpriseValue"),
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "No metrics data found"}))]
        
        elif name == "get_price_target":
            symbol = arguments["symbol"].upper()
            data = await fmp_request("/price-target-summary", {"symbol": symbol})
            
            if data and isinstance(data, list) and len(data) > 0:
                target = data[0]
                result = {
                    "symbol": target.get("symbol"),
                    "lastMonth": target.get("lastMonth"),
                    "lastMonthAvgPriceTarget": target.get("lastMonthAvgPriceTarget"),
                    "lastQuarter": target.get("lastQuarter"),
                    "lastQuarterAvgPriceTarget": target.get("lastQuarterAvgPriceTarget"),
                    "lastYear": target.get("lastYear"),
                    "lastYearAvgPriceTarget": target.get("lastYearAvgPriceTarget"),
                    "allTime": target.get("allTime"),
                    "allTimeAvgPriceTarget": target.get("allTimeAvgPriceTarget"),
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "No price target data found"}))]
        
        elif name == "search_symbol":
            query = arguments["query"]
            data = await fmp_request("/search-symbol", {"query": query})
            
            if data and isinstance(data, list):
                results = []
                for item in data[:10]:
                    results.append({
                        "symbol": item.get("symbol"),
                        "name": item.get("name"),
                        "exchange": item.get("exchangeShortName"),
                    })
                return [TextContent(type="text", text=json.dumps(results, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "No results found"}))]
        
        # MockBank Tools
        elif name == "get_balance":
            try:
                data = await mockbank_request("GET", "/api/balance")
                return [TextContent(type="text", text=json.dumps(data, indent=2))]
            except Exception as e:
                logger.error(f"MockBank balance error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": f"MockBank not available: {e}"}))]
        
        elif name == "get_portfolio":
            try:
                data = await mockbank_request("GET", "/api/stocks")
                return [TextContent(type="text", text=json.dumps(data, indent=2))]
            except Exception as e:
                logger.error(f"MockBank portfolio error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": f"MockBank not available: {e}"}))]
        
        elif name == "buy_stock":
            ticker = arguments["ticker"].upper()
            quantity = arguments["quantity"]
            price = arguments["price"]
            try:
                data = await mockbank_request("POST", f"/api/stocks/{ticker}/add", {
                    "quantity": quantity,
                    "price": price,
                })
                result = {
                    "action": "BUY",
                    "ticker": ticker,
                    "quantity": quantity,
                    "price": price,
                    "total": round(quantity * price, 2),
                    "result": data,
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"MockBank buy error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": f"Buy failed: {e}"}))]
        
        elif name == "sell_stock":
            ticker = arguments["ticker"].upper()
            quantity = arguments["quantity"]
            price = arguments["price"]
            try:
                data = await mockbank_request("POST", f"/api/stocks/{ticker}/remove", {
                    "quantity": quantity,
                    "price": price,
                })
                result = {
                    "action": "SELL",
                    "ticker": ticker,
                    "quantity": quantity,
                    "price": price,
                    "total": round(quantity * price, 2),
                    "result": data,
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"MockBank sell error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": f"Sell failed: {e}"}))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except httpx.HTTPError as e:
        error_msg = f"FMP API error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=json.dumps({"error": error_msg}))]
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=json.dumps({"error": error_msg}))]


async def serve():
    """Run the MCP server."""
    logger.info("Starting MCP FMP Server...")
    
    if not FMP_API_KEY:
        logger.warning("FMP_API_KEY not set - tools will fail!")
    else:
        logger.info(f"FMP API Key: {FMP_API_KEY[:8]}...{FMP_API_KEY[-4:]}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

