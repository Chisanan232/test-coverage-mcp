"""Unit tests for RepositoryHealthService."""

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
from test_coverage_mcp.services.health import RepositoryHealthService


@pytest.fixture
def mock_registry() -> ProviderRegistry:
    """Create a mock registry."""
    registry = ProviderRegistry()
    registry.clear()
    return registry


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = MagicMock()
    provider.get_metadata.return_value = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
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


@pytest.fixture
def discovery_service(mock_registry, mock_provider):
    """Create a discovery service with mock provider."""
    mock_registry.register(mock_provider)
    return ProviderDiscoveryService(mock_registry)


def test_health_service_initialization(discovery_service):
    """Test service initialization."""
    service = RepositoryHealthService(discovery_service)
    assert service._discovery is discovery_service


def test_aggregate_coverage_metrics(discovery_service):
    """Test aggregating coverage metrics."""
    service = RepositoryHealthService(discovery_service)

    metrics = service.aggregate_coverage_metrics("owner", "repo")
    assert "providers_queried" in metrics
    assert "providers_succeeded" in metrics
    assert "average_coverage" in metrics
    assert "coverage_range" in metrics


def test_identify_risks_low(discovery_service):
    """Test identifying low risk."""
    service = RepositoryHealthService(discovery_service)

    risk = service.identify_risks("owner", "repo", threshold=80.0)
    assert "risk_level" in risk
    assert "coverage_below_threshold" in risk
    assert "recommendations" in risk


def test_identify_risks_high(discovery_service):
    """Test identifying high risk."""
    service = RepositoryHealthService(discovery_service)

    risk = service.identify_risks("owner", "repo", threshold=95.0)
    assert "risk_level" in risk
    assert isinstance(risk["recommendations"], list)


def test_get_next_actions(discovery_service):
    """Test getting next actions."""
    service = RepositoryHealthService(discovery_service)

    actions = service.get_next_actions("owner", "repo")
    assert isinstance(actions, list)


def test_get_provider_fallback_chain(discovery_service):
    """Test getting provider fallback chain."""
    service = RepositoryHealthService(discovery_service)

    chain = service.get_provider_fallback_chain()
    assert isinstance(chain, list)
    assert len(chain) > 0


def test_get_provider_fallback_chain_with_capabilities(discovery_service):
    """Test getting provider fallback chain with required capabilities."""
    service = RepositoryHealthService(discovery_service)

    chain = service.get_provider_fallback_chain(
        required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
    )
    assert isinstance(chain, list)


def test_generate_risk_recommendations():
    """Test generating risk recommendations."""
    service = RepositoryHealthService()

    recommendations = service._generate_risk_recommendations(50.0, 80.0)
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert any("50" in rec for rec in recommendations)


def test_generate_risk_recommendations_critical():
    """Test generating recommendations for critical coverage."""
    service = RepositoryHealthService()

    recommendations = service._generate_risk_recommendations(30.0, 80.0)
    assert any("Critical" in rec for rec in recommendations)


def test_generate_risk_recommendations_high():
    """Test generating recommendations for high coverage."""
    service = RepositoryHealthService()

    recommendations = service._generate_risk_recommendations(60.0, 80.0)
    assert any("High priority" in rec for rec in recommendations)
