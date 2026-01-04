# Demo MCP Server

A demo MCP (Model Context Protocol) server built with FastMCP 2.0, featuring calculator tools, text processing utilities, and resource endpoints.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Install dependencies
uv sync

# Or install in development mode
uv pip install -e .
```

## Running the Server

### Using uv run (recommended)

```bash
# Run with stdio transport (default, for CLI integration)
uv run python mcp_server.py

# Run with FastMCP CLI
uv run fastmcp run mcp_server.py:mcp

# Run with HTTP transport on port 8000
uv run fastmcp run mcp_server.py:mcp --transport http --port 8000
```

### Direct execution (after installation)

```bash
# Run with stdio transport
python mcp_server.py

# Run with FastMCP CLI
fastmcp run mcp_server.py:mcp
```

## Available Tools

### Calculator Tools

| Tool | Description | Example |
|------|-------------|---------|
| `add(a, b)` | Add two numbers | `add(5, 3)` → `8` |
| `subtract(a, b)` | Subtract b from a | `subtract(10, 4)` → `6` |
| `multiply(a, b)` | Multiply two numbers | `multiply(3, 4)` → `12` |
| `divide(a, b)` | Divide a by b | `divide(10, 2)` → `5` |
| `power(base, exponent)` | Raise base to power | `power(2, 3)` → `8` |
| `sqrt(n)` | Square root | `sqrt(16)` → `4` |

### Text Processing Tools

| Tool | Description | Example |
|------|-------------|---------|
| `word_count(text)` | Count words, chars, lines | Returns dict with counts |
| `reverse_text(text)` | Reverse text | `reverse_text("hello")` → `"olleh"` |
| `to_uppercase(text)` | Convert to uppercase | `to_uppercase("hello")` → `"HELLO"` |
| `to_lowercase(text)` | Convert to lowercase | `to_lowercase("HELLO")` → `"hello"` |

### Utility Tools

| Tool | Description |
|------|-------------|
| `current_time()` | Get current date/time in ISO format |
| `greet(name, greeting)` | Generate personalized greeting |
| `echo_with_context(message)` | Echo message with context info |

## Available Resources

| URI | Description |
|-----|-------------|
| `resource://greeting` | Simple greeting message |
| `resource://server-info` | Server information and metadata |
| `resource://help` | Help documentation |
| `weather://{city}/current` | Mock weather data for a city |

## Prompt Templates

| Prompt | Description |
|--------|-------------|
| `analyze_text_prompt(text)` | Template for text analysis |
| `code_review_prompt(code, language)` | Template for code review |

## Integration with Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "demo-server": {
      "command": "/opt/miniconda3/bin/uv",
      "args": ["run", "--directory", "/Users/xuyin/Documents/Repository/modern-software-dev-assignments/lectures/week2/code", "python", "mcp_server.py"]
    }
  }
}
```

Or if using HTTP transport:

```json
{
  "mcpServers": {
    "demo-server": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Testing with a Client

```python
import asyncio
from fastmcp import Client

async def test_server():
    async with Client("http://localhost:8000/mcp") as client:
        # Call a tool
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"5 + 3 = {result}")

        # Read a resource
        resource = await client.read_resource("resource://server-info")
        print(f"Server info: {resource}")

asyncio.run(test_server())
```

## Debug
``` bash
npx @modelcontextprotocol/inspector uv run mcp_server.py
```
## Project Structure

```
.
├── mcp_server.py      # Main MCP server implementation
├── pyproject.toml     # Project configuration and dependencies
└── README.md          # This file
```

## License

MIT
