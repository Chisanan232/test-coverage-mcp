# list_coverage_providers Tool

## Overview

The `list_coverage_providers` tool discovers and lists all registered coverage providers with their metadata, capabilities, and health status.

## Function Signature

```python
def list_coverage_providers(
    include_capabilities: bool = True,
    include_health: bool = True,
) -> Dict[str, Any]
```

## Parameters

### include_capabilities (bool, default: True)

Include detailed capability information for each provider.

When `True`, returns:
- `supported_capabilities`: List of capabilities the provider supports
- `support_levels`: Dictionary mapping capabilities to support levels (basic, enhanced, advanced)

### include_health (bool, default: True)

Include health status information for each provider.

When `True`, returns:
- `is_healthy`: Whether the provider is currently healthy
- `last_check`: Timestamp of last health check
- `response_time_ms`: Provider response time in milliseconds
- `error_message`: Any error message from last check

## Return Value

Returns a dictionary with the following structure:

```python
{
    "providers": [
        {
            "name": str,                    # Provider name
            "version": str,                 # Provider version
            "description": str,             # Provider description
            "supported_capabilities": [str],  # (if include_capabilities=True)
            "support_levels": {str: str},     # (if include_capabilities=True)
            "health": {                       # (if include_health=True)
                "is_healthy": bool,
                "last_check": str,
                "response_time_ms": float,
                "error_message": str | None
            }
        }
    ],
    "total_providers": int,                # Total number of providers
    "healthy_providers": int | None,       # Number of healthy providers (if include_health=True)
    "execution_metadata": {
        "provider_name": str,
        "provider_version": str,
        "support_level": str,
        "used_capabilities": [],
        "analysis_depth": str,
        "execution_time_ms": float
    }
}
```

## Capabilities

Providers can support various capabilities:

- `repository_summary` - Overall repository coverage summary
- `file_coverage` - Per-file coverage information
- `coverage_delta` - Coverage changes between references
- `uncovered_regions` - Detailed uncovered code regions
- `test_recommendations` - Recommendations for test improvements
- `coverage_trends` - Historical coverage trends
- `coverage_config_diagnosis` - Coverage configuration analysis
- `coverage_goals` - Coverage goal tracking
- `cross_branch_comparison` - Compare coverage across branches
- `pull_request_analysis` - PR-specific coverage analysis
- `coverage_metrics` - Detailed coverage metrics
- `risk_assessment` - Risk assessment based on coverage
- `quality_gates` - Quality gate evaluation
- `historical_analysis` - Historical coverage analysis

## Support Levels

Each capability can have a support level:

- `basic` - Basic support for the capability
- `enhanced` - Enhanced support with additional features
- `advanced` - Full advanced support

## Examples

### List All Providers with Full Details

```python
result = list_coverage_providers(
    include_capabilities=True,
    include_health=True
)

for provider in result['providers']:
    print(f"{provider['name']} v{provider['version']}")
    print(f"  Healthy: {provider['health']['is_healthy']}")
    print(f"  Response time: {provider['health']['response_time_ms']}ms")
    print(f"  Capabilities: {', '.join(provider['supported_capabilities'])}")
```

### List Providers Without Health Check

```python
result = list_coverage_providers(
    include_capabilities=True,
    include_health=False
)

print(f"Found {result['total_providers']} providers")
```

### List Providers Without Capabilities

```python
result = list_coverage_providers(
    include_capabilities=False,
    include_health=True
)

healthy = result['healthy_providers']
total = result['total_providers']
print(f"Health: {healthy}/{total} providers healthy")
```

## Error Handling

The tool returns an error response if discovery fails:

```python
{
    "error": "Error message describing what went wrong",
    "error_type": "ProviderDiscoveryError",
    "providers": [],
    "total_providers": 0,
    "execution_metadata": { ... }
}
```

## Use Cases

### 1. Check Available Providers

```python
# Discover what providers are available
result = list_coverage_providers()
available_providers = [p['name'] for p in result['providers']]
print(f"Available providers: {available_providers}")
```

### 2. Find Providers with Specific Capability

```python
# Find providers that support coverage delta
result = list_coverage_providers(include_capabilities=True)
delta_providers = [
    p['name'] for p in result['providers']
    if 'coverage_delta' in p['supported_capabilities']
]
print(f"Providers with delta support: {delta_providers}")
```

### 3. Monitor Provider Health

```python
# Check health of all providers
result = list_coverage_providers(include_health=True)
unhealthy = [
    p['name'] for p in result['providers']
    if not p['health']['is_healthy']
]
if unhealthy:
    print(f"Unhealthy providers: {unhealthy}")
```

### 4. Performance Analysis

```python
# Analyze provider response times
result = list_coverage_providers(include_health=True)
for provider in result['providers']:
    response_time = provider['health']['response_time_ms']
    print(f"{provider['name']}: {response_time}ms")

avg_time = sum(
    p['health']['response_time_ms'] for p in result['providers']
) / len(result['providers'])
print(f"Average response time: {avg_time}ms")
```

## Performance Considerations

- **Caching**: Results can be cached as provider metadata rarely changes
- **Health Checks**: Health checks may take time; set `include_health=False` if not needed
- **Large Deployments**: With many providers, consider filtering results

## Related Tools

- `describe_coverage_provider` - Get detailed information about a specific provider
- `get_repository_test_health` - Analyze repository coverage health
