"""End-to-end tests for MCP tools."""

from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.registry import ProviderRegistry


@pytest.fixture(autouse=True)
def reset_mcp_factory() -> Generator[None, None, None]:
    """Reset MCP factory before each test."""
    mcp_factory.reset()
    yield
    mcp_factory.reset()


@pytest.fixture
def mock_registry() -> ProviderRegistry:
    """Create a mock registry."""
    registry = ProviderRegistry()
    registry.clear()
    return registry


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock provider."""
    provider = MagicMock()
    provider.get_metadata.return_value = ProviderMetadata(
        name="test_provider",
        version="1.0.0",
        description="Test provider",
        supported_capabilities=[
            ProviderCapability.REPOSITORY_SUMMARY,
            ProviderCapability.FILE_COVERAGE,
            ProviderCapability.COVERAGE_DELTA,
        ],
        support_levels={
            ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            ProviderCapability.FILE_COVERAGE: SupportLevel.BASIC,
            ProviderCapability.COVERAGE_DELTA: SupportLevel.ADVANCED,
        },
        analysis_depths=[],
    )
    provider.health_check.return_value = ProviderHealth(
        is_healthy=True,
        last_check="2024-01-01T00:00:00Z",
        error_message=None,
        response_time_ms=100.0,
    )
    return provider


class TestMCPServerE2E:
    """End-to-end tests for MCP server."""

    def test_mcp_server_creation(self) -> None:
        """Test that MCP server can be created."""
        server = mcp_factory.create()
        assert server is not None
        assert server.name == "TemplateMCPServer"

    def test_mcp_server_singleton(self) -> None:
        """Test that MCP server is a singleton."""
        server1 = mcp_factory.create()
        server2 = mcp_factory.get()
        assert server1 is server2

    def test_mcp_server_reset(self) -> None:
        """Test that MCP server can be reset."""
        server1 = mcp_factory.create()
        mcp_factory.reset()
        server2 = mcp_factory.create()
        assert server1 is not server2

    def test_mcp_server_has_sse_app(self) -> None:
        """Test that MCP server can create SSE app."""
        server = mcp_factory.create()
        sse_app = server.sse_app()
        assert sse_app is not None

    def test_mcp_server_has_http_app(self) -> None:
        """Test that MCP server can create HTTP app."""
        server = mcp_factory.create()
        http_app = server.streamable_http_app()
        assert http_app is not None

    @patch("test_coverage_mcp.mcp_server.app.FastMCP.run")
    def test_mcp_server_stdio_transport(self, mock_run: MagicMock) -> None:
        """Test that MCP server can run with stdio transport."""
        server = mcp_factory.create()
        server.run(transport="stdio")
        mock_run.assert_called_once_with(transport="stdio")


class TestCoverageProvidersToolE2E:
    """End-to-end tests for coverage providers tool."""

    @patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
    def test_list_coverage_providers_tool(self, mock_discovery_class: MagicMock) -> None:
        """Test list_coverage_providers tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.coverage_providers import (
            list_coverage_providers,
        )

        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        mock_metadata = ProviderMetadata(
            name="test_provider",
            version="1.0.0",
            description="Test provider",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        mock_discovery.list_providers.return_value = {"test_provider": mock_metadata}
        mock_discovery.get_provider_health.return_value = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )
        mock_discovery.get_all_health_status.return_value = {
            "test_provider": ProviderHealth(
                is_healthy=True,
                last_check="2024-01-01T00:00:00Z",
                error_message=None,
                response_time_ms=100.0,
            )
        }

        result = list_coverage_providers(include_capabilities=False, include_health=False)

        assert isinstance(result, dict)
        assert "providers" in result

    @patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
    def test_describe_coverage_provider_tool(self, mock_discovery_class: MagicMock) -> None:
        """Test describe_coverage_provider tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.coverage_providers import (
            describe_coverage_provider,
        )

        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        mock_metadata = ProviderMetadata(
            name="test_provider",
            version="1.0.0",
            description="Test provider",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        mock_discovery.get_provider.return_value = MagicMock()
        mock_discovery.get_provider.return_value.get_metadata.return_value = mock_metadata
        mock_discovery.get_provider_health.return_value = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )

        result = describe_coverage_provider("test_provider")

        assert isinstance(result, dict)
        assert "name" in result


class TestRepositoryHealthToolE2E:
    """End-to-end tests for repository health tool."""

    @patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
    def test_get_repository_health_tool(self, mock_health_class: MagicMock) -> None:
        """Test get_repository_test_health tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.repository_health import (
            get_repository_test_health,
        )

        mock_health = MagicMock()
        mock_health_class.return_value = mock_health

        mock_health.aggregate_coverage_metrics.return_value = {
            "providers_queried": 1,
            "providers_succeeded": 1,
            "average_coverage": 85.0,
            "coverage_range": {"min": 85.0, "max": 85.0},
        }
        mock_health.identify_risks.return_value = {
            "risk_level": "low",
            "coverage_below_threshold": False,
            "recommendations": ["Maintain current coverage level"],
        }

        result = get_repository_test_health(
            repo_slug="owner/repo",
            provider="test_provider",
            threshold=80.0,
        )

        assert isinstance(result, dict)


class TestPRAnalysisToolsE2E:
    """End-to-end tests for PR analysis tools."""

    def test_analyze_pr_coverage_tool(self) -> None:
        """Test analyze_pr_coverage_risk tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.analyze_pr_risk import (
            analyze_pr_coverage_risk,
        )

        # Test with valid inputs
        result = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="test_provider",
            base_ref="main",
            head_ref="feature",
        )

        # Should return a dict with analysis results
        assert isinstance(result, dict)


class TestLowCoverageFilesToolE2E:
    """End-to-end tests for low coverage files tool."""

    def test_identify_low_coverage_files_tool(self) -> None:
        """Test find_low_coverage_files tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.find_low_coverage_files import (
            find_low_coverage_files,
        )

        # Test with valid inputs
        result = find_low_coverage_files(
            repo_slug="owner/repo",
            provider="test_provider",
            ref="main",
            threshold=50.0,
        )

        # Should return a dict with results
        assert isinstance(result, dict)


class TestTestRecommendationToolE2E:
    """End-to-end tests for test recommendation tool."""

    def test_recommend_test_plan_tool(self) -> None:
        """Test recommend_test_plan tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.recommend_test_plan import (
            recommend_test_plan,
        )

        # Test with valid inputs
        result = recommend_test_plan(
            repo_slug="owner/repo",
            provider="test_provider",
        )

        # Should return a dict with results
        assert isinstance(result, dict)


class TestConfigDiagnosisToolE2E:
    """End-to-end tests for config diagnosis tool."""

    def test_diagnose_coverage_config_tool(self) -> None:
        """Test diagnose_coverage_configuration tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration import (
            diagnose_coverage_configuration,
        )

        # Test with valid inputs
        result = diagnose_coverage_configuration(
            repo_slug="owner/repo",
            provider="test_provider",
        )

        # Should return a dict with results
        assert isinstance(result, dict)


class TestExcludableCodeToolE2E:
    """End-to-end tests for excludable code tool."""

    def test_find_excludable_code_tool(self) -> None:
        """Test identify_excludable_code_candidates tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.identify_excludable_code_candidates import (
            identify_excludable_code_candidates,
        )

        # Test with valid inputs
        result = identify_excludable_code_candidates(
            repo_slug="owner/repo",
            provider="test_provider",
            ref="main",
        )

        # Should return a dict with results
        assert isinstance(result, dict)


class TestMultiToolWorkflowE2E:
    """End-to-end tests for multi-tool workflows."""

    def test_complete_pr_analysis_workflow(self) -> None:
        """Test complete PR analysis workflow."""
        from test_coverage_mcp.mcp_server.tools.coverage_providers import (
            list_coverage_providers,
        )
        from test_coverage_mcp.mcp_server.tools.analyze_pr_risk import (
            analyze_pr_coverage_risk,
        )

        # Execute workflow
        providers = list_coverage_providers()
        assert isinstance(providers, dict)

        pr_analysis = analyze_pr_coverage_risk(
            repo_slug="owner/repo",
            provider="test_provider",
            base_ref="main",
            head_ref="feature",
        )
        assert isinstance(pr_analysis, dict)

    def test_repository_health_workflow(self) -> None:
        """Test repository health analysis workflow."""
        from test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration import (
            diagnose_coverage_configuration,
        )
        from test_coverage_mcp.mcp_server.tools.repository_health import (
            get_repository_test_health,
        )

        # Execute workflow
        health = get_repository_test_health(
            repo_slug="owner/repo",
            provider="test_provider",
        )
        assert isinstance(health, dict)

        diagnosis = diagnose_coverage_configuration(
            repo_slug="owner/repo",
            provider="test_provider",
        )
        assert isinstance(diagnosis, dict)
