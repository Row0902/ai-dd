# Apply Progress: Polymorphic Validation — PR 1

## Status: COMPLETE (warnings fixed)

**91/91 tests passing**, ruff check + format clean, ty check clean.

## Completed Tasks

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
- [x] 1.11 ruff check + format: clean
- [x] 1.12 Persistence: Engram + OpenSpec updated

## Verification Warnings Fixed

1. **`Book.__post_init__` exceeded 20 lines** → Replaced with custom `__init__` (8 lines) + `@property` accessors (3 lines each). All methods well under 20-line limit.
2. **`ValidationError` not frozen** → Documented as PERMANENT CONSTRAINT in docstring. Python 3.14+ frozen dataclasses disallow `__setattr__`, conflicting with `Exception.__traceback__` at the C level. `eq=True` + manual `__hash__` achieves same value semantics.
3. **Book stored strings instead of VOs** → Now stores `_name: BookName`, `_author: BookAuthor | None`, `_url: BookUrl | None` internally. Public `@property` accessors return strings for backward compatibility.

## Files Created (14)

| File | Description |
|------|-------------|
| `src/domain/exceptions.py` | DomainError, ValidationError |
| `src/domain/validators/__init__.py` | Package init |
| `src/domain/validators/protocol.py` | Validator[T] ABC |
| `src/domain/validators/book_name.py` | BookNameValidator |
| `src/domain/validators/book_author.py` | BookAuthorValidator (optional-field aware) |
| `src/domain/validators/book_url.py` | BookUrlValidator |
| `src/domain/validators/composite.py` | CompositeValidator |
| `src/domain/value_objects/__init__.py` | Package init |
| `src/domain/value_objects/book_name.py` | BookName VO |
| `src/domain/value_objects/book_author.py` | BookAuthor VO |
| `src/domain/value_objects/book_url.py` | BookUrl VO |
| `src/test/unit/test_exceptions.py` | 10 tests |
| `src/test/unit/test_validators.py` | 17 tests (rewritten for VO-era) |
| `src/test/unit/test_value_objects.py` | 25 tests |

## Files Modified (4)

| File | Change |
|------|--------|
| `src/domain/entities.py` | VO composition + @property accessors |
| `src/test/unit/test_domain_entities.py` | Validation tests preserved (11) |
| `src/test/unit/test_book_use_cases.py` | Fixed InMemoryBookRepository (no more dataclasses.replace) |
| `src/test/integration/test_books_api.py` | Unchanged from earlier fix |

## Design Decisions

1. **ValidationError not frozen** — PERMANENT CONSTRAINT due to Python 3.14 Exception incompatibility.
2. **Book stores VOs, exposes strings** — Structural composition per spec, backward-compatible API via `@property`.
3. **Validators are VO-pass-through** — Since VOs validate eagerly at construction, field-level validators always see valid data. They remain for the Composite/Strategy pattern (PR 2 integration).
4. **InMemoryBookRepository no longer uses `dataclasses.replace()`** — Custom `__init__` with string parameters prevents replace. Constructs new Book instances from property values instead.
