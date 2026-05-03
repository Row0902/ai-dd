# Delta for polymorphic-validation

## Purpose

Add polymorphic validation infrastructure: a `Validator[T]` protocol, concrete validators per field, a composite aggregator, domain error types, and integration points in use cases and repository.

---

## ADDED Requirements

### Requirement: Validator Protocol

The system SHALL provide a generic `Validator[T]` abstract base class that concrete validators implement. Each validator MUST expose a single `validate(entity: T) -> list[ValidationError]` method.

#### Scenario: Protocol compliance

- GIVEN a concrete validator implementing `Validator[Book]`
- WHEN `validate(book)` is called with a valid `Book`
- THEN it returns an empty `list[ValidationError]`

#### Scenario: Validation error returned

- GIVEN a `Book` with an empty name
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list containing one `ValidationError` with `field="name"`

---

### Requirement: Concrete Validators

The system SHALL provide three concrete validators, one per file, each under 30 lines with one public method:

- `BookNameValidator`: Rejects empty or whitespace-only strings; rejects names exceeding 200 characters
- `BookAuthorValidator`: Rejects empty or whitespace-only strings; rejects authors exceeding 150 characters  
- `BookUrlValidator`: Rejects empty strings, malformed URLs, and URLs exceeding 2048 characters

#### Scenario: Valid name passes

- GIVEN a `Book` with `name="Clean Code"`
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns an empty list

#### Scenario: Empty name fails

- GIVEN a `Book` with `name="   "` (whitespace-only)
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="name", message="Name cannot be empty or whitespace")`

#### Scenario: Name too long fails

- GIVEN a `Book` with `name` longer than 200 characters
- WHEN `BookNameValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="name", message="Name exceeds 200 characters")`

#### Scenario: Valid author passes

- GIVEN a `Book` with `author="Robert C. Martin"`
- WHEN `BookAuthorValidator().validate(book)` is called
- THEN it returns an empty list

#### Scenario: Author too long fails

- GIVEN a `Book` with `author` longer than 150 characters
- WHEN `BookAuthorValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="author", message="Author exceeds 150 characters")`

#### Scenario: Valid URL passes

- GIVEN a `Book` with `url="https://example.com/book"`
- WHEN `BookUrlValidator().validate(book)` is called
- THEN it returns an empty list

#### Scenario: Malformed URL fails

- GIVEN a `Book` with `url="not-a-url"`
- WHEN `BookUrlValidator().validate(book)` is called
- THEN it returns a list with one `ValidationError(field="url", message="Invalid URL format")`

---

### Requirement: CompositeValidator

The system SHALL provide a `CompositeValidator` that accepts a list of validators and runs all of them, aggregating errors into a single flat list.

#### Scenario: All validators pass

- GIVEN a `CompositeValidator([BookNameValidator(), BookAuthorValidator(), BookUrlValidator()])` and a fully valid `Book`
- WHEN `validate(book)` is called
- THEN it returns an empty list

#### Scenario: Multiple failures aggregated

- GIVEN a `CompositeValidator([BookNameValidator(), BookAuthorValidator()])` and a `Book` with invalid name AND author
- WHEN `validate(book)` is called
- THEN it returns a list with 2 `ValidationError` items, one per field

---

### Requirement: Domain Error Types

The system SHALL provide a `DomainError` base exception class and a `ValidationError` dataclass with `field: str` and `message: str`.

#### Scenario: DomainErrorRaised

- GIVEN invalid data passed to a repository method
- WHEN the repository attempts to persist
- THEN it raises `DomainError` with a descriptive message

#### Scenario: ValidationError dataclass structure

- GIVEN a `ValidationError(field="name", message="Name is required")`
- THEN it has accessible `.field` and `.message` attributes

---

### Requirement: Use Case Integration

The system SHALL inject `Validator[Book]` into `create_book`, `update_book`, and `replace_book` use cases. Each use case MUST call `validator.validate(book)` before persistence and raise `DomainError` if validation fails.

#### Scenario: Valid book creation succeeds

- GIVEN `CreateBookUseCase` with a `Validator[Book]` and a valid `Book` payload
- WHEN `execute(payload)` is called
- THEN it persists the book without raising

#### Scenario: Invalid book creation raises DomainError

- GIVEN `CreateBookUseCase` with a `Validator[Book]` and a `Book` with empty name
- WHEN `execute(payload)` is called
- THEN it raises `DomainError` with validation errors and does NOT persist

---

### Requirement: Repository Contract

The system SHALL have repository methods (`create`, `update`, `replace`) raise `DomainError` on invalid data instead of coercing or ignoring.

#### Scenario: Create with invalid data raises DomainError

- GIVEN `JsonBookRepository.create(book)` where `book` has invalid `author`
- WHEN called
- THEN it raises `DomainError` and does NOT write to storage

---

### Requirement: Pydantic HTTP Boundary

The system SHALL validate `BookPayload` at the HTTP boundary using Pydantic `@field_validator` decorators, rejecting empty name, author, and malformed URLs before the request reaches the use case layer.

#### Scenario: Empty name rejected at HTTP layer

- GIVEN a POST request with `{"name": "", "author": "Bob", "url": "https://example.com"}`
- WHEN `BookPayload` is constructed
- THEN Pydantic raises a validation error and returns HTTP 422

#### Scenario: Valid payload passes through

- GIVEN a POST request with valid fields
- WHEN `BookPayload` is constructed
- THEN it succeeds and the model is passed to the use case