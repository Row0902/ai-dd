## 📚 Biblioteca Digital - AI Driven Development

Aplicacion FastAPI intencionalmente simple y con malas practicas. Todo el codigo esta en `src/main.py` y la persistencia actual se hace en `src/library.json` mediante I/O bloqueante sin locks. Esta base sirve como punto de partida para un refactor completo guiado por IA.

## 🎯 Objetivo del proyecto

Debes refactorizar la app aplicando Clean Architecture, Clean Code y principios SOLID. Tu meta es separar la logica de negocio de la persistencia, reemplazar el archivo JSON por una base de datos (SQLite o PostgreSQL) e integrar pruebas automatizadas.

## 📋 Dependencias y herramientas

Este proyecto se creo con **uv**. Incluyo `requirements.txt` para quienes no usan uv.

**Runtime:**
- [FastAPI](https://fastapi.tiangolo.com/) - framework web moderno
- [SQLModel](https://sqlmodel.tiangolo.com/#requirements) o [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) - ORM para la base de datos
  - SQLModel combina Pydantic + SQLAlchemy
  - SQLAlchemy se instala automaticamente con SQLModel
  - Puedes usar cualquiera de los dos

**Desarrollo:**
- [pytest](https://docs.pytest.org/en/stable/) - testing framework
- [ruff](https://docs.astral.sh/ruff/) - linter y formateador ultrarapido
- [ty](https://docs.astral.sh/ty/) - type checker

Ruff y Ty son **opcionales**. Si decides no usarlos, puedes eliminarlos o comentarlos en `pyproject.toml` y `requirements.txt`.

**Gestor de dependencias:**
- [uv](https://docs.astral.sh/uv/) - gestor de paquetes ultrarapido

## 📊 Diagrama de la aplicacion (estado actual)

```mermaid
flowchart TD
  Client[Cliente HTTP]
  Swagger[Swagger UI<br/>localhost:8000/docs]
  ReDoc[ReDoc<br/>localhost:8000/redoc]
  
  Client -->|GET /books| FastAPI[FastAPI App<br/>src/main.py]
  Client -->|GET /books/:id| FastAPI
  Client -->|GET /books/by-name/:name| FastAPI
  Client -->|POST /books| FastAPI
  Client -->|PUT /books/:id| FastAPI
  Client -->|DELETE /books/:id| FastAPI
  
  FastAPI -->|lectura/escritura| JSON[library.json<br/>I/O bloqueante]
  FastAPI -->|documentacion| Swagger
  FastAPI -->|documentacion| ReDoc
  
  style JSON fill:#f9f,stroke:#333,stroke-width:2px
  style Client fill:#e1f5ff,stroke:#01579b
  style FastAPI fill:#fff3e0,stroke:#e65100,stroke-width:2px
  style Swagger fill:#f3e5f5,stroke:#4a148c
  style ReDoc fill:#f3e5f5,stroke:#4a148c
```

**Diagrama esperado despues del refactor (con ORM y BD):**

```mermaid
flowchart TD
  Client[Cliente HTTP]
  Swagger[Swagger UI<br/>localhost:8000/docs]
  
  Client -->|HTTP Requests| FastAPI[FastAPI App<br/>src/main.py]
  FastAPI -->|documentacion| Swagger
  
  FastAPI -->|Servicios| Domain[Capa de Dominio<br/>src/domain/]
  Domain -->|Repositorio| Repository[Capa de Persistencia<br/>src/infrastructure/]
  Repository -->|SQLModel/SQLAlchemy ORM| Database[(SQLite/PostgreSQL)]
  
  Tests[Pruebas pytest<br/>src/test/]
  Tests -.->|unit tests| Domain
  Tests -.->|integration tests| Repository
  
  style Database fill:#4caf50,stroke:#1b5e20,stroke-width:2px,color:#fff
  style Domain fill:#2196f3,stroke:#0d47a1,stroke-width:2px,color:#fff
  style Repository fill:#ff9800,stroke:#e65100,stroke-width:2px,color:#fff
  style Tests fill:#9c27b0,stroke:#4a148c,stroke-width:2px,color:#fff
  style FastAPI fill:#fff3e0,stroke:#e65100,stroke-width:2px
```

## 📁 Estructura actual

- `src/main.py` — app FastAPI (unico archivo)
- `src/library.json` — almacenamiento persistente (se crea al ejecutar la app)
- `src/test/` — carpeta para pruebas (vacia, la llenarás durante el refactor)

## 🏗️ Estructura esperada post-refactor (Clean Architecture)

Puedes organizar tu proyecto de la siguiente manera como referencia:

```
proyecto/
├── src/
│   ├── domain/              # Logica de negocio (entidades, interfaces)
│   │   ├── models.py        # Entidades de dominio
│   │   └── services.py      # Servicios de negocio
│   ├── infrastructure/      # Persistencia y configuracion externa
│   │   ├── database.py      # Conexion a BD
│   │   └── repositories.py  # Implementacion de repositorios
│   ├── api/                 # Endpoints FastAPI
│   │   ├── routes.py        # Rutas
│   │   └── schemas.py       # Esquemas Pydantic
│   ├── test/                # Pruebas
│   │   ├── unit/            # Pruebas unitarias
│   │   ├── integration/     # Pruebas de integracion
│   │   └── conftest.py      # Fixtures compartidas
│   └── main.py              # Entrada de la app
├── .env                     # Variables de entorno (no commitar)
├── .env.example             # Plantilla de .env
├── pyproject.toml
└── requirements.txt
```

## 🚀 Instrucciones

### ✔️ Verificacion inicial

Antes de comenzar, verifica que la app actual funciona:

```bash
# Con uv
uv run fastapi dev src/main.py

# O con pip (tras activar entorno)
fastapi dev src/main.py
```

Debes ver: `Uvicorn running on http://127.0.0.1:8000`

Visita `http://localhost:8000/docs` para interactuar con la API.

### ⚙️ Ejecucion

#### Con uv (recomendado)

Sigue estos pasos en orden:

```bash
uv venv
uv sync
uv run fastapi dev src/main.py
```

Si activas el entorno virtual creado por uv, tambien puedes ejecutar:

```bash
fastapi dev src/main.py
```

Otros comandos utiles:

```bash
uv run pytest
uv run ruff format .
uv run ruff check .
uv run ty check .
```

#### Sin uv (pip tradicional)

1. Crea el entorno virtual:

**Windows (PowerShell):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate
```

**Windows (CMD):**
```bash
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instala dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la app:
```bash
fastapi dev src/main.py
```

Otros comandos utiles:

```bash
pytest
ruff format .
ruff check .
ty check .
```

### 🔧 Configuracion de variables de entorno

Crea un archivo `.env` en la raiz del proyecto (basate en `.env.example`):

```bash
DATABASE_URL=sqlite:///./library.db
# Para PostgreSQL: postgresql://user:password@localhost/dbname
DEBUG=True
```

Cargalas en tu codigo con `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
```

### 📝 Requisitos tecnicos de la entrega

1. **Clean Architecture:** Aplicar separacion clara de capas (dominio, aplicacion, infraestructura).
2. **Dependencias invertidas:** Los modelos de dominio no dependen de la persistencia.
3. **Base de datos:** Reemplazar `library.json` por **SQLite o PostgreSQL** usando **SQLModel o SQLAlchemy** como ORM.
4. **Pruebas:** Integrar pytest (unitarias e integracion). Cobertura minima: endpoints principales y logica de negocio.
5. **Documentacion:** Google Docstring en **todas las funciones/clases**. **No** usar comentarios inline.
6. **Decisiones tecnicas:** Documentar en README o docstrings.

### 🔄 Migracion a base de datos

Cuando refactorices con SQLModel o SQLAlchemy:

1. Define los modelos en `src/domain/models.py` con SQLModel o SQLAlchemy ORM.
2. Crea un script de migracion en `src/migrations/` o usa Alembic (opcional pero recomendado).
3. Configura la conexion a SQLite/PostgreSQL en `.env`.
4. Actualiza los endpoints para usar el ORM en lugar de I/O JSON.
5. Implementa un repositorio en `src/infrastructure/repositories.py` para centralizar acceso a datos.

**Ejemplo minimo de modelo SQLModel:**
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    author: str
    description: str = ""
    url: str = ""
    content: str = ""
```

**Ejemplo minimo de modelo SQLAlchemy:**
```python
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    author = Column(String)
    description = Column(String, default="")
    url = Column(String, default="")
    content = Column(String, default="")
```

### ✅ Pruebas

Las pruebas deben cubrir:

- Endpoints principales (GET, POST, PUT, DELETE)
- Logica de negocio (validaciones, busquedas)
- Casos de error (404, 400, etc.)

Estructura recomendada:

```python
# src/test/unit/test_services.py
def test_crear_libro():
    # Arrange, Act, Assert
    pass

# src/test/integration/test_api.py
def test_get_books_endpoint(client):
    response = client.get("/books")
    assert response.status_code == 200
```

Ejecuta:

```bash
pytest -v
pytest --cov=src
```

### 🔧 Flujo de GitHub (Ruff)

En `.github/workflows/ruff.yml` tienes un archivo vacio. Debes completar ese workflow para aplicar **formateo automatico con ruff** cuando envies cambios (push y Pull Request). El workflow debe ejecutar:

1. `ruff format --check` (verifica sin modificar; falla si hay cambios necesarios)
2. `ruff check` (lint)

**Recomendacion:** ejecuta `ruff format` localmente antes de hacer push para evitar fallos en CI.

Ejemplo minimo de job:
```yaml
name: Ruff Format & Lint
on: [push, pull_request]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: "format --check"
      - uses: astral-sh/ruff-action@v1
        with:
          args: "check"
```

### 📝 Malas practicas intencionales a refactorizar

El codigo base contiene deliberadamente:

- ✗ Todo en un archivo (sin separacion de capas)
- ✗ I/O bloqueante sin locks (race conditions)
- ✗ Almacenamiento en JSON (sin BD relacional)
- ✗ Sin validaciones robustas
- ✗ Sin docstrings (Google format)
- ✗ Sin pruebas
- ✗ Sin manejo de errores avanzado
- ✗ Sin logging estructurado
- ✗ Sin variables de entorno

Tu objetivo es **eliminar todas estas problemas** aplicando patrones profesionales.

### 📤 Entrega y evaluacion

**Deadline:** Antes de la ultima clase - **Martes 26 de mayo de 2026**

- **Trabajo individual** por defecto. Si deseas trabajar en equipo, solicita aprobacion a los instructores **via grupo** antes de comenzar.
- Se evaluara el **uso correcto de tecnicas de prompting**. Debes adjuntar los prompts utilizados durante tu interaccion con la IA junto con el proyecto modificado.
- Crea una **rama** desde `main` y envia una **Pull Request** con tus cambios y evidencia de los prompts.

**Como documentar los prompts:**

Crea un archivo `PROMPTS.md` en la raiz del proyecto:

```markdown
# Prompts utilizados - Refactor Biblioteca Digital

## 1. Arquitectura y estructura
**Prompt utilizado:**
\`\`\`
[Tu prompt aqui]
\`\`\`

**Resultado/Cambios:**
- Separacion de capas
- Creacion de modelos

## 2. Integracion con SQLModel
**Prompt utilizado:**
\`\`\`
[Tu prompt aqui]
\`\`\`

**Resultado/Cambios:**
- Modelos con SQLModel
- Sesion de BD

... continua con cada seccion importante
```

**Checklist de entrega:**
- [ ] Rama creada desde `main`
- [ ] Clean Architecture aplicada (separacion de capas)
- [ ] SQLModel o SQLAlchemy integrado con SQLite o PostgreSQL
- [ ] Pruebas automatizadas (pytest) funcionales
- [ ] Google Docstrings en todas las funciones/clases
- [ ] Ruff format sin errores
- [ ] Archivo `PROMPTS.md` con prompts adjuntos
- [ ] Pull Request enviada antes del 26 de mayo 2026
- [ ] PR con descripcion clara de cambios realizados

## 📖 Documentacion

### Documentacion interactiva de la API

La documentacion de la API esta disponible en: `http://localhost:8000/docs`

Swagger UI y ReDoc son generados automaticamente por FastAPI.

### Referencias de documentacion oficial

Durante el refactor, consulta la documentacion oficial:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Crear endpoints, validaciones, seguridad
- **[SQLModel](https://sqlmodel.tiangolo.com/#requirements)** - ORM basado en Pydantic y SQLAlchemy
- **[SQLAlchemy](https://docs.sqlalchemy.org/en/20/)** - ORM y operaciones avanzadas de BD
- **[pytest](https://docs.pytest.org/en/stable/)** - Testing framework
- **[ruff](https://docs.astral.sh/ruff/)** - Linter y formateador
- **[ty](https://docs.astral.sh/ty/)** - Type checker
- **[uv](https://docs.astral.sh/uv/)** - Gestor de dependencias

## ❓ Preguntas y soporte

**En caso de dudas:**

- Consulta a los **instructores via grupo** (preferido)
- Formular preguntas en el grupo permite que **todos tus companeros se beneficien** de la retroalimentacion
- Los instructores monitorearan el grupo regularmente
- Evita DMs privados para que la comunidad aprenda en conjunto

**Temas comunes:**
- Problemas con la BD: consulta la documentacion de SQLAlchemy
- Errores en pruebas: revisa los fixtures de pytest
- Formato de codigo: ejecuta `ruff format .` localmente
- Arquitectura: revisa los diagramas de este README

## 🐛 Troubleshooting

**"No se ejecuta la app"**
- Verifica que `uv venv` y `uv sync` se ejecutaron correctamente
- Comprueba que FastAPI esta instalado: `uv run pip list | grep fastapi`

**"Error de importacion de modulos"**
- Asegúrate de activar el entorno virtual
- Ejecuta `uv sync` nuevamente

**"Las pruebas no detectan los modelos"**
- Verifica la ruta en `sys.path` en `conftest.py`
- Usa rutas absolutas si es necesario

**"Ruff marca errores de formato"**
- Ejecuta `uv run ruff format .` para auto-formatear
- Revisa las reglas en `pyproject.toml`

## ℹ️ Nota

Repositorio para fines educativos - no usar en produccion.

