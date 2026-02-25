[group('DB')]
[doc('Create alembic revision')]
db-rev msg:
    @echo "[db] Create alembic revision: {{msg}}"
    @alembic revision --autogenerate -m "{{msg}}" --rev-id {{msg}}

[group('DB')]
[doc('Building a migration image')]
build-migrate-image:
	docker build -f docker/dockerfiles/Migration.dockerfile -t shortener-app-migrate .

[group('DB')]
[doc('Generate alembic revision file')]
db-rev-local msg:
    @just env-local
    @just db-rev "{{msg}}"

[group('DB')]
[doc('Downgrade alembic revision')]
db-downgrade-local:
    @just env-local
    @alembic downgrade -1

[group('DB')]
[doc('Upgrade DB migration to head')]
db-migrate:
    @echo "[db] upgrade head..."
    {{MIGRATION}} upgrade head

[group('DB')]
[doc('Downgrade DB migration')]
db-downgrade:
    @echo "[db] downgrade -1..."
    @just build-migrate-image
    {{MIGRATION}} downgrade -1

[group('DB')]
[doc('Show current DB migration')]
db-current:
    @echo "[db] Show current DB migration"
    @just build-migrate-image
    {{MIGRATION}} current

[group('DB')]
[doc('Apply alembic migration to DB')]
db-apply msg:
    @just env-docker
    @just build-migrate-image
    @just db-rev-local "{{msg}}"
    @just env-docker
    @just db-migrate
