#!/usr/bin/env bash
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGEM=pereira-repro

docker_run() {
  docker run --rm -it \
    --privileged \
    -v /lib/modules:/lib/modules:ro \
    -v "$RAIZ":/repo \
    -w /repo/pereira \
    "$IMAGEM" "$@"
}

case "${1:-}" in
  build)
    docker build -f "$RAIZ/docker/Dockerfile" -t "$IMAGEM" "$RAIZ"
    ;;
  shell)
    docker_run /bin/bash
    ;;
  exec)
    shift
    [ $# -gt 0 ] || { echo "informe o comando a executar" >&2; exit 1; }
    docker_run "$@"
    ;;
  *)
    echo "uso: $0 {build|shell|exec <comando>}" >&2
    exit 1
    ;;
esac
