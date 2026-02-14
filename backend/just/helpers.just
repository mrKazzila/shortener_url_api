# Choose just command
[group('Help')]
choose:
    @if command -v fzf >/dev/null 2>&1; then \
        just --choose; \
    else \
        echo "[choose] fzf not installed"; \
        echo "[choose] Install: brew install fzf"; \
        exit 1; \
    fi

[group('Internal')]
[private]
_docker-ready:
  @if docker info >/dev/null 2>&1; then \
    echo "[infra] Docker daemon is reachable ✅"; \
    exit 0; \
  fi; \
  echo "[infra] Docker daemon is unavailable ❌"; \
  echo "[infra] Launch OrbStack.app or Docker Desktop and repeat."; \
  exit 1


[group('Internal')]
[private]
_net-create:
    @just _docker-ready
    @if docker network inspect global_net >/dev/null 2>&1; then \
        echo "[global_net] already exists — skipping"; \
    else \
        echo "[global_net] creating..."; \
        docker network create global_net >/dev/null && echo "[global_net] created"; \
    fi

[group('Internal')]
[private]
_pgbouncer-userlist-check:
    @if [ ! -f docker/compose/infra/pgbouncer/userlist.txt ]; then \
        echo "[pgbouncer] Missing docker/compose/infra/pgbouncer/userlist.txt"; \
        echo "[pgbouncer] Create it manually and fill it with user entries for pgbouncer"; \
        exit 1; \
    fi
    @echo "[pgbouncer] userlist.txt found — OK"
