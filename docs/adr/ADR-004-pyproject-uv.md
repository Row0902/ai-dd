# ADR-004: pyproject.toml como fuente única + uv

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

El ecosistema Python tiene múltiples formas de declarar dependencias: `requirements.txt`, `setup.py`, `setup.cfg`, `pyproject.toml`. Históricamente, los proyectos mantenían varios archivos que se desincronizaban — `requirements.txt` con versiones pinnadas que no coincidían con `setup.cfg`, o `dev-requirements.txt` separado que se olvidaba de actualizar.

El CI necesita reproducibilidad exacta: el mismo conjunto de paquetes con las mismas versiones en cada ejecución. Sin un lock file, `pip install` podía resolver versiones diferentes en distintos momentos.

## Decisión

`pyproject.toml` como única fuente de verdad para todo:

- **Dependencias runtime**: sección `[project] dependencies` (FastAPI, SQLModel, bcrypt, PyJWT, etc.)
- **Dependencias dev**: sección `[dependency-groups] dev` (pytest, ruff, ty)
- **Configuración de herramientas**: `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.ty]` — todo en el mismo archivo
- **Gestor de dependencias**: `uv` (astral-sh) — `uv sync --frozen` en CI garantiza que se instale exactamente lo que dice `uv.lock`
- **Lock file**: `uv.lock` commiteado al repo

El `Dockerfile` copia `pyproject.toml` y `uv.lock` primero (cache de capas), luego `uv sync --no-dev --frozen` para producción.

## Alternativas consideradas

- **pip + requirements.txt**: El estándar de facto, pero sin lock file nativo. `pip freeze` genera un lock, pero no distingue entre dependencias directas y transitivas. Descartado por la falta de reproducibilidad.
- **Poetry**: Popular, con lock file y gestión de dependencias. Pero más lento que uv, genera `poetry.lock` que es ruidoso en diffs, y tiene opiniones fuertes sobre packaging. Descartado por la velocidad.
- **PDM**: Similar a Poetry pero más moderno. Menos adopción en el ecosistema. Descartado por el tamaño de la comunidad.

## Consecuencias

**Más fácil**: Un solo archivo para todo — dependencias, configuración de linters, pytest, type checker. `uv sync` es ~10x más rápido que `pip install`. El CI es determinista con `--frozen`. El Dockerfile usa la misma herramienta que el desarrollo.

**Más difícil**: `uv` es relativamente nuevo (astral-sh). Si se abandona, migrar a pip/poetry requiere generar un `requirements.txt` desde `uv.lock`. El equipo necesita tener `uv` instalado (no viene con Python).

**Riesgos**: `uv` no es parte del estándar PEP — es un tool de terceros. Si astral-sh cambia la API, puede romper el CI. Mitigación: `uv` genera `uv.lock` en un formato estándar, y `pip install -r requirements.txt` sigue siendo un fallback si se exporta.
