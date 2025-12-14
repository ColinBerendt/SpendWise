"""
Chat API Routes

POST /api/chat - Send message to Orchestrator Agent
GET  /api/chat/agents - List available agents

The Orchestrator routes requests to specialized sub-agents via handoffs.
"""

import re
import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class AgentUsed(BaseModel):
    id: str
    name: str
    icon: str
    color: str


class ChatMetadata(BaseModel):
    agents_used: list[AgentUsed]
    tools: list[dict]
    execution_time: float


class ChatResponse(BaseModel):
    message: str
    metadata: Optional[ChatMetadata]


# Agent display info
AGENT_INFO = {
    "orchestrator": {"name": "Orchestrator", "icon": "brain", "color": "purple"},
    "spending": {"name": "Spending Agent", "icon": "search", "color": "blue"},
    "spendingagent": {"name": "Spending Agent", "icon": "search", "color": "blue"},
    "budget": {"name": "Budget Agent", "icon": "wallet", "color": "green"},
    "budgetagent": {"name": "Budget Agent", "icon": "wallet", "color": "green"},
    "travel": {"name": "Travel Agent", "icon": "plane", "color": "teal"},
    "travelagent": {"name": "Travel Agent", "icon": "plane", "color": "teal"},
    "insights": {"name": "Insights Agent", "icon": "chart", "color": "amber"},
    "insightsagent": {"name": "Insights Agent", "icon": "chart", "color": "amber"},
    "sms": {"name": "SMS Agent", "icon": "phone", "color": "rose"},
    "stock": {"name": "Stock Agent", "icon": "trending", "color": "emerald"},
    "stockagent": {"name": "Stock Agent", "icon": "trending", "color": "emerald"},
}


def format_travel_response(response: str) -> str:
    """
    Convert structured travel response to readable markdown.
    
    Looks for ===TRAVEL_RESPONSE_START=== and ===TRAVEL_RESPONSE_END===
    and formats the content nicely.
    """
    travel_match = re.search(
        r'===TRAVEL_RESPONSE_START===\s*(.*?)\s*===TRAVEL_RESPONSE_END===',
        response,
        re.DOTALL
    )
    
    if not travel_match:
        return response
    
    content = travel_match.group(1).strip()
    
    # Parse fields
    fields = {}
    for line in content.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('HIGHLIGHT'):
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip()
        elif line.startswith('HIGHLIGHT'):
            key = line.split(':')[0].strip()
            value = ':'.join(line.split(':')[1:]).strip()
            fields[key] = value
    
    # Build formatted response
    dest = fields.get('DESTINATION', 'Unknown')
    dates = fields.get('DATES', '')
    nights = fields.get('NIGHTS', '')
    
    flights_price = fields.get('FLIGHTS_PRICE', 'N/A')
    flights_info = fields.get('FLIGHTS_INFO', '')
    
    hotel_price = fields.get('HOTEL_PRICE', 'N/A')
    hotel_info = fields.get('HOTEL_INFO', '')
    hotel_list = fields.get('HOTEL_LIST', '')
    
    daily_budget = fields.get('DAILY_BUDGET', 'N/A')
    daily_info = fields.get('DAILY_INFO', '')
    onsite_total = fields.get('ONSITE_TOTAL', 'N/A')
    
    total_cost = fields.get('TOTAL_COST', 'N/A')
    
    weather_temp = fields.get('WEATHER_TEMP', 'N/A')
    weather_info = fields.get('WEATHER_INFO', '')
    
    recommendation = fields.get('RECOMMENDATION', '')
    
    # Get highlights
    highlights = []
    for i in range(1, 6):
        h = fields.get(f'HIGHLIGHT_{i}', '')
        if h:
            highlights.append(h)
    
    # Format as clean text (no markdown tables - they don't render well)
    hotel_names = ', '.join(hotel_list.split(', ')[:5]) if hotel_list else 'N/A'
    
    formatted = f"""## Trip to {dest}

**Dates:** {dates} ({nights} nights)

---

### Costs

**Flights:** {flights_price}
{flights_info}

**Hotel:** {hotel_price}
{hotel_info}

**On-site:** {onsite_total}
{daily_budget}/day - {daily_info}

**Total: {total_cost}**

---

### Hotel Options
{hotel_names}

---

### Weather
**{weather_temp}** - {weather_info}

---

### Top Attractions
"""
    for i, h in enumerate(highlights, 1):
        formatted += f"{i}. {h}\n"
    
    if recommendation:
        formatted += f"\n---\n\n*{recommendation}*"
    
    # Get any content before and after the travel block
    before = response[:travel_match.start()].strip()
    after = response[travel_match.end():].strip()
    
    # Remove DATA SOURCES section if present
    after = re.sub(r'DATA SOURCES:.*', '', after, flags=re.DOTALL).strip()
    
    result = ""
    if before:
        result += before + "\n\n"
    result += formatted
    if after:
        result += "\n\n" + after
    
    return result


def parse_metadata(response: str, last_agent: str = None) -> tuple[str, ChatMetadata | None]:
    """
    Extract metadata block from agent response.
    
    Returns:
        tuple of (clean_message, metadata)
    """
    # Look for metadata block
    metadata_match = re.search(
        r'===CHAT_METADATA_START===\s*(.*?)\s*===CHAT_METADATA_END===',
        response,
        re.DOTALL
    )
    
    agents_used = []
    tools = []
    
    if metadata_match:
        # Extract clean message (without metadata)
        clean_message = response[:metadata_match.start()].strip()
        metadata_content = metadata_match.group(1)
        
        # Parse agents
        agents_match = re.search(r'AGENTS:\s*(.+)', metadata_content)
        if agents_match:
            agent_ids = [a.strip().lower() for a in agents_match.group(1).split(',')]
            for agent_id in agent_ids:
                if agent_id in AGENT_INFO:
                    info = AGENT_INFO[agent_id]
                    agents_used.append(AgentUsed(
                        id=agent_id,
                        name=info["name"],
                        icon=info["icon"],
                        color=info["color"],
                    ))
        
        # Parse tools
        tools_match = re.search(r'TOOLS:\s*(.+)', metadata_content)
        if tools_match:
            tool_parts = tools_match.group(1).split(',')
            for part in tool_parts:
                part = part.strip()
                if ':' in part:
                    tool_name, count = part.split(':')
                    try:
                        tools.append({"tool": tool_name.strip(), "count": int(count.strip())})
                    except ValueError:
                        tools.append({"tool": tool_name.strip(), "count": 1})
                else:
                    tools.append({"tool": part, "count": 1})
    else:
        clean_message = response.strip()
    
    # If no agents found in metadata, use last_agent info
    if not agents_used:
        # Always add orchestrator
        agents_used.append(AgentUsed(
            id="orchestrator",
            name="Orchestrator",
            icon="brain",
            color="purple",
        ))
        # Add the specialist agent if known
        if last_agent and last_agent.lower() in AGENT_INFO:
            info = AGENT_INFO[last_agent.lower()]
            agents_used.append(AgentUsed(
                id=last_agent.lower(),
                name=info["name"],
                icon=info["icon"],
                color=info["color"],
            ))
    
    metadata = ChatMetadata(
        agents_used=agents_used,
        tools=tools,
        execution_time=0,
    )
    
    return clean_message, metadata


@router.post("")
async def chat(request: Request, chat_req: ChatRequest):
    """
    Send a message to the Orchestrator Agent.
    
    The Orchestrator classifies the request and hands off to specialized agents:
    - SpendingAgent: transaction analysis (READ-ONLY)
    - BudgetAgent: budget management (READ+WRITE)
    - InsightsAgent: trends and comparisons (READ-ONLY)
    - TravelAgent: trip planning (READ + external APIs)
    """
    
    # Check if MCP is ready
    if not getattr(request.app.state, 'mcp_servers', None):
        raise HTTPException(
            status_code=503, 
            detail="MCP servers not initialized. Restart API and confirm permissions."
        )
    
    # Get individual MCP servers for access control
    sqlite_ro = getattr(request.app.state, 'sqlite_readonly', None)
    sqlite_rw = getattr(request.app.state, 'sqlite_readwrite', None)
    travel_mcp = getattr(request.app.state, 'travel_mcp', None)
    sms_mcp = getattr(request.app.state, 'sms_mcp', None)
    stock_mcp = getattr(request.app.state, 'stock_mcp', None)
    
    if not sqlite_ro or not sqlite_rw:
        raise HTTPException(
            status_code=503,
            detail="SQLite MCP servers not available."
        )
    
    start_time = time.time()
    
    try:
        from agents import Runner
        from spendwise.agents import (
            create_orchestrator_agent,
            create_spending_agent,
            create_budget_agent,
            create_insights_agent,
            create_travel_agent,
            create_stock_agent,
        )
        
        # Create sub-agents with ACCESS CONTROL:
        # READ-ONLY agents get sqlite_ro
        spending_agent = create_spending_agent(mcp_servers=[sqlite_ro])
        
        # Insights gets RO + SMS (for anomaly alerts)
        insights_servers = [sqlite_ro] + ([sms_mcp] if sms_mcp else [])
        insights_agent = create_insights_agent(mcp_servers=insights_servers)
        
        # Stock gets RO + FMP
        stock_servers = [sqlite_ro] + ([stock_mcp] if stock_mcp else [])
        stock_agent = create_stock_agent(mcp_servers=stock_servers)
        
        # Travel only needs Travel MCP (no SQLite)
        travel_servers = [travel_mcp] if travel_mcp else []
        travel_agent = create_travel_agent(mcp_servers=travel_servers)
        
        # READ-WRITE agent: Budget can modify budgets
        budget_agent = create_budget_agent(mcp_servers=[sqlite_rw])
        
        # Create orchestrator with handoffs (no direct MCP access - routes to sub-agents)
        orchestrator = create_orchestrator_agent(
            mcp_servers=[],  # Orchestrator only routes, doesn't access DB directly
            spending_agent=spending_agent,
            budget_agent=budget_agent,
            insights_agent=insights_agent,
            travel_agent=travel_agent,
            stock_agent=stock_agent,
        )
        
        # Run the agent
        result = await Runner.run(orchestrator, input=chat_req.message)
        
        execution_time = round(time.time() - start_time, 2)
        
        # Get the last agent that responded (for metadata)
        last_agent = None
        if hasattr(result, 'last_agent') and result.last_agent:
            last_agent = result.last_agent.name
        
        # Format travel response if present
        formatted_output = format_travel_response(result.final_output)
        
        # Parse response and metadata
        clean_message, metadata = parse_metadata(formatted_output, last_agent)
        
        if metadata:
            metadata.execution_time = execution_time
        
        return ChatResponse(
            message=clean_message,
            metadata=metadata,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents(request: Request):
    """List available agents and their status."""
    mcp_ready = getattr(request.app.state, 'mcp_servers', None) is not None
    
    # Only show main agents (not duplicates)
    main_agents = ["orchestrator", "spending", "budget", "insights", "travel", "stock", "sms"]
    
    agents = []
    for agent_id in main_agents:
        if agent_id in AGENT_INFO:
            info = AGENT_INFO[agent_id]
            agents.append({
                "id": agent_id,
                "name": info["name"],
                "icon": info["icon"],
                "color": info["color"],
                "available": mcp_ready,
            })
    
    return {
        "mcp_ready": mcp_ready,
        "agents": agents,
    }
