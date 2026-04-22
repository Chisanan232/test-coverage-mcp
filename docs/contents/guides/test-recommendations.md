# Test Recommendation Strategies

## Overview

The Test Recommendation Service generates intelligent test suggestions based on code analysis. It identifies coverage gaps and recommends specific test types, scenarios, and priorities to improve coverage efficiently.

## Recommendation Process

### 1. Gap Identification

Identifies uncovered regions in the codebase:

```python
uncovered_regions = [
    {
        "file_path": "src/processor.py",
        "start_line": 45,
        "end_line": 60,
        "region_type": "function",
        "risk_level": "high",
        "lines_count": 15,
    }
]
```

### 2. Test Type Suggestion

Recommends appropriate test types based on code region:

| Region Type | Suggested Test Types | Rationale |
|------------|----------------------|-----------|
| Function | Unit, Integration | Testable in isolation |
| Class | Unit, Integration | Multiple methods to test |
| Method | Unit, Integration | Part of public API |
| Block | Unit | Specific logic path |
| Branch | Unit | Conditional logic |
| Line | Unit | Specific statement |

### 3. Priority Ranking

Ranks gaps by importance using weighted scoring:

```
priority_score = (
    risk_level_score * 0.4 +      # 40% weight
    region_type_score * 0.3 +     # 30% weight
    lines_count_score * 0.3       # 30% weight
)
```

**Risk Level Weights**:
- Critical: 40 points
- High: 30 points
- Medium: 20 points
- Low: 10 points

**Region Type Weights**:
- Class: 30 points
- Function: 25 points
- Method: 25 points
- Block: 15 points
- Branch: 10 points
- Line: 5 points

### 4. Scenario Generation

Generates specific test scenarios for each gap:

#### Function Scenarios

```python
scenarios = [
    {
        "name": "test_function_happy_path",
        "description": "Test with valid inputs",
        "type": "happy_path",
    },
    {
        "name": "test_function_zero_input",
        "description": "Test with zero input",
        "type": "edge_case",
    },
    {
        "name": "test_function_negative_input",
        "description": "Test with negative input",
        "type": "edge_case",
    },
    {
        "name": "test_function_invalid_input",
        "description": "Test with invalid input",
        "type": "error_handling",
    },
]
```

#### Class Scenarios

```python
scenarios = [
    {
        "name": "test_class_initialization",
        "description": "Test class construction",
        "type": "initialization",
    },
    {
        "name": "test_class_state_transitions",
        "description": "Test state changes",
        "type": "state_transition",
    },
    {
        "name": "test_class_method_interactions",
        "description": "Test method interactions",
        "type": "method_interaction",
    },
]
```

### 5. Rationale Explanation

Provides clear explanation of why each test is important:

```
"This is a critical gap that could cause production issues.
The uncovered function is used by other components.
The gap spans 15 lines of code."
```

## Test Recommendation Types

### 1. Unit Tests

**When to use**: For individual functions and methods

**Example**:
```python
def test_calculate_total_valid_inputs():
    """Test calculate with valid inputs."""
    result = calculate(10, 20)
    assert result == 30

def test_calculate_zero_input():
    """Test calculate with zero input."""
    result = calculate(0, 10)
    assert result == 10

def test_calculate_negative_input():
    """Test calculate with negative input."""
    result = calculate(-5, 10)
    assert result == 5
```

### 2. Integration Tests

**When to use**: For classes and component interactions

**Example**:
```python
def test_processor_with_valid_data():
    """Test processor with valid data."""
    processor = DataProcessor()
    result = processor.process(valid_data)
    assert result.is_valid

def test_processor_with_invalid_data():
    """Test processor with invalid data."""
    processor = DataProcessor()
    result = processor.process(invalid_data)
    assert not result.is_valid
```

### 3. Edge Case Tests

**When to use**: For boundary conditions

**Example**:
```python
def test_parse_empty_string():
    """Test parsing empty string."""
    result = parse("")
    assert result == []

def test_parse_single_item():
    """Test parsing single item."""
    result = parse("item")
    assert result == ["item"]

def test_parse_max_items():
    """Test parsing maximum items."""
    items = ",".join([f"item{i}" for i in range(1000)])
    result = parse(items)
    assert len(result) == 1000
```

### 4. Error Handling Tests

**When to use**: For exception paths

**Example**:
```python
def test_divide_by_zero():
    """Test division by zero."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_input_type():
    """Test with invalid input type."""
    with pytest.raises(TypeError):
        process("not a number")
```

## Priority Levels

### Critical Priority

**Characteristics**:
- Risk score > 80
- Core functionality
- Used by multiple components
- Production impact

**Action**: Implement immediately

### High Priority

**Characteristics**:
- Risk score 60-80
- Important functionality
- Moderate impact
- Used by some components

**Action**: Implement soon

### Medium Priority

**Characteristics**:
- Risk score 40-60
- Moderate importance
- Limited impact
- Utility functions

**Action**: Implement when possible

### Low Priority

**Characteristics**:
- Risk score < 40
- Minor functionality
- Minimal impact
- Helper functions

**Action**: Implement as time permits

## Implementation Workflow

### Step 1: Get Recommendations

```python
from test_coverage_mcp.services.test_recommendation import TestRecommendationService

service = TestRecommendationService()
recommendations = service.recommend_tests(uncovered_regions, max_recommendations=10)
```

### Step 2: Sort by Priority

```python
sorted_recs = sorted(
    recommendations,
    key=lambda r: {"critical": 4, "high": 3, "medium": 2, "low": 1}[r.priority],
    reverse=True
)
```

### Step 3: Implement Tests

```python
for rec in sorted_recs:
    # Implement test for rec.file_path:rec.start_line-rec.end_line
    # Use rec.test_types and rec.scenarios as guidance
    # Follow rec.rationale for context
    pass
```

### Step 4: Verify Coverage

```python
# Run tests and verify coverage improvement
pytest --cov=src
```

## Best Practices

### 1. Follow Recommendations

Use the provided recommendations as a starting point:
- Test types guide which kind of tests to write
- Scenarios provide specific test cases
- Priority helps with scheduling

### 2. Add Context

Enhance recommendations with project-specific knowledge:
- Business logic requirements
- Performance constraints
- Integration dependencies

### 3. Test Quality

Focus on test quality, not just quantity:
- Clear test names
- Good assertions
- Proper setup/teardown
- Isolated tests

### 4. Iterative Improvement

Improve coverage incrementally:
- Start with critical gaps
- Move to high-priority gaps
- Address medium/low as time permits

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Test Recommendations

on: [pull_request]

jobs:
  recommendations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate Test Recommendations
        run: |
          python -c "
          from test_coverage_mcp.services.test_recommendation import TestRecommendationService

          service = TestRecommendationService()
          recommendations = service.recommend_tests(
              uncovered_regions,
              max_recommendations=5
          )

          for rec in recommendations:
              print(f'Priority: {rec.priority}')
              print(f'File: {rec.file_path}:{rec.start_line}-{rec.end_line}')
              print(f'Test Types: {rec.test_types}')
              print(f'Scenarios: {rec.scenarios}')
              print(f'Rationale: {rec.rationale}')
              print()
          "
```

## Common Patterns

### Pattern 1: Function with Multiple Paths

```python
def process_data(data):
    if not data:
        return None
    if isinstance(data, list):
        return [process_item(item) for item in data]
    else:
        return process_item(data)
```

**Recommended Tests**:
- Happy path: `process_data([1, 2, 3])`
- Edge case: `process_data([])`
- Edge case: `process_data(None)`
- Branch: `process_data(42)`

### Pattern 2: Class with State

```python
class StateMachine:
    def __init__(self):
        self.state = "initial"

    def transition(self, event):
        if self.state == "initial" and event == "start":
            self.state = "running"
        elif self.state == "running" and event == "stop":
            self.state = "stopped"
```

**Recommended Tests**:
- Initialization: `test_state_machine_init()`
- State transitions: `test_transition_start()`, `test_transition_stop()`
- Invalid transitions: `test_invalid_transition()`

### Pattern 3: Error Handling

```python
def parse_config(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {filename}")
    except json.JSONDecodeError:
        raise ConfigError(f"Invalid JSON in: {filename}")
```

**Recommended Tests**:
- Happy path: `test_parse_valid_config()`
- Error: `test_parse_missing_file()`
- Error: `test_parse_invalid_json()`

## Limitations

1. **Static Analysis**: Based on code structure, not runtime behavior
2. **Generic Scenarios**: May not cover all business logic
3. **No Business Context**: Doesn't understand domain-specific requirements
4. **Heuristic Based**: Scoring is approximate, not exact
5. **Manual Review**: Recommendations should be reviewed by developers

## Related Services

- **CoverageGapDiscoveryService**: Identifies coverage gaps
- **CoverageRiskAnalysisService**: Assesses overall risk
- **TestScenarioGenerator**: Generates detailed test scenarios

## See Also

- [Test Design Guide](../guides/test-design.md)
- [Coverage Gap Discovery](../architecture/gap-discovery.md)
- [Risk Analysis Methodology](../architecture/risk-analysis.md)
