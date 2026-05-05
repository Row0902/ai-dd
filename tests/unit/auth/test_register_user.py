"""Tests for application.use_cases.auth.register_user.

Unit tests with mocked dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.auth.entities import User, UserRole
from domain.auth.exceptions import UserAlreadyExists


@pytest.fixture()
def mock_repo():
    """Provide a mock UserRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture()
def mock_hasher():
    """Provide a mock PasswordHasher."""
    hasher = MagicMock()
    hasher.hash.return_value = "$2b$12$hashed_password"
    return hasher


class TestRegisterUser:
    """Tests for register_user use case."""

    async def test_register_user_creates_user(self, mock_repo, mock_hasher):
        """register_user() should create and return a new user."""
        from application.use_cases.auth.register_user import register_user

        mock_repo.find_by_email.return_value = None
        mock_repo.save.return_value = User(
            id="generated",
            email="alice@example.com",
            hashed_password="$2b$12$hashed_password",
            role=UserRole.USER,
        )

        result = await register_user(
            repo=mock_repo,
            hasher=mock_hasher,
            email="alice@example.com",
            password="secret123",
        )
        assert result.email == "alice@example.com"
        assert result.role == UserRole.USER
        mock_repo.save.assert_called_once()

    async def test_register_user_hashes_password(self, mock_repo, mock_hasher):
        """register_user() should hash the password before saving."""
        from application.use_cases.auth.register_user import register_user

        mock_repo.find_by_email.return_value = None
        mock_repo.save.return_value = User(
            id="generated",
            email="alice@example.com",
            hashed_password="$2b$12$hashed_password",
        )

        await register_user(
            repo=mock_repo,
            hasher=mock_hasher,
            email="alice@example.com",
            password="secret123",
        )
        mock_hasher.hash.assert_called_once_with("secret123")
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user.hashed_password == "$2b$12$hashed_password"

    async def test_register_user_raises_on_duplicate_email(
        self, mock_repo, mock_hasher
    ):
        """register_user() should raise UserAlreadyExists for duplicate email."""
        from application.use_cases.auth.register_user import register_user

        mock_repo.find_by_email.return_value = User(
            id="existing",
            email="alice@example.com",
            hashed_password="$2b$12$existing",
        )

        with pytest.raises(UserAlreadyExists):
            await register_user(
                repo=mock_repo,
                hasher=mock_hasher,
                email="alice@example.com",
                password="secret123",
            )
        mock_repo.save.assert_not_called()

    async def test_register_user_with_admin_role(self, mock_repo, mock_hasher):
        """register_user() should support creating admin users."""
        from application.use_cases.auth.register_user import register_user

        mock_repo.find_by_email.return_value = None
        mock_repo.save.return_value = User(
            id="generated",
            email="admin@example.com",
            hashed_password="$2b$12$hashed_password",
            role=UserRole.ADMIN,
        )

        await register_user(
            repo=mock_repo,
            hasher=mock_hasher,
            email="admin@example.com",
            password="secret123",
            role=UserRole.ADMIN,
        )
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user.role == UserRole.ADMIN
