"""Provider registry with singleton pattern."""

from typing import Dict, Optional

from test_coverage_mcp.domain import CoverageProvider, ProviderHealth, ProviderMetadata


class ProviderRegistry:
    """Global registry for coverage providers using singleton pattern."""

    _instance: Optional["ProviderRegistry"] = None
    _providers: Dict[str, CoverageProvider] = {}
    _default_provider: Optional[str] = None

    def __new__(cls) -> "ProviderRegistry":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, provider: CoverageProvider) -> None:
        """Register a coverage provider.

        Args:
            provider: Provider instance to register

        Raises:
            ValueError: If provider name is already registered
        """
        metadata = provider.get_metadata()
        name = metadata.name

        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered")

        self._providers[name] = provider

    def unregister(self, name: str) -> None:
        """Unregister a coverage provider.

        Args:
            name: Provider name to unregister

        Raises:
            ValueError: If provider is not registered
        """
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' is not registered")

        if self._default_provider == name:
            self._default_provider = None

        del self._providers[name]

    def get(self, name: str) -> Optional[CoverageProvider]:
        """Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(name)

    def get_default(self) -> Optional[CoverageProvider]:
        """Get the default provider.

        Returns:
            Default provider instance or None if not set
        """
        if self._default_provider is None:
            return None
        return self._providers.get(self._default_provider)

    def set_default(self, name: str) -> None:
        """Set the default provider.

        Args:
            name: Provider name to set as default

        Raises:
            ValueError: If provider is not registered
        """
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' is not registered")

        self._default_provider = name

    def list_providers(self) -> Dict[str, ProviderMetadata]:
        """List all registered providers with their metadata.

        Returns:
            Dictionary mapping provider names to their metadata
        """
        return {name: provider.get_metadata() for name, provider in self._providers.items()}

    def get_health_status(self) -> Dict[str, ProviderHealth]:
        """Get health status of all registered providers.

        Returns:
            Dictionary mapping provider names to their health status
        """
        return {name: provider.health_check() for name, provider in self._providers.items()}

    def get_provider_health(self, name: str) -> Optional[ProviderHealth]:
        """Get health status of a specific provider.

        Args:
            name: Provider name

        Returns:
            Health status or None if provider not found
        """
        provider = self.get(name)
        if provider is None:
            return None
        return provider.health_check()

    def clear(self) -> None:
        """Clear all registered providers (useful for testing)."""
        self._providers.clear()
        self._default_provider = None

    def is_empty(self) -> bool:
        """Check if registry is empty.

        Returns:
            True if no providers are registered
        """
        return len(self._providers) == 0

    def provider_count(self) -> int:
        """Get the number of registered providers.

        Returns:
            Number of registered providers
        """
        return len(self._providers)
