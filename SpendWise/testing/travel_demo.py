#!/usr/bin/env python3
"""
Travel Planning Demo

Demonstrates the Travel Agent with COMBINED Travel MCP Server:
- Flight search (Amadeus API - with fallback)
- Hotel search (Amadeus API - with fallback)
- Weather forecasts (OpenWeather API)
- Attractions & POIs (Overpass/OpenStreetMap)
- Budget analysis (SQLite)

All in ONE Docker sandbox container!

Usage:
    uv run testing/travel_demo.py

Required environment variables:
    OPENAI_API_KEY
    OPENWEATHER_API_KEY
    
Optional (has fallback):
    AMADEUS_API_KEY
    AMADEUS_API_SECRET
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from agents import Runner
from mcp_sandbox_openai_sdk import MCPServers

from spendwise.mcp import (
    create_sqlite_mcp_server,
    create_travel_mcp_server,  # Combined server for all travel APIs
)
from spendwise.agents import create_travel_agent

# Load environment variables
load_dotenv()

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "spendwise.db"


def check_env_vars():
    """Check required environment variables."""
    required = [
        "OPENAI_API_KEY",
        "OPENWEATHER_API_KEY",
    ]
    
    optional = [
        "AMADEUS_API_KEY",
        "AMADEUS_API_SECRET",
    ]
    
    missing = [var for var in required if not os.environ.get(var)]
    
    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        return False
    
    # Check optional
    missing_optional = [var for var in optional if not os.environ.get(var)]
    if missing_optional:
        print("Warning: Amadeus credentials not set - will use fallback estimates")
        print(f"  Missing: {', '.join(missing_optional)}")
        print()
    
    return True


async def run_travel_demo():
    """Run the travel planning demo."""
    
    print("=" * 60)
    print("SpendWise Travel Planning Demo")
    print("=" * 60)
    print()
    
    # Check environment
    if not check_env_vars():
        return
    
    # Check database
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        print("Run 'uv run testing/seed_data.py' first")
        return
    
    print("Creating MCP Servers...")
    print()
    
    # Create MCP servers
    sqlite_mcp = create_sqlite_mcp_server(DB_PATH, readonly=True)
    travel_mcp = create_travel_mcp_server()  # Combined: Amadeus + Weather + Overpass
    
    print("MCP Servers:")
    print("  - SQLite (readonly) -> Local database")
    print("  - Travel (combined) -> Amadeus + OpenWeather + Overpass")
    print()
    
    # Connect servers
    async with MCPServers(sqlite_mcp, travel_mcp) as servers:
        print("All servers connected!")
        print()
        
        # Create agent
        agent = create_travel_agent(mcp_servers=servers)
        
        # Demo scenarios
        scenarios = [
            "What would a weekend trip to Barcelona cost? I would travel next week Friday to Sunday.",
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print("-" * 60)
            print(f"Scenario {i}: {scenario}")
            print("-" * 60)
            print()
            
            result = await Runner.run(agent, input=scenario)
            
            print("Travel Agent:")
            print(result.final_output)
            print()
    
    print("=" * 60)
    print("Demo complete!")


def main():
    """Entry point."""
    asyncio.run(run_travel_demo())


if __name__ == "__main__":
    main()
