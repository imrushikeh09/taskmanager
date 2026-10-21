# ==============================================================================
# Multi-Stage Production Dockerfile for Task Manager Enterprise Backend
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Environment (Compiles dependencies & wheels)
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

# Set build environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install system compilation dependencies required for building C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Build Python wheels for fast, clean installation in the final stage
COPY requirements.txt .
RUN pip wheel --wheel-dir /build/wheels -r requirements.txt


# ------------------------------------------------------------------------------
# Stage 2: Final Runtime Environment (Ultra-lean, minimal attack surface)
# ------------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runner

# Set production runtime environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Install runtime system libraries (libpq5 for PostgreSQL client, postgresql-client for pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Principle of Least Privilege: Create dedicated non-root application user
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash -m appuser

# Install pre-compiled wheels from builder stage
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application code into container
COPY --chown=appuser:appgroup . /app

# Ensure staticfiles and media directories exist with appropriate permissions
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app/staticfiles /app/media

# Switch from root to unprivileged application user
USER appuser

# Expose standard application port
EXPOSE 8000

# Set entrypoint script for readiness checks & signal forwarding
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command executed through entrypoint
CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]

