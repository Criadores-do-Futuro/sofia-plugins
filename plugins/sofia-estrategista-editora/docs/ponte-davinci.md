# Preparação para DaVinci Resolve

O módulo `beditor.davinci_plan.translate` prepara argumentos para o MCP
`media_pool.append_to_timeline`; ainda não executa a edição, cria projeto ou
salva a timeline. Fontes precisam estar na Media Pool, suas taxas de quadros
precisam ser obtidas do editor e cada pista precisa ter índice conhecido.

`beditor.davinci_preflight.prepare` também recebe um retrato fornecido pelo
chamador, com `timeline_id`, `version_token`, `complete: true` e itens contendo
`kind`, `track_index`, `start_frame` e `end_frame` relativos à timeline. O token
é uma identificação da coleta, não uma versão nativa do Resolve. A função recusa
colisões conhecidas na mesma pista e não bloqueia alterações concorrentes. Ela
não consulta a timeline nem confere sozinha que o retrato seja completo ou atual.
Releia o projeto imediatamente antes da operação, salve e confira os itens após
salvar: a documentação factual do MCP relata que sobreposições podem ser
ignoradas e que itens de uma chamada com erro podem desaparecer no save.

O MCP informa que `endFrame` é exclusivo em medições feitas no Resolve Studio
21.0. A versão instalada, as taxas mistas e os tempos precisam ser verificados
na máquina real. Em 12 de novembro de 2026, nesta máquina, o MCP respondeu que
não havia instância ativa e a tentativa de inicialização retornou
`RESOLVE_NOT_RUNNING`. Não houve edição nem verificação de timeline do Resolve.
