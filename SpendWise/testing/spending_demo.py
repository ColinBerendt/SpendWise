#!/usr/bin/env python3
"""
Spending Agent Demo - Read-Only Database Access

The SpendingAgent can query transactions but cannot modify data.

Usage:
    cd SpendWise
    uv run testing/seed_data.py    # First seed the database
    uv run testing/spending_demo.py
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

from spendwise import create_spending_agent, create_sqlite_mcp_server


PROJECT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = PROJECT_DIR / "data" / "spendwise.db"


async def run_demo():
    load_dotenv()
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY in .env file")
        return
    
    if not DB_PATH.exists():
        print(f"Error: Database not found: {DB_PATH}")
        print("Run: uv run testing/seed_data.py")
        return
    
    print("\n" + "=" * 60)
    print("SPENDING AGENT DEMO")
    print("=" * 60)
    print("\nAccess: READ-ONLY (can query, cannot modify)")
    print(f"Database: {DB_PATH}")
    
    # Create READ-ONLY MCP server
    sqlite_mcp = create_sqlite_mcp_server(DB_PATH, readonly=True)
    
    try:
        async with MCPServers(sqlite_mcp) as servers:
            agent = create_spending_agent(mcp_servers=servers)
            
            print("\n" + "-" * 60)
            print("Try these commands:")
            print("  - 'How much did I spend this month?'")
            print("  - 'Show my top 5 expenses'")
            print("  - 'What did I spend on food?'")
            print("  - 'Compare this week to last week'")
            print("  - Type 'quit' to exit")
            print("-" * 60)
            
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("Goodbye!")
                        break
                    if not user_input:
                        continue
                    
                    result = await Runner.run(agent, input=user_input)
                    print(f"\nAgent: {result.final_output}")
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                    
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure Docker is running.")


def main():
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()

