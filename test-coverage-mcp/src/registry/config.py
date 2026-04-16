"""Configuration model for providers using Pydantic-Settings."""

from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseSettings):
    """Base configuration for coverage providers."""

    provider_name: str = Field(..., description="Name of the provider")
    provider_version: str = Field(default="1.0.0", description="Provider version")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    timeout_seconds: int = Field(default=30, description="API timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay_seconds: float = Field(default=1.0, description="Delay between retries")

    model_config = SettingsConfigDict(
        env_prefix="PROVIDER_",
        case_sensitive=False,
        extra="allow",
    )


class CodecovConfig(ProviderConfig):
    """Configuration for Codecov provider."""

    api_token: str = Field(..., description="Codecov API token")
    api_base_url: str = Field(
        default="https://api.codecov.io", description="Codecov API base URL"
    )
    owner: Optional[str] = Field(None, description="Repository owner")
    repo: Optional[str] = Field(None, description="Repository name")

    model_config = SettingsConfigDict(
        env_prefix="CODECOV_",
        case_sensitive=False,
        extra="allow",
    )


class RegistryConfig(BaseSettings):
    """Configuration for the provider registry."""

    auto_discover: bool = Field(
        default=True, description="Automatically discover providers via entry points"
    )
    auto_initialize: bool = Field(
        default=True, description="Automatically initialize discovered providers"
    )
    default_provider: Optional[str] = Field(
        None, description="Default provider to use"
    )
    provider_configs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Provider-specific configurations"
    )
    health_check_interval_seconds: int = Field(
        default=300, description="Interval between health checks"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = SettingsConfigDict(
        env_prefix="REGISTRY_",
        case_sensitive=False,
        extra="allow",
    )


class ApplicationConfig(BaseSettings):
    """Main application configuration."""

    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    providers: Dict[str, ProviderConfig] = Field(
        default_factory=dict, description="Provider configurations"
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Application log level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    @classmethod
    def from_env(cls) -> "ApplicationConfig":
        """Create configuration from environment variables.

        Returns:
            ApplicationConfig instance
        """
        return cls()

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider configuration or None
        """
        return self.providers.get(provider_name)
