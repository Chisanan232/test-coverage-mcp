"""Provider contracts and protocols for coverage analysis."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field

from test_coverage_mcp.domain.enums import (
    AnalysisDepth,
    ProviderCapability,
    RiskLevel,
    SupportLevel,
)


class ProviderHealth(BaseModel):
    """Health status of a coverage provider."""

    is_healthy: bool = Field(..., description="Whether provider is healthy")
    last_check: str = Field(..., description="ISO timestamp of last health check")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    response_time_ms: float = Field(..., description="Health check response time in ms")


class ProviderMetadata(BaseModel):
    """Metadata about a coverage provider."""

    name: str = Field(..., description="Provider name")
    version: str = Field(..., description="Provider version")
    description: str = Field(..., description="Provider description")
    supported_capabilities: list[ProviderCapability] = Field(
        ..., description="List of supported capabilities"
    )
    support_levels: dict[ProviderCapability, SupportLevel] = Field(
        ..., description="Support level for each capability"
    )
    analysis_depths: list[AnalysisDepth] = Field(
        ..., description="Supported analysis depths"
    )


class CoverageProvider(ABC):
    """Abstract base class for coverage providers."""

    @abstractmethod
    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        pass

    @abstractmethod
    def health_check(self) -> ProviderHealth:
        """Check provider health."""
        pass

    @abstractmethod
    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a capability."""
        pass

    @abstractmethod
    def get_support_level(
        self, capability: ProviderCapability
    ) -> Optional[SupportLevel]:
        """Get support level for a capability."""
        pass
