import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';

/**
 * palavras — tipografia cinética: as palavras entram uma a uma, no ritmo em que
 * são ditas, e ficam acumuladas na tela.
 *
 * É o plano para quando a fala ENUMERA. "Cama. Descanso. Cansaço." não é uma
 * cartela: é um acúmulo. E o acúmulo na tela é o que faz a promessa que o plano
 * seguinte quebra quando ninguém lembrou de nenhuma.
 *
 * `plano.palavras` traz a lista. A saída do acúmulo é do envelope `Movimento`
 * (`plano.saida`), não daqui — um lugar só decide o movimento de saída.
 * Ver referencias/movimento.md.
 */
export const Palavras: React.FC<{
  plano: Plano;
  duracao: number;
  /** palavras dos planos `palavras` imediatamente anteriores: o acúmulo não
      recomeça a cada corte, ele atravessa a enumeração inteira */
  acumulado?: string[];
}> = ({plano, duracao, acumulado = []}) => {
  const frame = useCurrentFrame();
  const {fps, height} = useVideoConfig();
  const p = useGrade();
  const novas = plano.palavras ?? [];
  const lista = [...acumulado, ...novas];

  if (novas.length === 0 && lista.length === 0) {
    return (
      <AbsoluteFill style={{backgroundColor: p.fundo, color: p.alerta, alignItems: 'center',
        justifyContent: 'center', fontFamily: 'IBM Plex Mono, monospace', fontSize: 28}}>
        {plano.id}: plano `palavras` sem lista.
      </AbsoluteFill>
    );
  }

  // as palavras se distribuem pela duracao util do plano; a ultima entra a tempo
  // de ser lida antes da saida
  const passo = (duracao * 0.78) / Math.max(1, novas.length);

  const fantasmas = plano.fantasmas ?? [];
  const acender = plano.acender ?? false;

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo}}>
      {/* o fundo fantasma: a lista de onde a palavra nova NAO veio. Sem ele a
          intrusao e so uma palavra num quadro vazio — com ele, ela aparece no
          lugar de uma lista que o espectador reconhece. */}
      {fantasmas.length > 0 ? (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', padding: '0 80px'}}>
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '24px 36px',
            alignItems: 'center', justifyContent: 'center'}}>
            {fantasmas.map((f, i) => (
              <span key={`${f}-${i}`} style={{
                fontFamily: 'Archivo Black, Inter, sans-serif',
                fontSize: 64, lineHeight: 1, color: p.sujeito,
                opacity: interpolate(frame, [0, fps * 0.7], [0.34, 0.17], {
                  extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
                }),
                filter: 'blur(1.5px)',
                transform: `rotate(${(i % 2 === 0 ? -1 : 1) * 1.4}deg)`,
              }}>{f}</span>
            ))}
          </div>
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill
        style={{
          alignItems: 'center', justifyContent: 'center',
          padding: `${height * 0.16}px 90px ${height * 0.24}px`,
        }}
      >
        <div style={{display: 'flex', flexWrap: 'wrap', gap: '18px 30px',
          alignItems: 'center', justifyContent: 'center'}}>
          {lista.map((palavra, i) => {
            // o que veio de antes ja esta na tela; so as novas entram no tempo
            const nova = i >= acumulado.length;
            const entra = nova ? (i - acumulado.length) * passo : 0;
            if (frame < entra) return null;
            const mola = nova ? spring({frame: frame - entra, fps, config: {damping: 14, mass: 0.5}}) : 1;
            // a palavra entra grande e assenta; as anteriores recuam de peso
            const recuo = Math.max(0, lista.length - 1 - i);
            const opac = interpolate(recuo, [0, 6], [1, 0.34], {extrapolateRight: 'clamp'});
            const corpo = interpolate(recuo, [0, 6], [92, 52], {extrapolateRight: 'clamp'});
            const inclina = (i % 2 === 0 ? -1 : 1) * (1.2 + (i % 3) * 0.5);
            return (
              <span
                key={`${palavra}-${i}`}
                style={{
                  fontFamily: 'Archivo Black, Inter, sans-serif',
                  // a palavra que acende e maior que qualquer uma da lista:
                  // ela nao pertence, e o tamanho e quem diz isso
                  fontSize: acender && nova ? corpo * 1.9 : corpo,
                  lineHeight: 1,
                  color: acender && nova ? p.quente : p.texto,
                  opacity: opac * mola,
                  transform: `scale(${interpolate(mola, [0, 1], [1.35, 1])}) rotate(${inclina}deg)`,
                  textShadow: acender && nova
                    ? `0 0 70px ${p.quente}, 0 0 24px ${p.quente}`
                    : '0 0 26px rgba(255,255,255,.35)',
                  whiteSpace: 'nowrap',
                }}
              >
                {palavra}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
