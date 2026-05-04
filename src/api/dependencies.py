"""Dependency providers for the API layer."""

from __future__ import annotations

from config.settings import AppSettings
from domain.auth.ports import (
    InvitationRepository,
    NotificationService,
    PasswordHasher,
    TokenService,
    UserRepository,
)
from domain.repositories import BookRepository
from infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.auth.in_memory_invitation_repository import (
    InMemoryInvitationRepository,
)
from infrastructure.auth.in_memory_user_repository import InMemoryUserRepository
from infrastructure.auth.jwt_token_service import JwtTokenService
from infrastructure.auth.logging_notification_service import (
    LoggingNotificationService,
)

_settings: AppSettings | None = None

# Singleton instances for in-memory repos (shared across requests)
_user_repo: UserRepository | None = None
_invitation_repo: InvitationRepository | None = None
_password_hasher: PasswordHasher | None = None
_notification_service: NotificationService | None = None


def get_settings() -> AppSettings:
    """Provide application settings (singleton).

    Returns:
        The global AppSettings instance.
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def get_book_repo() -> BookRepository:
    """Provide a BookRepository implementation.

    The composition root (e.g. `main.create_app`) must override this dependency.
    """
    raise RuntimeError("BookRepository provider not configured")


def get_user_repo() -> UserRepository:
    """Provide a UserRepository implementation.

    Returns:
        In-memory user repository (singleton).
    """
    global _user_repo
    if _user_repo is None:
        _user_repo = InMemoryUserRepository()
    return _user_repo


def get_invitation_repo() -> InvitationRepository:
    """Provide an InvitationRepository implementation.

    Returns:
        In-memory invitation repository (singleton).
    """
    global _invitation_repo
    if _invitation_repo is None:
        _invitation_repo = InMemoryInvitationRepository()
    return _invitation_repo


def get_password_hasher() -> PasswordHasher:
    """Provide a PasswordHasher implementation.

    Returns:
        Bcrypt password hasher instance.
    """
    global _password_hasher
    if _password_hasher is None:
        _password_hasher = BcryptPasswordHasher()
    return _password_hasher


def get_token_service() -> TokenService:
    """Provide a TokenService implementation.

    Returns:
        JWT token service configured with the app secret key.
    """
    settings = get_settings()
    return JwtTokenService(settings.SECRET_KEY)


def get_notification_service() -> NotificationService:
    """Provide a NotificationService implementation.

    Returns:
        Logging notification service instance.
    """
    global _notification_service
    if _notification_service is None:
        _notification_service = LoggingNotificationService()
    return _notification_service
