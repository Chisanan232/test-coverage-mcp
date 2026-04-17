"""Template MCP Server - A Model Context Protocol server template.

This package provides a comprehensive, production-ready template for building MCP (Model Context Protocol)
servers with support for multiple transport modes and integrated webhook functionality. It demonstrates
best practices for infrastructure design, separation of concerns, and extensibility.

Architecture Overview
=====================

The project follows a modular architecture with clear separation of concerns:

1. **Domain Layer** (src/models/)
   - Core business logic models shared across the application
   - Can be used as communication objects everywhere in the project
   - Includes CLI configuration models and enums

2. **MCP Server Layer** (src/mcp/)
   - MCP protocol implementation with factory pattern
   - Transport-specific implementations (stdio, SSE, HTTP streaming)
   - MCP-specific models for tool inputs/outputs

3. **Web Server Layer** (src/web_server/)
   - FastAPI-based HTTP server for webhooks and health checks
   - Request/Response DTOs for API endpoints
   - CORS and middleware configuration

4. **Integration Layer** (src/integrate/)
   - Combines MCP and web server into a single application
   - Handles transport mounting and lifecycle management
   - Provides unified server creation and configuration

5. **Configuration Layer** (src/config.py)
   - Centralized settings management using pydantic-settings
   - Environment variable and .env file support
   - Singleton pattern for settings access

6. **Entry Point** (src/entry.py)
   - CLI argument parsing and server startup
   - Supports standalone and integrated modes
   - Logging configuration and error handling

Design Patterns
===============

1. **Singleton Factory Pattern**
   - BaseServerFactory provides abstract factory interface
   - MCPServerFactory, WebServerFactory, IntegratedServerFactory implement specific factories
   - Ensures single instance per factory type
   - Supports reset for testing

2. **Context Manager Pattern**
   - integrated_server_lifecycle() for resource management
   - Proper initialization and cleanup of server instances

3. **Enum-based Configuration**
   - MCPTransportType for type-safe transport selection
   - LogLevel for logging configuration
   - Prevents invalid configuration values

4. **Dependency Injection**
   - Factories manage dependencies between components
   - Settings injected through configuration objects
   - Reduces coupling between modules

Main Components
===============

- **mcp**: MCP server implementation with factory pattern
- **web_server**: FastAPI web server for HTTP transports and webhooks
- **integrate**: Integrated server combining MCP and webhook functionality
- **config**: Configuration management with pydantic-settings
- **models**: Pydantic models for CLI and DTO objects
- **entry**: Command-line entry point
- **_base.py**: Abstract base factory class for all server factories

Features
========

- Multiple transport support (stdio, SSE, HTTP streaming)
- Singleton factory pattern for server instances
- Integrated mode for combined MCP + webhook servers
- Comprehensive configuration management
- Type-safe CLI argument parsing
- Health check endpoints
- CORS support
- Development auto-reload
- Comprehensive logging and error handling

Quick Start
===========

.. code-block:: bash

    # Run with default stdio transport
    python -m src.entry

    # Run with SSE transport
    python -m src.entry --transport sse --port 8000

    # Run in integrated mode
    python -m src.entry --integrated --transport sse

    # Run with custom configuration
    python -m src.entry --transport http-streaming --port 9000 --log-level debug

Extending This Template
=======================

Child projects should follow this structure:

1. **Add domain models** in src/models/ for project-specific business logic
2. **Extend MCP tools** in src/mcp/ with custom tool implementations
3. **Add API endpoints** in src/web_server/ for project-specific webhooks
4. **Override configuration** in src/config.py for project-specific settings
5. **Customize entry point** in src/entry.py if needed for special initialization

Type System
===========

The package provides comprehensive type definitions for static type checking
and follows PEP 695 (Python 3.12+) using modern type statement syntax.
All modules use type hints for better IDE support and static analysis.
"""

from __future__ import annotations

# Re-export commonly used components for convenience
from .config import Settings, get_settings
from .models.cli import LogLevel, MCPTransportType, ServerConfig

__version__ = "0.0.0"
__author__ = "Template Author"
__email__ = "template@example.com"

__all__ = [
    "LogLevel",
    "MCPTransportType",
    "ServerConfig",
    "Settings",
    "get_settings",
]
