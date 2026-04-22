"""Secure token and secret management using Pydantic-Settings."""

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSecrets(BaseSettings):
    """Secure storage for provider secrets."""

    api_token: Optional[SecretStr] = Field(
        None, description="API token (kept as secret)"
    )
    api_key: Optional[SecretStr] = Field(None, description="API key (kept as secret)")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[SecretStr] = Field(
        None, description="Password (kept as secret)"
    )

    model_config = SettingsConfigDict(
        env_prefix="PROVIDER_",
        case_sensitive=False,
        extra="allow",
    )

    def get_token(self) -> Optional[str]:
        """Get API token as string.

        Returns:
            Token string or None
        """
        if self.api_token is None:
            return None
        return self.api_token.get_secret_value()

    def get_key(self) -> Optional[str]:
        """Get API key as string.

        Returns:
            Key string or None
        """
        if self.api_key is None:
            return None
        return self.api_key.get_secret_value()

    def get_password(self) -> Optional[str]:
        """Get password as string.

        Returns:
            Password string or None
        """
        if self.password is None:
            return None
        return self.password.get_secret_value()


class CodecovSecrets(ProviderSecrets):
    """Secure storage for Codecov secrets."""

    codecov_token: Optional[SecretStr] = Field(
        None, description="Codecov API token"
    )

    model_config = SettingsConfigDict(
        env_prefix="CODECOV_",
        case_sensitive=False,
        extra="allow",
    )

    def get_codecov_token(self) -> Optional[str]:
        """Get Codecov token as string.

        Returns:
            Token string or None
        """
        if self.codecov_token is None:
            return None
        return self.codecov_token.get_secret_value()


class ApplicationSecrets(BaseSettings):
    """Application-level secrets management."""

    provider_secrets: Optional[ProviderSecrets] = Field(
        None, description="Provider secrets"
    )
    codecov_secrets: Optional[CodecovSecrets] = Field(
        None, description="Codecov-specific secrets"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    @classmethod
    def from_env(cls) -> "ApplicationSecrets":
        """Load secrets from environment.

        Returns:
            ApplicationSecrets instance
        """
        return cls()
