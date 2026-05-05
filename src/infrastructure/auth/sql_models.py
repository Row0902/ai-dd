"""SQLModel table definitions for auth persistence.

``UserModel`` and ``InvitationModel`` are plain SQLModel data classes —
NOT domain entities.  They mirror the column structure of the ``users``
and ``invitations`` tables and are mapped to/from domain entities via
inline conversion in the repository implementations.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel table for users.

    Attributes:
        id: Primary key (UUID hex string).
        email: User email address (unique, indexed).
        hashed_password: Bcrypt-hashed password.
        role: Role string (``"user"`` or ``"admin"``).
        is_active: Whether the account is active.
        created_at: Account creation timestamp.
    """

    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InvitationModel(SQLModel, table=True):  # type: ignore[call-arg]
    """SQLModel table for invitations.

    Attributes:
        id: Primary key (UUID hex string).
        token: UUID4 invitation token (unique, indexed).
        email: Invitee email address.
        role: Role string the invitee will receive.
        inviter_id: User ID of the admin who created the invitation.
        created_at: Invitation creation timestamp.
        expires_at: Expiration timestamp.
        used_at: When consumed; None means unused.
    """

    __tablename__ = "invitations"

    id: str = Field(primary_key=True)
    token: str = Field(index=True, unique=True)
    email: str
    role: str
    inviter_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    used_at: datetime | None = Field(default=None)
