# Build stage
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy workspace configuration
COPY pyproject.toml uv.lock ./
COPY LICENSE README.md ./

# Copy all package directories
COPY test-coverage-mcp/ ./test-coverage-mcp/
COPY test-coverage-mcp-codecov/ ./test-coverage-mcp-codecov/

# Create virtual environment and install all workspace packages
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --locked

# Final stage
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    SERVER_PORT=8000

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy workspace
COPY --from=builder /app/test-coverage-mcp ./test-coverage-mcp
COPY --from=builder /app/test-coverage-mcp-codecov ./test-coverage-mcp-codecov
COPY pyproject.toml uv.lock ./

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE ${SERVER_PORT}

# Entry point runs core package in integrated mode (MCP + webhook server)
# Uses SSE transport for HTTP-based MCP clients
CMD ["test-coverage-mcp", "--integrated", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
