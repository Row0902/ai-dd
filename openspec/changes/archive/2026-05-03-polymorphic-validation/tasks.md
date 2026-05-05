# Tasks: Polymorphic Validation + Value Objects

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1235 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | auto-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High

### Work Units

| Unit | Goal | Likely PR | Lines |
|------|------|-----------|-------|
| 1 | Domain infra: exceptions, validators, VOs, entity | PR 1 | ~350 |
| 2 | Integration: use cases, schemas, repo, router | PR 2 | ~350 |
| 3 | SRP split: file-per-use-case, serializer extraction | PR 3 | ~280 |

## PR 1: Domain Infrastructure (~350 lines)

- [x] 1.1 [seq] Create `src/domain/exceptions.py` — `DomainError(Exception)`, `ValidationError(field, message)` frozen dataclass (~30)
- [x] 1.2 [seq] Create `src/domain/validators/__init__.py` + `protocol.py` — `Validator[T]` protocol with `validate(entity: T) -> list[ValidationError]` (~25)
- [x] 1.3 [par] Create `book_name.py`, `book_author.py`, `book_url.py` — one file per concrete validator, each <30 lines (~65)
- [x] 1.4 [seq] Create `composite.py` — `CompositeValidator[T]` with flat error list aggregation, no nesting (~30)
- [x] 1.5 [par] Create `src/domain/value_objects/` — `BookName`, `BookAuthor`, `BookUrl` frozen dataclasses with `__post_init__` validation (~85)
- [x] 1.6 [seq] Modify `entities.py` — `Book` uses VO types; keep backward compat via `__init__` accepting raw strings (~40)
- [x] 1.7 [par] Create `test_validators.py` — parametrized tests per validator × valid/invalid cases (~120)
- [x] 1.8 [par] Create `test_value_objects.py` — construction, equality, hash, immutability, raises (~80)
- [x] 1.9 [par] Create `test_composite_validator.py` — empty/one/multiple/mixed composite tests (~60)
- [x] 1.10 [seq] Run `pytest` — all new + existing tests pass (98/98 green)

## PR 2: Integration (~350 lines)

- [x] 2.1 [seq] Add `validator: Validator[Book] | None = None` to `create_book`, `update_book`, `replace_book`; call `.validate()` before repo, raise `DomainError` on failure (~100)
- [x] 2.2 [par] Add `@field_validator` to `BookPayload` in `schemas.py` — reject empty name/author+whitespace, malformed URL (~25)
- [x] 2.3 [seq] Catch `ValidationError` in `routers/books.py` → HTTP 422 with `{"detail": [{"field","message"}]}` (~30)
- [x] 2.4 [par] Modify `_dict_to_book` in `json_book_repository.py` to raise `DomainError` on malformed data instead of returning `None` (~50)
- [x] 2.5 [par] Extend `test_book_use_cases.py` — add test cases: `validator=None` (existing), `validator=mock_pass`, `validator=mock_fail` (~80)
- [x] 2.6 [par] Create `test_schemas.py` — Pydantic `BookPayload` rejects empty/malformed, accepts valid data (~40)
- [x] 2.7 [seq] Run `pytest` — all tests green, existing behavior preserved

## PR 3: SRP Split (~280 lines)

- [x] 3.1 [par] Split `book_use_case.py` into 7 files: `create_book.py`, `read_book.py`, `list_books.py`, `search_books.py`, `update_book.py`, `replace_book.py`, `delete_book.py` — pure refactoring, no behavior change (~120)
- [x] 3.2 [par] Extract `JsonSerializer` from `json_book_repository.py` into `src/infrastructure/serializers/json_book_serializer.py` with `book_to_dict`/`dict_to_book` functions (~100)
- [x] 3.3 [seq] Update imports in `routers/books.py` and `test_book_use_cases.py` to new module paths (~40)
- [x] 3.4 [seq] Run `pytest` — verify zero behavioral changes, all tests pass (118/118 green)
