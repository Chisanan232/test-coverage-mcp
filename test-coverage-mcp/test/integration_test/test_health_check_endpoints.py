"""Integration tests for health check endpoints.

These tests verify the health check endpoints work correctly
when integrated with the full FastAPI application.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from test_coverage_mcp.mcp_server.app import MCPServerFactory
from test_coverage_mcp.web_server.app import WebServerFactory


class TestHealthCheckEndpointsIntegration:
    """Integration tests for health check endpoints."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self) -> None:
        """Setup and teardown for each test."""
        WebServerFactory.reset()
        MCPServerFactory.reset()
        yield
        WebServerFactory.reset()
        MCPServerFactory.reset()

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client with the full application.

        Returns
        -------
        TestClient
            FastAPI test client

        """
        with (
            patch("test_coverage_mcp.web_server.app.mcp_factory") as mock_mcp_factory,
            patch("test_coverage_mcp.web_server.app.get_settings") as mock_get_settings,
        ):
            mock_settings = MagicMock()
            mock_settings.cors_allow_origins = ["*"]
            mock_settings.cors_allow_credentials = True
            mock_settings.cors_allow_methods = ["*"]
            mock_settings.cors_allow_headers = ["*"]
            mock_get_settings.return_value = mock_settings

            mock_mcp_factory.lifespan.return_value = MagicMock()

            from test_coverage_mcp.web_server.app import create_app

            app = create_app()
            return TestClient(app)

    def test_basic_health_endpoint_exists(self, client: TestClient) -> None:
        """Test that basic health endpoint exists and is accessible."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_basic_health_endpoint_response_structure(self, client: TestClient) -> None:
        """Test that basic health endpoint returns correct structure."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data

        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_detailed_health_endpoint_exists(self, client: TestClient) -> None:
        """Test that detailed health endpoint exists and is accessible."""
        response = client.get("/health/detailed")
        assert response.status_code == 200

    def test_detailed_health_endpoint_response_structure(self, client: TestClient) -> None:
        """Test that detailed health endpoint returns correct structure."""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "components" in data

        assert data["status"] in ["healthy", "unhealthy", "degraded"]
        assert isinstance(data["components"], list)

        for component in data["components"]:
            assert "name" in component
            assert "status" in component
            assert "message" in component
            assert "last_check" in component
            assert "response_time_ms" in component
            assert component["status"] in ["healthy", "unhealthy", "degraded"]

    def test_liveness_endpoint_exists(self, client: TestClient) -> None:
        """Test that liveness endpoint exists and is accessible."""
        response = client.get("/health/liveness")
        assert response.status_code == 200

    def test_liveness_endpoint_response_structure(self, client: TestClient) -> None:
        """Test that liveness endpoint returns correct structure."""
        response = client.get("/health/liveness")
        assert response.status_code == 200

        data = response.json()
        assert "alive" in data
        assert "timestamp" in data

        assert data["alive"] is True

    def test_readiness_endpoint_exists(self, client: TestClient) -> None:
        """Test that readiness endpoint exists and is accessible."""
        response = client.get("/health/readiness")
        assert response.status_code == 200

    def test_readiness_endpoint_response_structure(self, client: TestClient) -> None:
        """Test that readiness endpoint returns correct structure."""
        response = client.get("/health/readiness")
        assert response.status_code == 200

        data = response.json()
        assert "ready" in data
        assert "timestamp" in data
        assert "message" in data
        assert "components_ready" in data

        assert isinstance(data["ready"], bool)
        assert isinstance(data["components_ready"], dict)

    def test_all_health_endpoints_return_json(self, client: TestClient) -> None:
        """Test that all health endpoints return JSON content type."""
        endpoints = ["/health", "/health/detailed", "/health/liveness", "/health/readiness"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]

    def test_health_endpoints_consistent_timestamps(self, client: TestClient) -> None:
        """Test that health endpoints return valid timestamps."""
        endpoints = ["/health", "/health/detailed", "/health/liveness", "/health/readiness"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            data = response.json()
            assert "timestamp" in data
            assert data["timestamp"] is not None

    def test_detailed_health_includes_component_checks(self, client: TestClient) -> None:
        """Test that detailed health check includes component checks."""
        response = client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert len(data["components"]) >= 2

        component_names = [c["name"] for c in data["components"]]
        assert "mcp_server" in component_names
        assert "web_server" in component_names

    def test_readiness_includes_component_readiness(self, client: TestClient) -> None:
        """Test that readiness check includes component readiness status."""
        response = client.get("/health/readiness")
        assert response.status_code == 200

        data = response.json()
        assert "components_ready" in data
        assert "mcp_server" in data["components_ready"]
        assert "web_server" in data["components_ready"]

    def test_health_endpoints_performance(self, client: TestClient) -> None:
        """Test that health endpoints respond quickly."""
        import time

        endpoints = ["/health", "/health/detailed", "/health/liveness", "/health/readiness"]

        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            elapsed_time = time.time() - start_time

            assert response.status_code == 200
            assert elapsed_time < 1.0

    def test_multiple_health_checks_consistent(self, client: TestClient) -> None:
        """Test that multiple health checks return consistent results."""
        response1 = client.get("/health")
        response2 = client.get("/health")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        assert data1["status"] == data2["status"]
        assert data1["version"] == data2["version"]

    def test_uptime_increases_over_time(self, client: TestClient) -> None:
        """Test that uptime increases over time."""
        import time

        response1 = client.get("/health")
        data1 = response1.json()
        uptime1 = data1["uptime_seconds"]

        time.sleep(0.1)

        response2 = client.get("/health")
        data2 = response2.json()
        uptime2 = data2["uptime_seconds"]

        assert uptime2 > uptime1
