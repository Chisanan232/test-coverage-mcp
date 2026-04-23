---
sidebar_position: 1
title: MCP Tools Overview
description: Comprehensive overview of all available MCP tools in test-coverage-mcp
---

# MCP Tools Overview

The test-coverage-mcp server provides a suite of Model Context Protocol (MCP) tools for analyzing code coverage, managing test coverage providers, and generating coverage insights.

## Available Tools

The server currently implements **5 core tools** organized into two categories:

### Provider Management Tools

Tools for discovering and managing coverage providers:

1. **List Coverage Providers** (`coverage.providers.list`)
   - Discover all available coverage providers
   - View provider capabilities and health status
   - Filter by support level and analysis depth

2. **Describe Coverage Provider** (`coverage.providers.describe`)
   - Get detailed information about a specific provider
   - View supported capabilities and limitations
   - Check provider health and status

### Coverage Analysis Tools

Tools for analyzing repository coverage and generating insights:

3. **Get Repository Test Health** (`coverage.repository.health`)
   - Analyze repository test coverage health
   - Get coverage metrics and test counts
   - Assess coverage risk levels

4. **Get Commit Coverage Summary** (`coverage.commit.summary`)
   - Retrieve coverage for specific commits
   - Track coverage changes per commit
   - Identify affected files and coverage impact

5. **Compare Coverage Between Refs** (`coverage.comparison.refs`)
   - Compare coverage between git references
   - Identify coverage regressions
   - Analyze coverage trends across branches

## Tool Categories

### By Use Case

**Discovery & Monitoring**
- List Coverage Providers
- Describe Coverage Provider
- Get Repository Test Health

**Analysis & Comparison**
- Get Commit Coverage Summary
- Compare Coverage Between Refs

### By Capability

**Read-Only Operations**
- All tools are read-only
- No destructive operations
- Safe for CI/CD integration

**Data Sources**
- Coverage provider integrations
- Git repository analysis
- Historical coverage data

## Common Parameters

Most tools accept these common parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `repo_slug` | string | Repository identifier (format: `owner/repo`) |
| `provider` | string (optional) | Specific coverage provider to use |
| `ref` | string (optional) | Git reference (branch, tag, or commit SHA) |

## Response Format

All tools return structured responses with:

```typescript
{
  // Tool-specific data
  data: {...},

  // Execution metadata
  execution_metadata: {
    provider_name: string,
    provider_version: string,
    support_level: "BASIC" | "ADVANCED" | "EXPERT",
    used_capabilities: string[],
    analysis_depth: "FILE" | "FUNCTION" | "REPOSITORY",
    execution_time_ms: number
  },

  // Error information (if applicable)
  error?: string,
  error_type?: string
}
```

## Error Handling

Tools provide clear error messages and types:

- `ProviderNotFoundError` - Provider doesn't exist
- `InvalidParameterError` - Invalid parameter values
- `ProviderHealthError` - Provider is unhealthy
- `CoverageAnalysisError` - Analysis failed
- `RepositoryHealthError` - Repository analysis failed
- `CommitAnalysisError` - Commit analysis failed
- `CoverageComparisonError` - Comparison failed

## Integration Examples

### Using with Claude

```
User: "What's the test coverage health of my repository?"

Claude uses: Get Repository Test Health
- Analyzes coverage metrics
- Identifies risk areas
- Provides recommendations
```

### Using with Automation

```python
from test_coverage_mcp.mcp_server.tools import (
    list_coverage_providers,
    get_repository_test_health,
    compare_coverage_between_refs
)

# Discover available providers
providers = list_coverage_providers()

# Check repository health
health = get_repository_test_health(
    repo_slug="owner/repo",
    threshold=80.0
)

# Compare coverage between branches
comparison = compare_coverage_between_refs(
    repo_slug="owner/repo",
    base_ref="main",
    head_ref="feature-branch"
)
```

## Next Steps

- **[Provider Discovery Tools](./provider-discovery.md)** - Learn about provider management
- **[Coverage Analysis Tools](./coverage-analysis.md)** - Analyze coverage metrics
- **[Tools Categorization](./tools-categorization.md)** - Tool selection guide
- **[Configuration Guide](../guides/configuration.md)** - Set up providers

## Tool Statistics

| Metric | Value |
|--------|-------|
| Total Tools | 5 |
| Read-Only Tools | 5 |
| Destructive Tools | 0 |
| Average Response Time | < 500ms |
| Supported Providers | 3+ |

## Future Tools

The following tools are planned for future releases:

- `get_coverage_trends` - Historical coverage analysis
- `identify_coverage_gaps` - Find untested code areas
- `get_test_recommendations` - AI-powered test suggestions
- `analyze_coverage_risk` - Risk assessment for changes
- `generate_coverage_report` - Generate coverage reports
- `validate_coverage_thresholds` - Validate against thresholds
