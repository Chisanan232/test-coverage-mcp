"""Unit tests for diagnose_coverage_configuration tool."""

import pytest

from test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration import (
    diagnose_coverage_configuration,
)


class TestDiagnoseCoverageConfigurationTool:
    """Tests for diagnose_coverage_configuration tool."""

    def test_diagnose_coverage_configuration_valid_input(self):
        """Test diagnosing configuration with valid input."""
        result = diagnose_coverage_configuration(
            repo_slug="owner/repo",
            provider="codecov",
        )

        assert isinstance(result, dict)
        assert "repo_owner" in result
        assert "repo_name" in result
        assert "config_valid" in result
        assert "parse_errors" in result
        assert "over_included_paths" in result
        assert "missing_exclusions" in result
        assert "threshold_issues" in result
        assert "scoping_issues" in result
        assert "summary" in result
        assert result["repo_owner"] == "owner"
        assert result["repo_name"] == "repo"

    def test_diagnose_coverage_configuration_invalid_repo_slug(self):
        """Test with invalid repo slug format."""
        result = diagnose_coverage_configuration(
            repo_slug="invalid",
            provider="codecov",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_diagnose_coverage_configuration_returns_lists(self):
        """Test that diagnosis returns proper list structures."""
        result = diagnose_coverage_configuration(
            repo_slug="owner/repo",
            provider="codecov",
        )

        assert isinstance(result["parse_errors"], list)
        assert isinstance(result["over_included_paths"], list)
        assert isinstance(result["missing_exclusions"], list)
        assert isinstance(result["threshold_issues"], list)
        assert isinstance(result["scoping_issues"], list)

    def test_diagnose_coverage_configuration_summary_present(self):
        """Test that summary is always present."""
        result = diagnose_coverage_configuration(
            repo_slug="owner/repo",
            provider="codecov",
        )

        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
