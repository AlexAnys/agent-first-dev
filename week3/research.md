# Gmail MCP Server Research Document

## 1. Overview

This document contains research findings for building an MCP (Model Context Protocol) server that wraps the Gmail API. The server will expose two MCP tools for **searching messages** and **getting message details**.

---

## 2. Gmail API Research

### 2.1 API Endpoints

The Gmail API provides REST endpoints for managing Gmail messages. We will focus on two methods:

#### 2.1.1 `users.messages.list` - Search Messages

**HTTP Request:**
```
GET https://gmail.googleapis.com/gmail/v1/users/{userId}/messages
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `userId` | string | The user's email address. The special value `me` can be used to indicate the authenticated user. |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `maxResults` | integer (uint32) | Maximum number of messages to return. Defaults to 100. Maximum allowed value is 500. |
| `pageToken` | string | Page token to retrieve a specific page of results in the list. |
| `q` | string | Only return messages matching the specified query. Supports the same query format as the Gmail search box. Example: `"from:someuser@example.com is:unread"` |
| `labelIds[]` | string | Only return messages with labels that match all of the specified label IDs. |
| `includeSpamTrash` | boolean | Include messages from SPAM and TRASH in the results. |

**Response Body:**
```json
{
  "messages": [
    {
      "id": "string",
      "threadId": "string"
    }
  ],
  "nextPageToken": "string",
  "resultSizeEstimate": "integer"
}
```

> **Note:** The `list` method returns only `id` and `threadId`. Additional message details must be fetched using `messages.get`.

#### 2.1.2 `users.messages.get` - Get Message Details

**HTTP Request:**
```
GET https://gmail.googleapis.com/gmail/v1/users/{userId}/messages/{id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `userId` | string | The user's email address. The special value `me` indicates the authenticated user. |
| `id` | string | The ID of the message to retrieve. Usually retrieved using `messages.list`. |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | enum (Format) | The format to return the message in. Options: `minimal`, `full`, `raw`, `metadata`. |
| `metadataHeaders[]` | string | When format is `METADATA`, only include headers specified. |

**Response Body - Message Resource:**
```json
{
  "id": "string",
  "threadId": "string",
  "labelIds": ["string"],
  "snippet": "string",
  "historyId": "string",
  "internalDate": "string (int64 format)",
  "payload": {
    "partId": "string",
    "mimeType": "string",
    "filename": "string",
    "headers": [
      {
        "name": "string",
        "value": "string"
      }
    ],
    "body": {
      "attachmentId": "string",
      "size": "integer",
      "data": "string (base64)"
    },
    "parts": [...]
  },
  "sizeEstimate": "integer",
  "raw": "string (base64url encoded)"
}
```

**Key Message Fields:**
- `id`: Immutable ID of the message
- `threadId`: ID of the thread the message belongs to
- `snippet`: A short part of the message text
- `internalDate`: Internal message creation timestamp (epoch ms)
- `payload.headers[]`: Contains headers like `From`, `To`, `Subject`, `Date`
- `sizeEstimate`: Estimated size in bytes

### 2.2 Authorization Scopes

Both `list` and `get` methods require one of the following OAuth scopes:

| Scope | Description |
|-------|-------------|
| `https://mail.google.com/` | Full access to Gmail |
| `https://www.googleapis.com/auth/gmail.modify` | Read, compose, send, and permanently delete emails |
| `https://www.googleapis.com/auth/gmail.readonly` | Read-only access to Gmail (**Recommended for this use case**) |
| `https://www.googleapis.com/auth/gmail.metadata` | Read metadata only (labels, headers) |

### 2.3 Rate Limits and Quotas

**Gmail API Rate Limits:**
| Limit Type | Value |
|------------|-------|
| Project Quota (Daily) | 1,200,000 requests |
| Per-User Request Quota (Daily) | 15,000 requests |
| Per-User-Per-Second Rate Limit | 250 quota units/second |

**Quota Units Per Method:**
| Method | Quota Units |
|--------------|--------------------|
| `messages.list` | 5 units |
| `messages.get` | 5 units |
| `labels.list` | 1 unit |
| `drafts.send` | 100 units |

**Error Responses for Rate Limits:**
- `HTTP 403` or `HTTP 429` - "Too Many Requests"
- Implement **exponential backoff** for retries

### 2.4 Authentication Flow (OAuth 2.0)

**Required Python Libraries:**
```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

**Authentication Steps:**
1. Create a Google Cloud Project
2. Enable Gmail API in Google Cloud Console
3. Configure OAuth Consent Screen
4. Create OAuth 2.0 Client ID (Desktop app type)
5. Download `credentials.json` file
6. Use `google-auth-oauthlib` for authentication flow
7. Store tokens in `token.json` for subsequent requests

---

## 3. FastMCP Framework Research

### 3.1 Overview

FastMCP is a Python framework for building MCP (Model Context Protocol) servers. It provides:
- Simple `@tool` decorator for exposing functions
- STDIO and HTTP transport support
- Built-in error handling and parameter validation
- Authentication providers

**Installation:**
```bash
pip install fastmcp
# or with uv
uv add fastmcp
```

### 3.2 Basic Server Setup

```python
from fastmcp import FastMCP

mcp = FastMCP("Gmail MCP Server")

@mcp.tool
def search_messages(query: str, max_results: int = 10) -> dict:
    """Search Gmail messages with a query string."""
    # Implementation here
    return {"messages": [...]}

@mcp.tool
def get_message(message_id: str) -> dict:
    """Get details of a specific Gmail message."""
    # Implementation here
    return {"id": message_id, "subject": "..."}

if __name__ == "__main__":
    mcp.run()
```

### 3.3 Transport Protocols

#### 3.3.1 STDIO Transport (Default) - Stage 1

For local development and Claude Desktop integration:

```python
if __name__ == "__main__":
    mcp.run()  # Uses STDIO transport by default
```

**Use Cases:**
- Local development and testing
- Claude Desktop integration
- Command-line tools
- Single-user applications

#### 3.3.2 HTTP Transport (Streamable) - Stage 2

For network accessibility and multiple clients:

```python
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

The server will be accessible at: `http://localhost:8000/mcp`

**HTTP Options:**
```python
mcp.run(
    transport="http",
    host="0.0.0.0",
    port=8000,
    path="/api/mcp/"  # Custom path
)
```

### 3.4 Error Handling

FastMCP provides `ToolError` for explicit error control:

```python
from fastmcp.exceptions import ToolError

@mcp.tool
def get_message(message_id: str) -> dict:
    """Get details of a specific Gmail message."""
    if not message_id:
        raise ToolError("Message ID is required")
    try:
        # API call
        pass
    except HttpError as e:
        if e.resp.status == 404:
            raise ToolError(f"Message not found: {message_id}")
        elif e.resp.status == 429:
            raise ToolError("Rate limit exceeded. Please wait and retry.")
        else:
            raise ToolError(f"Gmail API error: {str(e)}")
```

**Mask Error Details (Production):**
```python
mcp = FastMCP(name="Gmail Server", mask_error_details=True)
```

### 3.5 Tool Decorator Details

```python
@mcp.tool(
    annotations={
        "title": "Search Gmail Messages",
        "readOnlyHint": True,      # Tool doesn't modify data
        "openWorldHint": True      # Tool interacts with external systems
    }
)
def search_messages(
    query: str,
    max_results: int = 10
) -> dict:
    """
    Search Gmail messages using Gmail query syntax.
    
    Args:
        query: Gmail search query (e.g., "from:sender@example.com is:unread")
        max_results: Maximum number of results to return (1-100)
    
    Returns:
        Dictionary containing list of messages with id, snippet, and headers
    """
    pass
```

### 3.6 Running the Server

**Using Python directly:**
```bash
python main.py
```

**Using FastMCP CLI:**
```bash
# STDIO transport
fastmcp run main.py:mcp

# HTTP transport
fastmcp run main.py:mcp --transport http --port 8000
```

---

## 4. Claude Desktop Integration

### 4.1 Configuration File Location

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### 4.2 Manual Configuration

```json
{
  "mcpServers": {
    "gmail-server": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp",
        "--with", "google-auth-oauthlib",
        "--with", "google-api-python-client",
        "fastmcp", "run",
        "/path/to/week3/server/main.py"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### 4.3 Using FastMCP CLI

```bash
fastmcp install claude-desktop server/main.py \
  --server-name "Gmail MCP Server" \
  --with google-auth-oauthlib \
  --with google-api-python-client \
  --env-file .env
```

---

## 5. Cursor IDE Integration

### 5.1 Configuration File Location

- **All platforms:** `~/.cursor/mcp.json`

### 5.2 Configuration Example

```json
{
  "mcpServers": {
    "gmail-server": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp",
        "--with", "google-auth-oauthlib",
        "--with", "google-api-python-client",
        "fastmcp", "run",
        "/path/to/week3/server/main.py"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

---

## 6. Authentication for MCP Server (Extra Credit)

### 6.1 Bearer Token Authentication

For HTTP transport with authentication:

```python
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier

auth = JWTVerifier(
    jwks_uri="https://your-auth-system.com/.well-known/jwks.json",
    issuer="https://your-auth-system.com",
    audience="your-mcp-server"
)

mcp = FastMCP(name="Gmail Server", auth=auth)
```

### 6.2 Simple API Key Authentication

For a simpler approach, implement API key validation:

```python
import os
from fastmcp import FastMCP
from fastmcp.server.context import Context

mcp = FastMCP("Gmail Server")

def validate_api_key(api_key: str) -> bool:
    """Validate the provided API key."""
    expected_key = os.getenv("MCP_API_KEY")
    return api_key == expected_key

@mcp.tool
async def search_messages(
    query: str,
    max_results: int = 10,
    ctx: Context = None
) -> dict:
    """Search Gmail messages."""
    # For HTTP transport, validate API key from headers
    # Implementation depends on middleware setup
    pass
```

---

## 7. Implementation Plan

### 7.1 Stage 1: Local STDIO Server

**Objective:** Create a working STDIO MCP server for Claude Desktop/Cursor integration.

**Tasks:**
1. Set up project structure under `week3/server/`
2. Implement Gmail API authentication (OAuth 2.0)
3. Create `search_messages` tool
4. Create `get_message` tool
5. Implement error handling and rate limiting
6. Test with Claude Desktop

**Files to Create:**
```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── gmail_client.py   # Gmail API wrapper
│   └── tools.py          # MCP tool definitions
├── .env.example
└── README.md
```

### 7.2 Stage 2: Remote HTTP Server

**Objective:** Enable HTTP transport for network accessibility.

**Additional Tasks:**
1. Configure HTTP transport with proper host/port
2. Add CORS middleware for browser clients
3. Implement bearer token or API key authentication
4. Deploy to Vercel/Railway (optional for extra credit)

---

## 8. MCP Tool Specifications

### 8.1 Tool: `search_messages`

| Property | Value |
|----------|-------|
| Name | `search_messages` |
| Description | Search Gmail messages using Gmail query syntax |
| Parameters | `query` (str, required), `max_results` (int, optional, default=10) |
| Returns | List of message summaries with id, snippet, subject, from, date |

**Example Input:**
```json
{
  "query": "from:boss@company.com is:unread",
  "max_results": 5
}
```

**Example Output:**
```json
{
  "messages": [
    {
      "id": "18abc123def456",
      "threadId": "18abc123def456",
      "snippet": "Please review the attached document...",
      "subject": "Q4 Report Review",
      "from": "boss@company.com",
      "date": "2024-12-28T10:30:00Z"
    }
  ],
  "resultCount": 1,
  "hasMore": false
}
```

### 8.2 Tool: `get_message`

| Property | Value |
|----------|-------|
| Name | `get_message` |
| Description | Get full details of a specific Gmail message |
| Parameters | `message_id` (str, required), `format` (str, optional, default="full") |
| Returns | Complete message content with headers, body, and metadata |

**Example Input:**
```json
{
  "message_id": "18abc123def456",
  "format": "full"
}
```

**Example Output:**
```json
{
  "id": "18abc123def456",
  "threadId": "18abc123def456",
  "subject": "Q4 Report Review",
  "from": "boss@company.com",
  "to": "employee@company.com",
  "date": "2024-12-28T10:30:00Z",
  "body": "Please review the attached document and provide your feedback by EOD...",
  "labels": ["INBOX", "UNREAD"],
  "snippet": "Please review the attached document..."
}
```

---

## 9. Resilience Implementation

### 9.1 Error Handling Strategy

```python
from functools import wraps
import time
from googleapiclient.errors import HttpError
from fastmcp.exceptions import ToolError

def with_retry(max_retries=3, base_delay=1):
    """Decorator for exponential backoff retry."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except HttpError as e:
                    last_error = e
                    if e.resp.status == 429:  # Rate limited
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                    elif e.resp.status >= 500:  # Server error
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                    else:
                        raise
            raise ToolError(f"Failed after {max_retries} retries: {last_error}")
        return wrapper
    return decorator
```

### 9.2 Graceful Error Messages

| Error Condition | User-Facing Message |
|-----------------|---------------------|
| HTTP 401 | "Authentication required. Please re-authenticate with Gmail." |
| HTTP 403 | "Access denied. Check Gmail API permissions." |
| HTTP 404 | "Message not found. It may have been deleted." |
| HTTP 429 | "Rate limit exceeded. Please wait a moment and try again." |
| HTTP 5xx | "Gmail service temporarily unavailable. Retrying..." |
| Timeout | "Request timed out. Gmail may be slow. Please retry." |
| Empty Results | "No messages found matching your query." |

---

## 10. References

### Documentation Links

- **Gmail API Reference:**
  - [users.messages](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages)
  - [users.messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
  - [users.messages.get](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/get)

- **FastMCP Documentation:**
  - [Quickstart](https://gofastmcp.com/getting-started/quickstart)
  - [Tools](https://gofastmcp.com/servers/tools)
  - [Running Server](https://gofastmcp.com/deployment/running-server)
  - [HTTP Deployment](https://gofastmcp.com/deployment/http)
  - [Claude Desktop Integration](https://gofastmcp.com/integrations/claude-desktop)
  - [Cursor Integration](https://gofastmcp.com/integrations/cursor)
  - [Authentication](https://gofastmcp.com/servers/auth/authentication)

- **MCP Protocol:**
  - [MCP Server Quickstart](https://modelcontextprotocol.io/quickstart/server)
  - [MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

---

## 11. Dependencies

### Required Python Packages

```toml
[project]
dependencies = [
    "fastmcp>=2.0.0",
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-auth-httplib2>=0.2.0",
    "google-api-python-client>=2.0.0",
    "python-dotenv>=1.0.0"
]
```

### Development Requirements

```bash
# Using uv for package management
uv init week3
cd week3
uv add fastmcp google-auth-oauthlib google-api-python-client python-dotenv
```

---

## 12. Next Steps

1. **Create project structure** under `week3/server/`
2. **Set up Google Cloud Project** and obtain OAuth credentials
3. **Implement Gmail client wrapper** with authentication
4. **Create MCP tools** with proper error handling
5. **Test with Claude Desktop** (Stage 1)
6. **Enable HTTP transport** (Stage 2)
7. **Add authentication** (Extra Credit)
8. **Update README.md** with complete documentation
