"""
CLI Entry Point
===============

Command-line interface for running the MCP server.

This server uses HTTP transport (Streamable HTTP) for deployment.
Clients connect over the network to the /mcp endpoint.

HEALTH ENDPOINTS:
-----------------
In addition to the MCP protocol endpoint, this server exposes:
- GET /health - Health check endpoint (returns 200 OK if healthy)
- GET /info - Server information endpoint (returns JSON with version, etc.)

USAGE:
------
    # Start the server
    marketing-connect-mcp

    # With custom host/port
    marketing-connect-mcp --host 0.0.0.0 --port 8080

    # With debug logging
    MCP_DEBUG=true marketing-connect-mcp
"""

import argparse
import sys
from datetime import datetime, timezone
from typing import NoReturn

from starlette.requests import Request
from starlette.responses import JSONResponse

from marketing_connect_mcp_services.config import settings
from marketing_connect_mcp_services.server import mcp


# Track server start time for uptime calculation
_start_time: datetime | None = None


# =============================================================================
# CUSTOM ROUTES (Health/Info endpoints)
# =============================================================================
# These are registered with FastMCP's custom_route decorator


@mcp.custom_route("/", methods=["GET"])
async def root_endpoint(request: Request) -> JSONResponse:
    """
    Root endpoint - provides quick overview.
    """
    return JSONResponse({
        "service": settings.server_name,
        "version": settings.server_version,
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "info": "/info",
        },
        "status": "running",
    })


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """
    Health check endpoint.

    Returns 200 OK if the server is running.
    """
    return JSONResponse({
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.custom_route("/info", methods=["GET"])
async def info_endpoint(request: Request) -> JSONResponse:
    """
    Info endpoint.

    Returns server metadata for deployment verification.
    """
    uptime_seconds = None
    if _start_time:
        uptime_seconds = (datetime.now(timezone.utc) - _start_time).total_seconds()

    return JSONResponse({
        "app": {
            "name": settings.server_name,
            "version": settings.server_version,
            "description": "Marketing Connect MCP Server",
        },
        "server": {
            "host": settings.host,
            "port": settings.port,
            "debug": settings.debug,
            "log_level": settings.log_level,
        },
        "config": {
            "base_url": settings.base_url,
            "region": settings.region,
        },
        "runtime": {
            "start_time": _start_time.isoformat() if _start_time else None,
            "uptime_seconds": uptime_seconds,
        },
    })


# =============================================================================
# SERVER RUNNER
# =============================================================================


def run_server(host: str, port: int) -> NoReturn:
    """
    Start the MCP server with HTTP transport and health endpoints.

    Args:
        host: IP address to bind to
              "0.0.0.0" = listen on all network interfaces (accessible externally)
              "127.0.0.1" = localhost only (not accessible externally)
        port: TCP port number (1-65535)
    """
    global _start_time
    _start_time = datetime.now(timezone.utc)

    # Print startup info
    print()
    print("=" * 60)
    print(f"  {settings.server_name} v{settings.server_version}")
    print("=" * 60)
    print()
    print(f"  Server running at: http://{host}:{port}")
    print()
    print("  Endpoints:")
    print(f"    - MCP Protocol:  http://{host}:{port}/mcp")
    print(f"    - Health Check:  http://{host}:{port}/health")
    print(f"    - Server Info:   http://{host}:{port}/info")
    print()
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)
    print()

    # Use FastMCP's built-in run method with streamable HTTP transport
    # Note: host/port are configured in server.py via settings
    mcp.run(transport="streamable-http")

    sys.exit(0)


def main() -> None:
    """
    Main entry point - parses command line arguments and starts server.
    """
    parser = argparse.ArgumentParser(
        prog="marketing-connect-mcp",
        description="Marketing Connect MCP Server - AI integration services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  marketing-connect-mcp                    # Start with defaults (0.0.0.0:8000)
  marketing-connect-mcp --port 3000        # Custom port
  marketing-connect-mcp --host 127.0.0.1   # Localhost only

Environment Variables:
  MCP_HOST=0.0.0.0       Host to bind to
  MCP_PORT=8000          Port to listen on
  MCP_DEBUG=true         Enable debug mode
  MCP_LOG_LEVEL=DEBUG    Set log level
  MCP_BASE_URL=...       Application base URL
  MCP_REGION=...         Deployment region

Endpoints:
  /mcp      - MCP protocol endpoint (for AI clients)
  /health   - Health check (returns {"status": "UP"})
  /info     - Server information
        """,
    )

    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host/IP to bind to (default: {settings.host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to listen on (default: {settings.port})",
    )

    args = parser.parse_args()

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
