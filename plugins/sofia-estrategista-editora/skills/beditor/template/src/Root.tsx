import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Video, type Props} from './Video';
import plano from '../public/plano.json';
import captions from '../public/captions.json';

const dados = plano as unknown as Omit<Props, 'captions'>;

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Video"
    component={Video}
    durationInFrames={dados.duracaoEmFrames}
    fps={dados.fps}
    width={dados.largura}
    height={dados.altura}
    defaultProps={{...dados, captions: captions as Props['captions']}}
  />
);
