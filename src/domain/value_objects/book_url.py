"""BookUrl value object: frozen, validates URL format, max 2048 chars."""

from dataclasses import dataclass
from urllib.parse import urlparse

from domain.exceptions import ValidationError


@dataclass(frozen=True)
class BookUrl:
    """Immutable URL value object.

    Validates on construction: non-empty, valid URL format (via urllib.parse),
    max 2048 characters.

    Attributes:
        value: The validated URL string.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the URL on construction."""
        if not self.value.strip():
            raise ValidationError(field="url", message="Invalid URL format")
        if len(self.value) > 2048:
            raise ValidationError(field="url", message="URL exceeds 2048 characters")
        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(field="url", message="Invalid URL format")
