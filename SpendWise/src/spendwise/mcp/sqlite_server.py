"""
SQLite MCP Server configuration for sandboxed database access

Supports both read-only and read-write modes for different agent access levels.
"""

from pathlib import Path

from mcp_sandbox_openai_sdk import (
    FSAccess,
    MCPManifest,
    Permission,
    Registry,
    SandboxedMCPStdio,
)


# Manifest declares what the MCP server CAN do (permissions are verified at runtime)
sqlite_manifest = MCPManifest(
    name="SQLite MCP Server",
    description="MCP server for SQLite database operations.",
    registry=Registry.NPM,
    package_name="mcp-server-sqlite-npx",
    permissions=[
        Permission.MCP_AC_FILESYSTEM_READ,
        Permission.MCP_AC_FILESYSTEM_WRITE,
    ],
)


def create_sqlite_mcp_server(
    db_path: str | Path,
    readonly: bool = False,
    name: str | None = None,
) -> SandboxedMCPStdio:
    """
    Create a sandboxed SQLite MCP server.

    Args:
        db_path: Path to SQLite database file
        readonly: If True, only allow read operations (no INSERT/UPDATE/DELETE)
        name: Optional name for the MCP server instance

    Returns:
        SandboxedMCPStdio instance ready to be used with MCPServers context manager.
    
    Example:
        # Read-write server for ImportAgent
        rw_server = create_sqlite_mcp_server(db_path, readonly=False)
        
        # Read-only server for SpendingAgent
        ro_server = create_sqlite_mcp_server(db_path, readonly=True)
    """
    db_path = Path(db_path).resolve()
    db_dir = str(db_path.parent)
    db_file = str(db_path)

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Runtime permission based on readonly flag
    runtime_perms = [
        FSAccess(
            path=db_dir,
            read=True,
            write=not readonly,  # Only write if not readonly
        ),
    ]

    # Default name based on access mode
    if name is None:
        name = f"SQLite ({'RO' if readonly else 'RW'})"

    return SandboxedMCPStdio(
        name=name,
        manifest=sqlite_manifest,
        runtime_args=[db_file],
        runtime_permissions=runtime_perms,
    )