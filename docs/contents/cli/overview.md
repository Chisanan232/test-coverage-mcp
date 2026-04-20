# CLI Overview

## Introduction

The test-coverage-mcp CLI provides a command-line interface for managing and interacting with the MCP server. It supports multiple commands for serving, provider management, and system diagnostics.

## Quick Start

### Installation

```bash
pip install test-coverage-mcp
```

### Basic Usage

```bash
# Show help
test-coverage-mcp --help

# Enable verbose output
test-coverage-mcp --verbose serve

# Use custom configuration
test-coverage-mcp --config /path/to/config.yaml serve
```

## Available Commands

### serve

Start the MCP server with specified transport and provider.

```bash
test-coverage-mcp serve [OPTIONS]
```

**Options**:
- `--transport {stdio|http}` - Transport type (default: stdio)
- `--provider {auto|codecov}` - Coverage provider (default: auto)
- `--host TEXT` - Host to bind to (default: 127.0.0.1)
- `--port INTEGER` - Port to bind to (default: 8000)

**Examples**:
```bash
# Start with stdio transport
test-coverage-mcp serve

# Start with HTTP transport
test-coverage-mcp serve --transport http

# Start on custom host/port
test-coverage-mcp serve --transport http --host 0.0.0.0 --port 9000
```

### providers

Manage and list coverage providers.

```bash
test-coverage-mcp providers [COMMAND]
```

**Subcommands**:
- `list` - List all available providers
- `describe NAME` - Describe a specific provider

**Examples**:
```bash
# List all providers
test-coverage-mcp providers list

# Describe codecov provider
test-coverage-mcp providers describe codecov
```

### doctor

Check environment and system health.

```bash
test-coverage-mcp doctor [OPTIONS]
```

**Options**:
- `-v, --verbose` - Enable verbose output

**Examples**:
```bash
# Basic health check
test-coverage-mcp doctor

# Detailed health check
test-coverage-mcp doctor --verbose
```

### completion

Generate shell completion scripts.

```bash
test-coverage-mcp completion --shell {bash|zsh|fish}
```

**Examples**:
```bash
# Generate bash completion
test-coverage-mcp completion --shell bash

# Install bash completion
test-coverage-mcp completion --shell bash | sudo tee /etc/bash_completion.d/test-coverage-mcp

# Generate zsh completion
test-coverage-mcp completion --shell zsh

# Install zsh completion
test-coverage-mcp completion --shell zsh | sudo tee /usr/share/zsh/site-functions/_test-coverage-mcp
```

## Global Options

All commands support the following global options:

- `-v, --verbose` - Enable verbose output for debugging
- `--config PATH` - Path to configuration file

**Examples**:
```bash
# Verbose serve command
test-coverage-mcp --verbose serve

# With configuration file
test-coverage-mcp --config ~/.test-coverage-mcp/config.yaml serve
```

## Configuration

Configuration can be provided via:

1. **Configuration file** - Specified with `--config` option
2. **Environment variables** - Prefixed with `TEST_COVERAGE_MCP_`
3. **Command-line options** - Specific to each command

## Environment Variables

Common environment variables:

- `CODECOV_TOKEN` - Codecov API token
- `COVERALLS_TOKEN` - Coveralls API token
- `TEST_COVERAGE_MCP_CONFIG` - Path to configuration file

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Command-line syntax error

## Shell Completion

### Bash

```bash
test-coverage-mcp completion --shell bash | sudo tee /etc/bash_completion.d/test-coverage-mcp
source /etc/bash_completion.d/test-coverage-mcp
```

### Zsh

```bash
test-coverage-mcp completion --shell zsh | sudo tee /usr/share/zsh/site-functions/_test-coverage-mcp
```

### Fish

```bash
test-coverage-mcp completion --shell fish | sudo tee /usr/share/fish/vendor_completions.d/test-coverage-mcp.fish
```

## Troubleshooting

### Command not found

Ensure the package is installed:
```bash
pip install test-coverage-mcp
```

### Permission denied

If you get permission errors, try:
```bash
pip install --user test-coverage-mcp
```

### Health check failures

Run the doctor command to diagnose issues:
```bash
test-coverage-mcp doctor --verbose
```

## See Also

- [Serve Command Reference](./serve.md)
- [Providers Command Reference](./providers.md)
- [Doctor Command Reference](./doctor.md)
- [CLI Deployment Guide](../deployment/cli.md)
