import React from 'react';
import {AbsoluteFill, interpolate, Easing, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Entrada, Saida} from './tipos';

/** saida da placa: ~0,43s a 30fps, como manda a identidade (ritmo.md) */
export const FRAMES_SAIDA = 13;
export const FRAMES_ENTRADA = 8;

/**
 * O envelope de movimento de um plano: como ele chega e como ele sai.
 *
 * A saida acontece POR CIMA do plano seguinte — a sequencia se estende por
 * FRAMES_SAIDA, entao o que sai revela o que ja esta embaixo. E o corte que
 * carrega sentido: o acumulo de palavras varrido para fora deixa o vazio que a
 * proxima cena preenche.
 */
export const Movimento: React.FC<{
  entrada?: Entrada;
  saida?: Saida;
  duracao: number;
  children: React.ReactNode;
}> = ({entrada = 'corte', saida = 'corte', duracao, children}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const e = interpolate(frame, [0, FRAMES_ENTRADA], [0, 1], {
    extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });
  const inicioSaida = duracao;
  const s = interpolate(frame, [inicioSaida, inicioSaida + FRAMES_SAIDA], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.cubic),
  });

  let x = 0, y = 0, escala = 1, opac = 1;

  if (entrada === 'deslizar') x += interpolate(e, [0, 1], [width * 0.35, 0]);
  if (entrada === 'subir') y += interpolate(e, [0, 1], [height * 0.12, 0]);
  if (entrada === 'escalar') escala *= interpolate(e, [0, 1], [1.14, 1]);
  if (entrada !== 'corte') opac *= e;

  if (saida === 'varrer') x += interpolate(s, [0, 1], [0, -width * 1.06]);
  if (saida === 'empurrar') escala *= interpolate(s, [0, 1], [1, 1.34]);
  if (saida === 'implodir') escala *= interpolate(s, [0, 1], [1, 0.55]);
  if (saida === 'apagar' || saida === 'implodir' || saida === 'empurrar') opac *= 1 - s;

  return (
    <AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${escala})`, opacity: opac}}>
      {children}
    </AbsoluteFill>
  );
};
