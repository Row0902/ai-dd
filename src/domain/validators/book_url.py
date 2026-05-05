"""BookUrlValidator: validates URL format using urllib.parse."""

from urllib.parse import urlparse

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validators.protocol import Validator


class BookUrlValidator(Validator[Book]):
    """Validates the url field of a Book entity."""

    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that the book URL is well-formed and within length limits."""
        errors: list[ValidationError] = []
        if not entity.url:
            return errors
        if len(entity.url) > 2048:
            errors.append(
                ValidationError(field="url", message="URL exceeds 2048 characters")
            )
            return errors
        parsed = urlparse(entity.url)
        if not parsed.scheme or not parsed.netloc:
            errors.append(ValidationError(field="url", message="Invalid URL format"))
        return errors
