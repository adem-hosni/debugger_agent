import pytest
from pathlib import Path
from pydantic import ValidationError

from agent.config.settings import ModelConfig, AgentConfig, Settings


class TestModelConfig:
    """Tests for ModelConfig class."""

    def test_default_values(self):
        config = ModelConfig()
        assert config.provider_model == "openrouter:deepseek/deepseek-chat-v3"
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.top_p is None
        assert config.openrouter_app_url is None
        assert config.openrouter_app_title is None

    def test_custom_values(self):
        config = ModelConfig(
            provider_model="openrouter:anthropic/claude-3",
            temperature=0.5,
            max_tokens=2000,
            top_p=0.9,
            openrouter_app_url="https://example.com",
            openrouter_app_title="Test App",
        )
        assert config.provider_model == "openrouter:anthropic/claude-3"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.top_p == 0.9
        assert config.openrouter_app_url == "https://example.com"
        assert config.openrouter_app_title == "Test App"

    def test_temperature_validation(self):
        with pytest.raises(ValidationError):
            ModelConfig(temperature=-0.1)
        with pytest.raises(ValidationError):
            ModelConfig(temperature=2.1)

    def test_max_tokens_validation(self):
        with pytest.raises(ValidationError):
            ModelConfig(max_tokens=0)
        with pytest.raises(ValidationError):
            ModelConfig(max_tokens=-1)

    def test_top_p_validation(self):
        with pytest.raises(ValidationError):
            ModelConfig(top_p=-0.1)
        with pytest.raises(ValidationError):
            ModelConfig(top_p=1.1)


class TestAgentConfig:
    """Tests for AgentConfig class."""

    def test_default_values(self):
        config = AgentConfig()
        assert config.name == "general-assistant"
        assert config.system_prompt_file == "system_prompt.md"
        assert config.enable_subagents is True
        assert config.enable_filesystem is True
        assert config.recursion_limit == 50
        assert config.debug is False

    def test_custom_values(self):
        config = AgentConfig(
            name="custom-agent",
            system_prompt_file="custom_prompt.md",
            enable_subagents=False,
            enable_filesystem=False,
            recursion_limit=100,
            debug=True,
        )
        assert config.name == "custom-agent"
        assert config.system_prompt_file == "custom_prompt.md"
        assert config.enable_subagents is False
        assert config.enable_filesystem is False
        assert config.recursion_limit == 100
        assert config.debug is True

    def test_recursion_limit_validation(self):
        with pytest.raises(ValidationError):
            AgentConfig(recursion_limit=0)
        with pytest.raises(ValidationError):
            AgentConfig(recursion_limit=201)


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        settings = Settings(openrouter_api_key="test-key")
        assert settings.openrouter_api_key == "test-key"
        assert isinstance(settings.model, ModelConfig)
        assert isinstance(settings.agent, AgentConfig)
        assert settings.log_level == "INFO"
        assert settings.data_dir == Path("./data")

    def test_prompts_dir_property(self):
        settings = Settings(openrouter_api_key="test-key")
        prompts_dir = settings.prompts_dir
        assert prompts_dir.name == "prompts"
        assert prompts_dir.parent.name == "config"

    def test_env_file_loading(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("OPENROUTER_API_KEY=from-env-file\n")

        monkeypatch.chdir(tmp_path)
        settings = Settings()
        assert settings.openrouter_api_key == "from-env-file"
