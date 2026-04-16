"""Codecov API client using httpx."""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from test_coverage_mcp_codecov.api.dtos import (
    BranchDTO,
    CommitDTO,
    ComparisonDTO,
    FileDTO,
    PullRequestDTO,
    RepositoryDTO,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.codecov.io"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0


class CodecovAPIError(Exception):
    """Error from Codecov API."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize error."""
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class CodecovAPIClient:
    """Codecov API client with async support."""

    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """Initialize Codecov API client.

        Args:
            api_token: Codecov API token
            base_url: Base URL for API (default: https://api.codecov.io)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "CodecovAPIClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication.

        Returns:
            Headers dictionary
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "User-Agent": "test-coverage-mcp/1.0.0",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make authenticated request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            Response JSON data

        Raises:
            CodecovAPIError: If request fails
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_headers())

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs,
                )

                if response.status_code == 429:  # Rate limited
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    raise CodecovAPIError(
                        "Rate limited by Codecov API",
                        status_code=429,
                    )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise CodecovAPIError(
                    f"API error: {e.response.text}",
                    status_code=e.response.status_code,
                ) from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise CodecovAPIError(f"Request failed: {e}") from e

        raise CodecovAPIError("Max retries exceeded")

    async def get_repository(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> RepositoryDTO:
        """Get repository coverage information.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Optional branch name

        Returns:
            Repository coverage data
        """
        params = {}
        if branch:
            params["branch"] = branch

        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}",
            params=params,
        )

        return RepositoryDTO(**data.get("repository", {}))

    async def get_commit(
        self,
        owner: str,
        repo: str,
        commit_sha: str,
    ) -> CommitDTO:
        """Get commit coverage information.

        Args:
            owner: Repository owner
            repo: Repository name
            commit_sha: Commit SHA

        Returns:
            Commit coverage data
        """
        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}/commits/{commit_sha}",
        )

        return CommitDTO(**data.get("commit", {}))

    async def get_file_coverage(
        self,
        owner: str,
        repo: str,
        commit_sha: str,
        file_path: str,
    ) -> FileDTO:
        """Get file coverage information.

        Args:
            owner: Repository owner
            repo: Repository name
            commit_sha: Commit SHA
            file_path: File path

        Returns:
            File coverage data
        """
        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}/commits/{commit_sha}/files/{file_path}",
        )

        return FileDTO(**data.get("file", {}))

    async def get_comparison(
        self,
        owner: str,
        repo: str,
        base_commit: str,
        head_commit: str,
    ) -> ComparisonDTO:
        """Get coverage comparison between commits.

        Args:
            owner: Repository owner
            repo: Repository name
            base_commit: Base commit SHA
            head_commit: Head commit SHA

        Returns:
            Coverage comparison data
        """
        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}/compare/{base_commit}...{head_commit}",
        )

        return ComparisonDTO(**data.get("comparison", {}))

    async def get_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> BranchDTO:
        """Get branch coverage information.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name

        Returns:
            Branch coverage data
        """
        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}/branches/{branch}",
        )

        return BranchDTO(**data.get("branch", {}))

    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
    ) -> PullRequestDTO:
        """Get pull request coverage information.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request coverage data
        """
        data = await self._request(
            "GET",
            f"/api/v2/github/{owner}/{repo}/pulls/{pr_number}",
        )

        return PullRequestDTO(**data.get("pull_request", {}))

    async def health_check(self) -> bool:
        """Check API health.

        Returns:
            True if API is healthy
        """
        try:
            data = await self._request("GET", "/api/v2/health")
            return data.get("status") == "ok"
        except CodecovAPIError:
            return False
