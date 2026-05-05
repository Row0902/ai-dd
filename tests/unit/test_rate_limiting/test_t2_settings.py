"""Tests for T2: rate-limit settings in AppSettings."""

from __future__ import annotations

from config.settings import AppSettings


class TestRateLimitSettings:
    """Verify rate-limit configuration fields exist with correct defaults."""

    def test_settings_has_rate_limit_enabled(self) -> None:
        """RATE_LIMIT_ENABLED defaults to True."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_ENABLED is True

    def test_settings_has_rate_limit_fail_open(self) -> None:
        """RATE_LIMIT_FAIL_OPEN defaults to True."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_FAIL_OPEN is True

    def test_settings_has_rate_limit_login_max(self) -> None:
        """RATE_LIMIT_LOGIN_MAX defaults to 5."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_LOGIN_MAX == 5

    def test_settings_has_rate_limit_login_window(self) -> None:
        """RATE_LIMIT_LOGIN_WINDOW defaults to 60 seconds."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_LOGIN_WINDOW == 60

    def test_settings_has_rate_limit_register_max(self) -> None:
        """RATE_LIMIT_REGISTER_MAX defaults to 3."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_REGISTER_MAX == 3

    def test_settings_has_rate_limit_register_window(self) -> None:
        """RATE_LIMIT_REGISTER_WINDOW defaults to 60 seconds."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_REGISTER_WINDOW == 60

    def test_settings_has_rate_limit_global_max(self) -> None:
        """RATE_LIMIT_GLOBAL_MAX defaults to 100."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_GLOBAL_MAX == 100

    def test_settings_has_rate_limit_global_window(self) -> None:
        """RATE_LIMIT_GLOBAL_WINDOW defaults to 60 seconds."""
        settings = AppSettings()
        assert settings.RATE_LIMIT_GLOBAL_WINDOW == 60

    def test_settings_can_override_via_env(self, monkeypatch: object) -> None:
        """Rate limit fields can be overridden via environment variables."""
        import os

        os.environ["RATE_LIMIT_LOGIN_MAX"] = "10"
        try:
            settings = AppSettings()
            assert settings.RATE_LIMIT_LOGIN_MAX == 10
        finally:
            del os.environ["RATE_LIMIT_LOGIN_MAX"]
