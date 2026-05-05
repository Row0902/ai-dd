"""Auth permissions: role-to-operation mapping."""

from enum import StrEnum

from domain.auth.entities import UserRole


class Operation(StrEnum):
    """Discrete permission operations for resource access control.

    Attributes:
        BOOK_CREATE: Create new books.
        BOOK_READ: Read books.
        BOOK_UPDATE: Update existing books.
        BOOK_DELETE: Delete books.
        COLLECTION_CREATE: Create collections.
        COLLECTION_READ: Read collections.
        COLLECTION_UPDATE: Update collections.
        COLLECTION_DELETE: Delete collections.
        FAVORITE_ADD: Add books to favorites.
        FAVORITE_REMOVE: Remove books from favorites.
    """

    BOOK_CREATE = "book:create"
    BOOK_READ = "book:read"
    BOOK_UPDATE = "book:update"
    BOOK_DELETE = "book:delete"
    COLLECTION_CREATE = "collection:create"
    COLLECTION_READ = "collection:read"
    COLLECTION_UPDATE = "collection:update"
    COLLECTION_DELETE = "collection:delete"
    FAVORITE_ADD = "favorite:add"
    FAVORITE_REMOVE = "favorite:remove"


ROLE_PERMISSIONS: dict[UserRole, set[Operation]] = {
    UserRole.ADMIN: set(Operation),
    UserRole.USER: {
        Operation.BOOK_CREATE,
        Operation.BOOK_READ,
        Operation.BOOK_UPDATE,
        Operation.BOOK_DELETE,
        Operation.COLLECTION_CREATE,
        Operation.COLLECTION_READ,
        Operation.COLLECTION_UPDATE,
        Operation.COLLECTION_DELETE,
        Operation.FAVORITE_ADD,
        Operation.FAVORITE_REMOVE,
    },
}
