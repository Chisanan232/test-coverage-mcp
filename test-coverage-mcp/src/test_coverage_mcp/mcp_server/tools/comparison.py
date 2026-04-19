"""Coverage comparison tools for MCP."""

from typing import Any, Dict, Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    SupportLevel,
)
from test_coverage_mcp.services import (
    CoverageComparisonService,
    ProviderDiscoveryService,
)


def _create_execution_metadata(tool_name: str) -> Dict[str, Any]:
    """Create execution metadata for tool response.

    Args:
        tool_name: Name of the tool

    Returns:
        Dictionary with execution metadata
    """
    return {
        "provider_name": "test-coverage-mcp",
        "provider_version": "0.1.0",
        "support_level": SupportLevel.ADVANCED.value,
        "used_capabilities": [],
        "analysis_depth": AnalysisDepth.REPOSITORY.value,
        "execution_time_ms": 0.0,
    }


def compare_coverage_between_refs(
    repo_slug: str,
    base_ref: str,
    head_ref: str,
    provider: Optional[str] = None,
    regression_threshold: float = 1.0,
) -> Dict[str, Any]:
    """Compare coverage between two references.

    This tool analyzes coverage differences between two git references
    (branches, tags, or commits), identifying improvements, regressions,
    and providing detailed delta analysis.

    Args:
        repo_slug: Repository slug in format "owner/repo"
        base_ref: Base reference (branch, tag, or commit SHA)
        head_ref: Head reference to compare against
        provider: Specific provider to use (optional, uses best available if not specified)
        regression_threshold: Regression threshold percentage (default 1%)

    Returns:
        Dictionary containing:
        - repo_slug: Repository identifier
        - base_ref: Base reference analyzed
        - head_ref: Head reference analyzed
        - coverage_delta: Coverage change metrics
        - regression_analysis: Regression detection results
        - improvement_analysis: Improvement detection results
        - provider_results: Individual results from each provider
        - execution_metadata: Execution metadata

    Example:
        >>> result = compare_coverage_between_refs("owner/repo", "main", "feature-branch")
        >>> print(f"Delta: {result['coverage_delta']['delta_percentage']}%")
        >>> print(f"Improved: {result['improvement_analysis']['has_improvement']}")
    """
    try:
        if "/" not in repo_slug:
            return {
                "error": "Invalid repo_slug format. Use 'owner/repo'",
                "error_type": "InvalidRepositorySlugError",
                "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
            }

        if not base_ref or not head_ref:
            return {
                "error": "Both base_ref and head_ref are required",
                "error_type": "InvalidReferenceError",
                "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
            }

        if base_ref == head_ref:
            return {
                "error": "base_ref and head_ref must be different",
                "error_type": "InvalidReferenceError",
                "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
            }

        repo_owner, repo_name = repo_slug.split("/", 1)

        discovery_service = ProviderDiscoveryService()

        # Validate provider if specified
        if provider:
            selected_provider = discovery_service.get_provider(provider)
            if selected_provider is None:
                return {
                    "error": f"Provider '{provider}' not found",
                    "error_type": "ProviderNotFoundError",
                    "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
                }

        # Use comparison service to compare refs
        comparison_service = CoverageComparisonService(discovery_service)
        comparison_result = comparison_service.compare_refs(
            repo_owner, repo_name, base_ref, head_ref
        )

        # Detect regressions
        regression_result = comparison_service.detect_regressions(
            repo_owner, repo_name, base_ref, head_ref, regression_threshold
        )

        # Detect improvements
        improvement_result = comparison_service.detect_improvements(
            repo_owner, repo_name, base_ref, head_ref
        )

        return {
            "repo_slug": repo_slug,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "coverage_delta": {
                "base_coverage": comparison_result.get("base_coverage", 0.0),
                "head_coverage": comparison_result.get("head_coverage", 0.0),
                "delta_percentage": comparison_result.get("delta_percentage", 0.0),
                "delta_direction": "improved"
                if comparison_result.get("improved", False)
                else "regressed"
                if comparison_result.get("regression", False)
                else "unchanged",
            },
            "regression_analysis": {
                "has_regression": regression_result.get("has_regression", False),
                "severity": regression_result.get("severity", "none"),
                "threshold": regression_threshold,
                "delta_percentage": regression_result.get("delta_percentage", 0.0),
            },
            "improvement_analysis": {
                "has_improvement": improvement_result.get("has_improvement", False),
                "delta_percentage": improvement_result.get("delta_percentage", 0.0),
                "improvement_percentage": improvement_result.get("improvement_percentage", 0.0),
            },
            "provider_results": comparison_result.get("provider_results", {}),
            "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": "CoverageComparisonError",
            "repo_slug": repo_slug,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "execution_metadata": _create_execution_metadata("compare_coverage_between_refs"),
        }
