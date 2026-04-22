# 🔬 Test Coverage MCP Server

[![Docker Pulls](https://img.shields.io/docker/pulls/chisanan232/test-coverage-mcp)](https://hub.docker.com/r/chisanan232/test-coverage-mcp)
[![Docker Image Size](https://img.shields.io/docker/image-size/chisanan232/test-coverage-mcp/latest)](https://hub.docker.com/r/chisanan232/test-coverage-mcp)
[![Docker Stars](https://img.shields.io/docker/stars/chisanan232/test-coverage-mcp)](https://hub.docker.com/r/chisanan232/test-coverage-mcp)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://github.com/python/mypy)

## 🔍 Overview

A provider-extensible MCP (Model Context Protocol) server for test coverage intelligence. Offers a stable capability-driven tool contract with provider-specific enrichments for analyzing and understanding test coverage reports from multiple sources.

## 🐳 Docker Usage

### 🚀 Quick Start

Pull the Docker image:

```bash
docker pull chisanan232/test-coverage-mcp:latest
```

Run the container with default configuration (integrated mode with SSE transport):

```bash
docker run -d -p 8000:8000 chisanan232/test-coverage-mcp
```

Access the health check endpoint at `http://localhost:8000/health`

### 🔧 Configuration Options

The Docker container can be configured using environment variables:

| Environment Variable | Description                                                     | Default   |
|----------------------|-----------------------------------------------------------------|-----------|
| `TRANSPORT`          | MCP transport mode (`sse`, `stdio`, `streamable-http`)          | `sse`     |
| `HOST`               | Host to bind the server to                                      | `0.0.0.0` |
| `PORT`               | Port to bind the server to                                      | `8000`    |
| `INTEGRATED`         | Run integrated mode (MCP + webhook server) (`true`/`false`)     | `true`    |
| `LOG_LEVEL`          | Logging level (`debug`, `info`, `warning`, `error`)             | `info`    |
| `RELOAD`             | Enable auto-reload for development (`true`/`false`)             | `false`   |

### 📝 Using Environment Variables

Configure the server by passing environment variables to the Docker container:

**Default configuration (integrated mode with SSE transport)**:
```bash
docker run -d -p 8000:8000 chisanan232/test-coverage-mcp
```

**Custom transport (stdio)**:
```bash
docker run -e TRANSPORT=stdio chisanan232/test-coverage-mcp
```

**Custom port**:
```bash
docker run -d -p 9000:9000 -e PORT=9000 chisanan232/test-coverage-mcp
```

**Standalone mode (MCP only, no webhook)**:
```bash
docker run -d -p 8000:8000 -e INTEGRATED=false chisanan232/test-coverage-mcp
```

**Debug logging**:
```bash
docker run -d -p 8000:8000 -e LOG_LEVEL=debug chisanan232/test-coverage-mcp
```

**Multiple configuration options**:
```bash
docker run -d -p 8000:8000 \
  -e TRANSPORT=sse \
  -e LOG_LEVEL=debug \
  -e INTEGRATED=true \
  chisanan232/test-coverage-mcp
```

### 🔍 Health Check

The container includes a health check endpoint at `/health` that can be used to verify the server is running correctly:

```bash
curl http://localhost:8000/health
```

### 📊 Accessing the Server

**MCP SSE Endpoint** (for HTTP-based MCP clients):
```bash
curl http://localhost:8000/sse
```

**Webhook Server** (when in integrated mode):
The webhook server is available at `http://localhost:8000` with health check at `/health`

## 📚 Python Usage

### Installation

Install the package and its dependencies using `uv`:

```bash
uv sync
```

Or with pip:

```bash
pip install -e test-coverage-mcp/
```

### Starting the server

Run the MCP server with default configuration:

```bash
test-coverage-mcp
```

### Command Line Options

The server accepts the following command line options:

- `--integrated`: Run in integrated mode (MCP + webhook server) (default: enabled)
- `--transport`: Transport protocol to use (`sse`, `stdio`, `streamable-http`) (default: `sse`)
- `--host`: Host to bind the server to (default: `0.0.0.0`)
- `--port`: Port to bind the server to (default: `8000`)
- `--log-level`: Logging level (`debug`, `info`, `warning`, `error`) (default: `info`)
- `--reload`: Enable auto-reload for development
- `--env-file`: Path to a custom .env file for environment variables (default: `.env`)

Examples:

**Run with SSE transport on port 8000**:
```bash
test-coverage-mcp --transport sse --port 8000
```

**Run in standalone mode (MCP only)**:
```bash
test-coverage-mcp --transport stdio
```

**Run with debug logging**:
```bash
test-coverage-mcp --log-level debug
```

**Run with custom configuration**:
```bash
test-coverage-mcp --integrated --transport sse --host 0.0.0.0 --port 9000 --log-level debug
```

## 📋 Requirements

- Python 3.12+
- Docker (for container deployment)
- uv (recommended for development)

## 🌟 Features

- 🔬 Provider-extensible architecture for multiple coverage sources
- 🔄 Multiple transport protocols (SSE, stdio, HTTP streaming)
- 🎯 Stable capability-driven tool contract
- 🚀 Fast and efficient FastAPI implementation
- 📊 Comprehensive test coverage analysis
- 🔌 Plugin system for provider discovery
- 🏥 Health check endpoints
- 📝 Interactive API documentation with Swagger UI
- 🐳 Docker support with environment variable configuration

## 🔌 Supported Providers

- **Codecov**: Analyze coverage from Codecov API
- **More providers coming soon!**

## 🔨 Development

Want to contribute? Great! Check out our [GitHub repository](https://github.com/Chisanan232/test-coverage-mcp) for contribution guidelines.

## 📖 Documentation

Full documentation is available in the [GitHub repository](https://github.com/Chisanan232/test-coverage-mcp/tree/master/docs).

Health check endpoint: `http://localhost:8000/health`

## 📜 License

[MIT License](./LICENSE)
