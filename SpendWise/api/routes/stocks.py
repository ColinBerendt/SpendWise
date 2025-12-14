"""
Stock API Routes - Portfolio management and AI analysis

Connects to:
- MockBank API for portfolio/balance/trading
- FMP MCP Server for stock market data
- Stock Agent for AI analysis
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx

router = APIRouter()

# MockBank API (runs locally)
MOCKBANK_URL = "http://localhost:8080"


class TradeRequest(BaseModel):
    ticker: str
    quantity: int
    price: float


class AnalyzeRequest(BaseModel):
    symbols: list[str]


# ═══════════════════════════════════════════════════════════════
# MOCKBANK ENDPOINTS (Direct HTTP)
# ═══════════════════════════════════════════════════════════════

@router.get("/balance")
async def get_balance():
    """Get current cash balance from MockBank."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{MOCKBANK_URL}/api/balance")
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"MockBank not available: {e}")


@router.get("/portfolio")
async def get_portfolio():
    """Get stock portfolio from MockBank."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{MOCKBANK_URL}/api/stocks")
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"MockBank not available: {e}")


@router.post("/buy")
async def buy_stock(trade: TradeRequest):
    """Buy stocks via MockBank."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{MOCKBANK_URL}/api/stocks/{trade.ticker.upper()}/add",
                json={"quantity": trade.quantity, "price": trade.price}
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"MockBank not available: {e}")


@router.post("/sell")
async def sell_stock(trade: TradeRequest):
    """Sell stocks via MockBank."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{MOCKBANK_URL}/api/stocks/{trade.ticker.upper()}/remove",
                json={"quantity": trade.quantity, "price": trade.price}
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"MockBank not available: {e}")


# ═══════════════════════════════════════════════════════════════
# AI ANALYSIS ENDPOINTS (via Stock Agent)
# ═══════════════════════════════════════════════════════════════

@router.post("/analyze")
async def analyze_stocks(request: Request, body: AnalyzeRequest):
    """Analyze stocks using the Stock Agent."""
    stock_mcp = getattr(request.app.state, 'stock_mcp', None)
    
    if not stock_mcp:
        raise HTTPException(status_code=503, detail="Stock MCP not initialized")
    
    try:
        from agents import Runner
        from spendwise.agents import create_stock_agent
        
        # Create agent with Stock MCP
        stock_agent = create_stock_agent(mcp_servers=[stock_mcp])
        
        # Build analysis prompt with exact format
        symbols_str = ", ".join(body.symbols)
        prompt = f"""Analyze these stocks: {symbols_str}

For EACH stock, call get_quote, get_key_metrics, and get_price_target.
Then output in this EXACT format:

1. AAPL (Apple Inc.)
   Price: $278.78 (-0.68%)
   P/E: 34.1 | ROE: 151.9%
   Target: $288 | Upside: 3.3%
   Verdict: HOLD - Solid position

2. AMZN (Amazon.com Inc.)
   Price: $229.53 (+0.18%)
   P/E: 38.8 | ROE: 20.7%
   Target: $300 | Upside: 30.7%
   Verdict: BUY - Strong growth

Analyze ALL {len(body.symbols)} stocks: {symbols_str}
Do NOT skip any stock. Output data for EVERY symbol."""

        result = await Runner.run(stock_agent, input=prompt)
        
        return {
            "symbols": body.symbols,
            "analysis": result.final_output,
            "success": True
        }
        
    except Exception as e:
        return {
            "symbols": body.symbols,
            "analysis": f"Analysis failed: {str(e)}",
            "success": False
        }


@router.get("/recommendations")
async def get_recommendations(request: Request):
    """Get recommended stocks (market gainers) from FMP."""
    stock_mcp = getattr(request.app.state, 'stock_mcp', None)
    
    if not stock_mcp:
        # Fallback: return static popular stocks
        return {
            "stocks": [
                {"symbol": "NVDA", "name": "NVIDIA Corporation"},
                {"symbol": "META", "name": "Meta Platforms"},
                {"symbol": "TSLA", "name": "Tesla Inc"},
            ],
            "source": "static"
        }
    
    try:
        from agents import Runner
        from spendwise.agents import create_stock_agent
        
        stock_agent = create_stock_agent(mcp_servers=[stock_mcp])
        
        result = await Runner.run(
            stock_agent, 
            input="Get top 3 market gainers today. Just return their symbols and names, nothing else."
        )
        
        # Parse response to extract stocks
        # For now just return static fallback with the analysis
        return {
            "stocks": [
                {"symbol": "NVDA", "name": "NVIDIA Corporation"},
                {"symbol": "META", "name": "Meta Platforms"},
                {"symbol": "TSLA", "name": "Tesla Inc"},
            ],
            "analysis": result.final_output,
            "source": "fmp"
        }
        
    except Exception as e:
        return {
            "stocks": [
                {"symbol": "NVDA", "name": "NVIDIA Corporation"},
                {"symbol": "META", "name": "Meta Platforms"},  
                {"symbol": "TSLA", "name": "Tesla Inc"},
            ],
            "source": "static",
            "error": str(e)
        }


@router.get("/quote/{symbol}")
async def get_quote(request: Request, symbol: str):
    """Get real-time quote for a stock."""
    stock_mcp = getattr(request.app.state, 'stock_mcp', None)
    
    if not stock_mcp:
        raise HTTPException(status_code=503, detail="Stock MCP not initialized")
    
    try:
        from agents import Runner
        from spendwise.agents import create_stock_agent
        
        stock_agent = create_stock_agent(mcp_servers=[stock_mcp])
        
        result = await Runner.run(
            stock_agent,
            input=f"Get the current quote for {symbol.upper()}. Return ONLY: price, change%, and the recommendation (BUY/HOLD/SELL based on price target). Nothing else."
        )
        
        return {
            "symbol": symbol.upper(),
            "data": result.final_output,
            "success": True
        }
        
    except Exception as e:
        return {
            "symbol": symbol.upper(),
            "data": None,
            "error": str(e),
            "success": False
        }

