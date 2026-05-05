"""T7: Unit tests for RedisRateLimiter (sliding window via sorted sets)."""

from __future__ import annotations

import fakeredis
import fakeredis.aioredis
import pytest

from domain.rate_limiting.ports import RateLimiter
from infrastructure.rate_limiting.redis_rate_limiter import RedisRateLimiter


@pytest.fixture
def fake_redis() -> fakeredis.aioredis.FakeRedis:
    """Provide a fake async Redis instance."""
    return fakeredis.aioredis.FakeRedis()


@pytest.fixture
def limiter(fake_redis: fakeredis.FakeRedis) -> RedisRateLimiter:
    """Provide a RedisRateLimiter with fake Redis."""
    return RedisRateLimiter(fake_redis)


class TestRedisRateLimiterContract:
    """Verify RedisRateLimiter implements RateLimiter ABC."""

    def test_is_instance_of_rate_limiter(self, limiter: RedisRateLimiter) -> None:
        """Must implement the RateLimiter port."""
        assert isinstance(limiter, RateLimiter)


class TestCheckAllows:
    """Test check() allows requests under the limit."""

    @pytest.mark.asyncio
    async def test_first_request_allowed(self, limiter: RedisRateLimiter) -> None:
        """First request within window must be allowed."""
        result = await limiter.check(key="test:key", max_requests=5, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_requests_under_limit_allowed(self, limiter: RedisRateLimiter) -> None:
        """Requests under the limit must all be allowed."""
        for _ in range(5):
            result = await limiter.check(key="test:key", max_requests=10, window_seconds=60)
            assert result is True

    @pytest.mark.asyncio
    async def test_different_keys_independent(self, limiter: RedisRateLimiter) -> None:
        """Rate limits on different keys must be independent."""
        for _ in range(5):
            await limiter.check(key="key-a", max_requests=5, window_seconds=60)

        result = await limiter.check(key="key-b", max_requests=5, window_seconds=60)
        assert result is True


class TestCheckBlocks:
    """Test check() blocks requests at or over the limit."""

    @pytest.mark.asyncio
    async def test_request_at_limit_blocked(self, limiter: RedisRateLimiter) -> None:
        """Request that exceeds the limit must be blocked."""
        for _ in range(3):
            await limiter.check(key="test:block", max_requests=3, window_seconds=60)

        result = await limiter.check(key="test:block", max_requests=3, window_seconds=60)
        assert result is False

    @pytest.mark.asyncio
    async def test_request_over_limit_blocked(self, limiter: RedisRateLimiter) -> None:
        """Requests well over the limit must all be blocked."""
        for _ in range(10):
            await limiter.check(key="test:over", max_requests=2, window_seconds=60)

        result = await limiter.check(key="test:over", max_requests=2, window_seconds=60)
        assert result is False


class TestSlidingWindow:
    """Test that the sliding window expires old entries."""

    @pytest.mark.asyncio
    async def test_expired_entries_removed(self, limiter: RedisRateLimiter) -> None:
        """After window expires, new requests must be allowed."""
        for _ in range(3):
            await limiter.check(key="test:expire", max_requests=3, window_seconds=1)

        # Manually expire entries by waiting
        import asyncio
        await asyncio.sleep(1.1)

        result = await limiter.check(key="test:expire", max_requests=3, window_seconds=1)
        assert result is True


class TestReset:
    """Test reset() clears the rate limit counter."""

    @pytest.mark.asyncio
    async def test_reset_clears_counter(self, limiter: RedisRateLimiter) -> None:
        """After reset, requests must be allowed again."""
        for _ in range(3):
            await limiter.check(key="test:reset", max_requests=3, window_seconds=60)

        # Now at limit
        result = await limiter.check(key="test:reset", max_requests=3, window_seconds=60)
        assert result is False

        # Reset
        await limiter.reset(key="test:reset")

        # Should be allowed again
        result = await limiter.check(key="test:reset", max_requests=3, window_seconds=60)
        assert result is True


class TestFailOpen:
    """Test fail-open behavior when Redis is unreachable."""

    @pytest.mark.asyncio
    async def test_fail_open_on_connection_error(self) -> None:
        """When Redis raises ConnectionError, check() must return True."""
        from unittest.mock import AsyncMock, MagicMock

        broken_redis = MagicMock()
        broken_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
        mock_pipe.zcard = MagicMock(return_value=mock_pipe)
        mock_pipe.zadd = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(side_effect=ConnectionError("Connection refused"))
        broken_redis.pipeline.return_value = mock_pipe

        limiter = RedisRateLimiter(broken_redis)
        result = await limiter.check(key="test:fail", max_requests=1, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_fail_open_on_timeout_error(self) -> None:
        """T17: When Redis raises TimeoutError, check() must return True."""
        from unittest.mock import AsyncMock, MagicMock

        broken_redis = MagicMock()
        broken_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
        mock_pipe.zcard = MagicMock(return_value=mock_pipe)
        mock_pipe.zadd = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(side_effect=TimeoutError("Redis timeout"))
        broken_redis.pipeline.return_value = mock_pipe

        limiter = RedisRateLimiter(broken_redis)
        result = await limiter.check(key="test:timeout", max_requests=1, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_fail_open_on_redis_error(self) -> None:
        """T17: When Redis raises RedisError, check() must return True."""
        from unittest.mock import AsyncMock, MagicMock

        broken_redis = MagicMock()
        broken_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
        mock_pipe.zcard = MagicMock(return_value=mock_pipe)
        mock_pipe.zadd = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(side_effect=Exception("WRONGTYPE Operation against a key"))
        broken_redis.pipeline.return_value = mock_pipe

        limiter = RedisRateLimiter(broken_redis)
        result = await limiter.check(key="test:redis_error", max_requests=1, window_seconds=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_fail_open_on_response_error(self) -> None:
        """T17: When Redis raises ResponseError, check() must return True."""
        from unittest.mock import AsyncMock, MagicMock

        broken_redis = MagicMock()
        broken_redis.pipeline = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.zremrangebyscore = MagicMock(return_value=mock_pipe)
        mock_pipe.zcard = MagicMock(return_value=mock_pipe)
        mock_pipe.zadd = MagicMock(return_value=mock_pipe)
        mock_pipe.expire = MagicMock(return_value=mock_pipe)
        mock_pipe.execute = AsyncMock(side_effect=Exception("BUSY Redis is busy"))
        broken_redis.pipeline.return_value = mock_pipe

        limiter = RedisRateLimiter(broken_redis)
        result = await limiter.check(key="test:response_error", max_requests=1, window_seconds=60)
        assert result is True
