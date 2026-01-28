#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="./proto"
OUT_SRC="./src"
PKG_PREFIX="shortener_app/generated"
OUT_PY_DIR="${OUT_SRC}/shortener_app/generated"

rm -rf "${OUT_PY_DIR}"
mkdir -p "${OUT_PY_DIR}"

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "${TMP_DIR}"; }
trap cleanup EXIT

mkdir -p "${TMP_DIR}/${PKG_PREFIX}"
cp -R "${PROTO_DIR}/." "${TMP_DIR}/${PKG_PREFIX}/"

find "${TMP_DIR}/${PKG_PREFIX}" -name "*.proto" -print0 | sort -z | \
  xargs -0 python -m grpc_tools.protoc \
    -I "${TMP_DIR}" \
    -I "${TMP_DIR}/${PKG_PREFIX}" \
    --python_out="${OUT_SRC}" \
    --pyi_out="${OUT_SRC}" \
    --grpc_python_out="${OUT_SRC}"

find "${OUT_PY_DIR}" -type d -exec sh -c 'touch "$1/__init__.py"' _ {} \;

echo "Generated protos into ${OUT_PY_DIR}"
