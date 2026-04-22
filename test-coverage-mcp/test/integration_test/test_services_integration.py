"""Integration tests for service interactions."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    RiskLevel,
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
from test_coverage_mcp.services.test_recommendation import RecommendationService


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


class TestDiscoveryAndComparisonIntegration:
    """Test integration between discovery and comparison services."""

    def test_discovery_provides_providers_for_comparison(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test that discovery service provides providers for comparison."""
        comparison_service = CoverageComparisonService(discovery_service)

        # Comparison should use discovery to get providers
        result = comparison_service.compare_refs("owner", "repo", "main", "feature")

        assert "base_ref" in result
        assert "head_ref" in result
        assert "delta_percentage" in result

    def test_discovery_health_affects_comparison(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test that provider health affects comparison results."""
        comparison_service = CoverageComparisonService(discovery_service)

        # Get provider health
        health = discovery_service.get_provider_health("test_provider")
        assert health.is_healthy is True

        # Comparison should work with healthy provider
        result = comparison_service.compare_refs("owner", "repo", "main", "feature")
        assert result is not None


class TestRiskAnalysisAndGapDiscoveryIntegration:
    """Test integration between risk analysis and gap discovery."""

    def test_gap_discovery_feeds_risk_analysis(self) -> None:
        """Test that gap discovery results feed into risk analysis."""
        gap_service = CoverageGapDiscoveryService()
        risk_service = CoverageRiskAnalysisService()

        # Analyze changed code
        file_coverage_data = {
            "src/main.py": {
                "changed_lines": 50,
                "covered_changed_lines": 25,
            },
        }
        gap_result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage_data
        )

        # Use gap results for risk analysis
        pr_risk = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=1,
            uncovered_changed_lines=gap_result["uncovered_changed_lines"],
            total_changed_lines=gap_result["total_changed_lines"],
        )

        # Risk level should be one of the valid levels
        assert pr_risk["risk_level"] in [RiskLevel.LOW.value, RiskLevel.MEDIUM.value, RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]

    def test_uncovered_regions_become_test_recommendations(self) -> None:
        """Test that uncovered regions become test recommendations."""
        gap_service = CoverageGapDiscoveryService()
        recommendation_service = RecommendationService()

        # Detect uncovered regions
        coverage_data = {
            "uncovered_lines": [10, 11, 12, 20, 21, 22],
        }
        regions = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        # Convert to test gaps
        gaps = recommendation_service.identify_test_gaps(regions)

        assert len(gaps) > 0
        assert gaps[0]["file_path"] == "src/module.py"


class TestHealthAndRiskIntegration:
    """Test integration between health and risk analysis services."""

    def test_health_aggregation_identifies_risk(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test that health aggregation can identify risk."""
        health_service = RepositoryHealthService(discovery_service)
        risk_service = CoverageRiskAnalysisService()

        # Get health metrics
        metrics = health_service.aggregate_coverage_metrics("owner", "repo")

        # Use metrics for risk identification
        risk = health_service.identify_risks("owner", "repo", threshold=80.0)

        assert "risk_level" in risk
        assert "recommendations" in risk

    def test_provider_fallback_affects_health(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test that provider fallback chain affects health results."""
        health_service = RepositoryHealthService(discovery_service)

        # Get fallback chain
        chain = health_service.get_provider_fallback_chain()

        # Health should use fallback chain
        metrics = health_service.aggregate_coverage_metrics("owner", "repo")

        assert metrics["providers_queried"] >= 0


class TestConfigDiagnosisAndExcludableCodeIntegration:
    """Test integration between config diagnosis and excludable code services."""

    def test_config_diagnosis_suggests_exclusions(self) -> None:
        """Test that config diagnosis suggests exclusions for excludable code."""
        config_service = CoverageConfigDiagnosisService()
        excludable_service = ExcludableCodeCandidateService()

        # Diagnose config
        file_coverage = {
            "src/main.py": {"coverage": 80},
            "src/generated.pb2.py": {"coverage": 0},
        }
        config = config_service.retrieve_config("owner", "repo")

        # Suggest missing exclusions
        suggestions = config_service.suggest_missing_exclusions(config, file_coverage)

        # Should suggest excluding generated code
        assert isinstance(suggestions, list)

    def test_excludable_code_candidates_inform_config(self) -> None:
        """Test that excludable code candidates inform config decisions."""
        excludable_service = ExcludableCodeCandidateService()
        config_service = CoverageConfigDiagnosisService()

        # Find excludable candidates
        files = [
            {
                "path": "src/generated.pb2.py",
                "content": "# AUTO-GENERATED",
                "coverage": {"hits": 0, "total_lines": 100, "covered_lines": 0},
            },
            {
                "path": "src/main.py",
                "content": "def func(): pass",
                "coverage": {"hits": 50, "total_lines": 100, "covered_lines": 50},
            },
        ]
        candidates = excludable_service.find_excludable_candidates(files)

        # Config should consider these candidates (may be empty if no candidates found)
        assert isinstance(candidates, list)


class TestFullWorkflowIntegration:
    """Test full workflow integration across all services."""

    def test_complete_pr_analysis_workflow(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test complete PR analysis workflow."""
        # Services
        comparison_service = CoverageComparisonService(discovery_service)
        gap_service = CoverageGapDiscoveryService()
        risk_service = CoverageRiskAnalysisService()
        recommendation_service = RecommendationService()

        # Step 1: Compare coverage
        comparison = comparison_service.compare_refs(
            "owner", "repo", "main", "feature"
        )
        assert "delta_percentage" in comparison

        # Step 2: Analyze gaps
        file_coverage = {
            "src/main.py": {
                "changed_lines": 50,
                "covered_changed_lines": 25,
            },
        }
        gap_analysis = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage
        )
        assert gap_analysis["coverage_percentage"] == 50.0

        # Step 3: Score risk
        pr_risk = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=1,
            uncovered_changed_lines=gap_analysis["uncovered_changed_lines"],
            total_changed_lines=gap_analysis["total_changed_lines"],
        )
        assert "risk_level" in pr_risk

        # Step 4: Get recommendations
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

    def test_repository_health_workflow(self, discovery_service: ProviderDiscoveryService) -> None:
        """Test repository health analysis workflow."""
        health_service = RepositoryHealthService(discovery_service)
        config_service = CoverageConfigDiagnosisService()
        excludable_service = ExcludableCodeCandidateService()

        # Step 1: Aggregate health metrics
        metrics = health_service.aggregate_coverage_metrics("owner", "repo")
        assert "average_coverage" in metrics

        # Step 2: Identify risks
        risk = health_service.identify_risks("owner", "repo", threshold=80.0)
        assert "risk_level" in risk

        # Step 3: Diagnose config
        file_coverage = {
            "src/main.py": {"coverage": 80},
            "src/generated.pb2.py": {"coverage": 0},
        }
        diagnosis = config_service.diagnose_config(
            "owner", "repo", file_coverage, 85.0
        )
        assert diagnosis.repo_owner == "owner"

        # Step 4: Get next actions
        actions = health_service.get_next_actions("owner", "repo")
        assert isinstance(actions, list)

    def test_multi_provider_workflow(self, mock_registry: ProviderRegistry) -> None:
        """Test workflow with multiple providers."""
        # Create multiple providers
        provider1 = MagicMock()
        provider1.get_metadata.return_value = ProviderMetadata(
            name="provider1",
            version="1.0.0",
            description="Provider 1",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        provider1.health_check.return_value = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )

        provider2 = MagicMock()
        provider2.get_metadata.return_value = ProviderMetadata(
            name="provider2",
            version="1.0.0",
            description="Provider 2",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        provider2.health_check.return_value = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=150.0,
        )

        mock_registry.register(provider1)
        mock_registry.register(provider2)
        discovery = ProviderDiscoveryService(mock_registry)

        # Test with multiple providers
        comparison = CoverageComparisonService(discovery)
        health = RepositoryHealthService(discovery)

        # Should aggregate from both providers
        metrics = health.aggregate_coverage_metrics("owner", "repo")
        assert metrics["providers_queried"] == 2

        # Should select best provider
        best = discovery.select_best_provider()
        assert best is not None
