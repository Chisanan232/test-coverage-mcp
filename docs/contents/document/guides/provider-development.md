---
sidebar_position: 2
title: Provider Development Guide
description: Step-by-step guide to creating custom coverage providers
---

# Provider Development Guide

This guide walks you through creating a custom coverage provider for test-coverage-mcp.

## Overview

A coverage provider is a plugin that integrates with a coverage service (like Codecov, Coveralls, etc.) to fetch and analyze coverage data.

### Provider Architecture

```
Your Coverage Service
        ↓
Custom Provider Implementation
        ↓
test-coverage-mcp MCP Tools
        ↓
Claude / Client Applications
```

## Prerequisites

- Python 3.9+
- Understanding of the coverage service's API
- Familiarity with async/await patterns
- Basic knowledge of type hints

## Step 1: Understand the Provider Interface

All providers must implement the `CoverageProvider` interface:

```python
from abc import ABC, abstractmethod
from test_coverage_mcp.domain import (
    ProviderMetadata,
    ProviderHealth,
    ProviderCapability,
    SupportLevel,
)

class CoverageProvider(ABC):
    """Base interface for coverage providers."""

    @abstractmethod
    async def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata and capabilities."""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider health and connectivity."""
        pass

    @abstractmethod
    async def get_repository_coverage(
        self,
        repo_slug: str,
        ref: Optional[str] = None
    ) -> RepositoryCoverageSummary:
        """Get coverage for a repository."""
        pass

    @abstractmethod
    async def get_commit_coverage(
        self,
        repo_slug: str,
        commit_sha: str
    ) -> CommitCoverageSummary:
        """Get coverage for a specific commit."""
        pass

    @abstractmethod
    async def compare_coverage(
        self,
        repo_slug: str,
        base_ref: str,
        head_ref: str
    ) -> CoverageComparison:
        """Compare coverage between two references."""
        pass
```

## Step 2: Create Your Provider Implementation

### File Structure

```
src/test_coverage_mcp/providers/
├── __init__.py
├── base.py                    # Base provider class
├── your_provider/
│   ├── __init__.py
│   ├── client.py             # API client
│   ├── provider.py           # Provider implementation
│   ├── models.py             # Data models
│   └── config.py             # Configuration
└── registry.py               # Provider registry
```

### Example: Creating a Custom Provider

**1. Create the API client** (`providers/your_provider/client.py`):

```python
import aiohttp
from typing import Optional, Dict, Any

class YourProviderClient:
    """Client for Your Coverage Service API."""

    def __init__(self, api_token: str, base_url: str = "https://api.yourservice.com"):
        self.api_token = api_token
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_repository_coverage(
        self,
        repo_slug: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch repository coverage data."""
        params = {"repo": repo_slug}
        if ref:
            params["ref"] = ref

        async with self.session.get(
            f"{self.base_url}/coverage",
            params=params,
            headers={"Authorization": f"Bearer {self.api_token}"}
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def health_check(self) -> bool:
        """Check API connectivity."""
        try:
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception:
            return False
```

**2. Create the provider** (`providers/your_provider/provider.py`):

```python
from test_coverage_mcp.domain import (
    CoverageProvider,
    ProviderMetadata,
    ProviderHealth,
    ProviderCapability,
    SupportLevel,
    RepositoryCoverageSummary,
)
from .client import YourProviderClient

class YourProvider(CoverageProvider):
    """Your Coverage Service provider implementation."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.client = YourProviderClient(api_token)

    async def get_metadata(self) -> ProviderMetadata:
        """Return provider metadata."""
        return ProviderMetadata(
            name="your_provider",
            version="1.0.0",
            description="Integration with Your Coverage Service",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
                ProviderCapability.BRANCH_COVERAGE,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
                ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
                ProviderCapability.BRANCH_COVERAGE: SupportLevel.BASIC,
            },
            analysis_depths=[],
        )

    async def health_check(self) -> ProviderHealth:
        """Check provider health."""
        import time
        start = time.time()

        try:
            async with self.client as client:
                is_healthy = await client.health_check()
                response_time = (time.time() - start) * 1000

                return ProviderHealth(
                    is_healthy=is_healthy,
                    last_check=datetime.now(timezone.utc).isoformat(),
                    error_message=None if is_healthy else "API unavailable",
                    response_time_ms=response_time,
                )
        except Exception as e:
            return ProviderHealth(
                is_healthy=False,
                last_check=datetime.now(timezone.utc).isoformat(),
                error_message=str(e),
                response_time_ms=(time.time() - start) * 1000,
            )

    async def get_repository_coverage(
        self,
        repo_slug: str,
        ref: Optional[str] = None
    ) -> RepositoryCoverageSummary:
        """Get repository coverage."""
        async with self.client as client:
            data = await client.get_repository_coverage(repo_slug, ref)

            # Transform API response to domain model
            return RepositoryCoverageSummary(
                repository_slug=repo_slug,
                ref=ref or "main",
                coverage_percentage=data["coverage"],
                total_lines=data["total_lines"],
                covered_lines=data["covered_lines"],
                # ... other fields
            )

    # Implement other required methods...
```

## Step 3: Register Your Provider

**Register in the provider registry** (`providers/registry.py`):

```python
from test_coverage_mcp.providers.your_provider import YourProvider

class ProviderRegistry:
    """Registry for coverage providers."""

    _providers = {
        "your_provider": YourProvider,
        # ... other providers
    }

    @classmethod
    def get_provider(cls, name: str, **kwargs) -> CoverageProvider:
        """Get a provider instance."""
        if name not in cls._providers:
            raise ProviderNotFoundError(f"Provider '{name}' not found")

        return cls._providers[name](**kwargs)

    @classmethod
    def list_providers(cls) -> List[str]:
        """List available providers."""
        return list(cls._providers.keys())
```

## Step 4: Configuration

**Create configuration** (`providers/your_provider/config.py`):

```python
import os
from pydantic import BaseSettings

class YourProviderConfig(BaseSettings):
    """Configuration for Your Provider."""

    api_token: str = os.getenv("YOUR_PROVIDER_API_TOKEN", "")
    base_url: str = os.getenv(
        "YOUR_PROVIDER_BASE_URL",
        "https://api.yourservice.com"
    )
    timeout_seconds: int = int(os.getenv("YOUR_PROVIDER_TIMEOUT", "30"))

    class Config:
        env_prefix = "YOUR_PROVIDER_"
```

## Step 5: Testing

**Create tests** (`test/unit_test/providers/test_your_provider.py`):

```python
import pytest
from unittest.mock import AsyncMock, patch
from test_coverage_mcp.providers.your_provider import YourProvider

@pytest.fixture
def provider():
    return YourProvider(api_token="test_token")

@pytest.mark.asyncio
async def test_get_metadata(provider):
    """Test metadata retrieval."""
    metadata = await provider.get_metadata()

    assert metadata.name == "your_provider"
    assert metadata.version == "1.0.0"
    assert len(metadata.supported_capabilities) > 0

@pytest.mark.asyncio
async def test_health_check(provider):
    """Test health check."""
    with patch.object(provider.client, 'health_check', new_callable=AsyncMock) as mock:
        mock.return_value = True

        health = await provider.health_check()

        assert health.is_healthy is True
        assert health.response_time_ms > 0

@pytest.mark.asyncio
async def test_get_repository_coverage(provider):
    """Test repository coverage retrieval."""
    with patch.object(provider.client, 'get_repository_coverage', new_callable=AsyncMock) as mock:
        mock.return_value = {
            "coverage": 85.5,
            "total_lines": 1000,
            "covered_lines": 855,
        }

        coverage = await provider.get_repository_coverage("owner/repo")

        assert coverage.coverage_percentage == 85.5
        assert coverage.total_lines == 1000
```

## Step 6: Documentation

**Create provider documentation** (`docs/contents/mcp-tools/your-provider.md`):

```markdown
# Your Provider Integration

## Overview
Brief description of Your Provider and what it offers.

## Setup

### Prerequisites
- Your Provider account
- API token

### Configuration
Set environment variables:
```bash
export YOUR_PROVIDER_API_TOKEN="your_token"
export YOUR_PROVIDER_BASE_URL="https://api.yourservice.com"
```

## Features
- Feature 1
- Feature 2
- Feature 3

## Limitations
- Limitation 1
- Limitation 2

## Examples
...
```

## Step 7: Integration Testing

**Test with the MCP server**:

```python
from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.providers.registry import ProviderRegistry

# Create server
server = mcp_factory.create()

# Register provider
registry = ProviderRegistry()
provider = registry.get_provider("your_provider", api_token="test_token")

# Test with tools
from test_coverage_mcp.mcp_server.tools import get_repository_test_health

health = get_repository_test_health(
    repo_slug="owner/repo",
    provider="your_provider"
)
```

## Best Practices

✅ **DO**:
- Implement all required methods
- Handle errors gracefully
- Use async/await for I/O operations
- Add comprehensive tests
- Document limitations
- Validate input parameters
- Cache metadata when possible
- Implement proper logging

❌ **DON'T**:
- Block on I/O operations
- Expose API tokens in logs
- Assume API responses are always valid
- Skip error handling
- Ignore rate limits
- Make synchronous API calls
- Store sensitive data in code

## Troubleshooting

### Provider Not Registered
- Ensure provider is added to registry
- Check import statements
- Verify class inheritance

### Health Check Fails
- Verify API token is valid
- Check network connectivity
- Review API endpoint URL
- Check rate limiting

### Data Retrieval Fails
- Verify repository exists in provider
- Check repository slug format
- Verify API permissions
- Review error messages

## Publishing Your Provider

1. Create a separate package: `test-coverage-mcp-{provider_name}`
2. Implement the provider interface
3. Add comprehensive tests
4. Create documentation
5. Submit for inclusion in main project
6. Or publish independently on PyPI

## Examples

- [Codecov Provider](https://github.com/your-org/test-coverage-mcp-codecov)
- [Coveralls Provider](https://github.com/your-org/test-coverage-mcp-coveralls)

## Support

For questions or issues:
- Check existing provider implementations
- Review test cases
- Open an issue on GitHub
- Contact the maintainers

## Next Steps

- **[Configuration Guide](./configuration.md)** - Configure your provider
- **[MCP Tools Overview](../mcp-tools/overview.md)** - Tool specifications
- **[Contributing Guide](../contribute/contribute.md)** - Contribution guidelines
