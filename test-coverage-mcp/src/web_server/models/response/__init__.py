"""Web Server Response Models - HTTP response body definitions.

This package contains Pydantic models that define the response body structures for
web server API endpoints. Each endpoint has a corresponding response model that
validates and documents the returned response data and its types.

Purpose
=======

The response models package provides:

1. **Response Body Validation**
   - Pydantic models for HTTP response bodies
   - Type validation and conversion
   - Consistent response formats
   - Clear response documentation

2. **Documentation**
   - Field descriptions for API documentation
   - Type hints for static analysis
   - Examples in docstrings
   - Response format documentation

3. **Type Safety**
   - Ensures type-safe response handling
   - Validates response data before serialization
   - Enables IDE support and autocompletion
   - Supports static type checking

Design Principles
=================

1. **Endpoint-Specific Models**
   - Each endpoint has its own response model
   - Models are named consistently: [endpoint_name]_response.py
   - Clear relationship between endpoint and model

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

    src/web_server/models/response/
    ├── __init__.py
    ├── health_check.py
    ├── [endpoint_name]_response.py
    ├── [endpoint_name2]_response.py
    └── ...

Extension Guide for Child Projects
===================================

To add custom API endpoint response models:

1. **Create response model file**
   - Create [endpoint_name]_response.py in this directory
   - Define Pydantic model for response body
   - Add comprehensive field documentation

2. **Export in __init__.py**
   - Import model in __init__.py
   - Add to __all__ list
   - Make available for import

3. **Example response model**:

   .. code-block:: python

       # src/web_server/models/response/task_response.py
       from pydantic import BaseModel, Field
       from datetime import datetime

       class TaskResponse(BaseModel):
           \"\"\"Response model for task data.\"\"\"
           id: str = Field(
               description="Task ID",
               examples=["task-123"]
           )
           title: str = Field(
               description="Task title",
               examples=["Implement feature"]
           )
           description: str | None = Field(
               default=None,
               description="Task description"
           )
           priority: str = Field(
               description="Task priority",
               examples=["high"]
           )
           status: str = Field(
               description="Task status",
               examples=["pending", "in_progress", "completed"]
           )
           created_at: datetime = Field(
               description="Creation timestamp"
           )
           updated_at: datetime = Field(
               description="Last update timestamp"
           )

4. **Using response models in endpoints**:

   .. code-block:: python

       from fastapi import APIRouter
       from src.web_server.models.response.task_response import TaskResponse

       router = APIRouter(prefix="/tasks", tags=["tasks"])

       @router.get("/{task_id}", response_model=TaskResponse)
       async def get_task(task_id: str) -> TaskResponse:
           \"\"\"Get a task by ID.\"\"\"
           # Implementation here
           return TaskResponse(...)

Best Practices
==============

1. **Field Naming**
   - Use descriptive names
   - Follow snake_case convention
   - Avoid abbreviations
   - Be consistent across endpoints

2. **Error Handling**
   - Include error information in responses
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

       class SimpleResponse(BaseModel):
           id: str = Field(description="Resource ID")
           name: str = Field(description="Resource name")
           created_at: datetime = Field(description="Creation timestamp")

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

       class StructuredResponse(BaseModel):
           items: list[Item] = Field(description="List of items")
           total: int = Field(description="Total count")
           page: int = Field(description="Current page")

4. **Metadata Response**:

   .. code-block:: python

       class MetadataResponse(BaseModel):
           data: str = Field(description="Main response data")
           metadata: dict = Field(description="Response metadata")
           processing_time_ms: float = Field(description="Processing time")

5. **Paginated Response**:

   .. code-block:: python

       from typing import Generic, TypeVar

       T = TypeVar("T")

       class PaginatedResponse(BaseModel, Generic[T]):
           items: list[T] = Field(description="List of items")
           total: int = Field(description="Total count")
           page: int = Field(description="Current page")
           page_size: int = Field(description="Items per page")
           total_pages: int = Field(description="Total pages")

Testing
=======

Test response models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.web_server.models.response.task_response import TaskResponse
    from datetime import datetime

    def test_task_response_valid():
        response = TaskResponse(
            id="task-123",
            title="Test task",
            priority="high",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert response.id == "task-123"

    def test_task_response_invalid_type():
        with pytest.raises(ValidationError):
            TaskResponse(
                id=123,  # Must be string
                title="Test",
                priority="high",
                status="pending",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

Serialization
=============

Response models support JSON serialization for HTTP responses:

.. code-block:: python

    from src.web_server.models.response.task_response import TaskResponse

    # Create response
    response = TaskResponse(...)

    # Serialize to JSON
    json_str = response.model_dump_json()

    # Serialize to dict
    dict_data = response.model_dump()

    # Parse from JSON
    parsed = TaskResponse.model_validate_json(json_str)

API Documentation
=================

Response models are automatically documented in OpenAPI/Swagger:

.. code-block:: python

    from fastapi import FastAPI
    from src.web_server.models.response.task_response import TaskResponse

    app = FastAPI()

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: str):
        # Swagger automatically documents the response schema
        pass

    # Visit http://localhost:8000/docs for interactive documentation

Error Response Pattern
======================

Consistent error handling across endpoints:

.. code-block:: python

    class ErrorResponse(BaseModel):
        \"\"\"Generic error response.\"\"\"
        success: bool = Field(default=False, description="Operation failed")
        error: str = Field(description="Error message")
        error_code: str | None = Field(default=None, description="Error code")
        details: dict | None = Field(default=None, description="Error details")

    # Usage in endpoint
    from fastapi import HTTPException

    @router.get("/{item_id}")
    async def get_item(item_id: int):
        if item_id < 0:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Invalid item ID",
                    error_code="INVALID_ID"
                ).model_dump()
            )
        return ItemResponse(...)

Migration Guide
===============

When updating response models:

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

Custom validation for response models:

.. code-block:: python

    from pydantic import BaseModel, Field, field_validator

    class ValidatedResponse(BaseModel):
        value: float = Field(description="Response value")
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

Status Code Mapping
===================

Use response models with appropriate HTTP status codes:

.. code-block:: python

    from fastapi import APIRouter
    from src.web_server.models.response.task_response import TaskResponse

    router = APIRouter()

    @router.post("/tasks/", response_model=TaskResponse, status_code=201)
    async def create_task(request):
        # 201 Created
        return TaskResponse(...)

    @router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
    async def get_task(task_id: str):
        # 200 OK
        return TaskResponse(...)

    @router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
    async def update_task(task_id: str, request):
        # 200 OK
        return TaskResponse(...)

    @router.delete("/tasks/{task_id}", status_code=204)
    async def delete_task(task_id: str):
        # 204 No Content
        pass
"""

from __future__ import annotations

from .health_check import (
    ComponentHealthStatus,
    DetailedHealthCheckResponseDto,
    HealthyCheckResponseDto,
    LivenessCheckResponseDto,
    ReadinessCheckResponseDto,
)

__all__ = [
    "ComponentHealthStatus",
    "DetailedHealthCheckResponseDto",
    "HealthyCheckResponseDto",
    "LivenessCheckResponseDto",
    "ReadinessCheckResponseDto",
]
