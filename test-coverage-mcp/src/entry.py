"""Main entry point for the Template MCP Server.

This module provides the command-line interface for running the MCP server
template. It supports multiple transport modes and can run in standalone or
integrated mode.

Module Overview
===============
This entry point handles:
1. Parsing command-line arguments
2. Setting up logging
3. Loading environment variables from .env file
4. Initializing the server with proper configuration
5. Starting the server in the specified mode

Transport Modes
===============
1. **stdio** (default): Standard input/output transport for local MCP clients
2. **sse**: Server-Sent Events transport for HTTP-based clients
3. **streamable-http**: Streamable HTTP transport for HTTP-based clients

Server Modes
============
1. **Standalone**: Runs only the MCP server
2. **Integrated**: Runs both MCP server and webhook server

Quick Start Examples
====================

**1. Run with default stdio transport:**

    .. code-block:: bash

        python -m src.entry

**2. Run with SSE transport on port 8000:**

    .. code-block:: bash

        python -m src.entry --transport sse --host 0.0.0.0 --port 8000

**3. Run with streamable-http transport:**

    .. code-block:: bash

        python -m src.entry --transport streamable-http --host 0.0.0.0 --port 8000

**4. Run in integrated mode (MCP + Webhook):**

    .. code-block:: bash

        python -m src.entry --integrated --transport sse --host 0.0.0.0 --port 8000

**5. Using curl to test HTTP endpoints (SSE/Streamable-HTTP):**

    .. code-block:: bash

        # Health check
        curl http://localhost:8000/health

        # MCP SSE endpoint
        curl http://localhost:8000/sse

        # MCP HTTP streaming endpoint
        curl http://localhost:8000/mcp

Environment Variables
======================
- **API_TOKEN**: API authentication token (required)
- **ENV_FILE**: Path to .env file (optional, defaults to .env)
- **LOG_LEVEL**: Logging level (optional, defaults to info)
- **HOST**: Server host address (optional, defaults to 0.0.0.0)
- **PORT**: Server port number (optional, defaults to 8000)
- **TRANSPORT**: MCP transport protocol (optional, defaults to sse)

Configuration Files
===================
The server supports loading environment variables from a .env file:

    .. code-block:: bash

        # Load from custom .env file
        python -m src.entry --env-file /path/to/.env

        # Skip loading .env file
        python -m src.entry --no-env-file

Logging
=======
Control logging verbosity with the --log-level option:

    .. code-block:: bash

        # Debug logging
        python -m src.entry --log-level DEBUG

        # Info logging (default)
        python -m src.entry --log-level INFO

        # Warning logging
        python -m src.entry --log-level WARNING
"""

from __future__ import annotations

import argparse
import logging
import sys

import uvicorn
from pydantic import ValidationError

from .config import GetSettingsKwargs, Settings, get_settings
from .integrate.app import integrated_factory
from .mcp.app import mcp_factory
from .models.cli import LogLevel, MCPTransportType, ServerConfig

_LOG = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    This function parses CLI arguments and returns them as a namespace object.
    The arguments are later validated and converted to a ServerConfig model.

    Parameters
    ----------
    argv : Optional[list[str]], optional
        Command-line arguments to parse. If None, uses sys.argv.
        Useful for testing and programmatic invocation.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments

    Examples
    --------
    .. code-block:: python

        # Parse default arguments
        args = parse_args()

        # Parse custom arguments
        args = parse_args(["--transport", "sse", "--port", "8000"])

    """
    parser = argparse.ArgumentParser(
        description="Run the Template MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run with default settings
  %(prog)s --transport sse --port 8000       # Run with SSE transport
  %(prog)s --integrated --transport sse       # Run in integrated mode
  %(prog)s --log-level DEBUG --reload        # Run with debug logging
  %(prog)s --env-file .env.production         # Use custom .env file
  %(prog)s --token your_api_token            # Override API token
        """,
    )

    # Server configuration
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=[level.value for level in LogLevel],
        help="Logging level (default: info)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )

    # Environment configuration
    parser.add_argument(
        "--env-file",
        type=str,
        dest="env_file",
        default=".env",
        help="Path to the .env file for environment variables (default: .env)",
    )
    parser.add_argument(
        "--no-env-file",
        action="store_true",
        dest="no_env_file",
        help="Skip loading .env file",
    )

    # API configuration
    parser.add_argument(
        "--token",
        type=str,
        help="API token (overrides token from .env file if provided)",
    )

    # MCP configuration
    parser.add_argument(
        "--transport",
        type=str,
        default="sse",
        dest="transport",
        choices=[transport.value for transport in MCPTransportType],
        help="Transport protocol to use for MCP (sse or http-streaming, default: sse)",
    )

    # Server mode
    parser.add_argument(
        "--integrated",
        action="store_true",
        help="Run in integrated mode (MCP + webhook server)",
    )

    return parser.parse_args(argv)


def configure_logging(log_level: str) -> None:
    """Configure logging with the specified log level.

    Sets up the Python logging system with a standard format that includes
    timestamps, logger names, log levels, and messages. This is applied
    globally to all loggers in the application.

    Parameters
    ----------
    log_level : str
        The logging level to use (debug, info, warning, error, critical)

    Raises
    ------
    ValueError
        If an invalid log level is specified

    Examples
    --------
    .. code-block:: python

        # Configure debug logging
        configure_logging("debug")

        # Configure info logging (default)
        configure_logging("info")

        # Configure error logging
        configure_logging("error")

    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        error_msg = f"Invalid log level: {log_level}"
        raise ValueError(error_msg)

    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_server_config(args: argparse.Namespace) -> ServerConfig:
    """Create a ServerConfig from parsed arguments.

    This function converts the parsed CLI arguments into a validated
    ServerConfig model instance.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments

    Returns
    -------
    ServerConfig
        Validated server configuration

    Raises
    ------
    ValidationError
        If the configuration is invalid

    Examples
    --------
    .. code-block:: python

        args = parse_args(["--host", "0.0.0.0", "--port", "8000"])
        config = create_server_config(args)

    """
    args_dict = vars(args)

    # Remove arguments that are not part of ServerConfig
    config_dict = {key: value for key, value in args_dict.items() if key in ServerConfig.model_fields}

    try:
        return ServerConfig(**config_dict)
    except ValidationError as e:
        print(f"Error in server configuration: {e}", file=sys.stderr)
        sys.exit(1)


def initialize_server_environment(config: ServerConfig) -> Settings | None:
    """Initialize common server environment and settings.

    This function handles shared initialization logic for both standalone
    and integrated server modes, including logging configuration and
    settings loading.

    Parameters
    ----------
    config : ServerConfig
        Server configuration

    Returns
    -------
    Optional[object]
        Settings object if initialization succeeds, None otherwise

    Examples
    --------
    .. code-block:: python

        from src.models.cli import ServerConfig
        from src.entry import initialize_server_environment

        config = ServerConfig(transport="sse")
        settings = initialize_server_environment(config)
        if settings is None:
            return  # Initialization failed

    """
    # Configure logging
    configure_logging(config.log_level)

    # Initialize settings
    settings_kwargs: GetSettingsKwargs = {}
    if config.token:
        settings_kwargs["api_token"] = config.token

    try:
        return get_settings(
            env_file=config.env_file,
            no_env_file=config.env_file is None,
            force_reload=False,
            **settings_kwargs,
        )
    except Exception as e:
        _LOG.error(f"Failed to load configuration: {e}")
        return None


def run_standalone_server(config: ServerConfig) -> None:
    """Run the MCP server in standalone mode.

    This function runs only the MCP server without webhook functionality.
    The transport type determines how the server is started.

    Parameters
    ----------
    config : ServerConfig
        Server configuration

    Examples
    --------
    .. code-block:: python

        from src.models.cli import ServerConfig
        from src.entry import run_standalone_server

        config = ServerConfig(transport="sse")
        run_standalone_server(config)

    """
    # Initialize environment
    settings = initialize_server_environment(config)
    if settings is None:
        return

    # Create MCP server
    try:
        mcp_server = mcp_factory.create()
    except AssertionError:
        mcp_server = mcp_factory.get()

    # Run server based on transport
    if config.transport == MCPTransportType.SSE or config.transport == MCPTransportType.HTTP_STREAMING:
        # HTTP-based transport - run with uvicorn
        from src.web_server.app import create_app

        app = create_app(config)
        _LOG.info(f"Starting MCP server with {config.transport} transport on {config.host}:{config.port}")

        uvicorn.run(
            app=app,
            host=config.host,
            port=config.port,
            log_level=config.log_level,
            reload=config.reload,
        )
    else:
        # stdio transport - run directly
        _LOG.info("Starting MCP server with stdio transport")
        mcp_server.run(transport="stdio")


def run_integrated_server(config: ServerConfig) -> None:
    """Run the server in integrated mode (MCP + webhook).

    This function runs both the MCP server and webhook server together
    in a single FastAPI application.

    Parameters
    ----------
    config : ServerConfig
        Server configuration

    Examples
    --------
    .. code-block:: python

        from src.models.cli import ServerConfig
        from src.entry import run_integrated_server

        config = ServerConfig(transport="sse")
        run_integrated_server(config)

    """
    # Initialize environment
    settings = initialize_server_environment(config)
    if settings is None:
        return

    # Create integrated server
    try:
        app = integrated_factory.create(
            token=settings.get_api_token(),
            mcp_transport=config.transport,
            mcp_mount_path="/mcp",
        )
    except ValueError as e:
        _LOG.error(f"Invalid transport for integrated mode: {e}")
        return

    _LOG.info(f"Starting integrated server (MCP + webhook) on {config.host}:{config.port}")

    # Run with uvicorn
    uvicorn.run(
        app=app,
        host=config.host,
        port=config.port,
        log_level=config.log_level,
        reload=config.reload,
    )


def main(argv: list[str] | None = None) -> None:
    """Run the Template MCP Server main entry point.

    This function serves as the primary entry point when running the server
    from the command line. It:
    1. Parses command line arguments
    2. Validates the configuration
    3. Starts the server in the specified mode

    Parameters
    ----------
    argv : Optional[list[str]], optional
        Command-line arguments to parse. If None, uses sys.argv.
        Useful for testing and programmatic invocation.

    Examples
    --------
    .. code-block:: python

        # Run with default settings
        main()

        # Run with custom arguments
        main(["--transport", "sse", "--port", "8000"])

    """
    # Parse arguments
    args = parse_args(argv)

    # Create server configuration
    config = create_server_config(args)

    # Run server in the appropriate mode
    if args.integrated:
        run_integrated_server(config)
    else:
        run_standalone_server(config)


if __name__ == "__main__":
    main()
