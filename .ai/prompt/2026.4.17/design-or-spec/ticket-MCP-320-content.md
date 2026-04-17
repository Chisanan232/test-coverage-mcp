Parent epic: MCP-18 / MCP-19 (cross-cutting namespace and provider packaging follow-up)

Description:
The monorepo currently exposes the core Python package as `src`, which forces imports like `from src.domain import ...`. This should be corrected so the public Python namespace is the actual package name: `test_coverage_mcp`.

This ticket should follow the `src` layout design pattern. That means `src` remains the source-layout directory on disk, but the real Python package lives under it.

Target layout:

Core package:

`src/test_coverage_mcp/...`

Provider package:

`src/test_coverage_mcp/providers/codecov/...`

This change also needs a clear provider namespace strategy for the Codecov package. Recommended public namespace:

Core package: `test_coverage_mcp`

Provider package: `test_coverage_mcp.providers.codecov`

Design decision:
Use `providers` as the public namespace root instead of `adapter` or singular `provider`.

Rationale:

- Aligns with the existing plugin entry-point group: `test_coverage_mcp.providers`
- Scales naturally to multiple providers in the monorepo
- Keeps `adapter` as an internal implementation concept instead of the published import path
- Avoids awkward singular namespace growth like `test_coverage_mcp.provider.<name>`
- Keeps the project on a conventional Python `src` layout while still exposing a clean public package namespace

Implementation scope:

- Restructure the core package so `src/` is only the source-layout directory, not the import namespace.
- Move the core Python package under `src/test_coverage_mcp/`.
- Export the core library from `test_coverage_mcp/...`.
- Update packaging metadata and console-script entry points to reference `test_coverage_mcp` instead of `src`.
- Replace internal imports, tests, patch targets, and docs/examples that currently reference `src.*`.
- Replace CLI module examples that currently use `python -m src...` with `python -m test_coverage_mcp...` or the final supported CLI entry path.
- Restructure the Codecov provider package so it installs under the shared namespace `test_coverage_mcp.providers.codecov`.
- Update provider entry points and import examples to the new namespace.
- Validate editable install and workspace install behavior in the monorepo.

Acceptance criteria:

- Core filesystem layout follows `src/test_coverage_mcp/...`
- Provider filesystem layout follows `src/test_coverage_mcp/providers/codecov/...`
- Core imports use `from test_coverage_mcp...` instead of `from src...`
- The root console script no longer references `src.entry:main`
- Core docs and CLI examples no longer use `python -m src...`
- Provider package can be imported as `test_coverage_mcp.providers.codecov`
- Provider entry-point registration resolves the Codecov provider from the new namespace
- Tests and mocks use the new import paths successfully
- Packaging/build configuration works for both workspace members after the namespace migration
- A short architecture note documents why `src/test_coverage_mcp/...` is the chosen packaging layout and why `test_coverage_mcp.providers.<provider>` is the chosen public namespace

Relationship to current work:

- This is a follow-up to the current provider-system and Codecov packaging work
- It should be considered before finalizing the public import surface for provider implementations and CLI entry points
