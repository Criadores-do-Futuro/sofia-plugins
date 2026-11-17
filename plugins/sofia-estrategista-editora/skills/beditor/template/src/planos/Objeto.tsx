import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {Plano, PRESETS} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';
import {escala, parallax} from '../lib/ritmo';

/**
 * objeto / personagem / obra / arquivo / broll — a chapa vem de fora
 * (IA, acervo ou camera) e o movimento vem daqui.
 *
 * Parallax 2.5D: se voce separou a imagem em camadas (assunto/meio/fundo),
 * nomeie-as asset.png, asset-meio.png, asset-fundo.png que o componente usa.
 */
export const Objeto: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, preset, duracao,
}) => {
  const frame = useCurrentFrame();
  const p = useGrade();

  if (!plano.asset) {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: p.fundo, color: p.sujeito, alignItems: 'center', justifyContent: 'flex-end',
          fontFamily: 'IBM Plex Mono, monospace', fontSize: 26, textAlign: 'center', padding: 80,
          paddingBottom: 560,
        }}
      >
        {plano.id} · {plano.tipo} · asset pendente
        <div style={{opacity: 0.5, fontSize: 22, marginTop: 24}}>{plano.prompt}</div>
      </AbsoluteFill>
    );
  }

  const base = plano.asset.replace(/\.(png|jpg|jpeg|webp)$/i, '');
  const ext = plano.asset.slice(base.length);
  const camadas =
    plano.camera === 'parallax'
      ? [`${base}-fundo${ext}`, `${base}-meio${ext}`, plano.asset]
      : [plano.asset];

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo}}>
      {camadas.map((src, i) => {
        const s =
          camadas.length === 1
            ? escala(frame, duracao, plano.camera)
            : parallax(frame, duracao, (2 - i) as 0 | 1 | 2);
        return (
          <AbsoluteFill key={src} style={{transform: `scale(${s})`}}>
            <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};
