"""Edge case tests for find_untested_changed_code tool."""

import pytest

from test_coverage_mcp.mcp_server.tools.find_untested_code import find_untested_changed_code


class TestUntestedCodeEdgeCases:
    """Edge case tests for find_untested_changed_code tool."""

    def test_find_untested_code_repo_slug_with_multiple_slashes(self):
        """Test repo slug with multiple slashes (should use first slash)."""
        result = find_untested_changed_code(
            repo_slug="owner/repo/extra",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        # Should parse correctly using first slash
        assert "base_ref" in result
        assert result["base_ref"] == "main"

    def test_find_untested_code_repo_slug_no_slash(self):
        """Test repo slug without slash."""
        result = find_untested_changed_code(
            repo_slug="ownerrepo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "error" in result
        assert result["error_code"] == "INVALID_REPO_SLUG"

    def test_find_untested_code_empty_refs(self):
        """Test with empty base and head refs."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="",
            head_ref="",
        )

        # Should handle empty refs
        assert "base_ref" in result
        assert result["base_ref"] == ""

    def test_find_untested_code_long_repo_slug(self):
        """Test with very long repo slug."""
        long_owner = "a" * 100
        long_repo = "b" * 100
        result = find_untested_changed_code(
            repo_slug=f"{long_owner}/{long_repo}",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        # Should handle long names
        assert "base_ref" in result

    def test_find_untested_code_special_provider_names(self):
        """Test with various provider names."""
        providers = ["codecov", "coveralls", "codacy", "sonarqube", "custom-provider"]

        for provider in providers:
            result = find_untested_changed_code(
                repo_slug="owner/repo",
                provider=provider,
                base_ref="main",
                head_ref="feature",
            )

            assert "base_ref" in result
            assert "error" not in result

    def test_find_untested_code_commit_shas_as_refs(self):
        """Test with commit SHAs as refs."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="abc123def456",
            head_ref="def456ghi789",
        )

        assert result["base_ref"] == "abc123def456"
        assert result["head_ref"] == "def456ghi789"

    def test_find_untested_code_tag_refs(self):
        """Test with tag references."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="v1.0.0",
            head_ref="v1.1.0",
        )

        assert result["base_ref"] == "v1.0.0"
        assert result["head_ref"] == "v1.1.0"

    def test_find_untested_code_branch_with_slashes(self):
        """Test with branch names containing slashes."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="release/v1.0.0",
            head_ref="feature/JIRA-123/new-feature",
        )

        assert result["base_ref"] == "release/v1.0.0"
        assert result["head_ref"] == "feature/JIRA-123/new-feature"

    def test_find_untested_code_unicode_in_refs(self):
        """Test with unicode characters in refs."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature/新功能",
        )

        assert result["head_ref"] == "feature/新功能"

    def test_find_untested_code_whitespace_in_refs(self):
        """Test with whitespace in refs."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main branch",
            head_ref="feature branch",
        )

        # Should handle whitespace in refs
        assert result["base_ref"] == "main branch"

    def test_find_untested_code_case_sensitivity(self):
        """Test case sensitivity in repo slug."""
        result = find_untested_changed_code(
            repo_slug="Owner/Repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        # Should preserve case
        assert "base_ref" in result

    def test_find_untested_code_hyphenated_names(self):
        """Test with hyphenated owner and repo names."""
        result = find_untested_changed_code(
            repo_slug="my-org/my-repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "base_ref" in result

    def test_find_untested_code_numeric_names(self):
        """Test with numeric owner and repo names."""
        result = find_untested_changed_code(
            repo_slug="123/456",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "base_ref" in result

    def test_find_untested_code_underscore_names(self):
        """Test with underscore in names."""
        result = find_untested_changed_code(
            repo_slug="my_org/my_repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert "base_ref" in result

    def test_find_untested_code_result_structure_consistency(self):
        """Test that result structure is consistent across calls."""
        result1 = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        result2 = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        # Should have same keys
        assert set(result1.keys()) == set(result2.keys())

    def test_find_untested_code_numeric_values_types(self):
        """Test that numeric values have correct types."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert isinstance(result["total_changed_lines"], int)
        assert isinstance(result["covered_changed_lines"], int)
        assert isinstance(result["uncovered_changed_lines"], int)
        assert isinstance(result["coverage_percentage"], float)

    def test_find_untested_code_list_values_types(self):
        """Test that list values have correct types."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert isinstance(result["uncovered_regions"], list)
        assert isinstance(result["pending_regions"], list)

    def test_find_untested_code_boolean_values_types(self):
        """Test that boolean values have correct types."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert isinstance(result["has_pending"], bool)

    def test_find_untested_code_string_values_types(self):
        """Test that string values have correct types."""
        result = find_untested_changed_code(
            repo_slug="owner/repo",
            provider="codecov",
            base_ref="main",
            head_ref="feature",
        )

        assert isinstance(result["base_ref"], str)
        assert isinstance(result["head_ref"], str)
        assert isinstance(result["gap_summary"], str)
