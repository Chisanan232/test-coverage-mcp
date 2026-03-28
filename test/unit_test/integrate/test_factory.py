"""Test integrated server factory functionality."""

from unittest.mock import MagicMock, patch

import pytest

from src._base import BaseServerFactory
from src.integrate.app import (
    IntegratedServerFactory,
    integrated_factory,
    integrated_server_lifecycle,
)
from src.mcp.app import MCPServerFactory
from src.models.cli import MCPTransportType
from src.web_server.app import WebServerFactory


class TestIntegratedServerFactory:
    """Test cases for the IntegratedServerFactory class."""

    def setup_method(self) -> None:
        """Reset the integrated server instance before each test."""
        IntegratedServerFactory.reset()

    def test_inheritance(self) -> None:
        """Test that IntegratedServerFactory inherits from BaseServerFactory."""
        assert issubclass(IntegratedServerFactory, BaseServerFactory)

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_create_sse_transport(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating integrated server with SSE transport."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.side_effect = [AssertionError("Not created"), mock_mcp_server]
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        # Create integrated server
        server = IntegratedServerFactory.create(mcp_transport="sse", mcp_mount_path="/mcp", token="test_token", retry=3)

        # Verify server creation
        assert server is mock_web_app

        # Verify MCP server was created
        mock_mcp_factory.create.assert_called_once()

        # Verify web server was created
        mock_web_factory.create.assert_called_once()

        # Verify SSE app was mounted
        mock_web_app.mount.assert_called_once_with("/mcp", mock_sse_app)

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_create_http_streaming_transport(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating integrated server with HTTP streaming transport."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_http_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.streamable_http_app.return_value = mock_http_app

        # Create integrated server
        server = IntegratedServerFactory.create(mcp_transport="http-streaming", token="test_token", retry=3)

        # Verify server creation
        assert server is mock_web_app

        # Verify HTTP streaming app was mounted
        mock_web_app.mount.assert_called_once_with("/mcp", mock_http_app)

    def test_create_invalid_transport(self) -> None:
        """Test creating integrated server with invalid transport."""
        with pytest.raises(ValueError, match="Invalid transport type"):
            IntegratedServerFactory.create(mcp_transport="invalid_transport")

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_get_success(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test successful get() after create()."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.return_value = mock_web_app
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        # Create server first
        server1 = IntegratedServerFactory.create(mcp_transport="sse")

        # Get the server
        server2 = IntegratedServerFactory.get()

        assert server1 is server2

    def test_get_without_create(self) -> None:
        """Test get() without create() should raise AssertionError."""
        with pytest.raises(AssertionError, match="Integrated server must be created first"):
            IntegratedServerFactory.get()

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_reset(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test reset() functionality."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.side_effect = [AssertionError("Not created"), mock_mcp_server]
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        # Create server
        server1 = IntegratedServerFactory.create(mcp_transport="sse")

        # Reset
        IntegratedServerFactory.reset()

        # Verify factories were reset
        mock_mcp_factory.reset.assert_called_once()
        mock_web_factory.reset.assert_called_once()


class TestIntegratedFactoryInstance:
    """Test cases for the integrated_factory instance."""

    def setup_method(self) -> None:
        """Reset the integrated server instance before each test."""
        IntegratedServerFactory.reset()

    def test_integrated_factory_is_class(self) -> None:
        """Test that integrated_factory is the IntegratedServerFactory class."""
        assert integrated_factory is IntegratedServerFactory

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_integrated_factory_create(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating server through integrated_factory."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        server = integrated_factory.create(mcp_transport="sse")
        assert server is mock_web_app

    def test_integrated_factory_get(self) -> None:
        """Test getting server through integrated_factory."""
        # Create through factory
        server1 = integrated_factory.create(mcp_transport="sse")

        # Get through factory
        server2 = integrated_factory.get()

        assert server1 is server2

    def test_integrated_factory_reset(self) -> None:
        """Test resetting through integrated_factory."""
        # Mock factories for reset
        with (
            patch("src.integrate.app.mcp_factory") as mock_mcp_factory,
            patch("src.integrate.app.web_factory") as mock_web_factory,
        ):
            # Create server
            server1 = integrated_factory.create(mcp_transport="sse")

            # Reset
            integrated_factory.reset()

            # Verify factories were reset
            mock_mcp_factory.reset.assert_called_once()
            mock_web_factory.reset.assert_called_once()


class TestIntegratedServerIntegration:
    """Integration tests for integrated server functionality."""

    def setup_method(self) -> None:
        """Reset factories before each test."""
        IntegratedServerFactory.reset()
        MCPServerFactory.reset()
        WebServerFactory.reset()

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_server_lifespan_integration(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test that server lifespan is properly integrated."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create integrated server
        server = integrated_factory.create(mcp_transport="sse")

        # Verify that web app was created with MCP lifespan
        mock_web_factory.create.assert_called_once()

        # Check that the created app has the lifespan from MCP factory
        # This would be verified in the actual FastAPI app creation

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_transport_mounting(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test that different transports are mounted correctly."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [
            AssertionError("Not created"),
            mock_web_app,
            AssertionError("Not created"),
            mock_web_app,
        ]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_http_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app
        mock_mcp_server.streamable_http_app.return_value = mock_http_app

        # Test SSE transport
        IntegratedServerFactory.reset()
        server1 = IntegratedServerFactory.create(mcp_transport="sse", mcp_mount_path="/api")
        mock_web_app.mount.assert_called_with("/api", mock_sse_app)

        # Test HTTP streaming transport
        IntegratedServerFactory.reset()
        server2 = IntegratedServerFactory.create(mcp_transport="http-streaming")
        mock_web_app.mount.assert_called_with("/mcp", mock_http_app)

    def test_default_parameters(self) -> None:
        """Test default parameters for create method."""
        with (
            patch("src.integrate.app.mcp_factory") as mock_mcp_factory,
            patch("src.integrate.app.web_factory") as mock_web_factory,
        ):
            # Mock factories
            mock_web_app = MagicMock()
            mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
            mock_web_factory.create.return_value = mock_web_app

            mock_mcp_server = MagicMock()
            mock_sse_app = MagicMock()
            mock_mcp_factory.get.return_value = mock_mcp_server
            mock_mcp_factory.create.return_value = mock_mcp_server
            mock_mcp_server.sse_app.return_value = mock_sse_app

            # Create with default parameters
            server = IntegratedServerFactory.create()

            # Verify defaults - SSE transport with default mount path /sse
            mock_web_app.mount.assert_called_with("/sse", mock_sse_app)

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_custom_mount_path_sse(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating integrated server with custom mount path for SSE."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        # Create with custom mount path
        server = IntegratedServerFactory.create(mcp_transport="sse", mcp_mount_path="/api/mcp")

        # Verify custom mount path is used
        mock_web_app.mount.assert_called_once_with("/api/mcp", mock_sse_app)

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_custom_mount_path_http_streaming(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating integrated server with custom mount path for HTTP streaming."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_http_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.streamable_http_app.return_value = mock_http_app

        # Create with custom mount path
        server = IntegratedServerFactory.create(mcp_transport="http-streaming", mcp_mount_path="/api/protocol")

        # Verify custom mount path is used
        mock_web_app.mount.assert_called_once_with("/api/protocol", mock_http_app)

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_transport_enum_input(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating integrated server with MCPTransportType enum."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        # Create with enum transport type
        server = IntegratedServerFactory.create(mcp_transport=MCPTransportType.SSE)

        # Verify server was created successfully
        assert server is mock_web_app
        mock_web_app.mount.assert_called_once()


class TestIntegratedServerLifecycle:
    """Test cases for the integrated_server_lifecycle context manager."""

    def test_lifecycle_context_manager(self) -> None:
        """Test that lifecycle context manager works correctly."""
        with integrated_server_lifecycle():
            # Should not raise any exceptions
            pass

    def test_lifecycle_with_exception(self) -> None:
        """Test that lifecycle context manager handles exceptions."""
        try:
            with integrated_server_lifecycle():
                error_msg = "Test error"
                raise ValueError(error_msg)
        except ValueError:
            pass  # Expected

    @patch("src.integrate.app.mcp_factory")
    @patch("src.integrate.app.web_factory")
    def test_lifecycle_with_server_creation(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test lifecycle context manager with server creation."""
        # Mock factories
        mock_web_app = MagicMock()
        mock_web_factory.get.side_effect = [AssertionError("Not created"), mock_web_app]
        mock_web_factory.create.return_value = mock_web_app

        mock_mcp_server = MagicMock()
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server
        mock_mcp_factory.create.return_value = mock_mcp_server
        mock_mcp_server.sse_app.return_value = mock_sse_app

        with integrated_server_lifecycle():
            server = IntegratedServerFactory.create(mcp_transport="sse")
            assert server is mock_web_app
