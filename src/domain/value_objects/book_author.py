"""BookAuthor value object: frozen, validates non-empty, max author length."""

from dataclasses import dataclass

from domain.exceptions import ValidationError
from domain.validation_rules import MAX_AUTHOR_LENGTH


@dataclass(frozen=True)
class BookAuthor:
    """Immutable author name value object.

    Validates on construction: non-empty after stripping, max author length
    from ``validation_rules.MAX_AUTHOR_LENGTH``.

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
        if len(trimmed) > MAX_AUTHOR_LENGTH:
            raise ValidationError(
                field="author",
                message=f"Author exceeds {MAX_AUTHOR_LENGTH} characters",
            )
        object.__setattr__(self, "value", trimmed)
