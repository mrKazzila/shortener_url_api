# Ruff check(fix) and format
[group('Quality')]
ruff:
    @echo "[ruff] Running linters..."
    - ruff check --fix --silent .
    - ruff format --silent .

# Type checking (Pyright)
[group('Quality')]
pyright:
    uv run pyright
