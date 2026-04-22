# MCP Tools Complete Reference

## All 11 Tools at a Glance

| # | Tool | Category | Purpose |
|---|------|----------|---------|
| 1 | list_coverage_providers | Provider | Discover available providers |
| 2 | describe_coverage_provider | Provider | Get provider details |
| 3 | get_repository_test_health | Provider | Analyze repository health |
| 4 | get_commit_coverage_summary | Commit | Coverage at specific commit |
| 5 | compare_coverage_between_refs | Comparison | Compare coverage changes |
| 6 | find_untested_changed_code | PR Analysis | Identify coverage gaps |
| 7 | analyze_pr_coverage_risk | PR Analysis | Assess PR risk |
| 8 | find_low_coverage_files | Advanced | Find low-coverage files |
| 9 | diagnose_coverage_configuration | Advanced | Analyze configuration |
| 10 | recommend_test_plan | Advanced | Get test recommendations |
| 11 | identify_excludable_code_candidates | Advanced | Find code to exclude |

## Tool Categories

### Category 1: Provider Tools (Tools 1-3)

These tools manage and discover coverage providers.

#### Tool 1: list_coverage_providers

**Purpose**: Discover all available coverage providers

**Input**:
```json
{
  "include_capabilities": true,
  "include_health": true
}
```

**Output**:
```json
{
  "providers": [
    {
      "name": "codecov",
      "version": "1.0.0",
      "health": "healthy",
      "capabilities": {
        "repository_summary": true,
        "file_coverage": true,
        "coverage_delta": true
      }
    }
  ],
  "total_count": 1
}
```

**Use Cases**:
- Discover installed providers
- Check provider availability
- Verify provider health

#### Tool 2: describe_coverage_provider

**Purpose**: Get detailed information about a provider

**Input**:
```json
{
  "provider_name": "codecov"
}
```

**Output**:
```json
{
  "name": "codecov",
  "version": "1.0.0",
  "description": "Codecov coverage provider",
  "capabilities": {
    "repository_summary": true,
    "file_coverage": true,
    "coverage_delta": true,
    "uncovered_regions": true
  },
  "health": {
    "status": "healthy",
    "response_time_ms": 150
  },
  "limitations": []
}
```

**Use Cases**:
- Understand provider capabilities
- Check provider status
- Diagnose provider issues

#### Tool 3: get_repository_test_health

**Purpose**: Analyze repository test coverage health

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "coverage": 85.5,
  "health_status": "good",
  "files_count": 42,
  "lines_covered": 1234,
  "lines_total": 1440,
  "recommendations": [
    "Improve coverage in src/utils.py (60%)"
  ]
}
```

**Use Cases**:
- Get overall repository health
- Identify coverage trends
- Get improvement recommendations

### Category 2: Commit & Comparison Tools (Tools 4-5)

These tools analyze coverage at specific commits and compare changes.

#### Tool 4: get_commit_coverage_summary

**Purpose**: Get coverage information at a specific commit

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "commit_sha": "abc123def456",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "commit_sha": "abc123def456",
  "coverage": 85.5,
  "files_count": 42,
  "lines_covered": 1234,
  "lines_total": 1440,
  "timestamp": "2024-04-20T10:30:00Z"
}
```

**Use Cases**:
- Get coverage at specific commit
- Track coverage history
- Identify when coverage changed

#### Tool 5: compare_coverage_between_refs

**Purpose**: Compare coverage between two git references

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "base_ref": "main",
  "head_ref": "feature-branch",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "base_ref": "main",
  "head_ref": "feature-branch",
  "base_coverage": 80.0,
  "head_coverage": 85.5,
  "delta": 5.5,
  "status": "improved",
  "files_changed": 5,
  "coverage_improved": 3,
  "coverage_degraded": 1
}
```

**Use Cases**:
- Compare PR coverage changes
- Track coverage trends
- Identify regression risks

### Category 3: PR Analysis Tools (Tools 6-7)

These tools analyze pull requests for coverage issues.

#### Tool 6: find_untested_changed_code

**Purpose**: Identify untested code in changed files

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "pr_number": 123,
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "pr_number": 123,
  "untested_regions": [
    {
      "file": "src/utils.py",
      "line_start": 10,
      "line_end": 15,
      "type": "branch",
      "risk_level": "high"
    }
  ],
  "total_untested_lines": 42,
  "coverage_impact": "medium"
}
```

**Use Cases**:
- Review PR coverage gaps
- Identify missing tests
- Assess coverage risk

#### Tool 7: analyze_pr_coverage_risk

**Purpose**: Assess overall PR coverage risk

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "pr_number": 123,
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "pr_number": 123,
  "risk_level": "medium",
  "coverage_delta": -2.5,
  "untested_lines": 42,
  "risk_factors": [
    "Coverage decreased",
    "New untested code in critical files"
  ],
  "recommendations": [
    "Add tests for src/core.py",
    "Review branch coverage in utils.py"
  ]
}
```

**Use Cases**:
- Assess PR risk before merge
- Get test recommendations
- Make merge decisions

### Category 4: Advanced Analysis Tools (Tools 8-11)

These tools provide advanced coverage analysis.

#### Tool 8: find_low_coverage_files

**Purpose**: Identify files with low coverage

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "threshold": 70,
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "threshold": 70,
  "low_coverage_files": [
    {
      "file": "src/utils.py",
      "coverage": 60.0,
      "lines_covered": 60,
      "lines_total": 100
    }
  ],
  "total_files": 42,
  "files_below_threshold": 5
}
```

**Use Cases**:
- Identify coverage improvement targets
- Prioritize testing efforts
- Track coverage metrics

#### Tool 9: diagnose_coverage_configuration

**Purpose**: Analyze coverage configuration

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "configuration": {
    "coverage_tool": "pytest-cov",
    "exclude_patterns": ["tests/*", "venv/*"],
    "branch_coverage": true
  },
  "issues": [
    "Missing coverage for generated code"
  ],
  "recommendations": [
    "Configure coverage.xml generation",
    "Add branch coverage tracking"
  ]
}
```

**Use Cases**:
- Diagnose configuration issues
- Optimize coverage settings
- Improve measurement accuracy

#### Tool 10: recommend_test_plan

**Purpose**: Get test recommendations

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "focus_area": "low_coverage",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "recommendations": [
    {
      "file": "src/utils.py",
      "priority": "high",
      "reason": "60% coverage",
      "suggested_tests": [
        "Test error handling in parse_config()",
        "Test edge cases in validate_input()"
      ]
    }
  ],
  "estimated_effort": "medium"
}
```

**Use Cases**:
- Plan testing efforts
- Prioritize test development
- Improve coverage systematically

#### Tool 11: identify_excludable_code_candidates

**Purpose**: Find code that can be excluded from coverage

**Input**:
```json
{
  "repo_slug": "owner/repo",
  "provider": "codecov"
}
```

**Output**:
```json
{
  "repo_slug": "owner/repo",
  "candidates": [
    {
      "file": "src/debug.py",
      "lines": [10, 15, 20],
      "reason": "Debug code",
      "confidence": 0.95
    }
  ],
  "total_excludable_lines": 42
}
```

**Use Cases**:
- Identify code to exclude
- Clean up coverage metrics
- Focus on testable code

## Tool Selection Guide

### By Use Case

**Discovering Providers**:
- Use `list_coverage_providers` to find available providers
- Use `describe_coverage_provider` for details

**Analyzing Repository Health**:
- Use `get_repository_test_health` for overall health
- Use `find_low_coverage_files` for improvement targets

**Reviewing Pull Requests**:
- Use `compare_coverage_between_refs` for changes
- Use `find_untested_changed_code` for gaps
- Use `analyze_pr_coverage_risk` for risk assessment

**Planning Tests**:
- Use `recommend_test_plan` for guidance
- Use `diagnose_coverage_configuration` for setup
- Use `identify_excludable_code_candidates` for cleanup

**Tracking Commits**:
- Use `get_commit_coverage_summary` for specific commits
- Use `compare_coverage_between_refs` for trends

## Common Workflows

### Workflow 1: PR Review

1. `list_coverage_providers` - Check available providers
2. `compare_coverage_between_refs` - See coverage changes
3. `find_untested_changed_code` - Identify gaps
4. `analyze_pr_coverage_risk` - Assess risk
5. Make merge decision

### Workflow 2: Coverage Improvement

1. `get_repository_test_health` - Check current health
2. `find_low_coverage_files` - Identify targets
3. `recommend_test_plan` - Get suggestions
4. Implement tests
5. `get_repository_test_health` - Verify improvement

### Workflow 3: Configuration Audit

1. `describe_coverage_provider` - Check provider
2. `diagnose_coverage_configuration` - Analyze config
3. `identify_excludable_code_candidates` - Find exclusions
4. Update configuration
5. `get_repository_test_health` - Verify changes

## Error Handling

All tools return structured errors:

```json
{
  "error": {
    "type": "ProviderNotFound",
    "message": "Provider 'unknown' not found",
    "details": {
      "available_providers": ["codecov"]
    }
  }
}
```

## Performance Characteristics

- **Provider Tools**: < 100ms
- **Commit Tools**: 100-500ms
- **PR Analysis Tools**: 200-1000ms
- **Advanced Tools**: 500-2000ms

## See Also

- [Architecture Overview](../architecture/overview.md)
- [Plugin Development Guide](../guides/plugin-development.md)
- [CLI Reference](../cli/commands.md)
- [Deployment Guide](../deployment/docker.md)
