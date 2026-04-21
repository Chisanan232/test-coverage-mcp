"""Tool registration for MCP server."""

from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.mcp_server.tools.commit_summary import (
    get_commit_coverage_summary,
)
from test_coverage_mcp.mcp_server.tools.comparison import (
    compare_coverage_between_refs,
)
from test_coverage_mcp.mcp_server.tools.coverage_providers import (
    describe_coverage_provider,
    list_coverage_providers,
)
from test_coverage_mcp.mcp_server.tools.metadata import TOOL_METADATA
from test_coverage_mcp.mcp_server.tools.repository_health import (
    get_repository_test_health,
)


def register_tools() -> None:
    """Register all tools with the MCP server.

    This function should be called after the MCP server is created
    to register all available tools.
    """
    try:
        mcp = mcp_factory.get()

        # Register list_coverage_providers
        metadata = TOOL_METADATA["list_coverage_providers"]
        mcp.tool(
            title=metadata["title"],
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"],
        )(list_coverage_providers)

        # Register describe_coverage_provider
        metadata = TOOL_METADATA["describe_coverage_provider"]
        mcp.tool(
            title=metadata["title"],
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"],
        )(describe_coverage_provider)

        # Register get_repository_test_health
        metadata = TOOL_METADATA["get_repository_test_health"]
        mcp.tool(
            title=metadata["title"],
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"],
        )(get_repository_test_health)

        # Register get_commit_coverage_summary
        metadata = TOOL_METADATA["get_commit_coverage_summary"]
        mcp.tool(
            title=metadata["title"],
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"],
        )(get_commit_coverage_summary)

        # Register compare_coverage_between_refs
        metadata = TOOL_METADATA["compare_coverage_between_refs"]
        mcp.tool(
            title=metadata["title"],
            name=metadata["name"],
            description=metadata["description"],
            annotations=metadata["annotations"],
        )(compare_coverage_between_refs)
    except AssertionError:
        pass
