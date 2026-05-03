"""BookAuthorValidator: validates book author is non-empty and <=150 chars."""

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validators.protocol import Validator


class BookAuthorValidator(Validator[Book]):
    """Validates the author field of a Book entity."""

    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the author, if provided, is within length limits.

        An empty author is valid — the field is optional.
        """
        errors: list[ValidationError] = []
        if entity.author and len(entity.author) > 150:
            errors.append(
                ValidationError(field="author", message="Author exceeds 150 characters")
            )
        return errors
