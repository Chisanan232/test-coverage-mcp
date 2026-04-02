"""Test MCP server factory functionality."""

from unittest.mock import MagicMock, patch

import pytest

from src._base import BaseServerFactory
from src.mcp.app import MCPServerFactory, mcp_factory


class TestMCPServerFactory:
    """Test cases for the MCPServerFactory class."""

    def setup_method(self) -> None:
        """Reset the MCP server instance before each test."""
        MCPServerFactory.reset()

    def test_inheritance(self) -> None:
        """Test that MCPServerFactory inherits from BaseServerFactory."""
        assert issubclass(MCPServerFactory, BaseServerFactory)

    def test_create_singleton(self) -> None:
        """Test that create() enforces singleton pattern."""
        # Create first instance
        server1 = MCPServerFactory.create()
        assert server1 is not None
        assert server1.name == "TemplateMCPServer"

        # Try to create second instance - should raise AssertionError
        with pytest.raises(AssertionError, match="not allowed to create more than one instance"):
            MCPServerFactory.create()

    def test_get_success(self) -> None:
        """Test successful get() after create()."""
        # Create server first
        server = MCPServerFactory.create()

        # Get the server
        retrieved_server = MCPServerFactory.get()

        assert retrieved_server is server

    def test_get_without_create(self) -> None:
        """Test get() without create() should raise AssertionError."""
        with pytest.raises(AssertionError, match="It must be created FastMCP first"):
            MCPServerFactory.get()

    def test_reset(self) -> None:
        """Test reset() functionality."""
        # Create server
        server1 = MCPServerFactory.create()

        # Reset
        MCPServerFactory.reset()

        # Should be able to create again
        server2 = MCPServerFactory.create()
        assert server2 is not server1

    def test_lifespan_without_create(self) -> None:
        """Test lifespan() without create() should raise AssertionError."""
        with pytest.raises(AssertionError, match="Please create a FastMCP instance first"):
            MCPServerFactory.lifespan()

    def test_lifespan_success(self) -> None:
        """Test successful lifespan() after create()."""
        # Create server
        server = MCPServerFactory.create()

        # Get lifespan
        lifespan_func = MCPServerFactory.lifespan()

        # Should be callable
        assert callable(lifespan_func)


class TestMcpFactoryInstance:
    """Test cases for the mcp_factory instance."""

    def setup_method(self) -> None:
        """Reset the MCP server instance before each test."""
        MCPServerFactory.reset()

    def test_mcp_factory_is_class(self) -> None:
        """Test that mcp_factory is the MCPServerFactory class."""
        assert mcp_factory is MCPServerFactory

    def test_mcp_factory_create(self) -> None:
        """Test creating server through mcp_factory."""
        server = mcp_factory.create()
        assert server is not None
        assert server.name == "TemplateMCPServer"

    def test_mcp_factory_get(self) -> None:
        """Test getting server through mcp_factory."""
        # Create through factory
        server1 = mcp_factory.create()

        # Get through factory
        server2 = mcp_factory.get()

        assert server1 is server2

    def test_mcp_factory_reset(self) -> None:
        """Test resetting through mcp_factory."""
        # Create server
        server1 = mcp_factory.create()

        # Reset
        mcp_factory.reset()

        # Should be able to create again
        server2 = mcp_factory.create()
        assert server2 is not server1


class TestMcpServerIntegration:
    """Integration tests for MCP server functionality."""

    def setup_method(self) -> None:
        """Reset the MCP server instance before each test."""
        MCPServerFactory.reset()

    def test_server_tools_registration(self) -> None:
        """Test that tools can be registered on the server."""
        # Create server
        server = mcp_factory.create()

        # Register a test tool
        @server.tool("test_tool")
        async def test_tool(param: str) -> dict:
            return {"result": param}

        # Verify the tool was registered (this is a basic test)
        # In a real scenario, you might want to check the internal registry
        assert callable(test_tool)

    def test_server_transport_apps(self) -> None:
        """Test that transport apps can be created."""
        # Create server
        server = mcp_factory.create()

        # Create SSE app
        sse_app = server.sse_app()
        assert sse_app is not None

        # Create HTTP streaming app
        http_app = server.streamable_http_app()
        assert http_app is not None

    @patch("src.mcp.app.FastMCP.run")
    def test_server_stdio_run(self, mock_run: MagicMock) -> None:
        """Test running server with stdio transport."""
        # Create server
        server = mcp_factory.create()

        # Run with stdio transport
        server.run(transport="stdio")

        # Verify run was called
        mock_run.assert_called_once_with(transport="stdio")
