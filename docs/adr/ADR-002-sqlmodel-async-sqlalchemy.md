# ADR-002: SQLModel + async SQLAlchemy

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

FastAPI es async por naturaleza. Necesitábamos un ORM que soportara `async/await` sin bloquear el event loop. Las opciones disponibles: SQLAlchemy 2.0 async puro, SQLModel (wrapper de SQLAlchemy por el autor de FastAPI), Tortoise ORM, `databases` (encode), y asyncpg/raw SQL.

El proyecto usa múltiples backends: SQLite con aiosqlite en desarrollo, PostgreSQL con asyncpg en producción, e InMemory para tests. Necesitábamos algo que funcionara con los tres sin duplicar código.

## Decisión

SQLModel (`>=0.0.22`) para definir modelos de tabla + SQLAlchemy 2.0 async engine directamente.

Los modelos SQL viven en `src/infrastructure/persistence/sql_models.py` (`BookModel`, `FavoriteModel`) y `src/infrastructure/auth/sql_models.py` (`UserModel`, `InvitationModel`). Son clases planas que mapean a tablas — no contienen lógica de negocio.

La sesión async se gestiona en `src/infrastructure/persistence/session.py`:
- `create_engine_from_url()` convierte URLs sync a async (`sqlite://` → `sqlite+aiosqlite://`, `postgresql://` → `postgresql+asyncpg://`)
- `create_tables()` crea el schema usando `SQLModel.metadata.create_all`
- `get_session()` yielda un `AsyncSession` como context manager

En `src/main.py`, el factory `create_app()` decide el backend por scheme de URL y crea el engine una sola vez en el lifespan.

## Alternativas consideradas

- **SQLAlchemy 2.0 async puro**: Más control, pero sin la integración automática con Pydantic v2. Requiere definir schemas separados. Descartado por el boilerplate extra.
- **Tortoise ORM**: Maduro para async, pero ecosistema más pequeño, sin integración Pydantic nativa, y no es el "camino oficial" de FastAPI. Descartado.
- **`databases` (encode)**: Ligero, pero sin ORM — solo query builder. Pierde type safety y migraciones. Descartado.
- **Raw asyncpg/aiosqlite**: Máximo control y performance, pero sin abstracción de BD. Cambiar de SQLite a PostgreSQL requiere reescribir queries. Descartado.

## Consecuencias

**Más fácil**: Los modelos SQL se definen una vez y sirven para queries, validación Pydantic, y serialización JSON. La integración FastAPI-SQLModel es fluida. Migraciones futuras con Alembic son directas (SQLModel genera el metadata).

**Más difícil**: SQLModel está en 0.x — la API puede cambiar entre versiones. Hay edge cases donde SQLAlchemy puro es necesario (composite keys en `FavoriteModel` requieren `Field(primary_key=True)` en ambos campos). `from __future__ import annotations` es necesario en ~55 archivos para compatibilidad con generics.

**Riesgos**: Dependencia de un proyecto joven (SQLModel). Si se abandona, la migración a SQLAlchemy puro es factible pero requiere reescribir los modelos. Mitigación: los mappers aíslan el dominio del cambio.
