"""
Prompts Package
===============

Prompts are reusable interaction templates. They help users
structure their requests consistently and can include instructions
for the AI on how to approach a task.

WHEN TO USE PROMPTS:
--------------------
- Common tasks that benefit from consistent structure
- Complex workflows with multiple steps
- Tasks where you want to guide the AI's approach

HOW TO ADD A PROMPT:
--------------------
1. Create a new file in this directory
2. Import the mcp instance: from marketing_connect_mcp_services.server import mcp
3. Define your prompt with @mcp.prompt()
4. Import your module in server.py's _register_components()

EXAMPLE:
--------
    # In prompts/my_prompts.py
    from marketing_connect_mcp_services.server import mcp

    @mcp.prompt()
    async def my_prompt(topic: str) -> str:
        '''Generate a prompt for analyzing a topic.'''
        return f"Please analyze {topic}..."
"""

# Prompts are registered by importing their modules in server.py
