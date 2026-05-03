"""BookNameValidator: validates book name is non-empty and <=200 chars."""

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validators.protocol import Validator


class BookNameValidator(Validator[Book]):
    """Validates the name field of a Book entity."""

    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the book name is non-empty and within length limits."""
        errors: list[ValidationError] = []
        if not entity.name.strip():
            errors.append(
                ValidationError(
                    field="name", message="Name cannot be empty or whitespace"
                )
            )
        elif len(entity.name) > 200:
            errors.append(
                ValidationError(field="name", message="Name exceeds 200 characters")
            )
        return errors
