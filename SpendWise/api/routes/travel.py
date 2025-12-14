"""
Travel API Routes

POST /api/travel/plan - Get travel cost estimate from agent

Uses pre-initialized MCP servers from app.state (permissions confirmed at startup).
"""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    travelers: int = 1
    style: str = "medium"  # budget, medium, luxury


class TravelResponse(BaseModel):
    destination: str
    response: str
    success: bool


@router.post("/plan")
async def plan_trip(request: Request, travel_req: TravelRequest):
    """Get travel cost estimate from Travel Agent."""
    
    # Check if Travel MCP is ready
    travel_mcp = getattr(request.app.state, 'travel_mcp', None)
    if not travel_mcp:
        raise HTTPException(
            status_code=503,
            detail="Travel MCP not initialized. Check OPENWEATHER_API_KEY in .env and restart API."
        )
    
    try:
        from agents import Runner
        from spendwise.agents import create_travel_agent
        
        # Build prompt
        prompt = f"""
        Plan a trip to {travel_req.destination}.
        Dates: {travel_req.start_date} to {travel_req.end_date}
        Travelers: {travel_req.travelers}
        Style: {travel_req.style}
        
        Please provide:
        1. Estimated flight costs
        2. Hotel recommendations and costs
        3. Daily budget estimate
        4. Weather forecast
        5. Top attractions
        6. Total cost estimate
        """
        
        # Create agent with ONLY Travel MCP (no SQLite needed)
        agent = create_travel_agent(mcp_servers=[travel_mcp])
        result = await Runner.run(agent, input=prompt)
        
        return TravelResponse(
            destination=travel_req.destination,
            response=result.final_output,
            success=True,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return TravelResponse(
            destination=travel_req.destination,
            response=f"Error: {str(e)}",
            success=False,
        )


@router.get("/cities")
async def get_popular_cities():
    """Get list of popular travel destinations."""
    return {
        "cities": [
            {"name": "Barcelona", "code": "BCN", "country": "Spain"},
            {"name": "Rome", "code": "FCO", "country": "Italy"},
            {"name": "Paris", "code": "CDG", "country": "France"},
            {"name": "London", "code": "LHR", "country": "UK"},
            {"name": "Amsterdam", "code": "AMS", "country": "Netherlands"},
            {"name": "Berlin", "code": "BER", "country": "Germany"},
            {"name": "Prague", "code": "PRG", "country": "Czech Republic"},
            {"name": "Vienna", "code": "VIE", "country": "Austria"},
            {"name": "Lisbon", "code": "LIS", "country": "Portugal"},
            {"name": "Budapest", "code": "BUD", "country": "Hungary"},
        ]
    }


@router.get("/status")
async def get_travel_status(request: Request):
    """Check if travel API is ready."""
    travel_mcp = getattr(request.app.state, 'travel_mcp', None)
    weather_key = bool(os.environ.get("OPENWEATHER_API_KEY"))
    
    return {
        "ready": travel_mcp is not None,
        "travel_mcp": travel_mcp is not None,
        "weather_api": weather_key,
        "message": "Ready" if travel_mcp else "Travel MCP not initialized (check OPENWEATHER_API_KEY)",
    }
