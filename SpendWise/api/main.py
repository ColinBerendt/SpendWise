"""
SpendWise API - FastAPI Backend

Connects the frontend to:
- SQLite database
- AI Agents (via MCP sandbox - permissions confirmed at startup!)

Run:
    cd SpendWise
    uv run uvicorn api.main:app --reload --port 8000
    
    # Confirm permissions when prompted, then frontend will work
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment
load_dotenv()

# Import routes
from api.routes import transactions, budgets, chat, travel, stocks

# Global MCP servers - initialized at startup
_mcp_context = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: Create MCP sandboxes (user confirms permissions here)."""
    global _mcp_context
    
    print("\n" + "=" * 60)
    print("  SpendWise API - Starting")
    print("=" * 60)
    
    db_path = Path(__file__).parent.parent / "data" / "spendwise.db"
    print(f"\nDatabase: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    # Check if we should init MCP (need OpenAI key)
    if os.environ.get("OPENAI_API_KEY"):
        print("\n--- Initializing MCP Sandboxes ---")
        print("Please confirm permissions below...\n")
        
        try:
            from mcp_sandbox_openai_sdk import MCPServers
            from spendwise.mcp import (
                create_sqlite_mcp_server,
                create_travel_mcp_server,
                create_sms_mcp_server,
                create_stock_mcp_server,
            )
            
            # Create TWO SQLite servers for access control:
            # - Read-Only: Spending, Insights, Stock agents
            # - Read-Write: Budget agent (Import agent has own server in bank_sync.py)
            sqlite_readonly = create_sqlite_mcp_server(db_path, readonly=True, name="SQLite (RO)")
            sqlite_readwrite = create_sqlite_mcp_server(db_path, readonly=False, name="SQLite (RW)")
            print("SQLite MCP: RO + RW servers created")
            
            servers_list = [sqlite_readonly, sqlite_readwrite]
            
            # Travel MCP (if weather key is set)
            travel_mcp = None
            if os.environ.get("OPENWEATHER_API_KEY"):
                travel_mcp = create_travel_mcp_server()
                servers_list.append(travel_mcp)
                print("Travel MCP: enabled")
            else:
                print("Travel MCP: disabled (no OPENWEATHER_API_KEY)")
            
            # SMS MCP (if Twilio keys are set)
            sms_mcp = None
            if os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN"):
                sms_mcp = create_sms_mcp_server()
                servers_list.append(sms_mcp)
                print("SMS MCP: enabled")
            else:
                print("SMS MCP: disabled (no TWILIO keys)")
            
            # Stock MCP (if FMP key is set)
            stock_mcp = None
            if os.environ.get("FMP_API_KEY"):
                stock_mcp = create_stock_mcp_server()
                servers_list.append(stock_mcp)
                print("Stock MCP: enabled (FMP + MockBank)")
            else:
                print("Stock MCP: disabled (no FMP_API_KEY)")
            
            # Start the context manager - THIS IS WHERE PERMISSIONS ARE ASKED
            _mcp_context = MCPServers(*servers_list)
            app.state.mcp_servers = await _mcp_context.__aenter__()
            
            # Store individual servers for chat.py access control
            app.state.sqlite_readonly = sqlite_readonly
            app.state.sqlite_readwrite = sqlite_readwrite
            app.state.travel_mcp = travel_mcp
            app.state.sms_mcp = sms_mcp
            app.state.stock_mcp = stock_mcp
            
            print("\n--- MCP Sandboxes Ready! ---")
            
        except Exception as e:
            print(f"\nWarning: MCP init failed: {e}")
            print("Chat/Travel endpoints won't work, but basic API will.\n")
            app.state.mcp_servers = None
    else:
        print("\nWarning: OPENAI_API_KEY not set - AI features disabled")
        app.state.mcp_servers = None
    
    print("\n" + "=" * 60)
    print("  API Ready: http://localhost:8000")
    print("  Docs:      http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    yield  # Server runs here
    
    # Shutdown
    print("\nShutting down MCP sandboxes...")
    if _mcp_context:
        await _mcp_context.__aexit__(None, None, None)


# Create app
app = FastAPI(
    title="SpendWise API",
    description="AI-powered personal finance assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(travel.router, prefix="/api/travel", tags=["Travel"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])


@app.get("/")
async def root():
    """Health check."""
    return {
        "status": "ok",
        "service": "SpendWise API",
        "version": "0.1.0",
        "mcp_ready": hasattr(app.state, 'mcp_servers') and app.state.mcp_servers is not None,
    }


@app.get("/api/health")
async def health():
    """Health check with details."""
    db_path = Path(__file__).parent.parent / "data" / "spendwise.db"
    return {
        "status": "ok",
        "database": str(db_path),
        "database_exists": db_path.exists(),
        "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "mcp_ready": hasattr(app.state, 'mcp_servers') and app.state.mcp_servers is not None,
    }
