"""Main CLI entry point for test-coverage-mcp."""

import click

from test_coverage_mcp.cli.providers import providers
from test_coverage_mcp.cli.serve import serve


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: str) -> None:
    """Test Coverage MCP - Coverage analysis and testing tools."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config


cli.add_command(serve)
cli.add_command(providers)


if __name__ == "__main__":
    cli()
