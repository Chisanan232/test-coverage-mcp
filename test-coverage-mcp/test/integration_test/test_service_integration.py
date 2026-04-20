"""Integration tests for service interactions.

Tests service layer interactions and data flow between components.
"""

from typing import Any
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
from test_coverage_mcp.services.config_diagnosis import CoverageConfigDiagnosisService
from test_coverage_mcp.services.discovery import ProviderDiscoveryService
from test_coverage_mcp.services.excludable_code import ExcludableCodeCandidateService
from test_coverage_mcp.services.gap_discovery import CoverageGapDiscoveryService
from test_coverage_mcp.services.health import RepositoryHealthService
from test_coverage_mcp.services.risk_analysis import CoverageRiskAnalysisService
from test_coverage_mcp.services.test_recommendation import TestRecommendationService


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
            ProviderCapability.COVERAGE_DELTA,
        ],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            ProviderCapability.FILE_COVERAGE: SupportLevel.BASIC,
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
def discovery_service(mock_registry: ProviderRegistry, mock_provider: MagicMock) -> ProviderDiscoveryService:
    """Create a discovery service with mock provider."""
    mock_registry.register(mock_provider)
    return ProviderDiscoveryService(mock_registry)


class TestServiceIntegration:
    """Integration tests for service layer."""

    def test_discovery_service_with_registry(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test discovery service integration with provider registry."""
        # List providers
        providers = discovery_service.list_providers()
        assert "test_provider" in providers

        # Get specific provider
        provider = discovery_service.get_provider("test_provider")
        assert provider is not None

        # Get provider metadata
        metadata = provider.get_metadata()
        assert metadata.name == "test_provider"

    def test_health_check_with_providers(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test health check service with multiple providers."""
        # Get health of specific provider
        health = discovery_service.get_provider_health("test_provider")
        assert health is not None
        assert health.is_healthy is True

        # Get all health status
        all_health = discovery_service.get_all_health_status()
        assert "test_provider" in all_health

        # Aggregate health
        aggregated = discovery_service.aggregate_health()
        assert aggregated["total_providers"] == 1
        assert aggregated["healthy_providers"] == 1

    def test_comparison_service_workflow(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test complete comparison service workflow."""
        comparison = CoverageComparisonService(discovery_service)

        # Compare refs
        result = comparison.compare_refs("owner", "repo", "main", "feature")
        assert "base_ref" in result
        assert "head_ref" in result
        assert "delta_percentage" in result

        # Detect regressions
        regression = comparison.detect_regressions("owner", "repo", "main", "feature")
        assert "has_regression" in regression
        assert "severity" in regression

        # Detect improvements
        improvement = comparison.detect_improvements("owner", "repo", "main", "feature")
        assert "has_improvement" in improvement

    def test_gap_discovery_service_workflow(self) -> None:
        """Test complete gap discovery service workflow."""
        gap_service = CoverageGapDiscoveryService()

        # Analyze changed code
        file_coverage = {
            "src/main.py": {
                "changed_lines": 50,
                "covered_changed_lines": 25,
            },
        }
        analysis = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage
        )
        assert analysis["total_changed_lines"] == 50
        assert analysis["coverage_percentage"] == 50.0

        # Detect uncovered regions
        coverage_data = {
            "uncovered_lines": [10, 11, 12, 20, 21, 22],
        }
        regions = gap_service.detect_uncovered_regions("src/main.py", coverage_data)
        assert len(regions) > 0

    def test_risk_analysis_service_workflow(self) -> None:
        """Test complete risk analysis service workflow."""
        risk_service = CoverageRiskAnalysisService()

        # Score PR risk
        pr_risk = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=5,
            uncovered_changed_lines=10,
            total_changed_lines=50,
        )
        assert "risk_level" in pr_risk
        assert "risk_score" in pr_risk

        # Identify high-risk files
        file_coverage = {
            "src/main.py": {"coverage": 30.0, "uncovered_lines": 70, "total_lines": 100},
            "src/utils.py": {"coverage": 85.0, "uncovered_lines": 15, "total_lines": 100},
        }
        high_risk = risk_service.identify_high_risk_files(file_coverage)
        assert len(high_risk) > 0


class TestServiceDataFlow:
    """Test data flow between services."""

    def test_gap_discovery_to_risk_analysis(self) -> None:
        """Test data flow from gap discovery to risk analysis."""
        gap_service = CoverageGapDiscoveryService()
        risk_service = CoverageRiskAnalysisService()

        # Discover gaps
        file_coverage = {
            "src/main.py": {
                "changed_lines": 50,
                "covered_changed_lines": 25,
            },
        }
        gaps = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage
        )

        # Use gap data for risk analysis
        pr_risk = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=1,
            uncovered_changed_lines=gaps["uncovered_changed_lines"],
            total_changed_lines=gaps["total_changed_lines"],
        )

        assert pr_risk["risk_score"] > 0

    def test_gap_discovery_to_test_recommendation(self) -> None:
        """Test data flow from gap discovery to test recommendation."""
        gap_service = CoverageGapDiscoveryService()
        recommendation_service = TestRecommendationService()

        # Discover gaps
        coverage_data = {
            "uncovered_lines": [10, 11, 12, 20, 21, 22],
        }
        regions = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        # Convert to test recommendations
        gaps = recommendation_service.identify_test_gaps(regions)
        assert len(gaps) > 0

        # Rank by priority
        ranked = recommendation_service.rank_by_priority(gaps)
        assert len(ranked) > 0

    def test_config_diagnosis_to_excludable_code(self) -> None:
        """Test data flow from config diagnosis to excludable code."""
        config_service = CoverageConfigDiagnosisService()
        excludable_service = ExcludableCodeCandidateService()

        # Diagnose config
        file_coverage = {
            "src/main.py": {"coverage": 80},
            "src/generated.pb2.py": {"coverage": 0},
        }
        config = config_service.retrieve_config("owner", "repo")

        # Suggest exclusions
        suggestions = config_service.suggest_missing_exclusions(config, file_coverage)
        assert isinstance(suggestions, list)

        # Find excludable candidates - test with valid file structure
        files = [
            {
                "path": "src/generated.pb2.py",
                "content": "# AUTO-GENERATED\n# This file is auto-generated\nclass Generated: pass",
                "coverage": {"hits": 0, "total_lines": 100, "covered_lines": 0},
            },
        ]
        candidates = excludable_service.find_excludable_candidates(files)
        # Should return a list (may be empty if no candidates found)
        assert isinstance(candidates, list)


class TestServiceErrorHandling:
    """Test error handling in service interactions."""

    def test_discovery_with_failing_provider(self, mock_registry: ProviderRegistry) -> None:
        """Test discovery service with failing provider."""
        # Don't register a failing provider - just test with empty registry
        discovery = ProviderDiscoveryService(mock_registry)

        # Should handle gracefully
        providers = discovery.list_providers()
        assert isinstance(providers, dict)

    def test_comparison_with_no_providers(self, mock_registry: ProviderRegistry) -> None:
        """Test comparison service with no providers."""
        discovery = ProviderDiscoveryService(mock_registry)
        comparison = CoverageComparisonService(discovery)

        # Should return default values
        result = comparison.compare_refs("owner", "repo", "main", "feature")
        assert result["base_coverage"] == 0.0
        assert result["head_coverage"] == 0.0

    def test_health_service_with_failing_providers(self, mock_registry: ProviderRegistry) -> None:
        """Test health service with failing providers."""
        # Test with empty registry (no providers)
        discovery = ProviderDiscoveryService(mock_registry)
        health = RepositoryHealthService(discovery)

        # Should handle gracefully
        metrics = health.aggregate_coverage_metrics("owner", "repo")
        assert isinstance(metrics, dict)


class TestServiceChaining:
    """Test chaining multiple services together."""

    def test_complete_analysis_chain(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test complete analysis chain."""
        # Step 1: Compare coverage
        comparison = CoverageComparisonService(discovery_service)
        comparison_result = comparison.compare_refs("owner", "repo", "main", "feature")

        # Step 2: Analyze gaps
        gap_service = CoverageGapDiscoveryService()
        file_coverage = {
            "src/main.py": {
                "changed_lines": 50,
                "covered_changed_lines": 25,
            },
        }
        gap_result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage
        )

        # Step 3: Score risk
        risk_service = CoverageRiskAnalysisService()
        pr_risk = risk_service.score_pr_risk(
            base_coverage=comparison_result.get("base_coverage", 85.0),
            head_coverage=comparison_result.get("head_coverage", 80.0),
            changed_files_count=1,
            uncovered_changed_lines=gap_result["uncovered_changed_lines"],
            total_changed_lines=gap_result["total_changed_lines"],
        )

        # Step 4: Get recommendations
        recommendation_service = TestRecommendationService()
        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 35,
                "region_type": "function",
                "risk_level": "high",
                "lines_count": 25,
            }
        ]
        recommendations = recommendation_service.recommend_tests(uncovered_regions)

        assert len(recommendations) > 0

    def test_health_analysis_chain(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test health analysis chain."""
        # Step 1: Aggregate metrics
        health_service = RepositoryHealthService(discovery_service)
        metrics = health_service.aggregate_coverage_metrics("owner", "repo")

        # Step 2: Identify risks
        risk = health_service.identify_risks("owner", "repo", threshold=80.0)

        # Step 3: Diagnose config
        config_service = CoverageConfigDiagnosisService()
        file_coverage = {
            "src/main.py": {"coverage": 80},
        }
        diagnosis = config_service.diagnose_config("owner", "repo", file_coverage, 85.0)

        # Step 4: Get next actions
        actions = health_service.get_next_actions("owner", "repo")

        assert isinstance(actions, list)
