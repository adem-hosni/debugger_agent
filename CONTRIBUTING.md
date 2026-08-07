# Contributing to Debugger Agent

Thank you for your interest in contributing to Debugger Agent! This document provides guidelines and best practices for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/debugger_agent.git
   cd debugger_agent
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- C++ compiler (for memory_helper DLL)
- CMake 3.20+
- vcpkg (for Zydis dependency)

### Python Environment

```bash
cd agent
uv sync --extra dev
# or
pip install -e ".[dev]"
```

### Memory Helper (C++)

```bash
cd memory_helper
# Install vcpkg and Zydis
vcpkg install zydis:x64-windows
# Build with CMake
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=[vcpkg_root]/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
```

### Pre-commit Hooks

```bash
cd agent
pre-commit install
```

## Making Changes

### Branching Strategy

- `main` - Stable release branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring

### Guidelines

1. **Keep changes focused** - One feature/fix per PR
2. **Write tests** - Add tests for new functionality
3. **Update documentation** - Keep docs in sync with code
4. **Follow code style** - Run linting and formatting before committing

## Testing

### Running Tests

```bash
cd agent
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agent --cov-report=html

# Run specific test file
pytest tests/test_specific.py
```

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test fixtures and data
```

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Black-compatible** formatting (via Ruff)

### Running Checks

```bash
cd agent

# Format code
ruff format src/agent tests

# Lint code
ruff check src/agent tests

# Type check
mypy src/agent

# Run all checks
make check
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding/updating tests
- `chore` - Maintenance tasks

### Examples

```
feat(agent): add breakpoint management tool
fix(memory): handle null pointer in disassemble_region
docs: update README with new configuration options
test(cli): add tests for chat command
```

## Pull Request Process

1. **Ensure all checks pass**:
   - Tests pass
   - Linting passes
   - Type checking passes
   - Code is formatted

2. **Update documentation** if needed

3. **Add tests** for new functionality

4. **Write a clear PR description**:
   - What changes were made
   - Why the changes were needed
   - Any breaking changes
   - Screenshots (if UI changes)

5. **Request review** from maintainers

6. **Address feedback** promptly

### PR Checklist

- [ ] Tests pass
- [ ] Code formatted with Ruff
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)
- [ ] Commit messages follow convention

## Reporting Issues

### Bug Reports

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs/error messages

### Feature Requests

Use the feature request template and include:
- Clear description of the feature
- Use case/motivation
- Proposed implementation (if any)
- Alternatives considered

### Security Issues

**Do not** report security vulnerabilities in public issues. Email the maintainers directly.

## Getting Help

- Check existing [issues](https://github.com/your-username/debugger_agent/issues)
- Search [discussions](https://github.com/your-username/debugger_agent/discussions)
- Ask in a new discussion or issue

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- README.md contributors section
- Release notes

Thank you for contributing!