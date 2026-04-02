"""MCP Tool Output Models - Response definitions for MCP tools.

This package contains Pydantic models that define the output/response structures for MCP tools.
Each tool has a corresponding output model that validates and documents the returned data
and its types.

Purpose
=======

The output models package provides:

1. **Tool Response Validation**
   - Pydantic models for tool output/response data
   - Type validation and conversion
   - Consistent response formats
   - Clear error handling

2. **Documentation**
   - Field descriptions for IDE autocompletion
   - Type hints for static analysis
   - Examples in docstrings
   - Response format documentation

3. **Type Safety**
   - Ensures type-safe tool responses
   - Validates response data before serialization
   - Enables IDE support and autocompletion
   - Supports static type checking

Design Principles
=================

1. **Tool-Specific Models**
   - Each tool has its own output model
   - Models are named consistently: [tool_name]_output.py
   - Clear relationship between tool and model

2. **Comprehensive Validation**
   - Use Pydantic validators for complex validation
   - Add constraints where applicable
   - Provide helpful error messages
   - Support custom validation logic

3. **Clear Documentation**
   - Add docstrings to model classes
   - Add descriptions to all fields
   - Include examples in docstrings
   - Document response formats

4. **Flexibility**
   - Support optional response fields
   - Support multiple response types
   - Support nested models
   - Support error responses

File Organization
=================

.. code-block:: text

    src/mcp/models/output/
    ├── __init__.py
    ├── [tool_name]_output.py
    ├── [tool_name2]_output.py
    └── ...

Extension Guide for Child Projects
===================================

To add custom MCP tool output models:

1. **Create output model file**
   - Create [tool_name]_output.py in this directory
   - Define Pydantic model for tool response
   - Add comprehensive field documentation

2. **Export in __init__.py**
   - Import model in __init__.py
   - Add to __all__ list
   - Make available for import

3. **Example output model**:

   .. code-block:: python

       # src/mcp/models/output/calculator_output.py
       from pydantic import BaseModel, Field

       class CalculatorOutput(BaseModel):
           \"\"\"Output from calculator tool.\"\"\"
           result: float = Field(
               description="Calculation result",
               examples=[4.0, 16.0, 1.0]
           )
           expression: str = Field(
               description="Original expression evaluated"
           )
           error: str | None = Field(
               default=None,
               description="Error message if calculation failed"
           )

4. **Using output models in tools**:

   .. code-block:: python

       from fastmcp import Tool
       from src.mcp.models.input.calculator_input import CalculatorInput
       from src.mcp.models.output.calculator_output import CalculatorOutput

       @mcp_factory.get().tool()
       def calculate(input: CalculatorInput) -> CalculatorOutput:
           \"\"\"Perform mathematical calculations.\"\"\"
           try:
               result = eval(input.expression)
               return CalculatorOutput(
                   result=round(result, input.precision),
                   expression=input.expression
               )
           except Exception as e:
               return CalculatorOutput(
                   result=0,
                   expression=input.expression,
                   error=str(e)
               )

Best Practices
==============

1. **Field Naming**
   - Use descriptive names
   - Follow snake_case convention
   - Avoid abbreviations
   - Be consistent across tools

2. **Error Handling**
   - Include error field for failures
   - Provide error messages
   - Support partial responses
   - Document error conditions

3. **Documentation**
   - Add docstrings to classes
   - Add descriptions to fields
   - Include examples
   - Document response formats

4. **Type Hints**
   - Use proper type hints
   - Use Union for multiple types
   - Use Optional for nullable fields
   - Use Literal for fixed values

5. **Consistency**
   - Consistent response structure
   - Consistent field naming
   - Consistent error handling
   - Consistent data formats

Common Patterns
===============

1. **Simple Response**:

   .. code-block:: python

       class SimpleOutput(BaseModel):
           result: str = Field(description="Result of operation")
           timestamp: datetime = Field(description="Operation timestamp")

2. **Response with Error Handling**:

   .. code-block:: python

       class ResponseWithError(BaseModel):
           success: bool = Field(description="Whether operation succeeded")
           data: dict | None = Field(default=None, description="Response data")
           error: str | None = Field(default=None, description="Error message")

3. **Structured Response**:

   .. code-block:: python

       class Item(BaseModel):
           id: str = Field(description="Item ID")
           name: str = Field(description="Item name")
           value: float = Field(description="Item value")

       class StructuredOutput(BaseModel):
           items: list[Item] = Field(description="List of items")
           total: int = Field(description="Total count")
           page: int = Field(description="Current page")

4. **Metadata Response**:

   .. code-block:: python

       class MetadataOutput(BaseModel):
           data: str = Field(description="Main response data")
           metadata: dict = Field(description="Response metadata")
           processing_time_ms: float = Field(description="Processing time")

5. **Streaming Response**:

   .. code-block:: python

       class StreamingOutput(BaseModel):
           chunk: str = Field(description="Data chunk")
           is_final: bool = Field(description="Whether this is final chunk")
           chunk_index: int = Field(description="Chunk index")

Testing
=======

Test output models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.mcp.models.output.calculator_output import CalculatorOutput

    def test_calculator_output_valid():
        output = CalculatorOutput(
            result=4.0,
            expression="2 + 2"
        )
        assert output.result == 4.0
        assert output.error is None

    def test_calculator_output_with_error():
        output = CalculatorOutput(
            result=0,
            expression="invalid",
            error="Invalid expression"
        )
        assert output.error is not None

    def test_calculator_output_invalid_type():
        with pytest.raises(ValidationError):
            CalculatorOutput(result="not a number", expression="2 + 2")

Serialization
=============

Output models support JSON serialization for MCP protocol:

.. code-block:: python

    from src.mcp.models.output.calculator_output import CalculatorOutput

    # Create output
    output = CalculatorOutput(result=4.0, expression="2 + 2")

    # Serialize to JSON
    json_str = output.model_dump_json()

    # Parse from JSON
    parsed = CalculatorOutput.model_validate_json(json_str)

    # Serialize to dict
    dict_data = output.model_dump()

Error Response Pattern
======================

Consistent error handling across tools:

.. code-block:: python

    class ErrorOutput(BaseModel):
        \"\"\"Generic error response.\"\"\"
        success: bool = Field(default=False, description="Operation failed")
        error: str = Field(description="Error message")
        error_code: str | None = Field(default=None, description="Error code")
        details: dict | None = Field(default=None, description="Error details")

    # Usage in tool
    try:
        result = perform_operation()
        return SuccessOutput(data=result)
    except SpecificError as e:
        return ErrorOutput(
            error=str(e),
            error_code="SPECIFIC_ERROR",
            details={"cause": e.cause}
        )

Pagination Pattern
==================

For tools returning multiple items:

.. code-block:: python

    from typing import Generic, TypeVar

    T = TypeVar("T")

    class PaginatedOutput(BaseModel, Generic[T]):
        \"\"\"Paginated response.\"\"\"
        items: list[T] = Field(description="List of items")
        total: int = Field(description="Total count")
        page: int = Field(description="Current page")
        page_size: int = Field(description="Items per page")
        total_pages: int = Field(description="Total pages")
        has_next: bool = Field(description="Has next page")

Migration Guide
===============

When updating output models:

1. **Adding Optional Fields**
   - Add with default value
   - Backward compatible
   - Existing clients continue to work

2. **Removing Fields**
   - Mark as deprecated first
   - Provide migration path
   - Remove in next major version

3. **Changing Field Types**
   - Use Union types for compatibility
   - Provide migration examples
   - Document breaking changes

4. **Adding Required Fields**
   - Breaking change
   - Provide default value
   - Document migration path
   - Consider major version bump

Validation Examples
===================

Custom validation for output models:

.. code-block:: python

    from pydantic import BaseModel, Field, field_validator

    class ValidatedOutput(BaseModel):
        value: float = Field(description="Output value")
        min_value: float = Field(description="Minimum value")
        max_value: float = Field(description="Maximum value")

        @field_validator("value")
        @classmethod
        def validate_range(cls, v, info):
            if "min_value" in info.data and v < info.data["min_value"]:
                raise ValueError("value must be >= min_value")
            if "max_value" in info.data and v > info.data["max_value"]:
                raise ValueError("value must be <= max_value")
            return v
"""

from __future__ import annotations

__all__ = []
