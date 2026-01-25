# =====================
# Stacks: infra / app / monitoring
# =====================

# Build and up infra
[group('Infra')]
infra-up:
    @echo "[infra] Starting..."
    @just _net-create
    @just _pgbouncer-userlist-check
    {{INFRA}} up -d --build
    @echo "[infra] Started!"

# Stop infra (keeping volumes)
[group('Infra')]
infra-down:
    @echo "[infra] Stopping (keeping volumes)..."
    {{INFRA}} down
    @echo "[infra] Stopped!"

# Stop infra + removing volumes
[group('Infra')]
infra-clean:
    @echo "[infra] Stopping + removing volumes..."
    {{INFRA}} down -v
    @echo "[infra] Cleaned!"

# Build and up application with consumers
[group('App')]
app-up:
    @echo "[app] Starting..."
    @just _net-create
    @just env-docker
    {{APP}} up -d --build
    @echo "[app] Started!"

# Build and up only app
[group('App')]
app-up-api:
    @echo "[app] Starting grpc only..."
    @just _net-create
    @just env-docker
    {{APP}} up -d grpc
    @echo "[app] grpc started!"

# Rebuildy app and consumers
[group('App')]
app-rebuild:
    @just env-docker
    @just req-dev
    @echo "[app] Rebuilding fastapi + consumers..."
    {{APP}} up -d --build grpc consumer consumer-update  > /dev/null
    @just req-clean
    @echo "[app] Rebuilt."

# Bootstrap application
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

# Stop application (keeping volumes)
[group('App')]
app-down:
    @echo "[app] Stopping (keeping volumes)..."
    {{APP}} down
    @echo "[app] Stopped!"

# Stop application + removing volumes
[group('App')]
app-clean:
    @echo "[app] Stopping + removing volumes..."
    {{APP}} down -v
    @echo "[app] Cleaned!"

# Build and up monitoring
[group('Monitoring')]
mon-up:
    @echo "[mon] Starting..."
    {{MON}} up -d --build
    @echo "[mon] Started!"

# Stop monitoring (keeping volumes)
[group('Monitoring')]
mon-down:
    @echo "[mon] Stopping (keeping volumes)..."
    {{MON}} down
    @echo "[mon] Stopped!"

# Stop monitoring + removing volumes
[group('Monitoring')]
mon-clean:
    @echo "[mon] Stopping + removing volumes..."
    {{MON}} down -v
    @echo "[mon] Cleaned!"
