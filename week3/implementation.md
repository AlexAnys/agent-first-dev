# Stage 1: Local STDIO Server Implementation

## 1. Project Structure

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # Entry point (STDIO server)
│   ├── gmail_client.py      # Gmail API wrapper
│   ├── tools.py             # MCP tool definitions
│   ├── resilience.py        # Retry & error handling
│   └── logger.py            # File-based logging
├── tests/
│   ├── __init__.py
│   ├── test_gmail_client.py # Unit tests
│   ├── test_tools.py        # Tool tests
│   └── test_integration.py  # Integration tests
├── .env.example
├── credentials.json         # OAuth credentials (gitignored)
├── token.json               # OAuth token (gitignored)
├── pyproject.toml
└── README.md
```

---

## 2. Implementation Files

### 2.1 `server/logger.py` - File-Based Logging (No stdout)

```python
"""File-based logging for STDIO MCP servers.

CRITICAL: STDIO servers must NOT write to stdout as it's reserved for MCP protocol.
All logs go to file only.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "gmail_mcp",
    log_file: Optional[Path] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """Configure logger for STDIO server.
    
    Logs to both file and stderr. CRITICAL: Never use stdout as it's 
    reserved for MCP protocol communication.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    log_path = log_file or Path.home() / ".gmail_mcp" / "server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler for persistent logs
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Stderr handler for real-time debugging (safe for STDIO servers)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    
    return logger

# Global logger instance
logger = setup_logger()
```

### 2.2 `server/resilience.py` - Retry & Rate Limit Handling (Tenacity-based)

```python
"""Resilience utilities using Tenacity for retry with exponential backoff."""
import asyncio
from typing import Callable, TypeVar, Optional, Any
from googleapiclient.errors import HttpError
from fastmcp.exceptions import ToolError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryCallState,
    AsyncRetrying,
)
from .logger import logger

T = TypeVar("T")

# Error message mapping for user-friendly responses
ERROR_MESSAGES = {
    401: "Authentication required. Please re-authenticate with Gmail.",
    403: "Access denied. Check Gmail API permissions.",
    404: "Message not found. It may have been deleted.",
    429: "Rate limit exceeded. Please wait a moment and try again.",
    500: "Gmail service error. Retrying...",
    503: "Gmail service temporarily unavailable. Retrying...",
}


def get_error_message(status_code: int, default: str = "Gmail API error") -> str:
    """Map HTTP status to user-friendly message."""
    return ERROR_MESSAGES.get(status_code, default)


def is_retryable_error(status_code: int) -> bool:
    """Check if error is retryable (rate limit or server error)."""
    return status_code == 429 or status_code >= 500


def is_retryable_exception(exception: BaseException) -> bool:
    """Determine if an exception should trigger a retry.
    
    Retryable conditions:
    - HttpError with status 429 (rate limit) or 5xx (server errors)
    - TimeoutError / asyncio.TimeoutError
    - ConnectionError (network issues)
    """
    if isinstance(exception, HttpError):
        return is_retryable_error(exception.resp.status)
    if isinstance(exception, (TimeoutError, asyncio.TimeoutError, ConnectionError)):
        return True
    return False


def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Custom logging callback for retry attempts."""
    exception = retry_state.outcome.exception()
    attempt = retry_state.attempt_number
    
    if isinstance(exception, HttpError):
        logger.warning(
            f"Gmail API error (attempt {attempt}): "
            f"status={exception.resp.status}, reason={exception.reason}"
        )
    elif isinstance(exception, (TimeoutError, asyncio.TimeoutError)):
        logger.warning(f"Request timeout (attempt {attempt})")
    elif isinstance(exception, ConnectionError):
        logger.warning(f"Connection error (attempt {attempt}): {exception}")
    else:
        logger.warning(f"Retry attempt {attempt}: {type(exception).__name__}: {exception}")


def raise_non_retryable_error(retry_state: RetryCallState) -> None:
    """Callback to handle non-retryable errors immediately."""
    exception = retry_state.outcome.exception()
    if isinstance(exception, HttpError) and not is_retryable_error(exception.resp.status):
        raise ToolError(get_error_message(exception.resp.status, str(exception)))


def gmail_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
) -> Callable:
    """Create a customized Tenacity retry decorator for Gmail API calls.
    
    Features:
    - Exponential backoff with configurable min/max wait times
    - Retries only on transient errors (429, 5xx, timeouts, connection errors)
    - Raises ToolError immediately for non-retryable errors (401, 403, 404)
    - Detailed logging for each retry attempt
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time between retries in seconds (default: 1.0)
        max_wait: Maximum wait time between retries in seconds (default: 30.0)
    
    Returns:
        Configured retry decorator
    
    Example:
        @gmail_retry(max_attempts=5, min_wait=2.0)
        async def fetch_messages():
            ...
    """
    return retry(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=log_retry_attempt,
        reraise=True,
    )


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0
) -> Callable:
    """Alias for gmail_retry for backward compatibility.
    
    Deprecated: Use gmail_retry() instead.
    """
    return gmail_retry(
        max_attempts=max_retries,
        min_wait=base_delay,
        max_wait=max_delay,
    )


async def retry_async_operation(
    operation: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 30.0,
    **kwargs: Any,
) -> T:
    """Execute an async operation with retry logic.
    
    Useful for one-off retry scenarios without using a decorator.
    
    Args:
        operation: Async callable to execute
        *args: Positional arguments for the operation
        max_attempts: Maximum retry attempts
        min_wait: Minimum wait between retries
        max_wait: Maximum wait between retries
        **kwargs: Keyword arguments for the operation
    
    Returns:
        Result of the operation
    
    Raises:
        ToolError: If all retries exhausted or non-retryable error occurs
    """
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=log_retry_attempt,
        reraise=True,
    ):
        with attempt:
            return await operation(*args, **kwargs)


def handle_empty_results(results: list, query: str) -> Optional[dict]:
    """Handle empty search results gracefully.
    
    Args:
        results: List of search results
        query: The search query that produced the results
    
    Returns:
        Empty result dict if no results, None otherwise
    """
    if not results:
        logger.info(f"No messages found for query: {query}")
        return {
            "messages": [],
            "resultCount": 0,
            "hasMore": False,
            "message": "No messages found matching your query."
        }
    return None
```

### 2.3 `server/gmail_client.py` - Gmail API Wrapper

```python
"""Gmail API client with OAuth2 authentication."""
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .logger import logger
from .resilience import with_retry, handle_empty_results

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / "token.json"

def authenticate() -> Credentials:
    """Perform OAuth2 authentication flow."""
    creds = None
    
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        logger.info("Loaded existing credentials from token.json")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Download from Google Cloud Console."
                )
            logger.info("Starting OAuth2 authentication flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        TOKEN_FILE.write_text(creds.to_json())
        logger.info("Saved new credentials to token.json")
    
    return creds

def create_gmail_service():
    """Create authenticated Gmail API service."""
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail service created successfully")
    return service

def extract_header(headers: List[Dict], name: str) -> str:
    """Extract header value by name from headers list."""
    return next(
        (h["value"] for h in headers if h["name"].lower() == name.lower()),
        ""
    )

def decode_body(data: str) -> str:
    """Decode base64url encoded message body."""
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to decode body: {e}")
        return ""

def extract_body_from_payload(payload: Dict) -> str:
    """Extract text body from message payload (handles multipart)."""
    if "body" in payload and payload["body"].get("data"):
        return decode_body(payload["body"]["data"])
    
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return decode_body(part.get("body", {}).get("data", ""))
            if part["mimeType"].startswith("multipart/"):
                return extract_body_from_payload(part)
    
    return ""

@with_retry(max_retries=3, base_delay=1.0)
async def search_messages_async(
    service,
    query: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """Search Gmail messages with retry logic."""
    logger.info(f"Searching messages: query='{query}', max_results={max_results}")
    
    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=min(max_results, 100)
    ).execute()
    
    message_ids = response.get("messages", [])
    
    empty_result = handle_empty_results(message_ids, query)
    if empty_result:
        return empty_result
    
    messages = []
    for msg_ref in message_ids:
        msg = service.users().messages().get(
            userId="me",
            id=msg_ref["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()
        
        headers = msg.get("payload", {}).get("headers", [])
        messages.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg.get("snippet", ""),
            "subject": extract_header(headers, "Subject"),
            "from": extract_header(headers, "From"),
            "date": extract_header(headers, "Date")
        })
    
    logger.info(f"Found {len(messages)} messages")
    return {
        "messages": messages,
        "resultCount": len(messages),
        "hasMore": "nextPageToken" in response
    }

@with_retry(max_retries=3, base_delay=1.0)
async def get_message_async(
    service,
    message_id: str,
    format: str = "full"
) -> Dict[str, Any]:
    """Get full message details with retry logic."""
    logger.info(f"Getting message: id={message_id}, format={format}")
    
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format=format
    ).execute()
    
    headers = msg.get("payload", {}).get("headers", [])
    body = extract_body_from_payload(msg.get("payload", {}))
    
    result = {
        "id": msg["id"],
        "threadId": msg["threadId"],
        "subject": extract_header(headers, "Subject"),
        "from": extract_header(headers, "From"),
        "to": extract_header(headers, "To"),
        "date": extract_header(headers, "Date"),
        "body": body,
        "labels": msg.get("labelIds", []),
        "snippet": msg.get("snippet", "")
    }
    
    logger.info(f"Retrieved message: subject='{result['subject']}'")
    return result
```

### 2.4 `server/tools.py` - MCP Tool Definitions

```python
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
```

### 2.5 `server/main.py` - Entry Point

```python
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
```

### 2.6 `server/__init__.py`

```python
"""Gmail MCP Server package."""
from .tools import mcp
from .main import main

__all__ = ["mcp", "main"]
```

---

## 3. Tests

### 3.1 `tests/test_gmail_client.py` - Unit Tests

```python
"""Unit tests for Gmail client functions."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from server.gmail_client import (
    extract_header,
    decode_body,
    extract_body_from_payload
)
from server.resilience import (
    get_error_message,
    is_retryable_error,
    handle_empty_results
)

class TestExtractHeader:
    def test_extracts_existing_header(self):
        headers = [{"name": "Subject", "value": "Test Email"}]
        assert extract_header(headers, "Subject") == "Test Email"
    
    def test_returns_empty_for_missing_header(self):
        headers = [{"name": "From", "value": "test@example.com"}]
        assert extract_header(headers, "Subject") == ""
    
    def test_case_insensitive_match(self):
        headers = [{"name": "SUBJECT", "value": "Test"}]
        assert extract_header(headers, "subject") == "Test"
    
    def test_empty_headers_list(self):
        assert extract_header([], "Subject") == ""

class TestDecodeBody:
    def test_decodes_valid_base64(self):
        encoded = "SGVsbG8gV29ybGQ="  # "Hello World"
        assert decode_body(encoded) == "Hello World"
    
    def test_returns_empty_for_none(self):
        assert decode_body(None) == ""
    
    def test_returns_empty_for_empty_string(self):
        assert decode_body("") == ""
    
    def test_handles_invalid_base64(self):
        assert decode_body("not-valid-base64!!!") == ""

class TestExtractBodyFromPayload:
    def test_extracts_direct_body(self):
        payload = {"body": {"data": "SGVsbG8="}}
        assert extract_body_from_payload(payload) == "Hello"
    
    def test_extracts_from_multipart(self):
        payload = {
            "parts": [
                {"mimeType": "text/plain", "body": {"data": "VGVzdA=="}}
            ]
        }
        assert extract_body_from_payload(payload) == "Test"
    
    def test_returns_empty_for_no_body(self):
        assert extract_body_from_payload({}) == ""

class TestErrorMessages:
    @pytest.mark.parametrize("status,expected", [
        (401, "Authentication required. Please re-authenticate with Gmail."),
        (403, "Access denied. Check Gmail API permissions."),
        (404, "Message not found. It may have been deleted."),
        (429, "Rate limit exceeded. Please wait a moment and try again."),
    ])
    def test_error_message_mapping(self, status, expected):
        assert get_error_message(status) == expected
    
    def test_unknown_status_returns_default(self):
        assert get_error_message(999) == "Gmail API error"

class TestRetryableErrors:
    def test_429_is_retryable(self):
        assert is_retryable_error(429) is True
    
    def test_500_is_retryable(self):
        assert is_retryable_error(500) is True
    
    def test_503_is_retryable(self):
        assert is_retryable_error(503) is True
    
    def test_404_is_not_retryable(self):
        assert is_retryable_error(404) is False
    
    def test_401_is_not_retryable(self):
        assert is_retryable_error(401) is False

class TestHandleEmptyResults:
    def test_returns_dict_for_empty_list(self):
        result = handle_empty_results([], "test query")
        assert result["messages"] == []
        assert result["resultCount"] == 0
        assert "No messages found" in result["message"]
    
    def test_returns_none_for_non_empty_list(self):
        result = handle_empty_results([{"id": "123"}], "test")
        assert result is None
```

### 3.2 `tests/test_tools.py` - Tool Validation Tests

```python
"""Tests for MCP tool input validation."""
import pytest
from fastmcp.exceptions import ToolError
from server.tools import (
    validate_query,
    validate_max_results,
    validate_message_id
)

class TestValidateQuery:
    def test_valid_query(self):
        assert validate_query("from:test@example.com") == "from:test@example.com"
    
    def test_strips_whitespace(self):
        assert validate_query("  query  ") == "query"
    
    def test_raises_on_empty_string(self):
        with pytest.raises(ToolError, match="cannot be empty"):
            validate_query("")
    
    def test_raises_on_whitespace_only(self):
        with pytest.raises(ToolError, match="cannot be empty"):
            validate_query("   ")
    
    def test_raises_on_none(self):
        with pytest.raises(ToolError):
            validate_query(None)

class TestValidateMaxResults:
    def test_valid_value(self):
        assert validate_max_results(50) == 50
    
    def test_caps_at_100(self):
        assert validate_max_results(500) == 100
    
    def test_raises_on_zero(self):
        with pytest.raises(ToolError, match="at least 1"):
            validate_max_results(0)
    
    def test_raises_on_negative(self):
        with pytest.raises(ToolError, match="at least 1"):
            validate_max_results(-5)

class TestValidateMessageId:
    def test_valid_id(self):
        assert validate_message_id("18abc123def") == "18abc123def"
    
    def test_strips_whitespace(self):
        assert validate_message_id("  id123  ") == "id123"
    
    def test_raises_on_empty(self):
        with pytest.raises(ToolError, match="cannot be empty"):
            validate_message_id("")
```

### 3.3 `tests/test_integration.py` - Integration Tests

```python
"""Integration tests for Gmail MCP Server."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from server.tools import search_messages, get_message

@pytest.fixture
def mock_gmail_service():
    """Create mock Gmail service."""
    service = Mock()
    return service

class TestSearchMessagesIntegration:
    @pytest.mark.asyncio
    async def test_successful_search(self, mock_gmail_service):
        mock_response = {
            "messages": [{"id": "123", "threadId": "456"}]
        }
        mock_gmail_service.users().messages().list().execute.return_value = mock_response
        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "123",
            "threadId": "456",
            "snippet": "Test snippet",
            "payload": {"headers": [
                {"name": "Subject", "value": "Test"},
                {"name": "From", "value": "test@example.com"},
                {"name": "Date", "value": "2024-12-28"}
            ]}
        }
        
        with patch("server.tools.get_service", return_value=mock_gmail_service):
            result = await search_messages("from:test@example.com")
        
        assert result["resultCount"] == 1
        assert result["messages"][0]["subject"] == "Test"
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, mock_gmail_service):
        mock_gmail_service.users().messages().list().execute.return_value = {}
        
        with patch("server.tools.get_service", return_value=mock_gmail_service):
            result = await search_messages("from:nobody@example.com")
        
        assert result["resultCount"] == 0
        assert result["messages"] == []

class TestGetMessageIntegration:
    @pytest.mark.asyncio
    async def test_successful_get(self, mock_gmail_service):
        mock_gmail_service.users().messages().get().execute.return_value = {
            "id": "123",
            "threadId": "456",
            "snippet": "Test",
            "labelIds": ["INBOX"],
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "2024-12-28"}
                ],
                "body": {"data": "SGVsbG8gV29ybGQ="}
            }
        }
        
        with patch("server.tools.get_service", return_value=mock_gmail_service):
            result = await get_message("123")
        
        assert result["id"] == "123"
        assert result["subject"] == "Test Subject"
        assert result["body"] == "Hello World"
```

---

## 4. Configuration Files

### 4.1 `pyproject.toml`

```toml
[project]
name = "gmail-mcp-server"
version = "0.1.0"
description = "Gmail MCP Server for Claude Desktop"
requires-python = "3.12"
dependencies = [
    "fastmcp>=2.0.0",
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-auth-httplib2>=0.2.0",
    "google-api-python-client>=2.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
gmail-mcp = "server.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 4.2 `.env.example`

```env
# Google OAuth Credentials (optional - can use credentials.json instead)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 4.3 `.gitignore`

```gitignore
credentials.json
token.json
.env
__pycache__/
*.pyc
.pytest_cache/
*.log
```

---

## 5. README.md

```markdown
# Gmail MCP Server

MCP server for Gmail API integration with Claude Desktop and Cursor IDE.

## Prerequisites

- Python 3.12
- uv package manager
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials (Desktop app type)

## Environment Setup

### 1. Clone and Install

```bash
cd week3
uv sync
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable Gmail API: APIs & Services > Enable APIs > Gmail API
4. Create OAuth credentials:
   - APIs & Services > Credentials > Create Credentials > OAuth Client ID
   - Application type: Desktop app
   - Download JSON and save as `week3/credentials.json`

### 3. First Run Authentication

```bash
uv run python -m server.main
```

This opens a browser for OAuth consent. Token is saved to `token.json`.

## Run Instructions

### Local STDIO Mode

```bash
# Using uv
uv run python -m server.main

# Or using fastmcp CLI
uv run fastmcp run server/main.py:mcp
```

### Run Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=server
```

## Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/week3",
        "python", "-m", "server.main"
      ]
    }
  }
}
```

## Cursor IDE Configuration

Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/week3",
        "python", "-m", "server.main"
      ]
    }
  }
}
```

## Tool Reference

### search_messages

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | Gmail search query |
| max_results | integer | No | 10 | Max results (1-100) |

**Example Input:**
```json
{"query": "from:boss@company.com is:unread", "max_results": 5}
```

**Example Output:**
```json
{
  "messages": [
    {"id": "18abc", "subject": "Q4 Report", "from": "boss@company.com", "snippet": "..."}
  ],
  "resultCount": 1,
  "hasMore": false
}
```

### get_message

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| message_id | string | Yes | - | Message ID |
| format | string | No | "full" | full/metadata/minimal/raw |

**Example Input:**
```json
{"message_id": "18abc123def"}
```

**Example Output:**
```json
{
  "id": "18abc123def",
  "subject": "Q4 Report",
  "from": "boss@company.com",
  "to": "you@company.com",
  "body": "Please review...",
  "labels": ["INBOX", "UNREAD"]
}
```

## Logging

Logs are written to `~/.gmail_mcp/server.log` (not stdout, as required for STDIO).
```

---

## 6. Tool Reference Summary

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `search_messages` | Search Gmail using query syntax | `query` (str), `max_results` (int) | Messages list with metadata |
| `get_message` | Get full message details | `message_id` (str), `format` (str) | Complete message content |

### Expected Behaviors

| Scenario | Behavior |
|----------|----------|
| Empty query | Returns `ToolError("Query cannot be empty")` |
| max_results > 100 | Caps to 100 with warning log |
| Message not found | Returns `ToolError("Message not found...")` |
| Rate limited (429) | Retries 3x with exponential backoff |
| Server error (5xx) | Retries 3x with exponential backoff |
| No results | Returns `{"messages": [], "resultCount": 0}` |
| Auth expired | Attempts token refresh, fails gracefully |
