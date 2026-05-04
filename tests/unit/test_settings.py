"""Tests for config.settings: pydantic-settings AppSettings."""

import os

import pytest

from config.settings import AppSettings


class TestAppSettingsDefaults:
    """Verify default values for AppSettings fields."""

    def test_database_url_default(self, monkeypatch: pytest.MonkeyPatch):
        """DATABASE_URL defaults to memory:// when not set."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.DATABASE_URL == "memory://"

    def test_access_token_expire_minutes_default(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """ACCESS_TOKEN_EXPIRE_MINUTES defaults to 30."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_cors_origins_default(self, monkeypatch: pytest.MonkeyPatch):
        """CORS_ORIGINS defaults to localhost:3000."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.CORS_ORIGINS == ["http://localhost:3000"]

    def test_log_level_default(self, monkeypatch: pytest.MonkeyPatch):
        """LOG_LEVEL defaults to INFO."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.LOG_LEVEL == "INFO"

    def test_env_default(self, monkeypatch: pytest.MonkeyPatch):
        """ENV defaults to development."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.ENV == "development"


class TestAppSettingsFromEnv:
    """Verify AppSettings reads values from environment variables."""

    def test_database_url_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """DATABASE_URL can be set via environment variable."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert settings.DATABASE_URL == "sqlite:///./test.db"

    def test_secret_key_from_env(self, monkeypatch: pytest.MonkeyPatch):
        """SECRET_KEY can be set via environment variable."""
        monkeypatch.setenv("SECRET_KEY", "super-secret-key-at-least-32-chars")
        settings = AppSettings()
        assert settings.SECRET_KEY == "super-secret-key-at-least-32-chars"


class TestAppSettingsValidation:
    """Verify SECRET_KEY validation."""

    def test_secret_key_too_short_raises(self, monkeypatch: pytest.MonkeyPatch):
        """SECRET_KEY shorter than 32 chars raises ValueError."""
        monkeypatch.setenv("SECRET_KEY", "short")
        with pytest.raises(ValueError, match="SECRET_KEY"):
            AppSettings()

    def test_secret_key_exactly_32_chars_passes(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """SECRET_KEY with exactly 32 chars is accepted."""
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        settings = AppSettings()
        assert len(settings.SECRET_KEY) == 32

    def test_secret_key_has_dev_default(self, monkeypatch: pytest.MonkeyPatch):
        """SECRET_KEY has a dev-safe default when not set."""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        settings = AppSettings()
        assert len(settings.SECRET_KEY) >= 32
