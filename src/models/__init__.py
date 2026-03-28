"""Domain Models - Core business logic models and shared data structures.

This package contains Pydantic models that represent the core business logic and
data structures of the application. These models serve as communication objects
throughout the entire project and can be used in any layer.

Purpose
=======

The models package provides:

1. **CLI Configuration Models** (cli.py)
   - ServerConfig: Configuration for server startup
   - LogLevel: Enumeration for logging levels
   - MCPTransportType: Enumeration for MCP transport types
   - Used for type-safe CLI argument parsing and validation

2. **Shared Data Structures**
   - Domain models that represent core business concepts
   - Can be used as communication objects across all layers
   - Validated using Pydantic for data integrity

Design Principles
=================

1. **Single Responsibility**
   - Each model represents a single concept or configuration
   - Models are focused on data validation and serialization

2. **Reusability**
   - Models can be used in MCP tools, API endpoints, and internal logic
   - Provides consistent data structures across the application

3. **Type Safety**
   - All models use type hints for static type checking
   - Enums prevent invalid configuration values
   - Pydantic validation ensures data integrity

4. **Extensibility**
   - Child projects can add domain-specific models
   - Models can be extended through inheritance
   - New enums can be added for project-specific values

Sub-packages
============

- **cli.py**: CLI argument models and enums
  - ServerConfig: Main server configuration model
  - LogLevel: Logging level enumeration
  - MCPTransportType: MCP transport type enumeration

Extension Guide for Child Projects
===================================

To extend this template with project-specific models:

1. **Add domain models** in this package for business logic
   - Create new model files for project-specific concepts
   - Use Pydantic for validation

2. **Create project-specific enums**
   - Extend LogLevel if you need custom logging levels
   - Add new enums for project-specific configurations

3. **Use models as communication objects**
   - Pass models between layers instead of raw dictionaries
   - Ensures type safety and validation throughout the application

4. **Example structure for child projects**:

   .. code-block:: text

       src/models/
       ├── __init__.py
       ├── cli.py                    # CLI configuration (inherited)
       ├── user.py                   # Project-specific: User model
       ├── task.py                   # Project-specific: Task model
       └── enums.py                  # Project-specific: Custom enums

5. **Example usage in child projects**:

   .. code-block:: python

       from src.models import ServerConfig
       from src.models.user import User
       from src.models.task import Task

       config = ServerConfig()
       user = User(name="John", email="john@example.com")
       task = Task(title="Implement feature", assignee=user)

Usage Examples
==============

.. code-block:: python

    from src.models import ServerConfig, LogLevel, MCPTransportType

    # Create configuration with type safety
    config = ServerConfig(
        host="0.0.0.0",
        port=8000,
        log_level=LogLevel.INFO,
        transport=MCPTransportType.SSE
    )

    # Access enum values
    print(config.log_level.value)  # "info"
    print(config.transport.value)  # "sse"

    # Use in API responses or MCP tools
    response = {
        "config": config.model_dump(),
        "status": "ready"
    }
"""

from __future__ import annotations

# Re-export commonly used models
from .cli import LogLevel, MCPTransportType, ServerConfig

__all__ = [
    "LogLevel",
    "MCPTransportType",
    "ServerConfig",
]
