"""Unit tests for CoverageComparisonService."""

from unittest.mock import MagicMock

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
        supported_capabilities=[ProviderCapability.COVERAGE_DELTA],
        support_levels={
            ProviderCapability.COVERAGE_DELTA: SupportLevel.ADVANCED,
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


def test_comparison_service_initialization(discovery_service):
    """Test service initialization."""
    service = CoverageComparisonService(discovery_service)
    assert service._discovery is discovery_service


def test_compare_refs(discovery_service):
    """Test comparing refs."""
    service = CoverageComparisonService(discovery_service)

    result = service.compare_refs("owner", "repo", "main", "feature")
    assert "base_ref" in result
    assert "head_ref" in result
    assert "base_coverage" in result
    assert "head_coverage" in result
    assert "delta_percentage" in result
    assert "improved" in result
    assert "regression" in result


def test_detect_regressions_no_regression(discovery_service):
    """Test detecting no regression."""
    service = CoverageComparisonService(discovery_service)

    result = service.detect_regressions("owner", "repo", "main", "feature")
    assert "has_regression" in result
    assert "delta_percentage" in result
    assert "severity" in result


def test_detect_regressions_with_regression():
    """Test detecting regression."""
    service = CoverageComparisonService()

    result = service.detect_regressions(
        "owner", "repo", "main", "feature", threshold=1.0
    )
    assert isinstance(result["has_regression"], bool)
    assert isinstance(result["severity"], str)


def test_detect_improvements(discovery_service):
    """Test detecting improvements."""
    service = CoverageComparisonService(discovery_service)

    result = service.detect_improvements("owner", "repo", "main", "feature")
    assert "has_improvement" in result
    assert "delta_percentage" in result
    assert "improvement_percentage" in result


def test_compare_components(discovery_service):
    """Test comparing components."""
    service = CoverageComparisonService(discovery_service)

    result = service.compare_components("owner", "repo", "main", "feature")
    assert "base_ref" in result
    assert "head_ref" in result
    assert "components" in result


def test_compare_flags(discovery_service):
    """Test comparing flags."""
    service = CoverageComparisonService(discovery_service)

    result = service.compare_flags("owner", "repo", "main", "feature")
    assert "base_ref" in result
    assert "head_ref" in result
    assert "flags" in result


def test_calculate_severity_none():
    """Test severity calculation for no regression."""
    service = CoverageComparisonService()

    severity = service._calculate_severity(0.5)
    assert severity == "none"


def test_calculate_severity_minor():
    """Test severity calculation for minor regression."""
    service = CoverageComparisonService()

    severity = service._calculate_severity(-0.5)
    assert severity == "minor"


def test_calculate_severity_major():
    """Test severity calculation for major regression."""
    service = CoverageComparisonService()

    severity = service._calculate_severity(-3.0)
    assert severity == "major"


def test_calculate_severity_critical():
    """Test severity calculation for critical regression."""
    service = CoverageComparisonService()

    severity = service._calculate_severity(-10.0)
    assert severity == "critical"


def test_extract_coverage_empty():
    """Test extracting coverage from empty results."""
    service = CoverageComparisonService()

    coverage = service._extract_coverage({}, "base_coverage")
    assert coverage == 0.0


def test_extract_coverage_with_values():
    """Test extracting coverage from results with values."""
    service = CoverageComparisonService()

    results = {
        "provider1": {"base_coverage": 80.0},
        "provider2": {"base_coverage": 85.0},
    }
    coverage = service._extract_coverage(results, "base_coverage")
    assert coverage == 82.5
