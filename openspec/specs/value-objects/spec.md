# Delta for value-objects

## Purpose

Introduce three immutable value objects — `BookName`, `BookAuthor`, `BookUrl` — that encapsulate validation logic and replace raw string fields in the `Book` entity.

---

## ADDED Requirements

### Requirement: BookName Value Object

The system SHALL provide a `BookName` value object that wraps a string, validates on construction that it is non-empty after stripping, and raises `ValueError` (promoted to `ValidationError` in the domain layer) if invalid. Maximum length is 200 characters.

#### Scenario: Valid name constructed

- GIVEN `"Clean Code"` as input
- WHEN `BookName("Clean Code")` is constructed
- THEN it stores the stripped value `"Clean Code"` and is hashable

#### Scenario: Whitespace-only rejected

- GIVEN `"   "` as input
- WHEN `BookName("   ")` is constructed
- THEN it raises `ValidationError(field="name", message="Name cannot be empty or whitespace")`

#### Scenario: Empty string rejected

- GIVEN `""` as input
- WHEN `BookName("")` is constructed
- THEN it raises `ValidationError(field="name", message="Name cannot be empty or whitespace")`

#### Scenario: Name too long rejected

- GIVEN a string of 201 characters
- WHEN `BookName(long_string)` is constructed
- THEN it raises `ValidationError(field="name", message="Name exceeds 200 characters")`

#### Scenario: Trimmed on construction

- GIVEN `"  Clean Code  "` with surrounding whitespace
- WHEN `BookName("  Clean Code  ")` is constructed
- THEN the stored value is `"Clean Code"` (trimmed)

---

### Requirement: BookAuthor Value Object

The system SHALL provide a `BookAuthor` value object that wraps a string, validates on construction that it is non-empty after stripping, and raises `ValidationError` if invalid. Maximum length is 150 characters.

#### Scenario: Valid author constructed

- GIVEN `"Robert C. Martin"` as input
- WHEN `BookAuthor("Robert C. Martin")` is constructed
- THEN it stores `"Robert C. Martin"` and is hashable

#### Scenario: Empty string rejected

- GIVEN `""` as input
- WHEN `BookAuthor("")` is constructed
- THEN it raises `ValidationError(field="author", message="Author cannot be empty or whitespace")`

#### Scenario: Author too long rejected

- GIVEN a string of 151 characters
- WHEN `BookAuthor(long_string)` is constructed
- THEN it raises `ValidationError(field="author", message="Author exceeds 150 characters")`

---

### Requirement: BookUrl Value Object

The system SHALL provide a `BookUrl` value object that wraps a string, validates on construction that it is a valid URL using `urllib.parse`, and raises `ValidationError` if invalid. Maximum length is 2048 characters.

#### Scenario: Valid URL constructed

- GIVEN `"https://example.com/book"` as input
- WHEN `BookUrl("https://example.com/book")` is constructed
- THEN it stores the URL and is hashable

#### Scenario: Malformed URL rejected

- GIVEN `"not-a-valid-url"` as input
- WHEN `BookUrl("not-a-valid-url")` is constructed
- THEN it raises `ValidationError(field="url", message="Invalid URL format")`

#### Scenario: URL too long rejected

- GIVEN a string of 2049 characters
- WHEN `BookUrl(long_string)` is constructed
- THEN it raises `ValidationError(field="url", message="URL exceeds 2048 characters")`

---

### Requirement: Value Object Immutability

The system SHALL ensure all value objects are immutable: instances MUST be hashable, comparable by value, and their fields MUST NOT be modifiable after construction.

#### Scenario: Two equal VOs have same hash

- GIVEN `BookName("Clean Code")` and another `BookName("Clean Code")`
- WHEN compared with `==`
- THEN they are equal and have the same hash

#### Scenario: Modification raises AttributeError

- GIVEN a `BookName` instance
- WHEN attempting to set any attribute after construction
- THEN it raises `AttributeError`

---

### Requirement: Book Entity Integrates Value Objects

The system SHALL have `Book` entity compose `BookName`, `BookAuthor`, and `BookUrl` value objects instead of raw strings, delegating validation to the value object layer.

#### Scenario: Book constructed with valid VOs

- GIVEN valid `BookName`, `BookAuthor`, and `BookUrl` instances
- WHEN `Book(name, author, url)` is constructed
- THEN it stores the value objects and they are accessible

#### Scenario: Book construction fails with invalid VO

- GIVEN an invalid `BookName` (e.g., empty string)
- WHEN `Book(invalid_name, author, url)` is constructed
- THEN the `BookName` constructor raises `ValidationError`