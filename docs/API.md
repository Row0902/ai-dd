# API Reference — ai-dd

> **Base URL:** `http://localhost:8000` · **OpenAPI:** `/docs` · **Auth:** Bearer JWT
>
> ai-dd es una API REST para gestión de libros, colecciones y favoritos con autenticación JWT y control de acceso basado en roles (RBAC).

---

## Quick Start

Tres comandos para verificar que la API funciona:

```bash
# 1. Health check (sin auth)
curl http://localhost:8000/health

# 2. Registrar usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "secreto123"}'

# 3. Login y guardar token
export TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "secreto123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token listo: ${TOKEN:0:20}..."
```

---

## Autenticación

### Flujo JWT

1. **`POST /auth/register`** — crea una cuenta de usuario.
2. **`POST /auth/login`** — devuelve un `access_token` JWT firmado con HS256.
3. **Endpoints protegidos** — incluir `Authorization: Bearer <token>` en cada request.

### Estructura del token

El JWT contiene estos claims:

| Claim | Significado |
|-------|-------------|
| `sub` | ID del usuario (UUID) |
| `role` | Rol: `"admin"` o `"user"` |
| `iat` | Timestamp de emisión (epoch) |
| `exp` | Timestamp de expiración (epoch) |

### Duración

- **Default:** 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- Al expirar se recibe **401 Unauthorized** con `"detail": "token has expired"`.
- No hay refresh token — el cliente debe volver a hacer login.

### Cómo usar el token

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/books
```

### Roles y permisos

| Rol | Permisos |
|-----|----------|
| `admin` | Todas las operaciones (`book:*`, `collection:*`, `favorite:*`). Omite verificaciones de propiedad. |
| `user` | Todas las operaciones. La propiedad se verifica a nivel de caso de uso (solo puede modificar/eliminar sus propias colecciones). |

> **Nota:** actualmente ambos roles tienen el mismo conjunto de permisos. La diferencia está en la capa de aplicación: `admin` puede ver/modificar cualquier colección; `user` solo las suyas.

---

## Endpoints

---

### Health

Ruta base: `/`

| Método | Ruta | Auth | Código | Descripción |
|--------|------|------|--------|-------------|
| `GET` | `/` | No | 200 | Mensaje raíz de la API |
| `GET` | `/health` | No | 200 / 503 | Health check con sonda de base de datos |

**GET /** — Raíz

```bash
curl http://localhost:8000/
```

**Response 200:**
```json
{"msg": "AI Driven Development - biblioteca digital"}
```

---

**GET /health** — Health check

```bash
curl http://localhost:8000/health
```

**Response 200** (base de datos responde):
```json
{"status": "ok", "database": "up"}
```

**Response 503** (base de datos caída):
```json
{"status": "error", "database": "down"}
```

---

### Auth

Ruta base: `/auth`

| Método | Ruta | Auth | Código | Descripción |
|--------|------|------|--------|-------------|
| `POST` | `/auth/register` | No | 201 | Registrar nuevo usuario |
| `POST` | `/auth/login` | No | 200 | Iniciar sesión, obtener JWT |
| `POST` | `/auth/invitations` | Sí (`book:create`) | 201 | Crear invitación (admin) |

---

**POST /auth/register** — Registro

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "alicia@example.com", "password": "claveSecreta42"}'
```

**Body:**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `email` | string | ✅ | Email válido |
| `password` | string | ✅ | — |
| `invitation_token` | string | ❌ | Token de invitación (si el registro es por invitación) |

**Response 201:**
```json
{
  "id": "a1b2c3d4e5f6...",
  "email": "alicia@example.com",
  "role": "user",
  "is_active": true
}
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 409 | Email ya registrado | `{"detail": "Email already registered"}` |
| 422 | Token de invitación inválido/expirado | `{"detail": "..."}` |
| 422 | Validación de body fallida | `{"detail": [{"loc": ["body", "email"], "msg": "...", "type": "..."}]}` |

---

**POST /auth/login** — Inicio de sesión

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alicia@example.com", "password": "claveSecreta42"}'
```

**Body:**

| Campo | Tipo | Requerido |
|-------|------|-----------|
| `email` | string | ✅ |
| `password` | string | ✅ |

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 401 | Credenciales inválidas | `{"detail": "Invalid credentials"}` |
| 422 | Validación de body fallida | `{"detail": [{"loc": ["body", "email"], "msg": "...", "type": "..."}]}` |

---

**POST /auth/invitations** — Crear invitación

Requiere autenticación con permiso `book:create` (admin).

```bash
curl -X POST http://localhost:8000/auth/invitations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "nuevo@example.com", "role": "user"}'
```

**Body:**

| Campo | Tipo | Requerido | Valores válidos |
|-------|------|-----------|-----------------|
| `email` | string | ✅ | Email del invitado |
| `role` | string | ✅ | `"admin"` o `"user"` |

**Response 201:**
```json
{
  "id": "inv-uuid-aqui",
  "token": "token-uuid-aqui",
  "email": "nuevo@example.com",
  "role": "user",
  "expires_at": "2026-05-12T07:00:00+00:00"
}
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 400 | Rol inválido | `{"detail": "Invalid role: superadmin. Must be 'admin' or 'user'."}` |
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |
| 422 | Validación de body fallida | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |

---

### Books

Ruta base: `/books`

| Método | Ruta | Auth | Código | Descripción |
|--------|------|------|--------|-------------|
| `GET` | `/books` | Sí (`book:read`) | 200 | Listar libros con paginación |
| `GET` | `/books/{book_id}` | Sí (`book:read`) | 200 | Obtener libro por ID |
| `GET` | `/books/by-name/{name}` | Sí (`book:read`) | 200 | Buscar libros por nombre |
| `POST` | `/books` | Sí (`book:create`) | 201 | Crear libro |
| `PUT` | `/books/{book_id}` | Sí (`book:update`) | 200 | Reemplazar libro |
| `DELETE` | `/books/{book_id}` | Sí (`book:delete`) | 204 | Eliminar libro |

---

**GET /books** — Listar libros

Parámetros de query opcionales:

| Parámetro | Tipo | Default | Restricción |
|-----------|------|---------|-------------|
| `limit` | int | 20 | 1–100 |
| `offset` | int | 0 | ≥ 0 |

```bash
curl "http://localhost:8000/books?limit=5&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

**Response 200:**
```json
[
  {
    "id": "abc123",
    "name": "Clean Code",
    "author": "Robert C. Martin",
    "description": "A handbook of agile software craftsmanship",
    "url": "https://example.com/clean-code",
    "content": "Even bad code can function..."
  },
  {
    "id": "def456",
    "name": "Domain-Driven Design",
    "author": "Eric Evans",
    "description": "",
    "url": "",
    "content": ""
  }
]
```

> **Nota:** si no hay libros, la respuesta es `[]` (array vacío, no 404).

---

**GET /books/{book_id}** — Obtener libro

```bash
curl http://localhost:8000/books/abc123 \
  -H "Authorization: Bearer $TOKEN"
```

**Response 200:**
```json
{
  "id": "abc123",
  "name": "Clean Code",
  "author": "Robert C. Martin",
  "description": "A handbook of agile software craftsmanship",
  "url": "https://example.com/clean-code",
  "content": "Even bad code can function..."
}
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 404 | Libro no encontrado | `{"detail": "Not found"}` |
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |

---

**GET /books/by-name/{name}** — Buscar por nombre

Búsqueda case-insensitive de substrings. El `name` va en la URL (no como query param).

```bash
curl http://localhost:8000/books/by-name/clean \
  -H "Authorization: Bearer $TOKEN"
```

**Response 200:**
```json
[
  {
    "id": "abc123",
    "name": "Clean Code",
    "author": "Robert C. Martin",
    "description": "A handbook of agile software craftsmanship",
    "url": "https://example.com/clean-code",
    "content": "Even bad code can function..."
  }
]
```

> **Nota:** si no hay coincidencias, la respuesta es `[]`.

---

**POST /books** — Crear libro

```bash
curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean Code",
    "author": "Robert C. Martin",
    "description": "A handbook of agile software craftsmanship",
    "url": "https://example.com/clean-code",
    "content": "Even bad code can function..."
  }'
```

**Body (BookPayload):**

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| `name` | string | ✅ | No vacío, máx. 200 caracteres |
| `author` | string | ❌ | Máx. 150 caracteres |
| `description` | string | ❌ | Texto libre |
| `url` | string | ❌ | URL válida (scheme + netloc), máx. 2048 caracteres |
| `content` | string | ❌ | Texto libre |

**Response 201:**
```json
{
  "id": "abc123",
  "name": "Clean Code",
  "author": "Robert C. Martin",
  "description": "A handbook of agile software craftsmanship",
  "url": "https://example.com/clean-code",
  "content": "Even bad code can function..."
}
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |
| 422 | `name` vacío | `{"detail": [{"field": "name", "message": "Name cannot be empty or whitespace"}]}` |
| 422 | `name` excede 200 chars | `{"detail": [{"field": "name", "message": "Name exceeds maximum length of 200 characters"}]}` |
| 422 | `author` excede 150 chars | `{"detail": [{"field": "author", "message": "Author exceeds maximum length of 150 characters"}]}` |
| 422 | URL mal formada | `{"detail": [{"field": "url", "message": "Invalid URL format"}]}` |
| 422 | URL excede 2048 chars | `{"detail": [{"field": "url", "message": "URL exceeds maximum length of 2048 characters"}]}` |
| 422 | Validación Pydantic (body incompleto) | `{"detail": [{"loc": ["body", "name"], "msg": "field required", "type": "missing"}]}` |

---

**PUT /books/{book_id}** — Reemplazar libro

Reemplazo completo (semántica PUT). Todos los campos se sobrescriben — usa el body entero aunque solo cambies un campo.

```bash
curl -X PUT http://localhost:8000/books/abc123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean Code: Second Edition",
    "author": "Robert C. Martin",
    "description": "Updated edition",
    "url": "https://example.com/clean-code-v2",
    "content": "Updated content here..."
  }'
```

**Body:** Igual que `POST /books` (BookPayload).

**Response 200:**
```json
{
  "id": "abc123",
  "name": "Clean Code: Second Edition",
  "author": "Robert C. Martin",
  "description": "Updated edition",
  "url": "https://example.com/clean-code-v2",
  "content": "Updated content here..."
}
```

**Errores:** Mismos que `POST /books`, más:

| Status | Condición | Body |
|--------|-----------|------|
| 404 | Libro no encontrado | `{"detail": "Not found"}` |

---

**DELETE /books/{book_id}** — Eliminar libro

```bash
curl -X DELETE http://localhost:8000/books/abc123 \
  -H "Authorization: Bearer $TOKEN"
```

**Response 204:** Sin body.

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 404 | Libro no encontrado | `{"detail": "Not found"}` |
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |

---

### Collections

Ruta base: `/collections`

| Método | Ruta | Auth | Código | Descripción |
|--------|------|------|--------|-------------|
| `POST` | `/collections` | Sí (`collection:create`) | 201 | Crear colección |
| `GET` | `/collections` | Sí (`collection:read`) | 200 | Listar colecciones |
| `DELETE` | `/collections/{collection_id}` | Sí (`collection:delete`) | 204 | Eliminar colección |

---

**POST /collections** — Crear colección

```bash
curl -X POST http://localhost:8000/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Favoritos 2026", "description": "Lo mejor del año"}'
```

**Body:**

| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `name` | string | ✅ | — |
| `description` | string | ❌ | `""` |

**Response 201:**
```json
{
  "id": "col-uuid-aqui",
  "name": "Favoritos 2026",
  "description": "Lo mejor del año",
  "owner_id": "user-uuid-aqui",
  "book_ids": [],
  "created_at": "2026-05-05T12:00:00+00:00",
  "updated_at": "2026-05-05T12:00:00+00:00"
}
```

---

**GET /collections** — Listar colecciones

- **Admin:** ve todas las colecciones del sistema.
- **User:** ve solo las colecciones propias (donde `owner_id` coincide con su `user_id`).

```bash
curl http://localhost:8000/collections \
  -H "Authorization: Bearer $TOKEN"
```

**Response 200:**
```json
[
  {
    "id": "col-uuid-aqui",
    "name": "Favoritos 2026",
    "description": "Lo mejor del año",
    "owner_id": "user-uuid-aqui",
    "book_ids": ["abc123", "def456"],
    "created_at": "2026-05-05T12:00:00+00:00",
    "updated_at": "2026-05-06T08:30:00+00:00"
  }
]
```

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |

---

**DELETE /collections/{collection_id}** — Eliminar colección

Solo el dueño de la colección o un admin pueden eliminarla.

```bash
curl -X DELETE http://localhost:8000/collections/col-uuid-aqui \
  -H "Authorization: Bearer $TOKEN"
```

**Response 204:** Sin body.

**Errores:**

| Status | Condición | Body |
|--------|-----------|------|
| 404 | Colección no encontrada o no eres dueño | `{"detail": "Not found"}` |
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |

---

### Favorites

Ruta base: `/favorites`

| Método | Ruta | Auth | Código | Descripción |
|--------|------|------|--------|-------------|
| `POST` | `/favorites/{book_id}` | Sí (`favorite:add`) | 201 | Agregar a favoritos |
| `DELETE` | `/favorites/{book_id}` | Sí (`favorite:remove`) | 204 | Quitar de favoritos |
| `GET` | `/favorites` | Sí (`collection:read`) | 200 | Listar IDs de favoritos |

> **Nota:** `GET /favorites` requiere el permiso `collection:read` (no `favorite:*`). Esto es intencional — los favoritos se tratan como una colección implícita del usuario.

---

**POST /favorites/{book_id}** — Agregar a favoritos

Operación **idempotente**: si el libro ya está en favoritos, no hace nada y retorna 201 igual.

```bash
curl -X POST http://localhost:8000/favorites/abc123 \
  -H "Authorization: Bearer $TOKEN"
```

**Response 201:** Sin body.

---

**DELETE /favorites/{book_id}** — Quitar de favoritos

Operación **idempotente**: si el libro no estaba en favoritos, retorna 204 igual.

```bash
curl -X DELETE http://localhost:8000/favorites/abc123 \
  -H "Authorization: Bearer $TOKEN"
```

**Response 204:** Sin body.

---

**GET /favorites** — Listar favoritos

Retorna solo los **IDs** de libros, no los objetos completos. El orden es cronológico inverso (más recientes primero).

```bash
curl http://localhost:8000/favorites \
  -H "Authorization: Bearer $TOKEN"
```

**Response 200:**
```json
["def456", "abc123"]
```

> **Para obtener los datos completos de cada libro**, usa `GET /books/{book_id}` por cada ID favorito.

**Errores (todos los endpoints de favorites):**

| Status | Condición | Body |
|--------|-----------|------|
| 401 | Token inválido/expirado | `{"detail": "Invalid or expired token"}` |
| 403 | Sin permiso | `{"detail": "Insufficient permissions"}` |

---

## Referencia de permisos

Cada endpoint declara el permiso exacto que requiere. Los permisos se definen como strings `resource:action` en `domain.auth.permissions.Operation`:

| Permiso | Valor | Endpoints que lo usan |
|---------|-------|----------------------|
| `BOOK_CREATE` | `book:create` | `POST /books`, `POST /auth/invitations` |
| `BOOK_READ` | `book:read` | `GET /books`, `GET /books/{id}`, `GET /books/by-name/{name}` |
| `BOOK_UPDATE` | `book:update` | `PUT /books/{id}` |
| `BOOK_DELETE` | `book:delete` | `DELETE /books/{id}` |
| `COLLECTION_CREATE` | `collection:create` | `POST /collections` |
| `COLLECTION_READ` | `collection:read` | `GET /collections`, `GET /favorites` |
| `COLLECTION_UPDATE` | `collection:update` | *(no usado actualmente)* |
| `COLLECTION_DELETE` | `collection:delete` | `DELETE /collections/{id}` |
| `FAVORITE_ADD` | `favorite:add` | `POST /favorites/{book_id}` |
| `FAVORITE_REMOVE` | `favorite:remove` | `DELETE /favorites/{book_id}` |

---

## Formato de errores

Todos los errores siguen una estructura consistente:

```json
{"detail": "mensaje descriptivo"}
```

**Error 422 de dominio** (validación del lado del servidor):
```json
{
  "detail": [
    {"field": "name", "message": "Name cannot be empty or whitespace"}
  ]
}
```

**Error 422 de Pydantic** (validación de FastAPI):
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "missing"
    }
  ]
}
```

> **Atención:** el formato de `detail` en 422 **varía** según quién genera el error:
> - Errores de dominio → array de `{field, message}`.
> - Errores de Pydantic → array de `{loc, msg, type}`.
> - Ambos son status 422 pero tienen estructura diferente. Tu cliente debe manejar ambas.

---

## Complete Flow Example

Flujo completo: registro → login → crear libro → crear colección → agregar favorito → listar favoritos.

```bash
# ── 1. Registrar ──────────────────────────────────────
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "secreto123"}'

# → {"id":"...","email":"dev@example.com","role":"user","is_active":true}

# ── 2. Login (guardar token) ──────────────────────────
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@example.com", "password": "secreto123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# ── 3. Crear libro ────────────────────────────────────
BOOK=$(curl -s -X POST http://localhost:8000/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Domain-Driven Design", "author": "Eric Evans"}')

BOOK_ID=$(echo "$BOOK" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Libro creado: $BOOK_ID"

# ── 4. Crear colección ────────────────────────────────
COL=$(curl -s -X POST http://localhost:8000/collections \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Arquitectura", "description": "Libros de arquitectura de software"}')

COL_ID=$(echo "$COL" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Colección creada: $COL_ID"

# ── 5. Agregar a favoritos ───────────────────────────
curl -s -X POST http://localhost:8000/favorites/$BOOK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -o /dev/null -w "Favorito: %{http_code}\n"

# ── 6. Listar favoritos ──────────────────────────────
curl -s http://localhost:8000/favorites \
  -H "Authorization: Bearer $TOKEN"

# → ["abc123"]  (IDs de libros favoritos)

# ── 7. Listar libros con paginación ──────────────────
curl -s "http://localhost:8000/books?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# ── 8. Eliminar libro ────────────────────────────────
curl -s -X DELETE http://localhost:8000/books/$BOOK_ID \
  -H "Authorization: Bearer $TOKEN" \
  -o /dev/null -w "Delete: %{http_code}\n"
```

---

## Rate Limiting

La API aplica rate limiting per-IP usando Redis Sorted Sets (sliding window). Cada endpoint tiene su propio límite independiente.

### Límites por endpoint

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `POST /auth/login` | 5 requests | 60 segundos |
| `POST /auth/register` | 3 requests | 60 segundos |
| Todos los demás endpoints protegidos | 100 requests | 60 segundos |
| `GET /health` | Sin límite | — |

### Headers de respuesta

Todas las respuestas incluyen headers del estándar IETF draft:

| Header | Descripción |
|--------|-------------|
| `RateLimit-Limit` | Máximo de requests permitidos en la ventana |
| `RateLimit-Remaining` | Requests restantes en la ventana actual |
| `RateLimit-Reset` | Timestamp Unix de cuándo se reinicia la ventana |

### Respuesta 429

Cuando se excede el límite:

```json
{"detail": "Too many requests"}
```

Headers adicionales en 429:

| Header | Descripción |
|--------|-------------|
| `Retry-After` | Segundos hasta que el cliente puede reintentar |

### Configuración

Los límites se configuran vía variables de entorno:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | `true` | Habilitar/deshabilitar rate limiting |
| `RATE_LIMIT_FAIL_OPEN` | `true` | Permitir tráfico si Redis no está disponible |
| `RATE_LIMIT_LOGIN_MAX` | `5` | Máximo requests para login |
| `RATE_LIMIT_LOGIN_WINDOW` | `60` | Ventana para login (segundos) |
| `RATE_LIMIT_REGISTER_MAX` | `3` | Máximo requests para register |
| `RATE_LIMIT_REGISTER_WINDOW` | `60` | Ventana para register (segundos) |
| `RATE_LIMIT_GLOBAL_MAX` | `100` | Máximo requests para endpoints globales |
| `RATE_LIMIT_GLOBAL_WINDOW` | `60` | Ventana para endpoints globales (segundos) |

### Comportamiento fail-open

Si Redis no está disponible, las requests pasan normalmente (fail-open). Rate limiting es calidad de servicio, no seguridad — la disponibilidad tiene prioridad.

---

## CORS

La API acepta requests cross-origen desde los orígenes configurados en `CORS_ORIGINS` (variable de entorno, default `["http://localhost:3000"]`). Todos los métodos y headers están permitidos.

---

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| `1.0` | 2026-05-05 | API inicial: health, auth (register, login, invitations), books CRUD, collections CRUD, favorites. Autenticación JWT con RBAC. |
