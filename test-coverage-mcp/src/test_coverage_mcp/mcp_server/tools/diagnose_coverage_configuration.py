"""Tool for diagnosing coverage configuration."""

from typing import Any, Dict

from test_coverage_mcp.services.config_diagnosis import CoverageConfigDiagnosisService


def diagnose_coverage_configuration(
    repo_slug: str,
    provider: str,
) -> Dict[str, Any]:
    """Diagnose coverage configuration issues.

    Analyzes repository coverage configuration and identifies potential issues
    such as over-included paths, missing exclusions, threshold problems, and
    component scoping issues.

    Args:
        repo_slug: Repository slug (owner/repo)
        provider: Coverage provider name

    Returns:
        Dictionary with configuration diagnosis:
        - repo_owner: Repository owner
        - repo_name: Repository name
        - config_valid: Whether configuration is valid
        - parse_errors: List of parsing errors
        - over_included_paths: Paths that are over-included
        - missing_exclusions: Suggested missing exclusions
        - threshold_issues: Issues with coverage thresholds
        - scoping_issues: Issues with component/flag scoping
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

    # Initialize config diagnosis service
    diagnosis_service = CoverageConfigDiagnosisService()

    # Get file coverage data (in real implementation, would fetch from provider)
    file_coverage_data: Dict[str, Dict[str, Any]] = {}
    current_coverage = 0.0

    # Perform diagnosis
    diagnosis = diagnosis_service.diagnose_config(
        repo_owner, repo_name, file_coverage_data, current_coverage
    )

    return {
        "repo_owner": diagnosis.repo_owner,
        "repo_name": diagnosis.repo_name,
        "config_valid": diagnosis.config_valid,
        "parse_errors": diagnosis.parse_errors,
        "over_included_paths": diagnosis.over_included_paths,
        "missing_exclusions": diagnosis.missing_exclusions,
        "threshold_issues": diagnosis.threshold_issues,
        "scoping_issues": diagnosis.scoping_issues,
        "summary": diagnosis.summary,
    }
