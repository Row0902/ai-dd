"""Pydantic schemas for HTTP payloads.

All field constraints import from :mod:`domain.validation_rules` — the
single source of truth. No inline magic numbers.
"""

from __future__ import annotations

from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

from domain.validation_rules import (
    MAX_AUTHOR_LENGTH,
    MAX_TITLE_LENGTH,
    MAX_URL_LENGTH,
)


class BookPayload(BaseModel):
    """Request payload for creating or replacing a book."""

    name: str
    author: str = ""
    description: str = ""
    url: str = ""
    content: str = ""

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Reject empty/whitespace-only or over-long names."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        v = v.strip()
        if len(v) > MAX_TITLE_LENGTH:
            raise ValueError(
                f"Name exceeds maximum length of {MAX_TITLE_LENGTH} characters"
            )
        return v

    @field_validator("author")
    @classmethod
    def author_length(cls, v: str) -> str:
        """Reject author names that exceed maximum length."""
        if v and len(v) > MAX_AUTHOR_LENGTH:
            raise ValueError(
                f"Author exceeds maximum length of {MAX_AUTHOR_LENGTH} characters"
            )
        return v

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        """Reject malformed or over-long URLs. Empty string is allowed."""
        if not v:
            return v
        if len(v) > MAX_URL_LENGTH:
            raise ValueError(
                f"URL exceeds maximum length of {MAX_URL_LENGTH} characters"
            )
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        return v
