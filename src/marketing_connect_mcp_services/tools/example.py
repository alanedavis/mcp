"""
Example Tools
=============

This file demonstrates different tool patterns you can use.
Copy and modify these for your own integrations.

TOOL BASICS:
------------
- @mcp.tool() decorator registers the function as an MCP tool
- The docstring becomes the tool description (AI sees this!)
- Type hints define the input schema (AI sees parameter types)
- Return type should be str (text the AI will receive)

PATTERNS SHOWN:
---------------
1. Simple tool - basic input/output
2. Tool with optional parameters
3. Tool with complex parameters (dict/list)
4. Tool with error handling
5. Tool calling external services
6. Tool with Pydantic model input (structured objects)
"""

import json
import logging
from typing import Any

from marketing_connect_mcp_services.models import UserDetails
from marketing_connect_mcp_services.server import mcp

logger = logging.getLogger(__name__)


# =============================================================================
# PATTERN 1: Simple Tool
# =============================================================================
# The most basic pattern - takes input, returns output

@mcp.tool()
async def echo(message: str) -> str:
    """
    Echo back the provided message.

    This is a simple demonstration tool. Replace it with your own logic.

    Args:
        message: The text to echo back

    Returns:
        The same message, echoed back
    """
    return f"Echo: {message}"


# =============================================================================
# PATTERN 2: Tool with Optional Parameters
# =============================================================================
# Parameters with defaults are optional - AI doesn't have to provide them

@mcp.tool()
async def format_text(
    text: str,
    uppercase: bool = False,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """
    Format text with optional transformations.

    Demonstrates optional parameters with defaults.

    Args:
        text: The text to format (required)
        uppercase: Convert to uppercase (optional, default: false)
        prefix: Add this before the text (optional)
        suffix: Add this after the text (optional)

    Returns:
        The formatted text
    """
    result = text
    if uppercase:
        result = result.upper()
    return f"{prefix}{result}{suffix}"


# =============================================================================
# PATTERN 3: Tool with Complex Parameters
# =============================================================================
# You can accept dicts and lists for structured data

@mcp.tool()
async def process_items(
    items: list[str],
    options: dict[str, Any] | None = None,
) -> str:
    """
    Process a list of items with optional configuration.

    Demonstrates complex parameter types.

    Args:
        items: List of items to process
        options: Optional configuration dict with keys:
                 - reverse: bool - reverse the list
                 - limit: int - max items to return

    Returns:
        JSON string of processed items
    """
    options = options or {}

    result = items.copy()

    if options.get("reverse"):
        result = result[::-1]

    if limit := options.get("limit"):
        result = result[:limit]

    return json.dumps({"processed": result, "count": len(result)})


# =============================================================================
# PATTERN 4: Tool with Error Handling
# =============================================================================
# Show how to handle errors gracefully - return error info, don't crash

@mcp.tool()
async def divide(numerator: float, denominator: float) -> str:
    """
    Divide two numbers with error handling.

    Demonstrates proper error handling in tools.

    Args:
        numerator: The number to divide
        denominator: The number to divide by

    Returns:
        The result or an error message
    """
    try:
        if denominator == 0:
            return json.dumps({
                "success": False,
                "error": "Cannot divide by zero"
            })

        result = numerator / denominator
        return json.dumps({
            "success": True,
            "result": result
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# =============================================================================
# PATTERN 5: Tool Calling External Services
# =============================================================================
# Template for calling APIs, databases, etc.
# Uncomment and modify for your use case

# from marketing_connect_mcp_services.config import settings
# import httpx  # Add to dependencies if needed
#
# @mcp.tool()
# async def call_api(endpoint: str, method: str = "GET") -> str:
#     """
#     Call an external API endpoint.
#
#     Args:
#         endpoint: API endpoint path
#         method: HTTP method (GET, POST, etc.)
#
#     Returns:
#         API response as JSON string
#     """
#     async with httpx.AsyncClient() as client:
#         response = await client.request(
#             method=method,
#             url=f"{settings.base_url}{endpoint}",
#             headers={"Authorization": f"Bearer {settings.api_key}"},
#             timeout=30.0,
#         )
#         response.raise_for_status()
#         return response.text


# =============================================================================
# PATTERN 6: Calculator Example (More Realistic)
# =============================================================================
# A more realistic example showing a useful tool

@mcp.tool()
async def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Supports basic arithmetic: +, -, *, /, **, (), and numbers.

    Args:
        expression: Mathematical expression (e.g., "2 + 3 * 4")

    Returns:
        The calculated result or an error message

    Examples:
        calculate("2 + 3") -> "5"
        calculate("(10 - 3) * 2") -> "14"
    """
    # Only allow safe characters
    allowed = set("0123456789+-*/.(). ")
    if not all(c in allowed for c in expression):
        return json.dumps({
            "success": False,
            "error": "Expression contains invalid characters"
        })

    try:
        # Use eval with restricted builtins for safety
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({
            "success": True,
            "expression": expression,
            "result": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Calculation error: {e}"
        })


# =============================================================================
# PATTERN 7: Tool with Pydantic Model Input (Structured Objects)
# =============================================================================
# Use Pydantic models for complex, validated input objects.
# This provides schema validation and clear documentation for the AI.
#
# NOTE: UserDetails is imported from marketing_connect_mcp_services.models
# which is generated from OpenAPI schemas. Run 'make fetch-models' to update.


@mcp.tool()
async def greet_user(user: UserDetails) -> str:
    """
    Greet a user with their name and user SID.

    Demonstrates using a Pydantic model (generated from OpenAPI) as input.
    The AI will see the schema and provide properly structured input.

    Args:
        user: A UserDetails object containing userSid and name

    Returns:
        A greeting message with the user's details
    """
    logger.info(f"Greeting user: {user.name} ({user.userSid})")
    return f"Hello {user.name} ({user.userSid})"
