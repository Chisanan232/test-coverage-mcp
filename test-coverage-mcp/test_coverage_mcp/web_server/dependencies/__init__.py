"""Web Server Dependencies - External service dependencies and integrations.

This package is designed for child projects to implement external service dependencies,
third-party integrations, and external API clients for the web server component.

Purpose
=======

The dependencies package provides a structured way to organize external service integrations:

1. **Service Integration**: Connect to external APIs and services
2. **Dependency Management**: Manage connection pools and authentication
3. **Error Handling**: Handle external service failures gracefully
4. **Configuration**: Centralize external service configuration

Structure for Child Projects
============================

Child projects should organize their dependencies as follows:

.. code-block:: text

    src/web_server/dependencies/
    ├── __init__.py              # This file - package documentation
    ├── database.py              # Database connections and ORM setup
    ├── cache.py                 # Redis or other caching services
    ├── auth.py                  # Authentication service integrations
    ├── storage.py               # File storage services (S3, etc.)
    ├── notifications.py         # Email, SMS, push notifications
    ├── analytics.py             # Analytics and monitoring services
    └── external_apis/           # Optional: Sub-package for API clients
        ├── __init__.py
        ├── payment_gateway.py
        ├── crm_system.py
        └── social_media.py

Dependency Implementation Guidelines
===================================

1. **Connection Management**
   - Use connection pooling for databases and external services
   - Implement proper timeout and retry logic
   - Handle connection failures gracefully

2. **Authentication & Security**
   - Store credentials securely (environment variables, secrets manager)
   - Use proper authentication methods (OAuth, API keys, certificates)
   - Implement rate limiting and throttling

3. **Error Handling**
   - Use custom exception classes for different error types
   - Implement circuit breakers for unreliable services
   - Log errors with appropriate context

4. **Configuration**
   - Use Pydantic settings for configuration validation
   - Support different environments (dev, staging, prod)
   - Provide sensible defaults

Example Dependency Implementation
================================

Here's a complete example of a database dependency:

.. code-block:: python

    \"\"\"Database dependency with connection pooling.\"\"\"

    import logging
    from typing import Optional, AsyncGenerator
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from sqlalchemy.orm import sessionmaker, declarative_base
    from test_coverage_mcp.config import get_settings

    logger = logging.getLogger(__name__)

    class DatabaseDependency:
        \"\"\"Manages database connections and sessions.\"\"\"

        def __init__(self):
            self.settings = get_settings()
            self._engine = None
            self._async_engine = None
            self._session_factory = None
            self._async_session_factory = None
            self._base = declarative_base()

        @property
        def engine(self):
            \"\"\"Get synchronous database engine.\"\"\"
            if self._engine is None:
                self._engine = create_engine(
                    self.settings.database_url,
                    pool_size=self.settings.db_pool_size,
                    max_overflow=self.settings.db_max_overflow,
                    echo=self.settings.db_echo
                )
            return self._engine

        @property
        def async_engine(self):
            \"\"\"Get asynchronous database engine.\"\"\"
            if self._async_engine is None:
                self._async_engine = create_async_engine(
                    self.settings.async_database_url,
                    pool_size=self.settings.db_pool_size,
                    max_overflow=self.settings.db_max_overflow,
                    echo=self.settings.db_echo
                )
            return self._async_engine

        @property
        def session_factory(self):
            \"\"\"Get synchronous session factory.\"\"\"
            if self._session_factory is None:
                self._session_factory = sessionmaker(
                    bind=self.engine,
                    autocommit=False,
                    autoflush=False
                )
            return self._session_factory

        @property
        def async_session_factory(self):
            \"\"\"Get asynchronous session factory.\"\"\"
            if self._async_session_factory is None:
                self._async_session_factory = async_sessionmaker(
                    bind=self.async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            return self._async_session_factory

        def get_session(self) -> sessionmaker:
            \"\"\"Get a database session.\"\"\"
            return self.session_factory()

        async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
            \"\"\"Get an async database session.\"\"\"
            async with self.async_session_factory() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()

        @property
        def base(self):
            \"\"\"Get declarative base for models.\"\"\"
            return self._base

        async def close(self):
            \"\"\"Close all database connections.\"\"\"
            if self._async_engine:
                await self._async_engine.dispose()
            if self._engine:
                self._engine.dispose()

    # Global dependency instance
    db_dependency = DatabaseDependency()

Integration with Web Server
===========================

Dependencies can be injected into FastAPI endpoints using dependency injection:

.. code-block:: python

    from fastapi import Depends, FastAPI
    from test_coverage_mcp.web_server.dependencies.database import db_dependency
    from sqlalchemy.orm import Session

    app = FastAPI()

    @app.get("/users/{user_id}")
    async def get_user(
        user_id: int,
        session: Session = Depends(db_dependency.get_session)
    ):
        \"\"\"Get user by ID.\"\"\"
        # Use session for database operations
        pass

    @app.post("/data")
    async def create_data(
        data: DataModel,
        session: AsyncSession = Depends(db_dependency.get_async_session)
    ):
        \"\"\"Create data using async session.\"\"\"
        # Use async session for database operations
        pass

Testing Dependencies
=====================

Test dependencies with mock implementations:

.. code-block:: python

    import pytest
    from unittest.mock import Mock, AsyncMock
    from test_coverage_mcp.web_server.dependencies.database import db_dependency

    @pytest.fixture
    def mock_db_session():
        \"\"\"Mock database session for testing.\"\"\"
        session = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        session.commit = Mock()
        session.rollback = Mock()
        return session

    @pytest.fixture
    async def mock_async_session():
        \"\"\"Mock async database session for testing.\"\"\"
        session = AsyncMock()
        session.execute.return_value.scalar.return_value = None
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        return session

Best Practices
==============

1. **Connection Pooling**: Always use connection pools for external services
2. **Timeouts**: Set appropriate timeouts for all external calls
3. **Retries**: Implement exponential backoff for failed requests
4. **Circuit Breakers**: Use circuit breakers for unreliable services
5. **Logging**: Log all external service calls with timing
6. **Metrics**: Track success rates, latency, and error rates
7. **Security**: Never log sensitive credentials or data
8. **Testing**: Mock external services in unit tests

Common Dependency Patterns
===========================

1. **Database Dependencies**
   - ORM setup and connection management
   - Migration support
   - Query helpers and repositories

2. **Cache Dependencies**
   - Redis or Memcached connections
   - Serialization/deserialization
   - Cache invalidation strategies

3. **Authentication Dependencies**
   - OAuth providers
   - JWT token validation
   - User session management

4. **Storage Dependencies**
   - S3 or other object storage
   - File upload/download
   - CDN integration

5. **Notification Dependencies**
   - Email service providers
   - SMS gateways
   - Push notification services

6. **Analytics Dependencies**
   - Event tracking
   - Metrics collection
   - Monitoring dashboards

Advanced Features
=================

1. **Health Checks**: Implement health checks for all dependencies
2. **Graceful Degradation**: Fallback behavior when services are unavailable
3. **Async Support**: Full async/await support for I/O operations
4. **Connection Resilience**: Automatic reconnection and failover
5. **Configuration Hot Reload**: Update configuration without restart
6. **Metrics and Monitoring**: Built-in metrics for observability

Dependencies
============

Common dependencies for external services:

.. code-block:: toml

    [project.optional-dependencies]
    dependencies = [
        "sqlalchemy",        # Database ORM
        "alembic",           # Database migrations
        "asyncpg",           # Async PostgreSQL driver
        "redis",             # Caching
        "aioredis",          # Async Redis client
        "boto3",             # AWS SDK
        "httpx",             # HTTP client
        "aiohttp",           # Async HTTP client
        "celery",            # Task queue
        "kombu",             # Message broker
    ]

Configuration Examples
======================

Add these settings to your configuration:

.. code-block:: python

    # Database settings
    DATABASE_URL: str = "postgresql://user:pass@localhost/db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # External API settings
    API_TIMEOUT: int = 30
    API_RETRY_ATTEMPTS: int = 3
    API_RETRY_DELAY: float = 1.0

Import this package in your web server application:

.. code-block:: python

    # Import dependencies to make them available
    from test_coverage_mcp.web_server.dependencies import db_dependency, cache_dependency

    # Use in your FastAPI app
    from fastapi import FastAPI, Depends
    from test_coverage_mcp.web_server.dependencies.database import db_dependency

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        \"\"\"Health check with dependency status.\"\"\"
        return {
            "database": "healthy" if db_dependency.engine else "unhealthy",
            "status": "healthy"
        }

"""

from __future__ import annotations

from .health_check import get_health_check_service

# Import all dependency modules to make them available
# Child projects should add their dependency imports here:

# Example imports (uncomment and modify for your dependencies):
# from .database import DatabaseDependency, get_database
# from .auth import AuthDependency, get_current_user, verify_token
# from .cache import CacheDependency, get_cache
# from .external_api import ExternalAPIDependency, get_api_client
# from .config import ConfigDependency, get_config

__all__ = [
    "get_health_check_service",
    # Add your dependency classes and functions here
    # "DatabaseDependency",
    # "get_database",
    # "AuthDependency",
    # "get_current_user",
    # "verify_token",
    # "CacheDependency",
    # "get_cache",
    # "ExternalAPIDependency",
    # "get_api_client",
    # "ConfigDependency",
    # "get_config",
]

# Package metadata for dependency discovery
__dependency_package__ = True
__dependency_version__ = "1.0.0"
__supported_features__ = [
    "database_integration",
    "caching",
    "authentication",
    "storage",
    "notifications",
    "external_apis",
    "async_support",
    "connection_pooling",
]
