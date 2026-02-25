[group('Convenience')]
[doc('Run redis-cli in docker')]
redis-cli:
    @echo "[redis] Connecting..."
    {{INFRA}} exec redis redis-cli
