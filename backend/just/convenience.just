[group('Convenience')]
redis-cli:
    @echo "[redis] Connecting..."
    {{INFRA}} exec redis redis-cli
