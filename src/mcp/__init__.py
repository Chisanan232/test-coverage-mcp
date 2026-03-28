"""MCP Server - Model Context Protocol server implementation.

This package contains the MCP server implementation with support for multiple
transport modes (stdio, SSE, HTTP streaming). It uses the singleton factory
pattern to manage server lifecycle and provides transport-specific implementations.

Purpose
=======

The MCP package provides:

1. **MCP Server Factory** (app.py)
   - MCPServerFactory: Singleton factory for creating FastMCP instances
   - mcp_factory: Global factory instance for convenient access
   - Transport implementations: stdio, SSE, HTTP streaming
   - Lifespan management for FastAPI integration

2. **MCP-Specific Models** (models/)
   - Input models for MCP tool parameters
   - Output models for MCP tool responses
   - Tool-specific data structures

Architecture
============

The MCP server is built on the FastMCP framework and provides:

1. **Factory Pattern Implementation**
   - MCPServerFactory extends BaseServerFactory
   - Enforces singleton pattern (only one instance allowed)
   - Provides create(), get(), and reset() methods
   - Supports testing through reset functionality

2. **Transport Abstraction**
   - sse_app(): Returns FastAPI app for SSE transport
   - streamable_http_app(): Returns FastAPI app for HTTP streaming
   - stdio transport: Direct MCP protocol over stdin/stdout
   - Configurable mount paths for HTTP transports

3. **Lifecycle Management**
   - lifespan() context manager for FastAPI integration
   - Proper initialization and cleanup of server resources
   - Session management for client connections

Design Principles
=================

1. **Single Responsibility**
   - Factory handles server creation and lifecycle
   - Transport implementations are separate from core logic
   - Models are focused on data validation

2. **Extensibility**
   - Child projects can add custom MCP tools
   - Models can be extended for project-specific needs
   - Transport implementations can be customized

3. **Type Safety**
   - All methods have type hints
   - Enums for transport type selection
   - Pydantic models for tool inputs/outputs

4. **Testing Support**
   - Reset functionality for test isolation
   - Mocking-friendly factory interface
   - Clear error messages for debugging

Sub-packages
============

- **models/**: MCP-specific data models
  - input/: Tool input parameter models
  - output/: Tool output response models

Files
=====

- **app.py**: MCPServerFactory and transport implementations
  - MCPServerFactory: Main factory class
  - mcp_factory: Global factory instance

Extension Guide for Child Projects
===================================

To extend this template with custom MCP tools:

1. **Add custom tools** to the MCP server
   - Define tool functions with proper type hints
   - Use input models from src/mcp/models/input/
   - Return output models from src/mcp/models/output/

2. **Create tool-specific models** in src/mcp/models/
   - Input models in src/mcp/models/input/
   - Output models in src/mcp/models/output/
   - Use Pydantic for validation

3. **Example structure for child projects**:

   .. code-block:: text

       src/mcp/
       ├── __init__.py
       ├── app.py                    # Factory (inherited)
       ├── tools/                    # Project-specific tools
       │   ├── __init__.py
       │   ├── calculator.py         # Custom tool: calculator
       │   └── database.py           # Custom tool: database
       └── models/
           ├── input/
           │   ├── __init__.py
           │   ├── calculator_input.py
           │   └── database_input.py
           └── output/
               ├── __init__.py
               ├── calculator_output.py
               └── database_output.py

4. **Example tool implementation**:

   .. code-block:: python

       from fastmcp import Tool
       from src.mcp.models.input.calculator_input import CalculatorInput
       from src.mcp.models.output.calculator_output import CalculatorOutput

       @mcp_factory.get().tool()
       def calculate(input: CalculatorInput) -> CalculatorOutput:
           \"\"\"Perform mathematical calculations.\"\"\"
           result = eval(input.expression)
           return CalculatorOutput(result=result)

5. **Register tools with the server**:

   .. code-block:: python

       from src.mcp.app import mcp_factory

       # Create server instance
       server = mcp_factory.create()

       # Tools are automatically registered through decorators
       # or can be registered manually

Usage Examples
==============

.. code-block:: python

    from src.mcp import MCPServerFactory, mcp_factory

    # Create MCP server instance (singleton)
    server = mcp_factory.create()

    # Get existing server instance
    server = mcp_factory.get()

    # Get transport-specific apps
    sse_app = server.sse_app()
    http_app = server.streamable_http_app()

    # Use lifespan context manager with FastAPI
    from fastapi import FastAPI
    app = FastAPI(lifespan=mcp_factory.lifespan())

    # Reset for testing
    mcp_factory.reset()

Transport Selection
===================

The MCP server supports three transport modes:

1. **Stdio** (default)
   - Direct MCP protocol over stdin/stdout
   - Best for local development and testing
   - No HTTP overhead

2. **SSE (Server-Sent Events)**
   - HTTP-based unidirectional communication
   - Good for browser-based clients
   - Configurable mount path (default: /mcp/sse)

3. **HTTP Streaming**
   - Bidirectional HTTP streaming
   - Best for robust HTTP-based communication
   - Configurable mount path (default: /mcp)

Configuration
=============

Transport selection is configured through:

1. **CLI arguments**: --transport sse|http-streaming|stdio
2. **Environment variables**: TRANSPORT=sse
3. **Configuration objects**: MCPTransportType enum

Error Handling
==============

The factory provides clear error messages:

- "not allowed to create more than one instance": Singleton violation
- "It must be created FastMCP first": Accessing server before creation
- "Please create a FastMCP instance first": Accessing lifespan before creation

Testing
=======

For testing, use the reset functionality:

.. code-block:: python

    from src.mcp import mcp_factory
    import pytest

    @pytest.fixture
    def mcp_server():
        mcp_factory.reset()
        server = mcp_factory.create()
        yield server
        mcp_factory.reset()
"""

from __future__ import annotations

from .app import MCPServerFactory, mcp_factory

__all__ = [
    "MCPServerFactory",
    "mcp_factory",
]
