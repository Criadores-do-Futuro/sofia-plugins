import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano, PRESETS} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';
import {Papel} from '../lib/Papel';

/**
 * paper — a ficha bibliografica REAL do estudo citado.
 *
 * Ficha (titulo, autores, periodico, ano, DOI) e fato e pode aparecer.
 * Fac-simile da pagina, nao: este componente DESENHA uma ficha, nunca reproduz
 * o layout original. Uma citacao curta, entre aspas, com autor visivel.
 * Ver referencias/enriquecimento.md.
 */
export const Paper: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, preset, duracao,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const p = useGrade();
  const d = plano.paper;

  if (!d || !d.titulo) {
    return (
      <AbsoluteFill style={{backgroundColor: p.fundo, color: p.alerta, alignItems: 'center',
        justifyContent: 'flex-end', paddingBottom: height * 0.3, fontFamily: 'IBM Plex Mono, monospace', fontSize: 28}}>
        {plano.id}: plano `paper` sem ficha. Rode o enriquecimento.
      </AbsoluteFill>
    );
  }

  // a folha entra assentando: rotacao e escala cedendo nos primeiros 0,4s
  const t = interpolate(frame, [0, Math.min(duracao, 12)], [0, 1], {extrapolateRight: 'clamp'});
  const rot = interpolate(t, [0, 1], [-3.4, -1.6]);
  const esc = interpolate(t, [0, 1], [1.06, 1]) * interpolate(frame, [0, duracao], [1, 1.03], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: `rotate(${rot}deg) scale(${esc})`, width: width * 0.8}}>
        <Papel>
          <div style={{padding: '58px 54px 48px'}}>
            <div style={{fontFamily: 'IBM Plex Mono, monospace', fontSize: 22, letterSpacing: '.14em',
              textTransform: 'uppercase', opacity: 0.5, marginBottom: 26}}>
              {d.publicacao || 'artigo científico'}
            </div>
            <div style={{fontFamily: 'Fraunces, Georgia, serif', fontWeight: 800, fontSize: 54,
              lineHeight: 1.1, marginBottom: 22}}>
              {d.titulo}
            </div>
            <div style={{fontFamily: 'Fraunces, Georgia, serif', fontSize: 30, opacity: 0.75, marginBottom: 30}}>
              {d.autores}{d.ano ? ` · ${d.ano}` : ''}
            </div>
            {d.citacao ? (
              <div style={{borderLeft: '4px solid rgba(0,0,0,.35)', paddingLeft: 22, marginBottom: 30,
                fontFamily: 'Fraunces, Georgia, serif', fontStyle: 'italic', fontSize: 32, lineHeight: 1.28}}>
                “{d.citacao}”
              </div>
            ) : null}
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
              fontFamily: 'IBM Plex Mono, monospace', fontSize: 20, opacity: 0.55}}>
              <span>{d.doi ? `doi ${d.doi}` : ''}</span>
              <span>{d.verificado === false ? 'não verificado' : ''}</span>
            </div>
          </div>
        </Papel>
      </div>
    </AbsoluteFill>
  );
};
