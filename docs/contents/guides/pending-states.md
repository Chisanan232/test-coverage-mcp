# Handling Pending Analysis States

## Overview

Coverage analysis is not always instantaneous. Some providers support "pending" states where coverage data is being collected or analyzed. This guide explains how to handle these states correctly.

## What Are Pending States?

Pending states occur when:

1. **Coverage upload in progress**: Data is being uploaded to the provider
2. **Analysis running**: Provider is analyzing coverage data
3. **Partial results**: Some files analyzed, others still pending
4. **Async processing**: Provider processes data asynchronously

### Example Pending State

```python
coverage_data = {
    "coverage": 75.0,  # Current coverage
    "pending_regions": [
        {"start": 10, "end": 20, "status": "analyzing"},
        {"start": 50, "end": 60, "status": "pending"},
    ],
    "pending_coverage_estimate": 82.0,  # Estimated after completion
    "last_updated": "2024-04-19T10:30:00Z",
}
```

## Detecting Pending Analysis

### Using the Gap Discovery Service

```python
from test_coverage_mcp.services import CoverageGapDiscoveryService

service = CoverageGapDiscoveryService()

pending_data = {
    "coverage": 75.0,
    "pending_regions": [{"start": 10, "end": 20}],
    "pending_coverage_estimate": 85.0,
}

result = service.handle_pending_analysis("src/module.py", pending_data)

if result["has_pending"]:
    print(f"Pending regions: {result['pending_regions_count']}")
    print(f"Estimated coverage: {result['estimated_coverage']}%")
    print("Recommendations:", result["recommendations"])
```

### Output

```python
{
    "has_pending": True,
    "pending_regions_count": 1,
    "pending_regions": [{"start": 10, "end": 20}],
    "current_coverage": 75.0,
    "estimated_coverage": 85.0,
    "recommendations": [
        "Pending analysis in progress - results may change",
        "Wait for 1 pending region(s) to complete",
        "Re-check coverage after analysis completes"
    ]
}
```

## Handling Strategies

### Strategy 1: Wait for Completion

**When to use**: Critical decisions that require accurate data

```python
import time

def wait_for_coverage_analysis(service, file_path, max_wait_seconds=300):
    """Wait for coverage analysis to complete."""
    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        result = service.handle_pending_analysis(file_path, get_coverage_data())

        if not result["has_pending"]:
            return result  # Analysis complete

        print(f"Waiting... {result['pending_regions_count']} regions pending")
        time.sleep(5)  # Wait 5 seconds before checking again

    raise TimeoutError("Coverage analysis did not complete in time")
```

### Strategy 2: Use Estimated Coverage

**When to use**: Non-blocking analysis, can proceed with estimates

```python
def analyze_with_estimates(service, file_path):
    """Analyze coverage using estimated values."""
    result = service.handle_pending_analysis(file_path, get_coverage_data())

    if result["has_pending"]:
        # Use estimated coverage for decision-making
        coverage = result["estimated_coverage"]
        print(f"Using estimated coverage: {coverage}%")
    else:
        # Use actual coverage
        coverage = result["current_coverage"]
        print(f"Using actual coverage: {coverage}%")

    return coverage
```

### Strategy 3: Defer Decision

**When to use**: Can wait for next analysis cycle

```python
def defer_decision_until_complete(service, file_path):
    """Defer decision until analysis completes."""
    result = service.handle_pending_analysis(file_path, get_coverage_data())

    if result["has_pending"]:
        return {
            "status": "pending",
            "message": f"Analysis in progress, {result['pending_regions_count']} regions pending",
            "estimated_coverage": result["estimated_coverage"],
            "retry_after_seconds": 30,
        }

    return {
        "status": "complete",
        "coverage": result["current_coverage"],
    }
```

## Pending States in PR Analysis

### Before PR Merge

```python
def check_pr_ready_to_merge(pr_number, base_coverage, head_coverage):
    """Check if PR is ready to merge considering pending analysis."""
    service = CoverageGapDiscoveryService()

    # Get coverage data
    coverage_data = get_pr_coverage(pr_number)
    result = service.handle_pending_analysis(f"pr_{pr_number}", coverage_data)

    if result["has_pending"]:
        # Pending analysis - cannot merge yet
        return {
            "can_merge": False,
            "reason": "Coverage analysis in progress",
            "pending_count": result["pending_regions_count"],
            "estimated_coverage": result["estimated_coverage"],
        }

    # Analysis complete - evaluate coverage
    if result["current_coverage"] >= 80.0:
        return {"can_merge": True, "reason": "Coverage meets threshold"}
    else:
        return {"can_merge": False, "reason": "Coverage below threshold"}
```

## Pending States in Risk Analysis

### Adjusting Risk Score for Pending Data

```python
from test_coverage_mcp.services import CoverageRiskAnalysisService

def score_pr_with_pending_adjustment(risk_service, pr_data, pending_data):
    """Score PR risk while accounting for pending analysis."""

    # Check for pending analysis
    if pending_data.get("has_pending"):
        # Use estimated coverage instead of current
        head_coverage = pending_data.get("estimated_coverage", pr_data["head_coverage"])

        # Add confidence penalty
        confidence_penalty = 10.0  # Reduce confidence by 10 points
    else:
        head_coverage = pr_data["head_coverage"]
        confidence_penalty = 0.0

    # Score PR risk
    result = risk_service.score_pr_risk(
        base_coverage=pr_data["base_coverage"],
        head_coverage=head_coverage,
        changed_files_count=pr_data["changed_files_count"],
        uncovered_changed_lines=pr_data["uncovered_changed_lines"],
        total_changed_lines=pr_data["total_changed_lines"],
    )

    # Adjust for pending analysis
    if pending_data.get("has_pending"):
        result["risk_score"] += confidence_penalty
        result["notes"] = f"Risk score adjusted for pending analysis ({pending_data['pending_regions_count']} regions)"

    return result
```

## Pending States in Gap Discovery

### Detecting Gaps with Pending Regions

```python
def analyze_gaps_with_pending(gap_service, file_path, coverage_data):
    """Analyze coverage gaps while handling pending regions."""

    # Check for pending analysis
    pending_result = gap_service.handle_pending_analysis(file_path, coverage_data)

    if pending_result["has_pending"]:
        print(f"⏳ Analysis in progress for {file_path}")
        print(f"   Current coverage: {pending_result['current_coverage']}%")
        print(f"   Estimated coverage: {pending_result['estimated_coverage']}%")
        print(f"   Pending regions: {pending_result['pending_regions_count']}")

        # Detect gaps based on current data
        gaps = gap_service.detect_uncovered_regions(file_path, coverage_data)

        return {
            "gaps": gaps,
            "pending": True,
            "estimated_gaps_after_completion": estimate_gaps_after_pending(
                gaps, pending_result
            ),
        }
    else:
        # Analysis complete - detect final gaps
        gaps = gap_service.detect_uncovered_regions(file_path, coverage_data)

        return {
            "gaps": gaps,
            "pending": False,
        }
```

## Best Practices

### 1. Always Check for Pending States

```python
# ✓ Good
result = service.handle_pending_analysis(file_path, data)
if result["has_pending"]:
    # Handle pending case
    pass

# ✗ Bad - ignores pending analysis
coverage = data["coverage"]  # May be incomplete
```

### 2. Use Appropriate Thresholds for Pending Data

```python
# ✓ Good - adjust thresholds for pending
if pending_result["has_pending"]:
    threshold = 85.0  # Higher threshold for estimated data
else:
    threshold = 80.0  # Normal threshold for actual data

# ✗ Bad - same threshold regardless of data state
threshold = 80.0
```

### 3. Communicate Pending Status to Users

```python
# ✓ Good - inform users
if pending_result["has_pending"]:
    print("⏳ Coverage analysis in progress")
    print(f"   Estimated completion: {pending_result['estimated_time']}")

# ✗ Bad - silently use estimated data
coverage = pending_result["estimated_coverage"]
```

### 4. Retry with Exponential Backoff

```python
import time

def wait_for_analysis_with_backoff(service, file_path, max_retries=5):
    """Wait for analysis with exponential backoff."""
    retry_count = 0
    backoff_seconds = 1

    while retry_count < max_retries:
        result = service.handle_pending_analysis(file_path, get_coverage_data())

        if not result["has_pending"]:
            return result

        print(f"Waiting {backoff_seconds}s before retry...")
        time.sleep(backoff_seconds)

        backoff_seconds = min(backoff_seconds * 2, 60)  # Cap at 60 seconds
        retry_count += 1

    raise TimeoutError(f"Analysis did not complete after {max_retries} retries")
```

### 5. Log Pending States for Debugging

```python
import logging

logger = logging.getLogger(__name__)

def analyze_with_logging(service, file_path):
    """Analyze coverage with detailed logging."""
    result = service.handle_pending_analysis(file_path, get_coverage_data())

    if result["has_pending"]:
        logger.warning(
            "Pending analysis detected",
            extra={
                "file": file_path,
                "pending_regions": result["pending_regions_count"],
                "current_coverage": result["current_coverage"],
                "estimated_coverage": result["estimated_coverage"],
            }
        )
    else:
        logger.info(
            "Analysis complete",
            extra={
                "file": file_path,
                "coverage": result["current_coverage"],
            }
        )

    return result
```

## Common Issues and Solutions

### Issue 1: Stale Pending Data

**Problem**: Pending state never resolves

**Solution**:
```python
def check_pending_timeout(pending_result, timeout_minutes=30):
    """Check if pending analysis has timed out."""
    last_updated = pending_result.get("last_updated")

    if not last_updated:
        return False

    age_minutes = (datetime.utcnow() - last_updated).total_seconds() / 60

    if age_minutes > timeout_minutes:
        logger.error(f"Pending analysis timeout: {age_minutes} minutes old")
        return True

    return False
```

### Issue 2: Inconsistent Estimates

**Problem**: Estimated coverage differs significantly from actual

**Solution**:
```python
def validate_estimate_accuracy(current_coverage, estimated_coverage, max_diff=5.0):
    """Validate that estimate is reasonable."""
    diff = abs(estimated_coverage - current_coverage)

    if diff > max_diff:
        logger.warning(
            f"Estimate differs from current by {diff}%",
            extra={
                "current": current_coverage,
                "estimated": estimated_coverage,
            }
        )
        return False

    return True
```

### Issue 3: Partial Results

**Problem**: Some files analyzed, others still pending

**Solution**:
```python
def analyze_partial_results(gap_service, files_data):
    """Handle partial coverage results."""
    complete_files = []
    pending_files = []

    for file_path, coverage_data in files_data.items():
        result = gap_service.handle_pending_analysis(file_path, coverage_data)

        if result["has_pending"]:
            pending_files.append((file_path, result))
        else:
            complete_files.append((file_path, result))

    return {
        "complete": complete_files,
        "pending": pending_files,
        "completion_percentage": len(complete_files) / len(files_data) * 100,
    }
```

## Summary

Pending analysis states are common in coverage tools. Handle them correctly by:

1. **Detecting** pending states with `handle_pending_analysis()`
2. **Choosing** appropriate strategy (wait, estimate, defer)
3. **Adjusting** thresholds and confidence for pending data
4. **Communicating** status to users
5. **Logging** for debugging and monitoring
6. **Handling** edge cases and timeouts

Always prioritize data accuracy over speed when making critical decisions.
