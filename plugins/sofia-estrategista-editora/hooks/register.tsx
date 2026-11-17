import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Etapa, Janela, Quadro } from '../types'

// Painel da Sofia Estrategista: quantos cards há em cada etapa do planejamento no site e quanto já foi
// usado das janelas de 5 horas e de 7 dias do Claude, com quanto falta para cada uma zerar.
// Só roda onde há mods (Claude Code): no site, no app de conversa e no Codex este arquivo fica parado.

const PAINEL = 'sofia-painel'
const TITULO = 'Sofia Estrategista'
// Troque a marca quando o formato guardado mudar: um reload mantém o que a versão anterior guardou.
const quadro = atom({ plugin: 'sofia-estrategista-editora', key: 'quadro' } as const, null, { shape: 'quadro-1' })
const janelas = atom({ plugin: 'sofia-estrategista-editora', key: 'janelas' } as const, [], { shape: 'janelas-1' })

// O conector: a chave dele no .mcp.json deste plugin (a primeira), e os nomes com que o /mcp lista o
// mesmo conector quando a pessoa o ligou pelo site do Claude em vez do plugin.
const CONECTORES = ['sofia-estrategista', 'claude.ai Sofia Estrategista', 'Sofia Estrategista']
// O nome com que o /mcp lista o conector deste plugin: é o que a pessoa procura na lista para entrar.
const NOME_NO_MCP = 'plugin:sofia-estrategista-editora:sofia-estrategista'
const ETAPAS = ['Brainstorming', 'Estruturar', 'Revisar', 'Lapidar', 'Gravar']
const CORES_DAS_ETAPAS = ['magenta', 'blue', 'cyan', 'yellow', 'green']
const NOME_DA_JANELA: Record<string, string> = { five_hour: 'Sessão de 5 horas', seven_day: 'Semana (7 dias)' }
const RELER_A_CADA_MS = 5 * 60 * 1000

// ---------- leitura ----------

/** As etapas a partir da resposta de planejamento_quadro: os dados estruturados, ou o texto "### Etapa (n)". */
export function etapasDaResposta(estruturado: unknown, texto: string): { perfil?: string; etapas: Etapa[] } {
  const dados = estruturado as
    | {
        perfilId?: string
        colunas?: { rotulo?: string; cards?: unknown[] }[]
        perfis?: { id?: string; arroba?: string; rede?: string }[]
      }
    | undefined
  if (dados && Array.isArray(dados.colunas)) {
    const p = Array.isArray(dados.perfis) ? dados.perfis.find((x) => x.id === dados.perfilId) : undefined
    return {
      perfil: p?.arroba ? comArroba(p.arroba, p.rede) : dados.perfilId,
      etapas: dados.colunas.map((c) => ({ rotulo: c.rotulo ?? '?', total: Array.isArray(c.cards) ? c.cards.length : 0 })),
    }
  }
  const etapas: Etapa[] = []
  for (const linha of texto.split('\n')) {
    const m = /^###\s+(.+?)\s+\((\d+)\)\s*$/.exec(linha.trim())
    const rotulo = m?.[1]
    if (rotulo && ETAPAS.includes(rotulo)) etapas.push({ rotulo, total: Number(m?.[2] ?? 0) })
  }
  const id = /^##\s+Quadro do perfil\s+(.+)$/m.exec(texto)?.[1]?.trim()
  // Na lista do fim do texto: "- `id`: nome (@arroba, rede)".
  const linha = id ? new RegExp('^- `' + id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '`: .*\\(([^,()]+), ([^()]+)\\)\\s*$', 'm').exec(texto) : null
  const perfil = linha?.[1] ? comArroba(linha[1], linha[2]) : id
  return { perfil, etapas }
}

/** "@mechamedebento · Instagram", com o @ na frente mesmo que o site tenha guardado sem. */
export function comArroba(arroba: string, rede?: string): string {
  const a = arroba.trim()
  const comAt = a.startsWith('@') ? a : `@${a}`
  return rede?.trim() ? `${comAt} · ${rede.trim()}` : comAt
}

/** As janelas do Claude que o painel mostra, na ordem 5 horas e 7 dias. */
export function janelasDoUso(limites: readonly { kind: string; percentUsed: number; resetsAt?: string }[]): Janela[] {
  return limites
    .filter((l) => l.kind in NOME_DA_JANELA)
    .sort((a, b) => (a.kind === 'five_hour' ? -1 : b.kind === 'five_hour' ? 1 : 0))
    .map((l) => {
      const zera = l.resetsAt ? Date.parse(l.resetsAt) : NaN
      return { tipo: l.kind, usado: l.percentUsed, ...(Number.isFinite(zera) ? { zeraEm: zera } : {}) }
    })
}

// ---------- desenho ----------

/** Uma barra de `largura` blocos com `fracao` (0 a 1) preenchida. */
export function barra(fracao: number, largura: number): [string, string] {
  const cheios = Math.max(0, Math.min(largura, Math.round(fracao * largura)))
  return ['█'.repeat(cheios), '░'.repeat(largura - cheios)]
}

/** Quanto falta para a janela zerar: "1h 48min", "3d 4h", "12min". */
export function quantoFalta(ms: number): string {
  if (ms <= 0) return 'agora'
  const min = Math.ceil(ms / 60000)
  const dias = Math.floor(min / 1440)
  const horas = Math.floor((min % 1440) / 60)
  const minutos = min % 60
  if (dias > 0) return `${dias}d ${horas}h`
  if (horas > 0) return `${horas}h ${String(minutos).padStart(2, '0')}min`
  return `${minutos}min`
}

const corDoUso = (p: number) => (p >= 85 ? 'red' : p >= 60 ? 'yellow' : 'green')
const hora = (ms: number) => {
  const d = new Date(ms)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

// O nome com que o conector respondeu da última vez, e se uma leitura já está em andamento.
let servidor: string | null = null
let lendo = false

/** Lê o quadro em segundo plano: uma falha na leitura nunca trava a ferramenta nem a sessão. */
function lerEmSegundoPlano($: EngineInterface) {
  lerQuadro($).catch(() => undefined)
}

/** Lê o quadro no conector e guarda as contagens por etapa (ou o motivo de não ter lido). */
async function lerQuadro($: EngineInterface) {
    if (lendo) return
    lendo = true
    try {
      const agora = await $.clock.now()
      let motivo = `O conector Sofia Estrategista não está ligado. Digite /mcp, escolha ${NOME_NO_MCP} e entre com o e-mail do curso.`
      const candidatos = servidor ? [servidor] : CONECTORES
      for (const nome of candidatos) {
        const ligado = await $.mcp.connect(nome).catch(() => null)
        if (!ligado || !ligado.isConnected) continue
        try {
          const r = await $.mcp.call(ligado.server, 'planejamento_quadro', {})
          const texto = r.content.map((b) => (b.type === 'text' && typeof b.text === 'string' ? b.text : '')).join('\n')
          if (r.isError) {
            motivo = texto.slice(0, 160) || 'O conector não devolveu o quadro.'
            continue
          }
          const { perfil, etapas } = etapasDaResposta(r.structuredContent, texto)
          if (etapas.length === 0) continue
          servidor = ligado.server
          const lido: Quadro = { situacao: 'ok', perfil: perfil ?? 'sem perfil', etapas, lidoEm: agora }
          await update($, quadro, () => lido)
          atualizarStatus($)
          return
        } catch {
          motivo = `O conector Sofia Estrategista não respondeu. Digite /mcp, escolha ${ligado.server} e entre de novo com o e-mail do curso.`
        }
      }
      servidor = null
      const semConector: Quadro = { situacao: 'sem-conector', motivo, lidoEm: agora }
      await update($, quadro, () => semConector)
    } finally {
      lendo = false
    }
  }

/** A linha curta da barra de status, para quando o painel não cabe na tela. */
async function atualizarStatus($: EngineInterface) {
    const q = await read($, quadro)
    const js = await read($, janelas)
    const partes: string[] = []
    if (q?.situacao === 'ok') partes.push(`${q.etapas.reduce((s, e) => s + e.total, 0)} cards`)
    for (const j of js) partes.push(`${j.tipo === 'five_hour' ? '5h' : '7d'} ${Math.round(j.usado)}%`)
    $.ui.status(partes.length ? `Sofia · ${partes.join(' · ')}` : undefined)
}

export const register: Register = (on) => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'sofia-painel', description: 'Abre o painel da Sofia: cards por etapa e uso do Claude' })
    const uso = await $.session.usage()
    await update($, janelas, () => janelasDoUso(uso.rateLimits))
    lerEmSegundoPlano($)
    $.clock.every(RELER_A_CADA_MS, () => lerEmSegundoPlano($))
    $.ui.open({ id: PAINEL, title: TITULO }).catch(() => undefined)
    return next(e)
  })

  on('command.run', { command: 'sofia-painel' }, async ($) => {
    await $.ui.open({ id: PAINEL, title: TITULO })
    lerEmSegundoPlano($)
    return { text: 'Painel da Sofia aberto.' }
  })

  // O uso muda a cada resposta: o engine avisa quando uma janela anda um ponto inteiro.
  on('session.measure', async ($, e, next) => {
    if (e.changed.includes('rateLimits')) {
      await update($, janelas, () => janelasDoUso(e.rateLimits))
      await atualizarStatus($)
    }
    return next(e)
  })

  // Depois de uma ferramenta do planejamento, o quadro pode ter mudado: lê de novo.
  on('tool.call', async ($, e, next) => {
    const r = await next(e)
    if (/planejamento_|referencia_salvar/.test(e.tool) && !/planejamento_quadro$/.test(e.tool)) lerEmSegundoPlano($)
    return r
  })

  on('ui.render', { component: 'Pane', requestId: PAINEL }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const q = await read($, quadro)
    const js = await read($, janelas)
    const agora = await $.clock.now()
    const colunas = e.viewport?.columns ?? 60
    const larguraDaBarra = Math.max(8, Math.min(30, colunas - 30))

    const maior = q?.situacao === 'ok' ? Math.max(1, ...q.etapas.map((x) => x.total)) : 1
    const total = q?.situacao === 'ok' ? q.etapas.reduce((s, x) => s + x.total, 0) : 0

    return (
      <Box flexDirection="column" paddingX={1}>
        <Box justifyContent="space-between">
          <Text bold color="magenta">✦ Sofia Estrategista</Text>
          {q && <Text dimColor>lido às {hora(q.lidoEm)}</Text>}
        </Box>

        <Box marginTop={1} flexDirection="column">
          <Box>
            <Text bold>Planejamento</Text>
            {q?.situacao === 'ok' && <Text color="magenta">{`  ${q.perfil}`}</Text>}
          </Box>
          {q === null && <Text dimColor>Lendo o quadro no site…</Text>}
          {q?.situacao === 'sem-conector' && <Text color="yellow">{q.motivo}</Text>}
          {q?.situacao === 'ok' &&
            q.etapas.map((etapa, i) => {
              const [cheio, vazio] = barra(etapa.total / maior, larguraDaBarra)
              return (
                <Box key={etapa.rotulo}>
                  <Text>{etapa.rotulo.padEnd(14)}</Text>
                  <Text color={CORES_DAS_ETAPAS[i % CORES_DAS_ETAPAS.length]}>{cheio}</Text>
                  <Text dimColor>{vazio}</Text>
                  <Text bold> {String(etapa.total).padStart(3)}</Text>
                </Box>
              )
            })}
          {q?.situacao === 'ok' && <Text dimColor>{total === 1 ? '1 card no quadro' : `${total} cards no quadro`}</Text>}
        </Box>

        <Box marginTop={1} flexDirection="column">
          <Text bold>Uso do Claude</Text>
          {js.length === 0 && <Text dimColor>Aparece depois da primeira resposta, em planos com limite de uso.</Text>}
          {js.map((j) => {
            const [cheio, vazio] = barra(j.usado / 100, larguraDaBarra)
            return (
              <Box key={j.tipo} flexDirection="column">
                <Box>
                  <Text>{(NOME_DA_JANELA[j.tipo] ?? j.tipo).padEnd(18)}</Text>
                  <Text color={corDoUso(j.usado)}>{cheio}</Text>
                  <Text dimColor>{vazio}</Text>
                  <Text bold color={corDoUso(j.usado)}> {String(Math.round(j.usado)).padStart(3)}%</Text>
                </Box>
                <Text dimColor>
                  {'  '}
                  {j.zeraEm ? `zera em ${quantoFalta(j.zeraEm - agora)} (às ${hora(j.zeraEm)})` : 'sem horário de reinício'}
                  {` · faltam ${Math.max(0, 100 - Math.round(j.usado))}%`}
                </Text>
              </Box>
            )
          })}
        </Box>
      </Box>
    )
  })
}
