export type TipoPlano =
  /** o vídeo original, quem fala na tela — o padrão quando ha material filmado */
  | 'fala'
  | 'cartela' | 'dado' | 'tela' | 'objeto' | 'personagem'
  | 'broll' | 'hibrido' | 'tvcrt' | 'arquivo' | 'obra'
  | 'cotidiano' | 'pessoa' | 'paper' | 'retrato' | 'palavras';

export type Camera = 'push-in' | 'pull-out' | 'parallax' | 'estatico';

/** como o plano chega */
export type Entrada = 'corte' | 'deslizar' | 'subir' | 'escalar';
/** como o plano sai — a saida acontece por cima do plano seguinte */
export type Saida = 'corte' | 'varrer' | 'empurrar' | 'implodir' | 'apagar';

export type Plano = {
  id: string;
  t0: number;
  t1: number;
  duracaoMs: number;
  tipo: TipoPlano;
  fala: string;
  texto: string;
  camera: Camera;
  entrada?: Entrada;
  saida?: Saida;
  /** palavras: a lista que entra uma a uma, no ritmo da fala */
  palavras?: string[];
  /**
   * palavras: o que fica atras, cinza e apagado — a lista de onde a palavra
   * nova NAO veio. E o que faz a intrusao doer: ela aparece no lugar de uma
   * lista que o espectador reconhece e onde ela nunca esteve.
   */
  fantasmas?: string[];
  /** palavras: a palavra nova acende em quente, maior que todas as outras */
  acender?: boolean;
  /** o que se move neste plano, em uma frase — escrito pelo enriquecedor */
  movimento?: string;
  asset: string | null;
  prompt: string;
  fonte?: string;
  licenca?: string;
  /** dado: barras, so com numero que tem fonte */
  serie?: {rotulo: string; valor: number}[];
  /** dado: curva que se desenha da esquerda para a direita (0..1 no eixo y) */
  curva?: number[];
  /** tela: forma antiga — so larguras de balao, sem texto. Ainda aceita. */
  conversa?: {lado: 'esq' | 'dir'; largura: number}[];
  apagarMeio?: boolean;
  /**
   * tela: a interface desenhada. `chat` e uma coluna de mensagens (com
   * `apagarMeio`, o miolo se perde); `terminal` e um comando que se digita e
   * uma resposta que aparece. O que se escreve aqui NUNCA e a transcricao da
   * fala — e o que a fala nao diz e a tela mostra.
   */
  tela?: {
    modo: 'chat' | 'terminal';
    /** o que aparece na barra da janela */
    titulo?: string;
    /** chat: as mensagens, de cima para baixo */
    mensagens?: {lado: 'esq' | 'dir'; texto: string}[];
    /** chat: o miolo da coluna some no lugar */
    apagarMeio?: boolean;
    /**
     * terminal: o que ja estava digitado quando o plano comeca. Serve para
     * uma frase que atravessa varios planos: cada corte continua de onde o
     * anterior parou, em vez de recomecar do zero e virar falha de montagem.
     */
    prefixo?: string;
    /** terminal: o que e digitado NESTE plano, depois do prefixo */
    comando?: string;
    /** terminal: as linhas de resposta, uma a uma */
    linhas?: string[];
    /** terminal: trecho que se acende em quente dentro das linhas */
    destaque?: string;
  };
  /** o que este momento pede que se veja, em uma frase (enriquecimento) */
  ideia?: string;
  /** paper: ficha bibliografica real. Ficha e fato; fac-simile da pagina, nao. */
  paper?: {
    titulo: string; autores: string; publicacao: string; ano: number;
    doi?: string; url?: string; citacao?: string; verificado?: boolean;
  };
  /** retrato: so com licenca livre verificada. Sem imagem -> ficha tipografica. */
  retrato?: {
    nome: string; anos?: string; instituicao?: string;
    imagemUrl?: string; licenca?: string; fonte?: string;
    status: 'encontrado' | 'sem-imagem-livre';
  };
  /** false quando o plano ja carrega o proprio texto na tela */
  legenda?: boolean;
  /**
   * aroll+motion: o grafico entra POR CIMA de quem fala, num painel na
   * metade de baixo do quadro, sem cobrir o rosto. E o caso do gesto que o
   * grafico continua.
   */
  sobreFala?: boolean;
  /** motions que sao a mesma peca em estados diferentes (guia.familia) */
  familia?: string;
  /** o que mudou nesta aparicao da familia */
  estado?: string;
  /** por que este plano e assim — vem do guia, para a timeline mostrar */
  porque?: string;
};

/**
 * Planos que ja mostram texto no quadro. A legenda falada e SUPRIMIDA em cima
 * deles: ler a mesma coisa duas vezes rouba a atencao de ambas.
 */
export const TEM_TEXTO_PROPRIO: TipoPlano[] = ['cartela', 'paper', 'dado', 'tela', 'retrato', 'palavras'];

export type PlanoDoVideo = {
  versao: number;
  preset: 'noturno' | 'editorial';
  fps: number;
  largura: number;
  altura: number;
  duracaoMs: number;
  duracaoEmFrames: number;
  /**
   * vídeo original dentro de public/, quando ha material filmado.
   * Ele da imagem aos planos `fala` e a trilha de audio do vídeo inteiro.
   * Sem ele o projeto e 100% motion graphics e sai mudo (so audio separado).
   */
  fonteVideo?: string;
  /** quanto do original foi cortado antes do t0=0 do transcript */
  fonteOffsetMs?: number;
  /**
   * voz ja tratada dentro de public/ (scripts/acabamento.py).
   * Quando existe, e ela que toca — o audio embutido no vídeo fica de fora,
   * porque o Remotion so sabe multiplicar volume, nao corrigir timbre.
   */
  fonteAudio?: string;
  /** cama musical dentro de public/, por baixo da voz o video inteiro */
  trilha?: string;
  /** volume da cama, 0..1. Ela nunca disputa com a fala. */
  trilhaVolume?: number;
  planos: Plano[];
};

/** referencias/linguagem-visual.md */
export const PRESETS = {
  noturno: {
    fundo: '#0C0C0C',
    sujeito: '#CCCAC8',
    texto: '#FFFFFF',
    quente: '#FFB067',
    frio: '#7FB4FF',
    ambar: '#FFA33A',
    alerta: '#C94850',
    grao: 0.4,
    aberracao: 2,
    vinheta: 0.8,
  },
  editorial: {
    fundo: '#D9D8D1',
    sujeito: '#373639',
    texto: '#373639',
    quente: '#DBD653',
    frio: '#2E82F7',
    ambar: '#DBD653',
    alerta: '#C94850',
    grao: 0.05,
    aberracao: 1,
    vinheta: 0.06,
  },
} as const;

/** areas seguras do feed — nenhum texto fora desta faixa */
export const SEGURO = {topo: 0.12, base: 0.22, legenda: 0.46};
