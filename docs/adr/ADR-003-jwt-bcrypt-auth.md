# ADR-003: JWT HS256 + bcrypt sobre OAuth2/OIDC

**Fecha**: 2026-05-05
**Estado**: Aceptado

## Contexto

ai-dd es una API REST para un equipo interno, sin frontend SPA complejo ni necesidad de federación de identidad. Se requería autenticación stateless para proteger endpoints y autorización basada en roles (admin/user) para controlar acceso.

El flujo de registro es por invitación: un admin genera un token UUID4, el nuevo usuario se registra con ese token. No hay registro abierto.

## Decisión

Implementamos autenticación con JWT HS256 y bcrypt:

- **Tokens**: `JwtTokenService` (`src/infrastructure/auth/jwt_token_service.py`) firma tokens con HS256 usando un secreto compartido (`SECRET_KEY` en `AppSettings`). Payload: `{sub: user_id, role: role, iat, exp}`. Expiración configurable (default 30 min).
- **Passwords**: `BcryptPasswordHasher` (`src/infrastructure/auth/bcrypt_password_hasher.py`) con rounds=12. Implementa el puerto abstracto `PasswordHasher` del dominio.
- **Roles**: `UserRole` enum (`ADMIN`, `USER`) en `src/domain/auth/entities.py`. El middleware de auth (`src/api/middleware/auth.py`) extrae el rol del JWT y lo inyecta en el request.
- **RBAC**: Los casos de uso verifican permisos usando `src/domain/auth/permissions.py`. Un admin bypassa ownership checks; un user solo accede a sus propios recursos.

Los puertos abstractos (`TokenService`, `PasswordHasher`, `UserRepository`, `InvitationRepository`) viven en `src/domain/auth/ports.py` — el dominio no conoce PyJWT ni bcrypt.

## Alternativas consideradas

- **OAuth2/OIDC (Google, GitHub)**: Apropiado para apps con usuarios externos. Overkill para una API interna de equipo. Requiere configurar providers, redirect URIs, y manejar tokens de terceros. Descartado.
- **API Keys**: Simple, pero sin expiración automática, sin payload con claims (rol), y sin estándar amplio. Descartado por la falta de estructura.
- **Sessions con cookies**: Stateful — requiere almacenar sesiones (Redis/BD). Contradice el diseño REST stateless. Descartado.

## Consecuencias

**Más fácil**: Implementación completa en ~150 líneas. Sin dependencias externas (no necesita un auth server). Los tests mockean `TokenService` y `PasswordHasher` por ser puertos abstractos.

**Más difícil**: Sin refresh tokens — el cliente re-autentica al expirar el token. Sin revocación de tokens individuales (un token válido hasta que expira). Sin OAuth2 scopes granulares.

**Riesgos**: Si `SECRET_KEY` se compromete, todos los tokens son falsificables. Mitigación: validación de longitud mínima (32 chars) en `AppSettings.secret_key_min_length()`, y `.env` en `.gitignore`. Para un equipo pequeño con rotación de secretos, el riesgo es aceptable.
