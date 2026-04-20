"""Unit tests for CLI commands."""

from typing import Any

import pytest
from click.testing import CliRunner

from test_coverage_mcp.cli.main import cli


class TestCLIMain:
    """Tests for main CLI."""

    def test_cli_help(self) -> None:
        """Test CLI help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Test Coverage MCP" in result.output
        assert "Usage:" in result.output

    def test_cli_verbose_flag(self) -> None:
        """Test CLI verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cli_config_option(self) -> None:
        """Test CLI config option with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--config", "/nonexistent/file.yaml", "--help"])

        # Click doesn't validate file existence by default with exists=True
        # It will still show help, so we just verify it runs
        assert "Usage:" in result.output


class TestServeCommand:
    """Tests for serve command."""

    def test_serve_help(self) -> None:
        """Test serve command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--help"])

        assert result.exit_code == 0
        assert "Start the test-coverage-mcp MCP server" in result.output

    def test_serve_default_options(self) -> None:
        """Test serve command with default options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve"])

        assert result.exit_code == 0
        assert "Starting MCP server" in result.output

    def test_serve_with_http_transport(self) -> None:
        """Test serve command with HTTP transport."""
        runner = CliRunner()
        result = runner.invoke(cli, ["serve", "--transport", "http"])

        assert result.exit_code == 0
        assert "Starting MCP server" in result.output

    def test_serve_with_custom_host_port(self) -> None:
        """Test serve command with custom host and port."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["serve", "--transport", "http", "--host", "0.0.0.0", "--port", "9000"]
        )

        assert result.exit_code == 0


class TestProvidersCommand:
    """Tests for providers command."""

    def test_providers_help(self) -> None:
        """Test providers command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["providers", "--help"])

        assert result.exit_code == 0
        assert "Manage coverage providers" in result.output

    def test_providers_list(self) -> None:
        """Test providers list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["providers", "list"])

        assert result.exit_code == 0
        assert "Available providers:" in result.output
        assert "codecov" in result.output

    def test_providers_describe_codecov(self) -> None:
        """Test providers describe command for codecov."""
        runner = CliRunner()
        result = runner.invoke(cli, ["providers", "describe", "codecov"])

        assert result.exit_code == 0
        assert "codecov" in result.output
        assert "Capabilities:" in result.output

    def test_providers_describe_unknown(self) -> None:
        """Test providers describe command for unknown provider."""
        runner = CliRunner()
        result = runner.invoke(cli, ["providers", "describe", "unknown"])

        assert result.exit_code == 0
        assert "not found" in result.output


class TestDoctorCommand:
    """Tests for doctor command."""

    def test_doctor_help(self) -> None:
        """Test doctor command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor", "--help"])

        assert result.exit_code == 0
        assert "Check environment and system health" in result.output

    def test_doctor_basic(self) -> None:
        """Test doctor command basic execution."""
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])

        assert result.exit_code == 0
        assert "Running health checks" in result.output
        assert "Environment Variables:" in result.output
        assert "Provider Connectivity:" in result.output
        assert "Plugin Loading:" in result.output
        assert "Health Status:" in result.output

    def test_doctor_verbose(self) -> None:
        """Test doctor command with verbose output."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "doctor"])

        assert result.exit_code == 0
        assert "Detailed Information:" in result.output


class TestCompletionCommand:
    """Tests for completion command."""

    def test_completion_help(self) -> None:
        """Test completion command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "--help"])

        assert result.exit_code == 0
        assert "Generate shell completion script" in result.output

    def test_completion_bash(self) -> None:
        """Test bash completion generation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "--shell", "bash"])

        assert result.exit_code == 0
        assert "Bash completion" in result.output
        assert "test-coverage-mcp" in result.output

    def test_completion_zsh(self) -> None:
        """Test zsh completion generation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "--shell", "zsh"])

        assert result.exit_code == 0
        assert "Zsh completion" in result.output

    def test_completion_fish(self) -> None:
        """Test fish completion generation."""
        runner = CliRunner()
        result = runner.invoke(cli, ["completion", "--shell", "fish"])

        assert result.exit_code == 0
        assert "Fish completion" in result.output
