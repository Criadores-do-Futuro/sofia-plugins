import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {Plano, PRESETS} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';

/**
 * tela — a UI e desenhada, nunca gerada.
 * Nao imite conta, marca ou produto de terceiro: desenhe uma interface generica.
 *
 * Dois modos, porque a fala so pede dois:
 *
 *   chat      uma coluna de mensagens. Serve para falar de conversa, de
 *             historico, de contexto que cresce — e, com `apagarMeio`, de
 *             contexto que se perde no meio.
 *   terminal  uma janela com um comando que se digita e uma resposta que
 *             aparece. Serve para documentar um comando real em vez de
 *             ilustrar com um simbolo qualquer.
 *
 * A janela precisa ter LUZ. Uma interface desenhada quase na cor do fundo e
 * indistinguivel de tela preta — o espectador ve o video morrer e volta. O
 * painel fica claramente acima do fundo, e o corpo do texto e grande: este
 * quadro tem 1080 de largura e vai ser visto num telefone na mao.
 */

const PAINEL = '#262A31';
const CROMO = '#31363F';
const MONO = 'IBM Plex Mono, monospace';

export const Tela: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, duracao,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const p = useGrade();

  const t = plano.tela;
  // `conversa` e a forma antiga (so larguras, sem texto): continua valendo
  const legado = plano.conversa ?? [];
  const modo = t?.modo ?? (legado.length > 0 ? 'chat' : 'terminal');
  const apagarMeio = t?.apagarMeio ?? plano.apagarMeio ?? false;

  const janela = (titulo: string, filhos: React.ReactNode) => (
    <AbsoluteFill style={{backgroundColor: p.fundo, alignItems: 'center', justifyContent: 'center'}}>
      <div
        style={{
          width: width * 0.88,
          maxHeight: height * 0.7,
          borderRadius: 26,
          overflow: 'hidden',
          border: `2px solid ${p.sujeito}33`,
          background: PAINEL,
          boxShadow: `0 40px 120px rgba(0,0,0,.6), 0 0 120px ${p.frio}18`,
        }}
      >
        <div style={{
          height: 84, background: CROMO, display: 'flex', alignItems: 'center',
          gap: 14, padding: '0 30px', borderBottom: `1px solid ${p.sujeito}22`,
        }}>
          {[p.alerta, p.ambar, p.frio].map((c) => (
            <div key={c} style={{width: 18, height: 18, borderRadius: 9, background: `${c}AA`}} />
          ))}
          <div style={{marginLeft: 18, fontFamily: MONO, fontSize: 26, color: `${p.sujeito}99`}}>
            {titulo}
          </div>
        </div>
        <div style={{padding: '40px 38px 46px'}}>{filhos}</div>
      </div>
      <div style={{
        position: 'absolute', bottom: height * 0.11, opacity: 0.4, color: p.sujeito,
        fontFamily: MONO, fontSize: 22,
      }}>
        interface desenhada · não é captura de um app real
      </div>
    </AbsoluteFill>
  );

  // ---- chat ---------------------------------------------------------------
  if (modo === 'chat') {
    const msgs = t?.mensagens
      ?? legado.map((m) => ({lado: m.lado, texto: '·'.repeat(Math.max(3, Math.round(m.largura / 6)))}));
    // as mensagens entram uma a uma; a coluna sobe conforme enche
    const passo = (duracao * 0.55) / Math.max(1, msgs.length);
    const sobe = interpolate(frame, [0, duracao], [0, height * 0.06], {extrapolateRight: 'clamp'});
    const some = interpolate(frame, [duracao * 0.4, duracao * 0.85], [1, 0.06], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    const a = Math.floor(msgs.length * 0.3), b = Math.ceil(msgs.length * 0.72);

    return janela(t?.titulo ?? 'conversa', (
      <div style={{display: 'flex', flexDirection: 'column', gap: 22,
        transform: `translateY(${-sobe}px)`}}>
        {msgs.map((m, i) => {
          if (frame < i * passo) return null;
          const entra = interpolate(frame - i * passo, [0, 6], [0, 1], {
            extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
          });
          const meio = apagarMeio && i >= a && i < b;
          return (
            <div
              key={i}
              style={{
                alignSelf: m.lado === 'dir' ? 'flex-end' : 'flex-start',
                maxWidth: '78%',
                padding: '22px 28px',
                borderRadius: 22,
                background: m.lado === 'dir' ? `${p.frio}2E` : '#343943',
                border: `1px solid ${p.sujeito}2A`,
                fontFamily: MONO, fontSize: 34, lineHeight: 1.35,
                color: p.sujeito,
                opacity: (meio ? some : 1) * entra,
                filter: meio ? `blur(${(1 - some) * 5}px)` : undefined,
              }}
            >
              {m.texto}
            </div>
          );
        })}
      </div>
    ));
  }

  // ---- terminal -----------------------------------------------------------
  // O comando se digita; as linhas de resposta sobem depois, uma a uma. O que
  // se digita e o COMANDO, nunca a transcricao da fala: repetir na tela o que
  // o audio ja diz gasta a atencao duas vezes pelo mesmo conteudo.
  const prefixo = t?.prefixo ?? '';
  const comando = t?.comando ?? (t ? '' : plano.texto);
  const linhas = t?.linhas ?? [];
  const fimComando = duracao * (linhas.length ? 0.38 : 0.7);
  const cursor = Math.floor(interpolate(frame, [0, fimComando], [0, comando.length], {
    extrapolateRight: 'clamp',
  }));
  const digitando = cursor < comando.length;
  const passoLinha = (duracao * 0.45) / Math.max(1, linhas.length);

  const pinta = (texto: string) => {
    const d = t?.destaque;
    if (!d || !texto.includes(d)) return texto;
    const [antes, ...resto] = texto.split(d);
    return (
      <>
        {antes}
        <span style={{color: p.quente, textShadow: `0 0 30px ${p.quente}66`}}>{d}</span>
        {resto.join(d)}
      </>
    );
  };

  return janela(t?.titulo ?? 'entrada', (
    <div style={{fontFamily: MONO, fontSize: 42, lineHeight: 1.4, color: p.sujeito}}>
      <div>
        <span style={{color: p.ambar, marginRight: 16}}>{'>'}</span>
        {prefixo}
        {comando.slice(0, cursor)}
        {digitando || linhas.length === 0 ? (
          <span style={{opacity: frame % 30 < 15 ? 1 : 0, color: p.ambar}}>▌</span>
        ) : null}
      </div>
      {linhas.map((linha, i) => {
        const nasce = fimComando + i * passoLinha;
        if (frame < nasce) return null;
        const e = interpolate(frame - nasce, [0, 8], [0, 1], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
        });
        return (
          <div
            key={i}
            style={{
              marginTop: i === 0 ? 34 : 16,
              paddingLeft: 8,
              fontSize: 36,
              color: `${p.sujeito}D0`,
              opacity: e,
              transform: `translateY(${(1 - e) * 16}px)`,
            }}
          >
            {pinta(linha)}
          </div>
        );
      })}
    </div>
  ));
};
