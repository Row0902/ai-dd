"""Fixtures compartidas para pruebas.

Este archivo es cargado automaticamente por pytest. Define aqui
las fixtures que se usan en multiples archivos de pruebas.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import _reset_repos
from config.settings import AppSettings
from infrastructure.auth.jwt_token_service import JwtTokenService
from main import create_app

TEST_SECRET_KEY = "test-secret-key-at-least-32-chars-long"


@pytest.fixture
def sample_book():
    """Retorna un diccionario de prueba con datos de un libro.

    Returns:
        dict: Diccionario con campos de un libro de prueba.
    """
    return {
        "name": "Clean Code",
        "author": "Robert C. Martin",
        "description": "A Handbook of Agile Software Craftsmanship",
        "url": "https://example.com/clean-code",
        "content": "Chapter 1: Clean Code...",
    }


@pytest.fixture
def test_settings() -> AppSettings:
    """Provide test-specific application settings.

    Returns:
        AppSettings configured for testing with a known secret key.
    """
    return AppSettings(
        DATABASE_URL="memory://",
        SECRET_KEY=TEST_SECRET_KEY,
    )


@pytest.fixture
def client(test_settings: AppSettings) -> TestClient:
    """Create a TestClient with in-memory repository and test settings.

    Resets singleton repos to ensure test isolation.

    Args:
        test_settings: Test application settings.

    Returns:
        Configured TestClient instance.
    """
    _reset_repos()
    return TestClient(create_app(test_settings))


@pytest.fixture
def auth_headers(test_settings: AppSettings) -> dict[str, str]:
    """Provide Authorization headers for a standard test user.

    Args:
        test_settings: Test application settings (provides SECRET_KEY).

    Returns:
        Dict with Authorization Bearer header.
    """
    token_service = JwtTokenService(test_settings.SECRET_KEY)
    token = token_service.generate("test-user-id", "user")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_settings: AppSettings) -> dict[str, str]:
    """Provide Authorization headers for an admin test user.

    Args:
        test_settings: Test application settings (provides SECRET_KEY).

    Returns:
        Dict with Authorization Bearer header for admin role.
    """
    token_service = JwtTokenService(test_settings.SECRET_KEY)
    token = token_service.generate("admin-id", "admin")
    return {"Authorization": f"Bearer {token}"}
