#!/bin/bash
# Entrypoint script for test-coverage-mcp Docker container
# Accepts environment variables to configure MCP server startup

set -e

# Default values
TRANSPORT="${TRANSPORT:-sse}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
INTEGRATED="${INTEGRATED:-true}"
LOG_LEVEL="${LOG_LEVEL:-info}"
RELOAD="${RELOAD:-false}"

# Build command arguments
CMD_ARGS=()

# Add integrated mode flag
if [ "$INTEGRATED" = "true" ]; then
    CMD_ARGS+=("--integrated")
fi

# Add transport
CMD_ARGS+=("--transport" "$TRANSPORT")

# Add host and port
CMD_ARGS+=("--host" "$HOST")
CMD_ARGS+=("--port" "$PORT")

# Add log level
CMD_ARGS+=("--log-level" "$LOG_LEVEL")

# Add reload flag if enabled
if [ "$RELOAD" = "true" ]; then
    CMD_ARGS+=("--reload")
fi

# Execute the MCP server with built arguments
exec test-coverage-mcp "${CMD_ARGS[@]}"
