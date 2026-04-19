"""Provider discovery service for managing coverage providers."""

from typing import Dict, List, Optional

from test_coverage_mcp.domain import (
    CoverageProvider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
)
from test_coverage_mcp.registry import ProviderRegistry
from test_coverage_mcp.registry.discovery import discover_providers


class ProviderDiscoveryService:
    """Service for discovering and managing coverage providers."""

    def __init__(self, registry: Optional[ProviderRegistry] = None) -> None:
        """Initialize the discovery service.

        Args:
            registry: Provider registry instance. If None, uses singleton instance.
        """
        self._registry = registry or ProviderRegistry()

    def discover_and_register_providers(self) -> Dict[str, ProviderMetadata]:
        """Discover providers via entry points and register them.

        Returns:
            Dictionary mapping provider names to their metadata

        Raises:
            Exception: If provider discovery or registration fails
        """
        providers = discover_providers()

        for name, provider in providers.items():
            try:
                self._registry.register(provider)
            except ValueError as e:
                if "already registered" in str(e):
                    continue
                raise

        return self.list_providers()

    def list_providers(self) -> Dict[str, ProviderMetadata]:
        """List all registered providers with their metadata.

        Returns:
            Dictionary mapping provider names to their metadata
        """
        return self._registry.list_providers()

    def get_provider(self, name: str) -> Optional[CoverageProvider]:
        """Get a specific provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None if not found
        """
        return self._registry.get(name)

    def get_default_provider(self) -> Optional[CoverageProvider]:
        """Get the default provider.

        Returns:
            Default provider instance or None if not set
        """
        return self._registry.get_default()

    def set_default_provider(self, name: str) -> None:
        """Set the default provider.

        Args:
            name: Provider name to set as default

        Raises:
            ValueError: If provider is not registered
        """
        self._registry.set_default(name)

    def get_capability_matrix(self) -> Dict[str, Dict[str, str]]:
        """Generate a capability matrix for all providers.

        Returns:
            Dictionary mapping provider names to their capability support levels
        """
        matrix: Dict[str, Dict[str, str]] = {}

        for name, metadata in self.list_providers().items():
            matrix[name] = {
                cap.value: level.value
                for cap, level in metadata.support_levels.items()
            }

        return matrix

    def get_providers_for_capability(
        self, capability: ProviderCapability
    ) -> Dict[str, str]:
        """Get all providers that support a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            Dictionary mapping provider names to their support levels for this capability
        """
        providers_with_capability: Dict[str, str] = {}

        for name, metadata in self.list_providers().items():
            if capability in metadata.support_levels:
                level = metadata.support_levels[capability]
                providers_with_capability[name] = level.value

        return providers_with_capability

    def get_provider_health(self, name: str) -> Optional[ProviderHealth]:
        """Get health status of a specific provider.

        Args:
            name: Provider name

        Returns:
            Health status or None if provider not found
        """
        return self._registry.get_provider_health(name)

    def get_all_health_status(self) -> Dict[str, ProviderHealth]:
        """Get health status of all registered providers.

        Returns:
            Dictionary mapping provider names to their health status
        """
        return self._registry.get_health_status()

    def aggregate_health(self) -> Dict[str, bool | int | float]:
        """Aggregate health status across all providers.

        Returns:
            Dictionary with aggregated health metrics:
            - total_providers: Total number of registered providers
            - healthy_providers: Number of healthy providers
            - health_percentage: Percentage of healthy providers
            - avg_response_time_ms: Average response time across providers
        """
        health_status = self.get_all_health_status()

        if not health_status:
            return {
                "total_providers": 0,
                "healthy_providers": 0,
                "health_percentage": 0.0,
                "avg_response_time_ms": 0.0,
            }

        total = len(health_status)
        healthy = sum(1 for h in health_status.values() if h.is_healthy)
        avg_response_time = sum(h.response_time_ms for h in health_status.values()) / total

        return {
            "total_providers": total,
            "healthy_providers": healthy,
            "health_percentage": (healthy / total * 100) if total > 0 else 0.0,
            "avg_response_time_ms": avg_response_time,
        }

    def get_provider_versions(self) -> Dict[str, str]:
        """Get versions of all registered providers.

        Returns:
            Dictionary mapping provider names to their versions
        """
        return {
            name: metadata.version
            for name, metadata in self.list_providers().items()
        }

    def select_best_provider(
        self, required_capabilities: Optional[List[ProviderCapability]] = None
    ) -> Optional[CoverageProvider]:
        """Select the best provider based on capabilities and health.

        Args:
            required_capabilities: List of required capabilities. If None, returns default or first healthy provider.

        Returns:
            Best provider instance or None if no suitable provider found
        """
        default = self.get_default_provider()
        if default is not None:
            return default

        if not required_capabilities:
            health_status = self.get_all_health_status()
            for name, health in health_status.items():
                if health.is_healthy:
                    return self._registry.get(name)
            return None

        candidates: Dict[str, CoverageProvider] = {}
        health_status = self.get_all_health_status()

        for name, metadata in self.list_providers().items():
            if all(cap in metadata.supported_capabilities for cap in required_capabilities):
                health = health_status.get(name)
                if health and health.is_healthy:
                    candidates[name] = self._registry.get(name)

        if not candidates:
            return None

        best_name = min(
            candidates.keys(),
            key=lambda n: health_status[n].response_time_ms,
        )
        return candidates[best_name]
