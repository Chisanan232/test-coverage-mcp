# Pre-Commit Monorepo Redesign Plan

**Version**: 1.0  
**Date**: 2026-04-07  
**Status**: Planning - Awaiting Review

---

## 📋 Executive Summary

Redesign `.pre-commit-config.yaml` for monorepo architecture with:
- **Package-specific hooks** (backend Python packages)
- **Documentation hooks** (Docusaurus TypeScript/JavaScript frontend)
- **Workspace-level hooks** (shared configurations, scripts)
- **Optimized performance** (hooks only run on relevant files)

---

## 🎯 Current State Analysis

### Current Pre-Commit Configuration

**Issues**:
1. ❌ All Python hooks run on entire monorepo (inefficient)
2. ❌ No documentation-specific hooks (Docusaurus TypeScript/JavaScript)
3. ❌ No shell script validation (scripts/docker/, scripts/ci/)
4. ❌ No JSON/YAML validation beyond basic checks
5. ❌ No Markdown linting for documentation
6. ❌ Excludes `.github/` (should validate workflow files)
7. ❌ Excludes `docs/` (should validate documentation)

### Project Structure

```
test-coverage-mcp/                    # Root workspace
├── test-coverage-mcp/                # Core backend package (Python)
│   ├── src/                          # Python source
│   ├── test/                         # Python tests
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .coveragerc
├── test-coverage-mcp-codecov/        # Codecov backend package (Python)
│   ├── src/                          # Python source
│   ├── test/                         # Python tests
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .coveragerc
├── docs/                             # Documentation (Docusaurus)
│   ├── docusaurus.config.ts         # TypeScript config
│   ├── package.json                  # NPM dependencies
│   ├── pnpm-lock.yaml                # PNPM lock file
│   ├── src/                          # React/TypeScript components
│   ├── contents/                     # Markdown documentation
│   └── tsconfig.json                 # TypeScript config
├── scripts/                          # Shell scripts
│   ├── ci/                           # CI scripts
│   └── docker/                       # Docker scripts
├── .github/                          # GitHub Actions workflows
│   ├── workflows/                    # YAML workflow files
│   └── tag_and_release/              # Release configs
├── pyproject.toml                    # Workspace config
├── mypy.ini                          # Type checking (workspace)
├── ruff.toml                         # Linting (workspace)
└── Dockerfile                        # Docker build
```

---

## 🏗️ Redesign Strategy

### 1. Organize Hooks by Concern

**Four Hook Categories**:

1. **Universal Hooks** (all files)
   - File formatting (EOF, trailing whitespace)
   - Security (private keys, secrets)

2. **Backend Python Hooks** (Python packages)
   - Ruff (linting + formatting)
   - MyPy (type checking)
   - Debug statement detection
   - Per-package targeting

3. **Frontend Documentation Hooks** (Docusaurus)
   - ESLint (TypeScript/JavaScript)
   - Prettier (formatting)
   - TypeScript compilation check
   - Markdown linting

4. **Infrastructure Hooks** (configs, scripts, workflows)
   - YAML validation (workflows, configs)
   - JSON validation (package.json, tsconfig.json)
   - Shell script validation (shellcheck)
   - Dockerfile linting (hadolint)
   - TOML validation (pyproject.toml, ruff.toml)

### 2. File Path Targeting

**Precision targeting to avoid unnecessary runs**:

```yaml
# Example structure
- id: ruff
  files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/.*\.py$
  
- id: eslint
  files: ^docs/.*\.(ts|tsx|js|jsx)$
  
- id: shellcheck
  files: ^scripts/.*\.sh$
```

---

## 📝 Detailed Redesign Plan

### Hook Group 1: Universal File Checks

**Applies to**: All files in workspace

**Hooks**:
1. **end-of-file-fixer** - Ensure files end with newline
2. **trailing-whitespace** - Remove trailing whitespace
3. **detect-private-key** - Security check for leaked keys
4. **check-merge-conflict** - Detect merge conflict markers
5. **check-added-large-files** - Prevent large files (>500KB)

**File Targeting**: 
```yaml
files: ''  # All files (default)
exclude: |
  (?x)^(
    \.git/.*|
    \.venv/.*|
    \.mypy_cache/.*|
    \.ruff_cache/.*|
    dist/.*|
    .*\.lock$|
    pnpm-lock\.yaml
  )$
```

---

### Hook Group 2: Backend Python (Core + Codecov Packages)

**Applies to**: `test-coverage-mcp/`, `test-coverage-mcp-codecov/`

#### 2.1 Ruff (Linting + Formatting)

**Purpose**: Code quality and style consistency

**Configuration**:
```yaml
- id: ruff
  name: Ruff Linter (Backend Packages)
  files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/.*\.pyi?$
  args: [--fix]

- id: ruff-format
  name: Ruff Formatter (Backend Packages)
  files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/.*\.pyi?$
```

**Benefits**:
- Only runs on Python files in packages
- Uses workspace `ruff.toml` configuration
- Auto-fixes issues when possible

#### 2.2 MyPy (Type Checking)

**Purpose**: Static type checking

**Configuration**:
```yaml
- id: mypy
  name: MyPy Type Checking (Backend Packages)
  entry: mypy
  language: system
  files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/src/.*\.py$
  exclude: ^(test-coverage-mcp|test-coverage-mcp-codecov)/test/.*\.py$
  args:
    - --config-file=mypy.ini
```

**Benefits**:
- Only checks source code (not tests)
- Uses workspace `mypy.ini` configuration
- Per-package type checking isolation

#### 2.3 Debug Statement Detection

**Purpose**: Catch debug statements before commit

**Configuration**:
```yaml
- id: debug-statements
  name: Check Debug Statements (Backend)
  files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/src/.*\.py$
```

**Benefits**:
- Only checks source code (tests can have debug statements)
- Prevents `pdb`, `breakpoint()` in production code

#### 2.4 Python Import Sorting (Optional)

**Purpose**: Consistent import organization

**Configuration**:
```yaml
- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
    - id: isort
      name: ISort (Backend Packages)
      files: ^(test-coverage-mcp|test-coverage-mcp-codecov)/.*\.py$
      args:
        - --profile=black
        - --line-length=120
```

**Note**: May be redundant if Ruff handles import sorting

---

### Hook Group 3: Frontend Documentation (Docusaurus)

**Applies to**: `docs/`

#### 3.1 ESLint (TypeScript/JavaScript)

**Purpose**: Code quality for TypeScript/React components

**Configuration**:
```yaml
- repo: https://github.com/pre-commit/mirrors-eslint
  rev: v9.22.0
  hooks:
    - id: eslint
      name: ESLint (Documentation Frontend)
      files: ^docs/.*\.(ts|tsx|js|jsx)$
      additional_dependencies:
        - eslint@^9.22.0
        - '@typescript-eslint/parser@^7.0.0'
        - '@typescript-eslint/eslint-plugin@^7.0.0'
        - eslint-plugin-react@^7.35.0
      args:
        - --fix
        - --config=docs/.eslintrc.json
```

**Benefits**:
- Only runs on TypeScript/JavaScript in docs
- Auto-fixes linting issues
- Supports React/TypeScript patterns

#### 3.2 Prettier (Formatting)

**Purpose**: Consistent code formatting for frontend

**Configuration**:
```yaml
- repo: https://github.com/pre-commit/mirrors-prettier
  rev: v3.5.3
  hooks:
    - id: prettier
      name: Prettier (Documentation Frontend)
      files: ^docs/.*\.(ts|tsx|js|jsx|json|css|scss|md)$
      exclude: ^docs/pnpm-lock\.yaml$
      args:
        - --config=docs/.prettierrc.json
```

**Benefits**:
- Formats TypeScript, JavaScript, JSON, CSS, Markdown
- Consistent with Docusaurus ecosystem
- Excludes lock files

#### 3.3 TypeScript Compilation Check

**Purpose**: Ensure TypeScript compiles without errors

**Configuration**:
```yaml
- repo: local
  hooks:
    - id: tsc-check
      name: TypeScript Compilation Check (Documentation)
      entry: bash -c 'cd docs && npx tsc --noEmit'
      language: system
      files: ^docs/.*\.(ts|tsx)$
      pass_filenames: false
```

**Benefits**:
- Catches type errors before commit
- Uses docs/tsconfig.json configuration
- Only runs when TypeScript files change

#### 3.4 Markdown Linting

**Purpose**: Consistent Markdown formatting in documentation

**Configuration**:
```yaml
- repo: https://github.com/igorshubovych/markdownlint-cli
  rev: v0.43.1
  hooks:
    - id: markdownlint
      name: Markdownlint (Documentation)
      files: ^docs/contents/.*\.md$
      args:
        - --config=docs/.markdownlint.json
        - --fix
```

**Benefits**:
- Enforces Markdown best practices
- Auto-fixes common issues
- Only runs on documentation Markdown

---

### Hook Group 4: Infrastructure & Configuration

**Applies to**: `.github/`, `scripts/`, root configs

#### 4.1 YAML Validation

**Purpose**: Validate workflow and config YAML files

**Configuration**:
```yaml
- id: check-yaml
  name: Check YAML Files
  files: |
    (?x)^(
      \.github/workflows/.*\.ya?ml$|
      \.github/tag_and_release/.*\.ya?ml$|
      codecov\.yml$|
      \.pre-commit-config\.yaml$
    )
  args: ['--unsafe']  # Allow custom YAML tags (GitHub Actions)
```

**Benefits**:
- Validates GitHub Actions workflows
- Validates codecov.yml
- Catches YAML syntax errors

#### 4.2 JSON Validation

**Purpose**: Validate JSON configuration files

**Configuration**:
```yaml
- id: check-json
  name: Check JSON Files
  files: |
    (?x)^(
      docs/.*\.json$|
      \.github/.*\.json$|
      \.vscode/.*\.json$
    )$
  exclude: ^docs/pnpm-lock\.yaml$
```

**Benefits**:
- Validates package.json, tsconfig.json
- Validates VS Code configs
- Catches JSON syntax errors

#### 4.3 TOML Validation

**Purpose**: Validate Python project TOML files

**Configuration**:
```yaml
- repo: https://github.com/macisamuele/language-formatters-pre-commit-hooks
  rev: v2.16.0
  hooks:
    - id: pretty-format-toml
      name: Format TOML Files
      files: |
        (?x)^(
          pyproject\.toml$|
          ruff\.toml$|
          test-coverage-mcp/pyproject\.toml$|
          test-coverage-mcp-codecov/pyproject\.toml$
        )$
      args: [--autofix]
```

**Benefits**:
- Validates and formats TOML
- Catches syntax errors
- Consistent formatting

#### 4.4 Shell Script Validation (ShellCheck)

**Purpose**: Lint shell scripts for common issues

**Configuration**:
```yaml
- repo: https://github.com/shellcheck-py/shellcheck-py
  rev: v0.10.0.1
  hooks:
    - id: shellcheck
      name: ShellCheck (Scripts)
      files: |
        (?x)^(
          scripts/.*\.sh$|
          .*\.bash$
        )$
      args:
        - --severity=warning
        - --shell=bash
```

**Benefits**:
- Catches shell script bugs
- Enforces best practices
- Prevents common pitfalls

#### 4.5 Dockerfile Linting (Hadolint)

**Purpose**: Lint Dockerfile for best practices

**Configuration**:
```yaml
- repo: https://github.com/hadolint/hadolint
  rev: v2.13.2-beta
  hooks:
    - id: hadolint-docker
      name: Hadolint (Dockerfile)
      files: ^Dockerfile$
      args:
        - --ignore=DL3008  # Pin versions in apt-get (optional)
```

**Benefits**:
- Docker best practices
- Security checks
- Layer optimization tips

#### 4.6 UV Lock Check

**Purpose**: Ensure uv.lock is up-to-date

**Configuration**:
```yaml
- repo: https://github.com/astral-sh/uv-pre-commit
  rev: 0.9.28
  hooks:
    - id: uv-lock
      name: UV Lock Check (Workspace)
      files: |
        (?x)^(
          pyproject\.toml$|
          test-coverage-mcp/pyproject\.toml$|
          test-coverage-mcp-codecov/pyproject\.toml$
        )$
```

**Benefits**:
- Keeps dependencies in sync
- Prevents out-of-date lock file
- Workspace-aware

---

## 🎨 Recommended Hook Order

**Performance optimization: Fast checks first, slow checks last**

1. **Universal Checks** (fast, all files)
   - end-of-file-fixer
   - trailing-whitespace
   - check-merge-conflict
   - detect-private-key
   - check-added-large-files

2. **Syntax Validation** (fast, specific files)
   - check-yaml
   - check-json
   - pretty-format-toml

3. **Shell & Docker** (medium speed)
   - shellcheck
   - hadolint-docker

4. **Python Formatting** (medium speed, auto-fix)
   - ruff
   - ruff-format
   - debug-statements

5. **Frontend Formatting** (medium speed, auto-fix)
   - prettier
   - eslint

6. **Markdown** (medium speed)
   - markdownlint

7. **Type Checking** (slower, no auto-fix)
   - mypy (Python)
   - tsc-check (TypeScript)

8. **Dependency Lock** (slowest)
   - uv-lock

---

## 🚀 Implementation Strategy

### Pre-Commit Execution Policy

**User Requirement**: Pre-commit hooks should **only run before git push**, not on every commit.

**Configuration**:
```yaml
default_stages: [push]  # Global setting: run on push only
```

**Benefits**:
- ✅ Faster local commits (no hook execution)
- ✅ Validation before pushing to remote
- ✅ Can still run manually: `pre-commit run --all-files`
- ✅ No auto-installation needed

**Manual Execution** (when needed):
```bash
# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Run on staged files
pre-commit run
```

### Phase 1: Universal + Backend (Priority)

**Scope**:
1. Configure `default_stages: [push]` for push-only execution
2. Keep existing universal hooks with refined targeting
3. Refine Python hooks with precise file targeting
4. Add shell script validation (ShellCheck)
5. Add comprehensive config validation (YAML, JSON, TOML)

**Git Commit**: Single commit for Phase 1
```
🔧 pre-commit: Redesign Phase 1 - Backend and infrastructure hooks

- Set default_stages to [push] for push-only execution
- Refine Ruff/MyPy with package-specific file targeting
- Add ShellCheck for shell script validation
- Add YAML/JSON/TOML validation for configs
- Remove broad excludes for .github/ and docs/
- Optimize hook order for performance

Ref: Pre-commit Monorepo Redesign Plan, Phase 1
```

### Phase 2: Frontend Documentation (Secondary)

**Scope**:
1. Add ESLint for TypeScript/JavaScript
2. Add Prettier for formatting
3. Add TypeScript compilation check
4. Add Markdown linting
5. Create required config files (`.eslintrc.json`, `.prettierrc.json`, `.markdownlint.json`)

**Git Commits**: Two commits for Phase 2

**Commit 1**: Config files
```
🔧 docs: Add ESLint, Prettier, and Markdownlint configs

- Add docs/.eslintrc.json for TypeScript/React linting
- Add docs/.prettierrc.json for code formatting
- Add docs/.markdownlint.json for documentation linting
- Configs aligned with Docusaurus ecosystem

Ref: Pre-commit Monorepo Redesign Plan, Phase 2
```

**Commit 2**: Pre-commit hooks
```
🔧 pre-commit: Redesign Phase 2 - Frontend documentation hooks

- Add ESLint for TypeScript/JavaScript in docs/
- Add Prettier for frontend formatting
- Add TypeScript compilation check (tsc --noEmit)
- Add Markdownlint for documentation quality
- All hooks target docs/ directory only

Ref: Pre-commit Monorepo Redesign Plan, Phase 2
```

### Phase 3: Advanced Infrastructure (Optional)

**Scope**:
1. Add Hadolint for Dockerfile linting
2. Add additional security checks (if needed)
3. Fine-tune hook order and performance

**Git Commit**: Single commit for Phase 3
```
🔧 pre-commit: Redesign Phase 3 - Advanced infrastructure hooks

- Add Hadolint for Dockerfile best practices
- Add additional security checks (detect-secrets)
- Optimize hook execution order
- Fine-tune file targeting patterns

Ref: Pre-commit Monorepo Redesign Plan, Phase 3
```

### Total Git Commits

**4 commits total**:
1. Phase 1: Backend + Infrastructure (1 commit)
2. Phase 2: Config files (1 commit) + Pre-commit hooks (1 commit)
3. Phase 3: Advanced infrastructure (1 commit)

---

## 📊 Performance Considerations

### File Targeting Impact

**Before** (current):
- Ruff runs on ALL Python files in workspace
- MyPy runs on ALL Python files in both packages
- No documentation checks

**After** (optimized):
- Ruff runs ONLY on `test-coverage-mcp/` and `test-coverage-mcp-codecov/` Python files
- MyPy runs ONLY on `src/` directories (not tests)
- ESLint runs ONLY on `docs/` TypeScript/JavaScript
- ShellCheck runs ONLY on `scripts/` shell scripts

**Estimated Speed Improvement**: 30-50% faster for typical commits

### Hook Stages Configuration

**Global Setting** (applies to all hooks unless overridden):
```yaml
default_stages: [push]  # All hooks run on push only
```

**Per-Hook Override** (optional, for advanced use):
```yaml
- id: trailing-whitespace
  stages: [commit, push]  # Fast hook, can run on commit too
  
- id: mypy
  stages: [push]  # Inherits default (explicit for clarity)
  
- id: tsc-check
  stages: [manual]  # Only run manually with --hook-stage manual
```

**Manual Execution Examples**:
```bash
# Run all push-stage hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Run manual-stage hooks
pre-commit run --hook-stage manual --all-files
```

---

## 🔍 Testing Strategy

### Test Scenarios

1. **Backend-only change**: Modify `test-coverage-mcp/src/foo.py`
   - ✅ Should run: Universal, Ruff, MyPy, UV lock
   - ❌ Should NOT run: ESLint, Prettier, TSC, Markdownlint

2. **Frontend-only change**: Modify `docs/src/components/Foo.tsx`
   - ✅ Should run: Universal, ESLint, Prettier, TSC
   - ❌ Should NOT run: Ruff, MyPy

3. **Config change**: Modify `.github/workflows/ci-monorepo.yaml`
   - ✅ Should run: Universal, YAML validation
   - ❌ Should NOT run: Python, Frontend checks

4. **Script change**: Modify `scripts/docker/run-server.sh`
   - ✅ Should run: Universal, ShellCheck
   - ❌ Should NOT run: Python, Frontend checks

5. **Multi-package change**: Modify both `test-coverage-mcp/` and `docs/`
   - ✅ Should run: All relevant hooks for both areas

---

## 📋 Configuration Files to Create

### 1. `docs/.eslintrc.json` (if not exists)

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": ["react", "@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "warn",
    "react/react-in-jsx-scope": "off"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

### 2. `docs/.prettierrc.json` (if not exists)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

### 3. `docs/.markdownlint.json` (if not exists)

```json
{
  "default": true,
  "MD013": false,
  "MD033": false,
  "MD041": false
}
```

---

## ⚠️ Breaking Changes & Migration

### Changes from Current Config

**Execution Model**:
- ✅ **NEW**: Added `default_stages: [push]` - hooks run on push only
- ❌ **REMOVED**: Auto-execution on every commit

**File Targeting**:
- ❌ **REMOVED**: Global exclude for `.github/` and `docs/` directories
- ✅ **NEW**: Precise file targeting with regex patterns

**Hook Changes**:
- **Modified**: Ruff → targets specific package directories
- **Modified**: MyPy → targets only `src/` directories (not tests)
- **Modified**: YAML check → now includes workflow files
- **Added**: ESLint, Prettier, TypeScript check (docs/)
- **Added**: Markdown linting (docs/)
- **Added**: ShellCheck (scripts/)
- **Added**: Hadolint (Dockerfile)
- **Added**: JSON validation
- **Added**: TOML formatting

### Migration Steps

**Important**: Pre-commit hooks will **NOT auto-install or auto-run on commits**. They only run before push.

1. **Backup current config**:
   ```bash
   cp .pre-commit-config.yaml .pre-commit-config.yaml.backup
   ```

2. **Phase 1: Update config file** (Backend + Infrastructure):
   ```bash
   # Edit .pre-commit-config.yaml with Phase 1 changes
   git add .pre-commit-config.yaml
   git commit -m "🔧 pre-commit: Redesign Phase 1 - Backend and infrastructure hooks"
   ```

3. **Install hook dependencies** (one-time, updates as needed):
   ```bash
   # This downloads hook repositories, does NOT install git hooks
   pre-commit install-hooks
   ```

4. **Test Phase 1 hooks manually**:
   ```bash
   # Run all hooks to see what fails
   pre-commit run --all-files
   
   # Fix any issues that arise
   # Commit fixes separately
   ```

5. **Phase 2a: Add frontend config files**:
   ```bash
   # Create docs/.eslintrc.json, .prettierrc.json, .markdownlint.json
   git add docs/.eslintrc.json docs/.prettierrc.json docs/.markdownlint.json
   git commit -m "🔧 docs: Add ESLint, Prettier, and Markdownlint configs"
   ```

6. **Phase 2b: Add frontend hooks**:
   ```bash
   # Edit .pre-commit-config.yaml with Phase 2 changes
   pre-commit install-hooks  # Install new frontend hooks
   git add .pre-commit-config.yaml
   git commit -m "🔧 pre-commit: Redesign Phase 2 - Frontend documentation hooks"
   ```

7. **Test Phase 2 hooks manually**:
   ```bash
   # Run all hooks
   pre-commit run --all-files
   
   # Fix any issues
   # Commit fixes separately
   ```

8. **Phase 3: Add advanced hooks** (optional):
   ```bash
   # Edit .pre-commit-config.yaml with Phase 3 changes
   pre-commit install-hooks
   git add .pre-commit-config.yaml
   git commit -m "🔧 pre-commit: Redesign Phase 3 - Advanced infrastructure hooks"
   ```

9. **Normal workflow going forward**:
   ```bash
   # Commit code (no hooks run)
   git add .
   git commit -m "✨ feat: Add new feature"
   
   # Push (hooks run automatically before push)
   git push origin branch-name
   
   # Or run manually anytime
   pre-commit run --all-files
   ```

### No Auto-Installation

**User preference**: Do NOT install pre-commit git hooks to run automatically.

**What this means**:
- ✅ Hooks are configured in `.pre-commit-config.yaml`
- ✅ Hook dependencies can be installed with `pre-commit install-hooks`
- ❌ Do NOT run `pre-commit install` (this would auto-install git hooks)
- ✅ Hooks only run:
  - Before `git push` (if user manually sets up)
  - When manually called: `pre-commit run --all-files`

**Developer Setup** (optional, per-developer choice):
```bash
# If developer wants hooks to run on push:
pre-commit install --hook-type pre-push

# If developer wants to run manually only:
# Do nothing - just use: pre-commit run --all-files
```

---

## 📚 Documentation Updates Needed

### Update `CONTRIBUTING.md`

Add section on pre-commit hooks:

```markdown
## Pre-Commit Hooks

This project uses pre-commit hooks organized by concern. **Hooks are configured to run before `git push` only** (not on every commit).

### Hook Execution Policy

**When hooks run**:
- ✅ Before `git push` (if you set up: `pre-commit install --hook-type pre-push`)
- ✅ When manually executed: `pre-commit run --all-files`
- ❌ NOT on `git commit` (fast local commits)

### Backend Python Hooks
- **Ruff**: Linting and formatting for Python packages
- **MyPy**: Type checking for source code (src/ only)
- **Debug detection**: Prevents debug statements in source

### Frontend Documentation Hooks
- **ESLint**: Linting for TypeScript/JavaScript in docs/
- **Prettier**: Formatting for frontend code
- **TypeScript**: Compilation check (tsc --noEmit)
- **Markdownlint**: Documentation formatting

### Infrastructure Hooks
- **YAML/JSON/TOML**: Configuration validation
- **ShellCheck**: Shell script linting (scripts/)
- **Hadolint**: Dockerfile best practices
- **UV Lock**: Dependency synchronization

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run all hooks on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff --all-files

# Run on specific files
pre-commit run --files test-coverage-mcp/src/foo.py

# Run with verbose output
pre-commit run --all-files --verbose
```

### Optional: Enable Pre-Push Hooks

If you want hooks to run automatically before push:

```bash
# Install pre-push hook (one-time setup)
pre-commit install --hook-type pre-push

# Now hooks will run before every git push
```

To disable:
```bash
# Uninstall pre-push hook
pre-commit uninstall --hook-type pre-push

# Hooks still available manually
pre-commit run --all-files
```

### Troubleshooting

If hooks fail:
1. Read the error message carefully
2. Fix the issue in your code
3. Re-run: `pre-commit run --all-files`
4. If stuck, add `--verbose` flag for detailed output
5. To bypass (not recommended): `git push --no-verify`
```

---

## ✅ Benefits of Redesign

### 1. Performance
- ⚡ **30-50% faster** for typical commits
- 🎯 Hooks only run on relevant files
- 📦 Package-specific targeting

### 2. Maintainability
- 📝 Clear organization by concern
- 🔍 Easy to understand which hooks apply where
- 🎨 Consistent with monorepo structure

### 3. Quality
- ✨ Frontend code quality checks (TypeScript/JavaScript)
- 🐚 Shell script validation
- 🐳 Dockerfile best practices
- 📚 Documentation formatting

### 4. Developer Experience
- 🚀 Faster feedback loop
- 🎯 Relevant errors only
- 📖 Clear error messages
- 🔧 Auto-fix when possible

### 5. Scalability
- ➕ Easy to add new packages
- 🔌 Easy to add new hook types
- 🎚️ Fine-grained control

---

## 🔮 Future Enhancements

### Optional Additions (Future Phases)

1. **Security Scanning** (Phase 4)
   - `detect-secrets` for secret scanning
   - `safety` for Python dependency vulnerabilities
   - `npm audit` for frontend dependencies

2. **Test Coverage Enforcement** (Phase 5)
   - Hook to check coverage threshold
   - Prevent pushes that drop coverage below threshold

3. **Commit Message Validation** (Phase 6)
   - Enforce gitmoji format
   - Validate commit message structure
   - Check for issue references

4. **License Headers** (Phase 7)
   - Ensure all source files have license headers
   - Auto-add missing headers

5. **Import Analysis** (Phase 8)
   - Detect circular imports in Python packages
   - Enforce import boundaries between packages

---

## 📊 Comparison: Before vs After

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Execution timing** | On commit | On push (or manual) | Faster local commits |
| **Hooks run per push** | ~6 (all files) | ~3-4 (targeted) | 30-50% faster |
| **Python targeting** | All Python files | Package-specific | More precise |
| **Frontend checks** | None | ESLint, Prettier, TSC | New coverage |
| **Documentation** | None | Markdown linting | New coverage |
| **Scripts** | None | ShellCheck | New coverage |
| **Config validation** | Basic YAML | YAML, JSON, TOML | More comprehensive |
| **Docker** | None | Hadolint | New coverage |
| **Excludes** | `.github/`, `docs/` | Precise targeting | Better coverage |
| **Developer control** | Auto on commit | Optional, push or manual | More flexibility |

---

## 🎯 Recommendation

**Implement in 3 phases with 4 git commits**:

### Phase 1 (High Priority) - Backend & Infrastructure
**Scope**:
- ✅ Add `default_stages: [push]` for push-only execution
- ✅ Refine existing Python hooks with file targeting
- ✅ Add shell script validation (ShellCheck)
- ✅ Add comprehensive config validation (YAML, JSON, TOML)
- ✅ Remove broad excludes for `.github/` and `docs/`

**Git Commits**: 1 commit
**Estimated effort**: 2-3 hours
**Impact**: Immediate performance improvement, better infrastructure coverage, faster local commits

### Phase 2 (Medium Priority) - Frontend Documentation
**Scope**:
- ✅ Create ESLint, Prettier, Markdownlint config files
- ✅ Add ESLint for TypeScript/JavaScript
- ✅ Add Prettier for formatting
- ✅ Add TypeScript compilation check
- ✅ Add Markdown linting

**Git Commits**: 2 commits (configs + hooks)
**Estimated effort**: 2-3 hours
**Impact**: Documentation quality improvement, frontend code consistency

### Phase 3 (Optional) - Advanced Infrastructure
**Scope**:
- ✅ Add Hadolint for Dockerfile
- ✅ Add additional security checks (detect-secrets)
- ✅ Optimize hook order and performance

**Git Commits**: 1 commit
**Estimated effort**: 1-2 hours
**Impact**: Docker best practices, enhanced security

---

## 📝 Implementation Summary

### Total Git Commits: 4

1. **Phase 1**: `🔧 pre-commit: Redesign Phase 1 - Backend and infrastructure hooks`
2. **Phase 2a**: `🔧 docs: Add ESLint, Prettier, and Markdownlint configs`
3. **Phase 2b**: `🔧 pre-commit: Redesign Phase 2 - Frontend documentation hooks`
4. **Phase 3**: `🔧 pre-commit: Redesign Phase 3 - Advanced infrastructure hooks`

### Key Changes

1. **Execution Model**: Hooks run on push only (not commit)
2. **No Auto-Installation**: Hooks configured but not auto-installed
3. **File Targeting**: Precise regex patterns for each hook type
4. **Phased Implementation**: Each phase gets its own commit(s)
5. **Developer Choice**: Optional `pre-commit install --hook-type pre-push` for auto-execution

---

**End of Plan** 🚀

**Version**: 1.0 (Updated for push-only execution with phased commits)  
**Status**: Ready for review and approval

This redesign provides a comprehensive, scalable pre-commit configuration optimized for monorepo architecture with:
- ✅ **Push-only execution** (faster local commits)
- ✅ **Clear separation of concerns** (backend, frontend, infrastructure)
- ✅ **Phased implementation** (4 git commits)
- ✅ **No forced auto-installation** (developer's choice)
- ✅ **Significant performance improvements** (30-50% faster, targeted execution)
