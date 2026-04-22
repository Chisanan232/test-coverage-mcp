"""Tool for recommending test plans."""

from typing import Any, Dict, List

from test_coverage_mcp.services.test_recommendation import RecommendationService


def recommend_test_plan(
    repo_slug: str,
    provider: str,
    target: str = "repo",
) -> Dict[str, Any]:
    """Recommend a test plan for coverage improvement.

    Analyzes coverage gaps and generates intelligent test recommendations
    with prioritization and scenario suggestions.

    Args:
        repo_slug: Repository slug (owner/repo)
        provider: Coverage provider name
        target: Analysis target - 'repo', 'pr', or file path (default: 'repo')

    Returns:
        Dictionary with test plan recommendations:
        - target: The analysis target
        - total_gaps: Total number of coverage gaps
        - recommendations: List of test recommendations
        - summary: Summary of test plan
    """
    # Parse repo slug
    try:
        repo_owner, repo_name = repo_slug.split("/", 1)
    except ValueError:
        return {
            "error": f"Invalid repo_slug format: {repo_slug}. Expected 'owner/repo'",
            "error_code": "INVALID_REPO_SLUG",
        }

    # Validate target
    valid_targets = ["repo", "pr"]
    if target not in valid_targets and not target.startswith("src/"):
        return {
            "error": f"Invalid target: {target}. Must be 'repo', 'pr', or a file path",
            "error_code": "INVALID_TARGET",
        }

    # Initialize test recommendation service
    recommendation_service = RecommendationService()

    # Get uncovered regions (in real implementation, would fetch from provider)
    uncovered_regions: List[Dict[str, Any]] = []

    # Generate recommendations
    recommendations = recommendation_service.recommend_tests(
        uncovered_regions, max_recommendations=10
    )

    # Generate summary
    total_gaps = len(uncovered_regions)
    critical_count = sum(
        1 for rec in recommendations if rec.priority == "critical"
    )
    high_count = sum(1 for rec in recommendations if rec.priority == "high")

    summary = f"Test plan for {target}: {total_gaps} gaps identified, {critical_count} critical, {high_count} high priority"

    return {
        "target": target,
        "total_gaps": total_gaps,
        "recommendations": [
            {
                "file_path": rec.file_path,
                "start_line": rec.start_line,
                "end_line": rec.end_line,
                "region_type": rec.region_type,
                "test_types": rec.test_types,
                "scenarios": rec.scenarios,
                "priority": rec.priority,
                "rationale": rec.rationale,
            }
            for rec in recommendations
        ],
        "summary": summary,
    }
