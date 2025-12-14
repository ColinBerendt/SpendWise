"""
Travel MCP Server - Docker Sandbox Configuration

Combined server for all Travel APIs:
- Amadeus (Flights & Hotels) - with fallback
- OpenWeather (Weather)
- Overpass (Attractions, POIs)

One server instead of three = simpler, faster startup.
"""

import os
from pathlib import Path
from ipaddress import IPv4Address
from mcp_sandbox_openai_sdk import (
    DevMCPManifest,
    DomainPort,
    HostPort,
    EnvironmentVariable,
    Permission,
    Registry,
    SandboxedMCPStdio,
)

# Path to our local Travel MCP server
TRAVEL_SERVER_PATH = Path(__file__).parent.parent.parent.parent / "mcp-server-travel"


# Travel MCP Server manifest for local development
travel_manifest = DevMCPManifest(
    name="Travel API Server",
    description="Flights, Hotels, Weather, Attractions - all in one",
    registry=Registry.PYPI,
    package_name="mcp-server-travel",
    permissions=[
        Permission.MCP_AC_NETWORK_CLIENT,
        Permission.MCP_AC_SYSTEM_ENV_READ,
    ],
    code_mount=str(TRAVEL_SERVER_PATH.resolve()),
    exec_command="sh -c 'pip install -q --break-system-packages /sandbox >&2 && python3 -m mcp_server_travel'",
)


def create_travel_mcp_server(
    name: str = "Travel",
) -> SandboxedMCPStdio:
    """
    Create a sandboxed Travel MCP server.
    
    Combines all travel APIs:
    - Amadeus (flights, hotels) - may fail due to IP rotation, has fallback
    - OpenWeather (weather) - stable
    - Overpass (attractions) - stable, no API key needed
    
    Required environment variables:
    - AMADEUS_API_KEY (optional - fallback if missing)
    - AMADEUS_API_SECRET (optional - fallback if missing)
    - OPENWEATHER_API_KEY
    
    Returns:
        SandboxedMCPStdio instance
    """
    # Check OpenWeather (required)
    if not os.environ.get("OPENWEATHER_API_KEY"):
        raise ValueError("Missing OPENWEATHER_API_KEY environment variable")
    
    # Amadeus is optional (has fallback)
    has_amadeus = bool(os.environ.get("AMADEUS_API_KEY") and os.environ.get("AMADEUS_API_SECRET"))
    if not has_amadeus:
        print("Warning: Amadeus credentials not set - will use fallback estimates")
    
    # Ensure server path exists
    if not TRAVEL_SERVER_PATH.exists():
        raise FileNotFoundError(f"Travel server not found at {TRAVEL_SERVER_PATH}")
    
    runtime_perms = [
        # === Amadeus API ===
        DomainPort(domain="test.api.amadeus.com", port=443),
        DomainPort(domain="api.amadeus.com", port=443),
        DomainPort(domain="amadeus-self-service-test.apigee.net", port=443),
        DomainPort(domain="amadeus-self-service.dn.apigee.net", port=443),
        
        # Known Amadeus IPs (AWS EU - discovered via testing/discover_amadeus_ips.py)
        HostPort(host=IPv4Address("3.72.68.174"), port=443),
        HostPort(host=IPv4Address("3.120.238.1"), port=443),
        HostPort(host=IPv4Address("3.254.195.161"), port=443),   # NEW
        HostPort(host=IPv4Address("18.158.72.68"), port=443),
        HostPort(host=IPv4Address("18.193.119.72"), port=443),
        HostPort(host=IPv4Address("18.194.228.233"), port=443),
        HostPort(host=IPv4Address("34.241.251.57"), port=443),   # NEW
        HostPort(host=IPv4Address("35.159.123.231"), port=443),
        HostPort(host=IPv4Address("63.179.6.145"), port=443),
        
        # === OpenWeather API ===
        DomainPort(domain="api.openweathermap.org", port=443),
        
        # === Overpass API (OpenStreetMap) ===
        DomainPort(domain="overpass-api.de", port=443),
        
        # === PyPI for pip install ===
        DomainPort(domain="pypi.org", port=443),
        DomainPort(domain="files.pythonhosted.org", port=443),
        
        # === Environment variables ===
        EnvironmentVariable(name="OPENWEATHER_API_KEY"),
    ]
    
    # Add Amadeus env vars if available
    if has_amadeus:
        runtime_perms.extend([
            EnvironmentVariable(name="AMADEUS_API_KEY"),
            EnvironmentVariable(name="AMADEUS_API_SECRET"),
        ])
    
    return SandboxedMCPStdio(
        name=name,
        manifest=travel_manifest,
        runtime_args=[],
        runtime_permissions=runtime_perms,
    )

