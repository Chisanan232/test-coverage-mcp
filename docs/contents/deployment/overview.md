# Deployment Overview

## Deployment Options

test-coverage-mcp can be deployed in multiple ways depending on your needs.

## Quick Comparison

| Method | Setup | Complexity | Use Case |
|--------|-------|-----------|----------|
| CLI (stdio) | 5 min | Low | Claude Desktop, local development |
| CLI (HTTP) | 10 min | Low | Web clients, custom integrations |
| Docker | 10 min | Low | Production, containerized environments |
| Docker Compose | 15 min | Medium | Multi-container setups, testing |
| Kubernetes | 30 min | High | Enterprise, scalable deployments |

## Deployment Methods

### 1. CLI Deployment

**Best for**: Local development, Claude Desktop integration

**Quick Start**:
```bash
# Install
pip install test-coverage-mcp

# Run with stdio transport (Claude Desktop)
test-coverage-mcp serve --transport stdio

# Run with HTTP transport
test-coverage-mcp serve --transport http --host 0.0.0.0 --port 8000
```

**Advantages**:
- Simplest setup
- No Docker required
- Direct integration with Claude Desktop
- Easy debugging

**Disadvantages**:
- Manual dependency management
- No isolation
- Harder to scale

**See**: [CLI Deployment Guide](./cli.md)

### 2. Docker Deployment

**Best for**: Production, containerized environments

**Quick Start**:
```bash
# Build image
docker build -t test-coverage-mcp:latest .

# Run container
docker run -p 8000:8000 \
  -e CODECOV_TOKEN="your-token" \
  test-coverage-mcp:latest
```

**Advantages**:
- Isolated environment
- Reproducible deployments
- Easy scaling
- Version control
- Production-ready

**Disadvantages**:
- Requires Docker
- Slightly more setup

**See**: [Docker Deployment Guide](./docker.md)

### 3. Docker Compose Deployment

**Best for**: Development, testing, multi-container setups

**Quick Start**:
```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

**Advantages**:
- Easy multi-container management
- Development and production configs
- Health checks included
- Resource limits configured

**Disadvantages**:
- Requires Docker Compose
- More configuration

**See**: [Docker Compose Examples](../docker-compose.md)

### 4. Kubernetes Deployment

**Best for**: Enterprise, scalable deployments

**Quick Start**:
```bash
# Create namespace
kubectl create namespace test-coverage-mcp

# Deploy
kubectl apply -f k8s/deployment.yaml -n test-coverage-mcp

# Expose service
kubectl expose deployment test-coverage-mcp \
  --type=LoadBalancer \
  --port=8000 \
  -n test-coverage-mcp
```

**Advantages**:
- Highly scalable
- Auto-healing
- Rolling updates
- Resource management
- Enterprise-grade

**Disadvantages**:
- Complex setup
- Requires Kubernetes knowledge
- Overkill for small deployments

**See**: [Kubernetes Deployment Guide](./kubernetes.md)

## Configuration

All deployment methods use the same configuration:

### Environment Variables

```bash
# Provider authentication
CODECOV_TOKEN=your-token
COVERALLS_TOKEN=your-token

# Server configuration
TRANSPORT=sse              # sse or http
HOST=0.0.0.0              # Bind address
PORT=8000                 # Bind port
LOG_LEVEL=info            # debug, info, warning, error

# Development
RELOAD=false              # Auto-reload on code changes
INTEGRATED=true           # Integrated mode
```

### Configuration File

```yaml
# config.yaml
server:
  transport: sse
  host: 0.0.0.0
  port: 8000
  log_level: info

providers:
  codecov:
    token: ${CODECOV_TOKEN}
  coveralls:
    token: ${COVERALLS_TOKEN}

features:
  integrated: true
  reload: false
```

**See**: [Environment Variables Reference](./environment-variables.md)

## Choosing a Deployment Method

### For Local Development
```bash
# Option 1: CLI (simplest)
pip install test-coverage-mcp
test-coverage-mcp serve --transport stdio

# Option 2: Docker (isolated)
docker-compose -f docker-compose.dev.yml up
```

### For Claude Desktop
```bash
# Use CLI with stdio transport
test-coverage-mcp serve --transport stdio
```

### For Web Application
```bash
# Option 1: CLI with HTTP
test-coverage-mcp serve --transport http --port 8000

# Option 2: Docker
docker run -p 8000:8000 test-coverage-mcp:latest
```

### For Production
```bash
# Option 1: Docker (recommended)
docker run -p 8000:8000 \
  -e CODECOV_TOKEN="$CODECOV_TOKEN" \
  test-coverage-mcp:latest

# Option 2: Kubernetes (enterprise)
kubectl apply -f k8s/deployment.yaml
```

## Health Checks

All deployments support health checks:

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed

# Liveness
curl http://localhost:8000/health/live

# Readiness
curl http://localhost:8000/health/ready
```

## Monitoring

### Logs

**CLI**:
```bash
test-coverage-mcp serve --log-level debug
```

**Docker**:
```bash
docker logs -f <container-id>
```

**Docker Compose**:
```bash
docker-compose logs -f
```

### Metrics

- Response time
- Error rate
- Provider health
- Request count

## Security

### Authentication

- Use environment variables for tokens
- Never commit secrets
- Rotate tokens regularly
- Use secrets management (Vault, AWS Secrets Manager, etc.)

### Network

- Use HTTPS in production
- Restrict network access
- Use firewalls
- Implement rate limiting

### Container

- Run as non-root user
- Use read-only filesystem
- Drop unnecessary capabilities
- Scan images for vulnerabilities

**See**: [Security Best Practices](./security.md)

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Use different port
docker run -p 9000:8000 test-coverage-mcp:latest
```

**Provider authentication fails**:
```bash
# Verify token
echo $CODECOV_TOKEN

# Check provider health
curl http://localhost:8000/health/detailed
```

**Container won't start**:
```bash
# Check logs
docker logs <container-id>

# Run interactively
docker run -it test-coverage-mcp:latest /bin/bash
```

**See**: [Docker Troubleshooting Guide](./docker-troubleshooting.md)

## Performance Tuning

### Resource Allocation

```yaml
# Docker Compose
services:
  test-coverage-mcp:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

### Caching

- Enable response caching
- Use CDN for static content
- Cache provider responses

### Scaling

- Horizontal scaling with load balancer
- Multiple provider instances
- Connection pooling

## Backup & Recovery

### Configuration Backup

```bash
# Backup config
cp config.yaml config.yaml.backup

# Backup environment
env | grep -E "CODECOV|COVERALLS" > .env.backup
```

### Data Recovery

- Restore from backup
- Verify provider connectivity
- Run health checks

## Deployment Checklist

- [ ] Configure environment variables
- [ ] Set up provider authentication
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure health checks
- [ ] Test deployment
- [ ] Set up backups
- [ ] Document configuration
- [ ] Train team
- [ ] Plan maintenance

## Next Steps

1. Choose deployment method
2. Follow specific deployment guide
3. Configure environment
4. Test deployment
5. Set up monitoring
6. Document setup

## See Also

- [CLI Deployment Guide](./cli.md)
- [Docker Deployment Guide](./docker.md)
- [Environment Variables Reference](./environment-variables.md)
- [Security Best Practices](./security.md)
- [Troubleshooting Guide](./docker-troubleshooting.md)
