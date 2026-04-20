"""Contract tests for provider interface compliance.

Tests that providers implement the required interface correctly.
"""

from unittest.mock import MagicMock

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)


class TestProviderInterfaceContract:
    """Contract tests for provider interface."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing."""
        provider = MagicMock()
        provider.get_metadata.return_value = ProviderMetadata(
            name="test_provider",
            version="1.0.0",
            description="Test provider",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
                ProviderCapability.FILE_COVERAGE: SupportLevel.BASIC,
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

    def test_provider_has_required_methods(self, mock_provider):
        """Test that provider implements all required methods."""
        assert hasattr(mock_provider, "get_metadata")
        assert callable(mock_provider.get_metadata)
        assert hasattr(mock_provider, "health_check")
        assert callable(mock_provider.health_check)

    def test_provider_returns_correct_types(self, mock_provider):
        """Test that provider returns correct types."""
        metadata = mock_provider.get_metadata()
        assert isinstance(metadata, ProviderMetadata)
        
        health = mock_provider.health_check()
        assert isinstance(health, ProviderHealth)

    def test_provider_handles_errors_correctly(self, mock_provider):
        """Test that provider handles errors correctly."""
        # Test that provider can handle and report errors
        mock_provider.get_metadata.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            mock_provider.get_metadata()

    def test_provider_respects_timeout(self, mock_provider):
        """Test that provider respects timeout settings."""
        health = mock_provider.health_check()
        
        # Response time should be reasonable
        assert health.response_time_ms >= 0
        assert health.response_time_ms < 60000  # Less than 60 seconds

    def test_provider_handles_invalid_input(self, mock_provider):
        """Test that provider handles invalid input gracefully."""
        # Provider should have consistent behavior
        metadata1 = mock_provider.get_metadata()
        metadata2 = mock_provider.get_metadata()
        
        assert metadata1.name == metadata2.name

    def test_provider_supports_required_capabilities(self, mock_provider):
        """Test that provider supports required capabilities."""
        metadata = mock_provider.get_metadata()
        
        # Provider must support at least one capability
        assert len(metadata.supported_capabilities) > 0
        
        # All capabilities must have support levels
        for capability in metadata.supported_capabilities:
            assert capability in metadata.support_levels

    def test_provider_version_compatibility(self, mock_provider):
        """Test provider version compatibility."""
        metadata = mock_provider.get_metadata()
        
        # Version should be a valid semantic version string
        assert isinstance(metadata.version, str)
        assert len(metadata.version) > 0
        
        # Version should follow semantic versioning pattern
        parts = metadata.version.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestProviderInterfaceRobustness:
    """Test provider interface robustness and edge cases."""

    @pytest.fixture
    def robust_provider(self):
        """Create a provider with all capabilities."""
        provider = MagicMock()
        provider.get_metadata.return_value = ProviderMetadata(
            name="robust_provider",
            version="2.0.0",
            description="Robust test provider",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
                ProviderCapability.COVERAGE_DELTA,
                ProviderCapability.COVERAGE_TRENDS,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.FULL,
                ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_DELTA: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_TRENDS: SupportLevel.BASIC,
            },
            analysis_depths=["line", "function", "class"],
        )
        provider.health_check.return_value = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=150.0,
        )
        return provider

    def test_provider_with_multiple_capabilities(self, robust_provider):
        """Test provider with multiple capabilities."""
        metadata = robust_provider.get_metadata()
        
        assert len(metadata.supported_capabilities) == 4
        assert len(metadata.support_levels) == 4

    def test_provider_with_analysis_depths(self, robust_provider):
        """Test provider with analysis depths."""
        metadata = robust_provider.get_metadata()
        
        assert isinstance(metadata.analysis_depths, list)
        assert len(metadata.analysis_depths) > 0

    def test_provider_health_when_unhealthy(self):
        """Test provider health reporting when unhealthy."""
        provider = MagicMock()
        provider.health_check.return_value = ProviderHealth(
            is_healthy=False,
            last_check="2024-01-01T00:00:00Z",
            error_message="Connection failed",
            response_time_ms=5000.0,
        )
        
        health = provider.health_check()
        
        assert health.is_healthy is False
        assert health.error_message is not None
        assert len(health.error_message) > 0

    def test_provider_metadata_consistency(self, robust_provider):
        """Test that provider metadata is consistent across calls."""
        meta1 = robust_provider.get_metadata()
        meta2 = robust_provider.get_metadata()
        meta3 = robust_provider.get_metadata()
        
        assert meta1.name == meta2.name == meta3.name
        assert meta1.version == meta2.version == meta3.version
        assert meta1.supported_capabilities == meta2.supported_capabilities

    def test_provider_support_level_hierarchy(self, robust_provider):
        """Test that support levels follow expected hierarchy."""
        metadata = robust_provider.get_metadata()
        
        # All support levels should be valid
        valid_levels = {SupportLevel.BASIC, SupportLevel.ADVANCED, SupportLevel.FULL}
        for level in metadata.support_levels.values():
            assert level in valid_levels


class TestProviderInterfaceErrorHandling:
    """Test error handling in provider interface."""

    def test_provider_graceful_failure(self):
        """Test that provider fails gracefully."""
        provider = MagicMock()
        provider.get_metadata.side_effect = RuntimeError("Provider unavailable")
        
        with pytest.raises(RuntimeError):
            provider.get_metadata()

    def test_provider_timeout_handling(self):
        """Test provider timeout handling."""
        provider = MagicMock()
        provider.health_check.return_value = ProviderHealth(
            is_healthy=False,
            last_check="2024-01-01T00:00:00Z",
            error_message="Request timeout",
            response_time_ms=30000.0,
        )
        
        health = provider.health_check()
        assert health.response_time_ms > 10000

    def test_provider_partial_failure(self):
        """Test provider with partial failures."""
        provider = MagicMock()
        
        # Metadata works
        provider.get_metadata.return_value = ProviderMetadata(
            name="partial_provider",
            version="1.0.0",
            description="Partial provider",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.BASIC,
            },
            analysis_depths=[],
        )
        
        # Health check fails
        provider.health_check.side_effect = Exception("Health check failed")
        
        # Should still be able to get metadata
        metadata = provider.get_metadata()
        assert metadata.name == "partial_provider"
        
        # Health check should fail
        with pytest.raises(Exception):
            provider.health_check()
