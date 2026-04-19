"""Input and output models for advanced analysis tools."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FindLowCoverageFilesInput(BaseModel):
    """Input for find_low_coverage_files tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")
    ref: str = Field(..., description="Git reference (branch, tag, or commit)")
    threshold: float = Field(
        default=80.0, description="Coverage threshold percentage (0-100)"
    )
    limit: int = Field(default=10, description="Maximum number of files to return")


class LowCoverageFileOutput(BaseModel):
    """Output model for a file with low coverage."""

    file_path: str = Field(..., description="Path to the file")
    coverage_percentage: float = Field(..., description="File coverage percentage")
    covered_lines: int = Field(..., description="Number of covered lines")
    total_lines: int = Field(..., description="Total number of lines")
    improvement_potential: float = Field(
        ..., description="Potential coverage improvement"
    )


class FindLowCoverageFilesOutput(BaseModel):
    """Output for find_low_coverage_files tool."""

    ref: str = Field(..., description="Git reference analyzed")
    threshold: float = Field(..., description="Coverage threshold used")
    total_files: int = Field(..., description="Total files analyzed")
    files_below_threshold: int = Field(..., description="Number of files below threshold")
    low_coverage_files: List[LowCoverageFileOutput] = Field(
        ..., description="List of files with low coverage"
    )
    summary: str = Field(..., description="Summary of findings")


class DiagnoseCoverageConfigurationInput(BaseModel):
    """Input for diagnose_coverage_configuration tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")


class DiagnoseCoverageConfigurationOutput(BaseModel):
    """Output for diagnose_coverage_configuration tool."""

    repo_owner: str = Field(..., description="Repository owner")
    repo_name: str = Field(..., description="Repository name")
    config_valid: bool = Field(..., description="Whether configuration is valid")
    parse_errors: List[str] = Field(
        default_factory=list, description="Configuration parsing errors"
    )
    over_included_paths: List[Dict[str, Any]] = Field(
        default_factory=list, description="Paths that are over-included"
    )
    missing_exclusions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Suggested missing exclusions"
    )
    threshold_issues: List[str] = Field(
        default_factory=list, description="Issues with coverage thresholds"
    )
    scoping_issues: List[Dict[str, Any]] = Field(
        default_factory=list, description="Issues with component/flag scoping"
    )
    summary: str = Field(..., description="Summary of diagnosis findings")


class RecommendTestPlanInput(BaseModel):
    """Input for recommend_test_plan tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")
    target: str = Field(
        default="repo",
        description="Analysis target - 'repo', 'pr', or file path",
    )


class TestRecommendationOutput(BaseModel):
    """Output model for a test recommendation."""

    file_path: str = Field(..., description="Path to the file")
    start_line: int = Field(..., description="Start line number")
    end_line: int = Field(..., description="End line number")
    region_type: str = Field(..., description="Type of region (function, class, etc.)")
    test_types: List[str] = Field(..., description="Suggested test types")
    scenarios: List[str] = Field(..., description="Test scenarios to implement")
    priority: str = Field(..., description="Priority level (critical, high, medium, low)")
    rationale: str = Field(..., description="Explanation of why this test is important")


class RecommendTestPlanOutput(BaseModel):
    """Output for recommend_test_plan tool."""

    target: str = Field(..., description="The analysis target")
    total_gaps: int = Field(..., description="Total number of coverage gaps")
    recommendations: List[TestRecommendationOutput] = Field(
        ..., description="List of test recommendations"
    )
    summary: str = Field(..., description="Summary of test plan")


class IdentifyExcludableCodeCandidatesInput(BaseModel):
    """Input for identify_excludable_code_candidates tool."""

    repo_slug: str = Field(..., description="Repository slug (owner/repo)")
    provider: str = Field(..., description="Coverage provider name")
    ref: str = Field(..., description="Git reference (branch, tag, or commit)")


class ExcludableCodeCandidateOutput(BaseModel):
    """Output model for an excludable code candidate."""

    file_path: str = Field(..., description="Path to the file")
    excludability_score: float = Field(..., description="Excludability score (0-1)")
    should_exclude: bool = Field(..., description="Whether to exclude from coverage")
    breakdown: Dict[str, Any] = Field(
        ..., description="Breakdown of detection signals"
    )


class IdentifyExcludableCodeCandidatesOutput(BaseModel):
    """Output for identify_excludable_code_candidates tool."""

    ref: str = Field(..., description="Git reference analyzed")
    total_files: int = Field(..., description="Total files analyzed")
    candidate_count: int = Field(..., description="Number of excludable candidates")
    candidates: List[ExcludableCodeCandidateOutput] = Field(
        ..., description="List of excludable code candidates"
    )
    summary: str = Field(..., description="Summary of findings")
