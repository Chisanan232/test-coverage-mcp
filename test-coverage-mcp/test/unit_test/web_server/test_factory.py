"""Test web server factory functionality."""

from unittest.mock import MagicMock, patch

import pytest

from src._base import BaseServerFactory
from src.mcp.app import MCPServerFactory
from src.models.cli import MCPTransportType
from src.web_server.app import WebServerFactory, web_factory


class TestWebServerFactory:
    """Test cases for the WebServerFactory class."""

    def setup_method(self) -> None:
        """Reset the web server instance before each test."""
        WebServerFactory.reset()

    def test_inheritance(self) -> None:
        """Test that WebServerFactory inherits from BaseServerFactory."""
        assert issubclass(WebServerFactory, BaseServerFactory)

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_create_singleton(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test that create() enforces singleton pattern."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create first instance
        server1 = WebServerFactory.create()
        assert server1 is not None
        assert server1.title == "Template MCP Server"

        # Try to create second instance - should raise AssertionError
        with pytest.raises(AssertionError, match="not allowed to create more than one instance"):
            WebServerFactory.create()

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_get_success(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test successful get() after create()."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create server first
        server = WebServerFactory.create()

        # Get the server
        retrieved_server = WebServerFactory.get()

        assert retrieved_server is server

    def test_get_without_create(self) -> None:
        """Test get() without create() should raise AssertionError."""
        with pytest.raises(AssertionError, match="It must be created web server first"):
            WebServerFactory.get()

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_reset(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test reset() functionality."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create server
        server1 = WebServerFactory.create()

        # Reset
        WebServerFactory.reset()

        # Should be able to create again
        server2 = WebServerFactory.create()
        assert server2 is not server1


class TestWebFactoryInstance:
    """Test cases for the web_factory instance."""

    def setup_method(self) -> None:
        """Reset the web server instance before each test."""
        WebServerFactory.reset()

    def test_web_factory_is_class(self) -> None:
        """Test that web_factory is the WebServerFactory class."""
        assert web_factory is WebServerFactory

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_web_factory_create(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test creating server through web_factory."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        server = web_factory.create()
        assert server is not None
        assert server.title == "Template MCP Server"

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_web_factory_get(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test getting server through web_factory."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create through factory
        server1 = web_factory.create()

        # Get through factory
        server2 = web_factory.get()

        assert server1 is server2

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_web_factory_reset(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test resetting through web_factory."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create server
        server1 = web_factory.create()

        # Reset
        web_factory.reset()

        # Should be able to create again
        server2 = web_factory.create()
        assert server2 is not server1


class TestWebService:
    """Test cases for web service functionality."""

    def setup_method(self) -> None:
        """Reset factories before each test."""
        WebServerFactory.reset()
        MCPServerFactory.reset()

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.web_factory")
    def test_mount_service_sse(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test mounting SSE service."""
        # Mock factories
        mock_app = MagicMock()
        mock_web_factory.get.return_value = mock_app
        mock_sse_app = MagicMock()
        mock_mcp_factory.get.return_value.sse_app.return_value = mock_sse_app

        # Mount SSE service
        from src.web_server.app import mount_service

        mount_service(MCPTransportType.SSE)

        # Verify mounting
        mock_app.mount.assert_called_once_with("/sse", mock_sse_app)

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.web_factory")
    def test_mount_service_http_streaming(self, mock_web_factory: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test mounting HTTP streaming service."""
        # Mock factories
        mock_app = MagicMock()
        mock_web_factory.get.return_value = mock_app
        mock_http_app = MagicMock()
        mock_mcp_factory.get.return_value.streamable_http_app.return_value = mock_http_app

        # Mount HTTP streaming service
        from src.web_server.app import mount_service

        mount_service(MCPTransportType.HTTP_STREAMING)

        # Verify mounting
        mock_app.mount.assert_called_once_with("/mcp", mock_http_app)

    def test_mount_service_invalid_transport(self) -> None:
        """Test mounting service with invalid transport."""
        with pytest.raises(ValueError, match="Unknown transport protocol"):
            from src.web_server.app import mount_service

            mount_service("invalid_transport")  # This will raise ValueError for invalid transport

    @patch("src.web_server.app.mount_service")
    @patch("src.web_server.app.web_factory")
    def test_create_app(self, mock_web_factory: MagicMock, mock_mount_service: MagicMock) -> None:
        """Test create_app function."""
        # Mock web factory
        mock_app = MagicMock()
        mock_web_factory.get.return_value = mock_app

        # Import and test create_app
        from src.models.cli import MCPTransportType, ServerConfig
        from src.web_server.app import create_app

        # Test with default config
        app = create_app()
        assert app is mock_app

        # Test with custom config
        config = ServerConfig(transport=MCPTransportType.HTTP_STREAMING)
        app = create_app(config)
        assert app is mock_app

        # Verify mount_service was called
        assert mock_mount_service.call_count == 2


class TestWebServerIntegration:
    """Integration tests for web server functionality."""

    def setup_method(self) -> None:
        """Reset factories before each test."""
        WebServerFactory.reset()
        MCPServerFactory.reset()

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_health_check_endpoint(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test health check endpoint."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["*"]
        mock_settings.cors_allow_credentials = True
        mock_settings.cors_allow_methods = ["*"]
        mock_settings.cors_allow_headers = ["*"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create server
        server = web_factory.create()

        # Check that health check route is registered
        # This is a basic test - in a real scenario you might want to test the actual endpoint
        routes = [route.path for route in server.routes]
        assert "/health" in routes

    @patch("src.web_server.app.mcp_factory")
    @patch("src.web_server.app.get_settings")
    def test_cors_configuration(self, mock_get_settings: MagicMock, mock_mcp_factory: MagicMock) -> None:
        """Test CORS configuration."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.cors_allow_origins = ["https://example.com"]
        mock_settings.cors_allow_credentials = False
        mock_settings.cors_allow_methods = ["GET", "POST"]
        mock_settings.cors_allow_headers = ["Content-Type"]
        mock_get_settings.return_value = mock_settings

        # Mock MCP factory lifespan
        mock_mcp_factory.lifespan.return_value = MagicMock()

        # Create server
        server = web_factory.create()

        # Check that CORS middleware is added
        # This is a basic test - in a real scenario you might want to verify the actual configuration
        from starlette.middleware.cors import CORSMiddleware

        middleware_types = [middleware.cls for middleware in server.user_middleware]
        assert CORSMiddleware in middleware_types
