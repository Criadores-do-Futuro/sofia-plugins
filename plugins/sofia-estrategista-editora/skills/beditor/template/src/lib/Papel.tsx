import React from 'react';

/**
 * A folha: papel de jornal envelhecido, meio-tom visivel, sombra de contato.
 * Usada por `paper` e `retrato` — o material que faz o documento parecer objeto,
 * nao camada.
 */
export const Papel: React.FC<{children: React.ReactNode; escuro?: boolean}> = ({children, escuro = false}) => (
  <div
    style={{
      position: 'relative',
      background: escuro ? '#C9C6BD' : '#DEDACF',
      color: '#1B1A18',
      boxShadow: '0 22px 44px rgba(0,0,0,.55), 0 4px 10px rgba(0,0,0,.4)',
      overflow: 'hidden',
    }}
  >
    {children}
    {/* fibra do papel */}
    <div
      style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.5, mixBlendMode: 'multiply',
        backgroundImage:
          'repeating-linear-gradient(0deg, rgba(0,0,0,.05) 0 1px, transparent 1px 3px),' +
          'radial-gradient(circle at 30% 20%, rgba(0,0,0,.07), transparent 60%)',
      }}
    />
    {/* meio-tom de impressao */}
    <div
      style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.28, mixBlendMode: 'multiply',
        backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(0,0,0,.85) 0.8px, transparent 1px)',
        backgroundSize: '3px 3px',
      }}
    />
  </div>
);
