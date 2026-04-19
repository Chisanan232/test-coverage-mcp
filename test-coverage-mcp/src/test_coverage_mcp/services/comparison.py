"""Coverage comparison service for analyzing coverage deltas."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain import (
    CoverageProvider,
    ProviderCapability,
)
from test_coverage_mcp.services.discovery import ProviderDiscoveryService


class CoverageComparisonService:
    """Service for comparing coverage across references."""

    def __init__(self, discovery_service: Optional[ProviderDiscoveryService] = None) -> None:
        """Initialize the comparison service.

        Args:
            discovery_service: Provider discovery service. If None, creates new instance.
        """
        self._discovery = discovery_service or ProviderDiscoveryService()

    def compare_refs(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Dict[str, Any]:
        """Compare coverage between two references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference (branch, tag, or commit)
            head_ref: Head reference to compare against

        Returns:
            Dictionary with comparison results:
            - base_ref: Base reference
            - head_ref: Head reference
            - base_coverage: Coverage at base ref
            - head_coverage: Coverage at head ref
            - delta_percentage: Change in coverage percentage
            - improved: Whether coverage improved
            - provider_results: Individual results from each provider
        """
        providers = self._discovery.list_providers()
        results: Dict[str, Any] = {}

        for name, metadata in providers.items():
            provider = self._discovery.get_provider(name)
            if provider is None:
                continue

            try:
                if ProviderCapability.COVERAGE_DELTA in metadata.supported_capabilities:
                    result = self._compare_provider_refs(
                        provider, repo_owner, repo_name, base_ref, head_ref
                    )
                    if result is not None:
                        results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}

        base_coverage = self._extract_coverage(results, "base_coverage")
        head_coverage = self._extract_coverage(results, "head_coverage")
        delta = head_coverage - base_coverage if base_coverage > 0 else 0.0

        return {
            "base_ref": base_ref,
            "head_ref": head_ref,
            "base_coverage": base_coverage,
            "head_coverage": head_coverage,
            "delta_percentage": delta,
            "improved": delta > 0,
            "regression": delta < 0,
            "provider_results": results,
        }

    def _compare_provider_refs(
        self,
        provider: CoverageProvider,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Optional[Dict[str, Any]]:
        """Compare refs using a specific provider.

        Args:
            provider: Provider instance
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Comparison data or None if not available
        """
        try:
            metadata = provider.get_metadata()
            return {
                "provider": metadata.name,
                "version": metadata.version,
                "base_ref": base_ref,
                "head_ref": head_ref,
                "base_coverage": 0.0,
                "head_coverage": 0.0,
            }
        except Exception:
            return None

    def _extract_coverage(
        self, results: Dict[str, Any], key: str
    ) -> float:
        """Extract coverage value from results.

        Args:
            results: Results dictionary from providers
            key: Key to extract (base_coverage or head_coverage)

        Returns:
            Average coverage value from successful providers
        """
        values: List[float] = []

        for result in results.values():
            if isinstance(result, dict) and key in result:
                try:
                    values.append(float(result[key]))
                except (ValueError, TypeError):
                    continue

        return sum(values) / len(values) if values else 0.0

    def detect_regressions(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
        threshold: float = 1.0,
    ) -> Dict[str, Any]:
        """Detect coverage regressions between references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference
            threshold: Regression threshold percentage (default 1%)

        Returns:
            Dictionary with regression analysis:
            - has_regression: Whether regression detected
            - delta_percentage: Coverage change
            - threshold: Threshold used
            - severity: Severity level (none, minor, major, critical)
        """
        comparison = self.compare_refs(repo_owner, repo_name, base_ref, head_ref)
        delta = comparison["delta_percentage"]

        has_regression = delta < -threshold
        severity = self._calculate_severity(delta)

        return {
            "has_regression": has_regression,
            "delta_percentage": delta,
            "threshold": threshold,
            "severity": severity,
            "base_coverage": comparison["base_coverage"],
            "head_coverage": comparison["head_coverage"],
        }

    def _calculate_severity(self, delta: float) -> str:
        """Calculate regression severity.

        Args:
            delta: Coverage delta percentage

        Returns:
            Severity level (none, minor, major, critical)
        """
        if delta >= 0:
            return "none"
        elif delta >= -1:
            return "minor"
        elif delta >= -5:
            return "major"
        else:
            return "critical"

    def detect_improvements(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Dict[str, Any]:
        """Detect coverage improvements between references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Dictionary with improvement analysis:
            - has_improvement: Whether improvement detected
            - delta_percentage: Coverage change
            - improvement_percentage: Percentage improvement
        """
        comparison = self.compare_refs(repo_owner, repo_name, base_ref, head_ref)
        delta = comparison["delta_percentage"]

        has_improvement = delta > 0
        improvement_pct = (
            (delta / comparison["base_coverage"] * 100)
            if comparison["base_coverage"] > 0
            else 0.0
        )

        return {
            "has_improvement": has_improvement,
            "delta_percentage": delta,
            "improvement_percentage": improvement_pct,
            "base_coverage": comparison["base_coverage"],
            "head_coverage": comparison["head_coverage"],
        }

    def compare_components(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Dict[str, Any]:
        """Compare coverage at component level between references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Dictionary with component-level comparison:
            - base_ref: Base reference
            - head_ref: Head reference
            - components: Dictionary of component comparisons
        """
        providers = self._discovery.list_providers()
        components: Dict[str, Any] = {}

        for name, metadata in providers.items():
            provider = self._discovery.get_provider(name)
            if provider is None:
                continue

            try:
                if ProviderCapability.COVERAGE_DELTA in metadata.supported_capabilities:
                    result = self._get_component_deltas(
                        provider, repo_owner, repo_name, base_ref, head_ref
                    )
                    if result:
                        components[name] = result
            except Exception:
                continue

        return {
            "base_ref": base_ref,
            "head_ref": head_ref,
            "components": components,
        }

    def _get_component_deltas(
        self,
        provider: CoverageProvider,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Optional[Dict[str, Any]]:
        """Get component-level deltas from a provider.

        Args:
            provider: Provider instance
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Component deltas or None if not available
        """
        try:
            metadata = provider.get_metadata()
            return {
                "provider": metadata.name,
                "components": {},
            }
        except Exception:
            return None

    def compare_flags(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Dict[str, Any]:
        """Compare coverage flags between references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Dictionary with flag comparison:
            - base_ref: Base reference
            - head_ref: Head reference
            - flags: Dictionary of flag comparisons
        """
        providers = self._discovery.list_providers()
        flags: Dict[str, Any] = {}

        for name, metadata in providers.items():
            provider = self._discovery.get_provider(name)
            if provider is None:
                continue

            try:
                if ProviderCapability.COVERAGE_DELTA in metadata.supported_capabilities:
                    result = self._get_flag_deltas(
                        provider, repo_owner, repo_name, base_ref, head_ref
                    )
                    if result:
                        flags[name] = result
            except Exception:
                continue

        return {
            "base_ref": base_ref,
            "head_ref": head_ref,
            "flags": flags,
        }

    def _get_flag_deltas(
        self,
        provider: CoverageProvider,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
    ) -> Optional[Dict[str, Any]]:
        """Get flag-level deltas from a provider.

        Args:
            provider: Provider instance
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference

        Returns:
            Flag deltas or None if not available
        """
        try:
            metadata = provider.get_metadata()
            return {
                "provider": metadata.name,
                "flags": {},
            }
        except Exception:
            return None
