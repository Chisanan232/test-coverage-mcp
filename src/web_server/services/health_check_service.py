"""Health check service for monitoring server and component health.

This module provides a service for performing health checks on the server
and its components, including MCP server, web server, and other dependencies.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Literal

from ..models.response.health_check import (
    ComponentHealthStatus,
    DetailedHealthCheckResponseDto,
    HealthyCheckResponseDto,
    LivenessCheckResponseDto,
    ReadinessCheckResponseDto,
)

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Service for performing health checks on server components.

    This service provides methods for checking the health of various
    server components and generating health check responses.

    Attributes
    ----------
    _start_time : float
        Server start time in seconds since epoch

    """

    def __init__(self) -> None:
        """Initialize the health check service."""
        self._start_time = time.time()

    def get_uptime_seconds(self) -> float:
        """Get server uptime in seconds.

        Returns
        -------
        float
            Server uptime in seconds

        """
        return time.time() - self._start_time

    async def check_basic_health(self) -> HealthyCheckResponseDto:
        """Perform basic health check.

        This is a simple health check that returns the basic health status.

        Returns
        -------
        HealthyCheckResponseDto
            Basic health check response

        """
        return HealthyCheckResponseDto(
            status="healthy",
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="0.1.0",
            uptime_seconds=self.get_uptime_seconds(),
        )

    async def check_mcp_server_health(self) -> ComponentHealthStatus:
        """Check MCP server health.

        Returns
        -------
        ComponentHealthStatus
            MCP server health status

        """
        start_time = time.time()
        try:
            from ...mcp.app import mcp_factory

            mcp_server = mcp_factory.get()
            is_healthy = mcp_server is not None

            response_time = (time.time() - start_time) * 1000

            return ComponentHealthStatus(
                name="mcp_server",
                status="healthy" if is_healthy else "unhealthy",
                message="MCP server is running" if is_healthy else "MCP server is not available",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"MCP server health check failed: {e}")
            return ComponentHealthStatus(
                name="mcp_server",
                status="unhealthy",
                message=f"MCP server check failed: {str(e)}",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )

    async def check_web_server_health(self) -> ComponentHealthStatus:
        """Check web server health.

        Returns
        -------
        ComponentHealthStatus
            Web server health status

        """
        start_time = time.time()
        try:
            from ...web_server.app import web_factory

            web_server = web_factory.get()
            is_healthy = web_server is not None

            response_time = (time.time() - start_time) * 1000

            return ComponentHealthStatus(
                name="web_server",
                status="healthy" if is_healthy else "unhealthy",
                message="Web server is running" if is_healthy else "Web server is not available",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Web server health check failed: {e}")
            return ComponentHealthStatus(
                name="web_server",
                status="unhealthy",
                message=f"Web server check failed: {str(e)}",
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )

    async def check_detailed_health(self) -> DetailedHealthCheckResponseDto:
        """Perform detailed health check.

        This performs comprehensive health checks on all components
        and returns detailed status information.

        Returns
        -------
        DetailedHealthCheckResponseDto
            Detailed health check response with component statuses

        """
        components = []

        mcp_health = await self.check_mcp_server_health()
        components.append(mcp_health)

        web_health = await self.check_web_server_health()
        components.append(web_health)

        overall_status: Literal["healthy", "unhealthy", "degraded"] = "healthy"
        unhealthy_count = sum(1 for c in components if c.status == "unhealthy")
        degraded_count = sum(1 for c in components if c.status == "degraded")

        if unhealthy_count > 0:
            if unhealthy_count == len(components):
                overall_status = "unhealthy"
            else:
                overall_status = "degraded"
        elif degraded_count > 0:
            overall_status = "degraded"

        return DetailedHealthCheckResponseDto(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            version="0.1.0",
            uptime_seconds=self.get_uptime_seconds(),
            components=components,
        )

    async def check_liveness(self) -> LivenessCheckResponseDto:
        """Perform liveness check.

        This is a simple check to determine if the server is alive.
        It always returns True if the server is running.

        Returns
        -------
        LivenessCheckResponseDto
            Liveness check response

        """
        return LivenessCheckResponseDto(
            alive=True,
            timestamp=datetime.now(timezone.utc),
        )

    async def check_readiness(self) -> ReadinessCheckResponseDto:
        """Perform readiness check.

        This checks if the server is ready to accept traffic by
        verifying that all critical components are healthy.

        Returns
        -------
        ReadinessCheckResponseDto
            Readiness check response

        """
        components_ready: dict[str, bool] = {}

        mcp_health = await self.check_mcp_server_health()
        components_ready["mcp_server"] = mcp_health.status == "healthy"

        web_health = await self.check_web_server_health()
        components_ready["web_server"] = web_health.status == "healthy"

        all_ready = all(components_ready.values())

        message = "All components are ready" if all_ready else "Some components are not ready"

        return ReadinessCheckResponseDto(
            ready=all_ready,
            timestamp=datetime.now(timezone.utc),
            message=message,
            components_ready=components_ready,
        )


health_check_service = HealthCheckService()
