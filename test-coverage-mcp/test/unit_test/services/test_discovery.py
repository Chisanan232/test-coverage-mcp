"""Unit tests for ProviderDiscoveryService."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.registry import ProviderRegistry
from test_coverage_mcp.services.discovery import ProviderDiscoveryService


@pytest.fixture
def mock_registry() -> ProviderRegistry:
    """Create a mock registry."""
    registry = ProviderRegistry()
    registry.clear()
    return registry


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock provider."""
    provider = MagicMock()
    provider.get_metadata.return_value = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[
            ProviderCapability.REPOSITORY_SUMMARY,
            ProviderCapability.FILE_COVERAGE,
        ],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            ProviderCapability.FILE_COVERAGE: SupportLevel.BASIC,
        },
        analysis_depths=[],
    )
    provider.health_check.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=100.0,
    )
    return provider


def test_discovery_service_initialization(mock_registry: ProviderRegistry) -> None:
    """Test service initialization."""
    service = ProviderDiscoveryService(mock_registry)
    assert service._registry is mock_registry


def test_list_providers(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test listing providers."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    providers = service.list_providers()
    assert "test_provider" in providers
    assert providers["test_provider"].name == "test_provider"


def test_get_provider(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test getting a specific provider."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    provider = service.get_provider("test_provider")
    assert provider is not None
    assert provider.get_metadata().name == "test_provider"


def test_get_nonexistent_provider(mock_registry: ProviderRegistry) -> None:
    """Test getting a nonexistent provider."""
    service = ProviderDiscoveryService(mock_registry)
    provider = service.get_provider("nonexistent")
    assert provider is None


def test_set_default_provider(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test setting default provider."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    service.set_default_provider("test_provider")
    default = service.get_default_provider()
    assert default is not None
    assert default.get_metadata().name == "test_provider"


def test_capability_matrix(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test capability matrix generation."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    matrix = service.get_capability_matrix()
    assert "test_provider" in matrix
    assert "repository_summary" in matrix["test_provider"]
    assert matrix["test_provider"]["repository_summary"] == "advanced"


def test_get_providers_for_capability(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test getting providers for a capability."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    providers = service.get_providers_for_capability(
        ProviderCapability.REPOSITORY_SUMMARY
    )
    assert "test_provider" in providers
    assert providers["test_provider"] == "advanced"


def test_get_provider_health(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test getting provider health."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    health = service.get_provider_health("test_provider")
    assert health is not None
    assert health.is_healthy is True
    assert health.response_time_ms == 100.0


def test_get_all_health_status(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test getting all health status."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    health_status = service.get_all_health_status()
    assert "test_provider" in health_status
    assert health_status["test_provider"].is_healthy is True


def test_aggregate_health_empty(mock_registry: ProviderRegistry) -> None:
    """Test aggregating health with no providers."""
    service = ProviderDiscoveryService(mock_registry)
    health = service.aggregate_health()

    assert health["total_providers"] == 0
    assert health["healthy_providers"] == 0
    assert health["health_percentage"] == 0.0


def test_aggregate_health_with_providers(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test aggregating health with providers."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    health = service.aggregate_health()
    assert health["total_providers"] == 1
    assert health["healthy_providers"] == 1
    assert health["health_percentage"] == 100.0
    assert health["avg_response_time_ms"] == 100.0


def test_get_provider_versions(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test getting provider versions."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    versions = service.get_provider_versions()
    assert "test_provider" in versions
    assert versions["test_provider"] == "1.0.0"


def test_select_best_provider_with_default(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test selecting best provider with default set."""
    mock_registry.register(mock_provider)
    mock_registry.set_default("test_provider")
    service = ProviderDiscoveryService(mock_registry)

    best = service.select_best_provider()
    assert best is not None
    assert best.get_metadata().name == "test_provider"


def test_select_best_provider_no_default(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test selecting best provider without default."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    best = service.select_best_provider()
    assert best is not None
    assert best.get_metadata().name == "test_provider"


def test_select_best_provider_with_required_capabilities(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test selecting best provider with required capabilities."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    best = service.select_best_provider(
        required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
    )
    assert best is not None
    assert best.get_metadata().name == "test_provider"


def test_select_best_provider_missing_capability(mock_registry, mock_provider):
    """Test selecting best provider with missing capability."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    best = service.select_best_provider(
        required_capabilities=[ProviderCapability.COVERAGE_TRENDS]
    )
    assert best is None


def test_discover_and_register_providers(mock_registry):
    """Test discovering and registering providers."""
    service = ProviderDiscoveryService(mock_registry)

    with patch("test_coverage_mcp.services.discovery.discover_providers") as mock_discover:
        mock_provider = MagicMock()
        mock_provider.get_metadata.return_value = ProviderMetadata(
            name="discovered_provider",
            version="1.0.0",
            description="Discovered provider",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        mock_discover.return_value = {"discovered_provider": mock_provider}

        result = service.discover_and_register_providers()
        assert "discovered_provider" in result


def test_discover_and_register_providers_handles_duplicates(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> None:
    """Test that duplicate provider registration is handled."""
    mock_registry.register(mock_provider)
    service = ProviderDiscoveryService(mock_registry)

    with patch("test_coverage_mcp.services.discovery.discover_providers") as mock_discover:
        mock_discover.return_value = {"test_provider": mock_provider}

        # Should not raise error for duplicate
        result = service.discover_and_register_providers()
        assert "test_provider" in result


def test_get_provider_health_nonexistent(mock_registry: ProviderRegistry) -> None:
    """Test getting health of nonexistent provider."""
    service = ProviderDiscoveryService(mock_registry)
    health = service.get_provider_health("nonexistent")
    assert health is None


def test_aggregate_health_with_unhealthy_provider(mock_registry: ProviderRegistry) -> None:
    """Test aggregating health with unhealthy provider."""
    unhealthy_provider = MagicMock()
    unhealthy_provider.get_metadata.return_value = ProviderMetadata(
        name="unhealthy_provider",
        version="1.0.0",
        description="Unhealthy provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    unhealthy_provider.health_check.return_value = ProviderHealth(
        is_healthy=False,
        last_check="2024-01-01T00:00:00Z",
        error_message="Connection timeout",
        response_time_ms=5000.0,
    )

    mock_registry.register(unhealthy_provider)
    service = ProviderDiscoveryService(mock_registry)

    health = service.aggregate_health()
    assert health["total_providers"] == 1
    assert health["healthy_providers"] == 0
    assert health["health_percentage"] == 0.0


def test_select_best_provider_by_response_time(mock_registry: ProviderRegistry) -> None:
    """Test selecting best provider by response time."""
    fast_provider = MagicMock()
    fast_provider.get_metadata.return_value = ProviderMetadata(
        name="fast_provider",
        version="1.0.0",
        description="Fast provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    fast_provider.health_check.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=50.0,
    )

    slow_provider = MagicMock()
    slow_provider.get_metadata.return_value = ProviderMetadata(
        name="slow_provider",
        version="1.0.0",
        description="Slow provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    slow_provider.health_check.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=500.0,
    )

    mock_registry.register(fast_provider)
    mock_registry.register(slow_provider)
    service = ProviderDiscoveryService(mock_registry)

    best = service.select_best_provider(
        required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
    )
    assert best is not None
    assert best.get_metadata().name == "fast_provider"
