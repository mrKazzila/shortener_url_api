[group('Quality')]
[doc('Ruff check(fix) and format')]
ruff:
    @echo "[ruff] Running linters..."
    - ruff check --fix --silent .
    - ruff format --silent .

[group('Quality')]
[doc('Type checking (ty by astral)')]
ty:
    uv run ty check src tests

[group('Quality')]
[doc('Import linter (check CA)')]
import-linter:
    uv run lint-imports
