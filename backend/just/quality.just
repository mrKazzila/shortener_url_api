# Ruff check(fix) and format
[group('Quality')]
ruff:
    @echo "[ruff] Running linters..."
    - ruff check --fix --silent .
    - ruff format --silent .

# Type checking (Pyright)
[group('Quality')]
pyright:
    @uv run pyright

# Type checking (ty by astral)
[group('Quality')]
ty:
    uv run ty check src tests

# Import linter (check CA)
[group('Quality')]
import-linter:
    uv run lint-imports
