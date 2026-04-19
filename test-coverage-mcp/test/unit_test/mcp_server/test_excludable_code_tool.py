"""Unit tests for identify_excludable_code_candidates tool."""

import pytest

from test_coverage_mcp.mcp_server.tools.identify_excludable_code_candidates import (
    identify_excludable_code_candidates,
)


class TestIdentifyExcludableCodeCandidatesTool:
    """Tests for identify_excludable_code_candidates tool."""

    def test_identify_excludable_code_candidates_valid_input(self):
        """Test identifying excludable code candidates with valid input."""
        result = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        assert isinstance(result, dict)
        assert "ref" in result
        assert "total_files" in result
        assert "candidate_count" in result
        assert "candidates" in result
        assert "summary" in result
        assert result["ref"] == "main"
        assert isinstance(result["candidates"], list)

    def test_identify_excludable_code_candidates_invalid_repo_slug(self):
        """Test with invalid repo slug format."""
        result = identify_excludable_code_candidates(
            repo_slug="invalid",
            provider="codecov",
            ref="main",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_identify_excludable_code_candidates_returns_candidates(self):
        """Test that candidates are returned."""
        result = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        assert isinstance(result["candidates"], list)
        # Each candidate should have required fields
        for candidate in result["candidates"]:
            assert "file_path" in candidate
            assert "excludability_score" in candidate
            assert "should_exclude" in candidate
            assert "breakdown" in candidate

    def test_identify_excludable_code_candidates_summary_present(self):
        """Test that summary is always present."""
        result = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        assert "summary" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0

    def test_identify_excludable_code_candidates_counts_match(self):
        """Test that candidate count matches list length."""
        result = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        assert result["candidate_count"] == len(result["candidates"])

    def test_identify_excludable_code_candidates_different_refs(self):
        """Test with different git references."""
        result_main = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="main",
        )

        result_develop = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="codecov",
            ref="develop",
        )

        assert result_main["ref"] == "main"
        assert result_develop["ref"] == "develop"
