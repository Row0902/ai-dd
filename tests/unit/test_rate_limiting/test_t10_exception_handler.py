"""T10: Unit tests for 429 RateLimitExceededError handler in main.py."""

from __future__ import annotations

import pytest
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
        from starlette.exceptions import HTTPException as StarletteHTTPException

        # Check that RateLimitExceededError is handled
        handler = app.exception_handlers.get(RateLimitExceededError)
        assert handler is not None, "RateLimitExceededError handler not registered"

    def test_handler_returns_correct_body(self) -> None:
        """Handler returns {\"detail\": \"Too many requests\"}."""
        from starlette.requests import Request
        from starlette.responses import JSONResponse

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
