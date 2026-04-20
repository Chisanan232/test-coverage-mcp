"""Service for generating test recommendations."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain.models import TestRecommendation


class RecommendationService:
    """Service for generating test recommendations.

    Provides intelligent test recommendations based on:
    - Coverage gaps
    - Code complexity
    - Test type suggestions
    - Priority ranking
    """

    def __init__(self) -> None:
        """Initialize the test recommendation service."""
        pass

    def identify_test_gaps(
        self, uncovered_regions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify test gaps from uncovered regions.

        Args:
            uncovered_regions: List of uncovered regions

        Returns:
            List of identified test gaps with details
        """
        gaps = []

        for region in uncovered_regions:
            gap = {
                "file_path": region.get("file_path"),
                "start_line": region.get("start_line"),
                "end_line": region.get("end_line"),
                "region_type": region.get("region_type"),
                "lines_count": region.get("lines_count"),
                "risk_level": region.get("risk_level"),
            }
            gaps.append(gap)

        return gaps

    def suggest_test_types(self, region_type: str) -> List[str]:
        """Suggest appropriate test types for a region.

        Args:
            region_type: Type of code region (function, class, etc.)

        Returns:
            List of suggested test types
        """
        test_type_mapping = {
            "function": ["unit", "integration"],
            "class": ["unit", "integration"],
            "method": ["unit", "integration"],
            "block": ["unit"],
            "branch": ["unit"],
            "line": ["unit"],
        }

        return test_type_mapping.get(region_type, ["unit"])

    def rank_by_priority(
        self, gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank test gaps by priority.

        Args:
            gaps: List of test gaps

        Returns:
            Ranked list of gaps with priority scores
        """
        # Assign priority scores
        for gap in gaps:
            score = 0

            # Risk level contributes to priority
            risk_level = gap.get("risk_level", "low")
            risk_scores = {
                "critical": 40,
                "high": 30,
                "medium": 20,
                "low": 10,
            }
            score += risk_scores.get(risk_level, 10)

            # Region type contributes to priority
            region_type = gap.get("region_type", "line")
            type_scores = {
                "class": 30,
                "function": 25,
                "method": 25,
                "block": 15,
                "branch": 10,
                "line": 5,
            }
            score += type_scores.get(region_type, 5)

            # Lines count contributes to priority
            lines_count = gap.get("lines_count", 1)
            if lines_count > 50:
                score += 20
            elif lines_count > 20:
                score += 15
            elif lines_count > 10:
                score += 10
            else:
                score += 5

            gap["priority_score"] = score

        # Sort by priority score (descending)
        return sorted(gaps, key=lambda x: x["priority_score"], reverse=True)

    def generate_scenarios(self, region_type: str) -> List[Dict[str, str]]:
        """Generate test scenarios for a code region.

        Args:
            region_type: Type of code region

        Returns:
            List of test scenarios with descriptions
        """
        scenarios_by_type = {
            "function": [
                {
                    "name": "Happy path",
                    "description": "Test with valid inputs and expected behavior",
                },
                {
                    "name": "Edge cases",
                    "description": "Test boundary conditions and limits",
                },
                {
                    "name": "Error handling",
                    "description": "Test error conditions and exceptions",
                },
                {
                    "name": "Performance",
                    "description": "Test with large inputs and performance constraints",
                },
            ],
            "class": [
                {
                    "name": "Initialization",
                    "description": "Test class construction and initialization",
                },
                {
                    "name": "State transitions",
                    "description": "Test state changes and lifecycle",
                },
                {
                    "name": "Method interactions",
                    "description": "Test interactions between methods",
                },
                {
                    "name": "Error conditions",
                    "description": "Test error handling and recovery",
                },
            ],
            "method": [
                {
                    "name": "Normal operation",
                    "description": "Test method with typical inputs",
                },
                {
                    "name": "Boundary conditions",
                    "description": "Test method at limits",
                },
                {
                    "name": "Exception handling",
                    "description": "Test method error cases",
                },
            ],
            "block": [
                {
                    "name": "Execution path",
                    "description": "Test the code block execution",
                },
                {
                    "name": "State changes",
                    "description": "Test state modifications",
                },
            ],
            "branch": [
                {
                    "name": "True branch",
                    "description": "Test when condition is true",
                },
                {
                    "name": "False branch",
                    "description": "Test when condition is false",
                },
            ],
        }

        return scenarios_by_type.get(region_type, [])

    def explain_rationale(self, gap: Dict[str, Any]) -> str:
        """Explain why a test gap is important.

        Args:
            gap: Test gap information

        Returns:
            Explanation of the gap's importance
        """
        risk_level = gap.get("risk_level", "low")
        region_type = gap.get("region_type", "code")
        lines_count = gap.get("lines_count", 1)

        rationale_parts = []

        # Risk-based rationale
        if risk_level == "critical":
            rationale_parts.append(
                "This is a critical gap that could cause production issues"
            )
        elif risk_level == "high":
            rationale_parts.append("This is a high-risk gap that needs attention")
        elif risk_level == "medium":
            rationale_parts.append("This gap has moderate risk and should be addressed")

        # Type-based rationale
        if region_type == "class":
            rationale_parts.append(f"The uncovered {region_type} defines core functionality")
        elif region_type == "function":
            rationale_parts.append(
                f"The uncovered {region_type} is used by other components"
            )
        elif region_type == "method":
            rationale_parts.append(
                f"The uncovered {region_type} is part of the public API"
            )

        # Size-based rationale
        if lines_count > 50:
            rationale_parts.append(f"The gap spans {lines_count} lines of code")
        elif lines_count > 20:
            rationale_parts.append(f"The gap spans {lines_count} lines of code")

        return ". ".join(rationale_parts) if rationale_parts else "This gap needs test coverage"

    def recommend_tests(
        self, uncovered_regions: List[Dict[str, Any]], max_recommendations: int = 10
    ) -> List[TestRecommendation]:
        """Generate test recommendations for uncovered regions.

        Args:
            uncovered_regions: List of uncovered regions
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of test recommendations
        """
        # Identify gaps
        gaps = self.identify_test_gaps(uncovered_regions)

        # Rank by priority
        ranked_gaps = self.rank_by_priority(gaps)

        # Generate recommendations
        recommendations = []
        for gap in ranked_gaps[:max_recommendations]:
            region_type = gap.get("region_type", "code")
            test_types = self.suggest_test_types(region_type)
            scenarios = self.generate_scenarios(region_type)
            rationale = self.explain_rationale(gap)

            recommendation = TestRecommendation(
                file_path=gap["file_path"],
                start_line=gap["start_line"],
                end_line=gap["end_line"],
                region_type=region_type,
                test_types=test_types,
                scenarios=[s["description"] for s in scenarios],
                priority=self._score_to_priority(gap.get("priority_score", 0)),
                rationale=rationale,
            )
            recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def _score_to_priority(score: float) -> str:
        """Convert priority score to priority level.

        Args:
            score: Priority score

        Returns:
            Priority level (critical, high, medium, low)
        """
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
