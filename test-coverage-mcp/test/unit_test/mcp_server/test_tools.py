"""Unit tests for MCP tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.mcp_server.tools.coverage_providers import (
    describe_coverage_provider,
    list_coverage_providers,
)
from test_coverage_mcp.mcp_server.tools.repository_health import (
    get_repository_test_health,
)
from test_coverage_mcp.registry import ProviderRegistry


@pytest.fixture(autouse=True)
def reset_mcp_factory() -> None:
    """Reset MCP factory before each test."""
    mcp_factory.reset()
    mcp_factory.create()
    yield
    mcp_factory.reset()


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


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_list_coverage_providers_basic(mock_discovery_class: MagicMock) -> None:
    """Test list_coverage_providers with basic output."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery

    mock_metadata = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    mock_discovery.list_providers.return_value = {"test_provider": mock_metadata}
    mock_discovery.get_provider_health.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=100.0,
    )
    mock_discovery.get_all_health_status.return_value = {
        "test_provider": ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )
    }

    result = list_coverage_providers(include_capabilities=False, include_health=False)

    assert "providers" in result
    assert "total_providers" in result
    assert result["total_providers"] >= 0
    assert "execution_metadata" in result


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_list_coverage_providers_with_capabilities(mock_discovery_class: MagicMock) -> None:
    """Test list_coverage_providers with capabilities."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery

    mock_metadata = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    mock_discovery.list_providers.return_value = {"test_provider": mock_metadata}
    mock_discovery.get_all_health_status.return_value = {}

    result = list_coverage_providers(include_capabilities=True, include_health=False)

    assert "providers" in result
    if result["providers"]:
        assert "supported_capabilities" in result["providers"][0]


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_describe_coverage_provider_success(mock_discovery_class: MagicMock) -> None:
    """Test describe_coverage_provider with valid provider."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery

    mock_provider = MagicMock()
    mock_metadata = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    mock_provider.get_metadata.return_value = mock_metadata

    mock_discovery.get_provider.return_value = mock_provider
    mock_discovery.get_capability_matrix.return_value = {
        "test_provider": {"repository_summary": "advanced"}
    }
    mock_discovery.get_provider_health.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=100.0,
    )

    result = describe_coverage_provider("test_provider")

    assert "name" in result
    assert "version" in result
    assert "capabilities" in result
    assert "execution_metadata" in result


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_describe_coverage_provider_not_found(mock_discovery_class: MagicMock) -> None:
    """Test describe_coverage_provider with nonexistent provider."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = None

    result = describe_coverage_provider("nonexistent")

    assert "error" in result
    assert "ProviderNotFoundError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
@patch("test_coverage_mcp.mcp_server.tools.repository_health.ProviderDiscoveryService")
def test_get_repository_test_health_success(mock_discovery_class: MagicMock, mock_health_class: MagicMock) -> None:
    """Test get_repository_test_health with valid input."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = MagicMock()

    mock_health = MagicMock()
    mock_health_class.return_value = mock_health
    mock_health.aggregate_coverage_metrics.return_value = {
        "average_coverage": 85.0,
        "coverage_range": {"min": 80.0, "max": 90.0},
        "providers_queried": 1,
        "providers_succeeded": 1,
        "providers_failed": 0,
    }
    mock_health.identify_risks.return_value = {
        "risk_level": "low",
        "current_coverage": 85.0,
        "gap": 0.0,
        "recommendations": ["Continue monitoring coverage"],
    }
    mock_health.get_next_actions.return_value = ["Monitor coverage trends"]

    result = get_repository_test_health("owner/repo", threshold=80.0)

    assert "repo_slug" in result
    assert "coverage_metrics" in result
    assert "health_summary" in result
    assert "risk_analysis" in result
    assert "next_actions" in result
    assert "execution_metadata" in result


def test_get_repository_test_health_invalid_slug() -> None:
    """Test get_repository_test_health with invalid repo slug."""
    result = get_repository_test_health("invalid_slug")

    assert "error" in result
    assert "InvalidRepositorySlugError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
@patch("test_coverage_mcp.mcp_server.tools.repository_health.ProviderDiscoveryService")
def test_get_repository_test_health_provider_not_found(mock_discovery_class: MagicMock, mock_health_class: MagicMock) -> None:
    """Test get_repository_test_health with nonexistent provider."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = None

    result = get_repository_test_health("owner/repo", provider="nonexistent")

    assert "error" in result
    assert "ProviderNotFoundError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_list_coverage_providers_error_handling(mock_discovery_class: MagicMock) -> None:
    """Test list_coverage_providers error handling."""
    mock_discovery_class.side_effect = Exception("Discovery failed")

    result = list_coverage_providers()

    assert "error" in result
    assert "ProviderDiscoveryError" in result.get("error_type", "")
    assert result["providers"] == []


@patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
def test_describe_coverage_provider_error_handling(mock_discovery_class: MagicMock) -> None:
    """Test describe_coverage_provider error handling."""
    mock_discovery_class.side_effect = Exception("Description failed")

    result = describe_coverage_provider("test_provider")

    assert "error" in result
    assert "ProviderDescriptionError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
@patch("test_coverage_mcp.mcp_server.tools.repository_health.ProviderDiscoveryService")
def test_get_repository_test_health_error_handling(mock_discovery_class: MagicMock, mock_health_class: MagicMock) -> None:
    """Test get_repository_test_health error handling."""
    mock_discovery_class.side_effect = Exception("Health analysis failed")

    result = get_repository_test_health("owner/repo")

    assert "error" in result
    assert "RepositoryHealthAnalysisError" in result.get("error_type", "")
