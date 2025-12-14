#!/usr/bin/env python3
"""
Import Agent Demo - Read-Write Database Access + CSV Parsing

The ImportAgent can import transactions from CSV files.

Usage:
    cd SpendWise
    uv run testing/seed_data.py    # First seed the database
    uv run testing/import_demo.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from agents import Runner
from mcp_sandbox_openai_sdk import MCPServers

from spendwise import create_import_agent, create_sqlite_mcp_server, CSVParser


PROJECT_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = PROJECT_DIR / "data" / "spendwise.db"
SAMPLE_CSV = PROJECT_DIR / "testing" / "data" / "bank_export.csv"


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
    print("IMPORT AGENT DEMO")
    print("=" * 60)
    print("\nAccess: READ-WRITE (can import transactions)")
    print(f"Database: {DB_PATH}")
    
    # Create READ-WRITE MCP server
    sqlite_mcp = create_sqlite_mcp_server(DB_PATH, readonly=False)
    
    try:
        async with MCPServers(sqlite_mcp) as servers:
            agent = create_import_agent(mcp_servers=servers)
            
            # Check if sample CSV exists
            if SAMPLE_CSV.exists():
                print(f"\nSample CSV found: {SAMPLE_CSV.name}")
                print("Type 'import csv' to import it")
            
            print("\n" + "-" * 60)
            print("Commands:")
            print("  - 'import csv' - Import sample CSV file")
            print("  - 'show import log' - Show import history")
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
                    
                    # Handle CSV import
                    if "import csv" in user_input.lower():
                        if not SAMPLE_CSV.exists():
                            print("\nNo CSV file found. Creating sample...")
                            create_sample_csv()
                        
                        print(f"\nParsing {SAMPLE_CSV.name}...")
                        parser = CSVParser()
                        result = parser.parse_file(SAMPLE_CSV)
                        
                        if not result.success:
                            print(f"Parse error: {result.errors}")
                            continue
                        
                        print(f"Parsed {len(result.transactions)} transactions")
                        
                        # Send to agent for import
                        import_data = {
                            "source": "csv",
                            "filename": result.filename,
                            "transactions": result.to_dict()["transactions"]
                        }
                        
                        prompt = f"""Import these transactions into the database:

{json.dumps(import_data, indent=2)}

IMPORTANT:
1. Categorize each transaction based on description
2. Execute an INSERT INTO transactions for EVERY transaction
3. Log the import in import_log
4. Output summary

Execute the SQL INSERT statements, don't just show them!"""
                        
                        result = await Runner.run(agent, input=prompt)
                        print(f"\nAgent: {result.final_output}")
                    else:
                        result = await Runner.run(agent, input=user_input)
                        print(f"\nAgent: {result.final_output}")
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                    
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure Docker is running.")


def create_sample_csv():
    """Create a sample CSV file for testing"""
    import csv
    from datetime import date, timedelta
    import random
    
    SAMPLE_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    samples = [
        ("MIGROS ZURICH", -42.50),
        ("SBB MOBILE", -25.00),
        ("COOP CITY", -38.90),
        ("STARBUCKS", -7.50),
        ("AMAZON.DE", -65.00),
        ("UBER RIDE", -18.00),
        ("NETFLIX", -12.90),
    ]
    
    today = date.today()
    
    with open(SAMPLE_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount", "currency", "reference"])
        
        for i in range(10):
            desc, amount = random.choice(samples)
            tx_date = today - timedelta(days=random.randint(0, 7))
            writer.writerow([
                tx_date.isoformat(),
                desc,
                f"{amount:.2f}",
                "CHF",
                f"CSV-{i:04d}"
            ])
    
    print(f"Created: {SAMPLE_CSV}")


def main():
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
