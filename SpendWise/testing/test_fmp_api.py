#!/usr/bin/env python3
"""
FMP API Test Script (NEW STABLE ENDPOINTS)

Tests the new /stable/ endpoints from FMP.
Docs: https://site.financialmodelingprep.com/developer/docs

Usage:
    1. Add FMP_API_KEY to .env
    2. Run: uv run testing/test_fmp_api.py
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/stable"

if not API_KEY:
    print("Error: Set FMP_API_KEY in .env file")
    print("Get your free key at: https://site.financialmodelingprep.com/developer")
    exit(1)


def test_endpoint(name: str, url: str):
    """Test an API endpoint and show result."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url.replace(API_KEY, 'API_KEY')}")
    print("-" * 60)
    
    try:
        response = httpx.get(url, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"Status: OK (got {len(data)} items)")
                if data:
                    # Show first item nicely
                    first = data[0]
                    if isinstance(first, dict):
                        for k, v in list(first.items())[:5]:
                            print(f"  {k}: {v}")
                    else:
                        print(f"  {first}")
            elif isinstance(data, dict):
                if "Error Message" in data:
                    print(f"Status: ERROR - {data['Error Message']}")
                else:
                    print(f"Status: OK")
                    for k, v in list(data.items())[:5]:
                        print(f"  {k}: {v}")
            else:
                print(f"Status: OK")
                print(f"Data: {str(data)[:200]}")
        else:
            print(f"Status: FAILED ({response.status_code})")
            try:
                err = response.json()
                print(f"Error: {err.get('Error Message', response.text[:200])}")
            except:
                print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Status: ERROR - {e}")


def main():
    print("=" * 60)
    print("FMP API Test (NEW STABLE ENDPOINTS)")
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print("=" * 60)
    
    # NEW STABLE ENDPOINTS
    tests = [
        # === SEARCH ===
        ("Search Symbol", f"{BASE_URL}/search-symbol?query=AAPL&apikey={API_KEY}"),
        ("Search Name", f"{BASE_URL}/search-name?query=Apple&apikey={API_KEY}"),
        
        # === COMPANY INFO ===
        ("Company Profile", f"{BASE_URL}/profile?symbol=AAPL&apikey={API_KEY}"),
        
        # === STOCK DIRECTORY ===
        ("Stock List (sample)", f"{BASE_URL}/stock-list?apikey={API_KEY}"),
        ("ETF List", f"{BASE_URL}/etf-list?apikey={API_KEY}"),
        ("Actively Trading", f"{BASE_URL}/actively-trading-list?apikey={API_KEY}"),
        
        # === STOCK SCREENER ===
        ("Stock Screener", f"{BASE_URL}/company-screener?sector=Technology&limit=5&apikey={API_KEY}"),
        
        # === QUOTE ===
        ("Quote", f"{BASE_URL}/quote?symbol=AAPL&apikey={API_KEY}"),
        ("Quote Short", f"{BASE_URL}/quote-short?symbol=AAPL&apikey={API_KEY}"),
        ("Full Quote", f"{BASE_URL}/full-quote?symbol=AAPL&apikey={API_KEY}"),
        
        # === FINANCIAL STATEMENTS ===
        ("Income Statement", f"{BASE_URL}/income-statement?symbol=AAPL&limit=1&apikey={API_KEY}"),
        ("Balance Sheet", f"{BASE_URL}/balance-sheet-statement?symbol=AAPL&limit=1&apikey={API_KEY}"),
        ("Cash Flow", f"{BASE_URL}/cash-flow-statement?symbol=AAPL&limit=1&apikey={API_KEY}"),
        
        # === KEY METRICS ===
        ("Key Metrics", f"{BASE_URL}/key-metrics?symbol=AAPL&limit=1&apikey={API_KEY}"),
        ("Ratios", f"{BASE_URL}/ratios?symbol=AAPL&limit=1&apikey={API_KEY}"),
        ("Financial Growth", f"{BASE_URL}/financial-growth?symbol=AAPL&limit=1&apikey={API_KEY}"),
        
        # === HISTORICAL PRICES ===
        ("Historical Daily", f"{BASE_URL}/historical-price-eod/full?symbol=AAPL&apikey={API_KEY}"),
        ("Historical Intraday", f"{BASE_URL}/historical-chart/1hour?symbol=AAPL&apikey={API_KEY}"),
        
        # === MARKET DATA ===
        ("Market Gainers", f"{BASE_URL}/gainers?apikey={API_KEY}"),
        ("Market Losers", f"{BASE_URL}/losers?apikey={API_KEY}"),
        ("Most Active", f"{BASE_URL}/most-actives?apikey={API_KEY}"),
        ("Sector Performance", f"{BASE_URL}/sector-performance?apikey={API_KEY}"),
        
        # === NEWS ===
        ("Stock News", f"{BASE_URL}/news?symbol=AAPL&limit=5&apikey={API_KEY}"),
        ("General News", f"{BASE_URL}/news?limit=5&apikey={API_KEY}"),
        ("Press Releases", f"{BASE_URL}/press-releases?symbol=AAPL&limit=3&apikey={API_KEY}"),
        
        # === ANALYST DATA ===
        ("Price Target", f"{BASE_URL}/price-target?symbol=AAPL&apikey={API_KEY}"),
        ("Price Target Summary", f"{BASE_URL}/price-target-summary?symbol=AAPL&apikey={API_KEY}"),
        ("Analyst Estimates", f"{BASE_URL}/analyst-estimates?symbol=AAPL&apikey={API_KEY}"),
        ("Upgrades/Downgrades", f"{BASE_URL}/upgrades-downgrades?symbol=AAPL&apikey={API_KEY}"),
        
        # === EARNINGS ===
        ("Earnings Calendar", f"{BASE_URL}/earnings-calendar?apikey={API_KEY}"),
        ("Earnings Surprises", f"{BASE_URL}/earnings-surprises?symbol=AAPL&apikey={API_KEY}"),
        
        # === DIVIDENDS ===
        ("Dividend Calendar", f"{BASE_URL}/dividend-calendar?apikey={API_KEY}"),
        ("Historical Dividends", f"{BASE_URL}/historical-price-dividend?symbol=AAPL&apikey={API_KEY}"),
        
        # === OTHER ===
        ("Stock Peers", f"{BASE_URL}/peers?symbol=AAPL&apikey={API_KEY}"),
        ("DCF", f"{BASE_URL}/dcf?symbol=AAPL&apikey={API_KEY}"),
        ("Rating", f"{BASE_URL}/rating?symbol=AAPL&apikey={API_KEY}"),
        
        # === AVAILABLE LISTS ===
        ("Available Exchanges", f"{BASE_URL}/available-exchanges?apikey={API_KEY}"),
        ("Available Sectors", f"{BASE_URL}/available-sectors?apikey={API_KEY}"),
        ("Available Industries", f"{BASE_URL}/available-industries?apikey={API_KEY}"),
    ]
    
    ok_count = 0
    fail_count = 0
    
    for name, url in tests:
        test_endpoint(name, url)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nCheck above for which endpoints work with your API key.")
    print("Free tier may have limited access.")


if __name__ == "__main__":
    main()
