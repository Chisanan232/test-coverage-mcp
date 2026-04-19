# diagnose_coverage_configuration Tool

## Overview

The `diagnose_coverage_configuration` tool analyzes repository coverage configuration to identify potential issues and provide recommendations for improvement. It examines configuration files, coverage settings, and thresholds to detect problems early.

This tool leverages the `CoverageConfigDiagnosisService` to provide comprehensive configuration analysis with actionable recommendations.

## Function Signature

```python
def diagnose_coverage_configuration(
    repo_slug: str,
    provider: str,
) -> Dict[str, Any]
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_slug` | `str` | Yes | Repository slug in format `owner/repo` |
| `provider` | `str` | Yes | Coverage provider name (e.g., `codecov`, `coveralls`) |

## Return Value

Returns a dictionary with the following structure:

```python
{
    "repo_owner": str,                    # Repository owner
    "repo_name": str,                     # Repository name
    "config_valid": bool,                 # Whether configuration is valid
    "parse_errors": [str],                # Configuration parsing errors
    "over_included_paths": [              # Paths that are over-included
        {
            "path": str,                  # The over-included path
            "reason": str,                # Why it's over-included
            "suggestion": str,            # Suggested action
        },
        ...
    ],
    "missing_exclusions": [               # Suggested missing exclusions
        {
            "pattern": str,               # Pattern to exclude
            "reason": str,                # Why it should be excluded
            "affected_files": int,        # Number of affected files
        },
        ...
    ],
    "threshold_issues": [str],            # Issues with coverage thresholds
    "scoping_issues": [                   # Issues with component/flag scoping
        {
            "component": str,             # Component or flag name
            "issue": str,                 # The issue found
            "suggestion": str,            # Suggested fix
        },
        ...
    ],
    "summary": str,                       # Summary of diagnosis findings
}
```

## Error Responses

The tool returns error responses for invalid inputs:

```python
{
    "error": str,           # Error message
    "error_code": str,      # Error code (INVALID_REPO_SLUG)
}
```

## Usage Examples

### Diagnose configuration for a repository

```python
result = diagnose_coverage_configuration(
    repo_slug="myorg/myapp",
    provider="codecov",
)
```

### Check configuration for a different provider

```python
result = diagnose_coverage_configuration(
    repo_slug="myorg/myapp",
    provider="coveralls",
)
```

## Output Interpretation

### Configuration Validity

The `config_valid` field indicates whether the configuration is syntactically correct:
- `true`: Configuration is valid and can be used
- `false`: Configuration has parsing errors that need to be fixed

### Over-Included Paths

Paths that are included in coverage configuration but have no actual coverage data:
- Indicates wasted resources
- Should be removed or have coverage data added
- Common causes: typos, outdated paths, unused directories

### Missing Exclusions

Common patterns that should be excluded but aren't:
- Test files (`**/test/**`, `**/tests/**`)
- Mock files (`**/mock/**`)
- Build artifacts (`**/dist/**`, `**/build/**`)
- Virtual environments (`**/.venv/**`)
- Node modules (`**/node_modules/**`)

### Threshold Issues

Problems with coverage thresholds:
- Too high (>95%): Unrealistic goals that discourage developers
- Too low (<50%): Insufficient quality standards
- Regression: Current coverage below minimum threshold

### Scoping Issues

Problems with component or flag definitions:
- Missing path definitions
- Overlapping path scopes
- Undefined thresholds
- Inconsistent naming

## Best Practices

1. **Regular audits**: Run this tool regularly to catch configuration issues
2. **Fix errors first**: Address parsing errors before other issues
3. **Review suggestions**: Carefully review all recommendations
4. **Test changes**: Test configuration changes in a branch first
5. **Document decisions**: Document why certain exclusions are made

## Common Issues and Solutions

### Over-Included Paths

**Issue**: Configuration includes paths with no coverage data

**Solution**:
```python
# Remove the path from configuration or add coverage data
# Before: include_paths = ["src/", "unused/"]
# After: include_paths = ["src/"]
```

### Missing Exclusions

**Issue**: Test files are included in coverage metrics

**Solution**:
```python
# Add exclusion patterns for test files
# Before: exclude_paths = []
# After: exclude_paths = ["**/test/**", "**/tests/**"]
```

### Unrealistic Thresholds

**Issue**: Thresholds set too high or too low

**Solution**:
```python
# Set realistic thresholds
# Before: thresholds = {"minimum": 99}
# After: thresholds = {"minimum": 80, "target": 85}
```

### Overlapping Components

**Issue**: Same code in multiple components

**Solution**:
```python
# Clarify component boundaries
# Before: api: ["src/api/"], utils: ["src/api/utils/"]
# After: api: ["src/api/"], utils: ["src/utils/"]
```

## Related Tools

- **find_low_coverage_files**: Find files with low coverage
- **recommend_test_plan**: Get test recommendations
- **identify_excludable_code_candidates**: Find code to exclude

## Error Handling

### Invalid Repository Slug

```python
result = diagnose_coverage_configuration(
    repo_slug="invalid",  # Missing owner/repo format
    provider="codecov",
)
# Returns: {"error": "Invalid repo_slug format: invalid. Expected 'owner/repo'", "error_code": "INVALID_REPO_SLUG"}
```

## Performance Considerations

- Configuration analysis is fast and doesn't require coverage data
- Can be run frequently without performance impact
- Results are cached by the provider

## See Also

- [MCP Tools Overview](./overview.md)
- [Configuration Diagnosis Architecture](../architecture/config-diagnosis.md)
- [Configuration Validation Guide](../guides/config-validation.md)
