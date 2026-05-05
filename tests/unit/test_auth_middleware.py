"""Unit tests for the auth middleware: require_permission dependency."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from api.middleware.auth import require_permission
from config.settings import AppSettings
from domain.auth.permissions import Operation
from infrastructure.auth.jwt_token_service import JwtTokenService

TEST_SECRET = "test-secret-key-at-least-32-chars-long"


def _app_with_protected_endpoint(operation: Operation) -> FastAPI:
    """Create a minimal FastAPI app with a protected test endpoint.

    Args:
        operation: The operation to require for the test endpoint.

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        user: dict = Depends(require_permission(operation)),
    ):
        return {"user_id": user["user_id"], "role": user["role"]}

    return app


class TestRequirePermission:
    """Tests for the require_permission FastAPI dependency."""

    def test_valid_token_with_permission_returns_claims(self) -> None:
        """A valid token with the correct permission returns user claims."""
        app = _app_with_protected_endpoint(Operation.BOOK_READ)
        token_service = JwtTokenService(TEST_SECRET)
        token = token_service.generate("user-123", "user")

        # Override settings dependency
        from api.dependencies import get_settings

        app.dependency_overrides[get_settings] = lambda: AppSettings(
            DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET
        )

        client = TestClient(app)
        resp = client.get(
            "/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["user_id"] == "user-123"
        assert body["role"] == "user"

    def test_missing_auth_header_returns_401(self) -> None:
        """Missing Authorization header returns 401 (HTTPBearer default)."""
        app = _app_with_protected_endpoint(Operation.BOOK_READ)

        from api.dependencies import get_settings

        app.dependency_overrides[get_settings] = lambda: AppSettings(
            DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET
        )

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/protected")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self) -> None:
        """An invalid JWT token returns 401."""
        app = _app_with_protected_endpoint(Operation.BOOK_READ)

        from api.dependencies import get_settings

        app.dependency_overrides[get_settings] = lambda: AppSettings(
            DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET
        )

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid or expired token"

    def test_insufficient_permissions_returns_403(self) -> None:
        """A user without the required permission returns 403."""
        app = _app_with_protected_endpoint(Operation.BOOK_DELETE)
        token_service = JwtTokenService(TEST_SECRET)
        # Generate token with "user" role — has BOOK_DELETE per ROLE_PERMISSIONS
        # But let's test with an operation user DOESN'T have
        # Actually USER has all BOOK ops. Let's use a custom scenario.
        # We need to test the permission check. Since USER has all ops,
        # we test by requiring an op that exists but the role doesn't have.
        # For that we'd need a role that's not in ROLE_PERMISSIONS with that op.
        # Simplest: create a token with a role not in ROLE_PERMISSIONS.
        token = token_service.generate("user-123", "nonexistent_role")

        from api.dependencies import get_settings

        app.dependency_overrides[get_settings] = lambda: AppSettings(
            DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET
        )

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Insufficient permissions"

    def test_admin_has_all_permissions(self) -> None:
        """An admin token has access to all operations."""
        app = _app_with_protected_endpoint(Operation.BOOK_DELETE)
        token_service = JwtTokenService(TEST_SECRET)
        token = token_service.generate("admin-123", "admin")

        from api.dependencies import get_settings

        app.dependency_overrides[get_settings] = lambda: AppSettings(
            DATABASE_URL="memory://", SECRET_KEY=TEST_SECRET
        )

        client = TestClient(app)
        resp = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"
