"""Integration tests for services with Codecov provider."""

from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.registry import ProviderRegistry
from test_coverage_mcp.services.comparison import CoverageComparisonService
from test_coverage_mcp.services.discovery import ProviderDiscoveryService
from test_coverage_mcp.services.health import RepositoryHealthService


@pytest.fixture
def mock_codecov_provider():
    """Create a mock Codecov provider."""
    provider = MagicMock()
    provider.get_metadata.return_value = ProviderMetadata(
        name="codecov",
        version="0.1.0",
        description="Codecov coverage provider",
        supported_capabilities=[
            ProviderCapability.REPOSITORY_SUMMARY,
            ProviderCapability.FILE_COVERAGE,
            ProviderCapability.COVERAGE_DELTA,
            ProviderCapability.UNCOVERED_REGIONS,
        ],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
            ProviderCapability.COVERAGE_DELTA: SupportLevel.ENHANCED,
            ProviderCapability.UNCOVERED_REGIONS: SupportLevel.BASIC,
        },
        analysis_depths=[],
    )
    provider.health_check.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=150.0,
    )
    return provider


@pytest.fixture
def registry_with_codecov(mock_codecov_provider):
    """Create a registry with Codecov provider."""
    registry = ProviderRegistry()
    registry.clear()
    registry.register(mock_codecov_provider)
    return registry


@pytest.fixture
def discovery_service(registry_with_codecov):
    """Create a discovery service with Codecov."""
    return ProviderDiscoveryService(registry_with_codecov)


def test_discovery_service_with_codecov(discovery_service):
    """Test discovery service with Codecov provider."""
    providers = discovery_service.list_providers()
    assert "codecov" in providers
    assert providers["codecov"].name == "codecov"


def test_capability_matrix_with_codecov(discovery_service):
    """Test capability matrix with Codecov."""
    matrix = discovery_service.get_capability_matrix()
    assert "codecov" in matrix
    assert matrix["codecov"]["repository_summary"] == "advanced"
    assert matrix["codecov"]["file_coverage"] == "advanced"


def test_health_service_with_codecov(discovery_service):
    """Test health service with Codecov."""
    service = RepositoryHealthService(discovery_service)

    metrics = service.aggregate_coverage_metrics("owner", "repo")
    assert metrics["providers_queried"] == 1
    assert metrics["providers_succeeded"] >= 0


def test_risk_identification_with_codecov(discovery_service):
    """Test risk identification with Codecov."""
    service = RepositoryHealthService(discovery_service)

    risk = service.identify_risks("owner", "repo", threshold=80.0)
    assert "risk_level" in risk
    assert "recommendations" in risk


def test_comparison_service_with_codecov(discovery_service):
    """Test comparison service with Codecov."""
    service = CoverageComparisonService(discovery_service)

    result = service.compare_refs("owner", "repo", "main", "feature")
    assert result["base_ref"] == "main"
    assert result["head_ref"] == "feature"


def test_regression_detection_with_codecov(discovery_service):
    """Test regression detection with Codecov."""
    service = CoverageComparisonService(discovery_service)

    result = service.detect_regressions("owner", "repo", "main", "feature")
    assert "has_regression" in result
    assert "severity" in result


def test_improvement_detection_with_codecov(discovery_service):
    """Test improvement detection with Codecov."""
    service = CoverageComparisonService(discovery_service)

    result = service.detect_improvements("owner", "repo", "main", "feature")
    assert "has_improvement" in result
    assert "improvement_percentage" in result


def test_provider_selection_with_codecov(discovery_service):
    """Test provider selection with Codecov."""
    best = discovery_service.select_best_provider(
        required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
    )
    assert best is not None
    assert best.get_metadata().name == "codecov"


def test_fallback_chain_with_codecov(discovery_service):
    """Test fallback chain with Codecov."""
    service = RepositoryHealthService(discovery_service)

    chain = service.get_provider_fallback_chain(
        required_capabilities=[ProviderCapability.COVERAGE_DELTA]
    )
    assert isinstance(chain, list)
    assert len(chain) > 0


def test_health_aggregation_with_codecov(discovery_service):
    """Test health aggregation with Codecov."""
    health = discovery_service.aggregate_health()
    assert health["total_providers"] == 1
    assert health["healthy_providers"] == 1
    assert health["health_percentage"] == 100.0


def test_version_tracking_with_codecov(discovery_service):
    """Test version tracking with Codecov."""
    versions = discovery_service.get_provider_versions()
    assert "codecov" in versions
    assert versions["codecov"] == "0.1.0"


def test_next_actions_with_codecov(discovery_service):
    """Test next actions generation with Codecov."""
    service = RepositoryHealthService(discovery_service)

    actions = service.get_next_actions("owner", "repo")
    assert isinstance(actions, list)
