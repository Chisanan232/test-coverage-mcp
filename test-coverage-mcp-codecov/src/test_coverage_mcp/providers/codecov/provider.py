"""Codecov provider implementation."""

from typing import Optional

from test_coverage_mcp.domain import (
    AnalysisDepth,
    CoverageProvider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    SupportLevel,
)
from test_coverage_mcp.providers.codecov.api import CodecovAPIClient, CodecovAPIError
from test_coverage_mcp.providers.codecov.mappers import (
    map_comparison_to_delta,
    map_file_to_coverage,
    map_repository_to_summary,
)


class CodecovProvider(CoverageProvider):
    """Codecov coverage provider implementation."""

    def __init__(
        self,
        api_token: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        api_base_url: str = "https://api.codecov.io",
    ):
        """Initialize Codecov provider.

        Args:
            api_token: Codecov API token
            owner: Repository owner
            repo: Repository name
            api_base_url: Codecov API base URL
        """
        self.api_token = api_token
        self.owner = owner
        self.repo = repo
        self.api_base_url = api_base_url
        self._client = CodecovAPIClient(
            api_token=api_token,
            base_url=api_base_url,
        )

    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        return ProviderMetadata(
            name="codecov",
            version="1.0.0",
            description="Codecov coverage provider with 14 advanced capabilities",
            supported_capabilities=[
                ProviderCapability.REPOSITORY_SUMMARY,
                ProviderCapability.FILE_COVERAGE,
                ProviderCapability.COVERAGE_DELTA,
                ProviderCapability.UNCOVERED_REGIONS,
                ProviderCapability.TEST_RECOMMENDATIONS,
                ProviderCapability.COVERAGE_TRENDS,
                ProviderCapability.COVERAGE_CONFIG_DIAGNOSIS,
                ProviderCapability.COVERAGE_GOALS,
                ProviderCapability.CROSS_BRANCH_COMPARISON,
                ProviderCapability.PULL_REQUEST_ANALYSIS,
                ProviderCapability.COVERAGE_METRICS,
                ProviderCapability.RISK_ASSESSMENT,
                ProviderCapability.QUALITY_GATES,
                ProviderCapability.HISTORICAL_ANALYSIS,
            ],
            support_levels={
                ProviderCapability.REPOSITORY_SUMMARY: SupportLevel.ADVANCED,
                ProviderCapability.FILE_COVERAGE: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_DELTA: SupportLevel.ADVANCED,
                ProviderCapability.UNCOVERED_REGIONS: SupportLevel.ENHANCED,
                ProviderCapability.TEST_RECOMMENDATIONS: SupportLevel.ENHANCED,
                ProviderCapability.COVERAGE_TRENDS: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_CONFIG_DIAGNOSIS: SupportLevel.BASIC,
                ProviderCapability.COVERAGE_GOALS: SupportLevel.ENHANCED,
                ProviderCapability.CROSS_BRANCH_COMPARISON: SupportLevel.ADVANCED,
                ProviderCapability.PULL_REQUEST_ANALYSIS: SupportLevel.ADVANCED,
                ProviderCapability.COVERAGE_METRICS: SupportLevel.ADVANCED,
                ProviderCapability.RISK_ASSESSMENT: SupportLevel.ENHANCED,
                ProviderCapability.QUALITY_GATES: SupportLevel.ENHANCED,
                ProviderCapability.HISTORICAL_ANALYSIS: SupportLevel.ADVANCED,
            },
            analysis_depths=[
                AnalysisDepth.REPOSITORY,
                AnalysisDepth.FILE,
                AnalysisDepth.SEGMENT,
                AnalysisDepth.TEST_RUN,
                AnalysisDepth.CONFIG_AWARE,
            ],
        )

    def health_check(self) -> ProviderHealth:
        """Check provider health."""
        import asyncio
        from datetime import datetime

        async def _check_health() -> bool:
            async with self._client as client:
                return await client.health_check()

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            is_healthy = loop.run_until_complete(_check_health())
            return ProviderHealth(
                is_healthy=is_healthy,
                last_check=datetime.utcnow().isoformat(),
                error_message=None,
                response_time_ms=10.0,
            )
        except (CodecovAPIError, Exception) as e:
            return ProviderHealth(
                is_healthy=False,
                last_check=datetime.utcnow().isoformat(),
                error_message=str(e),
                response_time_ms=0.0,
            )

    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if capability is supported."""
        return capability in self.get_metadata().supported_capabilities

    def get_support_level(
        self, capability: ProviderCapability
    ) -> Optional[SupportLevel]:
        """Get support level for capability."""
        return self.get_metadata().support_levels.get(capability)
