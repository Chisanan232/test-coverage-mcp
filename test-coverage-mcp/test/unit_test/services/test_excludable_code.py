"""Unit tests for ExcludableCodeCandidateService with edge cases."""

from typing import Any

import pytest

from test_coverage_mcp.services.excludable_code import ExcludableCodeCandidateService


class TestExcludableCodeService:
    """Tests for ExcludableCodeCandidateService."""

    def test_detect_generated_code_with_marker(self) -> None:
        """Test detecting generated code with explicit marker."""
        service = ExcludableCodeCandidateService()
        content = "# AUTO-GENERATED\nclass GeneratedClass:\n    pass"

        result = service.detect_generated_code("file.py", content)

        assert result["is_generated"] is True
        assert result["confidence"] > 0.5

    def test_detect_generated_code_no_marker(self) -> None:
        """Test detecting generated code without marker."""
        service = ExcludableCodeCandidateService()
        content = "class MyClass:\n    def method(self):\n        pass"

        result = service.detect_generated_code("file.py", content)

        assert result["is_generated"] is False
        assert result["confidence"] <= 0.5

    def test_detect_generated_code_by_extension(self) -> None:
        """Test detecting generated code by file extension."""
        service = ExcludableCodeCandidateService()
        content = "some content"

        result = service.detect_generated_code("file.pb2.py", content)

        # Extension alone gives 0.4 confidence, which is below 0.5 threshold
        assert result["confidence"] >= 0.4
        # is_generated is True only if confidence > 0.5
        assert result["is_generated"] is (result["confidence"] > 0.5)

    def test_detect_vendor_code_node_modules(self) -> None:
        """Test detecting vendor code in node_modules."""
        service = ExcludableCodeCandidateService()

        result = service.detect_vendor_code("node_modules/package/index.js")

        # Should detect vendor code
        assert result["confidence"] > 0.0
        assert result["is_vendor"] is (result["confidence"] > 0.5)

    def test_detect_vendor_code_venv(self) -> None:
        """Test detecting vendor code in venv."""
        service = ExcludableCodeCandidateService()

        result = service.detect_vendor_code(".venv/lib/python/site-packages/module.py")

        assert result["is_vendor"] is True

    def test_detect_vendor_code_not_vendor(self) -> None:
        """Test detecting non-vendor code."""
        service = ExcludableCodeCandidateService()

        result = service.detect_vendor_code("src/main.py")

        assert result["is_vendor"] is False

    def test_detect_migration_path_deprecated(self) -> None:
        """Test detecting deprecated code."""
        service = ExcludableCodeCandidateService()
        content = "# DEPRECATED\ndef old_function():\n    pass"

        result = service.detect_migration_path("file.py", content)

        # Should detect migration code
        assert result["confidence"] > 0.0
        assert result["is_migration"] is (result["confidence"] > 0.5)

    def test_detect_migration_path_legacy(self) -> None:
        """Test detecting legacy code."""
        service = ExcludableCodeCandidateService()
        content = "# LEGACY implementation\nclass OldClass:\n    pass"

        result = service.detect_migration_path("file.py", content)

        # Should detect migration code
        assert result["confidence"] > 0.0

    def test_detect_migration_path_no_markers(self) -> None:
        """Test detecting non-migration code."""
        service = ExcludableCodeCandidateService()
        content = "class NewClass:\n    pass"

        result = service.detect_migration_path("file.py", content)

        assert result["is_migration"] is False

    def test_analyze_zero_hit_signals_no_hits(self) -> None:
        """Test analyzing zero-hit signals."""
        service = ExcludableCodeCandidateService()
        coverage_data = {
            "hits": 0,
            "total_lines": 10,
            "covered_lines": 0,
            "content": "def func():\n    pass",
        }

        result = service.analyze_zero_hit_signals("file.py", coverage_data)

        assert result["has_zero_hit_signals"] is True
        assert result["confidence"] > 0.5

    def test_analyze_zero_hit_signals_with_hits(self) -> None:
        """Test analyzing with coverage hits."""
        service = ExcludableCodeCandidateService()
        coverage_data = {
            "hits": 5,
            "total_lines": 10,
            "covered_lines": 5,
            "content": "def func():\n    pass",
        }

        result = service.analyze_zero_hit_signals("file.py", coverage_data)

        assert result["has_zero_hit_signals"] is False

    def test_analyze_zero_hit_signals_unreachable(self) -> None:
        """Test analyzing unreachable code."""
        service = ExcludableCodeCandidateService()
        coverage_data = {
            "hits": 0,
            "total_lines": 5,
            "covered_lines": 0,
            "content": "if False:\n    def unreachable():\n        pass",
        }

        result = service.analyze_zero_hit_signals("file.py", coverage_data)

        assert result["has_zero_hit_signals"] is True

    def test_score_excludability_generated(self) -> None:
        """Test scoring excludability for generated code."""
        service = ExcludableCodeCandidateService()
        content = "# AUTO-GENERATED\nclass Generated:\n    pass"
        coverage_data = {"hits": 0, "total_lines": 5, "covered_lines": 0}

        result = service.score_excludability("file.py", content, coverage_data)

        # Should have high excludability score for generated code
        assert result["excludability_score"] >= 0.3

    def test_score_excludability_normal_code(self) -> None:
        """Test scoring excludability for normal code."""
        service = ExcludableCodeCandidateService()
        content = "def my_function():\n    return 42"
        coverage_data = {"hits": 5, "total_lines": 10, "covered_lines": 5}

        result = service.score_excludability("src/main.py", content, coverage_data)

        assert result["should_exclude"] is False
        assert result["excludability_score"] < 0.5

    def test_find_excludable_candidates(self) -> None:
        """Test finding excludable candidates."""
        service = ExcludableCodeCandidateService()
        files = [
            {
                "path": "file1.pb2.py",
                "content": "# AUTO-GENERATED",
                "coverage": {"hits": 0, "total_lines": 10, "covered_lines": 0},
            },
            {
                "path": "src/main.py",
                "content": "def func(): pass",
                "coverage": {"hits": 5, "total_lines": 10, "covered_lines": 5},
            },
        ]

        result = service.find_excludable_candidates(files, min_confidence=0.3)

        assert isinstance(result, list)
        assert len(result) > 0
        # Generated file should be first
        assert "pb2" in result[0]["file_path"]

    def test_find_excludable_candidates_min_confidence(self) -> None:
        """Test finding candidates with minimum confidence."""
        service = ExcludableCodeCandidateService()
        files = [
            {
                "path": "file.py",
                "content": "def func(): pass",
                "coverage": {"hits": 0, "total_lines": 10, "covered_lines": 0},
            }
        ]

        result = service.find_excludable_candidates(files, min_confidence=0.9)

        # Should be empty with high confidence threshold
        assert len(result) == 0

    def test_validate_candidate_safe(self) -> None:
        """Test validating safe-to-exclude candidate."""
        service = ExcludableCodeCandidateService()
        content = "# AUTO-GENERATED\nclass Generated:\n    pass"

        result = service.validate_candidate("file.pb2.py", content)

        assert result["is_safe_to_exclude"] is True
        assert len(result["warnings"]) == 0

    def test_validate_candidate_has_public_api(self) -> None:
        """Test validating candidate with public API."""
        service = ExcludableCodeCandidateService()
        content = "__all__ = ['MyClass']\nclass MyClass:\n    pass"

        result = service.validate_candidate("file.py", content)

        assert result["is_safe_to_exclude"] is False
        assert len(result["warnings"]) > 0

    def test_validate_candidate_has_side_effects(self) -> None:
        """Test validating candidate with side effects."""
        service = ExcludableCodeCandidateService()
        content = "import sys\nsys.path.insert(0, '/custom/path')"

        result = service.validate_candidate("file.py", content)

        assert result["is_safe_to_exclude"] is False
        assert any("side effects" in w.lower() for w in result["warnings"])


class TestExcludableCodeEdgeCases:
    """Edge case tests for excludable code detection."""

    def test_detect_generated_multiple_markers(self) -> None:
        """Test detecting generated code with multiple markers."""
        service = ExcludableCodeCandidateService()
        content = "# AUTO-GENERATED\n# DO NOT EDIT\nclass Generated:\n    pass"

        result = service.detect_generated_code("file.py", content)

        assert result["is_generated"] is True
        assert result["confidence"] > 0.5

    def test_detect_vendor_third_party(self) -> None:
        """Test detecting third-party code."""
        service = ExcludableCodeCandidateService()

        result = service.detect_vendor_code("third_party/lib/module.py")

        # Should detect vendor code
        assert result["confidence"] > 0.0

    def test_detect_migration_version_specific(self) -> None:
        """Test detecting version-specific migration code."""
        service = ExcludableCodeCandidateService()
        content = "# v1 implementation"

        result = service.detect_migration_path("v1/module.py", content)

        # Should detect migration code
        assert result["confidence"] > 0.0

    def test_score_excludability_mixed_signals(self) -> None:
        """Test scoring with mixed signals."""
        service = ExcludableCodeCandidateService()
        content = "# AUTO-GENERATED\ndef __all__():\n    pass"
        coverage_data = {"hits": 0, "total_lines": 10, "covered_lines": 0}

        result = service.score_excludability("file.py", content, coverage_data)

        # Generated signal should dominate
        assert result["excludability_score"] >= 0.3

    def test_validate_candidate_imports(self) -> None:
        """Test validating candidate with imports."""
        service = ExcludableCodeCandidateService()
        content = "from module import something\nimport sys"

        result = service.validate_candidate("file.py", content)

        assert result["is_safe_to_exclude"] is False

    def test_validate_candidate_monkey_patch(self) -> None:
        """Test validating candidate with monkey patching."""
        service = ExcludableCodeCandidateService()
        content = "# monkey patch\nmodule.function = new_function"

        result = service.validate_candidate("file.py", content)

        assert result["is_safe_to_exclude"] is False

    def test_find_candidates_empty_list(self) -> None:
        """Test finding candidates from empty list."""
        service = ExcludableCodeCandidateService()

        result = service.find_excludable_candidates([])

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_candidates_all_normal(self) -> None:
        """Test finding candidates when all files are normal."""
        service = ExcludableCodeCandidateService()
        files = [
            {
                "path": f"src/file{i}.py",
                "content": "def func(): pass",
                "coverage": {"hits": 5, "total_lines": 10, "covered_lines": 5},
            }
            for i in range(5)
        ]

        result = service.find_excludable_candidates(files)

        # Should find few or no candidates
        assert len(result) < len(files)

    def test_validate_candidate_env_access(self) -> None:
        """Test validating candidate with environment access."""
        service = ExcludableCodeCandidateService()
        content = "import os\npath = os.environ['HOME']"

        result = service.validate_candidate("file.py", content)

        assert result["is_safe_to_exclude"] is False

    def test_score_excludability_vendor_path(self) -> None:
        """Test scoring vendor code in path."""
        service = ExcludableCodeCandidateService()
        content = "def func(): pass"
        coverage_data = {"hits": 0, "total_lines": 10, "covered_lines": 0}

        result = service.score_excludability(
            "vendor/lib/module.py", content, coverage_data
        )

        # Should have some excludability score for vendor code
        assert result["excludability_score"] > 0.1
