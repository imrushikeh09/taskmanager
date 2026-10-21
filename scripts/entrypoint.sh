#!/bin/sh
set -e

# ==============================================================================
# Task Manager Container Entrypoint Script
# Provides deterministic startup, database readiness polling, migrations,
# and graceful Unix process handoff via exec.
# ==============================================================================

echo "==> [Entrypoint] Starting Task Manager container initialization..."

# 1. Database Readiness Check
if [ "$DB_HOST" ]; then
    echo "==> [Entrypoint] Probing PostgreSQL readiness at ${DB_HOST}:${DB_PORT:-5432}..."
    until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "${DB_USER:-taskmanager_user}"; do
        echo "--> [Entrypoint] PostgreSQL is unavailable - sleeping 1s..."
        sleep 1
    done
    echo "==> [Entrypoint] PostgreSQL is online and accepting connections!"
fi

# 2. Database Migrations (Only executed by web container, skipped by celery workers)
if [ "$AUTO_MIGRATE" = "true" ]; then
    echo "==> [Entrypoint] Running database migrations..."
    python manage.py migrate --noinput
    echo "==> [Entrypoint] Migrations completed successfully."
fi

# 3. Static Asset Collection
if [ "$COLLECT_STATIC" = "true" ]; then
    echo "==> [Entrypoint] Collecting static files..."
    python manage.py collectstatic --noinput
    echo "==> [Entrypoint] Static files collected."
fi

echo "==> [Entrypoint] Initialization complete. Passing control to container command: $@"

# 4. Process Handoff to PID 1 (Guarantees SIGTERM signal forwarding to Gunicorn/Celery)
exec "$@"
