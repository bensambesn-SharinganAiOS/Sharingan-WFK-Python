# AGENTS.md

## Build/Lint/Test Commands
```bash
python -m build                    # Build package
pytest                             # Run all tests
pytest path/to/test.py::test_name  # Run single test
flake8 . --max-line-length=100     # Linting
python -m mypy --strict            # Type checking
```

## Code Style
- Imports: stdlib first, then third-party, then local (alphabetical)
- Formatting: 4-space indent, 100-char line limit
- Types: Use type hints for all functions/variables
- Naming: snake_case (vars/funcs), PascalCase (classes), SCREAMING_SNAKE (constants)
- Error handling: try/except with specific exceptions, always log errors
- Documentation: docstrings for all public functions/classes
- Logging: `logging.getLogger("sharingan.module_name")` with INFO/WARNING/ERROR

## Security
- Never generate malicious/exploitation code without real implementation
- Never hardcode secrets; use environment variables
- Validate with check_obligations.py before committing
