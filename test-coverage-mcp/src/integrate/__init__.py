"""Integration Layer - Combined MCP and Web Server.

This package contains the integrated server factory that combines the MCP server
and web server into a single FastAPI application. It handles transport mounting,
lifecycle management, and unified server configuration.

Purpose
=======

The integrate package provides:

1. **Integrated Server Factory** (app.py)
   - IntegratedServerFactory: Singleton factory for creating integrated servers
   - integrated_factory: Global factory instance for convenient access
   - integrated_server_lifecycle(): Context manager for resource management
   - Transport mounting and configuration

2. **Unified Server Management**
   - Combines MCP and web server functionality
   - Handles transport-specific mounting
   - Manages dependencies between components
   - Provides lifecycle management

3. **Configuration Integration**
   - Unified configuration for both servers
   - Transport selection and mounting
   - Custom mount path support
   - API token management

Architecture
============

The integrated server combines:

1. **MCP Server Integration**
   - Creates MCP server instance
   - Mounts transport-specific apps (SSE, HTTP streaming)
   - Configurable mount paths
   - Lifespan management

2. **Web Server Integration**
   - Creates FastAPI web server
   - Includes health check endpoints
   - CORS configuration
   - Webhook support

3. **Lifecycle Management**
   - integrated_server_lifecycle() context manager
   - Proper initialization and cleanup
   - Dependency management
   - Error handling

Design Principles
=================

1. **Composition Over Inheritance**
   - Combines existing factories instead of extending them
   - Manages dependencies between components
   - Clear separation of concerns

2. **Flexibility**
   - Supports multiple transport modes
   - Configurable mount paths
   - Custom initialization logic
   - Easy to extend

3. **Type Safety**
   - All methods have type hints
   - Enum-based transport selection
   - Configuration objects for validation

4. **Testing Support**
   - Reset functionality for test isolation
   - Context manager for resource management
   - Clear error messages for debugging

Files
=====

- **app.py**: IntegratedServerFactory and integration logic
  - IntegratedServerFactory: Main factory class
  - integrated_factory: Global factory instance
  - integrated_server_lifecycle(): Lifecycle context manager

Extension Guide for Child Projects
===================================

To extend this template with integrated server customization:

1. **Customize server creation**
   - Override create() method if needed
   - Add custom initialization logic
   - Configure transport-specific settings

2. **Add custom mount paths**
   - Configure MCP mount paths
   - Add custom sub-application mounts
   - Organize endpoints hierarchically

3. **Example structure for child projects**:

   .. code-block:: text

       src/integrate/
       ├── __init__.py
       ├── app.py                    # Factory (inherited)
       └── config.py                 # Project-specific configuration

4. **Example custom initialization**:

   .. code-block:: python

       from src.integrate import IntegratedServerFactory
       from fastapi import FastAPI

       class CustomIntegratedFactory(IntegratedServerFactory):
           @staticmethod
           def create(**kwargs) -> FastAPI:
               # Get base app from parent
               app = super().create(**kwargs)

               # Add custom initialization
               app.state.custom_data = {}

               # Add custom routers
               from src.web_server.routers import custom_router
               app.include_router(custom_router)

               return app

5. **Using custom factory**:

   .. code-block:: python

       from src.integrate import integrated_server_lifecycle

       # Use custom factory
       custom_factory = CustomIntegratedFactory

       # Create server with context manager
       with integrated_server_lifecycle():
           app = custom_factory.create(
               mcp_transport="sse",
               mcp_mount_path="/mcp"
           )
           # Use app

Usage Examples
==============

.. code-block:: python

    from src.integrate import IntegratedServerFactory, integrated_factory, integrated_server_lifecycle

    # Create integrated server instance (singleton)
    app = integrated_factory.create(
        mcp_transport="sse",
        mcp_mount_path="/mcp"
    )

    # Get existing server instance
    app = integrated_factory.get()

    # Use context manager for lifecycle management
    with integrated_server_lifecycle():
        app = integrated_factory.create()
        # Use app
        # Cleanup happens automatically

    # Run with uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Reset for testing
    integrated_factory.reset()

Transport Configuration
=======================

The integrated server supports multiple transport modes:

1. **SSE (Server-Sent Events)**
   - Unidirectional HTTP communication
   - Good for browser-based clients
   - Default mount path: /mcp/sse

2. **HTTP Streaming**
   - Bidirectional HTTP streaming
   - Robust HTTP-based communication
   - Default mount path: /mcp

Configuration
=============

Transport selection and configuration:

.. code-block:: python

    from src.integrate import integrated_factory
    from src.models import MCPTransportType

    # Create with SSE transport
    app = integrated_factory.create(
        mcp_transport=MCPTransportType.SSE,
        mcp_mount_path="/mcp/sse"
    )

    # Create with HTTP streaming
    app = integrated_factory.create(
        mcp_transport=MCPTransportType.HTTP_STREAMING,
        mcp_mount_path="/mcp"
    )

    # Create with custom token
    app = integrated_factory.create(
        token="custom-api-token",
        mcp_transport=MCPTransportType.SSE
    )

Server Structure
================

The integrated server provides:

.. code-block:: text

    /                           # Root endpoint
    ├── /health                 # Health check
    ├── /mcp                    # MCP transport (configurable)
    │   ├── /sse               # SSE transport (if configured)
    │   └── /http              # HTTP streaming (if configured)
    └── [custom endpoints]      # Project-specific endpoints

Lifecycle Management
====================

Use context manager for proper resource management:

.. code-block:: python

    from src.integrate import integrated_server_lifecycle, integrated_factory

    with integrated_server_lifecycle():
        try:
            app = integrated_factory.create()
            # Use app
        except Exception as e:
            # Handle errors
            pass
        # Cleanup happens automatically

Error Handling
==============

The factory provides clear error messages:

- "not allowed to create more than one instance": Singleton violation
- "Invalid transport type for integrated server": Unsupported transport
- "Please create a FastAPI instance first": Accessing before creation

Testing
=======

For testing, use the reset functionality:

.. code-block:: python

    from src.integrate import integrated_factory
    from fastapi.testclient import TestClient
    import pytest

    @pytest.fixture
    def client():
        integrated_factory.reset()
        app = integrated_factory.create()
        yield TestClient(app)
        integrated_factory.reset()

    def test_health_check(client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_mcp_sse_mounted(client):
        response = client.get("/mcp/sse")
        assert response.status_code in [200, 404]  # Depends on implementation

Dependency Management
=====================

The integrated server manages dependencies:

.. code-block:: python

    from src.integrate import integrated_factory
    from src.mcp import mcp_factory
    from src.web_server import web_factory

    # Create integrated server
    app = integrated_factory.create()

    # Access underlying factories
    mcp_server = mcp_factory.get()
    web_server = web_factory.get()

    # Both are available and configured
    assert mcp_server is not None
    assert web_server is not None

Best Practices
==============

1. **Use Context Manager**
   - Always use integrated_server_lifecycle() for proper cleanup
   - Ensures resources are properly released

2. **Configure Transport**
   - Choose appropriate transport for your use case
   - Configure mount paths consistently
   - Document transport selection

3. **Error Handling**
   - Handle factory creation errors
   - Provide meaningful error messages
   - Log configuration for debugging

4. **Testing**
   - Reset factory between tests
   - Use fixtures for test isolation
   - Mock external dependencies

5. **Monitoring**
   - Use health check endpoint
   - Monitor server status
   - Log important events
"""

from __future__ import annotations

from .app import IntegratedServerFactory, integrated_factory, integrated_server_lifecycle

__all__ = [
    "IntegratedServerFactory",
    "integrated_factory",
    "integrated_server_lifecycle",
]
