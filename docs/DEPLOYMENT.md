# Guía de Despliegue — ai-dd

> Cómo desplegar ai-dd en desarrollo, staging y producción.

---

## Desarrollo Local

### Sin Docker (más rápido para iterar)

```bash
uv sync
DATABASE_URL=sqlite:///./dev.db uv run uvicorn src.main:create_app --factory --reload
```

El backend por defecto es `memory://` (en memoria, sin persistencia). Para desarrollo con persistencia local usa `sqlite:///./dev.db`. La app se recarga automáticamente con `--reload`.

### Con Docker (PostgreSQL + Redis)

```bash
docker compose -f docker/docker-compose.yml up -d
```

Esto levanta PostgreSQL, Redis y la aplicación en un solo comando. La app usa las variables de entorno definidas en el compose:

```
DATABASE_URL=postgresql://ai_dd_user:ai_dd_pass@postgres:5432/ai_dd
REDIS_URL=redis://redis:6379/0
```

### Solo infraestructura (sin la app)

Si preferís correr la app nativamente pero usar PostgreSQL y Redis en contenedores:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

Luego:

```bash
DATABASE_URL=postgresql://ai_dd_user:ai_dd_pass@localhost:5432/ai_dd \
REDIS_URL=redis://localhost:6379/0 \
uv run uvicorn src.main:create_app --factory --reload
```

---

## Docker

### Servicios

| Servicio  | Imagen               | Puerto | Propósito                        |
|-----------|----------------------|--------|----------------------------------|
| app       | (build local)        | 8000   | API FastAPI                      |
| postgres  | `postgres:18-alpine` | 5432   | Base de datos relacional         |
| redis     | `redis:7-alpine`     | 6379   | Caché / sesiones (append-only)   |

### Dockerfile

Build de una sola etapa basado en `python:3.13-slim`. Decisiones clave:

1. **Base slim**: imagen mínima (~50 MB) — reduce superficie de ataque y tamaño final.
2. **UV como gestor de paquetes**: copiado desde `ghcr.io/astral-sh/uv:latest` vía `COPY --from`. Instalación de dependencias 10-100× más rápida que pip.
3. **`--no-dev` en prod**: solo dependencias de runtime — pytest, ruff, ty no entran en la imagen.
4. **`--frozen`**: reproduce exactamente el `uv.lock` — builds determinísticos.
5. **Entrypoint con `uv run`**: activa el venv automáticamente sin necesidad de activarlo manualmente.

```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables de Entorno (en el contenedor)

| Variable                    | Default (compose)                                                                 | Notas                                  |
|-----------------------------|------------------------------------------------------------------------------------|----------------------------------------|
| `DATABASE_URL`              | `postgresql://ai_dd_user:ai_dd_pass@postgres:5432/ai_dd`                          | Conexión a PostgreSQL en el compose    |
| `REDIS_URL`                 | `redis://redis:6379/0`                                                             | Conexión a Redis en el compose         |
| `SECRET_KEY`                | `${SECRET_KEY:-change-me-to-a-secret-key-at-least-32-characters-long}`             | Sobrescribir desde `.env` o shell      |
| `ENV`                       | `${ENV:-development}`                                                              | `production` activa logs JSON          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | (usa default: 30)                                                                | TTL de tokens JWT                      |
| `CORS_ORIGINS`              | (usa default: `["http://localhost:3000"]`)                                         | Lista JSON de orígenes permitidos      |
| `LOG_LEVEL`                 | (usa default: `INFO`)                                                              | Nivel de logging Python                |

### Build y Run Manual

```bash
# Build
docker build -t ai-dd .

# Run con archivo .env
docker run -p 8000:8000 --env-file .env ai-dd

# Run pasando variables directamente
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/ai_dd \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -e ENV=production \
  ai-dd
```

---

## docker-compose.yml

El compose orquesta tres servicios interconectados a través de una red `books-network` (driver `bridge`).

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│   app    │────▶│ postgres │     │  redis   │
│  :8000   │     │  :5432   │     │  :6379   │
└──────────┘     └──────────┘     └──────────┘
      │                │                 │
      └────────────────┴─────────────────┘
                books-network (bridge)
```

### Topología

- **app** depende de `postgres` y `redis` con `condition: service_healthy` — no arranca hasta que ambos estén listos.
- **postgres** y **redis** exponen sus puertos al host para desarrollo local (`5432` y `6379`).
- Los healthchecks usan `pg_isready` (PostgreSQL) y `redis-cli ping` (Redis) cada 10s.

### Volúmenes

| Volumen         | Driver | Contenido                       |
|-----------------|--------|---------------------------------|
| `postgres_data` | local  | Datos de PostgreSQL             |
| `redis_data`    | local  | Datos de Redis (AOF habilitado) |

Los volúmenes persisten entre reinicios. Para limpiar todo:

```bash
docker compose -f docker/docker-compose.yml down -v
```

### Perfiles de despliegue

Actualmente no hay perfiles (`profiles`) definidos — el compose levanta todos los servicios por igual. Para desarrollo sin la app:

```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

### Archivos de servicios incluidos

El compose principal usa la directiva `include` para componer servicios desde archivos separados:

```
docker/docker-compose.yml
  ├── docker/services/postgres.yml   → servicio postgres + volumen + red
  └── docker/services/redis.yml      → servicio redis + volumen + red
```

Esto permite reutilizar las definiciones de infraestructura en otros contextos (CI, staging, etc.).

---

## Variables de Entorno

### Obligatorias en producción

| Variable                    | Ejemplo producción                                      | Notas                                                      |
|-----------------------------|---------------------------------------------------------|------------------------------------------------------------|
| `SECRET_KEY`                | (generar con `openssl rand -hex 32`)                    | Mínimo 32 caracteres. Validado por `AppSettings`.          |
| `DATABASE_URL`              | `postgresql+asyncpg://user:pass@host:5432/ai_dd`        | PostgreSQL con driver asyncpg. Nunca `memory://` o sqlite. |
| `ENV`                       | `production`                                            | Activa JSON logging vía structlog.                         |

### Opcionales

| Variable                    | Default                          | Descripción                                    |
|-----------------------------|----------------------------------|------------------------------------------------|
| `REDIS_URL`                 | `redis://localhost:6379/0`       | Conexión a Redis para caché/sesiones           |
| `CORS_ORIGINS`              | `["http://localhost:3000"]`      | Lista JSON de orígenes permitidos por CORS     |
| `LOG_LEVEL`                 | `INFO`                           | Nivel de logging (DEBUG, INFO, WARNING, ERROR) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                           | Duración de tokens JWT en minutos              |

### Generar SECRET_KEY

```bash
openssl rand -hex 32
# o:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Nunca uses el valor por defecto (`dev-secret-key-change-in-production-32chars`) fuera de desarrollo local. Es público, está en el código fuente y no ofrece seguridad real.

---

## CI/CD

### GitHub Actions

El workflow de CI (`.github/workflows/ci.yml`) se ejecuta en:

| Evento             | Qué hace                              |
|--------------------|---------------------------------------|
| Push a `main`      | Tests + lint + type check             |
| Push a `develop`   | Tests + lint + type check             |
| Pull Request       | Tests + lint + type check             |

### Matrix de versiones

Se testea contra Python **3.13** y **3.14** en paralelo. Ambas versiones están especificadas como soportadas (`requires-python = ">=3.13"` en `pyproject.toml`).

### Pasos del pipeline

1. **Checkout** — `actions/checkout@v4`
2. **Setup Python** — `actions/setup-python@v5` con la versión de la matrix
3. **Setup uv** — `astral-sh/setup-uv` con caché habilitada
4. **Instalar dependencias** — `uv sync --frozen` (instala dev + prod)
5. **Tests** — `uv run pytest -x -q` (se detiene en el primer fallo)
6. **Type check** — `uv run ty check src/` (modo `all = "error"`)
7. **Lint** — `ruff check` vía `astral-sh/ruff-action`

---

## Producción

### Checklist pre-deploy

- [ ] `SECRET_KEY` generado (≥ 32 caracteres, único por entorno)
- [ ] `DATABASE_URL` apunta a PostgreSQL (no `memory://`, no SQLite)
- [ ] `ENV=production` (activa JSON logging y desactiva debug)
- [ ] `CORS_ORIGINS` restringido a dominios reales (no `["*"]`)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` ajustado según política de seguridad
- [ ] Archivo `.env` **no** commiteado (está en `.gitignore`)
- [ ] SSL/TLS terminado en reverse proxy (nginx, traefik, Caddy)
- [ ] Puerto `8000` no expuesto directamente a internet

### Reverse Proxy (nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Health Check

```bash
# Éxito (HTTP 200)
curl https://api.example.com/health
# {"status": "ok", "database": "up"}

# Falla de base de datos (HTTP 503)
# {"status": "error", "database": "down"}
```

El endpoint `/health` prueba conectividad real con la base de datos ejecutando una consulta ligera (`list(limit=1)`). Ideal para probes de liveness y readiness en Kubernetes o balanceadores de carga.

---

## Monitoreo

### Logs

**structlog** emite JSON en producción (`ENV=production`) y texto formateado en desarrollo. Esto permite integración directa con agregadores de logs.

Campos clave en cada entrada de log:

| Campo          | Ejemplo                    | Descripción                          |
|----------------|----------------------------|--------------------------------------|
| `event`        | `"request.completed"`      | Tipo de evento                       |
| `request_id`   | `"abc123..."`              | ID único de request (middleware)     |
| `duration_ms`  | `42.3`                     | Duración del request en milisegundos |
| `status_code`  | `200`                      | Código HTTP de respuesta             |
| `path`         | `"/api/books"`             | Ruta solicitada                      |
| `method`       | `"GET"`                    | Método HTTP                          |

Los logs se escriben a **stdout/stderr**. Redirigilos a tu agregador preferido:

- **Datadog**: Datadog Agent con `docker` o `journald` integration
- **ELK**: Filebeat → Logstash → Elasticsearch
- **Loki**: Promtail → Loki (con Grafana para visualización)
- **Docker**: `docker logs ai-dd-app` para acceso directo

### Métricas (futuro)

Métricas candidatas a exponer vía endpoint `/metrics` (Prometheus):

- `http_requests_total` — contador de requests por método y ruta
- `http_request_duration_seconds` — histograma de latencia (p50, p95, p99)
- `http_errors_total` — contador de errores por código de estado
- `db_connections_active` — conexiones activas a PostgreSQL
- `redis_commands_total` — comandos ejecutados contra Redis

---

## Backup y Recuperación

### PostgreSQL

```bash
# Backup completo
pg_dump "$DATABASE_URL" > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Backup comprimido
pg_dump "$DATABASE_URL" | gzip > "backup_$(date +%Y%m%d_%H%M%S).sql.gz"

# Restore
psql "$DATABASE_URL" < backup_20260505_120000.sql

# Restore desde comprimido
gunzip -c backup_20260505_120000.sql.gz | psql "$DATABASE_URL"
```

### Redis

Redis está configurado con `appendonly yes` (AOF), lo que garantiza durabilidad de los datos en disco. El volumen `redis_data` contiene el archivo `appendonly.aof`.

```bash
# Backup del volumen Redis
docker run --rm -v ai-dd_redis_data:/data -v $(pwd):/backup alpine \
  cp /data/appendonly.aof /backup/redis_backup_$(date +%Y%m%d).aof
```

### Automatización

Programá backups diarios con cron:

```bash
# /etc/cron.d/ai-dd-backup
0 2 * * * root pg_dump "postgresql://..." | gzip > /backups/ai-dd_$(date +\%Y\%m\%d).sql.gz
```

---

## Seguridad

- [ ] `SECRET_KEY` nunca en código fuente — usar variables de entorno o un gestor de secretos (Vault, AWS Secrets Manager)
- [ ] HTTPS en producción (TLS 1.2+) — terminar SSL en reverse proxy, nunca exponer HTTP plano
- [ ] Rate limiting por IP/endpoint (a implementar — usar slowapi o middleware custom)
- [ ] Dependencias actualizadas regularmente:
  ```bash
  uv lock --upgrade      # actualiza uv.lock a últimas versiones
  uv sync --frozen       # instala exactamente lo que dice el lock
  ```
- [ ] Escaneo de vulnerabilidades en dependencias:
  ```bash
  pip-audit              # escanea dependencias instaladas contra advisory DB
  # o vía CI:
  uv run pip-audit
  ```
- [ ] Contraseña de PostgreSQL y Redis **no** en valores por defecto del compose en producción
- [ ] Volúmenes de Docker con backups regulares (ver sección Backup)
- [ ] La imagen base `python:3.13-slim` se actualiza periódicamente — rebuild para incorporar parches de seguridad
