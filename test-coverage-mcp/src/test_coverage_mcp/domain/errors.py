"""Standardized error classes for tool execution."""


class ToolExecutionError(Exception):
    """Base error for tool execution failures."""

    pass


class ProviderNotFoundError(ToolExecutionError):
    """Raised when a requested provider is not found."""

    pass


class InvalidParameterError(ToolExecutionError):
    """Raised when tool parameters are invalid."""

    pass


class ProviderHealthError(ToolExecutionError):
    """Raised when provider health check fails."""

    pass


class ProviderDiscoveryError(ToolExecutionError):
    """Raised when provider discovery fails."""

    pass


class CoverageAnalysisError(ToolExecutionError):
    """Raised when coverage analysis fails."""

    pass


class RepositoryHealthError(ToolExecutionError):
    """Raised when repository health analysis fails."""

    pass


class CommitAnalysisError(ToolExecutionError):
    """Raised when commit analysis fails."""

    pass


class CoverageComparisonError(ToolExecutionError):
    """Raised when coverage comparison fails."""

    pass
