#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="./proto"
DOCS_DIR="../docs/grpc"

mkdir -p "${DOCS_DIR}"

# ----------------------------
# gRPC Docs via Docker
# ----------------------------
if command -v docker >/dev/null 2>&1; then
  echo "[docs] generating docs via docker -> ${DOCS_DIR}"

  DOCKER_PLATFORM_ARGS=()
  if [ "$(uname -m)" = "arm64" ]; then
    DOCKER_PLATFORM_ARGS=(--platform linux/amd64)
  fi

  DOCKER_PROTO_FILES=()
  while IFS= read -r f; do
    rel="${f#${PROTO_DIR}/}"
    DOCKER_PROTO_FILES+=("${rel}")
  done < <(find "${PROTO_DIR}" -name "*.proto" | sort)

  # HTML
  docker run --rm "${DOCKER_PLATFORM_ARGS[@]}" \
    -v "$(pwd)/${DOCS_DIR}:/out" \
    -v "$(pwd)/${PROTO_DIR}:/protos" \
    pseudomuto/protoc-gen-doc \
    -I /protos \
    "${DOCKER_PROTO_FILES[@]}"

  # Markdown
  docker run --rm "${DOCKER_PLATFORM_ARGS[@]}" \
    -v "$(pwd)/${DOCS_DIR}:/out" \
    -v "$(pwd)/${PROTO_DIR}:/protos" \
    pseudomuto/protoc-gen-doc \
    --doc_opt=markdown,grpc.md \
    -I /protos \
    "${DOCKER_PROTO_FILES[@]}"

  echo "[docs] done: ${DOCS_DIR}/index.html and ${DOCS_DIR}/grpc.md"
else
  echo "[docs] docker not found -> skip docs generation"
fi
