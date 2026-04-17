# CI/CD Monorepo Migration Plan
## test-coverage-mcp Project

**Date**: April 7, 2026
**Version**: 1.2 (3 Orchestrator Design - Based on User Requirements)
**Status**: Planning - Awaiting Final Review
**Dependencies**: Phase 0.5 & Phase 1.5 from implementation-plan.md

---

## 🔄 Updates from User Feedback

### Key Changes Made (Version 1.2) 🆕

**User Requirements**:
1. Must have 3 release types with specific triggers
2. Keep important settings (permissions, concurrency)
3. Remove redundant workflows instead of just deprecating

**Major Changes**:

1. **3 Release Orchestrators** ✅
   - **Validation**: `release-validate-monorepo.yml` (auto + manual)
   - **Staging**: `release-staging-monorepo.yml` (manual only)
   - **Production**: `release-monorepo.yml` (auto + manual)

2. **Trigger Conditions** ✅
   - Validation auto-triggers on PR with code changes affecting releases
   - Staging is manual-only (no auto-trigger)
   - Production auto-triggers on `.github/tag_and_release/release-**` file changes

3. **Important Settings Preserved** ✅
   - Permissions (`contents: write`, `packages: write`, `id-token: write`)
   - Concurrency control per workflow type
   - Manual inputs for package selection, level, python, docker, docs

4. **Cleanup Strategy Changed** ✨
   - **Was**: Update and deprecate old workflows
   - **Now**: Remove old workflows after new ones validated (Phase 5)
   - **Removed**: 6 files total
     - CI: `ci.yaml`, `rw_build_and_test.yaml`, `rw_run_all_test_and_record.yaml`
     - Release: `release.yml`, `release-staging.yml`, `release-validate.yml`
   - **Benefit**: Cleaner codebase, no confusion about which workflow to use

5. **Simplified Architecture** ✅
   - Removed local orchestration layers
   - Direct calls to upstream reusable workflows
   - Fewer files to maintain (15+ → ~10 workflows)

---

### Key Changes Made (Version 1.1)

1. **Release System Redesign** ✨
   - **User Concern**: "One workflow per package is hard to maintain"
   - **Solution**: Added **orchestrator pattern** as primary approach
   - **Result**: Single `release-monorepo.yml` handles all packages
   - **Benefit**: Add new packages by updating `intent.yaml` only (no new workflow files)

2. **CI Testing Approach Clarified** 📝
   - **User Choice**: Option B (Per-Package Matrix) ✅
   - **Clarification**: Use **upstream reusable workflows** (don't modify them)
   - **Implementation**: New `ci-monorepo.yaml` calls upstream workflows with `project_name`

3. **Legacy Workflow Strategy** 🔄
   - **User Choice**: Option A (Backward compatibility) ✅
   - **Approach**: Keep existing workflows, only fix placeholders
   - **Benefit**: Gradual migration with fallback options

### Recommended Workflow Structure (Final)

**After Migration Complete**:
```
.github/workflows/
# NEW CI Workflows
├── ci-monorepo.yaml                    # ✨ Per-package matrix CI
├── ci_includes_e2e_test.yaml           # 🔧 Updated for monorepo

# NEW Release Orchestrators (3 types)
├── release-validate-monorepo.yml       # ✨ Validation orchestrator
├── release-staging-monorepo.yml        # ✨ Staging orchestrator
├── release-monorepo.yml                # ✨ Production orchestrator

# Supporting Workflows (updated as needed)
├── docker-ci.yml                       # 🔧 Updated for monorepo (if needed)
├── documentation.yaml                  # 🔧 Updated for monorepo
├── type-check.yml                      # 🔧 Updated for monorepo
└── ... (other supporting workflows)
```

**Files REMOVED** (cleaned up in Phase 5):
```
OLD CI Workflows:
❌ ci.yaml                              # Replaced by ci-monorepo.yaml
❌ rw_build_and_test.yaml               # Local orchestration no longer needed
❌ rw_run_all_test_and_record.yaml      # Local orchestration no longer needed

OLD Release Workflows:
❌ release.yml                          # Replaced by release-monorepo.yml
❌ release-staging.yml                  # Replaced by release-staging-monorepo.yml
❌ release-validate.yml                 # Replaced by release-validate-monorepo.yml
```

**Net Result**:
- **Before**: 15+ workflow files (single-project + placeholders)
- **After**: ~10 workflow files (4 new + 6 updated + supporting)
- **Removed**: 6 redundant workflow files
- **Simplified**: Direct upstream workflow calls, no local orchestration layers

---

## 📋 Executive Summary

### Current State

**Project Structure**: UV Workspace Monorepo with 2 packages
- `test-coverage-mcp/` - Core MCP server package
- `test-coverage-mcp-codecov/` - Codecov provider plugin

**CI/CD Status**:
- ❌ Workflows configured for single-project structure
- ❌ Placeholder variables not replaced (`<your_base_branch>`, `<your_package_name>`)
- ❌ Test paths point to old structure (`test/` instead of `test-coverage-mcp/test/`)
- ❌ No monorepo-aware release workflows
- ❌ Single `intent.yaml` without package-specific configuration

### Target State

**CI/CD Goals**:
- ✅ Monorepo-aware CI workflows with per-package testing
- ✅ Per-package release workflows with independent versioning
- ✅ Tag prefixes for package identification (`core/v1.0.0`, `codecov/v0.1.0`)
- ✅ Smart change detection (only test/release changed packages)
- ✅ Updated `intent.yaml` with monorepo package definitions
- ✅ All placeholder variables replaced

---

## 🎯 Migration Scope

### Workflows Requiring Updates

#### **Category 1: CI/CD Testing** (High Priority)
1. `.github/workflows/ci.yaml` - Main CI workflow
2. `.github/workflows/ci_includes_e2e_test.yaml` - E2E test CI
3. `.github/workflows/rw_build_and_test.yaml` - Reusable build/test
4. `.github/workflows/rw_run_all_test_and_record.yaml` - Test orchestrator

#### **Category 2: Release Workflows** (High Priority)
5. `.github/workflows/release.yml` - Production release
6. `.github/workflows/release-staging.yml` - Staging release
7. `.github/workflows/release-validate.yml` - Release validation

#### **Category 3: Supporting Workflows** (Medium Priority)
8. `.github/workflows/docker-ci.yml` - Docker build CI
9. `.github/workflows/documentation.yaml` - Docs build
10. `.github/workflows/type-check.yml` - Type checking

#### **Category 4: Configuration Files** (High Priority)
11. `.github/tag_and_release/intent.yaml` - Release configuration
12. `.github/workflows/TODO_WORKSPACE_MIGRATION.md` - Remove after migration
13. `.github/workflows/REUSABLE_WORKFLOWS.md` - Update documentation

---

## 🗂️ Detailed Migration Plan

### Phase 1: Configuration Foundation (1-2 hours)

**Goal**: Update `intent.yaml` and prepare base configuration

#### Task 1.1: Backup and Transform intent.yaml

**Current Configuration**:
```yaml
# Single-project configuration
project:
  name: ~                    # Unset
  package_name: ~            # Unset
  base_branch: master        # ✓ Correct

release: true
level: patch
artifacts:
  python: auto
  docker: auto
  docs:
    mode: auto
    sections: ["docs", "dev"]
    strategy: always
```

**New Monorepo Configuration**:
```yaml
# Monorepo Multi-Package Configuration
packages:
  # Core MCP Server Package
  - name: core
    package_name: test-coverage-mcp
    working_directory: test-coverage-mcp
    tag_prefix: core/

    release: true
    level: auto

    artifacts:
      python: auto
      docker: skip                # Core has no Dockerfile yet
      docs:
        mode: auto
        sections: ["docs"]
        strategy: changed

    python:
      auth_method: token

    validation:
      version: "1.0.0-validation"
      test_version: "validation-test"

  # Codecov Provider Plugin Package
  - name: codecov
    package_name: test-coverage-mcp-codecov
    working_directory: test-coverage-mcp-codecov
    tag_prefix: codecov/

    release: true
    level: auto

    artifacts:
      python: auto
      docker: skip
      docs: skip                  # Uses core's docs

    python:
      auth_method: token

    validation:
      version: "0.1.0-validation"
      test_version: "validation-test"

# Global project settings
project:
  name: test-coverage-mcp
  base_branch: master

# Git configuration
git:
  commit:
    name: "GitHub Actions Bot"
    email: "actions@github.com"

# Documentation configuration
docs:
  paths:
    ci_cd: "docs/CI_CD.md"
    installation: "docs/INSTALLATION.md"
    readme: "README.md"
  preview:
    branch: "docs-preview"

notes: "Monorepo release with independent package versioning"
```

**Implementation Steps**:
1. Backup current `intent.yaml`:
   ```bash
   cp .github/tag_and_release/intent.yaml .github/tag_and_release/intent.yaml.backup
   ```

2. Replace `intent.yaml` with monorepo configuration

3. Validate YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('.github/tag_and_release/intent.yaml'))"
   ```

4. Verify against schema (if available):
   ```bash
   # Check if .github/tag_and_release/schema.json exists and validates
   ```

**Validation Checklist**:
- [ ] YAML syntax valid
- [ ] Both packages defined with all required fields
- [ ] Tag prefixes set correctly (`core/`, `codecov/`)
- [ ] Working directories point to correct package folders
- [ ] Global project settings preserved

---

#### Task 1.2: Update Documentation About New Structure

**Files to update**:
1. `.github/workflows/REUSABLE_WORKFLOWS.md`
   - Add monorepo workflow examples
   - Document `package-name` parameter usage
   - Show how to trigger per-package releases

**Git Commit**:
```bash
🔧 config: Transform intent.yaml to monorepo multi-package format
📝 docs: Update REUSABLE_WORKFLOWS.md with monorepo examples
```

---

### Phase 2: CI Testing Workflows Migration (3-4 hours)

**Goal**: Update CI workflows to support monorepo with per-package testing

**Decision**: ✅ **Option B Selected** - Per-Package Matrix approach with upstream reusable workflows

**Clarification on Workflow Architecture**:

This project uses a **two-tier workflow system**:

1. **Local Workflows** (`.github/workflows/*.yaml` in this repo):
   - Trigger workflows (define when to run)
   - Orchestration workflows (coordinate multiple steps)
   - Call upstream reusable workflows

2. **Upstream Reusable Workflows** (from `Chisanan232/GitHub-Action_Reusable_Workflows-Python`):
   - Actual test execution (`rw_uv_run_test.yaml`)
   - Coverage organization (`rw_organize_test_cov_reports.yaml`)
   - Coverage upload (`rw_upload_test_cov_report.yaml`)
   - Release workflows (`rw_release_complete.yaml`)

**Phase 2 Strategy**:
- ✅ Create **NEW** local workflow `ci-monorepo.yaml` that calls upstream reusable workflows
- ✅ Keep and update **existing** local workflows for backward compatibility
- ❌ Do NOT modify upstream reusable workflows (they already support monorepo via `project_name`)
- ❌ Do NOT redesign local legacy workflows (just fix placeholders)

This approach keeps the centralized upstream workflow management while adding monorepo-specific orchestration locally.

#### Task 2.1: Deprecate Old CI Workflow

**File**: `.github/workflows/ci.yaml`

**Status**: ⚠️ **DEPRECATED** - Will be removed in favor of `ci-monorepo.yaml`

**Rationale**:
- User selected **Option B: Per-Package Matrix** approach
- New `ci-monorepo.yaml` directly calls upstream reusable workflows
- Old `ci.yaml` → `rw_run_all_test_and_record.yaml` → `rw_build_and_test.yaml` chain is redundant
- Removes unnecessary local orchestration layers

**Migration Strategy**:
1. **Phase 2**: Create new `ci-monorepo.yaml` (Task 2.2)
2. **Phase 2**: Test new workflow with PRs
3. **Phase 5**: Remove `ci.yaml` after new workflow validated

**No updates needed** - This file will be deleted, not updated

---

#### Task 2.2: Create New Monorepo CI Workflow

**File**: `.github/workflows/ci-monorepo.yaml` (NEW)

**Implementation**:
```yaml
name: CI - Monorepo

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  # Step 1: Detect which packages changed
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      core: ${{ steps.changes.outputs.core }}
      codecov: ${{ steps.changes.outputs.codecov }}
    steps:
      - uses: actions/checkout@v6
      - uses: dorny/paths-filter@v3
        id: changes
        with:
          filters: |
            core:
              - 'test-coverage-mcp/**'
              - 'pyproject.toml'
              - 'uv.lock'
            codecov:
              - 'test-coverage-mcp-codecov/**'
              - 'pyproject.toml'
              - 'uv.lock'

  # Step 2: Test core package
  test-core-unit:
    needs: detect-changes
    if: needs.detect-changes.outputs.core == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@master
    with:
      test_type: 'unit-test'
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'
      test_folder: './test/unit_test'
      all_test_items_paths: '["./test/unit_test"]'
      python-versions: '["3.12", "3.13", "3.14"]'
      operating-systems: '["ubuntu-latest", "macos-latest"]'

  test-core-integration:
    needs: detect-changes
    if: needs.detect-changes.outputs.core == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@master
    with:
      test_type: 'integration-test'
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'
      test_folder: './test/integration_test'
      all_test_items_paths: '["./test/integration_test"]'
      python-versions: '["3.12", "3.13", "3.14"]'
      operating-systems: '["ubuntu-latest", "macos-latest"]'

  # Step 3: Test codecov package
  test-codecov-unit:
    needs: detect-changes
    if: needs.detect-changes.outputs.codecov == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@master
    with:
      test_type: 'unit-test'
      project_name: 'codecov'
      test_working_directory: './test-coverage-mcp-codecov'
      test_folder: './test/unit_test'
      all_test_items_paths: '["./test/unit_test"]'
      python-versions: '["3.12", "3.13", "3.14"]'
      operating-systems: '["ubuntu-latest", "macos-latest"]'

  test-codecov-integration:
    needs: detect-changes
    if: needs.detect-changes.outputs.codecov == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@master
    with:
      test_type: 'integration-test'
      project_name: 'codecov'
      test_working_directory: './test-coverage-mcp-codecov'
      test_folder: './test/integration_test'
      all_test_items_paths: '["./test/integration_test"]'
      python-versions: '["3.12", "3.13", "3.14"]'
      operating-systems: '["ubuntu-latest", "macos-latest"]'

  # Step 4: Organize coverage (per package, per test type)
  organize-coverage-core:
    needs: [test-core-unit, test-core-integration]
    if: always() && needs.detect-changes.outputs.core == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_organize_test_cov_reports.yaml@master
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'

  organize-coverage-codecov:
    needs: [test-codecov-unit, test-codecov-integration]
    if: always() && needs.detect-changes.outputs.codecov == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_organize_test_cov_reports.yaml@master
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'codecov'
      test_working_directory: './test-coverage-mcp-codecov'

  # Step 5: Upload coverage to Codecov
  upload-coverage-core:
    needs: organize-coverage-core
    if: always() && needs.detect-changes.outputs.core == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_upload_test_cov_report.yaml@master
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'
      upload-to-codecov: true
      codecov_flags: 'core,${{ matrix.test_type }}'
      codecov_name: 'test-coverage-mcp-core-${{ matrix.test_type }}'
    secrets:
      codecov_token: ${{ secrets.CODECOV_TOKEN }}

  upload-coverage-codecov:
    needs: organize-coverage-codecov
    if: always() && needs.detect-changes.outputs.codecov == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_upload_test_cov_report.yaml@master
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'codecov'
      test_working_directory: './test-coverage-mcp-codecov'
      upload-to-codecov: true
      codecov_flags: 'codecov,${{ matrix.test_type }}'
      codecov_name: 'test-coverage-mcp-codecov-${{ matrix.test_type }}'
    secrets:
      codecov_token: ${{ secrets.CODECOV_TOKEN }}

  # Step 6: SonarQube scan (uses multi-module config from Phase 1.5)
  sonarqube:
    needs: [upload-coverage-core, upload-coverage-codecov]
    if: always()
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_sonarqube_scan.yaml@master
    secrets:
      sonar_token: ${{ secrets.SONAR_TOKEN }}
```

**Benefits**:
- ✅ Only tests packages that changed
- ✅ Parallel execution per package
- ✅ Per-package coverage with flags (`core,unit-test`, `codecov,integration-test`)
- ✅ Clear failure isolation
- ✅ Artifact naming: `coverage_core_unit-test_ubuntu-latest_3.12`

---

#### Task 2.3: Mark Local Reusable Workflows for Removal

**Decision**: ✅ **REMOVE** - No longer needed with new `ci-monorepo.yaml`

**Files to remove**:
1. `.github/workflows/rw_build_and_test.yaml`
2. `.github/workflows/rw_run_all_test_and_record.yaml`

**Rationale**:
- These are **local orchestration** workflows (not upstream reusable workflows)
- They exist to coordinate calls between `ci.yaml` and upstream workflows
- With `ci-monorepo.yaml` directly calling upstream workflows, this layer is redundant
- Simplifies workflow architecture (fewer files to maintain)

**Current Architecture** (being replaced):
```
ci.yaml
  → rw_run_all_test_and_record.yaml (local)
    → rw_build_and_test.yaml (local)
      → rw_uv_run_test.yaml (upstream - Chisanan232 repo)
      → rw_organize_test_cov_reports.yaml (upstream)
      → rw_upload_test_cov_report.yaml (upstream)
```

**New Architecture** (simpler):
```
ci-monorepo.yaml
  → rw_uv_run_test.yaml (upstream - Chisanan232 repo)
  → rw_organize_test_cov_reports.yaml (upstream)
  → rw_upload_test_cov_report.yaml (upstream)
```

**Migration Strategy**:
1. **Phase 2**: Create new `ci-monorepo.yaml`
2. **Phase 2**: Test new workflow (old workflows still available as fallback)
3. **Phase 5**: Remove both local workflows after validation

**Important**: We are NOT removing **upstream** reusable workflows - only local orchestration layers that are now unnecessary.

**No updates needed** - These files will be deleted, not updated

---

#### Task 2.4: Update E2E Test Workflow

**File**: `.github/workflows/ci_includes_e2e_test.yaml`

**Changes**:
1. Replace `<your_base_branch>` → `master`
2. Update path triggers for monorepo
3. Add `project_name` parameter when calling reusable workflows

---

**Git Commits** (Phase 2):
```bash
✨ ci: Create ci-monorepo.yaml with per-package testing
✨ ci: Add change detection for conditional package testing
🔧 ci: Update ci_includes_e2e_test.yaml for monorepo
📝 ci: Add deprecation notice to ci.yaml (will be removed)
```

**Later in Phase 5** (after new workflow validated):
```bash
🗑️ ci: Remove deprecated ci.yaml
🗑️ ci: Remove local orchestration workflows (rw_build_and_test, rw_run_all_test_and_record)
```

---

### Phase 3: Release Workflows Migration (3-4 hours)

**Goal**: Create release workflows with independent package versioning

#### Release System Design Analysis

**User Requirements**:
1. ✅ Must have 3 release types: Validation, Staging, Production
2. ✅ Each must support manual trigger with package selection
3. ✅ Validation: Auto-trigger on code changes + manual
4. ✅ Staging: Manual trigger only
5. ✅ Production: Auto-trigger on release files + manual
6. ✅ Must be maintainable (orchestrator pattern, not per-package files)
7. ✅ Keep important settings (permissions, concurrency)

**Design Solution**: 3 orchestrator workflows covering all release scenarios

**Two Approaches Analyzed**:

##### **Approach A: Individual Workflows Per Package** (Current Plan)
```
.github/workflows/
├── release-core.yml           # Manual trigger for core
├── release-codecov.yml        # Manual trigger for codecov
├── release-staging-core.yml
└── release-staging-codecov.yml
```

**Pros**:
- ✅ Simple, clear separation of concerns
- ✅ Easy to trigger specific package release manually
- ✅ Easy to debug (know which workflow = which package)
- ✅ Different release schedules/triggers per package
- ✅ Good for starting with monorepo

**Cons**:
- ❌ More files to maintain (2n files for n packages)
- ❌ Workflow duplication
- ❌ Need to create new file for each new package
- ❌ **User's concern**: Hard to manage with many packages

##### **Approach B: Orchestrator Pattern** (Matrix-Style)
```
.github/workflows/
├── release-monorepo.yml       # One workflow, auto-detects packages
└── release-staging-monorepo.yml
```

**Pros**:
- ✅ **Single workflow to maintain**
- ✅ **Easy to add new packages** (just update intent.yaml)
- ✅ Consistent release process across all packages
- ✅ Can release multiple packages in one trigger
- ✅ Auto-detects which packages changed
- ✅ Supports both sequential and parallel releases

**Cons**:
- ❌ More complex workflow logic
- ❌ Cannot easily trigger single package release (need input selection)
- ❌ Harder to debug (need to trace which package in matrix failed)
- ❌ Requires orchestrator workflow support (available in reusable workflows)

#### **Selected Approach: 3 Orchestrator Workflows** ✅

Based on user requirements, implement **3 orchestrator workflows** (one per release type):

```
.github/workflows/
├── release-validate-monorepo.yml    # Validation (auto + manual)
├── release-staging-monorepo.yml     # Staging (manual only)
└── release-monorepo.yml             # Production (auto + manual)
```

**Benefits**:
- ✅ **3 release types** as required (validation, staging, production)
- ✅ **Single file per type** - add packages by updating `intent.yaml` only
- ✅ **Flexible triggers** - auto and/or manual per requirements
- ✅ **Package selection** - manual triggers accept package input
- ✅ **Consistent behavior** - all packages follow same process
- ✅ **Maintainable** - no per-package workflow proliferation

**No individual per-package workflows needed** - orchestrators handle all cases.

**Migration Path**:
- **Task 3.1**: Create validation orchestrator
- **Task 3.2**: Create staging orchestrator
- **Task 3.3**: Create production orchestrator
- **Task 3.4**: Deprecate legacy release workflows

This satisfies all user requirements while maintaining scalability.

---

#### Task 3.1: Create Release Validation Orchestrator

**File**: `.github/workflows/release-validate-monorepo.yml` (NEW)

**Purpose**: Validate release process (dry-run) for all packages

**Triggers**:
- ✅ **Auto**: On PR to `master` with changes to release-affecting files
- ✅ **Manual**: `workflow_dispatch` with package selection

**Implementation**:
```yaml
name: Release Validation - Monorepo

on:
  # Auto-trigger: On PR to master with release-affecting changes
  pull_request:
    branches:
      - master
    paths:
      - 'test-coverage-mcp/**'
      - 'test-coverage-mcp-codecov/**'
      - '.github/tag_and_release/**'
      - '.github/workflows/release-*.yml'
      - 'pyproject.toml'
      - 'uv.lock'

  # Manual trigger: With package selection and level
  workflow_dispatch:
    inputs:
      packages:
        description: 'Packages to validate (JSON array, e.g., ["core", "codecov"]). Leave empty for auto-detect.'
        required: false
        default: '[]'
        type: string
      level:
        description: 'Release level to test'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - patch
          - minor
          - major
      python:
        description: 'Python package release'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip
      docker:
        description: 'Docker image release'
        required: false
        default: 'skip'
        type: choice
        options:
          - auto
          - force
          - skip
      docs:
        description: 'Documentation versioning'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip

permissions:
  contents: read      # Validation doesn't write
  packages: read
  id-token: write     # For OIDC if needed

concurrency:
  group: release-validate-${{ github.ref }}
  cancel-in-progress: true  # Can cancel validation if new changes

jobs:
  validate-releases:
    name: Validate Release Process
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_monorepo_release_orchestrator.yaml@master
    with:
      packages: ${{ inputs.packages || '[]' }}
      level: ${{ inputs.level || 'auto' }}
      python: ${{ inputs.python || 'auto' }}
      docker: ${{ inputs.docker || 'skip' }}
      docs: ${{ inputs.docs || 'auto' }}
      dry-run: true              # Always dry-run for validation
      release-mode: 'sequential'
    secrets: inherit

  validation-summary:
    name: Validation Summary
    runs-on: ubuntu-latest
    needs: validate-releases
    if: always()
    steps:
      - name: Report validation results
        run: |
          echo "=== Release Validation Summary ==="
          echo ""
          echo "Validation Status: ${{ needs.validate-releases.result }}"
          echo "Packages Validated: ${{ needs.validate-releases.outputs.packages_validated }}"
          echo ""

          if [[ "${{ needs.validate-releases.result }}" == "success" ]]; then
            echo "✅ Release validation passed!"
            echo ""
            echo "📦 Validated Packages:"
            echo "${{ needs.validate-releases.outputs.validation_details }}"
            echo ""
            echo "Ready for staging or production release."
          else
            echo "❌ Release validation failed. Fix issues before releasing."
            exit 1
          fi
```

**Behavior**:
- **Auto-trigger**: When PR modifies package code or release configs
- **Manual trigger**: Select which packages to validate
- **Always dry-run**: Never actually releases, only validates
- **Checks**: Build, test, version bump validation (no commits/tags)

---

#### Task 3.2: Create Staging Release Orchestrator

**File**: `.github/workflows/release-staging-monorepo.yml` (NEW)

**Purpose**: Pre-production release to TestPyPI for all packages

**Triggers**:
- ✅ **Manual only**: `workflow_dispatch` with package selection
- ❌ **No auto-trigger**: Staging is always intentional

**Implementation**:
```yaml
name: Staging Release - Monorepo

on:
  # Manual trigger only - staging is always intentional
  workflow_dispatch:
    inputs:
      packages:
        description: 'Packages to release (JSON array, e.g., ["core", "codecov"]). Leave empty for all packages.'
        required: false
        default: '[]'
        type: string
      level:
        description: 'Release level'
        required: false
        default: 'patch'
        type: choice
        options:
          - patch
          - minor
          - major
      python:
        description: 'Python package release'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip
      docker:
        description: 'Docker image release'
        required: false
        default: 'skip'
        type: choice
        options:
          - auto
          - force
          - skip
      docs:
        description: 'Documentation versioning'
        required: false
        default: 'skip'
        type: choice
        options:
          - auto
          - force
          - skip

permissions:
  contents: write      # Create RC tags
  packages: write      # Push to registries
  id-token: write      # OIDC for TestPyPI

concurrency:
  group: release-staging-${{ github.ref_name }}
  cancel-in-progress: false  # Don't cancel staging releases

jobs:
  staging-releases:
    name: Orchestrate Staging Releases
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_monorepo_release_orchestrator.yaml@master
    with:
      packages: ${{ inputs.packages }}
      level: ${{ inputs.level }}
      python: ${{ inputs.python }}
      docker: ${{ inputs.docker }}
      docs: ${{ inputs.docs }}
      staging: true              # Staging mode: TestPyPI, RC tags
      release-mode: 'sequential'
    secrets: inherit

  staging-summary:
    name: Staging Release Summary
    runs-on: ubuntu-latest
    needs: staging-releases
    if: always()
    steps:
      - name: Report staging results
        run: |
          echo "=== Staging Release Summary ==="
          echo ""
          echo "Staging Status: ${{ needs.staging-releases.result }}"
          echo "Packages Released: ${{ needs.staging-releases.outputs.packages_released }}"
          echo ""

          if [[ "${{ needs.staging-releases.result }}" == "success" ]]; then
            echo "🎭 Staging release completed successfully!"
            echo ""
            echo "📦 Released to TestPyPI:"
            echo "${{ needs.staging-releases.outputs.release_details }}"
            echo ""
            echo "🏷️ RC Tags Created:"
            echo "${{ needs.staging-releases.outputs.rc_tags }}"
            echo ""
            echo "✅ Ready for production release after validation."
          else
            echo "❌ Staging release failed. Check logs above."
            exit 1
          fi
```

**Behavior**:
- **Manual only**: Must be triggered manually (no auto)
- **TestPyPI**: Publishes to TestPyPI for testing
- **RC tags**: Creates release candidate tags (e.g., `core/v1.0.0-rc.1`)
- **Test installations**: Can test packages before production release

---

#### Task 3.3: Create Production Release Orchestrator

**File**: `.github/workflows/release-monorepo.yml` (NEW)

**Purpose**: Production release to PyPI for all packages

**Triggers**:
- ✅ **Auto**: On push to `master` with changes to `.github/tag_and_release/release-**`
- ✅ **Manual**: `workflow_dispatch` with package selection

**Implementation**:
```yaml
name: Production Release - Monorepo

on:
  # Auto-trigger: On release file changes in master
  push:
    branches:
      - master
    paths:
      - .github/tag_and_release/release-**

  # Manual trigger: With package selection and options
  workflow_dispatch:
    inputs:
      packages:
        description: 'Packages to release (JSON array, e.g., ["core", "codecov"]). Leave empty for auto-detect.'
        required: false
        default: '[]'
        type: string
      level:
        description: 'Release level'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - patch
          - minor
          - major
      python:
        description: 'Python package release'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip
      docker:
        description: 'Docker image release'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip
      docs:
        description: 'Documentation versioning'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - force
          - skip

permissions:
  contents: write      # Create tags and GitHub releases
  packages: write      # Push to GHCR
  id-token: write      # OIDC for PyPI

concurrency:
  group: release-${{ github.ref_name }}
  cancel-in-progress: false  # Never cancel production releases

jobs:
  production-releases:
    name: Orchestrate Production Releases
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_monorepo_release_orchestrator.yaml@master
    with:
      packages: ${{ inputs.packages || '[]' }}
      level: ${{ inputs.level || 'auto' }}
      python: ${{ inputs.python || 'auto' }}
      docker: ${{ inputs.docker || 'auto' }}
      docs: ${{ inputs.docs || 'auto' }}
      staging: false             # Production mode: PyPI, version tags
      release-mode: 'sequential'
    secrets:
      DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      TEST_PYPI_API_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}

  production-summary:
    name: Production Release Summary
    runs-on: ubuntu-latest
    needs: production-releases
    if: always()
    steps:
      - name: Report production results
        run: |
          echo "=== Production Release Summary ==="
          echo ""
          echo "Release Status: ${{ needs.production-releases.result }}"
          echo "Packages Released: ${{ needs.production-releases.outputs.packages_released }}"
          echo ""

          if [[ "${{ needs.production-releases.result }}" == "success" && "${{ needs.production-releases.outputs.release_performed }}" == "true" ]]; then
            echo "🎉 Production release completed successfully!"
            echo ""
            echo "📦 Released to PyPI:"
            echo "${{ needs.production-releases.outputs.release_details }}"
            echo ""
            echo "🏷️ Version Tags Created:"
            echo "${{ needs.production-releases.outputs.version_tags }}"
            echo ""
            echo "📄 GitHub Releases:"
            echo "${{ needs.production-releases.outputs.github_releases }}"
          elif [[ "${{ needs.production-releases.outputs.release_performed }}" == "false" ]]; then
            echo "ℹ️ No release performed (intent evaluation determined no release needed)"
          else
            echo "❌ Production release failed. Check logs above."
            exit 1
          fi
```

**Behavior**:
- **Auto-trigger**: When `.github/tag_and_release/release-**` files pushed to master
- **Manual trigger**: Select packages, level, and options
- **PyPI**: Publishes to production PyPI
- **Version tags**: Creates final version tags (e.g., `core/v1.0.0`)
- **GitHub releases**: Creates official GitHub releases

---

#### Task 3.4: Remove Legacy Release Workflows

**Files to remove**:
1. `.github/workflows/release.yml` - Old single-project production release
2. `.github/workflows/release-staging.yml` - Old single-project staging release
3. `.github/workflows/release-validate.yml` - Old single-project validation

**Rationale**:
- Completely replaced by 3 new orchestrator workflows
- Old workflows designed for single-project (not monorepo)
- Keeping them could cause confusion (which workflow to use?)
- Clean break simplifies maintenance

**Replacement Mapping**:
```
OLD WORKFLOW                    → NEW ORCHESTRATOR
release-validate.yml            → release-validate-monorepo.yml
release-staging.yml             → release-staging-monorepo.yml
release.yml                     → release-monorepo.yml
```

**Migration Strategy**:
1. **Phase 3**: Create all 3 new orchestrator workflows
2. **Phase 3**: Test orchestrators with staging releases
3. **Phase 5**: Remove all 3 old release workflows after validation

**Safety Net**:
- New orchestrators created first (Phase 3)
- Tested before removing old ones
- Git history preserves old workflows if needed
- Can revert if issues discovered

**No updates needed** - These files will be deleted, not deprecated

---

**Git Commits** (Phase 3):
```bash
✨ release: Add release-validate-monorepo.yml (validation orchestrator)
✨ release: Add release-staging-monorepo.yml (staging orchestrator)
✨ release: Add release-monorepo.yml (production orchestrator)
📝 docs: Update release workflow documentation
```

**Later in Phase 5** (after new orchestrators validated):
```bash
🗑️ release: Remove old release workflows (release.yml, release-staging.yml, release-validate.yml)
```

---

### Phase 4: Supporting Workflows Migration (2-3 hours)

**Goal**: Update remaining workflows for monorepo compatibility

#### Task 4.1: Update Docker CI Workflow

**File**: `.github/workflows/docker-ci.yml`

**Changes**:
1. Determine which package(s) have Dockerfile
2. Update build context to package directory
3. Add `package-name` parameter if building multiple packages

**Current Analysis**:
- Check if core has Dockerfile: `test-coverage-mcp/Dockerfile`
- Check if codecov has Dockerfile: `test-coverage-mcp-codecov/Dockerfile`

**Recommendation**: Update based on actual Dockerfile locations

---

#### Task 4.2: Update Type Check Workflow

**File**: `.github/workflows/type-check.yml`

**Changes**:
1. Update mypy paths for workspace structure
2. Ensure `mypy.ini` workspace config is used (already done in Phase 1.5)
3. Run type checking per package or workspace-wide

---

#### Task 4.3: Update Documentation Workflow

**File**: `.github/workflows/documentation.yaml`

**Changes**:
1. Determine which package owns documentation
2. Update doc build paths
3. Consider if docs should be built per-package or monorepo-wide

**Recommendation**: Keep docs in core package only (codecov uses core's docs)

---

**Git Commits** (Phase 4):
```bash
🔧 ci: Update docker-ci.yml for workspace structure
🔧 ci: Update type-check.yml to use workspace mypy config
🔧 ci: Update documentation.yaml for monorepo docs
```

---

### Phase 5: Cleanup and Documentation (1-2 hours)

**Goal**: Remove deprecated workflows and update documentation

#### Task 5.1: Remove Old CI Workflows

**Files to remove**:
1. `.github/workflows/ci.yaml` - Replaced by `ci-monorepo.yaml`
2. `.github/workflows/rw_build_and_test.yaml` - Local orchestration no longer needed
3. `.github/workflows/rw_run_all_test_and_record.yaml` - Local orchestration no longer needed

**Pre-conditions** (verify before removal):
- [ ] `ci-monorepo.yaml` successfully runs on multiple PRs
- [ ] All test types pass (unit, integration, contract)
- [ ] Coverage reports uploaded correctly
- [ ] No regression in CI functionality

**Removal Steps**:
```bash
# Remove old CI workflows
git rm .github/workflows/ci.yaml
git rm .github/workflows/rw_build_and_test.yaml
git rm .github/workflows/rw_run_all_test_and_record.yaml

# Commit
git commit -m "🗑️ ci: Remove deprecated CI workflows

- Removed ci.yaml (replaced by ci-monorepo.yaml)
- Removed local orchestration layers (rw_build_and_test, rw_run_all_test_and_record)
- New ci-monorepo.yaml directly calls upstream reusable workflows
- Simplifies workflow architecture and reduces maintenance burden"
```

---

#### Task 5.2: Remove Old Release Workflows

**Files to remove**:
1. `.github/workflows/release.yml` - Replaced by `release-monorepo.yml`
2. `.github/workflows/release-staging.yml` - Replaced by `release-staging-monorepo.yml`
3. `.github/workflows/release-validate.yml` - Replaced by `release-validate-monorepo.yml`

**Pre-conditions** (verify before removal):
- [ ] Validation orchestrator successfully validates packages
- [ ] Staging orchestrator successfully releases to TestPyPI
- [ ] Production orchestrator successfully releases to PyPI
- [ ] Tags created correctly (`core/v*`, `codecov/v*`)
- [ ] GitHub releases created successfully

**Removal Steps**:
```bash
# Remove old release workflows
git rm .github/workflows/release.yml
git rm .github/workflows/release-staging.yml
git rm .github/workflows/release-validate.yml

# Commit
git commit -m "🗑️ release: Remove deprecated release workflows

- Removed release.yml (replaced by release-monorepo.yml)
- Removed release-staging.yml (replaced by release-staging-monorepo.yml)
- Removed release-validate.yml (replaced by release-validate-monorepo.yml)
- All 3 orchestrators tested and validated
- New orchestrators scale with intent.yaml package definitions"
```

---

#### Task 5.3: Remove Migration TODO

**File**: `.github/workflows/TODO_WORKSPACE_MIGRATION.md`

**Action**: Delete file after all migrations complete

---

#### Task 5.4: Update REUSABLE_WORKFLOWS.md

**File**: `.github/workflows/REUSABLE_WORKFLOWS.md`

**Changes to add**:

1. **Monorepo Section**:
   ```markdown
   ## Monorepo Workflows

   This project uses a UV workspace monorepo with 2 packages:
   - `test-coverage-mcp` (core) - Main MCP server
   - `test-coverage-mcp-codecov` (codecov) - Codecov provider plugin

   ### CI Testing
   - **Workflow**: `ci-monorepo.yaml`
   - **Features**: Per-package testing, change detection, parallel execution
   - **Artifact naming**: `coverage_{project_name}_{test_type}_{os}_{python}`

   ### Releases
   - **Core package**: Use `release-core.yml`
   - **Codecov package**: Use `release-codecov.yml`
   - **Tag format**: `core/v1.0.0`, `codecov/v0.1.0`
   ```

2. **Examples Section**:
   ```markdown
   ### Triggering Per-Package Release

   1. Go to Actions → Release - Core Package
   2. Click "Run workflow"
   3. Select release level (auto/patch/minor/major)
   4. Workflow creates tag `core/v1.0.0` and publishes to PyPI
   ```

---

#### Task 5.5: Update Project Documentation

**Files to update**:

1. **CONTRIBUTING.md**:
   - Add "Running CI Locally" section
   - Explain per-package testing
   - Document release process for monorepo
   - Show how to run tests for specific packages

2. **README.md**:
   - Update CI badges (may need per-package badges)
   - Add monorepo structure explanation
   - Update installation instructions

Example for CONTRIBUTING.md:
```markdown
## Running Tests in Monorepo

### Test All Packages
```bash
uv run pytest
```

### Test Core Package Only
```bash
cd test-coverage-mcp
uv run pytest test/unit_test/ -v
```

### Test Codecov Plugin Only
```bash
cd test-coverage-mcp-codecov
uv run pytest test/unit_test/ -v
```

## Release Process

The project uses 3 release orchestrator workflows:

### Validation (Pre-Release Check)
1. Automatically runs on PRs modifying package code
2. Or manually trigger: `.github/workflows/release-validate-monorepo.yml`
3. Validates build, tests, and version bumps (dry-run only)

### Staging Release (TestPyPI)
1. Manually trigger: `.github/workflows/release-staging-monorepo.yml`
2. Select packages: `["core"]` or `["codecov"]` or `["core", "codecov"]`
3. Publishes to TestPyPI with RC tags (e.g., `core/v1.0.0-rc.1`)
4. Test installations before production

### Production Release (PyPI)
1. **Auto-trigger**: Push changes to `.github/tag_and_release/release-**`
2. **Manual trigger**: `.github/workflows/release-monorepo.yml`
   - Select packages: `["core"]` or `["codecov"]` or both
   - Select release level (auto/patch/minor/major)
3. Creates version tags (e.g., `core/v1.0.0`)
4. Publishes to PyPI
5. Creates GitHub releases

### Releasing Specific Package
To release only the core package:
```bash
# Trigger release-monorepo.yml manually
# Input: packages = ["core"]
# Input: level = patch (or minor/major)
```

To release both packages:
```bash
# Input: packages = ["core", "codecov"]
# Or leave empty for auto-detection
```
```

---

**Git Commits** (Phase 5):
```bash
🗑️ ci: Remove deprecated CI workflows (ci.yaml, rw_build_and_test, rw_run_all_test_and_record)
🗑️ release: Remove deprecated release workflows (release.yml, release-staging.yml, release-validate.yml)
🗑️ ci: Remove TODO_WORKSPACE_MIGRATION.md after migration complete
📝 docs: Update REUSABLE_WORKFLOWS.md with monorepo examples
📝 docs: Add monorepo CI/CD section to CONTRIBUTING.md
📝 docs: Update README.md with monorepo structure
```

---

## 📊 Migration Strategy & Sequencing

### Recommended Execution Order

**Week 1: Foundation**
1. ✅ Phase 1: Configuration Foundation (Day 1)
   - Backup and update `intent.yaml`
   - Validate configuration

2. ✅ Phase 2: CI Testing Workflows (Days 2-3)
   - Create `ci-monorepo.yaml`
   - Update legacy CI workflows
   - Test with small PR

**Week 2: Releases**
3. ✅ Phase 3: Release Workflows (Days 4-6)
   - Create per-package release workflows
   - Create staging workflows
   - Create validation workflows
   - Test with staging release

**Week 3: Polish**
4. ✅ Phase 4: Supporting Workflows (Days 7-8)
   - Update Docker CI (if needed)
   - Update type checking
   - Update documentation workflows

5. ✅ Phase 5: Cleanup (Day 9)
   - Remove migration artifacts
   - Update documentation
   - Final validation

---

### Testing Strategy

#### Pre-Migration Validation
- [ ] All existing CI tests pass on `master`
- [ ] Current release workflow works
- [ ] Documentation builds successfully

#### Migration Testing
- [ ] **Phase 1**: YAML validation passes
- [ ] **Phase 2**:
  - Create test PR modifying only core → only core tests run
  - Create test PR modifying only codecov → only codecov tests run
  - Verify coverage artifacts have correct naming
- [ ] **Phase 3**:
  - Trigger staging release for core
  - Verify tag created: `core/v1.0.0-rc.1`
  - Verify TestPyPI upload
  - Install from TestPyPI and test
- [ ] **Phase 4**: All supporting workflows still function
- [ ] **Phase 5**: All documentation up to date

#### Post-Migration Validation
- [ ] Full CI run on `master` passes
- [ ] Core package releases successfully to PyPI
- [ ] Codecov package releases successfully to PyPI
- [ ] Git tags use correct prefixes
- [ ] GitHub releases created correctly
- [ ] Documentation reflects new process

---

## 🎯 Success Criteria

### CI/CD Testing
- ✅ CI only runs tests for changed packages
- ✅ Per-package coverage artifacts with proper naming
- ✅ Codecov shows separate flags: `core,unit-test`, `codecov,integration-test`
- ✅ SonarQube multi-module analysis receives coverage for both packages
- ✅ All placeholders replaced (`<your_base_branch>`, `<your_package_name>`)

### Release Workflows
- ✅ Core package releases to PyPI as `test-coverage-mcp`
- ✅ Codecov package releases to PyPI as `test-coverage-mcp-codecov`
- ✅ Git tags use prefixes: `core/v*`, `codecov/v*`
- ✅ GitHub releases created with package-specific titles
- ✅ Independent version management per package
- ✅ Validation workflows prevent broken releases

### Documentation
- ✅ CONTRIBUTING.md explains monorepo workflows
- ✅ REUSABLE_WORKFLOWS.md has monorepo examples
- ✅ README.md reflects monorepo structure
- ✅ Clear instructions for contributors

---

## ⚠️ Important Considerations

### Version Management

**Independent Versioning**:
- Core package: `test-coverage-mcp/pyproject.toml` → `version = "1.0.0"`
- Codecov package: `test-coverage-mcp-codecov/pyproject.toml` → `version = "0.1.0"`
- Versions can differ and evolve independently

### Release Order

**Best Practice**:
1. Release core first → Establishes stable base
2. Release plugins after → Can reference core's version

**Why**: Plugins depend on core, users install core then plugins

### Package Dependencies

**Current**:
```toml
# test-coverage-mcp-codecov/pyproject.toml
[tool.uv.sources]
test-coverage-mcp = { workspace = true }
```

**Recommendation for Production**:
```toml
dependencies = [
    "test-coverage-mcp>=1.0.0,<2.0.0",  # Compatible version range
    "httpx>=0.28.1",
]
```

### Backward Compatibility

**Legacy Workflows**:
- Keep deprecated workflows during migration period
- Add clear deprecation notices
- Provide migration path in documentation
- Remove after 1-2 successful releases

---

## 🔄 Rollback Plan

If migration encounters critical issues:

### Quick Rollback
```bash
# Restore backup configuration
cp .github/tag_and_release/intent.yaml.backup .github/tag_and_release/intent.yaml

# Revert CI workflow changes
git checkout master -- .github/workflows/ci.yaml

# Remove new workflows
rm .github/workflows/ci-monorepo.yaml
rm .github/workflows/release-core.yml
rm .github/workflows/release-codecov.yml
```

### Staged Rollback
1. Disable new workflows by removing triggers
2. Re-enable legacy workflows
3. Investigate issues in separate branch
4. Fix and retry migration

---

## 📝 Decision Log

### Approved Decisions ✅

**Configuration**:
- ✅ Base branch: `master` only (no `develop`)
- ✅ Python versions: `["3.12", "3.13", "3.14"]`
- ✅ Operating systems: `["ubuntu-latest", "macos-latest"]`
- ✅ Tag prefixes: `core/`, `codecov/`
- ✅ Independent package versioning

**CI Testing Workflow Strategy**:
- ✅ **Option B**: Create new `ci-monorepo.yaml` with per-package matrix
- ✅ Use upstream reusable workflows (don't modify them)
- ✅ Keep legacy workflows for backward compatibility (Option A in Task 2.3)

**Release Workflow Strategy**:
- ✅ **3 Release Types Required**: Validation, Staging, Production
- ✅ **3 Orchestrator Workflows**: One per release type, all handle multiple packages
- ✅ **Trigger Conditions**:
  - Validation: Auto (PR changes) + Manual
  - Staging: Manual only
  - Production: Auto (release file changes) + Manual
- ✅ **No per-package workflows needed** - orchestrators scale with intent.yaml

### Decisions Still Requiring Confirmation

1. **Docker Builds**:
   - [ ] Build from core package only
   - [ ] Build from both packages
   - [ ] Skip Docker builds entirely
   - **Action Required**: Check which packages have Dockerfile

2. **Documentation Builds**:
   - [ ] Build from core package only (recommended)
   - [ ] Build per-package docs
   - [ ] Unified monorepo docs
   - **Recommendation**: Core only (codecov uses core's docs)

3. **Release Orchestrator Validation**:
   - [ ] Test with dry-run first
   - [ ] Test staging release before production
   - **Recommendation**: Start with validation orchestrator, then staging, then production

---

## 📚 References

### Related Documents
- Phase 0.5 in `.ai/prompt/2026.3.29-4.2/plan/implementation-plan.md`
- Phase 1.5 in `.ai/prompt/2026.3.29-4.2/plan/implementation-plan.md`
- `.ai/prompt/2026.4.7/design-or-spec/monorepo-release-configuration-guide.md`
- `.github/workflows/TODO_WORKSPACE_MIGRATION.md`

### Reusable Workflows Repository
- https://github.com/Chisanan232/GitHub-Action_Reusable_Workflows-Python
- PR #136: Monorepo support with `project_name` parameter

### External Resources
- [UV Workspace Documentation](https://docs.astral.sh/uv/concepts/workspaces/)
- [GitHub Actions: Reusing Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Monorepo Release Strategies](https://monorepo.tools/versioning)

---

## ✅ Final Checklist

Before starting implementation:
- [ ] Review and approve this plan
- [ ] Confirm decision points above
- [ ] Backup current configurations
- [ ] Create feature branch for migration
- [ ] Prepare test environment

After implementation:
- [ ] All workflows execute without errors
- [ ] Test releases successful on both packages
- [ ] Documentation updated and reviewed
- [ ] Team trained on new workflows
- [ ] Migration artifacts removed

---

## 📊 Summary of Changes from Version 1.0 to 1.1

### Major Improvements Based on User Feedback

#### 1. Release System - Orchestrator First ✨

**Before (v1.0)**:
- Required creating separate workflow file per package
- `release-core.yml`, `release-codecov.yml`, `release-staging-core.yml`, etc.
- Adding 3rd package = 3 more workflow files

**After (v1.1)**:
- **Primary**: Single `release-monorepo.yml` orchestrator
- Auto-detects changed packages or accepts manual input
- Adding 3rd package = update `intent.yaml` only
- **Optional**: Individual workflows as fallback (can be skipped)

**User Benefit**: Dramatically reduces maintenance burden as monorepo grows.

---

#### 2. CI Testing - Clarified Architecture 📝

**Before (v1.0)**:
- Unclear if should modify reusable workflows
- Mixed messaging on legacy workflow handling

**After (v1.1)**:
- ✅ Clear two-tier architecture explained
- ✅ **Local workflows**: Orchestration and triggers (this repo)
- ✅ **Upstream workflows**: Reusable logic (don't modify)
- ✅ New `ci-monorepo.yaml` calls upstream workflows with `project_name`
- ✅ Keep legacy workflows for backward compatibility (minimal changes)

**User Benefit**: Clear separation of concerns, easier to understand and maintain.

---

#### 3. Legacy Workflows - Backward Compatible 🔄

**Before (v1.0)**:
- Recommendation was to deprecate/delete
- Risk of breaking existing processes

**After (v1.1)**:
- ✅ Keep and update with minimal changes
- ✅ Only fix placeholders and paths
- ✅ Provides fallback during migration
- ✅ Can be removed after new workflows proven stable

**User Benefit**: Safer migration with gradual transition.

---

### Implementation Complexity Comparison

**Version 1.0 (Individual Workflows)**:
- Files to create: ~10-12 workflow files
- Maintenance: Add 3-4 files per new package
- Complexity: Medium (lots of duplication)

**Version 1.1 (Orchestrator Pattern)**:
- Files to create: ~4-6 workflow files (primary) or ~10+ (with optional fallbacks)
- Maintenance: Add 1 config block in `intent.yaml` per new package
- Complexity: Low (single orchestrator handles all)

**Recommendation**: Start with primary workflows only (orchestrator + updated legacy), add optional individual workflows only if needed for debugging.

---

### Files to Create/Remove (Final List)

**NEW Workflows** (Phase 2 & 3):
```
CI:
✨ .github/workflows/ci-monorepo.yaml                  (per-package matrix CI)

Release:
✨ .github/workflows/release-validate-monorepo.yml     (validation orchestrator)
✨ .github/workflows/release-staging-monorepo.yml      (staging orchestrator)
✨ .github/workflows/release-monorepo.yml              (production orchestrator)
```

**UPDATED** (Phase 1 & 4):
```
Config:
🔧 .github/tag_and_release/intent.yaml                 (multi-package definitions)

Workflows:
🔧 .github/workflows/ci_includes_e2e_test.yaml         (monorepo paths)
🔧 .github/workflows/docker-ci.yml                     (if needed)
🔧 .github/workflows/documentation.yaml                (if needed)
```

**REMOVED** (Phase 5 - after validation):
```
Old CI:
🗑️ .github/workflows/ci.yaml                           (replaced by ci-monorepo.yaml)
🗑️ .github/workflows/rw_build_and_test.yaml            (local orchestration removed)
🗑️ .github/workflows/rw_run_all_test_and_record.yaml   (local orchestration removed)

Old Release:
🗑️ .github/workflows/release.yml                       (replaced by release-monorepo.yml)
🗑️ .github/workflows/release-staging.yml               (replaced by release-staging-monorepo.yml)
🗑️ .github/workflows/release-validate.yml              (replaced by release-validate-monorepo.yml)
```

**Summary**:
- **New**: 4 workflow files
- **Updated**: 2-4 files (depending on Docker/docs needs)
- **Removed**: 6 redundant workflow files
- **Net change**: Simplified from 15+ files to ~10 files

**Scalability**: Adding 3rd package requires only updating `intent.yaml` (no new workflow files needed!)

---

### Key Decision Summary

| Decision Point | User Selection | Rationale |
|----------------|----------------|-----------|
| **Release Types** | 3 types required | Validation, Staging, Production workflows |
| **Release Strategy** | 3 Orchestrator workflows | One per type, all packages in each |
| **Release Triggers** | Auto + Manual per type | Validation: auto+manual, Staging: manual, Production: auto+manual |
| **CI Testing** | Option B (Per-Package Matrix) | Better isolation, aligns with Phase 0.5 |
| **Legacy Workflows** | Option A (Keep & update) | Backward compatibility, safer migration |
| **Upstream Workflows** | Don't modify | Centralized management already working |

---

### Next Steps for User

1. **Review 3 Orchestrator Workflows** (Tasks 3.1-3.3)
   - Validation orchestrator (auto + manual triggers)
   - Staging orchestrator (manual only)
   - Production orchestrator (auto + manual)
   - Confirm permissions and concurrency settings are acceptable

2. **Review Decision Log** (section "Decisions Still Requiring Confirmation")
   - Confirm Docker build strategy (which packages have Dockerfile?)
   - Confirm documentation build strategy (core only or per-package?)

3. **Approve This Plan**
   - Confirm 3 orchestrator approach meets all requirements
   - Confirm trigger conditions (auto vs manual per workflow type)
   - Confirm permissions and settings

4. **Ready for Implementation**
   - Once approved, implementation can begin with Phase 1

---

**End of Plan** 🚀

**Version 1.2 Status**: Redesigned with 3 orchestrator workflows per user requirements.

**Summary**:
- ✅ **3 Release Types**: Validation, Staging, Production (as required)
- ✅ **Trigger Flexibility**: Auto + manual per type (as specified)
- ✅ **Important Settings**: Permissions, concurrency preserved
- ✅ **Maintainability**: All orchestrators scale with `intent.yaml`
- ✅ **Cleanup Strategy**: Old workflows removed after validation (Phase 5)
- ✅ **No per-package workflow files needed**
- ✅ **Simplified Architecture**: Direct upstream workflow calls (removed local orchestration layers)

This plan addresses the maintainability concern with orchestrator pattern while meeting all 3 release type requirements, preserving important workflow settings, and cleaning up redundant workflows for a simplified architecture.
