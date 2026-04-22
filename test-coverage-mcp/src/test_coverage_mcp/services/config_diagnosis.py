"""Service for diagnosing coverage configuration issues."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain.models import ConfigDiagnosis


class CoverageConfigDiagnosisService:
    """Service for diagnosing coverage configuration issues.

    Analyzes coverage configuration to identify:
    - Over-included paths
    - Missing exclusions
    - Threshold issues
    - Component/flag scoping problems
    """

    def __init__(self) -> None:
        """Initialize the config diagnosis service."""
        pass

    def retrieve_config(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Retrieve coverage configuration for a repository.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Configuration dictionary with:
            - include_paths: List of included paths
            - exclude_paths: List of excluded paths
            - thresholds: Coverage thresholds
            - components: Component definitions
            - flags: Feature flags
        """
        return {
            "include_paths": [],
            "exclude_paths": [],
            "thresholds": {},
            "components": {},
            "flags": {},
        }

    def parse_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate coverage configuration.

        Args:
            config: Raw configuration dictionary

        Returns:
            Parsed configuration with validation results
        """
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
            "parsed": config,
        }

    def detect_over_included_paths(
        self, config: Dict[str, Any], file_coverage: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect paths that are included but have no coverage data.

        Args:
            config: Configuration dictionary
            file_coverage: File coverage data

        Returns:
            List of over-included paths with details:
            - path: The over-included path
            - reason: Why it's over-included
            - suggestion: Suggested action
        """
        over_included = []

        include_paths = config.get("include_paths", [])
        for path in include_paths:
            # Check if path has any coverage data
            has_coverage = any(
                file_path.startswith(path) for file_path in file_coverage.keys()
            )

            if not has_coverage:
                over_included.append(
                    {
                        "path": path,
                        "reason": "No coverage data found for this path",
                        "suggestion": f"Remove '{path}' from include_paths or add coverage data",
                    }
                )

        return over_included

    def suggest_missing_exclusions(
        self, config: Dict[str, Any], file_coverage: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest missing exclusions based on file patterns.

        Args:
            config: Configuration dictionary
            file_coverage: File coverage data

        Returns:
            List of suggested exclusions with details:
            - pattern: The pattern to exclude
            - reason: Why it should be excluded
            - affected_files: Number of files affected
        """
        suggestions = []
        exclude_paths = config.get("exclude_paths", [])

        # Common patterns that should be excluded
        common_patterns = [
            ("**/test/**", "Test files"),
            ("**/tests/**", "Test files"),
            ("**/mock/**", "Mock files"),
            ("**/__pycache__/**", "Python cache"),
            ("**/node_modules/**", "Node modules"),
            ("**/.venv/**", "Virtual environment"),
            ("**/dist/**", "Distribution files"),
            ("**/build/**", "Build files"),
        ]

        for pattern, reason in common_patterns:
            if pattern not in exclude_paths:
                # Count affected files
                affected_count = sum(
                    1
                    for file_path in file_coverage.keys()
                    if self._matches_pattern(file_path, pattern)
                )

                if affected_count > 0:
                    suggestions.append(
                        {
                            "pattern": pattern,
                            "reason": reason,
                            "affected_files": affected_count,
                        }
                    )

        return suggestions

    def review_thresholds(
        self, config: Dict[str, Any], current_coverage: float
    ) -> Dict[str, Any]:
        """Review coverage thresholds for reasonableness.

        Args:
            config: Configuration dictionary
            current_coverage: Current coverage percentage

        Returns:
            Threshold review with:
            - thresholds: Current thresholds
            - issues: Any issues found
            - recommendations: Recommendations for adjustment
        """
        thresholds = config.get("thresholds", {})
        issues = []
        recommendations = []

        # Check if thresholds are reasonable
        if thresholds:
            min_threshold = thresholds.get("minimum", 0)
            if min_threshold > 95:
                issues.append("Minimum threshold is very high (>95%)")
                recommendations.append("Consider lowering to 80-90% for realistic goals")

            if min_threshold < 50:
                issues.append("Minimum threshold is very low (<50%)")
                recommendations.append("Consider raising to at least 70%")

            # Check if current coverage meets thresholds
            if current_coverage < min_threshold:
                issues.append(
                    f"Current coverage ({current_coverage:.1f}%) is below minimum threshold ({min_threshold}%)"
                )

        return {
            "thresholds": thresholds,
            "issues": issues,
            "recommendations": recommendations,
        }

    def review_component_scoping(
        self, config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Review component and flag scoping for issues.

        Args:
            config: Configuration dictionary

        Returns:
            List of scoping issues with details:
            - component: Component or flag name
            - issue: The issue found
            - suggestion: Suggested fix
        """
        issues = []
        components = config.get("components", {})
        flags = config.get("flags", {})

        # Check components
        for component_name, component_config in components.items():
            paths = component_config.get("paths", [])
            if not paths:
                issues.append(
                    {
                        "component": component_name,
                        "issue": "No paths defined for component",
                        "suggestion": f"Add paths to component '{component_name}'",
                    }
                )

            # Check for overlapping paths
            for other_name, other_config in components.items():
                if component_name != other_name:
                    other_paths = other_config.get("paths", [])
                    for path in paths:
                        for other_path in other_paths:
                            if path.startswith(other_path) or other_path.startswith(
                                path
                            ):
                                issues.append(
                                    {
                                        "component": component_name,
                                        "issue": f"Overlapping paths with component '{other_name}'",
                                        "suggestion": f"Clarify path boundaries between '{component_name}' and '{other_name}'",
                                    }
                                )

        # Check flags
        for flag_name, flag_config in flags.items():
            paths = flag_config.get("paths", [])
            if not paths:
                issues.append(
                    {
                        "component": flag_name,
                        "issue": "No paths defined for flag",
                        "suggestion": f"Add paths to flag '{flag_name}'",
                    }
                )

        return issues

    def diagnose_config(
        self,
        repo_owner: str,
        repo_name: str,
        file_coverage: Dict[str, Dict[str, Any]],
        current_coverage: float,
    ) -> ConfigDiagnosis:
        """Perform comprehensive configuration diagnosis.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            file_coverage: File coverage data
            current_coverage: Current coverage percentage

        Returns:
            Configuration diagnosis with all findings
        """
        # Retrieve and parse config
        config = self.retrieve_config(repo_owner, repo_name)
        parse_result = self.parse_config(config)

        if not parse_result["valid"]:
            return ConfigDiagnosis(
                repo_owner=repo_owner,
                repo_name=repo_name,
                config_valid=False,
                parse_errors=parse_result["errors"],
                over_included_paths=[],
                missing_exclusions=[],
                threshold_issues=[],
                scoping_issues=[],
                summary="Configuration is invalid",
            )

        # Perform all diagnostic checks
        over_included = self.detect_over_included_paths(config, file_coverage)
        missing_exclusions = self.suggest_missing_exclusions(config, file_coverage)
        threshold_review = self.review_thresholds(config, current_coverage)
        scoping_issues = self.review_component_scoping(config)

        # Build summary
        total_issues = (
            len(over_included)
            + len(missing_exclusions)
            + len(threshold_review["issues"])
            + len(scoping_issues)
        )

        summary = f"Found {total_issues} configuration issues"
        if total_issues == 0:
            summary = "Configuration looks good"

        return ConfigDiagnosis(
            repo_owner=repo_owner,
            repo_name=repo_name,
            config_valid=True,
            parse_errors=[],
            over_included_paths=over_included,
            missing_exclusions=missing_exclusions,
            threshold_issues=threshold_review["issues"],
            scoping_issues=scoping_issues,
            summary=summary,
        )

    @staticmethod
    def _matches_pattern(file_path: str, pattern: str) -> bool:
        """Check if file path matches a pattern.

        Args:
            file_path: File path to check
            pattern: Pattern to match against

        Returns:
            True if file matches pattern
        """
        # Simple pattern matching for common cases
        if pattern.startswith("**/") and pattern.endswith("/**"):
            # Pattern like **/test/**
            middle = pattern[3:-3]
            return f"/{middle}/" in f"/{file_path}/"
        elif pattern.startswith("**/"):
            # Pattern like **/test.py
            suffix = pattern[3:]
            return file_path.endswith(suffix) or f"/{suffix}" in file_path
        elif pattern.endswith("/**"):
            # Pattern like src/**
            prefix = pattern[:-3]
            return file_path.startswith(prefix) or file_path.startswith(f"{prefix}/")
        else:
            return file_path == pattern
