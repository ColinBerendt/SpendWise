"""
MCP Server for SMS via Twilio

A Model Context Protocol server that provides SMS sending capabilities.
Enables AI agents to send SMS messages through the Twilio API.
"""

from .server import serve
import asyncio


def main():
    """MCP SMS Server - Send SMS via Twilio"""
    asyncio.run(serve())


__all__ = ["main", "serve"]

