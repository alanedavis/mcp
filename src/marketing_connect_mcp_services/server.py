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

import logging

from fastmcp import FastMCP

from marketing_connect_mcp_services.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================
# FastMCP is the high-level API from Anthropic's MCP SDK
# It handles all the protocol details (JSON-RPC, message framing, etc.)
# You just define tools/resources/prompts with decorators

mcp = FastMCP(
    name=settings.server_name,
    instructions="Marketing Connect MCP Server for AI integrations",
    host=settings.host,
    port=settings.port,
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
    logger.debug("Registering MCP components...")

    # Import tools - each module registers its tools on import
    from marketing_connect_mcp_services.tools import (
        example as _example_tools,  # noqa: F401
    )
    logger.debug("Registered tools module: example")

    # Import resources
    from marketing_connect_mcp_services.resources import (
        example as _example_resources,  # noqa: F401
    )
    logger.debug("Registered resources module: example")

    # Import prompts
    from marketing_connect_mcp_services.prompts import (
        example as _example_prompts,  # noqa: F401
    )
    logger.debug("Registered prompts module: example")

    logger.debug("MCP component registration complete")

    # Add your own modules here:
    # from marketing_connect_mcp_services.tools import database as _db_tools  # noqa: F401
    # from marketing_connect_mcp_services.tools import api as _api_tools  # noqa: F401


# =============================================================================
# COMPONENT REGISTRATION
# =============================================================================
# Register all components at module load time
_register_components()


# =============================================================================
# SERVER ACCESS
# =============================================================================

def get_server() -> FastMCP:
    """
    Get the configured MCP server instance.

    Used by transport handlers (http) to run the server.
    """
    return mcp
