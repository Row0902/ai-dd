"""T11/T12: Tests for rate limiting on auth endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from api.dependencies import _reset_repos, get_rate_limiter
from config.settings import AppSettings
from domain.rate_limiting.exceptions import RateLimitExceededError
from domain.rate_limiting.ports import RateLimiter
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from main import create_app


TEST_SECRET = "test-secret-key-at-least-32-chars-long"


class TestLoginRateLimit:
    """Test rate limiting on POST /auth/login."""

    def _make_client(self) -> TestClient:
        """Create a test client with NoOpRateLimiter override."""
        _reset_repos()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        app = create_app(settings)
        app.dependency_overrides[get_rate_limiter] = lambda: NoOpRateLimiter()
        return TestClient(app)

    def test_login_endpoint_accepts_rate_limit_dependency(self) -> None:
        """Login endpoint must have require_rate_limit wired as dependency."""
        client = self._make_client()
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong",
        })
        # Should get 401 (invalid credentials), not 500 (missing dependency)
        assert response.status_code == 401

    def test_login_returns_429_when_rate_limited(self) -> None:
        """Login returns 429 when rate limiter blocks the request."""
        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = False

        _reset_repos()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        app = create_app(settings)
        app.dependency_overrides[get_rate_limiter] = lambda: mock_limiter
        client = TestClient(app)

        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong",
        })
        assert response.status_code == 429
        assert response.json() == {"detail": "Too many requests"}
        assert "Retry-After" in response.headers


class TestRegisterRateLimit:
    """Test rate limiting on POST /auth/register."""

    def _make_client(self) -> TestClient:
        """Create a test client with NoOpRateLimiter override."""
        _reset_repos()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        app = create_app(settings)
        app.dependency_overrides[get_rate_limiter] = lambda: NoOpRateLimiter()
        return TestClient(app)

    def test_register_endpoint_accepts_rate_limit_dependency(self) -> None:
        """Register endpoint must have require_rate_limit wired as dependency."""
        client = self._make_client()
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
        })
        # Should not get 500 (missing dependency)
        assert response.status_code in (201, 409, 422)

    def test_register_returns_429_when_rate_limited(self) -> None:
        """Register returns 429 when rate limiter blocks the request."""
        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = False

        _reset_repos()
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=True,
        )
        app = create_app(settings)
        app.dependency_overrides[get_rate_limiter] = lambda: mock_limiter
        client = TestClient(app)

        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert response.status_code == 429
        assert response.json() == {"detail": "Too many requests"}
        assert "Retry-After" in response.headers
