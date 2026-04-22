"""CLI models and data transfer objects.

This module contains Pydantic models for CLI argument parsing and data transfer
objects used throughout the application.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class LogLevel(str, Enum):
    """Logging level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MCPTransportType(str, Enum):
    """MCP transport type enumeration."""

    SSE = "sse"
    HTTP_STREAMING = "http-streaming"


class ServerConfig(BaseModel):
    """Server configuration model for CLI arguments.

    This model represents the configuration parameters that can be passed
    via command line arguments to the server.

    Attributes
    ----------
    host : str
        Server host address (default: "0.0.0.0")
    port : int
        Server port number (default: 8000, range: 1-65535)
    log_level : LogLevel
        Logging level (default: LogLevel.INFO)
    reload : bool
        Enable auto-reload for development (default: False)
    env_file : str | None
        Path to .env file (default: ".env")
    token : str | None
        API token (overrides env file if provided)
    transport : MCPTransportType
        MCP transport protocol (default: MCPTransportType.SSE)

    """

    model_config = ConfigDict(use_enum_values=True, extra="forbid")

    host: str = Field(
        default="127.0.0.1",
        description="Host to bind the server to",
    )
    port: int = Field(
        default=8000,
        description="Port to bind the server to",
        ge=1,
        le=65535,
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level",
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload for development",
    )
    env_file: str | None = Field(
        default=".env",
        description="Path to the .env file for environment variables",
    )
    token: str | None = Field(
        default=None,
        description="API token (overrides token from .env file if provided)",
    )
    transport: MCPTransportType = Field(
        default=MCPTransportType.SSE,
        description="Transport protocol to use for MCP",
    )
