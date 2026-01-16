# AGENTS.md

## Commands
- Build: `python -m build` or `poetry build` (for subprojects with pyproject.toml)
- Lint: `flake8 . --max-line-length=100` (E501 ignored)
- Test: `pytest` | Single test: `pytest path/to/test.py::test_name`
- TypeCheck: `python -m mypy --strict` (install mypy if needed)

## Code Style
- Imports: stdlib first, then third-party, then local (alphabetical within groups)
- Formatting: 4-space indent, 100-char line limit
- Types: Use type hints for function signatures and variables
- Naming: snake_case for functions/variables, PascalCase for classes, SCREAMING_SNAKE for constants
- Error handling: Use try/except with specific exceptions, always log errors
- Comments: Explain why, not what; no commented-out code
- Documentation: Use docstrings for all public functions/classes
- Testing: Aim for 80%+ coverage, use descriptive test names
