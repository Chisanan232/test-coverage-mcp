"""Unit tests for CoverageRiskAnalysisService."""

import pytest

from test_coverage_mcp.domain import RiskLevel
from test_coverage_mcp.services.risk_analysis import CoverageRiskAnalysisService


@pytest.fixture
def risk_service():
    """Create a CoverageRiskAnalysisService instance."""
    return CoverageRiskAnalysisService()


class TestScorePRRisk:
    """Tests for PR risk scoring."""

    def test_score_pr_risk_low_risk(self, risk_service):
        """Test PR risk scoring with low-risk scenario."""
        result = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=87.0,
            changed_files_count=2,
            uncovered_changed_lines=1,
            total_changed_lines=20,
        )

        assert result["risk_level"] == RiskLevel.LOW.value
        assert result["risk_score"] < 25.0
        assert result["coverage_delta"] == 2.0
        assert result["changed_code_coverage"] > 90.0

    def test_score_pr_risk_high_risk(self, risk_service):
        """Test PR risk scoring with high-risk scenario."""
        result = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=10,
            uncovered_changed_lines=50,
            total_changed_lines=100,
        )

        assert result["risk_level"] == RiskLevel.HIGH.value
        assert result["risk_score"] >= 50.0
        assert result["coverage_delta"] == -5.0
        assert result["changed_code_coverage"] == 50.0

    def test_score_pr_risk_critical(self, risk_service):
        """Test PR risk scoring with critical scenario."""
        result = risk_service.score_pr_risk(
            base_coverage=90.0,
            head_coverage=50.0,
            changed_files_count=20,
            uncovered_changed_lines=100,
            total_changed_lines=100,
        )

        assert result["risk_level"] == RiskLevel.CRITICAL.value
        assert result["risk_score"] >= 75.0
        assert result["coverage_delta"] == -40.0
        assert result["changed_code_coverage"] == 0.0

    def test_score_pr_risk_no_changes(self, risk_service):
        """Test PR risk scoring with no changes."""
        result = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=85.0,
            changed_files_count=0,
            uncovered_changed_lines=0,
            total_changed_lines=0,
        )

        # With no changes, changed_code_coverage is 0.0, which contributes to risk score
        assert result["changed_code_coverage"] == 0.0
        assert result["coverage_delta"] == 0.0

    def test_score_pr_risk_includes_recommendations(self, risk_service):
        """Test that PR risk scoring includes recommendations."""
        result = risk_service.score_pr_risk(
            base_coverage=85.0,
            head_coverage=80.0,
            changed_files_count=5,
            uncovered_changed_lines=10,
            total_changed_lines=50,
        )

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert isinstance(result["recommendations"], list)


class TestIdentifyHighRiskFiles:
    """Tests for high-risk file identification."""

    def test_identify_high_risk_files_basic(self, risk_service):
        """Test identifying high-risk files."""
        file_coverage_data = {
            "src/module1.py": {
                "coverage": 30.0,
                "uncovered_lines": 70,
                "total_lines": 100,
            },
            "src/module2.py": {
                "coverage": 85.0,
                "uncovered_lines": 15,
                "total_lines": 100,
            },
            "src/module3.py": {
                "coverage": 40.0,
                "uncovered_lines": 60,
                "total_lines": 100,
            },
        }

        result = risk_service.identify_high_risk_files(file_coverage_data, risk_threshold=50.0)

        assert len(result) == 2
        assert result[0]["file_path"] == "src/module1.py"
        assert result[0]["risk_score"] == 70.0
        assert result[1]["file_path"] == "src/module3.py"

    def test_identify_high_risk_files_empty(self, risk_service):
        """Test identifying high-risk files with empty data."""
        result = risk_service.identify_high_risk_files({}, risk_threshold=50.0)

        assert len(result) == 0

    def test_identify_high_risk_files_sorted(self, risk_service):
        """Test that high-risk files are sorted by risk score."""
        file_coverage_data = {
            "low_risk.py": {"coverage": 90.0, "uncovered_lines": 10, "total_lines": 100},
            "high_risk.py": {"coverage": 20.0, "uncovered_lines": 80, "total_lines": 100},
            "medium_risk.py": {"coverage": 50.0, "uncovered_lines": 50, "total_lines": 100},
        }

        result = risk_service.identify_high_risk_files(file_coverage_data, risk_threshold=30.0)

        # Should be sorted by risk score (highest first)
        assert result[0]["risk_score"] >= result[1]["risk_score"]

    def test_identify_high_risk_files_includes_recommendations(self, risk_service):
        """Test that high-risk files include recommendations."""
        file_coverage_data = {
            "risky.py": {"coverage": 25.0, "uncovered_lines": 75, "total_lines": 100},
        }

        result = risk_service.identify_high_risk_files(file_coverage_data)

        assert len(result) > 0
        assert "recommendations" in result[0]
        assert len(result[0]["recommendations"]) > 0


class TestDetectConfigVsMissingTests:
    """Tests for config vs missing tests detection."""

    def test_detect_missing_tests_scenario(self, risk_service):
        """Test detection of missing tests scenario."""
        coverage_data = {
            "coverage": 30.0,
            "uncovered_regions": [
                {"start": 10, "end": 20},
                {"start": 50, "end": 60},
            ],
        }

        result = risk_service.detect_config_vs_missing_tests(coverage_data)

        assert result["is_missing_tests"] is True
        assert "Add tests for uncovered code regions" in result["recommendations"]

    def test_detect_config_issue_scenario(self, risk_service):
        """Test detection of config issue scenario."""
        coverage_data = {"coverage": 75.0}
        config_data = {
            "is_valid": False,
            "issues": ["Missing coverage threshold", "Invalid exclude pattern"],
            "suggestions": ["Fix threshold", "Update exclude pattern"],
        }

        result = risk_service.detect_config_vs_missing_tests(coverage_data, config_data)

        assert result["is_config_issue"] is True
        assert "Review and fix coverage configuration" in result["recommendations"]

    def test_detect_both_issues(self, risk_service):
        """Test detection when both config and missing tests issues exist."""
        coverage_data = {
            "coverage": 40.0,
            "uncovered_regions": [{"start": 10, "end": 20}],
        }
        config_data = {
            "is_valid": False,
            "issues": ["Invalid config"],
            "suggestions": ["Fix config"],
        }

        result = risk_service.detect_config_vs_missing_tests(coverage_data, config_data)

        assert "indicators" in result
        assert "recommendations" in result
        # Both issues detected should generate recommendations
        assert len(result["indicators"]) > 0

    def test_detect_no_issues(self, risk_service):
        """Test detection when no issues exist."""
        coverage_data = {"coverage": 95.0}
        config_data = {"is_valid": True, "issues": []}

        result = risk_service.detect_config_vs_missing_tests(coverage_data, config_data)

        assert result["is_config_issue"] is False
        assert result["is_missing_tests"] is False


class TestRiskFactorCalculation:
    """Tests for risk factor calculation."""

    def test_calculate_risk_factors_all_covered(self, risk_service):
        """Test risk factors when all changes are covered."""
        factors = risk_service._calculate_risk_factors(
            coverage_delta=5.0,
            changed_files_count=3,
            uncovered_changed_lines=0,
            total_changed_lines=50,
            changed_code_coverage=100.0,
        )

        assert factors["coverage_regression"] == 0.0
        assert factors["uncovered_changes_risk"] == 0.0
        assert factors["changed_code_coverage_risk"] == 0.0

    def test_calculate_risk_factors_regression(self, risk_service):
        """Test risk factors with coverage regression."""
        factors = risk_service._calculate_risk_factors(
            coverage_delta=-10.0,
            changed_files_count=2,
            uncovered_changed_lines=20,
            total_changed_lines=50,
            changed_code_coverage=60.0,
        )

        assert factors["coverage_regression"] > 0.0
        assert factors["uncovered_changes_risk"] > 0.0


class TestRiskLevelDetermination:
    """Tests for risk level determination."""

    def test_determine_risk_level_critical(self, risk_service):
        """Test critical risk level determination."""
        risk_level = risk_service._determine_risk_level(80.0)
        assert risk_level == RiskLevel.CRITICAL

    def test_determine_risk_level_high(self, risk_service):
        """Test high risk level determination."""
        risk_level = risk_service._determine_risk_level(60.0)
        assert risk_level == RiskLevel.HIGH

    def test_determine_risk_level_medium(self, risk_service):
        """Test medium risk level determination."""
        risk_level = risk_service._determine_risk_level(30.0)
        assert risk_level == RiskLevel.MEDIUM

    def test_determine_risk_level_low(self, risk_service):
        """Test low risk level determination."""
        risk_level = risk_service._determine_risk_level(10.0)
        assert risk_level == RiskLevel.LOW
