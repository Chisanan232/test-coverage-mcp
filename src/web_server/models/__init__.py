"""Web Server Models - Request and Response DTO data structures.

This package contains Pydantic models that are specific to the web server
implementation. These models define the data structures for HTTP request and
response bodies, ensuring type safety and validation for API communication.

Purpose
=======

The models package provides:

1. **Request Models** (request/)
   - Define request body structures for API endpoints
   - Validate incoming request data
   - Provide type hints for endpoint functions
   - Enable IDE autocompletion

2. **Response Models** (response/)
   - Define response body structures for API endpoints
   - Validate outgoing response data
   - Ensure consistent response formats
   - Support serialization to JSON

Design Principles
=================

1. **Endpoint-Specific Organization**
   - Each endpoint has its own request/response models
   - Models are organized by endpoint functionality
   - Clear naming conventions for easy discovery

2. **Validation and Type Safety**
   - Pydantic models ensure data validation
   - Type hints enable static type checking
   - Field descriptions provide documentation

3. **Extensibility**
   - Models can be extended through inheritance
   - New models can be added for new endpoints
   - Backward compatibility through optional fields

4. **Serialization Support**
   - Models support JSON serialization
   - Compatible with HTTP protocol requirements
   - Support for complex nested structures

Sub-packages
============

- **request/**: HTTP request body models
  - Contains Pydantic models for request bodies
  - Each endpoint has a corresponding request model
  - Validates and documents request requirements

- **response/**: HTTP response body models
  - Contains Pydantic models for response bodies
  - Each endpoint has a corresponding response model
  - Ensures consistent response formats

File Organization
=================

.. code-block:: text

    src/web_server/models/
    ├── __init__.py
    ├── request/
    │   ├── __init__.py
    │   └── [endpoint_name]_request.py
    └── response/
        ├── __init__.py
        └── [endpoint_name]_response.py

Extension Guide for Child Projects
===================================

To add custom API endpoint models:

1. **Create request model** in src/web_server/models/request/
   - Define Pydantic model for request body
   - Add field descriptions and validation
   - Export in __init__.py

2. **Create response model** in src/web_server/models/response/
   - Define Pydantic model for response body
   - Add field descriptions and validation
   - Export in __init__.py

3. **Example structure for child projects**:

   .. code-block:: text

       src/web_server/models/
       ├── request/
       │   ├── __init__.py
       │   ├── task_request.py
       │   ├── user_request.py
       │   └── webhook_request.py
       └── response/
           ├── __init__.py
           ├── task_response.py
           ├── user_response.py
           └── webhook_response.py

4. **Example request model**:

   .. code-block:: python

       from pydantic import BaseModel, Field

       class CreateTaskRequest(BaseModel):
           \"\"\"Request model for creating a task.\"\"\"
           title: str = Field(
               description="Task title",
               min_length=1,
               max_length=255
           )
           description: str | None = Field(
               default=None,
               description="Task description"
           )
           priority: str = Field(
               default="medium",
               description="Task priority",
               pattern="^(low|medium|high)$"
           )

5. **Example response model**:

   .. code-block:: python

       from pydantic import BaseModel, Field
       from datetime import datetime

       class TaskResponse(BaseModel):
           \"\"\"Response model for task data.\"\"\"
           id: str = Field(description="Task ID")
           title: str = Field(description="Task title")
           description: str | None = Field(description="Task description")
           priority: str = Field(description="Task priority")
           created_at: datetime = Field(description="Creation timestamp")
           updated_at: datetime = Field(description="Last update timestamp")
           status: str = Field(description="Task status")

6. **Using models in endpoints**:

   .. code-block:: python

       from fastapi import APIRouter, HTTPException
       from src.web_server.models.request.task_request import CreateTaskRequest
       from src.web_server.models.response.task_response import TaskResponse

       router = APIRouter(prefix="/tasks", tags=["tasks"])

       @router.post("/", response_model=TaskResponse, status_code=201)
       async def create_task(request: CreateTaskRequest) -> TaskResponse:
           \"\"\"Create a new task.\"\"\"
           # Implementation here
           return TaskResponse(...)

       @router.get("/{task_id}", response_model=TaskResponse)
       async def get_task(task_id: str) -> TaskResponse:
           \"\"\"Get a task by ID.\"\"\"
           # Implementation here
           return TaskResponse(...)

Usage Examples
==============

.. code-block:: python

    from src.web_server.models.request.task_request import CreateTaskRequest
    from src.web_server.models.response.task_response import TaskResponse

    # Create request model with validation
    request_data = CreateTaskRequest(
        title="Implement feature",
        description="Add new API endpoint",
        priority="high"
    )

    # Use in endpoint function
    response = create_task(request_data)

    # Serialize to JSON for HTTP response
    json_response = response.model_dump_json()

    # Parse from JSON
    parsed = TaskResponse.model_validate_json(json_response)

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

Error Response Models
=====================

Define consistent error responses:

.. code-block:: python

    class ErrorResponse(BaseModel):
        \"\"\"Generic error response model.\"\"\"
        error: str = Field(description="Error message")
        detail: str | None = Field(default=None, description="Error details")
        status_code: int = Field(description="HTTP status code")

Pagination Models
=================

For paginated responses:

.. code-block:: python

    from typing import Generic, TypeVar

    T = TypeVar("T")

    class PaginatedResponse(BaseModel, Generic[T]):
        \"\"\"Paginated response model.\"\"\"
        items: list[T] = Field(description="List of items")
        total: int = Field(description="Total number of items")
        page: int = Field(description="Current page number")
        page_size: int = Field(description="Items per page")
        total_pages: int = Field(description="Total number of pages")

Testing
=======

Test models with Pydantic validation:

.. code-block:: python

    import pytest
    from pydantic import ValidationError
    from src.web_server.models.request.task_request import CreateTaskRequest

    def test_create_task_request_validation():
        # Valid request
        request = CreateTaskRequest(title="Test task")
        assert request.title == "Test task"

        # Invalid request - missing required field
        with pytest.raises(ValidationError):
            CreateTaskRequest()

        # Invalid request - field too long
        with pytest.raises(ValidationError):
            CreateTaskRequest(title="x" * 256)
"""

from __future__ import annotations

__all__ = []
