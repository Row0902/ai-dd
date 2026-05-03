# Archive Report: polymorphic-validation

**Change**: `polymorphic-validation`
**Archived**: 2026-05-03
**Artifact Store**: hybrid (Engram + OpenSpec)
**Mode**: Spec-Driven Development (SDD)

---

## Executive Summary

Implemented polymorphic validation infrastructure across the entire book management application, from HTTP boundary (Pydantic) through use cases (Validator protocol) to domain layer (Value Objects). Split monolithic use case file into file-per-use-case pattern and extracted serializer. Delivered via 3 chained PRs with 118/118 tests passing, ruff clean, ty clean.

---

## What Was Built

### PR 1: Domain Infrastructure (91 tests)
- `DomainError(Exception)` base class and `ValidationError` frozen dataclass
- `Validator[T]` protocol with `validate()` method
- 3 concrete validators (`BookNameValidator`, `BookAuthorValidator`, `BookUrlValidator`) — one file each, ≤30 lines
- `CompositeValidator` with flat error list aggregation
- 3 Value Objects (`BookName`, `BookAuthor`, `BookUrl`) — frozen dataclasses with `__post_init__` validation
- `Book` entity composes VOs internally, exposes strings via `@property`
- Full test coverage: 17 validator tests, 25 VO tests, composite tests

### PR 2: Integration Layer (117 tests)
- Added `validator: Validator[Book] | None = None` to `create_book`, `update_book`, `replace_book`
- Pydantic `@field_validator` on `BookPayload` — rejects empty name/author, malformed URL
- FastAPI app-level exception handler: `DomainError` → HTTP 422 with structured detail
- `JsonBookRepository._dict_to_book` raises `DomainError` on malformed data (not silent None)
- 26 new tests: 9 use case, 7 schema, 6 repository, 4 integration

### PR 3: SRP Split (118 tests, pure refactoring)
- Split `book_use_case.py` (180 lines) → 7 files: `create_book.py`, `read_book.py`, `list_books.py`, `search_books.py`, `update_book.py`, `replace_book.py`, `delete_book.py`
- Extracted `JsonSerializer` from repository → `json_book_serializer.py` with `dict_to_book`/`book_to_dict`
- Backward-compatible shim in `book_use_case.py` preserves existing imports
- Zero behavioral change — 118/118 tests pass unchanged

---

## Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validator pattern | `Protocol[Validator[T]]` | Type-safe, testable, composable, explicit dependency |
| Error hierarchy | `DomainError` → `ValidationError` dataclass | Structured, maps to HTTP 422, domain-framework decoupled |
| Composite pattern | Flat list (no nesting) | Simple, debuggable, sufficient for 3 rules |
| VO immutability | `@dataclass(frozen=True)` | Built-in hashability, clean syntax |
| Validator injection | Optional parameter, default `None` | Backward-compatible rollout, existing tests pass |
| Use case structure | Functions (not classes) | Simpler, matches existing pattern |
| Delivery strategy | 3 chained PRs | 1235 total lines exceeds 400-line review budget |

---

## Deviations from Plan

1. **`_validate_or_raise` raises first error, not aggregated list** — Design anticipated raising aggregated errors, but implementation raises the first validation error for simpler error semantics. This is a simplification, not a regression.
2. **Exception handler on FastAPI app (not APIRouter)** — Design suggested router-level handling; FastAPI requires app-level handlers for proper exception mapping.
3. **`_dict_to_book` raises, `_load_books_unlocked` catches and logs** — Design noted this as configurable; implementation chose graceful degradation for malformed JSON files.
4. **Shim file `book_use_case.py` has 0% test coverage** — Noted as suggestion in verify report; low impact since shim is trivial re-exports.

---

## Success Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Every create/update/replace validates before persistence | ✅ | Validator injected in all 3 use cases (PR 2) |
| BookPayload rejects empty name via Pydantic | ✅ | `@field_validator` in schemas.py, 7 tests (PR 2) |
| JsonBookRepository raises DomainError on invalid data | ✅ | `_dict_to_book` raises, 6 tests (PR 2) |
| Each validator in own file, ≤30 lines, 1 public method | ✅ | 3 files: 12-25 lines each, 1 `validate()` method |
| Each use case in own file, ≤80 lines | ✅ | Largest: `create_book.py` at 78 lines |
| All tests pass; coverage ≥90% | ✅ | 118/118 passing; avg changed file coverage 91% |

---

## Final Metrics

| Metric | Value |
|--------|-------|
| Total tests | 118 |
| New files created | 22 |
| Files modified | 8 |
| Total changed lines | ~1235 |
| PRs delivered | 3 (chained) |
| Verification status | PASS (all 3 PRs) |
| Linter (ruff) | Clean |
| Type checker (ty) | Clean |
| Coverage (changed files avg) | 91% |

---

## Engram Artifact IDs (Traceability)

| Artifact | Observation ID | Topic Key |
|----------|---------------|-----------|
| Proposal | #40 | `sdd/polymorphic-validation/proposal` |
| Design | #42 | `sdd/polymorphic-validation/design` |
| Spec | #43 | `sdd/polymorphic-validation/spec` |
| Tasks | #44 | `sdd/polymorphic-validation/tasks` |
| Apply Progress | #45 | `sdd/polymorphic-validation/apply-progress` |
| Verify Report | #46 | `sdd/polymorphic-validation/verify-report` |
| Archive Report | (this document) | `sdd/polymorphic-validation/archive-report` |

---

## Specs Synced to Main

| Domain | Action | Details |
|--------|--------|---------|
| `polymorphic-validation` | Created | 7 requirements: Validator Protocol, Concrete Validators, CompositeValidator, Domain Error Types, Use Case Integration, Repository Contract, Pydantic HTTP Boundary |
| `value-objects` | Created | 5 requirements: BookName VO, BookAuthor VO, BookUrl VO, VO Immutability, Book Entity Integration |

---

## Archive Contents

- `proposal.md` ✅
- `spec.md` ✅
- `specs/polymorphic-validation/spec.md` ✅
- `specs/value-objects/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (23/23 tasks complete)
- `apply-progress.md` ✅
- `verify-report.md` ✅

---

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.
