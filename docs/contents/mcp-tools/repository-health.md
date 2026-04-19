# get_repository_test_health Tool

## Overview

The `get_repository_test_health` tool analyzes test coverage health for a repository using available coverage providers. It identifies risks, provides recommendations, and generates next actions for improvement.

## Function Signature

```python
def get_repository_test_health(
    repo_slug: str,
    provider: Optional[str] = None,
    ref: Optional[str] = None,
    threshold: float = 80.0,
) -> Dict[str, Any]
```

## Parameters

### repo_slug (str, required)

Repository identifier in format `"owner/repo"`.

**Examples**: `"python/cpython"`, `"facebook/react"`, `"torvalds/linux"`

### provider (str, optional)

Specific provider to use for analysis. If not specified, uses the best available provider.

**Examples**: `"codecov"`, `"coveralls"`, `"sonarqube"`

### ref (str, optional)

Git reference to analyze (branch, tag, or commit SHA).

**Examples**: `"main"`, `"develop"`, `"v1.0.0"`, `"abc123def456"`

If not specified, analyzes the default branch.

### threshold (float, default: 80.0)

Coverage threshold percentage for risk assessment.

**Valid range**: 0.0 to 100.0

**Examples**: `80.0`, `85.0`, `90.0`

## Return Value

Returns a dictionary with the following structure:

```python
{
    "repo_slug": str,                   # Repository identifier
    "ref": str | None,                  # Git reference analyzed
    "coverage_metrics": {
        "average_coverage": float,      # Average coverage percentage
        "coverage_range": {
            "min": float,               # Minimum coverage
            "max": float                # Maximum coverage
        },
        "providers_queried": int,       # Number of providers queried
        "providers_succeeded": int,     # Number of successful providers
        "providers_failed": int         # Number of failed providers
    },
    "health_summary": {
        "is_healthy": bool,             # Whether coverage meets threshold
        "coverage_below_threshold": bool,
        "threshold": float
    },
    "risk_analysis": {
        "risk_level": str,              # "low", "medium", "high", "critical"
        "current_coverage": float,
        "gap": float,                   # Coverage gap to threshold
        "recommendations": [str]        # Improvement recommendations
    },
    "next_actions": [str],              # Recommended next actions
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

## Risk Levels

Risk levels are determined based on coverage gap:

- **LOW**: Coverage >= threshold
- **MEDIUM**: Coverage >= threshold - 10%
- **HIGH**: Coverage >= threshold - 20%
- **CRITICAL**: Coverage < threshold - 20%

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

### Provider Not Found

If the specified provider doesn't exist:

```python
{
    "error": "Provider 'nonexistent' not found",
    "error_type": "ProviderNotFoundError",
    "execution_metadata": { ... }
}
```

### Analysis Error

If an error occurs during analysis:

```python
{
    "error": "Error message describing what went wrong",
    "error_type": "RepositoryHealthAnalysisError",
    "repo_slug": "owner/repo",
    "execution_metadata": { ... }
}
```

## Examples

### Basic Health Check

```python
result = get_repository_test_health("owner/repo")

print(f"Repository: {result['repo_slug']}")
print(f"Coverage: {result['coverage_metrics']['average_coverage']}%")
print(f"Health: {'✓ Healthy' if result['health_summary']['is_healthy'] else '✗ Below threshold'}")
print(f"Risk Level: {result['risk_analysis']['risk_level']}")
```

### Check with Custom Threshold

```python
result = get_repository_test_health(
    "owner/repo",
    threshold=85.0
)

gap = result['risk_analysis']['gap']
if gap > 0:
    print(f"Need {gap}% more coverage to meet threshold")
```

### Analyze Specific Branch

```python
result = get_repository_test_health(
    "owner/repo",
    ref="develop"
)

print(f"Analyzing branch: {result['ref']}")
```

### Use Specific Provider

```python
result = get_repository_test_health(
    "owner/repo",
    provider="codecov"
)

print(f"Provider queried: {result['execution_metadata']['provider_name']}")
```

### Get Recommendations

```python
result = get_repository_test_health("owner/repo")

print("Recommendations:")
for rec in result['risk_analysis']['recommendations']:
    print(f"  - {rec}")

print("\nNext Actions:")
for action in result['next_actions']:
    print(f"  - {action}")
```

## Use Cases

### 1. Monitor Repository Health

```python
# Regular health checks
def monitor_repository(repo_slug, threshold=80.0):
    result = get_repository_test_health(repo_slug, threshold=threshold)
    
    if not result['health_summary']['is_healthy']:
        print(f"⚠️ {repo_slug}: Coverage below threshold")
        print(f"   Current: {result['coverage_metrics']['average_coverage']}%")
        print(f"   Gap: {result['risk_analysis']['gap']}%")
    else:
        print(f"✓ {repo_slug}: Healthy")

monitor_repository("owner/repo")
```

### 2. Compare Branches

```python
# Compare coverage across branches
def compare_branches(repo_slug, branches):
    results = {}
    for branch in branches:
        result = get_repository_test_health(repo_slug, ref=branch)
        results[branch] = result['coverage_metrics']['average_coverage']
    
    for branch, coverage in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{branch}: {coverage}%")

compare_branches("owner/repo", ["main", "develop", "staging"])
```

### 3. Risk Assessment

```python
# Assess coverage risk
def assess_risk(repo_slug):
    result = get_repository_test_health(repo_slug)
    
    risk_level = result['risk_analysis']['risk_level']
    coverage = result['coverage_metrics']['average_coverage']
    
    if risk_level == "critical":
        print(f"🔴 CRITICAL: Coverage is {coverage}%")
    elif risk_level == "high":
        print(f"🟠 HIGH: Coverage is {coverage}%")
    elif risk_level == "medium":
        print(f"🟡 MEDIUM: Coverage is {coverage}%")
    else:
        print(f"🟢 LOW: Coverage is {coverage}%")
    
    return risk_level

assess_risk("owner/repo")
```

### 4. Generate Improvement Plan

```python
# Generate improvement plan
def create_improvement_plan(repo_slug):
    result = get_repository_test_health(repo_slug, threshold=90.0)
    
    print(f"Improvement Plan for {repo_slug}")
    print(f"Current Coverage: {result['coverage_metrics']['average_coverage']}%")
    print(f"Target Coverage: {result['risk_analysis']['risk_level']}")
    print(f"Gap: {result['risk_analysis']['gap']}%")
    print("\nRecommendations:")
    for i, rec in enumerate(result['risk_analysis']['recommendations'], 1):
        print(f"{i}. {rec}")
    print("\nNext Actions:")
    for i, action in enumerate(result['next_actions'], 1):
        print(f"{i}. {action}")

create_improvement_plan("owner/repo")
```

### 5. Provider Fallback

```python
# Try specific provider, fallback to best available
def get_health_with_fallback(repo_slug, preferred_provider=None):
    if preferred_provider:
        result = get_repository_test_health(repo_slug, provider=preferred_provider)
        if 'error' not in result:
            return result
    
    # Fallback to best available
    return get_repository_test_health(repo_slug)

result = get_health_with_fallback("owner/repo", preferred_provider="codecov")
```

## Performance Considerations

- **Caching**: Results can be cached for a short period (e.g., 5-10 minutes)
- **Provider Queries**: Multiple providers may be queried; consider timeout settings
- **Large Repositories**: Analysis may take longer for large codebases
- **Batch Analysis**: For multiple repositories, consider rate limiting

## Interpreting Results

### Coverage Range

The `coverage_range` shows the spread of coverage across providers:

```python
range_spread = result['coverage_metrics']['coverage_range']['max'] - \
               result['coverage_metrics']['coverage_range']['min']

if range_spread > 5:
    print("⚠️ Large variance in coverage across providers")
```

### Provider Statistics

Check how many providers succeeded:

```python
success_rate = result['coverage_metrics']['providers_succeeded'] / \
               result['coverage_metrics']['providers_queried']

if success_rate < 1.0:
    print(f"⚠️ {result['coverage_metrics']['providers_failed']} provider(s) failed")
```

## Related Tools

- `list_coverage_providers` - List available providers
- `describe_coverage_provider` - Get provider details
