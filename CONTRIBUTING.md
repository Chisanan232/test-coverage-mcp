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

### Running Linters and Type Checkers

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

The project uses GitHub Actions for CI/CD:

- **Linting**: ruff, mypy on every push
- **Testing**: pytest on Python 3.12, 3.13, 3.14
- **Coverage**: Uploaded to Codecov
- **Quality**: SonarCloud analysis

## Questions?

Open an issue on GitHub or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
