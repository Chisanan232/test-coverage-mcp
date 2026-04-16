"""Domain models and contracts for test coverage MCP server."""

from src.domain.contracts import (
    CoverageProvider,
    ProviderHealth,
    ProviderMetadata,
)
from src.domain.enums import (
    AnalysisDepth,
    ProviderCapability,
    RiskLevel,
    SupportLevel,
)
from src.domain.models import (
    ConfigDiagnosis,
    CoverageDelta,
    ExecutionMetadata,
    FileCoverage,
    RepositoryCoverageSummary,
    TestRecommendation,
    ToolResponseBase,
    UncoveredRegion,
)

__all__ = [
    # Enums
    "ProviderCapability",
    "SupportLevel",
    "AnalysisDepth",
    "RiskLevel",
    # Contracts
    "CoverageProvider",
    "ProviderHealth",
    "ProviderMetadata",
    # Models
    "ExecutionMetadata",
    "ToolResponseBase",
    "RepositoryCoverageSummary",
    "FileCoverage",
    "CoverageDelta",
    "UncoveredRegion",
    "TestRecommendation",
    "ConfigDiagnosis",
]
