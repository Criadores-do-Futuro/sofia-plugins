import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano, PRESETS, SEGURO} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';
import {escala} from '../lib/ritmo';

/**
 * cartela — NAO e fundo chapado. E legenda sobre b-roll rebaixado.
 * Luminancia mediana medida na referencia: 35/255.
 */
export const Cartela: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, preset, duracao,
}) => {
  const frame = useCurrentFrame();
  const {height} = useVideoConfig();
  const p = useGrade();
  const s = escala(frame, duracao, plano.camera);

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo}}>
      {plano.asset ? (
        <AbsoluteFill style={{transform: `scale(${s})`}}>
          <Img src={staticFile(plano.asset)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          <AbsoluteFill style={{backgroundColor: 'rgba(0,0,0,.55)'}} />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill
        style={{
          justifyContent: 'flex-start',
          alignItems: 'center',
          paddingTop: height * SEGURO.legenda - 90,
        }}
      >
        <div
          style={{
            fontFamily: 'Inter, system-ui, sans-serif',
            fontWeight: 700,
            fontSize: 88,
            lineHeight: 1.04,
            letterSpacing: '-0.022em',
            color: p.texto,
            textAlign: 'center',
            maxWidth: '86%',
            textShadow: '0 0 24px rgba(255,255,255,.35), 0 0 60px rgba(255,255,255,.18)',
          }}
        >
          {plano.texto}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
