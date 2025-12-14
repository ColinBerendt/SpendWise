"""
SMS MCP Server - Docker Sandbox Configuration

Uses our custom mcp-server-sms package with Docker sandbox isolation.
Uses DevMCPManifest to mount the local code (not published to PyPI).
"""

import os
from pathlib import Path
from mcp_sandbox_openai_sdk import (
    DevMCPManifest,
    DomainPort,
    EnvironmentVariable,
    Permission,
    Registry,
    SandboxedMCPStdio,
)

# Path to our local SMS MCP server
SMS_SERVER_PATH = Path(__file__).parent.parent.parent.parent / "mcp-server-sms"


# SMS MCP Server manifest for local development
sms_manifest = DevMCPManifest(
    name="SpendWise SMS Server",
    description="Send SMS via Twilio with AI agents",
    registry=Registry.PYPI,
    package_name="mcp-server-sms",
    permissions=[
        Permission.MCP_AC_NETWORK_CLIENT,  # Network for Twilio + PyPI
        Permission.MCP_AC_SYSTEM_ENV_READ,  # Environment variables
    ],
    # Mount local code into container
    code_mount=str(SMS_SERVER_PATH.resolve()),
    # Install package with deps (--break-system-packages for PEP 668), then run
    exec_command="sh -c 'pip install -q --break-system-packages /sandbox >&2 && python3 -m mcp_server_sms'",
)


def create_sms_mcp_server(
    name: str = "SpendWise SMS",
) -> SandboxedMCPStdio:
    """
    Create a sandboxed SMS MCP server in Docker.
    
    The server runs in Docker with:
    - Network access to api.twilio.com:443 (for SMS)
    - Network access to pypi.org:443 + files.pythonhosted.org:443 (for pip install)
    - Environment variables for Twilio credentials
    
    Required environment variables:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_PHONE_NUMBER
    
    Optional:
    - NOTIFICATION_PHONE (default recipient, so agents don't need to specify)
    
    Returns:
        SandboxedMCPStdio instance
    """
    # Validate environment variables are set
    required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    # Ensure SMS server path exists
    if not SMS_SERVER_PATH.exists():
        raise FileNotFoundError(f"SMS server not found at {SMS_SERVER_PATH}")
    
    runtime_perms = [
        # Network: Twilio API
        DomainPort(domain="api.twilio.com", port=443),
        
        # Network: PyPI for pip install (needed for DevMCPManifest)
        DomainPort(domain="pypi.org", port=443),
        DomainPort(domain="files.pythonhosted.org", port=443),
        
        # Environment variables for Twilio credentials
        EnvironmentVariable(name="TWILIO_ACCOUNT_SID"),
        EnvironmentVariable(name="TWILIO_AUTH_TOKEN"),
        EnvironmentVariable(name="TWILIO_PHONE_NUMBER"),
        # Default recipient (optional - allows agents to skip 'to' parameter)
        EnvironmentVariable(name="NOTIFICATION_PHONE"),
    ]
    
    return SandboxedMCPStdio(
        name=name,
        manifest=sms_manifest,
        runtime_args=[],
        runtime_permissions=runtime_perms,
    )
