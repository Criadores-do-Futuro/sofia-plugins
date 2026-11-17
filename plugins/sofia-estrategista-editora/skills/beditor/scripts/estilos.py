#!/usr/bin/env python3
"""
estilos.py — a galeria de estilos para hook, legenda, música e SFX.

Pedido do dono (2026-09-11): "de preferência pra mim no estilo vox style, mas
podendo trocar de estilo... uma galeria de estilos para hook visual, para
legendas, músicas, SFX etc, sempre deixando intuitivo e elegante".

Cada elemento (`hook`, `legenda`, `musica`, `sfx`) tem uma galeria de estilos
nomeados. `escolher()` lê `guia.estilos.<elemento>` e cai no padrão do canal
quando o guia não escolhe nada. O padrão de todo elemento é o da casa, a não
ser que a marca do projeto (`marca.py`, `estilos` no `marca.json`) já tenha
fixado outra coisa — nesse caso o padrão daqui NUNCA decide por cima do que o
dono escolheu para aquele canal ou cliente. `validar()` recusa um `guia.estilos` que aponte para um id que não
existe na galeria.

`referencias/galeria-estilos.md` é a descrição para gente ler; os valores
concretos (fonte, cor, curva, envelope de som) moram só aqui, para as duas
pontas — o texto que o diretor lê e o código que desenha — nunca divergirem.
"""

# regra que toda entrada da galeria respeita, seja qual for o estilo: contraste
# real sobre o rosto e o fundo, no máximo duas cores por camada, uma curva de
# movimento só (nunca easing misto no mesmo elemento), e nada que precise de
# legenda para ser lido — a elegância aqui é a mesma coisa que a leiturabilidade.

HOOK = {
    "vox": {
        "rotulo": "Vox — barra de cor plana, tipografia de cartaz",
        "fonte": "'Archivo Black',Impact,sans-serif",
        "peso": 900, "eixos": None, "maiusculas": True,
        "corpo_pct": 0.095, "destaque_escala": 1.0, "entrelinha": 1.12,
        "tracking": "-0.01em",
        "cor_texto": "#FFF6E7", "cor_destaque_texto": "#211315",
        "barra_normal": "rgba(33,17,21,0.82)", "barra_destaque": "#F0B95B",
        "sombra": None,
        "entrada_ease": "back.out(1.7)", "entrada_dur": 0.30,
        "saida_ease": "power2.in", "saida_dur": 0.18,
    },
    "editorial": {
        # Montserrat, a mesma da legenda `editorial`: hook e legenda sao a
        # mesma voz tipografica do canal, e estavam discordando — a legenda em
        # Montserrat e o hook em Fraunces serif. O dono apontou em 2026-09-12:
        # "nao sei em que momento se perdeu mas use montserrat no hook visual".
        "rotulo": "Editorial — Montserrat pesada, âmbar sobre creme",
        "fonte": "'Montserrat',-apple-system,sans-serif",
        # `maiusculas` aqui nao e so estilo: e a metrica que dimensiona a linha.
        # O texto do hook ja e escrito em caixa alta no guia, e caixa alta e
        # mais larga por glifo — marcar False fazia a conta subestimar a
        # largura e a linha nascia grande demais para a margem.
        "peso": 800, "eixos": None, "maiusculas": True,
        # 0,12 da largura era tipografia de legenda, nao de gancho: ocupava
        # pouco mais da metade do quadro e lia timido no feed. 0,155 enche a
        # margem — o limite real e a conta de quanto cabe, que encolhe a linha
        # longa sozinha.
        "corpo_pct": 0.155, "destaque_escala": 1.08, "entrelinha": 0.98,
        "tracking": "-0.01em",
        "cor_texto": "#EFE7D6", "cor_destaque_texto": "#F3B35C",
        "barra_normal": None, "barra_destaque": None,
        "sombra": (3, 24, 0.42),
        "entrada_ease": "power4.out", "entrada_dur": 0.52,
        "saida_ease": "power2.in", "saida_dur": 0.42,
    },
    # Medido em 2026-09-12 num corpus de 129 quadros (referencia de terceiro,
    # usada so para medir — ver `aprender-estilo.md`, secao Direitos). O dono
    # pediu o estilo pelo nome: "crie um novo estilo chamado Explicativo".
    # Caixa alta oblíqua e AMARELO-LIMAO: o hook e a legenda sao a mesma voz,
    # e nesse estilo a voz e o amarelo. Sem barra — contorno fino e sombra dura
    # fazem o trabalho por cima do rosto, que e o fundo em todo o formato.
    "explicativo": {
        "rotulo": "Explicativo — caixa alta oblíqua, amarelo-limão sobre o rosto",
        "fonte": "'Montserrat',-apple-system,sans-serif",
        "peso": 900, "eixos": None, "maiusculas": True,
        "corpo_pct": 0.125, "destaque_escala": 1.0, "entrelinha": 1.02,
        "tracking": "-0.02em",
        "cor_texto": "#FFFFFF", "cor_destaque_texto": "#E8FF3A",
        "barra_normal": None, "barra_destaque": None,
        # duas camadas: contato curto e duro (o piso da letra sobre pele) e um
        # halo largo (separa do fundo de madeira escura). Medido: o fundo tem
        # 43% do quadro abaixo de 40/255, entao o halo e o que garante a letra
        # nos 57% claros — a janela atras da cabeca.
        "sombra": [(2, 6, 0.85), (0, 18, 0.55)],
        # rapido e com quique curto: a palavra chega antes de a proxima ser dita.
        "entrada_ease": "back.out(2.4)", "entrada_dur": 0.16,
        "saida_ease": "power2.in", "saida_dur": 0.12,
    },
    "minimal": {
        "rotulo": "Minimal — sem-serifa fina, sai do caminho da imagem",
        "fonte": "'Inter',-apple-system,sans-serif",
        "peso": 900, "eixos": None, "maiusculas": True,
        "corpo_pct": 0.075, "destaque_escala": 1.0, "entrelinha": 1.15,
        "tracking": "-0.005em",
        "cor_texto": "#FFF6E7", "cor_destaque_texto": "#F0B95B",
        "barra_normal": None, "barra_destaque": None,
        "sombra": (2, 16, 0.5),
        "entrada_ease": "power3.out", "entrada_dur": 0.34,
        "saida_ease": "power2.in", "saida_dur": 0.2,
    },
    # Pedido do dono em 2026-09-27, a partir de uma referência de terceiro
    # ("VIRALIZATE CON ESTOS 5 HOOKS"): a linha de apoio pequena e branca, a
    # linha de destaque MUITO maior e em âmbar — a diferença de tamanho entre
    # as duas é o que faz o número/promessa saltar. Medido só para pegar a
    # proporção (apoio:destaque ≈ 1:1.55) e a paleta; a composição é original,
    # não copia o pacote gráfico da referência (ver provenance-and-safety.md).
    "impacto": {
        "rotulo": "Impacto — apoio pequeno branco, destaque grande em âmbar",
        "fonte": "'Montserrat',-apple-system,sans-serif",
        "peso": 800, "eixos": None, "maiusculas": True,
        # destaque_escala 1.55 é o que dá o salto de tamanho da referência;
        # 0.155 de corpo_pct é o mesmo piso do `editorial` — a linha de apoio
        # não pode nascer menor que isso ou perde peso de manchete.
        "corpo_pct": 0.155, "destaque_escala": 1.55, "entrelinha": 1.04,
        "tracking": "-0.01em",
        "cor_texto": "#F7F5F0", "cor_destaque_texto": "#FFB629",
        "barra_normal": None, "barra_destaque": None,
        # duas camadas: contato duro e curto simula o contorno grosso da
        # referência sem precisar de stroke de SVG; halo largo separa do
        # fundo do A-roll, que muda de vídeo para vídeo.
        "sombra": [(3, 4, 0.85), (0, 22, 0.5)],
        "entrada_ease": "power4.out", "entrada_dur": 0.46,
        "saida_ease": "power2.in", "saida_dur": 0.34,
    },
}

LEGENDA = {
    "vox": {
        "rotulo": "Vox — caixa alta, barra plana sob a linha",
        "fonte": "'Archivo Black',Impact,sans-serif", "peso": 900, "maiusculas": True,
        "tamanho_pct": 0.052, "tracking": "-0.005em",
        "cor_texto": "#FFF6E7", "barra": "rgba(33,17,21,0.82)", "sombra": None,
        "entrada_ease": "back.out(2)", "entrada_dur": 0.14,
    },
    # Pedido do dono em 2026-09-12, sobre o video do bEditor: "para os proximos
    # neste estilo, nao use essas barras pretas nas legendas, use apenas sombra,
    # pode manter a fonte e a cor". Entrada nova em vez de mexer na `vox`: a
    # barra plana E a definicao da vox ("barra plana sob a linha"), e outros
    # projetos ja entregues dependem dela. Fonte, cor, corpo, tracking e entrada
    # sao identicos — muda so o fundo.
    "ilustrativo": {
        "rotulo": "Ilustrativo — caixa alta da vox, sem barra, sombra em duas camadas",
        "fonte": "'Archivo Black',Impact,sans-serif", "peso": 900, "maiusculas": True,
        "tamanho_pct": 0.052, "tracking": "-0.005em",
        "cor_texto": "#FFF6E7", "barra": None,
        # contato (da o piso da letra) + halo (separa do fundo claro). O estilo
        # ilustrativo pinta os motions sobre creme #F2EFE8: sem o halo, o texto
        # creme sobre fundo creme some. Ver `_sombra` no legenda_hf.py.
        "sombra": [(3, 8, 0.62), (0, 26, 0.5)],
        "entrada_ease": "back.out(2)", "entrada_dur": 0.14,
    },
    # O par da `explicativo` do HOOK. Neste estilo a legenda NAO e acessorio: ela
    # e o unico grafismo do video, porque o formato e `dinamismo` (rosto do
    # primeiro ao ultimo quadro, zero motion). Por isso ela e grande — 0,072 da
    # altura contra 0,052 da vox — e mora sobre o peito, nao sob o queixo.
    "explicativo": {
        "rotulo": "Explicativo — caixa alta oblíqua, amarelo na palavra que pesa",
        "fonte": "'Montserrat',-apple-system,sans-serif", "peso": 900, "maiusculas": True,
        "tamanho_pct": 0.072, "tracking": "-0.02em",
        "cor_texto": "#FFFFFF", "barra": None,
        # a mesma dupla do hook: contato duro + halo largo. O fundo aqui e rosto
        # e madeira, e o rosto tem pele clara — sem o contato a letra branca
        # some na testa e no ombro iluminado.
        "sombra": [(2, 6, 0.85), (0, 18, 0.55)],
        "entrada_ease": "back.out(2.4)", "entrada_dur": 0.12,
    },
    "editorial": {
        # Pedido do dono em 2026-09-27: "as legendas estao muito grandes, sem
        # sombra, e muito embaixo no video". 0.0667 dava 128 px de corpo; 0.044
        # da ~84 px. A sombra unica (4, 12, 0.55) sumia sobre fundo claro: agora
        # sao as duas camadas do hook — contato duro + halo largo.
        "rotulo": "Editorial — Montserrat, sombra macia, sem caixa",
        "fonte": "'Montserrat',-apple-system,sans-serif", "peso": 700, "maiusculas": False,
        "tamanho_pct": 0.044, "tracking": "-0.005em",
        "cor_texto": "#F0EDE8", "barra": None,
        "sombra": [(3, 4, 0.9), (0, 20, 0.6)],
        "entrada_ease": "power3.out", "entrada_dur": 0.16,
    },
}

# musica e sfx: o envelope sintetico do trilha.py e a unica execucao real hoje
# (nao ha biblioteca de musica nem de SFX na maquina — painel/criterios.yaml
# marca essa falta). O `estilo` aqui muda a FORMA do envelope (ataque, corte,
# quanto o pulso aparece), nao troca de instrumento — trilha.py sempre sintetiza.
MUSICA = {
    "vox": {
        "rotulo": "Vox — ataque curto, pulso à frente, corta rápido",
        "sobe_mult": 0.4, "desce_mult": 0.55, "pulso_mult": 1.6,
        "ganho_mult": 0.88, "tensao_mult": 1.15,
    },
    "editorial": {
        "rotulo": "Editorial — sustentado, respiro longo, quase sem pulso",
        "sobe_mult": 1.0, "desce_mult": 1.0, "pulso_mult": 1.0,
        "ganho_mult": 1.0, "tensao_mult": 1.0,
    },
    # Cama constante e baixa, sem dinamica: no `explicativo` a musica nunca é o
    # argumento — ela só impede o silêncio entre cortes secos de soar como falha.
    # Pulso quase nulo porque o ritmo ja vem do corte e da palavra que entra.
    "explicativo": {
        "rotulo": "Explicativo — cama constante e baixa, sem picos",
        "sobe_mult": 0.55, "desce_mult": 0.7, "pulso_mult": 0.5,
        "ganho_mult": 0.7, "tensao_mult": 1.25,
    },
}

# SFX ainda não tem execução (falta a biblioteca — ver painel). O id aqui só
# registra a intenção no guia, para o dia em que a etapa existir ler a mesma
# escolha: `vox` pede stabs secos e whooshes curtos na palavra-chave e no corte;
# `editorial` pede silêncio, com efeito só quando o momento realmente pede.
SFX = {
    "vox": {"rotulo": "Vox — stab seco na palavra-chave, whoosh curto no corte"},
    "editorial": {"rotulo": "Editorial — quase nenhum; só quando o momento pede"},
    "explicativo": {"rotulo": "Explicativo — whoosh curto a cada palavra que entra, baque grave na virada"},
}

# O motion graphics inteiro — as cores, as fontes e a MATERIA da imagem gerada.
# Cada estilo aqui foi medido num corpus de treinamento, e a `origem` diz qual:
# quem mudar um valor confere na pasta, nao no gosto do dia.
#
# `tokens` alimenta o hf.py (o HTML das composicoes); `materia` entra em todo
# prompt de imagem do assets.py, e e o que faz a imagem GERADA sair no estilo
# escolhido, em vez de sair generica e brigar com a composicao.
MOTION = {
    "vox": {
        "rotulo": "Vox — colagem de papel recortado sobre jornal",
        "origem": "Treinamento/estudo de vídeo público sobre motion editorial — 16 folhas de contato + transcrição",
        "tokens": {
            "FUNDO": "#E7E0D2", "SUPERFICIE": "#D9D0BE",
            "TEXTO": "#1B1714", "TEXTO_2": "#6B6256",
            "AMBAR": "#E8A33D", "CIANO": "#6E9BC4", "DESTAQUE": "#D9641F",
            "ACIDO": "#C4552A", "NEGADO": "#B3402C",
            "NEON": "#6E9BC4", "NEON_2": "#D9641F",
            "CARTAO_VIVO": "#FFFDF6", "CARTAO_FRACO": "rgba(251,246,234,0.72)",
            "PAINEL": "rgba(251,246,234,0.92)", "CROMO": "#C9BFA9",
            "BOLHA": "#EFE8D8", "BOLHA_EU": "#DCD2BC",
            "CARTAO": "rgba(251,246,234,0.94)", "JANELA": "#FBF6EA",
            "JANELA_BARRA": "#E7E0D2", "BORDA": "rgba(27,23,20,0.18)",
            "CENTRO": "#F2ECDE", "HALO": "transparent",
            "SOMBRA_CAMADA": "drop-shadow(0 10px 16px rgba(70,55,35,0.28))",
            "SOMBRA_TEXTO": "rgba(94,74,48,0.25)",
            "FONTE_TITULO": "'Archivo Black', Impact, sans-serif",
            "FONTE_LEITURA": "'Inter', -apple-system, sans-serif",
            "FONTE_MONO": "'JetBrains Mono', ui-monospace, monospace",
        },
        "materia": (
            "Paper cutout collage on aged newsprint: torn paper shapes with visible "
            "fibrous edges and soft drop shadows, halftone black-and-white archival "
            "photography, strips of masking tape, hand-drawn annotation arrows and "
            "brackets, flat even light, muted palette of dusty blue, rust orange, "
            "amber and cream."),
        # a grade de IMAGEM do estilo. Ate 2026-09-12 havia UMA grade fixa no
        # assets.py, escrita para o `noturno` (pretos em 12/255, rim light
        # ambar/ciano, vinheta pesada) e colada DEPOIS da materia de qualquer
        # estilo. O prompt saia brigando consigo mesmo — colagem de papel clara
        # seguida de noir escuro — e o gerador obedece o final. Agora cada
        # estilo traz a sua.
        "grade": (
            "Vertical 9:16, 1080x1920, full bleed. Flat even light, no cinematic "
            "falloff: the paper is lit like a page on a table. Cream #E7E0D2 ground, "
            "printed halftone texture, visible paper fibre. No dark vignette, no rim "
            "light, no bloom, no chromatic aberration. No text anywhere in the image, "
            "no watermark, no logo."),
        # o que as folhas de contato mostram quando o plano e uma pessoa ou um
        # arquivo: silhueta de papel, e foto de arquivo em meio-tom colada com fita
        "moldes": {
            "personagem": ("A flat paper cutout silhouette of a person in dusty blue, "
                           "torn paper edges, no face, pinned onto the collage, full "
                           "bleed vertical 9:16."),
            "arquivo": ("A halftone black-and-white archival photograph taped into the "
                        "collage with strips of masking tape, full bleed vertical 9:16."),
        },
        # papel impresso: o meio-tom e de TINTA (o ponto preto do jornal), o grao
        # multiplica em vez de clarear, e nao ha vinheta preta nem grade de luz
        "acabamento": {
            "vinheta": "radial-gradient(circle,transparent 55%,rgba(94,74,48,0.20) 100%)",
            "halftone_cor": "#1B1714", "halftone_opacidade": 0.13,
            "halftone_blend": "multiply", "halftone_camada": 0.55,
            "grao_opacidade": 0.10, "grao_blend": "multiply",
            "grade_cor": None, "bokeh_cor": None,
        },
    },
    "noturno": {
        "rotulo": "Noturno — 3D luminoso branco sobre preto frio",
        "origem": "Treinamento/noturno — 2.623 frames, 12 categorias",
        "tokens": {
            "FUNDO": "#0B0B0E", "SUPERFICIE": "#131318",
            "TEXTO": "#EDEDED", "TEXTO_2": "#8A8A93",
            "AMBAR": "#FFB067", "CIANO": "#7FB4FF", "DESTAQUE": "#F5EE38",
            "ACIDO": "#A8FF53", "NEGADO": "#D4675B",
            "NEON": "#21F0D0", "NEON_2": "#7B2CFF",
            "CARTAO_VIVO": "rgba(26,30,24,0.90)", "CARTAO_FRACO": "rgba(19,19,25,0.55)",
            "PAINEL": "rgba(10,10,14,0.8)", "CROMO": "#3A3F49",
            "BOLHA": "#333944", "BOLHA_EU": "#3C4657",
            "CARTAO": "rgba(19,19,25,0.85)", "JANELA": "#262A31",
            "JANELA_BARRA": "#1D2027", "BORDA": "rgba(255,255,255,0.09)",
            "CENTRO": "#15151D", "HALO": "rgba(245,238,56,0.42)",
            "SOMBRA_CAMADA": "drop-shadow(0 4px 10px rgba(0,0,0,0.9)) drop-shadow(0 25px 40px rgba(0,0,0,0.6))",
            "SOMBRA_TEXTO": "rgba(0,0,0,0.95)",
            "FONTE_TITULO": "'Anton', 'Archivo Black', Impact, sans-serif",
            "FONTE_LEITURA": "'Inter', -apple-system, sans-serif",
            "FONTE_MONO": "'JetBrains Mono', ui-monospace, monospace",
        },
        "materia": (
            "Luminous matte-white 3D render on a cold near-black background, soft warm "
            "amber and cool cyan rim light, 85mm lens, shallow depth of field, practical "
            "light from behind and above, deep shadows, the corners fall into darkness, "
            "matte materials, no signage."),
        # esta era a GRADE fixa do assets.py: nasceu aqui e so aqui vale
        "grade": (
            "Vertical 9:16, 1080x1920, full bleed: the scene fills the frame edge to edge. "
            "Darkness comes from the light falling off, not from cutting the subject out — "
            "the blacks sit at luminance 12/255, never lifted to grey, never crushed to "
            "zero. Subject reads as bone white #CCCAC8, never blown out to pure white. Rim "
            "light only from behind and above: warm #FFB067 on one side, cool #7FB4FF on "
            "the other, no frontal light. Chromatic aberration separating edges into orange "
            "and cyan, fine film grain over the entire frame including the blacks, heavy "
            "dark vignette in the corners, large soft bloom halo. Cinematic, contemplative, "
            "lonely. No text anywhere in the image, no watermark, no logo."),
        "moldes": {
            "personagem": ("A featureless smooth white humanoid figure: no face, no eyes, "
                           "no mouth, no skin texture, matte diffuse white surface. "
                           "Shallow depth of field, 40mm lens, low camera angle looking "
                           "slightly up."),
            "cotidiano": ("Full bleed vertical 9:16 frame, 35mm lens, handheld feel, "
                          "practical light sources only, deep shadows, the lower third "
                          "falls into darkness."),
            "obra": ("Photographic reproduction lit as a museum piece, full bleed "
                     "vertical 9:16, raking light from one side, deep shadows around it."),
            "arquivo": ("Archival photographic material, full bleed vertical 9:16, 50mm "
                        "lens, practical light, dust and grain, deep shadows in the corners."),
        },
        # o acabamento medido no canal: vinheta fechada, meio-tom e grao de luz
        "acabamento": {
            "vinheta": "radial-gradient(circle,transparent 40%,rgba(0,0,0,0.92) 100%)",
            "halftone_cor": "#ffffff", "halftone_opacidade": 0.16,
            "halftone_blend": "overlay", "halftone_camada": 0.85,
            "grao_opacidade": 0.07, "grao_blend": "screen",
            "grade_cor": "rgba(255,255,255,0.03)", "bokeh_cor": "rgba(255,255,255,0.15)",
        },
    },
    "techtok": {
        "rotulo": "TechTok — imagem cheia, legenda em chip, sem grafismo desenhado",
        "origem": "Treinamento/demonstracao — 1.455 frames de 61 vídeos",
        "tokens": {
            "FUNDO": "#0A0A0B", "SUPERFICIE": "#161618",
            "TEXTO": "#FFFFFF", "TEXTO_2": "#9A9AA0",
            "AMBAR": "#F5C451", "CIANO": "#6FA8FF", "DESTAQUE": "#E63A2E",
            "ACIDO": "#38E08A", "NEGADO": "#E63A2E",
            "NEON": "#7B5CFF", "NEON_2": "#00D4FF",
            "CARTAO_VIVO": "rgba(34,34,38,0.92)", "CARTAO_FRACO": "rgba(22,22,24,0.6)",
            "PAINEL": "rgba(10,10,12,0.85)", "CROMO": "#3A3A40",
            "BOLHA": "#26262B", "BOLHA_EU": "#33333A",
            "CARTAO": "rgba(22,22,24,0.88)", "JANELA": "#1C1C20",
            "JANELA_BARRA": "#141417", "BORDA": "rgba(255,255,255,0.10)",
            "CENTRO": "#141418", "HALO": "rgba(230,58,46,0.35)",
            "SOMBRA_CAMADA": "drop-shadow(0 6px 14px rgba(0,0,0,0.8)) drop-shadow(0 26px 44px rgba(0,0,0,0.55))",
            "SOMBRA_TEXTO": "rgba(0,0,0,0.9)",
            "FONTE_TITULO": "'Inter', 'Archivo Black', Impact, sans-serif",
            "FONTE_LEITURA": "'Inter', -apple-system, sans-serif",
            "FONTE_MONO": "'JetBrains Mono', ui-monospace, monospace",
        },
        "materia": (
            "Full-frame photoreal cinematic footage, cool neutral grade, shallow depth "
            "of field, no drawn graphics and no illustration — the frame is the thing "
            "itself, filmed."),
        "grade": (
            "Vertical 9:16, 1080x1920, full bleed photoreal frame, cool neutral grade, "
            "shallow depth of field, soft natural light. No drawn graphics, no "
            "illustration. No text anywhere in the image, no watermark, no logo."),
        # imagem filmada nao leva textura de impressao: so uma vinheta suave
        "acabamento": {
            "vinheta": "radial-gradient(circle,transparent 50%,rgba(0,0,0,0.7) 100%)",
            "halftone_cor": "#ffffff", "halftone_opacidade": 0.0,
            "halftone_blend": "overlay", "halftone_camada": 0.0,
            "grao_opacidade": 0.05, "grao_blend": "screen",
            "grade_cor": None, "bokeh_cor": "rgba(255,255,255,0.10)",
        },
    },
    # Pedido do dono em 2026-09-12, com a referencia decupada quadro a quadro
    # ("deteccao de corte com limiar 0,3 nao encontrou nenhum corte duro ao
    # longo dos 42 s"). Nao e 2D nem 3D: e motion design de GRAVACAO DE TELA.
    # O miolo inteiro e um canvas branco continuo onde prints e UI de app
    # flutuam como cartoes; o que parece corte e troca de elemento sobre o
    # mesmo branco, e o que parece camera e escala digital do canvas.
    "gravacao": {
        "rotulo": "Gravação — cards de UI sobre branco contínuo",
        "origem": ("Referência do dono decupada em 2026-09-12: 42 s, 0 cortes duros no "
                   "miolo (limiar 0,3), 0 trechos de silêncio a -40 dB, um conceito a "
                   "cada 4-6 s"),
        "tokens": {
            # branco puro e o chao, nao um cinza que finge de branco: a
            # referencia nao tem horizonte, sala nem textura nenhuma
            "FUNDO": "#FFFFFF", "SUPERFICIE": "#F2F2F7",
            "TEXTO": "#0B0B0C", "TEXTO_2": "#8E8E93",
            # as cores vem SO da UI nativa, nunca de uma paleta de marca
            "AMBAR": "#FF9F0A", "CIANO": "#007AFF", "DESTAQUE": "#007AFF",
            "ACIDO": "#34C759", "NEGADO": "#FF3B30",
            "NEON": "#007AFF", "NEON_2": "#FF3B30",
            "CARTAO_VIVO": "#FFFFFF", "CARTAO_FRACO": "#F2F2F7",
            "PAINEL": "rgba(255,255,255,0.98)", "CROMO": "#C7C9CE",
            "BOLHA": "#E9E9EB", "BOLHA_EU": "#007AFF",
            "CARTAO": "#FFFFFF", "JANELA": "#FFFFFF",
            "JANELA_BARRA": "#F7F7FA", "BORDA": "rgba(60,60,67,0.13)",
            "CENTRO": "#FFFFFF", "HALO": "transparent",
            # sombra de cartao real: um contato curto e um espalhamento largo
            "SOMBRA_CAMADA": ("drop-shadow(0 2px 5px rgba(17,24,39,0.10)) "
                              "drop-shadow(0 22px 44px rgba(17,24,39,0.16))"),
            "SOMBRA_TEXTO": "rgba(0,0,0,0.55)",
            "FONTE_TITULO": "'Anton', Impact, 'Archivo Black', sans-serif",
            "FONTE_LEITURA": ("'SF Pro Text', -apple-system, 'Inter', "
                              "Helvetica, sans-serif"),
            "FONTE_MONO": "'JetBrains Mono', ui-monospace, monospace",
        },
        "materia": (
            "A real phone screenshot or app interface element floating as a single "
            "rounded-corner card on a pure white #FFFFFF seamless canvas — no room, no "
            "horizon, no table, no texture, nothing behind the card. Accent colour only "
            "from native UI chrome: iMessage blue #007AFF, iOS grey-blue, Instagram red."),
        "moldes": {
            "personagem": ("A contact avatar circle and a chat thread on a white phone "
                           "screen, floating as one rounded card on pure white, no face "
                           "detail, full bleed vertical 9:16."),
            "objeto": ("A single phone or app UI card floating on pure white #FFFFFF, "
                       "soft realistic drop shadow under it, nothing else in frame, "
                       "full bleed vertical 9:16."),
            "arquivo": ("A file thumbnail grid from a phone gallery app, floating as one "
                        "rounded card on pure white, full bleed vertical 9:16."),
        },
        # a razao do "Do not render any legible text": a tipografia deste estilo
        # e queimada por cima, em fonte de verdade. Texto vindo do gerador chega
        # torto, com glifo inventado, e briga com a legenda.
        "grade": (
            "Vertical 9:16, 1080x1920, full bleed on a pure white #FFFFFF seamless "
            "canvas: no room, no horizon, no surface, no texture, no gradient. The "
            "subject is a screen-capture element treated as a floating card: rounded "
            "corners and one soft realistic drop shadow. Flat even light, no rim light, "
            "no bloom, no vignette, no chromatic aberration, no film grain. Accent "
            "colours only from native UI: iMessage blue #007AFF, iOS grey-blue chrome, "
            "Instagram red. Keep the lower third clean and empty for burned-in captions. "
            "Confident, fast, peer-to-peer tutorial mood. Do not render any legible "
            "text: no letters, no words, no numbers, no watermark, no logo."),
        # a camera nao gira: o que empurra e o proprio canvas, em escala
        "camera": {"de": "{scale:1.0}", "para": "{scale:1.055}", "ease": "none"},
        # branco puro nao aceita acabamento nenhum: vinheta come o quadro,
        # meio-tom vira sujeira e grao vira chuvisco sobre o cartao
        "acabamento": {
            "vinheta": None,
            "halftone_cor": "#FFFFFF", "halftone_opacidade": 0.0,
            "halftone_blend": "normal", "halftone_camada": 0.0,
            "grao_opacidade": 0.0, "grao_blend": "normal",
            "grade_cor": None, "bokeh_cor": None,
        },
    },
    # Pedido do dono em 2026-09-12, com a direcao escrita por ele inteira.
    # Nao e 2D nem 3D no sentido usual: e COMPOSICAO EDITORIAL — camadas planas
    # sobre material fotografico e documento escaneado, montadas como pagina de
    # revista que se move. Zero animacao de personagem: o que anima e o
    # enquadramento e a tipografia.
    "ilustrativo": {
        "rotulo": "Ilustrativo — composição editorial 2D, tipografia em movimento",
        "origem": ("Direção escrita pelo dono em 2026-09-12 a partir de vídeo-aula "
                   "de motion no padrão Vox"),
        "tokens": {
            # tres sistemas de fundo, girando: cartela creme com textura de
            # cedula, campo editorial quase-preto, e azul-ardosia de apoio
            "FUNDO": "#F2EFE8", "SUPERFICIE": "#E6E1D6",
            "TEXTO": "#0D0D0D", "TEXTO_2": "#6B6459",
            # UM acento por quadro. Nunca dois.
            "AMBAR": "#FFE01B", "CIANO": "#2E4257", "DESTAQUE": "#FF5A7E",
            "ACIDO": "#FFE01B", "NEGADO": "#E4572E",
            "NEON": "#FF5A7E", "NEON_2": "#FFE01B",
            "CARTAO_VIVO": "#FBF9F4", "CARTAO_FRACO": "#E6E1D6",
            "PAINEL": "rgba(242,239,232,0.96)", "CROMO": "#B9B2A4",
            "BOLHA": "#E6E1D6", "BOLHA_EU": "#2E4257",
            "CARTAO": "#FBF9F4", "JANELA": "#FBF9F4",
            "JANELA_BARRA": "#E6E1D6", "BORDA": "rgba(13,13,13,0.14)",
            "CENTRO": "#F7F5EF", "HALO": "transparent",
            # recorte de foto tem sombra dura e curta, de papel sobre papel
            "SOMBRA_CAMADA": ("drop-shadow(0 4px 9px rgba(13,13,13,0.20)) "
                              "drop-shadow(0 18px 30px rgba(13,13,13,0.12))"),
            "SOMBRA_TEXTO": "rgba(13,13,13,0.22)",
            # a assinatura e a serifa de alto contraste (didone). Playfair e a
            # que existe no conjunto carregado e tem o contraste certo.
            "FONTE_TITULO": "'Playfair Display', 'Bodoni 72', Didot, serif",
            "FONTE_LEITURA": "'Inter', -apple-system, sans-serif",
            # grotesca condensada para rotulo de dado, com algarismo tabular
            "FONTE_MONO": "'Oswald', 'JetBrains Mono', ui-monospace, monospace",
        },
        "materia": (
            "Vertical 9:16 editorial motion-graphics documentary still, Vox-inspired. "
            "2D flat compositing over archival photography and scanned documents: "
            "cutout photos with hard short drop shadows, paper and document scans, "
            "tinted maps, chart overlays. Warm cream #F2EFE8 ground with faint "
            "engraved banknote texture and a soft paper fold crease, or a near-black "
            "#0D0D0D editorial field. One single accent per frame, drawn from Vox "
            "yellow #FFE01B, hot pink #FF5A7E or deep slate blue #2E4257."),
        "moldes": {
            "personagem": ("A cutout archival photograph of a person, hard short drop "
                           "shadow, layered flat over a cream banknote-textured card, "
                           "full bleed vertical 9:16."),
            "arquivo": ("A scanned document or newspaper clipping laid flat on a cream "
                        "editorial card, slight paper fold crease, full bleed vertical "
                        "9:16."),
            "obra": ("A tinted archival reproduction layered over a near-black "
                     "editorial field, single accent colour, full bleed vertical 9:16."),
        },
        "grade": (
            "Vertical 9:16, 1080x1920, full bleed. 2D editorial compositing — flat "
            "graphic layers over photographic and archival material. NO 3D, no bounce, "
            "no wobble, no lens flare, no handheld shake, no character animation. "
            "Cream #F2EFE8 ground with faint engraved banknote texture and a soft paper "
            "fold crease, OR a near-black #0D0D0D editorial field. A single accent per "
            "frame from Vox yellow #FFE01B, hot pink #FF5A7E or deep slate blue "
            "#2E4257 — never two. Cutout photography with a hard short drop shadow. "
            "Clean, authoritative, newsroom-dense, zero irony. No text anywhere in the "
            "image, no watermark, no logo."),
        # "constant motion": a camera e um escaner deslizando sobre a pagina
        # impressa. 3% de push-in em TODO plano, linear, do primeiro ao ultimo
        # quadro — e o que faz o texto parado nao ler como slide.
        "camera": {"de": "{scale:1.0}", "para": "{scale:1.03}", "ease": "none"},
        # As emendas entre planos. O dono pediu em 2026-09-12: *"os cortes
        # precisam de uma transicao que deixe a experiencia fluida"*.
        # `entre_rosto` e o dissolve curto que costura dois reenquadramentos do
        # mesmo take — sem ele o jump cut e um tranco; `com_motion` e o
        # empurrao lateral que o estilo chama de whip-slide, para quando o
        # plano ao lado e um grafico. Duracao em ms: 5 quadros e 7 quadros a
        # 30 fps. Acima disso vira novela; abaixo, nao existe.
        "transicao": {"entre_rosto": "fade", "rosto_ms": 166,
                      "com_motion": "slideleft", "motion_ms": 233},
        # papel impresso: grao de fibra multiplicando, sem vinheta preta e sem
        # meio-tom de luz (os dois sao de estilo escuro e sujam o creme)
        "acabamento": {
            "vinheta": "radial-gradient(circle,transparent 62%,rgba(13,13,13,0.14) 100%)",
            "halftone_cor": "#0D0D0D", "halftone_opacidade": 0.05,
            "halftone_blend": "multiply", "halftone_camada": 0.35,
            "grao_opacidade": 0.07, "grao_blend": "multiply",
            "grade_cor": None, "bokeh_cor": None,
        },
    },
}

GALERIA = {"hook": HOOK, "legenda": LEGENDA, "motion": MOTION,
           "musica": MUSICA, "sfx": SFX}
# O hook volta ao `editorial` por pedido do dono (2026-09-11, depois de ver o
# vox no hook): "o hook visual prefiro como estava antes do vox, quero vox pra
# motion". O vox continua na galeria, e agora e o padrao do motion.
PADRAO = {"hook": "editorial", "legenda": "vox", "motion": "vox",
          "musica": "vox", "sfx": "vox"}


def escolher(guia, elemento, padrao_canal=None):
    """o id escolhido para `elemento`: o guia decide; sem isso, o padrão da
    marca (`estilos` no marca.json da marca do guia ou da máquina — ver
    marca.py); sem isso, o padrão da casa."""
    ids = (guia or {}).get("estilos") or {}
    if ids.get(elemento):
        return ids[elemento]
    if padrao_canal is None:
        try:
            import marca
            mc = marca.resolver(nome=(guia or {}).get("marca"))
            padrao_canal = mc.estilo(elemento) if mc else None
        except SystemExit:          # marca pedida e ausente: o estilo da casa, sem parar o render
            padrao_canal = None
    return padrao_canal or PADRAO[elemento]


def acabamento(nome):
    """as camadas analogicas (vinheta, meio-tom, grao, grade, bokeh) do estilo
    de motion. Sao do estilo porque vinheta preta sobre papel claro come o
    quadro inteiro, e meio-tom branco sobre papel some."""
    return (MOTION.get(nome) or MOTION[PADRAO["motion"]])["acabamento"]


def tokens(guia, elemento, padrao_canal=None):
    """o dicionário de valores do estilo escolhido, pronto para desenhar"""
    nome = escolher(guia, elemento, padrao_canal)
    galeria = GALERIA.get(elemento) or {}
    return galeria.get(nome) or galeria[PADRAO[elemento]]


def validar(guia):
    erros = []
    for elemento, nome in ((guia or {}).get("estilos") or {}).items():
        if elemento not in GALERIA:
            erros.append(f"estilos.{elemento}: elemento não existe na galeria "
                         f"(só {', '.join(GALERIA)})")
        elif nome not in GALERIA[elemento]:
            erros.append(f"estilos.{elemento}: `{nome}` não está na galeria — "
                         f"opções: {', '.join(GALERIA[elemento])}")
    return erros
