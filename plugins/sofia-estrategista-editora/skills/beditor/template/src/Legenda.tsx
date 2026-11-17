import React, {useMemo} from 'react';
import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';
import {createTikTokStyleCaptions, type Caption, type TikTokPage} from '@remotion/captions';
import {PRESETS, SEGURO, TEM_TEXTO_PROPRIO, type Plano} from './lib/tipos';
import {useGrade} from './lib/GradeContext';
import {entradaLegenda} from './lib/ritmo';
import {useCurrentFrame} from 'remotion';

/** 2 a 4 palavras por pagina, trocando no ritmo da fala (ritmo.md) */
const JANELA_MS = 900;

const Pagina: React.FC<{pagina: TikTokPage; preset: keyof typeof PRESETS; destacar: boolean}> = ({
  pagina, preset, destacar,
}) => {
  const frame = useCurrentFrame();
  const {fps, height} = useVideoConfig();
  const p = useGrade();
  const agora = pagina.startMs + (frame / fps) * 1000;
  const s = entradaLegenda(frame, fps);

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'flex-start',
        alignItems: 'center',
        paddingTop: height * SEGURO.legenda,
      }}
    >
      <div
        style={{
          transform: `scale(${s})`,
          fontFamily: 'Inter, system-ui, sans-serif',
          fontWeight: 700,
          fontSize: 80,
          lineHeight: 1.06,
          letterSpacing: '-0.022em',
          textAlign: 'center',
          maxWidth: '86%',
          whiteSpace: 'pre-wrap',
          color: p.texto,
          textShadow: '0 0 22px rgba(255,255,255,.4), 0 0 64px rgba(255,255,255,.2)',
        }}
      >
        {pagina.tokens.map((t, i) => {
          const ativo = destacar && t.fromMs <= agora && t.toMs > agora;
          return (
            <span key={`${t.fromMs}-${i}`} style={{color: ativo ? p.ambar : p.texto}}>
              {t.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Legenda: React.FC<{
  captions: Caption[];
  preset: keyof typeof PRESETS;
  /** os planos, para calar a legenda onde o quadro ja tem texto */
  planos: Plano[];
  /** destaque palavra a palavra so ajuda em fala rapida (ritmo.md) */
  destacar?: boolean;
}> = ({captions, preset, planos, destacar = false}) => {
  const {fps} = useVideoConfig();
  const {pages} = useMemo(
    () => createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: JANELA_MS}),
    [captions],
  );

  /**
   * Regra: onde ha motion graphics com texto na tela, a legenda cala.
   * Mostrar a mesma frase escrita duas vezes divide a atencao e nao soma nada.
   */
  const mudos = useMemo(
    () =>
      planos.filter((p) => (p.legenda === undefined ? TEM_TEXTO_PROPRIO.includes(p.tipo) : !p.legenda)),
    [planos],
  );
  const calada = (inicioMs: number, fimMs: number) => {
    const meio = (inicioMs + fimMs) / 2;
    return mudos.some((p) => meio >= p.t0 && meio < p.t1);
  };

  return (
    <AbsoluteFill>
      {pages.map((pagina, i) => {
        const proxima = pages[i + 1] ?? null;
        const de = (pagina.startMs / 1000) * fps;
        const ate = Math.min(
          proxima ? (proxima.startMs / 1000) * fps : Infinity,
          de + (JANELA_MS / 1000) * fps,
        );
        const dur = Math.round(ate - de);
        if (dur <= 0) return null;
        if (calada(pagina.startMs, pagina.startMs + (dur / fps) * 1000)) return null;
        return (
          <Sequence key={i} from={Math.round(de)} durationInFrames={dur}>
            <Pagina pagina={pagina} preset={preset} destacar={destacar} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
