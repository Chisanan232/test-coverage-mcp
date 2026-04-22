"""Core domain models for coverage analysis."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from test_coverage_mcp.domain.enums import (
    AnalysisDepth,
    ProviderCapability,
    RiskLevel,
    SupportLevel,
)


class ExecutionMetadata(BaseModel):
    """Metadata about tool execution."""

    provider_name: str = Field(..., description="Name of the provider used")
    provider_version: str = Field(..., description="Version of the provider")
    support_level: SupportLevel = Field(..., description="Support level achieved")
    used_capabilities: list[ProviderCapability] = Field(
        ..., description="Capabilities used in this execution"
    )
    analysis_depth: AnalysisDepth = Field(..., description="Depth of analysis performed")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Execution timestamp",
    )
    degradation_reason: Optional[str] = Field(
        None, description="Reason for any degradation from requested capabilities"
    )
    limitations: list[str] = Field(
        default_factory=list, description="Known limitations of this execution"
    )


class ToolResponseBase(BaseModel):
    """Base class for all tool responses."""

    summary: str = Field(..., description="Brief summary of findings")
    key_findings: list[str] = Field(..., description="Key findings from analysis")
    recommended_next_actions: list[str] = Field(
        ..., description="Recommended actions based on findings"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    execution_metadata: ExecutionMetadata = Field(
        ..., description="Metadata about the execution"
    )
    additional_context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context or raw data"
    )


class RepositoryCoverageSummary(ToolResponseBase):
    """Summary of repository coverage."""

    total_coverage_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Total coverage percentage"
    )
    covered_lines: int = Field(..., ge=0, description="Number of covered lines")
    total_lines: int = Field(..., ge=0, description="Total number of lines")
    file_count: int = Field(..., ge=0, description="Number of files analyzed")
    covered_file_count: int = Field(..., ge=0, description="Number of files with coverage")


class FileCoverage(ToolResponseBase):
    """Coverage information for a specific file."""

    file_path: str = Field(..., description="Path to the file")
    coverage_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="File coverage percentage"
    )
    covered_lines: int = Field(..., ge=0, description="Number of covered lines")
    total_lines: int = Field(..., ge=0, description="Total number of lines")
    uncovered_lines: list[int] = Field(
        default_factory=list, description="Line numbers that are uncovered"
    )


class CoverageDelta(ToolResponseBase):
    """Coverage change between two versions."""

    base_coverage: float = Field(..., ge=0.0, le=100.0, description="Base coverage percentage")
    current_coverage: float = Field(
        ..., ge=0.0, le=100.0, description="Current coverage percentage"
    )
    delta_percentage: float = Field(..., description="Change in coverage percentage")
    delta_lines: int = Field(..., description="Change in number of covered lines")
    improved: bool = Field(..., description="Whether coverage improved")


class UncoveredRegion(BaseModel):
    """Region of code that is not covered."""

    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., ge=1, description="Start line number")
    end_line: int = Field(..., ge=1, description="End line number")
    region_type: str = Field(..., description="Type of region (function, class, block, etc.)")
    risk_level: RiskLevel = Field(..., description="Risk level of this uncovered region")


class CoverageTestRecommendation(BaseModel):
    """Recommendation for test coverage improvement."""

    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., ge=1, description="Start line number")
    end_line: int = Field(..., ge=1, description="End line number")
    region_type: str = Field(..., description="Type of region (function, class, method, etc.)")
    test_types: list[str] = Field(..., description="Suggested test types (unit, integration, etc.)")
    scenarios: list[str] = Field(..., description="Test scenarios to implement")
    priority: str = Field(..., description="Priority level (critical, high, medium, low)")
    rationale: str = Field(..., description="Explanation of why this test is important")


class ConfigDiagnosis(BaseModel):
    """Diagnosis of coverage configuration issues."""

    repo_owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")
    config_valid: bool = Field(..., description="Whether configuration is valid")
    parse_errors: list[str] = Field(default_factory=list, description="Configuration parsing errors")
    over_included_paths: list[dict[str, Any]] = Field(
        default_factory=list, description="Paths that are over-included"
    )
    missing_exclusions: list[dict[str, Any]] = Field(
        default_factory=list, description="Suggested missing exclusions"
    )
    threshold_issues: list[str] = Field(
        default_factory=list, description="Issues with coverage thresholds"
    )
    scoping_issues: list[dict[str, Any]] = Field(
        default_factory=list, description="Issues with component/flag scoping"
    )
    summary: str = Field(..., description="Summary of diagnosis findings")
