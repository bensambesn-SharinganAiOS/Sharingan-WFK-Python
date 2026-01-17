# AGENTS.md

## Build/Lint/Test
```bash
pip install pytest flake8 mypy bandit pytest-mock pytest-cov  # Install dev tools
pytest tests/ -v --tb=short                                 # Run all tests
pytest tests/unit/test_core.py::TestCapabilityAssessment::test_assessment_returns_dict  # Single test
flake8 . --max-line-length=100 --ignore=E501               # Linting
mypy sharingan_app/ --ignore-missing-imports               # Type checking
bandit -r sharingan_app/ -f txt -q                          # Security scan
```

## Code Style
- **Imports**: stdlib → third-party → local (alphabetical order), docstrings required for public functions
- **Formatting**: 4-space indent, 100-char limit, type hints mandatory, no trailing whitespace
- **Naming**: snake_case (vars/funcs), PascalCase (classes), SCREAMING_SNAKE (constants)
- **Error handling**: try/except with specific exceptions, log with sharingan.module_name logger
- **Logging**: INFO/WARNING/ERROR levels, use logging.getLogger("sharingan.module_name")

## Project Context
- **Sharingan OS**: AI-Powered Cybersecurity Operating System (Python 3.10+)
- **Stack**: AI (tgpt, MiniMax, GLM-4), Memory, Security (Kali Tools), Web (Flask/FastAPI)
- **Structure**: sharingan_app/_internal/ (core/, tools/, data/, tests/)

## Security & Validation
- Never generate malicious/exploitation code; avoid fake/demonstration implementations
- Never hardcode secrets/tokens; use environment variables or config files
- Validate code with check_obligations.py before committing; never commit secrets
- Use dangerous mode only when explicitly approved: export SHARINGAN_DANGEROUS_MODE=true
