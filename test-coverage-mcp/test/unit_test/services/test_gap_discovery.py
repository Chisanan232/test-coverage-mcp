"""Unit tests for CoverageGapDiscoveryService."""

import pytest

from test_coverage_mcp.domain import RiskLevel
from test_coverage_mcp.services.gap_discovery import CoverageGapDiscoveryService


@pytest.fixture
def gap_service():
    """Create a CoverageGapDiscoveryService instance."""
    return CoverageGapDiscoveryService()


class TestAnalyzeChangedCode:
    """Tests for changed code analysis."""

    def test_analyze_changed_code_all_covered(self, gap_service):
        """Test analyzing changed code that is all covered."""
        file_coverage_data = {
            "src/module.py": {
                "changed_lines": 20,
                "covered_changed_lines": 20,
            },
        }

        result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage_data
        )

        assert result["total_changed_lines"] == 20
        assert result["covered_changed_lines"] == 20
        assert result["uncovered_changed_lines"] == 0
        assert result["coverage_percentage"] == 100.0

    def test_analyze_changed_code_partial_coverage(self, gap_service):
        """Test analyzing changed code with partial coverage."""
        file_coverage_data = {
            "src/module1.py": {
                "changed_lines": 30,
                "covered_changed_lines": 20,
            },
            "src/module2.py": {
                "changed_lines": 20,
                "covered_changed_lines": 15,
            },
        }

        result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage_data
        )

        assert result["total_changed_lines"] == 50
        assert result["covered_changed_lines"] == 35
        assert result["uncovered_changed_lines"] == 15
        assert result["coverage_percentage"] == 70.0
        assert len(result["files_with_gaps"]) == 2

    def test_analyze_changed_code_no_coverage(self, gap_service):
        """Test analyzing changed code with no coverage."""
        file_coverage_data = {
            "src/module.py": {
                "changed_lines": 25,
                "covered_changed_lines": 0,
            },
        }

        result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", file_coverage_data
        )

        assert result["coverage_percentage"] == 0.0
        assert result["uncovered_changed_lines"] == 25

    def test_analyze_changed_code_no_data(self, gap_service):
        """Test analyzing changed code with no file data."""
        result = gap_service.analyze_changed_code(
            "owner", "repo", "main", "feature", {}
        )

        assert result["total_changed_lines"] == 0
        assert result["coverage_percentage"] == 0.0


class TestDetectUncoveredRegions:
    """Tests for uncovered region detection."""

    def test_detect_uncovered_regions_single_region(self, gap_service):
        """Test detecting a single uncovered region."""
        coverage_data = {
            "uncovered_lines": [10, 11, 12, 13, 14],
        }

        result = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        assert len(result) == 1
        assert result[0]["start_line"] == 10
        assert result[0]["end_line"] == 14
        assert result[0]["lines_count"] == 5

    def test_detect_uncovered_regions_multiple_regions(self, gap_service):
        """Test detecting multiple uncovered regions."""
        coverage_data = {
            "uncovered_lines": [10, 11, 12, 20, 21, 22, 30],
        }

        result = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        assert len(result) == 3
        assert result[0]["start_line"] == 10
        assert result[0]["end_line"] == 12
        assert result[1]["start_line"] == 20
        assert result[2]["start_line"] == 30

    def test_detect_uncovered_regions_with_risk_levels(self, gap_service):
        """Test that uncovered regions have risk levels."""
        coverage_data = {
            "uncovered_lines": list(range(10, 70)),  # 60 lines
        }

        result = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        assert len(result) == 1
        assert "risk_level" in result[0]
        assert result[0]["risk_level"] in [
            RiskLevel.LOW.value,
            RiskLevel.MEDIUM.value,
            RiskLevel.HIGH.value,
            RiskLevel.CRITICAL.value,
        ]

    def test_detect_uncovered_regions_empty(self, gap_service):
        """Test detecting uncovered regions with no uncovered lines."""
        coverage_data = {"uncovered_lines": []}

        result = gap_service.detect_uncovered_regions("src/module.py", coverage_data)

        assert len(result) == 0


class TestAnalyzePartiallyCoveredRegions:
    """Tests for partially covered region analysis."""

    def test_analyze_partially_covered_regions_basic(self, gap_service):
        """Test analyzing partially covered regions."""
        coverage_data = {
            "coverage_by_line": {
                10: True,
                11: True,
                12: False,
                13: False,
                14: True,
                15: True,
            },
        }

        result = gap_service.analyze_partially_covered_regions("src/module.py", coverage_data)

        assert len(result) > 0
        assert all("coverage_percentage" in r for r in result)
        assert all("risk_level" in r for r in result)

    def test_analyze_partially_covered_regions_empty(self, gap_service):
        """Test analyzing partially covered regions with no data."""
        coverage_data = {"coverage_by_line": {}}

        result = gap_service.analyze_partially_covered_regions("src/module.py", coverage_data)

        assert len(result) == 0

    def test_analyze_partially_covered_regions_all_covered(self, gap_service):
        """Test analyzing when all lines are covered."""
        coverage_data = {
            "coverage_by_line": {
                10: True,
                11: True,
                12: True,
            },
        }

        result = gap_service.analyze_partially_covered_regions("src/module.py", coverage_data)

        # Should return empty since there's no mixed coverage
        assert len(result) == 0

    def test_analyze_partially_covered_regions_risk_levels(self, gap_service):
        """Test that partially covered regions have correct risk levels."""
        coverage_data = {
            "coverage_by_line": {
                10: True,
                11: False,
                12: False,
                13: False,
                14: False,
                15: False,
                16: False,
                17: False,
                18: False,
                19: False,
            },
        }

        result = gap_service.analyze_partially_covered_regions("src/module.py", coverage_data)

        if result:
            # Should have high or critical risk due to low coverage
            assert result[0]["risk_level"] in [
                RiskLevel.HIGH.value,
                RiskLevel.CRITICAL.value,
            ]


class TestHandlePendingAnalysis:
    """Tests for pending analysis handling."""

    def test_handle_pending_analysis_with_pending(self, gap_service):
        """Test handling pending analysis."""
        pending_data = {
            "coverage": 75.0,
            "pending_regions": [
                {"start": 10, "end": 20},
                {"start": 50, "end": 60},
            ],
            "pending_coverage_estimate": 85.0,
        }

        result = gap_service.handle_pending_analysis("src/module.py", pending_data)

        assert result["has_pending"] is True
        assert result["pending_regions_count"] == 2
        assert result["estimated_coverage"] == 85.0
        assert len(result["recommendations"]) > 0

    def test_handle_pending_analysis_no_pending(self, gap_service):
        """Test handling when no pending analysis."""
        pending_data = {
            "coverage": 90.0,
            "pending_regions": [],
        }

        result = gap_service.handle_pending_analysis("src/module.py", pending_data)

        assert result["has_pending"] is False
        assert result["pending_regions_count"] == 0
        assert len(result["recommendations"]) == 0

    def test_handle_pending_analysis_includes_recommendations(self, gap_service):
        """Test that pending analysis includes recommendations."""
        pending_data = {
            "coverage": 70.0,
            "pending_regions": [{"start": 10, "end": 20}],
        }

        result = gap_service.handle_pending_analysis("src/module.py", pending_data)

        assert "recommendations" in result
        assert any("Pending" in r for r in result["recommendations"])


class TestGroupUncoveredLines:
    """Tests for grouping uncovered lines."""

    def test_group_uncovered_lines_single_group(self, gap_service):
        """Test grouping consecutive uncovered lines."""
        uncovered_lines = [10, 11, 12, 13, 14]

        result = gap_service._group_uncovered_lines(uncovered_lines)

        assert len(result) == 1
        assert result[0]["start"] == 10
        assert result[0]["end"] == 14

    def test_group_uncovered_lines_multiple_groups(self, gap_service):
        """Test grouping non-consecutive uncovered lines."""
        uncovered_lines = [10, 11, 12, 20, 21, 30]

        result = gap_service._group_uncovered_lines(uncovered_lines)

        assert len(result) == 3
        assert result[0]["start"] == 10
        assert result[1]["start"] == 20
        assert result[2]["start"] == 30

    def test_group_uncovered_lines_empty(self, gap_service):
        """Test grouping empty uncovered lines."""
        result = gap_service._group_uncovered_lines([])

        assert len(result) == 0

    def test_group_uncovered_lines_duplicates(self, gap_service):
        """Test grouping with duplicate line numbers."""
        uncovered_lines = [10, 10, 11, 11, 12]

        result = gap_service._group_uncovered_lines(uncovered_lines)

        assert len(result) == 1
        assert result[0]["start"] == 10
        assert result[0]["end"] == 12


class TestInferRegionType:
    """Tests for region type inference."""

    def test_infer_region_type_class(self, gap_service):
        """Test inferring class region type."""
        region_type = gap_service._infer_region_type(100, {})
        assert region_type == "class"

    def test_infer_region_type_function(self, gap_service):
        """Test inferring function region type."""
        region_type = gap_service._infer_region_type(30, {})
        assert region_type == "function"

    def test_infer_region_type_method(self, gap_service):
        """Test inferring method region type."""
        region_type = gap_service._infer_region_type(15, {})
        assert region_type == "method"

    def test_infer_region_type_block(self, gap_service):
        """Test inferring block region type."""
        region_type = gap_service._infer_region_type(5, {})
        assert region_type == "block"

    def test_infer_region_type_line(self, gap_service):
        """Test inferring line region type."""
        region_type = gap_service._infer_region_type(1, {})
        assert region_type == "line"


class TestGenerateGapSummary:
    """Tests for gap summary generation."""

    def test_generate_gap_summary_all_covered(self, gap_service):
        """Test gap summary when all changes are covered."""
        summary = gap_service._generate_gap_summary(20, 0, 100.0)
        assert "All 20 changed lines are covered" in summary

    def test_generate_gap_summary_none_covered(self, gap_service):
        """Test gap summary when no changes are covered."""
        summary = gap_service._generate_gap_summary(20, 20, 0.0)
        assert "None of the 20 changed lines are covered" in summary

    def test_generate_gap_summary_partial(self, gap_service):
        """Test gap summary with partial coverage."""
        summary = gap_service._generate_gap_summary(50, 10, 80.0)
        assert "10 of 50" in summary
        assert "80.0%" in summary

    def test_generate_gap_summary_no_changes(self, gap_service):
        """Test gap summary with no changes."""
        summary = gap_service._generate_gap_summary(0, 0, 0.0)
        assert "No changes detected" in summary
