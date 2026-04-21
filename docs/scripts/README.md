# Documentation Scripts

This directory contains utility scripts for documentation maintenance and validation.

## verify-links.sh

**Purpose**: Validate internal links in documentation files

**What it does**:
- Checks markdown files for broken internal links (e.g., `[text](./path/to/file.md)`)
- Validates docusaurus configuration paths
- Reports broken links with file locations

**Usage**:
```bash
# Run locally before committing documentation changes
./docs/scripts/verify-links.sh

# Or from project root
bash docs/scripts/verify-links.sh
```

**When to use**:
- ✅ **Local development**: Before committing documentation changes
- ✅ **Pre-commit hook**: Can be added to `.pre-commit-config.yaml` for automatic validation
- ❌ **CI/CD**: Not needed in CI because:
  - The `documentation.yaml` workflow already validates the build succeeds
  - Broken links would cause the Docusaurus build to fail
  - The build artifact upload ensures only valid documentation is deployed

**Integration Options**:

### Option 1: Local Development Only (Current)
- Run manually before committing
- Catch issues early without CI overhead

### Option 2: Pre-Commit Hook
Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: verify-docs-links
      name: Verify documentation links
      entry: bash docs/scripts/verify-links.sh
      language: script
      files: ^docs/contents/.*\.md$
      stages: [commit]
```

### Option 3: CI Workflow
Add to `documentation.yaml` before build step:
```yaml
- name: Verify documentation links
  run: bash docs/scripts/verify-links.sh
```

**Current Recommendation**: Use Option 1 (local development) to keep CI/CD lean and fast.
