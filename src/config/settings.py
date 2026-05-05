"""Application settings via pydantic-settings.

Reads configuration from environment variables and ``.env`` file.
All environment-specific values (database URL, JWT secret, CORS origins)
are injected here — no hardcoded config elsewhere.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration loaded from env vars and .env file.

    Attributes:
        DATABASE_URL: Connection string for the persistence backend.
            Schemes: ``memory://`` (tests), ``sqlite://``, ``postgresql://``.
        REDIS_URL: Connection string for Redis cache/sessions.
        SECRET_KEY: Signing key for JWT tokens. Must be >= 32 characters.
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token lifetime in minutes.
        CORS_ORIGINS: Allowed CORS origins as a JSON list of strings.
        LOG_LEVEL: Python logging level name (DEBUG, INFO, WARNING, ERROR).
        ENV: Deployment environment (development, staging, production).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "memory://"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "dev-secret-key-change-in-production-32chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        """Validate SECRET_KEY is at least 32 characters."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
