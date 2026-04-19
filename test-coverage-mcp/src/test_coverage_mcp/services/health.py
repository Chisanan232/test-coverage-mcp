"""Repository health service for aggregating coverage metrics."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain import (
    CoverageProvider,
    ProviderCapability,
    ProviderHealth,
    RiskLevel,
)
from test_coverage_mcp.services.discovery import ProviderDiscoveryService


class RepositoryHealthService:
    """Service for analyzing repository health across providers."""

    def __init__(self, discovery_service: Optional[ProviderDiscoveryService] = None) -> None:
        """Initialize the health service.

        Args:
            discovery_service: Provider discovery service. If None, creates new instance.
        """
        self._discovery = discovery_service or ProviderDiscoveryService()

    def aggregate_coverage_metrics(
        self, repo_owner: str, repo_name: str
    ) -> Dict[str, Any]:
        """Aggregate coverage metrics from all available providers.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Dictionary with aggregated metrics:
            - providers_queried: Number of providers queried
            - providers_succeeded: Number of providers that returned data
            - providers_failed: Number of providers that failed
            - average_coverage: Average coverage across providers
            - coverage_range: Min and max coverage values
            - provider_results: Individual results from each provider
        """
        providers = self._discovery.list_providers()
        results: Dict[str, Any] = {}
        coverage_values: List[float] = []

        for name, metadata in providers.items():
            provider = self._discovery.get_provider(name)
            if provider is None:
                continue

            try:
                if ProviderCapability.REPOSITORY_SUMMARY in metadata.supported_capabilities:
                    result = self._query_provider_coverage(provider, repo_owner, repo_name)
                    if result is not None:
                        results[name] = result
                        if "coverage_percentage" in result:
                            coverage_values.append(result["coverage_percentage"])
            except Exception as e:
                results[name] = {"error": str(e)}

        avg_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0
        coverage_range = {
            "min": min(coverage_values) if coverage_values else 0.0,
            "max": max(coverage_values) if coverage_values else 0.0,
        }

        return {
            "providers_queried": len(providers),
            "providers_succeeded": len([r for r in results.values() if "error" not in r]),
            "providers_failed": len([r for r in results.values() if "error" in r]),
            "average_coverage": avg_coverage,
            "coverage_range": coverage_range,
            "provider_results": results,
        }

    def _query_provider_coverage(
        self, provider: CoverageProvider, repo_owner: str, repo_name: str
    ) -> Optional[Dict[str, Any]]:
        """Query a provider for coverage information.

        Args:
            provider: Provider instance
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            Coverage data or None if not available
        """
        try:
            metadata = provider.get_metadata()
            return {
                "provider": metadata.name,
                "version": metadata.version,
                "repo_owner": repo_owner,
                "repo_name": repo_name,
            }
        except Exception:
            return None

    def identify_risks(
        self, repo_owner: str, repo_name: str, threshold: float = 80.0
    ) -> Dict[str, Any]:
        """Identify coverage risks in the repository.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            threshold: Coverage threshold below which to flag as risk (default 80%)

        Returns:
            Dictionary with risk analysis:
            - risk_level: Overall risk level (low, medium, high, critical)
            - coverage_below_threshold: Whether coverage is below threshold
            - threshold: The threshold used
            - recommendations: List of recommendations
        """
        metrics = self.aggregate_coverage_metrics(repo_owner, repo_name)
        avg_coverage = metrics.get("average_coverage", 0.0)

        if avg_coverage >= threshold:
            risk_level = RiskLevel.LOW
        elif avg_coverage >= threshold - 10:
            risk_level = RiskLevel.MEDIUM
        elif avg_coverage >= threshold - 20:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        recommendations = self._generate_risk_recommendations(avg_coverage, threshold)

        return {
            "risk_level": risk_level.value,
            "coverage_below_threshold": avg_coverage < threshold,
            "current_coverage": avg_coverage,
            "threshold": threshold,
            "gap": max(0, threshold - avg_coverage),
            "recommendations": recommendations,
        }

    def _generate_risk_recommendations(
        self, current_coverage: float, threshold: float
    ) -> List[str]:
        """Generate recommendations based on coverage gap.

        Args:
            current_coverage: Current coverage percentage
            threshold: Target threshold

        Returns:
            List of recommendations
        """
        recommendations: List[str] = []

        if current_coverage < threshold:
            gap = threshold - current_coverage
            recommendations.append(
                f"Increase coverage by {gap:.1f}% to meet the {threshold}% threshold"
            )

        if current_coverage < 50:
            recommendations.append("Critical: Coverage is below 50%. Prioritize test coverage.")
        elif current_coverage < 70:
            recommendations.append("High priority: Focus on increasing coverage to 70%+")
        elif current_coverage < 85:
            recommendations.append("Medium priority: Aim for 85%+ coverage")

        recommendations.append("Review uncovered regions and prioritize high-risk areas")
        recommendations.append("Implement continuous coverage monitoring")

        return recommendations

    def get_next_actions(
        self, repo_owner: str, repo_name: str
    ) -> List[str]:
        """Generate next actions for improving repository health.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name

        Returns:
            List of recommended next actions
        """
        metrics = self.aggregate_coverage_metrics(repo_owner, repo_name)
        risk = self.identify_risks(repo_owner, repo_name)

        actions: List[str] = []

        if metrics["providers_failed"] > 0:
            actions.append(
                f"Investigate {metrics['providers_failed']} provider(s) that failed to return data"
            )

        actions.extend(risk["recommendations"])

        if metrics["coverage_range"]["max"] - metrics["coverage_range"]["min"] > 20:
            actions.append(
                "Large variance in coverage across providers - investigate discrepancies"
            )

        return actions

    def get_provider_fallback_chain(
        self, required_capabilities: Optional[List[ProviderCapability]] = None
    ) -> List[str]:
        """Get a fallback chain of providers for multi-provider support.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List of provider names in fallback order
        """
        providers = self._discovery.list_providers()
        health_status = self._discovery.get_all_health_status()

        provider_scores: Dict[str, float] = {}

        for name, metadata in providers.items():
            score = 0.0

            if required_capabilities:
                supported = sum(
                    1 for cap in required_capabilities
                    if cap in metadata.supported_capabilities
                )
                score += supported / len(required_capabilities) * 100

            health = health_status.get(name)
            if health and health.is_healthy:
                score += 50
                score -= health.response_time_ms / 10

            provider_scores[name] = score

        sorted_providers = sorted(
            provider_scores.items(), key=lambda x: x[1], reverse=True
        )
        return [name for name, _ in sorted_providers]
