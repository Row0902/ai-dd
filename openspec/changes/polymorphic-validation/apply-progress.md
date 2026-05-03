# Apply Progress: Polymorphic Validation

## PR 1: Domain Infrastructure — COMPLETE ✅

**91/91 tests passing**, ruff check + format clean, ty check clean.

### Completed Tasks

- [x] 1.1 `src/domain/exceptions.py` — DomainError + ValidationError (eq=True, documented constraint)
- [x] 1.2 `src/domain/validators/__init__.py` + `protocol.py` — Validator[T] ABC
- [x] 1.3 `book_name.py`, `book_author.py`, `book_url.py` — 3 concrete validators
- [x] 1.4 `composite.py` — CompositeValidator flat aggregation
- [x] 1.5 `src/domain/value_objects/` — BookName, BookAuthor, BookUrl (frozen dataclasses)
- [x] 1.6 `entities.py` — Book stores VOs internally, exposes strings via @property
- [x] 1.7 `test_validators.py` — 17 tests (protocol, validators, composite, spy)
- [x] 1.8 `test_value_objects.py` — 25 tests (construction, equality, hash, immutability)
- [x] 1.9 Composite tests included in test_validators.py
- [x] 1.10 Full suite: 91 tests passing

### Verification Warnings Fixed

1. **`Book.__post_init__` exceeded 20 lines** → Replaced with custom `__init__` (8 lines) + `@property` accessors (3 lines each).
2. **`ValidationError` not frozen** → Documented as PERMANENT CONSTRAINT. Python 3.14+ frozen dataclasses conflict with `Exception.__traceback__`.
3. **Book stored strings instead of VOs** → Now stores `_name: BookName`, `_author: BookAuthor | None`, `_url: BookUrl | None` internally.

### Files Created (PR 1)

| File | Description |
|------|-------------|
| `src/domain/exceptions.py` | DomainError, ValidationError |
| `src/domain/validators/__init__.py` | Package init |
| `src/domain/validators/protocol.py` | Validator[T] ABC |
| `src/domain/validators/book_name.py` | BookNameValidator |
| `src/domain/validators/book_author.py` | BookAuthorValidator |
| `src/domain/validators/book_url.py` | BookUrlValidator |
| `src/domain/validators/composite.py` | CompositeValidator |
| `src/domain/value_objects/__init__.py` | Package init |
| `src/domain/value_objects/book_name.py` | BookName VO |
| `src/domain/value_objects/book_author.py` | BookAuthor VO |
| `src/domain/value_objects/book_url.py` | BookUrl VO |
| `src/test/unit/test_exceptions.py` | 10 tests |
| `src/test/unit/test_validators.py` | 17 tests |
| `src/test/unit/test_value_objects.py` | 25 tests |

### Files Modified (PR 1)

| File | Change |
|------|--------|
| `src/domain/entities.py` | VO composition + @property accessors |
| `src/test/unit/test_domain_entities.py` | Validation tests preserved (11) |
| `src/test/unit/test_book_use_cases.py` | Fixed InMemoryBookRepository |

---

## PR 2: Integration Layer — COMPLETE ✅

**117/117 tests passing**, ruff check + format clean, ty check clean.

### TDD Cycle Evidence

| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 2.1+2.5 | `test_book_use_cases.py` | Unit | ✅ 91/91 | ✅ 9 fail | ✅ 19/19 | ✅ 3 cases/use case | ✅ Clean |
| 2.2+2.6 | `test_schemas.py` | Unit | N/A (new) | ✅ 3 fail | ✅ 7/7 | ✅ 7 cases | ✅ Clean |
| 2.3 | `test_books_api.py` | Integration | ✅ 100/100 | ✅ 4 fail | ✅ 10/10 | ✅ 4 cases | ✅ Clean |
| 2.4 | `test_json_book_repository.py` | Unit | ✅ 100/100 | ✅ 4 fail | ✅ 13/13 | ✅ 6 cases | ✅ Clean |

### Completed Tasks

- [x] 2.1 `create_book`, `update_book`, `replace_book` — added `validator: Validator[Book] | None = None` param; `_validate_or_raise` helper calls `.validate()` before repo, raises first error
- [x] 2.2 `schemas.py` — `@field_validator` for name (non-empty/whitespace) and url (valid format via urlparse)
- [x] 2.3 `main.py` — `DomainError` exception handler → HTTP 422 `{"detail": [{"field","message"}]}`
- [x] 2.4 `json_book_repository.py` — `_dict_to_book` raises `DomainError` on malformed data; `_load_books_unlocked` catches and logs
- [x] 2.5 `test_book_use_cases.py` — 9 new tests: `_PassValidator`, `_FailValidator` mocks for create/update/replace
- [x] 2.6 `test_schemas.py` — 7 tests: empty name, whitespace name, malformed URL, valid data, defaults
- [x] 2.7 Full suite: 117/117 passing

### Files Changed (PR 2)

| File | Action | What Changed |
|------|--------|-------------|
| `src/application/use_cases/book_use_case.py` | Modified | `validator` param + `_validate_or_raise` helper |
| `src/api/schemas.py` | Modified | `@field_validator` for name + url |
| `src/main.py` | Modified | `DomainError` exception handler |
| `src/infrastructure/json_book_repository.py` | Modified | `_dict_to_book` raises DomainError; `_load_books_unlocked` catches |
| `src/test/unit/test_book_use_cases.py` | Modified | 9 validator injection tests |
| `src/test/unit/test_schemas.py` | Created | 7 Pydantic validation tests |
| `src/test/unit/test_json_book_repository.py` | Modified | 6 `_dict_to_book` tests |
| `src/test/integration/test_books_api.py` | Modified | 4 HTTP 422 boundary tests |

### Key Design Decisions

1. **`_validate_or_raise` raises first error** — keeps error semantics simple; single-field validation is sufficient for the current use cases.
2. **Exception handler on `FastAPI` app** — `APIRouter` doesn't support `exception_handler`; must be on the app instance.
3. **`_dict_to_book` raises, `_load_books_unlocked` catches** — preserves graceful degradation for malformed JSON files while making the error explicit.

---

## PR 3: SRP Split — PENDING
