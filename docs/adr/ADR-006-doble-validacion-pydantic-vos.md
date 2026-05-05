# ADR-006: Doble validación (Pydantic + Domain VOs)

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

La validación ocurre en dos fronteras: el request HTTP (¿el JSON es válido?) y la entidad de dominio (¿cumple reglas de negocio?). Pydantic valida formatos en la API; los Value Objects garantizan invariantes en el dominio. ¿Validamos en un solo lugar o en ambos?

## Decisión

Doble validación con una fuente única de verdad para las constantes:

1. **API Layer** (`src/api/schemas.py`): `BookPayload` (Pydantic `BaseModel`) valida formatos en el boundary HTTP — campos requeridos, tipos, longitudes máximas, formato URL. Usa `@field_validator` con constantes importadas de `domain.validation_rules`.

2. **Domain Layer** (`src/domain/value_objects/`): `BookName`, `BookAuthor`, `BookUrl` (`@dataclass(frozen=True)`) validan reglas de negocio en construcción — non-empty, trimming, longitudes. Importan las mismas constantes de `domain.validation_rules`.

3. **Single Source of Truth** (`src/domain/validation_rules.py`): `MAX_TITLE_LENGTH=200`, `MAX_AUTHOR_LENGTH=150`, `MAX_URL_LENGTH=2048`, `ISBN_PATTERN`, `RULES_VERSION`. Ambas capas importan de aquí — cambiar un límite se hace en un solo lugar.

El flujo: HTTP request → `BookPayload` (Pydantic) → `CreateBook` use case → `Book(id, name, ...)` construye `BookName(name)` que valida again. Si Pydantic falla, el usuario ve 422. Si el VO falla, es un bug interno (no debería llegar ahí).

## Alternativas consideradas

- **Solo Pydantic, sin VOs**: Menos código, pero el dominio no se protege a sí mismo. Si alguien crea un `Book` directamente (sin pasar por la API), no hay validación. Descartado por la pérdida de defensa en profundidad.
- **Solo VOs, sin Pydantic**: El dominio valida, pero la API no tiene validación declarativa. Los errores HTTP serían exceptions genéricas en vez de 422 estructurado. Descartado por la experiencia del consumidor de la API.
- **Validación solo en BD**: Constraints de base de datos como última línea de defensa. Pero los errores de BD son genéricos y difíciles de mapear a campos del formulario. Descartado como estrategia primaria (se mantiene como safety net).

## Consecuencias

**Más fácil**: Cambiar un límite de validación se hace en `validation_rules.py` y se propaga a ambas capas. Los VOs son inmutables (`frozen=True`) — no hay estado inválido posible. Los tests del dominio no necesitan mock de Pydantic.

**Más difícil**: Algunas validaciones se duplican intencionalmente (e.g., `name` se valida en `BookPayload.name_must_not_be_empty` Y en `BookName.__post_init__`). Mantener la consistencia requiere que ambos importen de `validation_rules`.

**Riesgos**: Si alguien agrega una constante de validación inline (sin importar de `validation_rules.py`), las capas se desincronizan. Mitigación: ruff lint rules que detectan magic numbers, y code review.
