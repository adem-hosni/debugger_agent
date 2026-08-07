from typing import Any

from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from packages.agent.src.config.settings import AgentConfig, ModelConfig, get_settings


def load_system_prompt(prompt_file: str) -> str:
    settings = get_settings()
    prompt_path = settings.prompts_dir / prompt_file
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "You are a helpful AI assistant."


def build_model_kwargs(model_config: ModelConfig) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "temperature": model_config.temperature,
    }
    if model_config.max_tokens is not None:
        kwargs["max_tokens"] = model_config.max_tokens
    if model_config.top_p is not None:
        kwargs["top_p"] = model_config.top_p
    if model_config.openrouter_app_url:
        kwargs["app_url"] = model_config.openrouter_app_url
    if model_config.openrouter_app_title:
        kwargs["app_title"] = model_config.openrouter_app_title
    return kwargs


def create_agent(
    tools: list[BaseTool] | None = None,
    model_override: str | BaseChatModel | None = None,
    system_prompt_override: str | None = None,
    agent_config_override: AgentConfig | None = None,
    model_config_override: ModelConfig | None = None,
) -> Any:
    settings = get_settings()
    agent_config = agent_config_override or settings.agent
    model_config = model_config_override or settings.model

    system_prompt = system_prompt_override or load_system_prompt(agent_config.system_prompt_file)

    model = model_override or model_config.provider_model

    agent = create_deep_agent(
        model=model,
        tools=tools or [],
        system_prompt=system_prompt,
        name=agent_config.name,
        debug=agent_config.debug,
    )

    return agent


def create_agent_with_config(
    tools: list[BaseTool] | None = None,
    **overrides: Any,
) -> Any:
    settings = get_settings()
    agent_overrides = overrides.get("agent_config", {})
    model_overrides = overrides.get("model_config", {})
    agent_config = AgentConfig(**{**settings.agent.model_dump(), **agent_overrides})
    model_config = ModelConfig(**{**settings.model.model_dump(), **model_overrides})

    return create_agent(
        tools=tools,
        model_override=overrides.get("model"),
        system_prompt_override=overrides.get("system_prompt"),
        agent_config_override=agent_config,
        model_config_override=model_config,
    )
    model_config = ModelConfig(
        **{**settings.model.model_dump(), **overrides.get("model_config", {})}
    )

    return create_agent(
        tools=tools,
        model_override=overrides.get("model"),
        system_prompt_override=overrides.get("system_prompt"),
        agent_config_override=agent_config,
        model_config_override=model_config,
    )
