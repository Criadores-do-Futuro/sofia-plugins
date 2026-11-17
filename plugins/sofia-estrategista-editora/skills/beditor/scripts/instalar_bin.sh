#!/bin/zsh
# Compila as ferramentas Swift da skill em ~/.beditor/bin, só quando o fonte
# é mais novo que o binário. As duas rodam o Vision localmente: o rosto de
# quem fala não sai da máquina.
#
#   recorte          matte de pessoa (tela dividida, capa, rosto estilizado)
#   rastrear-rosto   caixa do rosto a cada 0,25 s → enquadrar_rosto.py
set -e
aqui=${0:A:h}
destino=~/.beditor/bin
mkdir -p $destino
for par in "recorte.swift:recorte" "rastrear_rosto.swift:rastrear-rosto"; do
  fonte=$aqui/${par%%:*}
  bin=$destino/${par##*:}
  if [[ ! -x $bin || $fonte -nt $bin ]]; then
    echo "compilando ${bin:t}…"
    xcrun swiftc -O -parse-as-library -o $bin $fonte 2>/dev/null \
      || xcrun swiftc -O -o $bin $fonte
  fi
  echo "${bin:t}: $bin"
done
