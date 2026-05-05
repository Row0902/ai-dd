# ADR-007: Favorites como junction table sin entidad de dominio

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

Favoritos es una relación N:M entre usuarios y libros. Un usuario puede marcar N libros como favoritos, y un libro puede ser favorito de M usuarios. La pregunta de diseño: ¿esto merece una entidad de dominio completa con sus propios atributos, o es una operación de relación pura?

Las fuerzas en juego: simplicidad vs extensibilidad. Favoritos actualmente solo necesita saber "quién marcó qué y cuándo". No hay notas, tags, categorías, ni orden personalizado.

## Decisión

Favorites NO tiene entidad de dominio. Solo existe como:

1. **Puerto abstracto** (`src/domain/favorites/repositories.py`): `FavoriteRepository(ABC)` con tres métodos: `add(user_id, book_id)`, `remove(user_id, book_id)`, `list_by_user(user_id) → list[str]`. Opera con primitivos (`str`), no con objetos de dominio.

2. **Junction table SQL** (`src/infrastructure/persistence/favorite_models.py`): `FavoriteModel(SQLModel, table=True)` con composite primary key (`user_id`, `book_id`) y un timestamp `added_at`.

3. **Implementaciones**: `InMemoryFavoriteRepository` (dict con key `(user_id, book_id)` → `datetime`) para tests, `SQLFavoriteRepository` para producción.

El caso de uso `AddFavorite` (`src/application/use_cases/favorites/add_favorite.py`) recibe `user_id` y `book_id` como strings y delega al repositorio. No hay construcción de objetos `Favorite`.

## Alternativas consideradas

- **Entidad `Favorite` con metadatos**: Crear un `@dataclass Favorite` con `user_id`, `book_id`, `added_at`, `notes`, `tags`, `sort_order`. Más extensible, pero over-engineering para el caso actual. Descartado — se puede migrar después si se necesitan metadatos.
- **Queries SQL directas sin repositorio**: Los routers consultan la BD directamente. Violta Clean Architecture — la API no debe saber de SQL. Descartado.
- **Redis sets**: `SADD favorites:{user_id} book_id`. Rápido, pero sin persistencia garantizada, sin `added_at`, y acopla a Redis. Descartado como fuente primaria.

## Consecuencias

**Más fácil**: Tres métodos simples, sin constructores de entidad, sin Value Objects, sin mapper. Los tests son triviales (el `InMemoryFavoriteRepository` son 50 líneas). Agregar/quitar favoritos es una operación O(1) con la composite key.

**Más difícil**: `list_by_user` retorna `list[str]` (IDs de libros), no entidades `Book` completas. El router necesita hacer un segundo query para obtener los detalles del libro. Sin `Favorite` entity, no se puede agregar metadata (notas, tags) sin migración.

**Riesgos**: Si en el futuro se necesitan metadatos (notas por favorito, categorías, orden personalizado), hay que crear la entidad `Favorite`, su modelo SQL, mapper, y migrar la junction table. Mitigación: la composite key (`user_id`, `book_id`) se mantiene como base — la migración sería additive (agregar columnas, no cambiar PK).
