"""Tests for provider registry."""

import pytest

from test_coverage_mcp.domain import (
    AnalysisDepth,
    CoverageProvider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.registry import ProviderRegistry


class MockProvider(CoverageProvider):
    """Mock provider for testing."""

    def __init__(self, name: str = "mock-provider", healthy: bool = True):
        """Initialize mock provider."""
        self.name = name
        self.healthy = healthy

    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        return ProviderMetadata(
            name=self.name,
            version="1.0.0",
            description="Mock provider for testing",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
                ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
            },
            analysis_depths=[AnalysisDepth.REPOSITORY, AnalysisDepth.FILE],
        )

    def health_check(self) -> ProviderHealth:
        """Check provider health."""
        return ProviderHealth(
            is_healthy=self.healthy,
            last_check="2026-04-16T00:00:00Z",
            error_message=None if self.healthy else "Mock error",
            response_time_ms=10.0,
        )

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if capability is supported."""
        return capability in self.get_metadata().supported_capabilities

    def get_support_level(self, capability: ProviderCapability) -> SupportLevel | None:
        """Get support level for capability."""
        return self.get_metadata().support_levels.get(capability)


class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        # Get singleton instance and clear it
        self.registry = ProviderRegistry()
        self.registry.clear()

    def test_singleton_pattern(self) -> None:
        """Test that ProviderRegistry is a singleton."""
        registry1 = ProviderRegistry()
        registry2 = ProviderRegistry()
        assert registry1 is registry2

    def test_register_provider(self) -> None:
        """Test registering a provider."""
        provider = MockProvider("test-provider")
        self.registry.register(provider)

        assert self.registry.get("test-provider") is provider
        assert self.registry.provider_count() == 1

    def test_register_duplicate_provider(self) -> None:
        """Test that registering duplicate provider raises error."""
        provider1 = MockProvider("test-provider")
        provider2 = MockProvider("test-provider")

        self.registry.register(provider1)

        with pytest.raises(ValueError, match="already registered"):
            self.registry.register(provider2)

    def test_unregister_provider(self) -> None:
        """Test unregistering a provider."""
        provider = MockProvider("test-provider")
        self.registry.register(provider)
        self.registry.unregister("test-provider")

        assert self.registry.get("test-provider") is None
        assert self.registry.is_empty()

    def test_unregister_nonexistent_provider(self) -> None:
        """Test unregistering nonexistent provider raises error."""
        with pytest.raises(ValueError, match="not registered"):
            self.registry.unregister("nonexistent")

    def test_get_provider(self) -> None:
        """Test getting a provider by name."""
        provider = MockProvider("test-provider")
        self.registry.register(provider)

        retrieved = self.registry.get("test-provider")
        assert retrieved is provider

    def test_get_nonexistent_provider(self) -> None:
        """Test getting nonexistent provider returns None."""
        assert self.registry.get("nonexistent") is None

    def test_set_default_provider(self) -> None:
        """Test setting default provider."""
        provider = MockProvider("test-provider")
        self.registry.register(provider)
        self.registry.set_default("test-provider")

        assert self.registry.get_default() is provider

    def test_set_default_nonexistent_provider(self) -> None:
        """Test setting nonexistent provider as default raises error."""
        with pytest.raises(ValueError, match="not registered"):
            self.registry.set_default("nonexistent")

    def test_unregister_default_provider(self) -> None:
        """Test that unregistering default provider clears it."""
        provider = MockProvider("test-provider")
        self.registry.register(provider)
        self.registry.set_default("test-provider")
        self.registry.unregister("test-provider")

        assert self.registry.get_default() is None

    def test_list_providers(self) -> None:
        """Test listing all providers."""
        provider1 = MockProvider("provider1")
        provider2 = MockProvider("provider2")

        self.registry.register(provider1)
        self.registry.register(provider2)

        providers = self.registry.list_providers()
        assert len(providers) == 2
        assert "provider1" in providers
        assert "provider2" in providers

    def test_get_health_status(self) -> None:
        """Test getting health status of all providers."""
        provider1 = MockProvider("provider1", healthy=True)
        provider2 = MockProvider("provider2", healthy=False)

        self.registry.register(provider1)
        self.registry.register(provider2)

        health_status = self.registry.get_health_status()
        assert len(health_status) == 2
        assert health_status["provider1"].is_healthy is True
        assert health_status["provider2"].is_healthy is False

    def test_get_provider_health(self) -> None:
        """Test getting health of specific provider."""
        provider = MockProvider("test-provider", healthy=True)
        self.registry.register(provider)

        health = self.registry.get_provider_health("test-provider")
        assert health is not None
        assert health.is_healthy is True

    def test_get_provider_health_nonexistent(self) -> None:
        """Test getting health of nonexistent provider returns None."""
        health = self.registry.get_provider_health("nonexistent")
        assert health is None

    def test_provider_count(self) -> None:
        """Test counting providers."""
        assert self.registry.provider_count() == 0

        self.registry.register(MockProvider("provider1"))
        assert self.registry.provider_count() == 1

        self.registry.register(MockProvider("provider2"))
        assert self.registry.provider_count() == 2

    def test_is_empty(self) -> None:
        """Test checking if registry is empty."""
        assert self.registry.is_empty() is True

        self.registry.register(MockProvider("test-provider"))
        assert self.registry.is_empty() is False

    def test_clear_registry(self) -> None:
        """Test clearing all providers."""
        self.registry.register(MockProvider("provider1"))
        self.registry.register(MockProvider("provider2"))
        self.registry.set_default("provider1")

        self.registry.clear()

        assert self.registry.is_empty() is True
        assert self.registry.get_default() is None
