# CLI Commands Reference

## serve

Start the test-coverage-mcp MCP server.

### Usage

```bash
test-coverage-mcp serve [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--transport` | `stdio\|http` | `stdio` | Transport type for MCP communication |
| `--provider` | `auto\|codecov` | `auto` | Coverage provider to use |
| `--host` | `TEXT` | `127.0.0.1` | Host to bind to (for http transport) |
| `--port` | `INTEGER` | `8000` | Port to bind to (for http transport) |

### Examples

**Start with stdio transport (default)**:
```bash
test-coverage-mcp serve
```

**Start with HTTP transport**:
```bash
test-coverage-mcp serve --transport http
```

**Start on custom host and port**:
```bash
test-coverage-mcp serve --transport http --host 0.0.0.0 --port 9000
```

**Use specific provider**:
```bash
test-coverage-mcp serve --provider codecov
```

### Environment Variables

- `CODECOV_TOKEN` - Codecov API token (if using codecov provider)

---

## providers

Manage coverage providers.

### Usage

```bash
test-coverage-mcp providers [COMMAND]
```

### Subcommands

#### list

List all available coverage providers.

```bash
test-coverage-mcp providers list
```

**Output**:
```
Available providers:
  - codecov: Codecov coverage provider
  - coveralls: Coveralls coverage provider (if installed)
```

#### describe

Describe a specific coverage provider.

```bash
test-coverage-mcp providers describe <NAME>
```

**Arguments**:
- `NAME` - Name of the provider to describe

**Example**:
```bash
test-coverage-mcp providers describe codecov
```

**Output**:
```
Provider: codecov
  Version: 0.1.0
  Description: Codecov coverage provider
  Capabilities:
    - repository_summary
    - file_coverage
    - coverage_delta
```

---

## doctor

Check environment and system health.

### Usage

```bash
test-coverage-mcp doctor [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `-v, --verbose` | `FLAG` | Enable verbose output |

### Output

The doctor command checks:

1. **Environment Variables**
   - CODECOV_TOKEN
   - COVERALLS_TOKEN
   - TEST_COVERAGE_MCP_CONFIG

2. **Provider Connectivity**
   - Codecov availability
   - Coveralls configuration

3. **Plugin Loading**
   - Core plugins status
   - MCP server readiness

4. **Overall Health Status**
   - Summary of all checks

### Examples

**Basic health check**:
```bash
test-coverage-mcp doctor
```

**Detailed health check**:
```bash
test-coverage-mcp doctor --verbose
```

### Output Example

```
Running health checks...

Environment Variables:
  ✓ CODECOV_TOKEN: ****...****
  ✗ COVERALLS_TOKEN: not set
  ✗ TEST_COVERAGE_MCP_CONFIG: not set

Provider Connectivity:
  ✓ Codecov: available
  ✗ Coveralls: not configured

Plugin Loading:
  ✓ Core plugins: loaded
  ✓ MCP server: ready

Overall Health Status: ✓ Healthy
```

---

## completion

Generate shell completion scripts.

### Usage

```bash
test-coverage-mcp completion --shell {bash|zsh|fish}
```

### Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--shell` | `bash\|zsh\|fish` | Yes | Shell type for completion |

### Supported Shells

#### Bash

```bash
test-coverage-mcp completion --shell bash
```

Install:
```bash
test-coverage-mcp completion --shell bash | sudo tee /etc/bash_completion.d/test-coverage-mcp
source /etc/bash_completion.d/test-coverage-mcp
```

#### Zsh

```bash
test-coverage-mcp completion --shell zsh
```

Install:
```bash
test-coverage-mcp completion --shell zsh | sudo tee /usr/share/zsh/site-functions/_test-coverage-mcp
```

#### Fish

```bash
test-coverage-mcp completion --shell fish
```

Install:
```bash
test-coverage-mcp completion --shell fish | sudo tee /usr/share/fish/vendor_completions.d/test-coverage-mcp.fish
```

---

## Global Options

All commands support these global options:

### --verbose, -v

Enable verbose output for debugging.

```bash
test-coverage-mcp --verbose serve
```

### --config

Path to configuration file.

```bash
test-coverage-mcp --config /path/to/config.yaml serve
```

### --help, -h

Show help message.

```bash
test-coverage-mcp --help
test-coverage-mcp serve --help
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Command-line syntax error |

---

## See Also

- [CLI Overview](./overview.md)
- [CLI Deployment Guide](../deployment/cli.md)
