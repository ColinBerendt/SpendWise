#!/usr/bin/env python3
"""
Discover Amadeus API IP addresses.

Makes multiple requests to Amadeus to discover different IPs
that can be added to the MCP server permissions.

Usage:
    uv run testing/discover_amadeus_ips.py
"""

import asyncio
import os
import socket
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv

load_dotenv()

AMADEUS_DOMAINS = [
    "test.api.amadeus.com",
    "api.amadeus.com", 
    "amadeus-self-service-test.apigee.net",
    "amadeus-self-service.dn.apigee.net",
]

discovered_ips = set()


def resolve_domain(domain: str) -> list[str]:
    """Resolve domain to IP addresses."""
    try:
        results = socket.getaddrinfo(domain, 443, socket.AF_INET)
        ips = list(set(r[4][0] for r in results))
        return ips
    except Exception as e:
        print(f"  Could not resolve {domain}: {e}")
        return []


async def get_token() -> str | None:
    """Get Amadeus OAuth token."""
    api_key = os.environ.get("AMADEUS_API_KEY")
    api_secret = os.environ.get("AMADEUS_API_SECRET")
    
    if not api_key or not api_secret:
        print("Missing AMADEUS_API_KEY or AMADEUS_API_SECRET")
        return None
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": api_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Auth failed: {response.status_code}")
            return None


async def make_request(token: str, endpoint: str, params: dict) -> None:
    """Make API request and track connection IP."""
    url = f"https://test.api.amadeus.com{endpoint}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
            
            # Get the IP from the connection
            if hasattr(response, 'extensions') and 'network_stream' in response.extensions:
                stream = response.extensions['network_stream']
                if hasattr(stream, 'get_extra_info'):
                    peername = stream.get_extra_info('peername')
                    if peername:
                        discovered_ips.add(peername[0])
            
            print(f"  {endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")


async def main():
    print("=" * 60)
    print("Amadeus IP Discovery")
    print("=" * 60)
    print()
    
    # 1. DNS Resolution
    print("1. DNS Resolution")
    print("-" * 40)
    
    all_dns_ips = set()
    for domain in AMADEUS_DOMAINS:
        ips = resolve_domain(domain)
        if ips:
            print(f"  {domain}:")
            for ip in ips:
                print(f"    - {ip}")
                all_dns_ips.add(ip)
    
    print()
    
    # 2. Multiple API Requests
    print("2. Making API Requests (to discover more IPs)")
    print("-" * 40)
    
    token = await get_token()
    if not token:
        print("Could not get token")
        return
    
    print("  Got token!")
    print()
    
    # Future dates
    tomorrow = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    # Make multiple requests
    requests = [
        ("/v2/shopping/flight-offers", {"originLocationCode": "ZRH", "destinationLocationCode": "BCN", "departureDate": tomorrow, "adults": 1, "max": 1}),
        ("/v2/shopping/flight-offers", {"originLocationCode": "ZRH", "destinationLocationCode": "ROM", "departureDate": tomorrow, "adults": 1, "max": 1}),
        ("/v2/shopping/flight-offers", {"originLocationCode": "ZRH", "destinationLocationCode": "PAR", "departureDate": tomorrow, "adults": 1, "max": 1}),
        ("/v2/shopping/flight-offers", {"originLocationCode": "ZRH", "destinationLocationCode": "LON", "departureDate": next_week, "adults": 1, "max": 1}),
        ("/v2/shopping/flight-offers", {"originLocationCode": "ZRH", "destinationLocationCode": "AMS", "departureDate": next_week, "adults": 1, "max": 1}),
        ("/v1/reference-data/locations/hotels/by-city", {"cityCode": "BCN"}),
        ("/v1/reference-data/locations/hotels/by-city", {"cityCode": "ROM"}),
        ("/v1/reference-data/locations/hotels/by-city", {"cityCode": "PAR"}),
        ("/v1/reference-data/locations", {"keyword": "Barcelona", "subType": "CITY"}),
        ("/v1/reference-data/locations", {"keyword": "Rome", "subType": "CITY"}),
    ]
    
    print("  Making requests...")
    for endpoint, params in requests:
        await make_request(token, endpoint, params)
        await asyncio.sleep(0.5)  # Small delay
    
    print()
    
    # 3. Summary
    print("3. Summary - All Discovered IPs")
    print("-" * 40)
    
    all_ips = all_dns_ips | discovered_ips
    
    print()
    print("  Copy these to travel_server.py:")
    print()
    for ip in sorted(all_ips):
        print(f'        HostPort(host=IPv4Address("{ip}"), port=443),')
    
    print()
    print(f"  Total unique IPs: {len(all_ips)}")
    print()
    
    # 4. Run multiple DNS checks with delay
    print("4. Additional DNS checks (IPs may rotate)")
    print("-" * 40)
    
    for i in range(5):
        print(f"  Check {i+1}/5...")
        await asyncio.sleep(2)
        for domain in ["test.api.amadeus.com"]:
            ips = resolve_domain(domain)
            for ip in ips:
                if ip not in all_ips:
                    print(f"    NEW IP: {ip}")
                    all_ips.add(ip)
    
    print()
    print("=" * 60)
    print("FINAL LIST - Copy to travel_server.py")
    print("=" * 60)
    print()
    for ip in sorted(all_ips):
        print(f'        HostPort(host=IPv4Address("{ip}"), port=443),')
    print()
    print(f"Total: {len(all_ips)} IPs")


if __name__ == "__main__":
    asyncio.run(main())

