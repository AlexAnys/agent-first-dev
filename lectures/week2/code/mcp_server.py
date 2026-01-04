"""
MCP Server built with FastMCP 2.0

This server provides example tools and resources demonstrating FastMCP capabilities.
"""

import math
from datetime import datetime
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

# Create the FastMCP server instance
mcp = FastMCP(
    name="DemoMCPServer",
    instructions="A demo MCP server with calculator, text processing, and utility tools."
)


# ============================================================================
# TOOLS - Executable functions that clients can call
# ============================================================================

@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ToolError("Division by zero is not allowed.")
    return a / b


@mcp.tool
def power(
    base: Annotated[float, Field(description="The base number")],
    exponent: Annotated[float, Field(description="The exponent")] = 2
) -> float:
    """Raise a number to a power. Defaults to squaring the number."""
    return math.pow(base, exponent)


@mcp.tool
def sqrt(n: float) -> float:
    """Calculate the square root of a number."""
    if n < 0:
        raise ToolError("Cannot calculate square root of a negative number.")
    return math.sqrt(n)


@mcp.tool
def word_count(text: str) -> dict:
    """Count words, characters, and lines in the given text."""
    words = len(text.split())
    characters = len(text)
    characters_no_spaces = len(text.replace(" ", ""))
    lines = len(text.splitlines()) if text else 0

    return {
        "words": words,
        "characters": characters,
        "characters_no_spaces": characters_no_spaces,
        "lines": lines
    }


@mcp.tool
def reverse_text(text: str) -> str:
    """Reverse the given text."""
    return text[::-1]


@mcp.tool
def to_uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


@mcp.tool
def to_lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


@mcp.tool
def current_time() -> str:
    """Get the current date and time."""
    return datetime.now().isoformat()


@mcp.tool
def greet(
    name: Annotated[str, Field(description="The name to greet")],
    greeting: Annotated[str, Field(description="The greeting to use")] = "Hello"
) -> str:
    """Generate a personalized greeting message."""
    return f"{greeting}, {name}!"


@mcp.tool
async def echo_with_context(message: str, ctx: Context) -> dict:
    """Echo back a message with context information."""
    await ctx.info(f"Echoing message: {message}")
    return {
        "message": message,
        "echoed_at": datetime.now().isoformat(),
        "request_id": ctx.request_id
    }


# ============================================================================
# RESOURCES - Data sources that clients can read
# ============================================================================

@mcp.resource("resource://greeting")
def get_greeting() -> str:
    """Provides a simple greeting message."""
    return "Hello from FastMCP 2.0! This is a demo MCP server."


@mcp.resource("resource://server-info")
def get_server_info() -> dict:
    """Provides information about this MCP server."""
    return {
        "name": "DemoMCPServer",
        "version": "1.0.0",
        "framework": "FastMCP 2.0",
        "tools_available": [
            "add", "subtract", "multiply", "divide",
            "power", "sqrt", "word_count", "reverse_text",
            "to_uppercase", "to_lowercase", "current_time",
            "greet", "echo_with_context"
        ],
        "started_at": datetime.now().isoformat()
    }


@mcp.resource("resource://help")
def get_help() -> str:
    """Provides help documentation for this server."""
    return """
# Demo MCP Server Help

## Calculator Tools
- add(a, b): Add two numbers
- subtract(a, b): Subtract b from a
- multiply(a, b): Multiply two numbers
- divide(a, b): Divide a by b
- power(base, exponent): Raise base to exponent power
- sqrt(n): Calculate square root

## Text Processing Tools
- word_count(text): Count words, characters, and lines
- reverse_text(text): Reverse text
- to_uppercase(text): Convert to uppercase
- to_lowercase(text): Convert to lowercase

## Utility Tools
- current_time(): Get current date/time
- greet(name, greeting): Generate greeting message
- echo_with_context(message): Echo message with context info

## Resources
- resource://greeting: Simple greeting
- resource://server-info: Server information
- resource://help: This help text
- weather://{city}/current: Weather for a city (template)
"""


# Resource template with parameters
@mcp.resource("weather://{city}/current")
def get_weather(city: str) -> dict:
    """Provides mock weather information for a specific city."""
    # This is mock data - in a real server, you'd call a weather API
    return {
        "city": city.capitalize(),
        "temperature": 22,
        "condition": "Sunny",
        "humidity": 65,
        "unit": "celsius",
        "retrieved_at": datetime.now().isoformat()
    }


# ============================================================================
# PROMPTS - Reusable prompt templates
# ============================================================================

@mcp.prompt
def analyze_text_prompt(text: str) -> str:
    """A prompt template for analyzing text."""
    return f"""Please analyze the following text and provide:
1. A brief summary
2. The main topics covered
3. The tone/sentiment
4. Any key insights

Text to analyze:
{text}
"""


@mcp.prompt
def code_review_prompt(code: str, language: str = "python") -> str:
    """A prompt template for code review."""
    return f"""Please review the following {language} code and provide:
1. Code quality assessment
2. Potential bugs or issues
3. Suggestions for improvement
4. Best practices recommendations

Code to review:
```{language}
{code}
```
"""


# ============================================================================
# RUN THE SERVER
# ============================================================================

if __name__ == "__main__":
    # Run with stdio transport (default, for CLI integration)
    # Use: python mcp_server.py

    # For HTTP transport, uncomment the following:
    # mcp.run(transport="http", port=8000)

    mcp.run()
