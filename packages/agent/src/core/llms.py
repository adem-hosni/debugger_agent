from typing import Any
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from config import get_settings
from config.settings import AgentConfig, ModelConfig, get_settings
from deepagents import create_deep_agent

from tools import get_orchestrator_tools, get_default_tools


def load_prompt(prompt_file: str) -> str | None:
    settings = get_settings()
    prompt_path = settings.prompts_dir / prompt_file
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return None


def build_model_kwargs(model_config: ModelConfig = ModelConfig()) -> dict[str, Any]:
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


def _build_orchestrator_llm() -> ChatOpenAI:
    load_dotenv()
    settings = get_settings()
    return ChatOpenAI(
        model=settings.model.provider_model,
        temperature=settings.model.temperature,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        streaming=True,
    )


tools = get_default_tools() + get_orchestrator_tools()
orchestrator_llm = _build_orchestrator_llm().bind_tools(tools)


def build_orchestrator_agent(
    name: str | None = None, system_prompt: str | None = load_prompt("system_prompt.md")
):
    return create_deep_agent(
        model=orchestrator_llm,
        tools=tools,
        name=name,
        system_prompt=system_prompt,
        memory=[]
    )


orchestrator_agent = build_orchestrator_agent("main-orchestrator")
