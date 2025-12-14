"""
Combined Travel MCP Server

All travel APIs in one server:
- Amadeus: Flights & Hotels (with fallback)
- OpenWeather: Weather forecasts
- Overpass: Attractions & POIs (OpenStreetMap)

Designed to run in Docker sandbox.
"""

import os
import logging
from typing import Any
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-travel")

# Create MCP server
server = Server("mcp-server-travel")

# API URLs
AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_BASE_URL = "https://test.api.amadeus.com"
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Amadeus token cache
_amadeus_token = None
_token_expires = None


# =============================================================================
# AMADEUS API (Flights & Hotels)
# =============================================================================

async def get_amadeus_token() -> str | None:
    """Get Amadeus OAuth2 token. Returns None on failure."""
    global _amadeus_token, _token_expires
    
    if _amadeus_token and _token_expires and datetime.now() < _token_expires:
        return _amadeus_token
    
    api_key = os.environ.get("AMADEUS_API_KEY")
    api_secret = os.environ.get("AMADEUS_API_SECRET")
    
    if not api_key or not api_secret:
        logger.warning("Amadeus credentials not configured")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                AMADEUS_AUTH_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": api_key,
                    "client_secret": api_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code != 200:
                logger.warning(f"Amadeus auth failed: {response.status_code}")
                return None
            
            data = response.json()
            _amadeus_token = data["access_token"]
            _token_expires = datetime.now()
            return _amadeus_token
            
    except Exception as e:
        logger.warning(f"Amadeus auth error: {e}")
        return None


async def amadeus_request(endpoint: str, params: dict) -> dict | None:
    """Make Amadeus API request. Returns None on failure."""
    token = await get_amadeus_token()
    if not token:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{AMADEUS_BASE_URL}{endpoint}",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
            
            if response.status_code >= 400:
                logger.warning(f"Amadeus API error: {response.status_code}")
                return None
            
            return response.json()
            
    except Exception as e:
        logger.warning(f"Amadeus request error: {e}")
        return None


# =============================================================================
# TOOLS
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all travel tools."""
    return [
        # Flights
        Tool(
            name="search_flights",
            description="Search for flights. Returns live prices or fallback estimate if API unavailable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin IATA code (e.g., ZRH)"},
                    "destination": {"type": "string", "description": "Destination IATA code (e.g., BCN)"},
                    "departure_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "return_date": {"type": "string", "description": "YYYY-MM-DD (optional)"},
                    "adults": {"type": "integer", "default": 1},
                },
                "required": ["origin", "destination", "departure_date"],
            },
        ),
        # Hotels
        Tool(
            name="search_hotels",
            description="Search for hotels. Returns live data or fallback estimate if API unavailable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city_code": {"type": "string", "description": "City IATA code (e.g., BCN)"},
                    "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                    "check_out": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["city_code", "check_in", "check_out"],
            },
        ),
        # Weather
        Tool(
            name="get_weather",
            description="Get weather forecast for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "default": 5},
                },
                "required": ["city"],
            },
        ),
        # Attractions
        Tool(
            name="get_attractions",
            description="Get tourist attractions in a city (OpenStreetMap)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["city"],
            },
        ),
        # Restaurants
        Tool(
            name="get_restaurants",
            description="Get restaurants in a city (OpenStreetMap)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "cuisine": {"type": "string", "description": "Cuisine type (optional)"},
                    "limit": {"type": "integer", "default": 10},
                },
                "required": ["city"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "search_flights":
        return await handle_flights(arguments)
    elif name == "search_hotels":
        return await handle_hotels(arguments)
    elif name == "get_weather":
        return await handle_weather(arguments)
    elif name == "get_attractions":
        return await handle_attractions(arguments)
    elif name == "get_restaurants":
        return await handle_restaurants(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# =============================================================================
# HANDLERS
# =============================================================================

async def handle_flights(args: dict) -> list[TextContent]:
    """Search flights with fallback."""
    origin = args["origin"].upper()
    destination = args["destination"].upper()
    departure = args["departure_date"]
    return_date = args.get("return_date")
    adults = args.get("adults", 1)
    
    logger.info(f"Searching flights: {origin} -> {destination}")
    
    # Try Amadeus API
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure,
        "adults": adults,
        "max": 5,
        "currencyCode": "CHF",
    }
    if return_date:
        params["returnDate"] = return_date
    
    data = await amadeus_request("/v2/shopping/flight-offers", params)
    
    if data and data.get("data"):
        # Live data available
        flights = []
        for offer in data["data"][:3]:
            price = offer.get("price", {})
            itineraries = offer.get("itineraries", [])
            outbound = itineraries[0] if itineraries else {}
            segments = outbound.get("segments", [])
            
            flights.append({
                "price": f"{price.get('total', 'N/A')} {price.get('currency', 'CHF')}",
                "airline": segments[0].get("carrierCode", "N/A") if segments else "N/A",
                "duration": outbound.get("duration", "N/A"),
                "stops": len(segments) - 1 if segments else 0,
            })
        
        result = f"Flights {origin} -> {destination} ({departure}):\n\n"
        for i, f in enumerate(flights, 1):
            result += f"{i}. {f['airline']} - {f['price']}\n"
            result += f"   Duration: {f['duration']}, Stops: {f['stops']}\n\n"
        
        result += "[Live data from Amadeus API]"
        return [TextContent(type="text", text=result)]
    
    else:
        # Fallback estimate
        is_short = origin in ["ZRH", "GVA", "BSL"] and destination in ["BCN", "MAD", "ROM", "BER", "AMS", "VIE", "PRG"]
        price_range = "120-200 CHF" if is_short else "200-400 CHF"
        
        result = f"Flights {origin} -> {destination} ({departure}):\n\n"
        result += f"ESTIMATED PRICE: {price_range} (round trip)\n\n"
        result += "Typical airlines: Vueling, EasyJet, Swiss, Lufthansa\n"
        result += "Duration: 1.5-2.5 hours (direct)\n\n"
        result += "[Fallback estimate - live API unavailable]"
        
        return [TextContent(type="text", text=result)]


async def handle_hotels(args: dict) -> list[TextContent]:
    """Search hotels with fallback."""
    city_code = args["city_code"].upper()
    check_in = args["check_in"]
    check_out = args["check_out"]
    
    logger.info(f"Searching hotels in {city_code}")
    
    # Try Amadeus API
    data = await amadeus_request(
        "/v1/reference-data/locations/hotels/by-city",
        {"cityCode": city_code}
    )
    
    if data and data.get("data"):
        hotels = []
        for hotel in data["data"][:5]:
            hotels.append({
                "name": hotel.get("name", "Unknown"),
                "distance": hotel.get("distance", {}).get("value", "N/A"),
            })
        
        result = f"Hotels in {city_code} ({check_in} to {check_out}):\n\n"
        for i, h in enumerate(hotels, 1):
            result += f"{i}. {h['name']}\n"
            result += f"   Distance from center: {h['distance']} km\n\n"
        
        result += "[Live data from Amadeus API]"
        return [TextContent(type="text", text=result)]
    
    else:
        # Fallback estimate
        tier = "expensive" if city_code in ["ZRH", "GVA", "LHR", "CDG"] else "medium"
        price = "150-250 CHF/night" if tier == "expensive" else "80-150 CHF/night"
        
        result = f"Hotels in {city_code} ({check_in} to {check_out}):\n\n"
        result += f"ESTIMATED PRICE: {price}\n\n"
        result += "Typical options:\n"
        result += "- Budget: Hostels, Airbnb (40-80 CHF)\n"
        result += "- Medium: 3-star hotels (80-150 CHF)\n"
        result += "- Luxury: 4-5 star (150-300+ CHF)\n\n"
        result += "[Fallback estimate - live API unavailable]"
        
        return [TextContent(type="text", text=result)]


async def handle_weather(args: dict) -> list[TextContent]:
    """Get weather forecast."""
    city = args["city"]
    days = min(args.get("days", 5), 5)
    
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return [TextContent(type="text", text="Weather API not configured")]
    
    logger.info(f"Getting weather for {city}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{OPENWEATHER_URL}/forecast",
                params={
                    "q": city,
                    "appid": api_key,
                    "units": "metric",
                    "cnt": days * 8,
                },
            )
            
            if response.status_code != 200:
                return [TextContent(type="text", text=f"Weather not found for {city}")]
            
            data = response.json()
        
        # Group by day
        daily = {}
        for fc in data.get("list", []):
            date = fc["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {"temps": [], "conditions": [], "rain": []}
            daily[date]["temps"].append(fc["main"]["temp"])
            daily[date]["conditions"].append(fc["weather"][0]["description"])
            daily[date]["rain"].append(fc.get("pop", 0) * 100)
        
        city_name = data.get("city", {}).get("name", city)
        result = f"Weather Forecast for {city_name}:\n\n"
        
        for date, day in list(daily.items())[:days]:
            temp_min = min(day["temps"])
            temp_max = max(day["temps"])
            condition = max(set(day["conditions"]), key=day["conditions"].count)
            rain = max(day["rain"])
            
            result += f"{date}: {temp_min:.0f}-{temp_max:.0f}C, {condition}, {rain:.0f}% rain\n"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return [TextContent(type="text", text=f"Weather lookup failed: {e}")]


async def handle_attractions(args: dict) -> list[TextContent]:
    """Get attractions from OpenStreetMap."""
    city = args["city"]
    limit = min(args.get("limit", 10), 15)
    
    logger.info(f"Getting attractions in {city}")
    
    query = f"""
    [out:json][timeout:25];
    area["name"="{city}"]["admin_level"~"[4-8]"]->.city;
    (
      node["tourism"="attraction"](area.city);
      way["tourism"="attraction"](area.city);
      node["historic"](area.city);
    );
    out body {limit};
    """
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                OVERPASS_URL,
                data={"data": query},
            )
            
            if response.status_code != 200:
                return [TextContent(type="text", text=f"Could not find attractions in {city}")]
            
            data = response.json()
        
        elements = data.get("elements", [])
        if not elements:
            return [TextContent(type="text", text=f"No attractions found in {city}")]
        
        result = f"Attractions in {city}:\n\n"
        for i, elem in enumerate(elements[:limit], 1):
            tags = elem.get("tags", {})
            name = tags.get("name", "Unnamed")
            if name == "Unnamed":
                continue
            tourism = tags.get("tourism", tags.get("historic", ""))
            result += f"{i}. {name}"
            if tourism:
                result += f" ({tourism})"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Attractions error: {e}")
        return [TextContent(type="text", text=f"Attractions lookup failed: {e}")]


async def handle_restaurants(args: dict) -> list[TextContent]:
    """Get restaurants from OpenStreetMap."""
    city = args["city"]
    cuisine = args.get("cuisine", "")
    limit = min(args.get("limit", 10), 15)
    
    logger.info(f"Getting restaurants in {city}")
    
    cuisine_filter = f'["cuisine"~"{cuisine}",i]' if cuisine else ""
    
    query = f"""
    [out:json][timeout:25];
    area["name"="{city}"]["admin_level"~"[4-8]"]->.city;
    (
      node["amenity"="restaurant"]{cuisine_filter}(area.city);
    );
    out body {limit};
    """
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                OVERPASS_URL,
                data={"data": query},
            )
            
            if response.status_code != 200:
                return [TextContent(type="text", text=f"Could not find restaurants in {city}")]
            
            data = response.json()
        
        elements = data.get("elements", [])
        if not elements:
            cuisine_text = f" ({cuisine})" if cuisine else ""
            return [TextContent(type="text", text=f"No restaurants{cuisine_text} found in {city}")]
        
        result = f"Restaurants in {city}:\n\n"
        for i, elem in enumerate(elements[:limit], 1):
            tags = elem.get("tags", {})
            name = tags.get("name", "Unnamed")
            if name == "Unnamed":
                continue
            cuisine_tag = tags.get("cuisine", "")
            result += f"{i}. {name}"
            if cuisine_tag:
                result += f" - {cuisine_tag}"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Restaurants error: {e}")
        return [TextContent(type="text", text=f"Restaurants lookup failed: {e}")]


async def serve():
    """Run the MCP server."""
    logger.info("Starting Travel MCP Server...")
    logger.info("APIs: Amadeus (flights/hotels), OpenWeather, Overpass (OSM)")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

