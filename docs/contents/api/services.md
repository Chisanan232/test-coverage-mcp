# Service API Reference

## ProviderDiscoveryService

### Class Definition

```python
class ProviderDiscoveryService:
    """Service for discovering and managing coverage providers."""
    
    def __init__(self, registry: Optional[ProviderRegistry] = None) -> None:
        """Initialize the discovery service."""
```

### Methods

#### discover_and_register_providers

```python
def discover_and_register_providers(self) -> Dict[str, ProviderMetadata]:
    """Discover providers via entry points and register them.
    
    Returns:
        Dictionary mapping provider names to their metadata
        
    Raises:
        Exception: If provider discovery or registration fails
    """
```

**Example:**
```python
service = ProviderDiscoveryService()
providers = service.discover_and_register_providers()
```

#### list_providers

```python
def list_providers(self) -> Dict[str, ProviderMetadata]:
    """List all registered providers with their metadata.
    
    Returns:
        Dictionary mapping provider names to their metadata
    """
```

**Example:**
```python
providers = service.list_providers()
for name, metadata in providers.items():
    print(f"{name}: {metadata.version}")
```

#### get_provider

```python
def get_provider(self, name: str) -> Optional[CoverageProvider]:
    """Get a specific provider by name.
    
    Args:
        name: Provider name
        
    Returns:
        Provider instance or None if not found
    """
```

**Example:**
```python
provider = service.get_provider("codecov")
if provider:
    metadata = provider.get_metadata()
```

#### get_default_provider

```python
def get_default_provider(self) -> Optional[CoverageProvider]:
    """Get the default provider.
    
    Returns:
        Default provider instance or None if not set
    """
```

#### set_default_provider

```python
def set_default_provider(self, name: str) -> None:
    """Set the default provider.
    
    Args:
        name: Provider name to set as default
        
    Raises:
        ValueError: If provider is not registered
    """
```

**Example:**
```python
service.set_default_provider("codecov")
```

#### get_capability_matrix

```python
def get_capability_matrix(self) -> Dict[str, Dict[str, str]]:
    """Generate a capability matrix for all providers.
    
    Returns:
        Dictionary mapping provider names to their capability support levels
    """
```

**Example:**
```python
matrix = service.get_capability_matrix()
# Output: {
#     "codecov": {
#         "repository_summary": "advanced",
#         "file_coverage": "advanced"
#     }
# }
```

#### get_providers_for_capability

```python
def get_providers_for_capability(
    self, capability: ProviderCapability
) -> Dict[str, str]:
    """Get all providers that support a specific capability.
    
    Args:
        capability: Capability to search for
        
    Returns:
        Dictionary mapping provider names to their support levels
    """
```

**Example:**
```python
providers = service.get_providers_for_capability(
    ProviderCapability.REPOSITORY_SUMMARY
)
```

#### get_provider_health

```python
def get_provider_health(self, name: str) -> Optional[ProviderHealth]:
    """Get health status of a specific provider.
    
    Args:
        name: Provider name
        
    Returns:
        Health status or None if provider not found
    """
```

#### get_all_health_status

```python
def get_all_health_status(self) -> Dict[str, ProviderHealth]:
    """Get health status of all registered providers.
    
    Returns:
        Dictionary mapping provider names to their health status
    """
```

#### aggregate_health

```python
def aggregate_health(self) -> Dict[str, bool | int | float]:
    """Aggregate health status across all providers.
    
    Returns:
        Dictionary with aggregated health metrics:
        - total_providers: Total number of registered providers
        - healthy_providers: Number of healthy providers
        - health_percentage: Percentage of healthy providers
        - avg_response_time_ms: Average response time
    """
```

**Example:**
```python
health = service.aggregate_health()
print(f"Health: {health['health_percentage']}%")
```

#### get_provider_versions

```python
def get_provider_versions(self) -> Dict[str, str]:
    """Get versions of all registered providers.
    
    Returns:
        Dictionary mapping provider names to their versions
    """
```

#### select_best_provider

```python
def select_best_provider(
    self, required_capabilities: Optional[List[ProviderCapability]] = None
) -> Optional[CoverageProvider]:
    """Select the best provider based on capabilities and health.
    
    Args:
        required_capabilities: List of required capabilities
        
    Returns:
        Best provider instance or None if no suitable provider found
    """
```

**Example:**
```python
provider = service.select_best_provider(
    required_capabilities=[ProviderCapability.REPOSITORY_SUMMARY]
)
```

---

## RepositoryHealthService

### Class Definition

```python
class RepositoryHealthService:
    """Service for analyzing repository health across providers."""
    
    def __init__(
        self, discovery_service: Optional[ProviderDiscoveryService] = None
    ) -> None:
        """Initialize the health service."""
```

### Methods

#### aggregate_coverage_metrics

```python
def aggregate_coverage_metrics(
    self, repo_owner: str, repo_name: str
) -> Dict[str, Any]:
    """Aggregate coverage metrics from all available providers.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        
    Returns:
        Dictionary with aggregated metrics
    """
```

**Example:**
```python
metrics = service.aggregate_coverage_metrics("owner", "repo")
print(f"Average Coverage: {metrics['average_coverage']}%")
```

#### identify_risks

```python
def identify_risks(
    self, repo_owner: str, repo_name: str, threshold: float = 80.0
) -> Dict[str, Any]:
    """Identify coverage risks in the repository.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        threshold: Coverage threshold (default 80%)
        
    Returns:
        Dictionary with risk analysis
    """
```

**Example:**
```python
risk = service.identify_risks("owner", "repo", threshold=85.0)
print(f"Risk Level: {risk['risk_level']}")
```

#### get_next_actions

```python
def get_next_actions(
    self, repo_owner: str, repo_name: str
) -> List[str]:
    """Generate next actions for improving repository health.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        
    Returns:
        List of recommended next actions
    """
```

**Example:**
```python
actions = service.get_next_actions("owner", "repo")
for action in actions:
    print(f"- {action}")
```

#### get_provider_fallback_chain

```python
def get_provider_fallback_chain(
    self, required_capabilities: Optional[List[ProviderCapability]] = None
) -> List[str]:
    """Get a fallback chain of providers for multi-provider support.
    
    Args:
        required_capabilities: List of required capabilities
        
    Returns:
        List of provider names in fallback order
    """
```

**Example:**
```python
chain = service.get_provider_fallback_chain(
    required_capabilities=[ProviderCapability.COVERAGE_DELTA]
)
```

---

## CoverageComparisonService

### Class Definition

```python
class CoverageComparisonService:
    """Service for comparing coverage across references."""
    
    def __init__(
        self, discovery_service: Optional[ProviderDiscoveryService] = None
    ) -> None:
        """Initialize the comparison service."""
```

### Methods

#### compare_refs

```python
def compare_refs(
    self,
    repo_owner: str,
    repo_name: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Compare coverage between two references.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        base_ref: Base reference (branch, tag, or commit)
        head_ref: Head reference to compare against
        
    Returns:
        Dictionary with comparison results
    """
```

**Example:**
```python
result = service.compare_refs("owner", "repo", "main", "feature")
print(f"Delta: {result['delta_percentage']}%")
```

#### detect_regressions

```python
def detect_regressions(
    self,
    repo_owner: str,
    repo_name: str,
    base_ref: str,
    head_ref: str,
    threshold: float = 1.0,
) -> Dict[str, Any]:
    """Detect coverage regressions between references.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        base_ref: Base reference
        head_ref: Head reference
        threshold: Regression threshold percentage (default 1%)
        
    Returns:
        Dictionary with regression analysis
    """
```

**Example:**
```python
regression = service.detect_regressions(
    "owner", "repo", "main", "feature", threshold=1.0
)
if regression['has_regression']:
    print(f"Severity: {regression['severity']}")
```

#### detect_improvements

```python
def detect_improvements(
    self,
    repo_owner: str,
    repo_name: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Detect coverage improvements between references.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        base_ref: Base reference
        head_ref: Head reference
        
    Returns:
        Dictionary with improvement analysis
    """
```

**Example:**
```python
improvement = service.detect_improvements("owner", "repo", "main", "feature")
if improvement['has_improvement']:
    print(f"Improvement: {improvement['improvement_percentage']}%")
```

#### compare_components

```python
def compare_components(
    self,
    repo_owner: str,
    repo_name: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Compare coverage at component level between references.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        base_ref: Base reference
        head_ref: Head reference
        
    Returns:
        Dictionary with component-level comparison
    """
```

#### compare_flags

```python
def compare_flags(
    self,
    repo_owner: str,
    repo_name: str,
    base_ref: str,
    head_ref: str,
) -> Dict[str, Any]:
    """Compare coverage flags between references.
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        base_ref: Base reference
        head_ref: Head reference
        
    Returns:
        Dictionary with flag comparison
    """
```

---

## Data Models

### ProviderHealth

```python
class ProviderHealth(BaseModel):
    is_healthy: bool
    last_check: str  # ISO timestamp
    error_message: Optional[str]
    response_time_ms: float
```

### ProviderMetadata

```python
class ProviderMetadata(BaseModel):
    name: str
    version: str
    description: str
    supported_capabilities: list[ProviderCapability]
    support_levels: dict[ProviderCapability, SupportLevel]
    analysis_depths: list[AnalysisDepth]
```

### Enums

#### ProviderCapability

- `REPOSITORY_SUMMARY`
- `FILE_COVERAGE`
- `COVERAGE_DELTA`
- `UNCOVERED_REGIONS`
- `TEST_RECOMMENDATIONS`
- `COVERAGE_TRENDS`
- `COVERAGE_CONFIG_DIAGNOSIS`
- `COVERAGE_GOALS`
- `CROSS_BRANCH_COMPARISON`
- `PULL_REQUEST_ANALYSIS`
- `COVERAGE_METRICS`
- `RISK_ASSESSMENT`
- `QUALITY_GATES`
- `HISTORICAL_ANALYSIS`

#### SupportLevel

- `BASIC`
- `ENHANCED`
- `ADVANCED`

#### RiskLevel

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`
