---
sidebar_position: 3
---

# Plugin System Architecture

## Overview

The plugin system enables dynamic discovery and management of coverage providers at runtime. It uses Python's entry points mechanism for automatic provider discovery and a singleton registry pattern for centralized provider management.

## Architecture

### Three-Layer Plugin Architecture

```
┌─────────────────────────────────────┐
│  Application Layer                  │
│  - MCP Tools                        │
│  - CLI Commands                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Registry & Lifecycle Layer         │
│  - ProviderRegistry (singleton)     │
│  - ProviderLifecycleManager         │
│  - ProviderDiscovery                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Provider Layer                     │
│  - CoverageProvider implementations │
│  - Codecov, Cobertura, etc.        │
└─────────────────────────────────────┘
```

## Components

### ProviderRegistry (Singleton)

Centralized registry for all coverage providers:

```python
from src.registry import ProviderRegistry

# Get singleton instance
registry = ProviderRegistry()

# Register a provider
registry.register(my_provider)

# Get a provider
provider = registry.get("codecov")

# Set default provider
registry.set_default("codecov")

# List all providers
providers = registry.list_providers()

# Check health of all providers
health = registry.get_health_status()
```

**Key Methods**:
- `register(provider)` - Register a provider
- `unregister(name)` - Remove a provider
- `get(name)` - Get provider by name
- `get_default()` - Get default provider
- `set_default(name)` - Set default provider
- `list_providers()` - Get all providers with metadata
- `get_health_status()` - Get health of all providers

### ProviderDiscovery

Automatic provider discovery via entry points:

```python
from src.registry.discovery import discover_providers, load_provider

# Auto-discover all providers
providers = discover_providers()

# Manually load a provider
provider = load_provider("my_package.providers", "MyProvider")
```

**Features**:
- Entry point scanning (`test_coverage_mcp.providers`)
- Dynamic loading with error handling
- Plugin metadata extraction
- Version compatibility checking

### ProviderLifecycleManager

Manages provider initialization, configuration, and shutdown:

```python
from src.registry.lifecycle import ProviderLifecycleManager

manager = ProviderLifecycleManager()

# Initialize provider with config
config = {"api_token": "xxx", "timeout": 30}
manager.initialize(provider, config)

# Check health
health = manager.check_health("codecov")

# Shutdown provider
manager.shutdown("codecov")

# Shutdown all
manager.shutdown_all()
```

**Features**:
- Configuration injection
- Health monitoring
- Graceful shutdown
- Initialization hooks

### Configuration Models

Pydantic-based configuration with environment variable support:

```python
from src.registry.config import CodecovConfig, RegistryConfig

# Load from environment
config = CodecovConfig()  # Reads CODECOV_* env vars

# Create with values
config = CodecovConfig(
    api_token="xxx",
    api_base_url="https://api.codecov.io",
    owner="myorg",
    repo="myrepo"
)
```

### Secrets Management

Secure secret storage using Pydantic-Settings:

```python
from src.registry.secrets import CodecovSecrets

secrets = CodecovSecrets()  # Reads CODECOV_TOKEN from env

# Get token safely (won't be logged)
token = secrets.get_codecov_token()
```

## Plugin Discovery Process

```
1. Application Startup
   ↓
2. Call discover_providers()
   ↓
3. Scan entry points (test_coverage_mcp.providers)
   ↓
4. Load each provider class
   ↓
5. Verify CoverageProvider interface
   ↓
6. Register in ProviderRegistry
   ↓
7. Initialize with configuration
   ↓
8. Perform health check
   ↓
9. Ready for use
```

## Entry Point Registration

Providers register themselves via `pyproject.toml`:

```toml
[project.entry-points."test_coverage_mcp.providers"]
codecov = "test_coverage_mcp_codecov:CodecovProvider"
cobertura = "my_cobertura_provider:CoberturaProvider"
```

## Provider Lifecycle

```
┌─────────────────┐
│   Discovered    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Initialized    │
│  (configured)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Healthy Check  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │           │
    ▼           ▼
┌────────┐  ┌──────────┐
│ Ready  │  │ Degraded │
└────┬───┘  └──────────┘
     │
     ▼
┌─────────────────┐
│  In Use         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Shutdown       │
└─────────────────┘
```

## Configuration Hierarchy

```
1. Environment Variables (highest priority)
   CODECOV_API_TOKEN=xxx
   CODECOV_API_BASE_URL=https://api.codecov.io

2. .env File
   CODECOV_API_TOKEN=xxx

3. Code Defaults (lowest priority)
   CodecovConfig(api_base_url="https://api.codecov.io")
```

## Error Handling

Providers handle errors gracefully:

```python
try:
    provider = registry.get("codecov")
    result = provider.get_repository_summary(repo)
except ProviderError as e:
    # Provider-specific error
    logger.error(f"Provider error: {e}")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
```

## Health Monitoring

Periodic health checks ensure provider availability:

```python
# Get current health
health = registry.get_provider_health("codecov")
if not health.is_healthy:
    logger.warning(f"Provider unhealthy: {health.error_message}")

# Check all providers
all_health = registry.get_health_status()
for name, health in all_health.items():
    print(f"{name}: {health.is_healthy}")
```

## Best Practices

### 1. Provider Implementation

```python
from src.domain import CoverageProvider, ProviderMetadata

class MyProvider(CoverageProvider):
    def get_metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="my-provider",
            version="1.0.0",
            description="My coverage provider",
            supported_capabilities=[...],
            support_levels={...},
            analysis_depths=[...],
        )

    def health_check(self) -> ProviderHealth:
        # Lightweight connectivity check
        pass
```

### 2. Configuration

```python
# Use environment variables
export CODECOV_API_TOKEN="xxx"
export CODECOV_API_BASE_URL="https://api.codecov.io"

# Or .env file
CODECOV_API_TOKEN=xxx
CODECOV_API_BASE_URL=https://api.codecov.io
```

### 3. Error Handling

```python
# Always check health before use
health = registry.get_provider_health("codecov")
if not health.is_healthy:
    # Use fallback or degrade gracefully
    pass
```

### 4. Lifecycle Management

```python
# Initialize on startup
manager = ProviderLifecycleManager()
for name, provider in discovered_providers.items():
    manager.initialize(provider, config)

# Shutdown on exit
import atexit
atexit.register(manager.shutdown_all)
```

## Testing

Mock providers for testing:

```python
from test.unit_test.registry.test_registry import MockProvider

provider = MockProvider("test-provider", healthy=True)
registry.register(provider)

# Test with mock
result = provider.get_repository_summary("test-repo")
```

## Next Steps

- Implement Codecov provider (Phase 4)
- Add provider configuration UI
- Implement provider health dashboard
- Add provider performance metrics
