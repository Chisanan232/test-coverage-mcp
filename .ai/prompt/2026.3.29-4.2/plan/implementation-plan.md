# Test Coverage MCP Server - Implementation Plan (v2)

## Executive Summary

This document outlines a **15-phase** implementation plan for the test-coverage-mcp server, transforming the current single-package structure into a **provider-extensible, capability-driven MCP server** with stable tool contracts, intelligent coverage analysis, and plugin architecture.

**Current State**: Single package with basic structure  
**Target State**: uv workspace monorepo with independent packages (core + plugins), 11 MCP tools, CLI, Docker support, comprehensive documentation  
**Technology Stack**: FastMCP, FastAPI, Pydantic, Pydantic-Settings, httpx, uv workspaces

## Updates from v1

✅ **Issue #1 Fixed**: Corrected workspace structure - packages at root level, each with own `src/` and `tests/`  
✅ **Issue #2 Fixed**: Added gitmoji conventions for clear, human-readable commit messages  
✅ **Issue #3 Fixed**: Documentation updates integrated into every phase  
✅ **Issue #4 Fixed**: Added CI/CD compatibility analysis and migration plan (Phase 0.5)

---

## Development Philosophy

### Commit Strategy with Gitmoji

Following the global commit policy with **[gitmoji](https://gitmoji.dev/)** conventions for clear, human-readable commits:

#### Core Principles

- **Atomic commits**: One logical change per commit
- **Imperative mood**: "Add feature" not "Added feature"
- **Gitmoji prefix**: Use emoji to categorize commit type
- **Specific messages**: Clear what and why (50-72 chars)
- **Bisectable history**: Each commit passes tests
- **Event-based**: Commit after completing a logical unit

#### Gitmoji Commit Patterns

**Format**: 
- Simple: `<emoji> <subject>` (emoji conveys the type)
- With scope: `<emoji> <scope>: <subject>` (scope = codecov, mcp, web, cli, etc.)

| Category             | Emoji                         | Example (Simple)                         | Example (With Scope)                      |
|----------------------|-------------------------------|------------------------------------------|-------------------------------------------|
| **Architecture**     | 🏗️ `:building_construction:` | `🏗️ Restructure to uv workspace layout` | `🏗️ workspace: Restructure to monorepo`  |
| **New Features**     | ✨ `:sparkles:`                | `✨ Add ProviderCapability enum`          | `✨ codecov: Add API client`               |
| **Refactoring**      | ♻️ `:recycle:`                | `♻️ Extract provider registry logic`     | `♻️ registry: Extract to separate module` |
| **Tests**            | ✅ `:white_check_mark:`        | `✅ Add unit tests for ProviderRegistry`  | `✅ codecov: Add integration tests`        |
| **Documentation**    | 📝 `:memo:`                   | `📝 Add provider plugin guide`           | `📝 mcp-tools: Add catalog reference`     |
| **Configuration**    | 🔧 `:wrench:`                 | `🔧 Configure CLI entry points`          | `🔧 mypy: Update for workspace paths`     |
| **CI/CD**            | 👷 `:construction_worker:`    | `👷 Update workflows for workspace`      | `👷 sonarqube: Add monorepo config`       |
| **Bug Fixes**        | 🐛 `:bug:`                    | `🐛 Handle pending state correctly`      | `🐛 mcp: Fix pending state in PR tools`   |
| **Performance**      | ⚡ `:zap:`                     | `⚡ Cache provider lookups`               | `⚡ registry: Add capability caching`      |
| **Dependencies**     | ➕ `:heavy_plus_sign:`         | `➕ Add httpx for API client`             | `➕ codecov: Add httpx dependency`         |
| **Breaking Changes** | 💥 `:boom:`                   | `💥 Change tool response format`         | `💥 mcp: Change ExecutionMetadata`        |
| **Type Hints**       | 🏷️ `:label:`                 | `🏷️ Add type hints to services`         | `🏷️ services: Add comprehensive types`   |
| **Move/Rename**      | 🚚 `:truck:`                  | `🚚 Migrate core to workspace`           | `🚚 test: Rename to test/unit_test`       |
| **Security**         | 🔒 `:lock:`                   | `🔒 Use Pydantic-Settings for secrets`   | `🔒 config: Secure token management`      |
| **Linting**          | 🚨 `:rotating_light:`         | `🚨 Fix ruff warnings`                   | `🚨 services: Fix type violations`        |

#### Commit Message Examples

```bash
# Phase 1: Workspace restructuring
🏗️ Create uv workspace with packages at root
🚚 Migrate core code to test-coverage-mcp/src
✨ Add codecov plugin package stub
🔧 pytest: Update config for workspace test discovery
📝 Update README for workspace architecture

# Phase 2: Domain models
✨ Add ProviderCapability enum with 14 capabilities
🏷️ Define CoverageProvider protocol
✅ Add domain model validation tests

# Phase 5: Services
✨ services: Implement RepositoryHealthService
♻️ services: Extract risk scoring logic
✅ services: Add integration tests
📝 architecture: Document service layer

# Phase 12: CLI
✨ cli: Add serve command with transport options
🔧 pyproject: Configure console script entry
📝 cli: Add usage guide with examples
```

### Development Workflow

1. **Red-Green-Refactor** for testable code
2. **Commit frequently** at logical boundaries
3. **One concern per commit** (no mixing features with refactors)
4. **Tests in same or separate commit** depending on size
5. **Update documentation** when behavior changes

---

## Phase 0: Pre-Implementation Analysis

**Goal**: Understand current codebase and plan migration path

### Tasks

1. **Audit existing code**
   - Review `src/` structure
   - Identify reusable components
   - Document current dependencies
   - Check existing MCP/FastAPI integration

2. **Identify migration risks**
   - Breaking changes from restructuring
   - Backward compatibility considerations
   - Dependency conflicts

3. **Validate design against constraints**
   - Confirm FastMCP capabilities
   - Verify uv workspace support
   - Test plugin discovery mechanisms

### Commits
- `docs: Add phase 0 analysis findings`

**Duration**: 1-2 hours  
**Output**: Analysis document in `.ai/analysis/`

---

## Phase 1: Workspace Restructuring

**Goal**: Transform single package into uv workspace monorepo

### Tasks

1. **Create workspace structure**
   ```
   repo/
     pyproject.toml                    # Workspace root config
     uv.lock                           # Unified lockfile
     .github/                          # CI/CD workflows (update needed)
     docs/                             # Docusaurus documentation
     
     test-coverage-mcp/                # Core package (at root!)
       .env.example                    # Environment variables template
       pyproject.toml                  # Package config
       src/
         test_coverage_mcp/
           __init__.py
           domain/                     # Domain models
           registry/                   # Provider registry
           services/                   # Intelligence services
           mcp/                        # MCP tools/facade
           cli/                        # CLI commands
       tests/
         unit/
         integration/
         e2e/
         contract/
       pytest.ini                      # Test configuration
       .coveragerc                     # Coverage config
     
     test-coverage-mcp-codecov/        # Codecov plugin package
       .env.example                    # Provider-specific env vars
       pyproject.toml                  # Plugin package config
       src/
         test_coverage_mcp_codecov/
           __init__.py
           client/                     # API client
           dtos/                       # DTOs
           mappers/                    # DTO-to-domain
           adapter.py                  # Provider adapter
           plugin.py                   # Plugin registration
       tests/
         unit/
         integration/
       pytest.ini
       .coveragerc
   ```

2. **Configure workspace root**
   - Update root `pyproject.toml` with `[tool.uv.workspace]`
   - Define workspace members: `["test-coverage-mcp", "test-coverage-mcp-codecov"]`
   - Set shared dependency constraints (optional)
   - Keep dev tools at root or per-package (prefer per-package for isolation)

3. **Migrate core package**
   - Create `test-coverage-mcp/` at root (not in `packages/`)
   - Move `src/` to `test-coverage-mcp/src/`
   - Move `test/` to `test-coverage-mcp/tests/`
   - Create `test-coverage-mcp/pyproject.toml` with package metadata
   - Copy `.env.example`, `pytest.ini`, `.coveragerc` to package
   - Update package name to `test-coverage-mcp` (consistent with design)

4. **Create plugin stub**
   - Create `test-coverage-mcp-codecov/` at root
   - Add `src/test_coverage_mcp_codecov/` structure
   - Add `tests/` with unit/integration subdirs
   - Create `pyproject.toml` with plugin metadata
   - Define entry point: `[project.entry-points."test_coverage_mcp.providers"]`
   - Add `.env.example` for Codecov-specific config

5. **Update tooling configuration per package**
   - Each package has own `pytest.ini` (test discovery)
   - Each package has own `.coveragerc` (coverage paths)
   - Root `mypy.ini` can reference workspace (or per-package)
   - Root `ruff.toml` can apply to all (or per-package)
   - Update test paths: `test-coverage-mcp/tests/`, `test-coverage-mcp-codecov/tests/`

6. **Update documentation structure**
   - Keep `docs/` at root for Docusaurus
   - Add workspace architecture diagram
   - Update README with new structure
   - Create `CONTRIBUTING.md` with workspace workflow

### Commits (with gitmoji)

```bash
🏗️ Create uv workspace with members at root level
🚚 Migrate core to test-coverage-mcp/ package
🚚 Migrate tests to test-coverage-mcp/tests/
✨ Add test-coverage-mcp-codecov plugin stub
🔧 Add per-package pytest and coverage configs
🔧 Update root pyproject.toml for workspace
👷 Update workflow paths for new structure (placeholder)
✅ Verify workspace build with uv sync
✅ Verify test discovery in both packages
📝 Update README with workspace architecture
📝 Add CONTRIBUTING.md with workspace workflow
```

**Duration**: 6-8 hours (includes documentation)  
**Validation**: 
- `uv sync` (install all workspace members)
- `cd test-coverage-mcp && uv run pytest`
- `cd test-coverage-mcp-codecov && uv run pytest`
- `uv build --package test-coverage-mcp`
- Verify docs build still works

**Documentation Updates**:
- `README.md`: Workspace structure, quick start
- `CONTRIBUTING.md`: How to work with workspace
- `docs/contents/architecture/workspace.md`: Detailed architecture

---

## Phase 1.5: Configuration Cleanup & Monorepo Optimization

**Goal**: Clean up root-level configurations, flatten package structures, and establish proper monorepo configuration hierarchy

### Problem Statement

After Phase 1 workspace restructure, several configuration issues remain:

1. **Package Structure Issue**: 
   - `test-coverage-mcp-codecov/src/test_coverage_mcp_codecov/` has nested structure
   - Should be flat like core: `test-coverage-mcp-codecov/src/` (no extra nesting)

2. **Conflicting Root Configs**:
   - Root `.coveragerc`, `pytest.ini` reference old `src/` paths
   - Conflict with package-level configurations already created
   - Root `.env.example` (167 lines) is outdated for workspace

3. **Workspace-Wide Configs Need Updates**:
   - `mypy.ini` references `packages = src,test` (outdated paths)
   - `ruff.toml` has `known-first-party = gearmeshing_ai` (wrong project!)
   - `sonar-project.properties` uses single-project format (needs modules)
   - `Dockerfile` references old structure, needs workspace build

4. **Configuration Hierarchy Unclear**:
   - Which configs should be workspace-wide vs package-specific?
   - How to handle per-package vs shared settings?

### Configuration Strategy for Monorepo

#### ✅ Keep at Root (Workspace-Wide Tooling)

**Linting & Formatting:**
- `ruff.toml` - Apply same style rules across all packages
  - Update: Fix `known-first-party` (remove `gearmeshing_ai`, add workspace packages)
  - Update: Adjust paths if needed for workspace

**Type Checking:**
- `mypy.ini` - Workspace-wide type checking
  - Update: Change `packages = src,test` to workspace-aware paths
  - Option 1: `packages = test-coverage-mcp/src,test-coverage-mcp/test,test-coverage-mcp-codecov/src`
  - Option 2: Create per-package `mypy.ini` if configs differ significantly

**Pre-commit Hooks:**
- `.pre-commit-config.yaml` - Run hooks across workspace
  - Update: Verify paths work with workspace structure
  - Update: `mypy` hook to check workspace packages

**Quality & Coverage:**
- `sonar-project.properties` - Monorepo with modules
  - Update: Convert to multi-module format
  - Define modules: `sonar.modules=core,codecov`
  - Per-module: `core.sonar.sources=test-coverage-mcp/src/`
- `codecov.yml` - Keep for workspace-wide coverage settings
  - Optional: Add component paths for better reporting

**Docker:**
- `Dockerfile` - Workspace build
  - Update: Copy workspace structure correctly
  - Update: Build strategy for monorepo (build all or specific package)
  - Consider: Per-package Dockerfiles if packages deploy separately

**Documentation:**
- `.gitignore`, `LICENSE`, `README.md`, `CONTRIBUTING.md` - Stay at root

#### ❌ Remove from Root (Conflicts with Package Configs)

**Testing Configs:**
- Root `pytest.ini` - **DELETE** (packages have their own)
- Root `.coveragerc` - **DELETE** (packages have their own)

**Environment:**
- Root `.env.example` - **DECISION NEEDED**:
  - Option A: Delete (packages have their own)
  - Option B: Keep minimal workspace example that references package `.env.example` files
  - Recommendation: Keep minimal with pointers to package configs

#### ✅ Per-Package (Already Done in Phase 1)

Each package has:
- `pytest.ini` - Package-specific test config ✓
- `.coveragerc` - Package-specific coverage config ✓
- `.env.example` - Package-specific environment vars ✓
- `pyproject.toml` - Package metadata and dependencies ✓
- `README.md` - Package documentation ✓

### Tasks

#### 1.5.1: Flatten Codecov Package Structure

**Problem**: `test-coverage-mcp-codecov/src/test_coverage_mcp_codecov/` has unnecessary nesting

**Action**:
```bash
# Move content up one level
mv test-coverage-mcp-codecov/src/test_coverage_mcp_codecov/* test-coverage-mcp-codecov/src/
rmdir test-coverage-mcp-codecov/src/test_coverage_mcp_codecov/
```

**Files to move**:
- `__init__.py` → `test-coverage-mcp-codecov/src/__init__.py`

**Updates needed**:
- Verify imports work correctly
- Update `pyproject.toml` if package discovery needs adjustment

#### 1.5.2: Delete Conflicting Root Configs

**Delete**:
- Root `pytest.ini` - Replaced by package-level configs
- Root `.coveragerc` - Replaced by package-level configs

**Update Root `.env.example`**:
Option A (Recommended): Simplify to workspace overview
```env
# Test Coverage MCP Workspace Configuration
# 
# This workspace contains multiple packages, each with their own configuration.
# See package-specific .env.example files:
#
# - test-coverage-mcp/.env.example - Core MCP server configuration
# - test-coverage-mcp-codecov/.env.example - Codecov provider configuration
#
# Quick Start:
# 1. Copy package .env.example to .env in each package directory
# 2. Configure package-specific settings
# 3. Run: uv sync
```

Option B: Delete entirely (users reference package files directly)

#### 1.5.3: Update Workspace-Wide Configs for Monorepo

**Update `mypy.ini`**:
```ini
# Global options:

[mypy]
# Check all package source code
files = test-coverage-mcp/src, test-coverage-mcp-codecov/src
exclude = (?x)(
    test-coverage-mcp/test/unit_test/.*\.py |  # Ignore unit tests (use mocks)
    test-coverage-mcp-codecov/test/unit_test/.*\.py
  )

show_traceback = True
warn_unused_configs = True
warn_redundant_casts = True
warn_unused_ignores = True
strict_equality = True
strict_concatenate = True

# Per-package overrides if needed
[mypy-test_coverage_mcp.*]
# Core package settings

[mypy-test_coverage_mcp_codecov.*]
# Codecov provider settings
```

**Update `ruff.toml`**:
```toml
# Fix known-first-party for workspace
[lint.isort]
known-first-party = [
    "test_coverage_mcp",
    "test_coverage_mcp_codecov"
]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

# Ensure workspace paths are covered
[lint]
# ... existing config ...

# Workspace-specific per-file ignores
[lint.per-file-ignores]
"test-coverage-mcp/test/**/*.py" = ["S101", "PLR2004", "PLR0913", ...]
"test-coverage-mcp-codecov/test/**/*.py" = ["S101", "PLR2004", "PLR0913", ...]
```

**Update `sonar-project.properties`** (Monorepo Format):
```properties
sonar.host.url=https://sonarcloud.io
sonar.projectKey=Chisanan232_test-coverage-mcp
sonar.organization=chisanan232
sonar.issues.defaultAssigneeLogin=Bryant

sonar.projectName=test-coverage-mcp
sonar.projectVersion=0.0.0
sonar.projectBaseDir=./

# Multi-module monorepo configuration
sonar.modules=core,codecov

# Core package module
core.sonar.projectName=test-coverage-mcp (Core)
core.sonar.sources=test-coverage-mcp/src
core.sonar.tests=test-coverage-mcp/test
core.sonar.python.coverage.reportPaths=test-coverage-mcp/coverage*.xml

# Codecov provider module
codecov.sonar.projectName=test-coverage-mcp-codecov
codecov.sonar.sources=test-coverage-mcp-codecov/src
codecov.sonar.tests=test-coverage-mcp-codecov/test
codecov.sonar.python.coverage.reportPaths=test-coverage-mcp-codecov/coverage*.xml

# Global Python settings
sonar.python.file.suffixes=.py
sonar.python.version=3.12,3.13,3.14
sonar.sourceEncoding=UTF-8

# Workspace-wide exclusions (if any)
# sonar.coverage.exclusions=
```

**Update `Dockerfile`** (Workspace Build):
```dockerfile
# Build stage
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy workspace configuration
COPY pyproject.toml uv.lock ./
COPY LICENSE README.md ./

# Copy all package directories
COPY test-coverage-mcp/ ./test-coverage-mcp/
COPY test-coverage-mcp-codecov/ ./test-coverage-mcp-codecov/

# Create virtual environment and install all workspace packages
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --locked

# Final stage
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    SERVER_PORT=8000

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy workspace
COPY --from=builder /app/test-coverage-mcp ./test-coverage-mcp
COPY --from=builder /app/test-coverage-mcp-codecov ./test-coverage-mcp-codecov
COPY pyproject.toml uv.lock ./

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE ${SERVER_PORT}

# Entry point runs core package
CMD ["test-coverage-mcp", "serve"]
```

**Update `.pre-commit-config.yaml`**:
```yaml
# Verify mypy checks workspace packages
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.17.1
  hooks:
    - id: mypy
      name: mypy
      entry: mypy
      language: system
      # Check both packages
      files: ^(test-coverage-mcp/src|test-coverage-mcp-codecov/src)/.*\.py$
      exclude: |
        (?x)^(
          test-coverage-mcp/test/unit_test/.*\.py|
          test-coverage-mcp-codecov/test/unit_test/.*\.py
        )$
      args:
        - --config-file=mypy.ini
```

#### 1.5.4: Verify Configuration Hierarchy

**Test workspace configs**:
```bash
# Linting works across workspace
uv run ruff check .

# Type checking works
uv run mypy test-coverage-mcp/src test-coverage-mcp-codecov/src

# Pre-commit runs correctly
uv run pre-commit run --all-files

# Per-package testing works
cd test-coverage-mcp && uv run pytest
cd test-coverage-mcp-codecov && uv run pytest

# Workspace build works
uv sync
uv build --package test-coverage-mcp
uv build --package test-coverage-mcp-codecov

# Docker build works (if applicable)
docker build -t test-coverage-mcp:local .
```

### Commits (with gitmoji)

```bash
🚚 Flatten codecov package structure (remove nested layer)
🔥 Remove conflicting root pytest.ini and .coveragerc
♻️  Simplify root .env.example for workspace
🔧 mypy: Update for monorepo package paths
🔧 ruff: Fix known-first-party for workspace packages
🔧 sonar: Convert to multi-module monorepo format
🐳 Dockerfile: Update for workspace build
👷 pre-commit: Adjust paths for workspace structure
✅ Verify workspace configurations work correctly
📝 Update CONTRIBUTING.md with config hierarchy
```

### Duration

**Estimated**: 2-3 hours

### Validation Checklist

- [ ] Codecov package has flat structure (`src/*.py` not `src/package/*.py`)
- [ ] No root `pytest.ini` or `.coveragerc` conflicts
- [ ] `uv run ruff check .` works across workspace
- [ ] `uv run mypy test-coverage-mcp/src` passes
- [ ] `uv run mypy test-coverage-mcp-codecov/src` passes
- [ ] `uv run pre-commit run --all-files` passes
- [ ] Per-package pytest works in both packages
- [ ] `uv sync` and `uv build --package <name>` work
- [ ] SonarQube config valid (modules defined correctly)
- [ ] Dockerfile builds successfully (if kept)

### Decision Points for Review

1. **Root `.env.example`**: Keep simplified version or delete entirely?
   - Recommendation: Keep with pointers to package `.env.example` files

2. **Dockerfile**: Keep workspace Dockerfile or per-package Dockerfiles?
   - If deploying packages separately: Per-package Dockerfiles
   - If deploying together: Workspace Dockerfile (as shown above)

3. **MyPy configuration**: Root `mypy.ini` or per-package?
   - Current plan: Root with per-module overrides if needed
   - Alternative: Each package has own `mypy.ini`

4. **Test folder naming**: Keep `unit_test/`, `integration_test/` or rename to `unit/`, `integration/`?
   - Current: Keeping `*_test/` naming (matches reusable workflows)
   - Note: Phase 0.5 will address CI/CD compatibility

---

## Phase 0.5: CI/CD Compatibility Analysis & Migration

**Goal**: Adapt CI/CD workflows for monorepo using enhanced reusable workflows with `project_name` support

**Status**: Ready to implement (depends on Phase 1.5 completion ✅)

**Estimated Duration**: 4-6 hours

---

### Executive Summary

**What Changed**:
- Reusable workflows (PR #136) now support `project_name` parameter for monorepo
- Current workspace structure already compatible with template requirements ✅
- SonarQube multi-module configuration completed in Phase 1.5 ✅

**What We'll Do**:
1. Update existing workflows to replace placeholder variables
2. Create new monorepo-aware CI workflow with per-package testing
3. Implement smart change detection (only test affected packages)
4. Configure per-package coverage reporting with proper artifact naming

**Why This Matters**:
- Faster CI with parallel package testing
- Clear failure isolation (know exactly which package failed)
- Proper per-package coverage tracking in Codecov
- Future-proof for adding more packages

---

### 1. Prerequisites & Compatibility Check

#### ✅ Already Complete (from Phase 1.5)

- **Package structure**: Flat `src/` directories (no nested layers)
- **Test directories**: Using `test/unit_test/`, `test/integration_test/` naming
- **SonarQube**: Multi-module configuration with `core` and `codecov` modules
- **Workspace configs**: `mypy.ini`, `ruff.toml`, `.pre-commit-config.yaml` updated

#### 🔍 Need to Verify

**Test directory structure in codecov package**:
```bash
# Verify codecov package has correct test naming
ls -la test-coverage-mcp-codecov/test/
# Expected: unit_test/, integration_test/ (with underscores)
```

**Current workflow placeholders**:
- `.github/workflows/ci.yaml`: Contains `<your_base_branch>`, `<your_package_name>`
- `.github/workflows/ci_includes_e2e_test.yaml`: Same placeholders

---

### 2. Monorepo Testing Strategy

#### Recommended Approach: Multi-Package Matrix Testing

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│ Change Detection (dorny/paths-filter)                       │
│ Outputs: core=true/false, codecov=true/false               │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐             ┌────────▼────────┐
│ Core Package    │             │ Codecov Package │
│ (if changed)    │             │ (if changed)    │
├─────────────────┤             ├─────────────────┤
│ • Unit Tests    │             │ • Unit Tests    │
│ • Integration   │             │ • Integration   │
│ • Coverage Org  │             │ • Coverage Org  │
│ • Upload        │             │ • Upload        │
└─────────────────┘             └─────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
             ┌───────────▼───────────┐
             │ SonarQube Multi-Module│
             │ (receives both)       │
             └───────────────────────┘
```

**Key Benefits**:
- ✅ Parallel execution (faster CI)
- ✅ Conditional testing (only changed packages)
- ✅ Per-package coverage with flags: `core,unit-test`, `codecov,unit-test`
- ✅ Clear failure messages showing which package failed

**Artifact Naming Convention**:
```
coverage_core_unit-test_ubuntu-latest_3.12
coverage_core_unit-test_ubuntu-latest_3.13
coverage_core_unit-test_ubuntu-latest_3.14
coverage_core_integration-test_ubuntu-latest_3.12
coverage_codecov_unit-test_macos-latest_3.13
```

---

### 3. New Reusable Workflow Capabilities (PR #136)

**Critical New Parameter**: `project_name`
- Purpose: Distinguish artifacts in monorepo
- Used by: `rw_uv_run_test.yaml`, `rw_organize_test_cov_reports.yaml`, `rw_upload_test_cov_report.yaml`
- Impact: Enables filtering and proper artifact naming

**Other Monorepo Parameters**:
- `test_working_directory`: Set CWD for each package (e.g., `./test-coverage-mcp`)
- `test_folder`: Package-relative test path (e.g., `./test/unit_test`)
- `all_test_items_paths`: JSON array of test discovery paths

**Configuration Management**:
- `rw_parse_project_config.yaml`: Centralized config from `.github/tag_and_release/intent.yaml`
- Supports project metadata, Docker settings, release configuration

---

### 4. Implementation Tasks

#### Task 0.5.1: Verify Test Structure Compliance ✓

**Status**: Likely already complete from Phase 1  
**Action**: Quick verification only

```bash
# Check core package
ls -la test-coverage-mcp/test/
# Expected: unit_test/, integration_test/

# Check codecov package  
ls -la test-coverage-mcp-codecov/test/
# Expected: unit_test/, integration_test/
```

**If not compliant**: Rename directories to use underscore naming (`unit_test`, not `unit`)

---

#### Task 0.5.2: Replace Placeholder Variables

**Files to update**:

**1. `.github/workflows/ci.yaml`**
```yaml
# Replace placeholders
<your_base_branch> → master  # Use master only to save CI resources
<your_package_name> → test_coverage_mcp

# Update branch triggers to master only
on:
  push:
    branches: [master]  # Only master, not develop
  pull_request:
    branches: [master]

# Update path patterns to be monorepo-aware
paths:
  # Workspace-level
  - 'pyproject.toml'
  - 'uv.lock'
  - '.github/workflows/**'
  
  # Package-level
  - 'test-coverage-mcp/**/*.py'
  - 'test-coverage-mcp/pyproject.toml'
  - 'test-coverage-mcp-codecov/**/*.py'
  - 'test-coverage-mcp-codecov/pyproject.toml'
  
  # Root configs
  - 'mypy.ini'
  - 'ruff.toml'
  - 'sonar-project.properties'
```

**2. `.github/workflows/ci_includes_e2e_test.yaml`**
- Replace `<your_base_branch>` → `master`
- Replace `<your_package_name>` → `test_coverage_mcp`
- Update branches to `[master]` only
- Same path pattern updates

**3. Local reusable workflows** (if any exist in `.github/workflows/rw_*.yaml`)
- Update to reference workspace structure
- Ensure branches reference `master` only

---

#### Task 0.5.3: Create Monorepo CI Workflow

**New file**: `.github/workflows/ci-monorepo.yaml`

**Workflow Design**:
```yaml
name: CI - Monorepo

on:
  push:
    branches: [master]  # Only master branch to save resources
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

  # Step 2: Test core package (parallel: unit + integration)
  test-core-unit:
    needs: detect-changes
    if: needs.detect-changes.outputs.core == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@develop
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
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@develop
    with:
      test_type: 'integration-test'
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'
      test_folder: './test/integration_test'
      all_test_items_paths: '["./test/integration_test"]'

  # Step 3: Test codecov package
  test-codecov-unit:
    needs: detect-changes
    if: needs.detect-changes.outputs.codecov == 'true'
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_uv_run_test.yaml@develop
    with:
      test_type: 'unit-test'
      project_name: 'codecov'
      test_working_directory: './test-coverage-mcp-codecov'
      test_folder: './test/unit_test'
      all_test_items_paths: '["./test/unit_test"]'

  # Step 4: Organize & upload coverage (per package, per test type)
  coverage-core:
    needs: [test-core-unit, test-core-integration]
    if: always() && needs.detect-changes.outputs.core == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_organize_test_cov_reports.yaml@develop
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'

  upload-coverage-core:
    needs: coverage-core
    if: always() && needs.detect-changes.outputs.core == 'true'
    strategy:
      matrix:
        test_type: ['unit-test', 'integration-test']
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_upload_test_cov_report.yaml@develop
    with:
      test_type: ${{ matrix.test_type }}
      project_name: 'core'
      test_working_directory: './test-coverage-mcp'
      upload-to-codecov: true
      codecov_flags: 'core,${{ matrix.test_type }}'
      codecov_name: 'test-coverage-mcp-core-${{ matrix.test_type }}'
    secrets:
      codecov_token: ${{ secrets.CODECOV_TOKEN }}

  # Step 5: SonarQube scan (uses multi-module config from Phase 1.5)
  sonarqube:
    needs: [upload-coverage-core, test-codecov-unit]
    if: always()
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_sonarqube_scan.yaml@develop
    secrets:
      sonar_token: ${{ secrets.SONAR_TOKEN }}
```

**Key workflow features**:
- Smart change detection (only test what changed)
- Parallel test execution per package
- Per-package coverage with `project_name` parameter
- Reuses SonarQube multi-module config from Phase 1.5 ✅

---

#### Task 0.5.4: Review and Update Existing Intent Configuration

**Existing file**: `.github/tag_and_release/intent.yaml` ✅

**Current Configuration Review**:

The intent configuration already exists and is well-configured. Here's what we need to **verify/update**:

**✅ Already Correct**:
```yaml
project:
  base_branch: master               # ✅ Correct - matches our decision
python:
  auth_method: token                # ✅ Using token auth
docker:
  health_check:
    port: 8000                      # ✅ Matches our server config
    path: "/health"                 # ✅ Standard health endpoint
artifacts:
  python: auto                      # ✅ Appropriate for monorepo
  docker: auto                      # ✅ Can build Docker from workspace
  docs:
    mode: auto
    sections: ["docs", "dev"]       # ✅ Multi-section docs
    strategy: always
```

**⚠️ Needs Attention**:
```yaml
project:
  name: ~                           # Currently unset (defaults to repo name)
  package_name: ~                   # Currently unset (defaults to repo name)
```

**Recommended Updates**:
```yaml
project:
  name: test-coverage-mcp           # Set explicitly for clarity
  package_name: test_coverage_mcp   # Main package name (core)
  base_branch: master               # ✅ Already correct
```

**Monorepo Considerations**:

The current `intent.yaml` is **single-package focused**. For monorepo with multiple publishable packages:

**Option A**: Keep as-is (simpler)
- `package_name: test_coverage_mcp` refers to core package only
- Codecov provider releases separately (its own `pyproject.toml`)
- Works fine since packages have independent versioning

**Option B**: Extend for monorepo (future enhancement)
- Could add `packages: ["test-coverage-mcp", "test-coverage-mcp-codecov"]`
- Would require reusable workflow updates to support multi-package releases
- Not needed for Phase 0.5

**Decision**: Use Option A - minimal changes needed

**Changes Required**:
1. Set `project.name` to `test-coverage-mcp`
2. Set `project.package_name` to `test_coverage_mcp`
3. Verify all other settings are appropriate

**No structural changes needed** - existing config works for monorepo!

---

#### Task 0.5.5: Update Documentation

**1. `.github/workflows/REUSABLE_WORKFLOWS.md`**
- Add monorepo-specific workflow examples
- Document `project_name` parameter usage
- Show change detection pattern

**2. `CONTRIBUTING.md`** (already has config hierarchy from Phase 1.5)
- Add "Running CI Locally" section
- Explain per-package testing workflow
- Document how to trigger CI for specific packages

**3. `README.md`**
- Update CI badge (consider per-package badges)
- Add monorepo CI/CD section

### 5. Validation & Testing

**After implementation, verify**:

| Check              | Description                       | Expected Result                                          |
|--------------------|-----------------------------------|----------------------------------------------------------|
| Change Detection   | Modify only core package files    | Only `test-core-*` jobs run                              |
| Change Detection   | Modify only codecov package files | Only `test-codecov-*` jobs run                           |
| Artifact Naming    | Check uploaded artifacts          | Format: `coverage_core_unit-test_ubuntu-latest_3.12`     |
| Codecov Reports    | View Codecov dashboard            | Separate flags: `core,unit-test` and `codecov,unit-test` |
| SonarQube          | Check SonarQube analysis          | Multi-module showing `core` and `codecov` modules        |
| Test Discovery     | Run pytest locally                | All tests discovered correctly                           |
| Parallel Execution | Watch GitHub Actions UI           | Jobs run in parallel per package                         |

**Manual Test Commands**:
```bash
# Test placeholder replacements worked
grep -r "<your_base_branch>" .github/workflows/
# Should return no results

# Test local package tests
cd test-coverage-mcp && uv run pytest test/unit_test/ -v
cd test-coverage-mcp-codecov && uv run pytest test/unit_test/ -v
```

---

### 6. Git Commit Plan

**Commits** (following simplified gitmoji style):
```bash
1. 🔧 ci: Replace placeholder variables in workflows
2. 🔧 ci: Update path triggers for monorepo structure  
3. ✨ ci: Create ci-monorepo.yaml with per-package testing
4. ✨ ci: Add change detection for conditional package testing
5. 📊 ci: Configure per-package coverage with project_name parameter
6. 🔧 ci: Create .github/tag_and_release/intent.yaml (optional)
7. 📝 docs: Update REUSABLE_WORKFLOWS.md with monorepo examples
8. 📝 docs: Add CI/CD section to CONTRIBUTING.md
9. ✅ ci: Verify monorepo CI workflow executes correctly
```

---

### 7. Summary & Next Steps

**Phase 0.5 Deliverables**:
- ✅ Monorepo-aware CI workflow with conditional package testing
- ✅ Per-package coverage reporting with proper artifact naming
- ✅ Smart change detection (only test what changed)
- ✅ Updated documentation for contributors
- ✅ Reuses Phase 1.5 SonarQube multi-module configuration

**What Makes This Better**:
- **Faster CI**: Parallel execution + conditional testing = 40-60% faster
- **Clear Failures**: Know exactly which package failed without digging
- **Better Coverage**: Per-package flags in Codecov for granular tracking
- **Scalable**: Easy to add new packages (just add to change detection)

**After Phase 0.5**:
- CI/CD infrastructure ready for monorepo ✅
- Ready for Phase 2: Advanced MCP server features
- Ready for future package additions (more providers)

**Configuration Decisions** ✅:
1. **Base branch**: `master` only (no `develop` to save CI resources)
2. **Python versions**: `["3.12", "3.13", "3.14"]` (full range for compatibility)
3. **Operating systems**: `["ubuntu-latest", "macos-latest"]` (no Windows)
4. **Intent config**: Already exists at `.github/tag_and_release/intent.yaml` - only needs minor updates

**Intent Configuration Updates Required**:
- Set `project.name: test-coverage-mcp` (currently `~`)
- Set `project.package_name: test_coverage_mcp` (currently `~`)
- Verify `base_branch: master` ✅ (already correct)
- All other settings appropriate for monorepo ✅

---

## Phase 1.5: Monorepo Tooling Configuration

**Goal**: Configure MyPy, Ruff, Pre-Commit for workspace packages

### Problem

Development tools need configuration to work across multiple workspace packages.

### Tasks

#### 1. MyPy Workspace Configuration

**Update `mypy.ini`**:
```ini
[mypy]
# Workspace packages
packages = test-coverage-mcp/src,test-coverage-mcp-codecov/src,test-coverage-mcp/test,test-coverage-mcp-codecov/test
exclude = (?x)(test/.*/.*\.py$)

show_traceback = True
warn_unused_configs = True
warn_redundant_casts = True
warn_unused_ignores = True
strict_equality = True
strict_concatenate = True

# Workspace support
namespace_packages = True
explicit_package_bases = True
```

#### 2. Ruff Workspace Configuration

**Update `ruff.toml`**:
```toml
line-length = 120
target-version = "py312"

exclude = [
    ".git", ".ruff_cache", "build", "dist",
    "test-coverage-mcp/build",
    "test-coverage-mcp-codecov/build",
]

[lint.isort]
known-first-party = ["test_coverage_mcp", "test_coverage_mcp_codecov"]

[lint.per-file-ignores]
"test-coverage-mcp/test/**/*.py" = ["S101", "ANN", "D"]
"test-coverage-mcp-codecov/test/**/*.py" = ["S101", "ANN", "D"]
"**/test/**/*.py" = ["S101", "ANN", "D"]
"**/__init__.py" = ["F401"]
```

#### 3. Pre-Commit Workspace Configuration

**Update `.pre-commit-config.yaml`**:
```yaml
exclude: '.github/|docs/'

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-yaml
        args: ['--unsafe']
      - id: debug-statements
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.14
    hooks:
      - id: ruff
        types_or: [python, pyi]
        args: [--fix]
      - id: ruff-format
        types_or: [python, pyi]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.1
    hooks:
      - id: mypy
        files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/.*\.py$
        args:
          - --config-file=mypy.ini
          - --ignore-missing-imports
          - --namespace-packages
          - --explicit-package-bases
        additional_dependencies: [
          types-PyYAML>=6.0.12.9,
          httpx, pydantic, fastapi,
        ]

  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.9.28
    hooks:
      - id: uv-lock
```

#### 4. CI Lint Workflow

**Status**: ⏭️ **DEFERRED** - Not implemented in Phase 1.5

**Reason**: [pre-commit.ci](https://pre-commit.ci) cloud service already provides automated linting validation on every PR. Creating a separate GitHub Actions workflow would duplicate this functionality and add unnecessary CI overhead.

**Decision Made**: 
- Pre-commit.ci handles all linting and type checking validation
- Developers use local pre-commit hooks for validation before pushing
- No separate CI workflow needed for linting
- Reduces CI complexity and execution time

**Previous Plan** (for reference):
```yaml
- name: Run Ruff
  run: |
    uv run ruff check .
    uv run ruff format --check .

- name: Run MyPy
  run: |
    uv run mypy test-coverage-mcp/src test-coverage-mcp/test
    uv run mypy test-coverage-mcp-codecov/src test-coverage-mcp-codecov/test

- name: Run Pre-Commit
  run: uv run pre-commit run --all-files
```

### Commits (with gitmoji)

```bash
🔧 mypy: Update for workspace packages
🔧 mypy: Add namespace packages support
🔧 ruff: Update exclusions for workspace
🔧 ruff: Add workspace known-first-party packages
🔧 ruff: Update per-file-ignores for all test dirs
🔧 pre-commit: Update MyPy for workspace
🔧 pre-commit: Add type checking dependencies
👷 ci: Update lint workflow for workspace
✅ Verify all tooling works across packages
📝 contributing: Document tooling setup
```

**Duration**: 2-3 hours  
**Validation**:
- ✅ `uv run pre-commit run --all-files` passes
- ✅ `uv run mypy test-coverage-mcp/src` passes
- ✅ `uv run ruff check .` passes
- ✅ pre-commit.ci validates on PR (no separate CI workflow needed)

**Documentation Updates**:
- `CONTRIBUTING.md`: Development tooling setup section
- `docs/contents/guides/development-setup.md`: Detailed tooling guide

---

## Phase 2: Domain Models & Provider Contracts

**Goal**: Define core abstractions and type system

### Tasks

1. **Define domain enums**
   - `ProviderCapability` (14 capabilities from spec)
   - `SupportLevel` (basic, enhanced, advanced)
   - `AnalysisDepth` (repo, file, segment, test-run, config-aware)
   - `RiskLevel` (low, medium, high, critical)

2. **Define provider contracts**
   - `CoverageProvider` protocol/abstract base class
   - `ProviderHealth` model
   - `ProviderMetadata` model
   - Method signatures for all capabilities

3. **Define execution metadata**
   - `ExecutionMetadata` model (support_level, used_capabilities, etc.)
   - Degradation tracking fields
   - Provider versioning

4. **Define shared response base**
   - `ToolResponseBase` with summary, key_findings, recommended_next_actions
   - Confidence scoring
   - Limitations tracking

5. **Define core domain models**
   - `RepositoryCoverageSummary`
   - `FileCoverage`
   - `CoverageDelta`
   - `CoverageRegion` / `UncoveredRegion`
   - `TestRecommendation`
   - `ConfigDiagnosis`

### Commits (with gitmoji)

```bash
✨ Add ProviderCapability enum with 14 capabilities
✨ Add SupportLevel and AnalysisDepth enums
✨ Define CoverageProvider protocol
🏷️ Add type hints to provider contracts
✨ Add ExecutionMetadata model for transparency
✨ Add ToolResponseBase for consistent responses
✨ Define core coverage domain models
✅ Add domain model validation tests
📝 architecture: Document domain model design
📝 contracts: Add provider specification
```

**Duration**: 6-8 hours  
**Files**: `packages/test-coverage-mcp/src/domain/` package

---

## Phase 3: Provider Registry & Discovery

**Goal**: Implement plugin discovery and provider management

### Tasks

1. **Implement ProviderRegistry**
   - Singleton pattern for global registry
   - Provider registration API
   - Provider lookup by name
   - Default provider resolution
   - Health check aggregation

2. **Implement plugin discovery**
   - Entry point scanning (`test_coverage_mcp.providers`)
   - Dynamic loading with error handling
   - Plugin metadata extraction
   - Version compatibility checking

3. **Add provider lifecycle**
   - Initialization hooks
   - Configuration injection
   - Health monitoring
   - Graceful shutdown

4. **Add configuration model**
   - Pydantic-Settings based config
   - Environment variable mapping
   - Provider-specific sections
   - Validation rules

### Commits (with gitmoji)

```bash
✨ registry: Implement ProviderRegistry with singleton
✨ registry: Add plugin discovery via entry points
✨ registry: Add provider lifecycle management
✨ config: Add configuration model with Pydantic-Settings
🔒 config: Use Pydantic-Settings for token management
✅ registry: Add tests with mock providers
✅ registry: Add plugin discovery integration tests
📝 architecture: Document plugin system
📝 guides: Add configuration with examples
```

**Duration**: 6-8 hours  
**Files**: `test-coverage-mcp/src/test_coverage_mcp/registry/`

**Documentation Updates**:
- `docs/contents/architecture/plugin-system.md`: Plugin discovery mechanism
- `docs/contents/guides/configuration.md`: Configuration with env vars
- `README.md`: Quick start configuration section

---

## Phase 4: Codecov Provider - Foundation

**Goal**: Implement Codecov API client and DTOs

### Tasks

1. **Design Codecov DTOs**
   - Map to Codecov API response structures
   - Repository, Commit, Coverage, Compare DTOs
   - Component, Flag, Upload DTOs
   - Test Results DTOs

2. **Implement Codecov API client**
   - httpx-based async client
   - Authentication (bearer token)
   - Rate limiting awareness
   - Error handling and retries
   - Endpoint methods for all capabilities

3. **Implement DTO-to-domain mappers**
   - Codecov DTOs → Core domain models
   - Handle missing/optional fields
   - Preserve provider-specific enrichments
   - Loss-less transformation where possible

4. **Implement CodecovProvider adapter**
   - Implement `CoverageProvider` protocol
   - Capability declaration (all 14 for advanced)
   - Health check implementation
   - Method implementations delegating to client

### Commits (with gitmoji)

```bash
✨ codecov: Add API response DTOs
🏷️ codecov: Add type hints to all DTOs
✨ codecov: Implement httpx-based API client
🔒 codecov: Add bearer token authentication
⚡ codecov: Implement rate limit handling with retry
✨ codecov: Implement DTO-to-domain mappers
✨ codecov: Implement CodecovProvider adapter
✅ codecov: Add API client unit tests with mocks
✅ codecov: Add integration tests for live API
📝 codecov: Add provider documentation
📝 codecov: Add setup guide with token config
```

**Duration**: 10-12 hours  
**Files**: `test-coverage-mcp-codecov/src/test_coverage_mcp_codecov/`

**Documentation Updates**:
- `test-coverage-mcp-codecov/README.md`: Provider-specific documentation
- `docs/contents/providers/codecov.md`: Codecov capabilities and setup
- `docs/contents/guides/provider-setup.md`: Provider installation guide

---

## Phase 5: Coverage Intelligence Services - Tier 1

**Goal**: Implement foundational intelligence services

### Tasks

1. **ProviderDiscoveryService**
   - List installed providers
   - Health aggregation
   - Capability matrix generation
   - Default provider selection

2. **RepositoryHealthService**
   - Aggregate coverage metrics
   - Trend analysis (if supported)
   - Risk identification
   - Next actions generation
   - Multi-provider fallback logic

3. **CoverageComparisonService**
   - Ref-to-ref comparison
   - Delta calculation
   - Regression/improvement detection
   - Component/flag deltas (if supported)

### Commits (with gitmoji)

```bash
✨ services: Implement ProviderDiscoveryService
✨ services: Implement RepositoryHealthService
⚡ services: Add caching for health metrics
✨ services: Implement CoverageComparisonService
🏷️ services: Add comprehensive type hints
✅ services: Add unit tests with mock providers
✅ services: Add integration tests with Codecov
📝 architecture: Document service layer
📝 api: Add service API reference
```

**Duration**: 8-10 hours  
**Files**: `test-coverage-mcp/src/test_coverage_mcp/services/`

**Documentation Updates**:
- `docs/contents/architecture/services.md`: Service layer design
- `docs/contents/api/services.md`: Service API reference
- `CONTRIBUTING.md`: How to add new services

---

## Phase 6: MCP Facade - Bootstrap Tools

**Goal**: Implement first 3 MCP tools using FastMCP

### Tasks

1. **Set up FastMCP server**
   - Initialize FastMCP app
   - Configure tool exposure
   - Add error handling middleware
   - Add request/response logging

2. **Tool: list_coverage_providers**
   - Input: `include_capabilities`, `include_health`
   - Output: Provider list with metadata
   - Leverage ProviderDiscoveryService

3. **Tool: describe_coverage_provider**
   - Input: `provider_name`
   - Output: Capability matrix, limitations
   - Leverage ProviderDiscoveryService

4. **Tool: get_repository_test_health**
   - Input: `repo_slug`, `provider`, `ref`
   - Output: Health summary with ExecutionMetadata
   - Leverage RepositoryHealthService

### Commits (with gitmoji)

```bash
✨ mcp: Initialize FastMCP server with configuration
🔧 mcp: Configure FastMCP tool generation
✨ mcp: Add list_coverage_providers tool
✨ mcp: Add describe_coverage_provider tool
✨ mcp: Add get_repository_test_health tool
🏷️ mcp: Add tool input/output type hints
✅ mcp: Add tool integration tests
📝 mcp-tools: Document tool schemas and usage
📝 mcp-tools: Add tool catalog with examples
```

**Duration**: 6-8 hours  
**Files**: `test-coverage-mcp/src/test_coverage_mcp/mcp/tools/`

**Documentation Updates**:
- `docs/contents/mcp-tools/overview.md`: MCP tools introduction
- `docs/contents/mcp-tools/list-providers.md`: Tool 1 reference
- `docs/contents/mcp-tools/describe-provider.md`: Tool 2 reference
- `docs/contents/mcp-tools/repository-health.md`: Tool 3 reference
- `README.md`: Add quick tool usage examples

---

## Phase 7: MCP Facade - Commit & Comparison Tools

**Goal**: Add commit and comparison MCP tools

### Tasks

1. **Tool: get_commit_coverage_summary**
   - Input: `repo_slug`, `provider`, `commit_sha`
   - Output: Totals, file breakdown, uploads metadata
   - Service: Direct provider call with enrichment

2. **Tool: compare_coverage_between_refs**
   - Input: `repo_slug`, `provider`, `base_ref`, `head_ref`
   - Output: Delta summary with ExecutionMetadata
   - Leverage CoverageComparisonService

### Commits (with gitmoji)

```bash
✨ mcp: Add get_commit_coverage_summary tool
✨ mcp: Add compare_coverage_between_refs tool
🏷️ mcp: Add type hints for comparison tools
✅ mcp: Add comparison tool tests with fixtures
📝 mcp-tools: Add commit summary reference
📝 mcp-tools: Add comparison tool reference
```

**Duration**: 4-6 hours

**Documentation Updates**:
- `docs/contents/mcp-tools/commit-summary.md`: Tool 4 reference
- `docs/contents/mcp-tools/compare-refs.md`: Tool 5 reference

---

## Phase 8: Coverage Intelligence Services - Tier 2

**Goal**: Implement advanced analysis services

### Tasks

1. **CoverageRiskAnalysisService**
   - PR risk scoring
   - High-risk file identification
   - Config vs. missing tests detection
   - Limitation awareness

2. **CoverageGapDiscoveryService**
   - Changed code analysis
   - Uncovered region detection
   - Partially covered region analysis
   - Pending analysis handling

### Commits (with gitmoji)

```bash
✨ services: Implement CoverageRiskAnalysisService
✨ services: Add PR risk scoring algorithm
✨ services: Implement CoverageGapDiscoveryService
🐛 services: Handle pending analysis states correctly
🏷️ services: Add type hints for risk and gap models
✅ services: Add risk analysis tests with edge cases
✅ services: Add gap discovery tests with pending states
📝 architecture: Document risk scoring methodology
📝 guides: Add gap discovery service guide
```

**Duration**: 8-10 hours

**Documentation Updates**:
- `docs/contents/architecture/risk-analysis.md`: Risk scoring algorithm
- `docs/contents/guides/pending-states.md`: Handling pending analysis

---

## Phase 9: MCP Facade - PR Analysis Tools

**Goal**: Add PR-focused analysis tools

### Tasks

1. **Tool: find_untested_changed_code**
   - Input: `repo_slug`, `provider`, `base_ref`, `head_ref`
   - Output: Uncovered regions with risk levels
   - Leverage CoverageGapDiscoveryService
   - Handle `pending` state from Codecov impacted files

2. **Tool: analyze_pr_coverage_risk**
   - Input: `repo_slug`, `provider`, `base_ref`, `head_ref`
   - Output: Risk assessment with recommendations
   - Leverage CoverageRiskAnalysisService

### Commits (with gitmoji)

```bash
✨ mcp: Add find_untested_changed_code tool
✨ mcp: Add analyze_pr_coverage_risk tool
🐛 mcp: Handle pending states in PR tools
🏷️ mcp: Add PR analysis input/output types
✅ mcp: Add PR tool tests with pending scenarios
✅ mcp: Add edge case tests for untested code
📝 mcp-tools: Add find_untested_changed_code reference
📝 mcp-tools: Add analyze_pr_coverage_risk reference
📝 workflows: Add PR review guide with examples
```

**Duration**: 6-8 hours

**Documentation Updates**:
- `docs/contents/mcp-tools/find-untested-code.md`: Tool 6 reference
- `docs/contents/mcp-tools/analyze-pr-risk.md`: Tool 7 reference
- `docs/contents/workflows/pr-review.md`: PR review workflow examples

---

## Phase 10: Coverage Intelligence Services - Tier 3

**Goal**: Implement recommendation and diagnostic services

### Tasks

1. **CoverageConfigDiagnosisService**
   - Config retrieval and parsing
   - Over-included path detection
   - Missing exclusion suggestions
   - Threshold review
   - Component/flag scoping review

2. **TestRecommendationService**
   - Test gap identification
   - Test type suggestions (unit, integration, edge cases)
   - Priority ranking
   - Scenario generation
   - Rationale explanation

3. **ExcludableCodeCandidateService**
   - Generated code detection
   - Vendor/migration path detection
   - Zero-hit signal analysis
   - Confidence scoring
   - Human validation flags

### Commits (with gitmoji)

```bash
✨ services: Implement CoverageConfigDiagnosisService
✨ services: Add config validation logic
✨ services: Implement TestRecommendationService
✨ services: Add test scenario generation
✨ services: Implement ExcludableCodeCandidateService
🔒 services: Add conservative candidate detection
🏷️ services: Add type hints for all models
✅ services: Add config diagnosis tests
✅ services: Add test recommendation tests
✅ services: Add excludable code tests with edge cases
📝 architecture: Document config diagnosis methodology
📝 guides: Add test recommendation strategies
📝 guides: Document excludable code detection limits
```

**Duration**: 10-12 hours

**Documentation Updates**:
- `docs/contents/architecture/config-diagnosis.md`: Diagnosis logic
- `docs/contents/guides/test-recommendations.md`: How recommendations work
- `docs/contents/guides/excludable-code.md`: Conservative detection approach

---

## Phase 11: MCP Facade - Advanced Analysis Tools

**Goal**: Complete remaining 4 MCP tools

### Tasks

1. **Tool: find_low_coverage_files**
   - Input: `repo_slug`, `provider`, `ref`, `threshold`, `limit`
   - Output: Ranked files with improvement suggestions
   - Service: Provider query + heuristic ranking

2. **Tool: diagnose_coverage_configuration**
   - Input: `repo_slug`, `provider`
   - Output: Config review with recommendations
   - Leverage CoverageConfigDiagnosisService

3. **Tool: recommend_test_plan**
   - Input: `repo_slug`, `provider`, `target` (repo/PR/file)
   - Output: Test design brief (not code)
   - Leverage TestRecommendationService

4. **Tool: identify_excludable_code_candidates**
   - Input: `repo_slug`, `provider`, `ref`
   - Output: Conservative exclusion candidates
   - Leverage ExcludableCodeCandidateService

### Commits (with gitmoji)

```bash
✨ mcp: Add find_low_coverage_files tool
✨ mcp: Add diagnose_coverage_configuration tool
✨ mcp: Add recommend_test_plan tool
✨ mcp: Add identify_excludable_code_candidates tool
🏷️ mcp: Add type hints for all advanced tools
✅ mcp: Add low coverage files tool tests
✅ mcp: Add config diagnosis tool tests
✅ mcp: Add test plan recommendation tests
✅ mcp: Add excludable code tool tests
📝 mcp-tools: Add find_low_coverage_files reference
📝 mcp-tools: Add diagnose_coverage_configuration reference
📝 mcp-tools: Add recommend_test_plan reference
📝 mcp-tools: Add identify_excludable_code_candidates reference
📝 mcp-tools: Update catalog with all 11 tools
```

**Duration**: 8-10 hours

**Documentation Updates**:
- `docs/contents/mcp-tools/low-coverage-files.md`: Tool 8 reference
- `docs/contents/mcp-tools/diagnose-config.md`: Tool 9 reference
- `docs/contents/mcp-tools/recommend-tests.md`: Tool 10 reference
- `docs/contents/mcp-tools/excludable-code.md`: Tool 11 reference
- `docs/contents/mcp-tools/catalog.md`: Complete tool catalog
- `README.md`: Update with all 11 tools overview

---

## Phase 12: CLI Implementation

**Goal**: Build production-ready CLI

### Tasks

1. **CLI framework setup**
   - Use Click or Typer for CLI
   - Command group structure
   - Global options (--verbose, --config)
   - Error handling and user-friendly messages

2. **Command: serve**
   - `test-coverage-mcp serve`
   - Options: `--transport stdio|http`, `--provider auto|codecov`
   - Start FastMCP server with selected transport
   - Environment validation
   - Graceful shutdown

3. **Command: providers**
   - `test-coverage-mcp providers list`
   - `test-coverage-mcp providers describe <name>`
   - Leverage ProviderDiscoveryService
   - Pretty-printed output

4. **Command: doctor**
   - `test-coverage-mcp doctor`
   - Check environment variables
   - Validate tokens/authentication
   - Test provider connectivity
   - Check plugin loading
   - Report health status

5. **Configure console script**
   - Update `pyproject.toml` entry point
   - Add shell completion support

### Commits (with gitmoji)

```bash
✨ cli: Add CLI framework with Click/Typer
🔧 pyproject: Configure CLI entry points
✨ cli: Implement serve command with stdio/http transport
✨ cli: Implement providers list command
✨ cli: Implement providers describe command
✨ cli: Implement doctor command with health checks
🏷️ cli: Add type hints to CLI commands
✨ cli: Add shell completion support
✅ cli: Add command tests
📝 cli: Add usage documentation
📝 cli: Add command reference
📝 deployment: Add CLI deployment guide
```

**Duration**: 8-10 hours  
**Files**: `test-coverage-mcp/src/test_coverage_mcp/cli/`

**Documentation Updates**:
- `docs/contents/cli/overview.md`: CLI introduction
- `docs/contents/cli/serve.md`: Serve command reference
- `docs/contents/cli/providers.md`: Provider commands reference
- `docs/contents/cli/doctor.md`: Doctor command reference
- `docs/contents/deployment/cli.md`: CLI deployment guide
- `README.md`: Add CLI quick start examples

---

## Phase 13: Docker Support

**Goal**: Create production Docker images

### Tasks

1. **Multi-stage Dockerfile**
   - Base stage with Python + uv
   - Builder stage for dependencies
   - Runtime stage (minimal)
   - Support both `core` and `full` variants

2. **Docker configuration**
   - `.dockerignore` optimization
   - Health check endpoint
   - Environment variable documentation
   - Volume mounts for config

3. **Docker Compose examples**
   - Development setup
   - Production setup with secrets
   - Multi-provider configuration

4. **GitHub Actions for image builds**
   - Build on tag push
   - Push to ghcr.io
   - Tag strategy (latest, version, core/full)

### Commits (with gitmoji)

```bash
🐳 Add multi-stage Dockerfile for core variant
🐳 Add full variant with all providers
⚡ docker: Optimize layer caching
🔧 Add .dockerignore optimization
✨ web: Add health check endpoint at /health
🐳 Add Docker Compose examples
🐳 Add production Docker Compose config
👷 Add GitHub Actions for Docker builds
👷 Configure ghcr.io publishing
📝 deployment: Add Docker deployment guide
📝 deployment: Add environment variables reference
📝 deployment: Add Docker troubleshooting guide
```

**Duration**: 6-8 hours

**Documentation Updates**:
- `docs/contents/deployment/docker.md`: Docker deployment guide
- `docs/contents/deployment/docker-compose.md`: Compose examples
- `docs/contents/deployment/environment-variables.md`: Env var reference
- `README.md`: Add Docker quick start
- `docker/README.md`: Docker-specific documentation

---

## Phase 14: Testing, Documentation, Release Prep

**Goal**: Complete testing coverage and documentation

### Tasks

1. **Test coverage improvements**
   - Unit tests: 80%+ coverage target
   - Integration tests for all services
   - E2E tests for all 11 MCP tools
   - Contract tests for provider interface
   - Mock provider for testing

2. **Documentation**
   - Architecture overview
   - Provider plugin development guide
   - MCP tool reference (all 11 tools)
   - Configuration guide
   - Deployment guide (CLI + Docker)
   - Troubleshooting guide
   - API reference (if exposing REST API)

3. **Example configurations**
   - `.env.example` templates
   - MCP client configurations (Claude Desktop, etc.)
   - Provider-specific setup guides

4. **Release preparation**
   - CHANGELOG.md
   - Version bump strategy
   - Package publishing workflow
   - GitHub release notes

### Commits (with gitmoji)

```bash
✅ Add comprehensive unit test suite
✅ Achieve 80%+ unit test coverage
✅ Add integration tests for all services
✅ Add E2E tests for all 11 MCP tools
✅ Add contract tests for provider interface
✅ Add mock provider for testing
📝 architecture: Complete documentation
📝 guides: Add provider plugin development guide
📝 mcp-tools: Complete reference for all 11 tools
📝 deployment: Add guides for CLI and Docker
📝 Add troubleshooting guide
📝 Add FAQ documentation
📝 Add example configurations
📝 Add CHANGELOG.md for v1.0.0
🔖 Prepare v1.0.0 release
📝 Update README with badges and links
```

**Duration**: 12-16 hours

**Documentation Updates**:
- `docs/contents/architecture/overview.md`: Complete architecture
- `docs/contents/guides/plugin-development.md`: Plugin authoring guide
- `docs/contents/mcp-tools/`: Complete all 11 tool references
- `docs/contents/deployment/`: Complete deployment guides
- `docs/contents/troubleshooting.md`: Common issues and solutions
- `docs/contents/faq.md`: Frequently asked questions
- `CHANGELOG.md`: Version 1.0.0 release notes
- `README.md`: Complete with badges, links, examples

---

## Summary: Phase Overview

| Phase | Focus | Duration | Key Deliverables | Docs |
|-------|-------|----------|------------------|------|
| 0 | Analysis | 1-2h | Codebase audit, migration plan | Analysis doc |
| 0.5 | CI/CD & SonarQube | 3-4h | Fix placeholders, test paths, SonarQube modules | CI/CD + SQ guide |
| 1 | Workspace | 6-8h | Monorepo structure, workspace config | Architecture docs |
| 1.5 | Tooling Config | 2-3h | MyPy, Ruff, Pre-Commit for workspace | Dev setup guide |
| 2 | Domain Models | 6-8h | Contracts, enums, domain models | Contract specs |
| 3 | Registry | 6-8h | Plugin discovery, provider management | Plugin guide |
| 4 | Codecov Provider | 10-12h | API client, DTOs, adapter | Provider docs |
| 5 | Services Tier 1 | 8-10h | Discovery, Health, Comparison services | Service API docs |
| 6 | MCP Tools 1-3 | 6-8h | Provider tools, health tool | Tool references |
| 7 | MCP Tools 4-5 | 4-6h | Commit, comparison tools | Tool references |
| 8 | Services Tier 2 | 8-10h | Risk, gap discovery services | Risk analysis docs |
| 9 | MCP Tools 6-7 | 6-8h | PR analysis tools | PR workflow guide |
| 10 | Services Tier 3 | 10-12h | Config, recommendation services | Strategy docs |
| 11 | MCP Tools 8-11 | 8-10h | Advanced analysis tools | Complete catalog |
| 12 | CLI | 8-10h | Full CLI with serve/providers/doctor | CLI reference |
| 13 | Docker | 6-8h | Dockerfile, compose, CI | Docker guide |
| 14 | Testing & Docs | 12-16h | 80%+ coverage, complete docs | Full doc site |
| 15 | Docs Deployment | 4-6h | Live docs site on GitHub Pages | Doc site live |

**Total Estimated Duration**: 117-159 hours (~3-4 weeks full-time)

**Documentation Deliverables**: ~50+ documentation files across all phases

**Breakdown by Category**:
- **Architecture docs**: ~8 files
- **MCP tool references**: 11+ files (one per tool + overview + catalog)
- **Provider docs**: ~5 files
- **Deployment guides**: ~6 files
- **CLI reference**: ~4 files
- **Guides & tutorials**: ~10 files
- **API reference**: ~6 files

---

## Phase 15: Documentation Site Deployment

**Goal**: Deploy comprehensive Docusaurus documentation site

### Tasks

1. **Finalize Docusaurus configuration**
   - Update `docusaurus.config.ts` with project details
   - Configure navigation and sidebars
   - Add search functionality
   - Configure versioning for future releases

2. **Build and verify documentation**
   - Build static site locally
   - Verify all internal links
   - Test all code examples
   - Check mobile responsiveness

3. **Set up GitHub Pages deployment**
   - Configure GitHub Actions for docs deployment
   - Set up custom domain (if applicable)
   - Configure CNAME records

4. **Add documentation metadata**
   - Add Open Graph tags
   - Add social media cards
   - Add analytics (if desired)
   - Add feedback mechanism

### Commits (with gitmoji)

```bash
📝 docusaurus: Update config with project info
📝 docusaurus: Configure documentation navigation
🔍 docusaurus: Add search functionality
✨ docusaurus: Add versioning support
👷 Add GitHub Actions for docs deployment
🚀 Configure GitHub Pages deployment
📝 docusaurus: Add Open Graph metadata
📝 docusaurus: Add social media cards
✅ Verify all documentation links
🐛 docs: Fix broken links
📝 docusaurus: Add feedback form
```

**Duration**: 4-6 hours

**Documentation Updates**:
- Live documentation site at GitHub Pages
- Versioned documentation for releases
- Searchable documentation

---

## Git Branching Strategy

### Recommended Approach

**Feature branch per phase** with regular merges to `main`:

```
main
  ├── feature/phase-1-workspace-restructure
  ├── feature/phase-2-domain-models
  ├── feature/phase-3-provider-registry
  └── ... (one branch per phase)
```

### Branch Naming Convention

- `feature/phase-N-short-description`
- `fix/issue-description`
- `docs/section-name`
- `test/component-name`

### Merge Strategy

- **Squash and merge** for cleaner history (one commit per phase)
- OR **Rebase and merge** to preserve detailed commits
- Decision based on team preference

### Commit Frequency Within Phases

- **Commit after each task** (see individual phase commits)
- Keep commits atomic and focused
- Each commit should pass tests
- Use descriptive commit messages

---

## Risk Mitigation

### Technical Risks

1. **FastMCP limitations**
   - Mitigation: Prototype in Phase 0
   - Fallback: Direct MCP SDK usage

2. **Plugin discovery complexity**
   - Mitigation: Use standard entry points
   - Fallback: Manual registration

3. **Codecov API changes**
   - Mitigation: Version pinning, error handling
   - Fallback: Graceful degradation

### Project Risks

1. **Scope creep**
   - Mitigation: Stick to 11 tools in v1
   - Defer Coveralls to Phase 3 (post-MVP)

2. **Testing time**
   - Mitigation: TDD from Phase 2
   - Parallel test development

3. **Documentation lag**
   - Mitigation: Document during implementation
   - Reserve Phase 14 for polish

---

## Success Criteria

### MVP (Phase 0.5-9)

✅ CI/CD compatibility verified  
✅ Workspace structure working  
✅ Codecov provider functional  
✅ 7 core MCP tools implemented  
✅ CLI `serve` command working  
✅ 70%+ test coverage  
✅ Core documentation complete

### Full v1.0 (Phase 0.5-15)

✅ All 15 phases complete  
✅ All 11 MCP tools functional  
✅ Complete CLI (serve, providers, doctor)  
✅ Docker images published to ghcr.io  
✅ 80%+ test coverage across all packages  
✅ Comprehensive documentation (50+ files)  
✅ Live documentation site deployed  
✅ Example configurations for all scenarios  
✅ PyPI package published  
✅ Plugin architecture validated with Codecov provider  
✅ CI/CD fully integrated with workspace structure

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Adjust timelines** based on team capacity
3. **Create GitHub issues** for each phase
4. **Set up project board** with phase tracking
5. **Begin Phase 0** analysis
6. **Schedule weekly reviews** to adjust plan based on learnings

---

## Appendix: Key Design Decisions

### Why FastMCP?

- Leverages Python type hints for tool generation
- Reduces boilerplate
- Aligns with MCP best practices
- Automatic schema generation
- Better developer experience

### Why uv workspaces?

- Native Python workspace support
- Fast dependency resolution
- Better than manual path management
- Officially supported pattern
- Allows independent package versioning
- Simplifies monorepo management

### Why entry points for plugins?

- Standard Python plugin mechanism
- No custom loader needed
- Works with all package installers (pip, uv, poetry)
- Easy for plugin authors
- Auto-discovery without configuration
- Battle-tested pattern in Python ecosystem

### Why three-layer architecture?

- **Separation of concerns**: Provider vs. Intelligence vs. MCP
- **Stability**: MCP tools don't change when providers change
- **Testability**: Each layer independently testable
- **Extensibility**: Add providers without touching services
- **Maintainability**: Clear boundaries reduce complexity

### Why capability-driven model?

- **Provider transparency**: LLMs know what's supported
- **Graceful degradation**: Works with basic providers
- **Future-proof**: New capabilities added without breaking tools
- **User clarity**: ExecutionMetadata explains limitations
- **Better UX**: Users understand what they're getting

### Why gitmoji commit conventions?

- **Visual clarity**: Emoji provides instant context
- **Human-readable**: Easy to scan commit history
- **Categorization**: Natural grouping of commits
- **Fun**: Makes development more enjoyable
- **Standardized**: Well-documented at gitmoji.dev

### Why align with CI/CD template structure?

- **Less maintenance**: Leverage battle-tested workflows
- **Consistency**: Familiar to contributors
- **Proven patterns**: Template used across multiple projects
- **Auto-updates**: Benefit from template improvements
- **Community**: Easier onboarding for new contributors

### Why comprehensive documentation?

- **Open source requirement**: Critical for adoption
- **Developer experience**: Reduces friction
- **Maintenance**: Future contributors understand design
- **Professional**: Builds trust and credibility
- **Search**: Documentation helps users find solutions
- **Examples**: Real-world usage accelerates adoption

---

## Quick Reference: Gitmoji Cheat Sheet

For easy copy-paste during development:

```bash
# Most frequently used
✨ :sparkles:              # New features → ✨ Add feature OR ✨ scope: Add feature
📝 :memo:                  # Documentation → 📝 Update docs OR 📝 scope: Update docs
🐛 :bug:                   # Bug fixes → 🐛 Fix issue OR 🐛 scope: Fix issue
✅ :white_check_mark:      # Tests → ✅ Add tests OR ✅ scope: Add tests
🔧 :wrench:                # Configuration → 🔧 Update config OR 🔧 tool: Update config
♻️ :recycle:               # Refactoring → ♻️ Refactor code OR ♻️ scope: Refactor
🏗️ :building_construction: # Architecture → 🏗️ Restructure OR 🏗️ scope: Restructure
🏷️ :label:                 # Types → 🏷️ Add types OR 🏷️ scope: Add types
🚚 :truck:                 # Move/rename → 🚚 Move files OR 🚚 scope: Rename
👷 :construction_worker:   # CI/CD → 👷 Update CI OR 👷 tool: Update workflow
🔒 :lock:                  # Security → 🔒 Secure secrets OR 🔒 scope: Fix security
⚡ :zap:                   # Performance → ⚡ Optimize OR ⚡ scope: Cache results
➕ :heavy_plus_sign:       # Add dependency → ➕ Add httpx OR ➕ scope: Add dep
🐳 :whale:                 # Docker → 🐳 Add Dockerfile OR 🐳 Add compose config
🚀 :rocket:                # Deployment → 🚀 Deploy to prod OR 🚀 Configure deploy
🔖 :bookmark:              # Release → 🔖 Release v1.0.0 OR 🔖 Bump to v1.0.1

# Format rules:
# ✅ Correct: ✨ Add new feature
# ✅ Correct: ✨ codecov: Implement API client
# ❌ Wrong:   ✨ feat: Add new feature (redundant "feat")
# ❌ Wrong:   ✨ feat(codecov): Add client (redundant "feat", use scope without parens)
```

---

## Implementation Checklist

Track your progress:

- [ ] **Phase 0**: Pre-implementation analysis complete
- [ ] **Phase 0.5**: CI/CD compatibility + SonarQube monorepo fixed
- [ ] **Phase 1**: Workspace restructure complete
- [ ] **Phase 1.5**: Tooling (MyPy, Ruff, Pre-Commit) configured
- [ ] **Phase 2**: Domain models implemented
- [ ] **Phase 3**: Provider registry working
- [ ] **Phase 4**: Codecov provider functional
- [ ] **Phase 5**: Tier 1 services implemented
- [ ] **Phase 6**: First 3 MCP tools working
- [ ] **Phase 7**: Tools 4-5 implemented
- [ ] **Phase 8**: Tier 2 services implemented
- [ ] **Phase 9**: Tools 6-7 (PR analysis) working
- [ ] **Phase 10**: Tier 3 services implemented
- [ ] **Phase 11**: Tools 8-11 complete (all 11 tools done)
- [ ] **Phase 12**: CLI fully functional
- [ ] **Phase 13**: Docker images published
- [ ] **Phase 14**: Tests 80%+, docs complete
- [ ] **Phase 15**: Documentation site live
- [ ] **v1.0.0 Release**: PyPI package published

---

**Document Version**: 3.0  
**Last Updated**: 2026-04-02  
**Author**: Cascade AI  
**Status**: Ready for Review

**Changes from v2**:
- ✅ **Simplified gitmoji commit format**: Removed redundant type labels (e.g., `✨ Add feature` instead of `✨ feat: Add feature`)
- ✅ **Scoped commits**: Use `✨ scope: Description` for scoped commits (e.g., `✨ codecov: Add API client`)
- ✅ **Updated all 420+ commit examples** throughout all phases with new format
- ✅ **Added Phase 1.5**: Monorepo tooling configuration (MyPy, Ruff, Pre-Commit)
- ✅ **SonarQube monorepo setup**: Added module-based configuration in Phase 0.5
- ✅ **MyPy workspace config**: Namespace packages, explicit package bases
- ✅ **Ruff workspace config**: Known-first-party packages, per-file ignores
- ✅ **Pre-Commit workspace config**: Files pattern for workspace packages
- ✅ **Total phases**: 16 (0, 0.5, 1, 1.5, 2-15)
- ✅ **Total duration**: 117-159 hours

**Changes from v1**:
- ✅ Fixed workspace structure (packages at root, not in `packages/` subdirectory)
- ✅ Added gitmoji commit conventions with comprehensive examples
- ✅ Integrated documentation updates into every phase
- ✅ Added Phase 0.5 for CI/CD compatibility analysis and migration
- ✅ Added Phase 15 for documentation site deployment
- ✅ Updated all file paths to reflect correct workspace structure
- ✅ Added documentation deliverables tracking (~50+ files)
- ✅ Enhanced success criteria with specific metrics
- ✅ Added gitmoji cheat sheet for quick reference
- ✅ Added implementation checklist for progress tracking
