r"""Web Server Request Models - HTTP request body definitions.

This package contains Pydantic models that define the request body structures for
web server API endpoints. Each endpoint has a corresponding request model that
validates and documents the required request data and its types.

Purpose
=======

The request models package provides:

1. **Request Body Validation**
   - Pydantic models for HTTP request bodies
   - Type validation and conversion
   - Field constraints and validation rules
   - Clear error messages for invalid requests

2. **Documentation**
   - Field descriptions for API documentation
   - Type hints for static analysis
   - Examples in docstrings
   - Constraint documentation

3. **Type Safety**
   - Ensures type-safe request handling
   - Prevents invalid request data
   - Enables IDE support and autocompletion
   - Supports static type checking

Design Principles
=================

1. **Endpoint-Specific Models**
   - Each endpoint has its own request model
   - Models are named consistently: [endpoint_name]_request.py
   - Clear relationship between endpoint and model

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
   - Support optional request fields with defaults
   - Support multiple field types
   - Support nested models
   - Support custom types

File Organization
=================

.. code-block:: text

    src/web_server/models/request/
    ├── __init__.py
    ├── [endpoint_name]_request.py
    ├── [endpoint_name2]_request.py
    └── ...

Extension Guide for Child Projects
===================================

To add custom API endpoint request models:

1. **Create request model file**
   - Create [endpoint_name]_request.py in this directory
   - Define Pydantic model for request body
   - Add comprehensive field documentation

2. **Export in __init__.py**
   - Import model in __init__.py
   - Add to __all__ list
   - Make available for import

3. **Example request model**:

   .. code-block:: python

       # src/web_server/models/request/create_task_request.py
       from pydantic import BaseModel, Field

       class CreateTaskRequest(BaseModel):
           \"\"\"Request model for creating a task.\"\"\"
           title: str = Field(
               description="Task title",
               min_length=1,
               max_length=255,
               examples=["Implement feature", "Fix bug"]
           )
           description: str | None = Field(
               default=None,
               description="Task description",
               max_length=1000
           )
           priority: str = Field(
               default="medium",
               description="Task priority",
               pattern="^(low|medium|high)$"
           )
           tags: list[str] = Field(
               default_factory=list,
               description="Task tags"
           )

4. **Using request models in endpoints**:

   .. code-block:: python

       from fastapi import APIRouter
       from src.web_server.models.request.create_task_request import CreateTaskRequest
       from src.web_server.models.response.task_response import TaskResponse

       router = APIRouter(prefix="/tasks", tags=["tasks"])

       @router.post("/", response_model=TaskResponse, status_code=201)
       async def create_task(request: CreateTaskRequest) -> TaskResponse:
           \"\"\"Create a new task.\"\"\"
           # Implementation here
           return TaskResponse(...)

Best Practices
==============

1. **Field Naming**
   - Use descriptive names
   - Follow snake_case convention
   - Avoid abbreviations
   - Be consistent across endpoints

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
   - Make fields optional when appropriate
   - Document default values
   - Consider user experience

Common Patterns
===============

1. **Simple Request**:

   .. code-block:: python

       class SimpleRequest(BaseModel):
           name: str = Field(description="User name")
           email: str = Field(description="User email")

2. **Request with Validation**:

   .. code-block:: python

       class ValidatedRequest(BaseModel):
           email: str = Field(
               description="Email address",
               pattern=r"^[^@]+@[^@]+\.[^@]+$"
           )
           age: int = Field(
               ge=0,
               le=150,
               description="Age in years"
           )

3. **Request with Optional Fields**:

   .. code-block:: python

       class OptionalRequest(BaseModel):
           required_field: str = Field(description="Required field")
           optional_field: str | None = Field(
               default=None,
               description="Optional field"
           )
           with_default: str = Field(
               default="default_value",
               description="Field with default"
           )

4. **Request with Nested Models**:

   .. code-block:: python

       class Address(BaseModel):
           street: str = Field(description="Street address")
           city: str = Field(description="City")
           zip_code: str = Field(description="ZIP code")

       class UserRequest(BaseModel):
           name: str = Field(description="User name")
           address: Address = Field(description="User address")

5. **Request with List Fields**:

   .. code-block:: python

       class ListRequest(BaseModel):
           items: list[str] = Field(
               description="List of items",
               min_items=1
           )
           tags: list[str] = Field(
               default_factory=list,
               description="List of tags"
           )

Testing
=======

Test request models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.web_server.models.request.create_task_request import CreateTaskRequest

    def test_create_task_request_valid():
        request = CreateTaskRequest(title="Test task")
        assert request.title == "Test task"
        assert request.priority == "medium"

    def test_create_task_request_invalid_title():
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="")  # Too short

    def test_create_task_request_invalid_priority():
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="Test", priority="urgent")  # Invalid value

Error Handling
==============

Request models provide clear validation errors:

.. code-block:: python

    from pydantic import ValidationError
    from src.web_server.models.request.create_task_request import CreateTaskRequest

    try:
        request = CreateTaskRequest(title="")
    except ValidationError as e:
        print(e.json())
        # Shows detailed error information

API Documentation
=================

Request models are automatically documented in OpenAPI/Swagger:

.. code-block:: python

    from fastapi import FastAPI
    from src.web_server.models.request.create_task_request import CreateTaskRequest

    app = FastAPI()

    @app.post("/tasks/")
    async def create_task(request: CreateTaskRequest):
        # Swagger automatically documents the request schema
        pass

    # Visit http://localhost:8000/docs for interactive documentation

Pagination Request Pattern
==========================

For endpoints with pagination:

.. code-block:: python

    class PaginatedRequest(BaseModel):
        \"\"\"Paginated request parameters.\"\"\"
        page: int = Field(
            default=1,
            ge=1,
            description="Page number"
        )
        page_size: int = Field(
            default=10,
            ge=1,
            le=100,
            description="Items per page"
        )
        sort_by: str | None = Field(
            default=None,
            description="Field to sort by"
        )
        sort_order: str = Field(
            default="asc",
            pattern="^(asc|desc)$",
            description="Sort order"
        )

Filter Request Pattern
======================

For endpoints with filtering:

.. code-block:: python

    class FilterRequest(BaseModel):
        \"\"\"Filter parameters.\"\"\"
        search: str | None = Field(
            default=None,
            description="Search query"
        )
        status: str | None = Field(
            default=None,
            pattern="^(active|inactive|pending)$",
            description="Filter by status"
        )
        date_from: datetime | None = Field(
            default=None,
            description="Start date"
        )
        date_to: datetime | None = Field(
            default=None,
            description="End date"
        )

Migration Guide
===============

When updating request models:

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

Custom validation for request models:

.. code-block:: python

    from pydantic import BaseModel, Field, field_validator

    class RangeRequest(BaseModel):
        min_value: float = Field(description="Minimum value")
        max_value: float = Field(description="Maximum value")

        @field_validator("max_value")
        @classmethod
        def validate_max_greater_than_min(cls, v, info):
            if "min_value" in info.data and v <= info.data["min_value"]:
                raise ValueError("max_value must be greater than min_value")
            return v
"""

from __future__ import annotations

__all__ = []
