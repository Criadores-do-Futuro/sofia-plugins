#!/usr/bin/env bash
# Compatibilidade: a implementação Python recebe os argumentos sem interpolação.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/collect-public.py" --comments "$@"
