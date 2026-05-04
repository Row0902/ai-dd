"""Unit tests for auth domain exceptions."""

from domain.auth.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvitationError,
    UserAlreadyExists,
)
from domain.exceptions import DomainError


class TestAuthExceptionHierarchy:
    """Test that all auth exceptions inherit from DomainError."""

    def test_authentication_error_inherits_domain_error(self) -> None:
        """AuthenticationError is a subclass of DomainError."""
        assert issubclass(AuthenticationError, DomainError)

    def test_authorization_error_inherits_domain_error(self) -> None:
        """AuthorizationError is a subclass of DomainError."""
        assert issubclass(AuthorizationError, DomainError)

    def test_user_already_exists_inherits_domain_error(self) -> None:
        """UserAlreadyExists is a subclass of DomainError."""
        assert issubclass(UserAlreadyExists, DomainError)

    def test_invitation_error_inherits_domain_error(self) -> None:
        """InvitationError is a subclass of DomainError."""
        assert issubclass(InvitationError, DomainError)


class TestAuthExceptionInstantiation:
    """Test that auth exceptions can be raised and carry messages."""

    def test_authentication_error_with_message(self) -> None:
        """AuthenticationError can be instantiated with a message."""
        error = AuthenticationError("invalid credentials")
        assert str(error) == "invalid credentials"

    def test_authorization_error_with_message(self) -> None:
        """AuthorizationError can be instantiated with a message."""
        error = AuthorizationError("insufficient permissions")
        assert str(error) == "insufficient permissions"

    def test_user_already_exists_with_message(self) -> None:
        """UserAlreadyExists can be instantiated with a message."""
        error = UserAlreadyExists("email already registered")
        assert str(error) == "email already registered"

    def test_invitation_error_with_message(self) -> None:
        """InvitationError can be instantiated with a message."""
        error = InvitationError("invitation expired")
        assert str(error) == "invitation expired"

    def test_auth_exceptions_can_be_caught_as_domain_error(self) -> None:
        """All auth exceptions can be caught as DomainError."""
        for exc_class in (
            AuthenticationError,
            AuthorizationError,
            UserAlreadyExists,
            InvitationError,
        ):
            try:
                raise exc_class("test")
            except DomainError:
                pass  # Expected
