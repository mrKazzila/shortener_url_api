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



[group('Quality')]
[doc('Semgrep')]
semgrep:
    @echo "Running Semgrep..."
    @semgrep scan \
        --config=p/python \
        --config=.semgrep/project-rules.yml \
        --error \
        --quiet

[group('Quality')]
[doc('Semgrep with results.json')]
semgrep-save-results:
    @semgrep scan \
        --config=p/python \
        --config=p/fastapi \
        --config=p/flask \
        --config=.semgrep/project-rules.yml \
        --json \
        --output=semgrep-results.json