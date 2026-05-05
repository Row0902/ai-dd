"""T13: Tests for global rate limiting on books, collections, favorites endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from api.dependencies import _reset_repos, get_rate_limiter
from config.settings import AppSettings
from domain.rate_limiting.ports import RateLimiter
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _make_client(
    mock_limiter: RateLimiter | None = None,
) -> TestClient:
    """Create a test client with rate limiting override.

    Args:
        mock_limiter: Optional mock limiter. If None, uses NoOpRateLimiter.

    Returns:
        Configured TestClient instance.
    """
    _reset_repos()
    settings = AppSettings(
        DATABASE_URL="memory://",
        SECRET_KEY=TEST_SECRET,
        RATE_LIMIT_ENABLED=True,
    )
    app = create_app(settings)
    limiter = mock_limiter if mock_limiter is not None else NoOpRateLimiter()
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    return TestClient(app)


def _auth_headers(user_id: str = "test-user-id", role: str = "user") -> dict[str, str]:
    """Create Authorization headers."""
    from infrastructure.auth.jwt_token_service import JwtTokenService

    token_service = JwtTokenService(TEST_SECRET)
    token = token_service.generate(user_id, role)
    return {"Authorization": f"Bearer {token}"}


class TestBooksGlobalRateLimit:
    """Test global rate limiting on books endpoints."""

    def test_list_books_has_rate_limit_dependency(self) -> None:
        """GET /books must have global rate limit dependency wired."""
        client = _make_client()
        resp = client.get("/books", headers=_auth_headers())
        # Should work with NoOpRateLimiter (not 500)
        assert resp.status_code == 200

    def test_list_books_returns_429_when_rate_limited(self) -> None:
        """GET /books returns 429 when rate limiter blocks."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.get("/books", headers=_auth_headers())
        assert resp.status_code == 429
        assert resp.json() == {"detail": "Too many requests"}

    def test_create_book_returns_429_when_rate_limited(self) -> None:
        """POST /books returns 429 when rate limiter blocks."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.post(
            "/books",
            json={"name": "Test", "author": "A"},
            headers=_auth_headers(role="admin"),
        )
        assert resp.status_code == 429


class TestCollectionsGlobalRateLimit:
    """Test global rate limiting on collections endpoints."""

    def test_list_collections_has_rate_limit_dependency(self) -> None:
        """GET /collections must have global rate limit dependency wired."""
        client = _make_client()
        resp = client.get("/collections", headers=_auth_headers())
        assert resp.status_code == 200

    def test_list_collections_returns_429_when_rate_limited(self) -> None:
        """GET /collections returns 429 when rate limiter blocks."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.get("/collections", headers=_auth_headers())
        assert resp.status_code == 429

    def test_create_collection_returns_429_when_rate_limited(self) -> None:
        """POST /collections returns 429 when rate limiter blocks."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.post(
            "/collections",
            json={"name": "Test"},
            headers=_auth_headers(),
        )
        assert resp.status_code == 429


class TestFavoritesGlobalRateLimit:
    """Test global rate limiting on favorites endpoints."""

    def test_list_favorites_has_rate_limit_dependency(self) -> None:
        """GET /favorites must have global rate limit dependency wired."""
        client = _make_client()
        resp = client.get("/favorites", headers=_auth_headers())
        assert resp.status_code == 200

    def test_list_favorites_returns_429_when_rate_limited(self) -> None:
        """GET /favorites returns 429 when rate limiter blocks."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.get("/favorites", headers=_auth_headers())
        assert resp.status_code == 429


class TestHealthExemptFromRateLimit:
    """Test that /health is exempt from rate limiting."""

    def test_health_not_rate_limited(self) -> None:
        """GET /health works even when rate limiter would block."""
        mock = AsyncMock(spec=RateLimiter)
        mock.check.return_value = False
        client = _make_client(mock)
        resp = client.get("/health")
        # Health should succeed even with blocking limiter
        assert resp.status_code == 200
