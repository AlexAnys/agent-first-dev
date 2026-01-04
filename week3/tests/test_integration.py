"""Integration tests for Gmail MCP Server."""
import pytest
from unittest.mock import Mock, patch
from server.gmail_client import search_messages_async, get_message_async


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

        result = await search_messages_async(mock_gmail_service, "from:test@example.com")

        assert result["resultCount"] == 1
        assert result["messages"][0]["subject"] == "Test"

    @pytest.mark.asyncio
    async def test_empty_search_results(self, mock_gmail_service):
        mock_gmail_service.users().messages().list().execute.return_value = {}

        result = await search_messages_async(mock_gmail_service, "from:nobody@example.com")

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

        result = await get_message_async(mock_gmail_service, "123")

        assert result["id"] == "123"
        assert result["subject"] == "Test Subject"
        assert result["body"] == "Hello World"
