# ADR-001: Clean Architecture con Data Mapper

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

El proyecto comenzó como un monolito en `src/main.py` con toda la lógica en un solo archivo. A medida que creció, surgieron problemas: la lógica de negocio estaba mezclada con la persistencia y el transporte HTTP, los tests requerían levantar bases de datos reales, y agregar nuevas entidades implicaba tocar capas que no correspondían.

Las fuerzas en juego: necesidad de testear el dominio sin dependencias de infraestructura, facilitar cambios de base de datos (SQLite en dev, PostgreSQL en prod), y mantener la puerta abierta para nuevos transportes (CLI, workers) sin reescribir lógica.

## Decisión

Adoptamos Clean Architecture con 4 capas y Data Mapper explícito:

1. **Domain** (`src/domain/`) — Entidades puras (`Book`, `User`, `Invitation` como `@dataclass`), Value Objects (`BookName`, `BookAuthor`, `BookUrl` como `@dataclass(frozen=True)`), y puertos abstractos (`BookRepository`, `FavoriteRepository`, `TokenService`).
2. **Application** (`src/application/use_cases/`) — Casos de uso (`CreateBook`, `LoginUser`, `AddFavorite`) que orquestan el dominio. No importan SQLModel ni FastAPI.
3. **Infrastructure** (`src/infrastructure/`) — Adaptadores concretos: `SQLBookRepository`, `InMemoryBookRepository`, `JwtTokenService`, `BcryptPasswordHasher`. Los mappers (`BookMapper`, `CollectionMapper`) traducen entre modelos SQL y entidades de dominio.
4. **API** (`src/api/`) — FastAPI routers, schemas Pydantic (`BookPayload`), middleware de auth, y dependencias.

La regla clave: las entidades de dominio **nunca** heredan de `SQLModel`. `BookModel` es una tabla SQL plana; `Book` es un dataclass con Value Objects. `BookMapper.to_domain()` y `BookMapper.to_model()` hacen la traducción.

## Alternativas consideradas

- **Active Record (SQLModel directo)**: Menos archivos, pero acopla el dominio a SQLAlchemy. Los tests necesitan BD real o mocks complejos. Descartado por violar separación de concerns.
- **Django-style fat models**: Lógica de negocio en el modelo ORM. Práctico para CRUD simple, pero no escala cuando el dominio crece. Descartado.
- **Raw SQL sin ORM**: Control total, pero pérdida de type safety y migraciones manuales. Descartado por el overhead de mantenimiento.

## Consecuencias

**Más fácil**: Testear dominio puro con `InMemoryBookRepository` (371 tests sin BD real). Cambiar de SQLite a PostgreSQL solo toca `infrastructure/persistence/session.py`. Agregar un nuevo transporte (CLI, GraphQL) solo requiere un router nuevo.

**Más difícil**: Cada entidad necesita un mapper (`BookMapper`, `CollectionMapper`) — boilerplate adicional. Crear una nueva entidad implica tocar 4+ archivos (entity, model, mapper, repository ABC, repository impl).

**Riesgos**: El boilerplate puede generar fatiga y tentación de "atajos" que rompan la arquitectura. Mitigación: los tests de integración verifican que el dominio no importe de infrastructure.
