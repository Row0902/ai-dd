"""Unit tests for auth domain entities."""

from datetime import UTC, datetime

from domain.auth.entities import Invitation, User, UserRole


class TestUserRole:
    """Test UserRole enum values."""

    def test_admin_value(self) -> None:
        """ADMIN enum has string value 'admin'."""
        assert UserRole.ADMIN.value == "admin"

    def test_user_value(self) -> None:
        """USER enum has string value 'user'."""
        assert UserRole.USER.value == "user"

    def test_user_role_is_str_enum(self) -> None:
        """UserRole members are also strings."""
        assert isinstance(UserRole.ADMIN, str)
        assert isinstance(UserRole.USER, str)


class TestUser:
    """Test User dataclass construction and defaults."""

    def test_user_creation_with_all_fields(self) -> None:
        """User can be constructed with all fields specified."""
        now = datetime.now(UTC)
        user = User(
            id="u1",
            email="test@example.com",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            is_active=False,
            created_at=now,
        )
        assert user.id == "u1"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed"
        assert user.role == UserRole.ADMIN
        assert user.is_active is False
        assert user.created_at is now

    def test_user_default_role_is_user(self) -> None:
        """User defaults to USER role when not specified."""
        user = User(id="u1", email="a@b.com", hashed_password="h")
        assert user.role == UserRole.USER

    def test_user_default_is_active_is_true(self) -> None:
        """User defaults to is_active=True when not specified."""
        user = User(id="u1", email="a@b.com", hashed_password="h")
        assert user.is_active is True

    def test_user_default_created_at_is_set(self) -> None:
        """User gets a created_at timestamp by default."""
        before = datetime.now(UTC)
        user = User(id="u1", email="a@b.com", hashed_password="h")
        after = datetime.now(UTC)
        assert before <= user.created_at <= after


class TestInvitation:
    """Test Invitation dataclass construction and defaults."""

    def test_invitation_creation_with_all_fields(self) -> None:
        """Invitation can be constructed with all fields specified."""
        now = datetime.now(UTC)
        expires = datetime.now(UTC)
        used = datetime.now(UTC)
        inv = Invitation(
            id="inv1",
            token="abc-123",
            email="invite@example.com",
            role=UserRole.ADMIN,
            inviter_id="admin1",
            created_at=now,
            expires_at=expires,
            used_at=used,
        )
        assert inv.id == "inv1"
        assert inv.token == "abc-123"
        assert inv.email == "invite@example.com"
        assert inv.role == UserRole.ADMIN
        assert inv.inviter_id == "admin1"
        assert inv.created_at is now
        assert inv.expires_at is expires
        assert inv.used_at is used

    def test_invitation_default_used_at_is_none(self) -> None:
        """Invitation defaults used_at to None (not yet consumed)."""
        inv = Invitation(
            id="inv1",
            token="abc",
            email="a@b.com",
            role=UserRole.USER,
            inviter_id="admin1",
        )
        assert inv.used_at is None

    def test_invitation_default_expires_at_is_none(self) -> None:
        """Invitation defaults expires_at to None."""
        inv = Invitation(
            id="inv1",
            token="abc",
            email="a@b.com",
            role=UserRole.USER,
            inviter_id="admin1",
        )
        assert inv.expires_at is None

    def test_invitation_default_created_at_is_set(self) -> None:
        """Invitation gets a created_at timestamp by default."""
        before = datetime.now(UTC)
        inv = Invitation(
            id="inv1",
            token="abc",
            email="a@b.com",
            role=UserRole.USER,
            inviter_id="admin1",
        )
        after = datetime.now(UTC)
        assert before <= inv.created_at <= after
