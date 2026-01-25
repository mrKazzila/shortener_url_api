#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="./proto"
OUT_DIR="./src/generated"

mkdir -p "${OUT_DIR}"

PROTOS=$(find "${PROTO_DIR}" -name "*.proto" | sort)

python -m grpc_tools.protoc \
  -I "${PROTO_DIR}" \
  --python_out="${OUT_DIR}" \
  --pyi_out="${OUT_DIR}" \
  --grpc_python_out="${OUT_DIR}" \
  ${PROTOS}

find "${OUT_DIR}" -type d -exec sh -c 'touch "$1/__init__.py"' _ {} \;

echo "Generated protos into ${OUT_DIR}"
