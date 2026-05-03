# Biblioteca Digital — Kata de Refactorización

> Aplicación educativa FastAPI diseñada como **kata de refactorización**. Parte de un monolito intencionalmente imperfecto y evoluciona hacia Clean Architecture + SOLID mediante asistencia de IA.

---

## Tabla de contenidos

- [Inicio rápido](#inicio-rápido)
- [Qué vas a aprender](#qué-vas-a-aprender)
- [El punto de partida](#el-punto-de-partida)
- [La consigna](#la-consigna)
- [Hoja de ruta paso a paso](#hoja-de-ruta-paso-a-paso)
- [Arquitectura objetivo](#arquitectura-objetivo)
- [Testing](#testing)
- [Herramientas](#herramientas)
- [Entrega](#entrega)
- [FAQ y troubleshooting](#faq-y-troubleshooting)

---

## Inicio rápido

Ejecuta la app en **3 comandos** para ver el estado inicial:

```bash
# 1. Crear entorno e instalar dependencias
uv sync

# 2. Levantar la app
uv run fastapi dev src/main.py

# 3. Abrir en navegador
open http://localhost:8000/docs
```

> Si no usas `uv`, activa un virtualenv e instala con `pip install -r requirements.txt`.

---

## Qué vas a aprender

| Concepto | Qué significa en este proyecto |
|----------|-------------------------------|
| **Clean Architecture** | Separar dominio, aplicación, infraestructura y presentación en capas independientes |
| **SOLID** | Aplicar SRP (una clase/función, una razón para cambiar), DIP (dependencias apuntan hacia el dominio) y OCP (extensión sin modificación) |
| **Polimorfismo** | Usar protocolos/ABC para inyectar validadores composables |
| **Value Objects** | Encapsular reglas de negocio en objetos inmutables que se auto-validan |
| **TDD** | Escribir el test primero, hacerlo pasar, refactorizar |
| **Pydantic validators** | Validar en el límite HTTP antes de que los datos entren al dominio |
| **Pruebas automatizadas** | Cobertura de unitarias (lógica de negocio) e integración (endpoints) |

---

## El punto de partida

`src/main.py` es un **monolito de 118 líneas** que hace todo:

- Define el modelo Pydantic `Book`
- Lee y escribe `library.json` (I/O bloqueante)
- Implementa los 6 endpoints directamente
- Sin capas, sin validación de dominio, sin abstracciones

### Malas prácticas intencionales

- [ ] Todo en un solo archivo (`src/main.py`)
- [ ] I/O bloqueante sin locks (race conditions potenciales)
- [ ] Persistencia en JSON (sin esquema ni transacciones)
- [ ] Sin validación de dominio (solo tipos Pydantic)
- [ ] Sin docstrings
- [ ] Sin tests
- [ ] Sin manejo de errores estructurado
- [ ] Sin variables de entorno configurables

---

## La consigna

Refactoriza la app aplicando **Clean Architecture + SOLID + TDD**. Tu meta no es "hacer que funcione" — ya funciona. Tu meta es **hacer que sea mantenible, testeable y extensible**.

### Requisitos obligatorios

1. **Clean Architecture**  
   Separar en 4 capas: `domain/`, `application/`, `infrastructure/`, `api/`. El dominio NO depende de ninguna otra capa.

2. **Validación polimórfica**  
   Crear un protocolo `Validator[T]` con validadores concretos (uno por archivo). Componerlos con `CompositeValidator`. Inyectar el validador en los casos de uso como parámetro opcional.

3. **Value Objects**  
   Extraer `BookName`, `BookAuthor`, `BookUrl` como objetos inmutables que validan en su constructor. La entidad `Book` debe componer estos VOs.

4. **Base de datos relacional**  
   Reemplazar `library.json` por SQLite o PostgreSQL usando SQLModel o SQLAlchemy.

5. **Tests**  
   - Unitarios: lógica de dominio (validadores, VOs, entidades)
   - Integración: endpoints HTTP
   - Cobertura mínima: endpoints principales + lógica de negocio

6. **Calidad de código**  
   - Google Docstrings en **todas** las funciones y clases públicas
   - `ruff check` y `ruff format` sin errores
   - `ty check` sin errores de tipo

### Requisitos opcionales (suman puntos)

- [ ] Agregar logging estructurado
- [ ] Usar variables de entorno (`.env`) para configuración
- [ ] Implementar migraciones con Alembic
- [ ] Agregar rate limiting o autenticación básica
- [ ] Documentar decisiones técnicas en `ARCHITECTURE.md`

---

## Hoja de ruta paso a paso

No intentes hacer todo de una. Sigue este orden:

### Paso 1 — Extraer el dominio (sin tocar FastAPI)

```
domain/
├── entities.py          # Book (composición de VOs)
├── exceptions.py        # DomainError, ValidationError
├── repositories.py      # BookRepository (ABC)
├── validators/
│   ├── protocol.py      # Validator[T]
│   ├── book_name.py     # BookNameValidator
│   ├── book_author.py   # BookAuthorValidator
│   ├── book_url.py      # BookUrlValidator
│   └── composite.py     # CompositeValidator
└── value_objects/
    ├── book_name.py     # BookName
    ├── book_author.py   # BookAuthor
    └── book_url.py      # BookUrl
```

> **Regla:** cada archivo ≤ 300 líneas, cada función ≤ 20 líneas.

### Paso 2 — Casos de uso (orquestación)

```
application/
└── use_cases/
    ├── create_book.py
    ├── read_book.py
    ├── list_books.py
    ├── search_books.py
    ├── update_book.py
    ├── replace_book.py
    └── delete_book.py
```

Cada caso de uso recibe un `Validator[Book] | None = None` y valida antes de persistir.

### Paso 3 — Infraestructura (persistencia + serialización)

```
infrastructure/
├── json_book_repository.py    # o sql_book_repository.py
└── serializers/
    └── json_book_serializer.py
```

Extraer la serialización del repositorio (SRP).

### Paso 4 — API (presentación)

```
api/
├── schemas.py         # BookPayload con @field_validator
├── routers/
│   └── books.py       # Endpoints FastAPI
├── dependencies.py    # Inyección de dependencias
└── mappers.py         # BookPayload <-> Book
```

Agregar `@field_validator` en `BookPayload` como **primera línea de defensa**.

### Paso 5 — Tests

```
tests/
├── conftest.py
├── unit/
│   ├── test_validators.py
│   ├── test_value_objects.py
│   ├── test_domain_entities.py
│   ├── test_book_use_cases.py
│   └── test_json_book_repository.py
└── integration/
    └── test_books_api.py
```

> **Recuerda:** `tests/` va en la raíz, no dentro de `src/`.

---

## Arquitectura objetivo

### Diagrama de capas

```
┌─────────────────────────────────────┐
│  API Layer (FastAPI)                │
│  schemas.py, routers/books.py       │
├─────────────────────────────────────┤
│  Application Layer                  │
│  use_cases/ (orquestación)          │
├─────────────────────────────────────┤
│  Domain Layer (sin dependencias)    │
│  entities, validators, VOs          │
├─────────────────────────────────────┤
│  Infrastructure Layer               │
│  repositories, serializers, BD      │
└─────────────────────────────────────┘
```

**Regla de oro:** las flechas de dependencia apuntan **hacia adentro** (hacia el dominio). El dominio no sabe nada de FastAPI, JSON ni SQL.

### Diagrama de flujo HTTP

```mermaid
flowchart LR
    Client[Cliente HTTP] -->|POST /books| Router[api/routers/books.py]
    Router -->|BookPayload| Schema[api/schemas.py]
    Schema -->|valida| Pydantic[@field_validator]
    Schema -->|Book| UseCase[application/use_cases/]
    UseCase -->|valida| Validator[domain/validators/]
    UseCase -->|persiste| Repo[infrastructure/]
    Repo -->|SQL/JSON| DB[(SQLite/JSON)]
    UseCase -->|Book| Router
    Router -->|JSON| Client
```

---

## Testing

### Ejecutar tests

```bash
# Todos los tests
pytest -v

# Solo unitarios
pytest tests/unit/ -v

# Solo integración
pytest tests/integration/ -v

# Con cobertura
pytest --cov=src --cov-report=term-missing
```

### Estructura de un test unitario

```python
# tests/unit/test_validators.py
from domain.entities import Book
from domain.validators.book_name import BookNameValidator


def test_empty_name_returns_error():
    """Un nombre vacío produce un ValidationError."""
    book = Book(id="1", name="")
    errors = BookNameValidator().validate(book)
    assert len(errors) == 1
    assert errors[0].field == "name"
```

### Estructura de un test de integración

```python
# tests/integration/test_books_api.py
from fastapi.testclient import TestClient
from main import create_app


def test_post_book_returns_201(client):
    """POST /books crea un libro y devuelve 201."""
    response = client.post("/books", json={"name": "Clean Code"})
    assert response.status_code == 201
    assert response.json()["name"] == "Clean Code"
```

---

## Herramientas

| Herramienta | Para qué | Comando |
|-------------|----------|---------|
| **uv** | Gestor de dependencias y entornos | `uv sync`, `uv run pytest` |
| **pytest** | Testing framework | `pytest -v` |
| **ruff** | Linter + formateador | `ruff check .`, `ruff format .` |
| **ty** | Type checker | `ty check src/` |

### Configuración mínima de `pyproject.toml`

Ya viene configurado. No lo modifiques salvo que sepas lo que haces.

---

## Entrega

### Formato

1. Crea una **rama** desde `main`:
   ```bash
   git checkout -b feat/tu-nombre-refactor
   ```

2. Realiza **commits frecuentes** con mensajes descriptivos:
   ```bash
   git commit -m "feat(domain): add Validator protocol and concrete validators"
   ```

3. Crea un **Pull Request** a `main` con:
   - Título descriptivo: `Refactor: Clean Architecture + SOLID + Validation`
   - Descripción de cambios realizados
   - Screenshots o logs de tests pasando
   - Archivo `PROMPTS.md` con los prompts utilizados (ver formato abajo)

### PROMPTS.md

Documenta tus interacciones con la IA:

```markdown
# Prompts utilizados

## 1. Extracción del dominio
**Prompt:**
```
[Pega tu prompt exacto aquí]
```

**Resultado:**
- Creación de `domain/entities.py`
- Creación de `domain/validators/`

## 2. ... (continúa con cada paso importante)
```

### Checklist de entrega

- [ ] Rama creada desde `main`
- [ ] Clean Architecture aplicada (4 capas separadas)
- [ ] Validación polimórfica con CompositeValidator
- [ ] Value Objects (BookName, BookAuthor, BookUrl)
- [ ] SQLModel o SQLAlchemy integrado
- [ ] Tests unitarios + integración funcionales
- [ ] Google Docstrings en todo el código público
- [ ] `ruff check` sin errores
- [ ] `PROMPTS.md` adjunto
- [ ] Pull Request enviada

**Deadline:** Martes 26 de mayo de 2026

---

## FAQ y troubleshooting

### "No se ejecuta la app"

```bash
# Verificar entorno
uv sync
uv run fastapi dev src/main.py

# Si usas pip
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
fastapi dev src/main.py
```

### "Error de importación de módulos"

- `pythonpath = ["src"]` ya está configurado en `pyproject.toml`
- Si usas VS Code, asegúrate de que el Python interpreter apunte al `.venv`

### "pytest no encuentra los tests"

```bash
# Los tests deben estar en tests/ (raíz), no en src/test/
ls tests/unit/test_*.py
pytest -v
```

### "Ruff marca errores de formato"

```bash
uv run ruff format .   # auto-formatea
uv run ruff check .    # verifica
```

### "ty marca errores en tests"

Algunos tests deliberadamente provocan errores (ej: mutar frozen dataclasses). Estos deben tener `# ty: ignore[codigo]`:

```python
name.value = "other"  # ty: ignore[invalid-assignment]
```

---

## Recursos oficiales

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
- [pytest](https://docs.pytest.org/)
- [ruff](https://docs.astral.sh/ruff/)
- [ty](https://docs.astral.sh/ty/)
- [uv](https://docs.astral.sh/uv/)
- [Clean Architecture — Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

> **Nota:** Repositorio para fines educativos. No usar en producción.
