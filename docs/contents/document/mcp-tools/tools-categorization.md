---
sidebar_position: 1.5
title: Tools Categorization & Selection Guide
description: Guide to selecting the right MCP tool for your use case
---

# Tools Categorization & Selection Guide

This guide helps you understand how to categorize and select the right MCP tool for your specific needs.

## Tool Matrix

### By Primary Purpose

| Purpose | Tools | Best For |
|---------|-------|----------|
| **Discovery** | List Providers, Describe Provider | Understanding available resources |
| **Monitoring** | Repository Health | Continuous coverage tracking |
| **Analysis** | Commit Summary, Compare Refs | Detailed coverage investigation |

### By Data Source

| Source | Tools | Use Case |
|--------|-------|----------|
| **Provider Metadata** | List Providers, Describe Provider | Understanding capabilities |
| **Repository State** | Repository Health | Current coverage status |
| **Commit History** | Commit Summary | Historical analysis |
| **Reference Comparison** | Compare Refs | Trend analysis |

### By Scope

| Scope | Tools | Granularity |
|-------|-------|-------------|
| **Provider Level** | List/Describe Providers | Provider capabilities |
| **Repository Level** | Repository Health | Entire repository |
| **Commit Level** | Commit Summary | Single commit |
| **Reference Level** | Compare Refs | Between references |

## Selection Decision Tree

```
Start
  ↓
Need to discover providers?
  ├─ Yes → List Coverage Providers
  │         ↓
  │         Need details about one?
  │         └─ Yes → Describe Coverage Provider
  │
  └─ No → Need to analyze coverage?
          ├─ Yes → What's your scope?
          │         ├─ Repository health → Get Repository Test Health
          │         ├─ Specific commit → Get Commit Coverage Summary
          │         └─ Compare versions → Compare Coverage Between Refs
          │
          └─ No → Check documentation
```

## Common Workflows

### Workflow 1: Pre-Merge Coverage Check

**Goal**: Verify coverage before merging a pull request

```
1. List Coverage Providers
   ↓ (verify providers are healthy)
2. Compare Coverage Between Refs
   ├─ base_ref: main
   └─ head_ref: feature-branch
   ↓ (check for regressions)
3. Get Repository Test Health (on feature branch)
   ↓ (verify overall health)
4. Decision: Merge or request improvements
```

**Tools Used**: Compare Refs, Repository Health

### Workflow 2: Commit-Level Analysis

**Goal**: Understand coverage impact of a specific commit

```
1. Get Commit Coverage Summary
   ├─ repo_slug: owner/repo
   └─ commit_sha: abc123
   ↓ (see affected files and changes)
2. Analyze results
   ├─ Files with coverage decline
   ├─ Files with improvement
   └─ Overall impact
3. Generate report or take action
```

**Tools Used**: Commit Summary

### Workflow 3: Provider Health Monitoring

**Goal**: Monitor coverage provider availability and performance

```
1. List Coverage Providers
   ├─ include_health: true
   └─ include_capabilities: true
   ↓ (check all providers)
2. For each unhealthy provider:
   Describe Coverage Provider
   ├─ Check error details
   └─ Review configuration
3. Alert or take corrective action
```

**Tools Used**: List Providers, Describe Provider

### Workflow 4: Coverage Trend Analysis

**Goal**: Track coverage changes over time

```
1. Get Repository Test Health
   ├─ ref: main
   └─ threshold: 80.0
   ↓ (current state)
2. Compare Coverage Between Refs
   ├─ base_ref: main
   └─ head_ref: develop
   ↓ (see trend direction)
3. Identify patterns
   ├─ Improving areas
   ├─ Declining areas
   └─ Stable areas
4. Plan improvements
```

**Tools Used**: Repository Health, Compare Refs

## Tool Combinations

### Recommended Pairings

| Pair | Purpose | Benefit |
|------|---------|---------|
| List + Describe Providers | Provider selection | Comprehensive provider info |
| Repository Health + Commit Summary | Detailed analysis | Context and specifics |
| Compare Refs + Commit Summary | Change analysis | Before/after view |
| List Providers + Repository Health | Full assessment | Complete picture |

### Anti-Patterns

❌ **Don't**: Use Commit Summary for repository-wide analysis
- **Why**: Commit-level data is too granular
- **Instead**: Use Repository Health

❌ **Don't**: Skip provider health checks
- **Why**: Unhealthy providers give unreliable data
- **Instead**: Always check List Providers first

❌ **Don't**: Compare unrelated references
- **Why**: Results may be meaningless
- **Instead**: Compare related branches/tags

## Performance Considerations

### Response Times

| Tool | Typical Time | Factors |
|------|--------------|---------|
| List Providers | < 100ms | Number of providers |
| Describe Provider | < 200ms | Provider complexity |
| Repository Health | 200-500ms | Repository size |
| Commit Summary | 300-800ms | Commit scope |
| Compare Refs | 500-2000ms | Reference distance |

### Optimization Tips

1. **Batch operations** when possible
2. **Use specific providers** instead of auto-detect
3. **Cache results** for frequently accessed data
4. **Monitor response times** for performance issues
5. **Use lightweight options** (e.g., exclude health checks)

## Error Recovery Strategies

### Provider Not Found

```
1. List Coverage Providers
2. Check available providers
3. Use available provider or add new one
4. Retry operation
```

### Unhealthy Provider

```
1. Describe Coverage Provider
2. Check error details
3. Wait for provider recovery OR
4. Switch to alternative provider
5. Retry operation
```

### Missing Coverage Data

```
1. Verify repository is tracked
2. Verify reference exists
3. Check provider configuration
4. Wait for data to be available
5. Retry operation
```

## Integration Patterns

### Pattern 1: Continuous Monitoring

```python
# Run periodically (e.g., hourly)
health = get_repository_test_health(repo_slug="owner/repo")
if health['repository']['health']['status'] == 'CRITICAL':
    alert_team()
```

### Pattern 2: Pull Request Checks

```python
# Run on PR creation/update
comparison = compare_coverage_between_refs(
    repo_slug="owner/repo",
    base_ref="main",
    head_ref=pr_branch
)
if comparison['comparison']['regression_detected']:
    comment_on_pr("Coverage regression detected")
```

### Pattern 3: Commit Analysis

```python
# Run on each commit
commit = get_commit_coverage_summary(
    repo_slug="owner/repo",
    commit_sha=commit_hash
)
log_metrics(commit['commit']['coverage'])
```

### Pattern 4: Provider Health Dashboard

```python
# Run periodically
providers = list_coverage_providers(
    include_health=True,
    include_capabilities=True
)
update_dashboard(providers)
```

## Best Practices Summary

✅ **DO**:
- Check provider health before analysis
- Use specific providers when known
- Cache results appropriately
- Monitor performance metrics
- Handle errors gracefully
- Document tool usage in your workflow

❌ **DON'T**:
- Assume providers are always healthy
- Use auto-detection in performance-critical paths
- Ignore error messages
- Compare unrelated references
- Overuse tools in tight loops
- Skip validation of parameters

## Next Steps

- **[Provider Discovery Tools](./provider-discovery.md)** - Detailed tool documentation
- **[Coverage Analysis Tools](./coverage-analysis.md)** - Analysis tool documentation
- **[Configuration Guide](../guides/configuration.md)** - Set up your environment
- **[Provider Development](../guides/provider-development.md)** - Create custom providers
