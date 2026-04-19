"""Tool registration for MCP server."""

from test_coverage_mcp.mcp_server.app import mcp_factory
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
    except AssertionError:
        pass
