#!/bin/bash
set -euo pipefail

current_dir=$(pwd)
echo "Current dir: $current_dir"

: "${WORKERS:=$(python - <<'PY'
import os
print(max(2, (os.cpu_count() or 2)))
PY
)}"

: "${PORT:=8000}"
: "${HOST:=0.0.0.0}"

case "${MODE:-DEV}" in
  "DEV")
    echo "Running uvicorn in DEV mode (workers=4)"
    exec python -m uvicorn app.main:app \
      --workers 4 \
      --host "$HOST" \
      --port "$PORT" \
      --loop uvloop \
      --http httptools \
      --no-use-colors \
      --no-access-log \
      --timeout-keep-alive 5 \
      --backlog 2048 \
      --log-config ./app/settings/logger_config.yaml
    ;;

  "PROD")
    echo "Running gunicorn in PROD mode (workers=$WORKERS)"
    exec python -m gunicorn app.main:app \
      --worker-class uvicorn.workers.UvicornWorker \
      --workers "$WORKERS" \
      --bind "$HOST:$PORT" \
      --keep-alive 5 \
      --timeout 60 \
      --graceful-timeout 30 \
      --backlog 2048 \
      --max-requests 20000 \
      --max-requests-jitter 2000 \
      --log-level info
    ;;

  *)
    echo "Unknown mode: $MODE. Please set MODE to DEV or PROD."
    exit 1
    ;;
esac
