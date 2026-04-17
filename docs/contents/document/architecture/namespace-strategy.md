---
sidebar_position: 4
---

# Namespace Strategy

## Overview

This document explains the public namespace strategy for the test-coverage-mcp project and its provider ecosystem.

## Core Package Namespace

The core library is published under the `test_coverage_mcp` namespace:

```python
from test_coverage_mcp.domain import CoverageProvider, ProviderMetadata
from test_coverage_mcp.registry import ProviderRegistry
from test_coverage_mcp.config import ApplicationConfig
```

### Rationale

- **Clear Intent**: The namespace directly reflects the project name
- **Consistency**: Matches the package name `test-coverage-mcp` (with underscores in Python)
- **Discoverability**: Users can easily find the package by name
- **Professionalism**: Follows Python naming conventions

## Provider Namespace Strategy

All provider implementations use a shared namespace: `test_coverage_mcp.providers.<provider_name>`

### Codecov Provider Example

```python
from test_coverage_mcp.providers.codecov import CodecovProvider
from test_coverage_mcp.providers.codecov.api import CodecovAPIClient
from test_coverage_mcp.providers.codecov.mappers import map_repository_to_summary
```

### Design Decisions

#### 1. **Use `providers` as the Public Namespace Root**

Instead of:
- ❌ `test_coverage_mcp.provider.codecov` (singular, awkward)
- ❌ `test_coverage_mcp.adapters.codecov` (internal concept)
- ❌ `test_coverage_mcp_codecov` (separate namespace)

We use:
- ✅ `test_coverage_mcp.providers.codecov` (plural, scalable)

**Rationale**:
- Aligns with the existing plugin entry-point group: `test_coverage_mcp.providers`
- Scales naturally to multiple providers in the monorepo
- Keeps "adapter" as an internal implementation concept
- Avoids awkward singular namespace growth

#### 2. **Namespace Packages for Shared Namespace**

The `test_coverage_mcp.providers` namespace is implemented as a namespace package:

```python
# test_coverage_mcp/providers/__init__.py
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

**Benefits**:
- Multiple packages can contribute to the same namespace
- Core package and provider packages can be installed independently
- Clean separation of concerns

#### 3. **Entry Point Registration**

Providers register themselves via entry points in `pyproject.toml`:

```toml
[project.entry-points."test_coverage_mcp.providers"]
codecov = "test_coverage_mcp.providers.codecov:CodecovProvider"
cobertura = "test_coverage_mcp.providers.cobertura:CoberturProvider"
```

**Benefits**:
- Dynamic provider discovery
- No hardcoded dependencies
- Plugins can be installed separately
- Clean plugin architecture

## Package Structure

### Core Package

```
test-coverage-mcp/
├── test-coverage-mcp/
│   ├── src/
│   │   └── test_coverage_mcp/
│   │       ├── domain/
│   │       ├── registry/
│   │       ├── config.py
│   │       └── entry.py
│   └── pyproject.toml
```

### Provider Package (Codecov Example)

```
test-coverage-mcp-codecov/
├── src/
│   └── test_coverage_mcp/
│       └── providers/
│           └── codecov/
│               ├── api/
│               │   ├── client.py
│               │   └── dtos.py
│               ├── mappers/
│               │   └── mappers.py
│               └── provider.py
└── pyproject.toml
```

## Installation

### Core Package Only

```bash
pip install test-coverage-mcp
```

Imports:
```python
from test_coverage_mcp.domain import CoverageProvider
from test_coverage_mcp.registry import ProviderRegistry
```

### With Codecov Provider

```bash
pip install test-coverage-mcp[codecov]
# or
pip install test-coverage-mcp test-coverage-mcp-codecov
```

Imports:
```python
from test_coverage_mcp.providers.codecov import CodecovProvider
```

### Multiple Providers

```bash
pip install test-coverage-mcp test-coverage-mcp-codecov test-coverage-mcp-cobertura
```

All providers are automatically discovered via entry points.

## Configuration

### Workspace Development

In the monorepo, all packages are installed in editable mode:

```bash
uv sync  # Installs all workspace packages
```

This makes all namespaces available:
```python
from test_coverage_mcp.domain import CoverageProvider
from test_coverage_mcp.providers.codecov import CodecovProvider
```

### Type Checking

MyPy configuration recognizes namespace packages:

```ini
[mypy]
packages = test-coverage-mcp/src,test-coverage-mcp-codecov/src
namespace_packages = True
explicit_package_bases = True
```

### Linting

Ruff configuration includes all first-party packages:

```toml
[lint.isort]
known-first-party = [
    "test_coverage_mcp",
    "test_coverage_mcp.providers",
    "test_coverage_mcp.providers.codecov"
]
```

## Migration from `src` Namespace

Previous versions used `from src.domain import ...` which was incorrect. The migration to `test_coverage_mcp` provides:

1. **Correct Public Namespace**: Matches the actual package name
2. **Better Discoverability**: Users can find imports by package name
3. **Proper Plugin Architecture**: Providers use a shared namespace
4. **Scalability**: Easy to add new providers

## Future Providers

When adding new providers, follow this pattern:

1. Create a new package: `test-coverage-mcp-<provider>`
2. Implement under: `test_coverage_mcp.providers.<provider>`
3. Register entry point: `<provider> = "test_coverage_mcp.providers.<provider>:ProviderClass"`
4. Update ruff.toml: Add `test_coverage_mcp.providers.<provider>` to `known-first-party`

Example for a Cobertura provider:

```python
# test-coverage-mcp-cobertura/src/test_coverage_mcp/providers/cobertura/__init__.py
from test_coverage_mcp.providers.cobertura.provider import CoberturProvider

__all__ = ["CoberturProvider"]
```

```toml
# test-coverage-mcp-cobertura/pyproject.toml
[project.entry-points."test_coverage_mcp.providers"]
cobertura = "test_coverage_mcp.providers.cobertura:CoberturProvider"
```

## Benefits Summary

✅ **Clear Hierarchy**: Core package → providers namespace → individual providers  
✅ **Scalable**: Easy to add new providers without namespace conflicts  
✅ **Discoverable**: Package names match import paths  
✅ **Professional**: Follows Python packaging best practices  
✅ **Flexible**: Providers can be installed independently  
✅ **Maintainable**: Clean separation of concerns  
✅ **Testable**: Namespace packages work with all testing frameworks  

## References

- [PEP 420 - Implicit Namespace Packages](https://www.python.org/dev/peps/pep-0420/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Entry Points Documentation](https://packaging.python.org/specifications/entry-points/)
