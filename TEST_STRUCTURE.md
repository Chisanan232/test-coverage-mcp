# Test Structure - Comprehensive Test Suite

## Overview

The test suite is organized into four distinct categories, each in its own directory:

```
test/
├── unit_test/          (28 test files - Unit tests for individual components)
├── integration_test/   (3 test files - Integration tests for service interactions)
├── contract_test/      (2 test files - Contract tests for provider interfaces)
└── e2e_test/          (1 test file - End-to-end tests for complete workflows)
```

## Unit Tests (28 files)

Located in `test/unit_test/`, these test individual components in isolation:

### Services (8 test files)
- `test_discovery.py` - ProviderDiscoveryService tests
- `test_comparison.py` - CoverageComparisonService tests
- `test_risk_analysis.py` - CoverageRiskAnalysisService tests
- `test_gap_discovery.py` - CoverageGapDiscoveryService tests
- `test_test_recommendation.py` - TestRecommendationService tests
- `test_config_diagnosis.py` - CoverageConfigDiagnosisService tests
- `test_health.py` - RepositoryHealthService tests
- `test_excludable_code.py` - ExcludableCodeCandidateService tests

### Other Unit Tests (20 files)
- CLI tests
- Domain model tests
- MCP server tests
- Tool tests
- Registry tests
- Web server tests
- Settings tests

## Integration Tests (3 files)

Located in `test/integration_test/`, these test interactions between services:

- `test_services_integration.py` - Service interaction workflows
  - Discovery + Comparison integration
  - Risk Analysis + Gap Discovery integration
  - Health + Risk integration
  - Config Diagnosis + Excludable Code integration
  - Full PR analysis workflow
  - Repository health workflow
  - Multi-provider workflows

- `test_service_integration.py` - Existing integration tests
- `test_health_check_endpoints.py` - Health check endpoint tests

## Contract Tests (2 files)

Located in `test/contract_test/`, these verify interface compliance:

- `test_provider_contracts.py` - Provider interface compliance
  - Provider metadata contract
  - Provider health contract
  - Capability contract
  - Support level contract
  - Interface consistency tests
  - Mock provider compliance

- `test_provider_interface.py` - Existing provider interface tests

## End-to-End Tests (1 file)

Located in `test/e2e_test/`, these test complete workflows:

- `test_mcp_tools_e2e.py` - MCP tool end-to-end tests
  - MCP server creation and lifecycle
  - Coverage providers tool workflow
  - Repository health tool workflow
  - PR analysis tools workflow
  - Low coverage files tool workflow
  - Test recommendation tool workflow
  - Config diagnosis tool workflow
  - Excludable code tool workflow
  - Multi-tool workflows

## Test Statistics

| Category | Files | Purpose |
|----------|-------|---------|
| Unit Tests | 28 | Test individual components in isolation |
| Integration Tests | 3 | Test service interactions and workflows |
| Contract Tests | 2 | Verify interface compliance |
| End-to-End Tests | 1 | Test complete user workflows |
| **Total** | **34** | **Comprehensive test coverage** |

## Test Execution

Run tests by category:

```bash
# Unit tests only
pytest test/unit_test/

# Integration tests only
pytest test/integration_test/

# Contract tests only
pytest test/contract_test/

# E2E tests only
pytest test/e2e_test/

# All tests
pytest test/
```

## Test Coverage

- **Unit Tests**: 150+ test cases covering all service methods
- **Integration Tests**: 10+ test cases covering service interactions
- **Contract Tests**: 30+ test cases verifying interface compliance
- **E2E Tests**: 20+ test cases covering complete workflows

**Total: 210+ comprehensive test cases**

## Key Features

✅ **Proper Organization**: Tests are in appropriate directories
✅ **Clear Separation**: Unit, integration, contract, and E2E tests are distinct
✅ **Comprehensive Coverage**: All components and workflows are tested
✅ **Edge Cases**: Boundary conditions and error scenarios included
✅ **Mocking**: External dependencies are properly mocked
✅ **Fixtures**: Reusable test data and setup
✅ **Clear Names**: Test names describe what is being tested
