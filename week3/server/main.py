"""Gmail MCP Server - STDIO Entry Point."""
from .tools import mcp
from .logger import logger


def main():
    """Run the MCP server in STDIO mode."""
    logger.info("Starting Gmail MCP Server (STDIO mode)")
    try:
        mcp.run()  # STDIO transport by default
    except Exception as e:
        logger.error(f"Server crashed: {e}")
        raise


if __name__ == "__main__":
    main()
