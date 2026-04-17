# Project Infrastructure and MCP Tool Design

## 1. Project Positioning

**Suggested project name**
`test-coverage-mcp`

**One-line positioning**
A Python-first, provider-extensible MCP server that exposes a **stable, provider-neutral MCP tool surface** while using provider adapters underneath to connect to Codecov, Coveralls, or other coverage data sources, and elevates raw coverage data into **coverage intelligence**. This aligns with MCP’s stable tool contract model, FastMCP’s tool generation approach, Python’s plugin discovery via entry points, and uv’s workspace-oriented packaging workflow. ([Model Context Protocol][1])

**Core design principles**

1. MCP tool names and primary semantics must remain stable across providers.
2. Provider differences must show up through `support_level`, `analysis_depth`, `used_capabilities`, `missing_capabilities`, `degraded`, and richer response payloads, not through fragmented tool names.
3. The abstraction should be capability-driven, not endpoint-driven.
4. The project should support both CLI startup and Docker startup, and be distributed as Python packages with provider plugin packages.
5. The repository should use a monorepo / uv workspace layout, while each package remains independently releasable. uv officially supports workspaces and package-scoped build/run workflows. ([Astral Docs][2])

---

## 2. The three-layer architecture

## 2.1 Provider Interface Layer

This layer defines provider contracts.

It is not exposed directly to MCP clients.
Its job is to answer: what capabilities does a provider support, and how are provider-specific DTOs mapped into core domain models?

**Core concepts**

* `CoverageProvider`
* `ProviderCapability`
* `ProviderHealth`
* provider-specific adapter
* provider-specific DTO mapper

**Capabilities should represent domain meaning, not SaaS endpoints**

* repository health
* commit totals
* file coverage
* coverage tree
* comparison
* impacted files
* segment comparison
* flags
* components
* test results
* test analytics
* config read
* coverage trend

Codecov’s public API clearly exposes compare, file comparison, impacted files, segmented comparison, components, flags, repo config, coverage trend, file report, report/tree, test-results, test-analytics, and totals, which makes it a strong advanced provider.   

---

## 2.2 Coverage Intelligence Service Layer

This layer converts provider data into engineering intelligence.

This is the true product core.
It should centralize heuristics, aggregation, degradation paths, recommendation logic, and normalized outputs.

**Main services**

* `ProviderDiscoveryService`
* `RepositoryHealthService`
* `CoverageComparisonService`
* `CoverageRiskAnalysisService`
* `CoverageGapDiscoveryService`
* `CoverageConfigDiagnosisService`
* `TestRecommendationService`
* `ExcludableCodeCandidateService`

**Responsibilities**

* choose the best basic / enhanced / advanced path
* aggregate multiple provider methods
* apply heuristics
* produce unified response models
* attach execution metadata

---

## 2.3 MCP Facade Layer

This layer exposes intelligence services as stable MCP tools.

Its responsibilities are limited to:

* request/response validation with Pydantic
* provider resolution
* orchestration
* FastMCP tool exposure

FastMCP uses Python type hints and docstrings to generate tool definitions, so this layer should remain thin and stable. ([Model Context Protocol][3])

---

## 3. Package / plugin architecture

## 3.1 Monorepo / uv workspace

Suggested layout:

```text
repo/
  pyproject.toml
  uv.lock
  packages/
    test-coverage-mcp/
    test-coverage-mcp-codecov/
    test-coverage-mcp-coveralls/
  tests/
    contract/
    integration/
    e2e/
```

uv officially describes workspaces as a way to manage multiple packages in one repository, which fits this core-plus-plugins architecture well. ([Astral Docs][2])

## 3.2 Core package

`test-coverage-mcp`

Contains:

* domain models
* provider contracts
* capability models
* registry
* services
* MCP tools
* CLI
* server bootstrap
* shared infrastructure

## 3.3 Plugin packages

`test-coverage-mcp-codecov`
`test-coverage-mcp-coveralls`

Each plugin contains:

* provider API client
* DTOs
* DTO-to-domain mapping
* provider adapter
* plugin registration entry point

## 3.4 Plugin discovery

Use Python packaging entry points. The official packaging guide and entry points specification explicitly support this pattern for plugin discovery. ([Python Packaging][4])

Example concept:

```toml
[project.entry-points."test_coverage_mcp.providers"]
codecov = "test_coverage_mcp_codecov.plugin:register"
coveralls = "test_coverage_mcp_coveralls.plugin:register"
```

---

## 4. CLI / Docker design

## 4.1 CLI

Suggested console entry point:

```bash
test-coverage-mcp serve
test-coverage-mcp providers list
test-coverage-mcp providers describe codecov
test-coverage-mcp doctor
```

**Subcommands**

* `serve`

  * starts the MCP server
  * supports `--transport stdio|http`
  * supports `--provider auto|codecov|coveralls`
* `providers list`

  * lists installed providers
* `providers describe <name>`

  * shows capability matrix
* `doctor`

  * checks env vars, tokens, plugin loading, provider health, and connectivity

Console scripts are a standard entry-point use case in Python packaging. ([Python Packaging][5])

## 4.2 Docker

Recommended options:

* `ghcr.io/<org>/test-coverage-mcp:core`
* `ghcr.io/<org>/test-coverage-mcp:full`

You may also start with a single image and toggle providers through environment variables.
uv’s Docker guide covers multi-stage builds, caching strategies, and project/dependency installation optimization. ([Astral Docs][6])

---

## 5. Provider capability model

Suggested enum:

```python
class ProviderCapability(str, Enum):
    REPOSITORY_HEALTH = "repository_health"
    COMMIT_TOTALS = "commit_totals"
    FILE_COVERAGE = "file_coverage"
    TREE_COVERAGE = "tree_coverage"
    COVERAGE_TREND = "coverage_trend"
    REF_COMPARISON = "ref_comparison"
    FILE_COMPARISON = "file_comparison"
    SEGMENT_COMPARISON = "segment_comparison"
    IMPACTED_FILES = "impacted_files"
    COMPONENTS = "components"
    FLAGS = "flags"
    TEST_RESULTS = "test_results"
    TEST_ANALYTICS = "test_analytics"
    CONFIG_READ = "config_read"
```

---

## 6. Shared execution metadata

Every high-level tool response should include:

```python
class ExecutionMetadata(BaseModel):
    provider: str
    provider_version: str | None = None
    support_level: Literal["basic", "enhanced", "advanced"]
    analysis_depth: Literal["repo", "file", "segment", "test-run", "config-aware"]
    used_capabilities: list[str]
    missing_capabilities: list[str]
    degraded: bool = False
    degradation_reason: str | None = None
```

This keeps the tool surface stable while making provider differences explicit and useful to LLMs.

---

## 7. MCP Tool Spec

Below are the 11 tools I recommend for v1.

### 7.1 `list_coverage_providers`

**Purpose**
List installed, enabled, and available providers.

**When to use**

* client bootstrap
* multi-provider selection
* provider installation/auth debugging

**Problem solved**
Prevents the LLM from blindly calling unsupported or unavailable providers.

**Suggested input**

```json
{
  "include_capabilities": true,
  "include_health": true
}
```

**Suggested output**

* providers
* installed / enabled / healthy flags
* default provider
* capability summary

---

### 7.2 `describe_coverage_provider`

**Purpose**
Describe a provider’s capability matrix and limitations.

**When to use**

* understand weaker analysis results
* debug degraded responses
* plan orchestration paths

**Problem solved**
Makes provider differences visible without splitting the tool surface.

---

### 7.3 `get_repository_test_health`

**Purpose**
Return a high-level repository coverage and test health summary.

**When to use**

* repo onboarding
* weekly audits
* release readiness checks
* test debt reviews

**Problem solved**
Answers: “How healthy is this repository from a test protection standpoint?”

**Output highlights**

* overall coverage
* trend summary
* lowest coverage areas
* test signal summary
* config posture summary
* top risks
* next actions

---

### 7.4 `get_commit_coverage_summary`

**Purpose**
Summarize coverage for a specific commit / branch / ref.

**When to use**

* CI inspection
* anomalous commit investigation
* baseline inspection before comparisons

**Problem solved**
Answers: “What does coverage look like for this version?”

**Output highlights**

* totals
* file breakdown summary
* suspicious low-confidence files
* optional components / flags / uploads metadata

Codecov’s totals, report, file report, and commit upload endpoints support this well.  

---

### 7.5 `find_low_coverage_files`

**Purpose**
Find the files most worth prioritizing for test investment.

**When to use**

* test debt triage
* coverage improvement planning
* critical-path hardening

**Problem solved**
Answers: “Which files are the best next targets for adding tests?”

**Output highlights**

* ranked files
* coverage percentage
* why it matters
* risk
* suggested test types

---

### 7.6 `compare_coverage_between_refs`

**Purpose**
Compare coverage across two refs or a pull request.

**When to use**

* PR review
* merge gating
* regression checks

**Problem solved**
Answers: “Did this change improve or degrade coverage, and where?”

**Output highlights**

* overall delta
* patch delta
* changed file summary
* component/flag delta if available
* regressions / improvements

Codecov’s compare, compare/components, and compare/flags endpoints directly support this use case.  

---

### 7.7 `find_untested_changed_code`

**Purpose**
Identify changed regions that are not adequately protected by tests.

**When to use**

* before AI test generation
* PR review comments
* regression prevention

**Problem solved**
Answers: “What changed, but is still not covered by tests?”

**Output highlights**

* uncovered changed regions
* partially covered changed regions
* grouped by file
* risk level
* suggested scenario labels

**Advanced provider advantage**
Codecov can leverage impacted files and segment comparison for segment-level / line-range analysis. Its impacted-files endpoint explicitly returns `pending` and `processed` states, so this tool must model pending analysis rather than treating it as an error.  

---

### 7.8 `analyze_pr_coverage_risk`

**Purpose**
Produce a coverage-oriented risk assessment for a pull request.

**When to use**

* PR bot comments
* automated review
* release risk checks
* Slack/JIRA summaries

**Problem solved**
Not just “coverage dropped by X%,” but:

* which files are risky
* what changed and remains unprotected
* whether core components/flags are affected
* whether the issue looks like config rather than missing tests

**Output highlights**

* overall_risk
* highest_risk_files
* key_findings
* coverage_gaps
* config_suspicions
* recommended_test_targets
* limitations

---

### 7.9 `diagnose_coverage_configuration`

**Purpose**
Diagnose whether the coverage configuration itself is unhealthy.

**When to use**

* initial coverage SaaS adoption
* suspicious coverage reports
* generated/migrations/vendor code dragging metrics down
* threshold / target / flag / component tuning

**Problem solved**
Answers:

* are irrelevant files included?
* are exclusions missing?
* are flags/components poorly scoped?
* is the policy too strict or too loose?

**Output highlights**

* config summary
* suspected over-included paths
* likely missing exclusions
* threshold review
* component/flag review
* suggested actions

Codecov’s repo config endpoint plus filterable totals/report structures make this especially useful.  

---

### 7.10 `recommend_test_plan`

**Purpose**
Generate an actionable testing plan for a repo / PR / file.

**When to use**

* before AI writes tests
* when developers need next-step guidance
* in PR review follow-up

**Problem solved**
Answers: “What tests should be added?” instead of merely reporting low coverage.

**Output highlights**

* unit test candidates
* unhappy path cases
* boundary cases
* integration candidates
* regression priorities
* rationale

**Important note**
This tool should generate a **test design brief**, not raw test code.

---

### 7.11 `identify_excludable_code_candidates`

**Purpose**
Identify code regions or files that may be reasonable candidates for exclusion from coverage policy.

**When to use**

* too much generated code
* migration / tooling / vendor / bootstrap code distorting coverage
* coverage policy refinement

**Problem solved**
Answers: “What code may be better excluded or at least reviewed for exclusion?”

**Critical boundary**
This tool must **not** claim unreachable code or dead code as fact.
It should only emit:

* candidate
* suspected_reason
* evidence
* confidence
* requires_human_validation

**Output highlights**

* candidate files / paths / regions
* suspected reasons
* zero-hit style signals if available
* suggested config action
* caution notes

This tool is valuable, but must remain conservative because coverage providers are not static analyzers.

---

## 8. Error and state model

All tools should clearly distinguish:

* `error`
* `unsupported`
* `degraded`
* `pending`

This is especially important for `find_untested_changed_code` and `analyze_pr_coverage_risk` when using impacted-files style analysis. Codecov explicitly documents `pending` vs `processed` states. 

---

## 9. Recommended base response model

```python
class ToolResponseBase(BaseModel):
    summary: str
    key_findings: list[str]
    recommended_next_actions: list[str]
    execution_metadata: ExecutionMetadata
    limitations: list[str] = Field(default_factory=list)
    confidence: float | None = None
```

This makes the tools much easier for LLMs to consume:

* understand the conclusion
* know the next step
* judge confidence
* decide whether to call another tool

---

## 10. Suggested implementation phases

**MVP Phase 1**

* provider registry
* Codecov plugin
* CLI `serve/providers/doctor`
* tools:

  * `list_coverage_providers`
  * `describe_coverage_provider`
  * `get_repository_test_health`
  * `get_commit_coverage_summary`
  * `compare_coverage_between_refs`
  * `find_untested_changed_code`
  * `analyze_pr_coverage_risk`

**Phase 2**

* `find_low_coverage_files`
* `diagnose_coverage_configuration`
* `recommend_test_plan`
* `identify_excludable_code_candidates`

**Phase 3**

* Coveralls plugin
* local/artifact provider
* richer policy configuration
* optional resources/prompts side channel
