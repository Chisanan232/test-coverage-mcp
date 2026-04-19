"""Input and output models for PR analysis tools."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FindUntestedCodeInput(BaseModel):
    """Input for find_untested_changed_code tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")
    base_ref: str = Field(..., description="Base reference (branch, tag, or commit)")
    head_ref: str = Field(..., description="Head reference to compare against")


class UncoveredRegionOutput(BaseModel):
    """Output model for uncovered region."""

    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., description="Start line number")
    end_line: int = Field(..., description="End line number")
    region_type: str = Field(..., description="Type of region (function, class, etc.)")
    risk_level: str = Field(..., description="Risk level of uncovered region")
    lines_count: int = Field(..., description="Number of lines in region")


class FindUntestedCodeOutput(BaseModel):
    """Output for find_untested_changed_code tool."""

    base_ref: str = Field(..., description="Base reference")
    head_ref: str = Field(..., description="Head reference")
    total_changed_lines: int = Field(..., description="Total lines changed")
    covered_changed_lines: int = Field(..., description="Lines changed that are covered")
    uncovered_changed_lines: int = Field(..., description="Lines changed that are uncovered")
    coverage_percentage: float = Field(..., description="Coverage of changed code")
    uncovered_regions: List[UncoveredRegionOutput] = Field(
        ..., description="List of uncovered regions"
    )
    pending_regions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Regions with pending analysis"
    )
    has_pending: bool = Field(
        default=False, description="Whether pending analysis exists"
    )
    gap_summary: str = Field(..., description="Summary of coverage gaps")


class AnalyzePRRiskInput(BaseModel):
    """Input for analyze_pr_coverage_risk tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")
    base_ref: str = Field(..., description="Base reference (branch, tag, or commit)")
    head_ref: str = Field(..., description="Head reference to compare against")


class RiskRecommendation(BaseModel):
    """Risk recommendation model."""

    priority: str = Field(..., description="Priority level (low, medium, high, critical)")
    message: str = Field(..., description="Recommendation message")
    action: str = Field(..., description="Suggested action to take")


class AnalyzePRRiskOutput(BaseModel):
    """Output for analyze_pr_coverage_risk tool."""

    base_ref: str = Field(..., description="Base reference")
    head_ref: str = Field(..., description="Head reference")
    risk_level: str = Field(..., description="Overall risk level")
    risk_score: float = Field(..., description="Numerical risk score (0-100)")
    coverage_delta: float = Field(..., description="Change in coverage percentage")
    changed_code_coverage: float = Field(..., description="Coverage of changed code")
    changed_files_count: int = Field(..., description="Number of files changed")
    uncovered_changed_lines: int = Field(..., description="Number of uncovered changed lines")
    total_changed_lines: int = Field(..., description="Total number of changed lines")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    high_risk_files: List[Dict[str, Any]] = Field(
        default_factory=list, description="Files with high coverage risk"
    )
