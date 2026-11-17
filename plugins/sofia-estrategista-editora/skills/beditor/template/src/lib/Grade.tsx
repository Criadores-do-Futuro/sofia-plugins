import React from 'react';
import {AbsoluteFill, useCurrentFrame, random} from 'remotion';
import {PRESETS} from './tipos';

/**
 * A grade da identidade. NAO edite os numeros aqui sem ler
 * referencias/linguagem-visual.md — eles foram medidos, nao escolhidos.
 *
 * Ordem obrigatoria: bloom -> aberracao -> vinheta -> grao -> curva.
 */
export const FiltrosGrade: React.FC<{preset: keyof typeof PRESETS}> = ({preset}) => {
  const p = PRESETS[preset];
  return (
    <svg width={0} height={0} style={{position: 'absolute'}}>
      <defs>
        {/* aberracao cromatica: separa laranja/ciano nas bordas */}
        <filter id="bed-aberracao" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
          <feOffset in="SourceGraphic" dx={p.aberracao} dy={0} result="r" />
          <feColorMatrix in="r" type="matrix" result="rc"
            values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" />
          <feOffset in="SourceGraphic" dx={-p.aberracao} dy={0} result="b" />
          <feColorMatrix in="b" type="matrix" result="bc"
            values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" />
          <feColorMatrix in="SourceGraphic" type="matrix" result="gc"
            values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" />
          <feBlend in="rc" in2="gc" mode="screen" result="rg" />
          <feBlend in="rg" in2="bc" mode="screen" />
        </filter>

        {/* curva: preto levantado a 12/255, branco segurado em 235 — sempre por ultimo */}
        <filter id="bed-curva" colorInterpolationFilters="sRGB">
          <feComponentTransfer>
            <feFuncR type="linear" slope="0.874" intercept="0.047" />
            <feFuncG type="linear" slope="0.874" intercept="0.047" />
            <feFuncB type="linear" slope="0.874" intercept="0.047" />
          </feComponentTransfer>
          <feColorMatrix type="saturate" values="0.8" />
        </filter>
      </defs>
    </svg>
  );
};

/** grao: ressemeado a cada frame, vive inclusive dentro do preto */
export const Grao: React.FC<{intensidade: number}> = ({intensidade}) => {
  const frame = useCurrentFrame();
  const semente = Math.floor(random(`grao-${frame}`) * 1000);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'overlay', opacity: intensidade}}>
      <svg width="100%" height="100%">
        <filter id={`bed-grao-${semente}`} colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={1} seed={semente} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#bed-grao-${semente})`} />
      </svg>
    </AbsoluteFill>
  );
};

/** vinheta: cantos quase pretos */
export const Vinheta: React.FC<{forca: number}> = ({forca}) => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      background: `radial-gradient(ellipse 72% 62% at 50% 46%, rgba(0,0,0,0) 40%, rgba(0,0,0,${forca}) 100%)`,
    }}
  />
);

/** bloom: halo largo e macio nas altas luzes */
export const Bloom: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill>
    {children}
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        mixBlendMode: 'screen',
        filter: 'blur(28px) brightness(1.25) contrast(1.6)',
        opacity: 0.35,
      }}
    >
      {children}
    </AbsoluteFill>
  </AbsoluteFill>
);

/** halftone da variante 2026 — desligado por padrao */
export const Halftone: React.FC<{opacidade?: number}> = ({opacidade = 0.18}) => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      mixBlendMode: 'overlay',
      opacity: opacidade,
      backgroundImage:
        'radial-gradient(circle at 1px 1px, rgba(255,255,255,.9) 0.9px, transparent 1px)',
      backgroundSize: '4px 4px',
    }}
  />
);

/** grade fina de linhas da variante 2026 */
export const Grade2026: React.FC<{opacidade?: number}> = ({opacidade = 0.12}) => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      opacity: opacidade,
      backgroundImage:
        'linear-gradient(rgba(255,255,255,.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.5) 1px, transparent 1px)',
      backgroundSize: '90px 90px',
    }}
  />
);
