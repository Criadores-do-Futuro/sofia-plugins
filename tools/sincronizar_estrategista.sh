#!/usr/bin/env bash
# Traz para plugins/sofia-estrategista-editora o mesmo conteúdo que o .zip da
# Sofia Estrategista leva, a partir de um clone do repositório de origem.
# A lista de itens vem do próprio empacotador de lá (scripts/empacotar.sh),
# então as duas cópias nunca divergem no que entra no plugin.
#
# Uso: tools/sincronizar_estrategista.sh CAMINHO_DO_CLONE [REF]   (REF padrão: origin/main)
set -euo pipefail

ORIGEM="${1:?informe o caminho do clone de sofia-estrategista-editora}"
REF="${2:-origin/main}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="$RAIZ/plugins/sofia-estrategista-editora"

git -C "$ORIGEM" fetch -q origin
ITENS=()
while IFS= read -r item; do
  [ -n "$item" ] && ITENS+=("$item")
done < <(git -C "$ORIGEM" show "$REF:scripts/empacotar.sh" | sed -n '/^ITENS=(/,/^)/p' | sed '1d;$d' | tr -d ' ')
[ "${#ITENS[@]}" -gt 0 ] || { echo "Não achei a lista ITENS no empacotar.sh de $REF" >&2; exit 1; }

PRESENTES=()
for item in "${ITENS[@]}"; do
  if git -C "$ORIGEM" cat-file -e "$REF:$item" 2>/dev/null; then PRESENTES+=("$item"); fi
done

rm -rf "$DESTINO"
mkdir -p "$DESTINO"
git -C "$ORIGEM" archive "$REF" -- "${PRESENTES[@]}" | tar -x -C "$DESTINO"

# Mesmas exclusões do empacotador (lista FORA), para a cópia ter os arquivos do .zip.
while IFS= read -r padrao; do
  [ -n "$padrao" ] || continue
  find "$DESTINO" -path "$DESTINO/$padrao" -type f -delete
done < <(git -C "$ORIGEM" show "$REF:scripts/empacotar.sh" | sed -n '/^FORA=(/,/^)/p' | sed '1d;$d' \
  | grep -o "'[^']*'" | tr -d "'")
find "$DESTINO" -type d -empty -delete

VERSAO="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$DESTINO/.claude-plugin/plugin.json")"
echo "Sofia Estrategista $VERSAO copiada de $REF ($(git -C "$ORIGEM" rev-parse --short "$REF"))."
echo "Atualize a versão nos dois catálogos e rode: python3 -m unittest discover -s tests"
