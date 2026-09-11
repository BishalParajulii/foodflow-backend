# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# System deps: build tools for wheels (uvicorn[standard], psycopg), curl for healthchecks,
# libpq-dev + postgresql-client (pg_isready) for DB readiness checks.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching).
COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install .

# Copy project source.
COPY . .

# Create non-root user and prepare runtime dirs.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/staticfiles /app/media /app/celerybeat \
    && chown -R appuser:appuser /app \
    && chmod +x /app/scripts/docker-entrypoint.sh

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

ENTRYPOINT ["scripts/docker-entrypoint.sh"]
CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-"]
