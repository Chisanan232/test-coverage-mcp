"""Plugin discovery via entry points."""

import importlib.metadata
import logging
from typing import Dict, List

from src.domain import CoverageProvider

logger = logging.getLogger(__name__)

PROVIDER_ENTRY_POINT = "test_coverage_mcp.providers"


class ProviderDiscoveryError(Exception):
    """Error during provider discovery."""

    pass


def discover_providers() -> Dict[str, CoverageProvider]:
    """Discover and load providers via entry points.

    Returns:
        Dictionary mapping provider names to provider instances

    Raises:
        ProviderDiscoveryError: If discovery or loading fails
    """
    providers: Dict[str, CoverageProvider] = {}

    try:
        entry_points = importlib.metadata.entry_points()

        # Handle both Python 3.9 and 3.10+ API
        if hasattr(entry_points, "select"):
            # Python 3.10+
            provider_eps = entry_points.select(group=PROVIDER_ENTRY_POINT)
        else:
            # Python 3.9
            provider_eps = entry_points.get(PROVIDER_ENTRY_POINT, [])

        for ep in provider_eps:
            try:
                provider_class = ep.load()
                provider = provider_class()

                # Verify it's a CoverageProvider
                if not isinstance(provider, CoverageProvider):
                    logger.warning(
                        f"Entry point '{ep.name}' does not implement CoverageProvider, skipping"
                    )
                    continue

                metadata = provider.get_metadata()
                providers[metadata.name] = provider
                logger.info(f"Discovered provider: {metadata.name} v{metadata.version}")

            except Exception as e:
                logger.error(f"Failed to load provider from entry point '{ep.name}': {e}")
                continue

    except Exception as e:
        raise ProviderDiscoveryError(f"Provider discovery failed: {e}") from e

    return providers


def load_provider(module_path: str, class_name: str) -> CoverageProvider:
    """Manually load a provider from a module.

    Args:
        module_path: Full module path (e.g., 'my_package.providers.codecov')
        class_name: Class name of the provider

    Returns:
        Provider instance

    Raises:
        ProviderDiscoveryError: If loading fails
    """
    try:
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)
        provider = provider_class()

        if not isinstance(provider, CoverageProvider):
            raise ProviderDiscoveryError(
                f"{class_name} from {module_path} does not implement CoverageProvider"
            )

        return provider

    except ImportError as e:
        raise ProviderDiscoveryError(f"Failed to import module '{module_path}': {e}") from e
    except AttributeError as e:
        raise ProviderDiscoveryError(
            f"Class '{class_name}' not found in module '{module_path}': {e}"
        ) from e
    except Exception as e:
        raise ProviderDiscoveryError(f"Failed to load provider: {e}") from e


def get_provider_versions(providers: Dict[str, CoverageProvider]) -> Dict[str, str]:
    """Get versions of all providers.

    Args:
        providers: Dictionary of providers

    Returns:
        Dictionary mapping provider names to versions
    """
    return {name: provider.get_metadata().version for name, provider in providers.items()}


def check_version_compatibility(
    provider_version: str, min_version: str, max_version: str
) -> bool:
    """Check if provider version is compatible.

    Args:
        provider_version: Provider version string
        min_version: Minimum required version
        max_version: Maximum allowed version

    Returns:
        True if version is compatible
    """
    from packaging import version

    try:
        pv = version.parse(provider_version)
        min_v = version.parse(min_version)
        max_v = version.parse(max_version)

        return min_v <= pv <= max_v
    except Exception:
        logger.warning(f"Could not parse versions for compatibility check")
        return True
