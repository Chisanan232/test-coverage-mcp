# Documentation Deployment

## Overview

The documentation site is built with **Docusaurus** and deployed to **GitHub Pages** using automated CI/CD workflows.

## Deployment Architecture

### Build & Deployment Flow

```
Push to master
    ↓
documentation.yaml workflow triggered
    ↓
Check if docs changed
    ↓
Build Docusaurus site
    ↓
Upload to GitHub Pages
    ↓
Live at: https://chisanan232.github.io/test-coverage-mcp/
```

## CI/CD Workflows

### 1. Documentation Build Check (Pull Requests)

**File**: `.github/workflows/docs-build-check.yaml`

**Trigger**: Pull requests with documentation changes

**What it does**:
- Builds documentation to verify no errors
- Validates build quality
- Checks for critical files (index.html, 404.html)
- Provides build summary in PR

**Node Version**: Node 24

### 2. Documentation Deployment (Master Branch)

**File**: `.github/workflows/documentation.yaml`

**Trigger**:
- Push to master with documentation changes
- Release workflow completion

**What it does**:
- Checks if documentation files changed
- Builds Docusaurus site
- Deploys to GitHub Pages
- Updates live documentation

**Node Version**: Node 24

**Deployment Target**: GitHub Pages at custom domain `test-coverage-mcp.chisanan232.dev`

## Documentation Structure

### Content Organization

```
docs/
├── contents/
│   ├── document/          # Main documentation
│   │   ├── deployment/    # Deployment guides
│   │   ├── architecture/  # Architecture docs
│   │   └── sidebars.ts    # Navigation structure
│   ├── development/       # Development guides
│   ├── blog/             # Blog posts
│   └── ...
├── docusaurus.config.ts   # Docusaurus configuration
├── package.json           # Dependencies
└── pnpm-lock.yaml        # Lock file
```

### Key Configuration

**Docusaurus Config** (`docusaurus.config.ts`):
- Project branding: test-coverage-mcp
- Search: Full-text search with docusaurus-search-local
- Versioning: Current version only (no versioned docs yet)
- Social Media: Open Graph and Twitter Card metadata
- Custom Domain: test-coverage-mcp.chisanan232.dev

## Automatic Deployment

### When Documentation Deploys

Documentation automatically deploys when:

1. **Changes pushed to master** in these paths:
   - `.github/workflows/documentation.yaml`
   - `docs/**/*.md`, `docs/**/*.mdx`
   - `docs/**/*.ts`, `docs/**/*.tsx`
   - `docs/docusaurus.config.ts`
   - `docs/package.json`, `docs/pnpm-lock.yaml`

2. **Release workflow completes** successfully

### Deployment Status

- ✅ Builds successfully with Node 24
- ✅ Deploys to GitHub Pages
- ✅ Custom domain configured
- ✅ Search functionality enabled
- ✅ Social media metadata included

## Local Development

### Build Locally

```bash
cd docs
pnpm install
pnpm run build
```

### Preview Build

```bash
pnpm run serve
```

### Development Server

```bash
pnpm run start
```

## Troubleshooting

### Build Failures

Check the workflow logs in `.github/workflows/documentation.yaml`

Common issues:
- Node version mismatch (requires Node 24+)
- Missing dependencies (run `pnpm install`)
- Broken markdown links (check file references)

### Deployment Issues

- Verify GitHub Pages settings in repository
- Check custom domain DNS configuration
- Review GitHub Actions permissions

## Future Enhancements

- [ ] Versioned documentation (when v1.0.0 released)
- [ ] Internationalization support
- [ ] Search analytics
- [ ] Documentation versioning strategy
