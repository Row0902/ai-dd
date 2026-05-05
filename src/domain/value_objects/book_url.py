"""BookUrl value object: frozen, validates URL format, max URL length."""

from dataclasses import dataclass
from urllib.parse import urlparse

from domain.exceptions import ValidationError
from domain.validation_rules import MAX_URL_LENGTH


@dataclass(frozen=True, slots=True)
class BookUrl:
    """Immutable URL value object.

    Validates on construction: non-empty, valid URL format (via urllib.parse),
    max URL length from ``validation_rules.MAX_URL_LENGTH``.

    Attributes:
        value: The validated URL string.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the URL on construction."""
        if not self.value.strip():
            raise ValidationError(field="url", message="Invalid URL format")
        if len(self.value) > MAX_URL_LENGTH:
            raise ValidationError(
                field="url",
                message=f"URL exceeds {MAX_URL_LENGTH} characters",
            )
        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(field="url", message="Invalid URL format")
