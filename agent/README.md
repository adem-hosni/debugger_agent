# DeepAgents AI Assistant

A professional AI assistant built with [DeepAgents](https://github.com/langchain-ai/deepagents) and [OpenRouter](https://openrouter.ai/), featuring a clean CLI interface and extensible architecture.

## Features

- **DeepAgents Integration**: Full planning, subagent, and filesystem capabilities
- **OpenRouter Support**: Access 100+ models through a unified API
- **Professional Structure**: Modular, typed, and well-organized codebase
- **CLI Interface**: Interactive chat and single-prompt execution
- **Configuration Management**: Environment-based settings with validation
- **Extensible Tools**: Easy to add custom tools and capabilities

## Quick Start

### Installation

```bash
# Install dependencies
pip install -e ".[dev]"

# Or with uv (recommended)
uv sync --extra dev
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your OpenRouter API key to `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxx
```

3. (Optional) Customize the model:
```bash
MODEL_PROVIDER_MODEL=openrouter:deepseek/deepseek-chat-v3
```

### Usage

**Interactive chat:**
```bash
python -m agent chat
```

**Single prompt:**
```bash
python -m agent run "Explain quantum computing in simple terms"
```

**With custom model:**
```bash
python -m agent chat --model openrouter:anthropic/claude-sonnet-4
```

**Show configuration:**
```bash
python -m agent config
```

## Commands

| Command | Description |
|---------|-------------|
| `chat` | Start interactive chat session |
| `run` | Execute single prompt and exit |
| `config` | Display current configuration |

### Chat Session Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `exit` / `quit` | Exit the session |
| `clear` | Clear conversation history |
| `model` | Show current model |
| `tools` | List available tools |

## Project Structure

```
src/agent/
├── agents/
│   ├── __init__.py
│   └── factory.py          # Agent creation logic
├── cli/
│   ├── __init__.py
│   └── main.py             # CLI commands (Typer + Rich)
├── config/
│   ├── __init__.py
│   └── settings.py         # Pydantic settings management
├── prompts/
│   └── system_prompt.md    # System prompt template
├── tools/
│   ├── __init__.py
│   └── builtin.py          # Built-in tools
├── __init__.py
main.py                     # Entry point
```

## Adding Custom Tools

Create a new tool in `src/agent/tools/custom.py`:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what this tool does."""
    return f"Result: {param}"
```

Then register it in `factory.py` or pass it directly:

```python
from agent.tools.custom import my_custom_tool
from agent.agents.factory import create_agent_with_config

agent = create_agent_with_config(tools=[my_custom_tool] + get_default_tools())
```

## Changing the System Prompt

Edit `src/agent/prompts/system_prompt.md` or pass a custom file:

```bash
python -m agent chat --prompt ./my_prompt.md
```

## Model Selection

Use any OpenRouter model in `provider:model` format:

- `openrouter:deepseek/deepseek-chat-v3` (default)
- `openrouter:anthropic/claude-sonnet-4`
- `openrouter:openai/gpt-5.5`
- `openrouter:google/gemini-2.5-pro`
- `openrouter:meta-llama/llama-4-scout`
- And 100+ more at [openrouter.ai/models](https://openrouter.ai/models)

## Development

```bash
# Run tests
pytest

# Type check
mypy src/agent

# Lint
ruff check src/agent

# Format
ruff format src/agent
```

## Requirements

- Python 3.13+
- OpenRouter API key

## License

MIT