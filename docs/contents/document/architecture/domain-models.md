---
sidebar_position: 1
---

# Domain Models & Provider Contracts

## Overview

The domain models define the core abstractions and type system for the test-coverage-mcp server. They establish a stable contract between the MCP server and coverage providers, enabling provider-specific implementations while maintaining consistent tool interfaces.

## Architecture

### Three-Layer Model

```
┌─────────────────────────────────────────┐
│  Tool Responses (ToolResponseBase)      │
│  - RepositoryCoverageSummary            │
│  - FileCoverage                         │
│  - CoverageDelta                        │
│  - ConfigDiagnosis                      │
└─────────────────────────────────────────┘
                    ▲
                    │
┌─────────────────────────────────────────┐
│  Execution Metadata                     │
│  - Provider info                        │
│  - Capabilities used                    │
│  - Degradation tracking                 │
└─────────────────────────────────────────┘
                    ▲
                    │
┌─────────────────────────────────────────┐
│  Provider Contracts                     │
│  - CoverageProvider (ABC)               │
│  - ProviderMetadata                     │
│  - ProviderHealth                       │
└─────────────────────────────────────────┘
```

## Enums

### ProviderCapability

Defines the 14 capabilities that coverage providers can support:

**Basic Analysis**
- `REPOSITORY_SUMMARY` - Overall repository coverage
- `FILE_COVERAGE` - Per-file coverage details
- `COVERAGE_DELTA` - Coverage changes between versions

**Advanced Analysis**
- `UNCOVERED_REGIONS` - Identify uncovered code regions
- `TEST_RECOMMENDATIONS` - Suggest tests for gaps
- `COVERAGE_TRENDS` - Historical coverage trends

**Configuration**
- `COVERAGE_CONFIG_DIAGNOSIS` - Analyze coverage configuration
- `COVERAGE_GOALS` - Define and track coverage goals

**Comparison & Metrics**
- `CROSS_BRANCH_COMPARISON` - Compare coverage across branches
- `PULL_REQUEST_ANALYSIS` - PR-specific coverage analysis
- `COVERAGE_METRICS` - Detailed coverage metrics

**Advanced Features**
- `RISK_ASSESSMENT` - Risk level assessment
- `QUALITY_GATES` - Quality gate enforcement
- `HISTORICAL_ANALYSIS` - Long-term trend analysis

### SupportLevel

Indicates the depth of support for a capability:
- `BASIC` - Minimal implementation
- `ENHANCED` - Extended functionality
- `ADVANCED` - Full feature support

### AnalysisDepth

Specifies the granularity of analysis:
- `REPOSITORY` - Repository-level analysis
- `FILE` - File-level analysis
- `SEGMENT` - Code segment analysis
- `TEST_RUN` - Test run-specific analysis
- `CONFIG_AWARE` - Configuration-aware analysis

### RiskLevel

Categorizes the risk of uncovered code:
- `LOW` - Minor functionality
- `MEDIUM` - Important functionality
- `HIGH` - Critical functionality
- `CRITICAL` - System-critical functionality

## Provider Contracts

### CoverageProvider (ABC)

Abstract base class that all providers must implement:

```python
class CoverageProvider(ABC):
    @abstractmethod
    def get_metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        pass

    @abstractmethod
    def health_check(self) -> ProviderHealth:
        """Check provider health."""
        pass

    @abstractmethod
    def supports_capability(self, capability: ProviderCapability) -> bool:
        """Check if provider supports a capability."""
        pass

    @abstractmethod
    def get_support_level(
        self, capability: ProviderCapability
    ) -> Optional[SupportLevel]:
        """Get support level for a capability."""
        pass
```

### ProviderMetadata

Contains provider information:
- `name` - Provider name (e.g., "codecov")
- `version` - Provider version
- `description` - Provider description
- `supported_capabilities` - List of supported capabilities
- `support_levels` - Support level for each capability
- `analysis_depths` - Supported analysis depths

### ProviderHealth

Tracks provider health status:
- `is_healthy` - Whether provider is operational
- `last_check` - Timestamp of last health check
- `error_message` - Error message if unhealthy
- `response_time_ms` - Health check response time

## Tool Response Models

### ToolResponseBase

Base class for all tool responses with consistent structure:

```python
class ToolResponseBase(BaseModel):
    summary: str                           # Brief summary
    key_findings: list[str]               # Key findings
    recommended_next_actions: list[str]   # Recommended actions
    confidence_score: float               # 0.0-1.0 confidence
    execution_metadata: ExecutionMetadata # Execution details
    additional_context: dict[str, Any]    # Raw data
```

### ExecutionMetadata

Tracks execution details for transparency:
- `provider_name` - Provider used
- `provider_version` - Provider version
- `support_level` - Support level achieved
- `used_capabilities` - Capabilities used
- `analysis_depth` - Analysis granularity
- `execution_time_ms` - Execution time
- `timestamp` - Execution timestamp
- `degradation_reason` - Why capabilities were limited
- `limitations` - Known limitations

## Domain Models

### RepositoryCoverageSummary

Overall repository coverage information:
- `total_coverage_percentage` - Overall coverage %
- `covered_lines` - Number of covered lines
- `total_lines` - Total lines of code
- `file_count` - Number of files
- `covered_file_count` - Files with coverage

### FileCoverage

Per-file coverage details:
- `file_path` - Path to file
- `coverage_percentage` - File coverage %
- `covered_lines` - Covered lines count
- `total_lines` - Total lines in file
- `uncovered_lines` - List of uncovered line numbers

### CoverageDelta

Coverage change tracking:
- `base_coverage` - Base coverage %
- `current_coverage` - Current coverage %
- `delta_percentage` - Change in %
- `delta_lines` - Change in line count
- `improved` - Whether coverage improved

### UncoveredRegion

Represents an uncovered code region:
- `file_path` - File containing region
- `start_line` - Start line number
- `end_line` - End line number
- `region_type` - Type (function, class, block, etc.)
- `risk_level` - Risk level of gap

### TestRecommendation

Suggests tests for coverage improvement:
- `file_path` - File to test
- `uncovered_region` - Region to test
- `recommendation` - Specific suggestion
- `estimated_impact` - Expected coverage improvement %
- `priority` - Priority level (1-5)

### ConfigDiagnosis

Analyzes coverage configuration:
- `config_file` - Configuration file path
- `issues` - Identified issues
- `suggestions` - Improvement suggestions
- `is_valid` - Whether configuration is valid

## Design Principles

### 1. Provider Agnostic

Models are provider-agnostic, allowing different providers (Codecov, Cobertura, etc.) to implement the same contract.

### 2. Transparency

ExecutionMetadata provides full transparency about what was executed, how, and any limitations encountered.

### 3. Extensibility

Additional context can be stored in `additional_context` dict without modifying the base model.

### 4. Type Safety

Pydantic models ensure runtime validation and type safety across the system.

### 5. Confidence Tracking

All responses include confidence scores, allowing consumers to assess result reliability.

## Usage Example

```python
from test_coverage_mcp.domain import (
    RepositoryCoverageSummary,
    ExecutionMetadata,
    SupportLevel,
    AnalysisDepth,
    ProviderCapability,
)

# Create execution metadata
metadata = ExecutionMetadata(
    provider_name="codecov",
    provider_version="1.0.0",
    support_level=SupportLevel.ADVANCED,
    used_capabilities=[ProviderCapability.REPOSITORY_SUMMARY],
    analysis_depth=AnalysisDepth.REPOSITORY,
    execution_time_ms=150.0,
)

# Create response
summary = RepositoryCoverageSummary(
    summary="Repository has good coverage",
    key_findings=["85% overall coverage"],
    recommended_next_actions=["Focus on low coverage files"],
    confidence_score=0.95,
    execution_metadata=metadata,
    total_coverage_percentage=85.0,
    covered_lines=8500,
    total_lines=10000,
    file_count=150,
    covered_file_count=145,
)
```

## Next Steps

- **Phase 3**: Implement ProviderRegistry for plugin discovery
- **Phase 4**: Create Codecov provider implementation
- **Phase 5**: Implement service layer for analysis
