# Design: Polymorphic Validation + SRP File Constraints

## Technical Approach

Layered validation: Pydantic at HTTP boundary, `Validator[Book]` protocol in use cases, `ValueObject` self-validation in domain. Error hierarchy rooted in `DomainError(Exception)`. Composite aggregator uses flat list (no nesting). Value Objects enforce immutability via `frozen=True` dataclass. Injection via optional `validator` parameter with `None` default — backward-compatible rollout.

## Architecture Decisions

### Decision: Validator Protocol vs plain functions vs decorators

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `Protocol[Validator[T]]` | Type-safe, testable, composable, explicit dependency | ✅ Chosen |
| Plain functions | Simpler, but no type parameter, harder to compose | Rejected |
| Decorators | Implicit, hard to test in isolation, couples to call site | Rejected |

**Rationale**: Protocol gives us `Validator[Book]` type annotation — use cases declare their validation dependency explicitly. Enables mock injection in tests. Matches the project's existing ABC pattern (`BookRepository`).

### Decision: Error hierarchy

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `DomainError(Exception)` → `ValidationError` dataclass | Structured, catchable at API layer, carries field+message | ✅ Chosen |
| String-based exceptions | Simple, but unstructured, hard to map to HTTP 422 | Rejected |
| Pydantic `ValidationError` in domain | Couples domain to framework | Rejected |

**Rationale**: `DomainError` is the domain's exception base. `ValidationError` is a dataclass with `field: str` and `message: str` — maps cleanly to HTTP 422 response bodies. API router catches `ValidationError` and returns structured JSON.

### Decision: Composite pattern — flat list, no nesting

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Flat list of validators | Simple, debuggable, linear aggregation | ✅ Chosen |
| Chain of Responsibility | Flexible but over-engineered for 3 rules | Rejected |
| Decorator nesting | Elegant but hard to debug, order-dependent | Rejected |

**Rationale**: Only 3 business rules (name required, author non-empty, url format). Flat list with `CompositeValidator` collecting all errors before raising is sufficient. No nesting needed.

### Decision: Value Object immutability strategy

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `@dataclass(frozen=True)` | Built-in, hashable, clean syntax | ✅ Chosen |
| `__slots__` + manual `__hash__` | More control, more boilerplate | Rejected |

**Rationale**: `frozen=True` gives immutability, auto-generated `__hash__` and `__eq__` for free. VOs validate in `__post_init__` — if invalid, raise `ValidationError` immediately.

### Decision: Validator injection strategy

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Optional `validator` parameter, default `None` | Backward-compatible, opt-in rollout | ✅ Chosen |
| Required `validator` parameter | Breaking change, forces all callers to update | Rejected |
| Constructor injection (class-based use cases) | Over-engineered for functional use cases | Rejected |

**Rationale**: Use cases are functions, not classes. Adding `validator: Validator[Book] | None = None` to `create_book`/`update_book`/`replace_book` keeps existing tests passing. When `None`, skip validation (Phase 1). When provided, validate before repo call (Phase 3).

## Data Flow

```
POST /books/
    │
    ▼
BookPayload (Pydantic)
    │  name: str (min_length=1)
    │  url: str (optional HttpUrl validator)
    ▼
create_book(repo, validator=book_validator, ...)
    │
    ▼
CompositeValidator.validate(book)
    │  ├─ BookNameValidator.validate(book)
    │  ├─ BookAuthorValidator.validate(book)
    │  └─ BookUrlValidator.validate(book)
    │
    ▼ (if errors)
raise ValidationError(fields=[...])
    │
    ▼ (API catches)
HTTP 422 { "detail": [{"field": "name", "message": "..."}] }
    │
    ▼ (no errors)
repo.create(book) → 201
```

Repository read path:
```
_load_books_unlocked()
    │
    ▼
_dict_to_book(item)
    │  malformed data → raise DomainError (not silent None)
    ▼
DomainError caught in _load_books → log + skip (or raise, configurable)
```

## File Changes

| File | Action | Est. Lines | Classes | Public Methods | Description |
|------|--------|------------|---------|----------------|-------------|
| `src/domain/exceptions.py` | Create | ~30 | 2 | 0 | `DomainError(Exception)`, `ValidationError` dataclass |
| `src/domain/validators/__init__.py` | Create | ~5 | 0 | 0 | Package init |
| `src/domain/validators/protocol.py` | Create | ~20 | 1 | 1 | `Validator[T]` Protocol with `validate()` |
| `src/domain/validators/composite.py` | Create | ~30 | 1 | 1 | `CompositeValidator` — flat list aggregator |
| `src/domain/validators/book_name.py` | Create | ~20 | 1 | 1 | `BookNameValidator` — non-empty name |
| `src/domain/validators/book_author.py` | Create | ~20 | 1 | 1 | `BookAuthorValidator` — non-empty author |
| `src/domain/validators/book_url.py` | Create | ~25 | 1 | 1 | `BookUrlValidator` — URL format check |
| `src/domain/value_objects/__init__.py` | Create | ~5 | 0 | 0 | Package init |
| `src/domain/value_objects/book_name.py` | Create | ~25 | 1 | 0 | `BookName` VO — frozen, validates non-empty |
| `src/domain/value_objects/book_author.py` | Create | ~25 | 1 | 0 | `BookAuthor` VO — frozen, validates non-empty |
| `src/domain/value_objects/book_url.py` | Create | ~30 | 1 | 0 | `BookUrl` VO — frozen, validates URL format |
| `src/domain/entities.py` | Modify | ~40 | 1 | 0 | Add `__post_init__` using VOs, keep backward compat |
| `src/application/use_cases/book_use_case.py` | Modify | ~200 | 0 | 7 | Add `validator` param to create/update/replace |
| `src/api/schemas.py` | Modify | ~25 | 1 | 0 | Add Pydantic validators (min_length, url check) |
| `src/api/routers/books.py` | Modify | ~110 | 0 | 6 | Catch `ValidationError` → 422 |
| `src/infrastructure/json_book_repository.py` | Modify | ~175 | 1 | 6 | `_dict_to_book` raises `DomainError` on malformed data |
| `src/test/unit/test_validators.py` | Create | ~120 | 4 | 12 | Unit tests for all validators |
| `src/test/unit/test_value_objects.py` | Create | ~80 | 3 | 9 | Unit tests for VOs (construction, equality, hash, immutability) |
| `src/test/unit/test_composite_validator.py` | Create | ~60 | 1 | 4 | Tests: empty, one, multiple, mixed results |
| `src/test/unit/test_book_use_cases.py` | Modify | ~180 | 2 | 12 | Add tests with mocked validator |

**Totals**: 12 new files (~645 lines), 5 modified files (~590 lines), ~1235 lines changed.

## Interfaces / Contracts

```python
# domain/exceptions.py
@dataclass(frozen=True)
class ValidationError(DomainError):
    field: str
    message: str

class DomainError(Exception):
    """Base exception for all domain-layer errors."""

# domain/validators/protocol.py
T = TypeVar("T")

class Validator(Protocol[T]):
    def validate(self, entity: T) -> list[ValidationError]: ...

# domain/validators/composite.py
class CompositeValidator(Generic[T]):
    def __init__(self, validators: list[Validator[T]]) -> None: ...
    def validate(self, entity: T) -> list[ValidationError]: ...
        # Returns aggregated errors from all validators (no short-circuit)

# Concrete validators (one per file)
class BookNameValidator:
    def validate(self, book: Book) -> list[ValidationError]:
        # Returns [ValidationError("name", "Name is required")] if empty

class BookAuthorValidator:
    def validate(self, book: Book) -> list[ValidationError]:
        # Returns [ValidationError("author", "Author is required")] if empty

class BookUrlValidator:
    def validate(self, book: Book) -> list[ValidationError]:
        # Returns [ValidationError("url", "Invalid URL format")] if non-empty and malformed

# domain/value_objects/book_name.py
@dataclass(frozen=True)
class BookName:
    value: str
    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValidationError(field="name", message="Name is required")

# Modified use case signature:
def create_book(
    repo: BookRepository,
    *,
    name: str,
    author: str = "",
    description: str = "",
    url: str = "",
    content: str = "",
    validator: Validator[Book] | None = None,  # NEW
) -> Book:
    draft = Book(id="", name=name, author=author, ...)
    if validator is not None:
        errors = validator.validate(draft)
        if errors:
            raise ValidationError(fields=errors)  # or first error
    return repo.create(draft)
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit — validators | Each validator: valid input → empty list, invalid → correct `ValidationError` | Parametrize with valid/invalid Book instances |
| Unit — CompositeValidator | Empty list, one validator, multiple validators, mixed pass/fail | Mock validators returning known errors |
| Unit — Value Objects | Construction, equality, hash, immutability (frozen), `__post_init__` raises on invalid | Direct instantiation + `pytest.raises` |
| Unit — use cases | `create_book` with validator=None (existing behavior), with validator that passes, with validator that fails (mock) | Extend existing `InMemoryBookRepository` pattern |
| Unit — repository | `_dict_to_book` raises `DomainError` on malformed data | Feed bad dicts directly |
| Integration — Pydantic | `BookPayload` rejects empty name, accepts valid data | Direct schema instantiation + `ValidationError` |

Existing tests: `test_book_use_cases.py` calls `create_book(repo, name=...)` without `validator` — these pass unchanged because default is `None`. New tests explicitly pass a validator.

## Migration / Rollout

**Phase 1 (PR 1) — Domain Infrastructure**: Create exceptions, validators, VOs. No integration. All existing tests pass unchanged.

**Phase 2 (PR 2) — Integration**: Add `validator` param to use cases (optional, default `None`). Add Pydantic validators to schemas. Modify `_dict_to_book` to raise `DomainError`. Catch `ValidationError` in router. Existing tests still pass.

**Phase 3 (PR 3) — SRP Split**: Split `book_use_case.py` into 6 files. Extract `JsonSerializer`. Pure refactoring — no behavior change.

Each phase is independently reversible via `git revert`. Branches: `feat/polymorphic-validation-infra`, `feat/polymorphic-validation-integration`, `refactor/use-case-srp-split`.

## Open Questions

- [ ] Should `ValidationError` carry a list of field errors or be one-per-field? (Design assumes one-per-field, composite aggregates)
- [ ] Should `_dict_to_book` raise on malformed data or log-and-skip? (Design assumes raise, configurable later)
- [ ] Should `BookUrlValidator` use `urllib.parse.urlparse` or a regex? (Design assumes `urlparse` — stdlib, no deps)
