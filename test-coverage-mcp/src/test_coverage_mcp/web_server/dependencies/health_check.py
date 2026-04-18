"""Health check dependencies for FastAPI.

This module provides dependency injection functions for health check services.
"""

from __future__ import annotations

from ..services.health_check_service import HealthCheckService, health_check_service


def get_health_check_service() -> HealthCheckService:
    """Dependency to get health check service instance.

    This dependency provides the health check service singleton instance
    for use in FastAPI route handlers.

    Returns
    -------
    HealthCheckService
        Health check service instance

    Examples
    --------
    >>> from fastapi import APIRouter, Depends
    >>> from .dependencies.health_check import get_health_check_service
    >>>
    >>> router = APIRouter()
    >>>
    >>> @router.get("/health")
    >>> async def health_check(
    ...     service: HealthCheckService = Depends(get_health_check_service)
    ... ):
    ...     return await service.check_basic_health()

    """
    return health_check_service
