# test-coverage-mcp

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/Chisanan232/test-coverage-mcp)](https://github.com/Chisanan232/test-coverage-mcp/releases)
[![PyPI](https://img.shields.io/pypi/v/test-coverage-mcp)](https://pypi.org/project/test-coverage-mcp/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/Chisanan232/test-coverage-mcp/pkgs/container/test-coverage-mcp)

🔬 A provider-extensible MCP server for test coverage intelligence, with a stable capability-driven tool contract and provider-specific enrichments.

## Overview

`test-coverage-mcp` provides intelligent test coverage analysis through the Model Context Protocol (MCP). It features a provider-extensible architecture that supports multiple coverage platforms (Codecov, Coveralls, etc.) while maintaining a stable tool interface.

### Key Features

- **Provider-Extensible Architecture**: Plugin system for coverage providers
- **Capability-Driven Design**: Tools adapt to provider capabilities
- **11 MCP Tools**: Comprehensive coverage analysis and recommendations
- **Multiple Transports**: stdio, HTTP, SSE support
- **Web API**: FastAPI-based REST interface
- **Docker Support**: Production-ready containerization
- **Full Documentation**: Complete guides and API reference

## Python Versions Support

Requires Python 3.12 or higher (3.12, 3.13, 3.14)

## Workspace Architecture

This project uses a **uv workspace** monorepo structure:

```
test-coverage-mcp/           # Root workspace
├── test-coverage-mcp/       # Core package
│   ├── src/                 # Core source code
│   ├── test/                # Core tests
│   └── pyproject.toml       # Package config
├── test-coverage-mcp-codecov/  # Codecov provider plugin
│   ├── src/                 # Provider source code
│   ├── test/                # Provider tests
│   └── pyproject.toml       # Plugin config
└── pyproject.toml           # Workspace config
```

## Quick Start

### Installation

```bash
# Install core package
pip install test-coverage-mcp

# Install with Codecov provider
pip install test-coverage-mcp test-coverage-mcp-codecov
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/Chisanan232/test-coverage-mcp.git
cd test-coverage-mcp

# Install workspace with uv
uv sync

# Run tests
cd test-coverage-mcp && uv run pytest
```

## Documentation

📚 **Full Documentation**: https://test-coverage-mcp.readthedocs.io/

### Quick Links

- **[Getting Started](docs/contents/deployment/overview.md)** - Installation and quick start
- **[Architecture Overview](docs/contents/architecture/overview.md)** - System design and components
- **[MCP Tools Reference](docs/contents/mcp-tools/reference.md)** - Complete tool documentation
- **[Deployment Guides](docs/contents/deployment/)** - CLI, Docker, Kubernetes deployment
- **[Plugin Development](docs/contents/guides/plugin-development.md)** - Create custom providers
- **[Troubleshooting](docs/contents/troubleshooting.md)** - Common issues and solutions
- **[CHANGELOG](CHANGELOG.md)** - Version history and releases

### Development

See `CONTRIBUTING.md` for development workflow and workspace details.

## CI/CD Workflows

test-coverage-mcp uses comprehensive GitHub Actions workflows for automated testing, building, and deployment:

### 🚀 Key Workflows

- **Lint & Type Check**: Ruff linting, MyPy type checking, pre-commit hooks
- **Test Suite**: Unit, integration, and end-to-end tests across Python versions
- **Code Coverage**: Automated coverage reporting and tracking
- **Docker**: Build, test, and push Docker images
- **Documentation**: Build and deploy documentation
- **Release**: Automated versioning and PyPI publishing

### 📚 Documentation

- **[Contributing Guide](CONTRIBUTING.md)**: Development workflow and setup
- **[GitHub Workflows](.github/workflows/)**: Complete workflow definitions
- **[CI Configuration](.github/)**: Workflow configuration and setup


## Coding Style and Quality

**test-coverage-mcp** follows coding styles **_black_** and **_Ruff_** to control code quality.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: ruff](https://img.shields.io/badge/linting-ruff-gold)](https://github.com/astral-sh/ruff)
[![type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue)](https://github.com/python/mypy)

## Download Statistics

[![Downloads](https://pepy.tech/badge/test-coverage-mcp)](https://pepy.tech/project/test-coverage-mcp)
[![Downloads](https://pepy.tech/badge/test-coverage-mcp/month)](https://pepy.tech/project/test-coverage-mcp)


## License

[MIT License](./LICENSE)
