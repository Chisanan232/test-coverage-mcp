# Service Layer Architecture

## Overview

The service layer provides high-level intelligence services for coverage analysis. These services aggregate data from multiple providers, perform complex analysis, and expose unified APIs for coverage insights.

## Services

### ProviderDiscoveryService

Manages provider discovery, registration, and capability analysis.

**Key Responsibilities:**
- Discover providers via entry points
- Register and manage provider lifecycle
- Query provider capabilities and health
- Generate capability matrices
- Select best provider based on requirements

**Methods:**
- `discover_and_register_providers()` - Auto-discover and register providers
- `list_providers()` - List all registered providers
- `get_provider(name)` - Get specific provider
- `get_capability_matrix()` - Generate capability support matrix
- `get_providers_for_capability(capability)` - Find providers supporting a capability
- `aggregate_health()` - Aggregate health across providers
- `select_best_provider(required_capabilities)` - Select optimal provider

**Example Usage:**
```python
from test_coverage_mcp.services import ProviderDiscoveryService

service = ProviderDiscoveryService()
service.discover_and_register_providers()

# Get capability matrix
matrix = service.get_capability_matrix()

# Select best provider for specific capabilities
provider = service.select_best_provider(
    required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
)
```

### RepositoryHealthService

Analyzes repository coverage health and identifies risks.

**Key Responsibilities:**
- Aggregate coverage metrics from providers
- Identify coverage risks and gaps
- Generate recommendations for improvement
- Provide multi-provider fallback chains
- Track coverage trends

**Methods:**
- `aggregate_coverage_metrics(repo_owner, repo_name)` - Get aggregated metrics
- `identify_risks(repo_owner, repo_name, threshold)` - Identify coverage risks
- `get_next_actions(repo_owner, repo_name)` - Generate action items
- `get_provider_fallback_chain(required_capabilities)` - Get fallback order

**Risk Levels:**
- `LOW` - Coverage >= threshold
- `MEDIUM` - Coverage >= threshold - 10%
- `HIGH` - Coverage >= threshold - 20%
- `CRITICAL` - Coverage < threshold - 20%

**Example Usage:**
```python
from test_coverage_mcp.services import RepositoryHealthService

service = RepositoryHealthService()

# Identify risks
risk = service.identify_risks("owner", "repo", threshold=80.0)
print(f"Risk Level: {risk['risk_level']}")
print(f"Gap: {risk['gap']}%")

# Get next actions
actions = service.get_next_actions("owner", "repo")
for action in actions:
    print(f"- {action}")
```

### CoverageComparisonService

Compares coverage across references and detects changes.

**Key Responsibilities:**
- Compare coverage between refs (branches, tags, commits)
- Detect regressions and improvements
- Analyze component and flag-level deltas
- Calculate impact metrics

**Methods:**
- `compare_refs(repo_owner, repo_name, base_ref, head_ref)` - Compare two refs
- `detect_regressions(repo_owner, repo_name, base_ref, head_ref, threshold)` - Detect regressions
- `detect_improvements(repo_owner, repo_name, base_ref, head_ref)` - Detect improvements
- `compare_components(repo_owner, repo_name, base_ref, head_ref)` - Component-level comparison
- `compare_flags(repo_owner, repo_name, base_ref, head_ref)` - Flag-level comparison

**Severity Levels:**
- `none` - No regression (delta >= 0)
- `minor` - Small regression (-1% to 0%)
- `major` - Moderate regression (-5% to -1%)
- `critical` - Large regression (< -5%)

**Example Usage:**
```python
from test_coverage_mcp.services import CoverageComparisonService

service = CoverageComparisonService()

# Compare refs
result = service.compare_refs("owner", "repo", "main", "feature")
print(f"Delta: {result['delta_percentage']}%")

# Detect regressions
regression = service.detect_regressions(
    "owner", "repo", "main", "feature", threshold=1.0
)
if regression['has_regression']:
    print(f"Regression detected: {regression['severity']}")
```

## Architecture Patterns

### Multi-Provider Support

Services are designed to work with multiple providers:

1. **Discovery** - Auto-discover available providers
2. **Aggregation** - Collect data from all providers
3. **Fallback** - Use fallback chain if primary fails
4. **Consensus** - Average results across providers

### Health-Aware Selection

Provider selection considers:
- Capability support
- Health status
- Response time
- User preferences (default provider)

### Risk Assessment

Risk identification uses:
- Coverage thresholds
- Historical baselines
- Component analysis
- Trend detection

## Integration Points

### With Registry

Services use `ProviderRegistry` for:
- Provider lifecycle management
- Health status tracking
- Default provider selection

### With Providers

Services interact with providers via:
- `CoverageProvider` interface
- Capability queries
- Health checks
- Data retrieval

### With Domain Models

Services use domain models for:
- Type safety
- Consistent data structures
- Validation

## Error Handling

Services implement graceful degradation:

1. **Provider Failures** - Continue with remaining providers
2. **Missing Capabilities** - Fall back to alternative approaches
3. **Health Issues** - Mark unhealthy providers as unavailable
4. **Data Inconsistencies** - Average or validate results

## Performance Considerations

### Caching

Consider caching for:
- Provider metadata (rarely changes)
- Health status (cache with TTL)
- Capability matrices (cache with TTL)

### Async Operations

For future optimization:
- Parallel provider queries
- Async health checks
- Background metric aggregation

## Testing

Services are tested with:
- Mock providers
- Unit tests for individual methods
- Integration tests with real providers
- Edge case handling

## Future Enhancements

1. **Caching Layer** - Add TTL-based caching for metrics
2. **Async Support** - Non-blocking provider queries
3. **Webhooks** - Real-time coverage alerts
4. **Trend Analysis** - Historical coverage tracking
5. **Custom Metrics** - User-defined coverage goals
