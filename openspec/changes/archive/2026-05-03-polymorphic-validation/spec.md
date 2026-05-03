# Spec: Polymorphic Validation + Value Objects

## Change: `polymorphic-validation`

Two new capabilities: polymorphic-validation infrastructure and value objects.

---

## 1. polymorphic-validation

### Purpose

Add polymorphic validation infrastructure: a `Validator[T]` protocol, concrete validators per field, a composite aggregator, domain error types, and integration points in use cases and repository.

### Requirement: Validator Protocol

The system SHALL provide a generic `Validator[T]` abstract base class that concrete validators implement. Each validator MUST expose a single `validate(entity: T) -> list[ValidationError]` method.

**Scenario: Protocol compliance**
- GIVEN a concrete validator implementing `Validator[Book]`
- WHEN `validate(book)` is called with a valid `Book`
- THEN it returns an empty `list[ValidationError]`

**Scenario: Validation error returned**
- GIVEN a `Book` with an empty name
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list containing one `ValidationError` with `field="name"`

### Requirement: Concrete Validators

The system SHALL provide three concrete validators, one per file, each under 30 lines with one public method:

- `BookNameValidator`: Rejects empty or whitespace-only strings; rejects names exceeding 200 characters
- `BookAuthorValidator`: Rejects empty or whitespace-only strings; rejects authors exceeding 150 characters  
- `BookUrlValidator`: Rejects empty strings, malformed URLs, and URLs exceeding 2048 characters

**Scenario: Valid name passes**
- GIVEN a `Book` with `name="Clean Code"`
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns an empty list

**Scenario: Empty name fails**
- GIVEN a `Book` with `name="   "` (whitespace-only)
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="name", message="Name cannot be empty or whitespace")`

**Scenario: Name too long fails**
- GIVEN a `Book` with `name` longer than 200 characters
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="name", message="Name exceeds 200 characters")`

**Scenario: Valid author passes**
- GIVEN a `Book` with `author="Robert C. Martin"`
- WHEN `BookAuthorValidator().validate(book)` is called
- THEN it returns an empty list

**Scenario: Author too long fails**
- GIVEN a `Book` with `author` longer than 150 characters
- WHEN `BookAuthorValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="author", message="Author exceeds 150 characters")`

**Scenario: Valid URL passes**
- GIVEN a `Book` with `url="https://example.com/book"`
- WHEN `BookUrlValidator().validate(book)` is called
- THEN it returns an empty list

**Scenario: Malformed URL fails**
- GIVEN a `Book` with `url="not-a-url"`
- WHEN `BookUrlValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="url", message="Invalid URL format")`

### Requirement: CompositeValidator

The system SHALL provide a `CompositeValidator` that accepts a list of validators and runs all of them, aggregating errors into a single flat list.

**Scenario: All validators pass**
- GIVEN a `CompositeValidator([BookNameValidator(), BookAuthorValidator(), BookUrlValidator()])` and a fully valid `Book`
- WHEN `validate(book)` is called
- THEN it returns an empty list

**Scenario: Multiple failures aggregated**
- GIVEN a `CompositeValidator([BookNameValidator(), BookAuthorValidator()])` and a `Book` with invalid name AND author
- WHEN `validate(book)` is called
- THEN it returns a list with 2 `ValidationError` items, one per field

### Requirement: Domain Error Types

The system SHALL provide a `DomainError` base exception class and a `ValidationError` dataclass with `field: str` and `message: str`.

**Scenario: DomainError raised**
- GIVEN invalid data passed to a repository method
- WHEN the repository attempts to persist
- THEN it raises `DomainError` with a descriptive message

**Scenario: ValidationError dataclass structure**
- GIVEN a `ValidationError(field="name", message="Name is required")`
- THEN it has accessible `.field` and `.message` attributes

### Requirement: Use Case Integration

The system SHALL inject `Validator[Book]` into `create_book`, `update_book`, and `replace_book` use cases. Each use case MUST call `validator.validate(book)` before persistence and raise `DomainError` if validation fails.

**Scenario: Valid book creation succeeds**
- GIVEN `CreateBookUseCase` with a `Validator[Book]` and a valid `Book` payload
- WHEN `execute(payload)` is called
- THEN it persists the book without raising

**Scenario: Invalid book creation raises DomainError**
- GIVEN `CreateBookUseCase` with a `Validator[Book]` and a `Book` with empty name
- WHEN `execute(payload)` is called
- THEN it raises `DomainError` with validation errors and does NOT persist

### Requirement: Repository Contract

The system SHALL have repository methods (`create`, `update`, `replace`) raise `DomainError` on invalid data instead of coercing or ignoring.

**Scenario: Create with invalid data raises DomainError**
- GIVEN `JsonBookRepository.create(book)` where `book` has invalid `author`
- WHEN called
- THEN it raises `DomainError` and does NOT write to storage

### Requirement: Pydantic HTTP Boundary

The system SHALL validate `BookPayload` at the HTTP boundary using Pydantic `@field_validator` decorators, rejecting empty name, author, and malformed URLs before the request reaches the use case layer.

**Scenario: Empty name rejected at HTTP layer**
- GIVEN a POST request with `{"name": "", "author": "Bob", "url": "https://example.com"}`
- WHEN `BookPayload` is constructed
- THEN Pydantic raises a validation error and returns HTTP 422

**Scenario: Valid payload passes through**
- GIVEN a POST request with valid fields
- WHEN `BookPayload` is constructed
- THEN it succeeds and the model is passed to the use case

---

## 2. value-objects

### Purpose

Introduce three immutable value objects — `BookName`, `BookAuthor`, `BookUrl` — that encapsulate validation logic and replace raw string fields in the `Book` entity.

### Requirement: BookName Value Object

The system SHALL provide a `BookName` value object that wraps a string, validates on construction that it is non-empty after stripping, and raises `ValidationError` if invalid. Maximum length is 200 characters.

**Scenario: Valid name constructed**
- GIVEN `"Clean Code"` as input
- WHEN `BookName("Clean Code")` is constructed
- THEN it stores the stripped value `"Clean Code"` and is hashable

**Scenario: Whitespace-only rejected**
- GIVEN `"   "` as input
- WHEN `BookName("   ")` is constructed
- THEN it raises `ValidationError(field="name", message="Name cannot be empty or whitespace")`

**Scenario: Empty string rejected**
- GIVEN `""` as input
- WHEN `BookName("")` is constructed
- THEN it raises `ValidationError(field="name", message="Name cannot be empty or whitespace")`

**Scenario: Name too long rejected**
- GIVEN a string of 201 characters
- WHEN `BookName(long_string)` is constructed
- THEN it raises `ValidationError(field="name", message="Name exceeds 200 characters")`

**Scenario: Trimmed on construction**
- GIVEN `"  Clean Code  "` with surrounding whitespace
- WHEN `BookName("  Clean Code  ")` is constructed
- THEN the stored value is `"Clean Code"` (trimmed)

### Requirement: BookAuthor Value Object

The system SHALL provide a `BookAuthor` value object that wraps a string, validates on construction that it is non-empty after stripping, and raises `ValidationError` if invalid. Maximum length is 150 characters.

**Scenario: Valid author constructed**
- GIVEN `"Robert C. Martin"` as input
- WHEN `BookAuthor("Robert C. Martin")` is constructed
- THEN it stores `"Robert C. Martin"` and is hashable

**Scenario: Empty string rejected**
- GIVEN `""` as input
- WHEN `BookAuthor("")` is constructed
- THEN it raises `ValidationError(field="author", message="Author cannot be empty or whitespace")`

**Scenario: Author too long rejected**
- GIVEN a string of 151 characters
- WHEN `BookAuthor(long_string)` is constructed
- THEN it raises `ValidationError(field="author", message="Author exceeds 150 characters")`

### Requirement: BookUrl Value Object

The system SHALL provide a `BookUrl` value object that wraps a string, validates on construction that it is a valid URL using `urllib.parse`, and raises `ValidationError` if invalid. Maximum length is 2048 characters.

**Scenario: Valid URL constructed**
- GIVEN `"https://example.com/book"` as input
- WHEN `BookUrl("https://example.com/book")` is constructed
- THEN it stores the URL and is hashable

**Scenario: Malformed URL rejected**
- GIVEN `"not-a-valid-url"` as input
- WHEN `BookUrl("not-a-valid-url")` is constructed
- THEN it raises `ValidationError(field="url", message="Invalid URL format")`

**Scenario: URL too long rejected**
- GIVEN a string of 2049 characters
- WHEN `BookUrl(long_string)` is constructed
- THEN it raises `ValidationError(field="url", message="URL exceeds 2048 characters")`

### Requirement: Value Object Immutability

The system SHALL ensure all value objects are immutable: instances MUST be hashable, comparable by value, and their fields MUST NOT be modifiable after construction.

**Scenario: Two equal VOs have same hash**
- GIVEN `BookName("Clean Code")` and another `BookName("Clean Code")`
- WHEN compared with `==`
- THEN they are equal and have the same hash

**Scenario: Modification raises AttributeError**
- GIVEN a `BookName` instance
- WHEN attempting to set any attribute after construction
- THEN it raises `AttributeError`

### Requirement: Book Entity Integrates Value Objects

The system SHALL have `Book` entity compose `BookName`, `BookAuthor`, and `BookUrl` value objects instead of raw strings, delegating validation to the value object layer.

**Scenario: Book constructed with valid VOs**
- GIVEN valid `BookName`, `BookAuthor`, and `BookUrl` instances
- WHEN `Book(name, author, url)` is constructed
- THEN it stores the value objects and they are accessible

**Scenario: Book construction fails with invalid VO**
- GIVEN an invalid `BookName` (e.g., empty string)
- WHEN `Book(invalid_name, author, url)` is constructed
- THEN the `BookName` constructor raises `ValidationError`