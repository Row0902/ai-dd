"""Unit tests for auth permission mapping."""

from domain.auth.entities import UserRole
from domain.auth.permissions import ROLE_PERMISSIONS, Operation


class TestOperation:
    """Test Operation enum values."""

    def test_book_create_value(self) -> None:
        """BOOK_CREATE has correct string value."""
        assert Operation.BOOK_CREATE.value == "book:create"

    def test_book_read_value(self) -> None:
        """BOOK_READ has correct string value."""
        assert Operation.BOOK_READ.value == "book:read"

    def test_book_update_value(self) -> None:
        """BOOK_UPDATE has correct string value."""
        assert Operation.BOOK_UPDATE.value == "book:update"

    def test_book_delete_value(self) -> None:
        """BOOK_DELETE has correct string value."""
        assert Operation.BOOK_DELETE.value == "book:delete"

    def test_collection_create_value(self) -> None:
        """COLLECTION_CREATE has correct string value."""
        assert Operation.COLLECTION_CREATE.value == "collection:create"

    def test_collection_read_value(self) -> None:
        """COLLECTION_READ has correct string value."""
        assert Operation.COLLECTION_READ.value == "collection:read"

    def test_collection_update_value(self) -> None:
        """COLLECTION_UPDATE has correct string value."""
        assert Operation.COLLECTION_UPDATE.value == "collection:update"

    def test_collection_delete_value(self) -> None:
        """COLLECTION_DELETE has correct string value."""
        assert Operation.COLLECTION_DELETE.value == "collection:delete"

    def test_favorite_add_value(self) -> None:
        """FAVORITE_ADD has correct string value."""
        assert Operation.FAVORITE_ADD.value == "favorite:add"

    def test_favorite_remove_value(self) -> None:
        """FAVORITE_REMOVE has correct string value."""
        assert Operation.FAVORITE_REMOVE.value == "favorite:remove"


class TestRolePermissions:
    """Test ROLE_PERMISSIONS mapping completeness."""

    def test_admin_has_all_operations(self) -> None:
        """ADMIN role has permission for every Operation."""
        admin_perms = ROLE_PERMISSIONS[UserRole.ADMIN]
        assert admin_perms == set(Operation)

    def test_user_has_all_operations(self) -> None:
        """USER role has permission for every Operation (ownership enforced at use-case layer)."""
        user_perms = ROLE_PERMISSIONS[UserRole.USER]
        assert user_perms == set(Operation)

    def test_all_roles_in_mapping(self) -> None:
        """Every UserRole has an entry in ROLE_PERMISSIONS."""
        for role in UserRole:
            assert role in ROLE_PERMISSIONS

    def test_operation_is_str_enum(self) -> None:
        """Operation members are also strings."""
        assert isinstance(Operation.BOOK_CREATE, str)
        assert isinstance(Operation.BOOK_READ, str)
