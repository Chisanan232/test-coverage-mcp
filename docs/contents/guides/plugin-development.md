# Provider Plugin Development Guide

## Overview

This guide explains how to develop custom coverage provider plugins for test-coverage-mcp.

## Plugin Architecture

Plugins are Python packages that implement the provider interface and are discovered automatically at runtime.

## Provider Interface

All providers must implement the `CoverageProvider` interface:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CoverageProvider(ABC):
    """Base interface for coverage providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Provider version."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check provider health."""
        pass

    @abstractmethod
    def get_repository_coverage(
        self, repo_slug: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get repository coverage."""
        pass

    @abstractmethod
    def get_file_coverage(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file coverage."""
        pass

    @abstractmethod
    def compare_coverage(
        self, repo_slug: str, base_ref: str, head_ref: str
    ) -> Dict[str, Any]:
        """Compare coverage between refs."""
        pass

    @abstractmethod
    def get_uncovered_regions(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get uncovered regions."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """Get provider capabilities."""
        pass
```

## Creating a Plugin

### 1. Project Structure

```
my-coverage-provider/
├── src/
│   └── my_coverage_provider/
│       ├── __init__.py
│       ├── provider.py
│       ├── client.py
│       └── models.py
├── test/
│   ├── unit_test/
│   │   └── test_provider.py
│   └── integration_test/
│       └── test_provider_integration.py
├── pyproject.toml
└── README.md
```

### 2. Implement Provider

**provider.py**:
```python
from typing import Any, Dict, List, Optional
from test_coverage_mcp.domain.models import CoverageProvider


class MyProvider(CoverageProvider):
    """My custom coverage provider."""

    def __init__(self, api_token: str):
        """Initialize provider.

        Args:
            api_token: API token for authentication
        """
        self.api_token = api_token
        self.client = MyAPIClient(api_token)

    @property
    def name(self) -> str:
        """Provider name."""
        return "my-provider"

    @property
    def version(self) -> str:
        """Provider version."""
        return "1.0.0"

    def health_check(self) -> Dict[str, Any]:
        """Check provider health."""
        try:
            status = self.client.check_health()
            return {
                "status": "healthy" if status else "unhealthy",
                "name": self.name,
                "version": self.version,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_repository_coverage(
        self, repo_slug: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get repository coverage."""
        coverage_data = self.client.get_coverage(repo_slug, ref)
        return {
            "repo_slug": repo_slug,
            "ref": ref or "master",
            "coverage": coverage_data["coverage_percent"],
            "files_count": coverage_data["files_count"],
            "lines_covered": coverage_data["lines_covered"],
            "lines_total": coverage_data["lines_total"],
        }

    def get_file_coverage(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file coverage."""
        file_data = self.client.get_file_coverage(repo_slug, file_path, ref)
        return {
            "repo_slug": repo_slug,
            "file_path": file_path,
            "ref": ref or "master",
            "coverage": file_data["coverage_percent"],
            "lines_covered": file_data["lines_covered"],
            "lines_total": file_data["lines_total"],
        }

    def compare_coverage(
        self, repo_slug: str, base_ref: str, head_ref: str
    ) -> Dict[str, Any]:
        """Compare coverage between refs."""
        base = self.client.get_coverage(repo_slug, base_ref)
        head = self.client.get_coverage(repo_slug, head_ref)
        delta = head["coverage_percent"] - base["coverage_percent"]

        return {
            "repo_slug": repo_slug,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "base_coverage": base["coverage_percent"],
            "head_coverage": head["coverage_percent"],
            "delta": delta,
            "status": "improved" if delta > 0 else "degraded",
        }

    def get_uncovered_regions(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get uncovered regions."""
        regions = self.client.get_uncovered_regions(repo_slug, file_path, ref)
        return [
            {
                "line_start": region["start_line"],
                "line_end": region["end_line"],
                "type": region["type"],
                "risk_level": self._assess_risk(region),
            }
            for region in regions
        ]

    def get_capabilities(self) -> Dict[str, bool]:
        """Get provider capabilities."""
        return {
            "repository_summary": True,
            "file_coverage": True,
            "coverage_delta": True,
            "uncovered_regions": True,
            "branch_coverage": True,
            "line_coverage": True,
        }

    def _assess_risk(self, region: Dict[str, Any]) -> str:
        """Assess risk level of uncovered region."""
        # Custom logic for risk assessment
        if region["type"] == "branch":
            return "medium"
        elif region["type"] == "line":
            return "high"
        return "low"
```

### 3. API Client

**client.py**:
```python
import httpx
from typing import Any, Dict, List, Optional


class MyAPIClient:
    """API client for my coverage provider."""

    BASE_URL = "https://api.my-provider.com"

    def __init__(self, api_token: str):
        """Initialize client."""
        self.api_token = api_token
        self.client = httpx.Client(
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30.0,
        )

    def check_health(self) -> bool:
        """Check API health."""
        try:
            response = self.client.get(f"{self.BASE_URL}/health")
            return response.status_code == 200
        except Exception:
            return False

    def get_coverage(
        self, repo_slug: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get repository coverage."""
        params = {"repo": repo_slug}
        if ref:
            params["ref"] = ref

        response = self.client.get(
            f"{self.BASE_URL}/coverage",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get_file_coverage(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file coverage."""
        params = {"repo": repo_slug, "file": file_path}
        if ref:
            params["ref"] = ref

        response = self.client.get(
            f"{self.BASE_URL}/coverage/file",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get_uncovered_regions(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get uncovered regions."""
        params = {"repo": repo_slug, "file": file_path}
        if ref:
            params["ref"] = ref

        response = self.client.get(
            f"{self.BASE_URL}/coverage/uncovered",
            params=params,
        )
        response.raise_for_status()
        return response.json()["regions"]
```

### 4. Configuration

**pyproject.toml**:
```toml
[project]
name = "my-coverage-provider"
version = "1.0.0"
description = "My custom coverage provider for test-coverage-mcp"
dependencies = [
    "test-coverage-mcp>=0.1.0",
    "httpx>=0.28.0",
]

[project.entry-points."test_coverage_mcp.providers"]
my-provider = "my_coverage_provider.provider:MyProvider"
```

### 5. Testing

**test/unit_test/test_provider.py**:
```python
import pytest
from my_coverage_provider.provider import MyProvider


class TestMyProvider:
    """Tests for MyProvider."""

    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return MyProvider(api_token="test-token")

    def test_provider_name(self, provider):
        """Test provider name."""
        assert provider.name == "my-provider"

    def test_provider_version(self, provider):
        """Test provider version."""
        assert provider.version == "1.0.0"

    def test_get_capabilities(self, provider):
        """Test capabilities."""
        caps = provider.get_capabilities()
        assert caps["repository_summary"] is True
        assert caps["file_coverage"] is True

    def test_health_check(self, provider):
        """Test health check."""
        # Mock the API client
        health = provider.health_check()
        assert "status" in health
```

## Plugin Discovery

Plugins are discovered automatically using Python entry points:

```python
# In pyproject.toml
[project.entry-points."test_coverage_mcp.providers"]
my-provider = "my_coverage_provider.provider:MyProvider"
```

The registry will:
1. Scan installed packages for entry points
2. Load provider classes
3. Instantiate with configuration
4. Register in the provider registry

## Configuration

Providers are configured via environment variables:

```bash
# Token-based authentication
export MY_PROVIDER_TOKEN="your-api-token"

# Custom endpoint
export MY_PROVIDER_ENDPOINT="https://custom.api.com"

# Timeout settings
export MY_PROVIDER_TIMEOUT="30"
```

## Best Practices

### 1. Error Handling
- Wrap API calls in try-except
- Return meaningful error messages
- Implement health checks
- Handle timeouts gracefully

### 2. Performance
- Cache results when appropriate
- Implement request timeouts
- Batch API calls
- Use connection pooling

### 3. Type Safety
- Use type hints throughout
- Validate input parameters
- Use Pydantic models
- Document return types

### 4. Testing
- Unit test all methods
- Mock external APIs
- Test error scenarios
- Verify interface compliance

### 5. Documentation
- Document configuration options
- Provide usage examples
- Explain capabilities
- Include troubleshooting

## Publishing Your Plugin

1. Create GitHub repository
2. Add to PyPI
3. Document in README
4. Add to plugin registry
5. Create example configuration

## Example Plugins

See the Codecov provider implementation for a complete example:
- `test-coverage-mcp-codecov` package
- Full implementation with tests
- Production-ready code

## Support

For questions or issues:
- GitHub Issues: https://github.com/Chisanan232/test-coverage-mcp/issues
- Documentation: https://test-coverage-mcp.readthedocs.io/
- Discussions: https://github.com/Chisanan232/test-coverage-mcp/discussions
