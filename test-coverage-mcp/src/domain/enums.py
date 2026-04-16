"""Domain enums for test coverage analysis."""

from enum import Enum


class ProviderCapability(str, Enum):
    """Coverage provider capabilities."""

    # Basic analysis
    REPOSITORY_SUMMARY = "repository_summary"
    FILE_COVERAGE = "file_coverage"
    COVERAGE_DELTA = "coverage_delta"

    # Advanced analysis
    UNCOVERED_REGIONS = "uncovered_regions"
    TEST_RECOMMENDATIONS = "test_recommendations"
    COVERAGE_TRENDS = "coverage_trends"

    # Configuration analysis
    COVERAGE_CONFIG_DIAGNOSIS = "coverage_config_diagnosis"
    COVERAGE_GOALS = "coverage_goals"

    # Comparison and metrics
    CROSS_BRANCH_COMPARISON = "cross_branch_comparison"
    PULL_REQUEST_ANALYSIS = "pull_request_analysis"
    COVERAGE_METRICS = "coverage_metrics"

    # Advanced features
    RISK_ASSESSMENT = "risk_assessment"
    QUALITY_GATES = "quality_gates"
    HISTORICAL_ANALYSIS = "historical_analysis"


class SupportLevel(str, Enum):
    """Provider support level for capabilities."""

    BASIC = "basic"
    ENHANCED = "enhanced"
    ADVANCED = "advanced"


class AnalysisDepth(str, Enum):
    """Depth of coverage analysis."""

    REPOSITORY = "repo"
    FILE = "file"
    SEGMENT = "segment"
    TEST_RUN = "test-run"
    CONFIG_AWARE = "config-aware"


class RiskLevel(str, Enum):
    """Risk level for coverage gaps."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
