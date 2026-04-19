# compare_coverage_between_refs Tool

## Overview

The `compare_coverage_between_refs` tool analyzes coverage differences between two git references (branches, tags, or commits), identifying improvements, regressions, and providing detailed delta analysis.

## Function Signature

```python
def compare_coverage_between_refs(
    repo_slug: str,
    base_ref: str,
    head_ref: str,
    provider: Optional[str] = None,
    regression_threshold: float = 1.0,
) -> Dict[str, Any]
```

## Parameters

### repo_slug (str, required)

Repository identifier in format `"owner/repo"`.

**Examples**: `"python/cpython"`, `"facebook/react"`, `"torvalds/linux"`

### base_ref (str, required)

Base reference (branch, tag, or commit SHA) to compare from.

**Examples**: `"main"`, `"v1.0.0"`, `"abc123def456"`

### head_ref (str, required)

Head reference to compare against. Must be different from base_ref.

**Examples**: `"feature-branch"`, `"develop"`, `"def456ghi789"`

### provider (str, optional)

Specific provider to use for analysis. If not specified, uses all available providers.

**Examples**: `"codecov"`, `"coveralls"`, `"sonarqube"`

### regression_threshold (float, default: 1.0)

Regression threshold percentage. Coverage drops below this threshold are flagged as regressions.

**Valid range**: 0.0 to 100.0

**Examples**: `0.5`, `1.0`, `2.0`

## Return Value

Returns a dictionary with the following structure:

```python
{
    "repo_slug": str,                   # Repository identifier
    "base_ref": str,                    # Base reference
    "head_ref": str,                    # Head reference
    "coverage_delta": {
        "base_coverage": float,         # Coverage at base ref
        "head_coverage": float,         # Coverage at head ref
        "delta_percentage": float,      # Change in coverage
        "delta_direction": str          # "improved", "regressed", or "unchanged"
    },
    "regression_analysis": {
        "has_regression": bool,         # Whether regression detected
        "severity": str,                # "none", "minor", "major", "critical"
        "threshold": float,             # Threshold used
        "delta_percentage": float       # Coverage delta
    },
    "improvement_analysis": {
        "has_improvement": bool,        # Whether improvement detected
        "delta_percentage": float,      # Coverage delta
        "improvement_percentage": float # Percentage improvement
    },
    "provider_results": {               # Individual results from each provider
        "provider_name": {
            "provider": str,
            "version": str,
            "base_ref": str,
            "head_ref": str,
            "base_coverage": float,
            "head_coverage": float
        }
    },
    "execution_metadata": {
        "provider_name": str,
        "provider_version": str,
        "support_level": str,
        "used_capabilities": [],
        "analysis_depth": str,
        "execution_time_ms": float
    }
}
```

## Regression Severity Levels

Severity is determined based on coverage delta:

- **none**: No regression (delta >= 0%)
- **minor**: Small regression (-1% to 0%)
- **major**: Significant regression (-5% to -1%)
- **critical**: Critical regression (< -5%)

## Error Responses

### Invalid Repository Slug

If the repository slug format is invalid:

```python
{
    "error": "Invalid repo_slug format. Use 'owner/repo'",
    "error_type": "InvalidRepositorySlugError",
    "execution_metadata": { ... }
}
```

### Invalid References

If references are missing or identical:

```python
{
    "error": "Both base_ref and head_ref are required",
    "error_type": "InvalidReferenceError",
    "execution_metadata": { ... }
}
```

### Provider Not Found

If the specified provider doesn't exist:

```python
{
    "error": "Provider 'nonexistent' not found",
    "error_type": "ProviderNotFoundError",
    "execution_metadata": { ... }
}
```

### Comparison Error

If an error occurs during comparison:

```python
{
    "error": "Error message describing what went wrong",
    "error_type": "CoverageComparisonError",
    "repo_slug": "owner/repo",
    "base_ref": "main",
    "head_ref": "feature",
    "execution_metadata": { ... }
}
```

## Examples

### Compare Branches

```python
result = compare_coverage_between_refs("owner/repo", "main", "feature-branch")

delta = result['coverage_delta']
print(f"Base ({delta['base_ref']}): {delta['base_coverage']}%")
print(f"Head ({delta['head_ref']}): {delta['head_coverage']}%")
print(f"Delta: {delta['delta_percentage']:+.1f}%")
print(f"Direction: {delta['delta_direction']}")
```

### Check for Regressions

```python
result = compare_coverage_between_refs("owner/repo", "main", "feature-branch")

regression = result['regression_analysis']
if regression['has_regression']:
    print(f"⚠️ Regression detected!")
    print(f"  Severity: {regression['severity']}")
    print(f"  Delta: {regression['delta_percentage']:.1f}%")
else:
    print("✓ No regression detected")
```

### Analyze Improvements

```python
result = compare_coverage_between_refs("owner/repo", "main", "feature-branch")

improvement = result['improvement_analysis']
if improvement['has_improvement']:
    print(f"✓ Coverage improved!")
    print(f"  Delta: {improvement['delta_percentage']:+.1f}%")
    print(f"  Improvement: {improvement['improvement_percentage']:.2f}%")
```

### Compare with Custom Threshold

```python
result = compare_coverage_between_refs(
    "owner/repo",
    "main",
    "feature-branch",
    regression_threshold=2.0
)

regression = result['regression_analysis']
print(f"Regression threshold: {regression['threshold']}%")
print(f"Has regression: {regression['has_regression']}")
```

### Compare Using Specific Provider

```python
result = compare_coverage_between_refs(
    "owner/repo",
    "main",
    "feature-branch",
    provider="codecov"
)

print(f"Provider results: {result['provider_results']}")
```

## Use Cases

### 1. PR Coverage Analysis

```python
# Analyze coverage change in a pull request
def analyze_pr_coverage(repo_slug, base_branch, pr_branch):
    result = compare_coverage_between_refs(repo_slug, base_branch, pr_branch)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    delta = result['coverage_delta']
    regression = result['regression_analysis']
    
    print(f"PR Coverage Analysis")
    print(f"Base: {delta['base_coverage']}%")
    print(f"PR: {delta['head_coverage']}%")
    print(f"Delta: {delta['delta_percentage']:+.1f}%")
    
    if regression['has_regression']:
        print(f"⚠️ Regression: {regression['severity']}")
    else:
        print("✓ No regression")

analyze_pr_coverage("owner/repo", "main", "feature/new-feature")
```

### 2. Release Coverage Verification

```python
# Verify coverage hasn't regressed in a release
def verify_release_coverage(repo_slug, previous_version, new_version):
    result = compare_coverage_between_refs(
        repo_slug,
        f"v{previous_version}",
        f"v{new_version}",
        regression_threshold=0.5
    )
    
    regression = result['regression_analysis']
    if regression['has_regression']:
        print(f"❌ Release {new_version} has coverage regression!")
        print(f"   Severity: {regression['severity']}")
        return False
    else:
        print(f"✓ Release {new_version} coverage OK")
        return True

verify_release_coverage("owner/repo", "1.0.0", "1.1.0")
```

### 3. Branch Comparison

```python
# Compare coverage across multiple branches
def compare_branches(repo_slug, branches):
    base = branches[0]
    results = {}
    
    for branch in branches[1:]:
        result = compare_coverage_between_refs(repo_slug, base, branch)
        if 'error' not in result:
            delta = result['coverage_delta']
            results[branch] = {
                'coverage': delta['head_coverage'],
                'delta': delta['delta_percentage']
            }
    
    print(f"Coverage comparison (base: {base}):")
    for branch, data in results.items():
        print(f"  {branch}: {data['coverage']}% ({data['delta']:+.1f}%)")

compare_branches("owner/repo", ["main", "develop", "staging"])
```

### 4. Regression Detection

```python
# Detect and report regressions
def detect_regressions(repo_slug, base_ref, head_ref, threshold=1.0):
    result = compare_coverage_between_refs(
        repo_slug,
        base_ref,
        head_ref,
        regression_threshold=threshold
    )
    
    regression = result['regression_analysis']
    
    severity_emoji = {
        'none': '✓',
        'minor': '⚠️',
        'major': '⚠️⚠️',
        'critical': '❌'
    }
    
    emoji = severity_emoji.get(regression['severity'], '?')
    print(f"{emoji} Regression Analysis")
    print(f"  Has regression: {regression['has_regression']}")
    print(f"  Severity: {regression['severity']}")
    print(f"  Delta: {regression['delta_percentage']:.1f}%")
    print(f"  Threshold: {regression['threshold']}%")

detect_regressions("owner/repo", "main", "feature-branch", threshold=1.0)
```

### 5. Trend Analysis

```python
# Analyze coverage trend across commits
def analyze_trend(repo_slug, commits):
    results = []
    
    for i in range(len(commits) - 1):
        result = compare_coverage_between_refs(
            repo_slug,
            commits[i],
            commits[i + 1]
        )
        
        if 'error' not in result:
            delta = result['coverage_delta']
            results.append({
                'from': commits[i],
                'to': commits[i + 1],
                'delta': delta['delta_percentage']
            })
    
    print("Coverage Trend:")
    for r in results:
        direction = "↑" if r['delta'] > 0 else "↓" if r['delta'] < 0 else "→"
        print(f"  {r['from']} → {r['to']}: {direction} {r['delta']:+.1f}%")

analyze_trend("owner/repo", ["abc123d", "def456g", "ghi789h"])
```

## Performance Considerations

- **Caching**: Results can be cached for a short period (e.g., 5-10 minutes)
- **Provider Queries**: Multiple providers may be queried; consider timeout settings
- **Large Repositories**: Comparison may take longer for large codebases
- **Batch Analysis**: For multiple comparisons, consider rate limiting

## Interpreting Results

### Coverage Delta

The `coverage_delta` shows the change in coverage:

```python
delta = result['coverage_delta']
if delta['delta_percentage'] > 0:
    print(f"Coverage improved by {delta['delta_percentage']:.1f}%")
elif delta['delta_percentage'] < 0:
    print(f"Coverage regressed by {abs(delta['delta_percentage']):.1f}%")
else:
    print("Coverage unchanged")
```

### Regression Severity

Understand the severity of regressions:

```python
regression = result['regression_analysis']
severity_levels = {
    'none': 'No regression',
    'minor': 'Small regression',
    'major': 'Significant regression',
    'critical': 'Critical regression'
}
print(f"Severity: {severity_levels[regression['severity']]}")
```

### Provider Results

Check individual provider results:

```python
for provider, data in result['provider_results'].items():
    if 'error' not in data:
        print(f"{provider}: {data['base_coverage']}% → {data['head_coverage']}%")
    else:
        print(f"{provider}: Error - {data['error']}")
```

## Related Tools

- `get_commit_coverage_summary` - Get coverage for a specific commit
- `get_repository_test_health` - Analyze repository coverage health
- `list_coverage_providers` - List available providers
