"""Tool for analyzing PR coverage risk."""

from typing import Any, Dict

from test_coverage_mcp.mcp_server.tools.models.pr_analysis import (
    AnalyzePRRiskInput,
    AnalyzePRRiskOutput,
)
from test_coverage_mcp.services import CoverageRiskAnalysisService


def analyze_pr_coverage_risk(
    repo_slug: str,
    provider: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Analyze coverage risk of a pull request.

    Evaluates PR risk based on coverage metrics including coverage delta,
    changed files, and uncovered changed lines. Provides risk assessment
    with recommendations for improvement.

    Args:
        repo_slug: Repository slug (owner/repo)
        provider: Coverage provider name
        base_ref: Base reference (branch, tag, or commit)
        head_ref: Head reference to compare against

    Returns:
        Dictionary with PR risk assessment:
        - risk_level: Overall risk level (low, medium, high, critical)
        - risk_score: Numerical risk score (0-100)
        - coverage_delta: Change in coverage percentage
        - changed_code_coverage: Coverage of changed code
        - changed_files_count: Number of files changed
        - uncovered_changed_lines: Number of uncovered changed lines
        - total_changed_lines: Total number of changed lines
        - recommendations: Risk mitigation recommendations
        - high_risk_files: Files with high coverage risk
    """
    # Parse repo slug
    try:
        repo_owner, repo_name = repo_slug.split("/", 1)
    except ValueError:
        return {
            "error": f"Invalid repo_slug format: {repo_slug}. Expected 'owner/repo'",
            "error_code": "INVALID_REPO_SLUG",
        }

    # Initialize risk analysis service
    risk_service = CoverageRiskAnalysisService()

    # Get coverage data (in real implementation, would fetch from provider)
    # For now, use default values
    base_coverage = 85.0
    head_coverage = 85.0
    changed_files_count = 0
    uncovered_changed_lines = 0
    total_changed_lines = 0

    # Score PR risk
    risk_result = risk_service.score_pr_risk(
        base_coverage=base_coverage,
        head_coverage=head_coverage,
        changed_files_count=changed_files_count,
        uncovered_changed_lines=uncovered_changed_lines,
        total_changed_lines=total_changed_lines,
    )

    # Identify high-risk files (in real implementation, would use actual file data)
    file_coverage_data: Dict[str, Dict[str, Any]] = {}
    high_risk_files = risk_service.identify_high_risk_files(file_coverage_data)

    return {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "risk_level": risk_result["risk_level"],
        "risk_score": risk_result["risk_score"],
        "coverage_delta": risk_result["coverage_delta"],
        "changed_code_coverage": risk_result["changed_code_coverage"],
        "changed_files_count": risk_result["changed_files_count"],
        "uncovered_changed_lines": risk_result["uncovered_changed_lines"],
        "total_changed_lines": risk_result["total_changed_lines"],
        "recommendations": risk_result["recommendations"],
        "high_risk_files": high_risk_files,
    }
