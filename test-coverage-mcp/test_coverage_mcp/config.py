"""Configuration management using pydantic-settings.

This module provides centralized configuration management for the MCP server
template. It uses pydantic-settings to load configuration from environment
variables, .env files, and other sources.

Configuration Sources
=====================
Configuration is loaded from the following sources in order of precedence:
1. Direct parameter assignment (highest priority)
2. Environment variables
3. .env file (if specified)
4. Default values (lowest priority)

Environment Variables
=====================
The following environment variables are supported:
- API_TOKEN: API authentication token
- ENV_FILE: Path to .env file
- LOG_LEVEL: Logging level (debug, info, warning, error, critical)
- HOST: Server host address
- PORT: Server port number
- TRANSPORT: MCP transport protocol (sse, http-streaming)
- CORS_ALLOW_ORIGINS: CORS allowed origins
- CORS_ALLOW_CREDENTIALS: CORS allow credentials
- CORS_ALLOW_METHODS: CORS allowed methods
- CORS_ALLOW_HEADERS: CORS allowed headers

Usage Examples
==============

**Basic Usage:**

.. code-block:: python

    from src.config import get_settings

    settings = get_settings()
    print(f"Token: {settings.api_token}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")

**With Custom .env File:**

.. code-block:: python

    settings = get_settings(env_file="/path/to/.env")

**With Override Parameters:**

.. code-block:: python

    settings = get_settings(api_token="custom_token", port=9000)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, TypedDict, Unpack

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Type aliases for better readability
LogLevel = Literal["debug", "info", "warning", "error", "critical"]
TransportType = Literal["sse", "http-streaming"]


class GetSettingsKwargs(TypedDict, total=False):
    """TypedDict for get_settings() keyword arguments."""

    api_token: str | None
    host: str
    port: int
    log_level: LogLevel
    transport: TransportType
    cors_allow_origins: list[str]
    cors_allow_credentials: bool
    cors_allow_methods: list[str]
    cors_allow_headers: list[str]


class Settings(BaseSettings):
    """Application settings configuration.

    This class defines all configuration parameters for the MCP server template.
    It uses pydantic-settings to automatically load configuration from environment
    variables and .env files.

    Attributes
    ----------
    api_token : SecretStr
        API authentication token (loaded from API_TOKEN env var)
    env_file : str | None
        Path to .env file (loaded from ENV_FILE env var)
    log_level : LogLevel
        Logging level (loaded from LOG_LEVEL env var, defaults to "info")
    host : str
        Server host address (loaded from HOST env var, defaults to "0.0.0.0")
    port : int
        Server port number (loaded from PORT env var, defaults to 8000)
    transport : TransportType
        MCP transport protocol (loaded from TRANSPORT env var, defaults to "sse")
    cors_allow_origins : list[str]
        CORS allowed origins (loaded from CORS_ALLOW_ORIGINS env var)
    cors_allow_credentials : bool
        CORS allow credentials (loaded from CORS_ALLOW_CREDENTIALS env var)
    cors_allow_methods : list[str]
        CORS allowed methods (loaded from CORS_ALLOW_METHODS env var)
    cors_allow_headers : list[str]
        CORS allowed headers (loaded from CORS_ALLOW_HEADERS env var)

    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_token: SecretStr | None = Field(
        default=None,
        description="API authentication token",
        alias="API_TOKEN",
    )

    # Environment Configuration
    env_file: str | None = Field(
        default=".env",
        description="Path to .env file",
        alias="ENV_FILE",
    )

    # Server Configuration
    log_level: LogLevel = Field(
        default="info",
        description="Logging level",
        alias="LOG_LEVEL",
    )
    host: str = Field(
        default="127.0.0.1",
        description="Server host address",
        alias="HOST",
    )
    port: int = Field(
        default=8000,
        description="Server port number",
        alias="PORT",
        ge=1,
        le=65535,
    )
    transport: TransportType = Field(
        default="sse",
        description="MCP transport protocol",
        alias="TRANSPORT",
    )

    # CORS Configuration
    cors_allow_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins",
        alias="CORS_ALLOW_ORIGINS",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="CORS allow credentials",
        alias="CORS_ALLOW_CREDENTIALS",
    )
    cors_allow_methods: list[str] = Field(
        default=["*"],
        description="CORS allowed methods",
        alias="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: list[str] = Field(
        default=["*"],
        description="CORS allowed headers",
        alias="CORS_ALLOW_HEADERS",
    )

    def get_api_token(self) -> str | None:
        """Get the API token as a string.

        Returns
        -------
        str | None
            The API token as a plain string, or None if not set

        Examples
        --------
        .. code-block:: python

            settings = get_settings()
            token = settings.get_api_token()
            if token:
                print(f"Token is set: {token[:10]}...")
            else:
                print("No token configured")

        """
        return self.api_token.get_secret_value() if self.api_token else None

    @classmethod
    def from_env_file(cls, env_file: str | Path) -> Settings:
        """Create settings from a specific .env file.

        Parameters
        ----------
        env_file : str | Path
            Path to the .env file

        Returns
        -------
        Settings
            Settings instance loaded from the specified .env file

        Examples
        --------
        .. code-block:: python

            settings = Settings.from_env_file("/path/to/.env")

        """
        return cls(_env_file=str(env_file))

    # Global settings instance cache


_settings_instance: Settings | None = None


def get_settings(
    env_file: str | Path | None = None,
    no_env_file: bool = False,
    force_reload: bool = False,
    **kwargs: Unpack[GetSettingsKwargs],
) -> Settings:
    """Get the application settings instance.

    This function provides a singleton-like behavior for settings access.
    It caches the settings instance and optionally reloads it when needed.

    Parameters
    ----------
    env_file : str | Path | None, optional
        Path to .env file. If provided, overrides the default .env file.
    no_env_file : bool, optional
        If True, skips loading any .env file. Defaults to False.
    force_reload : bool, optional
        If True, forces a reload of settings even if cached. Defaults to False.
    **kwargs
        Additional parameters to override settings

    Returns
    -------
    Settings
        The application settings instance

    Examples
    --------
    .. code-block:: python

        # Get default settings
        settings = get_settings()

        # Get settings with custom .env file
        settings = get_settings(env_file="/path/to/.env")

        # Get settings with overrides
        settings = get_settings(api_token="custom_token", port=9000)

        # Force reload
        settings = get_settings(force_reload=True)

    """
    global _settings_instance

    # Return cached instance if available and not forcing reload
    if _settings_instance is not None and not force_reload:
        return _settings_instance

    # Prepare configuration arguments
    config_kwargs: dict[str, object] = {}

    # Handle .env file configuration
    if not no_env_file:
        if env_file:
            config_kwargs["_env_file"] = str(env_file)
        elif os.path.exists(".env"):
            config_kwargs["_env_file"] = ".env"

    # Add any override parameters
    if kwargs:
        config_kwargs.update(dict(kwargs))

    # Create new settings instance
    _settings_instance = Settings(**config_kwargs)

    return _settings_instance


def reset_settings() -> None:
    """Reset the cached settings instance.

    This function clears the cached settings instance, forcing the next
    call to get_settings() to create a new instance. Primarily used for testing.

    Examples
    --------
    .. code-block:: python

        from src.config import reset_settings, get_settings

        reset_settings()
        settings = get_settings()  # Creates fresh instance

    """
    global _settings_instance
    _settings_instance = None
