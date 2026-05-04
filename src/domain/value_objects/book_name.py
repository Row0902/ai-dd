"""BookName value object: frozen, validates non-empty, max title length."""

from dataclasses import dataclass

from domain.exceptions import ValidationError
from domain.validation_rules import MAX_TITLE_LENGTH


@dataclass(frozen=True)
class BookName:
    """Immutable book title value object.

    Validates on construction: non-empty after stripping, max title length
    from ``validation_rules.MAX_TITLE_LENGTH``.

    Attributes:
        value: The validated, trimmed book title.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the name on construction."""
        # Reassign via object.__setattr__ because frozen=True
        trimmed = self.value.strip()
        if not trimmed:
            raise ValidationError(
                field="name", message="Name cannot be empty or whitespace"
            )
        if len(trimmed) > MAX_TITLE_LENGTH:
            raise ValidationError(
                field="name",
                message=f"Name exceeds {MAX_TITLE_LENGTH} characters",
            )
        object.__setattr__(self, "value", trimmed)
