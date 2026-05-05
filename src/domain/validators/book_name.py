"""BookNameValidator: validates book name is non-empty and within length limits."""

from typing import override

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validation_rules import MAX_TITLE_LENGTH
from domain.validators.protocol import Validator


class BookNameValidator(Validator[Book]):
    """Validates the name field of a Book entity."""

    @override
    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the book name is non-empty and within length limits."""
        errors: list[ValidationError] = []
        if not entity.name.strip():
            errors.append(
                ValidationError(
                    field="name", message="Name cannot be empty or whitespace"
                )
            )
        elif len(entity.name) > MAX_TITLE_LENGTH:
            errors.append(
                ValidationError(
                    field="name",
                    message=f"Name exceeds {MAX_TITLE_LENGTH} characters",
                )
            )
        return errors
