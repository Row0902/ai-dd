"""Tests for infrastructure.repository_registry: scheme → class mapping."""

import pytest

from domain.repositories import BookRepository
from infrastructure.repository_registry import register, resolve


class FakeRepo(BookRepository):
    """Minimal concrete repo for testing registry."""

    def list(self, limit=20, offset=0):
        return []

    def get(self, book_id):
        return None

    def get_by_name(self, name):
        return []

    def create(self, book):
        return book

    def update(self, book_id, book):
        return None

    def delete(self, book_id):
        return False


class TestRegistryResolve:
    """Verify resolve() returns the correct class for a scheme."""

    def test_resolve_registered_scheme(self):
        """resolve() returns the class registered for a known scheme."""
        register("fake", FakeRepo)
        cls = resolve("fake")
        assert cls is FakeRepo

    def test_resolve_unknown_scheme_raises_value_error(self):
        """resolve() raises ValueError for an unknown scheme."""
        with pytest.raises(ValueError, match="Unsupported database scheme"):
            resolve("mysql")

    def test_resolve_memory_scheme(self):
        """resolve('memory') returns a class after registration."""
        register("memory", FakeRepo)
        cls = resolve("memory")
        assert cls is FakeRepo


class TestRegistryRegister:
    """Verify register() stores scheme → class mappings."""

    def test_register_overwrites_previous(self):
        """register() with an existing scheme overwrites the previous class."""

        class AnotherRepo(BookRepository):
            def list(self, limit=20, offset=0):
                return []

            def get(self, book_id):
                return None

            def get_by_name(self, name):
                return []

            def create(self, book):
                return book

            def update(self, book_id, book):
                return None

            def delete(self, book_id):
                return False

        register("overwrite-test", FakeRepo)
        register("overwrite-test", AnotherRepo)
        assert resolve("overwrite-test") is AnotherRepo
