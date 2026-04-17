"""Web Server Routers - FastAPI route definitions and API endpoints.

This package is designed for child projects to implement FastAPI routers, API endpoints,
and HTTP route handlers for the web server component.

Purpose
=======

The routers package provides a structured way to organize API endpoints:

1. **Route Organization**: Group related endpoints in separate routers
2. **HTTP Handlers**: Implement request/response logic
3. **API Documentation**: Auto-generate OpenAPI/Swagger documentation
4. **Middleware Integration**: Apply middleware to specific route groups

Structure for Child Projects
============================

Child projects should organize their routers as follows:

.. code-block:: text

    src/web_server/routers/
    ├── __init__.py              # This file - package documentation
    ├── health.py                # Health check and status endpoints
    ├── users.py                 # User management endpoints
    ├── data.py                  # Data processing and analysis endpoints
    ├── files.py                 # File upload/download endpoints
    ├── webhooks.py              # Webhook handlers
    ├── admin.py                 # Admin and management endpoints
    └── api/                     # Optional: Sub-package for versioned APIs
        ├── __init__.py
        ├── v1/
        │   ├── __init__.py
        │   ├── users.py
        │   └── data.py
        └── v2/
            ├── __init__.py
            ├── users.py
            └── data.py

Router Implementation Guidelines
=================================

1. **Single Responsibility**
   - Each router should handle a specific domain or resource
   - Keep related endpoints together
   - Use clear, RESTful URL patterns

2. **Dependency Injection**
   - Use FastAPI's dependency injection system
   - Inject services, dependencies, and utilities
   - Make endpoints testable and maintainable

3. **Error Handling**
   - Use HTTP status codes appropriately
   - Return consistent error response formats
   - Handle validation errors automatically

4. **Documentation**
   - Use FastAPI's automatic documentation
   - Add descriptive docstrings for endpoints
   - Include examples in request/response models

Example Router Implementation
=============================

Here's a complete example of a users router:

.. code-block:: python

    \"\"\"User management router for FastAPI.\"\"\"

    from typing import List, Optional
    from fastapi import APIRouter, Depends, HTTPException, Query, Path
    from fastapi.responses import JSONResponse
    from test_coverage_mcp.web_server.services.user_service import UserService, UserAlreadyExistsError
    from test_coverage_mcp.web_server.models.request.user import UserCreateRequest, UserUpdateRequest
    from test_coverage_mcp.web_server.models.response.user import UserResponse, UserListResponse, ErrorResponse

    router = APIRouter(
        prefix="/users",
        tags=["users"],
        responses={404: {"model": ErrorResponse, "description": "User not found"}},
    )

    @router.post("/", response_model=UserResponse, status_code=201)
    async def create_user(
        user_data: UserCreateRequest,
        user_service: UserService = Depends()
    ) -> UserResponse:
        \"\"\"Create a new user account.

Args:
            user_data: User creation data including email, username, password

Returns:
            Created user information

Raises:
            HTTPException: If user already exists or validation fails

Example:
            >>> POST /users
            >>> {
            ...     "email": "user@example.com",
            ...     "username": "testuser",
            ...     "password": "securepassword"
            ... }
        \"\"\"
        try:
            user = await user_service.create_user(user_data)
            return user
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
                headers={"X-Error": "UserAlreadyExists"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Internal server error while creating user"
            )

    @router.get("/{user_id}", response_model=UserResponse)
    async def get_user(
        user_id: int = Path(..., ge=1, description="User ID"),
        user_service: UserService = Depends()
    ) -> UserResponse:
        \"\"\"Get user by ID.

Args:
            user_id: Unique identifier of the user

Returns:
            User information

Raises:
            HTTPException: If user not found

Example:
            >>> GET /users/123
        \"\"\"
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found",
                headers={"X-Error": "UserNotFound"}
            )
        return user

    @router.put("/{user_id}", response_model=UserResponse)
    async def update_user(
        user_id: int = Path(..., ge=1, description="User ID"),
        user_data: UserUpdateRequest = Depends(),
        user_service: UserService = Depends()
    ) -> UserResponse:
        \"\"\"Update user information.

Args:
            user_id: Unique identifier of the user
            user_data: User update data

Returns:
            Updated user information

Raises:
            HTTPException: If user not found or validation fails

Example:
            >>> PUT /users/123
            >>> {
            ...     "username": "newusername",
            ...     "status": "active"
            ... }
        \"\"\"
        user = await user_service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )
        return user

    @router.delete("/{user_id}", status_code=204)
    async def delete_user(
        user_id: int = Path(..., ge=1, description="User ID"),
        user_service: UserService = Depends()
    ) -> None:
        \"\"\"Delete user account.

Args:
            user_id: Unique identifier of the user

Raises:
            HTTPException: If user not found

Example:
            >>> DELETE /users/123
        \"\"\"
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

    @router.get("/", response_model=UserListResponse)
    async def list_users(
        skip: int = Query(0, ge=0, description="Number of users to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
        user_service: UserService = Depends()
    ) -> UserListResponse:
        \"\"\"List users with pagination.

Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return

Returns:
            Paginated list of users

Example:
            >>> GET /users?skip=0&limit=50
        \"\"\"
        return await user_service.list_users(skip=skip, limit=limit)

    @router.get("/{user_id}/status", response_model=dict)
    async def get_user_status(
        user_id: int = Path(..., ge=1, description="User ID"),
        user_service: UserService = Depends()
    ) -> dict:
        \"\"\"Get user status information.

Args:
            user_id: Unique identifier of the user

Returns:
            User status information

Example:
            >>> GET /users/123/status
        \"\"\"
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID {user_id} not found"
            )

        return {
            "user_id": user.id,
            "status": user.status,
            "last_updated": user.updated_at,
            "is_active": user.status == "active"
        }

Integration with Web Server
===========================

Routers are integrated into the main FastAPI application:

.. code-block:: python

    from fastapi import FastAPI
    from test_coverage_mcp.web_server.routers import users, health, data

    app = FastAPI(
        title="MCP Server API",
        description="API for MCP Server Template",
        version="1.0.0"
    )

    # Include routers
    app.include_router(users.router)
    app.include_router(health.router)
    app.include_router(data.router)

    # Or with custom prefix
    app.include_router(
        users.router,
        prefix="/api/v1",
        tags=["users", "api-v1"]
    )

Advanced Router Features
=======================

1. **Middleware**: Apply middleware to specific routers

.. code-block:: python

    from fastapi import FastAPI
    from test_coverage_mcp.web_server.middleware.auth import auth_middleware
    from test_coverage_mcp.web_server.routers.admin import router as admin_router

    app = FastAPI()

    # Apply authentication middleware to admin routes
    admin_router.middleware("http")(auth_middleware)
    app.include_router(admin_router)

2. **Dependencies**: Router-level dependencies

.. code-block:: python

    from fastapi import APIRouter, Depends
    from test_coverage_mcp.web_server.dependencies.auth import get_current_user

    router = APIRouter(
        prefix="/protected",
        dependencies=[Depends(get_current_user)],
        tags=["protected"]
    )

3. **Exception Handlers**: Router-specific exception handling

.. code-block:: python

    from fastapi import APIRouter
    from test_coverage_mcp.web_server.exceptions import UserNotFoundError

    router = APIRouter()

    @router.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

Testing Routers
===============

Test routers with TestClient and mocked dependencies:

.. code-block:: python

    import pytest
    from fastapi.testclient import TestClient
    from unittest.mock import Mock, AsyncMock
    from test_coverage_mcp.web_server.app import app
    from test_coverage_mcp.web_server.routers.users import router
    from test_coverage_mcp.web_server.services.user_service import UserService

    @pytest.fixture
    def client():
        return TestClient(app)

    @pytest.fixture
    def mock_user_service():
        service = Mock(spec=UserService)
        service.create_user = AsyncMock()
        service.get_user = AsyncMock()
        return service

    def test_create_user_success(client, mock_user_service):
        \"\"\"Test successful user creation.\"\"\"
        # Mock the service dependency
        app.dependency_overrides[UserService] = lambda: mock_user_service

        # Mock response
        from test_coverage_mcp.web_server.models.response.user import UserResponse
        mock_user_service.create_user.return_value = UserResponse(
            id=1,
            email="test@example.com",
            username="testuser",
            status="active"
        )

        response = client.post("/users/", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        })

        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

        # Clean up
        app.dependency_overrides.clear()

Best Practices
==============

1. **RESTful Design**: Follow REST conventions for URLs and HTTP methods
2. **Status Codes**: Use appropriate HTTP status codes
3. **Validation**: Use Pydantic models for request/response validation
4. **Documentation**: Include comprehensive docstrings and examples
5. **Error Handling**: Provide consistent error response formats
6. **Testing**: Write comprehensive tests for all endpoints
7. **Security**: Implement proper authentication and authorization
8. **Performance**: Use async/await for I/O operations

Common Router Patterns
======================

1. **CRUD Routers**
   - Standard Create, Read, Update, Delete operations
   - Pagination and filtering
   - Bulk operations

2. **Resource Routers**
   - Nested resources (e.g., /users/{id}/posts)
   - Resource relationships
   - Composite operations

3. **Webhook Routers**
   - External service integrations
   - Event processing
   - Signature verification

4. **Admin Routers**
   - Administrative operations
   - System management
   - Monitoring endpoints

5. **API Versioning**
   - Versioned endpoints (/api/v1/, /api/v2/)
   - Backward compatibility
   - Migration strategies

Advanced Features
=================

1. **Background Tasks**: Use FastAPI BackgroundTasks for async operations
2. **Streaming Responses**: Support for large data streaming
3. **File Uploads**: Handle file uploads with proper validation
4. **WebSockets**: Real-time communication endpoints
5. **Rate Limiting**: Implement rate limiting per endpoint
6. **Caching**: Add caching headers and logic

Dependencies
============

Common dependencies for routers:

.. code-block:: toml

    [project.optional-dependencies]
    routers = [
        "fastapi",           # Web framework
        "pydantic",          # Data validation
        "python-multipart",  # File uploads
        "aiofiles",          # Async file operations
        "jinja2",            # Templates
        "python-jose",       # JWT tokens
        "passlib",           # Password hashing
    ]

Configuration Examples
======================

Add these settings to your configuration:

.. code-block:: python

    # Router settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    FILE_UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    WEBHOOK_TIMEOUT: int = 30

Import this package in your web server application:

.. code-block:: python

    # Import routers to make them available
    from test_coverage_mcp.web_server.routers import users_router, health_router, data_router

    # Include in your FastAPI app
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(users_router)
    app.include_router(health_router)
    app.include_router(data_router)

"""

from __future__ import annotations

from .health_check import router as health_check_router

# Import all router modules to make them available
# Child projects should add their router imports here:

# Example imports (uncomment and modify for your routers):
# from .users import router as users_router
# from .data import router as data_router
# from .files import router as files_router
# from .webhooks import router as webhooks_router
# from .admin import router as admin_router

__all__ = [
    "health_check_router",
    # Add your router instances here
    # "users_router",
    # "data_router",
    # "files_router",
    # "webhooks_router",
    # "admin_router",
]

# Package metadata for router discovery
__router_package__ = True
__router_version__ = "1.0.0"
__supported_features__ = [
    "restful_api",
    "crud_operations",
    "dependency_injection",
    "auto_documentation",
    "validation",
    "error_handling",
    "middleware_support",
    "async_support",
]
