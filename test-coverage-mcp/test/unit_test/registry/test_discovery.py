"""Tests for plugin discovery."""

import pytest

from test_coverage_mcp.domain import (
    AnalysisDepth,
    CoverageProvider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.registry.discovery import (
    ProviderDiscoveryError,
    check_version_compatibility,
    discover_providers,
    get_provider_versions,
    load_provider,
)


class TestProvider(CoverageProvider):
    """Test provider for discovery tests."""

    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        return ProviderMetadata(
            name="test-provider",
            version="1.0.0",
            description="Test provider",
            supported_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
            },
            analysis_depths=[AnalysisDepth.REPOSITORY],
        )

    def health_check(self) -> ProviderHealth:
        """Check provider health."""
        return ProviderHealth(
            is_healthy=True,
            last_check="2026-04-16T00:00:00Z",
            error_message=None,
            response_time_ms=10.0,
        )

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if capability is supported."""
        return capability == ProviderCapability.REPOSITORY_SUMMARY

    def get_support_level(self, capability: ProviderCapability) -> SupportLevel | None:
        """Get support level for capability."""
        if capability == ProviderCapability.REPOSITORY_SUMMARY:
            return SupportLevel.ADVANCED
        return None


class TestDiscovery:
    """Tests for plugin discovery."""

    def test_discover_providers(self) -> None:
        """Test discovering providers via entry points."""
        # This test will pass even if no providers are discovered
        # since we're testing the discovery mechanism, not actual providers
        providers = discover_providers()
        assert isinstance(providers, dict)

    def test_load_provider_success(self) -> None:
        """Test loading a provider from module."""
        # Load the test provider from this module
        provider = load_provider(
            "test.unit_test.registry.test_discovery", "TestProvider"
        )
        assert isinstance(provider, CoverageProvider)
        assert provider.get_metadata().name == "test-provider"

    def test_load_provider_invalid_module(self) -> None:
        """Test loading from invalid module raises error."""
        with pytest.raises(ProviderDiscoveryError):
            load_provider("nonexistent.module", "TestProvider")

    def test_load_provider_invalid_class(self) -> None:
        """Test loading invalid class raises error."""
        with pytest.raises(ProviderDiscoveryError):
            load_provider(
                "test.unit_test.registry.test_discovery", "NonexistentClass"
            )

    def test_load_provider_not_coverage_provider(self) -> None:
        """Test loading non-CoverageProvider class raises error."""
        with pytest.raises(ProviderDiscoveryError):
            load_provider("test.unit_test.registry.test_discovery", "str")

    def test_get_provider_versions(self) -> None:
        """Test getting versions of providers."""
        provider1 = TestProvider()
        provider2 = TestProvider()

        providers = {
            "provider1": provider1,
            "provider2": provider2,
        }

        versions = get_provider_versions(providers)
        assert versions["provider1"] == "1.0.0"
        assert versions["provider2"] == "1.0.0"

    def test_check_version_compatibility_valid(self) -> None:
        """Test version compatibility check with valid version."""
        assert check_version_compatibility("1.0.0", "1.0.0", "2.0.0") is True
        assert check_version_compatibility("1.5.0", "1.0.0", "2.0.0") is True
        assert check_version_compatibility("2.0.0", "1.0.0", "2.0.0") is True

    def test_check_version_compatibility_invalid(self) -> None:
        """Test version compatibility check with invalid version."""
        assert check_version_compatibility("0.9.0", "1.0.0", "2.0.0") is False
        assert check_version_compatibility("2.1.0", "1.0.0", "2.0.0") is False

    def test_check_version_compatibility_invalid_format(self) -> None:
        """Test version compatibility check with invalid format."""
        # Should return True (default) for unparseable versions
        result = check_version_compatibility("invalid", "1.0.0", "2.0.0")
        assert result is True
