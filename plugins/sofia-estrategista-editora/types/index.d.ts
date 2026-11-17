/** Uma etapa do quadro: o nome da coluna e quantos cards ela tem. */
export type Etapa = { rotulo: string; total: number }

/** O quadro lido do conector, ou o motivo de não ter lido. */
export type Quadro =
  | { situacao: 'ok'; perfil: string; etapas: Etapa[]; lidoEm: number }
  | { situacao: 'sem-conector'; motivo: string; lidoEm: number }

/** Uma janela de uso do Claude: 5 horas ou 7 dias. */
export type Janela = { tipo: string; usado: number; zeraEm?: number }

declare module 'claude-code' {
  interface PluginState {
    'sofia-estrategista-editora': {
      quadro: Shaped<Quadro | null>
      janelas: Shaped<Janela[]>
    }
  }
}
