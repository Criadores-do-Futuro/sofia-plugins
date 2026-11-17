"""O corte de silêncio nas TRÊS posições, e a folga que o split edit gasta.

    python3 silencio.py <dados.json> <take.wav>

Cabeça, cauda e miolo. A versão anterior deste script só tratava a cabeça, e as
outras duas cobraram no mesmo projeto:

  CABEÇA  corta em «início da voz − 120 ms». O limiar de energia é RELATIVO ao
          próprio pedaço (8% do percentil 90 dele). Limiar fixo passa batido por
          vogal solta — «O GTA VI…» ficou com 1,45 s de ar na abertura do vídeo,
          porque uma vogal tem uma fração da energia de uma plosiva.

  CAUDA   450 ms depois do fim da última palavra, SEMPRE. O transcritor marca o
          fim da PALAVRA antes do fim do SOM dela; cortar no fim da palavra
          decepa a queda da vogal. Foi o que comeu «quente» e «gente», e o dono
          ouviu os dois.

  MIOLO   buraco de voz ≥ 500 ms vira pausa de 250 ms. É a posição que se
          esquece e a pior das três: buraco no meio de um momento não é cabeça de
          pedaço nenhum, então um aperto que só trata cabeças passa por ele sem
          ver. O maior que escapou tinha 4,65 s.

A pausa de 250 ms FICA. O alvo não é zero silêncio: fala sem respiro cansa e some
a pontuação. O ouvido lê 250 ms como respiração e 600 ms como buraco.

E cada emenda sai carimbada com `folgaMs` (quanto silêncio ela removeu) e
`folgaLimpa` (se esse silêncio é mesmo só silêncio). O split edit só pode gastar
folga limpa: emenda onde o diretor tirou uma FRASE tem fala na folga, e usá-la
mostraria em imagem a frase que o corte jogou fora.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

SR = 16000
GUARDA_CABECA = 120      # ms antes da voz — o que a plosiva precisa, e nada mais
GUARDA_CAUDA = 450       # TETO da cauda: nunca se leva mais do que isto
DECAIMENTO_MIN = 150     # e nunca se corta antes disto depois da última palavra
RESPIRO_SAIDA = 180      # ar depois que o som já caiu — o que sobra da cauda
BURACO_MIN = 500
PAUSA = 250
JANELA_FOLGA = 600       # o quanto antes da voz que entra se exige silêncio
FRACAO, PISO = 0.08, 0.0015


def envelope(wav):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav),
                          "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    j = int(0.01 * SR)
    k = len(a) // j
    return np.sqrt((a[:k * j].reshape(k, j) ** 2).mean(1))


def cortar(d, wav):
    env = envelope(wav)
    # o limiar sai das regiões COM SINAL. Numa linha do tempo virtual (vários
    # takes costurados com silêncio digital nos vãos) a maior parte do arquivo é
    # zero, e um p90 tirado do arquivo inteiro daria zero.
    vivo = env[env > 1e-5]
    LIM = max(PISO, float(np.percentile(vivo if len(vivo) else env, 90)) * FRACAO)

    def voz(de, ate):
        i0, i1 = int(de / 10), min(int(ate / 10), len(env))
        tr = env[i0:i1]
        lim = max(PISO, float(np.percentile(tr, 90)) * FRACAO) if len(tr) > 20 else LIM
        return tr > lim, i0

    def inicio(de, ate):
        v, i0 = voz(de, ate)
        for i in range(len(v) - 6):
            if v[i] and v[i:i + 6].sum() >= 5:
                return (i0 + i) * 10
        return None

    def buracos(de, ate):
        v, i0 = voz(de, ate)
        corrida, saida = 0, []
        for i, f in enumerate(~v):
            if f:
                corrida += 1
            else:
                if corrida * 10 >= BURACO_MIN:
                    saida.append(((i0 + i - corrida) * 10, (i0 + i) * 10))
                corrida = 0
        return saida

    def fim_do_som(palavra_ate, teto):
        """Onde a cauda termina: depois do SOM cair, não 450 ms fixos.

        A guarda de 450 ms nasceu de um defeito real — cortar no fim da palavra
        decepou «quente» e «gente», porque o transcritor marca o fim da PALAVRA
        antes do fim do SOM. Só que 450 ms fixos entregam muito mais do que a
        queda da vogal precisa, e na emenda essa sobra encosta na guarda de
        cabeça de 120 ms do pedaço seguinte. As duas somam, e num vídeo medido
        isso deixou 21 buracos acima de meio segundo — o mesmo defeito que a
        guarda existe para evitar, com o sinal trocado.

        A queda da vogal não é uma duração: é um evento, e o envelope sabe
        quando ele acabou.
        """
        i0 = int(palavra_ate / 10)
        i1 = min(int(teto / 10), len(env))
        i = i0
        while i < i1 and env[i] > LIM:
            i += 1
        return int(min(teto, max(palavra_ate + DECAIMENTO_MIN, i * 10 + RESPIRO_SAIDA)))

    def folga_limpa(prev_ate, de, folga):
        """Os últimos JANELA_FOLGA ms antes da voz que entra são só silêncio?

        É a janela que o split edit consome. Perguntar pelo buraco INTEIRO
        removido reprova toda emenda entre takes diferentes, onde o buraco
        contém a cauda descartada do take anterior — cauda que o corte já jogou
        fora e que a imagem nunca vê.
        """
        if folga < 200:
            return False
        i1 = int(de / 10)
        i0 = max(int(prev_ate / 10), i1 - JANELA_FOLGA // 10)
        if i1 - i0 < 10:
            return False
        return bool((env[i0:i1] > LIM).sum() * 10 < 60)

    def cauda_calada(ate):
        """quantos ms de silêncio contínuo há no FIM do pedaço que termina em `ate`.

        É o segundo teto do split edit, e o que eu tinha esquecido. A folga limpa
        garante que o silêncio REMOVIDO é silêncio; não garante que o pedaço que
        SAI já parou de falar. Num corte de miolo a cauda tem 250 ms e a queda da
        vogal ocupa os primeiros ~100: adiantar a imagem 240 ms ali põe a boca
        fechada do pedaço novo sobre a voz ainda soando do pedaço velho — que é
        exatamente o erro de sincronia que o split edit existe para não cometer.
        """
        i = min(int(ate / 10), len(env)) - 1
        n = 0
        while i >= 0 and env[i] <= LIM and n < 200:
            n += 1
            i -= 1
        return n * 10

    W = d["palavras"]
    pedacos = []
    for m in d["momentos"]:
        if m["decisao"] == "cortar":
            continue
        de0 = m["deMs"] - m.get("arCabecaMs", 0)
        ate0 = m["ateMs"]
        v = inicio(de0, ate0)
        de = max(de0, v - GUARDA_CABECA) if v else de0
        dentro = [w for w in W if w["de"] >= de0 and w["ate"] <= ate0 and w["ate"] > w["de"]]
        if dentro:
            ate = fim_do_som(dentro[-1]["ate"],
                             min(ate0 + GUARDA_CAUDA, dentro[-1]["ate"] + GUARDA_CAUDA))
        else:
            ate = ate0 + GUARDA_CAUDA

        # as recusas de DENTRO do momento entram junto com os buracos: para o
        # montador as duas são a mesma coisa — um intervalo que não vai ao
        # corte. A diferença é de origem, e mora no `porque` de cada uma. É
        # assim que a falsa partida sai (ver `escutar.py`).
        corte_em = []
        for ci in d.get("cortesInternos", []):
            if de < ci["deMs"] and ci["ateMs"] < ate:
                corte_em.append((ci["deMs"], ci["ateMs"]))
        for h0, h1 in buracos(de, ate):
            if h0 <= de + 50 or h1 >= ate - 50:
                continue
            fim, comeco = h0 + PAUSA, h1 - GUARDA_CABECA
            if comeco - fim < 150:
                continue
            if any(a <= fim <= b or a <= comeco <= b for a, b in corte_em):
                continue          # esse silêncio já vai embora com a recusa
            corte_em.append((fim, comeco))
        corte_em.sort()

        p = de
        for fim, comeco in corte_em:
            pedacos.append({"de": p, "ate": fim, "id": m["id"], "take": m.get("take")})
            p = comeco
        pedacos.append({"de": p, "ate": ate, "id": m["id"], "take": m.get("take")})

    tab, cursor, ganho = [], 0, 0
    for i, p in enumerate(pedacos):
        folga = (p["de"] - pedacos[i - 1]["ate"]) if i else 0
        # folga negativa não é silêncio removido: é REMONTAGEM. Acontece quando
        # um trecho relido entra antes da explicação que no take veio antes
        # dele. Não recebe split edit e não entra na conta do ar economizado.
        remontagem = folga < 0
        # o take vai na linha porque o render lê o A-roll por quadro LOCAL do take
        # (`pasta_aroll`), e num vídeo de vários takes o momento sozinho não diz qual
        tab.append({"brutoDe": p["de"], "brutoAte": p["ate"], "momento": p["id"], "take": p["take"],
                    "doDiretor": True, "corteDe": cursor,
                    "corteAte": cursor + (p["ate"] - p["de"]),
                    "folgaMs": max(0, folga), "remontagem": remontagem,
                    "folgaLimpa": (folga_limpa(pedacos[i - 1]["ate"], p["de"], folga)
                                   if i and not remontagem else False),
                    "caudaCaladaMs": cauda_calada(pedacos[i - 1]["ate"]) if i else 0})
        cursor += p["ate"] - p["de"]
        if not remontagem:
            ganho += folga
    return tab, ganho


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    # `dados.json` mora em `edicao/`; a telemetria do projeto, em `edicao/oficina/`
    dados = Path(sys.argv[1]).resolve()
    with oficina.Cronometro(dados.parent / "oficina", "cortar", args={"dados": dados.name}) as cron:
        d = json.load(open(sys.argv[1], encoding="utf-8"))
        antes = d["tabela"][-1]["corteAte"]
        tab, ganho = cortar(d, sys.argv[2])
        d["tabela"] = tab
        json.dump(d, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        fim = tab[-1]["corteAte"]
        limpas = [t for t in tab[1:] if t["folgaLimpa"] and t["folgaMs"] >= 300]
        cron.extra.update(pedacos=len(tab), emendas=len(limpas), antesMs=antes, fimMs=fim)
        print(f"{len(tab)} pedaços · {antes/1000:.1f} s → {fim/1000:.1f} s")
        print(f"{len(limpas)} emendas com folga limpa para split edit")
