"""FastAPI Web Server for MCP Template.

Design:
- Provides a singleton FastAPI app via `WebServerFactory`.
- Mounts the Model Context Protocol (MCP) server under either SSE or HTTP streaming
  transports using `mount_service()`.
- Integrates webhook ingress under `/webhook`.
- Adds a `/health` endpoint for liveness checks.

Transports:
- SSE: mounted at `/sse`
- HTTP streaming: mounted at `/mcp`

High-level flow (sequence):
    Client → FastAPI → (SSE|HTTP-streaming) → MCP Server → External API
                                 ↘
                                  Webhooks → /webhook → EventSink (local|mq) → Handlers

 Architecture (Mermaid):
 ```mermaid
 sequenceDiagram
     autonumber
     participant Client
     participant FastAPI as FastAPI App
     participant MCP as MCP Server
     participant External as External API
     participant WH as Webhook Router
     participant Sink as EventSink
     participant H as Handlers

     Client->>FastAPI: HTTP (SSE / HTTP-streaming)
     FastAPI->>MCP: Forward protocol traffic
     MCP->>External: REST API calls
     External-->>MCP: API responses
     MCP-->>FastAPI: Tool results
     FastAPI-->>Client: Responses

     Note over External,WH: Out-of-band webhooks
     External->>WH: POST /webhook/external
     WH->>Sink: Normalize and dispatch
     Sink->>H: Execute registered handlers
 ```
"""

from __future__ import annotations

from typing import TypedDict, Unpack

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .._base import BaseServerFactory
from ..config import get_settings
from ..mcp_server.app import mcp_factory
from ..models.cli import MCPTransportType, ServerConfig
from .routers import health_check_router

_WEB_SERVER_INSTANCE: FastAPI | None = None


class WebServerKwargs(TypedDict, total=False):
    """TypedDict for WebServerFactory.create() keyword arguments."""

    pass


class WebServerFactory(BaseServerFactory[FastAPI]):
    """Factory for creating and managing FastAPI web server instances.

    This factory implements the singleton pattern to ensure only one
    FastAPI server instance exists throughout the application lifecycle.
    It provides methods for creating, retrieving, and resetting the server.

    The server is configured with:
    - CORS middleware for cross-origin requests
    - Webhook router for event handling
    - MCP server mounting for protocol support
    - Health check endpoint

    Usage Examples:
        # Python - Create and use the web server
        from test_coverage_mcp.web_server.app import WebServerFactory

        server = WebServerFactory.create()
        # Server is now running with MCP endpoints

        # Get existing server
        server = WebServerFactory.get()

        # Reset for testing
        WebServerFactory.reset()
    """

    @staticmethod
    def create(**kwargs: Unpack[WebServerKwargs]) -> FastAPI:
        """Create and configure the web API server singleton instance.

        This method creates a new FastAPI application with the following features:
        - CORS middleware configured for all origins (adjust for production)
        - Webhook router mounted
        - MCP server lifespan management
        - Comprehensive error handling

        Args:
            **kwargs: Additional arguments (unused, but included for base class compatibility)

        Returns:
            Configured FastAPI server instance

        Raises:
            AssertionError: If a server instance already exists

        Usage Examples:
            # Python - Create the web server
            server = WebServerFactory.create()

        """
        # Create a new FastAPI instance
        global _WEB_SERVER_INSTANCE
        assert _WEB_SERVER_INSTANCE is None, "It is not allowed to create more than one instance of web server."

        # Create FastAPI app
        _WEB_SERVER_INSTANCE = FastAPI(
            title="Template MCP Server",
            description="A FastAPI web server that hosts a template MCP server for interacting with external APIs",
            version="0.1.0",
            lifespan=mcp_factory.lifespan(),
        )

        # Get settings for CORS configuration
        settings = get_settings()

        # Configure CORS
        _WEB_SERVER_INSTANCE.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
        )

        # Include health check router
        _WEB_SERVER_INSTANCE.include_router(health_check_router)

        return _WEB_SERVER_INSTANCE

    @staticmethod
    def get() -> FastAPI:
        """Get the existing FastAPI web server singleton instance.

        Returns the previously created server instance. Raises an assertion
        error if no server has been created yet. Use create() to initialize
        the server before calling this method.

        Returns:
            Configured FastAPI server instance

        Raises:
            AssertionError: If the server has not been created yet

        Usage Examples:
            # Python - Get existing server
            server = WebServerFactory.get()
            # Server is ready to use

        """
        assert _WEB_SERVER_INSTANCE is not None, "It must be created web server first."
        return _WEB_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """Reset the singleton instance to None.

        This method clears the cached server instance, allowing a new one
        to be created. Primarily used for testing and in scenarios where
        you need to reinitialize the server with different configuration.

        Usage Examples:
            # Python - Reset for testing
            WebServerFactory.reset()
            server = WebServerFactory.create()
        """
        global _WEB_SERVER_INSTANCE
        _WEB_SERVER_INSTANCE = None


web_factory = WebServerFactory


def mount_service(transport: str | MCPTransportType = "sse") -> None:
    """Mount the MCP service into the FastAPI web server.

    This function mounts the Model Context Protocol (MCP) server as a sub-application
    on the FastAPI server, enabling MCP clients to communicate with external APIs
    through the specified transport protocol.

    The MCP server can be accessed at:
    - SSE transport: http://host:port/sse
    - HTTP Streaming transport: http://host:port/mcp

    Args:
        transport: The transport protocol to use for MCP (sse or http-streaming).
                  Defaults to MCPTransportType.SSE.

    Raises:
        ValueError: If an unknown transport protocol is specified

    Usage Examples:
        # Python - Mount with SSE transport (default)
        mount_service(transport="sse")

        # Python - Mount with HTTP streaming transport
        mount_service(transport="http-streaming")

        # curl - Access MCP via SSE
        curl http://localhost:8000/sse

        # curl - Access MCP via HTTP streaming
        curl http://localhost:8000/mcp

    """
    # Convert string to enum if needed
    if isinstance(transport, str):
        try:
            transport_enum = MCPTransportType(transport)
        except ValueError as err:
            error_msg = f"Unknown transport protocol: {transport}"
            raise ValueError(error_msg) from err
    else:
        transport_enum = transport

    match transport_enum:
        case MCPTransportType.SSE:
            web_factory.get().mount("/sse", mcp_factory.get().sse_app())
        case MCPTransportType.HTTP_STREAMING:
            web_factory.get().mount("/mcp", mcp_factory.get().streamable_http_app())


def create_app(
    server_config: ServerConfig | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application with MCP server mounted.

    This function is the main entry point for initializing the Template MCP server.
    It performs the following initialization steps:

    1. Mounts the MCP server with the specified transport protocol
    2. Registers user-defined event handlers (if any)
    3. Configures health check endpoint
    4. Applies CORS and security settings

    The resulting FastAPI application is ready to:
    - Accept MCP protocol requests via SSE or HTTP streaming
    - Handle webhook events
    - Provide health check status
    - Serve API documentation at /docs and /redoc

    Args:
        server_config: Optional ServerConfig instance containing:
            - env_file: Path to .env file for environment variables
            - token: API token (overrides env variable if provided)
            - transport: MCP transport protocol (sse or http-streaming)
            - host: Server host address
            - port: Server port number
            - log_level: Logging level
            - reload: Enable auto-reload for development

    Returns:
        Fully configured FastAPI application instance

    Raises:
        ValueError: If an invalid transport protocol is specified

    Usage Examples:
        # Python - Create app with default configuration
        app = create_app()

        # Python - Create app with custom configuration
        from test_coverage_mcp.models.cli import ServerConfig
        config = ServerConfig(
            host="0.0.0.0",
            port=8080,
            transport="sse",
            log_level="debug"
        )
        app = create_app(server_config=config)

        # CLI - Run with custom settings
        python -m src.entry --host 0.0.0.0 --port 8080 --transport sse

    """
    # Create the web server if it doesn't exist
    try:
        app = web_factory.get()
    except AssertionError:
        app = web_factory.create()

    # Determine transport from server_config or use default
    transport = MCPTransportType.SSE
    if server_config:
        transport = server_config.transport

    # Mount the MCP service with the specified transport
    mount_service(transport)

    return app
