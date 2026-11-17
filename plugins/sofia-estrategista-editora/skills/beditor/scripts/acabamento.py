#!/usr/bin/env python3
"""
acabamento.py — tratamento de voz e de imagem que o Remotion nao faz.

voz: rumor, chiado, barro em 240 Hz, presenca em 3,2 kHz, de-esser,
compressor, limitador, -14 LUFS. O Remotion so multiplica volume; corrigir
timbre e trabalho de filtro.

imagem: contraste no meio-tom (gamma), dessaturacao e nitidez. Nitidez nao
existe em CSS e `contrast()` levanta o preto junto — entao entra no arquivo.

cama: a musica nao tem volume "certo" em abstrato; ela fica N dB abaixo da
voz, medida em LUFS. Chutar esse numero foi o erro que fez a musica parecer
alta quando a voz e que estava baixa. Volume so nao basta: voz e musica disputam
3-7 kHz, onde mora a consoante. A cama passa por um low pass e abaixa um pouco
enquanto ha fala (ducking); nas pausas ela volta.
"""
import subprocess

import cor as _cor

VOZ = ",".join([
    "highpass=f=85",                    # rumor de mesa e ar-condicionado
    "afftdn=nf=-26:tn=1",               # chiado de sala, leve
    "equalizer=f=240:t=q:w=1.0:g=-2.5",  # o barro que abafa a consoante
    "equalizer=f=3200:t=q:w=1.2:g=3.0",  # presenca: o que faz entender a palavra
    "highshelf=f=5400:g=2",              # brilho acima de 5,4 kHz; o de-esser segura o "s"
    "deesser=i=0.4",
    "acompressor=threshold=-21dB:ratio=3:attack=8:release=180:makeup=2",
    # latency=1: o limitador olha 5 ms a frente e, sem isso, atrasa a voz 5 ms
    "alimiter=limit=0.95:latency=1",
    "loudnorm=I=-14:TP=-1.5:LRA=11",
])
# Contraste e nitidez do A-roll. Os numeros subiram uma vez, a pedido do dono do
# canal: rosto de celular em 4K aguenta mais micro-contraste do que a curva
# timida original, e a grade de `compor.py` levanta o preto para 12/255 depois —
# o que se ganha aqui em separacao nao vira preto esmagado la. Se um dia parecer
# duro demais, mexa em `contrast`, nao em `unsharp`: halo em volta do rosto e
# irreversivel e aparece justamente no plano em que o rosto sustenta sozinho.
# `saturation` e `gamma_b` ficam em 1.0 de proposito: a cor gravada e a cor que
# sai. Dessaturar de leve e empurrar o azul parecia inofensivo e nao era — junto
# com a grade antiga, deixava a pele rosada. Aqui so se mexe em luminancia.
#
# Esses numeros agora sao o PADRAO DE FABRICA de `cor.py`, nao uma constante: o
# editor ajusta a grade no painel de revisao e a escolha vira preferencia do
# canal (`~/.beditor/cor.json`) ou deste video (`guia.cor`). `IMAGEM` continua
# existindo porque ha chamada antiga apontando para ela — e a grade de fabrica.
IMAGEM = _cor.filtro(_cor.COR_PADRAO)
SEPARACAO_DB = 18.0

# A cama abre espaco para a voz em frequencia, nao so em volume. Dois polos em
# cascata = 24 dB/oitava: em 6 kHz a musica ja esta ~24 dB abaixo do que era, e
# a faixa de 3-7 kHz da consoante fica livre. Soa "debaixo d'agua" sozinha;
# atras da voz, some o embolado. Corte mais alto devolve brilho a musica e
# tira clareza da fala — suba so se a trilha for o assunto do trecho.
CAMA_LOWPASS_HZ = 3000
CAMA = f"lowpass=f={CAMA_LOWPASS_HZ},lowpass=f={CAMA_LOWPASS_HZ}"
# Ducking: a voz tratada (-14 LUFS) comanda o compressor da cama. Limiar abaixo
# do nivel da fala e acima do chiado; ~4-6 dB de reducao durante a frase,
# release longo para a musica nao "respirar" entre palavras.
DUCKING = "threshold=0.04:ratio=3:attack=20:release=400"


def mistura_voz_cama(voz, cama, saida="[a]", extras=()):
    """fragmento de filter_complex: `cama` (rotulo, ja com volume) abaixa
    enquanto `voz` fala; soma voz, cama e `extras` (swoosh) em `saida`. O low
    pass nao entra aqui: ele ja vem gravado na cama (`CAMA`), para o render do
    Remotion receber a mesma musica."""
    return (f"{voz}asplit=2[_vm][_vs];{cama}[_vs]sidechaincompress={DUCKING}[_cd];"
            f"[_vm][_cd]{''.join(extras)}amix=inputs={2 + len(extras)}:duration=first:normalize=0{saida}")


def encoder(crf, preset="medium", altura=1920):
    """os argumentos de video do ffmpeg.

    `BEDITOR_RAPIDO=1` troca o libx264 pelo encoder de hardware do Mac. Serve
    para a passada de REVISAO, em que o editor julga corte, sincronia e hook —
    e nenhuma dessas coisas muda com o encoder. O master fica no libx264, que
    e onde a qualidade e o produto. Nao inverta os dois."""
    import os
    if os.environ.get("BEDITOR_RAPIDO"):
        taxa = {1920: "12M", 3840: "40M"}.get(altura, "12M")
        return ["-c:v", "h264_videotoolbox", "-b:v", taxa, "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p"]


def cadeia_voz(cortes=None):
    """`VOZ` com os cortes desta voz (`voz.py`) logo depois da limpeza e antes
    da presenca: tirar o fanhoso primeiro, realcar depois — realce em cima de
    ressonancia so a deixa mais alta."""
    if not cortes:
        return VOZ
    passos = VOZ.split(",")
    extra = [f"equalizer=f={c['f']}:t=q:w={c.get('q', 4)}:g={c['g']}" for c in cortes]
    i = next(i for i, p in enumerate(passos) if p.startswith("equalizer=f=3200"))
    return ",".join(passos[:i] + extra + passos[i:])


def atraso_da_cadeia_ms(entrada, cadeia, inicio_s=None, dur_s=20.0):
    """quanto a cadeia atrasa a voz, medido nela mesma: correlacao cruzada de
    um trecho falado antes e depois dos filtros.

    Medido em 2026-09-27: o `afftdn` segura a voz 25 ms (processa em janelas)
    e o `alimiter` sem `latency=1`, 5 ms. Juntos davam 30 ms de voz atrasada
    em relacao a boca — num A-roll que estava em sincronia na amostra. Medir
    em vez de tabelar: trocar um filtro da cadeia muda o numero."""
    import numpy as np
    SR = 48000

    def pcm(ss, af=None):
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{dur_s:.3f}", "-i", str(entrada),
               "-vn", "-ac", "1", "-ar", str(SR), *(["-af", af] if af else []), "-f", "f32le", "-"]
        return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)

    ss = inicio_s if inicio_s is not None else 30.0
    ref = pcm(ss)
    if len(ref) < SR * 4:                      # video curto: mede do comeco
        ss, ref = 0.0, pcm(0.0)
    fil = pcm(ss, cadeia)
    M, jan = SR // 10, 2 * SR
    # a janela de 2 s mais falada, longe das pontas (o loudnorm e o
    # compressor mudam o ganho, nao o tempo; a correlacao nao liga para ganho)
    passos = range(M, max(M + 1, len(ref) - jan - M), SR // 2)
    s0 = max(passos, key=lambda s: float((ref[s:s + jan] ** 2).mean()))
    seg = ref[s0:s0 + jan]
    b = fil[s0 - M:s0 + jan + M]
    if len(b) < jan + 2 * M:
        return 0.0
    cc = np.correlate(b, seg, "valid")
    return (int(np.argmax(np.abs(cc))) - M) / SR * 1000


def tratar_voz(entrada, saida, cortes=None):
    """a voz tratada, com o atraso da cadeia DESCONTADO: sem isso a voz sai
    atrasada em relacao a boca (ver `atraso_da_cadeia_ms`). O corte e na
    cabeca e o mesmo tanto volta de silencio no fim, para a duracao nao mudar."""
    cadeia = cadeia_voz(cortes)
    atraso = atraso_da_cadeia_ms(entrada, cadeia)
    if atraso > 0.5:
        d = atraso / 1000
        cadeia += f",atrim=start={d:.5f},asetpts=PTS-STARTPTS,apad=pad_dur={d:.5f}"
        print(f"voz: a cadeia atrasa {atraso:.1f} ms — descontado", flush=True)
    elif atraso < -0.5:
        raise RuntimeError(f"a cadeia de voz ADIANTA {atraso:.1f} ms — algo esta errado nela")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-vn", "-af", cadeia,
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(saida)], check=True)


def tratar_imagem(entrada, saida, fps=30, grade=None):
    """`grade` e a ficha de cor ja resolvida (`cor.da_ficha(guia)`). Sem ela,
    vale a preferencia do canal — e, na falta dela, a grade de fabrica."""
    vf = _cor.filtro(grade) if grade is not None else _cor.filtro(_cor.da_ficha())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(entrada), "-vf", vf, "-an",
                    *encoder(18, "medium"),
                    "-vsync", "cfr", "-r", str(fps), str(saida)], check=True)


def lufs(arquivo):
    """loudness integrado (ebur128) — a unica medida que corresponde ao que o
    ouvido chama de alto. Pico nao serve: a cama tem pico alto e volume baixo,
    a voz o contrario."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arquivo), "-vn",
                        "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    for linha in r.stderr.splitlines():
        if linha.strip().startswith("I:"):
            return float(linha.split()[1])
    raise RuntimeError(f"nao consegui medir {arquivo}")


def volume_da_cama_por_lufs(voz_lufs, cama_lufs, separacao_db=SEPARACAO_DB):
    alvo = voz_lufs - separacao_db
    return round(min(1.0, 10 ** ((alvo - cama_lufs) / 20)), 3)


def volume_da_cama(voz, cama, separacao_db=SEPARACAO_DB):
    return volume_da_cama_por_lufs(lufs(voz), lufs(cama), separacao_db)
