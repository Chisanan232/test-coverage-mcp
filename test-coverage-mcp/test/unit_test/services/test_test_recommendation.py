"""Unit tests for TestRecommendationService."""

import pytest

from test_coverage_mcp.services.test_recommendation import TestRecommendationService


class TestTestRecommendationService:
    """Tests for TestRecommendationService."""

    def test_identify_test_gaps(self):
        """Test identifying test gaps."""
        service = TestRecommendationService()
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

    def test_suggest_test_types_function(self):
        """Test suggesting test types for function."""
        service = TestRecommendationService()

        result = service.suggest_test_types("function")

        assert isinstance(result, list)
        assert "unit" in result
        assert "integration" in result

    def test_suggest_test_types_class(self):
        """Test suggesting test types for class."""
        service = TestRecommendationService()

        result = service.suggest_test_types("class")

        assert isinstance(result, list)
        assert "unit" in result
        assert "integration" in result

    def test_suggest_test_types_method(self):
        """Test suggesting test types for method."""
        service = TestRecommendationService()

        result = service.suggest_test_types("method")

        assert isinstance(result, list)
        assert "unit" in result

    def test_rank_by_priority(self):
        """Test ranking gaps by priority."""
        service = TestRecommendationService()
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

    def test_generate_scenarios_function(self):
        """Test generating scenarios for function."""
        service = TestRecommendationService()

        result = service.generate_scenarios("function")

        assert isinstance(result, list)
        assert len(result) > 0
        assert all("name" in s and "description" in s for s in result)

    def test_generate_scenarios_class(self):
        """Test generating scenarios for class."""
        service = TestRecommendationService()

        result = service.generate_scenarios("class")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_scenarios_method(self):
        """Test generating scenarios for method."""
        service = TestRecommendationService()

        result = service.generate_scenarios("method")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_explain_rationale_critical(self):
        """Test explaining rationale for critical gap."""
        service = TestRecommendationService()
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

    def test_explain_rationale_high(self):
        """Test explaining rationale for high risk gap."""
        service = TestRecommendationService()
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

    def test_recommend_tests(self):
        """Test generating test recommendations."""
        service = TestRecommendationService()
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

    def test_recommend_tests_max_recommendations(self):
        """Test limiting recommendations."""
        service = TestRecommendationService()
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

    def test_score_to_priority_critical(self):
        """Test converting score to critical priority."""
        result = TestRecommendationService._score_to_priority(85.0)
        assert result == "critical"

    def test_score_to_priority_high(self):
        """Test converting score to high priority."""
        result = TestRecommendationService._score_to_priority(65.0)
        assert result == "high"

    def test_score_to_priority_medium(self):
        """Test converting score to medium priority."""
        result = TestRecommendationService._score_to_priority(45.0)
        assert result == "medium"

    def test_score_to_priority_low(self):
        """Test converting score to low priority."""
        result = TestRecommendationService._score_to_priority(20.0)
        assert result == "low"
