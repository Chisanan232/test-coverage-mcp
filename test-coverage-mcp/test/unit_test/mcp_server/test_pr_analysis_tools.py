"""Unit tests for PR analysis tools."""

import pytest

from test_coverage_mcp.mcp_server.tools.analyze_pr_risk import analyze_pr_coverage_risk
from test_coverage_mcp.mcp_server.tools.find_untested_code import find_untested_changed_code


class TestFindUntestedChangedCode:
    """Tests for find_untested_changed_code tool."""

    def test_find_untested_code_valid_repo_slug(self):
        """Test finding untested code with valid repo slug."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "base_ref" in result
        assert "head_ref" in result
        assert result["base_ref"] == "main"
        assert result["head_ref"] == "feature"
        assert "total_changed_lines" in result
        assert "coverage_percentage" in result

    def test_find_untested_code_invalid_repo_slug(self):
        """Test finding untested code with invalid repo slug."""
        result = find_untested_changed_code(
            repo_slug="invalid",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_find_untested_code_no_changes(self):
        """Test finding untested code with no changes."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert result["total_changed_lines"] == 0
        assert result["uncovered_changed_lines"] == 0
        assert result["coverage_percentage"] == 0.0

    def test_find_untested_code_includes_pending_flag(self):
        """Test that result includes pending analysis flag."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "has_pending" in result
        assert isinstance(result["has_pending"], bool)

    def test_find_untested_code_includes_gap_summary(self):
        """Test that result includes gap summary."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "gap_summary" in result
        assert isinstance(result["gap_summary"], str)

    def test_find_untested_code_uncovered_regions_structure(self):
        """Test that uncovered regions have correct structure."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "uncovered_regions" in result
        assert isinstance(result["uncovered_regions"], list)

        # If there are uncovered regions, check structure
        for region in result["uncovered_regions"]:
            assert "file_path" in region
            assert "start_line" in region
            assert "end_line" in region
            assert "region_type" in region
            assert "risk_level" in region
            assert "lines_count" in region


class TestAnalyzePRCoverageRisk:
    """Tests for analyze_pr_coverage_risk tool."""

    def test_analyze_pr_risk_valid_repo_slug(self):
        """Test analyzing PR risk with valid repo slug."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "base_ref" in result
        assert "head_ref" in result
        assert result["base_ref"] == "main"
        assert result["head_ref"] == "feature"
        assert "risk_level" in result
        assert "risk_score" in result

    def test_analyze_pr_risk_invalid_repo_slug(self):
        """Test analyzing PR risk with invalid repo slug."""
        result = analyze_pr_coverage_risk(
            repo_slug="invalid",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_analyze_pr_risk_includes_risk_level(self):
        """Test that result includes risk level."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "risk_level" in result
        assert result["risk_level"] in ["low", "medium", "high", "critical"]

    def test_analyze_pr_risk_includes_risk_score(self):
        """Test that result includes risk score."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "risk_score" in result
        assert isinstance(result["risk_score"], (int, float))
        assert 0.0 <= result["risk_score"] <= 100.0

    def test_analyze_pr_risk_includes_recommendations(self):
        """Test that result includes recommendations."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_analyze_pr_risk_includes_coverage_delta(self):
        """Test that result includes coverage delta."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "coverage_delta" in result
        assert isinstance(result["coverage_delta"], (int, float))

    def test_analyze_pr_risk_includes_high_risk_files(self):
        """Test that result includes high risk files list."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "high_risk_files" in result
        assert isinstance(result["high_risk_files"], list)

    def test_analyze_pr_risk_no_changes(self):
        """Test analyzing PR risk with no changes."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert result["changed_files_count"] == 0
        assert result["total_changed_lines"] == 0
        assert result["uncovered_changed_lines"] == 0


class TestPRToolsWithPendingStates:
    """Tests for PR tools with pending analysis states."""

    def test_find_untested_code_pending_regions(self):
        """Test that find_untested_code handles pending regions."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "pending_regions" in result
        assert isinstance(result["pending_regions"], list)

    def test_find_untested_code_has_pending_flag(self):
        """Test that find_untested_code includes has_pending flag."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "has_pending" in result
        assert isinstance(result["has_pending"], bool)


class TestPRToolsEdgeCases:
    """Tests for PR tools edge cases."""

    def test_find_untested_code_empty_provider(self):
        """Test finding untested code with empty provider."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="",
            base_ref="main",
            head_ref="feature",
        )

        # Should still work with empty provider
        assert "base_ref" in result

    def test_analyze_pr_risk_same_refs(self):
        """Test analyzing PR risk with same base and head refs."""
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="main",
        )

        # Should handle same refs gracefully
        assert "risk_level" in result
        assert result["coverage_delta"] == 0.0

    def test_find_untested_code_special_chars_in_refs(self):
        """Test finding untested code with special characters in refs."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="release/v1.0.0",
            head_ref="feature/JIRA-123-new-feature",
        )

        assert result["base_ref"] == "release/v1.0.0"
        assert result["head_ref"] == "feature/JIRA-123-new-feature"
