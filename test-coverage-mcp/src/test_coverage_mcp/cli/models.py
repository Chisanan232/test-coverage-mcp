"""Type models for CLI commands."""

from typing import Optional

from pydantic import BaseModel, Field


class ServeOptions(BaseModel):
    """Options for serve command."""

    transport: str = Field(default="stdio", description="Transport type: stdio or http")
    provider: str = Field(default="auto", description="Provider: auto or codecov")
    host: str = Field(default="127.0.0.1", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")


class ProvidersListOptions(BaseModel):
    """Options for providers list command."""

    verbose: bool = Field(default=False, description="Enable verbose output")


class ProvidersDescribeOptions(BaseModel):
    """Options for providers describe command."""

    name: str = Field(..., description="Provider name")
    verbose: bool = Field(default=False, description="Enable verbose output")


class DoctorOptions(BaseModel):
    """Options for doctor command."""

    verbose: bool = Field(default=False, description="Enable verbose output")


class CLIContext(BaseModel):
    """CLI context object."""

    verbose: bool = Field(default=False, description="Enable verbose output")
    config: Optional[str] = Field(default=None, description="Path to configuration file")
