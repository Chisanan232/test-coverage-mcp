"""Unit tests for comparison MCP tools."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.mcp_server.app import mcp_factory
from test_coverage_mcp.mcp_server.tools.commit_summary import (
    get_commit_coverage_summary,
)
from test_coverage_mcp.mcp_server.tools.comparison import (
    compare_coverage_between_refs,
)


@pytest.fixture(autouse=True)
def reset_mcp_factory() -> None:
    """Reset MCP factory before each test."""
    mcp_factory.reset()
    mcp_factory.create()
    yield
    mcp_factory.reset()


@patch("test_coverage_mcp.mcp_server.tools.commit_summary.ProviderDiscoveryService")
def test_get_commit_coverage_summary_success(mock_discovery_class: MagicMock) -> None:
    """Test get_commit_coverage_summary with valid input."""
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

    mock_provider = MagicMock()
    mock_provider.get_metadata.return_value = mock_metadata
    mock_discovery.get_provider.return_value = mock_provider

    result = get_commit_coverage_summary("owner/repo", "abc123def456")

    assert "repo_slug" in result
    assert "commit_sha" in result
    assert "coverage_summary" in result
    assert "file_breakdown" in result
    assert "uploads_metadata" in result
    assert "execution_metadata" in result
    assert result["repo_slug"] == "owner/repo"
    assert result["commit_sha"] == "abc123def456"


def test_get_commit_coverage_summary_invalid_slug() -> None:
    """Test get_commit_coverage_summary with invalid repo slug."""
    result = get_commit_coverage_summary("invalid_slug", "abc123def456")

    assert "error" in result
    assert "InvalidRepositorySlugError" in result.get("error_type", "")


def test_get_commit_coverage_summary_invalid_sha() -> None:
    """Test get_commit_coverage_summary with invalid commit SHA."""
    result = get_commit_coverage_summary("owner/repo", "abc")

    assert "error" in result
    assert "InvalidCommitShaError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.commit_summary.ProviderDiscoveryService")
def test_get_commit_coverage_summary_provider_not_found(mock_discovery_class: MagicMock) -> None:
    """Test get_commit_coverage_summary with nonexistent provider."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = None

    result = get_commit_coverage_summary("owner/repo", "abc123def456", provider="nonexistent")

    assert "error" in result
    assert "ProviderNotFoundError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.comparison.CoverageComparisonService")
@patch("test_coverage_mcp.mcp_server.tools.comparison.ProviderDiscoveryService")
def test_compare_coverage_between_refs_success(mock_discovery_class: MagicMock, mock_comparison_class: MagicMock) -> None:
    """Test compare_coverage_between_refs with valid input."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = MagicMock()

    mock_comparison = MagicMock()
    mock_comparison_class.return_value = mock_comparison
    mock_comparison.compare_refs.return_value = {
        "base_ref": "main",
        "head_ref": "feature",
        "base_coverage": 85.0,
        "head_coverage": 87.0,
        "delta_percentage": 2.0,
        "improved": True,
        "regression": False,
        "provider_results": {},
    }
    mock_comparison.detect_regressions.return_value = {
        "has_regression": False,
        "delta_percentage": 2.0,
        "threshold": 1.0,
        "severity": "none",
        "base_coverage": 85.0,
        "head_coverage": 87.0,
    }
    mock_comparison.detect_improvements.return_value = {
        "has_improvement": True,
        "delta_percentage": 2.0,
        "improvement_percentage": 2.35,
        "base_coverage": 85.0,
        "head_coverage": 87.0,
    }

    result = compare_coverage_between_refs("owner/repo", "main", "feature")

    assert "repo_slug" in result
    assert "base_ref" in result
    assert "head_ref" in result
    assert "coverage_delta" in result
    assert "regression_analysis" in result
    assert "improvement_analysis" in result
    assert "execution_metadata" in result
    assert result["repo_slug"] == "owner/repo"
    assert result["base_ref"] == "main"
    assert result["head_ref"] == "feature"


def test_compare_coverage_between_refs_invalid_slug():
    """Test compare_coverage_between_refs with invalid repo slug."""
    result = compare_coverage_between_refs("invalid_slug", "main", "feature")

    assert "error" in result
    assert "InvalidRepositorySlugError" in result.get("error_type", "")


def test_compare_coverage_between_refs_same_refs():
    """Test compare_coverage_between_refs with same base and head refs."""
    result = compare_coverage_between_refs("owner/repo", "main", "main")

    assert "error" in result
    assert "InvalidReferenceError" in result.get("error_type", "")


def test_compare_coverage_between_refs_missing_refs():
    """Test compare_coverage_between_refs with missing references."""
    result = compare_coverage_between_refs("owner/repo", "", "feature")

    assert "error" in result
    assert "InvalidReferenceError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.comparison.ProviderDiscoveryService")
def test_compare_coverage_between_refs_provider_not_found(mock_discovery_class):
    """Test compare_coverage_between_refs with nonexistent provider."""
    mock_discovery = MagicMock()
    mock_discovery_class.return_value = mock_discovery
    mock_discovery.get_provider.return_value = None

    result = compare_coverage_between_refs(
        "owner/repo", "main", "feature", provider="nonexistent"
    )

    assert "error" in result
    assert "ProviderNotFoundError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.commit_summary.ProviderDiscoveryService")
def test_get_commit_coverage_summary_error_handling(mock_discovery_class):
    """Test get_commit_coverage_summary error handling."""
    mock_discovery_class.side_effect = Exception("Discovery failed")

    result = get_commit_coverage_summary("owner/repo", "abc123def456")

    assert "error" in result
    assert "CommitCoverageSummaryError" in result.get("error_type", "")


@patch("test_coverage_mcp.mcp_server.tools.comparison.CoverageComparisonService")
@patch("test_coverage_mcp.mcp_server.tools.comparison.ProviderDiscoveryService")
def test_compare_coverage_between_refs_error_handling(mock_discovery_class, mock_comparison_class):
    """Test compare_coverage_between_refs error handling."""
    mock_discovery_class.side_effect = Exception("Comparison failed")

    result = compare_coverage_between_refs("owner/repo", "main", "feature")

    assert "error" in result
    assert "CoverageComparisonError" in result.get("error_type", "")
