# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: Package not found

**Error**: `ModuleNotFoundError: No module named 'test_coverage_mcp'`

**Solution**:
```bash
# Reinstall package
pip install -e .

# Or with uv
uv pip install -e .

# Verify installation
python -c "import test_coverage_mcp; print(test_coverage_mcp.__version__)"
```

#### Issue: Dependency conflicts

**Error**: `ERROR: pip's dependency resolver does not currently take into account...`

**Solution**:
```bash
# Clear cache and reinstall
pip cache purge
pip install --no-cache-dir test-coverage-mcp

# Or use uv
uv sync --refresh
```

### Provider Issues

#### Issue: Provider not found

**Error**: `ProviderNotFound: Provider 'codecov' not found`

**Solution**:
```bash
# List available providers
test-coverage-mcp providers list

# Install provider
pip install test-coverage-mcp-codecov

# Verify installation
test-coverage-mcp providers describe codecov
```

#### Issue: Authentication failure

**Error**: `AuthenticationError: Invalid token`

**Solution**:
```bash
# Verify token is set
echo $CODECOV_TOKEN

# Test token validity
curl -H "Authorization: token $CODECOV_TOKEN" \
  https://codecov.io/api/v2/repos

# Update token
export CODECOV_TOKEN="new-token"

# Test provider health
test-coverage-mcp doctor
```

#### Issue: Provider timeout

**Error**: `TimeoutError: Provider request timed out`

**Solution**:
```bash
# Increase timeout
export PROVIDER_TIMEOUT=60

# Check provider health
test-coverage-mcp doctor

# Check network connectivity
ping codecov.io
curl -I https://codecov.io
```

### Server Issues

#### Issue: Port already in use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Use different port
test-coverage-mcp serve --port 9000
```

#### Issue: Server won't start

**Error**: `Failed to start server`

**Solution**:
```bash
# Check logs
test-coverage-mcp serve --log-level debug

# Verify configuration
test-coverage-mcp doctor

# Check environment
env | grep -E "TRANSPORT|HOST|PORT"
```

#### Issue: Health check failing

**Error**: `Health check failed`

**Solution**:
```bash
# Check detailed health
curl http://localhost:8000/health/detailed

# Check provider health
test-coverage-mcp doctor

# Check logs
docker logs <container-id>
```

### CLI Issues

#### Issue: Command not found

**Error**: `command not found: test-coverage-mcp`

**Solution**:
```bash
# Verify installation
which test-coverage-mcp

# Reinstall
pip install test-coverage-mcp

# Add to PATH
export PATH="$PATH:~/.local/bin"
```

#### Issue: Permission denied

**Error**: `Permission denied: test-coverage-mcp`

**Solution**:
```bash
# Fix permissions
chmod +x ~/.local/bin/test-coverage-mcp

# Or reinstall
pip install --force-reinstall test-coverage-mcp
```

### Docker Issues

#### Issue: Image build fails

**Error**: `failed to build: ...`

**Solution**:
```bash
# Check Dockerfile
docker build --progress=plain -t test-coverage-mcp:latest .

# Clear cache
docker build --no-cache -t test-coverage-mcp:latest .

# Check dependencies
docker run --rm python:3.13-slim pip install test-coverage-mcp
```

#### Issue: Container won't start

**Error**: `Container exited with code 1`

**Solution**:
```bash
# Check logs
docker logs <container-id>

# Run interactively
docker run -it test-coverage-mcp:latest /bin/bash

# Check environment
docker run -e CODECOV_TOKEN="test" test-coverage-mcp:latest env
```

#### Issue: Can't connect to container

**Error**: `Connection refused`

**Solution**:
```bash
# Check port mapping
docker port <container-id>

# Test from container
docker exec <container-id> curl http://localhost:8000/health

# Check firewall
sudo ufw allow 8000
```

### Configuration Issues

#### Issue: Configuration file not found

**Error**: `FileNotFoundError: config.yaml not found`

**Solution**:
```bash
# Check path
echo $TEST_COVERAGE_MCP_CONFIG

# Create config file
cat > config.yaml << EOF
server:
  transport: sse
  port: 8000
EOF

# Set path
export TEST_COVERAGE_MCP_CONFIG="$(pwd)/config.yaml"
```

#### Issue: Invalid configuration

**Error**: `ConfigurationError: Invalid configuration`

**Solution**:
```bash
# Validate YAML
python -m yaml config.yaml

# Check syntax
cat config.yaml

# Use defaults
rm config.yaml
```

### Integration Issues

#### Issue: Claude Desktop integration not working

**Error**: `MCP server not responding`

**Solution**:
```bash
# Test stdio transport
test-coverage-mcp serve --transport stdio

# Check Claude Desktop config
cat ~/.config/Claude/claude_desktop_config.json

# Verify command
which test-coverage-mcp
```

#### Issue: HTTP client can't connect

**Error**: `Connection refused`

**Solution**:
```bash
# Check server is running
curl http://localhost:8000/health

# Check host/port
test-coverage-mcp serve --host 0.0.0.0 --port 8000

# Check firewall
sudo ufw allow 8000
```

### Performance Issues

#### Issue: Slow response times

**Error**: `Request timeout`

**Solution**:
```bash
# Check provider health
test-coverage-mcp doctor

# Monitor performance
time curl http://localhost:8000/health

# Check resource usage
docker stats <container-id>

# Increase timeout
export PROVIDER_TIMEOUT=60
```

#### Issue: High memory usage

**Error**: `Out of memory`

**Solution**:
```bash
# Check memory usage
docker stats <container-id>

# Increase memory limit
docker run --memory=1g test-coverage-mcp:latest

# Check for memory leaks
docker exec <container-id> ps aux
```

## Debugging

### Enable Debug Logging

```bash
# CLI
test-coverage-mcp serve --log-level debug

# Docker
docker run -e LOG_LEVEL=debug test-coverage-mcp:latest

# Docker Compose
LOG_LEVEL=debug docker-compose up
```

### Collect Diagnostic Information

```bash
# System info
uname -a
python --version
pip list

# Configuration
env | grep -E "CODECOV|COVERALLS|TRANSPORT"

# Provider info
test-coverage-mcp doctor

# Server logs
docker logs <container-id> > /tmp/logs.txt

# Health check
curl -v http://localhost:8000/health
```

### Test Provider Connection

```bash
# Test Codecov
curl -H "Authorization: token $CODECOV_TOKEN" \
  https://codecov.io/api/v2/repos

# Test provider through MCP
test-coverage-mcp providers list
test-coverage-mcp providers describe codecov
```

## Getting Help

### Resources

- **GitHub Issues**: https://github.com/Chisanan232/test-coverage-mcp/issues
- **Discussions**: https://github.com/Chisanan232/test-coverage-mcp/discussions
- **Documentation**: https://test-coverage-mcp.readthedocs.io/

### Reporting Issues

When reporting issues, include:

1. **Environment**:
   ```bash
   python --version
   pip show test-coverage-mcp
   ```

2. **Configuration**:
   ```bash
   env | grep -E "CODECOV|COVERALLS|TRANSPORT"
   ```

3. **Error message**:
   ```bash
   # Full error output
   test-coverage-mcp serve --log-level debug 2>&1
   ```

4. **Steps to reproduce**:
   - Clear, numbered steps
   - Expected vs actual behavior

5. **Logs**:
   ```bash
   # Attach relevant logs
   docker logs <container-id> > logs.txt
   ```

## FAQ

**Q: How do I update the package?**
```bash
pip install --upgrade test-coverage-mcp
```

**Q: How do I uninstall?**
```bash
pip uninstall test-coverage-mcp
```

**Q: Can I use multiple providers?**
Yes, install multiple provider packages and they'll be auto-discovered.

**Q: How do I change the port?**
```bash
test-coverage-mcp serve --port 9000
```

**Q: Can I use environment variables for all settings?**
Yes, see [Environment Variables Reference](./deployment/environment-variables.md)

**Q: How do I run tests?**
```bash
cd test-coverage-mcp
uv run pytest
```

**Q: Where are logs stored?**
Logs are printed to stdout. Use `--log-level` to control verbosity.

## See Also

- [Docker Troubleshooting Guide](./deployment/docker-troubleshooting.md)
- [Environment Variables Reference](./deployment/environment-variables.md)
- [Deployment Overview](./deployment/overview.md)
- [Architecture Overview](./architecture/overview.md)
