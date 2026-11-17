import React from 'react';
import {AbsoluteFill, Img, staticFile, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano, PRESETS} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';
import {Papel} from '../lib/Papel';

/**
 * retrato — a pessoa citada, em preto e branco de papel de jornal.
 *
 * So entra imagem de licenca livre VERIFICADA, e a licenca aparece na tarja.
 * Nunca gere o rosto de uma pessoa real: sem imagem livre, o componente cai
 * sozinho na ficha tipografica, que e honesta e fica boa.
 * Ver referencias/enriquecimento.md.
 */
export const Retrato: React.FC<{plano: Plano; preset: keyof typeof PRESETS; duracao: number}> = ({
  plano, preset, duracao,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const p = useGrade();
  const r = plano.retrato;

  if (!r) {
    return (
      <AbsoluteFill style={{backgroundColor: p.fundo, color: p.alerta, alignItems: 'center',
        justifyContent: 'flex-end', paddingBottom: height * 0.3, fontFamily: 'IBM Plex Mono, monospace', fontSize: 28}}>
        {plano.id}: plano `retrato` sem ficha. Rode o enriquecimento.
      </AbsoluteFill>
    );
  }

  const temImagem = r.status === 'encontrado' && !!plano.asset && !!r.licenca;
  const esc = interpolate(frame, [0, duracao], [1, 1.05], {extrapolateRight: 'clamp'});
  const rot = -1.2;

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: `rotate(${rot}deg) scale(${esc})`, width: width * 0.62}}>
        <Papel escuro>
          {temImagem ? (
            <div style={{position: 'relative', width: '100%', aspectRatio: '4 / 5', overflow: 'hidden'}}>
              <Img
                src={staticFile(plano.asset as string)}
                style={{
                  width: '100%', height: '100%', objectFit: 'cover',
                  // jornal: cinza puro, contraste alto, pretos fechados
                  filter: 'grayscale(1) contrast(1.55) brightness(1.06) sepia(.12)',
                }}
              />
              {/* trama de impressao por cima do rosto */}
              <div style={{position: 'absolute', inset: 0, mixBlendMode: 'multiply', opacity: 0.55,
                backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(0,0,0,.9) 1px, transparent 1.4px)',
                backgroundSize: '4px 4px'}} />
            </div>
          ) : (
            // ficha tipografica: o caminho honesto quando nao ha imagem livre.
            // O aviso de licenca fica no plano.json e no console, nunca queimado
            // no quadro — quem assiste nao precisa da nossa contabilidade.
            <div style={{padding: '70px 54px 62px', textAlign: 'left'}}>
              <div style={{fontFamily: 'IBM Plex Mono, monospace', fontSize: 20, letterSpacing: '.16em',
                textTransform: 'uppercase', opacity: 0.45, marginBottom: 30}}>
                {r.instituicao || 'pesquisador'}
              </div>
              <div style={{fontFamily: 'Fraunces, Georgia, serif', fontWeight: 800, fontSize: 76,
                lineHeight: 1.02, marginBottom: 18}}>
                {r.nome}
              </div>
              {r.anos ? (
                <div style={{fontFamily: 'Fraunces, Georgia, serif', fontSize: 38, opacity: 0.7}}>{r.anos}</div>
              ) : null}
            </div>
          )}
          {/* a tarja so existe quando ha imagem: sem ela, o nome ja esta na ficha
              e repetir seria mostrar a mesma coisa duas vezes */}
          {temImagem ? (
            <div style={{padding: '20px 26px', borderTop: '2px solid rgba(0,0,0,.25)',
              fontFamily: 'IBM Plex Mono, monospace', fontSize: 19, lineHeight: 1.45, opacity: 0.72}}>
              <div style={{fontSize: 24, opacity: 1}}>{r.nome}{r.anos ? ` · ${r.anos}` : ''}</div>
              {r.instituicao ? <div>{r.instituicao}</div> : null}
              <div style={{opacity: 0.7}}>{r.fonte} · {r.licenca}</div>
            </div>
          ) : null}
        </Papel>
      </div>
    </AbsoluteFill>
  );
};
