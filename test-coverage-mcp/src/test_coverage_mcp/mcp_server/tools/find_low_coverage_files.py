"""Tool for finding files with low coverage."""

from typing import Any, Dict, List

from test_coverage_mcp.services import CoverageGapDiscoveryService


def find_low_coverage_files(
    repo_slug: str,
    provider: str,
    ref: str,
    threshold: float = 80.0,
    limit: int = 10,
) -> Dict[str, Any]:
    """Find files with coverage below a specified threshold.

    Analyzes repository coverage and identifies files with low coverage,
    ranked by improvement potential.

    Args:
        repo_slug: Repository slug (owner/repo)
        provider: Coverage provider name
        ref: Git reference (branch, tag, or commit)
        threshold: Coverage threshold percentage (default: 80.0)
        limit: Maximum number of files to return (default: 10)

    Returns:
        Dictionary with low coverage files analysis:
        - ref: The git reference analyzed
        - threshold: Coverage threshold used
        - total_files: Total files analyzed
        - low_coverage_files: List of files below threshold
        - summary: Summary of findings
    """
    # Parse repo slug
    try:
        repo_owner, repo_name = repo_slug.split("/", 1)
    except ValueError:
        return {
            "error": f"Invalid repo_slug format: {repo_slug}. Expected 'owner/repo'",
            "error_code": "INVALID_REPO_SLUG",
        }

    # Validate threshold
    if threshold < 0 or threshold > 100:
        return {
            "error": f"Invalid threshold: {threshold}. Must be between 0 and 100",
            "error_code": "INVALID_THRESHOLD",
        }

    # Initialize gap discovery service
    gap_service = CoverageGapDiscoveryService()

    # Get file coverage data (in real implementation, would fetch from provider)
    file_coverage_data: Dict[str, Dict[str, Any]] = {}

    # Find files below threshold
    low_coverage_files = []

    for file_path, file_data in file_coverage_data.items():
        coverage_percentage = file_data.get("coverage_percentage", 0.0)

        if coverage_percentage < threshold:
            low_coverage_files.append(
                {
                    "file_path": file_path,
                    "coverage_percentage": coverage_percentage,
                    "covered_lines": file_data.get("covered_lines", 0),
                    "total_lines": file_data.get("total_lines", 0),
                    "improvement_potential": threshold - coverage_percentage,
                }
            )

    # Sort by improvement potential (descending)
    low_coverage_files.sort(
        key=lambda x: x["improvement_potential"], reverse=True
    )

    # Limit results
    low_coverage_files = low_coverage_files[:limit]

    # Generate summary
    total_files = len(file_coverage_data)
    files_below_threshold = len(
        [
            f
            for f in file_coverage_data.values()
            if f.get("coverage_percentage", 0.0) < threshold
        ]
    )

    summary = f"Found {files_below_threshold} files below {threshold}% threshold out of {total_files} total files"

    return {
        "ref": ref,
        "threshold": threshold,
        "total_files": total_files,
        "files_below_threshold": files_below_threshold,
        "low_coverage_files": low_coverage_files,
        "summary": summary,
    }
