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
