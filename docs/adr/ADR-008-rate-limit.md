# ADR-008: Rate Limiting per-IP con Redis Sorted Sets

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

La API no tenía protección contra abuso: un atacante podía hacer brute-force a `/auth/login` sin restricciones. Se necesitaba rate limiting per-endpoint que fuera configurable, resiliente a fallos de Redis, y que siguiera la Clean Architecture del proyecto.

Los requisitos clave:
- Proteger endpoints de auth (`/login` 5 req/60s, `/register` 3 req/60s).
- Rate limit global para el resto de endpoints (100 req/60s).
- Eximir `/health` (usado por load balancers).
- Fail-open: si Redis cae, el tráfico no se bloquea.
- Headers IETF draft (`RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`).

## Decisión

Implementamos rate limiting per-endpoint vía dependencia FastAPI (`require_rate_limit()`), siguiendo el patrón de `require_permission()`:

- **Algoritmo**: Sliding Window con Redis Sorted Sets. Pipeline atómico: `ZREMRANGEBYSCORE` → `ZCARD` → `ZADD` → `EXPIRE`. Evita el problema de burst-at-boundary de los fixed windows.
- **Inyección**: `Depends(require_rate_limit(max, window))` en cada endpoint. Permite granularidad por-endpoint sin middleware global.
- **Scope**: Per-IP, extraído de `X-Forwarded-For` (primer hop) o `request.client.host`.
- **Fail-open**: `RedisRateLimiter.check()` captura todas las excepciones y retorna `True` con warning log. Rate limiting es QoS, no security boundary.
- **NoOp fallback**: Cuando `RATE_LIMIT_ENABLED=False` o `DATABASE_URL=memory://`, se usa `NoOpRateLimiter` (sin Redis).
- **Puerto abstracto**: `RateLimiter` ABC en `domain/rate_limiting/ports.py` con `check()` y `reset()`. El dominio no conoce Redis ni FastAPI.
- **Headers**: Estándar IETF draft. Los 4 headers se setean en `_enforce_rate_limit()` y en el exception handler de `RateLimitExceededError`.

## Alternativas consideradas

- **Fixed Window (INCR + TTL)**: Más simple, pero vulnerable a burst-at-boundary. Un atacante puede hacer 5 requests al final de una ventana y 5 más al inicio de la siguiente = 10 en 2 segundos. Descartado.
- **Token Bucket**: Más flexible para permitir bursts controlados. Más complejo de implementar con Redis. Overkill para el caso de uso actual. Descartado.
- **Global middleware**: Un solo middleware para todos los endpoints. Pierde granularidad por-endpoint (login necesita 5/60s, books necesita 100/60s). Descartado.
- **Per-user rate limiting**: Más preciso (un usuario con múltiples IPs no se ve limitado). Requiere cambios en el pipeline de auth. Diferido a futuro.

## Consecuencias

**Más fácil**: Configuración vía variables de entorno (`RATE_LIMIT_LOGIN_MAX`, etc.) — sin cambios de código para ajustar límites. Rollback instantáneo: `RATE_LIMIT_ENABLED=False` convierte todo en NoOp. Tests usan `fakeredis` y un `CountingRateLimiter` en memoria.

**Más difícil**: `RateLimit-Remaining` es aproximado en respuestas exitosas (siempre muestra `max - 1` en lugar del conteo real). Corregir esto requeriría cambiar el ABC `RateLimiter.check()` de `bool` a un result object con `{allowed, remaining}` — se decidió no hacerlo en esta iteración para no romper la interfaz.

**Riesgos**: Si Redis se llena de keys (más IPs concurrentes que TTL), el consumo de memoria crece. Mitigación: `EXPIRE` en cada key con `window_seconds` como TTL. Para un equipo interno, el volumen es despreciable.
