# Apply Progress — polymorphic-validation

## PR 1: Domain Infrastructure — COMPLETED ✅

### Tasks
- [x] 1.1 Create `src/domain/exceptions.py` — DomainError(Exception), ValidationError(field, message) dataclass
- [x] 1.2 Create `src/domain/validators/__init__.py` + `protocol.py` — Validator[T] ABC
- [x] 1.3 Create concrete validators (`book_name.py`, `book_author.py`, `book_url.py`)
- [x] 1.4 Create `composite.py` — CompositeValidator[T]
- [x] 1.5 Create Value Objects (`BookName`, `BookAuthor`, `BookUrl`)
- [x] 1.6 Modify `entities.py` — Book stores VOs internally, exposes strings via @property
- [x] 1.7 Tests for validators (test_validators.py, 17 tests)
- [x] 1.8 Tests for value objects (test_value_objects.py, 25 tests)
- [x] 1.9 Composite validator tests (included in test_validators.py)
- [x] 1.10 Full pytest: 91/91 passing
- [x] 1.11 ruff check + format: clean
- [x] 1.12 Persistence: Engram + OpenSpec updated

### Files Changed (PR 1)
| File | Action |
|------|--------|
| `src/domain/exceptions.py` | Created |
| `src/domain/validators/__init__.py` | Created |
| `src/domain/validators/protocol.py` | Created |
| `src/domain/validators/book_name.py` | Created |
| `src/domain/validators/book_author.py` | Created |
| `src/domain/validators/book_url.py` | Created |
| `src/domain/validators/composite.py` | Created |
| `src/domain/value_objects/__init__.py` | Created |
| `src/domain/value_objects/book_name.py` | Created |
| `src/domain/value_objects/book_author.py` | Created |
| `src/domain/value_objects/book_url.py` | Created |
| `src/domain/entities.py` | Modified |
| `src/test/unit/test_exceptions.py` | Created |
| `src/test/unit/test_validators.py` | Created |
| `src/test/unit/test_value_objects.py` | Created |
| `src/test/unit/test_domain_entities.py` | Modified |
| `src/test/unit/test_book_use_cases.py` | Modified |

## PR 2: Integration Layer — COMPLETED ✅

### Tasks
- [x] 2.1 Add `validator: Validator[Book] | None = None` to `create_book`, `update_book`, `replace_book` — calls `.validate()` before repo, raises DomainError on failure
- [x] 2.2 Add `@field_validator` to `BookPayload` in `schemas.py` — rejects empty/whitespace name, malformed URL
- [x] 2.3 Catch `DomainError` in app (main.py) → HTTP 422 with `{"detail": [{"field","message"}]}`
- [x] 2.4 Modify `_dict_to_book` in `json_book_repository.py` to raise `DomainError` on malformed data (not return None)
- [x] 2.5 Extend `test_book_use_cases.py` — 9 new tests: validator=None, mock_pass, mock_fail for create/update/replace
- [x] 2.6 Create `test_schemas.py` — 7 tests: Pydantic BookPayload rejects empty/malformed, accepts valid data
- [x] 2.7 Full pytest: 117/117 passing, ruff clean, ty clean

### TDD Cycle Evidence
| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 2.1+2.5 | `test_book_use_cases.py` | Unit | ✅ 91/91 | ✅ 9 fail | ✅ 19/19 | ✅ 3 cases per use case | ✅ Clean |
| 2.2+2.6 | `test_schemas.py` | Unit | N/A (new) | ✅ 3 fail | ✅ 7/7 | ✅ 7 cases total | ✅ Clean |
| 2.3 | `test_books_api.py` | Integration | ✅ 100/100 | ✅ 4 fail | ✅ 10/10 | ✅ 4 new cases | ✅ Clean |
| 2.4 | `test_json_book_repository.py` | Unit | ✅ 100/100 | ✅ 4 fail | ✅ 13/13 | ✅ 6 cases total | ✅ Clean |

### Files Changed (PR 2)
| File | Action | What Changed |
|------|--------|-------------|
| `src/application/use_cases/book_use_case.py` | Modified | Added `validator` param to create/update/replace; added `_validate_or_raise` helper |
| `src/api/schemas.py` | Modified | Added `@field_validator` for name (non-empty) and url (valid format) |
| `src/main.py` | Modified | Added `DomainError` exception handler → HTTP 422 with structured detail |
| `src/infrastructure/json_book_repository.py` | Modified | `_dict_to_book` raises `DomainError` on malformed data; `_load_books_unlocked` catches and logs |
| `src/test/unit/test_book_use_cases.py` | Modified | Added 9 validator injection tests + mock validators |
| `src/test/unit/test_schemas.py` | Created | 7 Pydantic validation tests |
| `src/test/unit/test_json_book_repository.py` | Modified | Added 6 `_dict_to_book` tests |
| `src/test/integration/test_books_api.py` | Modified | Added 4 HTTP 422 boundary tests |

### Key Design Decisions
- `_validate_or_raise`: raises first error (not aggregated list) — keeps error semantics simple
- Exception handler on `FastAPI` app (not `APIRouter`) — FastAPI requires app-level handlers
- `_dict_to_book` raises `DomainError`, `_load_books_unlocked` catches and logs — preserves graceful degradation for malformed JSON files

### Test Summary (PR 2)
- Total: 117 passing, 0 failing
- New tests: 26 (9 use case + 7 schema + 6 repo + 4 integration)
- Existing tests preserved: all 91 pass unchanged

## PR 3: SRP Split — COMPLETED ✅

### Tasks
- [x] 3.1 Split `book_use_case.py` into 7 per-use-case files under `src/application/use_cases/`
  - `create_book.py` — create_book + _validate_or_raise (shared helper)
  - `read_book.py` — get_book
  - `list_books.py` — list_books
  - `search_books.py` — get_books_by_name
  - `update_book.py` — update_book (imports _validate_or_raise from create_book)
  - `replace_book.py` — replace_book (imports _validate_or_raise from create_book)
  - `delete_book.py` — delete_book
  - `book_use_case.py` — converted to backward-compatible re-export shim
  - `__init__.py` — updated with public re-exports
- [x] 3.2 Extract serializer from `json_book_repository.py`
  - Created `src/infrastructure/serializers/__init__.py`
  - Created `src/infrastructure/serializers/json_book_serializer.py` with `dict_to_book` and `book_to_dict`
  - `JsonBookRepository._dict_to_book` and `_book_to_dict` now delegate to serializer (backward-compatible)
- [x] 3.3 Update imports in `routers/books.py` and `test_book_use_cases.py` to per-file imports
- [x] 3.4 Full pytest: 118/118 passing, ruff clean

### Files Changed (PR 3)
| File | Action | What Changed |
|------|--------|-------------|
| `src/application/use_cases/create_book.py` | Created | create_book + _validate_or_raise helper |
| `src/application/use_cases/read_book.py` | Created | get_book |
| `src/application/use_cases/list_books.py` | Created | list_books |
| `src/application/use_cases/search_books.py` | Created | get_books_by_name |
| `src/application/use_cases/update_book.py` | Created | update_book |
| `src/application/use_cases/replace_book.py` | Created | replace_book |
| `src/application/use_cases/delete_book.py` | Created | delete_book |
| `src/application/use_cases/__init__.py` | Modified | Added re-exports for all use case functions |
| `src/application/use_cases/book_use_case.py` | Modified | Converted to re-export shim (backward compat) |
| `src/infrastructure/serializers/__init__.py` | Created | Package init |
| `src/infrastructure/serializers/json_book_serializer.py` | Created | dict_to_book + book_to_dict functions |
| `src/infrastructure/json_book_repository.py` | Modified | Delegates to serializer; static methods kept for backward compat |
| `src/api/routers/books.py` | Modified | Imports from per-file modules instead of book_use_case |
| `src/test/unit/test_book_use_cases.py` | Modified | Imports from per-file modules instead of book_use_case |

### Test Summary (PR 3)
- Total: 118 passing, 0 failing
- Tests written: 0 (pure refactoring — zero behavioral change)
- All existing tests pass without modification (except import paths)
