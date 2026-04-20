# CLI Deployment Guide

## Overview

This guide covers deploying and configuring the test-coverage-mcp CLI in production environments.

## Installation

### From PyPI

```bash
pip install test-coverage-mcp
```

### From Source

```bash
git clone https://github.com/Chisanan232/test-coverage-mcp.git
cd test-coverage-mcp/test-coverage-mcp
pip install -e .
```

### System-wide Installation

```bash
sudo pip install test-coverage-mcp
```

## Configuration

### Configuration File

Create a configuration file at `~/.test-coverage-mcp/config.yaml`:

```yaml
# Provider settings
provider:
  default: codecov
  codecov:
    token: ${CODECOV_TOKEN}
    base_url: https://codecov.io

# Server settings
server:
  transport: stdio
  host: 127.0.0.1
  port: 8000

# Logging
logging:
  level: INFO
  format: json
```

### Environment Variables

Set environment variables for authentication:

```bash
export CODECOV_TOKEN="your-codecov-token"
export COVERALLS_TOKEN="your-coveralls-token"
export TEST_COVERAGE_MCP_CONFIG="/path/to/config.yaml"
```

## Running the Server

### Stdio Transport (Default)

```bash
test-coverage-mcp serve
```

This is ideal for use with Claude and other MCP clients.

### HTTP Transport

```bash
test-coverage-mcp serve --transport http --host 0.0.0.0 --port 8000
```

### With Custom Configuration

```bash
test-coverage-mcp --config /etc/test-coverage-mcp/config.yaml serve
```

## Systemd Service

Create `/etc/systemd/system/test-coverage-mcp.service`:

```ini
[Unit]
Description=Test Coverage MCP Server
After=network.target

[Service]
Type=simple
User=coverage
Group=coverage
WorkingDirectory=/home/coverage
Environment="CODECOV_TOKEN=your-token"
ExecStart=/usr/local/bin/test-coverage-mcp serve --transport http --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable test-coverage-mcp
sudo systemctl start test-coverage-mcp
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim

RUN pip install test-coverage-mcp

ENV CODECOV_TOKEN=""
ENV COVERALLS_TOKEN=""

EXPOSE 8000

CMD ["test-coverage-mcp", "serve", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  test-coverage-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      CODECOV_TOKEN: ${CODECOV_TOKEN}
      COVERALLS_TOKEN: ${COVERALLS_TOKEN}
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-coverage-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: test-coverage-mcp
  template:
    metadata:
      labels:
        app: test-coverage-mcp
    spec:
      containers:
      - name: test-coverage-mcp
        image: test-coverage-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: CODECOV_TOKEN
          valueFrom:
            secretKeyRef:
              name: coverage-tokens
              key: codecov
        - name: COVERALLS_TOKEN
          valueFrom:
            secretKeyRef:
              name: coverage-tokens
              key: coveralls
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: test-coverage-mcp
spec:
  selector:
    app: test-coverage-mcp
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

Deploy:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Health Checks

### Using the Doctor Command

```bash
test-coverage-mcp doctor
```

### HTTP Health Endpoint

When running with HTTP transport:

```bash
curl http://localhost:8000/health
```

### Systemd Health Check

```bash
systemctl status test-coverage-mcp
```

## Monitoring

### Logging

Enable verbose logging:

```bash
test-coverage-mcp --verbose serve
```

### Metrics

Monitor resource usage:

```bash
# CPU and memory
ps aux | grep test-coverage-mcp

# Network connections
netstat -tulpn | grep 8000
```

## Security Considerations

1. **Token Management**
   - Use environment variables or secrets management
   - Never commit tokens to version control
   - Rotate tokens regularly

2. **Network Security**
   - Use HTTPS for HTTP transport in production
   - Restrict access with firewall rules
   - Use VPN or private networks when possible

3. **Access Control**
   - Run with minimal privileges
   - Use dedicated user accounts
   - Implement authentication/authorization

4. **Updates**
   - Keep the package updated
   - Monitor security advisories
   - Test updates in staging first

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
test-coverage-mcp serve --transport http --port 9000
```

### Token Issues

```bash
# Verify token is set
echo $CODECOV_TOKEN

# Run doctor to check configuration
test-coverage-mcp doctor --verbose
```

### Connection Issues

```bash
# Test connectivity
curl -v http://localhost:8000/health

# Check firewall
sudo ufw status
```

## Performance Tuning

### Resource Limits

For Docker:
```bash
docker run --memory=512m --cpus=0.5 test-coverage-mcp
```

For Kubernetes:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Connection Pooling

Configure in `config.yaml`:
```yaml
http:
  pool_size: 10
  timeout: 30
```

## Backup and Recovery

### Configuration Backup

```bash
cp -r ~/.test-coverage-mcp ~/.test-coverage-mcp.backup
```

### Log Rotation

For systemd:
```ini
StandardOutput=journal
StandardError=journal
```

## See Also

- [CLI Overview](../cli/overview.md)
- [CLI Commands Reference](../cli/commands.md)
