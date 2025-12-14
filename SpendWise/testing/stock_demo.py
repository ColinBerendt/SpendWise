#!/usr/bin/env python3
"""
Stock Agent Demo - Analyze stocks, manage portfolio, and trade

This demo shows how the Stock Agent:
1. Fetches real-time stock data from FMP
2. Manages portfolio via MockBank
3. Executes buy/sell trades

Usage:
    cd SpendWise
    # First start MockBank: cd ../MockBank && uv run python server.py
    uv run python testing/stock_demo.py
    
Requirements:
    - FMP_API_KEY in .env
    - OPENAI_API_KEY in .env
    - MockBank running on http://localhost:8080
"""

import asyncio
import os
import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

# Check for required keys
if not os.environ.get("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set in .env")
    sys.exit(1)

if not os.environ.get("FMP_API_KEY"):
    print("ERROR: FMP_API_KEY not set in .env")
    print("Get a free key at: https://site.financialmodelingprep.com/developer")
    sys.exit(1)

MOCKBANK_URL = "http://localhost:8080"


async def check_mockbank():
    """Check if MockBank is running."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{MOCKBANK_URL}/api/balance")
            return resp.status_code == 200
    except:
        return False


async def show_account_status():
    """Display current account status from MockBank."""
    try:
        async with httpx.AsyncClient() as client:
            # Get balance
            balance_resp = await client.get(f"{MOCKBANK_URL}/api/balance")
            balance_data = balance_resp.json()
            
            # Get portfolio
            portfolio_resp = await client.get(f"{MOCKBANK_URL}/api/stocks")
            portfolio_data = portfolio_resp.json()
            
            print()
            print("=" * 60)
            print("  ACCOUNT STATUS (MockBank)")
            print("=" * 60)
            print(f"  Cash Balance: {balance_data.get('balance', 0):,.2f} CHF")
            print()
            
            portfolio = portfolio_data.get("portfolio", [])
            if portfolio:
                print("  Portfolio:")
                for stock in portfolio:
                    ticker = stock.get("ticker", "?")
                    qty = stock.get("quantity", 0)
                    invested = stock.get("invested", 0)
                    print(f"    - {ticker}: {qty} shares (invested: {invested:,.2f} CHF)")
            else:
                print("  Portfolio: (empty)")
            print("=" * 60)
            print()
    except Exception as e:
        print(f"  [Could not fetch MockBank status: {e}]")


async def main():
    print()
    print("=" * 60)
    print("  SpendWise Stock Agent Demo")
    print("=" * 60)
    print()
    
    # Check MockBank
    print("[CHECK] MockBank server...")
    if not await check_mockbank():
        print("[ERROR] MockBank not running!")
        print("        Start it first: cd MockBank && uv run python server.py")
        print()
        sys.exit(1)
    print("[CHECK] MockBank OK")
    
    # Show current account status
    await show_account_status()
    
    # Import here to avoid issues if dependencies missing
    from agents import Runner
    from mcp_sandbox_openai_sdk import MCPServers
    from spendwise.mcp import create_stock_mcp_server
    from spendwise.agents import create_stock_agent
    
    print("[INIT] Creating Stock MCP Server (FMP + MockBank)...")
    print("[INIT] You will be asked to confirm permissions.")
    print()
    
    # Create Stock MCP server (FMP API + MockBank trading)
    stock_mcp = create_stock_mcp_server()
    
    # Start MCP context
    async with MCPServers(stock_mcp) as mcp_servers:
        # Create Stock Agent
        stock_agent = create_stock_agent(mcp_servers=mcp_servers)
        
        print()
        print("[INIT] Stock Agent ready!")
        print("=" * 60)
        print()
        print("Examples:")
        print("  - 'Analyze AAPL for me'")
        print("  - 'Show my portfolio'")
        print("  - 'Buy 5 shares of AAPL'")
        print("  - 'Sell all my MSFT'")
        print()
        
        # Interactive mode
        print("Interactive mode - type 'quit' to exit, 'status' to see account")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                if not user_input:
                    continue
                if user_input.lower() == 'status':
                    await show_account_status()
                    continue
                
                print("Processing...")
                result = await Runner.run(stock_agent, input=user_input)
                print(f"\nAgent:\n{result.final_output}")
                
            except KeyboardInterrupt:
                print("\nBye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    # Show final status
    print()
    await show_account_status()


if __name__ == "__main__":
    asyncio.run(main())

