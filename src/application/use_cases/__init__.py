"""Use case entrypoints.

All use case functions are re-exported here for convenience.
Individual functions can also be imported from their dedicated modules.
"""

from __future__ import annotations

from application.use_cases.create_book import _validate_or_raise, create_book
from application.use_cases.delete_book import delete_book
from application.use_cases.list_books import list_books
from application.use_cases.read_book import get_book
from application.use_cases.replace_book import replace_book
from application.use_cases.search_books import get_books_by_name
from application.use_cases.update_book import update_book

__all__ = [
    "create_book",
    "_validate_or_raise",
    "delete_book",
    "get_book",
    "get_books_by_name",
    "list_books",
    "replace_book",
    "update_book",
]
