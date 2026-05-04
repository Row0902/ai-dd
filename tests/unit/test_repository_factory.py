"""Tests for infrastructure.repository_factory: settings → repository instance."""

import pytest

from config.settings import AppSettings
from domain.repositories import BookRepository
from infrastructure.repository_factory import create_repository
from infrastructure.repository_registry import register


class FakeRepo(BookRepository):
    """Minimal concrete repo for testing factory."""

    def __init__(self):
        """Initialize fake repository."""
        pass

    async def list(self, limit=20, offset=0):
        """Return empty list."""
        return []

    async def get(self, book_id):
        """Return None for any id."""
        return None

    async def get_by_name(self, name):
        """Return empty list for any name."""
        return []

    async def create(self, book):
        """Return book as-is."""
        return book

    async def update(self, book_id, book):
        """Return None for any id."""
        return None

    async def delete(self, book_id):
        """Return False for any id."""
        return False


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure registry state doesn't leak between tests."""
    from infrastructure.repository_registry import _REGISTRY

    _REGISTRY.clear()
    yield
    _REGISTRY.clear()


def _make_settings(database_url: str = "memory://") -> AppSettings:
    """Helper to create AppSettings with a specific DATABASE_URL."""
    return AppSettings(DATABASE_URL=database_url)


class TestCreateRepository:
    """Verify factory resolves correct repository from settings."""

    def test_resolves_memory_scheme(self):
        """Factory returns registered class for memory:// scheme."""
        register("memory", FakeRepo)
        repo = create_repository(_make_settings("memory://"))
        assert isinstance(repo, FakeRepo)

    def test_resolves_sqlite_scheme(self):
        """Factory returns registered class for sqlite:// scheme."""
        register("sqlite", FakeRepo)
        repo = create_repository(_make_settings("sqlite:///./test.db"))
        assert isinstance(repo, FakeRepo)

    def test_fallback_to_memory_when_url_empty(self):
        """Factory falls back to memory:// when DATABASE_URL is empty."""
        register("memory", FakeRepo)
        repo = create_repository(_make_settings(""))
        assert isinstance(repo, FakeRepo)

    def test_unknown_scheme_raises_value_error(self):
        """Factory raises ValueError for unregistered scheme."""
        with pytest.raises(ValueError, match="Unsupported database scheme"):
            create_repository(_make_settings("mysql://localhost/db"))
