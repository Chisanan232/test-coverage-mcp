---
sidebar_position: 2
title: Provider Discovery Tools
description: Documentation for provider management tools - List and Describe coverage providers
---

# Provider Discovery Tools

Provider discovery tools help you find and understand available coverage providers in your environment.

## List Coverage Providers

**Tool Name**: `coverage.providers.list`

Discover all available coverage providers with their capabilities and health status.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_capabilities` | boolean | No | true | Include provider capabilities in response |
| `include_health` | boolean | No | true | Include provider health status in response |

### Response

```typescript
{
  providers: [
    {
      name: string,
      version: string,
      description: string,
      capabilities: {
        repository_summary: "BASIC" | "ADVANCED" | "EXPERT",
        file_coverage: "BASIC" | "ADVANCED" | "EXPERT",
        function_coverage: "BASIC" | "ADVANCED" | "EXPERT",
        branch_coverage: "BASIC" | "ADVANCED" | "EXPERT",
        line_coverage: "BASIC" | "ADVANCED" | "EXPERT"
      },
      health: {
        is_healthy: boolean,
        last_check: string (ISO 8601),
        error_message?: string,
        response_time_ms: number
      }
    }
  ],
  total_providers: number,
  execution_metadata: {...}
}
```

### Examples

**List all providers with full details:**
```bash
# Using MCP client
tool: coverage.providers.list
parameters:
  include_capabilities: true
  include_health: true
```

**List only provider names (lightweight):**
```bash
tool: coverage.providers.list
parameters:
  include_capabilities: false
  include_health: false
```

### Use Cases

- Discover what coverage providers are available
- Check provider health before running analysis
- Verify provider capabilities for your needs
- Monitor provider status over time

---

## Describe Coverage Provider

**Tool Name**: `coverage.providers.describe`

Get detailed information about a specific coverage provider.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `provider_name` | string | Yes | Name of the provider to describe |

### Response

```typescript
{
  provider: {
    name: string,
    version: string,
    description: string,
    capabilities: {
      repository_summary: "BASIC" | "ADVANCED" | "EXPERT",
      file_coverage: "BASIC" | "ADVANCED" | "EXPERT",
      function_coverage: "BASIC" | "ADVANCED" | "EXPERT",
      branch_coverage: "BASIC" | "ADVANCED" | "EXPERT",
      line_coverage: "BASIC" | "ADVANCED" | "EXPERT"
    },
    limitations: string[],
    health: {
      is_healthy: boolean,
      last_check: string (ISO 8601),
      error_message?: string,
      response_time_ms: number
    },
    configuration: {
      required_env_vars: string[],
      optional_env_vars: string[],
      default_timeout_ms: number
    }
  },
  execution_metadata: {...}
}
```

### Examples

**Get details about Codecov provider:**
```bash
tool: coverage.providers.describe
parameters:
  provider_name: "codecov"
```

**Response example:**
```json
{
  "provider": {
    "name": "codecov",
    "version": "1.0.0",
    "description": "Codecov coverage provider integration",
    "capabilities": {
      "repository_summary": "ADVANCED",
      "file_coverage": "ADVANCED",
      "function_coverage": "BASIC",
      "branch_coverage": "ADVANCED",
      "line_coverage": "ADVANCED"
    },
    "limitations": [
      "Requires Codecov API token",
      "Rate limited to 100 requests/hour",
      "Historical data limited to 90 days"
    ],
    "health": {
      "is_healthy": true,
      "last_check": "2024-01-15T10:30:00Z",
      "response_time_ms": 245
    }
  }
}
```

### Use Cases

- Understand provider capabilities before using
- Check provider configuration requirements
- Verify provider is healthy and responsive
- Review provider limitations and constraints
- Plan coverage analysis strategy

---

## Capability Levels

Providers support different capability levels:

| Level | Description | Use Case |
|-------|-------------|----------|
| **BASIC** | Limited functionality, basic metrics | Quick checks, simple analysis |
| **ADVANCED** | Full functionality, detailed metrics | Production use, detailed analysis |
| **EXPERT** | Advanced features, custom analysis | Complex scenarios, specialized needs |

---

## Health Status

Provider health indicates availability and performance:

| Status | Meaning | Action |
|--------|---------|--------|
| **Healthy** | Provider is working normally | Safe to use |
| **Unhealthy** | Provider has issues | Check error message, retry later |
| **Degraded** | Provider is slow but working | May use, expect delays |

---

## Error Handling

### Common Errors

**Provider Not Found**
```json
{
  "error": "Provider 'unknown' not found",
  "error_type": "ProviderNotFoundError"
}
```

**Provider Unhealthy**
```json
{
  "error": "Provider 'codecov' is currently unhealthy",
  "error_type": "ProviderHealthError",
  "details": {
    "last_error": "Connection timeout",
    "last_check": "2024-01-15T10:30:00Z"
  }
}
```

---

## Best Practices

1. **Check provider health** before running analysis
2. **Understand capabilities** to set realistic expectations
3. **Review limitations** to plan your workflow
4. **Monitor response times** for performance optimization
5. **Handle errors gracefully** with fallback providers

---

## Integration Examples

### Python

```python
from test_coverage_mcp.mcp_server.tools import (
    list_coverage_providers,
    describe_coverage_provider
)

# List all providers
providers = list_coverage_providers(
    include_capabilities=True,
    include_health=True
)

# Find healthy providers
healthy = [p for p in providers['providers'] if p['health']['is_healthy']]

# Get details about a specific provider
codecov = describe_coverage_provider(provider_name='codecov')

# Check if provider supports needed capability
if codecov['provider']['capabilities']['file_coverage'] == 'ADVANCED':
    print("Provider supports detailed file coverage analysis")
```

### Workflow

```
1. List available providers
   ↓
2. Filter by health status
   ↓
3. Describe selected provider
   ↓
4. Verify capabilities match needs
   ↓
5. Use provider for analysis
```

---

## Next Steps

- **[Coverage Analysis Tools](./repository-health.md)** - Analyze coverage metrics
- **[Configuration Guide](../guides/configuration.md)** - Set up providers
- **[API Reference](./reference.md)** - Detailed specifications
