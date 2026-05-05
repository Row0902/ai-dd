"""T8: Unit tests for require_rate_limit() dependency factory."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.rate_limiting.exceptions import RateLimitExceededError
from domain.rate_limiting.ports import RateLimiter


class TestExtractClientIp:
    """Test IP extraction from request."""

    def _make_request(
        self,
        client_host: str | None = "127.0.0.1",
        x_forwarded_for: str | None = None,
    ) -> MagicMock:
        """Create a mock FastAPI Request."""
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = client_host
        request.url = MagicMock()
        request.url.path = "/test"
        headers = {}
        if x_forwarded_for is not None:
            headers["x-forwarded-for"] = x_forwarded_for
        request.headers = headers
        return request

    def test_uses_client_host_when_no_proxy_header(self) -> None:
        """IP comes from request.client.host when no X-Forwarded-For."""
        from api.middleware.rate_limit import _extract_client_ip

        request = self._make_request(client_host="10.0.0.1")
        assert _extract_client_ip(request) == "10.0.0.1"

    def test_uses_first_forwarded_ip(self) -> None:
        """IP comes from first entry in X-Forwarded-For."""
        from api.middleware.rate_limit import _extract_client_ip

        request = self._make_request(
            client_host="10.0.0.1",
            x_forwarded_for="203.0.113.50, 10.0.0.1",
        )
        assert _extract_client_ip(request) == "203.0.113.50"

    def test_single_forwarded_ip(self) -> None:
        """Single IP in X-Forwarded-For is used directly."""
        from api.middleware.rate_limit import _extract_client_ip

        request = self._make_request(
            client_host="10.0.0.1",
            x_forwarded_for="198.51.100.1",
        )
        assert _extract_client_ip(request) == "198.51.100.1"

    def test_falls_back_when_client_is_none(self) -> None:
        """Falls back to 'unknown' when request.client is None."""
        from api.middleware.rate_limit import _extract_client_ip

        request = MagicMock()
        request.client = None
        request.headers = {}
        assert _extract_client_ip(request) == "unknown"


class TestRequireRateLimitFactory:
    """Test the require_rate_limit() factory function."""

    @pytest.mark.asyncio
    async def test_allows_request_under_limit(self) -> None:
        """Dependency allows request when limiter returns True."""
        from api.middleware.rate_limit import require_rate_limit

        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = True

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "10.0.0.1"
        request.url = MagicMock()
        request.url.path = "/test"
        request.headers = {}
        response = MagicMock()
        response.headers = {}

        dep = require_rate_limit(5, 60)
        # Should not raise
        await dep(request=request, response=response, limiter=mock_limiter)

        # Headers should be set
        assert "RateLimit-Limit" in response.headers
        assert "RateLimit-Remaining" in response.headers
        assert "RateLimit-Reset" in response.headers

    @pytest.mark.asyncio
    async def test_raises_when_over_limit(self) -> None:
        """Dependency raises RateLimitExceededError when limiter returns False."""
        from api.middleware.rate_limit import require_rate_limit

        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = False

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "10.0.0.1"
        request.url = MagicMock()
        request.url.path = "/test"
        request.headers = {}
        response = MagicMock()
        response.headers = {}

        dep = require_rate_limit(5, 60)
        with pytest.raises(RateLimitExceededError) as exc_info:
            await dep(request=request, response=response, limiter=mock_limiter)

        assert exc_info.value.retry_after > 0

    @pytest.mark.asyncio
    async def test_builds_correct_rate_limit_key(self) -> None:
        """Key format is rate_limit:{ip}:{path}."""
        from api.middleware.rate_limit import require_rate_limit

        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = True

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.url = MagicMock()
        request.url.path = "/auth/login"
        request.headers = {}
        response = MagicMock()
        response.headers = {}

        dep = require_rate_limit(5, 60)
        await dep(request=request, response=response, limiter=mock_limiter)

        mock_limiter.check.assert_called_once_with(
            key="rate_limit:192.168.1.1:/auth/login",
            max_requests=5,
            window_seconds=60,
        )

    @pytest.mark.asyncio
    async def test_sets_remaining_header_to_zero_when_at_limit(self) -> None:
        """RateLimit-Remaining is 0 when at the limit."""
        from api.middleware.rate_limit import require_rate_limit

        mock_limiter = AsyncMock(spec=RateLimiter)
        mock_limiter.check.return_value = False

        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "10.0.0.1"
        request.url = MagicMock()
        request.url.path = "/test"
        request.headers = {}
        response = MagicMock()
        response.headers = {}

        dep = require_rate_limit(5, 60)
        with pytest.raises(RateLimitExceededError):
            await dep(request=request, response=response, limiter=mock_limiter)

        assert response.headers["RateLimit-Remaining"] == "0"
        assert response.headers["RateLimit-Limit"] == "5"
