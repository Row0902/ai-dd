"""Pydantic schemas for HTTP payloads."""

from __future__ import annotations

from urllib.parse import urlparse

from pydantic import BaseModel, field_validator


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
        """Reject empty or whitespace-only names."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        """Reject malformed URLs. Empty string is allowed."""
        if not v:
            return v
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        return v
