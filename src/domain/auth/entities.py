"""Auth domain entities: User, Invitation, UserRole."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class UserRole(StrEnum):
    """Role assigned to a user within the system.

    Attributes:
        ADMIN: Full access, can bypass ownership checks.
        USER: Standard access, ownership enforced at use-case layer.
    """

    ADMIN = "admin"
    USER = "user"


@dataclass(slots=True)
class User:
    """User entity in the auth domain.

    Attributes:
        id: Unique identifier (UUID hex).
        email: User email address.
        hashed_password: Bcrypt-hashed password.
        role: Role determining permission level.
        is_active: Whether the user account is active.
        created_at: Timestamp of account creation.
    """

    id: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Invitation:
    """Invitation entity for onboarding new users.

    Attributes:
        id: Unique identifier (UUID hex).
        token: UUID4 invitation token.
        email: Invitee email address.
        role: Role the invitee will receive upon acceptance.
        inviter_id: User ID of the admin who created the invitation.
        created_at: Timestamp of invitation creation.
        expires_at: Expiration timestamp (created_at + 7 days typical).
        used_at: Timestamp when consumed; None means unused.
    """

    id: str
    token: str
    email: str
    role: UserRole
    inviter_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    used_at: datetime | None = None
