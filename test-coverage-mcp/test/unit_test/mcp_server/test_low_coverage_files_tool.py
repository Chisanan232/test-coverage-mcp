"""Unit tests for find_low_coverage_files tool."""

import pytest

from test_coverage_mcp.mcp_server.tools.find_low_coverage_files import (
    find_low_coverage_files,
)


class TestFindLowCoverageFilesTool:
    """Tests for find_low_coverage_files tool."""

    def test_find_low_coverage_files_valid_input(self):
        """Test finding low coverage files with valid input."""
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
            threshold=80.0,
            limit=10,
        )

        assert isinstance(result, dict)
        assert "ref" in result
        assert "threshold" in result
        assert "total_files" in result
        assert "low_coverage_files" in result
        assert "summary" in result
        assert result["ref"] == "main"
        assert result["threshold"] == 80.0

    def test_find_low_coverage_files_invalid_repo_slug(self):
        """Test with invalid repo slug format."""
        result = find_low_coverage_files(
            repo_slug="invalid",
            provider="codecov",
            ref="main",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_find_low_coverage_files_invalid_threshold_high(self):
        """Test with threshold above 100."""
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
            threshold=150.0,
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_THRESHOLD"

    def test_find_low_coverage_files_invalid_threshold_negative(self):
        """Test with negative threshold."""
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
            threshold=-10.0,
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_THRESHOLD"

    def test_find_low_coverage_files_default_threshold(self):
        """Test with default threshold."""
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        assert result["threshold"] == 80.0

    def test_find_low_coverage_files_custom_limit(self):
        """Test with custom limit."""
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
            limit=5,
        )

        assert isinstance(result, dict)
        assert "low_coverage_files" in result
