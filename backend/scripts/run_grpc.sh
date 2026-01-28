#!/bin/sh
set -eu

echo "Current dir: $(pwd)"

: "${GRPC_HOST:=0.0.0.0}"
: "${GRPC_PORT:=50051}"
: "${APP_HOME:=/home/unprivilegeduser/shortener}"

src_path="${APP_HOME}/src"

case ":${PYTHONPATH:-}:" in
  *":${src_path}:"*) ;;
  *) PYTHONPATH="${src_path}${PYTHONPATH:+:${PYTHONPATH}}"
     export PYTHONPATH
     ;;
esac

echo "[PYTHONPATH] ${PYTHONPATH:-}"
echo "[gRPC] starting server on ${GRPC_HOST}:${GRPC_PORT}"

exec python -m shortener_app
