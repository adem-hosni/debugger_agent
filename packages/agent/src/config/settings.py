from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_", extra="ignore")

    provider_model: str = Field(
        default="openrouter:deepseek/deepseek-chat-v3",
        description="Model identifier in provider:model format",
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)

    openrouter_app_url: str | None = Field(
        default=None, description="OpenRouter app URL for attribution"
    )
    openrouter_app_title: str | None = Field(
        default=None, description="OpenRouter app title for attribution"
    )


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", extra="ignore")

    name: str = Field(default="general-assistant")
    system_prompt_file: str = Field(default="system_prompt.md")
    enable_subagents: bool = Field(default=True)
    enable_filesystem: bool = Field(default=True)
    recursion_limit: int = Field(default=50, ge=1, le=200)
    debug: bool = Field(default=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key",
        validation_alias="OPENROUTER_API_KEY",
    )

    model: ModelConfig = Field(default_factory=ModelConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

    log_level: str = Field(default="INFO")
    data_dir: Path = Field(default=Path("./data"))

    @property
    def prompts_dir(self) -> Path:
        return Path(__file__).parent.parent / "prompts"


@lru_cache
def get_settings() -> Settings:
    return Settings()
