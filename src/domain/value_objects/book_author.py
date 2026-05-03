"""BookAuthor value object: frozen, validates non-empty, max 150 chars."""

from dataclasses import dataclass

from domain.exceptions import ValidationError


@dataclass(frozen=True)
class BookAuthor:
    """Immutable author name value object.

    Validates on construction: non-empty after stripping, max 150 characters.

    Attributes:
        value: The validated, trimmed author name.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the author on construction."""
        trimmed = self.value.strip()
        if not trimmed:
            raise ValidationError(
                field="author", message="Author cannot be empty or whitespace"
            )
        if len(trimmed) > 150:
            raise ValidationError(
                field="author", message="Author exceeds 150 characters"
            )
        object.__setattr__(self, "value", trimmed)
