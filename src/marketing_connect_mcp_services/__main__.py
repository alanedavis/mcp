"""
Module entry point.

When you run: python -m marketing_connect_mcp_services
Python looks for this __main__.py file and executes it.

This is an alternative to the `marketing-connect-mcp` CLI command.
Both do the same thing - start the HTTP server.

USAGE:
------
    python -m marketing_connect_mcp_services
    python -m marketing_connect_mcp_services --port 3000
"""

from marketing_connect_mcp_services.cli import main

if __name__ == "__main__":
    main()
