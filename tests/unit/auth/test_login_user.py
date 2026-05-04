"""Tests for application.use_cases.auth.login_user.

Unit tests with mocked dependencies.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.auth.entities import User, UserRole
from domain.auth.exceptions import AuthenticationError


@pytest.fixture()
def mock_repo():
    """Provide a mock UserRepository."""
    repo = AsyncMock()
    return repo


@pytest.fixture()
def mock_hasher():
    """Provide a mock PasswordHasher."""
    hasher = MagicMock()
    return hasher


@pytest.fixture()
def mock_token_service():
    """Provide a mock TokenService."""
    svc = MagicMock()
    svc.generate.return_value = "jwt-token-123"
    return svc


class TestLoginUser:
    """Tests for login_user use case."""

    async def test_login_user_returns_token(
        self, mock_repo, mock_hasher, mock_token_service
    ):
        """login_user() should return access_token on valid credentials."""
        from application.use_cases.auth.login_user import login_user

        mock_repo.find_by_email.return_value = User(
            id="u1",
            email="alice@example.com",
            hashed_password="$2b$12$hashed",
            role=UserRole.USER,
        )
        mock_hasher.verify.return_value = True

        result = await login_user(
            repo=mock_repo,
            hasher=mock_hasher,
            token_service=mock_token_service,
            email="alice@example.com",
            password="secret123",
        )
        assert result["access_token"] == "jwt-token-123"
        assert result["token_type"] == "bearer"
        mock_token_service.generate.assert_called_once_with("u1", "user")

    async def test_login_user_raises_on_wrong_password(
        self, mock_repo, mock_hasher, mock_token_service
    ):
        """login_user() should raise AuthenticationError on wrong password."""
        from application.use_cases.auth.login_user import login_user

        mock_repo.find_by_email.return_value = User(
            id="u1",
            email="alice@example.com",
            hashed_password="$2b$12$hashed",
        )
        mock_hasher.verify.return_value = False

        with pytest.raises(AuthenticationError):
            await login_user(
                repo=mock_repo,
                hasher=mock_hasher,
                token_service=mock_token_service,
                email="alice@example.com",
                password="wrong",
            )

    async def test_login_user_raises_on_unknown_email(
        self, mock_repo, mock_hasher, mock_token_service
    ):
        """login_user() should raise AuthenticationError on unknown email."""
        from application.use_cases.auth.login_user import login_user

        mock_repo.find_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            await login_user(
                repo=mock_repo,
                hasher=mock_hasher,
                token_service=mock_token_service,
                email="nobody@example.com",
                password="secret123",
            )
