# Build stage
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy only workspace configuration files first (for better layer caching)
COPY pyproject.toml uv.lock ./
COPY LICENSE README.md ./

# Copy all package directories (before installing to ensure they're available)
COPY test-coverage-mcp/ ./test-coverage-mcp/
COPY test-coverage-mcp-codecov/ ./test-coverage-mcp-codecov/

# Create virtual environment and install dependencies
RUN uv sync --locked

# Final stage
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    SERVER_PORT=8000

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy workspace
COPY --from=builder /app/test-coverage-mcp ./test-coverage-mcp
COPY --from=builder /app/test-coverage-mcp-codecov ./test-coverage-mcp-codecov
COPY pyproject.toml uv.lock ./

# Copy entrypoint script
COPY scripts/docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE ${SERVER_PORT}

# Environment variables for server configuration
ENV TRANSPORT=sse \
    HOST=0.0.0.0 \
    PORT=8000 \
    INTEGRATED=true \
    LOG_LEVEL=info \
    RELOAD=false

# Entry point script handles dynamic configuration via environment variables
ENTRYPOINT ["/app/entrypoint.sh"]
