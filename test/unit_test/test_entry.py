"""Test entry point functionality."""

from argparse import Namespace
from unittest.mock import MagicMock, patch

import pytest

from src.entry import (
    configure_logging,
    create_server_config,
    initialize_server_environment,
    main,
    parse_args,
    run_integrated_server,
    run_standalone_server,
)
from src.models.cli import LogLevel, MCPTransportType, ServerConfig


class TestParseArgs:
    """Test cases for the parse_args function."""

    def test_parse_default_args(self) -> None:
        """Test parsing default arguments."""
        args = parse_args([])

        assert args.host == "127.0.0.1"
        assert args.port == 8000
        assert args.log_level == "info"
        assert args.reload is False
        assert args.env_file == ".env"
        assert args.no_env_file is False
        assert args.token is None
        assert args.transport == "sse"
        assert args.integrated is False

    def test_parse_custom_args(self) -> None:
        """Test parsing custom arguments."""
        args = parse_args(
            [
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
                "--log-level",
                "debug",
                "--reload",
                "--env-file",
                "/custom/.env",
                "--token",
                "test_token",
                "--transport",
                "http-streaming",
                "--integrated",
            ]
        )

        assert args.host == "127.0.0.1"
        assert args.port == 9000
        assert args.log_level == "debug"
        assert args.reload is True
        assert args.env_file == "/custom/.env"
        assert args.no_env_file is False
        assert args.token == "test_token"
        assert args.transport == "http-streaming"
        assert args.integrated is True

    def test_parse_no_env_file(self) -> None:
        """Test parsing with --no-env-file flag."""
        args = parse_args(["--no-env-file"])

        assert args.no_env_file is True
        assert args.env_file == ".env"  # Still has default value

    def test_parse_help(self) -> None:
        """Test parsing help argument."""
        with pytest.raises(SystemExit):
            parse_args(["--help"])

    def test_parse_invalid_transport(self) -> None:
        """Test parsing invalid transport type."""
        with pytest.raises(SystemExit):
            parse_args(["--transport", "invalid"])

    def test_parse_invalid_log_level(self) -> None:
        """Test parsing invalid log level."""
        with pytest.raises(SystemExit):
            parse_args(["--log-level", "invalid"])

    def test_parse_invalid_port(self) -> None:
        """Test parsing invalid port number."""
        with pytest.raises(SystemExit):
            parse_args(["--port", "invalid"])

    def test_parse_argv_parameter(self) -> None:
        """Test parsing with custom argv list."""
        argv = ["--host", "192.168.1.1", "--port", "8080"]
        args = parse_args(argv)

        assert args.host == "192.168.1.1"
        assert args.port == 8080


class TestCreateServerConfig:
    """Test cases for the create_server_config function."""

    def test_create_config_from_default_args(self) -> None:
        """Test creating config from default arguments."""
        args = parse_args([])
        config = create_server_config(args)

        assert isinstance(config, ServerConfig)
        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.log_level == LogLevel.INFO
        assert config.transport == MCPTransportType.SSE

    def test_create_config_from_custom_args(self) -> None:
        """Test creating config from custom arguments."""
        args = parse_args(
            [
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
                "--log-level",
                "debug",
                "--transport",
                "http-streaming",
                "--reload",
                "--token",
                "test_token",
            ]
        )
        config = create_server_config(args)

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.log_level == LogLevel.DEBUG
        assert config.transport == MCPTransportType.HTTP_STREAMING
        assert config.reload is True
        assert config.token == "test_token"

    def test_create_config_filters_irrelevant_args(self) -> None:
        """Test that irrelevant arguments are filtered out."""
        args = parse_args(["--integrated", "--no-env-file"])
        config = create_server_config(args)

        # Should not have integrated or no_env_file attributes
        assert not hasattr(config, "integrated")
        assert not hasattr(config, "no_env_file")


class TestConfigureLogging:
    """Test cases for the configure_logging function."""

    def test_configure_logging_info(self) -> None:
        """Test configuring info logging."""
        # Should not raise an exception
        configure_logging("info")

    def test_configure_logging_debug(self) -> None:
        """Test configuring debug logging."""
        # Should not raise an exception
        configure_logging("debug")

    def test_configure_logging_invalid_level(self) -> None:
        """Test configuring invalid logging level."""
        with pytest.raises(ValueError, match="Invalid log level"):
            configure_logging("invalid")


class TestInitializeServerEnvironment:
    """Test cases for the initialize_server_environment function."""

    @patch("src.entry.get_settings")
    @patch("src.entry.configure_logging")
    def test_initialize_success(self, mock_configure_logging: MagicMock, mock_get_settings: MagicMock) -> None:
        """Test successful environment initialization."""
        # Mock settings
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        config = ServerConfig()
        result = initialize_server_environment(config)

        # Verify logging was configured
        mock_configure_logging.assert_called_once_with(config.log_level)

        # Verify settings were loaded
        mock_get_settings.assert_called_once()

        # Verify settings were returned
        assert result is mock_settings

    @patch("src.entry.get_settings")
    @patch("src.entry.configure_logging")
    def test_initialize_with_token(self, mock_configure_logging: MagicMock, mock_get_settings: MagicMock) -> None:
        """Test environment initialization with token override."""
        # Mock settings
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        config = ServerConfig(token="custom_token")
        result = initialize_server_environment(config)

        # Verify settings were loaded with token
        call_kwargs = mock_get_settings.call_args[1]
        assert call_kwargs.get("api_token") == "custom_token"

        # Verify settings were returned
        assert result is mock_settings

    @patch("src.entry.get_settings")
    @patch("src.entry.configure_logging")
    def test_initialize_config_error(self, mock_configure_logging: MagicMock, mock_get_settings: MagicMock) -> None:
        """Test environment initialization with configuration error."""
        # Mock settings to raise an exception
        mock_get_settings.side_effect = Exception("Configuration error")

        config = ServerConfig()
        result = initialize_server_environment(config)

        # Verify logging was configured
        mock_configure_logging.assert_called_once()

        # Verify None was returned on error
        assert result is None


class TestRunStandaloneServer:
    """Test cases for the run_standalone_server function."""

    @patch("src.entry.initialize_server_environment")
    @patch("src.entry.mcp_factory")
    def test_run_sse_transport(self, mock_mcp_factory: MagicMock, mock_init_env: MagicMock) -> None:
        """Test running standalone server with SSE transport."""
        # Mock environment initialization
        mock_settings = MagicMock()
        mock_init_env.return_value = mock_settings

        # Mock MCP server
        mock_server = MagicMock()
        mock_mcp_factory.create.return_value = mock_server
        mock_mcp_factory.get.return_value = mock_server

        # Create config
        config = ServerConfig(transport=MCPTransportType.SSE)

        with patch("src.web_server.app.create_app") as mock_create_app, patch("src.entry.uvicorn.run") as mock_uvicorn:
            mock_app = MagicMock()
            mock_create_app.return_value = mock_app

            run_standalone_server(config)

            # Verify environment was initialized
            mock_init_env.assert_called_once_with(config)

            # Verify uvicorn was called
            mock_uvicorn.assert_called_once()

    @patch("src.entry.initialize_server_environment")
    def test_run_server_init_error(self, mock_init_env: MagicMock) -> None:
        """Test running server with initialization error."""
        # Mock environment initialization to return None
        mock_init_env.return_value = None

        config = ServerConfig()

        # Should not raise exception, should return early
        run_standalone_server(config)  # Should complete without error

        # Verify environment initialization was attempted
        mock_init_env.assert_called_once_with(config)


class TestRunIntegratedServer:
    """Test cases for the run_integrated_server function."""

    @patch("src.entry.initialize_server_environment")
    @patch("src.entry.integrated_factory")
    def test_run_integrated_success(self, mock_integrated_factory: MagicMock, mock_init_env: MagicMock) -> None:
        """Test running integrated server successfully."""
        # Mock environment initialization
        mock_settings = MagicMock()
        mock_settings.get_api_token.return_value = "test_token"
        mock_init_env.return_value = mock_settings

        # Mock integrated factory
        mock_app = MagicMock()
        mock_integrated_factory.create.return_value = mock_app

        # Create config
        config = ServerConfig(transport=MCPTransportType.SSE)

        with patch("src.entry.uvicorn.run") as mock_uvicorn:
            run_integrated_server(config)

            # Verify environment was initialized
            mock_init_env.assert_called_once_with(config)

            # Verify integrated server was created
            mock_integrated_factory.create.assert_called_once_with(
                token="test_token", mcp_transport=config.transport, mcp_mount_path="/mcp"
            )

            # Verify uvicorn was called
            mock_uvicorn.assert_called_once()

    @patch("src.entry.initialize_server_environment")
    def test_run_integrated_init_error(self, mock_init_env: MagicMock) -> None:
        """Test running integrated server with initialization error."""
        # Mock environment initialization to return None
        mock_init_env.return_value = None

        config = ServerConfig()

        # Should not raise exception, should return early
        run_integrated_server(config)  # Should complete without error

        # Verify environment initialization was attempted
        mock_init_env.assert_called_once_with(config)

    @patch("src.entry.initialize_server_environment")
    @patch("src.entry.integrated_factory")
    def test_run_integrated_invalid_transport(
        self, mock_integrated_factory: MagicMock, mock_init_env: MagicMock
    ) -> None:
        """Test running integrated server with invalid transport."""
        # Mock environment initialization
        mock_settings = MagicMock()
        mock_settings.get_api_token.return_value = "test_token"
        mock_init_env.return_value = mock_settings

        # Mock integrated factory to raise ValueError
        mock_integrated_factory.create.side_effect = ValueError("Invalid transport")

        config = ServerConfig(transport=MCPTransportType.SSE)

        # Should not raise exception, but should log error
        run_integrated_server(config)  # Should complete without error


class TestMain:
    """Test cases for the main function."""

    @patch("src.entry.run_integrated_server")
    @patch("src.entry.create_server_config")
    @patch("src.entry.parse_args")
    def test_main_integrated_mode(
        self, mock_parse_args: MagicMock, mock_create_server_config: MagicMock, mock_run_integrated_server: MagicMock
    ) -> None:
        """Test main function in integrated mode."""
        # Mock arguments
        mock_args = Namespace(integrated=True)
        mock_parse_args.return_value = mock_args

        # Mock config
        mock_config = MagicMock()
        mock_create_server_config.return_value = mock_config

        # Run main
        main()

        # Verify calls
        mock_parse_args.assert_called_once_with(None)
        mock_create_server_config.assert_called_once_with(mock_args)
        mock_run_integrated_server.assert_called_once_with(mock_config)

    @patch("src.entry.run_standalone_server")
    @patch("src.entry.create_server_config")
    @patch("src.entry.parse_args")
    def test_main_standalone_mode(
        self, mock_parse_args: MagicMock, mock_create_server_config: MagicMock, mock_run_standalone_server: MagicMock
    ) -> None:
        """Test main function in standalone mode."""
        # Mock arguments
        mock_args = Namespace(integrated=False)
        mock_parse_args.return_value = mock_args

        # Mock config
        mock_config = MagicMock()
        mock_create_server_config.return_value = mock_config

        # Run main
        main()

        # Verify calls
        mock_parse_args.assert_called_once_with(None)
        mock_create_server_config.assert_called_once_with(mock_args)
        mock_run_standalone_server.assert_called_once_with(mock_config)

    @patch("src.entry.run_standalone_server")
    @patch("src.entry.create_server_config")
    @patch("src.entry.parse_args")
    def test_main_with_argv(
        self, mock_parse_args: MagicMock, mock_create_server_config: MagicMock, mock_run_standalone_server: MagicMock
    ) -> None:
        """Test main function with custom argv."""
        # Mock arguments
        mock_args = Namespace(integrated=False)
        mock_parse_args.return_value = mock_args

        # Mock config
        mock_config = MagicMock()
        mock_create_server_config.return_value = mock_config

        # Run main with custom argv
        argv = ["--host", "127.0.0.1", "--port", "9000"]
        main(argv)

        # Verify parse_args was called with custom argv
        mock_parse_args.assert_called_once_with(argv)

    @patch("src.entry.create_server_config")
    @patch("src.entry.parse_args")
    def test_main_config_validation_error(
        self, mock_parse_args: MagicMock, mock_create_server_config: MagicMock
    ) -> None:
        """Test main function with configuration validation error."""
        # Mock arguments
        mock_args = Namespace(integrated=False)
        mock_parse_args.return_value = mock_args

        # Mock config validation error
        mock_create_server_config.side_effect = SystemExit(1)

        # Should exit with error code
        with pytest.raises(SystemExit):
            main()
