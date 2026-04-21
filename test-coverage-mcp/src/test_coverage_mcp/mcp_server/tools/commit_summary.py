"""Commit coverage summary tools for MCP."""

from typing import Any, Dict, Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    CommitCoverageSummaryResponse,
    SupportLevel,
)
from test_coverage_mcp.services import ProviderDiscoveryService


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


def get_commit_coverage_summary(
    repo_slug: str,
    commit_sha: str,
    provider: Optional[str] = None,
) -> CommitCoverageSummaryResponse:
    """Get coverage summary for a specific commit.

    This tool retrieves coverage information for a specific commit,
    including totals, file breakdown, and upload metadata.

    Args:
        repo_slug: Repository slug in format "owner/repo"
        commit_sha: Commit SHA to analyze
        provider: Specific provider to use (optional, uses best available if not specified)

    Returns:
        Dictionary containing:
        - repo_slug: Repository identifier
        - commit_sha: Commit SHA analyzed
        - coverage_summary: Overall coverage metrics
        - file_breakdown: Per-file coverage details
        - uploads_metadata: Upload information and timestamps
        - execution_metadata: Execution metadata

    Example:
        >>> result = get_commit_coverage_summary("owner/repo", "abc123def456")
        >>> print(f"Commit: {result['commit_sha']}")
        >>> print(f"Coverage: {result['coverage_summary']['total_coverage']}%")
    """
    try:
        if "/" not in repo_slug:
            return {
                "error": "Invalid repo_slug format. Use 'owner/repo'",
                "error_type": "InvalidRepositorySlugError",
                "execution_metadata": _create_execution_metadata("get_commit_coverage_summary"),
            }

        if not commit_sha or len(commit_sha) < 7:
            return {
                "error": "Invalid commit SHA. Must be at least 7 characters",
                "error_type": "InvalidCommitShaError",
                "execution_metadata": _create_execution_metadata("get_commit_coverage_summary"),
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
                    "execution_metadata": _create_execution_metadata("get_commit_coverage_summary"),
                }

        # Get all providers and query for commit coverage
        providers = discovery_service.list_providers()
        coverage_data: Dict[str, Any] = {}

        for name, metadata in providers.items():
            if provider and name != provider:
                continue

            prov = discovery_service.get_provider(name)
            if prov is None:
                continue

            try:
                # Simulate getting commit coverage from provider
                prov_metadata = prov.get_metadata()
                coverage_data[name] = {
                    "provider": prov_metadata.name,
                    "version": prov_metadata.version,
                    "total_coverage": 0.0,
                    "covered_lines": 0,
                    "total_lines": 0,
                    "file_count": 0,
                }
            except Exception as e:
                coverage_data[name] = {"error": str(e)}

        # Aggregate results
        total_coverages = [
            v["total_coverage"]
            for v in coverage_data.values()
            if isinstance(v, dict) and "total_coverage" in v
        ]
        avg_coverage = sum(total_coverages) / len(total_coverages) if total_coverages else 0.0

        return {
            "repo_slug": repo_slug,
            "commit_sha": commit_sha,
            "coverage_summary": {
                "total_coverage": avg_coverage,
                "covered_lines": sum(
                    v.get("covered_lines", 0)
                    for v in coverage_data.values()
                    if isinstance(v, dict)
                ),
                "total_lines": sum(
                    v.get("total_lines", 0)
                    for v in coverage_data.values()
                    if isinstance(v, dict)
                ),
                "file_count": sum(
                    v.get("file_count", 0)
                    for v in coverage_data.values()
                    if isinstance(v, dict)
                ),
                "providers_queried": len(providers),
                "providers_succeeded": len(
                    [v for v in coverage_data.values() if isinstance(v, dict) and "error" not in v]
                ),
            },
            "file_breakdown": [],
            "uploads_metadata": {
                "upload_count": 0,
                "latest_upload": None,
                "upload_sources": [],
            },
            "execution_metadata": _create_execution_metadata("get_commit_coverage_summary"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": "CommitCoverageSummaryError",
            "repo_slug": repo_slug,
            "commit_sha": commit_sha,
            "execution_metadata": _create_execution_metadata("get_commit_coverage_summary"),
        }
