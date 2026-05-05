"""Domain entities: pure business logic, no framework imports."""

from dataclasses import dataclass, field

from domain.value_objects.book_author import BookAuthor
from domain.value_objects.book_name import BookName
from domain.value_objects.book_url import BookUrl


@dataclass(slots=True)
class Book:
    """Book entity in the domain model.

    Composes ``BookName``, ``BookAuthor``, and ``BookUrl`` value objects
    internally for structural domain integrity.  Public access to ``name``,
    ``author``, and ``url`` returns plain strings — consumers see the same API
    but the entity guarantees validation at construction time.

    Attributes:
        id: Unique identifier (UUID hex).
        name: Validated book title (read-only string property).
        author: Validated author name, or ``""`` when unset.
        description: Extended book description.
        url: Validated reference URL, or ``""`` when unset.
        content: Book content or summary.
    """

    id: str
    _name: BookName = field(init=False)
    _author: BookAuthor | None = field(init=False, default=None)
    _url: BookUrl | None = field(init=False, default=None)
    description: str = ""
    content: str = ""

    def __init__(
        self,
        id: str,
        name: str = "",
        author: str = "",
        url: str = "",
        description: str = "",
        content: str = "",
    ) -> None:
        """Initialise a Book, constructing value objects from raw strings.

        Validation happens eagerly inside each value-object constructor.
        ``author`` and ``url`` are optional — empty strings produce ``None``
        internally.
        """
        self.id = id
        self._name = BookName(name)
        self._author = BookAuthor(author) if author else None
        self._url = BookUrl(url) if url else None
        self.description = description
        self.content = content

    # ------------------------------------------------------------------
    # Public string properties (backward-compatible API)
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the validated book title as a plain string."""
        return self._name.value

    @property
    def author(self) -> str:
        """Return the validated author name, or ``""`` when unset."""
        return self._author.value if self._author else ""

    @property
    def url(self) -> str:
        """Return the validated URL, or ``""`` when unset."""
        return self._url.value if self._url else ""
