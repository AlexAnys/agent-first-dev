"""MCP tool definitions for Gmail operations."""
from typing import Optional
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from .gmail_client import (
    create_gmail_service,
    search_messages_async,
    get_message_async
)
from .logger import logger

mcp = FastMCP("Gmail MCP Server")
_gmail_service = None


def get_service():
    """Lazy initialization of Gmail service."""
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = create_gmail_service()
    return _gmail_service


def validate_query(query: str) -> str:
    """Validate and sanitize search query."""
    if not query or not query.strip():
        raise ToolError("Query cannot be empty")
    return query.strip()


def validate_max_results(max_results: int) -> int:
    """Validate max_results parameter."""
    if max_results < 1:
        raise ToolError("max_results must be at least 1")
    if max_results > 100:
        logger.warning(f"max_results capped from {max_results} to 100")
        return 100
    return max_results


def validate_message_id(message_id: str) -> str:
    """Validate message ID format."""
    if not message_id or not message_id.strip():
        raise ToolError("Message ID cannot be empty")
    return message_id.strip()


@mcp.tool(
    annotations={
        "title": "Search Gmail Messages",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
async def search_messages(
    query: str,
    max_results: int = 10
) -> dict:
    """
    Search Gmail messages using Gmail query syntax.

    Args:
        query: Gmail search query (e.g., "from:sender@example.com is:unread")
        max_results: Maximum number of results (1-100, default: 10)

    Returns:
        Dictionary with messages list, count, and pagination info
    """
    validated_query = validate_query(query)
    validated_max = validate_max_results(max_results)

    logger.info(f"Tool invoked: search_messages(query='{validated_query}')")

    service = get_service()
    return await search_messages_async(service, validated_query, validated_max)


@mcp.tool(
    annotations={
        "title": "Get Gmail Message",
        "readOnlyHint": True,
        "openWorldHint": True
    }
)
async def get_message(
    message_id: str,
    format: str = "full"
) -> dict:
    """
    Get full details of a specific Gmail message.

    Args:
        message_id: The ID of the message to retrieve
        format: Response format (full, metadata, minimal, raw)

    Returns:
        Complete message with headers, body, labels, and metadata
    """
    validated_id = validate_message_id(message_id)
    valid_formats = {"full", "metadata", "minimal", "raw"}

    if format not in valid_formats:
        raise ToolError(f"Invalid format. Must be one of: {valid_formats}")

    logger.info(f"Tool invoked: get_message(id='{validated_id}')")

    service = get_service()
    return await get_message_async(service, validated_id, format)
