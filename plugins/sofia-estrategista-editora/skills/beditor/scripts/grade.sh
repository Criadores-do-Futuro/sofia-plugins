#!/usr/bin/env bash
# grade.sh — segunda passada de grade em ffmpeg (opcional)
# uso: bash grade.sh entrada.mp4 saida.mp4 [noturno|editorial]
#
# Serve sobretudo para footage que ENTRA no pipeline (filmado, acervo, video de IA):
# alinha esse material a grade antes de virar asset. Sobre o master do Remotion a
# curva seria aplicada duas vezes e o preto subiria para ~22/255 — nesse caso, pule.
set -euo pipefail
IN="${1:?uso: grade.sh entrada.mp4 saida.mp4 [preset]}"
OUT="${2:?uso: grade.sh entrada.mp4 saida.mp4 [preset]}"
PRESET="${3:-noturno}"

if [ "$PRESET" = "noturno" ]; then
  # curva: preto a 12/255, branco segurado em 235 · -20% saturacao
  # aberracao: canal R deslocado +2px, canal B -2px, recombinados
  # vinheta forte · grao constante inclusive no preto
  FILTRO="split=3[r][g][b];
  [r]lutrgb=g=0:b=0,crop=iw-4:ih:4:0,pad=iw+4:ih:0:0[rr];
  [b]lutrgb=r=0:g=0,crop=iw-4:ih:0:0,pad=iw+4:ih:4:0[bb];
  [g]lutrgb=r=0:b=0[gg];
  [rr][gg]blend=all_mode=screen[rg];
  [rg][bb]blend=all_mode=screen,
  curves=all='0/0.047 0.5/0.5 1/0.921',
  eq=saturation=0.80,
  vignette=angle=PI/3.4,
  noise=alls=9:allf=t+u,
  format=yuv420p"
else
  FILTRO="eq=saturation=0.92,vignette=angle=PI/8,noise=alls=3:allf=t+u,format=yuv420p"
fi

ffmpeg -hide_banner -loglevel error -y -i "$IN" \
  -filter_complex "$FILTRO" \
  -c:v libx264 -crf 17 -preset slow -c:a copy "$OUT"

echo "grade aplicada: $OUT"
echo
echo "teste do histograma (noturno: pico abaixo de 40, pico estreito acima de 235):"
ffmpeg -hide_banner -loglevel error -y -i "$OUT" -vf "select=eq(n\,30),signalstats,metadata=print:key=lavfi.signalstats.YAVG" -vframes 1 -f null - 2>&1 | head -3 || true
