"""Coverage provider discovery tools for MCP."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    ExecutionMetadata,
    ProviderCapability,
    ProviderDescriptionResponse,
    ProviderListResponse,
    SupportLevel,
)
from test_coverage_mcp.services import ProviderDiscoveryService


def _create_execution_metadata(tool_name: str) -> Dict[str, Any]:
    """Create execution metadata for tool response.

    Args:
        tool_name: Name of the tool

    Returns:
        Dictionary with execution metadata
    """
    return {
        "provider_name": "test-coverage-mcp",
        "provider_version": "0.1.0",
        "support_level": SupportLevel.ADVANCED.value,
        "used_capabilities": [],
        "analysis_depth": AnalysisDepth.REPOSITORY.value,
        "execution_time_ms": 0.0,
    }


def list_coverage_providers(
    include_capabilities: bool = True,
    include_health: bool = True,
) -> ProviderListResponse:
    """List all available coverage providers with their metadata.

    This tool discovers and lists all registered coverage providers, optionally
    including their capabilities and health status.

    Args:
        include_capabilities: Include capability information for each provider
        include_health: Include health status for each provider

    Returns:
        Dictionary containing:
        - providers: List of provider information
        - total_providers: Total number of providers
        - healthy_providers: Number of healthy providers (if include_health=True)
        - execution_metadata: Execution metadata with timestamp and duration

    Example:
        >>> result = list_coverage_providers(include_capabilities=True, include_health=True)
        >>> print(f"Found {result['total_providers']} providers")
        >>> for provider in result['providers']:
        ...     print(f"- {provider['name']}: {provider['version']}")
    """
    try:
        service = ProviderDiscoveryService()
        providers_dict = service.list_providers()

        providers_list: List[Dict[str, Any]] = []

        for name, metadata in providers_dict.items():
            provider_info: Dict[str, Any] = {
                "name": metadata.name,
                "version": metadata.version,
                "description": metadata.description,
            }

            if include_capabilities:
                provider_info["supported_capabilities"] = [
                    cap.value for cap in metadata.supported_capabilities
                ]
                provider_info["support_levels"] = {
                    cap.value: level.value
                    for cap, level in metadata.support_levels.items()
                }

            if include_health:
                health = service.get_provider_health(name)
                if health:
                    provider_info["health"] = {
                        "is_healthy": health.is_healthy,
                        "last_check": health.last_check,
                        "response_time_ms": health.response_time_ms,
                        "error_message": health.error_message,
                    }

            providers_list.append(provider_info)

        health_status = service.get_all_health_status() if include_health else {}
        healthy_count = sum(1 for h in health_status.values() if h.is_healthy)

        return {
            "providers": providers_list,
            "total_providers": len(providers_list),
            "healthy_providers": healthy_count if include_health else None,
            "execution_metadata": _create_execution_metadata("list_coverage_providers"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": "ProviderDiscoveryError",
            "providers": [],
            "total_providers": 0,
            "execution_metadata": _create_execution_metadata("list_coverage_providers"),
        }


def describe_coverage_provider(provider_name: str) -> ProviderDescriptionResponse:
    """Get detailed information about a specific coverage provider.

    This tool provides comprehensive information about a provider including
    its capabilities, limitations, and current health status.

    Args:
        provider_name: Name of the provider to describe

    Returns:
        Dictionary containing:
        - name: Provider name
        - version: Provider version
        - description: Provider description
        - capabilities: Detailed capability information
        - health: Current health status
        - execution_metadata: Execution metadata

    Example:
        >>> result = describe_coverage_provider("codecov")
        >>> print(f"Provider: {result['name']} v{result['version']}")
        >>> print(f"Capabilities: {result['capabilities']}")
    """
    try:
        service = ProviderDiscoveryService()
        provider = service.get_provider(provider_name)

        if provider is None:
            return {
                "error": f"Provider '{provider_name}' not found",
                "error_type": "ProviderNotFoundError",
                "execution_metadata": _create_execution_metadata("describe_coverage_provider"),
            }

        metadata = provider.get_metadata()

        capability_matrix = service.get_capability_matrix()
        provider_capabilities = capability_matrix.get(provider_name, {})

        health = service.get_provider_health(provider_name)

        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "capabilities": {
                "supported": [cap.value for cap in metadata.supported_capabilities],
                "support_levels": {
                    cap.value: level.value
                    for cap, level in metadata.support_levels.items()
                },
                "capability_matrix": provider_capabilities,
            },
            "health": {
                "is_healthy": health.is_healthy if health else False,
                "last_check": health.last_check if health else None,
                "response_time_ms": health.response_time_ms if health else None,
                "error_message": health.error_message if health else None,
            } if health else None,
            "execution_metadata": _create_execution_metadata("describe_coverage_provider"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": "ProviderDescriptionError",
            "execution_metadata": _create_execution_metadata("describe_coverage_provider"),
        }
