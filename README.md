# Debugger Agent

[![CI](https://github.com/hosni/debugger_agent/workflows/CI/badge.svg)](https://github.com/hosni/debugger_agent/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: MyPy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A professional debugging agent for reverse engineering & debugging softwares in realtime, built with DeepAgents and OpenRouter. Features a Python AI agent with C++ memory helper for process debugging and disassembly.

> DISCLAIMER: This repository is made for only educational purposes.

## Architecture

```
debugger_agent/
├── packages/
│   ├── agent/           # Python AI agent (DeepAgents + OpenRouter)
│   └── memory_helper/   # C++ memory debugging library
├── .github/workflows/   # CI/CD pipelines
├── tests/               # Integration tests
└── docs/                # Documentation
```

## Components

### Python Agent (`packages/agent`)
- **DeepAgents Integration**: Full planning, subagent, and filesystem capabilities
- **OpenRouter Support**: Access 100+ models through a unified API
- **CLI Interface**: Interactive chat and single-prompt execution
- **Configuration Management**: Environment-based settings with validation
- **Extensible Tools**: Easy to add custom debugging tools

### C++ Memory Helper (`packages/memory_helper`)
- Process attachment and memory region enumeration
- Disassembly using Zydis library
- Multi-threaded region processing
- JSON output for analysis

## Quick Start

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- C++ compiler (for memory_helper)
- CMake 3.20+
- vcpkg (for Zydis dependency)

### Installation

```bash
# Clone the repository
git clone https://github.com/hosni/debugger_agent.git
cd debugger_agent

# Install Python agent dependencies
cd packages/agent
uv sync --extra dev
# or
pip install -e ".[dev]"

# Build C++ memory helper (Windows)
cd ../memory_helper
vcpkg install zydis:x64-windows
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=[vcpkg_root]/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
```

### Configuration

```bash
cd packages/agent
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

### Usage

```bash
# Interactive chat
cd packages/agent
python -m agent chat

# Single prompt
python -m agent run "Analyze this crackme..."

# Show configuration
python -m agent config
```

## Development

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration

# Run with coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Type check
make typecheck

# Run all checks
make check

# Build C++ component
make build-cpp

# Build Python package
make build
```

## Project Structure

```
debugger_agent/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/      # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── packages/
│   ├── agent/
│   │   ├── src/agent/       # Source code
│   │   ├── tests/           # Test suite
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── memory_helper/
│       ├── src/             # C++ source
│       ├── build/           # Build output
│       └── CMakeLists.txt
├── docs/                    # Documentation
├── .editorconfig
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Development setup
- Code style
- Commit messages
- Pull request process
- Reporting issues

## License

MIT License - see [LICENSE](LICENSE) for details.
