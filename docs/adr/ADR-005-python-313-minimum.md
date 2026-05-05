# ADR-005: Python 3.13 como versión mínima

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

El proyecto originalmente soportaba `>=3.11`. Python 3.13 se lanzó como estable en octubre de 2024, trayendo mejoras significativas en performance (5-15% vs 3.11 según benchmarks de la PSF) y nuevas características de tipado. El CI matrix actual es `[3.13, 3.14]`.

## Decisión

Establecemos Python 3.13 como versión mínima (`requires-python = ">=3.13"` en `pyproject.toml`).

Características aprovechadas:
- **PEP 695**: Type parameter syntax nativa (`type Alias = int` en vez de `Alias = TypeVar(...)`)
- **PEP 698**: Decorador `@override` para métodos que sobreescriben padres
- **Performance**: Mejoras en el intérprete CPython (5-15% vs 3.11)
- **Error messages**: Tracebacks más precisos y mensajes de error mejorados

La CI matrix en GitHub Actions testea contra `[3.13, 3.14]` para detectar problemas de compatibilidad tempranos.

## Alternativas consideradas

- **Mantener 3.11**: Máxima compatibilidad con sistemas que no han migrado. Pero 3.11 pierde soporte de seguridad en octubre de 2027, y no tiene PEP 695/698. Descartado por no aprovechar mejoras modernas.
- **Subir a 3.14**: Muy nuevo (en desarrollo). Dependencias de terceros pueden no soportarlo aún. Descartado por estabilidad.

## Consecuencias

**Más fácil**: Sintaxis de tipado más limpia a medida que se refactoriza. Mejor performance sin cambios de código. Mensajes de error más claros durante desarrollo.

**Más difícil**: `from __future__ import annotations` sigue presente en ~55 archivos como vestigio de la compatibilidad con versiones anteriores. Se puede eliminar cuando se confirme que no se necesita soporte para 3.12-. Usuarios en sistemas con Python 3.11 o anterior no pueden ejecutar el proyecto sin un version manager (pyenv, uv python).

**Riesgos**: Entornos corporativos con Python 3.11 fijo no pueden usar el proyecto directamente. Mitigación: Docker (`python:3.13-slim` en el Dockerfile) abstrae la versión del host.
