# Generating requirements.txt (dev)
[group('Requirements')]
req-dev:
    @echo "[req.txt] Generating requirements.txt (dev)..."
    @uv pip compile pyproject.toml --group dev -o requirements.txt

# Generating requirements.txt (prod)
[group('Requirements')]
req-prod:
    @echo "[req.txt] Generating requirements.txt (prod)..."
    @uv pip compile pyproject.toml -o requirements.txt

# Removing requirements.txt
[group('Requirements')]
req-clean:
    @echo "[req.txt] Removing requirements.txt..."
    rm -f requirements.txt
