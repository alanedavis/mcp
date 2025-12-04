"""
Example Prompts
===============

Prompts are templates that help structure AI interactions.
They're user-invoked (unlike tools which AI invokes).

PROMPT BASICS:
--------------
- @mcp.prompt() decorator registers the function
- Parameters let users customize the prompt
- Return a string that will be sent to the AI
- Can reference tools and resources the AI should use

PATTERNS SHOWN:
---------------
1. Simple prompt - basic template
2. Parameterized prompt - customizable
3. Multi-step prompt - workflow guidance
"""

from marketing_connect_mcp_services.server import mcp


# =============================================================================
# PATTERN 1: Simple Prompt
# =============================================================================
# Basic template with no parameters

@mcp.prompt()
async def help_prompt() -> str:
    """
    Get help with using this MCP server.
    """
    return """
I need help understanding what this MCP server can do.

Please:
1. Read the server://capabilities resource to understand available tools
2. Summarize the main features
3. Give me an example of how to use each tool
"""


# =============================================================================
# PATTERN 2: Parameterized Prompt
# =============================================================================
# Template with user-provided parameters

@mcp.prompt()
async def analyze_prompt(topic: str, depth: str = "brief") -> str:
    """
    Generate a prompt for analyzing a topic.

    Args:
        topic: What to analyze
        depth: How detailed - "brief", "moderate", or "comprehensive"
    """
    depth_instructions = {
        "brief": "Provide a short, 2-3 sentence analysis.",
        "moderate": "Provide a balanced analysis with key points.",
        "comprehensive": "Provide a detailed analysis covering all aspects.",
    }

    instruction = depth_instructions.get(depth, depth_instructions["moderate"])

    return f"""
Please analyze the following topic: {topic}

{instruction}

If relevant tools are available, use them to gather data.
Structure your response with clear sections.
"""


@mcp.prompt()
async def summarize_prompt(content_type: str, format: str = "bullets") -> str:
    """
    Generate a prompt for summarizing content.

    Args:
        content_type: What kind of content (article, conversation, data)
        format: Output format - "bullets", "paragraph", or "outline"
    """
    format_instructions = {
        "bullets": "Present the summary as bullet points.",
        "paragraph": "Write the summary as a flowing paragraph.",
        "outline": "Structure the summary as a hierarchical outline.",
    }

    return f"""
Please summarize the {content_type} content.

{format_instructions.get(format, format_instructions["bullets"])}

Focus on:
- Key points and main ideas
- Important details that shouldn't be missed
- Any actionable items or conclusions
"""


# =============================================================================
# PATTERN 3: Multi-Step Workflow Prompt
# =============================================================================
# Guides the AI through a sequence of operations

@mcp.prompt()
async def data_exploration_prompt(data_type: str) -> str:
    """
    Guide exploration of a data type.

    Args:
        data_type: The type of data to explore (user, product, order)
    """
    return f"""
Let's explore the {data_type} data structure systematically.

STEP 1: Understand the Schema
- Read the data://schema/{data_type} resource
- List all fields and their types
- Identify required vs optional fields

STEP 2: Examine Relationships
- Note any foreign key references
- Explain how this relates to other data types

STEP 3: Suggest Operations
- What common operations would be useful?
- What validations should be applied?

STEP 4: Summary
- Provide a brief summary of the {data_type} data structure
- Suggest any improvements or considerations
"""


@mcp.prompt()
async def troubleshooting_prompt(issue: str) -> str:
    """
    Guide troubleshooting of an issue.

    Args:
        issue: Description of the problem
    """
    return f"""
Help me troubleshoot this issue: {issue}

DIAGNOSTIC STEPS:
1. First, check server://status to verify the server is healthy
2. Review server://capabilities to understand available tools
3. Identify which components might be involved

INVESTIGATION:
- What could cause this issue?
- What information do we need to diagnose it?
- What tools or resources should we check?

RESOLUTION:
- Suggest possible fixes
- Explain how to verify the fix worked
"""
