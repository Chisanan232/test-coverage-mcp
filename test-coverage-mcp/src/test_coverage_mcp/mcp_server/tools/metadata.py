"""Tool metadata and decorator infrastructure for MCP server."""

from typing import Any, Dict

TOOL_METADATA: Dict[str, Dict[str, Any]] = {
    "list_coverage_providers": {
        "title": "List Coverage Providers",
        "name": "coverage.providers.list",
        "description": "Discover all available coverage providers with their capabilities and health status",
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
    "describe_coverage_provider": {
        "title": "Describe Coverage Provider",
        "name": "coverage.providers.describe",
        "description": "Get detailed information about a specific coverage provider including capabilities and health status",
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
    "get_repository_test_health": {
        "title": "Get Repository Test Health",
        "name": "coverage.repository.health",
        "description": "Analyze repository test health including coverage metrics, test count, and risk assessment",
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
    "get_commit_coverage_summary": {
        "title": "Get Commit Coverage Summary",
        "name": "coverage.commit.summary",
        "description": "Get coverage summary for a specific commit including coverage change and affected files",
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
    "compare_coverage_between_refs": {
        "title": "Compare Coverage Between Refs",
        "name": "coverage.comparison.refs",
        "description": "Compare coverage metrics between two git references (branches, tags, commits)",
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": True,
        },
    },
}
