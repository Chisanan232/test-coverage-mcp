"""Tool for finding untested changed code in pull requests."""

from typing import Any, Dict

from test_coverage_mcp.mcp_server.tools.models.pr_analysis import (
    FindUntestedCodeInput,
    FindUntestedCodeOutput,
    UncoveredRegionOutput,
)
from test_coverage_mcp.services import CoverageGapDiscoveryService


def find_untested_changed_code(
    repo_slug: str,
    provider: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Find untested changed code between two references.

    Analyzes coverage gaps in changed code and identifies uncovered regions
    that need test coverage. Handles pending analysis states from providers.

    Args:
        repo_slug: Repository slug (owner/repo)
        provider: Coverage provider name
        base_ref: Base reference (branch, tag, or commit)
        head_ref: Head reference to compare against

    Returns:
        Dictionary with untested code analysis:
        - total_changed_lines: Total lines changed
        - covered_changed_lines: Lines changed that are covered
        - uncovered_changed_lines: Lines changed that are uncovered
        - coverage_percentage: Coverage of changed code
        - uncovered_regions: List of uncovered regions with risk levels
        - pending_regions: Regions with pending analysis
        - has_pending: Whether pending analysis exists
        - gap_summary: Summary of coverage gaps
    """
    # Parse repo slug
    try:
        repo_owner, repo_name = repo_slug.split("/", 1)
    except ValueError:
        return {
            "error": f"Invalid repo_slug format: {repo_slug}. Expected 'owner/repo'",
            "error_code": "INVALID_REPO_SLUG",
        }

    # Initialize gap discovery service
    gap_service = CoverageGapDiscoveryService()

    # Get file coverage data (in real implementation, would fetch from provider)
    # For now, return structure with empty data
    file_coverage_data: Dict[str, Dict[str, Any]] = {}

    # Analyze changed code
    changed_code_analysis = gap_service.analyze_changed_code(
        repo_owner, repo_name, base_ref, head_ref, file_coverage_data
    )

    # Detect uncovered regions for each file
    uncovered_regions_list = []
    pending_regions_list = []
    has_pending = False

    for file_path in file_coverage_data.keys():
        file_data = file_coverage_data[file_path]

        # Detect uncovered regions
        uncovered_regions = gap_service.detect_uncovered_regions(file_path, file_data)
        for region in uncovered_regions:
            uncovered_regions_list.append(
                UncoveredRegionOutput(
                    file_path=region["file_path"],
                    start_line=region["start_line"],
                    end_line=region["end_line"],
                    region_type=region["region_type"],
                    risk_level=region["risk_level"],
                    lines_count=region["lines_count"],
                )
            )

        # Handle pending analysis
        pending_result = gap_service.handle_pending_analysis(file_path, file_data)
        if pending_result["has_pending"]:
            has_pending = True
            pending_regions_list.extend(pending_result["pending_regions"])

    return {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "total_changed_lines": changed_code_analysis["total_changed_lines"],
        "covered_changed_lines": changed_code_analysis["covered_changed_lines"],
        "uncovered_changed_lines": changed_code_analysis["uncovered_changed_lines"],
        "coverage_percentage": changed_code_analysis["coverage_percentage"],
        "uncovered_regions": [r.model_dump() for r in uncovered_regions_list],
        "pending_regions": pending_regions_list,
        "has_pending": has_pending,
        "gap_summary": changed_code_analysis["gap_summary"],
    }
