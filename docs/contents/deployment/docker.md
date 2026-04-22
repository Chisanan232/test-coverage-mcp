# Docker Deployment Guide

## Overview

This guide covers deploying test-coverage-mcp using Docker containers.

## Quick Start

### Using Docker Compose (Development)

```bash
# Clone the repository
git clone https://github.com/Chisanan232/test-coverage-mcp.git
cd test-coverage-mcp

# Start the service
docker-compose -f docker-compose.dev.yml up
```

The service will be available at `http://localhost:8000`.

### Using Docker Compose (Production)

```bash
# Set environment variables
export CODECOV_TOKEN="your-token"
export COVERALLS_TOKEN="your-token"

# Start the service
docker-compose -f docker-compose.prod.yml up -d
```

## Building Docker Images

### Build from Source

```bash
# Build the image
docker build -t test-coverage-mcp:latest .

# Run the container
docker run -p 8000:8000 test-coverage-mcp:latest
```

### Using Pre-built Images

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/Chisanan232/test-coverage-mcp:latest

# Run the container
docker run -p 8000:8000 ghcr.io/Chisanan232/test-coverage-mcp:latest
```

## Docker Compose

### Development Setup

```bash
docker-compose -f docker-compose.dev.yml up
```

Features:
- Hot reload enabled
- Debug logging
- Volume mounts for live code changes
- Health checks

### Production Setup

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Features:
- Resource limits
- Security options
- Read-only root filesystem
- Health checks with longer intervals
- Automatic restart policy

## Environment Variables

### Required Variables

- `CODECOV_TOKEN` - Codecov API token (if using Codecov provider)
- `COVERALLS_TOKEN` - Coveralls API token (if using Coveralls provider)

### Optional Variables

- `TRANSPORT` - Transport type: `sse` or `http` (default: `sse`)
- `HOST` - Host to bind to (default: `0.0.0.0`)
- `PORT` - Port to bind to (default: `8000`)
- `LOG_LEVEL` - Logging level: `debug`, `info`, `warning`, `error` (default: `info`)
- `RELOAD` - Enable auto-reload (default: `false`)

### Setting Environment Variables

**With Docker:**
```bash
docker run -e CODECOV_TOKEN="token" -p 8000:8000 test-coverage-mcp:latest
```

**With Docker Compose:**
```bash
# Create .env file
echo "CODECOV_TOKEN=your-token" > .env
echo "COVERALLS_TOKEN=your-token" >> .env

# Run with .env file
docker-compose -f docker-compose.prod.yml up -d
```

## Health Checks

### Basic Health Check

```bash
curl http://localhost:8000/health
```

### Detailed Health Check

```bash
curl http://localhost:8000/health/detailed
```

### Liveness Check

```bash
curl http://localhost:8000/health/live
```

### Readiness Check

```bash
curl http://localhost:8000/health/ready
```

## Docker Networking

### Custom Network

```bash
# Create a custom network
docker network create test-coverage-mcp-net

# Run container on custom network
docker run --network test-coverage-mcp-net -p 8000:8000 test-coverage-mcp:latest
```

### Multi-Container Setup

```yaml
version: '3.8'

services:
  test-coverage-mcp:
    image: test-coverage-mcp:latest
    networks:
      - app-network
    environment:
      CODECOV_TOKEN: ${CODECOV_TOKEN}

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    networks:
      - app-network
    depends_on:
      - test-coverage-mcp

networks:
  app-network:
    driver: bridge
```

## Volume Mounts

### Configuration Files

```bash
docker run \
  -v ~/.test-coverage-mcp/config.yaml:/app/config.yaml \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

### Development with Source Code

```bash
docker run \
  -v $(pwd)/test-coverage-mcp/src:/app/test-coverage-mcp/src \
  -e RELOAD=true \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

## Resource Management

### Memory Limits

```bash
docker run \
  --memory=512m \
  --memory-reservation=256m \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

### CPU Limits

```bash
docker run \
  --cpus=1 \
  --cpus-shares=1024 \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

## Logging

### View Logs

```bash
# Real-time logs
docker logs -f <container-id>

# Last 100 lines
docker logs --tail 100 <container-id>

# With timestamps
docker logs -t <container-id>
```

### Log Drivers

**JSON File (default):**
```bash
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

**Syslog:**
```bash
docker run \
  --log-driver syslog \
  --log-opt syslog-address=udp://localhost:514 \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

## Security

### Non-root User

The container runs as a non-root user (`appuser`) by default.

### Read-only Filesystem

In production, the root filesystem is read-only. Temporary files are written to `/tmp` and `/var/tmp`.

### Security Options

```bash
docker run \
  --security-opt no-new-privileges:true \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  -p 8000:8000 \
  test-coverage-mcp:latest
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs <container-id>

# Inspect container
docker inspect <container-id>

# Run with interactive shell
docker run -it test-coverage-mcp:latest /bin/bash
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Use different port
docker run -p 9000:8000 test-coverage-mcp:latest
```

### Health Check Failing

```bash
# Check health status
docker inspect --format='{{json .State.Health}}' <container-id>

# Test health endpoint manually
docker exec <container-id> curl http://localhost:8000/health
```

### Out of Memory

```bash
# Increase memory limit
docker run --memory=1g -p 8000:8000 test-coverage-mcp:latest

# Check memory usage
docker stats <container-id>
```

## Performance Optimization

### Layer Caching

The Dockerfile is optimized for layer caching:
1. Configuration files are copied first
2. Dependencies are installed
3. Source code is copied last

This ensures that code changes don't invalidate the dependency cache.

### Multi-stage Build

The Dockerfile uses multi-stage builds:
- **Builder stage**: Installs dependencies
- **Runtime stage**: Contains only runtime dependencies

This reduces the final image size.

### Image Size

```bash
# Check image size
docker images test-coverage-mcp

# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t test-coverage-mcp:latest .
```

## See Also

- [Docker Compose Examples](./docker-compose.md)
- [Environment Variables Reference](./environment-variables.md)
- [CLI Deployment Guide](./cli.md)
