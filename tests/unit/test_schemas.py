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

    def test_name_exceeding_max_length_rejected(self) -> None:
        """A name longer than MAX_TITLE_LENGTH is rejected."""
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="X" * 201, author="Bob")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_name_at_max_length_accepted(self) -> None:
        """A name exactly at MAX_TITLE_LENGTH is accepted."""
        payload = BookPayload(name="X" * 200, author="Bob")
        assert len(payload.name) == 200

    def test_author_exceeding_max_length_rejected(self) -> None:
        """An author name longer than MAX_AUTHOR_LENGTH is rejected."""
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="Book", author="X" * 151)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("author",) for e in errors)

    def test_author_at_max_length_accepted(self) -> None:
        """An author name exactly at MAX_AUTHOR_LENGTH is accepted."""
        payload = BookPayload(name="Book", author="X" * 150)
        assert len(payload.author) == 150

    def test_url_exceeding_max_length_rejected(self) -> None:
        """A URL longer than MAX_URL_LENGTH is rejected."""
        long_url = "https://example.com/" + "a" * 2048
        with pytest.raises(PydanticValidationError) as exc_info:
            BookPayload(name="Book", url=long_url)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("url",) for e in errors)

    def test_url_at_max_length_accepted(self) -> None:
        """A URL exactly at MAX_URL_LENGTH is accepted."""
        valid_url = "https://example.com/" + "a" * (2048 - len("https://example.com/"))
        payload = BookPayload(name="Book", url=valid_url)
        assert len(payload.url) == 2048
