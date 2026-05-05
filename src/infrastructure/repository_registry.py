"""Repository registry: maps URL schemes to repository classes.

Simple dict-based registry — no metaclass magic. Register concrete
repository classes for each supported ``DATABASE_URL`` scheme
(``memory``, ``sqlite``, ``postgresql``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.repositories import BookRepository

_REGISTRY: dict[str, type[BookRepository]] = {}


def register(scheme: str, cls: type[BookRepository]) -> None:
    """Register a repository class for a URL scheme.

    Args:
        scheme: The URL scheme (e.g., ``memory``, ``sqlite``, ``postgresql``).
        cls: The concrete repository class to instantiate for this scheme.
    """
    _REGISTRY[scheme] = cls


def resolve(scheme: str) -> type[BookRepository]:
    """Resolve a URL scheme to its registered repository class.

    Args:
        scheme: The URL scheme to look up.

    Returns:
        The registered repository class.

    Raises:
        ValueError: If no repository is registered for the scheme.
    """
    if scheme not in _REGISTRY:
        raise ValueError(f"Unsupported database scheme: {scheme}")
    return _REGISTRY[scheme]
