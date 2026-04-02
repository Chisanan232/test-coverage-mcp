"""MCP Tool Input Models - Parameter definitions for MCP tools.

This package contains Pydantic models that define the input parameters for MCP tools.
Each tool has a corresponding input model that validates and documents the required
parameters and their types.

Purpose
=======

The input models package provides:

1. **Tool Parameter Validation**
   - Pydantic models for tool input parameters
   - Type validation and conversion
   - Field constraints and validation rules
   - Clear error messages for invalid inputs

2. **Documentation**
   - Field descriptions for IDE autocompletion
   - Type hints for static analysis
   - Examples in docstrings
   - Constraint documentation

3. **Type Safety**
   - Ensures type-safe tool invocation
   - Prevents invalid parameter values
   - Enables IDE support and autocompletion
   - Supports static type checking

Design Principles
=================

1. **Tool-Specific Models**
   - Each tool has its own input model
   - Models are named consistently: [tool_name]_input.py
   - Clear relationship between tool and model

2. **Comprehensive Validation**
   - Use Pydantic validators for complex validation
   - Add constraints (min, max, pattern, etc.)
   - Provide helpful error messages
   - Support custom validation logic

3. **Clear Documentation**
   - Add docstrings to model classes
   - Add descriptions to all fields
   - Include examples in docstrings
   - Document constraints and validation

4. **Flexibility**
   - Support optional parameters with defaults
   - Support multiple parameter types
   - Support nested models
   - Support custom types

File Organization
=================

.. code-block:: text

    src/mcp/models/input/
    ├── __init__.py
    ├── [tool_name]_input.py
    ├── [tool_name2]_input.py
    └── ...

Extension Guide for Child Projects
===================================

To add custom MCP tool input models:

1. **Create input model file**
   - Create [tool_name]_input.py in this directory
   - Define Pydantic model for tool parameters
   - Add comprehensive field documentation

2. **Export in __init__.py**
   - Import model in __init__.py
   - Add to __all__ list
   - Make available for import

3. **Example input model**:

   .. code-block:: python

       # src/mcp/models/input/calculator_input.py
       from pydantic import BaseModel, Field

       class CalculatorInput(BaseModel):
           \"\"\"Input parameters for calculator tool.\"\"\"
           expression: str = Field(
               description="Mathematical expression to evaluate",
               examples=["2 + 2", "sqrt(16)", "sin(pi/2)"]
           )
           precision: int = Field(
               default=2,
               ge=0,
               le=10,
               description="Decimal precision for results"
           )

4. **Using input models in tools**:

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

2. **Validation**
   - Add constraints (min, max, pattern)
   - Use Pydantic validators for complex logic
   - Provide helpful error messages
   - Document validation rules

3. **Documentation**
   - Add docstrings to classes
   - Add descriptions to fields
   - Include examples
   - Document constraints

4. **Type Hints**
   - Use proper type hints
   - Use Union for multiple types
   - Use Optional for nullable fields
   - Use Literal for fixed values

5. **Defaults**
   - Provide sensible defaults
   - Make parameters optional when appropriate
   - Document default values
   - Consider user experience

Common Patterns
===============

1. **Simple Parameters**:

   .. code-block:: python

       class SimpleInput(BaseModel):
           text: str = Field(description="Input text")
           count: int = Field(default=1, ge=1, description="Repeat count")

2. **Constrained Parameters**:

   .. code-block:: python

       class ConstrainedInput(BaseModel):
           email: str = Field(description="Email address", pattern=r"^[^@]+@[^@]+$")
           age: int = Field(ge=0, le=150, description="Age in years")
           status: str = Field(description="Status", pattern="^(active|inactive)$")

3. **Optional Parameters**:

   .. code-block:: python

       class OptionalInput(BaseModel):
           required_field: str = Field(description="Required field")
           optional_field: str | None = Field(default=None, description="Optional field")
           with_default: str = Field(default="default_value", description="Field with default")

4. **Nested Models**:

   .. code-block:: python

       class Address(BaseModel):
           street: str = Field(description="Street address")
           city: str = Field(description="City")
           zip_code: str = Field(description="ZIP code")

       class UserInput(BaseModel):
           name: str = Field(description="User name")
           address: Address = Field(description="User address")

5. **List Parameters**:

   .. code-block:: python

       class ListInput(BaseModel):
           items: list[str] = Field(description="List of items")
           tags: list[str] = Field(default_factory=list, description="List of tags")

Testing
=======

Test input models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.mcp.models.input.calculator_input import CalculatorInput

    def test_calculator_input_valid():
        input_data = CalculatorInput(expression="2 + 2")
        assert input_data.expression == "2 + 2"
        assert input_data.precision == 2

    def test_calculator_input_invalid_type():
        with pytest.raises(ValidationError):
            CalculatorInput(expression=123)  # Must be string

    def test_calculator_input_invalid_precision():
        with pytest.raises(ValidationError):
            CalculatorInput(expression="2 + 2", precision=15)  # Max 10

Error Handling
==============

Input models provide clear validation errors:

.. code-block:: python

    from pydantic import ValidationError
    from src.mcp.models.input.calculator_input import CalculatorInput

    try:
        input_data = CalculatorInput(expression=123)
    except ValidationError as e:
        print(e.json())
        # Shows detailed error information

Migration Guide
===============

When updating input models:

1. **Adding Optional Fields**
   - Add with default value
   - Backward compatible
   - Existing tools continue to work

2. **Removing Fields**
   - Mark as deprecated first
   - Provide migration path
   - Remove in next major version

3. **Changing Field Types**
   - Use Union types for compatibility
   - Provide migration examples
   - Document breaking changes

4. **Adding Constraints**
   - May break existing usage
   - Document constraints clearly
   - Provide migration path
"""

from __future__ import annotations

__all__ = []
