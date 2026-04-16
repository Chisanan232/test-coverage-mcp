"""Provider lifecycle management."""

import logging
from typing import Any, Dict, Optional

from src.domain import CoverageProvider, ProviderHealth

logger = logging.getLogger(__name__)


class ProviderLifecycleManager:
    """Manages provider initialization, configuration, and shutdown."""

    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self._initialized_providers: Dict[str, CoverageProvider] = {}
        self._provider_configs: Dict[str, Dict[str, Any]] = {}
        self._health_checks: Dict[str, ProviderHealth] = {}

    def initialize(
        self, provider: CoverageProvider, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize a provider with configuration.

        Args:
            provider: Provider instance to initialize
            config: Optional configuration dictionary
        """
        metadata = provider.get_metadata()
        name = metadata.name

        try:
            # Store configuration
            if config:
                self._provider_configs[name] = config
                logger.info(f"Configured provider '{name}' with custom settings")

            # Perform health check
            health = provider.health_check()
            self._health_checks[name] = health

            if health.is_healthy:
                self._initialized_providers[name] = provider
                logger.info(f"Successfully initialized provider '{name}'")
            else:
                logger.warning(
                    f"Provider '{name}' is unhealthy: {health.error_message}"
                )

        except Exception as e:
            logger.error(f"Failed to initialize provider '{name}': {e}")
            raise

    def shutdown(self, name: str) -> None:
        """Shutdown a provider gracefully.

        Args:
            name: Provider name
        """
        if name not in self._initialized_providers:
            logger.warning(f"Provider '{name}' is not initialized")
            return

        try:
            # Call shutdown hook if available
            provider = self._initialized_providers[name]
            if hasattr(provider, "shutdown"):
                provider.shutdown()

            del self._initialized_providers[name]
            if name in self._provider_configs:
                del self._provider_configs[name]
            if name in self._health_checks:
                del self._health_checks[name]

            logger.info(f"Successfully shut down provider '{name}'")

        except Exception as e:
            logger.error(f"Error shutting down provider '{name}': {e}")
            raise

    def shutdown_all(self) -> None:
        """Shutdown all initialized providers."""
        names = list(self._initialized_providers.keys())
        for name in names:
            try:
                self.shutdown(name)
            except Exception as e:
                logger.error(f"Error during shutdown of '{name}': {e}")

    def get_initialized(self, name: str) -> Optional[CoverageProvider]:
        """Get an initialized provider.

        Args:
            name: Provider name

        Returns:
            Provider instance or None if not initialized
        """
        return self._initialized_providers.get(name)

    def is_initialized(self, name: str) -> bool:
        """Check if a provider is initialized.

        Args:
            name: Provider name

        Returns:
            True if provider is initialized
        """
        return name in self._initialized_providers

    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a provider.

        Args:
            name: Provider name

        Returns:
            Configuration dictionary or None
        """
        return self._provider_configs.get(name)

    def update_config(self, name: str, config: Dict[str, Any]) -> None:
        """Update configuration for a provider.

        Args:
            name: Provider name
            config: New configuration
        """
        if name not in self._initialized_providers:
            raise ValueError(f"Provider '{name}' is not initialized")

        self._provider_configs[name] = config
        logger.info(f"Updated configuration for provider '{name}'")

    def check_health(self, name: str) -> Optional[ProviderHealth]:
        """Check health of a provider.

        Args:
            name: Provider name

        Returns:
            Health status or None if not initialized
        """
        if name not in self._initialized_providers:
            return None

        try:
            provider = self._initialized_providers[name]
            health = provider.health_check()
            self._health_checks[name] = health
            return health

        except Exception as e:
            logger.error(f"Health check failed for provider '{name}': {e}")
            return None

    def check_all_health(self) -> Dict[str, ProviderHealth]:
        """Check health of all initialized providers.

        Returns:
            Dictionary mapping provider names to health status
        """
        results = {}
        for name in self._initialized_providers:
            health = self.check_health(name)
            if health:
                results[name] = health

        return results

    def get_last_health(self, name: str) -> Optional[ProviderHealth]:
        """Get last recorded health status.

        Args:
            name: Provider name

        Returns:
            Last health status or None
        """
        return self._health_checks.get(name)

    def list_initialized(self) -> Dict[str, CoverageProvider]:
        """List all initialized providers.

        Returns:
            Dictionary of initialized providers
        """
        return dict(self._initialized_providers)
