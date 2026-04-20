"""Domain models and contracts for test coverage MCP server."""

from test_coverage_mcp.domain.contracts import (
    CoverageProvider,
    ProviderHealth,
    ProviderMetadata,
)
from test_coverage_mcp.domain.enums import (
    AnalysisDepth,
    ProviderCapability,
    RiskLevel,
    SupportLevel,
)
from test_coverage_mcp.domain.models import (
    ConfigDiagnosis,
    CoverageDelta,
    CoverageTestRecommendation,
    ExecutionMetadata,
    FileCoverage,
    RepositoryCoverageSummary,
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
    "CoverageTestRecommendation",
    "ConfigDiagnosis",
]
