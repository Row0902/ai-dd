# Guía de Desarrollo — ai-dd

> Todo lo que necesitas para empezar a contribuir en 10 minutos.

## Requisitos

| Herramienta | Versión mínima | Para qué |
|-------------|---------------|----------|
| Python | 3.13+ | Runtime (`.python-version` dice 3.14) |
| uv | cualquiera | Gestor de paquetes y entornos |
| Docker | 24+ | PostgreSQL y Redis (opcional, sin Docker usas `memory://`) |
| Git | cualquiera | Control de versiones |

## Setup en 3 comandos

```bash
# 1. Clonar e instalar dependencias
git clone <repo-url>
cd ai-dd
uv sync

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar la app
uv run fastapi dev src/main.py
```

Abrí `http://localhost:8000/docs` para ver la API interactiva (Swagger UI). La app arranca con base de datos en memoria (`DATABASE_URL=memory://` por defecto).

## Estructura del Proyecto

```
ai-dd/
├── src/
│   ├── main.py                       # Composition root: app factory + lifespan
│   ├── config/
│   │   └── settings.py               # AppSettings (pydantic-settings, .env)
│   ├── api/                          # Capa de presentación (FastAPI)
│   │   ├── routers/                  # Endpoints HTTP
│   │   │   ├── books.py              # CRUD de libros
│   │   │   ├── auth.py               # Registro, login, invitaciones
│   │   │   ├── collections.py        # Colecciones de libros
│   │   │   ├── favorites.py          # Favoritos (per-user)
│   │   │   └── health.py             # Health check (GET /health)
│   │   ├── schemas.py                # BookPayload con @field_validator
│   │   ├── mappers.py                # book_to_dict (dominio → JSON)
│   │   ├── dependencies.py           # DI: get_book_repo, get_settings, etc.
│   │   └── middleware/
│   │       ├── auth.py               # require_permission (JWT + RBAC)
│   │       └── logging.py            # Request logging via structlog
│   ├── application/
│   │   └── use_cases/                # Casos de uso (funciones async puras)
│   │       ├── create_book.py        # create_book(repo, name, ...)
│   │       ├── read_book.py          # get_book(repo, book_id)
│   │       ├── list_books.py         # list_books(repo, limit, offset)
│   │       ├── search_books.py       # get_books_by_name(repo, name)
│   │       ├── update_book.py        # update_book(repo, book_id, ...)
│   │       ├── replace_book.py       # replace_book (PUT semantics)
│   │       ├── delete_book.py        # delete_book(repo, book_id)
│   │       ├── book_use_case.py      # BookUseCase (clase con get_book_repo override)
│   │       ├── auth/                 # login_user, register_user, etc.
│   │       ├── collections/          # create_collection, list_collections, etc.
│   │       └── favorites/            # add_favorite, list_favorites, etc.
│   ├── domain/                       # Capa de dominio (sin dependencias externas)
│   │   ├── entities.py               # Book (dataclass con VOs)
│   │   ├── exceptions.py             # DomainError, ValidationError, AggregatedValidationError
│   │   ├── repositories.py           # BookRepository (ABC)
│   │   ├── validation_rules.py       # MAX_TITLE_LENGTH, MAX_AUTHOR_LENGTH, etc.
│   │   ├── value_objects/            # Objetos inmutables que se auto-validan
│   │   │   ├── book_name.py          # BookName (frozen dataclass)
│   │   │   ├── book_author.py        # BookAuthor
│   │   │   └── book_url.py           # BookUrl
│   │   ├── validators/               # Validadores polimórficos (Strategy)
│   │   │   ├── protocol.py           # Validator[T] (ABC)
│   │   │   ├── book_name.py          # BookNameValidator
│   │   │   ├── book_author.py        # BookAuthorValidator
│   │   │   ├── book_url.py           # BookUrlValidator
│   │   │   └── composite.py          # CompositeValidator
│   │   ├── auth/                     # Entidades y puertos de autenticación
│   │   │   ├── entities.py           # User, Invitation
│   │   │   ├── ports.py              # UserRepository, TokenService, etc. (ABCs)
│   │   │   ├── permissions.py        # Role, Operation, require_permission
│   │   │   └── exceptions.py         # AuthenticationError, AuthorizationError, etc.
│   │   ├── collections/              # CollectionRepository (ABC) + entidades
│   │   └── favorites/                # FavoriteRepository (ABC)
│   └── infrastructure/               # Adaptadores concretos
│       ├── persistence/              # Repositorios SQL + mappers
│       │   ├── sql_models.py         # BookModel (SQLModel)
│       │   ├── sql_book_repository.py # SQLBookRepository
│       │   ├── book_mapper.py        # BookMapper (Book ↔ BookModel)
│       │   ├── session.py            # create_engine_from_url, create_tables
│       │   ├── sql_collection_repository.py
│       │   ├── sql_favorite_repository.py
│       │   ├── in_memory_collection_repository.py
│       │   └── in_memory_favorite_repository.py
│       ├── memory_book_repository.py  # InMemoryBookRepository
│       ├── json_book_repository.py    # JsonBookRepository (legacy)
│       ├── repository_factory.py      # create_repository(settings)
│       ├── repository_registry.py     # register(key, factory)
│       ├── auth/                      # JWT, bcrypt, in-memory users
│       │   ├── jwt_token_service.py  # JwtTokenService
│       │   ├── bcrypt_password_hasher.py
│       │   ├── in_memory_user_repository.py
│       │   ├── sql_user_repository.py
│       │   ├── in_memory_invitation_repository.py
│       │   ├── sql_invitation_repository.py
│       │   ├── sql_models.py         # UserModel, InvitationModel
│       │   └── logging_notification_service.py
│       └── serializers/
│           └── json_book_serializer.py
├── tests/
│   ├── conftest.py                   # Fixtures globales (client, auth_headers, etc.)
│   ├── unit/                         # Tests de lógica de dominio (sin HTTP)
│   │   ├── conftest.py               # _valid_book helper
│   │   ├── test_value_objects.py     # BookName, BookAuthor, BookUrl
│   │   ├── test_validators.py        # Validator protocol + happy-path
│   │   ├── test_composite_validator.py
│   │   ├── test_domain_entities.py   # Book entity
│   │   ├── test_exceptions.py        # DomainError hierarchy
│   │   ├── test_validation_rules.py
│   │   ├── test_schemas.py           # BookPayload validators
│   │   ├── test_book_use_cases.py
│   │   ├── test_memory_book_repository.py
│   │   ├── test_json_book_repository.py
│   │   ├── test_sql_book_repository.py
│   │   ├── test_sql_models.py
│   │   ├── test_book_mapper.py
│   │   ├── test_session.py
│   │   ├── test_repository_factory.py
│   │   ├── test_repository_registry.py
│   │   ├── test_auth_middleware.py
│   │   ├── auth/                     # Auth-specific unit tests
│   │   ├── collections/
│   │   └── favorites/
│   └── integration/                  # Tests HTTP end-to-end con TestClient
│       ├── test_books_api.py         # CRUD + paginación + validación + auth
│       ├── test_auth_api.py          # Registro, login, refresh
│       ├── test_collections_api.py
│       ├── test_favorites_api.py
│       └── test_health.py            # GET /health
├── docker/
│   ├── docker-compose.yml            # PostgreSQL + Redis + app
│   └── services/
│       ├── postgres.yml
│       └── redis.yml
├── docs/
│   ├── ARCHITECTURE.md               # Arquitectura completa (649 líneas)
│   ├── DEVELOPMENT.md                # Este archivo
│   └── adr/                          # 7 ADRs con decisiones de arquitectura
├── .github/workflows/
│   └── ci.yml                        # CI: Python 3.13/3.14, pytest, ty, ruff
├── .env.example                      # Template de variables de entorno
├── pyproject.toml                    # Dependencias + ruff + ty + pytest config
├── Dockerfile                        # Imagen de producción (python:3.13-slim)
└── README.md                         # Descripción del proyecto
```

> Para detalles completos de arquitectura, leé [`ARCHITECTURE.md`](./ARCHITECTURE.md). Las decisiones de diseño están documentadas en [`adr/`](./adr/).

## Flujo de Desarrollo

### 1. Ejecutar la app

```bash
# Con recarga automática (desarrollo)
uv run fastapi dev src/main.py --reload

# Sin recarga (similar a producción)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Abrí `http://localhost:8000/docs` — Swagger UI con todos los endpoints.

**Health check:**
```bash
curl http://localhost:8000/health
# {"status":"ok","database":"up"}
```

### 2. Ejecutar tests

```bash
# Todos los tests
uv run pytest

# Solo unitarios (lógica de dominio, sin HTTP)
uv run pytest tests/unit/ -v

# Solo integración (HTTP con TestClient)
uv run pytest tests/integration/ -v

# Con cobertura
uv run pytest --cov=src --cov-report=term-missing

# Un archivo específico
uv run pytest tests/unit/test_value_objects.py -v

# Con salida detallada de fallos
uv run pytest -v --tb=long
```

### 3. Linting y type checking

```bash
# Linter (reglas D, B, I, N, Q, UP + Google docstrings)
uv run ruff check src/ tests/

# Formateador (line-length 88, double quotes, Google docstrings)
uv run ruff format src/ tests/

# Type checker (modo estricto, solo src/)
uv run ty check src/
```

> **Regla:** Antes de commitear, `ruff check` y `ty check src/` deben pasar sin errores. `ruff format` ya está configurado con `fix = true` en `pyproject.toml`.

### 4. Docker (PostgreSQL + Redis)

```bash
# Levantar servicios de infraestructura
docker compose -f docker/docker-compose.yml up -d

# Configurar .env para PostgreSQL
DATABASE_URL=postgresql://ai_dd_user:ai_dd_pass@localhost:5432/ai_dd

# Ejecutar con SQL
uv run fastapi dev src/main.py
```

Para desarrollo rápido sin Docker, usá `DATABASE_URL=memory://` (por defecto).

## Arquitectura en 30 segundos

El proyecto sigue **Clean Architecture (Puertos y Adaptadores)** con 4 capas:

```
api/ (FastAPI) → application/ (use cases) → domain/ (entities, VOs, ABCs)
                                                  ↑
                                     infrastructure/ (adapters)
```

**Regla de oro:** Las dependencias apuntan hacia el dominio. `domain/` no importa nada de `api/`, `application/`, ni `infrastructure/`. Las implementaciones concretas viven en `infrastructure/` y se inyectan en `main.py` (composition root) mediante `dependency_overrides`.

**Doble validación:**
1. **Capa HTTP:** `BookPayload` (Pydantic) con `@field_validator` — primera línea de defensa. Rechaza requests inválidos con 422 antes de tocar el dominio.
2. **Capa de dominio:** `BookName`, `BookAuthor`, `BookUrl` (Value Objects) — validan en construcción. Si un caso de uso construye una entidad con datos inválidos, explota inmediatamente.

## Cómo agregar...

### ...un nuevo endpoint

Vamos a agregar `GET /books/{id}/stats` que devuelve estadísticas de un libro (cantidad de caracteres, palabras, etc.). Este es un ejemplo concreto paso a paso.

#### Paso 1: Crear el caso de uso

Archivo: `src/application/use_cases/book_stats.py`

```python
"""Book statistics use case."""

from __future__ import annotations

import builtins

from domain.entities import Book
from domain.repositories import BookRepository


async def get_book_stats(
    repo: BookRepository, book_id: str
) -> builtins.dict[str, int] | None:
    """Return statistics for a book.

    Args:
        repo: Repository port.
        book_id: Book identifier.

    Returns:
        Dict with stats (char_count, word_count) or None if not found.
    """
    book = await repo.get(book_id)
    if book is None:
        return None
    content = book.content or ""
    return {
        "char_count": len(content),
        "word_count": len(content.split()) if content else 0,
    }
```

#### Paso 2: Agregar el endpoint al router

Archivo: `src/api/routers/books.py` — agregar al final del archivo:

```python
from application.use_cases.book_stats import get_book_stats  # nuevo import

@router.get("/books/{book_id}/stats")
async def get_book_stats_endpoint(
    book_id: str,
    repo: Annotated[BookRepository, Depends(get_book_repo)],
    user: dict = Depends(require_permission(Operation.BOOK_READ)),
):
    """Get statistics for a book."""
    stats = await get_book_stats(repo, book_id)
    if stats is not None:
        return stats
    raise HTTPException(status_code=404, detail="Not found")
```

#### Paso 3: Escribir el test de integración

Archivo: `tests/integration/test_books_api.py` — agregar al final:

```python
class TestBookStats:
    """Tests for GET /books/{id}/stats endpoint."""

    def test_get_stats_for_existing_book(self) -> None:
        """GET /books/{id}/stats returns char and word counts."""
        client = _client()
        headers = _auth_headers()
        created = client.post(
            "/books",
            json={"name": "Stats Book", "content": "one two three four"},
            headers=headers,
        ).json()

        resp = client.get(f"/books/{created['id']}/stats", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == {"char_count": 18, "word_count": 4}

    def test_get_stats_for_missing_book_returns_404(self) -> None:
        """GET /books/{id}/stats returns 404 for missing book."""
        client = _client()
        resp = client.get("/books/nonexistent/stats", headers=_auth_headers())
        assert resp.status_code == 404
```

#### Paso 4: Verificar

```bash
uv run pytest tests/integration/test_books_api.py::TestBookStats -v
uv run ruff check src/api/routers/books.py src/application/use_cases/book_stats.py
uv run ty check src/
```

### ...una nueva entidad de dominio

Vamos a agregar `Review` (reseña de un libro) con las 4 capas. Este es el patrón que sigue TODO en el proyecto.

#### Paso 1: Value Object `ReviewRating` (dominio)

Archivo: `src/domain/value_objects/review_rating.py`

```python
"""ReviewRating value object: frozen, validates 1-5 range."""

from dataclasses import dataclass

from domain.exceptions import ValidationError


@dataclass(frozen=True)
class ReviewRating:
    """Immutable rating value object (1-5).

    Attributes:
        value: Integer rating between 1 and 5 inclusive.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate rating is between 1 and 5."""
        if not 1 <= self.value <= 5:
            raise ValidationError(
                field="rating", message="Rating must be between 1 and 5"
            )
```

#### Paso 2: Entidad `Review` (dominio)

Archivo: `src/domain/entities.py` — o crear `src/domain/review_entities.py`:

```python
"""Review domain entity."""

from dataclasses import dataclass

from domain.value_objects.review_rating import ReviewRating


@dataclass
class Review:
    """A user review of a book.

    Attributes:
        id: Unique identifier.
        book_id: ID of the reviewed book.
        user_id: ID of the reviewing user.
        rating: Rating value object (1-5).
        comment: Optional review text.
    """

    id: str
    book_id: str
    user_id: str
    _rating: ReviewRating
    comment: str = ""

    def __init__(
        self, id: str, book_id: str, user_id: str, rating: int, comment: str = ""
    ) -> None:
        self.id = id
        self.book_id = book_id
        self.user_id = user_id
        self._rating = ReviewRating(rating)
        self.comment = comment

    @property
    def rating(self) -> int:
        """Return the validated rating as plain int."""
        return self._rating.value
```

#### Paso 3: Repository ABC (dominio)

Archivo: `src/domain/review_repositories.py`

```python
"""Review repository port."""

from abc import ABC, abstractmethod
import builtins

from domain.review_entities import Review


class ReviewRepository(ABC):
    """Port for review persistence."""

    @abstractmethod
    async def list_by_book(self, book_id: str) -> builtins.list[Review]: ...

    @abstractmethod
    async def create(self, review: Review) -> Review: ...
```

#### Paso 4: SQL Model (infraestructura)

Archivo: `src/infrastructure/persistence/review_models.py`

```python
"""SQLModel definitions for reviews."""

from sqlmodel import Field, SQLModel


class ReviewModel(SQLModel, table=True):
    """SQL table for book reviews."""

    __tablename__ = "reviews"

    id: str = Field(primary_key=True)
    book_id: str = Field(index=True)
    user_id: str = Field(index=True)
    rating: int
    comment: str = ""
```

#### Paso 5: Mapper (infraestructura)

Archivo: `src/infrastructure/persistence/review_mapper.py`

```python
"""Mapper between Review domain entity and ReviewModel."""

from domain.review_entities import Review
from infrastructure.persistence.review_models import ReviewModel


class ReviewMapper:
    """Static mapper: Review ↔ ReviewModel."""

    @staticmethod
    def to_domain(model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            book_id=model.book_id,
            user_id=model.user_id,
            rating=model.rating,
            comment=model.comment,
        )

    @staticmethod
    def to_model(entity: Review) -> ReviewModel:
        return ReviewModel(
            id=entity.id,
            book_id=entity.book_id,
            user_id=entity.user_id,
            rating=entity.rating,
            comment=entity.comment,
        )
```

#### Paso 6: SQL Repository (infraestructura)

Archivo: `src/infrastructure/persistence/sql_review_repository.py`

```python
"""SQL-backed review repository."""

import builtins
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.review_entities import Review
from domain.review_repositories import ReviewRepository
from infrastructure.persistence.review_mapper import ReviewMapper
from infrastructure.persistence.review_models import ReviewModel


class SQLReviewRepository(ReviewRepository):
    """ReviewRepository backed by SQL via async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_book(self, book_id: str) -> builtins.list[Review]:
        statement = select(ReviewModel).where(ReviewModel.book_id == book_id)
        result = await self._session.execute(statement)
        return [ReviewMapper.to_domain(m) for m in result.scalars().all()]

    async def create(self, review: Review) -> Review:
        review_id = review.id or uuid.uuid4().hex
        model = ReviewMapper.to_model(
            Review(
                id=review_id,
                book_id=review.book_id,
                user_id=review.user_id,
                rating=review.rating,
                comment=review.comment,
            )
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return ReviewMapper.to_domain(model)
```

#### Paso 7: Caso de uso (aplicación)

Archivo: `src/application/use_cases/create_review.py`

```python
"""Create review use case."""

from domain.review_entities import Review
from domain.review_repositories import ReviewRepository


async def create_review(
    repo: ReviewRepository,
    *,
    book_id: str,
    user_id: str,
    rating: int,
    comment: str = "",
) -> Review:
    """Create a book review.

    Args:
        repo: Review repository port.
        book_id: Book being reviewed.
        user_id: User writing the review.
        rating: Rating 1-5.
        comment: Optional review text.

    Returns:
        Persisted review entity.
    """
    review = Review(
        id="",
        book_id=book_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
    )
    return await repo.create(review)
```

#### Paso 8: Test unitario

Archivo: `tests/unit/test_review_rating.py`

```python
"""Unit tests for ReviewRating value object."""

import pytest

from domain.exceptions import ValidationError
from domain.value_objects.review_rating import ReviewRating


def test_valid_rating() -> None:
    """Rating 3 is valid."""
    r = ReviewRating(3)
    assert r.value == 3


def test_rating_too_low_raises() -> None:
    """Rating 0 raises ValidationError."""
    with pytest.raises(ValidationError) as e:
        ReviewRating(0)
    assert e.value.field == "rating"


def test_rating_too_high_raises() -> None:
    """Rating 6 raises ValidationError."""
    with pytest.raises(ValidationError) as e:
        ReviewRating(6)
    assert e.value.field == "rating"
```

#### Paso 9: Verificar

```bash
uv run pytest tests/unit/test_review_rating.py -v
uv run ty check src/
uv run ruff check src/
```

### ...un nuevo validador

Los validadores implementan el protocolo `Validator[T]` (Strategy pattern) y se componen con `CompositeValidator`. Se inyectan en los casos de uso como parámetro opcional `validator: Validator[Book] | None = None`.

#### Ejemplo: `BookContentValidator`

Archivo: `src/domain/validators/book_content.py`

```python
"""BookContentValidator: validates book content is non-empty."""

from domain.entities import Book
from domain.exceptions import ValidationError
from domain.validators.protocol import Validator


class BookContentValidator(Validator[Book]):
    """Validates the content field of a Book entity."""

    def validate(self, entity: Book) -> list[ValidationError]:
        """Validate that content is not empty or whitespace-only."""
        errors: list[ValidationError] = []
        if not entity.content.strip():
            errors.append(
                ValidationError(
                    field="content",
                    message="Content cannot be empty or whitespace",
                )
            )
        return errors
```

#### Cómo componerlo

En el caso de uso `create_book.py`, pasás un `CompositeValidator`:

```python
from domain.validators.book_name import BookNameValidator
from domain.validators.book_content import BookContentValidator
from domain.validators.composite import CompositeValidator

validator = CompositeValidator([
    BookNameValidator(),
    BookContentValidator(),
])

book = await create_book(repo, name="Clean Code", validator=validator)
```

#### Test

Archivo: `tests/unit/test_book_content_validator.py`

```python
from domain.validators.book_content import BookContentValidator
from tests.unit.conftest import _valid_book


def test_empty_content_returns_error() -> None:
    """Empty content produces a validation error."""
    book = _valid_book(content="")
    errors = BookContentValidator().validate(book)
    assert len(errors) == 1
    assert errors[0].field == "content"
```

## Convenciones

### Commits

Usamos **Conventional Commits** con scopes que reflejan la capa:

```
feat(domain): agregar ReviewRating value object
feat(api): agregar GET /books/{id}/stats
fix(infra): corregir session leak en SQLBookRepository
refactor(domain): extraer validadores a archivos separados
docs: actualizar guía de desarrollo
test(integration): agregar tests de paginación
```

**Work-unit commits:** Cada commit incluye tests + código + docs que pertenecen al mismo cambio. No separar por tipo de archivo (ej: un commit solo de tests, otro solo de código).

### Código

- **Google docstrings** en TODAS las funciones y clases públicas. Configurado en `pyproject.toml` (`convention = "google"`), ruff lo valida con la regla `D`.
- **`ruff format`** antes de commitear. El auto-formateo está activado (`fix = true`).
- **`ruff check`** sin errores (reglas: `B`, `D`, `I`, `N`, `Q`, `UP`).
- **`ty check src/`** sin errores (modo `all = "error"`).
- **Máximo ~300 líneas por archivo, ~20 líneas por función.** Si un archivo crece, es señal de que necesita dividirse.
- **`from __future__ import annotations`** en todos los archivos.
- **Nombres de constantes:** `UPPER_SNAKE_CASE` desde `domain/validation_rules.py` (única fuente de verdad).
- **Nombres de funciones públicas y variables:** `snake_case`; **clases:** `PascalCase`.
- **Strings con comillas dobles** (configurado en ruff).
- **No uses números mágicos ni strings inline.** Importalos de `domain/validation_rules.py`.

### Tests

- **1 test por comportamiento**, no 1 test por método. El nombre del test describe qué debería pasar.
- **Usar fixtures de `conftest.py`** cuando apliquen:
  - `client` — `TestClient` con repositorio en memoria (tests de integración)
  - `auth_headers` — token JWT de usuario estándar
  - `admin_auth_headers` — token JWT de admin
  - `sample_book` — diccionario con datos de prueba
  - `_valid_book()` — helper para crear Books válidos (tests unitarios)
- **Tests de dominio: sin mocks, puro.** Las entidades y VOs se prueban directamente.
- **Tests de API:** `TestClient` + repositorio `memory://`. Sin base de datos real.
- **Archivos de test:** `test_<modulo>.py` dentro de `tests/unit/` o `tests/integration/`.
- **Clases de test** para agrupar comportamientos relacionados: `TestBookName`, `TestBooksApi`.

### PRs

- **Rama desde `feat/production-readiness`** (o la rama de feature correspondiente), no desde `main` directamente para features grandes.
- **PR description con:** qué cambia, por qué, cómo verificarlo.
- **Tests deben pasar en CI** (Python 3.13 y 3.14).
- **Máximo ~400 líneas cambiadas** por PR (carga cognitiva del reviewer). Si es más grande, dividir en stacked PRs.

## CI/CD

El workflow de GitHub Actions (`.github/workflows/ci.yml`) se ejecuta en:

- **push** a `main` o `develop`
- **pull_request** hacia `main` o `develop`

Ejecuta en **Python 3.13 y 3.14** (matrix):

1. `uv sync --frozen` — instala dependencias exactas del lockfile
2. `uv run pytest -x -q` — tests (se detiene al primer fallo)
3. `uv run ty check src/` — type checking estricto
4. `ruff check` — linting (vía `ruff-action`)

> Si los tests pasan en local pero fallan en CI, asegurate de haber corrido `uv sync --frozen` para validar que tu lockfile está actualizado.

## Debugging

### Problemas comunes

**"Module not found" o "No module named 'src'"**
```bash
uv sync                          # reinstalar dependencias
uv run python -c "import sys; print(sys.path)"
```
El `pythonpath = ["src"]` en `pyproject.toml` agrega `src/` al path. Si usás VS Code, asegurate de que el intérprete apunte al `.venv`.

**"port 8000 already in use"**
```bash
lsof -i :8000                   # encontrar el proceso
kill -9 <PID>                   # matarlo
```
O levantá en otro puerto: `uv run uvicorn src.main:app --port 8001`.

**Tests fallan en CI pero no en local**
```bash
uv sync --frozen                # verificar lockfile
uv run pytest --tb=long         # salida detallada
```
El CI usa `--frozen`, que instala exactamente lo que está en `uv.lock`. Si agregaste dependencias sin actualizar el lockfile, falla.

**ty errors en `src/`**
```bash
uv run ty check src/            # ver todos los errores
uv run ty check src/ --verbose  # salida detallada
```
Los archivos de test (`**/test_*.py`) tienen reglas más permisivas (`possibly-unresolved-reference = "warn"`).

**ruff errors de docstrings (D)**
```bash
uv run ruff check src/ --select D  # solo errores de docstrings
uv run ruff format src/            # auto-formatear
```
Las reglas `D203` y `D213` están ignoradas (conflicto entre estilos de docstring). La convención es Google (`D` completo menos esas dos + `D104`).

**Error `ValidationError` no se convierte a 422**
Verificá que el handler esté registrado en `main.py` (`@app.exception_handler(DomainError)`). Los handlers de excepción deben estar a nivel aplicación, no a nivel router.

**`AttributeError: cannot set attribute` en tests de VOs**
Los value objects son `frozen=True` — no se puede mutar. Si un test deliberadamente intenta mutar, agregá:
```python
author.value = "other"  # ty: ignore[invalid-assignment]
```

**Error "BookRepository provider not configured"**
El dependency override de `get_book_repo` no se configuró. Asegurate de que `create_app()` esté llamando a `app.dependency_overrides[get_book_repo] = repo_dep`.

## Recursos

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — Arquitectura completa (649 líneas, 11 secciones)
- [`adr/`](./adr/) — 7 Decisiones de Arquitectura (ADR-001 a ADR-007)
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [SQLModel docs](https://sqlmodel.tiangolo.com/)
- [pytest docs](https://docs.pytest.org/)
- [ruff docs](https://docs.astral.sh/ruff/)
- [ty docs](https://docs.astral.sh/ty/)
- [uv docs](https://docs.astral.sh/uv/)
- [Clean Architecture — Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
