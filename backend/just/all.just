[group('All')]
all-up:
    @just infra-up
    @just app-up
    @just mon-up
    @echo "[all] up"

[group('All')]
all-down:
    @just mon-down
    @just app-down
    @just infra-down
    @echo "[all] down"
