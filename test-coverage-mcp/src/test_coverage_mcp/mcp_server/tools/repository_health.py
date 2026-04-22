"""Repository health analysis tools for MCP."""

from typing import Any, Dict, Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    ExecutionMetadata,
    RepositoryHealthResponse,
    SupportLevel,
)
from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.mcp_server.tools.metadata import TOOL_METADATA
from test_coverage_mcp.services import ProviderDiscoveryService, RepositoryHealthService

# Get or create MCP instance for decorator registration
_mcp = mcp_factory.get_or_create()


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


_health_metadata = TOOL_METADATA["get_repository_test_health"]


@_mcp.tool(
    title=_health_metadata["title"],
    name=_health_metadata["name"],
    description=_health_metadata["description"],
    annotations=_health_metadata["annotations"],
)
def get_repository_test_health(
    repo_slug: str,
    provider: Optional[str] = None,
    ref: Optional[str] = None,
    threshold: float = 80.0,
) -> RepositoryHealthResponse:
    """Get test coverage health summary for a repository.

    This tool analyzes the test coverage health of a repository using available
    coverage providers. It identifies risks, provides recommendations, and
    generates next actions for improvement.

    Args:
        repo_slug: Repository slug in format "owner/repo"
        provider: Specific provider to use (optional, uses best available if not specified)
        ref: Git reference (branch, tag, commit) to analyze (optional)
        threshold: Coverage threshold percentage (default 80%)

    Returns:
        Dictionary containing:
        - repo_slug: Repository identifier
        - coverage_metrics: Aggregated coverage metrics
        - health_summary: Overall health status
        - risk_analysis: Risk identification and recommendations
        - next_actions: Recommended actions for improvement
        - execution_metadata: Execution metadata

    Example:
        >>> result = get_repository_test_health("owner/repo", threshold=85.0)
        >>> print(f"Coverage: {result['coverage_metrics']['average_coverage']}%")
        >>> print(f"Risk Level: {result['risk_analysis']['risk_level']}")
        >>> for action in result['next_actions']:
        ...     print(f"- {action}")
    """
    try:
        if "/" not in repo_slug:
            return {
                "error": "Invalid repo_slug format. Use 'owner/repo'",
                "error_type": "InvalidRepositorySlugError",
                "execution_metadata": _create_execution_metadata("get_repository_test_health"),
            }

        repo_owner, repo_name = repo_slug.split("/", 1)

        discovery_service = ProviderDiscoveryService()
        health_service = RepositoryHealthService(discovery_service)

        if provider:
            selected_provider = discovery_service.get_provider(provider)
            if selected_provider is None:
                return {
                    "error": f"Provider '{provider}' not found",
                    "error_type": "ProviderNotFoundError",
                    "execution_metadata": _create_execution_metadata("get_repository_test_health"),
                }

        metrics = health_service.aggregate_coverage_metrics(repo_owner, repo_name)
        risk_analysis = health_service.identify_risks(repo_owner, repo_name, threshold)
        next_actions = health_service.get_next_actions(repo_owner, repo_name)

        return {
            "repo_slug": repo_slug,
            "ref": ref,
            "coverage_metrics": {
                "average_coverage": metrics.get("average_coverage", 0.0),
                "coverage_range": metrics.get("coverage_range", {}),
                "providers_queried": metrics.get("providers_queried", 0),
                "providers_succeeded": metrics.get("providers_succeeded", 0),
                "providers_failed": metrics.get("providers_failed", 0),
            },
            "health_summary": {
                "is_healthy": metrics.get("average_coverage", 0.0) >= threshold,
                "coverage_below_threshold": metrics.get("average_coverage", 0.0) < threshold,
                "threshold": threshold,
            },
            "risk_analysis": {
                "risk_level": risk_analysis.get("risk_level"),
                "current_coverage": risk_analysis.get("current_coverage", 0.0),
                "gap": risk_analysis.get("gap", 0.0),
                "recommendations": risk_analysis.get("recommendations", []),
            },
            "next_actions": next_actions,
            "execution_metadata": _create_execution_metadata("get_repository_test_health"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": "RepositoryHealthAnalysisError",
            "repo_slug": repo_slug,
            "execution_metadata": _create_execution_metadata("get_repository_test_health"),
        }
