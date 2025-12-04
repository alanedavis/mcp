"""
MCP Server - Main Entry Point
==============================

This is the core of your MCP server. It:
1. Initializes the FastMCP server
2. Registers tools, resources, and prompts from submodules
3. Provides the server instance for transport handlers

ARCHITECTURE:
-------------
    marketing_connect_mcp_services/
    ├── server.py          <- You are here (orchestration)
    ├── tools/             <- Add your tools here
    │   ├── __init__.py
    │   └── example.py     <- Example tool implementations
    ├── resources/         <- Add your resources here
    │   ├── __init__.py
    │   └── example.py     <- Example resource implementations
    └── prompts/           <- Add your prompts here
        ├── __init__.py
        └── example.py     <- Example prompt implementations

HOW TO EXTEND:
--------------
1. Create a new file in tools/, resources/, or prompts/
2. Define your functions with @mcp.tool(), @mcp.resource(), or @mcp.prompt()
3. Import and register them in the respective __init__.py
4. They'll be automatically available to MCP clients

MCP CONCEPTS:
-------------
- TOOLS: Functions the AI model can invoke (like POST endpoints)
- RESOURCES: Data loaded into AI context (like GET endpoints)
- PROMPTS: Reusable interaction templates
"""

from mcp.server.fastmcp import FastMCP

from marketing_connect_mcp_services.config import settings

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================
# FastMCP is the high-level API from Anthropic's MCP SDK
# It handles all the protocol details (JSON-RPC, message framing, etc.)
# You just define tools/resources/prompts with decorators

mcp = FastMCP(
    name=settings.server_name,
    version=settings.server_version,
    description="Marketing Connect MCP Server for AI integrations",
)


# =============================================================================
# REGISTER COMPONENTS
# =============================================================================
# Import tool/resource/prompt modules to register them with the server
# Each module uses the shared `mcp` instance via: from marketing_connect_mcp_services.server import mcp

def _register_components() -> None:
    """
    Import all component modules to register their handlers.

    WHY A FUNCTION?
    - Avoids circular imports (modules import `mcp` from here)
    - Called lazily when server starts
    - Easy to see what's registered
    """
    # Import tools - each module registers its tools on import
    from marketing_connect_mcp_services.tools import example as _example_tools  # noqa: F401

    # Import resources
    from marketing_connect_mcp_services.resources import example as _example_resources  # noqa: F401

    # Import prompts
    from marketing_connect_mcp_services.prompts import example as _example_prompts  # noqa: F401

    # Add your own modules here:
    # from marketing_connect_mcp_services.tools import database as _db_tools  # noqa: F401
    # from marketing_connect_mcp_services.tools import api as _api_tools  # noqa: F401


# =============================================================================
# LIFECYCLE HOOKS
# =============================================================================

@mcp.on_event("startup")
async def on_startup() -> None:
    """
    Called when the MCP server starts.

    Use this for:
    - Initializing database connections
    - Validating configuration
    - Loading cached data
    """
    print(f"Starting {settings.server_name} v{settings.server_version}...")
    print(f"   Debug mode: {settings.debug}")

    # Register all components
    _register_components()

    # List registered tools for debugging
    if settings.debug:
        # Access the low-level server to list tools
        print("   Registered tools:")
        for tool in mcp._tool_manager._tools.values():
            print(f"      - {tool.name}: {tool.description[:50]}...")


@mcp.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Called when the MCP server stops.

    Use this for:
    - Closing database connections
    - Flushing caches
    - Cleanup operations
    """
    print(f"{settings.server_name} shutting down...")


# =============================================================================
# SERVER ACCESS
# =============================================================================

def get_server() -> FastMCP:
    """
    Get the configured MCP server instance.

    Used by transport handlers (http) to run the server.
    """
    return mcp
