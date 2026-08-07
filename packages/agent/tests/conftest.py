import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent.config.settings import ModelConfig, AgentConfig, Settings, get_settings
from agent.tools.builtin import calculate, get_default_tools
from agent.agents.factory import create_agent, load_system_prompt, build_model_kwargs


@pytest.fixture
def sample_env_file(tmp_path):
    """Create a temporary .env file for testing."""
    env_content = """
OPENROUTER_API_KEY=test-key-123
MODEL_PROVIDER_MODEL=openrouter:test/model
MODEL_TEMPERATURE=0.5
MODEL_MAX_TOKENS=1000
AGENT_NAME=test-agent
AGENT_DEBUG=true
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def mock_settings(monkeypatch, sample_env_file):
    """Create mock settings with test values."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
    monkeypatch.setenv("MODEL_PROVIDER_MODEL", "openrouter:test/model")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.5")
    monkeypatch.setenv("MODEL_MAX_TOKENS", "1000")
    monkeypatch.setenv("AGENT_NAME", "test-agent")
    monkeypatch.setenv("AGENT_DEBUG", "true")

    # Clear the cache
    get_settings.cache_clear()
    return get_settings()
