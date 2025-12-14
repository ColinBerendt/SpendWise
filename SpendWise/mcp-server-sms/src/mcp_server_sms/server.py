"""
MCP Server for SMS via Twilio

Provides tools for AI agents to send SMS messages through the Twilio API.
Designed to run in a Docker sandbox with controlled network access.
"""

import os
import base64
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server-sms")

# Create MCP server
server = Server("mcp-server-sms")


def get_twilio_credentials() -> tuple[str, str, str]:
    """Get Twilio credentials from environment variables."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    
    if not all([account_sid, auth_token, from_number]):
        raise ValueError(
            "Missing Twilio credentials. Set TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
        )
    
    return account_sid, auth_token, from_number


def get_default_recipient() -> str | None:
    """Get default recipient phone number from environment variable."""
    return os.environ.get("NOTIFICATION_PHONE")


async def send_twilio_sms(to: str, body: str) -> dict[str, Any]:
    """
    Send an SMS via Twilio REST API.
    
    Args:
        to: Recipient phone number (E.164 format, e.g., +41768013831)
        body: Message content
    
    Returns:
        Twilio API response
    """
    account_sid, auth_token, from_number = get_twilio_credentials()
    
    # Twilio Messages API endpoint
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    # Basic auth header
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    # Request body
    data = {
        "To": to,
        "From": from_number,
        "Body": body,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        
        if response.status_code >= 400:
            error_data = response.json()
            raise Exception(f"Twilio API error: {error_data.get('message', response.text)}")
        
        return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available SMS tools."""
    default_recipient = get_default_recipient()
    recipient_note = " (uses default from NOTIFICATION_PHONE if not provided)" if default_recipient else ""
    
    return [
        Tool(
            name="send_sms",
            description=(
                "Send an SMS message via Twilio. "
                "Use this to notify users about budget alerts, transactions, etc."
                f"{recipient_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient phone number in E.164 format (optional - uses default if set)",
                    },
                    "message": {
                        "type": "string",
                        "description": "The SMS message content (max 1600 characters)",
                    },
                },
                "required": ["message"],  # 'to' is now optional
            },
        ),
        Tool(
            name="send_budget_alert",
            description=(
                "Send a formatted budget alert SMS. "
                "Includes category, usage stats, and an optional custom/humorous message."
                f"{recipient_note}"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient phone number in E.164 format (optional - uses default if set)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Budget category name (e.g., 'Groceries', 'Entertainment')",
                    },
                    "spent": {
                        "type": "number",
                        "description": "Amount spent so far",
                    },
                    "budget": {
                        "type": "number",
                        "description": "Total budget amount",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (default: CHF)",
                        "default": "CHF",
                    },
                    "custom_message": {
                        "type": "string",
                        "description": "Optional custom/humorous message to add (e.g., 'Time for rice and beans!')",
                        "default": "",
                    },
                },
                "required": ["category", "spent", "budget"],  # 'to' is now optional
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "send_sms":
        # Use provided 'to' or fall back to default recipient
        to = arguments.get("to") or get_default_recipient()
        message = arguments["message"]
        
        if not to:
            return [TextContent(
                type="text",
                text="Error: No recipient phone number provided and NOTIFICATION_PHONE not set."
            )]
        
        logger.info(f"Sending SMS to {to}: {message[:50]}...")
        
        try:
            result = await send_twilio_sms(to, message)
            return [TextContent(
                type="text",
                text=f"SMS sent successfully! SID: {result.get('sid', 'unknown')}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to send SMS: {str(e)}"
            )]
    
    elif name == "send_budget_alert":
        # Use provided 'to' or fall back to default recipient
        to = arguments.get("to") or get_default_recipient()
        
        if not to:
            return [TextContent(
                type="text",
                text="Error: No recipient phone number provided and NOTIFICATION_PHONE not set."
            )]
        
        category = arguments["category"]
        spent = arguments["spent"]
        budget = arguments["budget"]
        currency = arguments.get("currency", "CHF")
        custom_message = arguments.get("custom_message", "")
        
        # Calculate percentage
        percentage = (spent / budget) * 100 if budget > 0 else 0
        
        # Determine status icon
        if percentage >= 100:
            status_icon = "[!!]"
            status = "OVER BUDGET"
        elif percentage >= 80:
            status_icon = "[!]"
            status = "WARNING"
        else:
            status_icon = "[OK]"
            status = "OK"
        
        # Format message
        lines = [
            f"{status_icon} SpendWise: {category}",
            f"{currency} {spent:.0f}/{budget:.0f} ({percentage:.0f}%)",
        ]
        
        # Add custom/humorous message if provided
        if custom_message:
            lines.append(custom_message)
        
        message = "\n".join(lines)
        
        logger.info(f"Sending budget alert to {to} for {category}")
        
        try:
            result = await send_twilio_sms(to, message)
            return [TextContent(
                type="text",
                text=f"Budget alert sent! SID: {result.get('sid', 'unknown')}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to send alert: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def serve():
    """Run the MCP server."""
    logger.info("Starting MCP SMS Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

