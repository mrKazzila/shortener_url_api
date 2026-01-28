# =====================
# Settings
# =====================
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

APP := "docker compose --project-directory . --env-file env/.env -p shortener_app-app -f docker/compose/app/docker-compose.yml"
INFRA := "docker compose --project-directory docker/compose/infra --env-file env/.env -p shortener_app-infra -f docker/compose/infra/infra.yml"
MON := "docker compose --project-directory docker/compose/monitoring --env-file env/.env -p shortener_app-mon -f docker/compose/monitoring/docker-compose.yml"

# =====================
# Imports
# =====================
import 'quality.just'
import 'env.just'
import 'req.just'
import 'helpers.just'
import 'kafka.just'
import 'db.just'
import 'stacks.just'
import 'all.just'
import 'convenience.just'
import 'docs.just'
import 'prepare.just'

# Local commands (don't commit)
import? 'local.just'

# =====================
# Aliases
# =====================
alias iu := infra-up
alias id := infra-down
alias ic := infra-clean

alias au := app-up
alias ad := app-down
alias ac := app-clean
alias ab := app-bootstrap

alias mu := mon-up
alias md := mon-down
alias mc := mon-clean

alias up := all-up
alias down := all-down

alias r := redis-cli
alias h := default
