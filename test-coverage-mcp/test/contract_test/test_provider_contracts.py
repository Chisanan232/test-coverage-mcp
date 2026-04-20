"""Contract tests for provider interface compliance."""

from unittest.mock import MagicMock

import pytest

from test_coverage_mcp.domain import (
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)


class ProviderContractTests:
    """Base class for provider contract tests."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance for testing."""
        raise NotImplementedError("Subclasses must implement provider fixture")

    def test_provider_has_get_metadata_method(self, provider):
        """Test that provider implements get_metadata method."""
        assert hasattr(provider, "get_metadata")
        assert callable(provider.get_metadata)

    def test_get_metadata_returns_provider_metadata(self, provider):
        """Test that get_metadata returns ProviderMetadata."""
        metadata = provider.get_metadata()
        assert isinstance(metadata, ProviderMetadata)

    def test_metadata_has_required_fields(self, provider):
        """Test that metadata contains all required fields."""
        metadata = provider.get_metadata()

        assert hasattr(metadata, "name")
        assert hasattr(metadata, "version")
        assert hasattr(metadata, "description")
        assert hasattr(metadata, "supported_capabilities")
        assert hasattr(metadata, "support_levels")
        assert hasattr(metadata, "analysis_depths")

    def test_metadata_name_is_string(self, provider):
        """Test that metadata name is a string."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.name, str)
        assert len(metadata.name) > 0

    def test_metadata_version_is_string(self, provider):
        """Test that metadata version is a string."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.version, str)
        assert len(metadata.version) > 0

    def test_metadata_description_is_string(self, provider):
        """Test that metadata description is a string."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.description, str)

    def test_metadata_capabilities_is_list(self, provider):
        """Test that supported_capabilities is a list."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.supported_capabilities, list)

    def test_metadata_capabilities_are_valid(self, provider):
        """Test that all capabilities are valid ProviderCapability values."""
        metadata = provider.get_metadata()
        for capability in metadata.supported_capabilities:
            assert isinstance(capability, ProviderCapability)

    def test_metadata_support_levels_is_dict(self, provider):
        """Test that support_levels is a dictionary."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.support_levels, dict)

    def test_metadata_support_levels_keys_are_capabilities(self, provider):
        """Test that support_levels keys are valid capabilities."""
        metadata = provider.get_metadata()
        for capability in metadata.support_levels.keys():
            assert isinstance(capability, ProviderCapability)

    def test_metadata_support_levels_values_are_support_level(self, provider):
        """Test that support_levels values are SupportLevel."""
        metadata = provider.get_metadata()
        for level in metadata.support_levels.values():
            assert isinstance(level, SupportLevel)

    def test_metadata_analysis_depths_is_list(self, provider):
        """Test that analysis_depths is a list."""
        metadata = provider.get_metadata()
        assert isinstance(metadata.analysis_depths, list)

    def test_provider_has_health_check_method(self, provider):
        """Test that provider implements health_check method."""
        assert hasattr(provider, "health_check")
        assert callable(provider.health_check)

    def test_health_check_returns_provider_health(self, provider):
        """Test that health_check returns ProviderHealth."""
        health = provider.health_check()
        assert isinstance(health, ProviderHealth)

    def test_health_has_required_fields(self, provider):
        """Test that health contains all required fields."""
        health = provider.health_check()

        assert hasattr(health, "is_healthy")
        assert hasattr(health, "last_check")
        assert hasattr(health, "error_message")
        assert hasattr(health, "response_time_ms")

    def test_health_is_healthy_is_boolean(self, provider):
        """Test that is_healthy is a boolean."""
        health = provider.health_check()
        assert isinstance(health.is_healthy, bool)

    def test_health_last_check_is_string(self, provider):
        """Test that last_check is a string."""
        health = provider.health_check()
        assert isinstance(health.last_check, str)

    def test_health_response_time_is_numeric(self, provider):
        """Test that response_time_ms is numeric."""
        health = provider.health_check()
        assert isinstance(health.response_time_ms, (int, float))
        assert health.response_time_ms >= 0

    def test_health_error_message_is_string_or_none(self, provider):
        """Test that error_message is string or None."""
        health = provider.health_check()
        assert health.error_message is None or isinstance(health.error_message, str)

    def test_health_error_message_only_when_unhealthy(self, provider):
        """Test that error_message is only set when unhealthy."""
        health = provider.health_check()
        if health.is_healthy:
            assert health.error_message is None
        else:
            assert health.error_message is not None

    def test_provider_consistency_across_calls(self, provider):
        """Test that provider returns consistent metadata."""
        metadata1 = provider.get_metadata()
        metadata2 = provider.get_metadata()

        assert metadata1.name == metadata2.name
        assert metadata1.version == metadata2.version
        assert metadata1.supported_capabilities == metadata2.supported_capabilities

    def test_provider_capabilities_match_support_levels(self, provider):
        """Test that all capabilities have support levels defined."""
        metadata = provider.get_metadata()

        for capability in metadata.supported_capabilities:
            assert capability in metadata.support_levels


class TestMockProviderCompliance(ProviderContractTests):
    """Test that mock provider complies with provider contract."""

    @pytest.fixture
    def provider(self):
        """Create a mock provider."""
        provider = MagicMock()
        provider.get_metadata.return_value = ProviderMetadata(
            name="mock_provider",
            version="1.0.0",
            description="Mock provider for testing",
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


class TestProviderCapabilityContract:
    """Test provider capability contract."""

    def test_repository_summary_capability_exists(self):
        """Test that REPOSITORY_SUMMARY capability exists."""
        assert hasattr(ProviderCapability, "REPOSITORY_SUMMARY")

    def test_file_coverage_capability_exists(self):
        """Test that FILE_COVERAGE capability exists."""
        assert hasattr(ProviderCapability, "FILE_COVERAGE")

    def test_coverage_delta_capability_exists(self):
        """Test that COVERAGE_DELTA capability exists."""
        assert hasattr(ProviderCapability, "COVERAGE_DELTA")

    def test_coverage_trends_capability_exists(self):
        """Test that COVERAGE_TRENDS capability exists."""
        assert hasattr(ProviderCapability, "COVERAGE_TRENDS")

    def test_all_capabilities_are_enum_members(self):
        """Test that all capabilities are ProviderCapability enum members."""
        for capability in ProviderCapability:
            assert isinstance(capability, ProviderCapability)


class TestSupportLevelContract:
    """Test support level contract."""

    def test_basic_support_level_exists(self):
        """Test that BASIC support level exists."""
        assert hasattr(SupportLevel, "BASIC")

    def test_advanced_support_level_exists(self):
        """Test that ADVANCED support level exists."""
        assert hasattr(SupportLevel, "ADVANCED")

    def test_enhanced_support_level_exists(self):
        """Test that ENHANCED support level exists."""
        assert hasattr(SupportLevel, "ENHANCED")

    def test_all_support_levels_are_enum_members(self):
        """Test that all support levels are SupportLevel enum members."""
        for level in SupportLevel:
            assert isinstance(level, SupportLevel)


class TestProviderMetadataContract:
    """Test ProviderMetadata contract."""

    def test_provider_metadata_instantiation(self):
        """Test that ProviderMetadata can be instantiated."""
        metadata = ProviderMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )
        assert metadata.name == "test"

    def test_provider_metadata_with_multiple_capabilities(self):
        """Test ProviderMetadata with multiple capabilities."""
        metadata = ProviderMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
                ProviderCapability.COVERAGE_DELTA,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
                ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_DELTA: SupportLevel.BASIC,
            },
            analysis_depths=[],
        )
        assert len(metadata.supported_capabilities) == 3


class TestProviderHealthContract:
    """Test ProviderHealth contract."""

    def test_provider_health_healthy_instantiation(self):
        """Test creating healthy provider health."""
        health = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )
        assert health.is_healthy is True
        assert health.error_message is None

    def test_provider_health_unhealthy_instantiation(self):
        """Test creating unhealthy provider health."""
        health = ProviderHealth(
            is_healthy=False,
            last_check="2024-01-01T00:00:00Z",
            error_message="Connection timeout",
            response_time_ms=5000.0,
        )
        assert health.is_healthy is False
        assert health.error_message == "Connection timeout"

    def test_provider_health_response_time_validation(self):
        """Test that response time is reasonable."""
        health = ProviderHealth(
            is_healthy=True,
            last_check="2024-01-01T00:00:00Z",
            error_message=None,
            response_time_ms=100.0,
        )
        assert 0 <= health.response_time_ms <= 60000  # 0-60 seconds


class TestProviderInterfaceContract:
    """Test overall provider interface contract."""

    def test_provider_must_implement_get_metadata(self):
        """Test that provider interface requires get_metadata."""
        provider = MagicMock()
        assert hasattr(provider, "get_metadata") or callable(getattr(provider, "get_metadata", None))

    def test_provider_must_implement_health_check(self):
        """Test that provider interface requires health_check."""
        provider = MagicMock()
        assert hasattr(provider, "health_check") or callable(getattr(provider, "health_check", None))

    def test_provider_metadata_must_be_consistent(self):
        """Test that provider metadata is consistent."""
        provider = MagicMock()
        provider.get_metadata.return_value = ProviderMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[],
        )

        # Multiple calls should return same metadata
        meta1 = provider.get_metadata()
        meta2 = provider.get_metadata()
        assert meta1.name == meta2.name
