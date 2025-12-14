#!/usr/bin/env python3
"""
Bank Sync Script - Syncs transactions from MockBank to SpendWise

This script:
1. Creates the Import Agent + Insights Agent + MCP at startup (permissions confirmed ONCE)
2. Runs a sync loop every 5 seconds
3. Fetches from MockBank via direct HTTP (no MCP needed)
4. Uses the Import Agent to categorize and save new transactions
5. Uses the Insights Agent to detect suspicious transactions and send SMS alerts

Usage:
    cd SpendWise
    uv run python scripts/bank_sync.py
    
Requirements:
    - MockBank running on localhost:8080
    - SpendWise database initialized
    - OpenAI API key in .env
    - Twilio keys in .env (for SMS alerts)
"""

import asyncio
import os
import sqlite3
import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

# Check for OpenAI key
if not os.environ.get("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set in .env")
    sys.exit(1)

# Configuration
DB_PATH = Path(__file__).parent.parent / "data" / "spendwise.db"
MOCKBANK_URL = os.environ.get("MOCKBANK_URL", "http://localhost:8080")
SYNC_INTERVAL = 5  # seconds


def get_local_references() -> set[str]:
    """Get all transaction references from local SpendWise database."""
    if not DB_PATH.exists():
        print(f"WARNING: Database not found at {DB_PATH}")
        return set()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute("SELECT reference FROM transactions WHERE reference IS NOT NULL")
        refs = {row[0] for row in cursor.fetchall()}
        return refs
    finally:
        conn.close()


def get_local_transaction_count() -> int:
    """Get total transaction count from local database."""
    if not DB_PATH.exists():
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM transactions")
        return cursor.fetchone()[0]
    finally:
        conn.close()


async def fetch_mockbank_transactions() -> list[dict]:
    """
    Fetch all transactions from MockBank via direct HTTP.
    No MCP needed - MockBank is a trusted local service!
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MOCKBANK_URL}/api/transactions")
            response.raise_for_status()
            data = response.json()
            return data.get("transactions", [])
    except httpx.HTTPError as e:
        print(f"[SYNC] MockBank HTTP error: {e}")
        return []
    except Exception as e:
        print(f"[SYNC] Error fetching from MockBank: {e}")
        return []


async def check_for_new_transactions() -> list[dict]:
    """Check MockBank for new transactions not in local DB."""
    local_refs = get_local_references()
    all_transactions = await fetch_mockbank_transactions()
    
    if not all_transactions:
        return []
    
    # Filter to only new transactions (reference not in local DB)
    new_transactions = [
        tx for tx in all_transactions
        if tx.get("reference") and tx.get("reference") not in local_refs
    ]
    
    return new_transactions


async def check_for_deleted_transactions() -> tuple[list[str], bool]:
    """
    Check for transactions that exist locally but NOT in MockBank.
    
    Returns:
        tuple of (deleted_refs, bank_reachable)
        - If bank is unreachable, returns ([], False) - DON'T DELETE!
        - If bank is reachable, returns (refs_to_delete, True)
    """
    local_refs = get_local_references()
    all_transactions = await fetch_mockbank_transactions()
    
    # Safety check: Don't delete if MockBank is unreachable
    # Empty list could mean "offline" not "everything deleted"
    if not all_transactions:
        # If we have local refs but bank returns empty, assume offline
        if local_refs:
            return [], False  # Bank unreachable, skip deletion
        return [], True  # Both empty, that's fine
    
    # Get all references from MockBank
    bank_refs = {tx.get("reference") for tx in all_transactions if tx.get("reference")}
    
    # Find local refs that are NOT in the bank (deleted in bank)
    deleted_refs = [ref for ref in local_refs if ref not in bank_refs]
    
    return deleted_refs, True


def delete_local_transactions(references: list[str]) -> int:
    """Delete transactions from local DB by reference."""
    if not references or not DB_PATH.exists():
        return 0
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # Delete transactions with matching references
        placeholders = ",".join("?" * len(references))
        cursor = conn.execute(
            f"DELETE FROM transactions WHERE reference IN ({placeholders})",
            references
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


async def main():
    """Main sync loop."""
    print("=" * 60)
    print("  SpendWise Bank Sync")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"MockBank: {MOCKBANK_URL}")
    print(f"Sync interval: {SYNC_INTERVAL} seconds")
    print("=" * 60)
    print()
    
    # Check if DB exists
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run: uv run python testing/seed_data.py")
        sys.exit(1)
    
    # Test MockBank connection
    print("[INIT] Testing MockBank connection...")
    test_tx = await fetch_mockbank_transactions()
    if test_tx:
        print(f"[INIT] MockBank OK - {len(test_tx)} transactions available")
    else:
        print("[INIT] WARNING: MockBank not reachable or empty")
        print(f"       Make sure MockBank is running on {MOCKBANK_URL}")
    
    # Initialize Agents with MCP (permissions confirmed once during startup)
    print()
    print("[INIT] Initializing Agents (Import + Insights)...")
    print("[INIT] You will be asked to confirm MCP permissions ONCE.")
    print()
    
    from agents import Runner
    from mcp_sandbox_openai_sdk import MCPServers
    from spendwise.mcp import create_sqlite_mcp_server
    from spendwise.agents import create_import_agent, create_insights_agent
    
    # Create MCP servers
    sqlite_mcp = create_sqlite_mcp_server(DB_PATH, readonly=False)
    
    # Check if SMS is available
    sms_mcp = None
    has_sms = os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN")
    if has_sms:
        from spendwise.mcp import create_sms_mcp_server
        sms_mcp = create_sms_mcp_server()
        print("[INIT] SMS MCP: enabled (Twilio keys found)")
    else:
        print("[INIT] SMS MCP: disabled (no Twilio keys)")
    
    # Build MCP servers list
    servers_list = [sqlite_mcp]
    if sms_mcp:
        servers_list.append(sms_mcp)
    
    # Start MCP context (permissions confirmed during initialization)
    async with MCPServers(*servers_list) as mcp_servers:
        # Create agents (reused for all syncs)
        import_agent = create_import_agent(mcp_servers=mcp_servers)
        insights_agent = create_insights_agent(mcp_servers=mcp_servers) if has_sms else None
        
        print()
        print("[INIT] Import Agent ready!")
        if insights_agent:
            print("[INIT] Insights Agent ready! (will check for suspicious transactions)")
        print("[INIT] Starting sync loop... (Press Ctrl+C to stop)")
        print("=" * 60)
        print()
        
        # Sync loop
        while True:
            try:
                local_count = get_local_transaction_count()
                print(f"[SYNC] Local DB: {local_count} transactions")
                print(f"[SYNC] Checking MockBank...")
                
                # Check for DELETED transactions (in local but not in bank)
                deleted_refs, bank_reachable = await check_for_deleted_transactions()
                
                if not bank_reachable:
                    print("[SYNC] MockBank unreachable - skipping delete check (safety)")
                elif deleted_refs:
                    print(f"[SYNC] Found {len(deleted_refs)} DELETED transactions (removed from bank)")
                    for ref in deleted_refs[:5]:
                        print(f"  - Removing: {ref}")
                    if len(deleted_refs) > 5:
                        print(f"  ... and {len(deleted_refs) - 5} more")
                    
                    deleted_count = delete_local_transactions(deleted_refs)
                    print(f"[SYNC] Removed {deleted_count} transactions from local DB")
                
                # Check for NEW transactions (direct HTTP, no MCP)
                new_transactions = await check_for_new_transactions()
                
                if not new_transactions:
                    print("[SYNC] No new transactions")
                else:
                    print(f"[SYNC] Found {len(new_transactions)} NEW transactions!")
                    
                    # Show what we found
                    for tx in new_transactions[:5]:
                        print(f"  - {tx.get('date')}: {tx.get('description')} | {tx.get('amount')} CHF")
                    if len(new_transactions) > 5:
                        print(f"  ... and {len(new_transactions) - 5} more")
                    
                    # Format for Import Agent - CLEAR separation of fields
                    tx_lines = []
                    for tx in new_transactions:
                        tx_lines.append(f"""
DATE: {tx['date']}
DESCRIPTION: {tx['description']}
AMOUNT: {tx['amount']} {tx.get('currency', 'CHF')}
REFERENCE: {tx['reference']}
---""")
                    tx_text = "\n".join(tx_lines)
                    
                    prompt = f"""
Import these new transactions from MockBank:

{tx_text}

RULES:
1. Use the DESCRIPTION field as-is for the description column
2. Use the AMOUNT field as-is (already has correct sign from MockBank)
3. Use 'bank_api' as source
4. Keep the REFERENCE as-is

STOCK TRANSACTION SIGNS (MockBank already handles this correctly):
- STOCK: +X = BUY = negative amount (money out) - ALREADY CORRECT
- STOCK: -X = SELL = positive amount (money in) - ALREADY CORRECT
- DO NOT change the amount sign!

Execute INSERT OR IGNORE for each transaction.
"""
                    
                    print("[SYNC] Running Import Agent...")
                    result = await Runner.run(import_agent, input=prompt)
                    print(f"[SYNC] Import result:")
                    print(result.final_output[:500] if len(result.final_output) > 500 else result.final_output)
                    print()
                    
                    # Run Insights Agent to check for suspicious transactions
                    if insights_agent and new_transactions:
                        print("[SYNC] Running Insights Agent to check for suspicious activity...")
                        
                        # Format newly imported transactions for analysis
                        tx_summary = "\n".join([
                            f"- {tx.get('date')}: {tx.get('description')} | {tx.get('amount')} CHF"
                            for tx in new_transactions
                        ])
                        
                        insights_prompt = f"""
Analyze these NEWLY IMPORTED transactions for suspicious activity:

{tx_summary}

Check if any of these are suspicious based on:
- Unusual merchants (pawn shops, crypto ATMs, gambling)
- Unusually high amounts compared to typical spending
- Suspicious timing or patterns
- Round suspicious amounts (exactly 1000, 5000 CHF)

If you find something TRULY suspicious, send ONE SMS alert with a funny but concerned message.
If nothing suspicious, just say "All clear - no suspicious transactions detected."

Remember: Normal shopping, dining, or entertainment is NOT suspicious, even if expensive.
"""
                        
                        try:
                            insights_result = await Runner.run(insights_agent, input=insights_prompt)
                            print(f"[SYNC] Insights check:")
                            print(insights_result.final_output[:300] if len(insights_result.final_output) > 300 else insights_result.final_output)
                        except Exception as e:
                            print(f"[SYNC] Insights check failed: {e}")
                        print()
                
            except KeyboardInterrupt:
                print("\n[SYNC] Stopping...")
                break
            except Exception as e:
                print(f"[SYNC] Error: {e}")
            
            print(f"[SYNC] Waiting {SYNC_INTERVAL} seconds...")
            print("-" * 40)
            
            try:
                await asyncio.sleep(SYNC_INTERVAL)
            except KeyboardInterrupt:
                print("\n[SYNC] Stopping...")
                break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
