from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from agent.agents.factory import create_agent_with_config
from agent.config.settings import get_settings
from agent.tools.builtin import get_default_tools

app = typer.Typer(
    name="agent",
    help="DeepAgents-based AI Assistant with OpenRouter",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _build_overrides(
    model: str | None,
    prompt_file: str | None,
    debug: bool,
) -> dict[str, Any]:
    overrides = {}
    if model:
        overrides["model"] = model
    if prompt_file:
        prompt_path = Path(prompt_file)
        if prompt_path.exists():
            overrides["system_prompt"] = prompt_path.read_text(encoding="utf-8")
        else:
            console.print(f"[red]Prompt file not found: {prompt_file}[/red]")
            raise typer.Exit(1)
    if debug:
        overrides.setdefault("agent_config", {})["debug"] = True
    return overrides


def _get_last_message_content(result: dict[str, Any]) -> str | None:
    messages = result.get("messages")
    if not messages:
        return None
    last_msg = messages[-1]
    if hasattr(last_msg, "content"):
        return last_msg.content
    if isinstance(last_msg, dict):
        return last_msg.get("content", "")
    return str(last_msg)


def _print_response(content: str) -> None:
    if content:
        console.print()
        console.print(Markdown(content))
        console.print()


def print_welcome() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]DeepAgents AI Assistant[/bold cyan]\n[dim]Powered by OpenRouter[/dim]",
            border_style="cyan",
        )
    )
    console.print("Type 'exit' or 'quit' to leave. Type 'help' for commands.\n")


def print_help() -> None:
    console.print(
        Panel(
            "[bold]Commands:[/bold]\n"
            "  [cyan]help[/cyan]     - Show this help\n"
            "  [cyan]exit[/cyan]     - Exit the assistant\n"
            "  [cyan]clear[/cyan]    - Clear conversation history\n"
            "  [cyan]model[/cyan]    - Show current model\n"
            "  [cyan]tools[/cyan]    - List available tools\n",
            title="Help",
            border_style="green",
        )
    )


def _handle_chat_commands(
    user_input: str,
    model: str | None,
    settings: Any,
    state: dict[str, Any],
    tools: list[Any],
) -> tuple[bool, dict[str, Any]]:
    if user_input.lower() in ("exit", "quit"):
        console.print("[yellow]Goodbye![/yellow]")
        return True, state
    if user_input.lower() == "help":
        print_help()
        return False, state
    if user_input.lower() == "clear":
        return False, {"messages": []}
    if user_input.lower() == "model":
        console.print(f"[dim]Current model: {model or settings.model.provider_model}[/dim]")
        return False, state
    if user_input.lower() == "tools":
        console.print("[dim]Available tools:[/dim]")
        for tool in tools:
            console.print(f"  - {tool.name}: {tool.description}")
        return False, state
    return False, state


@app.command()
def chat(
    model: str | None = typer.Option(
        None, "--model", "-m", help="Override model (provider:model format)"
    ),
    prompt_file: str | None = typer.Option(
        None, "--prompt", "-p", help="Custom system prompt file"
    ),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
) -> None:
    """Start an interactive chat session with the agent."""
    settings = get_settings()
    overrides = _build_overrides(model, prompt_file, debug)
    agent = create_agent_with_config(tools=get_default_tools(), **overrides)

    print_welcome()
    console.print(f"[dim]Model: {model or settings.model.provider_model}[/dim]\n")

    config = {"recursion_limit": settings.agent.recursion_limit}
    state = {"messages": []}
    tools = get_default_tools()

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not user_input:
            continue

        should_exit, state = _handle_chat_commands(user_input, model, settings, state, tools)
        if should_exit:
            break
        if user_input.lower() in ("help", "clear", "model", "tools"):
            continue

        state["messages"].append({"role": "user", "content": user_input})

        try:
            with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
                result = agent.invoke(state, config=config)

            content = _get_last_message_content(result)
            _print_response(content)

            state = result

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            if debug:
                import traceback

                console.print(traceback.format_exc())


@app.command()
def run(
    prompt: str = typer.Argument(..., help="Single prompt to execute"),
    model: str | None = typer.Option(None, "--model", "-m"),
    prompt_file: str | None = typer.Option(None, "--prompt", "-p"),
    debug: bool = typer.Option(False, "--debug", "-d"),
) -> None:
    """Run a single prompt and exit."""
    settings = get_settings()
    overrides = _build_overrides(model, prompt_file, debug)
    agent = create_agent_with_config(tools=get_default_tools(), **overrides)

    config = {"recursion_limit": settings.agent.recursion_limit}
    state = {"messages": [{"role": "user", "content": prompt}]}

    try:
        with console.status("[bold cyan]Processing...[/bold cyan]", spinner="dots"):
            result = agent.invoke(state, config=config)

        content = _get_last_message_content(result)
        if content:
            console.print(Markdown(content))

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if debug:
            import traceback

            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def config() -> None:
    """Show current configuration."""
    settings = get_settings()
    console.print(
        Panel.fit(
            f"[bold]Model:[/bold] {settings.model.provider_model}\n"
            f"[bold]Temperature:[/bold] {settings.model.temperature}\n"
            f"[bold]Max Tokens:[/bold] {settings.model.max_tokens or 'unset'}\n"
            f"[bold]Agent Name:[/bold] {settings.agent.name}\n"
            f"[bold]Debug:[/bold] {settings.agent.debug}\n"
            f"[bold]Recursion Limit:[/bold] {settings.agent.recursion_limit}",
            title="Configuration",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    app()
