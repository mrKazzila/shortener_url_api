# Set local env
[group('Env')]
env-local:
    @sed -i '' 's/^DB_HOST=.*/DB_HOST=localhost/' env/.env
    @sed -i '' 's/^DB_PORT=.*/DB_PORT=5433/' env/.env
    @sed -i '' 's/^REDIS_HOST=.*/REDIS_HOST=localhost/' env/.env
    @echo "[env] set for LOCAL"

# Set docker env
[group('Env')]
env-docker:
    @sed -i '' 's/^DB_HOST=.*/DB_HOST=postgres/' env/.env
    @sed -i '' 's/^DB_PORT=.*/DB_PORT=5432/' env/.env
    @sed -i '' 's/^REDIS_HOST=.*/REDIS_HOST=redis/' env/.env
    @echo "[env] set for DOCKER"
