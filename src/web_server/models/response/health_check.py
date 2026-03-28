"""Data transfer objects for health check and other responses.

This module contains Pydantic models for API responses and data transfer objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthyCheckResponseDto(BaseModel):
    """Health check response DTO.

    This model represents the health check response returned by the /health endpoint.
    It provides a standardized format for health status reporting.

    Attributes
    ----------
    status : Literal["healthy", "unhealthy"]
        Health status of the server
    timestamp : str | None
        ISO timestamp of when the health check was performed
    version : str | None
        Server version information
    uptime_seconds : float | None
        Server uptime in seconds
    checks : dict[str, bool] | None
        Individual health check results for different components

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "0.1.0",
                "uptime_seconds": 3600.0,
                "checks": {
                    "database": True,
                    "external_api": True,
                    "mcp_server": True,
                },
            }
        },
    )

    status: Literal["healthy", "unhealthy"] = Field(
        default="healthy",
        description="Health status of the server",
    )
    timestamp: str | None = Field(
        default=None,
        description="Timestamp of the health check in ISO format",
    )
    version: str | None = Field(
        default=None,
        description="Server version information",
    )
    uptime_seconds: float | None = Field(
        default=None,
        description="Server uptime in seconds",
    )
    checks: dict[str, bool] | None = Field(
        default=None,
        description="Individual health check results for different components",
    )


class ComponentHealthStatus(BaseModel):
    """Health status for individual component.

    This model represents the health status of a single component in the system.

    Attributes
    ----------
    name : str
        Component name
    status : Literal["healthy", "unhealthy", "degraded"]
        Health status of the component
    message : str | None
        Optional status message or error description
    last_check : datetime | None
        Timestamp of the last health check
    response_time_ms : float | None
        Response time in milliseconds

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "mcp_server",
                "status": "healthy",
                "message": "MCP server is running",
                "last_check": "2024-01-01T12:00:00Z",
                "response_time_ms": 5.2,
            }
        },
    )

    name: str = Field(
        description="Component name",
    )
    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        description="Health status of the component",
    )
    message: str | None = Field(
        default=None,
        description="Optional status message or error description",
    )
    last_check: datetime | None = Field(
        default=None,
        description="Timestamp of the last health check",
    )
    response_time_ms: float | None = Field(
        default=None,
        description="Response time in milliseconds",
    )


class DetailedHealthCheckResponseDto(BaseModel):
    """Detailed health check response DTO.

    This model provides comprehensive health information including
    individual component statuses and system metrics.

    Attributes
    ----------
    status : Literal["healthy", "unhealthy", "degraded"]
        Overall health status of the server
    timestamp : datetime
        ISO timestamp of when the health check was performed
    version : str | None
        Server version information
    uptime_seconds : float | None
        Server uptime in seconds
    components : list[ComponentHealthStatus]
        Individual health check results for different components

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "version": "0.1.0",
                "uptime_seconds": 3600.0,
                "components": [
                    {
                        "name": "mcp_server",
                        "status": "healthy",
                        "message": "MCP server is running",
                        "last_check": "2024-01-01T12:00:00Z",
                        "response_time_ms": 5.2,
                    },
                    {
                        "name": "web_server",
                        "status": "healthy",
                        "message": "Web server is running",
                        "last_check": "2024-01-01T12:00:00Z",
                        "response_time_ms": 2.1,
                    },
                ],
            }
        },
    )

    status: Literal["healthy", "unhealthy", "degraded"] = Field(
        description="Overall health status of the server",
    )
    timestamp: datetime = Field(
        description="Timestamp of the health check in ISO format",
    )
    version: str | None = Field(
        default=None,
        description="Server version information",
    )
    uptime_seconds: float | None = Field(
        default=None,
        description="Server uptime in seconds",
    )
    components: list[ComponentHealthStatus] = Field(
        default_factory=list,
        description="Individual health check results for different components",
    )


class LivenessCheckResponseDto(BaseModel):
    """Liveness check response DTO.

    This model represents a simple liveness probe response,
    indicating whether the server is alive and running.

    Attributes
    ----------
    alive : bool
        Whether the server is alive
    timestamp : datetime
        ISO timestamp of when the check was performed

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "alive": True,
                "timestamp": "2024-01-01T12:00:00Z",
            }
        },
    )

    alive: bool = Field(
        default=True,
        description="Whether the server is alive",
    )
    timestamp: datetime = Field(
        description="Timestamp of the check in ISO format",
    )


class ReadinessCheckResponseDto(BaseModel):
    """Readiness check response DTO.

    This model represents a readiness probe response,
    indicating whether the server is ready to accept traffic.

    Attributes
    ----------
    ready : bool
        Whether the server is ready to accept traffic
    timestamp : datetime
        ISO timestamp of when the check was performed
    message : str | None
        Optional message about readiness status
    components_ready : dict[str, bool] | None
        Readiness status of individual components

    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra="forbid",
        json_schema_extra={
            "example": {
                "ready": True,
                "timestamp": "2024-01-01T12:00:00Z",
                "message": "All components are ready",
                "components_ready": {
                    "mcp_server": True,
                    "web_server": True,
                },
            }
        },
    )

    ready: bool = Field(
        description="Whether the server is ready to accept traffic",
    )
    timestamp: datetime = Field(
        description="Timestamp of the check in ISO format",
    )
    message: str | None = Field(
        default=None,
        description="Optional message about readiness status",
    )
    components_ready: dict[str, bool] | None = Field(
        default=None,
        description="Readiness status of individual components",
    )
