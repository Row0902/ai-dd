"""Tests for T4: RateLimitExceededError exception."""

from __future__ import annotations


class TestRateLimitExceededError:
    """Verify RateLimitExceededError is a proper domain exception."""

    def test_exception_is_importable(self) -> None:
        """RateLimitExceededError can be imported from domain.rate_limiting."""
        from domain.rate_limiting.exceptions import RateLimitExceededError

        assert RateLimitExceededError is not None

    def test_exception_extends_domain_error(self) -> None:
        """RateLimitExceededError is a subclass of DomainError."""
        from domain.exceptions import DomainError
        from domain.rate_limiting.exceptions import RateLimitExceededError

        assert issubclass(RateLimitExceededError, DomainError)

    def test_exception_is_subclass_of_exception(self) -> None:
        """RateLimitExceededError is ultimately an Exception."""
        from domain.rate_limiting.exceptions import RateLimitExceededError

        assert issubclass(RateLimitExceededError, Exception)

    def test_exception_has_retry_after_field(self) -> None:
        """RateLimitExceededError carries a retry_after integer field."""
        from domain.rate_limiting.exceptions import RateLimitExceededError

        exc = RateLimitExceededError(retry_after=30)
        assert exc.retry_after == 30

    def test_exception_str_representation(self) -> None:
        """RateLimitExceededError has a readable string representation."""
        from domain.rate_limiting.exceptions import RateLimitExceededError

        exc = RateLimitExceededError(retry_after=45)
        result = str(exc)
        assert "45" in result
        assert len(result) > 0

    def test_exception_can_be_raised_and_caught(self) -> None:
        """RateLimitExceededError can be raised and caught as DomainError."""
        import pytest

        from domain.exceptions import DomainError
        from domain.rate_limiting.exceptions import RateLimitExceededError

        with pytest.raises(DomainError):
            raise RateLimitExceededError(retry_after=10)

    def test_exception_preserves_retry_after_after_raise(self) -> None:
        """retry_after field survives exception propagation."""
        from domain.rate_limiting.exceptions import RateLimitExceededError

        try:
            raise RateLimitExceededError(retry_after=60)
        except RateLimitExceededError as exc:
            assert exc.retry_after == 60
