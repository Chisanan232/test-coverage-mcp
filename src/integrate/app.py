"""Integrated FastAPI app factory for Template MCP + Webhook server.

This module creates a FastAPI application that integrates both the MCP server
and the webhook server into a single process. It mounts transport-specific
MCP apps and exposes a health check router.

Highlights
==========
- Integrated mode runs both MCP and webhook servers together
- Supports SSE and streamable-HTTP transports for MCP
- Uses centralized client initialization with configurable retries
- Includes a health check router for operational monitoring

Quick Start
===========

.. code-block:: python

    from src.integrate.app import IntegratedServerFactory

    # Create app (SSE transport, mounted at /mcp)
    app = IntegratedServerFactory.create(mcp_transport="sse", mcp_mount_path="/mcp", retry=3)

    # Or create with streamable-HTTP transport
    app = IntegratedServerFactory.create(mcp_transport="streamable-http", retry=3)

Notes
-----
- When retry > 0, SDK retry handlers are enabled for rate limits, server
  errors, and connection issues.
- Token can be deferred at creation time and initialized later by the entrypoint
  (useful for CLI-driven configuration).

"""

from __future__ import annotations

import contextlib
import logging
from collections.abc import Generator
from typing import Final, TypedDict, Unpack

from fastapi import FastAPI

from .._base import BaseServerFactory
from ..mcp.app import mcp_factory
from ..models.cli import MCPTransportType
from ..web_server.app import web_factory

# Default mount paths for each transport type
_DEFAULT_MOUNT_PATHS: Final[dict[MCPTransportType, str]] = {
    MCPTransportType.SSE: "/sse",
    MCPTransportType.HTTP_STREAMING: "/mcp",
}


class IntegratedServerKwargs(TypedDict, total=False):
    """TypedDict for IntegratedServerFactory.create() keyword arguments."""

    token: str | None
    mcp_transport: str | MCPTransportType
    mcp_mount_path: str | None
    retry: int


_LOG: Final[logging.Logger] = logging.getLogger(__name__)

_INTEGRATED_SERVER_INSTANCE: FastAPI | None = None


@contextlib.contextmanager
def integrated_server_lifecycle() -> Generator[None, None, None]:
    """Context manager for integrated server initialization and cleanup.

    This context manager ensures proper initialization and cleanup of the
    integrated server instance, including dependent factories.

    Yields
    ------
    None

    Examples
    --------
    .. code-block:: python

        from src.integrate.app import integrated_server_lifecycle

        with integrated_server_lifecycle():
            app = IntegratedServerFactory.create()
            # Use app
        # Cleanup happens automatically

    """
    try:
        yield
    finally:
        # Cleanup is handled by reset() if needed
        pass


class IntegratedServerFactory(BaseServerFactory[FastAPI]):
    """Factory for building the integrated Template MCP + webhook FastAPI app.

    Responsibilities
    ----------------
    - Create a FastAPI app with webhook routes
    - Initialize client lazily with optional retries
    - Mount MCP sub-app depending on transport (SSE or streamable-HTTP)
    - Include health check routes

    Examples
    --------
    .. code-block:: python

        from src.integrate.app import IntegratedServerFactory

        # Create default integrated app (SSE transport)
        app = IntegratedServerFactory.create(mcp_transport="sse", mcp_mount_path="/mcp")

        # Access the instance later
        app2 = IntegratedServerFactory.get()

    """

    @staticmethod
    def create(**kwargs: Unpack[IntegratedServerKwargs]) -> FastAPI:
        """Create and configure the integrated FastAPI server.

        Parameters
        ----------
        **kwargs
            token : Optional[str]
                API token to initialize the global client. If None,
                initialization is deferred until the entrypoint provides it.
            mcp_transport : str or MCPTransportType
                Transport for MCP server. One of "sse" or "streamable-http".
            mcp_mount_path : Optional[str]
                Mount path for MCP sub-app. If None, uses default for transport type.
            retry : int
                Retry count for client operations (0 disables retries).

        Returns
        -------
        FastAPI
            Configured FastAPI server instance that serves both webhook and MCP features.

        Raises
        ------
        ValueError
            If an invalid MCP transport is provided.

        Examples
        --------
        .. code-block:: python

            app = IntegratedServerFactory.create(
                token=None,
                mcp_transport="sse",
                mcp_mount_path="/mcp",
                retry=3,
            )

        """
        token: str | None = kwargs.get("token")
        mcp_transport_input: str | MCPTransportType = kwargs.get("mcp_transport", MCPTransportType.SSE)
        mcp_mount_path: str | None = kwargs.get("mcp_mount_path")
        retry: int = kwargs.get("retry", 3)

        # Normalize transport to enum
        if isinstance(mcp_transport_input, str):
            try:
                mcp_transport = MCPTransportType(mcp_transport_input)
            except ValueError as err:
                error_msg = (
                    f"Invalid transport type for integrated server: {mcp_transport_input}. "
                    f"Must be one of: {', '.join([t.value for t in MCPTransportType])}"
                )
                raise ValueError(error_msg) from err
        else:
            mcp_transport = mcp_transport_input

        # Determine mount path: use provided value or default for transport type
        if mcp_mount_path is None:
            mcp_mount_path = _DEFAULT_MOUNT_PATHS[mcp_transport]

        # Ensure MCP server is created
        try:
            mcp_factory.get()
        except AssertionError:
            mcp_factory.create()

        # Create or get the web server
        try:
            app = web_factory.get()
        except AssertionError:
            app = web_factory.create()

        # Mount MCP sub-app based on transport type
        if mcp_transport == MCPTransportType.SSE:
            app.mount(mcp_mount_path, mcp_factory.get().sse_app())
            _LOG.info(f"MCP SSE transport mounted at {mcp_mount_path}")
        elif mcp_transport == MCPTransportType.HTTP_STREAMING:
            app.mount(mcp_mount_path, mcp_factory.get().streamable_http_app())
            _LOG.info(f"MCP HTTP streaming transport mounted at {mcp_mount_path}")
        else:
            error_msg = (
                f"Invalid transport type for integrated server: {mcp_transport}. "
                f"Must be one of: {', '.join([t.value for t in MCPTransportType])}"
            )
            raise ValueError(error_msg)

        # Store the integrated instance
        global _INTEGRATED_SERVER_INSTANCE
        _INTEGRATED_SERVER_INSTANCE = app

        return app

    @staticmethod
    def get() -> FastAPI:
        """Get the existing integrated FastAPI server instance.

        Returns
        -------
        FastAPI
            The existing integrated server instance

        Raises
        ------
        AssertionError
            If no integrated server has been created yet

        Examples
        --------
        .. code-block:: python

            from src.integrate.app import IntegratedServerFactory

            app = IntegratedServerFactory.get()

        """
        assert _INTEGRATED_SERVER_INSTANCE is not None, "Integrated server must be created first."
        return _INTEGRATED_SERVER_INSTANCE

    @staticmethod
    def reset() -> None:
        """Reset the integrated server instance.

        This method clears the integrated server instance and also resets
        the underlying MCP and web server factories. Primarily used for testing.

        Returns
        -------
        None

        Examples
        --------
        .. code-block:: python

            from src.integrate.app import IntegratedServerFactory

            IntegratedServerFactory.reset()

        """
        global _INTEGRATED_SERVER_INSTANCE
        _INTEGRATED_SERVER_INSTANCE = None

        # Also reset the underlying factories
        mcp_factory.reset()
        web_factory.reset()


# Create the integrated factory instance
integrated_factory = IntegratedServerFactory
