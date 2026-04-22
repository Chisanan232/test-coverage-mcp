# find_untested_changed_code Tool

## Overview

The `find_untested_changed_code` tool analyzes coverage gaps in changed code between two references (branches, tags, or commits). It identifies uncovered regions that need test coverage and provides risk level assessments for each gap.

This tool leverages the `CoverageGapDiscoveryService` to detect and analyze coverage gaps, with built-in support for pending analysis states from coverage providers like Codecov.

## Function Signature

```python
def find_untested_changed_code(
    repo_slug: str,
    provider: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_slug` | `str` | Yes | Repository slug in format `owner/repo` |
| `provider` | `str` | Yes | Coverage provider name (e.g., `codecov`, `coveralls`) |
| `base_ref` | `str` | Yes | Base reference (branch, tag, or commit SHA) |
| `head_ref` | `str` | Yes | Head reference to compare against |

## Return Value

Returns a dictionary with the following structure:

```python
{
    "base_ref": str,                          # Base reference used
    "head_ref": str,                          # Head reference used
    "total_changed_lines": int,               # Total lines changed
    "covered_changed_lines": int,             # Lines changed that are covered
    "uncovered_changed_lines": int,           # Lines changed that are uncovered
    "coverage_percentage": float,             # Coverage of changed code (0-100)
    "uncovered_regions": [                    # List of uncovered regions
        {
            "file_path": str,                 # Path to the file
            "start_line": int,                # Start line number
            "end_line": int,                  # End line number
            "region_type": str,               # Type: function, class, method, block, branch, line
            "risk_level": str,                # Risk level: low, medium, high, critical
            "lines_count": int,               # Number of lines in region
        },
        ...
    ],
    "pending_regions": [                      # Regions with pending analysis
        {
            "start": int,                     # Start line
            "end": int,                       # End line
            "status": str,                    # Status: analyzing, pending
        },
        ...
    ],
    "has_pending": bool,                      # Whether pending analysis exists
    "gap_summary": str,                       # Human-readable summary of gaps
}
```

## Error Responses

### Invalid Repository Slug

```python
{
    "error": "Invalid repo_slug format: invalid. Expected 'owner/repo'",
    "error_code": "INVALID_REPO_SLUG",
}
```

## Examples

### Basic Usage

```python
from test_coverage_mcp.mcp_server.tools import find_untested_changed_code

result = find_untested_changed_code(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

print(f"Coverage of changed code: {result['coverage_percentage']:.1f}%")
print(f"Uncovered lines: {result['uncovered_changed_lines']}")
print(f"Gap summary: {result['gap_summary']}")
```

### Handling Pending Analysis

```python
result = find_untested_changed_code(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

if result["has_pending"]:
    print(f"⏳ Analysis in progress ({len(result['pending_regions'])} regions)")
    print("Recommendations:")
    for rec in result.get("recommendations", []):
        print(f"  - {rec}")
else:
    print(f"✓ Analysis complete")
    print(f"Uncovered regions: {len(result['uncovered_regions'])}")
```

### Analyzing Uncovered Regions

```python
result = find_untested_changed_code(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

# Group by risk level
critical_regions = [r for r in result["uncovered_regions"] if r["risk_level"] == "critical"]
high_regions = [r for r in result["uncovered_regions"] if r["risk_level"] == "high"]

print(f"Critical gaps: {len(critical_regions)}")
for region in critical_regions:
    print(f"  {region['file_path']}:{region['start_line']}-{region['end_line']} ({region['region_type']})")

print(f"High gaps: {len(high_regions)}")
```

### Processing Results

```python
result = find_untested_changed_code(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

# Check for errors
if "error" in result:
    print(f"Error: {result['error']}")
    exit(1)

# Analyze coverage
if result["coverage_percentage"] < 80.0:
    print(f"⚠️ Low coverage: {result['coverage_percentage']:.1f}%")
    print(f"Need to add tests for {result['uncovered_changed_lines']} lines")
else:
    print(f"✓ Good coverage: {result['coverage_percentage']:.1f}%")

# List files with gaps
files_with_gaps = {}
for region in result["uncovered_regions"]:
    file_path = region["file_path"]
    if file_path not in files_with_gaps:
        files_with_gaps[file_path] = []
    files_with_gaps[file_path].append(region)

print(f"\nFiles with gaps ({len(files_with_gaps)}):")
for file_path, regions in files_with_gaps.items():
    print(f"  {file_path}: {len(regions)} region(s)")
```

## Use Cases

### 1. PR Review Automation

Automatically check for untested code in pull requests:

```python
def check_pr_coverage(pr_number, base_ref, head_ref):
    result = find_untested_changed_code(
        repo_slug="myorg/myapp",
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    if result["coverage_percentage"] < 80.0:
        return {
            "status": "FAIL",
            "message": f"PR coverage too low: {result['coverage_percentage']:.1f}%",
            "uncovered_regions": result["uncovered_regions"],
        }

    return {"status": "PASS", "message": "Coverage meets threshold"}
```

### 2. Test Gap Analysis

Identify which parts of changed code need tests:

```python
def analyze_test_gaps(repo_slug, base_ref, head_ref):
    result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    # Group by region type
    gaps_by_type = {}
    for region in result["uncovered_regions"]:
        region_type = region["region_type"]
        if region_type not in gaps_by_type:
            gaps_by_type[region_type] = []
        gaps_by_type[region_type].append(region)

    return gaps_by_type
```

### 3. CI/CD Integration

Fail the build if critical coverage gaps exist:

```python
def ci_coverage_check(repo_slug, base_ref, head_ref):
    result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    # Check for critical gaps
    critical_gaps = [r for r in result["uncovered_regions"] if r["risk_level"] == "critical"]

    if critical_gaps:
        print(f"❌ Build failed: {len(critical_gaps)} critical coverage gaps")
        return False

    print(f"✓ Build passed: Coverage acceptable")
    return True
```

### 4. Pending Analysis Handling

Handle incomplete coverage analysis gracefully:

```python
def check_with_pending_handling(repo_slug, base_ref, head_ref):
    result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    if result["has_pending"]:
        print(f"⏳ Analysis in progress ({len(result['pending_regions'])} regions)")
        print("Recommendations:")
        for rec in result.get("recommendations", []):
            print(f"  - {rec}")
        return None  # Defer decision

    # Analysis complete
    return result["coverage_percentage"]
```

## Performance Considerations

### Execution Time

- **No changes**: < 100ms
- **Small PR (< 50 lines)**: 100-500ms
- **Medium PR (50-500 lines)**: 500ms-2s
- **Large PR (> 500 lines)**: 2-10s

### Optimization Tips

1. **Limit scope**: Analyze only changed files, not entire codebase
2. **Cache results**: Store results to avoid re-analysis
3. **Batch operations**: Process multiple PRs in parallel
4. **Handle pending**: Don't wait indefinitely for pending analysis

## Limitations

1. **Provider dependent**: Results depend on coverage provider accuracy
2. **Pending analysis**: Some providers have async analysis that may not be complete
3. **Line-level only**: Doesn't account for branch/condition coverage
4. **Dead code**: May flag unreachable code as gaps
5. **Dynamic code**: May miss dynamically generated code

## Related Tools

- **analyze_pr_coverage_risk**: Assess overall PR risk level
- **get_commit_coverage_summary**: Get coverage for specific commit
- **compare_coverage_between_refs**: Compare coverage between references

## Troubleshooting

### No Uncovered Regions Found

**Cause**: All changed code is covered or no file data available

**Solution**: Verify that:
1. Coverage data is available from provider
2. Files were actually changed
3. Provider supports the repository

### Pending Regions Not Resolving

**Cause**: Coverage provider still analyzing data

**Solution**:
1. Wait for provider to complete analysis
2. Check provider status page
3. Re-run tool after a delay

### Invalid Repository Slug

**Cause**: Repo slug not in `owner/repo` format

**Solution**: Ensure repo slug is formatted correctly:
```python
# ✓ Correct
repo_slug = "myorg/myapp"

# ✗ Incorrect
repo_slug = "myapp"
repo_slug = "myorg/myapp/extra"
```

## API Reference

See `FindUntestedCodeInput` and `FindUntestedCodeOutput` models in:
- `test_coverage_mcp.mcp_server.tools.models.pr_analysis`
