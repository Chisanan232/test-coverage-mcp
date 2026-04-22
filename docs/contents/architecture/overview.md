# Architecture Overview

## System Architecture

test-coverage-mcp is a provider-extensible MCP server for test coverage intelligence. It provides a stable capability-driven tool contract with provider-specific enrichments.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Clients                              │
│              (Claude, Other AI Tools, etc.)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    MCP Protocol (SSE/HTTP)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    MCP Server                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              11 MCP Tools                              │ │
│  │  ┌─────────────┬─────────────┬──────────────────────┐ │ │
│  │  │  Provider   │  Commit &   │  PR Analysis Tools   │ │ │
│  │  │  Tools      │  Comparison │  (6-7)               │ │ │
│  │  │  (1-3)      │  (4-5)      │                      │ │ │
│  │  └─────────────┴─────────────┴──────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Advanced Analysis Tools (8-11)                  │ │ │
│  │  │  - find_low_coverage_files                       │ │ │
│  │  │  - diagnose_coverage_configuration               │ │ │
│  │  │  - recommend_test_plan                           │ │ │
│  │  │  - identify_excludable_code_candidates           │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐   │
│  │           Service Layer (Tier 1-3)                  │   │
│  │  ┌──────────────┬──────────────┬──────────────────┐ │   │
│  │  │ Discovery    │ Health Check │ Comparison       │ │   │
│  │  │ Service      │ Service      │ Service          │ │   │
│  │  └──────────────┴──────────────┴──────────────────┘ │   │
│  │  ┌──────────────┬──────────────┬──────────────────┐ │   │
│  │  │ Risk         │ Gap          │ Config           │ │   │
│  │  │ Analysis     │ Discovery    │ Diagnosis        │ │   │
│  │  └──────────────┴──────────────┴──────────────────┘ │   │
│  │  ┌──────────────┬──────────────┬──────────────────┐ │   │
│  │  │ Test         │ Excludable   │ Conservative     │ │   │
│  │  │ Recommendation│ Code         │ Detection        │ │   │
│  │  └──────────────┴──────────────┴──────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐   │
│  │        Provider Registry & Discovery                │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Plugin Discovery Service                    │   │   │
│  │  │  - Detect installed providers                │   │   │
│  │  │  - Load provider plugins                     │   │   │
│  │  │  - Manage provider lifecycle                 │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼────┐         ┌───▼────┐        ┌───▼────┐
    │ Codecov │         │Provider│        │Provider│
    │Provider │         │ 2      │        │ N      │
    └────────┘         └────────┘        └────────┘
        │                  │                  │
    ┌───▼──────────────────▼──────────────────▼───┐
    │     External Coverage Providers              │
    │  (Codecov, Coveralls, etc.)                  │
    └────────────────────────────────────────────┘
```

## Core Components

### 1. MCP Tools (11 Total)

**Provider Tools (1-3)**:
- `list_coverage_providers` - Discover available providers
- `describe_coverage_provider` - Get provider details
- `get_repository_test_health` - Analyze repository health

**Commit & Comparison Tools (4-5)**:
- `get_commit_coverage_summary` - Coverage at specific commit
- `compare_coverage_between_refs` - Compare coverage changes

**PR Analysis Tools (6-7)**:
- `find_untested_changed_code` - Identify coverage gaps in changes
- `analyze_pr_coverage_risk` - Assess PR risk

**Advanced Analysis Tools (8-11)**:
- `find_low_coverage_files` - Identify low-coverage files
- `diagnose_coverage_configuration` - Analyze configuration
- `recommend_test_plan` - Get test recommendations
- `identify_excludable_code_candidates` - Find code to exclude

### 2. Service Layer

**Tier 1 Services**:
- **Discovery Service**: Provider detection and management
- **Health Check Service**: System health monitoring
- **Comparison Service**: Coverage comparison logic

**Tier 2 Services**:
- **Risk Analysis Service**: PR risk assessment
- **Gap Discovery Service**: Uncovered code identification
- **Config Diagnosis Service**: Configuration validation

**Tier 3 Services**:
- **Test Recommendation Service**: Test suggestions
- **Excludable Code Service**: Code exclusion detection
- **Conservative Detection Service**: Pattern-based detection

### 3. Provider Registry

- **Plugin Discovery**: Automatic provider detection
- **Provider Management**: Lifecycle management
- **Capability Matrix**: Feature support tracking

### 4. External Providers

- **Codecov**: Primary provider implementation
- **Extensible**: Support for additional providers

## Data Flow

### Tool Execution Flow

```
1. Client sends MCP request
   ↓
2. MCP Server receives request
   ↓
3. Tool handler parses input
   ↓
4. Service layer processes request
   ↓
5. Provider interface called
   ↓
6. External provider API called
   ↓
7. Results aggregated
   ↓
8. Response sent to client
```

### Provider Integration

```
1. Provider Registry discovers providers
   ↓
2. Provider capabilities loaded
   ↓
3. Health checks performed
   ↓
4. Requests routed to appropriate provider
   ↓
5. Results cached/aggregated
   ↓
6. Enrichments applied
```

## Design Principles

### 1. Multi-Provider Support
- Aggregate data from multiple providers
- Graceful degradation if providers fail
- Consistent interface across providers

### 2. Capability-Driven Contract
- Stable tool interface
- Provider-specific enrichments
- Version compatibility

### 3. Type Safety
- Full type hints throughout
- Pydantic models for validation
- Runtime type checking

### 4. Error Handling
- Comprehensive error messages
- Specific exception types
- Graceful degradation

### 5. Extensibility
- Plugin-based provider system
- Service-oriented architecture
- Clear separation of concerns

## Technology Stack

- **Language**: Python 3.12+
- **MCP Framework**: mcp[cli]
- **Web Framework**: FastAPI
- **Data Validation**: Pydantic
- **HTTP Client**: httpx
- **Package Manager**: uv

## Deployment Options

- **Stdio Transport**: For Claude Desktop integration
- **HTTP Transport**: For web-based clients
- **Docker**: Containerized deployment
- **Kubernetes**: Orchestrated deployment

## Security Considerations

- Non-root user execution
- Read-only filesystem (production)
- Token masking in logs
- Input validation
- Error message sanitization

## Performance Characteristics

- **Startup Time**: < 2 seconds
- **Tool Execution**: 100-500ms (depending on provider)
- **Memory Usage**: ~100-200MB base
- **Concurrent Requests**: Configurable

## Monitoring & Observability

- Health check endpoints
- Structured logging
- Error tracking
- Performance metrics
- Provider health status

## Future Enhancements

- Additional providers (Coveralls, etc.)
- Caching layer for performance
- Webhook support for real-time updates
- Advanced analytics
- Custom rule engine
