"""Unit tests for health check service."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from test_coverage_mcp.web_server.models.response.health_check import (
    ComponentHealthStatus,
    DetailedHealthCheckResponseDto,
    HealthyCheckResponseDto,
    LivenessCheckResponseDto,
    ReadinessCheckResponseDto,
)
from test_coverage_mcp.web_server.services.health_check_service import HealthCheckService


class TestHealthCheckService:
    """Test cases for HealthCheckService."""

    @pytest.fixture
    def service(self) -> HealthCheckService:
        """Create a health check service instance for testing.

        Returns
        -------
        HealthCheckService
            Health check service instance

        """
        return HealthCheckService()

    def test_initialization(self, service: HealthCheckService) -> None:
        """Test service initialization."""
        assert service is not None
        assert service._start_time > 0

    def test_get_uptime_seconds(self, service: HealthCheckService) -> None:
        """Test get_uptime_seconds method."""
        uptime = service.get_uptime_seconds()
        assert uptime >= 0
        assert isinstance(uptime, float)

    @pytest.mark.asyncio
    async def test_check_basic_health(self, service: HealthCheckService) -> None:
        """Test basic health check."""
        result = await service.check_basic_health()

        assert isinstance(result, HealthyCheckResponseDto)
        assert result.status == "healthy"
        assert result.timestamp is not None
        assert result.version == "0.1.0"
        assert result.uptime_seconds is not None
        assert result.uptime_seconds >= 0

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_mcp_server_health_success(
        self, mock_mcp_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test MCP server health check when server is healthy."""
        mock_mcp_server = MagicMock()
        mock_mcp_factory.get.return_value = mock_mcp_server

        result = await service.check_mcp_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "mcp_server"
        assert result.status == "healthy"
        assert result.message == "MCP server is running"
        assert result.last_check is not None
        assert isinstance(result.last_check, datetime)
        assert result.response_time_ms is not None
        assert result.response_time_ms >= 0

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_mcp_server_health_unavailable(
        self, mock_mcp_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test MCP server health check when server is unavailable."""
        mock_mcp_factory.get.return_value = None

        result = await service.check_mcp_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "mcp_server"
        assert result.status == "unhealthy"
        assert result.message == "MCP server is not available"
        assert result.last_check is not None
        assert result.response_time_ms is not None

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_mcp_server_health_exception(
        self, mock_mcp_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test MCP server health check when an exception occurs."""
        mock_mcp_factory.get.side_effect = Exception("Test error")

        result = await service.check_mcp_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "mcp_server"
        assert result.status == "unhealthy"
        assert "Test error" in result.message
        assert result.last_check is not None
        assert result.response_time_ms is not None

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    async def test_check_web_server_health_success(
        self, mock_web_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test web server health check when server is healthy."""
        mock_web_server = MagicMock()
        mock_web_factory.get.return_value = mock_web_server

        result = await service.check_web_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "web_server"
        assert result.status == "healthy"
        assert result.message == "Web server is running"
        assert result.last_check is not None
        assert isinstance(result.last_check, datetime)
        assert result.response_time_ms is not None
        assert result.response_time_ms >= 0

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    async def test_check_web_server_health_unavailable(
        self, mock_web_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test web server health check when server is unavailable."""
        mock_web_factory.get.return_value = None

        result = await service.check_web_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "web_server"
        assert result.status == "unhealthy"
        assert result.message == "Web server is not available"
        assert result.last_check is not None
        assert result.response_time_ms is not None

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    async def test_check_web_server_health_exception(
        self, mock_web_factory: MagicMock, service: HealthCheckService
    ) -> None:
        """Test web server health check when an exception occurs."""
        mock_web_factory.get.side_effect = Exception("Test error")

        result = await service.check_web_server_health()

        assert isinstance(result, ComponentHealthStatus)
        assert result.name == "web_server"
        assert result.status == "unhealthy"
        assert "Test error" in result.message
        assert result.last_check is not None
        assert result.response_time_ms is not None

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_detailed_health_all_healthy(
        self,
        mock_mcp_factory: MagicMock,
        mock_web_factory: MagicMock,
        service: HealthCheckService,
    ) -> None:
        """Test detailed health check when all components are healthy."""
        mock_mcp_factory.get.return_value = MagicMock()
        mock_web_factory.get.return_value = MagicMock()

        result = await service.check_detailed_health()

        assert isinstance(result, DetailedHealthCheckResponseDto)
        assert result.status == "healthy"
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
        assert result.version == "0.1.0"
        assert result.uptime_seconds is not None
        assert len(result.components) == 2
        assert all(c.status == "healthy" for c in result.components)

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_detailed_health_one_unhealthy(
        self,
        mock_mcp_factory: MagicMock,
        mock_web_factory: MagicMock,
        service: HealthCheckService,
    ) -> None:
        """Test detailed health check when one component is unhealthy."""
        mock_mcp_factory.get.return_value = None
        mock_web_factory.get.return_value = MagicMock()

        result = await service.check_detailed_health()

        assert isinstance(result, DetailedHealthCheckResponseDto)
        assert result.status == "degraded"
        assert len(result.components) == 2

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_detailed_health_all_unhealthy(
        self,
        mock_mcp_factory: MagicMock,
        mock_web_factory: MagicMock,
        service: HealthCheckService,
    ) -> None:
        """Test detailed health check when all components are unhealthy."""
        mock_mcp_factory.get.return_value = None
        mock_web_factory.get.return_value = None

        result = await service.check_detailed_health()

        assert isinstance(result, DetailedHealthCheckResponseDto)
        assert result.status == "unhealthy"
        assert len(result.components) == 2
        assert all(c.status == "unhealthy" for c in result.components)

    @pytest.mark.asyncio
    async def test_check_liveness(self, service: HealthCheckService) -> None:
        """Test liveness check."""
        result = await service.check_liveness()

        assert isinstance(result, LivenessCheckResponseDto)
        assert result.alive is True
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_readiness_all_ready(
        self,
        mock_mcp_factory: MagicMock,
        mock_web_factory: MagicMock,
        service: HealthCheckService,
    ) -> None:
        """Test readiness check when all components are ready."""
        mock_mcp_factory.get.return_value = MagicMock()
        mock_web_factory.get.return_value = MagicMock()

        result = await service.check_readiness()

        assert isinstance(result, ReadinessCheckResponseDto)
        assert result.ready is True
        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)
        assert result.message == "All components are ready"
        assert result.components_ready is not None
        assert result.components_ready["mcp_server"] is True
        assert result.components_ready["web_server"] is True

    @pytest.mark.asyncio
    @patch("test_coverage_mcp.web_server.app.web_factory")
    @patch("test_coverage_mcp.mcp_server.app.mcp_factory")
    async def test_check_readiness_not_ready(
        self,
        mock_mcp_factory: MagicMock,
        mock_web_factory: MagicMock,
        service: HealthCheckService,
    ) -> None:
        """Test readiness check when some components are not ready."""
        mock_mcp_factory.get.return_value = None
        mock_web_factory.get.return_value = MagicMock()

        result = await service.check_readiness()

        assert isinstance(result, ReadinessCheckResponseDto)
        assert result.ready is False
        assert result.timestamp is not None
        assert result.message == "Some components are not ready"
        assert result.components_ready is not None
        assert result.components_ready["mcp_server"] is False
        assert result.components_ready["web_server"] is True
