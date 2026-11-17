import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano, PRESETS} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';

/**
 * dado — desenhado em codigo, nunca gerado.
 * Sem `plano.serie` e sem `plano.fonte`, o componente se recusa a desenhar:
 * numero sem fonte nao vira grafico (SKILL.md).
 */
export const Dado: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, preset, duracao,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const p = useGrade();
  const serie = plano.serie ?? [];
  const curva = plano.curva ?? [];
  const semFonte = !plano.fonte || plano.fonte.startsWith('TODO');
  const falta = (serie.length === 0 && curva.length === 0) || semFonte;

  if (falta) {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: p.fundo, color: p.alerta, alignItems: 'center', justifyContent: 'flex-end',
          fontFamily: 'IBM Plex Mono, monospace', fontSize: 30, textAlign: 'center', padding: 80,
          paddingBottom: height * 0.28,
        }}
      >
        {plano.id}: grafico sem serie ou sem fonte.
        <div style={{opacity: 0.7, fontSize: 24, marginTop: 20}}>
          preencha "serie" e "fonte" em plano.json, ou troque o tipo para "objeto".
        </div>
      </AbsoluteFill>
    );
  }

  // curva: desenha-se da esquerda para a direita, no ritmo do plano
  if (curva.length > 1) {
    const larg = width * 0.74, alt = height * 0.26;
    const x0 = (width - larg) / 2, y0 = height * 0.40;
    const pontos = curva.map((v, i) => [x0 + (i / (curva.length - 1)) * larg, y0 + (1 - v) * alt]);
    const d = pontos.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const total = larg * 1.6;
    const revelado = interpolate(frame, [0, duracao * 0.78], [0, total], {extrapolateRight: 'clamp'});
    return (
      <AbsoluteFill style={{backgroundColor: p.fundo}}>
        <svg width={width} height={height} style={{position: 'absolute'}}>
          <path d={d} fill="none" stroke={p.ambar} strokeWidth={7} strokeLinecap="round"
            strokeDasharray={total} strokeDashoffset={total - revelado}
            style={{filter: `drop-shadow(0 0 22px ${p.ambar}88)`}} />
        </svg>
        {plano.texto ? (
          <div style={{position: 'absolute', top: height * 0.66, width: '100%', textAlign: 'center',
            fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 62, color: p.texto,
            padding: '0 8%', lineHeight: 1.08,
            textShadow: '0 0 22px rgba(255,255,255,.35)'}}>
            {plano.texto}
          </div>
        ) : null}
        <div style={{position: 'absolute', bottom: height * 0.20, width: '100%', textAlign: 'center',
          fontFamily: 'IBM Plex Mono, monospace', fontSize: 22, color: p.sujeito, opacity: 0.45}}>
          {plano.fonte}
        </div>
      </AbsoluteFill>
    );
  }

  const max = Math.max(...serie.map((s) => s.valor));
  const larguraBarra = (width * 0.72) / serie.length;
  const alturaMax = height * 0.34;
  const crescimento = interpolate(frame, [0, Math.round(duracao * 0.55)], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo, alignItems: 'center', justifyContent: 'flex-end', paddingBottom: height * 0.30}}>
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 18, height: alturaMax}}>
        {serie.map((s) => (
          <div key={s.rotulo} style={{textAlign: 'center'}}>
            <div
              style={{
                width: larguraBarra * 0.7,
                height: (s.valor / max) * alturaMax * crescimento,
                background: `linear-gradient(180deg, ${p.quente}, ${p.ambar})`,
              }}
            />
            <div
              style={{
                fontFamily: 'IBM Plex Mono, monospace', fontSize: 26, color: p.sujeito,
                marginTop: 14, opacity: 0.8,
              }}
            >
              {s.rotulo}
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          position: 'absolute', bottom: height * 0.24,
          fontFamily: 'IBM Plex Mono, monospace', fontSize: 22, color: p.sujeito, opacity: 0.45,
        }}
      >
        {plano.fonte}
      </div>
    </AbsoluteFill>
  );
};
