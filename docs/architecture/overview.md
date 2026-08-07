# System Overview

## High-Level Architecture

The Debugger Agent consists of two main components:

1. **Python Agent** (`packages/agent`) - AI-powered reverse engineering assistant
2. **C++ Memory Helper** (`packages/memory_helper`) - Low-level process debugging library

## Component Interaction

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   User/CLI      │────▶│   Python Agent   │────▶│  C++ Memory Helper  │
│   (Typer/Rich)  │     │  (DeepAgents)    │     │  (Zydis/ctypes)     │
└─────────────────┘     └──────────────────┘     └─────────────────────┘
                                │                         │
                                ▼                         ▼
                        ┌──────────────────┐     ┌─────────────────────┐
                        │  OpenRouter API  │     │  Target Process     │
                        │  (LLM Models)    │     │  (crackme.exe)      │
                        └──────────────────┘     └─────────────────────┘
```

## Data Flow

1. User provides crackme analysis request via CLI
2. Python Agent processes request using DeepAgents framework
3. Agent may invoke tools (calculate, custom debugging tools)
4. For memory analysis, agent calls C++ Memory Helper via ctypes
5. Memory Helper attaches to target process, enumerates regions, disassembles
6. Results returned to agent for analysis
7. Agent provides response to user

## Technology Stack

### Python Agent
- **DeepAgents** - Agent framework with planning and subagents
- **LangChain** - LLM orchestration
- **OpenRouter** - Unified API for 100+ models
- **Pydantic Settings** - Configuration management
- **Typer + Rich** - CLI interface
- **Ruff + MyPy** - Code quality

### C++ Memory Helper
- **Zydis** - x86/x86-64 disassembler
- **CMake** - Build system
- **vcpkg** - Dependency management
- **ctypes** - Python interop

## Security Considerations

- Process attachment requires appropriate permissions
- Memory reading limited to accessible regions
- No code injection or modification
- Output sanitized before LLM processing