"""Auth domain exceptions: authentication, authorization, and invitation errors."""

from domain.exceptions import DomainError


class AuthenticationError(DomainError):
    """Raised when authentication fails (invalid credentials, expired token)."""


class AuthorizationError(DomainError):
    """Raised when an authenticated user lacks required permissions."""


class UserAlreadyExists(DomainError):  # noqa: N818
    """Raised when attempting to register with an email that already exists."""


class InvitationError(DomainError):
    """Raised when an invitation is invalid, expired, or already used."""
