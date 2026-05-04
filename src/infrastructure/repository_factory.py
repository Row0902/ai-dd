"""Repository factory: resolves a BookRepository from settings.

Parses the ``DATABASE_URL`` scheme and looks up the corresponding
repository class in the registry. Falls back to ``memory://`` when
the URL is empty or unset.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from domain.repositories import BookRepository
from infrastructure.repository_registry import resolve

if TYPE_CHECKING:
    from config.settings import AppSettings


def create_repository(settings: AppSettings) -> BookRepository:
    """Create a BookRepository instance from application settings.

    Args:
        settings: Application settings containing ``DATABASE_URL``.

    Returns:
        An instance of the repository class registered for the URL scheme.

    Raises:
        ValueError: If the URL scheme is not registered.
    """
    scheme = urlparse(settings.DATABASE_URL).scheme or "memory"
    cls = resolve(scheme)
    return cls()
