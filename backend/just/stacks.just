# =====================
# Stacks: infra / app / monitoring
# =====================

[group('Infra')]
infra-up:
    @echo "[infra] Starting..."
    @just _net-create
    @just _pgbouncer-userlist-check
    {{INFRA}} up -d --build
    @echo "[infra] Started!"

[group('Infra')]
infra-down:
    @echo "[infra] Stopping (keeping volumes)..."
    {{INFRA}} down
    @echo "[infra] Stopped!"

[group('Infra')]
infra-clean:
    @echo "[infra] Stopping + removing volumes..."
    {{INFRA}} down -v
    @echo "[infra] Cleaned!"

[group('App')]
app-up:
    @echo "[app] Starting..."
    @just _net-create
    @just env-docker
    {{APP}} up -d --build
    @echo "[app] Started!"

[group('App')]
app-up-api:
    @echo "[app] Starting grpc only..."
    @just _net-create
    @just env-docker
    {{APP}} up -d grpc
    @echo "[app] grpc started!"

[group('App')]
app-rebuild:
    @just env-docker
    @just req-dev
    @echo "[app] Rebuilding fastapi + consumers..."
    {{APP}} up -d --build grpc consumer consumer-update  > /dev/null
    @just req-clean
    @echo "[app] Rebuilt."

[group('App')]
app-bootstrap partitions replicas:
    @echo "[app] Bootstrapping..."
    @just _net-create
    @just env-docker
    @just req-dev
    @just db-up
    @just kafka-topics {{partitions}}
    @just consumers-scale {{replicas}}
    @just app-up-api
    @just req-clean
    @echo "[app] Bootstrap completed."

[group('App')]
app-down:
    @echo "[app] Stopping (keeping volumes)..."
    {{APP}} down
    @echo "[app] Stopped!"

[group('App')]
app-clean:
    @echo "[app] Stopping + removing volumes..."
    {{APP}} down -v
    @echo "[app] Cleaned!"

[group('Monitoring')]
mon-up:
    @echo "[mon] Starting..."
    {{MON}} up -d --build
    @echo "[mon] Started!"

[group('Monitoring')]
mon-down:
    @echo "[mon] Stopping (keeping volumes)..."
    {{MON}} down
    @echo "[mon] Stopped!"

[group('Monitoring')]
mon-clean:
    @echo "[mon] Stopping + removing volumes..."
    {{MON}} down -v
    @echo "[mon] Cleaned!"
