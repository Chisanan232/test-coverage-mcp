---
sidebar_position: 2
---

# Configuration Guide

## Overview

The test-coverage-mcp server uses Pydantic-Settings for flexible configuration management. Configuration can be provided via environment variables, `.env` files, or code.

## Quick Start

### 1. Environment Variables

Set provider credentials as environment variables:

```bash
# Codecov
export CODECOV_API_TOKEN="your-codecov-token"
export CODECOV_API_BASE_URL="https://api.codecov.io"
export CODECOV_OWNER="your-org"
export CODECOV_REPO="your-repo"

# Registry
export REGISTRY_AUTO_DISCOVER="true"
export REGISTRY_AUTO_INITIALIZE="true"
export REGISTRY_DEFAULT_PROVIDER="codecov"
```

### 2. .env File

Create a `.env` file in your project root:

```bash
# .env

# Codecov Configuration
CODECOV_API_TOKEN=your-codecov-token
CODECOV_API_BASE_URL=https://api.codecov.io
CODECOV_OWNER=your-org
CODECOV_REPO=your-repo
CODECOV_TIMEOUT_SECONDS=30
CODECOV_RETRY_ATTEMPTS=3

# Registry Configuration
REGISTRY_AUTO_DISCOVER=true
REGISTRY_AUTO_INITIALIZE=true
REGISTRY_DEFAULT_PROVIDER=codecov
REGISTRY_HEALTH_CHECK_INTERVAL_SECONDS=300
REGISTRY_LOG_LEVEL=INFO

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
```

### 3. Code Configuration

```python
from src.registry.config import CodecovConfig, RegistryConfig, ApplicationConfig

# Create configuration
codecov_config = CodecovConfig(
    api_token="your-token",
    api_base_url="https://api.codecov.io",
    owner="your-org",
    repo="your-repo",
)

registry_config = RegistryConfig(
    auto_discover=True,
    auto_initialize=True,
    default_provider="codecov",
)

app_config = ApplicationConfig(
    registry=registry_config,
    debug=False,
)
```

## Provider Configuration

### Codecov

**Required Fields**:
- `api_token` - Your Codecov API token

**Optional Fields**:
- `api_base_url` - Codecov API endpoint (default: `https://api.codecov.io`)
- `owner` - Repository owner
- `repo` - Repository name
- `timeout_seconds` - API timeout (default: 30)
- `retry_attempts` - Retry count (default: 3)
- `retry_delay_seconds` - Delay between retries (default: 1.0)

**Example**:

```bash
# Environment variables
export CODECOV_API_TOKEN="your-token"
export CODECOV_OWNER="my-org"
export CODECOV_REPO="my-repo"
export CODECOV_TIMEOUT_SECONDS=60
```

```python
# Code
config = CodecovConfig(
    api_token="your-token",
    owner="my-org",
    repo="my-repo",
    timeout_seconds=60,
)
```

### Custom Providers

Extend `ProviderConfig` for custom providers:

```python
from pydantic import Field
from src.registry.config import ProviderConfig

class MyProviderConfig(ProviderConfig):
    """Configuration for my custom provider."""

    api_endpoint: str = Field(..., description="API endpoint")
    api_key: str = Field(..., description="API key")
    custom_setting: str = Field(default="value")
```

## Registry Configuration

### Auto-Discovery

Automatically discover providers via entry points:

```bash
export REGISTRY_AUTO_DISCOVER=true
```

### Auto-Initialization

Automatically initialize discovered providers:

```bash
export REGISTRY_AUTO_INITIALIZE=true
```

### Default Provider

Set the default provider to use:

```bash
export REGISTRY_DEFAULT_PROVIDER=codecov
```

### Health Check Interval

Set health check frequency (in seconds):

```bash
export REGISTRY_HEALTH_CHECK_INTERVAL_SECONDS=300
```

## Secrets Management

### Secure Token Storage

Tokens are stored as `SecretStr` and won't be logged:

```python
from src.registry.secrets import CodecovSecrets

secrets = CodecovSecrets()  # Reads from environment
token = secrets.get_codecov_token()  # Safe to use
```

### Environment Variable Naming

Secrets use the same environment variable names as configuration:

```bash
# These are treated as secrets
export CODECOV_API_TOKEN="your-token"
export PROVIDER_API_TOKEN="your-token"
```

## Configuration Priority

Configuration is loaded in this order (highest to lowest priority):

1. **Environment Variables** - Override everything
2. **.env File** - Loaded if present
3. **Code Defaults** - Built-in defaults

Example:

```python
# 1. Environment: CODECOV_API_TOKEN=env-token
# 2. .env file: CODECOV_API_TOKEN=file-token
# 3. Code: CodecovConfig(api_token="code-token")

# Result: env-token (environment wins)
config = CodecovConfig()
```

## Configuration Examples

### Development Setup

```bash
# .env.development
CODECOV_API_TOKEN=dev-token
CODECOV_API_BASE_URL=https://api.codecov.io
DEBUG=true
LOG_LEVEL=DEBUG
REGISTRY_LOG_LEVEL=DEBUG
```

### Production Setup

```bash
# .env.production
CODECOV_API_TOKEN=${CODECOV_TOKEN}  # From secrets manager
CODECOV_API_BASE_URL=https://api.codecov.io
DEBUG=false
LOG_LEVEL=INFO
REGISTRY_HEALTH_CHECK_INTERVAL_SECONDS=600
```

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.12

WORKDIR /app

COPY . .

# Set environment variables
ENV CODECOV_API_TOKEN=${CODECOV_TOKEN}
ENV CODECOV_OWNER=${CODECOV_OWNER}
ENV CODECOV_REPO=${CODECOV_REPO}
ENV REGISTRY_AUTO_DISCOVER=true
ENV REGISTRY_AUTO_INITIALIZE=true

RUN pip install -e .

CMD ["test-coverage-mcp", "serve"]
```

### Kubernetes Setup

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-coverage-mcp
spec:
  template:
    spec:
      containers:
      - name: test-coverage-mcp
        image: test-coverage-mcp:latest
        env:
        - name: CODECOV_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: codecov-secrets
              key: api-token
        - name: CODECOV_OWNER
          value: "my-org"
        - name: CODECOV_REPO
          value: "my-repo"
        - name: REGISTRY_AUTO_DISCOVER
          value: "true"
```

## Validation

Configuration is validated using Pydantic:

```python
from src.registry.config import CodecovConfig
from pydantic import ValidationError

try:
    config = CodecovConfig()  # Missing required api_token
except ValidationError as e:
    print(f"Configuration error: {e}")
```

## Environment Variable Reference

### Core Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `DEBUG` | boolean | No | false | Enable debug mode |
| `LOG_LEVEL` | string | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `API_TOKEN` | string | Yes | - | API authentication token |
| `ENV_FILE` | string | No | .env | Path to .env file |

### Provider Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `{PROVIDER}_API_TOKEN` | string | Yes | - | Provider API token |
| `{PROVIDER}_API_BASE_URL` | string | No | provider-specific | API endpoint URL |
| `{PROVIDER}_TIMEOUT_SECONDS` | integer | No | 30 | Request timeout |
| `{PROVIDER}_RETRY_ATTEMPTS` | integer | No | 3 | Retry count |
| `{PROVIDER}_RETRY_DELAY_SECONDS` | float | No | 1.0 | Delay between retries |

### Registry Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `REGISTRY_AUTO_DISCOVER` | boolean | No | true | Auto-discover providers |
| `REGISTRY_AUTO_INITIALIZE` | boolean | No | true | Auto-initialize providers |
| `REGISTRY_DEFAULT_PROVIDER` | string | No | - | Default provider name |
| `REGISTRY_HEALTH_CHECK_INTERVAL_SECONDS` | integer | No | 300 | Health check frequency |
| `REGISTRY_LOG_LEVEL` | string | No | INFO | Registry logging level |

### MCP Server Configuration

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `MCP_HOST` | string | No | 0.0.0.0 | Server host address |
| `MCP_PORT` | integer | No | 8000 | Server port |
| `MCP_TRANSPORT` | string | No | sse | Transport type (sse, http-streaming, stdio) |
| `MCP_WORKERS` | integer | No | 4 | Number of worker processes |

## Troubleshooting

### Missing Configuration

```
ValidationError: api_token
  Field required [type=missing, input_value={}, input_type=dict]
```

**Solution**: Set `CODECOV_API_TOKEN` environment variable or in `.env` file.

**Verification**:
```bash
# Check if variable is set
echo $CODECOV_API_TOKEN

# Or check .env file
grep CODECOV_API_TOKEN .env
```

### Invalid Configuration

```
ValidationError: timeout_seconds
  Input should be a valid integer [type=int_parsing, input_value='invalid']
```

**Solution**: Ensure numeric values are valid (e.g., `CODECOV_TIMEOUT_SECONDS=30`).

**Verification**:
```bash
# Check variable value
echo $CODECOV_TIMEOUT_SECONDS

# Should be a number, not a string
```

### Provider Not Found

```
ValueError: Provider 'codecov' is not registered
```

**Solution**: Ensure provider is installed and `REGISTRY_AUTO_DISCOVER=true`.

**Verification**:
```bash
# Check if provider is installed
pip list | grep test-coverage-mcp

# Check registry setting
echo $REGISTRY_AUTO_DISCOVER
```

### Connection Timeout

```
TimeoutError: Provider 'codecov' request timed out after 30 seconds
```

**Solution**: Increase timeout or check network connectivity.

**Fix**:
```bash
# Increase timeout
export CODECOV_TIMEOUT_SECONDS=60

# Or check network
curl -I https://api.codecov.io
```

### Authentication Failed

```
AuthenticationError: Invalid API token for provider 'codecov'
```

**Solution**: Verify API token is correct and has required permissions.

**Verification**:
```bash
# Test API token
curl -H "Authorization: Bearer $CODECOV_API_TOKEN" \
  https://api.codecov.io/health

# Should return 200 OK
```

### Provider Health Check Failed

```
ProviderHealthError: Provider 'codecov' is currently unhealthy
```

**Solution**: Check provider status and retry later.

**Diagnosis**:
```python
from test_coverage_mcp.mcp_server.tools import describe_coverage_provider

provider = describe_coverage_provider(provider_name='codecov')
print(provider['provider']['health'])
```

## Configuration Validation Checklist

Before deploying, verify:

- [ ] All required environment variables are set
- [ ] API tokens are valid and have correct permissions
- [ ] Network connectivity to provider APIs
- [ ] Timeout values are appropriate for your network
- [ ] Provider health checks pass
- [ ] Log levels are appropriate for environment
- [ ] Secrets are not committed to version control
- [ ] Configuration is consistent across environments

## Best Practices

1. **Use .env files for development**
   ```bash
   # .env
   CODECOV_API_TOKEN=dev-token
   ```

2. **Use environment variables for production**
   ```bash
   export CODECOV_API_TOKEN=$(aws secretsmanager get-secret-value ...)
   ```

3. **Never commit secrets**
   ```bash
   # .gitignore
   .env
   .env.local
   ```

4. **Use different configs per environment**
   ```bash
   .env.development
   .env.staging
   .env.production
   ```

5. **Validate configuration on startup**
   ```python
   try:
       config = ApplicationConfig.from_env()
   except ValidationError as e:
       logger.error(f"Invalid configuration: {e}")
       sys.exit(1)
   ```

## Next Steps

- [Provider Specification](../architecture/provider-specification.md)
- [Plugin System Architecture](../architecture/plugin-system.md)
- [MCP Tools Overview](../mcp-tools/overview.md)
