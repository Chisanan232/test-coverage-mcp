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

## Reusable GitHub Actions Workflows & Actions

This template provides a comprehensive set of **reusable GitHub Actions workflows and actions** that can be called from other repositories to standardize CI/CD operations. Projects using this template can leverage these centralized components for consistent automation.

### 🚀 Key Features

- **Centralized Management**: All workflows and actions are maintained in this template repository
- **Standardized Operations**: Consistent CI/CD processes across all projects
- **Easy Integration**: Simple calls using external repository references
- **Comprehensive Coverage**: Testing, building, releasing, Docker operations, documentation, and setup utilities

### 📋 Available Workflows

| Workflow                                             | Purpose                      | Key Features                           |
|------------------------------------------------------|------------------------------|----------------------------------------|
| `rw_build_and_test.yaml`                             | Run comprehensive test suite | Unit, integration, e2e, contract tests |
| `rw_run_all_test_and_record.yaml`                    | Complete CI with reporting   | CodeCov upload, SonarCloud analysis    |
| `rw_python_package.yaml`                             | Python package operations    | Build, test, publish to PyPI           |
| `rw_docker_operations.yaml`                          | Docker operations            | Build, test, push, security scanning   |
| `rw_parse_release_intent.yaml`                       | Release configuration parser | Determines release components          |
| `rw_build_git-tag_and_create_github-release_v2.yaml` | Git tagging and releases     | Automated version management           |
| `rw_docs_operations.yaml`                            | Documentation operations     | Build, version, deploy docs            |

### 📦 Available Actions

| Action | Purpose | Key Features |
|--------|---------|--------------|
| `setup-python-uv` | Python & UV setup with dependencies | Multi-version support, intelligent caching, flexible dependency groups |

### 🔧 Quick Start

To use these reusable workflows in your project, simply call them using external repository references:

```yaml
# .github/workflows/ci.yaml in your project
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    uses: Chisanan232/Template-Python-UV-Project/.github/workflows/rw_run_all_test_and_record.yaml@master
    secrets:
      codecov_token: ${{ secrets.CODECOV_TOKEN }}
      sonar_token: ${{ secrets.SONAR_TOKEN }}
```

### 📚 Complete Documentation

- **[Reusable Workflows Guide](.github/workflows/REUSABLE_WORKFLOWS.md)**: Complete documentation with all inputs, outputs, and usage examples
- **[Example Workflows](.github/workflows/examples/)**: Ready-to-use example workflows for common scenarios
- **Template Placeholders**: All workflows use `<your_*>` placeholders for easy customization

### 💡 Benefits for Projects Using This Template

1. **Reduced Boilerplate**: No need to write complex CI/CD workflows from scratch
2. **Best Practices**: Workflows follow established patterns and security practices
3. **Automatic Updates**: Bug fixes and improvements are centrally maintained
4. **Consistency**: Same workflow behavior across all projects using the template
5. **Easy Maintenance**: Update workflows in one place, benefits all projects


## Coding style and following rules

**_<your lib name>_** follows coding styles **_black_** and **_PyLint_** to control code quality.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)


## Downloading state

🚧 The download state for your library

[![Downloads](https://pepy.tech/badge/<your lib name>)](https://pepy.tech/project/<your lib name>)
[![Downloads](https://pepy.tech/badge/<your lib name>/month)](https://pepy.tech/project/<your lib name>)


## License

[MIT License](./LICENSE)
