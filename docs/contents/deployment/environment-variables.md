# Environment Variables Reference

## Overview

This document describes all environment variables supported by test-coverage-mcp.

## Provider Authentication

### CODECOV_TOKEN

**Type**: String  
**Required**: No (required if using Codecov provider)  
**Default**: None

Codecov API token for authentication.

```bash
export CODECOV_TOKEN="your-codecov-token"
```

### COVERALLS_TOKEN

**Type**: String  
**Required**: No (required if using Coveralls provider)  
**Default**: None

Coveralls API token for authentication.

```bash
export COVERALLS_TOKEN="your-coveralls-token"
```

## Server Configuration

### TRANSPORT

**Type**: String  
**Required**: No  
**Default**: `sse`  
**Valid Values**: `sse`, `http`

Transport protocol for MCP communication.

```bash
export TRANSPORT=sse
```

### HOST

**Type**: String  
**Required**: No  
**Default**: `0.0.0.0`

Host address to bind the server to.

```bash
export HOST=0.0.0.0
```

### PORT

**Type**: Integer  
**Required**: No  
**Default**: `8000`

Port to bind the server to.

```bash
export PORT=8000
```

### SERVER_PORT

**Type**: Integer  
**Required**: No  
**Default**: `8000`

Alias for `PORT`. Used in Docker images.

```bash
export SERVER_PORT=8000
```

## Logging Configuration

### LOG_LEVEL

**Type**: String  
**Required**: No  
**Default**: `info`  
**Valid Values**: `debug`, `info`, `warning`, `error`, `critical`

Logging level for the application.

```bash
export LOG_LEVEL=info
```

### RELOAD

**Type**: Boolean  
**Required**: No  
**Default**: `false`

Enable auto-reload on code changes (development only).

```bash
export RELOAD=true
```

## Application Configuration

### TEST_COVERAGE_MCP_CONFIG

**Type**: String  
**Required**: No  
**Default**: None

Path to configuration file.

```bash
export TEST_COVERAGE_MCP_CONFIG=/etc/test-coverage-mcp/config.yaml
```

### INTEGRATED

**Type**: Boolean  
**Required**: No  
**Default**: `true`

Run in integrated mode (combined web server and MCP).

```bash
export INTEGRATED=true
```

## Docker-specific Variables

### PYTHONDONTWRITEBYTECODE

**Type**: Boolean  
**Required**: No  
**Default**: `1`

Prevent Python from writing bytecode files.

```bash
export PYTHONDONTWRITEBYTECODE=1
```

### PYTHONUNBUFFERED

**Type**: Boolean  
**Required**: No  
**Default**: `1`

Run Python in unbuffered mode for real-time logging.

```bash
export PYTHONUNBUFFERED=1
```

## Setting Environment Variables

### Command Line

```bash
docker run -e CODECOV_TOKEN="token" test-coverage-mcp:latest
```

### Docker Compose (.env file)

Create a `.env` file in the project root:

```env
CODECOV_TOKEN=your-codecov-token
COVERALLS_TOKEN=your-coveralls-token
TRANSPORT=sse
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
```

Then run:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Compose (inline)

```bash
docker-compose -f docker-compose.prod.yml \
  -e CODECOV_TOKEN="token" \
  -e COVERALLS_TOKEN="token" \
  up -d
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-coverage-mcp-config
data:
  TRANSPORT: sse
  HOST: "0.0.0.0"
  PORT: "8000"
  LOG_LEVEL: info

---
apiVersion: v1
kind: Secret
metadata:
  name: test-coverage-mcp-secrets
type: Opaque
stringData:
  CODECOV_TOKEN: your-codecov-token
  COVERALLS_TOKEN: your-coveralls-token

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-coverage-mcp
spec:
  template:
    spec:
      containers:
      - name: test-coverage-mcp
        envFrom:
        - configMapRef:
            name: test-coverage-mcp-config
        - secretRef:
            name: test-coverage-mcp-secrets
```

### Systemd Service

Create `/etc/systemd/system/test-coverage-mcp.service`:

```ini
[Service]
Environment="CODECOV_TOKEN=your-token"
Environment="COVERALLS_TOKEN=your-token"
Environment="TRANSPORT=sse"
Environment="LOG_LEVEL=info"
ExecStart=/usr/local/bin/test-coverage-mcp serve
```

## Environment Variable Precedence

Variables are loaded in the following order (later overrides earlier):

1. System environment variables
2. `.env` file (if present)
3. Configuration file (if specified)
4. Command-line options

## Security Best Practices

### Token Management

1. **Never commit tokens to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo ".env.local" >> .gitignore
   ```

2. **Use secrets management**
   - Docker Secrets (Swarm)
   - Kubernetes Secrets
   - HashiCorp Vault
   - AWS Secrets Manager

3. **Rotate tokens regularly**
   ```bash
   # Update token
   export CODECOV_TOKEN="new-token"
   
   # Restart service
   docker-compose restart
   ```

4. **Mask tokens in logs**
   ```bash
   # Tokens are automatically masked in output
   docker logs <container-id> | grep TOKEN
   # Output: CODECOV_TOKEN=****...****
   ```

### Environment Variable Security

```bash
# Use read-only environment files
chmod 600 .env

# Use secrets for sensitive data
docker secret create codecov_token -
# Enter token and press Ctrl+D

# Reference in compose file
docker-compose.yml:
  environment:
    CODECOV_TOKEN_FILE: /run/secrets/codecov_token
```

## Troubleshooting

### Variables Not Being Loaded

```bash
# Check if variables are set
env | grep CODECOV

# Check Docker environment
docker inspect <container-id> | grep -A 20 Env

# Check .env file
cat .env
```

### Token Authentication Failures

```bash
# Verify token is set
echo $CODECOV_TOKEN

# Test token validity
curl -H "Authorization: token $CODECOV_TOKEN" \
  https://codecov.io/api/v2/repos

# Check logs for authentication errors
docker logs <container-id> | grep -i auth
```

### Configuration Not Applied

```bash
# Verify configuration file path
echo $TEST_COVERAGE_MCP_CONFIG

# Check file permissions
ls -la $TEST_COVERAGE_MCP_CONFIG

# Validate YAML syntax
python -m yaml $TEST_COVERAGE_MCP_CONFIG
```

## Examples

### Development Setup

```bash
export CODECOV_TOKEN="dev-token"
export LOG_LEVEL=debug
export RELOAD=true
docker-compose -f docker-compose.dev.yml up
```

### Production Setup

```bash
export CODECOV_TOKEN="prod-token"
export COVERALLS_TOKEN="prod-token"
export LOG_LEVEL=info
export RELOAD=false
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline

```bash
# GitHub Actions
env:
  CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
  COVERALLS_TOKEN: ${{ secrets.COVERALLS_TOKEN }}
  LOG_LEVEL: info
```

## See Also

- [Docker Deployment Guide](./docker.md)
- [CLI Deployment Guide](./cli.md)
- [Configuration Guide](../configuration.md)
