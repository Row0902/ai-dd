"""Auth router: registration, login, and invitation endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import (
    get_invitation_repo,
    get_notification_service,
    get_password_hasher,
    get_token_service,
    get_user_repo,
)
from api.middleware.auth import require_permission
from api.middleware.rate_limit import login_rate_limit, register_rate_limit
from application.use_cases.auth.create_invitation import create_invitation
from application.use_cases.auth.login_user import login_user
from application.use_cases.auth.register_user import register_user
from application.use_cases.auth.validate_invitation import validate_invitation
from domain.auth.entities import UserRole
from domain.auth.exceptions import (
    AuthenticationError,
    InvitationError,
    UserAlreadyExists,
)
from domain.auth.permissions import Operation
from domain.auth.ports import (
    InvitationRepository,
    NotificationService,
    PasswordHasher,
    TokenService,
    UserRepository,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterPayload(BaseModel):
    """Request payload for user registration."""

    email: str
    password: str
    invitation_token: str | None = None


class LoginPayload(BaseModel):
    """Request payload for user login."""

    email: str
    password: str


class CreateInvitationPayload(BaseModel):
    """Request payload for creating an invitation."""

    email: str
    role: str


@router.post("/register", status_code=201)
async def register_endpoint(
    payload: RegisterPayload,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    invitation_repo: Annotated[InvitationRepository, Depends(get_invitation_repo)],
    _rate_limit: None = Depends(register_rate_limit),
):
    """Register a new user.

    If ``invitation_token`` is provided, validates it first.

    Args:
        payload: Registration data (email, password, optional invitation token).
        user_repo: User repository port.
        hasher: Password hasher port.
        invitation_repo: Invitation repository port.

    Returns:
        User dict (without password hash).

    Raises:
        HTTPException: 409 if email already registered.
        HTTPException: 422 if invitation token is invalid.
    """
    if payload.invitation_token:
        try:
            await validate_invitation(invitation_repo, payload.invitation_token)
        except InvitationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        user = await register_user(user_repo, hasher, payload.email, payload.password)
    except UserAlreadyExists as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }


@router.post("/login")
async def login_endpoint(
    payload: LoginPayload,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    _rate_limit: None = Depends(login_rate_limit),
):
    """Authenticate a user and return a JWT.

    Args:
        payload: Login data (email, password).
        user_repo: User repository port.
        hasher: Password hasher port.
        token_service: Token generation port.

    Returns:
        Dict with ``access_token`` and ``token_type``.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    try:
        return await login_user(
            user_repo, hasher, token_service, payload.email, payload.password
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/invitations", status_code=201)
async def create_invitation_endpoint(
    payload: CreateInvitationPayload,
    invitation_repo: Annotated[InvitationRepository, Depends(get_invitation_repo)],
    notification: Annotated[NotificationService, Depends(get_notification_service)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    admin: dict = Depends(require_permission(Operation.BOOK_CREATE)),
):
    """Create an invitation (admin only).

    Args:
        payload: Invitation data (email, role).
        invitation_repo: Invitation repository port.
        notification: Notification service port.
        user_repo: User repository port.
        admin: Current admin user claims from auth middleware.

    Returns:
        Invitation dict with token.

    Raises:
        HTTPException: 400 if role is invalid.
    """
    try:
        role = UserRole(payload.role)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {payload.role}. Must be 'admin' or 'user'.",
        ) from exc

    # Fetch admin user name for notification
    admin_user = await user_repo.find_by_id(admin["user_id"])
    inviter_name = admin_user.email if admin_user else "Admin"

    invitation = await create_invitation(
        invitation_repo,
        notification,
        inviter_id=admin["user_id"],
        inviter_name=inviter_name,
        email=payload.email,
        role=role,
    )
    return {
        "id": invitation.id,
        "token": invitation.token,
        "email": invitation.email,
        "role": invitation.role.value,
        "expires_at": invitation.expires_at.isoformat()
        if invitation.expires_at
        else None,
    }
