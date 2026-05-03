"""Unit tests for Pydantic schemas — HTTP boundary validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from api.schemas import BookPayload


class TestBookPayload:
    """Tests for BookPayload field validators."""

    def test_valid_payload_accepted(self) -> None:
        """A fully valid payload is accepted without errors."""
        payload = BookPayload(
            name="Clean Code",
            author="Robert C. Martin",
            url="https://example.com/book",
        )
        assert payload.name == "Clean Code"
        assert payload.author == "Robert C. Martin"
        assert payload.url == "https://example.com/book"

    def test_valid_payload_with_defaults(self) -> None:
        """A payload with only name is accepted (author/url default to empty)."""
        payload = BookPayload(name="Clean Code")
        assert payload.name == "Clean Code"
        assert payload.author == ""
        assert payload.url == ""

    def test_empty_name_rejected(self) -> None:
        """An empty name string is rejected."""
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="", author="Bob", url="https://example.com")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_whitespace_only_name_rejected(self) -> None:
        """A whitespace-only name is rejected."""
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="   ", author="Bob", url="https://example.com")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_malformed_url_rejected(self) -> None:
        """A malformed URL is rejected."""
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="Book", url="not-a-valid-url")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("url",) for e in errors)

    def test_empty_url_accepted(self) -> None:
        """An empty URL is accepted (url is optional)."""
        payload = BookPayload(name="Book", url="")
        assert payload.url == ""

    def test_valid_url_accepted(self) -> None:
        """A properly formatted URL is accepted."""
        payload = BookPayload(name="Book", url="https://example.com/path?q=1")
        assert payload.url == "https://example.com/path?q=1"
