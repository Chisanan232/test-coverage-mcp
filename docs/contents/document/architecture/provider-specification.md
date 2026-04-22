---
sidebar_position: 2
---

# Provider Specification

## Overview

This document specifies the contract that coverage providers must implement to integrate with the test-coverage-mcp server. Providers are plugins that connect to various coverage analysis tools (Codecov, Cobertura, etc.) and expose their capabilities through a standardized interface.

## Provider Contract

All providers must implement the `CoverageProvider` abstract base class:

```python
from test_coverage_mcp.domain import (
    CoverageProvider,
    ProviderCapability,
    ProviderMetadata,
    ProviderHealth,
    SupportLevel,
)

class MyProvider(CoverageProvider):
    """Custom coverage provider implementation."""

    def get_metadata(self) -> ProviderMetadata:
        """Return provider metadata."""
        pass

    def health_check(self) -> ProviderHealth:
        """Check provider health and connectivity."""
        pass

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if capability is supported."""
        pass

    def get_support_level(
        self, capability: ProviderCapability
    ) -> Optional[SupportLevel]:
        """Get support level for a capability."""
        pass
```

## Metadata

Every provider must provide metadata describing its capabilities:

```python
def get_metadata(self) -> ProviderMetadata:
    return ProviderMetadata(
        name="my-provider",
        version="1.0.0",
        description="My custom coverage provider",
        supported_capabilities=[
            ProviderCapability.REPOSITORY_SUMMARY,
            ProviderCapability.FILE_COVERAGE,
            ProviderCapability.COVERAGE_DELTA,
        ],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
            ProviderCapability.COVERAGE_DELTA: SupportLevel.ENHANCED,
        },
        analysis_depths=[
            AnalysisDepth.REPOSITORY,
            AnalysisDepth.FILE,
        ],
    )
```

## Health Checks

Providers must implement health checks to verify connectivity and availability:

```python
def health_check(self) -> ProviderHealth:
    try:
        start = time.time()
        # Perform lightweight connectivity check
        response = self.api_client.health()
        elapsed = (time.time() - start) * 1000  # Convert to ms

        return ProviderHealth(
            is_healthy=response.status == "ok",
            last_check=datetime.utcnow().isoformat(),
            error_message=None,
            response_time_ms=elapsed,
        )
    except Exception as e:
        return ProviderHealth(
            is_healthy=False,
            last_check=datetime.utcnow().isoformat(),
            error_message=str(e),
            response_time_ms=0.0,
        )
```

## Capability Support

Providers declare which capabilities they support:

```python
def supports_capability(self, capability: ProviderCapability) -> bool:
    return capability in self.get_metadata().supported_capabilities

def get_support_level(
    self, capability: ProviderCapability
) -> Optional[SupportLevel]:
    metadata = self.get_metadata()
    return metadata.support_levels.get(capability)
```

## Implementation Patterns

### Configuration

Providers should accept configuration via environment variables or configuration objects:

```python
from pydantic_settings import BaseSettings

class MyProviderConfig(BaseSettings):
    """Configuration for my provider."""

    api_token: str
    api_base_url: str = "https://api.example.com"
    timeout_seconds: int = 30

    class Config:
        env_prefix = "MY_PROVIDER_"

class MyProvider(CoverageProvider):
    def __init__(self, config: MyProviderConfig):
        self.config = config
        self.api_client = APIClient(
            token=config.api_token,
            base_url=config.api_base_url,
            timeout=config.timeout_seconds,
        )
```

### Error Handling

Providers should handle errors gracefully and provide meaningful error messages:

```python
def get_repository_summary(self, repo: str) -> RepositoryCoverageSummary:
    try:
        data = self.api_client.get_coverage(repo)
        return self._parse_coverage_data(data)
    except APIError as e:
        # Degrade gracefully
        return RepositoryCoverageSummary(
            summary=f"Error fetching coverage: {e.message}",
            key_findings=[],
            recommended_next_actions=["Check API connectivity"],
            confidence_score=0.0,
            execution_metadata=ExecutionMetadata(
                provider_name=self.get_metadata().name,
                provider_version=self.get_metadata().version,
                support_level=SupportLevel.BASIC,
                used_capabilities=[],
                analysis_depth=AnalysisDepth.REPOSITORY,
                execution_time_ms=0.0,
                degradation_reason=str(e),
            ),
            total_coverage_percentage=0.0,
            covered_lines=0,
            total_lines=0,
            file_count=0,
            covered_file_count=0,
        )
```

### Caching

Providers may implement caching to improve performance:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedProvider(CoverageProvider):
    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache = {}
        self._cache_times = {}

    def _get_cached(self, key: str) -> Optional[Any]:
        if key in self._cache:
            cached_time = self._cache_times[key]
            if datetime.utcnow() - cached_time < self.cache_ttl:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._cache_times[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._cache_times[key] = datetime.utcnow()
```

## Testing

Providers should include comprehensive tests:

```python
import pytest
from test_coverage_mcp.domain import (
    ProviderCapability,
    SupportLevel,
    AnalysisDepth,
)

class TestMyProvider:
    @pytest.fixture
    def provider(self):
        config = MyProviderConfig(api_token="test-token")
        return MyProvider(config)

    def test_metadata(self, provider):
        metadata = provider.get_metadata()
        assert metadata.name == "my-provider"
        assert ProviderCapability.REPOSITORY_SUMMARY in metadata.supported_capabilities

    def test_health_check(self, provider):
        health = provider.health_check()
        assert isinstance(health.is_healthy, bool)
        assert health.response_time_ms >= 0

    def test_supports_capability(self, provider):
        assert provider.supports_capability(ProviderCapability.REPOSITORY_SUMMARY)
        assert provider.get_support_level(ProviderCapability.REPOSITORY_SUMMARY) is not None
```

## Registration

Providers are registered via entry points in `pyproject.toml`:

```toml
[project.entry-points."test_coverage_mcp.providers"]
my-provider = "my_provider_package:MyProvider"
```

The registry will automatically discover and load providers at startup.

## Capability Implementation Guide

### REPOSITORY_SUMMARY

Return overall repository coverage:

```python
def get_repository_summary(self, repo: str) -> RepositoryCoverageSummary:
    """Get repository-level coverage summary."""
    pass
```

### FILE_COVERAGE

Return per-file coverage details:

```python
def get_file_coverage(self, repo: str, file_path: str) -> FileCoverage:
    """Get coverage for a specific file."""
    pass
```

### COVERAGE_DELTA

Compare coverage between versions:

```python
def get_coverage_delta(
    self, repo: str, base_ref: str, head_ref: str
) -> CoverageDelta:
    """Get coverage change between refs."""
    pass
```

### UNCOVERED_REGIONS

Identify uncovered code regions:

```python
def get_uncovered_regions(self, repo: str, file_path: str) -> list[UncoveredRegion]:
    """Get uncovered regions in a file."""
    pass
```

### TEST_RECOMMENDATIONS

Suggest tests for gaps:

```python
def get_test_recommendations(
    self, repo: str, file_path: str
) -> list[TestRecommendation]:
    """Get test recommendations for uncovered regions."""
    pass
```

## Best Practices

1. **Fail Gracefully**: Always provide meaningful error messages
2. **Track Degradation**: Use `degradation_reason` when capabilities are limited
3. **Confidence Scoring**: Adjust confidence based on data quality
4. **Caching**: Cache results when appropriate
5. **Logging**: Log important events for debugging
6. **Testing**: Provide comprehensive test coverage
7. **Documentation**: Document provider-specific behavior
8. **Versioning**: Follow semantic versioning

## Example: Codecov Provider

See the Codecov provider implementation for a complete example:
- Location: `test-coverage-mcp-codecov/src/`
- Implements all basic capabilities
- Handles API errors gracefully
- Includes comprehensive tests

## Next Steps

- Implement your provider following this specification
- Register via entry point in `pyproject.toml`
- Add tests for your provider
- Document provider-specific behavior
- Submit PR for integration
