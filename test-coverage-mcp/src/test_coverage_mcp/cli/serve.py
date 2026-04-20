"""Serve command for starting the MCP server."""

import click


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Transport type for MCP server",
)
@click.option(
    "--provider",
    type=click.Choice(["auto", "codecov"]),
    default="auto",
    help="Coverage provider to use",
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind to (for http transport)",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port to bind to (for http transport)",
)
@click.pass_context
def serve(
    ctx: click.Context,
    transport: str,
    provider: str,
    host: str,
    port: int,
) -> None:
    """Start the test-coverage-mcp MCP server.

    Supports both stdio and HTTP transports for MCP communication.
    """
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        click.echo(f"Starting MCP server with transport={transport}, provider={provider}")

    if transport == "stdio":
        click.echo("Starting MCP server with stdio transport...")
        # Implementation would start the MCP server with stdio transport
    elif transport == "http":
        click.echo(f"Starting MCP server on {host}:{port}...")
        # Implementation would start the MCP server with HTTP transport
