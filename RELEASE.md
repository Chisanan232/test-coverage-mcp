# Release Preparation Guide

## Version 1.0.0 Release Checklist

### Pre-Release

- [x] All features implemented
- [x] All tests passing
- [x] Documentation complete
- [x] CHANGELOG updated
- [x] Examples provided
- [x] Docker images built
- [x] CI/CD workflows configured

### Release Steps

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   # test-coverage-mcp: 0.1.0 -> 1.0.0
   # test-coverage-mcp-codecov: 0.1.0 -> 1.0.0
   ```

2. **Create Release Tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Build and Publish**
   ```bash
   # Python packages to PyPI
   uv build
   uv publish

   # Docker images to ghcr.io
   docker build -t ghcr.io/Chisanan232/test-coverage-mcp:v1.0.0 .
   docker push ghcr.io/Chisanan232/test-coverage-mcp:v1.0.0
   ```

4. **Create GitHub Release**
   - Use CHANGELOG.md content
   - Attach release artifacts
   - Mark as latest release

5. **Announce Release**
   - GitHub Discussions
   - Documentation site
   - Social media

### Post-Release

- [ ] Monitor for issues
- [ ] Update documentation site
- [ ] Update package registries
- [ ] Announce in community channels
- [ ] Plan next release

## Release Notes Template

```markdown
# Version 1.0.0 Release

## Overview
First stable release of test-coverage-mcp with complete feature set.

## What's New
- 11 MCP tools for comprehensive coverage analysis
- Docker deployment support
- Full CLI implementation
- Complete documentation

## Installation
```bash
pip install test-coverage-mcp==1.0.0
```

## Documentation
- [Getting Started](https://test-coverage-mcp.readthedocs.io/)
- [Architecture Overview](https://test-coverage-mcp.readthedocs.io/architecture/)
- [Deployment Guide](https://test-coverage-mcp.readthedocs.io/deployment/)

## Breaking Changes
None - this is the first stable release.

## Contributors
Thanks to all contributors who made this release possible!

## Support
- Issues: https://github.com/Chisanan232/test-coverage-mcp/issues
- Discussions: https://github.com/Chisanan232/test-coverage-mcp/discussions
```

## Versioning Strategy

### Version Format
`MAJOR.MINOR.PATCH`

### Release Schedule
- Major: Significant features or breaking changes
- Minor: New features, backward compatible
- Patch: Bug fixes, security updates

### Maintenance
- Support current and previous major versions
- Security updates for 1 year
- Bug fixes for 6 months

## Future Releases

### v1.1.0 (Planned)
- Additional providers (Coveralls, etc.)
- Caching layer
- Performance optimizations

### v1.2.0 (Planned)
- Webhook support
- Advanced analytics
- Custom rule engine

### v2.0.0 (Future)
- Major architectural improvements
- Breaking changes allowed
- New capabilities

## See Also
- [CHANGELOG.md](./CHANGELOG.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [License](./LICENSE)
