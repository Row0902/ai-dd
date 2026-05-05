"""Dependency providers for the API layer."""

from __future__ import annotations

from urllib.parse import urlparse

from config.settings import AppSettings
from domain.auth.ports import (
    InvitationRepository,
    NotificationService,
    PasswordHasher,
    TokenService,
    UserRepository,
)
from domain.collections.repositories import CollectionRepository
from domain.favorites.repositories import FavoriteRepository
from domain.rate_limiting.ports import RateLimiter
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
from infrastructure.persistence.in_memory_collection_repository import (
    InMemoryCollectionRepository,
)
from infrastructure.persistence.in_memory_favorite_repository import (
    InMemoryFavoriteRepository,
)
from infrastructure.rate_limiting.noop_rate_limiter import NoOpRateLimiter
from infrastructure.rate_limiting.redis_client import create_redis_client
from infrastructure.rate_limiting.redis_rate_limiter import RedisRateLimiter

_settings: AppSettings | None = None

# Singleton instances for in-memory repos (shared across requests)
_user_repo: UserRepository | None = None
_invitation_repo: InvitationRepository | None = None
_password_hasher: PasswordHasher | None = None
_notification_service: NotificationService | None = None
_collection_repo: CollectionRepository | None = None
_favorite_repo: FavoriteRepository | None = None
_rate_limiter: RateLimiter | None = None


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


def get_collection_repo() -> CollectionRepository:
    """Provide a CollectionRepository implementation.

    Returns:
        In-memory collection repository (singleton).
    """
    global _collection_repo
    if _collection_repo is None:
        _collection_repo = InMemoryCollectionRepository()
    return _collection_repo


def get_favorite_repo() -> FavoriteRepository:
    """Provide a FavoriteRepository implementation.

    Returns:
        In-memory favorite repository (singleton).
    """
    global _favorite_repo
    if _favorite_repo is None:
        _favorite_repo = InMemoryFavoriteRepository()
    return _favorite_repo


def get_redis_client(settings: AppSettings | None = None):
    """Provide an async Redis client from application settings.

    Args:
        settings: Application settings. If None, uses get_settings().

    Returns:
        A ``redis.asyncio.Redis`` client instance.
    """
    if settings is None:
        settings = get_settings()
    return create_redis_client(settings)


def get_rate_limiter() -> RateLimiter:
    """Provide a RateLimiter implementation based on settings.

    Resolution order:
    1. ``RATE_LIMIT_ENABLED=False`` → NoOpRateLimiter
    2. ``DATABASE_URL=memory://`` → NoOpRateLimiter
    3. Otherwise → RedisRateLimiter

    Returns:
        A RateLimiter implementation (singleton).
    """
    global _rate_limiter
    if _rate_limiter is not None:
        return _rate_limiter

    settings = get_settings()

    if not settings.RATE_LIMIT_ENABLED:
        _rate_limiter = NoOpRateLimiter()
        return _rate_limiter

    scheme = urlparse(settings.DATABASE_URL).scheme or "memory"
    if scheme == "memory":
        _rate_limiter = NoOpRateLimiter()
        return _rate_limiter

    redis_client = get_redis_client(settings)
    _rate_limiter = RedisRateLimiter(redis_client)
    return _rate_limiter


def _reset_repos() -> None:
    """Reset all singleton repository instances.

    Called during test setup to ensure test isolation.
    """
    global _collection_repo, _favorite_repo, _rate_limiter
    _collection_repo = None
    _favorite_repo = None
    _rate_limiter = None
