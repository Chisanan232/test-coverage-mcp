"""Tests for domain models."""

from datetime import datetime

import pytest

from test_coverage_mcp.domain import (
    AnalysisDepth,
    ConfigDiagnosis,
    CoverageDelta,
    CoverageTestRecommendation,
    ExecutionMetadata,
    FileCoverage,
    ProviderCapability,
    RepositoryCoverageSummary,
    RiskLevel,
    SupportLevel,
    ToolResponseBase,
    UncoveredRegion,
)


class TestExecutionMetadata:
    """Tests for ExecutionMetadata model."""

    def test_execution_metadata_creation(self) -> None:
        """Test creating ExecutionMetadata."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.ADVANCED,
            used_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
            ],
            analysis_depth=AnalysisDepth.FILE,
            execution_time_ms=150.5,
        )

        assert metadata.provider_name == "codecov"
        assert metadata.provider_version == "1.0.0"
        assert metadata.support_level == SupportLevel.ADVANCED
        assert len(metadata.used_capabilities) == 2
        assert metadata.analysis_depth == AnalysisDepth.FILE
        assert metadata.execution_time_ms == 150.5
        assert isinstance(metadata.timestamp, datetime)

    def test_execution_metadata_with_degradation(self) -> None:
        """Test ExecutionMetadata with degradation reason."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.BASIC,
            used_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            analysis_depth=AnalysisDepth.REPOSITORY,
            execution_time_ms=100.0,
            degradation_reason="API rate limit reached",
            limitations=["No file-level coverage", "No trend analysis"],
        )

        assert metadata.degradation_reason == "API rate limit reached"
        assert len(metadata.limitations) == 2


class TestToolResponseBase:
    """Tests for ToolResponseBase model."""

    def test_tool_response_base_creation(self) -> None:
        """Test creating ToolResponseBase."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.ADVANCED,
            used_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            analysis_depth=AnalysisDepth.REPOSITORY,
            execution_time_ms=100.0,
        )

        response = ToolResponseBase(
            summary="Repository has good coverage",
            key_findings=["85% overall coverage", "10 files with low coverage"],
            recommended_next_actions=["Focus on low coverage files", "Add integration tests"],
            confidence_score=0.95,
            execution_metadata=metadata,
        )

        assert response.summary == "Repository has good coverage"
        assert len(response.key_findings) == 2
        assert len(response.recommended_next_actions) == 2
        assert response.confidence_score == 0.95

    def test_tool_response_confidence_validation(self) -> None:
        """Test confidence score validation."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.BASIC,
            used_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            analysis_depth=AnalysisDepth.REPOSITORY,
            execution_time_ms=100.0,
        )

        with pytest.raises(ValueError):
            ToolResponseBase(
                summary="Test",
                key_findings=[],
                recommended_next_actions=[],
                confidence_score=1.5,  # Invalid: > 1.0
                execution_metadata=metadata,
            )


class TestRepositoryCoverageSummary:
    """Tests for RepositoryCoverageSummary model."""

    def test_repository_coverage_summary_creation(self) -> None:
        """Test creating RepositoryCoverageSummary."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.ADVANCED,
            used_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            analysis_depth=AnalysisDepth.REPOSITORY,
            execution_time_ms=100.0,
        )

        summary = RepositoryCoverageSummary(
            summary="Repository coverage summary",
            key_findings=["85% coverage", "Improving trend"],
            recommended_next_actions=["Add tests"],
            confidence_score=0.95,
            execution_metadata=metadata,
            total_coverage_percentage=85.5,
            covered_lines=8550,
            total_lines=10000,
            file_count=150,
            covered_file_count=145,
        )

        assert summary.total_coverage_percentage == 85.5
        assert summary.covered_lines == 8550
        assert summary.total_lines == 10000
        assert summary.file_count == 150


class TestFileCoverage:
    """Tests for FileCoverage model."""

    def test_file_coverage_creation(self) -> None:
        """Test creating FileCoverage."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.ADVANCED,
            used_capabilities=[ProviderCapability.FILE_COVERAGE],
            analysis_depth=AnalysisDepth.FILE,
            execution_time_ms=50.0,
        )

        coverage = FileCoverage(
            summary="File coverage details",
            key_findings=["75% coverage"],
            recommended_next_actions=["Add tests for lines 10-20"],
            confidence_score=0.9,
            execution_metadata=metadata,
            file_path="src/main.py",
            coverage_percentage=75.0,
            covered_lines=150,
            total_lines=200,
            uncovered_lines=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        )

        assert coverage.file_path == "src/main.py"
        assert coverage.coverage_percentage == 75.0
        assert len(coverage.uncovered_lines) == 11


class TestCoverageDelta:
    """Tests for CoverageDelta model."""

    def test_coverage_delta_improvement(self) -> None:
        """Test CoverageDelta with improvement."""
        metadata = ExecutionMetadata(
            provider_name="codecov",
            provider_version="1.0.0",
            support_level=SupportLevel.ADVANCED,
            used_capabilities=[ProviderCapability.COVERAGE_DELTA],
            analysis_depth=AnalysisDepth.REPOSITORY,
            execution_time_ms=100.0,
        )

        delta = CoverageDelta(
            summary="Coverage improved",
            key_findings=["Coverage increased by 5%"],
            recommended_next_actions=[],
            confidence_score=0.98,
            execution_metadata=metadata,
            base_coverage=80.0,
            current_coverage=85.0,
            delta_percentage=5.0,
            delta_lines=500,
            improved=True,
        )

        assert delta.base_coverage == 80.0
        assert delta.current_coverage == 85.0
        assert delta.delta_percentage == 5.0
        assert delta.improved is True


class TestUncoveredRegion:
    """Tests for UncoveredRegion model."""

    def test_uncovered_region_creation(self) -> None:
        """Test creating UncoveredRegion."""
        region = UncoveredRegion(
            file_path="src/utils.py",
            start_line=50,
            end_line=75,
            region_type="function",
            risk_level=RiskLevel.HIGH,
        )

        assert region.file_path == "src/utils.py"
        assert region.start_line == 50
        assert region.end_line == 75
        assert region.region_type == "function"
        assert region.risk_level == RiskLevel.HIGH


class TestCoverageTestRecommendation:
    """Tests for CoverageTestRecommendation model."""

    def test_test_recommendation_creation(self) -> None:
        """Test creating CoverageTestRecommendation."""
        recommendation = CoverageTestRecommendation(
            file_path="src/utils.py",
            start_line=50,
            end_line=75,
            region_type="function",
            test_types=["unit", "integration"],
            scenarios=["happy path", "edge cases", "error handling"],
            priority="high",
            rationale="This function is critical for email validation",
        )

        assert recommendation.file_path == "src/utils.py"
        assert recommendation.start_line == 50
        assert recommendation.end_line == 75
        assert recommendation.region_type == "function"
        assert recommendation.priority == "high"
        assert len(recommendation.test_types) == 2
        assert len(recommendation.scenarios) == 3


class TestConfigDiagnosis:
    """Tests for ConfigDiagnosis model."""

    def test_config_diagnosis_creation(self) -> None:
        """Test creating ConfigDiagnosis."""
        diagnosis = ConfigDiagnosis(
            repo_owner="myorg",
            repo_name="myapp",
            config_valid=False,
            parse_errors=["Invalid YAML syntax"],
            over_included_paths=[
                {
                    "path": "unused/",
                    "reason": "No coverage data found",
                    "suggestion": "Remove from include_paths",
                }
            ],
            missing_exclusions=[
                {
                    "pattern": "**/test/**",
                    "reason": "Test files",
                    "affected_files": 45,
                }
            ],
            threshold_issues=["Minimum threshold is very high (>95%)"],
            scoping_issues=[
                {
                    "component": "api",
                    "issue": "Overlapping paths with component 'utils'",
                    "suggestion": "Clarify path boundaries",
                }
            ],
            summary="Found 4 configuration issues",
        )

        assert diagnosis.repo_owner == "myorg"
        assert diagnosis.repo_name == "myapp"
        assert diagnosis.config_valid is False
        assert len(diagnosis.parse_errors) == 1
        assert len(diagnosis.over_included_paths) == 1
        assert len(diagnosis.missing_exclusions) == 1
