import {interpolate, Easing} from 'remotion';

export const msParaFrames = (ms: number, fps: number) => Math.round((ms / 1000) * fps);

/** push-in de 6% na duracao do plano — imperceptivel e muda tudo (ritmo.md) */
export const escala = (
  frame: number,
  duracao: number,
  camera: string,
): number => {
  if (camera === 'push-in') return interpolate(frame, [0, duracao], [1, 1.06], {extrapolateRight: 'clamp'});
  if (camera === 'pull-out') return interpolate(frame, [0, duracao], [1.08, 1], {extrapolateRight: 'clamp'});
  return 1;
};

/** camadas do parallax 2.5D: assunto 100%, meio 70%, fundo 40% */
export const parallax = (frame: number, duracao: number, camada: 0 | 1 | 2) => {
  const peso = [1, 0.7, 0.4][camada];
  return interpolate(frame, [0, duracao], [1, 1 + 0.08 * peso], {extrapolateRight: 'clamp'});
};

/** entrada de legenda: 0,10s, escala 0,92 -> 1 (ritmo.md) */
export const entradaLegenda = (frame: number, fps: number) =>
  interpolate(frame, [0, Math.max(1, Math.round(fps * 0.1))], [0.92, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
