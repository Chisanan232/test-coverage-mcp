"""End-to-end tests for MCP tools."""

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
def reset_mcp_factory():
    """Reset MCP factory before each test."""
    mcp_factory.reset()
    yield
    mcp_factory.reset()


@pytest.fixture
def mock_registry():
    """Create a mock registry."""
    registry = ProviderRegistry()
    registry.clear()
    return registry


@pytest.fixture
def mock_provider():
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

    def test_mcp_server_creation(self):
        """Test that MCP server can be created."""
        server = mcp_factory.create()
        assert server is not None
        assert server.name == "TemplateMCPServer"

    def test_mcp_server_singleton(self):
        """Test that MCP server is a singleton."""
        server1 = mcp_factory.create()
        server2 = mcp_factory.get()
        assert server1 is server2

    def test_mcp_server_reset(self):
        """Test that MCP server can be reset."""
        server1 = mcp_factory.create()
        mcp_factory.reset()
        server2 = mcp_factory.create()
        assert server1 is not server2

    def test_mcp_server_has_sse_app(self):
        """Test that MCP server can create SSE app."""
        server = mcp_factory.create()
        sse_app = server.sse_app()
        assert sse_app is not None

    def test_mcp_server_has_http_app(self):
        """Test that MCP server can create HTTP app."""
        server = mcp_factory.create()
        http_app = server.streamable_http_app()
        assert http_app is not None

    @patch("test_coverage_mcp.mcp_server.app.FastMCP.run")
    def test_mcp_server_stdio_transport(self, mock_run):
        """Test that MCP server can run with stdio transport."""
        server = mcp_factory.create()
        server.run(transport="stdio")
        mock_run.assert_called_once_with(transport="stdio")


class TestCoverageProvidersToolE2E:
    """End-to-end tests for coverage providers tool."""

    @patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
    def test_list_coverage_providers_tool(self, mock_discovery_class):
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

        assert isinstance(result, str)
        assert "test_provider" in result

    @patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
    def test_describe_coverage_provider_tool(self, mock_discovery_class):
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

        assert isinstance(result, str)
        assert "test_provider" in result


class TestRepositoryHealthToolE2E:
    """End-to-end tests for repository health tool."""

    @patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
    def test_get_repository_health_tool(self, mock_health_class):
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

        result = get_repository_test_health("owner", "repo", threshold=80.0)

        assert isinstance(result, str)
        assert "owner" in result or "repo" in result


class TestPRAnalysisToolsE2E:
    """End-to-end tests for PR analysis tools."""

    @patch("test_coverage_mcp.mcp_server.tools.analyze_pr_risk.CoverageComparisonService")
    @patch("test_coverage_mcp.mcp_server.tools.analyze_pr_risk.CoverageRiskAnalysisService")
    def test_analyze_pr_coverage_tool(self, mock_risk_class, mock_comparison_class):
        """Test analyze_pr_coverage tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.analyze_pr_risk import analyze_pr_coverage

        mock_comparison = MagicMock()
        mock_comparison_class.return_value = mock_comparison
        mock_comparison.compare_refs.return_value = {
            "base_ref": "main",
            "head_ref": "feature",
            "base_coverage": 85.0,
            "head_coverage": 80.0,
            "delta_percentage": -5.0,
            "improved": False,
            "regression": True,
        }

        mock_risk = MagicMock()
        mock_risk_class.return_value = mock_risk
        mock_risk.score_pr_risk.return_value = {
            "risk_level": "high",
            "risk_score": 65.0,
            "coverage_delta": -5.0,
            "changed_code_coverage": 75.0,
            "recommendations": ["Add tests for changed code"],
        }

        result = analyze_pr_coverage("owner", "repo", "main", "feature")

        assert isinstance(result, str)
        assert "main" in result or "feature" in result


class TestLowCoverageFilesToolE2E:
    """End-to-end tests for low coverage files tool."""

    @patch("test_coverage_mcp.mcp_server.tools.find_low_coverage_files.CoverageRiskAnalysisService")
    def test_identify_low_coverage_files_tool(self, mock_risk_class):
        """Test identify_low_coverage_files tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.find_low_coverage_files import (
            identify_low_coverage_files,
        )

        mock_risk = MagicMock()
        mock_risk_class.return_value = mock_risk

        file_coverage = {
            "src/main.py": {"coverage": 30.0, "uncovered_lines": 70, "total_lines": 100},
            "src/utils.py": {"coverage": 85.0, "uncovered_lines": 15, "total_lines": 100},
        }
        mock_risk.identify_high_risk_files.return_value = [
            {
                "file_path": "src/main.py",
                "coverage": 30.0,
                "risk_score": 70.0,
                "recommendations": ["Add tests for main.py"],
            }
        ]

        result = identify_low_coverage_files(file_coverage, risk_threshold=50.0)

        assert isinstance(result, str)
        assert "src/main.py" in result


class TestTestRecommendationToolE2E:
    """End-to-end tests for test recommendation tool."""

    @patch("test_coverage_mcp.mcp_server.tools.recommend_test_plan.TestRecommendationService")
    def test_recommend_test_plan_tool(self, mock_recommendation_class):
        """Test recommend_test_plan tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.recommend_test_plan import (
            recommend_test_plan,
        )

        mock_recommendation = MagicMock()
        mock_recommendation_class.return_value = mock_recommendation

        uncovered_regions = [
            {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 20,
                "region_type": "function",
                "risk_level": "high",
                "lines_count": 10,
            }
        ]
        mock_recommendation.recommend_tests.return_value = [
            MagicMock(
                file_path="src/main.py",
                start_line=10,
                end_line=20,
                region_type="function",
                test_types=["unit", "integration"],
                scenarios=["normal case", "edge case"],
                priority="high",
                rationale="Critical function needs testing",
            )
        ]

        result = recommend_test_plan(uncovered_regions)

        assert isinstance(result, str)
        assert "src/main.py" in result


class TestConfigDiagnosisToolE2E:
    """End-to-end tests for config diagnosis tool."""

    @patch("test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration.CoverageConfigDiagnosisService")
    def test_diagnose_coverage_config_tool(self, mock_config_class):
        """Test diagnose_coverage_config tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration import (
            diagnose_coverage_config,
        )

        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        file_coverage = {
            "src/main.py": {"coverage": 80},
            "tests/test_main.py": {"coverage": 0},
        }
        mock_config.diagnose_config.return_value = MagicMock(
            repo_owner="owner",
            repo_name="repo",
            config_valid=True,
            summary="Configuration is valid",
            issues=[],
            suggestions=[],
        )

        result = diagnose_coverage_config("owner", "repo", file_coverage, 85.0)

        assert isinstance(result, str)
        assert "owner" in result or "repo" in result


class TestExcludableCodeToolE2E:
    """End-to-end tests for excludable code tool."""

    @patch("test_coverage_mcp.mcp_server.tools.identify_excludable_code_candidates.ExcludableCodeCandidateService")
    def test_find_excludable_code_tool(self, mock_excludable_class):
        """Test find_excludable_code tool end-to-end."""
        from test_coverage_mcp.mcp_server.tools.identify_excludable_code_candidates import (
            find_excludable_code,
        )

        mock_excludable = MagicMock()
        mock_excludable_class.return_value = mock_excludable

        files = [
            {
                "path": "src/generated.pb2.py",
                "content": "# AUTO-GENERATED",
                "coverage": {"hits": 0, "total_lines": 100, "covered_lines": 0},
            },
            {
                "path": "src/main.py",
                "content": "def func(): pass",
                "coverage": {"hits": 50, "total_lines": 100, "covered_lines": 50},
            },
        ]
        mock_excludable.find_excludable_candidates.return_value = [
            {
                "file_path": "src/generated.pb2.py",
                "excludability_score": 0.85,
                "should_exclude": True,
                "reasons": ["Generated code"],
            }
        ]

        result = find_excludable_code(files, min_confidence=0.3)

        assert isinstance(result, str)
        assert "src/generated.pb2.py" in result


class TestMultiToolWorkflowE2E:
    """End-to-end tests for multi-tool workflows."""

    @patch("test_coverage_mcp.mcp_server.tools.coverage_providers.ProviderDiscoveryService")
    @patch("test_coverage_mcp.mcp_server.tools.analyze_pr_risk.CoverageComparisonService")
    @patch("test_coverage_mcp.mcp_server.tools.analyze_pr_risk.CoverageRiskAnalysisService")
    @patch("test_coverage_mcp.mcp_server.tools.find_low_coverage_files.CoverageRiskAnalysisService")
    def test_complete_pr_analysis_workflow(
        self,
        mock_risk_class2,
        mock_risk_class,
        mock_comparison_class,
        mock_discovery_class,
    ):
        """Test complete PR analysis workflow."""
        from test_coverage_mcp.mcp_server.tools.coverage_providers import (
            list_coverage_providers,
        )
        from test_coverage_mcp.mcp_server.tools.analyze_pr_risk import analyze_pr_coverage

        # Setup mocks
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

        mock_comparison = MagicMock()
        mock_comparison_class.return_value = mock_comparison
        mock_comparison.compare_refs.return_value = {
            "base_ref": "main",
            "head_ref": "feature",
            "base_coverage": 85.0,
            "head_coverage": 80.0,
            "delta_percentage": -5.0,
        }

        mock_risk = MagicMock()
        mock_risk_class.return_value = mock_risk
        mock_risk.score_pr_risk.return_value = {
            "risk_level": "high",
            "risk_score": 65.0,
        }

        # Execute workflow
        providers = list_coverage_providers()
        assert isinstance(providers, str)

        pr_analysis = analyze_pr_coverage("owner", "repo", "main", "feature")
        assert isinstance(pr_analysis, str)

    @patch("test_coverage_mcp.mcp_server.tools.repository_health.RepositoryHealthService")
    @patch("test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration.CoverageConfigDiagnosisService")
    def test_repository_health_workflow(self, mock_config_class, mock_health_class):
        """Test repository health analysis workflow."""
        from test_coverage_mcp.mcp_server.tools.diagnose_coverage_configuration import (
            diagnose_coverage_config,
        )
        from test_coverage_mcp.mcp_server.tools.repository_health import (
            get_repository_test_health,
        )

        # Setup mocks
        mock_health = MagicMock()
        mock_health_class.return_value = mock_health
        mock_health.aggregate_coverage_metrics.return_value = {
            "average_coverage": 85.0,
        }
        mock_health.identify_risks.return_value = {
            "risk_level": "low",
        }

        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.diagnose_config.return_value = MagicMock(
            config_valid=True,
            summary="Configuration is valid",
        )

        # Execute workflow
        health = get_repository_test_health("owner", "repo")
        assert isinstance(health, str)

        diagnosis = diagnose_coverage_config("owner", "repo", {}, 85.0)
        assert isinstance(diagnosis, str)
