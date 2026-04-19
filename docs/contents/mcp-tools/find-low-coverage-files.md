# find_low_coverage_files Tool

## Overview

The `find_low_coverage_files` tool identifies files in a repository with coverage below a specified threshold. It analyzes repository coverage data and ranks files by improvement potential, helping teams prioritize coverage improvement efforts.

This tool leverages the `CoverageGapDiscoveryService` to analyze file coverage and provides actionable insights for coverage improvement.

## Function Signature

```python
def find_low_coverage_files(
    repo_slug: str,
    provider: str,
    ref: str,
    threshold: float = 80.0,
    limit: int = 10,
) -> Dict[str, Any]
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repo_slug` | `str` | Yes | - | Repository slug in format `owner/repo` |
| `provider` | `str` | Yes | - | Coverage provider name (e.g., `codecov`, `coveralls`) |
| `ref` | `str` | Yes | - | Git reference (branch, tag, or commit SHA) |
| `threshold` | `float` | No | `80.0` | Coverage threshold percentage (0-100) |
| `limit` | `int` | No | `10` | Maximum number of files to return |

## Return Value

Returns a dictionary with the following structure:

```python
{
    "ref": str,                           # Git reference analyzed
    "threshold": float,                   # Coverage threshold used
    "total_files": int,                   # Total files analyzed
    "files_below_threshold": int,         # Number of files below threshold
    "low_coverage_files": [               # List of files with low coverage
        {
            "file_path": str,             # Path to the file
            "coverage_percentage": float, # File coverage percentage
            "covered_lines": int,         # Number of covered lines
            "total_lines": int,           # Total number of lines
            "improvement_potential": float, # Potential coverage improvement
        },
        ...
    ],
    "summary": str,                       # Summary of findings
}
```

## Error Responses

The tool returns error responses for invalid inputs:

```python
{
    "error": str,           # Error message
    "error_code": str,      # Error code (INVALID_REPO_SLUG, INVALID_THRESHOLD)
}
```

## Usage Examples

### Find files below 80% coverage (default)

```python
result = find_low_coverage_files(
    repo_slug="myorg/myapp",
    provider="codecov",
    ref="main",
)
```

### Find files below 70% coverage with custom limit

```python
result = find_low_coverage_files(
    repo_slug="myorg/myapp",
    provider="codecov",
    ref="develop",
    threshold=70.0,
    limit=20,
)
```

### Find files below 90% coverage for a specific commit

```python
result = find_low_coverage_files(
    repo_slug="myorg/myapp",
    provider="codecov",
    ref="abc123def456",
    threshold=90.0,
    limit=5,
)
```

## Output Interpretation

### Coverage Percentage

The `coverage_percentage` indicates what percentage of lines in the file are covered by tests:
- 0-50%: Very low coverage, high priority for improvement
- 50-70%: Low coverage, should be improved
- 70-80%: Moderate coverage, could be improved
- 80-90%: Good coverage, acceptable for most code
- 90-100%: Excellent coverage

### Improvement Potential

The `improvement_potential` shows how much coverage could increase if the file reached the threshold:
- Higher values indicate more potential for improvement
- Files are ranked by this value to help prioritize efforts

## Best Practices

1. **Start with high-impact files**: Focus on files with high improvement potential
2. **Set realistic thresholds**: 80% is a good default, adjust based on your project
3. **Prioritize by size**: Larger files with low coverage have more impact
4. **Iterate regularly**: Run this tool regularly to track progress
5. **Combine with other tools**: Use with `recommend_test_plan` for specific test recommendations

## Related Tools

- **recommend_test_plan**: Get specific test recommendations for coverage improvement
- **analyze_pr_coverage_risk**: Analyze coverage risk in pull requests
- **get_repository_test_health**: Get overall repository health metrics

## Error Handling

### Invalid Repository Slug

```python
result = find_low_coverage_files(
    repo_slug="invalid",  # Missing owner/repo format
    provider="codecov",
    ref="main",
)
# Returns: {"error": "Invalid repo_slug format: invalid. Expected 'owner/repo'", "error_code": "INVALID_REPO_SLUG"}
```

### Invalid Threshold

```python
result = find_low_coverage_files(
    repo_slug="owner/repo",
    provider="codecov",
    ref="main",
    threshold=150.0,  # Above 100
)
# Returns: {"error": "Invalid threshold: 150.0. Must be between 0 and 100", "error_code": "INVALID_THRESHOLD"}
```

## Performance Considerations

- The tool analyzes all files in the repository
- Results are limited by the `limit` parameter to avoid overwhelming output
- Files are pre-sorted by improvement potential for efficiency

## See Also

- [MCP Tools Overview](./overview.md)
- [Test Plan Recommendation](./recommend-test-plan.md)
- [PR Risk Analysis](./analyze-pr-risk.md)
