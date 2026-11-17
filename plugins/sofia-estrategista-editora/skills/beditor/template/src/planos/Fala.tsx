import React from 'react';
import {AbsoluteFill, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Plano} from '../lib/tipos';
import {useGrade} from '../lib/GradeContext';

/**
 * fala — o vídeo original, a pessoa falando.
 *
 * Este é o plano padrão, nao o plano de emergencia. Motion graphics entra
 * onde ilustra alguma coisa; onde nao ilustra, o rosto de quem fala sustenta
 * a atencao melhor do que uma imagem generica ou uma cartela de texto.
 *
 * O corte vem do proprio material: `trimBefore` posiciona a fonte no mesmo
 * instante da fala, entao a boca continua sincronizada com o audio.
 */
export const Fala: React.FC<{
  plano: Plano;
  duracao: number;
  /** caminho do vídeo original dentro de public/ */
  fonte: string;
  /** quanto do original foi cortado antes do t0 do transcript */
  offsetMs?: number;
}> = ({plano, duracao, fonte, offsetMs = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useGrade();

  const inicio = Math.max(0, Math.round(((plano.t0 - offsetMs) / 1000) * fps));

  // o material ja tem o movimento de quem fala: a camera so acompanha de leve
  const escala =
    plano.camera === 'push-in'
      ? interpolate(frame, [0, duracao], [1.0, 1.06], {extrapolateRight: 'clamp'})
      : plano.camera === 'pull-out'
        ? interpolate(frame, [0, duracao], [1.06, 1.0], {extrapolateRight: 'clamp'})
        : 1;

  return (
    <AbsoluteFill style={{backgroundColor: p.fundo, overflow: 'hidden'}}>
      <OffthreadVideo
        src={staticFile(fonte)}
        trimBefore={inicio}
        // o audio da composicao inteira vem de uma unica trilha em Video.tsx;
        // aqui a imagem entra muda para nao duplicar a voz
        volume={0}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${escala})`,
          // O grosso da grade — contraste no meio-tom, dessaturacao e nitidez —
          // ja esta gravado no arquivo por acabamento.py, porque CSS nao sabe
          // dar nitidez e `contrast()` levanta o preto junto. Aqui fica so o
          // fio de ajuste que casa o filmado com o desenhado.
          filter: 'saturate(0.96) contrast(1.02)',
        }}
      />
    </AbsoluteFill>
  );
};
