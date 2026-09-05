#!/usr/bin/env bash
set -e

# Docker entrypoint for FoodFlow.
# - Waits for Postgres + Redis (when configured via DATABASE_URL / REDIS_URL).
# - Runs migrations + collectstatic.
# - Execs the CMD (default: gunicorn ASGI server).

DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_USER="${POSTGRES_USER:-foodflow}"
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

wait_for_postgres() {
  # Only wait when DATABASE_URL looks like postgres.
  if [[ "${DATABASE_URL:-}" == postgres* ]]; then
    echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT}..."
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
      echo "Postgres unavailable - sleeping 1s"
      sleep 1
    done
    echo "Postgres is up."
  fi
}

wait_for_redis() {
  # Only wait when Redis URLs point at the compose `redis` host.
  if [[ "${REDIS_URL:-}" == *"redis"* ]] || [[ "${CELERY_BROKER_URL:-}" == *"redis"* ]]; then
    echo "Waiting for Redis at ${REDIS_HOST}:${REDIS_PORT}..."
    until python -c "import socket; s=socket.create_connection(('${REDIS_HOST}', ${REDIS_PORT}), timeout=2); s.close()" 2>/dev/null; do
      echo "Redis unavailable - sleeping 1s"
      sleep 1
    done
    echo "Redis is up."
  fi
}

wait_for_postgres
wait_for_redis

# Only the web server should run migrations/collectstatic.
# Concurrent `migrate` from web + celery worker + beat on a fresh DB causes
# UniqueViolation races (pg_type_typname_nsp_index). Auto-detect web commands,
# overridable via RUN_MIGRATIONS=1/0.
SHOULD_MIGRATE=0
if [ "${RUN_MIGRATIONS:-auto}" = "1" ]; then
  SHOULD_MIGRATE=1
elif [ "${RUN_MIGRATIONS:-auto}" = "0" ]; then
  SHOULD_MIGRATE=0
else
  case "$*" in
    *gunicorn*|*runserver*|*uvicorn*|*daphne*) SHOULD_MIGRATE=1 ;;
  esac
fi

if [ "$SHOULD_MIGRATE" = "1" ]; then
  echo "Running Django checks..."
  python manage.py check

  echo "Applying database migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput --clear
else
  echo "Skipping migrations/collectstatic (RUN_MIGRATIONS=${RUN_MIGRATIONS:-auto}, cmd: $*)"
fi

echo "Starting: $*"
exec "$@"
