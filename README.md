# Marketing Connect MCP Services

A Model Context Protocol (MCP) server for Marketing Connect AI integrations.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard from Anthropic that enables AI models to securely interact with external tools and data sources. This server exposes:

- **Tools**: Functions the AI can invoke (like API endpoints)
- **Resources**: Data loaded into AI context (like configuration or schemas)
- **Prompts**: Reusable interaction templates

## What is FastMCP?

[FastMCP](https://gofastmcp.com/getting-started/welcome) is a high-level Python framework that simplifies building MCP servers. It provides a decorator-based API similar to FastAPI, reducing boilerplate and accelerating development.

### Why Use FastMCP?

| Benefit | Description |
|---------|-------------|
| **Minimal Boilerplate** | Simple decorators like `@mcp.tool()` replace complex class hierarchies |
| **Automatic Schema Generation** | Input/output schemas generated from Python type hints |
| **Built-in HTTP Transport** | Production-ready server with health checks and SSE support |
| **Pydantic Integration** | Native support for Pydantic models as tool inputs |

### MCP SDK vs FastMCP Comparison

**Without FastMCP** (using low-level MCP SDK):

```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="greet",
            description="Greet a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User name"}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "greet":
        return [TextContent(type="text", text=f"Hello {arguments['name']}!")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
```

**With FastMCP**:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def greet(name: str) -> str:
    """Greet a user."""
    return f"Hello {name}!"

if __name__ == "__main__":
    mcp.run()
```

FastMCP reduces ~30 lines to ~10 while maintaining full MCP protocol compliance.

## Quick Start

### Prerequisites

Install from Devshell:
- `Python 3.11+` (3.13 recommended)
- `make`
- `buildi-cli`
- `tfl`
- `httpie`

### Installation

```bash
# Install uv package manager
make ci-prebuild

# Install all dependencies (creates .venv automatically)
make build
```

### Model Generation

This server uses Pydantic models generated from an OpenAPI specification. The models are generated using `datamodel-code-generator`.

#### From Local .tgz (npm-packed OpenAPI spec)

```bash
# Command to be run in marketing-connect-spec/marketing-connect-mcp-services (in terminal)
  # Inside path src/main/resources/model/api dir
tar -czvf models.tgz mcpservices.api.yml schema/

# Generate models from a local .tgz file
make generate-models SPEC_TGZ=path/to/models.tgz
```

#### From Artifactory URL

```bash
# Generate models from a URL (e.g., artifactory)
make generate-models-url SPEC_URL=https://artifactory.example.com/openapi-spec.tgz
```

#### From Local YAML File

```bash
# Generate models directly from a local OpenAPI YAML file
make generate-models-local SPEC_FILE=path/to/openapi.yaml
```

#### Model Management

```bash
# Show generated model classes
make models-show

# Clean generated models
make models-clean
```

The generated models are placed in `src/marketing_connect_mcp_services/models/` and can be imported as:

```python
from marketing_connect_mcp_services.models import ProductDetails, GreetingResponse
```

### Running the Server

```bash
# Start the server (default: 0.0.0.0:8000)
make run

# Or with debug mode
make run-debug

# Or directly with uv
uv run marketing-connect-mcp --port 3000
```

### Verify Deployment

The server exposes health check endpoints for deployment verification:

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service overview |
| `GET /health` | Health check (returns `{"status": "UP"}`) |
| `GET /info` | Server metadata (version, config, uptime) |
| `POST /mcp` | MCP protocol endpoint (for AI clients) |

```bash
# Check health
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/info

# Service overview
curl http://localhost:8000/
```

### Testing the MCP Protocol

The MCP endpoint uses the Streamable HTTP transport and requires specific headers:

```bash
# Initialize MCP session
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0"}
    }
  }'
```

Expected response (SSE format):
```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{...},"serverInfo":{"name":"marketing-connect-mcp-services","version":"..."}}}
```

```bash
# List available tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Note:** The MCP protocol is stateful. The `initialize` request works without a session, but subsequent requests like `tools/list` and `tools/call` require a session ID header (`Mcp-Session-Id`) from the initialization response. For full protocol testing, use an MCP client library

## Project Structure

```
marketing-connect-mcp-services/
├── src/marketing_connect_mcp_services/
│   ├── __init__.py          # Package exports
│   ├── server.py            # FastMCP server setup
│   ├── config.py            # Pydantic settings
│   ├── cli.py               # CLI entry point
│   ├── tools/               # MCP tools (AI-invokable functions)
│   │   ├── __init__.py
│   │   └── example.py       # Example tool patterns
│   ├── resources/           # MCP resources (context data)
│   │   ├── __init__.py
│   │   └── example.py       # Example resource patterns
│   └── prompts/             # MCP prompts (interaction templates)
│       ├── __init__.py
│       └── example.py       # Example prompt patterns
├── tests/                   # Test suite
├── pyproject.toml           # Hatchling build config + dependencies
├── uv.lock                  # Dependency lock file
├── Makefile                 # Build commands
└── .env.example             # Environment template
```

## Build System

This project uses modern Python tooling:

| Tool | Purpose |
|------|---------|
| **[Hatchling](https://hatch.pypa.io/)** | Build backend (PEP 517) |
| **[uv](https://github.com/astral-sh/uv)** | Fast package manager (10-100x faster than pip) |

### Why uv?

- **Fast**: Written in Rust, installs packages 10-100x faster than pip
- **Lock files**: `uv.lock` ensures reproducible builds
- **Compatible**: Works with standard `pyproject.toml`
- **Simple**: Single binary, no plugins needed

## Configuration

Configuration is managed via environment variables (prefix: `MCP_`).

Copy `.env.example` to `.env` and customize:

```bash
# Server identity
MCP_SERVER_NAME=marketing-connect-mcp-services
MCP_SERVER_VERSION=1.0.0

# HTTP server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Logging
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO

# Application settings
MCP_BASE_URL=https://your-app-url.com
MCP_REGION=us-east-1
```

### JPMC Artifact Repository

The PyPI index is configured in `pyproject.toml`:

```toml
[tool.uv]
index-url = "https://artifacts-read.gkp.jpmchase.net/artifactory/api/pypi/pypi/simple"
```

You can also override via environment variable:
```bash
export UV_INDEX_URL=https://your-pypi-mirror.com/simple
```

## Development

### Testing

```bash
# Run tests
make test

# Run tests with coverage
make cover

# Verbose output
make test-verbose
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Auto-fix lint issues
make lint-fix

# Type check
make typecheck

# Run all checks
make check
```

### Pre-commit Hooks

```bash
make precommit
```

### Dependency Management

```bash
# Update lock file
make lock

# Update all dependencies to latest
make update

# Install production deps only
make build-prod
```

## Adding Custom Integrations

### Adding a Tool

Create a new file in `tools/` and register it:

```python
# tools/my_tools.py
from marketing_connect_mcp_services.server import mcp

@mcp.tool()
async def my_custom_tool(param: str) -> str:
    """Description the AI will see."""
    return f"Result: {param}"
```

Then import in `server.py`:

```python
from marketing_connect_mcp_services.tools import my_tools  # noqa: F401
```

### Adding a Resource

```python
# resources/my_resources.py
from marketing_connect_mcp_services.server import mcp

@mcp.resource("myapp://config")
async def get_config() -> str:
    """Returns configuration data."""
    return "config data"
```

### Adding a Prompt

```python
# prompts/my_prompts.py
from marketing_connect_mcp_services.server import mcp

@mcp.prompt()
async def analysis_prompt(topic: str) -> str:
    """Generate an analysis prompt."""
    return f"Please analyze: {topic}"
```

## CI/CD

```bash
# Full CI pipeline (clean, build, test, package)
make ci

# Generate SSAP reports
make ssap

# Build wheel package
make package
```

## Make Targets

| Target | Description |
|--------|-------------|
| `make run` | Start the MCP server |
| `make run-debug` | Start with debug logging |
| `make build` | Install all dependencies |
| `make build-prod` | Install production deps only |
| `make test` | Run tests |
| `make cover` | Run tests with coverage |
| `make format` | Format code |
| `make lint` | Lint code |
| `make typecheck` | Run mypy type checking |
| `make check` | Run lint + typecheck + test |
| `make generate-models` | Generate Pydantic models from .tgz |
| `make generate-models-url` | Generate models from URL |
| `make generate-models-local` | Generate models from local YAML |
| `make models-show` | Show generated model classes |
| `make models-clean` | Remove generated models |
| `make lock` | Update uv.lock |
| `make update` | Update all dependencies |
| `make ci` | Full CI pipeline |
| `make ssap` | Generate SSAP reports |
| `make package` | Build wheel |
| `make help` | Show all targets |

## Documentation

- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastMCP SDK](https://github.com/anthropics/mcp)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Hatchling](https://hatch.pypa.io/)