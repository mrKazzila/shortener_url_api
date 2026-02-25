[group('Infra')]
[doc('Build and up infra')]
infra-up:
    @echo "[infra] Starting..."
    @just _net-create
    @just _pgbouncer-userlist-check
    {{INFRA}} up -d --build
    @echo "[infra] Started!"

[group('Infra')]
[doc('Stop infra (keeping volumes)')]
infra-down:
    @echo "[infra] Stopping (keeping volumes)..."
    {{INFRA}} down
    @echo "[infra] Stopped!"

[group('Infra')]
[doc('Stop infra + removing volumes')]
infra-clean:
    @echo "[infra] Stopping + removing volumes..."
    {{INFRA}} down -v
    @echo "[infra] Cleaned!"

[group('App')]
[doc('Build and up application with consumers')]
app-up:
    @echo "[app] Starting..."
    @just _net-create
    @just env-docker
    {{APP}} up -d --build
    @echo "[app] Started!"

[group('App')]
[doc('Build and up only app')]
app-up-api:
    @echo "[app] Starting grpc only..."
    @just _net-create
    @just env-docker
    {{APP}} up -d grpc
    @echo "[app] grpc started!"

[group('App')]
[doc('Rebuildy app and consumers')]
app-rebuild:
    @just env-docker
    @echo "[app] Rebuilding grpc server + consumers..."
    {{APP}} up -d --build grpc consumer consumer-update
    @echo "[app] Rebuilt."

[group('App')]
[doc('Bootstrap application')]
app-bootstrap partitions replicas:
    @echo "[app] Bootstrapping..."
    @just _net-create
    @just env-docker
    @just build-migrate-image
    @just db-migrate
    @just kafka-topics {{partitions}}
    @just consumers-scale {{replicas}}
    @just app-up-api
    @echo "[app] Bootstrap completed."

[group('App')]
[doc('Stop application (keeping volumes)')]
app-down:
    @echo "[app] Stopping (keeping volumes)..."
    {{APP}} down
    @echo "[app] Stopped!"

[group('App')]
[doc('Stop application + removing volumes')]
app-clean:
    @echo "[app] Stopping + removing volumes..."
    {{APP}} down -v
    @echo "[app] Cleaned!"

[group('Monitoring')]
[doc('Build and up monitoring')]
mon-up:
    @echo "[mon] Starting..."
    {{MON}} up -d --build
    @echo "[mon] Started!"

[group('Monitoring')]
[doc('Stop monitoring (keeping volumes)')]
mon-down:
    @echo "[mon] Stopping (keeping volumes)..."
    {{MON}} down
    @echo "[mon] Stopped!"

[group('Monitoring')]
[doc('Stop monitoring + removing volumes')]
mon-clean:
    @echo "[mon] Stopping + removing volumes..."
    {{MON}} down -v
    @echo "[mon] Cleaned!"
