"""
Resources Package
=================

Resources provide data that gets loaded into the AI's context.
Unlike tools (which the AI invokes), resources are fetched by
the client application when it needs to give the AI background info.

WHEN TO USE RESOURCES VS TOOLS:
-------------------------------
- RESOURCE: Static or semi-static data (schemas, configs, documentation)
- TOOL: Dynamic operations (CRUD, API calls, calculations)

HOW TO ADD A RESOURCE:
----------------------
1. Create a new file in this directory
2. Import the mcp instance: from marketing_connect_mcp_services.server import mcp
3. Define your resource with @mcp.resource("uri://pattern")
4. Import your module in server.py's _register_components()

EXAMPLE:
--------
    # In resources/my_resources.py
    from marketing_connect_mcp_services.server import mcp

    @mcp.resource("myapp://config")
    async def get_config() -> str:
        '''Returns the app configuration.'''
        return "config data here"
"""

# Resources are registered by importing their modules in server.py
