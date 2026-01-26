#!/bin/bash
set -euo pipefail

current_dir=$(pwd)
echo "Current dir: $current_dir"

: "${GRPC_HOST:=0.0.0.0}"
: "${GRPC_PORT:=50051}"

case ":${PYTHONPATH:-}:" in
  *":${APP_HOME}/src/generated:"*) ;;
  *) export PYTHONPATH="${APP_HOME}/src/generated:${PYTHONPATH:-}" ;;
esac

echo "[PYTHONPATH] $PYTHONPATH"
echo "[gRPC] starting server on ${GRPC_HOST}:${GRPC_PORT}"

exec python -m src.main
