"""Integration tests for the auth API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from config.settings import AppSettings
from infrastructure.auth.jwt_token_service import JwtTokenService
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _client(test_settings: AppSettings | None = None) -> TestClient:
    """Create a TestClient with test settings.

    Args:
        test_settings: Optional settings override.

    Returns:
        Configured TestClient instance.
    """
    if test_settings is None:
        test_settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
        )
    return TestClient(create_app(test_settings))


def _admin_headers(test_settings: AppSettings) -> dict[str, str]:
    """Create Authorization headers for an admin user.

    Args:
        test_settings: Test application settings.

    Returns:
        Dict with Authorization Bearer header for admin role.
    """
    token_service = JwtTokenService(test_settings.SECRET_KEY)
    token = token_service.generate("admin-id", "admin")
    return {"Authorization": f"Bearer {token}"}


class TestAuthRegister:
    """Tests for POST /auth/register."""

    def test_register_returns_201_with_user(self) -> None:
        """POST /auth/register creates a user and returns 201."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        resp = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "secure-password"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "test@example.com"
        assert body["role"] == "user"
        assert body["is_active"] is True
        assert "hashed_password" not in body
        assert "id" in body

    def test_register_duplicate_email_returns_409(self) -> None:
        """POST /auth/register with existing email returns 409."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "password123"},
        )
        resp = client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "password456"},
        )
        assert resp.status_code == 409

    def test_register_with_invitation_token(self) -> None:
        """POST /auth/register with a valid invitation token succeeds."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        admin_headers = _admin_headers(settings)

        # Create invitation
        invite_resp = client.post(
            "/auth/invitations",
            json={"email": "invited@example.com", "role": "user"},
            headers=admin_headers,
        )
        assert invite_resp.status_code == 201
        token = invite_resp.json()["token"]

        # Register with invitation
        resp = client.post(
            "/auth/register",
            json={
                "email": "invited@example.com",
                "password": "password123",
                "invitation_token": token,
            },
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "invited@example.com"


class TestAuthLogin:
    """Tests for POST /auth/login."""

    def test_login_returns_access_token(self) -> None:
        """POST /auth/login returns a JWT access token."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        client.post(
            "/auth/register",
            json={"email": "login@example.com", "password": "mypassword"},
        )
        resp = client.post(
            "/auth/login",
            json={"email": "login@example.com", "password": "mypassword"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self) -> None:
        """POST /auth/login with wrong password returns 401."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        client.post(
            "/auth/register",
            json={"email": "wrong@example.com", "password": "correct"},
        )
        resp = client.post(
            "/auth/login",
            json={"email": "wrong@example.com", "password": "incorrect"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user_returns_401(self) -> None:
        """POST /auth/login with nonexistent email returns 401."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        resp = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "password"},
        )
        assert resp.status_code == 401


class TestAuthInvitations:
    """Tests for POST /auth/invitations."""

    def test_create_invitation_requires_admin(self) -> None:
        """POST /auth/invitations requires admin permission."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        admin_headers = _admin_headers(settings)
        resp = client.post(
            "/auth/invitations",
            json={"email": "new@example.com", "role": "user"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "new@example.com"
        assert "token" in body

    def test_create_invitation_without_auth_returns_401(self) -> None:
        """POST /auth/invitations without auth returns 401."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        resp = client.post(
            "/auth/invitations",
            json={"email": "new@example.com", "role": "user"},
        )
        assert resp.status_code == 401

    def test_create_invitation_with_user_role_succeeds(self) -> None:
        """POST /auth/invitations with user role succeeds (user has BOOK_CREATE)."""
        settings = AppSettings(DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET)
        client = _client(settings)
        token_service = JwtTokenService(TEST_SECRET)
        token = token_service.generate("user-id", "user")
        user_headers = {"Authorization": f"Bearer {token}"}
        resp = client.post(
            "/auth/invitations",
            json={"email": "new@example.com", "role": "user"},
            headers=user_headers,
        )
        assert resp.status_code == 201
