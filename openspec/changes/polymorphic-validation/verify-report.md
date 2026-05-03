# Verification Report — PR 2: Integration Layer

**Change**: `polymorphic-validation`
**Version**: PR 2 only — Integration layer (use cases, schemas, repository, router)
**Mode**: Strict TDD
**Date**: 2026-05-03
**Verifier**: sdd-verify

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 7 |
| Tasks complete | 7 |
| Tasks incomplete | 0 |

All PR 2 tasks are marked complete in the apply-progress artifact:
- ✅ 2.1 Add `validator` param to `create_book`, `update_book`, `replace_book`; call `.validate()` before repo, raise `DomainError` on failure
- ✅ 2.2 Add `@field_validator` to `BookPayload` in `schemas.py` — reject empty/whitespace name, malformed URL
- ✅ 2.3 Catch `DomainError` in app (`main.py`) → HTTP 422 with structured detail
- ✅ 2.4 Modify `_dict_to_book` in `json_book_repository.py` to raise `DomainError` on malformed data
- ✅ 2.5 Extend `test_book_use_cases.py` — 9 new tests for validator injection
- ✅ 2.6 Create `test_schemas.py` — 7 Pydantic validation tests
- ✅ 2.7 Full pytest: 117/117 passing, ruff clean, ty clean

---

## Build & Tests Execution

**Build**: ✅ Passed
```
ruff check src/ → All checks passed!
ruff format --check src/ → 40 files already formatted
ty check src/ → All checks passed!
```

**Tests**: ✅ 117 passed / ❌ 0 failed / ⚠️ 0 skipped
```
src/test/integration/test_books_api.py ..........
src/test/unit/test_book_use_cases.py ...................
src/test/unit/test_composite_validator.py ....
src/test/unit/test_domain_entities.py ................
src/test/unit/test_exceptions.py ..........
src/test/unit/test_json_book_repository.py .............
src/test/unit/test_schemas.py .......
src/test/unit/test_validators.py .............
src/test/unit/test_value_objects.py .........................
```

**Coverage**: 98% total / PR-2 changed files below
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/application/use_cases/book_use_case.py` | 100% | — | — | ✅ Excellent |
| `src/api/schemas.py` | 100% | — | — | ✅ Excellent |
| `src/api/routers/books.py` | 92% | — | L88, L98, L102 | ✅ Excellent |
| `src/main.py` | 75% | — | L33-37, L42, L51-53 | ⚠️ Acceptable |
| `src/infrastructure/json_book_repository.py` | 99% | — | L92 | ✅ Excellent |

**Average changed file coverage**: 93%

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found TDD Cycle Evidence table in apply-progress |
| All tasks have tests | ✅ | 4/4 task groups have test files |
| RED confirmed (tests exist) | ✅ | `test_book_use_cases.py`, `test_schemas.py`, `test_books_api.py`, `test_json_book_repository.py` all exist |
| GREEN confirmed (tests pass) | ✅ | All 117 tests pass on execution |
| Triangulation adequate | ✅ | 9 use-case cases (3 per use case × pass/fail/none), 7 schema cases, 4 integration cases, 6 repo cases |
| Safety Net for modified files | ✅ | 91/91, 100/100, 100/100 safety nets reported and verified |

**TDD Compliance**: 6/6 checks passed

---

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 107 | 8 | pytest |
| Integration | 10 | 1 | pytest + FastAPI TestClient |
| E2E | 0 | 0 | — |
| **Total** | **117** | **9** | |

PR 2 new tests: 26 (9 use-case + 7 schema + 6 repo + 4 integration)

---

## Changed File Coverage

| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/application/use_cases/book_use_case.py` | 100% | — | — | ✅ Excellent |
| `src/api/schemas.py` | 100% | — | — | ✅ Excellent |
| `src/api/routers/books.py` | 92% | — | L88, L98, L102 | ✅ Excellent |
| `src/main.py` | 75% | — | L33-37, L42, L51-53 | ⚠️ Acceptable |
| `src/infrastructure/json_book_repository.py` | 99% | — | L92 | ✅ Excellent |

**Average changed file coverage**: 93%

---

## Assertion Quality

**Assertion quality**: ✅ All assertions verify real behavior

Scan of all new and modified test files found no tautologies, ghost loops, smoke-test-only patterns, or mock-heavy tests. All assertions verify concrete behavior (status codes, field values, exception types, repository state).

---

## Quality Metrics

**Linter**: ✅ No errors / ✅ No warnings (ruff)
**Type Checker**: ✅ No errors (ty)

---

## Spec Compliance Matrix

### PR 2 Scope: Integration Layer

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Use Case Integration | Validator[Book] injected into create_book/update_book/replace_book | `test_book_use_cases.py::TestBookUseCasesWithValidator` (all 9 tests) | ✅ COMPLIANT |
| Use Case Integration | validator=None preserves existing behavior | `test_book_use_cases.py::test_create_book_with_validator_none_preserves_behavior` + all original tests pass unchanged | ✅ COMPLIANT |
| Use Case Integration | validator.validate() called before persistence | `test_book_use_cases.py::test_create_book_with_failing_validator_raises_domain_error` (repo empty after failure) | ✅ COMPLIANT |
| Use Case Integration | DomainError raised on validation failure | `test_book_use_cases.py::test_create_book_with_failing_validator_raises_domain_error` | ✅ COMPLIANT |
| Repository Contract | _dict_to_book raises DomainError on malformed data | `test_json_book_repository.py::TestDictToBook` (4 tests) | ✅ COMPLIANT |
| Pydantic HTTP Boundary | empty name rejected at HTTP layer (422) | `test_schemas.py::test_empty_name_rejected` + `test_books_api.py::test_post_empty_name_returns_422` | ✅ COMPLIANT |
| Pydantic HTTP Boundary | whitespace-only name rejected at HTTP layer (422) | `test_schemas.py::test_whitespace_only_name_rejected` + `test_books_api.py::test_post_whitespace_name_returns_422` | ✅ COMPLIANT |
| Pydantic HTTP Boundary | malformed URL rejected at HTTP layer (422) | `test_schemas.py::test_malformed_url_rejected` + `test_books_api.py::test_post_malformed_url_returns_422` | ✅ COMPLIANT |
| Pydantic HTTP Boundary | valid payload passes through | `test_schemas.py::test_valid_payload_accepted` + integration tests | ✅ COMPLIANT |

**Compliance summary**: 9/9 PR-2 scenarios compliant

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| `validator: Validator[Book] \| None = None` added to create_book | ✅ Implemented | `book_use_case.py` L56-65 |
| `validator: Validator[Book] \| None = None` added to update_book | ✅ Implemented | `book_use_case.py` L98-108 |
| `validator: Validator[Book] \| None = None` added to replace_book | ✅ Implemented | `book_use_case.py` L147-157 |
| `_validate_or_raise` helper validates before persistence | ✅ Implemented | `book_use_case.py` L205-219; called before all repo operations |
| `@field_validator("name")` rejects empty/whitespace | ✅ Implemented | `schemas.py` L19-25 |
| `@field_validator("url")` rejects malformed URLs | ✅ Implemented | `schemas.py` L27-36 |
| Exception handler returns HTTP 422 with structured detail | ✅ Implemented | `main.py` L30-37 returns `{"detail": [{"field", "message"}]}` |
| `_dict_to_book` raises DomainError on malformed data | ✅ Implemented | `json_book_repository.py` L145-175; raises for missing/invalid id and name |
| `_load_books_unlocked` catches DomainError and logs | ✅ Implemented | `json_book_repository.py` L109-118; graceful degradation for corrupt JSON entries |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Validator injection via optional param `validator: Validator[Book] \| None = None` | ✅ Yes | Implemented exactly as designed |
| Flat composite used (no nesting) | ✅ Yes | `CompositeValidator` iterates flat list; `_validate_or_raise` uses single validator or composite |
| DomainError raised (not ValidationError directly) | ✅ Yes | `_validate_or_raise` raises `errors[0]` which is a `ValidationError` subclass of `DomainError` |
| HTTP 422 response format: `{"detail": [{"field": "...", "message": "..."}]}` | ✅ Yes | `main.py` exception handler produces exactly this shape |
| Exception handler on FastAPI app (not APIRouter) | ⚠️ Deviated | Design File Changes table says router catches error, but FastAPI requires app-level handlers. Apply-progress documents this as a known framework constraint. Functionally equivalent. |
| `_validate_or_raise` raises first error only | ⚠️ Deviated | Design code example shows `raise ValidationError(fields=errors)` as an option; implementation raises `errors[0]` only. Spec says "raises DomainError with validation errors" (plural). This limits error reporting to the first failure. |

**Design compliance**: 4/6 followed, 2 minor deviations (both functionally acceptable)

---

## Backward Compatibility

| Check | Result | Details |
|-------|--------|---------|
| Existing tests pass without modification | ✅ Yes | All original tests from PR 1 still pass (117/117 total) |
| validator=None (default) has zero behavioral change | ✅ Yes | `_validate_or_raise` returns early when `validator is None`; all existing use-case tests pass unchanged |
| Router does not pass validator — defaults to None | ✅ Yes | `books.py` endpoints call use cases without `validator` kwarg, preserving pre-PR-2 behavior |
| Pydantic validators only added to `BookPayload` — no endpoint signature changes | ✅ Yes | Endpoints continue to accept same payload shape; validation is additive |

---

## Size / SRP Compliance

| Check | Result | Details |
|-------|--------|---------|
| All methods ≤ 20 lines | ✅ Yes | Longest method: `replace_book` at 12 executable lines; `_validate_or_raise` at 5 lines; all endpoint handlers ≤ 10 lines |
| All files under 500 lines | ✅ Yes | Largest changed file: `book_use_case.py` at 219 lines; `json_book_repository.py` at 186 lines; `books.py` at 103 lines |

---

## Issues Found

### CRITICAL (must fix before archive):
None.

### WARNING (should fix):
1. **`_validate_or_raise` raises only the first error, not all aggregated errors**
   - **Location**: `src/application/use_cases/book_use_case.py` L218-219
   - **Details**: `raise errors[0]` discards subsequent validation errors. The spec says "raises DomainError with validation errors" (plural), suggesting all errors should be reported. This limits the usefulness of `CompositeValidator` — users only see the first failure even when multiple fields are invalid.
   - **Impact**: When using `CompositeValidator`, only the first validator's error is raised. The remaining errors are silently dropped.
   - **Fix**: Aggregate errors into a single exception or introduce a `ValidationErrors` container exception that carries the full list.

2. **Exception handler located in `main.py` instead of `books.py` router**
   - **Location**: `src/main.py` L30-37
   - **Details**: Design File Changes table specifies `src/api/routers/books.py` should catch `ValidationError → 422`. The handler is instead on the FastAPI app instance in `main.py`.
   - **Impact**: Functionally equivalent — all routes benefit from the handler. But it deviates from the design's file-change plan.
   - **Note**: Apply-progress documents this as a known FastAPI constraint (`APIRouter` cannot register exception handlers; only `FastAPI` app can).

### SUGGESTION (nice to have):
1. **Router could wire a default `CompositeValidator` into use cases**
   - Currently the router never passes a validator, so domain validation is bypassed at the HTTP layer (only Pydantic validation runs). Wiring a default `CompositeValidator` would enable full domain validation for all HTTP requests without requiring callers to change.
   - This is likely deferred to a future PR or left as an opt-in for direct use-case consumers.

2. **`main.py` exception handler branch for non-ValidationError DomainError is uncovered**
   - Line 35-36 (`detail = [{"field": "unknown", "message": str(exc)}]`) is never exercised by tests. Adding a test for a plain `DomainError` (non-ValidationError subclass) would bring coverage to 100%.

3. **Router endpoint `update_book` is missing from the router**
   - The `books.py` router only has `POST`, `PUT`, `GET`, `DELETE`. There is no `PATCH` endpoint for `update_book` (partial update). This is pre-existing and not changed by PR 2, but means the `update_book` use case with validator is only testable via unit tests, not integration tests.

---

## Verdict

**PASS WITH WARNINGS**

PR 2 implementation is behaviorally correct, all 117 tests pass, TDD discipline was followed, and all spec scenarios within PR 2 scope are compliant. Backward compatibility is fully preserved — existing tests pass without modification and `validator=None` has zero behavioral change.

Two WARNINGS are raised:
1. `_validate_or_raise` raises only the first validation error, limiting `CompositeValidator` usefulness. This deviates from the spec's plural "validation errors" wording.
2. Exception handler location deviates from the design's File Changes table (app-level vs router-level), though this is a documented FastAPI constraint.

Neither warning blocks archive, but warning #1 should be addressed in PR 3 or a follow-up if full composite error aggregation is desired.

---

## Files Examined

### Source (PR 2 changed)
- `src/application/use_cases/book_use_case.py` (219 lines, modified)
- `src/api/schemas.py` (36 lines, modified)
- `src/api/routers/books.py` (103 lines, modified)
- `src/main.py` (53 lines, modified)
- `src/infrastructure/json_book_repository.py` (186 lines, modified)

### Source (PR 1 — referenced for context)
- `src/domain/exceptions.py` (38 lines)
- `src/domain/validators/protocol.py` (29 lines)
- `src/domain/validators/composite.py` (39 lines)
- `src/domain/validators/book_name.py` (24 lines)
- `src/domain/validators/book_author.py` (21 lines)
- `src/domain/validators/book_url.py` (26 lines)
- `src/domain/entities.py` (74 lines)

### Tests (PR 2 changed/new)
- `src/test/unit/test_book_use_cases.py` (286 lines, modified — 9 new tests)
- `src/test/unit/test_schemas.py` (61 lines, created — 7 tests)
- `src/test/unit/test_json_book_repository.py` (123 lines, modified — 6 new tests)
- `src/test/integration/test_books_api.py` (138 lines, modified — 4 new tests)
