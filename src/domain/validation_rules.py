"""Validation rules: single source of truth for all book field constraints.

All validators, value objects, and Pydantic schemas MUST import from here
instead of using inline literals. Rule changes require a version bump.
"""

MAX_TITLE_LENGTH: int = 200
"""Maximum allowed length for a book title."""

MAX_AUTHOR_LENGTH: int = 150
"""Maximum allowed length for an author name."""

MIN_PUBLICATION_YEAR: int = 1000
"""Earliest valid publication year."""

MAX_URL_LENGTH: int = 2048
"""Maximum allowed length for a reference URL."""

ISBN_PATTERN: str = r"^(?:\d{9}[\dXx]|\d{13})$"
"""Regex pattern for ISBN-10 or ISBN-13 (digits only, optional X check digit)."""

RULES_VERSION: str = "1.0"
"""Semantic version of the validation rules. Bump on any constraint change."""
