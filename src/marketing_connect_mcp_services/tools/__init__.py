"""
Tools Package
=============

Tools are functions that AI models can invoke. Think of them like
API endpoints that the AI decides when to call.

HOW TO ADD A TOOL:
------------------
1. Create a new file in this directory (e.g., my_tools.py)
2. Import the mcp instance: from marketing_connect_mcp_services.server import mcp
3. Define your tool with the @mcp.tool() decorator
4. Import your module in server.py's _register_components()

EXAMPLE:
--------
    # In tools/my_tools.py
    from marketing_connect_mcp_services.server import mcp

    @mcp.tool()
    async def my_tool(param: str) -> str:
        '''Description the AI will see.'''
        return f"Result for {param}"
"""

# Tools are registered by importing their modules in server.py
