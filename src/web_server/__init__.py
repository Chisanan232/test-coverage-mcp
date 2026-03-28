"""Web Server - FastAPI-based HTTP server for webhooks and health checks.

This package contains the FastAPI web server implementation that provides HTTP
transport support for MCP, webhook functionality, health checks, and CORS configuration.
It uses the singleton factory pattern to manage server lifecycle.

Purpose
=======

The web_server package provides:

1. **Web Server Factory** (app.py)
   - WebServerFactory: Singleton factory for creating FastAPI instances
   - web_factory: Global factory instance for convenient access
   - create_app(): Helper function for creating configured apps
   - mount_service(): Helper function for mounting sub-applications

2. **HTTP Transport Support**
   - SSE (Server-Sent Events) transport mounting
   - HTTP streaming transport mounting
   - Configurable mount paths for MCP sub-apps

3. **API Endpoints**
   - Health check endpoint (/health)
   - Webhook endpoints for external integrations
   - CORS configuration for cross-origin requests

4. **Request/Response DTOs** (models/)
   - Request models for API endpoints
   - Response models for API responses
   - Type-safe data structures for HTTP communication

Architecture
============

The web server is built on FastAPI and provides:

1. **Factory Pattern Implementation**
   - WebServerFactory extends BaseServerFactory
   - Enforces singleton pattern (only one instance allowed)
   - Provides create(), get(), and reset() methods
   - Supports testing through reset functionality

2. **Middleware Configuration**
   - CORS middleware for cross-origin requests
   - Request/response logging
   - Error handling middleware
   - Custom middleware support

3. **Routing and Mounting**
   - Health check router for monitoring
   - Sub-application mounting for MCP transports
   - Custom route registration
   - Lifespan event handlers

4. **Configuration Management**
   - Settings injection through dependency injection
   - CORS configuration from settings
   - Configurable host and port
   - Development mode support

Design Principles
=================

1. **Single Responsibility**
   - Factory handles server creation and lifecycle
   - Routers handle specific endpoint groups
   - Models handle data validation

2. **Extensibility**
   - Child projects can add custom endpoints
   - Models can be extended for project-specific needs
   - Middleware can be customized

3. **Type Safety**
   - All endpoints have type hints
   - Request/response models for validation
   - Pydantic models for data structures

4. **Testing Support**
   - Reset functionality for test isolation
   - Mocking-friendly factory interface
   - Clear error messages for debugging

Sub-packages
============

- **models/**: Request and response DTO models
  - request/: Request body models for API endpoints
  - response/: Response body models for API responses

Files
=====

- **app.py**: WebServerFactory and FastAPI configuration
  - WebServerFactory: Main factory class
  - web_factory: Global factory instance
  - create_app(): Helper for app creation
  - mount_service(): Helper for mounting sub-apps

Extension Guide for Child Projects
===================================

To extend this template with custom API endpoints:

1. **Add custom endpoints** to the web server
   - Create endpoint functions with proper type hints
   - Use request models from src/web_server/models/request/
   - Return response models from src/web_server/models/response/

2. **Create endpoint-specific models** in src/web_server/models/
   - Request models in src/web_server/models/request/
   - Response models in src/web_server/models/response/
   - Use Pydantic for validation

3. **Example structure for child projects**:

   .. code-block:: text

       src/web_server/
       ├── __init__.py
       ├── app.py                    # Factory (inherited)
       ├── routers/                  # Project-specific endpoints
       │   ├── __init__.py
       │   ├── tasks.py              # Task management endpoints
       │   └── users.py              # User management endpoints
       └── models/
           ├── request/
           │   ├── __init__.py
           │   ├── task_request.py
           │   └── user_request.py
           └── response/
               ├── __init__.py
               ├── task_response.py
               └── user_response.py

4. **Example request model**:

   .. code-block:: python

       from pydantic import BaseModel, Field

       class CreateTaskRequest(BaseModel):
           \"\"\"Request model for creating a task.\"\"\"
           title: str = Field(description="Task title")
           description: str | None = Field(
               default=None,
               description="Task description"
           )
           priority: str = Field(
               default="medium",
               description="Task priority"
           )

5. **Example response model**:

   .. code-block:: python

       from pydantic import BaseModel, Field
       from datetime import datetime

       class TaskResponse(BaseModel):
           \"\"\"Response model for task data.\"\"\"
           id: str = Field(description="Task ID")
           title: str = Field(description="Task title")
           created_at: datetime = Field(description="Creation timestamp")
           status: str = Field(description="Task status")

6. **Example endpoint implementation**:

   .. code-block:: python

       from fastapi import APIRouter, HTTPException
       from src.web_server.models.request.task_request import CreateTaskRequest
       from src.web_server.models.response.task_response import TaskResponse

       router = APIRouter(prefix="/tasks", tags=["tasks"])

       @router.post("/", response_model=TaskResponse)
       async def create_task(request: CreateTaskRequest) -> TaskResponse:
           \"\"\"Create a new task.\"\"\"
           # Implementation here
           return TaskResponse(...)

       # Register router with app
       from src.web_server import web_factory
       app = web_factory.get()
       app.include_router(router)

Usage Examples
==============

.. code-block:: python

    from src.web_server import WebServerFactory, web_factory, create_app

    # Create web server instance (singleton)
    app = web_factory.create()

    # Get existing server instance
    app = web_factory.get()

    # Create app with custom configuration
    from src.models import ServerConfig
    config = ServerConfig(port=8000)
    app = create_app(config)

    # Mount a sub-application
    from fastapi import FastAPI
    sub_app = FastAPI()
    mount_service(app, sub_app, "/api/v1")

    # Run with uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Reset for testing
    web_factory.reset()

Health Check Endpoint
=====================

The web server provides a health check endpoint:

.. code-block:: bash

    GET /health

Response:

.. code-block:: json

    {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00Z",
        "version": "0.0.0"
    }

CORS Configuration
==================

CORS is configured from settings:

.. code-block:: python

    from src.config import get_settings

    settings = get_settings()
    # CORS settings:
    # - cors_allow_origins: List of allowed origins
    # - cors_allow_credentials: Allow credentials
    # - cors_allow_methods: Allowed HTTP methods
    # - cors_allow_headers: Allowed headers

Error Handling
==============

The web server provides consistent error handling:

.. code-block:: python

    from fastapi import HTTPException

    @router.get("/items/{item_id}")
    async def get_item(item_id: int):
        if item_id < 0:
            raise HTTPException(
                status_code=400,
                detail="Item ID must be positive"
            )
        return {"item_id": item_id}

Testing
=======

For testing, use the reset functionality:

.. code-block:: python

    from src.web_server import web_factory
    from fastapi.testclient import TestClient
    import pytest

    @pytest.fixture
    def client():
        web_factory.reset()
        app = web_factory.create()
        yield TestClient(app)
        web_factory.reset()

    def test_health_check(client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

Middleware
==========

Custom middleware can be added:

.. code-block:: python

    from fastapi import FastAPI
    from starlette.middleware import Middleware
    from starlette.middleware.base import BaseHTTPMiddleware

    class CustomMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            # Pre-processing
            response = await call_next(request)
            # Post-processing
            return response

    app = FastAPI(
        middleware=[Middleware(CustomMiddleware)]
    )

Lifespan Events
===============

Lifespan events can be configured:

.. code-block:: python

    from contextlib import asynccontextmanager
    from fastapi import FastAPI

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        print("Starting up")

Yield:
        # Shutdown
        print("Shutting down")

    app = FastAPI(lifespan=lifespan)

"""

from __future__ import annotations

from .app import WebServerFactory, create_app, mount_service, web_factory

__all__ = [
    "WebServerFactory",
    "create_app",
    "mount_service",
    "web_factory",
]
