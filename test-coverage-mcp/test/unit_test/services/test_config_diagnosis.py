"""Unit tests for CoverageConfigDiagnosisService."""

import pytest

from test_coverage_mcp.services.config_diagnosis import CoverageConfigDiagnosisService


class TestConfigDiagnosisService:
    """Tests for CoverageConfigDiagnosisService."""

    def test_retrieve_config(self):
        """Test retrieving configuration."""
        service = CoverageConfigDiagnosisService()
        config = service.retrieve_config("owner", "repo")

        assert isinstance(config, dict)
        assert "include_paths" in config
        assert "exclude_paths" in config
        assert "thresholds" in config
        assert "components" in config
        assert "flags" in config

    def test_parse_config_valid(self):
        """Test parsing valid configuration."""
        service = CoverageConfigDiagnosisService()
        config = {
            "include_paths": ["src/"],
            "exclude_paths": ["tests/"],
            "thresholds": {"minimum": 80},
            "components": {},
            "flags": {},
        }

        result = service.parse_config(config)

        assert result["valid"] is True
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_detect_over_included_paths(self):
        """Test detecting over-included paths."""
        service = CoverageConfigDiagnosisService()
        config = {
            "include_paths": ["src/", "unused/"],
            "exclude_paths": [],
        }
        file_coverage = {
            "src/main.py": {"coverage": 80},
            "src/utils.py": {"coverage": 90},
        }

        result = service.detect_over_included_paths(config, file_coverage)

        assert isinstance(result, list)
        # "unused/" should be detected as over-included
        over_included_paths = [r["path"] for r in result]
        assert "unused/" in over_included_paths

    def test_suggest_missing_exclusions(self):
        """Test suggesting missing exclusions."""
        service = CoverageConfigDiagnosisService()
        config = {
            "include_paths": ["src/"],
            "exclude_paths": [],
        }
        file_coverage = {
            "src/main.py": {"coverage": 80},
            "src/test/test_main.py": {"coverage": 0},
            "src/tests/test_utils.py": {"coverage": 0},
        }

        result = service.suggest_missing_exclusions(config, file_coverage)

        assert isinstance(result, list)
        # Should suggest excluding test directories
        patterns = [r["pattern"] for r in result]
        assert len(patterns) > 0

    def test_review_thresholds_high(self):
        """Test reviewing thresholds that are too high."""
        service = CoverageConfigDiagnosisService()
        config = {
            "thresholds": {"minimum": 99},
        }

        result = service.review_thresholds(config, 85.0)

        assert isinstance(result["issues"], list)
        assert len(result["issues"]) > 0
        assert isinstance(result["recommendations"], list)

    def test_review_thresholds_low(self):
        """Test reviewing thresholds that are too low."""
        service = CoverageConfigDiagnosisService()
        config = {
            "thresholds": {"minimum": 30},
        }

        result = service.review_thresholds(config, 85.0)

        assert isinstance(result["issues"], list)
        assert len(result["issues"]) > 0

    def test_review_component_scoping(self):
        """Test reviewing component scoping."""
        service = CoverageConfigDiagnosisService()
        config = {
            "components": {
                "api": {"paths": ["src/api/"]},
                "core": {"paths": ["src/core/"]},
            },
            "flags": {},
        }

        result = service.review_component_scoping(config)

        assert isinstance(result, list)

    def test_review_component_scoping_missing_paths(self):
        """Test reviewing component scoping with missing paths."""
        service = CoverageConfigDiagnosisService()
        config = {
            "components": {
                "api": {"paths": []},
            },
            "flags": {},
        }

        result = service.review_component_scoping(config)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any("No paths" in issue["issue"] for issue in result)

    def test_diagnose_config_valid(self):
        """Test diagnosing valid configuration."""
        service = CoverageConfigDiagnosisService()
        file_coverage = {
            "src/main.py": {"coverage": 80},
        }

        result = service.diagnose_config("owner", "repo", file_coverage, 85.0)

        assert result.repo_owner == "owner"
        assert result.repo_name == "repo"
        assert result.config_valid is True
        assert isinstance(result.summary, str)

    def test_diagnose_config_with_issues(self):
        """Test diagnosing configuration with issues."""
        service = CoverageConfigDiagnosisService()
        file_coverage = {}

        result = service.diagnose_config("owner", "repo", file_coverage, 50.0)

        assert result.repo_owner == "owner"
        assert result.repo_name == "repo"
        assert isinstance(result.summary, str)

    def test_matches_pattern_wildcard(self):
        """Test pattern matching with wildcards."""
        assert CoverageConfigDiagnosisService._matches_pattern(
            "src/test/main.py", "**/test/**"
        )
        assert CoverageConfigDiagnosisService._matches_pattern(
            "src/tests/test_main.py", "**/tests/**"
        )

    def test_matches_pattern_directory(self):
        """Test pattern matching with directory patterns."""
        assert CoverageConfigDiagnosisService._matches_pattern(
            "src/main.py", "src/**"
        )
        assert not CoverageConfigDiagnosisService._matches_pattern(
            "tests/main.py", "src/**"
        )

    def test_matches_pattern_exact(self):
        """Test exact pattern matching."""
        assert CoverageConfigDiagnosisService._matches_pattern(
            "src/main.py", "src/main.py"
        )
        assert not CoverageConfigDiagnosisService._matches_pattern(
            "src/main.py", "src/other.py"
        )
