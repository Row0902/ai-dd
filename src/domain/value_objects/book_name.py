"""BookName value object: frozen, validates non-empty, max 200 chars."""

from dataclasses import dataclass

from domain.exceptions import ValidationError


@dataclass(frozen=True)
class BookName:
    """Immutable book title value object.

    Validates on construction: non-empty after stripping, max 200 characters.

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
        if len(trimmed) > 200:
            raise ValidationError(field="name", message="Name exceeds 200 characters")
        object.__setattr__(self, "value", trimmed)
