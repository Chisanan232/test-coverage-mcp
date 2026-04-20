"""Mock provider for testing.

Provides a mock implementation of the provider interface for testing.
"""

from typing import Any, Dict, List, Optional


class MockProvider:
    """Mock coverage provider for testing."""

    def __init__(self, name: str = "mock", version: str = "1.0.0"):
        """Initialize mock provider.

        Args:
            name: Provider name
            version: Provider version
        """
        self.name = name
        self.version = version
        self.is_healthy = True

    def get_repository_coverage(
        self, repo_slug: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get repository coverage.

        Args:
            repo_slug: Repository slug
            ref: Git reference

        Returns:
            Coverage data
        """
        return {
            "repo_slug": repo_slug,
            "ref": ref or "master",
            "coverage": 85.5,
            "files_count": 42,
            "lines_covered": 1234,
            "lines_total": 1440,
        }

    def get_file_coverage(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file coverage.

        Args:
            repo_slug: Repository slug
            file_path: File path
            ref: Git reference

        Returns:
            File coverage data
        """
        return {
            "repo_slug": repo_slug,
            "file_path": file_path,
            "ref": ref or "master",
            "coverage": 90.0,
            "lines_covered": 100,
            "lines_total": 111,
        }

    def compare_coverage(
        self, repo_slug: str, base_ref: str, head_ref: str
    ) -> Dict[str, Any]:
        """Compare coverage between refs.

        Args:
            repo_slug: Repository slug
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Comparison data
        """
        return {
            "repo_slug": repo_slug,
            "base_ref": base_ref,
            "head_ref": head_ref,
            "base_coverage": 80.0,
            "head_coverage": 85.5,
            "delta": 5.5,
            "status": "improved",
        }

    def get_uncovered_regions(
        self, repo_slug: str, file_path: str, ref: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get uncovered regions in a file.

        Args:
            repo_slug: Repository slug
            file_path: File path
            ref: Git reference

        Returns:
            List of uncovered regions
        """
        return [
            {
                "line_start": 10,
                "line_end": 15,
                "type": "branch",
                "risk_level": "medium",
            },
            {
                "line_start": 25,
                "line_end": 30,
                "type": "line",
                "risk_level": "high",
            },
        ]

    def health_check(self) -> Dict[str, Any]:
        """Check provider health.

        Returns:
            Health status
        """
        return {
            "status": "healthy" if self.is_healthy else "unhealthy",
            "name": self.name,
            "version": self.version,
            "response_time_ms": 50,
        }

    def get_capabilities(self) -> Dict[str, bool]:
        """Get provider capabilities.

        Returns:
            Capability matrix
        """
        return {
            "repository_summary": True,
            "file_coverage": True,
            "coverage_delta": True,
            "uncovered_regions": True,
            "branch_coverage": True,
            "line_coverage": True,
        }
