"""Tool registration for MCP server.

This module imports all tool modules to trigger their decorator registration.
Tools are registered at module import time using @mcp.tool() decorators
with lazy MCP initialization via get_or_create().
"""

# Import all tool modules to trigger decorator registration
from test_coverage_mcp.mcp_server.tools.commit_summary import (  # noqa: F401
    get_commit_coverage_summary,
)
from test_coverage_mcp.mcp_server.tools.comparison import (  # noqa: F401
    compare_coverage_between_refs,
)
from test_coverage_mcp.mcp_server.tools.coverage_providers import (  # noqa: F401
    describe_coverage_provider,
    list_coverage_providers,
)
from test_coverage_mcp.mcp_server.tools.repository_health import (  # noqa: F401
    get_repository_test_health,
)


def register_tools() -> None:
    """Register all tools with the MCP server.

    This function is a no-op since tools are now registered at module import time
    via @mcp.tool() decorators. It's kept for backward compatibility.
    """
    pass
