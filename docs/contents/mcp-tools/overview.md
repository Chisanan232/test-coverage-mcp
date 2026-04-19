# MCP Tools Overview

## Introduction

The test-coverage-mcp project provides a set of Model Context Protocol (MCP) tools that enable AI systems to interact with coverage providers and analyze test coverage data. These tools are designed to be used with Claude and other MCP-compatible clients.

## Available Tools

### 1. list_coverage_providers

Lists all available coverage providers with their metadata and capabilities.

**Purpose**: Discover what coverage providers are installed and their capabilities

**Parameters**:
- `include_capabilities` (bool, default: True) - Include capability information
- `include_health` (bool, default: True) - Include health status

**Returns**:
- List of providers with metadata
- Total provider count
- Health statistics

**Use Cases**:
- Discover available providers in the system
- Check provider health status
- Understand provider capabilities before using them

### 2. describe_coverage_provider

Get detailed information about a specific coverage provider.

**Purpose**: Understand a provider's capabilities, limitations, and current status

**Parameters**:
- `provider_name` (str, required) - Name of the provider to describe

**Returns**:
- Provider metadata (name, version, description)
- Capability matrix with support levels
- Current health status
- Limitations and error messages

**Use Cases**:
- Get detailed provider information
- Check if a provider supports specific capabilities
- Diagnose provider issues

### 3. get_repository_test_health

Analyze test coverage health for a repository.

**Purpose**: Get comprehensive coverage health analysis with risk assessment and recommendations

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, optional) - Specific provider to use
- `ref` (str, optional) - Git reference (branch, tag, commit)
- `threshold` (float, default: 80.0) - Coverage threshold percentage

**Returns**:
- Coverage metrics (average, range, provider stats)
- Health summary (is_healthy, below_threshold)
- Risk analysis (level, gap, recommendations)
- Next actions for improvement

**Use Cases**:
- Check repository coverage health
- Identify coverage risks
- Get recommendations for improvement
- Track coverage trends

### 4. get_commit_coverage_summary

Get coverage summary for a specific commit.

**Purpose**: Analyze coverage at a specific point in time

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `commit_sha` (str, required) - Commit SHA

**Returns**:
- Coverage metrics for the commit
- File coverage details
- Execution metadata

**Use Cases**:
- Check coverage at a specific commit
- Analyze historical coverage
- Track coverage changes over time

### 5. compare_coverage_between_refs

Compare coverage between two git references.

**Purpose**: Analyze coverage changes between branches, tags, or commits

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `base_ref` (str, required) - Base reference
- `head_ref` (str, required) - Head reference to compare

**Returns**:
- Base and head coverage percentages
- Coverage delta
- Provider-specific results
- Improvement/regression status

**Use Cases**:
- Compare coverage between branches
- Detect coverage regressions
- Track coverage improvements

### 6. find_untested_changed_code

Find untested code in changed files.

**Purpose**: Identify coverage gaps in changed code between two references

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `base_ref` (str, required) - Base reference
- `head_ref` (str, required) - Head reference

**Returns**:
- Changed code statistics
- Uncovered regions with risk levels
- Pending analysis regions
- Gap summary

**Use Cases**:
- Review coverage in pull requests
- Identify untested changes
- Assess PR coverage risk

### 7. analyze_pr_coverage_risk

Analyze coverage risk in a pull request.

**Purpose**: Evaluate coverage risk and provide mitigation recommendations

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `base_ref` (str, required) - Base reference
- `head_ref` (str, required) - Head reference

**Returns**:
- Risk level and score
- Coverage delta
- High-risk files
- Recommendations

**Use Cases**:
- Assess PR coverage risk
- Get risk mitigation recommendations
- Make merge decisions

### 8. find_low_coverage_files

Find files with coverage below a threshold.

**Purpose**: Identify files that need coverage improvement

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `ref` (str, required) - Git reference
- `threshold` (float, default: 80.0) - Coverage threshold
- `limit` (int, default: 10) - Maximum files to return

**Returns**:
- Files below threshold
- Coverage percentages
- Improvement potential
- Summary

**Use Cases**:
- Find low coverage files
- Prioritize coverage improvement
- Track coverage progress

### 9. diagnose_coverage_configuration

Diagnose coverage configuration issues.

**Purpose**: Analyze configuration and identify problems

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name

**Returns**:
- Configuration validity
- Over-included paths
- Missing exclusions
- Threshold issues
- Scoping issues
- Summary

**Use Cases**:
- Audit coverage configuration
- Identify configuration problems
- Get improvement recommendations

### 10. recommend_test_plan

Generate test recommendations for coverage improvement.

**Purpose**: Get intelligent test suggestions based on coverage gaps

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `target` (str, default: "repo") - Analysis target: repo, pr, or file path

**Returns**:
- Test recommendations with priority
- Suggested test types and scenarios
- Rationale for each recommendation
- Summary

**Use Cases**:
- Get test recommendations
- Plan test implementation
- Improve coverage efficiently

### 11. identify_excludable_code_candidates

Identify code that should be excluded from coverage.

**Purpose**: Find code candidates for exclusion using conservative detection

**Parameters**:
- `repo_slug` (str, required) - Repository in format "owner/repo"
- `provider` (str, required) - Coverage provider name
- `ref` (str, required) - Git reference

**Returns**:
- Excludable code candidates
- Excludability scores
- Detection signal breakdown
- Summary

**Use Cases**:
- Find generated code
- Identify vendor code
- Detect deprecated code
- Improve coverage metrics

## Tool Architecture

### Design Principles

1. **Multi-Provider Support**: Tools aggregate data from multiple providers
2. **Graceful Degradation**: Continue with available providers if some fail
3. **Health-Aware**: Consider provider health and response time
4. **Type Safety**: Full type hints for all parameters and returns
5. **Error Handling**: Comprehensive error messages and error types

### Integration Points

Tools integrate with:
- **ProviderDiscoveryService**: For provider management
- **RepositoryHealthService**: For health analysis
- **CoverageComparisonService**: For coverage comparison (future)
- **ProviderRegistry**: For provider lifecycle

## Error Handling

All tools return structured error responses:

```json
{
  "error": "Error message",
  "error_type": "ErrorType",
  "execution_metadata": { ... }
}
```

Common error types:
- `ProviderDiscoveryError` - Provider discovery failed
- `ProviderNotFoundError` - Requested provider not found
- `InvalidRepositorySlugError` - Invalid repo format
- `RepositoryHealthAnalysisError` - Health analysis failed

## Execution Metadata

All tool responses include execution metadata:

```json
{
  "provider_name": "test-coverage-mcp",
  "provider_version": "0.1.0",
  "support_level": "advanced",
  "used_capabilities": [],
  "analysis_depth": "repo",
  "execution_time_ms": 0.0
}
```

## Usage Examples

### List All Providers

```
list_coverage_providers(include_capabilities=True, include_health=True)
```

Response:
```json
{
  "providers": [
    {
      "name": "codecov",
      "version": "0.1.0",
      "description": "Codecov coverage provider",
      "supported_capabilities": ["repository_summary", "file_coverage"],
      "support_levels": {
        "repository_summary": "advanced",
        "file_coverage": "advanced"
      },
      "health": {
        "is_healthy": true,
        "response_time_ms": 150.0
      }
    }
  ],
  "total_providers": 1,
  "healthy_providers": 1
}
```

### Describe a Provider

```
describe_coverage_provider("codecov")
```

Response:
```json
{
  "name": "codecov",
  "version": "0.1.0",
  "description": "Codecov coverage provider",
  "capabilities": {
    "supported": ["repository_summary", "file_coverage"],
    "support_levels": {
      "repository_summary": "advanced",
      "file_coverage": "advanced"
    }
  },
  "health": {
    "is_healthy": true,
    "response_time_ms": 150.0
  }
}
```

### Get Repository Health

```
get_repository_test_health("owner/repo", threshold=85.0)
```

Response:
```json
{
  "repo_slug": "owner/repo",
  "coverage_metrics": {
    "average_coverage": 82.5,
    "coverage_range": {
      "min": 80.0,
      "max": 85.0
    },
    "providers_queried": 1,
    "providers_succeeded": 1,
    "providers_failed": 0
  },
  "health_summary": {
    "is_healthy": false,
    "coverage_below_threshold": true,
    "threshold": 85.0
  },
  "risk_analysis": {
    "risk_level": "medium",
    "current_coverage": 82.5,
    "gap": 2.5,
    "recommendations": [
      "Increase coverage by 2.5% to meet the 85% threshold",
      "Review uncovered regions and prioritize high-risk areas"
    ]
  },
  "next_actions": [
    "Increase coverage by 2.5% to meet the 85% threshold",
    "Review uncovered regions and prioritize high-risk areas",
    "Implement continuous coverage monitoring"
  ]
}
```

## Future Enhancements

1. **Coverage Comparison Tool** - Compare coverage between refs
2. **Regression Detection** - Identify coverage regressions
3. **Trend Analysis** - Track coverage over time
4. **Custom Metrics** - User-defined coverage goals
5. **Webhook Support** - Real-time coverage alerts

## Best Practices

1. **Always check provider health** before relying on results
2. **Use appropriate thresholds** for your project
3. **Handle errors gracefully** in client applications
4. **Cache results** when appropriate to reduce load
5. **Monitor execution metadata** for performance insights
