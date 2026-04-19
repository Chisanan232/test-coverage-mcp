"""Coverage intelligence services for test coverage analysis."""

from test_coverage_mcp.services.comparison import CoverageComparisonService
from test_coverage_mcp.services.discovery import ProviderDiscoveryService
from test_coverage_mcp.services.gap_discovery import CoverageGapDiscoveryService
from test_coverage_mcp.services.health import RepositoryHealthService
from test_coverage_mcp.services.risk_analysis import CoverageRiskAnalysisService

__all__ = [
    "ProviderDiscoveryService",
    "RepositoryHealthService",
    "CoverageComparisonService",
    "CoverageRiskAnalysisService",
    "CoverageGapDiscoveryService",
]
