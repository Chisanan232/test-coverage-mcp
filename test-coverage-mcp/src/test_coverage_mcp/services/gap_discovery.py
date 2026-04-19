"""Coverage gap discovery service for analyzing uncovered code regions."""

from typing import Any, Dict, List, Optional

from test_coverage_mcp.domain import RiskLevel


class CoverageGapDiscoveryService:
    """Service for discovering and analyzing coverage gaps in code."""

    def __init__(self) -> None:
        """Initialize the gap discovery service."""
        self._gap_type_risk_map = {
            "function": RiskLevel.HIGH,
            "class": RiskLevel.HIGH,
            "method": RiskLevel.MEDIUM,
            "block": RiskLevel.MEDIUM,
            "branch": RiskLevel.LOW,
            "line": RiskLevel.LOW,
        }

    def analyze_changed_code(
        self,
        repo_owner: str,
        repo_name: str,
        base_ref: str,
        head_ref: str,
        file_coverage_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze coverage of changed code between references.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            base_ref: Base reference
            head_ref: Head reference
            file_coverage_data: File coverage data (optional)

        Returns:
            Dictionary with changed code analysis:
            - total_changed_lines: Total lines changed
            - covered_changed_lines: Lines changed that are covered
            - uncovered_changed_lines: Lines changed that are uncovered
            - coverage_percentage: Coverage of changed code
            - files_with_gaps: Files with coverage gaps in changes
            - gap_summary: Summary of gaps found
        """
        # Initialize analysis results
        total_changed_lines = 0
        covered_changed_lines = 0
        uncovered_changed_lines = 0
        files_with_gaps: List[Dict[str, Any]] = []

        # Analyze file coverage data if provided
        if file_coverage_data:
            for file_path, coverage_info in file_coverage_data.items():
                changed_lines = coverage_info.get("changed_lines", 0)
                if changed_lines > 0:
                    total_changed_lines += changed_lines
                    covered_lines = coverage_info.get("covered_changed_lines", 0)
                    covered_changed_lines += covered_lines
                    uncovered_lines = changed_lines - covered_lines
                    uncovered_changed_lines += uncovered_lines

                    if uncovered_lines > 0:
                        files_with_gaps.append(
                            {
                                "file_path": file_path,
                                "changed_lines": changed_lines,
                                "covered_lines": covered_lines,
                                "uncovered_lines": uncovered_lines,
                                "coverage": (
                                    (covered_lines / changed_lines * 100) if changed_lines > 0 else 0.0
                                ),
                            }
                        )

        # Calculate coverage percentage
        coverage_percentage = (
            (covered_changed_lines / total_changed_lines * 100)
            if total_changed_lines > 0
            else 0.0
        )

        # Generate gap summary
        gap_summary = self._generate_gap_summary(
            total_changed_lines, uncovered_changed_lines, coverage_percentage
        )

        return {
            "base_ref": base_ref,
            "head_ref": head_ref,
            "total_changed_lines": total_changed_lines,
            "covered_changed_lines": covered_changed_lines,
            "uncovered_changed_lines": uncovered_changed_lines,
            "coverage_percentage": coverage_percentage,
            "files_with_gaps": files_with_gaps,
            "gap_summary": gap_summary,
        }

    def detect_uncovered_regions(
        self,
        file_path: str,
        coverage_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Detect uncovered regions in a file.

        Args:
            file_path: Path to the file
            coverage_data: Coverage data for the file

        Returns:
            List of uncovered regions with details:
            - start_line: Start line number
            - end_line: End line number
            - region_type: Type of region (function, class, etc.)
            - risk_level: Risk level of uncovered region
            - lines_count: Number of lines in region
            - context: Code context (optional)
        """
        uncovered_regions: List[Dict[str, Any]] = []

        uncovered_lines = coverage_data.get("uncovered_lines", [])
        if not uncovered_lines:
            return uncovered_regions

        # Group consecutive uncovered lines into regions
        regions = self._group_uncovered_lines(uncovered_lines)

        for region in regions:
            start_line = region["start"]
            end_line = region["end"]
            lines_count = end_line - start_line + 1

            # Determine region type (simplified - in real implementation would parse code)
            region_type = self._infer_region_type(lines_count, coverage_data)

            # Determine risk level
            risk_level = self._gap_type_risk_map.get(region_type, RiskLevel.MEDIUM)

            uncovered_regions.append(
                {
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "region_type": region_type,
                    "risk_level": risk_level.value,
                    "lines_count": lines_count,
                }
            )

        return uncovered_regions

    def analyze_partially_covered_regions(
        self,
        file_path: str,
        coverage_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Analyze regions with partial coverage.

        Args:
            file_path: Path to the file
            coverage_data: Coverage data for the file

        Returns:
            List of partially covered regions:
            - start_line: Start line number
            - end_line: End line number
            - coverage_percentage: Coverage percentage of region
            - covered_lines: Number of covered lines
            - uncovered_lines: Number of uncovered lines
            - risk_level: Risk level
        """
        partially_covered: List[Dict[str, Any]] = []

        # Get coverage by line
        coverage_by_line = coverage_data.get("coverage_by_line", {})
        if not coverage_by_line:
            return partially_covered

        # Find regions with mixed coverage
        regions = self._find_mixed_coverage_regions(coverage_by_line)

        for region in regions:
            start_line = region["start"]
            end_line = region["end"]
            covered_count = region["covered"]
            uncovered_count = region["uncovered"]
            total_count = covered_count + uncovered_count

            coverage_percentage = (
                (covered_count / total_count * 100) if total_count > 0 else 0.0
            )

            # Determine risk level based on coverage
            if coverage_percentage < 30.0:
                risk_level = RiskLevel.CRITICAL
            elif coverage_percentage < 60.0:
                risk_level = RiskLevel.HIGH
            elif coverage_percentage < 80.0:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            partially_covered.append(
                {
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "coverage_percentage": coverage_percentage,
                    "covered_lines": covered_count,
                    "uncovered_lines": uncovered_count,
                    "risk_level": risk_level.value,
                }
            )

        return partially_covered

    def handle_pending_analysis(
        self,
        file_path: str,
        pending_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle coverage data with pending analysis states.

        Args:
            file_path: Path to the file
            pending_data: Data with pending analysis states

        Returns:
            Dictionary with pending analysis handling:
            - has_pending: Whether pending analysis exists
            - pending_regions: Regions with pending analysis
            - estimated_coverage: Estimated coverage if pending completes
            - recommendations: Recommendations for handling pending
        """
        pending_regions = pending_data.get("pending_regions", [])
        has_pending = len(pending_regions) > 0

        estimated_coverage = pending_data.get("coverage", 0.0)
        if has_pending and pending_data.get("pending_coverage_estimate"):
            # Estimate coverage assuming pending analysis completes
            estimated_coverage = pending_data["pending_coverage_estimate"]

        recommendations: List[str] = []
        if has_pending:
            recommendations.append("Pending analysis in progress - results may change")
            recommendations.append(f"Wait for {len(pending_regions)} pending region(s) to complete")
            recommendations.append("Re-check coverage after analysis completes")

        return {
            "file_path": file_path,
            "has_pending": has_pending,
            "pending_regions_count": len(pending_regions),
            "pending_regions": pending_regions,
            "current_coverage": pending_data.get("coverage", 0.0),
            "estimated_coverage": estimated_coverage,
            "recommendations": recommendations,
        }

    def _group_uncovered_lines(self, uncovered_lines: List[int]) -> List[Dict[str, int]]:
        """Group consecutive uncovered lines into regions.

        Args:
            uncovered_lines: List of uncovered line numbers

        Returns:
            List of regions with start and end lines
        """
        if not uncovered_lines:
            return []

        sorted_lines = sorted(set(uncovered_lines))
        regions: List[Dict[str, int]] = []
        current_region_start = sorted_lines[0]
        current_region_end = sorted_lines[0]

        for line_num in sorted_lines[1:]:
            if line_num == current_region_end + 1:
                # Extend current region
                current_region_end = line_num
            else:
                # Save current region and start new one
                regions.append({"start": current_region_start, "end": current_region_end})
                current_region_start = line_num
                current_region_end = line_num

        # Add final region
        regions.append({"start": current_region_start, "end": current_region_end})

        return regions

    def _find_mixed_coverage_regions(
        self, coverage_by_line: Dict[int, bool]
    ) -> List[Dict[str, Any]]:
        """Find regions with mixed coverage (some covered, some not).

        Args:
            coverage_by_line: Dictionary mapping line numbers to coverage status

        Returns:
            List of regions with mixed coverage
        """
        if not coverage_by_line:
            return []

        sorted_lines = sorted(coverage_by_line.keys())
        regions: List[Dict[str, Any]] = []
        current_region_start = sorted_lines[0]
        current_region_end = sorted_lines[0]
        covered_count = 1 if coverage_by_line[sorted_lines[0]] else 0
        uncovered_count = 0 if coverage_by_line[sorted_lines[0]] else 1

        for line_num in sorted_lines[1:]:
            if line_num == current_region_end + 1:
                # Extend current region
                current_region_end = line_num
                if coverage_by_line[line_num]:
                    covered_count += 1
                else:
                    uncovered_count += 1
            else:
                # Check if region has mixed coverage
                if covered_count > 0 and uncovered_count > 0:
                    regions.append(
                        {
                            "start": current_region_start,
                            "end": current_region_end,
                            "covered": covered_count,
                            "uncovered": uncovered_count,
                        }
                    )

                # Start new region
                current_region_start = line_num
                current_region_end = line_num
                covered_count = 1 if coverage_by_line[line_num] else 0
                uncovered_count = 0 if coverage_by_line[line_num] else 1

        # Check final region
        if covered_count > 0 and uncovered_count > 0:
            regions.append(
                {
                    "start": current_region_start,
                    "end": current_region_end,
                    "covered": covered_count,
                    "uncovered": uncovered_count,
                }
            )

        return regions

    def _infer_region_type(self, lines_count: int, coverage_data: Dict[str, Any]) -> str:
        """Infer the type of region based on size and context.

        Args:
            lines_count: Number of lines in region
            coverage_data: Coverage data context

        Returns:
            Region type (function, class, method, block, branch, line)
        """
        if lines_count > 50:
            return "class"
        elif lines_count > 20:
            return "function"
        elif lines_count > 10:
            return "method"
        elif lines_count > 3:
            return "block"
        elif lines_count > 1:
            return "branch"
        else:
            return "line"

    def _generate_gap_summary(
        self,
        total_changed_lines: int,
        uncovered_changed_lines: int,
        coverage_percentage: float,
    ) -> str:
        """Generate a summary of coverage gaps.

        Args:
            total_changed_lines: Total lines changed
            uncovered_changed_lines: Uncovered lines changed
            coverage_percentage: Coverage percentage

        Returns:
            Summary string
        """
        if total_changed_lines == 0:
            return "No changes detected"

        if coverage_percentage == 100.0:
            return f"✓ All {total_changed_lines} changed lines are covered"

        if coverage_percentage == 0.0:
            return f"✗ None of the {total_changed_lines} changed lines are covered"

        return (
            f"{uncovered_changed_lines} of {total_changed_lines} changed lines are uncovered "
            f"({coverage_percentage:.1f}% covered)"
        )
