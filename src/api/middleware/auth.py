"""Auth middleware: JWT extraction and permission checking for FastAPI."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies import get_settings
from config.settings import AppSettings
from domain.auth.entities import UserRole
from domain.auth.exceptions import AuthenticationError
from domain.auth.permissions import ROLE_PERMISSIONS, Operation
from infrastructure.auth.jwt_token_service import JwtTokenService

security = HTTPBearer()


def require_permission(operation: Operation):
    """Create a FastAPI dependency that enforces a permission check.

    Extracts a JWT from the ``Authorization: Bearer <token>`` header,
    verifies it, and checks that the user's role grants the requested
    operation.  Stores the authenticated user id in ``request.state``
    so downstream middleware (e.g., logging) can access it.

    Args:
        operation: The required operation for the endpoint.

    Returns:
        An async dependency function that yields user claims dict
        with ``user_id`` and ``role`` keys.

    Raises:
        HTTPException: 401 if token is missing or invalid.
        HTTPException: 403 if the user lacks the required permission.
    """

    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        settings: AppSettings = Depends(get_settings),
        request: Request = None,  # ty: ignore[invalid-parameter-default]
    ) -> dict:
        """Verify JWT and check permission.

        Args:
            credentials: Bearer token from the Authorization header.
            settings: Application settings providing the JWT secret.
            request: The incoming HTTP request (used to store user context).

        Returns:
            Dict with ``user_id`` and ``role`` keys.

        Raises:
            HTTPException: 401 for invalid tokens, 403 for insufficient permissions.
        """
        token_service = JwtTokenService(settings.SECRET_KEY)
        try:
            claims = token_service.verify(credentials.credentials)
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=401, detail="Invalid or expired token"
            ) from exc
        try:
            role = UserRole(claims["role"])
        except ValueError as exc:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions"
            ) from exc
        if operation not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        ctx = {"user_id": claims["sub"], "role": role}
        if request:
            request.state.user_id = claims["sub"]
            request.state.user_role = role.value
        return ctx

    return dependency
