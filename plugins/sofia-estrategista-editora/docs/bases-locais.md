# Bases locais identificadas

Levantamento em 5 de novembro de 2026. A finalidade abaixo foi inferida dos
arquivos locais; não implica que cada capacidade esteja testada e operacional.
O catálogo detalhado de caminhos e movimentações fica no inventário do SSD,
fora deste repositório. Clones distintos continuam identificados separadamente.

| Base | Contribuição a estudar | Limite para este produto |
| --- | --- | --- |
| bEditor — plugin ativo | Direção em PT-BR, treinamento, fluxo CapCut, qualidade e sincronia | Preservar decisões e verificar contratos atuais |
| bEditor — laboratório | Histórico de arquitetura e referências preservadas | Não confundir código antigo com integração CapCut implementada |
| bEditor — `mcp/capcut-bridge` | Servidor MCP local que prepara projetos CapCut Desktop com cortes, áudio, legendas e keyframes, segundo seu README | Exige CapCut fechado, cria projeto novo e não controla a interface nem exporta; operação não retestada neste levantamento |
| Sofia e suas variantes | Método, público/bolha, formatos, roteiro e crítica | Fonte editorial; variantes têm públicos e superfícies diferentes |
| Skill de Editor | Plugin de direção de vídeo curto em PT-BR e planos por especialidade | Plano de edição não prova execução na timeline |
| Bento Coprodutor | Orquestração de trabalho criativo | Reaproveitar somente o que serve ao fluxo de edição |
| video-use | Fluxo conversacional e operações de edição | Avaliar ideias sem adotar seu renderizador como montagem final |
| bCut / Cutpilot | Timeline comandada por IA, ferramentas e revisão | Editor próprio; usar como referência de interação e contratos |
| Bento Editor | Edição local e interface | Editor próprio, complementar à pesquisa |
| Herk / HyperFrames Student Kit | Planejamento, narrativa visual e revisão | Método e formatos continuam Sofia; execução final continua CapCut |
| corte-viral e motion-vox | Decupagem, controle de qualidade e linguagem visual | Pastas de referência sem Git próprio nesta instalação |
| Open Generative AI e projetos associados | Catálogos, geração de assets e trabalhos assíncronos | Geração fornece materiais, não substitui a timeline |
| ComfyUI | Geração e preparação de materiais | Integração opcional, conforme capacidade e autorização |
| Claude Blender Skills e Animated Shorts | Planejamento de cenas e geração visual | Referências para assets, com licenças a revisar |
| Treinamento bEditor e Catálogo Audiovisual | Acervo, procedência e repertório | Acervo não é automaticamente material autorizado para redistribuição |

Antes de incorporar qualquer componente: conferir licença, origem, alterações
locais e contrato de execução. Nenhum desses repositórios foi incorporado como
dependência automática ou publicado junto deste projeto.

## Duas rotas a comparar

O laboratório já contém uma ponte local para rascunhos do CapCut Desktop,
enquanto a skill ativa descreve o plugin oficial e o editor colaborativo Web.
Essas rotas têm contratos diferentes. Antes de escolher a distribuição do novo
plugin, provar retomada, alteração da mesma timeline, suporte a versões e
exportação em cada rota; a existência de uma importação de draft não resolve
sozinha o ciclo de revisão conversacional.

## Referências adicionadas

- [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion): skill de animação artística por código, com estilos visuais; avaliar aplicações em personagens, ícones e assets do CapCut.
- [earshot](https://github.com/Leonxlnx/earshot): análise de áudio e apoio à seleção e criação de efeitos sonoros.
- [video-director](https://github.com/win4r/video-director): direção e revisão de vídeos.

Esses projetos são referências separadas, clonadas no SSD; suas capacidades e licenças devem ser avaliadas antes da integração. Nenhuma delas comprova montagem automática no CapCut.

- [DaVinci Resolve MCP](https://github.com/samuelgursky/davinci-resolve-mcp): integração MCP com o DaVinci Resolve; requer instalação e configuração do Resolve para operar uma timeline.
- [Plugin oficial CapCut para Codex](https://sf16-sg.tiktokcdn.com/obj/eden-sg/962370eh7nupenuhbo/capcut_codex_plugin/SKILL.md): instruções oficiais de instalação; nesta máquina foi instalado e conectado. A distribuição fornecida é um pacote, não um repositório Git informado.
