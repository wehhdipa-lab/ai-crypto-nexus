# Contributing to AI Crypto Nexus

Thank you for your interest in contributing! This document provides guidelines and steps for contributing.

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup
```bash
# Clone the repo
git clone https://github.com/your-org/ai-crypto-nexus.git
cd ai-crypto-nexus

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Copy env template
cp .env.example .env

# Start services
docker-compose up -d postgres redis

# Run tests
pytest tests/ -v
```

## Development Workflow

### Branch Naming
- `feature/<description>` — New features
- `fix/<description>` — Bug fixes
- `docs/<description>` — Documentation
- `refactor/<description>` — Code refactoring

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add whale tracking with ML anomaly detection
fix: correct impermanent loss calculation for multi-token pools
docs: update trading strategy documentation
refactor: extract risk management into separate module
```

### Code Standards
- **Type Hints**: All function signatures must have type hints
- **Docstrings**: Google-style docstrings for all public functions
- **Linting**: We use `ruff` for linting and formatting
- **Testing**: Minimum 80% coverage for new code
- **Async**: Use `async/await` for all I/O operations

### Running Checks
```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/nexus/

# Tests
pytest tests/ -v --cov=nexus --cov-report=html

# All checks
make check
```

## Security Guidelines

### Private Keys
- **NEVER** commit private keys, mnemonics, or keystore files
- Use environment variables or encrypted keystores
- All wallet operations must go through `nexus.utils.encryption`

### Smart Contract Interactions
- Always validate contract addresses against known registries
- Use checksummed addresses
- Implement slippage protection on all swaps
- Add deadline parameters to all transactions

### Reporting Vulnerabilities
For security issues, please email security@ai-crypto-nexus.dev instead of opening a public issue.

## Adding New Strategies

1. Create a new file in `src/nexus/trading/strategies/`
2. Inherit from `BaseStrategy`
3. Implement required methods: `generate_signals()`, `backtest()`, `get_params()`
4. Add unit tests in `tests/test_trading.py`
5. Document in `docs/trading.md`

## Adding New Agents

1. Create a new file in `src/nexus/agents/`
2. Inherit from `BaseAgent`
3. Implement required methods: `plan()`, `execute()`, `reflect()`
4. Register in the orchestrator's agent registry
5. Add integration tests in `tests/test_agents.py`

## Pull Request Process

1. Update documentation for any new features
2. Add tests for new functionality
3. Ensure all CI checks pass
4. Request review from at least one maintainer
5. Squash commits before merging

## Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please be respectful and inclusive in all interactions.
