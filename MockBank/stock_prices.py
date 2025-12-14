"""
MockBank Stock Prices - Fetch current prices from Yahoo Finance
"""

import yfinance as yf
from typing import Optional


# Cache prices for a short time to avoid too many API calls
_price_cache: dict[str, float] = {}
_exchange_rate_cache: float | None = None


def get_current_price(ticker: str) -> Optional[float]:
    """Get current stock price in USD from Yahoo Finance."""
    ticker = ticker.upper()
    
    # Check cache first
    if ticker in _price_cache:
        return _price_cache[ticker]
    
    try:
        stock = yf.Ticker(ticker)
        # Try to get the current price
        price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice")
        
        if price:
            _price_cache[ticker] = float(price)
            return float(price)
        return None
    except Exception as e:
        print(f"Warning: Could not fetch price for {ticker}: {e}")
        return None


def get_prices_for_tickers(tickers: list[str]) -> dict[str, Optional[float]]:
    """Get current prices for multiple tickers."""
    result = {}
    
    for ticker in tickers:
        result[ticker.upper()] = get_current_price(ticker)
    
    return result


def enrich_stocks_with_prices(stocks: list[dict]) -> list[dict]:
    """
    Add current prices and market values to stock list.
    
    Args:
        stocks: List of stock dicts with ticker, quantity, invested
    
    Returns:
        Enriched stock list with current_price, market_value, gain_loss
    """
    if not stocks:
        return stocks
    
    # Get live exchange rate
    usd_to_chf = get_usd_to_chf_rate()
    
    # Get all tickers
    tickers = [s["ticker"] for s in stocks]
    
    # Fetch prices
    prices = get_prices_for_tickers(tickers)
    
    # Enrich each stock
    enriched = []
    for stock in stocks:
        ticker = stock["ticker"]
        current_price_usd = prices.get(ticker)
        
        if current_price_usd:
            current_price_chf = current_price_usd * usd_to_chf
            market_value = stock["quantity"] * current_price_chf
            gain_loss = market_value - stock["invested"]
            gain_loss_pct = (gain_loss / stock["invested"] * 100) if stock["invested"] > 0 else 0
        else:
            current_price_chf = None
            market_value = None
            gain_loss = None
            gain_loss_pct = None
        
        enriched.append({
            **stock,
            "current_price_usd": current_price_usd,
            "current_price_chf": current_price_chf,
            "market_value": market_value,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "exchange_rate": usd_to_chf,
        })
    
    return enriched


def get_usd_to_chf_rate() -> float:
    """Get current USD/CHF exchange rate from Yahoo Finance."""
    global _exchange_rate_cache
    
    if _exchange_rate_cache is not None:
        return _exchange_rate_cache
    
    try:
        ticker = yf.Ticker("USDCHF=X")
        rate = ticker.info.get("regularMarketPrice") or ticker.info.get("previousClose")
        if rate:
            _exchange_rate_cache = float(rate)
            print(f"Exchange rate: 1 USD = {_exchange_rate_cache:.4f} CHF")
            return _exchange_rate_cache
    except Exception as e:
        print(f"Warning: Could not fetch exchange rate: {e}")
    
    # Fallback to fixed rate
    return 0.88


def get_total_portfolio_value(stocks: list[dict]) -> float:
    """
    Calculate total portfolio market value in CHF.
    
    Args:
        stocks: List of stock dicts with ticker, quantity
    
    Returns:
        Total market value in CHF, or 0 if prices unavailable
    """
    if not stocks:
        return 0.0
    
    usd_to_chf = get_usd_to_chf_rate()
    total = 0.0
    
    for stock in stocks:
        price_usd = get_current_price(stock["ticker"])
        if price_usd:
            total += stock["quantity"] * price_usd * usd_to_chf
    
    return round(total, 2)


def clear_cache():
    """Clear the price cache."""
    global _price_cache, _exchange_rate_cache
    _price_cache = {}
    _exchange_rate_cache = None

