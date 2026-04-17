# Monorepo Release Configuration Guide
## test-coverage-mcp Project

**Date**: April 7, 2026  
**Project**: test-coverage-mcp  
**Current Status**: UV Workspace Monorepo (2 packages)  
**Target**: Configure GitHub Actions release workflows for monorepo

---

## 📋 Project Structure Analysis

Your project is already a **UV workspace monorepo** with the following structure:

```
test-coverage-mcp/
├── pyproject.toml                        # Workspace root
│   └── [tool.uv.workspace]
│       └── members = ["test-coverage-mcp", "test-coverage-mcp-codecov"]
│
├── test-coverage-mcp/                    # Package 1: Core MCP server
│   ├── pyproject.toml
│   │   └── name = "test-coverage-mcp"
│   ├── src/
│   └── test/
│
└── test-coverage-mcp-codecov/            # Package 2: Codecov provider plugin
    ├── pyproject.toml
    │   └── name = "test-coverage-mcp-codecov"
    ├── src/
    └── test/
```

### Package Summary

| Package | Name | Type | Dependencies |
|---------|------|------|--------------|
| **Core** | `test-coverage-mcp` | MCP Server | FastAPI, Pydantic, MCP, HTTPx |
| **Codecov** | `test-coverage-mcp-codecov` | Provider Plugin | test-coverage-mcp (workspace), HTTPx |

---

## 🎯 Recommended Monorepo Configuration

### Step 1: Update `.github/tag_and_release/intent.yaml`

Replace your current single-project configuration with monorepo configuration:

```yaml
# Enhanced Monorepo Release Configuration
# This file controls release behavior for all packages in the monorepo

# === MONOREPO CONFIGURATION ===
# Define all packages in the monorepo
packages:
  # Core MCP Server Package
  - name: core                                    # Identifier for workflow (tag prefix)
    package_name: test-coverage-mcp               # PyPI package name
    working_directory: test-coverage-mcp          # Package source directory
    tag_prefix: core/                             # Git tag prefix (e.g., core/v1.0.0)
    
    # Release control
    release: true
    level: auto                                   # auto | patch | minor | major
    
    # Artifacts
    artifacts:
      python: auto                                # auto | force | skip
      docker: skip                                # Core doesn't have Dockerfile
      docs:
        mode: auto
        sections: ["docs"]
        strategy: changed
    
    # Python configuration
    python:
      auth_method: token                          # or 'oidc' for trusted publisher
    
    # Validation
    validation:
      version: "1.0.0-validation"
      test_version: "validation-test"
  
  # Codecov Provider Plugin Package
  - name: codecov                                 # Identifier for workflow
    package_name: test-coverage-mcp-codecov       # PyPI package name
    working_directory: test-coverage-mcp-codecov  # Package source directory
    tag_prefix: codecov/                          # Git tag prefix (e.g., codecov/v0.1.0)
    
    # Release control
    release: true
    level: auto
    
    # Artifacts
    artifacts:
      python: auto
      docker: skip                                # Plugin doesn't have Dockerfile
      docs: skip                                  # Plugin uses core's docs
    
    # Python configuration
    python:
      auth_method: token
    
    # Validation
    validation:
      version: "0.1.0-validation"
      test_version: "validation-test"

# === GLOBAL PROJECT SETTINGS ===
# These apply to all packages unless overridden
project:
  name: test-coverage-mcp                         # Repository name
  base_branch: master                             # Main branch

# === GIT CONFIGURATION ===
git:
  commit:
    name: "GitHub Actions Bot"
    email: "actions@github.com"

# === DOCUMENTATION CONFIGURATION ===
docs:
  paths:
    ci_cd: "docs/CI_CD.md"
    installation: "docs/INSTALLATION.md"
    readme: "README.md"
  preview:
    branch: "docs-preview"

notes: "Monorepo release with independent package versioning"
```

---

## 🚀 Workflow Configuration Options

You have **two approaches** for releasing packages:

### Option 1: Manual Package Release (Recommended for Start)

Use existing workflows with `package-name` parameter to release specific packages.

#### Release Core Package

```yaml
# .github/workflows/release-core.yml
name: Release Core Package

on:
  workflow_dispatch:
    inputs:
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

permissions:
  contents: write
  packages: write
  id-token: write

jobs:
  release:
    name: Release test-coverage-mcp (Core)
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_release_complete.yaml@master
    with:
      package-name: 'core'           # ← Monorepo package identifier
      level: ${{ inputs.level }}
      python: 'auto'
      docker: 'skip'                  # Core has no Dockerfile
      docs: 'auto'
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      TEST_PYPI_API_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

#### Release Codecov Plugin Package

```yaml
# .github/workflows/release-codecov.yml
name: Release Codecov Plugin

on:
  workflow_dispatch:
    inputs:
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

permissions:
  contents: write
  packages: write
  id-token: write

jobs:
  release:
    name: Release test-coverage-mcp-codecov
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_release_complete.yaml@master
    with:
      package-name: 'codecov'         # ← Monorepo package identifier
      level: ${{ inputs.level }}
      python: 'auto'
      docker: 'skip'
      docs: 'skip'                    # Plugin uses core's docs
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      TEST_PYPI_API_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

---

### Option 2: Automated Multi-Package Orchestrator

Use the orchestrator to release multiple packages automatically.

```yaml
# .github/workflows/release-monorepo.yml
name: Monorepo Multi-Package Release

on:
  workflow_dispatch:
    inputs:
      packages:
        description: 'Packages to release (JSON array, e.g., ["core", "codecov"]). Leave empty for auto-detect.'
        required: false
        default: '[]'
        type: string
      release-mode:
        description: 'Release mode'
        required: false
        default: 'sequential'
        type: choice
        options:
          - sequential  # Release one at a time (safer)
          - parallel    # Release simultaneously (faster)
      dry-run:
        description: 'Dry run - show what would be released'
        required: false
        default: false
        type: boolean

permissions:
  contents: write
  packages: write
  id-token: write

jobs:
  orchestrate-releases:
    name: Orchestrate Package Releases
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_monorepo_release_orchestrator.yaml@master
    with:
      packages: ${{ inputs.packages }}
      release-mode: ${{ inputs.release-mode }}
      dry-run: ${{ inputs.dry-run }}
    secrets: inherit
```

**Usage Examples**:
- **Auto-detect**: Leave packages empty → releases only changed packages
- **Specific packages**: `["core"]` → release only core
- **Multiple packages**: `["core", "codecov"]` → release both
- **Dry run**: Enable to see what would be released without actually releasing

---

## 🔄 Staging and Validation Workflows

### Staging Release (for testing)

```yaml
# .github/workflows/release-staging-core.yml
name: Staging Release - Core

on:
  workflow_dispatch:
    inputs:
      level:
        description: 'Release level'
        required: false
        default: 'patch'
        type: choice
        options:
          - patch
          - minor
          - major

permissions:
  contents: write
  packages: write
  id-token: write

jobs:
  staging:
    name: Staging Release - Core Package
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_release_staging_complete.yaml@master
    with:
      package-name: 'core'
      level: ${{ inputs.level }}
    secrets:
      PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      TEST_PYPI_API_TOKEN: ${{ secrets.TEST_PYPI_API_TOKEN }}
```

### Validation (dry run)

```yaml
# .github/workflows/release-validate-core.yml
name: Validate Release - Core

on:
  pull_request:
    branches:
      - master
    paths:
      - test-coverage-mcp/**
      - .github/tag_and_release/**
  workflow_dispatch:
    inputs:
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

permissions:
  contents: read
  packages: read
  id-token: write

jobs:
  validation:
    name: Validate Release - Core Package
    uses: Chisanan232/GitHub-Action_Reusable_Workflows-Python/.github/workflows/rw_release_validation_complete.yaml@master
    with:
      package-name: 'core'
      level: ${{ inputs.level }}
      python: 'auto'
      docker: 'skip'
      docs: 'auto'
```

---

## 📦 Expected Release Behavior

### Core Package Release

**When**: Trigger `release-core.yml` workflow

**Actions**:
1. ✅ Parse `intent.yaml` for `core` package configuration
2. ✅ Build Python package from `test-coverage-mcp/` directory
3. ✅ Run tests in `test-coverage-mcp/` directory
4. ✅ Bump version in `test-coverage-mcp/pyproject.toml`
5. ✅ Create git tag: `core/v1.0.0` (with `core/` prefix)
6. ✅ Publish to PyPI as `test-coverage-mcp`
7. ✅ Create GitHub release: "Core v1.0.0"

**Git Tags**:
```bash
core/v1.0.0
core/v1.0.1
core/v1.1.0
```

---

### Codecov Plugin Release

**When**: Trigger `release-codecov.yml` workflow

**Actions**:
1. ✅ Parse `intent.yaml` for `codecov` package configuration
2. ✅ Build Python package from `test-coverage-mcp-codecov/` directory
3. ✅ Run tests in `test-coverage-mcp-codecov/` directory
4. ✅ Bump version in `test-coverage-mcp-codecov/pyproject.toml`
5. ✅ Create git tag: `codecov/v0.1.0` (with `codecov/` prefix)
6. ✅ Publish to PyPI as `test-coverage-mcp-codecov`
7. ✅ Create GitHub release: "Codecov Plugin v0.1.0"

**Git Tags**:
```bash
codecov/v0.1.0
codecov/v0.1.1
codecov/v0.2.0
```

---

## 🔍 Tag Naming Convention

### Single-Project (Before)
```bash
v1.0.0
v1.0.1
v1.1.0
```

### Monorepo (After)
```bash
core/v1.0.0      # Core package releases
core/v1.0.1
core/v1.1.0

codecov/v0.1.0   # Codecov plugin releases
codecov/v0.1.1
codecov/v0.2.0
```

**Benefits**:
- ✅ Clear separation of package versions
- ✅ Independent versioning per package
- ✅ Easy to filter tags by package
- ✅ Standard monorepo practice

---

## 🎬 Migration Steps

### Phase 1: Update Configuration (Safe)

1. **Backup current `intent.yaml`**:
   ```bash
   cp .github/tag_and_release/intent.yaml .github/tag_and_release/intent.yaml.backup
   ```

2. **Update `intent.yaml`** with monorepo configuration (see Step 1 above)

3. **Test configuration parsing**:
   ```bash
   # This will validate your intent.yaml structure
   python -c "import yaml; yaml.safe_load(open('.github/tag_and_release/intent.yaml'))"
   ```

---

### Phase 2: Add Manual Release Workflows

4. **Create package-specific workflows**:
   ```bash
   # Core package
   touch .github/workflows/release-core.yml
   # Codecov package
   touch .github/workflows/release-codecov.yml
   ```

5. **Add workflow content** (see Option 1 examples above)

6. **Test with validation workflow**:
   - Create PR with changes
   - Trigger `release-validate-core.yml`
   - Verify builds and tests pass

---

### Phase 3: Test Release (Staging)

7. **Test staging release**:
   ```bash
   # Manually trigger staging workflow for core
   # Check:
   # - RC tag created: core/v1.0.0-rc.1
   # - TestPyPI upload successful
   # - No errors in workflow
   ```

8. **Verify artifacts**:
   ```bash
   # Install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ test-coverage-mcp
   ```

---

### Phase 4: Production Release

9. **Release first package**:
   ```bash
   # Trigger release-core.yml workflow
   # Verify:
   # - Tag: core/v1.0.0
   # - PyPI: test-coverage-mcp published
   # - GitHub Release created
   ```

10. **Release second package**:
    ```bash
    # Trigger release-codecov.yml workflow
    # Verify:
    # - Tag: codecov/v0.1.0
    # - PyPI: test-coverage-mcp-codecov published
    # - GitHub Release created
    ```

---

### Phase 5: Optional Orchestrator (Advanced)

11. **Add orchestrator workflow** (see Option 2 above)

12. **Test auto-detection**:
    ```bash
    # Make changes to core package
    # Trigger orchestrator with empty packages
    # Should auto-detect and release only core
    ```

---

## ⚠️ Important Considerations

### Version Management

**Independent Versioning** (Recommended):
- Each package has its own version in `pyproject.toml`
- Versions can differ (e.g., core at v2.0.0, codecov at v0.5.0)
- Each package releases independently

**Version File Locations**:
```
test-coverage-mcp/pyproject.toml            → version = "1.0.0"
test-coverage-mcp-codecov/pyproject.toml    → version = "0.1.0"
```

### Package Dependencies

**Current Dependency**:
```toml
# test-coverage-mcp-codecov/pyproject.toml
[tool.uv.sources]
test-coverage-mcp = { workspace = true }
```

**Recommendation**:
- Keep workspace dependency for development
- When releasing codecov plugin, ensure compatible core version is specified
- Consider adding version constraints in `dependencies`:
  ```toml
  dependencies = [
      "test-coverage-mcp>=1.0.0,<2.0.0",  # Compatible range
      "httpx>=0.28.1",
  ]
  ```

### Release Order

**Best Practice**:
1. **Release core first** → Establishes base version
2. **Release plugins after** → Can reference core's stable version

**Why**:
- Plugins depend on core
- Users install core, then plugins
- Maintains compatibility

---

## 🧪 Testing Checklist

Before production release:

- [ ] `intent.yaml` validates (no YAML errors)
- [ ] Config job parses correctly (check workflow logs)
- [ ] Python package builds from correct directory
- [ ] Tests run in correct directory
- [ ] Version bumps in correct `pyproject.toml`
- [ ] Git tags have correct prefix (`core/`, `codecov/`)
- [ ] PyPI packages published with correct names
- [ ] GitHub releases created with correct titles
- [ ] Codecov plugin installs with core dependency

---

## 📚 Additional Resources

### Documentation to Update

After configuration:

1. **README.md**: Add monorepo release instructions
2. **CONTRIBUTING.md**: Update release procedures
3. **Development docs**: Explain package structure

### Example Commands

```bash
# Check current tags
git tag -l "core/*"
git tag -l "codecov/*"

# Install specific versions
pip install test-coverage-mcp==1.0.0
pip install test-coverage-mcp-codecov==0.1.0

# Verify versions
python -c "import test_coverage_mcp; print(test_coverage_mcp.__version__)"
```

---

## 🤝 Support and Next Steps

### If You Need Help

1. **Validation issues**: Check `.github/tag_and_release/schema.json`
2. **Workflow errors**: Review workflow logs in GitHub Actions
3. **Tag conflicts**: Ensure tag prefixes are correct
4. **Build failures**: Verify working directories in intent.yaml

### Recommended Next Actions

1. ✅ Update `intent.yaml` with monorepo configuration
2. ✅ Create package-specific release workflows
3. ✅ Test with validation workflow
4. ✅ Test staging release for core package
5. ✅ Production release core package
6. ✅ Production release codecov package
7. ✅ Document new release process

---

## Summary

Your project is perfectly suited for monorepo workflows because it's already a UV workspace with 2 packages. The reusable workflows now support this pattern seamlessly with:

✅ Package-specific configuration via `intent.yaml`  
✅ Independent version management per package  
✅ Tag prefixes for clear package identification  
✅ Backward compatible (no breaking changes)  
✅ Flexible release strategies (manual or orchestrated)

Follow the migration steps, and you'll have a robust monorepo release system! 🚀
