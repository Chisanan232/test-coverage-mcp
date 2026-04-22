"""Coverage risk analysis service for PR and code analysis."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain import RiskLevel


class CoverageRiskAnalysisService:
    """Service for analyzing coverage risks in pull requests and code changes."""

    def __init__(self) -> None:
        """Initialize the risk analysis service."""
        self._risk_thresholds = {
            RiskLevel.CRITICAL: 0.0,
            RiskLevel.HIGH: 20.0,
            RiskLevel.MEDIUM: 50.0,
            RiskLevel.LOW: 80.0,
        }

    def score_pr_risk(
        self,
        base_coverage: float,
        head_coverage: float,
        changed_files_count: int,
        uncovered_changed_lines: int,
        total_changed_lines: int,
    ) -> Dict[str, Any]:
        """Score the risk level of a pull request.

        Analyzes coverage metrics to determine PR risk level based on:
        - Coverage delta
        - Number of changed files
        - Uncovered changed lines
        - Coverage of changed code

        Args:
            base_coverage: Base branch coverage percentage
            head_coverage: PR branch coverage percentage
            changed_files_count: Number of files changed in PR
            uncovered_changed_lines: Number of uncovered lines in changes
            total_changed_lines: Total number of changed lines

        Returns:
            Dictionary with PR risk scoring:
            - risk_level: Overall risk level (low, medium, high, critical)
            - risk_score: Numerical risk score (0-100)
            - coverage_delta: Change in coverage percentage
            - changed_code_coverage: Coverage of changed code
            - factors: Individual risk factors
            - recommendations: Risk mitigation recommendations
        """
        # Calculate coverage delta
        coverage_delta = head_coverage - base_coverage

        # Calculate coverage of changed code
        changed_code_coverage = (
            ((total_changed_lines - uncovered_changed_lines) / total_changed_lines * 100)
            if total_changed_lines > 0
            else 0.0
        )

        # Calculate risk factors
        factors = self._calculate_risk_factors(
            coverage_delta,
            changed_files_count,
            uncovered_changed_lines,
            total_changed_lines,
            changed_code_coverage,
        )

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(factors)

        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)

        # Generate recommendations
        recommendations = self._generate_risk_recommendations(
            risk_level, factors, coverage_delta, changed_code_coverage
        )

        return {
            "risk_level": risk_level.value,
            "risk_score": risk_score,
            "coverage_delta": coverage_delta,
            "changed_code_coverage": changed_code_coverage,
            "factors": factors,
            "recommendations": recommendations,
            "base_coverage": base_coverage,
            "head_coverage": head_coverage,
            "changed_files_count": changed_files_count,
            "uncovered_changed_lines": uncovered_changed_lines,
            "total_changed_lines": total_changed_lines,
        }

    def identify_high_risk_files(
        self,
        file_coverage_data: Dict[str, Dict[str, Any]],
        risk_threshold: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """Identify files with high coverage risk.

        Args:
            file_coverage_data: Dictionary mapping file paths to coverage data
            risk_threshold: Risk threshold percentage (default 50%)

        Returns:
            List of high-risk files with details:
            - file_path: Path to the file
            - coverage: Current coverage percentage
            - risk_level: Risk level of the file
            - risk_score: Numerical risk score
            - uncovered_lines: Number of uncovered lines
            - recommendations: Recommendations for improvement
        """
        high_risk_files: List[Dict[str, Any]] = []

        for file_path, coverage_info in file_coverage_data.items():
            coverage = coverage_info.get("coverage", 0.0)
            uncovered_lines = coverage_info.get("uncovered_lines", 0)
            total_lines = coverage_info.get("total_lines", 0)

            # Calculate risk score for file
            risk_score = 100.0 - coverage

            # Check if file exceeds risk threshold
            if risk_score >= risk_threshold:
                risk_level = self._determine_risk_level(risk_score)

                high_risk_files.append(
                    {
                        "file_path": file_path,
                        "coverage": coverage,
                        "risk_level": risk_level.value,
                        "risk_score": risk_score,
                        "uncovered_lines": uncovered_lines,
                        "total_lines": total_lines,
                        "recommendations": self._generate_file_recommendations(
                            file_path, coverage, uncovered_lines, total_lines
                        ),
                    }
                )

        # Sort by risk score (highest first)
        high_risk_files.sort(key=lambda x: x["risk_score"], reverse=True)

        return high_risk_files

    def detect_config_vs_missing_tests(
        self,
        coverage_data: Dict[str, Any],
        config_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Detect whether low coverage is due to config issues or missing tests.

        Args:
            coverage_data: Coverage analysis data
            config_data: Coverage configuration data (optional)

        Returns:
            Dictionary with analysis:
            - is_config_issue: Whether issue is likely config-related
            - is_missing_tests: Whether issue is likely missing tests
            - confidence: Confidence score (0-1)
            - indicators: List of indicators found
            - recommendations: Recommendations for resolution
        """
        indicators: List[str] = []
        config_score = 0.0
        missing_tests_score = 0.0

        # Check for config issues
        if config_data:
            if not config_data.get("is_valid", False):
                indicators.append("Invalid coverage configuration detected")
                config_score += 0.5

            if config_data.get("issues"):
                indicators.append(f"{len(config_data['issues'])} configuration issues found")
                config_score += 0.3

        # Check for missing tests indicators
        coverage = coverage_data.get("coverage", 0.0)
        if coverage < 50.0:
            indicators.append("Coverage below 50% suggests missing tests")
            missing_tests_score += 0.4

        uncovered_regions = coverage_data.get("uncovered_regions", [])
        if uncovered_regions:
            indicators.append(f"{len(uncovered_regions)} uncovered regions detected")
            missing_tests_score += 0.3

        # Normalize scores
        total_score = config_score + missing_tests_score
        if total_score > 0:
            config_score /= total_score
            missing_tests_score /= total_score
        else:
            config_score = 0.5
            missing_tests_score = 0.5

        is_config_issue = config_score > 0.6
        is_missing_tests = missing_tests_score > 0.6

        recommendations = []
        if is_config_issue:
            recommendations.append("Review and fix coverage configuration")
            if config_data and config_data.get("suggestions"):
                recommendations.extend(config_data["suggestions"][:2])

        if is_missing_tests:
            recommendations.append("Add tests for uncovered code regions")
            recommendations.append("Focus on high-risk areas first")

        return {
            "is_config_issue": is_config_issue,
            "is_missing_tests": is_missing_tests,
            "confidence": max(config_score, missing_tests_score),
            "config_score": config_score,
            "missing_tests_score": missing_tests_score,
            "indicators": indicators,
            "recommendations": recommendations,
        }

    def _calculate_risk_factors(
        self,
        coverage_delta: float,
        changed_files_count: int,
        uncovered_changed_lines: int,
        total_changed_lines: int,
        changed_code_coverage: float,
    ) -> Dict[str, float]:
        """Calculate individual risk factors for a PR.

        Args:
            coverage_delta: Change in coverage percentage
            changed_files_count: Number of files changed
            uncovered_changed_lines: Number of uncovered changed lines
            total_changed_lines: Total changed lines
            changed_code_coverage: Coverage of changed code

        Returns:
            Dictionary with risk factors (0-100 scale)
        """
        factors: Dict[str, float] = {}

        # Coverage delta factor (negative delta is risky)
        if coverage_delta < 0:
            factors["coverage_regression"] = min(100.0, abs(coverage_delta) * 10)
        else:
            factors["coverage_regression"] = 0.0

        # Changed files factor (more files = more risk)
        factors["file_count_risk"] = min(100.0, changed_files_count * 5)

        # Uncovered changed lines factor (most important)
        if total_changed_lines > 0:
            uncovered_ratio = uncovered_changed_lines / total_changed_lines
            factors["uncovered_changes_risk"] = uncovered_ratio * 100.0
        else:
            factors["uncovered_changes_risk"] = 0.0

        # Changed code coverage factor
        factors["changed_code_coverage_risk"] = 100.0 - changed_code_coverage

        return factors

    def _calculate_risk_score(self, factors: Dict[str, float]) -> float:
        """Calculate overall risk score from factors.

        Args:
            factors: Dictionary of risk factors

        Returns:
            Overall risk score (0-100)
        """
        if not factors:
            return 0.0

        # Weight factors
        weights = {
            "uncovered_changes_risk": 0.4,
            "changed_code_coverage_risk": 0.3,
            "coverage_regression": 0.2,
            "file_count_risk": 0.1,
        }

        weighted_score = 0.0
        for factor_name, factor_value in factors.items():
            weight = weights.get(factor_name, 0.0)
            weighted_score += factor_value * weight

        return min(100.0, weighted_score)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score.

        Args:
            risk_score: Numerical risk score (0-100)

        Returns:
            Risk level enum
        """
        if risk_score >= 75.0:
            return RiskLevel.CRITICAL
        elif risk_score >= 50.0:
            return RiskLevel.HIGH
        elif risk_score >= 25.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_risk_recommendations(
        self,
        risk_level: RiskLevel,
        factors: Dict[str, float],
        coverage_delta: float,
        changed_code_coverage: float,
    ) -> List[str]:
        """Generate recommendations based on risk analysis.

        Args:
            risk_level: Overall risk level
            factors: Risk factors
            coverage_delta: Coverage change
            changed_code_coverage: Coverage of changed code

        Returns:
            List of recommendations
        """
        recommendations: List[str] = []

        if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            recommendations.append("⚠️ High-risk PR detected - careful review recommended")

        if coverage_delta < 0:
            recommendations.append(f"Coverage regression of {abs(coverage_delta):.1f}% detected")

        if changed_code_coverage < 80.0:
            recommendations.append(
                f"Only {changed_code_coverage:.1f}% of changed code is covered - add tests"
            )

        if factors.get("file_count_risk", 0) > 50:
            recommendations.append("Many files changed - consider breaking into smaller PRs")

        if risk_level == RiskLevel.LOW:
            recommendations.append("✓ Low-risk PR - coverage looks good")

        return recommendations

    def _generate_file_recommendations(
        self,
        file_path: str,
        coverage: float,
        uncovered_lines: int,
        total_lines: int,
    ) -> List[str]:
        """Generate recommendations for a specific file.

        Args:
            file_path: Path to the file
            coverage: Coverage percentage
            uncovered_lines: Number of uncovered lines
            total_lines: Total lines in file

        Returns:
            List of recommendations
        """
        recommendations: List[str] = []

        if coverage < 30.0:
            recommendations.append(f"Critical: {file_path} has very low coverage ({coverage:.1f}%)")
        elif coverage < 60.0:
            recommendations.append(f"High priority: {file_path} needs test coverage")
        else:
            recommendations.append(f"Medium priority: Improve coverage in {file_path}")

        if uncovered_lines > 0:
            recommendations.append(f"Add tests for {uncovered_lines} uncovered lines")

        return recommendations
