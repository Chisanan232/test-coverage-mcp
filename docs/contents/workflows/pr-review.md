# PR Review Workflow Guide

## Overview

This guide explains how to use the PR analysis tools to review pull requests effectively. The workflow helps identify coverage gaps, assess risk, and ensure code quality standards are met.

## Quick Start

### 1. Analyze PR Risk

Start by assessing the overall risk of the PR:

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
```

### 2. Find Untested Code

Identify specific uncovered regions:

```python
from test_coverage_mcp.mcp_server.tools import find_untested_changed_code

result = find_untested_changed_code(
    repo_slug="myorg/myapp",
    provider="codecov",
    base_ref="main",
    head_ref="feature/new-feature",
)

print(f"Uncovered lines: {result['uncovered_changed_lines']}")
print(f"Coverage: {result['coverage_percentage']:.1f}%")
```

### 3. Review Recommendations

Act on the recommendations provided:

```python
if result["risk_level"] == "critical":
    print("❌ Request changes - critical coverage issues")
elif result["risk_level"] == "high":
    print("⚠️ Request changes - significant gaps")
else:
    print("✓ Approve - acceptable coverage")
```

## Detailed Review Process

### Step 1: Initial Risk Assessment

Assess the overall risk level:

```python
def initial_risk_assessment(repo_slug, base_ref, head_ref):
    """Perform initial risk assessment of PR."""
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    assessment = {
        "risk_level": result["risk_level"],
        "risk_score": result["risk_score"],
        "coverage_delta": result["coverage_delta"],
        "changed_code_coverage": result["changed_code_coverage"],
    }

    # Determine review action
    if result["risk_level"] == "critical":
        assessment["action"] = "BLOCK"
        assessment["reason"] = "Critical coverage risk"
    elif result["risk_level"] == "high":
        assessment["action"] = "REQUEST_CHANGES"
        assessment["reason"] = "High coverage risk"
    elif result["risk_level"] == "medium":
        assessment["action"] = "REVIEW"
        assessment["reason"] = "Medium coverage risk"
    else:
        assessment["action"] = "APPROVE"
        assessment["reason"] = "Low coverage risk"

    return assessment
```

### Step 2: Identify Coverage Gaps

Find specific uncovered regions:

```python
def identify_coverage_gaps(repo_slug, base_ref, head_ref):
    """Identify specific coverage gaps in PR."""
    result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    # Group by file
    gaps_by_file = {}
    for region in result["uncovered_regions"]:
        file_path = region["file_path"]
        if file_path not in gaps_by_file:
            gaps_by_file[file_path] = []
        gaps_by_file[file_path].append(region)

    # Group by risk level
    gaps_by_risk = {}
    for region in result["uncovered_regions"]:
        risk_level = region["risk_level"]
        if risk_level not in gaps_by_risk:
            gaps_by_risk[risk_level] = []
        gaps_by_risk[risk_level].append(region)

    return {
        "by_file": gaps_by_file,
        "by_risk": gaps_by_risk,
        "total": len(result["uncovered_regions"]),
        "pending": result["has_pending"],
    }
```

### Step 3: Analyze High-Risk Files

Focus on files with highest risk:

```python
def analyze_high_risk_files(repo_slug, base_ref, head_ref):
    """Analyze files with high coverage risk."""
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    if not result["high_risk_files"]:
        return {"message": "No high-risk files found"}

    analysis = {
        "total_high_risk_files": len(result["high_risk_files"]),
        "files": [],
    }

    for file_info in result["high_risk_files"]:
        analysis["files"].append({
            "path": file_info["file_path"],
            "coverage": file_info["coverage"],
            "risk_level": file_info["risk_level"],
            "uncovered_lines": file_info["uncovered_lines"],
            "recommendations": file_info["recommendations"],
        })

    return analysis
```

### Step 4: Check for Regressions

Detect coverage regressions:

```python
def check_for_regressions(repo_slug, base_ref, head_ref):
    """Check for coverage regressions."""
    result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    if result["coverage_delta"] < 0:
        return {
            "has_regression": True,
            "delta": result["coverage_delta"],
            "severity": "critical" if result["coverage_delta"] < -5 else "warning",
            "message": f"Coverage regression of {abs(result['coverage_delta']):.1f}%",
        }

    return {
        "has_regression": False,
        "delta": result["coverage_delta"],
        "message": "No regression detected",
    }
```

### Step 5: Generate Review Summary

Create a comprehensive review summary:

```python
def generate_review_summary(repo_slug, base_ref, head_ref):
    """Generate comprehensive PR review summary."""
    risk_result = analyze_pr_coverage_risk(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    gap_result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    summary = {
        "risk_assessment": {
            "level": risk_result["risk_level"],
            "score": risk_result["risk_score"],
            "delta": risk_result["coverage_delta"],
        },
        "coverage_metrics": {
            "changed_code_coverage": risk_result["changed_code_coverage"],
            "changed_files": risk_result["changed_files_count"],
            "uncovered_lines": risk_result["uncovered_changed_lines"],
            "total_changed_lines": risk_result["total_changed_lines"],
        },
        "gaps": {
            "total": len(gap_result["uncovered_regions"]),
            "has_pending": gap_result["has_pending"],
            "summary": gap_result["gap_summary"],
        },
        "high_risk_files": len(risk_result["high_risk_files"]),
        "recommendations": risk_result["recommendations"],
    }

    return summary
```

## Review Decision Matrix

Use this matrix to make review decisions:

| Risk Level | Coverage | Action | Comment |
|-----------|----------|--------|---------|
| Critical | < 50% | BLOCK | Critical coverage issues must be fixed |
| Critical | 50-80% | BLOCK | Significant gaps in changed code |
| High | < 70% | REQUEST_CHANGES | Request additional tests |
| High | 70-85% | REQUEST_CHANGES | Some gaps need addressing |
| Medium | < 80% | REVIEW | Review carefully before approving |
| Medium | 80%+ | REVIEW | Monitor coverage trends |
| Low | 80%+ | APPROVE | Coverage acceptable |
| Low | 90%+ | APPROVE | Excellent coverage |

## Example Review Scenarios

### Scenario 1: Low-Risk PR

```
Risk Level: LOW
Risk Score: 15.0/100
Coverage Delta: +2.5%
Changed Code Coverage: 92.0%
Uncovered Lines: 2

Action: ✓ APPROVE
Reason: Excellent coverage with improvement
```

### Scenario 2: Medium-Risk PR

```
Risk Level: MEDIUM
Risk Score: 35.0/100
Coverage Delta: -1.0%
Changed Code Coverage: 78.0%
Uncovered Lines: 15

Action: ⚠️ REVIEW
Reason: Some coverage gaps, slight regression
Recommendations:
  - Add tests for 15 uncovered lines
  - Focus on critical regions first
```

### Scenario 3: High-Risk PR

```
Risk Level: HIGH
Risk Score: 62.0/100
Coverage Delta: -5.0%
Changed Code Coverage: 55.0%
Uncovered Lines: 45

Action: 🔴 REQUEST_CHANGES
Reason: Significant coverage gaps and regression
Recommendations:
  - Add tests for 45 uncovered lines
  - Address coverage regression
  - Focus on high-risk regions
High-Risk Files: 3
  - src/core/processor.py (35% coverage)
  - src/utils/helpers.py (40% coverage)
  - src/api/handlers.py (45% coverage)
```

### Scenario 4: Critical-Risk PR

```
Risk Level: CRITICAL
Risk Score: 85.0/100
Coverage Delta: -10.0%
Changed Code Coverage: 30.0%
Uncovered Lines: 120

Action: ❌ BLOCK
Reason: Critical coverage issues
Recommendations:
  - Add tests for 120 uncovered lines
  - Significant regression detected
  - Multiple high-risk files
High-Risk Files: 8
  - src/core/engine.py (20% coverage)
  - src/database/models.py (25% coverage)
  - ... (6 more files)
```

## Handling Pending Analysis

When coverage analysis is incomplete:

```python
def handle_pending_analysis(repo_slug, base_ref, head_ref):
    """Handle PR review when analysis is pending."""
    result = find_untested_changed_code(
        repo_slug=repo_slug,
        provider="codecov",
        base_ref=base_ref,
        head_ref=head_ref,
    )

    if result["has_pending"]:
        return {
            "status": "PENDING",
            "message": f"Coverage analysis in progress ({len(result['pending_regions'])} regions)",
            "action": "DEFER",
            "recommendations": [
                "Wait for coverage analysis to complete",
                "Re-check PR after analysis completes",
                "Estimated completion: 5-10 minutes",
            ],
        }

    # Analysis complete - proceed with review
    return {"status": "COMPLETE"}
```

## Integration Examples

### GitHub Actions Integration

```yaml
name: PR Coverage Review

on: [pull_request]

jobs:
  coverage-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Analyze PR Risk
        run: |
          python -c "
          from test_coverage_mcp.mcp_server.tools import analyze_pr_coverage_risk

          result = analyze_pr_coverage_risk(
              repo_slug='${{ github.repository }}',
              provider='codecov',
              base_ref='${{ github.base_ref }}',
              head_ref='${{ github.head_ref }}',
          )

          if result['risk_level'] == 'critical':
              print('::error::Critical coverage risk detected')
              exit(1)
          elif result['risk_level'] == 'high':
              print('::warning::High coverage risk detected')
          "
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python -c "
from test_coverage_mcp.mcp_server.tools import find_untested_changed_code

result = find_untested_changed_code(
    repo_slug='myorg/myapp',
    provider='codecov',
    base_ref='main',
    head_ref='HEAD',
)

if result['coverage_percentage'] < 80.0:
    print('⚠️ Low coverage in changes: {:.1f}%'.format(result['coverage_percentage']))
    exit(1)
"
```

## Best Practices

1. **Always check risk level first** - Start with overall risk assessment
2. **Review high-risk files** - Focus on files with lowest coverage
3. **Check for regressions** - Ensure coverage doesn't decrease
4. **Handle pending analysis** - Don't make decisions on incomplete data
5. **Provide feedback** - Share recommendations with PR author
6. **Document decisions** - Record why you approved or requested changes
7. **Track trends** - Monitor coverage trends over time
8. **Automate gates** - Use CI/CD to enforce coverage standards

## Troubleshooting

### Analysis Fails

**Cause**: Coverage provider unavailable or invalid credentials

**Solution**:
1. Check provider status
2. Verify credentials
3. Retry after a delay

### Pending Analysis Takes Too Long

**Cause**: Provider is slow to analyze

**Solution**:
1. Wait for provider to complete
2. Check provider status page
3. Consider deferring review

### Conflicting Risk Assessments

**Cause**: Different tools give different results

**Solution**:
1. Verify provider data is consistent
2. Check for data freshness
3. Use most recent analysis

## Related Documentation

- [Risk Analysis Methodology](../architecture/risk-analysis.md)
- [Pending States Guide](../guides/pending-states.md)
- [find_untested_changed_code Tool](../mcp-tools/find-untested-code.md)
- [analyze_pr_coverage_risk Tool](../mcp-tools/analyze-pr-risk.md)
