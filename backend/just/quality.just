[group('Quality')]
lint:
    @echo "[ruff] Running linters..."
    - ruff check --fix --silent .
    - ruff format --silent .
