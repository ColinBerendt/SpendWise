"""
Travel MCP Server - Combined Travel APIs

All travel APIs in one server:
- Amadeus: Flights & Hotels (with fallback)
- OpenWeather: Weather forecasts
- Overpass: Attractions & POIs (OpenStreetMap)
"""

from .server import serve
import asyncio


def main():
    """MCP Travel Server - Flights, Hotels, Weather, Attractions"""
    asyncio.run(serve())


__all__ = ["main", "serve"]

