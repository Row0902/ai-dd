"""Tests for T4: RateLimitExceeded exception."""

from __future__ import annotations


class TestRateLimitExceeded:
    """Verify RateLimitExceeded is a proper domain exception."""

    def test_exception_is_importable(self) -> None:
        """RateLimitExceeded can be imported from domain.rate_limiting."""
        from domain.rate_limiting.exceptions import RateLimitExceeded

        assert RateLimitExceeded is not None

    def test_exception_extends_domain_error(self) -> None:
        """RateLimitExceeded is a subclass of DomainError."""
        from domain.exceptions import DomainError
        from domain.rate_limiting.exceptions import RateLimitExceeded

        assert issubclass(RateLimitExceeded, DomainError)

    def test_exception_is_subclass_of_exception(self) -> None:
        """RateLimitExceeded is ultimately an Exception."""
        from domain.rate_limiting.exceptions import RateLimitExceeded

        assert issubclass(RateLimitExceeded, Exception)

    def test_exception_has_retry_after_field(self) -> None:
        """RateLimitExceeded carries a retry_after integer field."""
        from domain.rate_limiting.exceptions import RateLimitExceeded

        exc = RateLimitExceeded(retry_after=30)
        assert exc.retry_after == 30

    def test_exception_str_representation(self) -> None:
        """RateLimitExceeded has a readable string representation."""
        from domain.rate_limiting.exceptions import RateLimitExceeded

        exc = RateLimitExceeded(retry_after=45)
        result = str(exc)
        assert "45" in result
        assert len(result) > 0

    def test_exception_can_be_raised_and_caught(self) -> None:
        """RateLimitExceeded can be raised and caught as DomainError."""
        import pytest

        from domain.exceptions import DomainError
        from domain.rate_limiting.exceptions import RateLimitExceeded

        with pytest.raises(DomainError):
            raise RateLimitExceeded(retry_after=10)

    def test_exception_preserves_retry_after_after_raise(self) -> None:
        """retry_after field survives exception propagation."""
        from domain.rate_limiting.exceptions import RateLimitExceeded

        try:
            raise RateLimitExceeded(retry_after=60)
        except RateLimitExceeded as exc:
            assert exc.retry_after == 60
