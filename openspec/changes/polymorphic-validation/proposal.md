# Proposal: Polymorphic Validation + SRP File Constraints

## Intent

The app has ZERO validation across all layers — no `__post_init__`, no Pydantic validators, no domain guards. Users can create books with empty names, junk URLs, and malformed data. Additionally, `book_use_case.py` (180 lines) violates SRP by bundling 7 use cases, and `JsonBookRepository` (167 lines) mixes I/O, serialization, threading, and CRUD. Add polymorphic validation infrastructure and enforce file-per-class/function rules with size budgets (files 200-300 L, classes 3-10 public methods).

## Scope

### In Scope
- Validator Protocol (`Validator[T]`) with concrete validators (name, author, url), one per file
- `CompositeValidator` for composing validators; `DomainError` base + `ValidationError` dataclass
- Pydantic validators in `BookPayload` (HTTP layer first defense)
- Value Objects (`BookName`, `BookAuthor`, `BookUrl`) with self-validation in `__init__`
- Integrate validators into `create_book`/`update_book`/`replace_book` use cases
- `JsonBookRepository` rejects invalid data with `DomainError` instead of silent coercion
- Split `book_use_case.py` → one file per use case; extract `JsonSerializer` from repository
- Unit tests for every validator, value object, and use case

### Out of Scope
- ORM/database migration (JSON repo stays)
- Authentication/authorization
- API input sanitization beyond Pydantic
- Composite decorator alternative (keep flat list, no nesting)

## Capabilities

### New Capabilities
- `polymorphic-validation`: Validator Protocol, concrete validators, composite, `DomainError`/`ValidationError` types, integration points in use cases and repository
- `value-objects`: `BookName`, `BookAuthor`, `BookUrl` value objects with self-validation and immutability

### Modified Capabilities
- None (no existing specs)

## Approach

Incremental, phased based on exploration recommendation:

1. **Infrastructure**: `src/domain/exceptions.py` + `src/domain/validators/` (protocol, composite, 3 concrete validators). Each validator file ~30 lines, 1 class, 1 `validate` method.
2. **Value Objects**: `src/domain/value_objects/` — 3 files, self-validating in `__init__`, immutable. `Book` composes them.
3. **Integration**: Inject `Validator[Book]` into create/update/replace. Add Pydantic validators in `BookPayload`. Repository raises `DomainError`.
4. **SRP Split**: `book_use_case.py` → 6 files under `use_cases/`. `JsonSerializer` extracted from repository.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/domain/exceptions.py` | New | `DomainError`, `ValidationError` |
| `src/domain/validators/` | New | Protocol + 4 concrete files (~120 total lines) |
| `src/domain/value_objects/` | New | 3 VO files (~90 total lines) |
| `src/domain/entities.py` | Modified | `__post_init__`, compose VOs |
| `src/application/use_cases/` | Refactored | 1→6 files, validator injection |
| `src/api/schemas.py` | Modified | Add Pydantic validators |
| `src/infrastructure/json_book_repository.py` | Modified | Raise `DomainError`, extract serializer |
| `src/test/unit/` | New tests | ~500 lines, 1 file per source file |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Over-engineering for simple CRUD | Medium | Only 3 business rules; keep validators minimal (~12 lines each) |
| Breaks existing tests | High | Add validation as opt-in parameter first, then make mandatory |
| File-per-class produces tiny files (<10 lines) | Low | Merge related classes if <5 methods; guide, not dogma |
| Composite debugging complexity | Low | Flat list only; no nested composites |

## Rollback Plan

- Remove `src/domain/validators/` and `src/domain/value_objects/`
- Revert use cases to accept raw strings (remove `Validator` parameter)
- Revert `Book` to plain dataclass without `__post_init__`
- Restore original `book_use_case.py` (single file) from git

## Dependencies

- None (no external libraries; Python 3.12+ stdlib + Pydantic already in stack)

## Success Criteria

- [ ] Every `create_book`/`update_book`/`replace_book` call validates before persistence
- [ ] `BookPayload` rejects empty name via Pydantic validators
- [ ] `JsonBookRepository` raises `DomainError` (not `None`) on invalid data
- [ ] Each validator in its own file, ≤30 lines, 1 public method
- [ ] Each use case in its own file, ≤80 lines
- [ ] All existing + new tests pass; new coverage ≥90%

## Review Workload Forecast

- **Estimated additions**: ~450 lines code + ~500 lines tests = ~950 total new
- **Estimated deletions**: ~30 lines (extracted from existing files)
- **Total changed lines**: ~980
- **Decision needed before apply**: Yes
- **Chained PRs recommended**: Yes (3 PRs)
- **400-line budget risk**: High

### Chained PR Plan

| PR | Scope | Est. lines |
|----|-------|------------|
| 1 | Domain infra: exceptions + validators + value objects | ~350 |
| 2 | Integration: use cases + schemas + repository | ~350 |
| 3 | SRP split: file-per-use-case + serializer extraction | ~280 |
