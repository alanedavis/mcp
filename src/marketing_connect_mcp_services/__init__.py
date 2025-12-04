"""
Marketing Connect MCP Services
==============================

A Model Context Protocol (MCP) server for Marketing Connect AI integrations.

QUICK START:
------------
    # Start the HTTP server
    marketing-connect-mcp

    # With custom port
    marketing-connect-mcp --port 3000

EXTENDING:
----------
Add tools in: marketing_connect_mcp_services/tools/
Add resources in: marketing_connect_mcp_services/resources/
Add prompts in: marketing_connect_mcp_services/prompts/

See the example files in each directory for patterns.

PROGRAMMATIC USAGE:
-------------------
    from marketing_connect_mcp_services import mcp, settings

    # Add a tool dynamically
    @mcp.tool()
    async def my_tool(param: str) -> str:
        return f"Result: {param}"

LOGGING:
--------
    from marketing_connect_mcp_services import setup_logging, get_logger

    # Initialize logging at application startup
    setup_logging()

    # Get a logger in any module
    logger = get_logger(__name__)
    logger.info("Hello from my module")
"""

from marketing_connect_mcp_services.config import Settings, get_settings, settings
from marketing_connect_mcp_services.logging_config import (
    LogContext,
    get_logger,
    setup_logging,
)
from marketing_connect_mcp_services.server import get_server, mcp

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "mcp",
    "get_server",
    "settings",
    "get_settings",
    "Settings",
    "setup_logging",
    "get_logger",
    "LogContext",
]
