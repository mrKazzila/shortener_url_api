[group('Tests')]
test-local marker="unit":
    uv run pytest -q -m {{marker}}

[group('Tests')]
test-local-all:
    uv run pytest -q

[group('Tests')]
test-docker marker="":
    #!/usr/bin/env bash
    set -eu -o pipefail

    {{INFRA_TEST}} up -d
    cleanup() { {{INFRA_TEST}} down -v; }
    trap cleanup EXIT

    if [[ -n "{{marker}}" ]]; then
    {{APP_TEST}} run --rm tests pytest -p pytest_asyncio -q -m "{{marker}}" -o cache_dir=/tmp/pytest_cache
    else
    {{APP_TEST}} run --rm tests pytest -q -o cache_dir=/tmp/pytest_cache
    fi

[group('Tests')]
unit:
    just test-local unit

[group('Tests')]
integration:
    just test-docker integration

[group('Tests')]
migrations:
    just test-docker migrations

[group('Tests')]
e2e:
    just test-docker e2e

[group('Tests')]
tests:
    just test-docker