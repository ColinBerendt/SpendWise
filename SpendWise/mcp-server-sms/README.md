# MCP Server SMS

A custom MCP server that sends SMS via Twilio - designed to run in a Docker sandbox.

## What We Built

### Problem
We wanted to build an AI agent that can send SMS - but isolated in a Docker container with controlled network access.

### Solution
We built our own MCP server in Python that:
1. Implements the MCP protocol (via `mcp` library)
2. Makes Twilio API calls to send SMS
3. Runs in a Docker sandbox with access only to `api.twilio.com`

## Architektur

```
+------------------+     +------------------------+     +----------------+
|   AI Agent       |     |   Docker Sandbox       |     |   Twilio API   |
|   (OpenAI)       |<--->|   mcp-server-sms       |<--->|   SMS senden   |
|                  | MCP |   (Python)             | HTTPS|                |
+------------------+     +------------------------+     +----------------+
                                    |
                         Only api.twilio.com:443
                         allowed (iptables)
```

## Key Files

```
mcp-server-sms/
├── pyproject.toml              # Package config
└── src/mcp_server_sms/
    ├── __init__.py             # Entry point (main)
    ├── __main__.py             # Module runner
    └── server.py               # MCP Server Implementation
```

## How It Works

### 1. MCP Server definiert Tools

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="send_sms",
            description="Send SMS via Twilio",
            inputSchema={...}
        ),
        Tool(
            name="send_budget_alert",
            description="Send formatted budget alert",
            inputSchema={...}
        ),
    ]
```

### 2. DevMCPManifest for Local Development

Since our package is not published on PyPI, we use `DevMCPManifest`:

```python
sms_manifest = DevMCPManifest(
    name="SpendWise SMS Server",
    registry=Registry.PYPI,
    package_name="mcp-server-sms",
    permissions=[
        Permission.MCP_AC_NETWORK_CLIENT,
        Permission.MCP_AC_SYSTEM_ENV_READ,
    ],
    code_mount=str(SMS_SERVER_PATH),  # Local code
    exec_command="sh -c 'pip install ... && python3 -m mcp_server_sms'",
)
```

### 3. Runtime Permissions

```python
runtime_perms = [
    # Network: Only Twilio + PyPI
    DomainPort(domain="api.twilio.com", port=443),
    DomainPort(domain="pypi.org", port=443),
    DomainPort(domain="files.pythonhosted.org", port=443),
    
    # Environment Variables
    EnvironmentVariable(name="TWILIO_ACCOUNT_SID"),
    EnvironmentVariable(name="TWILIO_AUTH_TOKEN"),
    EnvironmentVariable(name="TWILIO_PHONE_NUMBER"),
]
```

## Challenges & Solutions

| Problem | Solution |
|---------|----------|
| Package not on PyPI | `DevMCPManifest` with `code_mount` |
| PEP 668 (externally-managed-environment) | `pip install --break-system-packages` |
| `python` not in PATH | Use `python3` |
| Missing dependencies | Add PyPI domains to allowed egress |

## Usage

### Configure .env

```env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
NOTIFICATION_PHONE=+41791234567
```

### Start Demo

```bash
cd SpendWise
uv run testing/seed_data.py   # Test data
uv run testing/mcp_sms_demo.py
```

### Confirm Permissions

```
Allow access to file system path: .../data (read: True, write: False) → yes
Allow access to domain: api.twilio.com:443 → yes
Allow access to domain: pypi.org:443 → yes
Allow access to domain: files.pythonhosted.org:443 → yes
Allow access to env var: TWILIO_ACCOUNT_SID → yes
Allow access to env var: TWILIO_AUTH_TOKEN → yes
Allow access to env var: TWILIO_PHONE_NUMBER → yes
```

## For Production

To publish the package:

```bash
cd mcp-server-sms
uv build
uv publish
```

Then `MCPManifest` can be used instead of `DevMCPManifest`:

```python
sms_manifest = MCPManifest(
    name="SMS MCP Server",
    registry=Registry.PYPI,
    package_name="mcp-server-sms",  # From PyPI
    permissions=[...],
)
```

## License

MIT
