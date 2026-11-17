import React, {createContext, useContext} from 'react';
import {PRESETS} from './tipos';

/** os campos da grade, com tipo largo — o preset e `as const`, o estilo
    aprendido nao e, e os dois precisam caber aqui */
export type Grade = {
  fundo: string; sujeito: string; texto: string;
  quente: string; frio: string; ambar: string; alerta: string;
  grao: number; aberracao: number; vinheta: number;
};

const Ctx = createContext<Grade>(PRESETS.noturno);

/**
 * A grade em vigor. Vem do preset fechado (`noturno`/`editorial`) ou do estilo
 * APRENDIDO — o campo `grade` do plano.json, medido por scripts/aprender.py.
 * Ver referencias/aprender-estilo.md.
 */
export const useGrade = () => useContext(Ctx);

export const ProvedorDeGrade: React.FC<{
  preset: keyof typeof PRESETS;
  grade?: Partial<Grade>;
  children: React.ReactNode;
}> = ({preset, grade, children}) => (
  <Ctx.Provider value={{...PRESETS[preset], ...(grade ?? {})}}>{children}</Ctx.Provider>
);
