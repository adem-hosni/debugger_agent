import pytest
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from agent.cli.main import app, _build_overrides, _get_last_message_content, _print_response


class TestBuildOverrides:
    """Tests for _build_overrides function."""

    def test_empty_overrides(self):
        overrides = _build_overrides(None, None, False)
        assert overrides == {}

    def test_model_override(self):
        overrides = _build_overrides("openrouter:custom/model", None, False)
        assert overrides == {"model": "openrouter:custom/model"}

    def test_prompt_file_override(self, tmp_path):
        prompt_file = tmp_path / "custom_prompt.md"
        prompt_file.write_text("Custom system prompt")

        overrides = _build_overrides(None, str(prompt_file), False)
        assert overrides == {"system_prompt": "Custom system prompt"}

    def test_prompt_file_not_found(self):
        with pytest.raises(SystemExit):
            _build_overrides(None, "nonexistent.md", False)

    def test_debug_override(self):
        overrides = _build_overrides(None, None, True)
        assert overrides == {"agent_config": {"debug": True}}

    def test_combined_overrides(self, tmp_path):
        prompt_file = tmp_path / "custom_prompt.md"
        prompt_file.write_text("Custom prompt")

        overrides = _build_overrides("openrouter:custom/model", str(prompt_file), True)
        assert overrides == {
            "model": "openrouter:custom/model",
            "system_prompt": "Custom prompt",
            "agent_config": {"debug": True},
        }


class TestGetLastMessageContent:
    """Tests for _get_last_message_content function."""

    def test_with_messages_list(self):
        mock_msg = Mock()
        mock_msg.content = "Test response"
        result = {"messages": [mock_msg]}

        content = _get_last_message_content(result)
        assert content == "Test response"

    def test_with_dict_message(self):
        result = {"messages": [{"role": "assistant", "content": "Dict response"}]}

        content = _get_last_message_content(result)
        assert content == "Dict response"

    def test_with_string_message(self):
        result = {"messages": ["String response"]}

        content = _get_last_message_content(result)
        assert content == "String response"

    def test_empty_messages(self):
        result = {"messages": []}

        content = _get_last_message_content(result)
        assert content is None

    def test_no_messages_key(self):
        result = {}

        content = _get_last_message_content(result)
        assert content is None


class TestCLICommands:
    """Tests for CLI commands using CliRunner."""

    @patch("agent.cli.main.create_agent_with_config")
    @patch("agent.cli.main.get_default_tools")
    @patch("agent.cli.main.get_settings")
    def test_config_command(self, mock_get_settings, mock_get_default_tools, mock_create_agent):
        mock_settings = Mock()
        mock_settings.model.provider_model = "openrouter:test/model"
        mock_settings.model.temperature = 0.7
        mock_settings.model.max_tokens = None
        mock_settings.agent.name = "test-agent"
        mock_settings.agent.debug = False
        mock_settings.agent.recursion_limit = 50
        mock_get_settings.return_value = mock_settings

        runner = CliRunner()
        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "Configuration" in result.output
        assert "openrouter:test/model" in result.output
        assert "test-agent" in result.output

    @patch("agent.cli.main.create_agent_with_config")
    @patch("agent.cli.main.get_default_tools")
    @patch("agent.cli.main.get_settings")
    def test_run_command(self, mock_get_settings, mock_get_default_tools, mock_create_agent):
        mock_settings = Mock()
        mock_settings.agent.recursion_limit = 50
        mock_settings.model.provider_model = "openrouter:test/model"
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_agent.invoke.return_value = {"messages": [Mock(content="Test response")]}
        mock_create_agent.return_value = mock_agent
        mock_get_default_tools.return_value = []

        runner = CliRunner()
        result = runner.invoke(app, ["run", "Test prompt"])

        assert result.exit_code == 0
        assert "Test response" in result.output

    def test_help_command(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "DeepAgents AI Assistant" in result.output
        assert "chat" in result.output
        assert "run" in result.output
        assert "config" in result.output
