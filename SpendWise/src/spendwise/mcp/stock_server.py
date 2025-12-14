"""
Stock MCP Server - Docker Sandbox Configuration

Uses custom mcp-server-stock package with Docker sandbox isolation.
Provides access to:
- Financial Modeling Prep API for stock data
- MockBank API for portfolio management and trading
"""

import os
from pathlib import Path
from mcp_sandbox_openai_sdk import (
    DevMCPManifest,
    DomainPort,
    EnvironmentVariable,
    HostPort,
    Permission,
    Registry,
    SandboxedMCPStdio,
)

# Path to our local Stock MCP server
STOCK_SERVER_PATH = Path(__file__).parent.parent.parent.parent / "mcp-server-stock"


# Stock MCP Server manifest for local development
stock_manifest = DevMCPManifest(
    name="SpendWise Stock Server",
    description="Stock market data and trading via FMP API + MockBank",
    registry=Registry.PYPI,
    package_name="mcp-server-stock",
    permissions=[
        Permission.MCP_AC_NETWORK_CLIENT,  # Network for FMP API + PyPI
        Permission.MCP_AC_SYSTEM_ENV_READ,  # Environment variables
    ],
    # Mount local code into container
    code_mount=str(STOCK_SERVER_PATH.resolve()),
    # Install package with deps, redirect output to stderr
    exec_command="sh -c 'pip install -q --break-system-packages /sandbox >&2 && python3 -m mcp_server_stock'",
)


def create_stock_mcp_server(
    name: str = "SpendWise Stock",
) -> SandboxedMCPStdio:
    """
    Create a sandboxed Stock MCP server in Docker.
    
    The server runs in Docker with:
    - Network access to financialmodelingprep.com (for API)
    - Network access to pypi.org (for pip install)
    - Network access to MockBank (for trading)
    - Environment variable for FMP API key
    
    Required environment variables:
    - FMP_API_KEY
    
    Returns:
        SandboxedMCPStdio instance
    """
    # Validate environment variable is set
    if not os.environ.get("FMP_API_KEY"):
        raise ValueError("Missing environment variable: FMP_API_KEY")
    
    # Ensure server path exists
    if not STOCK_SERVER_PATH.exists():
        raise FileNotFoundError(f"Stock server not found at {STOCK_SERVER_PATH}")
    
    runtime_perms = [
        # Network: FMP API
        DomainPort(domain="financialmodelingprep.com", port=443),
        
        # Network: MockBank API (localhost from Docker's perspective)
        DomainPort(domain="host.docker.internal", port=8080),
        HostPort(host="127.0.0.1", port=8080),
        
        # Network: PyPI for pip install (needed for DevMCPManifest)
        DomainPort(domain="pypi.org", port=443),
        DomainPort(domain="files.pythonhosted.org", port=443),
        
        # Environment variable for FMP API key
        EnvironmentVariable(name="FMP_API_KEY"),
    ]
    
    return SandboxedMCPStdio(
        name=name,
        manifest=stock_manifest,
        runtime_args=[],
        runtime_permissions=runtime_perms,
    )

