"""Unit tests for health check router."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from src.web_server.dependencies.health_check import get_health_check_service
from src.web_server.models.response.health_check import (
    ComponentHealthStatus,
    DetailedHealthCheckResponseDto,
    HealthyCheckResponseDto,
    LivenessCheckResponseDto,
    ReadinessCheckResponseDto,
)
from src.web_server.routers.health_check import router
from src.web_server.services.health_check_service import HealthCheckService


@pytest.fixture
def mock_health_service() -> MagicMock:
    """Create a mock health check service.

    Returns
    -------
    MagicMock
        Mock health check service

    """
    service = MagicMock(spec=HealthCheckService)
    service.check_basic_health = AsyncMock()
    service.check_detailed_health = AsyncMock()
    service.check_liveness = AsyncMock()
    service.check_readiness = AsyncMock()
    return service


@pytest.fixture
def client(mock_health_service: MagicMock) -> TestClient:
    """Create a test client with mocked health service.

    Parameters
    ----------
    mock_health_service : MagicMock
        Mock health check service

    Returns
    -------
    TestClient
        FastAPI test client

    """
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_health_check_service] = lambda: mock_health_service

    return TestClient(app)


class TestHealthCheckRouter:
    """Test cases for health check router endpoints."""

    def test_basic_health_check_success(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test basic health check endpoint returns success."""
        mock_health_service.check_basic_health.return_value = HealthyCheckResponseDto(
            status="healthy",
            timestamp="2024-01-01T12:00:00Z",
            version="0.1.0",
            uptime_seconds=3600.0,
        )

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["uptime_seconds"] == 3600.0
        mock_health_service.check_basic_health.assert_called_once()

    def test_detailed_health_check_success(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test detailed health check endpoint returns success."""
        mock_health_service.check_detailed_health.return_value = DetailedHealthCheckResponseDto(
            status="healthy",
            timestamp=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
            version="0.1.0",
            uptime_seconds=3600.0,
            components=[
                ComponentHealthStatus(
                    name="mcp_server",
                    status="healthy",
                    message="MCP server is running",
                    last_check=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
                    response_time_ms=5.2,
                ),
                ComponentHealthStatus(
                    name="web_server",
                    status="healthy",
                    message="Web server is running",
                    last_check=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
                    response_time_ms=2.1,
                ),
            ],
        )

        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["uptime_seconds"] == 3600.0
        assert len(data["components"]) == 2
        assert data["components"][0]["name"] == "mcp_server"
        assert data["components"][0]["status"] == "healthy"
        assert data["components"][1]["name"] == "web_server"
        assert data["components"][1]["status"] == "healthy"
        mock_health_service.check_detailed_health.assert_called_once()

    def test_detailed_health_check_degraded(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test detailed health check endpoint returns degraded status."""
        mock_health_service.check_detailed_health.return_value = DetailedHealthCheckResponseDto(
            status="degraded",
            timestamp=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
            version="0.1.0",
            uptime_seconds=3600.0,
            components=[
                ComponentHealthStatus(
                    name="mcp_server",
                    status="unhealthy",
                    message="MCP server is not available",
                    last_check=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
                    response_time_ms=5.2,
                ),
                ComponentHealthStatus(
                    name="web_server",
                    status="healthy",
                    message="Web server is running",
                    last_check=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
                    response_time_ms=2.1,
                ),
            ],
        )

        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert len(data["components"]) == 2

    def test_liveness_check_success(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test liveness check endpoint returns success."""
        mock_health_service.check_liveness.return_value = LivenessCheckResponseDto(
            alive=True,
            timestamp=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
        )

        response = client.get("/health/liveness")

        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data
        mock_health_service.check_liveness.assert_called_once()

    def test_readiness_check_ready(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test readiness check endpoint returns ready status."""
        mock_health_service.check_readiness.return_value = ReadinessCheckResponseDto(
            ready=True,
            timestamp=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
            message="All components are ready",
            components_ready={
                "mcp_server": True,
                "web_server": True,
            },
        )

        response = client.get("/health/readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["message"] == "All components are ready"
        assert data["components_ready"]["mcp_server"] is True
        assert data["components_ready"]["web_server"] is True
        mock_health_service.check_readiness.assert_called_once()

    def test_readiness_check_not_ready(self, client: TestClient, mock_health_service: MagicMock) -> None:
        """Test readiness check endpoint returns not ready status."""
        mock_health_service.check_readiness.return_value = ReadinessCheckResponseDto(
            ready=False,
            timestamp=datetime.fromisoformat("2024-01-01T12:00:00+00:00"),
            message="Some components are not ready",
            components_ready={
                "mcp_server": False,
                "web_server": True,
            },
        )

        response = client.get("/health/readiness")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is False
        assert data["message"] == "Some components are not ready"
        assert data["components_ready"]["mcp_server"] is False
        assert data["components_ready"]["web_server"] is True


class TestHealthCheckRouterIntegration:
    """Integration tests for health check router."""

    def test_router_prefix(self) -> None:
        """Test that router has correct prefix."""
        assert router.prefix == "/health"

    def test_router_tags(self) -> None:
        """Test that router has correct tags."""
        assert "health" in router.tags

    def test_all_endpoints_registered(self) -> None:
        """Test that all health check endpoints are registered."""
        routes = [route.path for route in router.routes]
        assert "/health" in routes
        assert "/health/detailed" in routes
        assert "/health/liveness" in routes
        assert "/health/readiness" in routes
