"""DTO to domain model mappers."""

from typing import Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    CoverageDelta,
    ExecutionMetadata,
    FileCoverage,
    ProviderCapability,
    RepositoryCoverageSummary,
    SupportLevel,
)
from test_coverage_mcp.providers.codecov.api.dtos import (
    ComparisonDTO,
    FileDTO,
    RepositoryDTO,
)


def map_repository_to_summary(
    repo_dto: RepositoryDTO,
    execution_metadata: ExecutionMetadata,
) -> RepositoryCoverageSummary:
    """Map Codecov repository DTO to domain model.

    Args:
        repo_dto: Codecov repository DTO
        execution_metadata: Execution metadata

    Returns:
        Repository coverage summary domain model
    """
    totals = repo_dto.totals or {}

    return RepositoryCoverageSummary(
        summary=f"Repository {repo_dto.name} coverage analysis",
        key_findings=[
            f"Overall coverage: {repo_dto.coverage or 0}%",
            f"Language: {repo_dto.language or 'Unknown'}",
            f"Private: {repo_dto.private or False}",
        ],
        recommended_next_actions=[
            "Review files with low coverage",
            "Focus on critical paths",
        ],
        confidence_score=0.95,
        execution_metadata=execution_metadata,
        total_coverage_percentage=repo_dto.coverage or 0.0,
        covered_lines=totals.get("hits", 0) or 0,
        total_lines=totals.get("lines", 0) or 0,
        file_count=0,
        covered_file_count=0,
        additional_context={
            "repository_name": repo_dto.name,
            "owner": repo_dto.owner,
            "url": repo_dto.url,
            "default_branch": repo_dto.branch,
            "last_update": repo_dto.last_update.isoformat() if repo_dto.last_update else None,
        },
    )


def map_file_to_coverage(
    file_dto: FileDTO,
    execution_metadata: ExecutionMetadata,
) -> FileCoverage:
    """Map Codecov file DTO to domain model.

    Args:
        file_dto: Codecov file DTO
        execution_metadata: Execution metadata

    Returns:
        File coverage domain model
    """
    return FileCoverage(
        summary=f"Coverage for {file_dto.name}",
        key_findings=[
            f"File coverage: {file_dto.coverage or 0}%",
            f"Complexity: {file_dto.complexity or 0}",
        ],
        recommended_next_actions=[
            "Add tests for uncovered lines",
            "Review complex sections",
        ],
        confidence_score=0.90,
        execution_metadata=execution_metadata,
        file_path=file_dto.name,
        coverage_percentage=file_dto.coverage or 0.0,
        covered_lines=file_dto.hits or 0,
        total_lines=file_dto.lines or 0,
        uncovered_lines=[],
        additional_context={
            "misses": file_dto.misses,
            "partials": file_dto.partials,
            "complexity": file_dto.complexity,
        },
    )


def map_comparison_to_delta(
    comparison_dto: ComparisonDTO,
    execution_metadata: ExecutionMetadata,
) -> CoverageDelta:
    """Map Codecov comparison DTO to domain model.

    Args:
        comparison_dto: Codecov comparison DTO
        execution_metadata: Execution metadata

    Returns:
        Coverage delta domain model
    """
    base_coverage = comparison_dto.base_coverage or 0.0
    head_coverage = comparison_dto.head_coverage or 0.0
    delta = head_coverage - base_coverage

    return CoverageDelta(
        summary=f"Coverage change: {delta:+.2f}%",
        key_findings=[
            f"Base coverage: {base_coverage}%",
            f"Head coverage: {head_coverage}%",
            f"Change: {delta:+.2f}%",
            f"Files changed: {comparison_dto.files_changed or 0}",
        ],
        recommended_next_actions=[
            "Review files with coverage decrease",
            "Add tests for new code",
        ] if delta < 0 else [
            "Maintain coverage improvements",
            "Continue adding tests",
        ],
        confidence_score=0.92,
        execution_metadata=execution_metadata,
        base_coverage=base_coverage,
        current_coverage=head_coverage,
        delta_percentage=delta,
        delta_lines=0,
        improved=delta >= 0,
        additional_context={
            "base_commit": comparison_dto.base_commit,
            "head_commit": comparison_dto.head_commit,
            "patch_coverage": comparison_dto.patch_coverage,
            "files_with_change": comparison_dto.files_with_coverage_change,
        },
    )
