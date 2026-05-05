"""Domain value objects: immutable, self-validating domain primitives."""

from domain.value_objects.book_author import BookAuthor
from domain.value_objects.book_name import BookName
from domain.value_objects.book_url import BookUrl

__all__ = ["BookAuthor", "BookName", "BookUrl"]
