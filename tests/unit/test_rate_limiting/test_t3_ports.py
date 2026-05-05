"""Tests for T3: RateLimiter ABC port."""

from __future__ import annotations

import inspect

import pytest


class TestRateLimiterABC:
    """Verify RateLimiter is a proper abstract base class."""

    def test_rate_limiter_is_importable(self) -> None:
        """RateLimiter can be imported from domain.rate_limiting."""
        from domain.rate_limiting import RateLimiter

        assert RateLimiter is not None

    def test_rate_limiter_is_abstract(self) -> None:
        """RateLimiter cannot be instantiated directly."""
        from domain.rate_limiting import RateLimiter

        with pytest.raises(TypeError, match="abstract"):
            RateLimiter()  # type: ignore[abstract]

    def test_rate_limiter_has_check_method(self) -> None:
        """RateLimiter defines async check() method."""
        from domain.rate_limiting import RateLimiter

        assert hasattr(RateLimiter, "check")
        assert inspect.iscoroutinefunction(RateLimiter.check)

    def test_rate_limiter_has_reset_method(self) -> None:
        """RateLimiter defines async reset() method."""
        from domain.rate_limiting import RateLimiter

        assert hasattr(RateLimiter, "reset")
        assert inspect.iscoroutinefunction(RateLimiter.reset)

    def test_check_method_signature(self) -> None:
        """check() accepts key, max_requests, window_seconds and returns bool."""
        import typing

        from domain.rate_limiting import RateLimiter

        hints = typing.get_type_hints(RateLimiter.check)
        assert hints["key"] is str
        assert hints["max_requests"] is int
        assert hints["window_seconds"] is int
        assert hints["return"] is bool

    def test_reset_method_signature(self) -> None:
        """reset() accepts key and returns None."""
        import typing

        from domain.rate_limiting import RateLimiter

        hints = typing.get_type_hints(RateLimiter.reset)
        assert hints["key"] is str
        assert hints["return"] is type(None)

    def test_concrete_implementation_works(self) -> None:
        """A concrete subclass of RateLimiter can be instantiated."""
        from domain.rate_limiting import RateLimiter

        class StubRateLimiter(RateLimiter):
            async def check(self, key: str, max_requests: int, window_seconds: int) -> bool:
                return True

            async def reset(self, key: str) -> None:
                pass

        limiter = StubRateLimiter()
        assert limiter is not None
