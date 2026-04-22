# Coverage Risk Analysis Methodology

## Overview

The Coverage Risk Analysis Service provides intelligent PR risk scoring and high-risk file identification based on coverage metrics and code change analysis. This document describes the risk scoring algorithm and methodology.

## Risk Scoring Algorithm

### Overview

The risk scoring system evaluates pull requests on a scale of 0-100, where:
- **0-25**: Low risk ✓
- **25-50**: Medium risk ⚠️
- **50-75**: High risk ⚠️⚠️
- **75-100**: Critical risk ❌

### Risk Factors

The algorithm considers four weighted risk factors:

#### 1. Uncovered Changes Risk (40% weight)
**Most critical factor** - Measures coverage of changed code.

```
uncovered_changes_risk = (uncovered_changed_lines / total_changed_lines) * 100
```

**Interpretation**:
- 0%: All changed code is covered (low risk)
- 50%: Half of changed code is uncovered (medium risk)
- 100%: No changed code is covered (critical risk)

**Example**:
```python
# PR changes 100 lines, 20 are uncovered
uncovered_changes_risk = (20 / 100) * 100 = 20.0
```

#### 2. Changed Code Coverage Risk (30% weight)
**Important factor** - Overall coverage percentage of changed code.

```
changed_code_coverage_risk = 100.0 - changed_code_coverage_percentage
```

**Interpretation**:
- 0%: 100% of changed code is covered (low risk)
- 50%: 50% of changed code is covered (medium risk)
- 100%: 0% of changed code is covered (critical risk)

**Example**:
```python
# PR changes 50 lines, 40 are covered
changed_code_coverage = (40 / 50) * 100 = 80%
changed_code_coverage_risk = 100.0 - 80.0 = 20.0
```

#### 3. Coverage Regression (20% weight)
**Important factor** - Detects when coverage decreases.

```
coverage_regression = min(100.0, abs(coverage_delta) * 10) if delta < 0 else 0.0
```

**Interpretation**:
- 0%: No regression or improvement (low risk)
- 50%: 5% regression (medium risk)
- 100%: 10%+ regression (critical risk)

**Example**:
```python
# Base coverage: 85%, PR coverage: 80%
coverage_delta = 80 - 85 = -5%
coverage_regression = min(100.0, 5 * 10) = 50.0
```

#### 4. File Count Risk (10% weight)
**Minor factor** - More files = more risk.

```
file_count_risk = min(100.0, changed_files_count * 5)
```

**Interpretation**:
- 0%: 0 files changed (low risk)
- 50%: 10 files changed (medium risk)
- 100%: 20+ files changed (critical risk)

**Example**:
```python
# PR changes 8 files
file_count_risk = min(100.0, 8 * 5) = 40.0
```

### Overall Risk Score Calculation

```
risk_score = (
    uncovered_changes_risk * 0.4 +
    changed_code_coverage_risk * 0.3 +
    coverage_regression * 0.2 +
    file_count_risk * 0.1
)
```

### Example Calculation

**Scenario**: PR with mixed coverage issues

```python
# PR metrics
base_coverage = 85.0
head_coverage = 82.0  # -3% regression
changed_files_count = 5
uncovered_changed_lines = 30
total_changed_lines = 100
changed_code_coverage = 70.0

# Calculate factors
uncovered_changes_risk = (30 / 100) * 100 = 30.0
changed_code_coverage_risk = 100.0 - 70.0 = 30.0
coverage_regression = min(100.0, 3 * 10) = 30.0
file_count_risk = min(100.0, 5 * 5) = 25.0

# Calculate risk score
risk_score = (30.0 * 0.4) + (30.0 * 0.3) + (30.0 * 0.2) + (25.0 * 0.1)
           = 12.0 + 9.0 + 6.0 + 2.5
           = 29.5

# Risk level: MEDIUM (25-50 range)
```

## Risk Level Thresholds

| Risk Score | Risk Level | Recommendation |
|-----------|-----------|-----------------|
| 0-25 | Low ✓ | Approve - coverage looks good |
| 25-50 | Medium ⚠️ | Review - some coverage gaps |
| 50-75 | High ⚠️⚠️ | Request changes - significant gaps |
| 75-100 | Critical ❌ | Block - critical coverage issues |

## High-Risk File Identification

### Risk Score for Files

For individual files, risk is calculated as:

```
file_risk_score = 100.0 - file_coverage_percentage
```

### Risk Levels for Files

| Coverage | Risk Level | Action |
|----------|-----------|--------|
| 90-100% | Low | No action needed |
| 70-90% | Medium | Monitor coverage |
| 50-70% | High | Add tests |
| 0-50% | Critical | Priority testing |

### Example

```python
# File with 35% coverage
file_risk_score = 100.0 - 35.0 = 65.0
risk_level = HIGH

# Recommendations
- "High priority: src/module.py needs test coverage"
- "Add tests for 65 uncovered lines"
```

## Config vs Missing Tests Detection

### Scoring Methodology

The service uses indicators to determine the root cause:

#### Config Issue Indicators
- Invalid coverage configuration (0.5 points)
- Configuration issues found (0.3 points)
- Exclude patterns not working (0.2 points)

#### Missing Tests Indicators
- Coverage below 50% (0.4 points)
- Uncovered regions detected (0.3 points)
- No test files found (0.3 points)

### Decision Logic

```python
config_score = sum(config_indicators)
missing_tests_score = sum(missing_tests_indicators)

# Normalize scores
total = config_score + missing_tests_score
config_score /= total
missing_tests_score /= total

# Determine root cause
is_config_issue = config_score > 0.6
is_missing_tests = missing_tests_score > 0.6
```

### Example

**Scenario 1: Config Issue**
```
Indicators:
- Invalid configuration detected (0.5)
- 2 configuration issues found (0.3)

config_score = 0.8
missing_tests_score = 0.2

Result: is_config_issue = True
Recommendation: "Review and fix coverage configuration"
```

**Scenario 2: Missing Tests**
```
Indicators:
- Coverage below 50% (0.4)
- 5 uncovered regions detected (0.3)

config_score = 0.3
missing_tests_score = 0.7

Result: is_missing_tests = True
Recommendation: "Add tests for uncovered code regions"
```

## Recommendations Generation

### PR Risk Recommendations

Based on risk level and factors:

```python
if risk_level in (CRITICAL, HIGH):
    "⚠️ High-risk PR detected - careful review recommended"

if coverage_delta < 0:
    f"Coverage regression of {abs(coverage_delta):.1f}% detected"

if changed_code_coverage < 80.0:
    f"Only {changed_code_coverage:.1f}% of changed code is covered - add tests"

if file_count_risk > 50:
    "Many files changed - consider breaking into smaller PRs"
```

### File Risk Recommendations

```python
if coverage < 30.0:
    f"Critical: {file_path} has very low coverage ({coverage:.1f}%)"
elif coverage < 60.0:
    f"High priority: {file_path} needs test coverage"
else:
    f"Medium priority: Improve coverage in {file_path}"
```

## Best Practices

### 1. Interpreting Risk Scores

- **Low Risk (0-25)**: Safe to merge, coverage is good
- **Medium Risk (25-50)**: Review carefully, some gaps exist
- **High Risk (50-75)**: Request changes, significant gaps
- **Critical Risk (75-100)**: Block merge, critical issues

### 2. Addressing High-Risk PRs

1. **Identify** high-risk files using `identify_high_risk_files()`
2. **Analyze** changed code using `analyze_changed_code()`
3. **Detect** uncovered regions using `detect_uncovered_regions()`
4. **Add** tests for critical regions
5. **Re-evaluate** risk after changes

### 3. Preventing Regressions

- Monitor `coverage_delta` for negative values
- Set regression thresholds (e.g., -1% = fail)
- Use `detect_regressions()` in CI/CD
- Block merges with critical regressions

### 4. Configuration Issues

Use `detect_config_vs_missing_tests()` to:
- Identify configuration problems early
- Distinguish from missing tests
- Apply correct remediation

## Limitations and Caveats

### Known Limitations

1. **Line-level coverage**: Doesn't account for branch/condition coverage
2. **Dead code**: May flag uncovered dead code as gaps
3. **Test quality**: Doesn't measure test quality, only coverage
4. **Dynamic code**: May miss dynamically generated code
5. **Pending analysis**: Some providers have pending analysis states

### Handling Pending Analysis

When coverage data is incomplete:

```python
result = gap_service.handle_pending_analysis(file_path, pending_data)

if result["has_pending"]:
    # Wait for analysis to complete
    # Re-evaluate risk after completion
    estimated_coverage = result["estimated_coverage"]
```

## Integration with CI/CD

### Example GitHub Actions Integration

```yaml
- name: Analyze PR Risk
  run: |
    python -c "
    from test_coverage_mcp.services import CoverageRiskAnalysisService

    service = CoverageRiskAnalysisService()
    result = service.score_pr_risk(
        base_coverage=85.0,
        head_coverage=82.0,
        changed_files_count=5,
        uncovered_changed_lines=30,
        total_changed_lines=100
    )

    if result['risk_level'] == 'critical':
        exit(1)  # Fail the build
    "
```

## Future Enhancements

1. **Machine Learning**: Train model on historical data
2. **Complexity Metrics**: Factor in cyclomatic complexity
3. **Test Quality**: Analyze test effectiveness
4. **Trend Analysis**: Track risk over time
5. **Custom Thresholds**: Per-project risk configuration
