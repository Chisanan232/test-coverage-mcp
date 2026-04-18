"""Tests for Codecov provider."""

import pytest

from test_coverage_mcp.domain import ProviderCapability, SupportLevel
from test_coverage_mcp.providers.codecov import CodecovProvider


class TestCodecovProvider:
    """Tests for CodecovProvider."""

    def test_provider_metadata(self) -> None:
        """Test provider metadata."""
        provider = CodecovProvider(api_token="test-token")
        metadata = provider.get_metadata()

        assert metadata.name == "codecov"
        assert metadata.version == "1.0.0"
        assert len(metadata.supported_capabilities) == 14

    def test_supports_all_capabilities(self) -> None:
        """Test that provider supports all 14 capabilities."""
        provider = CodecovProvider(api_token="test-token")

        capabilities = [
            ProviderCapability.REPOSITORY_SUMMARY,
            ProviderCapability.FILE_COVERAGE,
            ProviderCapability.COVERAGE_DELTA,
            ProviderCapability.UNCOVERED_REGIONS,
            ProviderCapability.TEST_RECOMMENDATIONS,
            ProviderCapability.COVERAGE_TRENDS,
            ProviderCapability.COVERAGE_CONFIG_DIAGNOSIS,
            ProviderCapability.COVERAGE_GOALS,
            ProviderCapability.CROSS_BRANCH_COMPARISON,
            ProviderCapability.PULL_REQUEST_ANALYSIS,
            ProviderCapability.COVERAGE_METRICS,
            ProviderCapability.RISK_ASSESSMENT,
            ProviderCapability.QUALITY_GATES,
            ProviderCapability.HISTORICAL_ANALYSIS,
        ]

        for capability in capabilities:
            assert provider.supports_capability(capability)

    def test_support_levels(self) -> None:
        """Test support levels for capabilities."""
        provider = CodecovProvider(api_token="test-token")

        assert (
            provider.get_support_level(ProviderCapability.REPOSITORY_SUMMARY)
            == SupportLevel.ADVANCED
        )
        assert (
            provider.get_support_level(ProviderCapability.FILE_COVERAGE)
            == SupportLevel.ADVANCED
        )
        assert (
            provider.get_support_level(ProviderCapability.COVERAGE_CONFIG_DIAGNOSIS)
            == SupportLevel.BASIC
        )

    def test_health_check(self) -> None:
        """Test health check."""
        provider = CodecovProvider(api_token="test-token")
        health = provider.health_check()

        assert health.last_check is not None
        assert health.response_time_ms >= 0
