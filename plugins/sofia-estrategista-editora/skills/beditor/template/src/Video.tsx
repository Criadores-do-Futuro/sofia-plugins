import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import type {Caption} from '@remotion/captions';
import {PlanoDoVideo, PRESETS} from './lib/tipos';
import {msParaFrames} from './lib/ritmo';
import {FiltrosGrade, Grao, Vinheta, Bloom, Halftone, Grade2026} from './lib/Grade';
import {ProvedorDeGrade, type Grade} from './lib/GradeContext';
import {Cartela} from './planos/Cartela';
import {Objeto} from './planos/Objeto';
import {Dado} from './planos/Dado';
import {Tela} from './planos/Tela';
import {Paper} from './planos/Paper';
import {Retrato} from './planos/Retrato';
import {Palavras} from './planos/Palavras';
import {Fala} from './planos/Fala';
import {Movimento, FRAMES_SAIDA, FRAMES_ENTRADA} from './lib/Movimento';
import {Legenda} from './Legenda';

export type Props = PlanoDoVideo & {
  captions: Caption[];
  /** estilo aprendido: sobrescreve o preset campo a campo (aprender-estilo.md) */
  grade?: Partial<Grade>;
  /** variante 2026: recorte + grade de linhas + halftone */
  variante2026?: boolean;
  destacarPalavra?: boolean;
};

export const Video: React.FC<Props> = ({
  preset, planos, captions, grade, fonteVideo, fonteAudio, fonteOffsetMs = 0,
  trilha, trilhaVolume = 0.55, duracaoEmFrames,
  variante2026 = false, destacarPalavra = false,
}) => {
  const {fps} = useVideoConfig();
  const p = {...PRESETS[preset], ...(grade ?? {})};

  return (
    <ProvedorDeGrade preset={preset} grade={grade}>
    <AbsoluteFill style={{backgroundColor: p.fundo}}>
      <FiltrosGrade preset={preset} />

      {/* uma unica trilha para o vídeo inteiro: a voz nao pode cortar junto
          com a imagem, senao o motion graphics picota a fala.
          Havendo `fonteAudio`, e a voz ja tratada — equalizada, comprimida e
          normalizada — que entra; o audio bruto do vídeo nunca toca junto. */}
      {fonteAudio || fonteVideo ? (
        <Audio
          src={staticFile((fonteAudio ?? fonteVideo) as string)}
          trimBefore={fonteAudio ? 0 : msParaFrames(fonteOffsetMs, fps)}
        />
      ) : null}

      {/* a cama entra e sai em fade, para nao aparecer nem sumir de repente */}
      {trilha ? (
        <Audio
          src={staticFile(trilha)}
          volume={(f) =>
            trilhaVolume *
            interpolate(f, [0, fps, duracaoEmFrames - fps * 2, duracaoEmFrames],
              [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
          }
        />
      ) : null}

      {/* conteudo — bloom, aberracao e curva na ordem de linguagem-visual.md */}
      <AbsoluteFill style={{filter: 'url(#bed-curva)'}}>
        <AbsoluteFill style={{filter: 'url(#bed-aberracao)'}}>
          <Bloom>
            <AbsoluteFill>
              {planos.map((plano, indice) => {
                // acumulo da enumeracao: junta as palavras dos planos
                // `palavras` contiguos anteriores
                const acumulado: string[] = [];
                if (plano.tipo === 'palavras') {
                  for (let k = indice - 1; k >= 0 && planos[k].tipo === 'palavras'; k--) {
                    acumulado.unshift(...(planos[k].palavras ?? []));
                  }
                }
                const de = msParaFrames(plano.t0, fps);
                const dur = Math.max(1, msParaFrames(plano.duracaoMs, fps));
                const comum = {plano, preset, duracao: dur};
                const Componente =
                  plano.tipo === 'fala' && fonteVideo
                    ? <Fala plano={plano} duracao={dur} fonte={fonteVideo} offsetMs={fonteOffsetMs} />
                  // sem material filmado, `fala` nao tem o que mostrar: cai na cartela
                  : plano.tipo === 'fala' ? <Cartela {...comum} />
                  : plano.tipo === 'cartela' ? <Cartela {...comum} />
                  : plano.tipo === 'dado' ? <Dado {...comum} />
                  : plano.tipo === 'tela' ? <Tela {...comum} />
                  : plano.tipo === 'paper' ? <Paper {...comum} />
                  : plano.tipo === 'retrato' ? <Retrato {...comum} />
                  : plano.tipo === 'palavras'
                    ? <Palavras plano={plano} duracao={dur} acumulado={acumulado} />
                  : <Objeto {...comum} />;
                // A saida se estende por cima do plano seguinte, revelando-o.
                // E a entrada do SEGUINTE tambem precisa de chao: um plano que
                // entra em fade sobre nada entra em fade a partir do preto —
                // um piscar de tela morta a cada motion graphics. Entao este
                // plano segura embaixo enquanto o proximo aparece.
                const proximo = planos[indice + 1];
                const chao =
                  proximo && proximo.entrada && proximo.entrada !== 'corte'
                    ? FRAMES_ENTRADA : 0;
                const cauda = Math.max(
                  plano.saida && plano.saida !== 'corte' ? FRAMES_SAIDA : 0,
                  chao,
                );
                // aroll+motion: o grafico entra num painel na metade de baixo,
                // por cima de quem fala — o rosto continua em cima
                const conteudo = plano.sobreFala && fonteVideo ? (
                  <>
                    <Fala plano={plano} duracao={dur} fonte={fonteVideo} offsetMs={fonteOffsetMs} />
                    <AbsoluteFill style={{top: '50%', height: '46%', left: '4%', width: '92%',
                      borderRadius: 28, overflow: 'hidden', boxShadow: '0 30px 90px rgba(0,0,0,.55)'}}>
                      {Componente}
                    </AbsoluteFill>
                  </>
                ) : Componente;
                return (
                  <Sequence key={plano.id} from={de} durationInFrames={dur + cauda}
                    name={`${plano.id} ${plano.tipo}`}>
                    <Movimento entrada={plano.entrada} saida={plano.saida} duracao={dur}>
                      {conteudo}
                    </Movimento>
                  </Sequence>
                );
              })}
            </AbsoluteFill>
          </Bloom>
        </AbsoluteFill>
      </AbsoluteFill>

      {variante2026 ? <Grade2026 /> : null}
      <Vinheta forca={p.vinheta} />
      <Grao intensidade={p.grao} />
      {variante2026 ? <Halftone /> : null}

      {/* a legenda recebe o mesmo tratamento do quadro, mas por cima do grao
          para nao perder nitidez de glifo */}
      <AbsoluteFill style={{filter: 'url(#bed-aberracao)'}}>
        <Legenda captions={captions} preset={preset} planos={planos} destacar={destacarPalavra} />
      </AbsoluteFill>
    </AbsoluteFill>
    </ProvedorDeGrade>
  );
};
