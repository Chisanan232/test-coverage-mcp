# Testing Guide

## Overview

This document describes the testing strategy and structure for test-coverage-mcp.

## Test Structure

```
test/
├── unit_test/          # Unit tests for individual components
│   ├── cli/            # CLI command tests
│   ├── domain/         # Domain model tests
│   ├── integrate/      # Integration module tests
│   ├── mcp/            # MCP server tests
│   ├── mcp_server/     # MCP tool tests
│   ├── models/         # Data model tests
│   ├── registry/       # Plugin registry tests
│   ├── services/       # Service layer tests
│   └── web_server/     # Web server tests
├── integration_test/   # Integration tests (future)
└── e2e_test/          # End-to-end tests (future)
```

## Running Tests

### All Tests
```bash
cd test-coverage-mcp
uv run pytest
```

### Specific Test File
```bash
uv run pytest test/unit_test/cli/test_cli_commands.py -v
```

### With Coverage Report
```bash
uv run pytest --cov=src/test_coverage_mcp --cov-report=html
```

### By Category
```bash
# Unit tests only
uv run pytest test/unit_test/ -v

# CLI tests
uv run pytest test/unit_test/cli/ -v

# Service tests
uv run pytest test/unit_test/services/ -v
```

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage target
- **Integration Tests**: All service interactions
- **E2E Tests**: All 11 MCP tools
- **Contract Tests**: Provider interface compliance

## Test Categories

### Unit Tests
- Individual function/method testing
- Mock external dependencies
- Fast execution
- High coverage target

### Integration Tests
- Service interaction testing
- Database/API integration
- Slower execution
- Real dependencies

### E2E Tests
- Full workflow testing
- All 11 MCP tools
- Real-world scenarios
- Slowest execution

### Contract Tests
- Provider interface compliance
- Version compatibility
- API contract validation

## Mocking Strategy

### External Dependencies
- Mock HTTP requests (httpx)
- Mock file system operations
- Mock provider APIs
- Mock environment variables

### Test Fixtures
- Reusable test data
- Common setup/teardown
- Parameterized tests

## Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<functionality>_<scenario>`

Example:
```python
class TestCoverageComparison:
    def test_compare_refs_with_valid_inputs(self):
        pass

    def test_compare_refs_with_invalid_repo(self):
        pass
```

## Continuous Integration

Tests run automatically on:
- Every push to any branch
- Pull requests
- Tags (release builds)

See `.github/workflows/ci-test.yaml` for details.

## Coverage Reports

Coverage reports are generated in:
- `htmlcov/index.html` - HTML report
- `.coverage` - Coverage data file

View HTML report:
```bash
open htmlcov/index.html
```

## Best Practices

1. **Write tests first** - TDD approach when possible
2. **Keep tests focused** - One assertion per test when possible
3. **Use descriptive names** - Test name should describe what's being tested
4. **Mock external calls** - Don't make real API calls in tests
5. **Use fixtures** - Share common test setup
6. **Test edge cases** - Include boundary conditions
7. **Keep tests fast** - Avoid unnecessary delays
8. **Maintain tests** - Update when code changes

## Common Issues

### Import Errors
```bash
# Ensure test-coverage-mcp is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Missing Dependencies
```bash
# Install test dependencies
uv sync
```

### Flaky Tests
- Avoid time-dependent tests
- Mock time-based functions
- Use deterministic test data

## Adding New Tests

1. Create test file in appropriate directory
2. Follow naming conventions
3. Use existing fixtures
4. Mock external dependencies
5. Run tests locally before committing
6. Ensure coverage doesn't decrease

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
