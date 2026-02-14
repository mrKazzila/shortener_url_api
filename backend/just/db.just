# Create alembic revision
[group('DB')]
db-rev msg:
    @echo "[db] Create alembic revision: {{msg}}"
    @alembic revision --autogenerate -m "{{msg}}" --rev-id {{msg}}

# Building a migration image
[group('DB')]
build-migrate-image:
	docker build -f docker/dockerfiles/Migration.dockerfile -t shortener-app-migrate .

# Generate alembic revision file
[group('DB')]
db-rev-local msg:
    @just env-local
    @just db-rev "{{msg}}"

# Downgrade alembic revision
[group('DB')]
db-downgrade-local:
    @just env-local
    @alembic downgrade -1

# Upgrade DB migration to head
[group('DB')]
db-migrate:
    @echo "[db] upgrade head..."
    {{MIGRATION}} upgrade head

# Downgrade DB migration
[group('DB')]
db-downgrade:
    @echo "[db] downgrade -1..."
    @just build-migrate-image
    {{MIGRATION}} downgrade -1

# Show current DB migration
[group('DB')]
db-current:
    @echo "[db] Show current DB migration"
    @just build-migrate-image
    {{MIGRATION}} current

# Apply alembic migration to DB
[group('DB')]
db-apply msg:
    @just env-docker
    @just build-migrate-image
    @just db-rev-local "{{msg}}"
    @just env-docker
    @just db-migrate
