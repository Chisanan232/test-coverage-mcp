# recommend_test_plan Tool

## Overview

The `recommend_test_plan` tool generates intelligent test recommendations based on coverage gaps. It analyzes uncovered code regions and provides prioritized test suggestions with specific scenarios and rationale.

This tool leverages the `TestRecommendationService` to provide actionable test recommendations that help teams improve coverage efficiently.

## Function Signature

```python
def recommend_test_plan(
    repo_slug: str,
    provider: str,
    target: str = "repo",
) -> Dict[str, Any]
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repo_slug` | `str` | Yes | - | Repository slug in format `owner/repo` |
| `provider` | `str` | Yes | - | Coverage provider name (e.g., `codecov`, `coveralls`) |
| `target` | `str` | No | `"repo"` | Analysis target: `repo`, `pr`, or file path (e.g., `src/main.py`) |

## Return Value

Returns a dictionary with the following structure:

```python
{
    "target": str,                        # The analysis target
    "total_gaps": int,                    # Total number of coverage gaps
    "recommendations": [                  # List of test recommendations
        {
            "file_path": str,             # Path to the file
            "start_line": int,            # Start line number
            "end_line": int,              # End line number
            "region_type": str,           # Type: function, class, method, block, branch, line
            "test_types": [str],          # Suggested test types: unit, integration, etc.
            "scenarios": [str],           # Test scenarios to implement
            "priority": str,              # Priority: critical, high, medium, low
            "rationale": str,             # Explanation of why this test is important
        },
        ...
    ],
    "summary": str,                       # Summary of test plan
}
```

## Error Responses

The tool returns error responses for invalid inputs:

```python
{
    "error": str,           # Error message
    "error_code": str,      # Error code (INVALID_REPO_SLUG, INVALID_TARGET)
}
```

## Usage Examples

### Get test recommendations for entire repository

```python
result = recommend_test_plan(
    repo_slug="myorg/myapp",
    provider="codecov",
    target="repo",
)
```

### Get test recommendations for a pull request

```python
result = recommend_test_plan(
    repo_slug="myorg/myapp",
    provider="codecov",
    target="pr",
)
```

### Get test recommendations for a specific file

```python
result = recommend_test_plan(
    repo_slug="myorg/myapp",
    provider="codecov",
    target="src/main.py",
)
```

## Output Interpretation

### Priority Levels

Recommendations are prioritized based on risk and impact:

- **Critical**: Risk score > 80, core functionality, production impact
- **High**: Risk score 60-80, important functionality, moderate impact
- **Medium**: Risk score 40-60, moderate importance, limited impact
- **Low**: Risk score < 40, minor functionality, minimal impact

### Test Types

Suggested test types based on code region:

- **Unit Tests**: For individual functions and methods
- **Integration Tests**: For classes and component interactions
- **Branch Coverage**: For conditional logic
- **Exception Handling**: For error paths
- **Performance Tests**: For performance-critical code

### Scenarios

Specific test scenarios to implement:

- **Happy Path**: Test with valid inputs and expected behavior
- **Edge Cases**: Test boundary conditions and limits
- **Error Handling**: Test error conditions and exceptions
- **State Transitions**: Test state changes and lifecycle
- **Performance**: Test with large inputs and constraints

## Best Practices

1. **Start with critical gaps**: Focus on critical and high-priority recommendations
2. **Follow test types**: Use suggested test types as guidance
3. **Implement scenarios**: Implement all suggested scenarios for comprehensive coverage
4. **Review rationale**: Understand why each test is important
5. **Iterate regularly**: Run this tool regularly to track progress

## Common Patterns

### Function with Multiple Paths

For functions with conditional logic:
- Test happy path with valid inputs
- Test edge cases (zero, negative, empty)
- Test error conditions
- Test boundary values

### Class with State

For stateful classes:
- Test initialization
- Test state transitions
- Test method interactions
- Test error recovery

### Error Handling

For functions that raise exceptions:
- Test normal operation
- Test each exception type
- Test error messages
- Test recovery behavior

## Related Tools

- **find_low_coverage_files**: Find files with low coverage
- **diagnose_coverage_configuration**: Analyze configuration issues
- **identify_excludable_code_candidates**: Find code to exclude

## Error Handling

### Invalid Repository Slug

```python
result = recommend_test_plan(
    repo_slug="invalid",  # Missing owner/repo format
    provider="codecov",
)
# Returns: {"error": "Invalid repo_slug format: invalid. Expected 'owner/repo'", "error_code": "INVALID_REPO_SLUG"}
```

### Invalid Target

```python
result = recommend_test_plan(
    repo_slug="owner/repo",
    provider="codecov",
    target="invalid_target",  # Not 'repo', 'pr', or a file path
)
# Returns: {"error": "Invalid target: invalid_target. Must be 'repo', 'pr', or a file path", "error_code": "INVALID_TARGET"}
```

## Performance Considerations

- Analysis is limited to top 10 recommendations by default
- Recommendations are pre-sorted by priority
- Results are cached by the provider

## See Also

- [MCP Tools Overview](./overview.md)
- [Test Recommendation Strategies](../guides/test-recommendations.md)
- [Test Design Guide](../guides/test-design.md)
