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
