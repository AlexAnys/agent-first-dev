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
# for dev
uv sync --extra dev
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
        "--directory", "/Users/xuyin/Documents/Repository/modern-software-dev-assignments/week3",
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

## Expected Behaviors

| Scenario | Behavior |
|----------|----------|
| Empty query | Returns `ToolError("Query cannot be empty")` |
| max_results > 100 | Caps to 100 with warning log |
| Message not found | Returns `ToolError("Message not found...")` |
| Rate limited (429) | Retries 3x with exponential backoff |
| Server error (5xx) | Retries 3x with exponential backoff |
| No results | Returns `{"messages": [], "resultCount": 0}` |
| Auth expired | Attempts token refresh, fails gracefully |
