---
sidebar_position: 3
title: Coverage Analysis Tools
description: Documentation for coverage analysis tools - Repository health, commits, and comparisons
---

# Coverage Analysis Tools

Coverage analysis tools help you understand and track code coverage metrics across your repository.

## Get Repository Test Health

**Tool Name**: `coverage.repository.health`

Analyze repository test coverage health including coverage metrics, test count, and risk assessment.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repo_slug` | string | Yes | - | Repository identifier (format: `owner/repo`) |
| `provider` | string | No | auto-detect | Specific coverage provider to use |
| `ref` | string | No | default branch | Git reference (branch, tag, or commit SHA) |
| `threshold` | float | No | 80.0 | Coverage threshold percentage (0-100) |

### Response

```typescript
{
  repository: {
    slug: string,
    ref: string,
    coverage: {
      overall: number,
      by_type: {
        line: number,
        branch: number,
        function: number
      }
    },
    metrics: {
      total_lines: number,
      covered_lines: number,
      uncovered_lines: number,
      total_branches: number,
      covered_branches: number,
      total_functions: number,
      covered_functions: number
    },
    test_info: {
      total_tests: number,
      passing_tests: number,
      failing_tests: number,
      skipped_tests: number
    },
    health: {
      status: "HEALTHY" | "AT_RISK" | "CRITICAL",
      risk_level: "LOW" | "MEDIUM" | "HIGH",
      risk_score: number (0-100),
      trend: "IMPROVING" | "STABLE" | "DECLINING"
    }
  },
  execution_metadata: {...}
}
```

### Examples

**Check repository health with default settings:**
```bash
tool: coverage.repository.health
parameters:
  repo_slug: "owner/repo"
```

**Check specific branch with custom threshold:**
```bash
tool: coverage.repository.health
parameters:
  repo_slug: "owner/repo"
  ref: "develop"
  threshold: 85.0
```

### Use Cases

- Monitor repository coverage health
- Identify coverage regressions
- Set and enforce coverage thresholds
- Track coverage trends over time
- Assess test quality and completeness

---

## Get Commit Coverage Summary

**Tool Name**: `coverage.commit.summary`

Get coverage summary for a specific commit including coverage change and affected files.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_slug` | string | Yes | Repository identifier (format: `owner/repo`) |
| `commit_sha` | string | Yes | Git commit SHA (full or abbreviated) |
| `provider` | string | No | Specific coverage provider to use |

### Response

```typescript
{
  commit: {
    sha: string,
    message: string,
    author: string,
    timestamp: string (ISO 8601),
    coverage: {
      overall: number,
      change: number,
      by_type: {
        line: number,
        branch: number,
        function: number
      }
    },
    affected_files: [
      {
        path: string,
        coverage: number,
        change: number,
        lines_added: number,
        lines_removed: number,
        uncovered_lines: number
      }
    ],
    summary: {
      files_changed: number,
      files_improved: number,
      files_declined: number,
      total_lines_changed: number
    }
  },
  execution_metadata: {...}
}
```

### Examples

**Get coverage for a specific commit:**
```bash
tool: coverage.commit.summary
parameters:
  repo_slug: "owner/repo"
  commit_sha: "abc123def456"
```

**Response example:**
```json
{
  "commit": {
    "sha": "abc123def456",
    "message": "feat: add new feature",
    "author": "john@example.com",
    "timestamp": "2024-01-15T10:30:00Z",
    "coverage": {
      "overall": 82.5,
      "change": 2.1,
      "by_type": {
        "line": 82.5,
        "branch": 75.3,
        "function": 88.2
      }
    },
    "affected_files": [
      {
        "path": "src/feature.py",
        "coverage": 95.0,
        "change": 5.0,
        "lines_added": 50,
        "lines_removed": 10,
        "uncovered_lines": 2
      }
    ]
  }
}
```

### Use Cases

- Analyze coverage impact of specific commits
- Track coverage changes in pull requests
- Identify commits with coverage regressions
- Review coverage for code reviews
- Generate commit-level coverage reports

---

## Compare Coverage Between Refs

**Tool Name**: `coverage.comparison.refs`

Compare coverage metrics between two git references (branches, tags, commits).

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_slug` | string | Yes | Repository identifier (format: `owner/repo`) |
| `base_ref` | string | Yes | Base reference (branch, tag, or commit SHA) |
| `head_ref` | string | Yes | Head reference (branch, tag, or commit SHA) |
| `provider` | string | No | Specific coverage provider to use |
| `regression_threshold` | float | No | Threshold for regression detection (%) |

### Response

```typescript
{
  comparison: {
    base_ref: string,
    head_ref: string,
    coverage: {
      base: number,
      head: number,
      change: number,
      change_percent: number,
      status: "IMPROVED" | "STABLE" | "REGRESSED"
    },
    by_type: {
      line: { base: number, head: number, change: number },
      branch: { base: number, head: number, change: number },
      function: { base: number, head: number, change: number }
    },
    files: {
      total_changed: number,
      improved: number,
      declined: number,
      unchanged: number,
      top_improvements: [...],
      top_regressions: [...]
    },
    regression_detected: boolean,
    regression_details?: {
      files_with_regression: number,
      largest_regression: number,
      regression_files: [...]
    }
  },
  execution_metadata: {...}
}
```

### Examples

**Compare main branch with feature branch:**
```bash
tool: coverage.comparison.refs
parameters:
  repo_slug: "owner/repo"
  base_ref: "main"
  head_ref: "feature/new-feature"
```

**Compare two commits:**
```bash
tool: coverage.comparison.refs
parameters:
  repo_slug: "owner/repo"
  base_ref: "abc123def456"
  head_ref: "def456ghi789"
  regression_threshold: 1.0
```

### Use Cases

- Review coverage changes in pull requests
- Detect coverage regressions before merge
- Compare coverage across branches
- Track coverage improvements
- Enforce coverage quality gates

---

## Health Status Levels

Coverage health is assessed on multiple levels:

| Status | Coverage | Risk Level | Action |
|--------|----------|-----------|--------|
| **HEALTHY** | ≥ threshold | LOW | Merge allowed |
| **AT_RISK** | 70-threshold | MEDIUM | Review required |
| **CRITICAL** | < 70% | HIGH | Improvements needed |

---

## Coverage Types

Tools report multiple coverage types:

| Type | Description | Importance |
|------|-------------|-----------|
| **Line Coverage** | % of lines executed | High |
| **Branch Coverage** | % of branches taken | Medium |
| **Function Coverage** | % of functions called | Medium |

---

## Error Handling

### Common Errors

**Repository Not Found**
```json
{
  "error": "Repository 'owner/repo' not found",
  "error_type": "RepositoryHealthError"
}
```

**Commit Not Found**
```json
{
  "error": "Commit 'abc123' not found in repository",
  "error_type": "CommitAnalysisError"
}
```

**Coverage Data Unavailable**
```json
{
  "error": "No coverage data available for ref 'main'",
  "error_type": "CoverageAnalysisError"
}
```

---

## Best Practices

1. **Set realistic thresholds** based on project maturity
2. **Monitor trends** over time, not just snapshots
3. **Investigate regressions** immediately
4. **Use comparisons** for pull request reviews
5. **Track metrics** for continuous improvement

---

## Integration Examples

### Python

```python
from test_coverage_mcp.mcp_server.tools import (
    get_repository_test_health,
    get_commit_coverage_summary,
    compare_coverage_between_refs
)

# Check repository health
health = get_repository_test_health(
    repo_slug="owner/repo",
    threshold=80.0
)

# Get commit coverage
commit = get_commit_coverage_summary(
    repo_slug="owner/repo",
    commit_sha="abc123"
)

# Compare branches
comparison = compare_coverage_between_refs(
    repo_slug="owner/repo",
    base_ref="main",
    head_ref="feature-branch",
    regression_threshold=1.0
)

# Check for regressions
if comparison['comparison']['regression_detected']:
    print("Coverage regression detected!")
    print(f"Regression: {comparison['comparison']['coverage']['change']}%")
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Check Coverage
  run: |
    # Compare with main branch
    mcp-tool coverage.comparison.refs \
      --repo-slug owner/repo \
      --base-ref main \
      --head-ref ${{ github.head_ref }}
```

---

## Next Steps

- **[Provider Discovery Tools](./provider-discovery.md)** - Discover providers
- **[Configuration Guide](../guides/configuration.md)** - Set up coverage analysis
- **[API Reference](./reference.md)** - Detailed specifications
