"""Health check router for FastAPI.

This module provides health check endpoints for monitoring server
and component health, including basic health, detailed health,
liveness, and readiness checks.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies.health_check import get_health_check_service
from ..models.response.health_check import (
    DetailedHealthCheckResponseDto,
    HealthyCheckResponseDto,
    LivenessCheckResponseDto,
    ReadinessCheckResponseDto,
)
from ..services.health_check_service import HealthCheckService

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Health check successful"},
        503: {"description": "Service unavailable"},
    },
)


@router.get("", response_model=HealthyCheckResponseDto, status_code=200)
async def basic_health_check(
    service: HealthCheckService = Depends(get_health_check_service),
) -> HealthyCheckResponseDto:
    """Basic health check endpoint.

    This endpoint provides a simple health check response with
    basic server information including status, version, and uptime.

    Parameters
    ----------
    service : HealthCheckService
        Health check service instance (injected)

    Returns
    -------
    HealthyCheckResponseDto
        Basic health check response

    Examples
    --------
    >>> GET /health
    >>> {
    ...     "status": "healthy",
    ...     "timestamp": "2024-01-01T12:00:00Z",
    ...     "version": "0.1.0",
    ...     "uptime_seconds": 3600.0
    ... }

    """
    return await service.check_basic_health()


@router.get("/detailed", response_model=DetailedHealthCheckResponseDto, status_code=200)
async def detailed_health_check(
    service: HealthCheckService = Depends(get_health_check_service),
) -> DetailedHealthCheckResponseDto:
    """Detailed health check endpoint.

    This endpoint provides comprehensive health information including
    individual component statuses and system metrics.

    Parameters
    ----------
    service : HealthCheckService
        Health check service instance (injected)

    Returns
    -------
    DetailedHealthCheckResponseDto
        Detailed health check response with component statuses

    Examples
    --------
    >>> GET /health/detailed
    >>> {
    ...     "status": "healthy",
    ...     "timestamp": "2024-01-01T12:00:00Z",
    ...     "version": "0.1.0",
    ...     "uptime_seconds": 3600.0,
    ...     "components": [
    ...         {
    ...             "name": "mcp_server",
    ...             "status": "healthy",
    ...             "message": "MCP server is running",
    ...             "last_check": "2024-01-01T12:00:00Z",
    ...             "response_time_ms": 5.2
    ...         }
    ...     ]
    ... }

    """
    return await service.check_detailed_health()


@router.get("/liveness", response_model=LivenessCheckResponseDto, status_code=200)
async def liveness_check(
    service: HealthCheckService = Depends(get_health_check_service),
) -> LivenessCheckResponseDto:
    """Liveness check endpoint.

    This endpoint provides a simple liveness probe response,
    indicating whether the server is alive and running.
    This is typically used by Kubernetes or other orchestration
    systems to determine if the container should be restarted.

    Parameters
    ----------
    service : HealthCheckService
        Health check service instance (injected)

    Returns
    -------
    LivenessCheckResponseDto
        Liveness check response

    Examples
    --------
    >>> GET /health/liveness
    >>> {
    ...     "alive": true,
    ...     "timestamp": "2024-01-01T12:00:00Z"
    ... }

    """
    return await service.check_liveness()


@router.get("/readiness", response_model=ReadinessCheckResponseDto, status_code=200)
async def readiness_check(
    service: HealthCheckService = Depends(get_health_check_service),
) -> ReadinessCheckResponseDto:
    """Readiness check endpoint.

    This endpoint checks if the server is ready to accept traffic by
    verifying that all critical components are healthy.
    This is typically used by Kubernetes or other orchestration
    systems to determine if traffic should be routed to this instance.

    Parameters
    ----------
    service : HealthCheckService
        Health check service instance (injected)

    Returns
    -------
    ReadinessCheckResponseDto
        Readiness check response

    Examples
    --------
    >>> GET /health/readiness
    >>> {
    ...     "ready": true,
    ...     "timestamp": "2024-01-01T12:00:00Z",
    ...     "message": "All components are ready",
    ...     "components_ready": {
    ...         "mcp_server": true,
    ...         "web_server": true
    ...     }
    ... }

    """
    return await service.check_readiness()
