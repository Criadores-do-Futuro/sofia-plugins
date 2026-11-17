#!/usr/bin/env bash
# projeto.sh — monta o projeto Remotion a partir do template do bEditor
# uso: bash projeto.sh <pasta-do-projeto>
set -euo pipefail

SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:?uso: projeto.sh <pasta-do-projeto>}"
# A identidade viaja dentro do plugin: motion-vox e uma skill irma, ao lado desta.
FONTES="$(cd "$SKILL/.." && pwd)/motion-vox/fontes"

mkdir -p "$DEST"
[ -f "$DEST/plano.json" ] || { echo "erro: $DEST/plano.json nao existe — rode plano.py primeiro"; exit 1; }

# template (nao sobrescreve componentes que voce ja editou)
cp -n "$SKILL/template/package.json" "$SKILL/template/tsconfig.json" "$SKILL/template/remotion.config.ts" "$DEST/" 2>/dev/null || true
mkdir -p "$DEST/src/planos" "$DEST/src/lib" "$DEST/public/assets" "$DEST/public/fontes"
cp -Rn "$SKILL/template/src/." "$DEST/src/" 2>/dev/null || true

# o Root le de public/
cp "$DEST/plano.json" "$DEST/public/plano.json"

# fontes livres (OFL/Apache) — a identidade viaja junto
if [ -d "$FONTES" ]; then
  cp -n "$FONTES/Inter-opsz-wght.ttf"           "$DEST/public/fontes/Inter.ttf" 2>/dev/null || true
  cp -n "$FONTES/ArchivoNarrow-wght.ttf"        "$DEST/public/fontes/ArchivoNarrow.ttf" 2>/dev/null || true
  cp -n "$FONTES/Fraunces-SOFT-WONK-opsz-wght.ttf" "$DEST/public/fontes/Fraunces.ttf" 2>/dev/null || true
  cp -n "$FONTES/ArchivoBlack-Regular.ttf" "$FONTES/Anton-Regular.ttf" \
        "$FONTES/IBMPlexMono-Medium.ttf" "$FONTES/PermanentMarker-Regular.ttf" \
        "$DEST/public/fontes/" 2>/dev/null || true
  cp -n "$FONTES"/*.txt "$DEST/public/fontes/" 2>/dev/null || true
else
  echo "aviso: $FONTES nao encontrado — a legenda vai cair na fonte do sistema."
fi

cd "$DEST"
[ -d node_modules ] || npm install --silent

echo
echo "pronto. preview:  cd $DEST && npx remotion studio"
echo "render:           cd $DEST && npx remotion render Video out/master.mp4"
