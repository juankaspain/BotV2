# Contributing to BotV2

First off, thank you for considering contributing to BotV2! It's people like you that make BotV2 such a great tool for algorithmic trading.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- Virtual environment (recommended)
- PostgreSQL (optional, for production)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/BotV2.git
   cd BotV2
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/juankaspain/BotV2.git
   ```

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Logs or screenshots** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Clear title** describing the suggestion
- **Detailed description** of the proposed functionality
- **Use case** explaining why this would be useful
- **Possible implementation** approach (optional)

### Adding New Trading Strategies

New strategies are welcome! Please ensure:

1. Strategy follows the base `Strategy` class interface
2. Includes comprehensive unit tests
3. Has proper documentation
4. Backtesting results are provided
5. Risk parameters are clearly defined

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Run tests to verify setup
pytest tests/ -v
```

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Update README.md for significant changes
- Add inline comments for complex logic

### Example

```python
def calculate_position_size(
    capital: float,
    risk_per_trade: float,
    stop_loss_pct: float
) -> float:
    """Calculate optimal position size based on risk parameters.
    
    Args:
        capital: Available trading capital in base currency.
        risk_per_trade: Maximum risk per trade as decimal (e.g., 0.02 for 2%).
        stop_loss_pct: Stop loss percentage as decimal.
        
    Returns:
        Optimal position size in base currency.
        
    Raises:
        ValueError: If any parameter is negative or zero.
    """
    if capital <= 0 or risk_per_trade <= 0 or stop_loss_pct <= 0:
        raise ValueError("All parameters must be positive")
    
    return (capital * risk_per_trade) / stop_loss_pct
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `perf` | Performance improvements |
| `chore` | Maintenance tasks |

### Examples

```
feat(strategies): add Ichimoku cloud strategy
fix(risk): correct Kelly criterion calculation
docs(readme): update installation instructions
test(backtesting): add slippage simulation tests
```

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following our style guidelines

4. **Run tests**:
   ```bash
   pytest tests/ -v --cov=bot
   ```

5. **Run linting**:
   ```bash
   flake8 bot/ dashboard/
   mypy bot/ --ignore-missing-imports
   ```

### Submitting

1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request against `main` branch

3. Fill out the PR template completely

4. Wait for review and address feedback

### PR Requirements

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Code coverage maintained (>90%)
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Conventional commit messages
- [ ] PR description explains changes

## Questions?

Feel free to open a [Discussion](https://github.com/juankaspain/BotV2/discussions) for questions or ideas!

---

Thank you for contributing to BotV2!
