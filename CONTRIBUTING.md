# Contributing to test-coverage-mcp

Thank you for your interest in contributing to test-coverage-mcp!

## Workspace Structure

This project uses a **uv workspace** monorepo with multiple packages:

```
test-coverage-mcp/                    # Root workspace
├── test-coverage-mcp/                # Core package
│   ├── src/                          # Core source code
│   │   ├── mcp_server/               # MCP server implementation
│   │   ├── web_server/               # Web API server
│   │   ├── integrate/                # Integrated server
│   │   ├── models/                   # Domain models
│   │   ├── config.py                 # Configuration
│   │   └── entry.py                  # Entry point
│   ├── test/                         # Core tests
│   │   ├── unit_test/                # Unit tests
│   │   └── integration_test/         # Integration tests
│   ├── pyproject.toml                # Package configuration
│   ├── pytest.ini                    # Pytest config (per-package)
│   ├── .coveragerc                   # Coverage config (per-package)
│   └── .env.example                  # Environment vars (per-package)
├── test-coverage-mcp-codecov/        # Codecov provider plugin
│   ├── src/                          # Flat structure (no nested package dir)
│   │   └── __init__.py
│   ├── test/
│   ├── pyproject.toml                # Package configuration
│   ├── pytest.ini                    # Pytest config (per-package)
│   ├── .coveragerc                   # Coverage config (per-package)
│   └── .env.example                  # Environment vars (per-package)
├── pyproject.toml                    # Workspace configuration
├── mypy.ini                          # Type checking (workspace-wide)
├── ruff.toml                         # Linting (workspace-wide)
├── sonar-project.properties          # SonarQube (multi-module monorepo)
├── Dockerfile                        # Docker build (workspace build)
├── .pre-commit-config.yaml           # Pre-commit hooks (workspace-wide)
└── .env.example                      # Workspace overview (points to package configs)
```

## Configuration Hierarchy

The workspace uses a **two-level configuration hierarchy**:

### Workspace-Wide Configurations (Root Level)

These configurations apply to **all packages** in the workspace:

- **`ruff.toml`** - Code linting and formatting rules
  - Defines style rules, import ordering, per-file ignores for all packages
  - Uses `known-first-party` to recognize workspace packages

- **`mypy.ini`** - Type checking configuration
  - Checks all package source code
  - Uses `explicit_package_bases` for multiple `src/` directories
  - Per-package overrides available if needed

- **`.pre-commit-config.yaml`** - Pre-commit hooks
  - Runs ruff, mypy across workspace
  - Configured with workspace-aware file paths

- **`sonar-project.properties`** - SonarQube quality analysis
  - Multi-module configuration with `sonar.modules=core,codecov`
  - Each module has separate source, test, and coverage paths

- **`Dockerfile`** - Container build
  - Builds entire workspace with all packages
  - Entry point runs core package

- **`.env.example`** - Workspace overview
  - Points developers to package-specific `.env.example` files

### Per-Package Configurations

Each package has its **own isolated configurations**:

- **`pyproject.toml`** - Package metadata, dependencies, build config
- **`pytest.ini`** - Package-specific test configuration
- **`.coveragerc`** - Package-specific coverage settings
- **`.env.example`** - Package-specific environment variables
- **`README.md`** - Package documentation

### When to Edit Which Config

| Task | Configuration File | Level |
|------|-------------------|-------|
| Add/change linting rules | `ruff.toml` | Workspace |
| Add type checking rules | `mypy.ini` | Workspace |
| Add pre-commit hook | `.pre-commit-config.yaml` | Workspace |
| Add SonarQube module | `sonar-project.properties` | Workspace |
| Add package dependency | `<package>/pyproject.toml` | Per-package |
| Change test settings | `<package>/pytest.ini` | Per-package |
| Change coverage settings | `<package>/.coveragerc` | Per-package |
| Add environment variable | `<package>/.env.example` | Per-package |

**Golden Rule**: If it affects code quality/style across the workspace, edit the root config. If it's specific to how one package works, edit the package config.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/Chisanan232/test-coverage-mcp.git
cd test-coverage-mcp

# Install all workspace packages and dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
```

## Working with the Workspace

### Running Tests

```bash
# Test core package
cd test-coverage-mcp
uv run pytest

# Test codecov provider
cd test-coverage-mcp-codecov
uv run pytest

# Test both packages from root
uv run pytest test-coverage-mcp/test/
uv run pytest test-coverage-mcp-codecov/test/
```

### Development Tooling Setup

The workspace uses three main development tools configured at the workspace level:

#### MyPy (Type Checking)

**Configuration**: `mypy.ini`
- Checks all package source code and tests
- Supports namespace packages with `explicit_package_bases`
- Per-package overrides available

```bash
# Type check core package
uv run mypy test-coverage-mcp/src

# Type check codecov provider
uv run mypy test-coverage-mcp-codecov/src

# Type check all packages
uv run mypy test-coverage-mcp/src test-coverage-mcp-codecov/src
```

#### Ruff (Linting & Formatting)

**Configuration**: `ruff.toml`
- Comprehensive rule set (E, F, UP, B, SIM, I, N, etc.)
- Workspace-aware `known-first-party` packages
- Per-file ignores for tests and special files

```bash
# Check code style
uv run ruff check .

# Format code (auto-fix)
uv run ruff format .

# Check and format together
uv run ruff check . && uv run ruff format .
```

#### Pre-Commit Hooks

**Configuration**: `.pre-commit-config.yaml`
- Runs on `push` (not on commit by default)
- Includes ruff, mypy, YAML checks, and more
- Workspace-aware file patterns

```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files

# Install hooks (runs automatically on push)
uv run pre-commit install
```

### Running All Quality Checks

```bash
# From root directory
uv run ruff check .
uv run ruff format .
uv run mypy test-coverage-mcp/src
uv run mypy test-coverage-mcp-codecov/src

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Building Packages

```bash
# Build core package
uv build --package test-coverage-mcp

# Build codecov provider
uv build --package test-coverage-mcp-codecov
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow existing code style (enforced by ruff)
- Add type hints (checked by mypy)
- Write tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
# Run tests
cd test-coverage-mcp && uv run pytest

# Run linters
uv run ruff check .
uv run ruff format .

# Run type checker
uv run mypy test-coverage-mcp/src

# Run pre-commit checks
uv run pre-commit run --all-files
```

### 4. Commit Changes

Follow the commit message format with gitmoji:

```bash
# Simple format
✨ Add new feature
🐛 Fix bug in parser
📝 Update documentation

# With scope
✨ codecov: Add API client
🔧 mypy: Update workspace config
✅ core: Add unit tests
```

See the gitmoji guide in the implementation plan for more examples.

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Adding a New Provider

To add a new coverage provider:

1. Create a new package directory: `test-coverage-mcp-{provider}/`
2. Add to workspace in root `pyproject.toml`:
   ```toml
   [tool.uv.workspace]
   members = ["test-coverage-mcp", "test-coverage-mcp-codecov", "test-coverage-mcp-{provider}"]
   ```
3. Create package structure:
   ```
   test-coverage-mcp-{provider}/
   ├── src/test_coverage_mcp_{provider}/
   │   └── __init__.py
   ├── test/
   ├── pyproject.toml
   ├── pytest.ini
   └── .coveragerc
   ```
4. Implement the `CoverageProvider` protocol (to be defined in Phase 2)
5. Register entry point in `pyproject.toml`

## Code Style Guidelines

- **Line length**: 120 characters (enforced by ruff)
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Required for all public modules, classes, and functions
- **Import order**: Handled by ruff (isort)
- **Test naming**: `test_*.py` for files, `test_*` for functions

## Testing Guidelines

- Write unit tests for all new functionality
- Integration tests for API endpoints and external services
- Aim for 80%+ code coverage
- Use pytest fixtures for common setup
- Mock external dependencies

## CI/CD

The project uses GitHub Actions for monorepo CI/CD with per-package workflows:

### Running Tests in Monorepo

#### Test All Packages
```bash
uv run pytest
```

#### Test Core Package Only
```bash
cd test-coverage-mcp
uv run pytest test/unit_test/ -v
```

#### Test Codecov Plugin Only
```bash
cd test-coverage-mcp-codecov
uv run pytest test/unit_test/ -v
```

### CI Workflow

**File**: `.github/workflows/ci-monorepo.yaml`

- **Per-package testing**: Automatically detects which packages changed
- **Matrix testing**: Python 3.12, 3.13, 3.14 on ubuntu-latest, macos-latest
- **Coverage**: Uploaded to Codecov with package-specific flags (e.g., `core,unit-test`)
- **Quality**: SonarQube multi-module analysis

### Release Process

The project uses 3 release orchestrator workflows:

#### Validation (Pre-Release Check)
1. Automatically runs on PRs modifying package code
2. Or manually trigger: `.github/workflows/release-validate-monorepo.yml`
3. Validates build, tests, and version bumps (dry-run only)

#### Staging Release (TestPyPI)
1. Manually trigger: `.github/workflows/release-staging-monorepo.yml`
2. Select packages: `["core"]` or `["codecov"]` or `["core", "codecov"]`
3. Publishes to TestPyPI with RC tags (e.g., `core/v1.0.0-rc.1`)
4. Test installations before production

#### Production Release (PyPI)
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

### Adding a New Package to CI/CD

When adding a new package (e.g., `test-coverage-mcp-sonarqube`):

1. Update `.github/tag_and_release/intent.yaml`:
   ```yaml
   packages:
     - name: core
       # ... existing config
     - name: codecov
       # ... existing config
     - name: sonarqube
       package_name: test-coverage-mcp-sonarqube
       working_directory: ./test-coverage-mcp-sonarqube
       tag_prefix: sonarqube/
   ```

2. **That's it!** No new workflow files needed. All 3 orchestrators automatically handle the new package.

3. The CI workflow will also auto-detect changes to the new package directory.

## Questions?

Open an issue on GitHub or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
