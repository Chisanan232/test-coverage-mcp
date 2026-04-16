"""Data Transfer Objects for Codecov API responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CoverageMetrics(BaseModel):
    """Coverage metrics from Codecov."""

    coverage: Optional[float] = Field(None, description="Coverage percentage")
    lines: Optional[int] = Field(None, description="Total lines")
    hits: Optional[int] = Field(None, description="Covered lines")
    misses: Optional[int] = Field(None, description="Uncovered lines")
    partials: Optional[int] = Field(None, description="Partial lines")
    branches: Optional[int] = Field(None, description="Total branches")
    branch_hits: Optional[int] = Field(None, description="Covered branches")


class FileDTO(BaseModel):
    """File coverage information from Codecov."""

    name: str = Field(..., description="File path")
    coverage: Optional[float] = Field(None, description="File coverage percentage")
    lines: Optional[int] = Field(None, description="Total lines in file")
    hits: Optional[int] = Field(None, description="Covered lines in file")
    misses: Optional[int] = Field(None, description="Uncovered lines in file")
    partials: Optional[int] = Field(None, description="Partial lines in file")
    complexity: Optional[float] = Field(None, description="Cyclomatic complexity")


class CommitDTO(BaseModel):
    """Commit information from Codecov."""

    commitid: str = Field(..., description="Commit SHA")
    message: Optional[str] = Field(None, description="Commit message")
    timestamp: Optional[datetime] = Field(None, description="Commit timestamp")
    author: Optional[str] = Field(None, description="Commit author")
    coverage: Optional[float] = Field(None, description="Coverage for this commit")
    totals: Optional[CoverageMetrics] = Field(None, description="Coverage metrics")
    files: Optional[List[FileDTO]] = Field(None, description="Files in commit")


class RepositoryDTO(BaseModel):
    """Repository information from Codecov."""

    name: str = Field(..., description="Repository name")
    owner: Optional[str] = Field(None, description="Repository owner")
    url: Optional[str] = Field(None, description="Repository URL")
    private: Optional[bool] = Field(None, description="Whether repository is private")
    language: Optional[str] = Field(None, description="Primary language")
    coverage: Optional[float] = Field(None, description="Current coverage")
    totals: Optional[CoverageMetrics] = Field(None, description="Coverage metrics")
    last_update: Optional[datetime] = Field(None, description="Last update timestamp")
    branch: Optional[str] = Field(None, description="Default branch")


class ComparisonDTO(BaseModel):
    """Coverage comparison between commits."""

    base_commit: Optional[str] = Field(None, description="Base commit SHA")
    head_commit: Optional[str] = Field(None, description="Head commit SHA")
    base_coverage: Optional[float] = Field(None, description="Base coverage percentage")
    head_coverage: Optional[float] = Field(None, description="Head coverage percentage")
    coverage_change: Optional[float] = Field(None, description="Coverage change percentage")
    files_changed: Optional[int] = Field(None, description="Number of files changed")
    files_with_coverage_change: Optional[int] = Field(
        None, description="Files with coverage change"
    )
    patch_coverage: Optional[float] = Field(None, description="Patch coverage percentage")


class FlagDTO(BaseModel):
    """Coverage flag information."""

    name: str = Field(..., description="Flag name")
    coverage: Optional[float] = Field(None, description="Flag coverage percentage")
    carryforward: Optional[bool] = Field(None, description="Whether flag carries forward")
    totals: Optional[CoverageMetrics] = Field(None, description="Coverage metrics")


class ComponentDTO(BaseModel):
    """Component coverage information."""

    name: str = Field(..., description="Component name")
    coverage: Optional[float] = Field(None, description="Component coverage percentage")
    totals: Optional[CoverageMetrics] = Field(None, description="Coverage metrics")


class UploadDTO(BaseModel):
    """Coverage upload information."""

    id: str = Field(..., description="Upload ID")
    created_at: Optional[datetime] = Field(None, description="Upload timestamp")
    state: Optional[str] = Field(None, description="Upload state (completed, failed, etc)")
    coverage: Optional[float] = Field(None, description="Coverage from this upload")
    flags: Optional[List[str]] = Field(None, description="Associated flags")
    provider: Optional[str] = Field(None, description="CI provider")


class TestResultDTO(BaseModel):
    """Test result information."""

    name: str = Field(..., description="Test name")
    status: str = Field(..., description="Test status (passed, failed, skipped)")
    duration: Optional[float] = Field(None, description="Test duration in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")


class BranchDTO(BaseModel):
    """Branch information from Codecov."""

    name: str = Field(..., description="Branch name")
    coverage: Optional[float] = Field(None, description="Branch coverage percentage")
    totals: Optional[CoverageMetrics] = Field(None, description="Coverage metrics")
    last_update: Optional[datetime] = Field(None, description="Last update timestamp")
    is_default: Optional[bool] = Field(None, description="Whether this is default branch")


class PullRequestDTO(BaseModel):
    """Pull request information from Codecov."""

    number: int = Field(..., description="PR number")
    title: Optional[str] = Field(None, description="PR title")
    state: Optional[str] = Field(None, description="PR state (open, closed, merged)")
    base_branch: Optional[str] = Field(None, description="Base branch")
    head_branch: Optional[str] = Field(None, description="Head branch")
    base_commit: Optional[str] = Field(None, description="Base commit SHA")
    head_commit: Optional[str] = Field(None, description="Head commit SHA")
    coverage: Optional[float] = Field(None, description="PR coverage percentage")
    comparison: Optional[ComparisonDTO] = Field(None, description="Coverage comparison")
    created_at: Optional[datetime] = Field(None, description="PR creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="PR update timestamp")


class CodecovErrorDTO(BaseModel):
    """Error response from Codecov API."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    status_code: Optional[int] = Field(None, description="HTTP status code")


class CodecovResponseDTO(BaseModel):
    """Generic Codecov API response wrapper."""

    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[CodecovErrorDTO] = Field(None, description="Error information")
    meta: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
