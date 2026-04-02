"""MCP Tools - Custom MCP tool implementations.

This package is designed for child projects to implement custom MCP (Model Context Protocol) tools.
Child projects can add their own tools here to extend the MCP server functionality.

Purpose
=======

The tools package provides a structured way to organize custom MCP tools:

1. **Tool Organization**: Separate tools by functionality or domain
2. **Modular Design**: Each tool in its own module for maintainability
3. **Type Safety**: Use Pydantic models for input/output validation
4. **Reusability**: Tools can be easily shared and reused

Structure for Child Projects
============================

Child projects should organize their tools as follows:

.. code-block:: text

    src/mcp/tools/
    ├── __init__.py              # This file - package documentation
    ├── calculator.py            # Example: Mathematical calculation tools
    ├── database.py              # Example: Database operation tools
    ├── file_operations.py       # Example: File system tools
    ├── api_client.py            # Example: External API integration tools
    └── custom/                  # Optional: Sub-package for complex tools
        ├── __init__.py
        ├── advanced_tool.py
        └── utils.py

Tool Implementation Guidelines
=============================

1. **Tool Function Structure**
   - Use proper type hints for all parameters and return values
   - Use input models from src/mcp/models/input/ for validation
   - Return output models from src/mcp/models/output/
   - Include comprehensive docstrings with examples

2. **Error Handling**
   - Use try-except blocks for external operations
   - Return meaningful error messages in output models
   - Log errors appropriately for debugging

3. **Performance Considerations**
   - Avoid long-running operations without timeout
   - Use async/await for I/O operations when possible
   - Cache results when appropriate

Example Tool Implementation
============================

Here's a complete example of how to implement a custom MCP tool:

.. code-block:: python

    \"\"\"Calculator tool for mathematical operations.\"\"\"

    from typing import Union
    from fastmcp import Tool
    from src.mcp.models.input.calculator_input import CalculatorInput
    from src.mcp.models.output.calculator_output import CalculatorOutput, CalculatorError

    @mcp_factory.get().tool()
    def calculate(input: CalculatorInput) -> Union[CalculatorOutput, CalculatorError]:
        \"\"\"Perform mathematical calculations safely.

Args:
            input: CalculatorInput with expression and precision

Returns:
            CalculatorOutput with result or CalculatorError if calculation fails

Example:
            >>> calculate(CalculatorInput(expression="2 + 2", precision=2))
            CalculatorOutput(result=4.0, expression="2 + 2", precision=2)
        \"\"\"
        try:
            # Safe evaluation (avoid eval() for security)
            result = safe_eval(input.expression)
            rounded_result = round(result, input.precision)

            return CalculatorOutput(
                result=rounded_result,
                expression=input.expression,
                precision=input.precision
            )
        except Exception as e:
            return CalculatorError(
                expression=input.expression,
                error=str(e),
                error_type="CalculationError"
            )

Integration with MCP Server
===========================

Tools are automatically registered with the MCP server through decorators:

.. code-block:: python

    from src.mcp.app import mcp_factory

    # Tools are registered when the module is imported
    # Import your tools in src/mcp/tools/__init__.py
    from .calculator import calculate
    from .database import query_database

    # Tools are now available in the MCP server

Testing Custom Tools
====================

Test your tools with proper fixtures:

.. code-block:: python

    import pytest
    from src.mcp.tools.calculator import calculate
    from src.mcp.models.input.calculator_input import CalculatorInput

    def test_calculate_addition():
        \"\"\"Test basic addition.\"\"\"
        input_data = CalculatorInput(expression="2 + 2", precision=2)
        result = calculate(input_data)

        assert result.result == 4.0
        assert result.expression == "2 + 2"
        assert result.precision == 2

    def test_calculate_invalid_expression():
        \"\"\"Test error handling for invalid expressions.\"\"\"
        input_data = CalculatorInput(expression="invalid", precision=2)
        result = calculate(input_data)

        assert hasattr(result, 'error')
        assert result.error_type == "CalculationError"

Best Practices
==============

1. **Security**: Never use eval() or exec() with user input
2. **Validation**: Always validate input through Pydantic models
3. **Error Handling**: Provide clear, actionable error messages
4. **Documentation**: Include examples in docstrings
5. **Testing**: Write comprehensive tests for all tools
6. **Performance**: Consider async operations for I/O-bound tasks
7. **Logging**: Add appropriate logging for debugging
8. **Type Safety**: Use strict type hints throughout

Common Tool Patterns
=====================

1. **Data Processing Tools**
   - Transform, filter, or analyze data
   - Return structured results with metadata

2. **External API Tools**
   - Integrate with third-party services
   - Handle authentication and rate limiting
   - Cache responses when appropriate

3. **Database Tools**
   - Query, insert, update, or delete data
   - Use connection pooling for performance
   - Handle database errors gracefully

4. **File System Tools**
   - Read, write, or manipulate files
   - Validate file paths and permissions
   - Handle file encoding issues

5. **Calculation Tools**
   - Perform mathematical or statistical operations
   - Handle precision and rounding correctly
   - Validate mathematical expressions safely

Advanced Features
=================

1. **Async Tools**: Use async/await for I/O operations
2. **Streaming**: Support streaming responses for large datasets
3. **Caching**: Implement caching for expensive operations
4. **Batching**: Process multiple items in a single call
5. **Validation**: Custom validation logic beyond Pydantic
6. **Authentication**: Require API keys or other credentials

Dependencies
============

Common dependencies for MCP tools:

.. code-block:: toml

    [project.optional-dependencies]
    tools = [
        "requests",      # HTTP client for API tools
        "sqlalchemy",   # Database ORM
        "pandas",       # Data processing
        "numpy",        # Numerical computations
        "aiohttp",      # Async HTTP client
        "redis",        # Caching
    ]

Import this package in your main MCP application:

.. code-block:: python

    # Import all tools to register them with the MCP server
    from src.mcp.tools import *

    # Or import specific tools
    from src.mcp.tools.calculator import calculate
    from src.mcp.tools.database import query_database

"""

from __future__ import annotations

# Import all tool modules to register them with the MCP server
# Child projects should add their tool imports here:

# Example imports (uncomment and modify for your tools):
# from .calculator import calculate
# from .database import query_database
# from .file_operations import read_file, write_file
# from .api_client import call_external_api

__all__ = [
    # Add your tool functions here
    # "calculate",
    # "query_database",
    # "read_file",
    # "write_file",
    # "call_external_api",
]

# Package metadata for tool discovery
__tool_package__ = True
__tool_version__ = "1.0.0"
__supported_features__ = [
    "synchronous_tools",
    "asynchronous_tools",
    "error_handling",
    "input_validation",
    "output_validation",
]
