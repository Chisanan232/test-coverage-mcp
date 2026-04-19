# get_commit_coverage_summary Tool

## Overview

The `get_commit_coverage_summary` tool retrieves coverage information for a specific commit, including totals, file breakdown, and upload metadata.

## Function Signature

```python
def get_commit_coverage_summary(
    repo_slug: str,
    commit_sha: str,
    provider: Optional[str] = None,
) -> Dict[str, Any]
```

## Parameters

### repo_slug (str, required)

Repository identifier in format `"owner/repo"`.

**Examples**: `"python/cpython"`, `"facebook/react"`, `"torvalds/linux"`

### commit_sha (str, required)

Commit SHA to analyze. Must be at least 7 characters (short SHA format).

**Examples**: `"abc123d"`, `"abc123def456"`, `"abc123def456789..."`

### provider (str, optional)

Specific provider to use for analysis. If not specified, uses all available providers.

**Examples**: `"codecov"`, `"coveralls"`, `"sonarqube"`

## Return Value

Returns a dictionary with the following structure:

```python
{
    "repo_slug": str,                   # Repository identifier
    "commit_sha": str,                  # Commit SHA analyzed
    "coverage_summary": {
        "total_coverage": float,        # Overall coverage percentage
        "covered_lines": int,           # Total covered lines
        "total_lines": int,             # Total lines of code
        "file_count": int,              # Number of files analyzed
        "providers_queried": int,       # Number of providers queried
        "providers_succeeded": int      # Number of successful providers
    },
    "file_breakdown": [                 # Per-file coverage details
        {
            "file_path": str,
            "coverage": float,
            "covered_lines": int,
            "total_lines": int
        }
    ],
    "uploads_metadata": {
        "upload_count": int,            # Number of coverage uploads
        "latest_upload": str | None,    # Timestamp of latest upload
        "upload_sources": [str]         # Sources of uploads (CI, manual, etc.)
    },
    "execution_metadata": {
        "provider_name": str,
        "provider_version": str,
        "support_level": str,
        "used_capabilities": [],
        "analysis_depth": str,
        "execution_time_ms": float
    }
}
```

## Error Responses

### Invalid Repository Slug

If the repository slug format is invalid:

```python
{
    "error": "Invalid repo_slug format. Use 'owner/repo'",
    "error_type": "InvalidRepositorySlugError",
    "execution_metadata": { ... }
}
```

### Invalid Commit SHA

If the commit SHA is invalid or too short:

```python
{
    "error": "Invalid commit SHA. Must be at least 7 characters",
    "error_type": "InvalidCommitShaError",
    "execution_metadata": { ... }
}
```

### Provider Not Found

If the specified provider doesn't exist:

```python
{
    "error": "Provider 'nonexistent' not found",
    "error_type": "ProviderNotFoundError",
    "execution_metadata": { ... }
}
```

### Analysis Error

If an error occurs during analysis:

```python
{
    "error": "Error message describing what went wrong",
    "error_type": "CommitCoverageSummaryError",
    "repo_slug": "owner/repo",
    "commit_sha": "abc123d",
    "execution_metadata": { ... }
}
```

## Examples

### Get Commit Coverage

```python
result = get_commit_coverage_summary("owner/repo", "abc123def456")

print(f"Commit: {result['commit_sha']}")
print(f"Coverage: {result['coverage_summary']['total_coverage']}%")
print(f"Files analyzed: {result['coverage_summary']['file_count']}")
```

### Get Commit Coverage from Specific Provider

```python
result = get_commit_coverage_summary(
    "owner/repo",
    "abc123def456",
    provider="codecov"
)

print(f"Provider: codecov")
print(f"Coverage: {result['coverage_summary']['total_coverage']}%")
```

### Analyze File Breakdown

```python
result = get_commit_coverage_summary("owner/repo", "abc123def456")

print("File Coverage Breakdown:")
for file_info in result['file_breakdown']:
    print(f"  {file_info['file_path']}: {file_info['coverage']}%")
```

### Check Upload Metadata

```python
result = get_commit_coverage_summary("owner/repo", "abc123def456")

metadata = result['uploads_metadata']
print(f"Uploads: {metadata['upload_count']}")
print(f"Latest: {metadata['latest_upload']}")
print(f"Sources: {', '.join(metadata['upload_sources'])}")
```

## Use Cases

### 1. Verify Commit Coverage

```python
# Check coverage for a specific commit
def check_commit_coverage(repo_slug, commit_sha, min_coverage=80.0):
    result = get_commit_coverage_summary(repo_slug, commit_sha)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return False
    
    coverage = result['coverage_summary']['total_coverage']
    if coverage >= min_coverage:
        print(f"✓ Coverage {coverage}% meets minimum {min_coverage}%")
        return True
    else:
        print(f"✗ Coverage {coverage}% below minimum {min_coverage}%")
        return False

check_commit_coverage("owner/repo", "abc123def456", min_coverage=85.0)
```

### 2. Compare Commits

```python
# Compare coverage between commits
def compare_commits(repo_slug, commit1, commit2):
    result1 = get_commit_coverage_summary(repo_slug, commit1)
    result2 = get_commit_coverage_summary(repo_slug, commit2)
    
    cov1 = result1['coverage_summary']['total_coverage']
    cov2 = result2['coverage_summary']['total_coverage']
    delta = cov2 - cov1
    
    print(f"Commit {commit1}: {cov1}%")
    print(f"Commit {commit2}: {cov2}%")
    print(f"Delta: {delta:+.1f}%")

compare_commits("owner/repo", "abc123d", "def456g")
```

### 3. Identify Low Coverage Files

```python
# Find files with low coverage in a commit
def find_low_coverage_files(repo_slug, commit_sha, threshold=50.0):
    result = get_commit_coverage_summary(repo_slug, commit_sha)
    
    low_coverage = [
        f for f in result['file_breakdown']
        if f['coverage'] < threshold
    ]
    
    if low_coverage:
        print(f"Files with coverage < {threshold}%:")
        for file_info in low_coverage:
            print(f"  {file_info['file_path']}: {file_info['coverage']}%")
    else:
        print(f"All files have coverage >= {threshold}%")

find_low_coverage_files("owner/repo", "abc123def456", threshold=70.0)
```

### 4. Track Coverage Trends

```python
# Track coverage across multiple commits
def track_coverage_trend(repo_slug, commits):
    results = {}
    for commit in commits:
        result = get_commit_coverage_summary(repo_slug, commit)
        if 'error' not in result:
            results[commit] = result['coverage_summary']['total_coverage']
    
    for commit, coverage in results.items():
        print(f"{commit}: {coverage}%")
    
    if results:
        trend = "↑" if list(results.values())[-1] > list(results.values())[0] else "↓"
        print(f"Trend: {trend}")

track_coverage_trend("owner/repo", ["abc123d", "def456g", "ghi789h"])
```

### 5. Generate Coverage Report

```python
# Generate a coverage report for a commit
def generate_coverage_report(repo_slug, commit_sha):
    result = get_commit_coverage_summary(repo_slug, commit_sha)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    summary = result['coverage_summary']
    uploads = result['uploads_metadata']
    
    print(f"Coverage Report for {repo_slug}")
    print(f"Commit: {commit_sha}")
    print(f"\nCoverage Metrics:")
    print(f"  Total Coverage: {summary['total_coverage']}%")
    print(f"  Covered Lines: {summary['covered_lines']}")
    print(f"  Total Lines: {summary['total_lines']}")
    print(f"  Files Analyzed: {summary['file_count']}")
    print(f"\nProviders:")
    print(f"  Queried: {summary['providers_queried']}")
    print(f"  Succeeded: {summary['providers_succeeded']}")
    print(f"\nUploads:")
    print(f"  Count: {uploads['upload_count']}")
    print(f"  Latest: {uploads['latest_upload']}")

generate_coverage_report("owner/repo", "abc123def456")
```

## Performance Considerations

- **Caching**: Results can be cached as commit coverage is immutable
- **Provider Queries**: Multiple providers may be queried; consider timeout settings
- **File Breakdown**: Large repositories may have extensive file lists
- **Batch Analysis**: For multiple commits, consider rate limiting

## Interpreting Results

### Coverage Summary

The `coverage_summary` provides aggregated metrics:

```python
summary = result['coverage_summary']
coverage_percentage = summary['total_coverage']
line_coverage = summary['covered_lines'] / summary['total_lines'] * 100
```

### Provider Statistics

Check how many providers succeeded:

```python
success_rate = result['coverage_summary']['providers_succeeded'] / \
               result['coverage_summary']['providers_queried']

if success_rate < 1.0:
    print(f"⚠️ {result['coverage_summary']['providers_queried'] - result['coverage_summary']['providers_succeeded']} provider(s) failed")
```

### Upload Metadata

Understand coverage upload sources:

```python
uploads = result['uploads_metadata']
if uploads['upload_count'] > 0:
    print(f"Coverage uploaded from: {', '.join(uploads['upload_sources'])}")
```

## Related Tools

- `compare_coverage_between_refs` - Compare coverage between references
- `get_repository_test_health` - Analyze repository coverage health
- `list_coverage_providers` - List available providers
