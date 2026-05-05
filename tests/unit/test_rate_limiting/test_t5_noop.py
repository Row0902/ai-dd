"""T5: Unit tests for NoOpRateLimiter — always allows requests."""

from __future__ import annotations

import pytest

from domain.rate_limiting.ports import RateLimiter
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter


class TestNoOpRateLimiter:
    """Tests for NoOpRateLimiter behavior and contract compliance."""

    @pytest.fixture
    def limiter(self) -> NoOpRateLimiter:
        """Provide a NoOpRateLimiter instance."""
        return NoOpRateLimiter()

    def test_is_instance_of_rate_limiter(self, limiter: NoOpRateLimiter) -> None:
        """NoOpRateLimiter must implement the RateLimiter ABC."""
        assert isinstance(limiter, RateLimiter)

    @pytest.mark.asyncio
    async def test_check_always_returns_true(self, limiter: NoOpRateLimiter) -> None:
        """check() must always return True regardless of parameters."""
        result = await limiter.check(key="any-key", max_requests=1, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_returns_true_with_zero_limit(self, limiter: NoOpRateLimiter) -> None:
        """check() returns True even when max_requests is 0 (would block real limiter)."""
        result = await limiter.check(key="test", max_requests=0, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_returns_true_with_various_keys(self, limiter: NoOpRateLimiter) -> None:
        """check() returns True for any key string."""
        keys = ["ip:path", "192.168.1.1:/api/books", "", "rate_limit:10.0.0.1:/auth/login"]
        for key in keys:
            result = await limiter.check(key=key, max_requests=10, window_seconds=60)
            assert result is True

    @pytest.mark.asyncio
    async def test_reset_does_nothing(self, limiter: NoOpRateLimiter) -> None:
        """reset() must complete without error (no-op)."""
        await limiter.reset(key="any-key")
        # No assertion needed — just verify it doesn't raise
