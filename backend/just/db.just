# Create alembic revision
[group('DB')]
db-rev msg:
    @echo "[db] Create alembic revision: {{msg}}"
    @alembic revision --autogenerate -m "{{msg}}"

# Generate alembic revision file
[group('DB')]
db-rev-local msg:
    @just env-local
    @just db-rev "{{msg}}"

# Downgrade alembic revision
[group('DB')]
db-down-local:
    @just env-local
    @alembic downgrade -1

# Upgrade DB migration to head
[group('DB')]
db-up:
    @echo "[db] upgrade head..."
    {{APP}} run --rm grpc python -m alembic upgrade head > /dev/null

# Downgrade DB migration
[group('DB')]
db-down:
    @echo "[db] downgrade -1..."
    {{APP}} run --rm grpc python -m alembic downgrade -1

# Apply alembic migration to DB
[group('DB')]
db-apply msg:
    @just env-docker
    @just db-up
    @just db-rev-local "{{msg}}"
    @just env-docker
    @just db-up
