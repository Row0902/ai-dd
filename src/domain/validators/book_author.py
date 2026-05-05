"""BookAuthorValidator: validates book author is within length limits."""

from typing import override

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validation_rules import MAX_AUTHOR_LENGTH
from domain.validators.protocol import Validator


class BookAuthorValidator(Validator[Book]):
    """Validates the author field of a Book entity."""

    @override
    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the author, if provided, is within length limits.

        An empty author is valid — the field is optional.
        """
        errors: list[ValidationError] = []
        if entity.author and len(entity.author) > MAX_AUTHOR_LENGTH:
            errors.append(
                ValidationError(
                    field="author",
                    message=f"Author exceeds {MAX_AUTHOR_LENGTH} characters",
                )
            )
        return errors
