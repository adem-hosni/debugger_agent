import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from agent.agents.factory import load_system_prompt, build_model_kwargs, create_agent
from agent.config.settings import ModelConfig, AgentConfig


class TestLoadSystemPrompt:
    """Tests for load_system_prompt function."""

    def test_loads_existing_file(self, tmp_path):
        prompt_file = tmp_path / "test_prompt.md"
        prompt_file.write_text("# Test Prompt\n\nYou are a test assistant.")

        with patch("agent.agents.factory.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.prompts_dir = tmp_path
            mock_get_settings.return_value = mock_settings

            result = load_system_prompt("test_prompt.md")
            assert result == "# Test Prompt\n\nYou are a test assistant."

    def test_returns_default_for_missing_file(self, tmp_path):
        with patch("agent.agents.factory.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.prompts_dir = tmp_path
            mock_get_settings.return_value = mock_settings

            result = load_system_prompt("nonexistent.md")
            assert result == "You are a helpful AI assistant."


class TestBuildModelKwargs:
    """Tests for build_model_kwargs function."""

    def test_basic_kwargs(self):
        config = ModelConfig(temperature=0.5)
        kwargs = build_model_kwargs(config)
        assert kwargs == {"temperature": 0.5}

    def test_with_max_tokens(self):
        config = ModelConfig(temperature=0.5, max_tokens=1000)
        kwargs = build_model_kwargs(config)
        assert kwargs == {"temperature": 0.5, "max_tokens": 1000}

    def test_with_top_p(self):
        config = ModelConfig(temperature=0.5, top_p=0.9)
        kwargs = build_model_kwargs(config)
        assert kwargs == {"temperature": 0.5, "top_p": 0.9}

    def test_with_openrouter_app_url(self):
        config = ModelConfig(temperature=0.5, openrouter_app_url="https://app.com")
        kwargs = build_model_kwargs(config)
        assert kwargs == {"temperature": 0.5, "app_url": "https://app.com"}

    def test_with_openrouter_app_title(self):
        config = ModelConfig(temperature=0.5, openrouter_app_title="My App")
        kwargs = build_model_kwargs(config)
        assert kwargs == {"temperature": 0.5, "app_title": "My App"}

    def test_all_options(self):
        config = ModelConfig(
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
            openrouter_app_url="https://app.com",
            openrouter_app_title="My App",
        )
        kwargs = build_model_kwargs(config)
        assert kwargs == {
            "temperature": 0.5,
            "max_tokens": 1000,
            "top_p": 0.9,
            "app_url": "https://app.com",
            "app_title": "My App",
        }


class TestCreateAgent:
    """Tests for create_agent function."""

    @patch("agent.agents.factory.create_deep_agent")
    @patch("agent.agents.factory.get_settings")
    def test_create_agent_with_defaults(self, mock_get_settings, mock_create_deep_agent):
        mock_settings = Mock()
        mock_settings.agent = AgentConfig()
        mock_settings.model = ModelConfig()
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        result = create_agent()

        assert result == mock_agent
        mock_create_deep_agent.assert_called_once()

    @patch("agent.agents.factory.create_deep_agent")
    @patch("agent.agents.factory.get_settings")
    def test_create_agent_with_custom_tools(self, mock_get_settings, mock_create_deep_agent):
        mock_settings = Mock()
        mock_settings.agent = AgentConfig()
        mock_settings.model = ModelConfig()
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        custom_tool = Mock()
        result = create_agent(tools=[custom_tool])

        assert result == mock_agent
        call_args = mock_create_deep_agent.call_args
        assert call_args.kwargs["tools"] == [custom_tool]

    @patch("agent.agents.factory.create_deep_agent")
    @patch("agent.agents.factory.get_settings")
    def test_create_agent_with_model_override(self, mock_get_settings, mock_create_deep_agent):
        mock_settings = Mock()
        mock_settings.agent = AgentConfig()
        mock_settings.model = ModelConfig()
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        result = create_agent(model_override="openrouter:custom/model")

        call_args = mock_create_deep_agent.call_args
        assert call_args.kwargs["model"] == "openrouter:custom/model"

    @patch("agent.agents.factory.create_deep_agent")
    @patch("agent.agents.factory.get_settings")
    def test_create_agent_with_system_prompt_override(
        self, mock_get_settings, mock_create_deep_agent
    ):
        mock_settings = Mock()
        mock_settings.agent = AgentConfig()
        mock_settings.model = ModelConfig()
        mock_get_settings.return_value = mock_settings

        mock_agent = Mock()
        mock_create_deep_agent.return_value = mock_agent

        result = create_agent(system_prompt_override="Custom prompt")

        call_args = mock_create_deep_agent.call_args
        assert call_args.kwargs["system_prompt"] == "Custom prompt"
