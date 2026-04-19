# analyze_pr_coverage_risk Tool

## Overview

The `analyze_pr_coverage_risk` tool evaluates the coverage risk of a pull request based on coverage metrics. It provides a risk assessment with numerical scoring, risk level classification, and actionable recommendations for improvement.

This tool leverages the `CoverageRiskAnalysisService` to analyze multiple risk factors including coverage delta, changed files, and uncovered changed lines.

## Function Signature

```python
def analyze_pr_coverage_risk(
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
    "risk_level": str,                        # Risk level: low, medium, high, critical
    "risk_score": float,                      # Numerical risk score (0-100)
    "coverage_delta": float,                  # Change in coverage percentage
    "changed_code_coverage": float,           # Coverage of changed code (0-100)
    "changed_files_count": int,               # Number of files changed
    "uncovered_changed_lines": int,           # Number of uncovered changed lines
    "total_changed_lines": int,               # Total number of changed lines
    "recommendations": [str],                 # List of recommendations
    "high_risk_files": [                      # Files with high coverage risk
        {
            "file_path": str,                 # Path to the file
            "coverage": float,                # Coverage percentage
            "risk_level": str,                # Risk level
            "risk_score": float,              # Risk score
            "uncovered_lines": int,           # Number of uncovered lines
            "recommendations": [str],         # File-specific recommendations
        },
        ...
    ],
}
```

## Risk Levels

| Risk Level | Risk Score | Interpretation | Action |
|-----------|-----------|-----------------|--------|
| **Low** | 0-25 | Safe to merge | Approve |
| **Medium** | 25-50 | Review carefully | Review |
| **High** | 50-75 | Request changes | Request changes |
| **Critical** | 75-100 | Block merge | Block |

## Risk Scoring Algorithm

The risk score is calculated using weighted factors:

```
risk_score = (
    uncovered_changes_risk * 0.4 +      # 40% weight
    changed_code_coverage_risk * 0.3 +  # 30% weight
    coverage_regression * 0.2 +         # 20% weight
    file_count_risk * 0.1               # 10% weight
)
```

### Risk Factors

1. **Uncovered Changes Risk (40%)**: Ratio of uncovered to total changed lines
2. **Changed Code Coverage Risk (30%)**: Overall coverage of changed code
3. **Coverage Regression (20%)**: Negative change in coverage percentage
4. **File Count Risk (10%)**: Number of files changed

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
from test_coverage_mcp.mcp_server.tools import analyze_pr_coverage_risk

result = analyze_pr_coverage_risk(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

print(f"Risk Level: {result['risk_level'].upper()}")
print(f"Risk Score: {result['risk_score']:.1f}/100")
print(f"Coverage Delta: {result['coverage_delta']:+.1f}%")
```

### Risk-Based Decision Making

```python
result = analyze_pr_coverage_risk(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

if result["risk_level"] == "critical":
    print("❌ PR blocked: Critical coverage risk")
    for rec in result["recommendations"]:
        print(f"  - {rec}")
    exit(1)
elif result["risk_level"] == "high":
    print("⚠️ PR needs review: High coverage risk")
    for rec in result["recommendations"]:
        print(f"  - {rec}")
else:
    print("✓ PR approved: Acceptable coverage risk")
```

### Analyzing High-Risk Files

```python
result = analyze_pr_coverage_risk(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

if result["high_risk_files"]:
    print(f"Files needing attention ({len(result['high_risk_files'])}):")
    for file_info in result["high_risk_files"]:
        print(f"\n  {file_info['file_path']}")
        print(f"    Coverage: {file_info['coverage']:.1f}%")
        print(f"    Risk Level: {file_info['risk_level']}")
        print(f"    Uncovered Lines: {file_info['uncovered_lines']}")
        for rec in file_info["recommendations"]:
            print(f"    - {rec}")
```

### Coverage Regression Detection

```python
result = analyze_pr_coverage_risk(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

if result["coverage_delta"] < 0:
    print(f"⚠️ Coverage regression: {abs(result['coverage_delta']):.1f}%")
    print(f"Changed code coverage: {result['changed_code_coverage']:.1f}%")
    print(f"Uncovered lines in changes: {result['uncovered_changed_lines']}")
else:
    print(f"✓ Coverage improved: {result['coverage_delta']:+.1f}%")
```

### Detailed Risk Analysis

```python
result = analyze_pr_coverage_risk(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

print("PR Risk Assessment")
print("=" * 50)
print(f"Risk Level: {result['risk_level'].upper()}")
print(f"Risk Score: {result['risk_score']:.1f}/100")
print()
print("Coverage Metrics:")
print(f"  Base Coverage: {result.get('base_coverage', 'N/A')}%")
print(f"  Head Coverage: {result.get('head_coverage', 'N/A')}%")
print(f"  Delta: {result['coverage_delta']:+.1f}%")
print()
print("Changed Code:")
print(f"  Files Changed: {result['changed_files_count']}")
print(f"  Total Lines: {result['total_changed_lines']}")
print(f"  Covered Lines: {result['total_changed_lines'] - result['uncovered_changed_lines']}")
print(f"  Uncovered Lines: {result['uncovered_changed_lines']}")
print(f"  Coverage: {result['changed_code_coverage']:.1f}%")
print()
print("Recommendations:")
for i, rec in enumerate(result["recommendations"], 1):
    print(f"  {i}. {rec}")
```

## Use Cases

### 1. PR Review Automation

Automatically assess PR risk before review:

```python
def auto_assess_pr_risk(repo_slug, base_ref, head_ref):
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )
    
    return {
        "risk_level": result["risk_level"],
        "risk_score": result["risk_score"],
        "needs_review": result["risk_level"] in ["high", "critical"],
        "recommendations": result["recommendations"],
    }
```

### 2. CI/CD Pipeline Integration

Enforce coverage standards in CI/CD:

```python
def ci_coverage_gate(repo_slug, base_ref, head_ref, max_risk_score=50):
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )
    
    if result["risk_score"] > max_risk_score:
        print(f"❌ Build failed: Risk score {result['risk_score']:.1f} exceeds limit {max_risk_score}")
        return False
    
    print(f"✓ Build passed: Risk score {result['risk_score']:.1f}")
    return True
```

### 3. Regression Detection

Detect and prevent coverage regressions:

```python
def detect_regression(repo_slug, base_ref, head_ref, max_regression=-1.0):
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )
    
    if result["coverage_delta"] < max_regression:
        print(f"⚠️ Coverage regression: {result['coverage_delta']:.1f}%")
        return False
    
    return True
```

### 4. Team Dashboard

Display PR risk metrics in team dashboard:

```python
def get_pr_metrics(repo_slug, base_ref, head_ref):
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )
    
    return {
        "risk_level": result["risk_level"],
        "risk_score": result["risk_score"],
        "coverage_delta": result["coverage_delta"],
        "changed_code_coverage": result["changed_code_coverage"],
        "high_risk_files_count": len(result["high_risk_files"]),
    }
```

## Performance Considerations

### Execution Time

- **No changes**: < 100ms
- **Small PR (< 50 lines)**: 100-500ms
- **Medium PR (50-500 lines)**: 500ms-2s
- **Large PR (> 500 lines)**: 2-10s

### Optimization Tips

1. **Cache results**: Store results to avoid re-analysis
2. **Batch operations**: Process multiple PRs in parallel
3. **Limit file analysis**: Focus on changed files only
4. **Use thresholds**: Skip analysis for trivial changes

## Limitations

1. **Provider dependent**: Results depend on coverage provider accuracy
2. **Line-level only**: Doesn't account for branch/condition coverage
3. **Historical context**: Doesn't consider historical trends
4. **Test quality**: Doesn't measure test effectiveness
5. **Dynamic code**: May miss dynamically generated code

## Related Tools

- **find_untested_changed_code**: Identify specific uncovered regions
- **get_commit_coverage_summary**: Get coverage for specific commit
- **compare_coverage_between_refs**: Compare coverage between references

## Troubleshooting

### Risk Score Too High

**Cause**: Multiple risk factors contributing to high score

**Solution**:
1. Reduce uncovered changed lines (add tests)
2. Improve coverage of changed code
3. Avoid coverage regressions
4. Limit number of files changed

### No High-Risk Files Found

**Cause**: All files have acceptable coverage

**Solution**: This is expected behavior. No action needed.

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

See `AnalyzePRRiskInput` and `AnalyzePRRiskOutput` models in:
- `test_coverage_mcp.mcp_server.tools.models.pr_analysis`
