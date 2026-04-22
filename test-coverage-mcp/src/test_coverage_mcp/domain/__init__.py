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
from test_coverage_mcp.domain.errors import (
    CommitAnalysisError,
    CoverageAnalysisError,
    CoverageComparisonError,
    InvalidParameterError,
    ProviderDiscoveryError,
    ProviderHealthError,
    ProviderNotFoundError,
    RepositoryHealthError,
    ToolExecutionError,
)
from test_coverage_mcp.domain.models import (
    CommitCoverageSummaryResponse,
    ConfigDiagnosis,
    CoverageComparisonResponse,
    CoverageDelta,
    CoverageTestRecommendation,
    ExecutionMetadata,
    ExecutionMetadataResponse,
    FileCoverage,
    ProviderDescriptionResponse,
    ProviderInfo,
    ProviderListResponse,
    RepositoryCoverageSummary,
    RepositoryHealthResponse,
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
    # Errors
    "ToolExecutionError",
    "ProviderNotFoundError",
    "InvalidParameterError",
    "ProviderHealthError",
    "ProviderDiscoveryError",
    "CoverageAnalysisError",
    "RepositoryHealthError",
    "CommitAnalysisError",
    "CoverageComparisonError",
    # Models
    "ExecutionMetadata",
    "ExecutionMetadataResponse",
    "ProviderInfo",
    "ProviderListResponse",
    "ProviderDescriptionResponse",
    "RepositoryHealthResponse",
    "CommitCoverageSummaryResponse",
    "CoverageComparisonResponse",
    "ToolResponseBase",
    "RepositoryCoverageSummary",
    "FileCoverage",
    "CoverageDelta",
    "UncoveredRegion",
    "CoverageTestRecommendation",
    "ConfigDiagnosis",
]
