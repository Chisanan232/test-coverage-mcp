# describe_coverage_provider Tool

## Overview

The `describe_coverage_provider` tool provides comprehensive information about a specific coverage provider, including its capabilities, limitations, and current health status.

## Function Signature

```python
def describe_coverage_provider(provider_name: str) -> Dict[str, Any]
```

## Parameters

### provider_name (str, required)

The name of the provider to describe.

**Example values**: `"codecov"`, `"coveralls"`, `"sonarqube"`

## Return Value

Returns a dictionary with the following structure:

```python
{
    "name": str,                        # Provider name
    "version": str,                     # Provider version
    "description": str,                 # Provider description
    "capabilities": {
        "supported": [str],             # List of supported capabilities
        "support_levels": {str: str},   # Capability -> support level mapping
        "capability_matrix": {str: str} # Detailed capability matrix
    },
    "health": {
        "is_healthy": bool,
        "last_check": str | None,
        "response_time_ms": float | None,
        "error_message": str | None
    } | None,
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

## Error Responses

### Provider Not Found

If the provider doesn't exist:

```python
{
    "error": "Provider 'nonexistent' not found",
    "error_type": "ProviderNotFoundError",
    "execution_metadata": { ... }
}
```

### Provider Description Error

If an error occurs while describing the provider:

```python
{
    "error": "Error message describing what went wrong",
    "error_type": "ProviderDescriptionError",
    "execution_metadata": { ... }
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

### Get Provider Details

```python
result = describe_coverage_provider("codecov")

print(f"Provider: {result['name']} v{result['version']}")
print(f"Description: {result['description']}")
print(f"Healthy: {result['health']['is_healthy']}")
```

### Check Capability Support

```python
result = describe_coverage_provider("codecov")

# Check if provider supports coverage delta
supports_delta = "coverage_delta" in result['capabilities']['supported']
if supports_delta:
    level = result['capabilities']['support_levels']['coverage_delta']
    print(f"Coverage delta support: {level}")
```

### Analyze Provider Health

```python
result = describe_coverage_provider("codecov")

if result['health']:
    health = result['health']
    print(f"Healthy: {health['is_healthy']}")
    print(f"Response time: {health['response_time_ms']}ms")
    if health['error_message']:
        print(f"Error: {health['error_message']}")
```

### Compare Capabilities

```python
def compare_providers(provider_names):
    """Compare capabilities of multiple providers."""
    results = {}
    for name in provider_names:
        result = describe_coverage_provider(name)
        if 'error' not in result:
            results[name] = result['capabilities']['supported']
    
    # Find common capabilities
    if results:
        common = set(results[list(results.keys())[0]])
        for caps in results.values():
            common &= set(caps)
        print(f"Common capabilities: {common}")

compare_providers(["codecov", "coveralls"])
```

## Use Cases

### 1. Verify Provider Capabilities

```python
# Check if provider supports required capabilities
required = ["repository_summary", "coverage_delta"]
result = describe_coverage_provider("codecov")

supported = result['capabilities']['supported']
has_all = all(cap in supported for cap in required)
print(f"Has required capabilities: {has_all}")
```

### 2. Diagnose Provider Issues

```python
# Check provider health and error messages
result = describe_coverage_provider("codecov")

if not result['health']['is_healthy']:
    error = result['health']['error_message']
    print(f"Provider issue: {error}")
```

### 3. Select Best Provider

```python
# Find provider with best support for a capability
from test_coverage_mcp.mcp_server.tools import list_coverage_providers

providers = list_coverage_providers()['providers']
best_provider = None
best_level = None

for provider in providers:
    result = describe_coverage_provider(provider['name'])
    if 'coverage_delta' in result['capabilities']['supported']:
        level = result['capabilities']['support_levels']['coverage_delta']
        if best_level is None or level > best_level:
            best_provider = provider['name']
            best_level = level

print(f"Best provider for coverage_delta: {best_provider} ({best_level})")
```

### 4. Document Provider Capabilities

```python
# Generate documentation for a provider
result = describe_coverage_provider("codecov")

print(f"# {result['name']} Provider")
print(f"\nVersion: {result['version']}")
print(f"Description: {result['description']}")
print(f"\n## Supported Capabilities")
for cap, level in result['capabilities']['support_levels'].items():
    print(f"- {cap}: {level}")
```

## Performance Considerations

- **Caching**: Provider information can be cached as it rarely changes
- **Health Checks**: Health information is current but may take time to retrieve
- **Error Handling**: Provider might be temporarily unavailable

## Related Tools

- `list_coverage_providers` - List all available providers
- `get_repository_test_health` - Analyze repository coverage health
