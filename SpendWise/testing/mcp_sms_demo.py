#!/usr/bin/env python3
"""
MCP SMS Demo - AI Agent with SMS Capabilities (Docker)

The agent can:
- Query budgets in SQLite
- Send custom SMS
- Send budget alerts

Usage:
    cd SpendWise
    uv run testing/seed_data.py
    uv run testing/mcp_sms_demo.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from agents import Runner
from mcp_sandbox_openai_sdk import MCPServers

from spendwise import create_sqlite_mcp_server, create_sms_mcp_server, create_insights_agent

load_dotenv()

PROJECT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = PROJECT_DIR / "data" / "spendwise.db"


async def run_demo():
    # Check environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: Set OPENAI_API_KEY in .env")
        return
    
    if not DB_PATH.exists():
        print("Error: Run 'uv run testing/seed_data.py' first")
        return
    
    # Check Twilio config
    twilio_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    missing = [v for v in twilio_vars if not os.environ.get(v)]
    if missing:
        print(f"Warning: Missing Twilio vars: {', '.join(missing)}")
        print("SMS sending will fail!")
    
    phone = os.environ.get("NOTIFICATION_PHONE", "")
    
    print("\n" + "=" * 60)
    print("  SMS AGENT - Docker Sandbox Demo")
    print("=" * 60)
    print(f"\n  SQLite MCP: Docker (readonly)")
    print(f"  SMS MCP:    Docker (api.twilio.com)")
    print(f"  Default Phone: {phone or 'not set'}")
    print("\n" + "=" * 60)
    
    # Create MCP servers
    sqlite_mcp = create_sqlite_mcp_server(DB_PATH, readonly=True)
    
    try:
        sms_mcp = create_sms_mcp_server()
    except ValueError as e:
        print(f"\nError: {e}")
        return
    
    try:
        async with MCPServers(sqlite_mcp, sms_mcp) as servers:
            agent = create_insights_agent(mcp_servers=servers)
            
            print("\nExamples:")
            print(f"  - 'Send hello to {phone}'" if phone else "  - 'Send hello to +41...'")
            print(f"  - 'Check budgets and alert me'" if phone else "  - 'Check budgets'")
            print("  - 'Remind me via SMS about the meeting'")
            print("  - 'quit' to exit")
            print("-" * 60)
            
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    
                    if user_input.lower() in ["quit", "exit", "q"]:
                        print("Goodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    # Add default phone if user mentions "me"
                    prompt = user_input
                    if phone and any(w in user_input.lower() for w in ["me", "my"]):
                        prompt = f"{user_input} (Phone: {phone})"
                    
                    print("\nAgent working...")
                    result = await Runner.run(agent, input=prompt)
                    print(f"\nAgent: {result.final_output}")
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def main():
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
