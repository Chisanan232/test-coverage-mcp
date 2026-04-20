"""Unit tests for RecommendationService."""

from typing import Any

import pytest

from test_coverage_mcp.services.test_recommendation import RecommendationService


class TestTestRecommendationService:
    """Tests for TestRecommendationService."""

    def test_identify_test_gaps(self) -> None:
        """Test identifying test gaps."""
        service = RecommendationService()
        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "risk_level": "high",
                "lines_count": 10,
            }
        ]

        result = service.identify_test_gaps(uncovered_regions)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["file_path"] == "src/main.py"

    def test_suggest_test_types_function(self) -> None:
        """Test suggesting test types for function."""
        service = RecommendationService()

        result = service.suggest_test_types("function")

        assert isinstance(result, list)
        assert "unit" in result
        assert "integration" in result

    def test_suggest_test_types_class(self) -> None:
        """Test suggesting test types for class."""
        service = RecommendationService()

        result = service.suggest_test_types("class")

        assert isinstance(result, list)
        assert "unit" in result
        assert "integration" in result

    def test_suggest_test_types_method(self) -> None:
        """Test suggesting test types for method."""
        service = RecommendationService()

        result = service.suggest_test_types("method")

        assert isinstance(result, list)
        assert "unit" in result

    def test_rank_by_priority(self) -> None:
        """Test ranking gaps by priority."""
        service = RecommendationService()
        gaps = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "risk_level": "low",
                "lines_count": 5,
            },
            {
                "file_path": "src/core.py",
                "start_line": 30,
                "end_line": 80,
                "region_type": "class",
                "risk_level": "critical",
                "lines_count": 50,
            },
        ]

        result = service.rank_by_priority(gaps)

        assert isinstance(result, list)
        assert len(result) == 2
        # Critical should be ranked higher
        assert result[0]["risk_level"] == "critical"
        assert "priority_score" in result[0]

    def test_generate_scenarios_function(self) -> None:
        """Test generating scenarios for function."""
        service = RecommendationService()

        result = service.generate_scenarios("function")

        assert isinstance(result, list)
        assert len(result) > 0
        assert all("name" in s and "description" in s for s in result)

    def test_generate_scenarios_class(self) -> None:
        """Test generating scenarios for class."""
        service = RecommendationService()

        result = service.generate_scenarios("class")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_scenarios_method(self) -> None:
        """Test generating scenarios for method."""
        service = RecommendationService()

        result = service.generate_scenarios("method")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_explain_rationale_critical(self) -> None:
        """Test explaining rationale for critical gap."""
        service = RecommendationService()
        gap = {
            "file_path": "src/main.py",
            "start_line": 10,
            "end_line": 20,
            "region_type": "function",
            "risk_level": "critical",
            "lines_count": 50,
        }

        result = service.explain_rationale(gap)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "critical" in result.lower()

    def test_explain_rationale_high(self) -> None:
        """Test explaining rationale for high risk gap."""
        service = RecommendationService()
        gap = {
            "file_path": "src/main.py",
            "start_line": 10,
            "end_line": 20,
            "region_type": "class",
            "risk_level": "high",
            "lines_count": 30,
        }

        result = service.explain_rationale(gap)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_recommend_tests(self) -> None:
        """Test generating test recommendations."""
        service = RecommendationService()
        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "risk_level": "high",
                "lines_count": 10,
            },
            {
                "file_path": "src/utils.py",
                "start_line": 30,
                "end_line": 40,
                "region_type": "function",
                "risk_level": "low",
                "lines_count": 5,
            },
        ]

        result = service.recommend_tests(uncovered_regions)

        assert isinstance(result, list)
        assert len(result) > 0
        # All recommendations should have required fields
        for rec in result:
            assert rec.file_path
            assert rec.start_line
            assert rec.end_line
            assert rec.region_type
            assert rec.test_types
            assert rec.scenarios
            assert rec.priority
            assert rec.rationale

    def test_recommend_tests_max_recommendations(self) -> None:
        """Test limiting recommendations."""
        service = RecommendationService()
        uncovered_regions = [
            {
                "file_path": f"src/file{i}.py",
                "start_line": i * 10 + 1,
                "end_line": i * 10 + 10,
                "region_type": "function",
                "risk_level": "low",
                "lines_count": 5,
            }
            for i in range(20)
        ]

        result = service.recommend_tests(uncovered_regions, max_recommendations=5)

        assert len(result) <= 5

    def test_score_to_priority_critical(self) -> None:
        """Test converting score to critical priority."""
        result = RecommendationService._score_to_priority(85.0)
        assert result == "critical"

    def test_score_to_priority_high(self) -> None:
        """Test converting score to high priority."""
        result = RecommendationService._score_to_priority(65.0)
        assert result == "high"

    def test_score_to_priority_medium(self) -> None:
        """Test converting score to medium priority."""
        result = RecommendationService._score_to_priority(45.0)
        assert result == "medium"

    def test_score_to_priority_low(self) -> None:
        """Test converting score to low priority."""
        result = RecommendationService._score_to_priority(20.0)
        assert result == "low"


class TestTestRecommendationEdgeCases:
    """Tests for edge cases in test recommendations."""

    def test_identify_test_gaps_empty_list(self) -> None:
        """Test identifying gaps with empty list."""
        service = RecommendationService()
        result = service.identify_test_gaps([])
        assert result == []

    def test_identify_test_gaps_multiple_regions(self) -> None:
        """Test identifying gaps with multiple regions."""
        service = RecommendationService()
        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "risk_level": "high",
                "lines_count": 10,
            },
            {
                "file_path": "src/utils.py",
                "start_line": 30,
                "end_line": 40,
                "region_type": "class",
                "risk_level": "critical",
                "lines_count": 10,
            },
        ]

        result = service.identify_test_gaps(uncovered_regions)
        assert len(result) == 2

    def test_suggest_test_types_unknown_type(self) -> None:
        """Test suggesting test types for unknown type."""
        service = RecommendationService()
        result = service.suggest_test_types("unknown")
        assert isinstance(result, list)
        assert "unit" in result

    def test_rank_by_priority_empty_list(self) -> None:
        """Test ranking empty list."""
        service = RecommendationService()
        result = service.rank_by_priority([])
        assert result == []

    def test_rank_by_priority_single_gap(self) -> None:
        """Test ranking single gap."""
        service = RecommendationService()
        gaps = [
            {
                "file_path": "src/main.py",
                "risk_level": "high",
                "region_type": "function",
                "lines_count": 20,
            }
        ]

        result = service.rank_by_priority(gaps)
        assert len(result) == 1
        assert "priority_score" in result[0]

    def test_rank_by_priority_maintains_order(self) -> None:
        """Test that ranking maintains correct order."""
        service = RecommendationService()
        gaps = [
            {
                "file_path": "src/low.py",
                "risk_level": "low",
                "region_type": "line",
                "lines_count": 1,
            },
            {
                "file_path": "src/critical.py",
                "risk_level": "critical",
                "region_type": "class",
                "lines_count": 100,
            },
            {
                "file_path": "src/medium.py",
                "risk_level": "medium",
                "region_type": "function",
                "lines_count": 30,
            },
        ]

        result = service.rank_by_priority(gaps)
        # Critical should be first
        assert result[0]["risk_level"] == "critical"
        # Low should be last
        assert result[-1]["risk_level"] == "low"

    def test_rank_by_priority_all_same_risk(self) -> None:
        """Test ranking when all gaps have same risk level."""
        service = RecommendationService()
        gaps = [
            {
                "file_path": "src/file1.py",
                "risk_level": "high",
                "region_type": "function",
                "lines_count": 10,
            },
            {
                "file_path": "src/file2.py",
                "risk_level": "high",
                "region_type": "function",
                "lines_count": 20,
            },
            {
                "file_path": "src/file3.py",
                "risk_level": "high",
                "region_type": "class",
                "lines_count": 30,
            },
        ]

        result = service.rank_by_priority(gaps)
        # Class should be ranked higher than function
        assert result[0]["region_type"] == "class"

    def test_suggest_test_types_all_types(self) -> None:
        """Test suggesting test types for all region types."""
        service = RecommendationService()
        region_types = ["function", "class", "method", "block", "branch", "line"]

        for region_type in region_types:
            result = service.suggest_test_types(region_type)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_identify_test_gaps_preserves_data(self) -> None:
        """Test that identifying gaps preserves all data."""
        service = RecommendationService()
        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "lines_count": 11,
                "risk_level": "high",
            }
        ]

        result = service.identify_test_gaps(uncovered_regions)
        gap = result[0]

        assert gap["file_path"] == "src/main.py"
        assert gap["start_line"] == 10
        assert gap["end_line"] == 20
        assert gap["region_type"] == "function"
        assert gap["lines_count"] == 11
        assert gap["risk_level"] == "high"
