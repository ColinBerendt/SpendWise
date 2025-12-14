# MCP Server Travel

Combined MCP Server for all Travel APIs.

## APIs Included

| API | Purpose | Fallback |
|-----|---------|----------|
| Amadeus | Flights, Hotels | Price estimates |
| OpenWeather | Weather forecasts | - |
| Overpass (OSM) | Attractions, Restaurants | - |

## Tools

### Flights & Hotels (Amadeus)
- `search_flights(origin, destination, date)` - Search flights
- `search_hotels(city_code, check_in, check_out)` - Search hotels

### Weather (OpenWeather)
- `get_weather(city, days)` - Weather forecast

### POIs (OpenStreetMap)
- `get_attractions(city, limit)` - Tourist attractions
- `get_restaurants(city, cuisine, limit)` - Restaurants

## Fallback Behavior

When Amadeus API is unavailable (network issues), the server returns
intelligent estimates based on destination type:

- Short-haul flights (ZRH to EU): 120-200 CHF
- Long-haul flights: 200-400 CHF
- Hotels (expensive cities): 150-250 CHF/night
- Hotels (medium cities): 80-150 CHF/night

## Usage

Runs in Docker sandbox via `mcp-sandbox-openai-sdk`.

