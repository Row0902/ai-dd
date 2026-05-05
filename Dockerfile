FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files for caching
COPY pyproject.toml uv.lock ./

# Install only production dependencies (no pytest, ruff, ty)
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application using uv run for proper venv activation
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
