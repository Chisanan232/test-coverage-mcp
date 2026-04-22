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
        mcp.tool()(list_coverage_providers)
        mcp.tool()(describe_coverage_provider)
        mcp.tool()(get_repository_test_health)
        mcp.tool()(get_commit_coverage_summary)
        mcp.tool()(compare_coverage_between_refs)
    except AssertionError:
        pass
