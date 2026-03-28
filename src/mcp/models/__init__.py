"""MCP-Specific Models - Tool input and output data structures.

This package contains Pydantic models that are specific to the MCP server
implementation. These models define the data structures for MCP tool inputs
and outputs, ensuring type safety and validation for tool communication.

Purpose
=======

The models package provides:

1. **Input Models** (input/)
   - Define parameters for MCP tools
   - Validate tool input data
   - Provide type hints for tool functions
   - Enable IDE autocompletion

2. **Output Models** (output/)
   - Define return values for MCP tools
   - Validate tool output data
   - Ensure consistent response formats
   - Support serialization to JSON

Design Principles
=================

1. **Tool-Specific Organization**
   - Each tool has its own input/output models
   - Models are organized by tool functionality
   - Clear naming conventions for easy discovery

2. **Validation and Type Safety**
   - Pydantic models ensure data validation
   - Type hints enable static type checking
   - Field descriptions provide documentation

3. **Extensibility**
   - Models can be extended through inheritance
   - New models can be added for new tools
   - Backward compatibility through optional fields

4. **Serialization Support**
   - Models support JSON serialization
   - Compatible with MCP protocol requirements
   - Support for complex nested structures

Sub-packages
============

- **input/**: MCP tool input parameter models
  - Contains Pydantic models for tool parameters
  - Each tool has a corresponding input model
  - Validates and documents tool requirements

- **output/**: MCP tool output response models
  - Contains Pydantic models for tool responses
  - Each tool has a corresponding output model
  - Ensures consistent response formats

File Organization
=================

.. code-block:: text

    src/mcp/models/
    ├── __init__.py
    ├── input/
    │   ├── __init__.py
    │   └── [tool_name]_input.py
    └── output/
        ├── __init__.py
        └── [tool_name]_output.py

Extension Guide for Child Projects
===================================

To add custom MCP tool models:

1. **Create input model** in src/mcp/models/input/
   - Define Pydantic model for tool parameters
   - Add field descriptions and validation
   - Export in __init__.py

2. **Create output model** in src/mcp/models/output/
   - Define Pydantic model for tool response
   - Add field descriptions and validation
   - Export in __init__.py

3. **Example structure for child projects**:

   .. code-block:: text

       src/mcp/models/
       ├── input/
       │   ├── __init__.py
       │   ├── calculator_input.py
       │   ├── database_input.py
       │   └── file_input.py
       └── output/
           ├── __init__.py
           ├── calculator_output.py
           ├── database_output.py
           └── file_output.py

4. **Example input model**:

   .. code-block:: python

       from pydantic import BaseModel, Field

       class CalculatorInput(BaseModel):
           \"\"\"Input parameters for calculator tool.\"\"\"
           expression: str = Field(
               description="Mathematical expression to evaluate"
           )
           precision: int = Field(
               default=2,
               description="Decimal precision for results"
           )

5. **Example output model**:

   .. code-block:: python

       from pydantic import BaseModel, Field

       class CalculatorOutput(BaseModel):
           \"\"\"Output from calculator tool.\"\"\"
           result: float = Field(description="Calculation result")
           expression: str = Field(description="Original expression")
           error: str | None = Field(
               default=None,
               description="Error message if calculation failed"
           )

6. **Using models in tools**:

   .. code-block:: python

       from src.mcp import mcp_factory
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

Usage Examples
==============

.. code-block:: python

    from src.mcp.models.input.calculator_input import CalculatorInput
    from src.mcp.models.output.calculator_output import CalculatorOutput

    # Create input model with validation
    input_data = CalculatorInput(
        expression="2 + 2 * 3",
        precision=2
    )

    # Use in tool function
    output = calculate(input_data)

    # Serialize to JSON for MCP protocol
    json_output = output.model_dump_json()

    # Parse from JSON
    parsed = CalculatorOutput.model_validate_json(json_output)

Best Practices
==============

1. **Clear Field Names**
   - Use descriptive names for all fields
   - Follow snake_case naming convention
   - Avoid abbreviations

2. **Documentation**
   - Add docstrings to model classes
   - Add descriptions to all fields
   - Include examples in docstrings

3. **Validation**
   - Use Pydantic validators for complex validation
   - Add constraints (min, max, pattern) where applicable
   - Provide helpful error messages

4. **Backward Compatibility**
   - Make new fields optional with defaults
   - Don't remove existing fields
   - Use Field(deprecated=True) for deprecated fields

5. **Type Hints**
   - Use proper type hints for all fields
   - Use Union types for multiple possibilities
   - Use Optional for nullable fields

Error Handling
==============

Models should handle errors gracefully:

.. code-block:: python

    class ToolOutput(BaseModel):
        \"\"\"Generic tool output with error handling.\"\"\"
        success: bool = Field(description="Whether tool succeeded")
        data: dict | None = Field(default=None, description="Tool output")
        error: str | None = Field(default=None, description="Error message")

Testing
=======

Test models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.mcp.models.input.calculator_input import CalculatorInput

    def test_calculator_input_validation():
        # Valid input
        input_data = CalculatorInput(expression="2 + 2")
        assert input_data.expression == "2 + 2"

        # Invalid input
        with pytest.raises(ValidationError):
            CalculatorInput(expression=123)  # Must be string
"""

from __future__ import annotations

__all__ = []
