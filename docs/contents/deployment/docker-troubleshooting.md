# Docker Troubleshooting Guide

## Container Issues

### Container Won't Start

**Symptom**: Container exits immediately after starting

**Diagnosis**:
```bash
# Check exit code
docker ps -a | grep test-coverage-mcp

# View logs
docker logs <container-id>

# Inspect container
docker inspect <container-id>
```

**Solutions**:

1. **Check configuration**
   ```bash
   # Verify environment variables
   docker inspect <container-id> | grep -A 50 Env
   ```

2. **Check entrypoint**
   ```bash
   # Run with interactive shell
   docker run -it test-coverage-mcp:latest /bin/bash
   ```

3. **Check dependencies**
   ```bash
   # Verify all dependencies are installed
   docker run test-coverage-mcp:latest pip list
   ```

### Container Crashes Repeatedly

**Symptom**: Container keeps restarting

**Diagnosis**:
```bash
# Check restart policy
docker inspect <container-id> | grep -A 5 RestartPolicy

# View recent logs
docker logs --tail 50 <container-id>

# Check resource usage
docker stats <container-id>
```

**Solutions**:

1. **Increase resource limits**
   ```bash
   docker run --memory=1g --cpus=2 test-coverage-mcp:latest
   ```

2. **Disable auto-restart for debugging**
   ```bash
   docker run --restart=no test-coverage-mcp:latest
   ```

3. **Check for memory leaks**
   ```bash
   # Monitor memory usage
   docker stats --no-stream <container-id>
   ```

## Network Issues

### Port Already in Use

**Symptom**: `Error response from daemon: driver failed programming external connectivity on endpoint`

**Diagnosis**:
```bash
# Find process using port
lsof -i :8000
netstat -tulpn | grep 8000
```

**Solutions**:

```bash
# Use different port
docker run -p 9000:8000 test-coverage-mcp:latest

# Kill process using port
kill -9 <PID>

# Check Docker port mappings
docker port <container-id>
```

### Can't Connect to Container

**Symptom**: Connection refused when accessing `http://localhost:8000`

**Diagnosis**:
```bash
# Check if container is running
docker ps | grep test-coverage-mcp

# Check port mapping
docker port <container-id>

# Test connectivity from host
curl http://localhost:8000/health

# Test from inside container
docker exec <container-id> curl http://localhost:8000/health
```

**Solutions**:

1. **Verify port mapping**
   ```bash
   # Check if port is correctly mapped
   docker inspect <container-id> | grep -A 10 PortBindings
   ```

2. **Check firewall**
   ```bash
   # On Linux
   sudo ufw status
   sudo ufw allow 8000

   # On macOS
   # Check System Preferences > Security & Privacy > Firewall
   ```

3. **Use correct hostname**
   ```bash
   # From host machine
   curl http://localhost:8000

   # From another container
   curl http://<container-name>:8000
   ```

### DNS Resolution Issues

**Symptom**: `Name or service not known` errors

**Diagnosis**:
```bash
# Test DNS from container
docker exec <container-id> nslookup google.com

# Check DNS configuration
docker inspect <container-id> | grep -i dns
```

**Solutions**:

```bash
# Specify DNS servers
docker run --dns 8.8.8.8 --dns 8.8.4.4 test-coverage-mcp:latest

# In Docker Compose
services:
  test-coverage-mcp:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

## Health Check Issues

### Health Check Failing

**Symptom**: Health check status shows `unhealthy`

**Diagnosis**:
```bash
# Check health status
docker inspect --format='{{json .State.Health}}' <container-id>

# View health check logs
docker inspect <container-id> | grep -A 20 Health

# Test health endpoint manually
docker exec <container-id> curl http://localhost:8000/health
```

**Solutions**:

1. **Verify health endpoint is working**
   ```bash
   # Inside container
   docker exec <container-id> curl -v http://localhost:8000/health
   ```

2. **Increase health check timeout**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s  # Increase this
     retries: 3
     start_period: 30s
   ```

3. **Check application logs**
   ```bash
   docker logs <container-id> | grep -i error
   ```

## Resource Issues

### Out of Memory

**Symptom**: Container killed with `OOMKilled` status

**Diagnosis**:
```bash
# Check if OOMKilled
docker inspect <container-id> | grep OOMKilled

# Monitor memory usage
docker stats <container-id>

# Check memory limits
docker inspect <container-id> | grep -i memory
```

**Solutions**:

```bash
# Increase memory limit
docker run --memory=1g test-coverage-mcp:latest

# In Docker Compose
services:
  test-coverage-mcp:
    deploy:
      resources:
        limits:
          memory: 1G
```

### High CPU Usage

**Symptom**: Container consuming excessive CPU

**Diagnosis**:
```bash
# Monitor CPU usage
docker stats <container-id>

# Profile application
docker exec <container-id> python -m cProfile -o /tmp/profile.prof /app/app.py
```

**Solutions**:

1. **Limit CPU usage**
   ```bash
   docker run --cpus=1 test-coverage-mcp:latest
   ```

2. **Check for infinite loops**
   ```bash
   docker logs <container-id> | tail -100
   ```

3. **Optimize application**
   - Review application logs
   - Check for resource-intensive operations
   - Profile the application

## Volume and Mount Issues

### Permission Denied on Volume

**Symptom**: `Permission denied` when accessing mounted volumes

**Diagnosis**:
```bash
# Check volume permissions
ls -la /path/to/volume

# Check container user
docker exec <container-id> id

# Check volume mount
docker inspect <container-id> | grep -A 10 Mounts
```

**Solutions**:

```bash
# Fix permissions
sudo chown -R 1000:1000 /path/to/volume
chmod 755 /path/to/volume

# Run with specific user
docker run --user 1000:1000 -v /path/to/volume:/app/data test-coverage-mcp:latest
```

### Volume Not Mounting

**Symptom**: Volume not accessible inside container

**Diagnosis**:
```bash
# Check if volume is mounted
docker inspect <container-id> | grep -A 10 Mounts

# List volumes
docker volume ls

# Inspect volume
docker volume inspect <volume-name>
```

**Solutions**:

```bash
# Verify path exists
ls -la /path/to/volume

# Use absolute paths
docker run -v /absolute/path:/app/data test-coverage-mcp:latest

# Check Docker volume driver
docker volume inspect <volume-name> | grep Driver
```

## Image Issues

### Image Build Fails

**Symptom**: `docker build` command fails

**Diagnosis**:
```bash
# Build with verbose output
docker build --progress=plain -t test-coverage-mcp:latest .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile
```

**Solutions**:

1. **Check base image availability**
   ```bash
   docker pull python:3.13-slim
   ```

2. **Check build context**
   ```bash
   # Verify files exist
   ls -la test-coverage-mcp/
   ls -la pyproject.toml
   ```

3. **Clear build cache**
   ```bash
   docker build --no-cache -t test-coverage-mcp:latest .
   ```

### Image Too Large

**Symptom**: Docker image size is unexpectedly large

**Diagnosis**:
```bash
# Check image size
docker images test-coverage-mcp

# Analyze layers
docker history test-coverage-mcp:latest

# Inspect image
docker inspect test-coverage-mcp:latest
```

**Solutions**:

1. **Use multi-stage builds** (already implemented)
2. **Remove unnecessary files**
   ```dockerfile
   RUN apt-get clean && rm -rf /var/lib/apt/lists/*
   ```

3. **Use .dockerignore** (already implemented)

## Logging Issues

### Logs Not Appearing

**Symptom**: `docker logs` returns empty output

**Diagnosis**:
```bash
# Check if container is running
docker ps | grep test-coverage-mcp

# Check log driver
docker inspect <container-id> | grep -i logdriver

# Check application output
docker exec <container-id> tail -f /var/log/app.log
```

**Solutions**:

1. **Ensure unbuffered output**
   ```bash
   export PYTHONUNBUFFERED=1
   ```

2. **Check log driver configuration**
   ```bash
   docker run --log-driver json-file test-coverage-mcp:latest
   ```

3. **Increase log retention**
   ```bash
   docker run \
     --log-opt max-size=10m \
     --log-opt max-file=3 \
     test-coverage-mcp:latest
   ```

### Logs Too Large

**Symptom**: Log files consuming excessive disk space

**Solutions**:

```bash
# Configure log rotation
docker run \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  test-coverage-mcp:latest

# Clean up old logs
docker logs --tail 0 <container-id>
docker container prune
```

## Docker Compose Issues

### Service Won't Start

**Symptom**: `docker-compose up` fails

**Diagnosis**:
```bash
# Check compose file syntax
docker-compose config

# View detailed output
docker-compose up --verbose

# Check service logs
docker-compose logs <service-name>
```

**Solutions**:

1. **Validate compose file**
   ```bash
   docker-compose -f docker-compose.prod.yml config
   ```

2. **Check environment variables**
   ```bash
   cat .env
   docker-compose config | grep -i codecov
   ```

3. **Check service dependencies**
   ```bash
   docker-compose ps
   ```

### Services Can't Communicate

**Symptom**: Services can't reach each other

**Diagnosis**:
```bash
# Check network
docker network ls
docker network inspect <network-name>

# Test connectivity
docker-compose exec <service> ping <other-service>
```

**Solutions**:

```bash
# Ensure services are on same network
docker-compose ps

# Use service name for DNS
curl http://test-coverage-mcp:8000/health
```

## Performance Issues

### Slow Container Startup

**Symptom**: Container takes long time to start

**Solutions**:

1. **Optimize Dockerfile**
   - Reduce layer count
   - Cache dependencies
   - Use .dockerignore

2. **Use BuildKit**
   ```bash
   DOCKER_BUILDKIT=1 docker build -t test-coverage-mcp:latest .
   ```

3. **Increase start_period**
   ```yaml
   healthcheck:
     start_period: 60s
   ```

### Slow Application Performance

**Symptom**: Application runs slowly in container

**Solutions**:

1. **Check resource limits**
   ```bash
   docker stats <container-id>
   ```

2. **Profile application**
   ```bash
   docker exec <container-id> python -m cProfile app.py
   ```

3. **Check I/O performance**
   ```bash
   docker exec <container-id> iostat -x 1
   ```

## Getting Help

### Collect Diagnostic Information

```bash
# System information
docker version
docker info

# Container information
docker inspect <container-id>

# Logs
docker logs <container-id> > /tmp/logs.txt

# Resource usage
docker stats <container-id> --no-stream

# Network information
docker network inspect <network-name>
```

### Report Issues

When reporting issues, include:
1. Docker version
2. Container logs
3. Environment variables (without sensitive data)
4. Steps to reproduce
5. Expected vs actual behavior

## See Also

- [Docker Deployment Guide](./docker.md)
- [Environment Variables Reference](./environment-variables.md)
- [Docker Documentation](https://docs.docker.com/)
