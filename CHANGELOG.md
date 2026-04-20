# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-04-20

### Added

#### Core Features
- **11 MCP Tools** for comprehensive coverage analysis
  - Provider Tools (3): list_coverage_providers, describe_coverage_provider, get_repository_test_health
  - Commit & Comparison Tools (2): get_commit_coverage_summary, compare_coverage_between_refs
  - PR Analysis Tools (2): find_untested_changed_code, analyze_pr_coverage_risk
  - Advanced Analysis Tools (4): find_low_coverage_files, diagnose_coverage_configuration, recommend_test_plan, identify_excludable_code_candidates

#### Service Layer
- **Tier 1 Services**: Discovery, Health Check, Comparison
- **Tier 2 Services**: Risk Analysis, Gap Discovery, Config Diagnosis
- **Tier 3 Services**: Test Recommendation, Excludable Code, Conservative Detection

#### Provider Support
- **Codecov Provider**: Full implementation with API client
- **Plugin System**: Extensible provider architecture with auto-discovery
- **Provider Registry**: Dynamic provider management and capability tracking

#### CLI
- **Serve Command**: Start MCP server with stdio/HTTP transport
- **Providers Command**: List and describe available providers
- **Doctor Command**: Health checks and diagnostics
- **Completion Command**: Shell completion support (bash, zsh, fish)

#### Deployment
- **Docker Support**:
  - Multi-stage Dockerfile with layer caching optimization
  - Development and production Docker Compose configurations
  - GitHub Actions for automated image builds and publishing
  - .dockerignore for build optimization
  
- **CLI Deployment**:
  - Stdio transport for Claude Desktop integration
  - HTTP transport for web clients
  - Configuration via environment variables and config files
  - Health check endpoints

#### Documentation
- **Architecture Overview**: System design and component interactions
- **Provider Plugin Development Guide**: Complete guide for creating custom providers
- **MCP Tools Reference**: Detailed documentation for all 11 tools
- **Deployment Guides**: CLI, Docker, and Kubernetes deployment instructions
- **Environment Variables Reference**: Complete configuration reference
- **Troubleshooting Guide**: Common issues and solutions
- **Example Configurations**: Claude Desktop, config.yaml, .env examples

#### Testing
- **Unit Test Suite**: Comprehensive unit tests with 80%+ coverage target
- **Integration Tests**: Service interaction testing framework
- **E2E Tests**: End-to-end test structure for all 11 MCP tools
- **Contract Tests**: Provider interface compliance testing
- **Mock Provider**: Test implementation for development and testing

#### Development
- **Type Safety**: Full type hints throughout codebase
- **Pydantic Models**: Input/output validation for all tools
- **Error Handling**: Comprehensive error messages and specific exception types
- **Logging**: Structured logging with configurable levels
- **Configuration**: Environment variables and config file support

### Infrastructure
- **CI/CD**: GitHub Actions workflows for testing and deployment
- **Pre-commit Hooks**: Code quality checks (MyPy, Ruff, formatting)
- **Workspace Configuration**: Monorepo support with shared tooling
- **Package Management**: uv-based dependency management

### Documentation
- Complete API reference for all 11 tools
- Architecture and design documentation
- Deployment guides for multiple platforms
- Troubleshooting and FAQ sections
- Example configurations and use cases

## [0.1.0] - 2024-04-01

### Added
- Initial project structure
- Domain models and contracts
- Provider registry system
- Codecov provider implementation
- Basic MCP server setup
- CLI framework

## Unreleased

### Planned
- Additional providers (Coveralls, etc.)
- Caching layer for performance
- Webhook support for real-time updates
- Advanced analytics dashboard
- Custom rule engine
- API documentation (OpenAPI/Swagger)
- Performance optimizations
- Additional language support

---

## Migration Guide

### From 0.1.0 to 1.0.0

#### Breaking Changes
None - this is the first stable release.

#### New Features
- 11 MCP tools (previously 7)
- Docker deployment support
- CLI with multiple commands
- Extended documentation

#### Configuration Changes
- New environment variables for CLI options
- New config file format support
- New deployment options

#### Installation
```bash
# Update to 1.0.0
pip install --upgrade test-coverage-mcp==1.0.0

# Or with uv
uv pip install test-coverage-mcp==1.0.0
```

#### Migration Steps
1. Update environment variables (see Environment Variables Reference)
2. Update configuration files (see example configs)
3. Test with `test-coverage-mcp doctor`
4. Update deployment scripts
5. Redeploy application

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Support

- **Issues**: https://github.com/Chisanan232/test-coverage-mcp/issues
- **Discussions**: https://github.com/Chisanan232/test-coverage-mcp/discussions
- **Documentation**: https://test-coverage-mcp.readthedocs.io/

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
