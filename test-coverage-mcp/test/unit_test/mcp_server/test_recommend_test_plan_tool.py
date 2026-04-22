"""Unit tests for recommend_test_plan tool."""

from typing import Any

import pytest

from test_coverage_mcp.mcp_server.tools.recommend_test_plan import (
    recommend_test_plan,
)


class TestRecommendTestPlanTool:
    """Tests for recommend_test_plan tool."""

    def test_recommend_test_plan_valid_input_repo(self) -> None:
        """Test recommending test plan for repository."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
            target="repo",
        )

        assert isinstance(result, dict)
        assert "target" in result
        assert "total_gaps" in result
        assert "recommendations" in result
        assert "summary" in result
        assert result["target"] == "repo"
        assert isinstance(result["recommendations"], list)

    def test_recommend_test_plan_valid_input_pr(self) -> None:
        """Test recommending test plan for pull request."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
            target="pr",
        )

        assert isinstance(result, dict)
        assert result["target"] == "pr"

    def test_recommend_test_plan_valid_input_file(self) -> None:
        """Test recommending test plan for specific file."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
            target="src/main.py",
        )

        assert isinstance(result, dict)
        assert result["target"] == "src/main.py"

    def test_recommend_test_plan_invalid_repo_slug(self) -> None:
        """Test with invalid repo slug format."""
        result = recommend_test_plan(
            repo_slug="invalid",
            provider="codecov",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_recommend_test_plan_invalid_target(self) -> None:
        """Test with invalid target."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
            target="invalid_target",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_TARGET"

    def test_recommend_test_plan_default_target(self) -> None:
        """Test with default target."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
        )

        assert result["target"] == "repo"

    def test_recommend_test_plan_returns_recommendations(self) -> None:
        """Test that recommendations are returned."""
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="codecov",
        )

        assert isinstance(result["recommendations"], list)
        # Each recommendation should have required fields
        for rec in result["recommendations"]:
            assert "file_path" in rec
            assert "start_line" in rec
            assert "end_line" in rec
            assert "region_type" in rec
            assert "test_types" in rec
            assert "scenarios" in rec
            assert "priority" in rec
            assert "rationale" in rec
