# Integration tests for the agent package

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for the full agent pipeline."""

    @patch("agent.agents.factory.create_deep_agent")
    @patch("agent.agents.factory.get_settings")
    def test_full_agent_creation_pipeline(self, mock_get_settings, mock_create_deep_agent):
        """Test the complete agent creation flow."""
        from agent.agents.factory import create_agent_with_config
        from agent.tools.builtin import get_default_tools
        from agent.config.settings import AgentConfig, ModelConfig

        mock_settings = Mock()
        mock_settings.agent = AgentConfig()
        mock_settings.model = ModelConfig()
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        tools = get_default_tools()
        agent = create_agent_with_config(tools=tools)

        assert agent == mock_agent
        mock_create_deep_agent.assert_called_once()
        call_kwargs = mock_create_deep_agent.call_args.kwargs
        assert "tools" in call_kwargs
        assert len(call_kwargs["tools"]) == 1

    @patch("agent.cli.main.create_agent_with_config")
    @patch("agent.cli.main.get_default_tools")
    @patch("agent.cli.main.get_settings")
    def test_chat_command_flow(self, mock_get_settings, mock_get_default_tools, mock_create_agent):
        """Test the chat command execution flow."""
        from agent.cli.main import app
        from typer.testing import CliRunner

        mock_settings = Mock()
        mock_settings.agent.recursion_limit = 50
        mock_settings.model.provider_model = "openrouter:test/model"
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_agent.invoke.return_value = {
            "messages": [
                {"role": "user", "content": "Hello"},
                Mock(content="Hello! How can I help you?"),
            ]
        }
        mock_create_agent.return_value = mock_agent
        mock_get_default_tools.return_value = []

        runner = CliRunner()
        # We can't easily test interactive chat, but we can test the setup
        result = runner.invoke(app, ["chat", "--help"])

        assert result.exit_code == 0
        assert "interactive chat session" in result.output


@pytest.mark.integration
class TestSettingsIntegration:
    """Integration tests for settings loading."""

    def test_settings_load_from_env(self, tmp_path, monkeypatch):
        """Test settings load correctly from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OPENROUTER_API_KEY=integration-test-key
MODEL_PROVIDER_MODEL=openrouter:integration/model
MODEL_TEMPERATURE=0.3
AGENT_NAME=integration-agent
AGENT_DEBUG=true
""")

        monkeypatch.chdir(tmp_path)

        from agent.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()

        assert settings.openrouter_api_key == "integration-test-key"
        assert settings.model.provider_model == "openrouter:integration/model"
        assert settings.model.temperature == 0.3
        assert settings.agent.name == "integration-agent"
        assert settings.agent.debug is True
