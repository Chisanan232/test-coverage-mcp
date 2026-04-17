"""Web Server Services - Business logic and service layer implementations.

This package is designed for child projects to implement business logic, service layer components,
and application-specific services for the web server component.

Purpose
=======

The services package provides a structured way to organize business logic and services:

1. **Business Logic**: Implement application-specific business rules
2. **Service Layer**: Abstract complex operations and external integrations
3. **Data Processing**: Transform and process data between layers
4. **Orchestration**: Coordinate multiple dependencies and operations

Structure for Child Projects
============================

Child projects should organize their services as follows:

.. code-block:: text

    src/web_server/services/
    ├── __init__.py              # This file - package documentation
    ├── user_service.py          # User management and authentication
    ├── data_service.py          # Data processing and analysis
    ├── notification_service.py  # Notification and messaging
    ├── file_service.py          # File upload/download and processing
    ├── analytics_service.py     # Analytics and reporting
    ├── integration_service.py   # Third-party service integrations
    └── business/                # Optional: Sub-package for domain services
        ├── __init__.py
        ├── order_service.py
        ├── payment_service.py
        └── inventory_service.py

Service Implementation Guidelines
=================================

1. **Single Responsibility**
   - Each service should have a clear, focused purpose
   - Avoid mixing different domains in one service
   - Keep methods cohesive and related

2. **Dependency Injection**
   - Inject dependencies through constructor or method parameters
   - Use interfaces/protocols for testability
   - Avoid hardcoded dependencies

3. **Error Handling**
   - Use custom exceptions for different error types
   - Provide meaningful error messages
   - Log errors with appropriate context

4. **Transaction Management**
   - Handle database transactions properly
   - Implement rollback on failures
   - Use context managers for resource cleanup

Example Service Implementation
=============================

Here's a complete example of a user service:

.. code-block:: python

    \"\"\"User service for managing user accounts and authentication.\"\"\"

    import logging
    from typing import Optional, List
    from datetime import datetime, timedelta
    from sqlalchemy.orm import Session
    from test_coverage_mcp.web_server.dependencies.database import db_dependency
    from test_coverage_mcp.web_server.models.request.user import UserCreateRequest, UserUpdateRequest
    from test_coverage_mcp.web_server.models.response.user import UserResponse, UserListResponse
    from test_coverage_mcp.models.dto.user import UserDTO, UserStatus

    logger = logging.getLogger(__name__)

    class UserService:
        \"\"\"Service for user management operations.\"\"\"

        def __init__(self, session: Session = Depends(db_dependency.get_session)):
            self.session = session
            self._cache = {}  # Simple in-memory cache for demo

        async def create_user(self, user_data: UserCreateRequest) -> UserResponse:
            \"\"\"Create a new user account.

Args:
                user_data: User creation request with email, password, etc.

Returns:
                UserResponse with created user information

Raises:
                UserAlreadyExistsError: If user with email already exists
                ValidationError: If input data is invalid
            \"\"\"
            try:
                # Check if user already exists
                existing_user = self._find_user_by_email(user_data.email)
                if existing_user:
                    raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

                # Create new user
                user = UserDTO(
                    email=user_data.email,
                    username=user_data.username,
                    status=UserStatus.ACTIVE,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                # Hash password (simplified for demo)
                user.password_hash = self._hash_password(user_data.password)

                # Save to database
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)

                # Clear cache
                self._cache.clear()

                logger.info(f"Created user: {user.email}")
                return UserResponse.from_dto(user)

            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to create user: {e}")
                raise

        async def get_user(self, user_id: int) -> Optional[UserResponse]:
            \"\"\"Get user by ID.\"\"\"
            try:
                # Check cache first
                if user_id in self._cache:
                    return self._cache[user_id]

                user = self.session.query(UserDTO).filter(UserDTO.id == user_id).first()
                if user:
                    response = UserResponse.from_dto(user)
                    self._cache[user_id] = response
                    return response

                return None

            except Exception as e:
                logger.error(f"Failed to get user {user_id}: {e}")
                return None

        async def update_user(self, user_id: int, user_data: UserUpdateRequest) -> Optional[UserResponse]:
            \"\"\"Update user information.\"\"\"
            try:
                user = self.session.query(UserDTO).filter(UserDTO.id == user_id).first()
                if not user:
                    return None

                # Update fields
                if user_data.username:
                    user.username = user_data.username
                if user_data.status:
                    user.status = user_data.status

                user.updated_at = datetime.utcnow()

                self.session.commit()
                self.session.refresh(user)

                # Update cache
                response = UserResponse.from_dto(user)
                self._cache[user_id] = response

                logger.info(f"Updated user: {user.email}")
                return response

            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to update user {user_id}: {e}")
                return None

        async def delete_user(self, user_id: int) -> bool:
            \"\"\"Delete user account.\"\"\"
            try:
                user = self.session.query(UserDTO).filter(UserDTO.id == user_id).first()
                if not user:
                    return False

                self.session.delete(user)
                self.session.commit()

                # Clear cache
                if user_id in self._cache:
                    del self._cache[user_id]

                logger.info(f"Deleted user: {user.email}")
                return True

            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to delete user {user_id}: {e}")
                return False

        async def list_users(self, skip: int = 0, limit: int = 100) -> UserListResponse:
            \"\"\"List users with pagination.\"\"\"
            try:
                users = self.session.query(UserDTO).offset(skip).limit(limit).all()
                total = self.session.query(UserDTO).count()

                user_responses = [UserResponse.from_dto(user) for user in users]

                return UserListResponse(
                    users=user_responses,
                    total=total,
                    skip=skip,
                    limit=limit
                )

            except Exception as e:
                logger.error(f"Failed to list users: {e}")
                return UserListResponse(users=[], total=0, skip=skip, limit=limit)

        def _find_user_by_email(self, email: str) -> Optional[UserDTO]:
            \"\"\"Find user by email address.\"\"\"
            return self.session.query(UserDTO).filter(UserDTO.email == email).first()

        def _hash_password(self, password: str) -> str:
            \"\"\"Hash password (simplified for demo).\"\"\"
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

    # Custom exceptions
    class UserAlreadyExistsError(Exception):
        \"\"\"Raised when trying to create a user that already exists.\"\"\"
        pass

    class ValidationError(Exception):
        \"\"\"Raised when input validation fails.\"\"\"
        pass

Integration with Web Server
===========================

Services can be used in FastAPI endpoints through dependency injection:

.. code-block:: python

    from fastapi import Depends, FastAPI, HTTPException
    from test_coverage_mcp.web_server.services.user_service import UserService
    from test_coverage_mcp.web_server.models.request.user import UserCreateRequest

    app = FastAPI()

    @app.post("/users", response_model=UserResponse)
    async def create_user(
        user_data: UserCreateRequest,
        user_service: UserService = Depends()
    ):
        \"\"\"Create a new user.\"\"\"
        try:
            return await user_service.create_user(user_data)
        except UserService.UserAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/users/{user_id}", response_model=UserResponse)
    async def get_user(
        user_id: int,
        user_service: UserService = Depends()
    ):
        \"\"\"Get user by ID.\"\"\"
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

Testing Services
================

Test services with mock dependencies:

.. code-block:: python

    import pytest
    from unittest.mock import Mock, AsyncMock
    from test_coverage_mcp.web_server.services.user_service import UserService

    @pytest.fixture
    def mock_session():
        \"\"\"Mock database session for testing.\"\"\"
        session = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.refresh = Mock()
        return session

    @pytest.fixture
    def user_service(mock_session):
        \"\"\"User service with mocked dependencies.\"\"\"
        return UserService(session=mock_session)

    @pytest.mark.asyncio
    async def test_create_user_success(user_service, mock_session):
        \"\"\"Test successful user creation.\"\"\"
        from test_coverage_mcp.web_server.models.request.user import UserCreateRequest

        user_data = UserCreateRequest(
            email="test@example.com",
            username="testuser",
            password="password123"
        )

        # Mock no existing user
        user_service._find_user_by_email = Mock(return_value=None)

        result = await user_service.create_user(user_data)

        assert result.email == "test@example.com"
        assert result.username == "testuser"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

Best Practices
==============

1. **Separation of Concerns**: Keep services focused on business logic
2. **Dependency Injection**: Make services testable and flexible
3. **Error Handling**: Use custom exceptions and proper logging
4. **Transaction Management**: Handle database transactions correctly
5. **Caching**: Implement appropriate caching strategies
6. **Validation**: Validate inputs at the service layer
7. **Logging**: Log important operations and errors
8. **Testing**: Write comprehensive unit and integration tests

Common Service Patterns
=======================

1. **CRUD Services**
   - Create, Read, Update, Delete operations
   - Pagination and filtering
   - Bulk operations

2. **Business Logic Services**
   - Complex business rules and workflows
   - Multi-step operations
   - State management

3. **Integration Services**
   - Third-party API integrations
   - Data synchronization
   - Event handling

4. **Processing Services**
   - Data transformation and processing
   - File processing
   - Background jobs

5. **Notification Services**
   - Email, SMS, push notifications
   - Template management
   - Delivery tracking

Advanced Features
=================

1. **Async Support**: Full async/await support for I/O operations
2. **Caching**: Multi-level caching with invalidation
3. **Events**: Event-driven architecture support
4. **Background Jobs**: Integration with task queues
5. **Metrics**: Built-in metrics and monitoring
6. **Circuit Breakers**: Resilience patterns for external calls

Dependencies
============

Common dependencies for services:

.. code-block:: toml

    [project.optional-dependencies]
    services = [
        "pydantic",          # Data validation
        "sqlalchemy",        # Database ORM
        "redis",             # Caching
        "celery",            # Background jobs
        "httpx",             # HTTP client
        "jinja2",            # Templates
        "boto3",             # AWS SDK
    ]

Configuration Examples
======================

Add these settings to your configuration:

.. code-block:: python

    # Service settings
    USER_SERVICE_CACHE_TTL: int = 300  # 5 minutes
    USER_SERVICE_MAX_CACHE_SIZE: int = 1000
    NOTIFICATION_SERVICE_RETRY_ATTEMPTS: int = 3
    FILE_SERVICE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    ANALYTICS_SERVICE_BATCH_SIZE: int = 100

Import this package in your web server application:

.. code-block:: python

    # Import services to make them available
    from test_coverage_mcp.web_server.services import UserService, DataService, NotificationService

    # Use in your FastAPI app
    from fastapi import FastAPI, Depends
    from test_coverage_mcp.web_server.services.user_service import UserService

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        \"\"\"Health check with service status.\"\"\"
        return {
            "services": "healthy",
            "status": "healthy"
        }

"""

from __future__ import annotations

from .health_check_service import HealthCheckService, health_check_service

# Import all service modules to make them available
# Child projects should add their service imports here:

# Example imports (uncomment and modify for your services):
# from .user_service import UserService
# from .data_service import DataService
# from .notification_service import NotificationService
# from .file_service import FileService
# from .analytics_service import AnalyticsService

__all__ = [
    "HealthCheckService",
    "health_check_service",
    # Add your service classes here
    # "UserService",
    # "DataService",
    # "NotificationService",
    # "FileService",
    # "AnalyticsService",
]

# Package metadata for service discovery
__service_package__ = True
__service_version__ = "1.0.0"
__supported_features__ = [
    "business_logic",
    "data_processing",
    "crud_operations",
    "async_support",
    "caching",
    "error_handling",
    "dependency_injection",
    "transaction_management",
]
