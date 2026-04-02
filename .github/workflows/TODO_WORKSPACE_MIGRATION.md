# CI/CD Workspace Migration TODO

⚠️ **Action Required**: CI workflow paths need to be updated for workspace structure.

## Changes Needed

1. Update test paths from `test/` to `test-coverage-mcp/test/` and `test-coverage-mcp-codecov/test/`
2. Update source paths from `src/` to `test-coverage-mcp/src/` and `test-coverage-mcp-codecov/src/`
3. Update coverage report paths for workspace packages
4. Rename test directories from `unit/` to `unit_test/` and `integration/` to `integration_test/`
5. Add missing test directories: `e2e_test/`, `contract_test/`

## Workflows to Update

- `.github/workflows/ci.yaml`
- `.github/workflows/rw_build_and_test.yaml`
- `.github/workflows/rw_run_all_test_and_record.yaml`

See Phase 0.5 in the implementation plan for detailed migration steps.
