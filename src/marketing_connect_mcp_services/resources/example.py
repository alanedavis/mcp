"""
Example Resources
=================

Resources provide context data to AI models. They're loaded into
the AI's context window to give it background information.

RESOURCE BASICS:
----------------
- @mcp.resource("uri://path") decorator registers the function
- URI can include parameters: "myapp://users/{user_id}"
- Return type should be str (content the AI will receive)
- Content can be text, JSON, markdown, etc.

PATTERNS SHOWN:
---------------
1. Static resource - always returns the same data
2. Parameterized resource - takes URI parameters
3. Dynamic resource - fetches data on demand
"""

import json
from datetime import datetime, timezone

from marketing_connect_mcp_services.config import settings
from marketing_connect_mcp_services.server import mcp


# =============================================================================
# PATTERN 1: Static Resource
# =============================================================================
# Returns fixed information - good for configs, schemas, documentation

@mcp.resource("server://info")
async def get_server_info() -> str:
    """
    Get basic server information.

    This resource provides static server metadata.
    """
    return f"""
Marketing Connect MCP Server Information
========================================
Name: {settings.server_name}
Version: {settings.server_version}
Debug Mode: {settings.debug}
Base URL: {settings.base_url or 'Not configured'}
Region: {settings.region or 'Not configured'}

This is the Marketing Connect MCP server for AI integrations.
"""


@mcp.resource("server://capabilities")
async def get_capabilities() -> str:
    """
    Describe what this server can do.

    Helps AI understand available functionality.
    """
    return """
Server Capabilities
===================

TOOLS AVAILABLE:
- echo: Echo back a message
- format_text: Format text with options
- process_items: Process a list of items
- divide: Divide numbers safely
- calculate: Evaluate math expressions

RESOURCES AVAILABLE:
- server://info: Server information
- server://capabilities: This document
- server://status: Current server status
- data://schema/{name}: Get schema for a data type

PROMPTS AVAILABLE:
- analyze: Template for analysis tasks
- summarize: Template for summarization
"""


# =============================================================================
# PATTERN 2: Parameterized Resource
# =============================================================================
# URI includes parameters that are passed to your function

@mcp.resource("data://schema/{schema_name}")
async def get_schema(schema_name: str) -> str:
    """
    Get the schema definition for a data type.

    Args:
        schema_name: Name of the schema (user, product, order)
    """
    schemas = {
        "user": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "created_at": {"type": "string", "format": "date-time"},
            },
            "required": ["id", "name", "email"],
        },
        "product": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number", "minimum": 0},
                "in_stock": {"type": "boolean"},
            },
            "required": ["id", "name", "price"],
        },
        "order": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "user_id": {"type": "string"},
                "items": {"type": "array"},
                "total": {"type": "number"},
                "status": {"type": "string", "enum": ["pending", "shipped", "delivered"]},
            },
        },
    }

    if schema_name not in schemas:
        return f"Schema '{schema_name}' not found. Available: {', '.join(schemas.keys())}"

    return json.dumps(schemas[schema_name], indent=2)


# =============================================================================
# PATTERN 3: Dynamic Resource
# =============================================================================
# Fetches or computes data on demand

@mcp.resource("server://status")
async def get_status() -> str:
    """
    Get current server status.

    This resource returns dynamic, real-time information.
    """
    return json.dumps({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": settings.server_name,
        "version": settings.server_version,
        "config": {
            "base_url": settings.base_url,
            "region": settings.region,
            "debug": settings.debug,
        },
    }, indent=2)


# =============================================================================
# PATTERN 4: Documentation Resource
# =============================================================================
# Provide documentation that helps AI use your tools effectively

@mcp.resource("docs://getting-started")
async def get_getting_started() -> str:
    """
    Getting started guide for using this MCP server.
    """
    return """
Getting Started with Marketing Connect MCP Server
==================================================

This is the Marketing Connect MCP server for AI integrations.

## Available Tools

### echo
Simply echoes back your message. Good for testing.
Example: echo(message="Hello!")

### format_text
Formats text with options like uppercase, prefix, suffix.
Example: format_text(text="hello", uppercase=true, prefix=">>> ")

### calculate
Evaluates mathematical expressions safely.
Example: calculate(expression="2 + 3 * 4")

## Available Resources

- server://info - Basic server info
- server://status - Real-time status
- data://schema/{name} - Data schemas (user, product, order)

## Tips

1. Use the calculate tool for math operations
2. Check server://status if something seems wrong
3. Read data://schema/{name} to understand data structures
"""
