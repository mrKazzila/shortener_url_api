# =====================
# Settings
# =====================
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

APP := "docker compose --env-file env/.env -p shortener-app -f docker-compose.yaml"
INFRA := "docker compose --env-file env/.env -p shortener-infra -f docker/infra/docker-compose.yml"
MON := "docker compose --env-file env/.env -p shortener-mon -f docker/monitoring/docker-compose.yml"


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

# Local commands (don't commit)
import? 'just/local.just'

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
