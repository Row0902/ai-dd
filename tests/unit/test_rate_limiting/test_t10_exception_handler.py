"""T10: Unit tests for 429 RateLimitExceededError handler in main.py."""

from __future__ import annotations

from fastapi.testclient import TestClient

from config.settings import AppSettings
from domain.rate_limiting.exceptions import RateLimitExceededError
from main import create_app

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


class TestRateLimitExceptionHandler:
    """Test the 429 exception handler registered in create_app()."""

    def _make_app(self) -> TestClient:
        """Create a test client with rate limiting disabled (NoOp)."""
        settings = AppSettings(
            DATABASE_URL="memory://",
            SECRET_KEY=TEST_SECRET,
            RATE_LIMIT_ENABLED=False,
        )
        return TestClient(create_app(settings))

    def test_handler_returns_429_status(self) -> None:
        """RateLimitExceededError handler returns HTTP 429."""
        client = self._make_app()
        app = client.app

        # Verify the handler is registered by checking exception handlers
        # The handler should be in the app's exception handlers

        # Check that RateLimitExceededError is handled
        handler = app.exception_handlers.get(RateLimitExceededError)
        assert handler is not None, "RateLimitExceededError handler not registered"

    def test_handler_returns_correct_body(self) -> None:
        r"""Handler returns {\"detail\": \"Too many requests\"}."""
        from starlette.requests import Request

        client = self._make_app()
        app = client.app
        handler = app.exception_handlers[RateLimitExceededError]

        # Create a mock request
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)

        exc = RateLimitExceededError(retry_after=60, limit=10)
        import asyncio

        response = asyncio.run(handler(request, exc))
        assert response.status_code == 429

        import json

        body = json.loads(response.body)
        assert body == {"detail": "Too many requests"}

    def test_handler_sets_retry_after_header(self) -> None:
        """Handler sets Retry-After header from exception."""
        from starlette.requests import Request

        client = self._make_app()
        app = client.app
        handler = app.exception_handlers[RateLimitExceededError]

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)

        exc = RateLimitExceededError(retry_after=45, limit=10)
        import asyncio

        response = asyncio.run(handler(request, exc))
        assert response.headers["Retry-After"] == "45"

    def test_handler_sets_all_four_ietf_headers(self) -> None:
        """T15: 429 response includes all 4 IETF RateLimit headers.

        Verifies REQ-RL-003: Retry-After, RateLimit-Limit,
        RateLimit-Remaining, and RateLimit-Reset are all present.
        """
        from starlette.requests import Request

        client = self._make_app()
        app = client.app
        handler = app.exception_handlers[RateLimitExceededError]

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "query_string": b"",
            "headers": [],
        }
        request = Request(scope)

        exc = RateLimitExceededError(retry_after=30, limit=5)
        import asyncio

        response = asyncio.run(handler(request, exc))

        # All 4 IETF headers must be present
        assert "Retry-After" in response.headers
        assert "RateLimit-Limit" in response.headers
        assert "RateLimit-Remaining" in response.headers
        assert "RateLimit-Reset" in response.headers

        # Verify values
        assert response.headers["Retry-After"] == "30"
        assert response.headers["RateLimit-Limit"] == "5"
        assert response.headers["RateLimit-Remaining"] == "0"
        assert int(response.headers["RateLimit-Reset"]) > 0
