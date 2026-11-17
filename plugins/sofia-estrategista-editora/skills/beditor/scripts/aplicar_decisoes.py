#!/usr/bin/env python3
"""
aplicar_decisoes.py — leva de volta ao guia o que o editor marcou na mesa.

A mesa de decupagem (artifact) grava um documento com tres mapas:

  escolhas  {M03: "fica"|"sai"}          o momento inteiro entra ou nao
  jcuts     {M03: 1200}                  o audio entra 1200 ms antes da imagem
  cortes    {M03: [{de, ate}, ...]}      os pedacos do momento que ficam
  motions   {M03: {tipo, ideia, ...}}    o motion editado na mesa; null remove

e mais duas decisoes que nao sao de momento nenhum, e por isso passavam batido:

  cor       {contraste, branco, ...}     a grade fechada na aba Cor. Vai para
            + corPreferenciaDoCanal      `~/.beditor/cor.json` quando ele marca
                                         que vale para o canal, ou para
                                         `guia.cor` quando e so deste video.
  hook      {linhas, opcao}              o gancho da abertura, que viaja no guia
                                         e e desenhado junto da legenda.

Este script traduz isso para o guia:

  sai  -> decisao "cortar" (o motion, se havia, e guardado em `_motion` para
          poder voltar sem o diretor reescrever a ideia)
  fica -> volta a decisao anterior: `_motion` guardado, ou `aroll`

  jcut  -> `audioAntesMs` no momento (o validador confere contra a pausa da
          frase, do mesmo jeito que ja faz com o `entraAntesMs` do motion)
  corte -> o momento e aparado, e a sobra vira um momento `cortar` ao lado:
          o guia so aceita momentos que cobrem o take inteiro. Um momento
          picado em dois pedacos separados nao cabe nessa forma — o script
          recusa e manda de volta para o diretor.

Depois roda o validador. Se a mudanca abrir buraco ou quebrar familia, o erro
sai em portugues e nada e escrito pela metade.

Uso: aplicar_decisoes.py --guia guia/guia.json --decisoes decisoes.json
     (o JSON e o que `Artifact action:"read_db"` devolve, ou {"escolhas":{...}})
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cor  # noqa: E402
import mascara  # noqa: E402
import validar  # noqa: E402


def aplicar(guia, escolhas):
    mudou = []
    for m in guia.get("momentos", []):
        alvo = escolhas.get(m["id"])
        if alvo not in ("fica", "sai"):
            continue
        era = m["decisao"]
        if alvo == "sai" and era != "cortar":
            if m.get("motion"):
                m["_motion"] = m.pop("motion")
            m["decisao"] = "cortar"
            m["porque"] = (m.get("porque", "") + " · cortado na mesa pelo editor").strip(" ·")
            mudou.append(f"{m['id']}: {era} → cortar")
        elif alvo == "fica" and era == "cortar":
            if m.get("_motion"):
                m["motion"] = m.pop("_motion")
                m["decisao"] = "motion"
            else:
                m["decisao"] = "aroll"
            m["porque"] = (m.get("porque", "") + " · devolvido na mesa pelo editor").strip(" ·")
            mudou.append(f"{m['id']}: cortar → {m['decisao']}")
    return mudou


def aplicar_jcuts(guia, jcuts, contato=None):
    """o audio de um momento comecando antes da imagem dele.

    A mesa deixa arrastar o audio a vontade; a fala anterior nao deixa. Se o
    arrasto passou da pausa que existe antes da frase, aparamos ate a pausa em
    vez de devolver o guia inteiro reprovado — o editor quis o J-cut, so nao
    tinha todo esse silencio disponivel."""
    mudou = []
    for m in guia.get("momentos", []):
        v = jcuts.get(m["id"])
        if v is None:
            continue
        v = int(v)
        if v > 0 and contato:
            fa = validar._frase_de(contato, m["deMs"])
            teto = int((fa or {}).get("pausaAntesMs", 0))
            if fa is not None and v > teto:
                mudou.append(f"{m['id']}: J-cut de {v} ms aparado para {teto} ms — "
                             f"e todo o silencio que existe antes da frase")
                v = teto
        if v == int(m.get("audioAntesMs") or 0):
            continue
        if v > 0:
            m["audioAntesMs"] = v
            mudou.append(f"{m['id']}: audio entra {v} ms antes da imagem (J-cut da mesa)")
        else:
            m.pop("audioAntesMs", None)
            mudou.append(f"{m['id']}: J-cut desfeito, audio volta a colar na imagem")
    return mudou


CAMPOS_MESA = ("tipo", "ideia", "movimento", "entrada", "saida",
               "entraAntesMs", "familia", "estado")


def aplicar_motions(guia, motions):
    """o motion que o editor escreveu, criou ou removeu na mesa.

    A mesa mexe so nos campos que ela mostra; `camera`, `dados` e o que o
    enriquecedor trouxer ficam como estavam. `null` remove o motion."""
    mudou = []
    for m in guia.get("momentos", []):
        if m["id"] not in motions:
            continue
        novo = motions[m["id"]]
        if not novo:
            if m.pop("motion", None) or m.pop("_motion", None):
                if m["decisao"] in ("motion", "aroll+motion"):
                    m["decisao"] = "aroll"
                mudou.append(f"{m['id']}: motion removido na mesa — so o rosto")
            continue
        guardado = m["decisao"] == "cortar"          # momento fora: guarda para quando voltar
        alvo = dict(m.get("motion") or m.get("_motion") or {})
        antes = json.dumps(alvo, sort_keys=True, ensure_ascii=False)
        for k in CAMPOS_MESA:
            if k in novo:
                v = novo[k]
                alvo[k] = int(v or 0) if k == "entraAntesMs" else (v or "")
        for k in ("familia", "estado"):
            alvo[k] = alvo.get(k) or None
        # a mesa mexe nos dados que ela sabe editar; o resto (curva, ficha do
        # enriquecedor) fica onde estava
        juntos = dict(alvo.get("dados") or {})
        juntos.update(novo.get("dados") or {})
        alvo["dados"] = juntos
        if json.dumps(alvo, sort_keys=True, ensure_ascii=False) == antes and not guardado:
            continue
        if guardado:
            m["_motion"] = alvo
            m.pop("motion", None)
            mudou.append(f"{m['id']}: motion escrito na mesa, guardado — o momento esta cortado")
            continue
        era = m["decisao"]
        m["motion"] = alvo
        m.pop("_motion", None)
        if era == "aroll":
            m["decisao"] = "aroll+motion"
        mudou.append(f"{m['id']}: motion `{alvo.get('tipo') or 'sem tipo'}` da mesa"
                     + (f" ({era} → {m['decisao']})" if era != m["decisao"] else ""))
    return mudou


def _sobra(m, de, ate, suf):
    """o pedaco que o editor tirou de dentro do momento, como momento `cortar`"""
    s = {k: v for k, v in m.items() if k not in ("motion", "_motion", "audioAntesMs")}
    s.update(id=m["id"] + suf, deMs=de, ateMs=ate, decisao="cortar",
             porque="aparado na mesa pelo editor", precisaDeFato=False)
    return s


def _continuacao(m, de, ate, n):
    """o pedaco seguinte do mesmo momento, depois de uma pausa aparada.

    O motion entra num pedaco so: um mesmo grafico nao aparece duas vezes, e
    dois motion do mesmo tipo seguidos sem familia o validador recusa."""
    s = {k: v for k, v in m.items() if k not in ("motion", "_motion", "audioAntesMs")}
    s.update(id=f"{m['id']}-{n}", deMs=de, ateMs=ate, decisao="aroll",
             porque=f"continuacao de {m['id']} depois da pausa aparada na mesa",
             precisaDeFato=False)
    return s


MIN_MOTION_MS = 2500


def _onde_cabe_o_motion(vivos):
    """em qual pedaco o grafico tem tempo de ser lido.

    Tirar as pausas do meio pode deixar o primeiro pedaco com meio segundo. Um
    grafico ali pisca em vez de comunicar — e o validador reprova, com razao.
    Entao o motion vai para o pedaco mais longo, desde que ele passe do minimo;
    se nenhum passar, o momento perde o grafico e vira rosto."""
    if not vivos:
        return None
    maior = max(range(len(vivos)), key=lambda i: vivos[i][1] - vivos[i][0])
    return maior if vivos[maior][1] - vivos[maior][0] >= MIN_MOTION_MS else None


def aplicar_cortes(guia, cortes):
    """corte dentro do momento: apara `deMs`/`ateMs` e devolve o resto como
    momento `cortar`, para o take continuar coberto de ponta a ponta.

    Momento partido em varios pedacos (tirar as pausas do meio faz isso) vira
    uma sequencia: o primeiro pedaco guarda o momento, cada pausa vira um
    `cortar`, e cada pedaco seguinte vira um `aroll` que continua a fala."""
    saida, mudou = [], []
    for m in guia.get("momentos", []):
        partes = cortes.get(m["id"])
        if not partes:
            saida.append(m)
            continue
        pares = sorted((int(p["de"]), int(p["ate"])) for p in partes)
        juntos = [list(pares[0])]
        for de, ate in pares[1:]:
            if de - juntos[-1][1] <= 1:          # so um corte, os dois lados ficam
                juntos[-1][1] = max(juntos[-1][1], ate)
            else:
                juntos.append([de, ate])
        vivos = []
        for de, ate in juntos:
            de, ate = max(de, m["deMs"]), min(ate, m["ateMs"])
            if ate - de > 0:
                vivos.append((de, ate))
        if not vivos:
            return None, [f"{m['id']}: a mesa deixou o momento sem duracao"]
        if len(vivos) > 1:
            tem_motion = bool(m.get("motion"))
            i_motion = _onde_cabe_o_motion(vivos) if tem_motion else None
            cursor, n_corte, n_parte = m["deMs"], 0, 1
            for i, (de, ate) in enumerate(vivos):
                if de > cursor:
                    n_corte += 1
                    saida.append(_sobra(m, cursor, de, f"p{n_corte}"))
                if i == 0:
                    alvo = dict(m)
                    alvo["deMs"], alvo["ateMs"] = de, ate
                    if i_motion != 0:
                        alvo.pop("motion", None)
                        alvo["decisao"] = "aroll"
                    saida.append(alvo)
                else:
                    n_parte += 1
                    parte = _continuacao(m, de, ate, n_parte)
                    if i == i_motion:
                        parte["motion"] = json.loads(json.dumps(m["motion"]))
                        parte["decisao"] = "aroll+motion"
                    saida.append(parte)
                cursor = ate
            if cursor < m["ateMs"]:
                n_corte += 1
                saida.append(_sobra(m, cursor, m["ateMs"], f"p{n_corte}"))
            recado = f"{m['id']}: {len(vivos)} pedacos e {n_corte} pausa(s) fora, da mesa"
            if tem_motion and i_motion is None:
                recado += " · o grafico caiu: nenhum pedaco chegou a 2,5 s"
            elif tem_motion and i_motion:
                recado += f" · o grafico foi para o pedaco {i_motion + 1}, que tem tempo de ser lido"
            mudou.append(recado)
            continue
        de, ate = vivos[0]
        if de <= m["deMs"] and ate >= m["ateMs"]:
            saida.append(m)
            continue
        if de > m["deMs"]:
            saida.append(_sobra(m, m["deMs"], de, "a"))
        alvo = dict(m)
        alvo["deMs"], alvo["ateMs"] = de, ate
        recado = f"{m['id']}: aparado na mesa para {de}–{ate} ms"
        if alvo.get("motion") and ate - de < MIN_MOTION_MS:
            alvo.pop("motion", None)
            alvo["decisao"] = "aroll"
            recado += f" · o grafico caiu: sobraram {ate - de} ms, menos que os 2,5 s de leitura"
        saida.append(alvo)
        if ate < m["ateMs"]:
            saida.append(_sobra(m, ate, m["ateMs"], "z"))
        mudou.append(recado)
    guia["momentos"] = saida
    return guia, mudou


def aplicar_cor(guia, dec, pendente=None):
    """A grade que o editor fechou na aba Cor. A marca dele decide onde ela mora:
    preferencia do canal, que atravessa os proximos videos, ou so este guia.

    Quando ele manda a grade para o canal e o guia ainda carrega uma grade deste
    video, a do guia e retirada — senao a mais especifica continuaria mandando e
    a preferencia recem-gravada nao apareceria justamente no video em que ele a
    escolheu. A retirada sai no relatorio, nunca calada."""
    grade = dec.get("cor")
    if not isinstance(grade, dict) or not grade:
        return []
    resolvida = cor.resolver(grade)
    if dec.get("corPreferenciaDoCanal"):
        igual = cor.resolver(cor.ler_preferencia()) == resolvida
        if igual and not guia.get("cor"):
            return []
        # a gravacao fica pendente ate o validador passar: o guia nao e escrito
        # pela metade, e a preferencia do canal tambem nao
        if pendente is not None:
            pendente["cor"] = grade
        recado = [f"cor: preferencia do canal em {cor.PREFERENCIA}"]
        if guia.pop("cor", None) is not None:
            recado.append("cor: a grade so deste video saiu do guia — quem manda agora e a do canal")
        return recado
    if guia.get("cor") == resolvida:
        return []
    guia["cor"] = resolvida
    return ["cor: grade deste video escrita no guia"]


def aplicar_hook(guia, dec):
    """O gancho escolhido na aba Hook. Viaja no guia e e desenhado junto da
    legenda (`legenda_hf.py`); `opcao` fica so para saber qual das tres ele
    escolheu quando alguem for perguntar depois."""
    h = dec.get("hook")
    if not isinstance(h, dict):
        return []
    linhas = [str(x).strip() for x in (h.get("linhas") or []) if str(x).strip()]
    if not linhas:
        return []
    novo = dict(guia.get("hook") or {})
    novo.update({k: v for k, v in h.items()
                 if k in ("linhas", "opcao", "destaque", "ateMs")})
    novo["linhas"] = linhas
    if novo == (guia.get("hook") or {}):
        return []
    guia["hook"] = novo
    return [f"hook: «{' / '.join(linhas)}»"]


def aplicar_mascara(guia, dec):
    """A aba Máscara da mesa: o Dividir horizontal com Suavizar (`mascara.py`).
    Desligar grava `ligada: false` em vez de apagar o bloco, para a linha e o
    suavizar escolhidos voltarem iguais se ele religar."""
    m = dec.get("mascara")
    if not isinstance(m, dict):
        return []
    novo = mascara.normalizar({k: v for k, v in m.items()
                               if k in ("ligada", "linhaPct", "suavizarPct",
                                        "manter", "cor", "onde")})
    if guia.get("mascara") == novo or (not novo["ligada"] and "mascara" not in guia):
        return []
    guia["mascara"] = novo
    if not novo["ligada"]:
        return ["mascara: desligada"]
    return [f"mascara: Dividir horizontal · linha {novo['linhaPct']:.0f}% · "
            f"suavizar {novo['suavizarPct']:.0f}% · {novo['onde']}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guia", required=True)
    ap.add_argument("--decisoes", required=True)
    ap.add_argument("--contato")
    a = ap.parse_args()

    guia = json.loads(Path(a.guia).read_text(encoding="utf-8"))
    bruto = json.loads(Path(a.decisoes).read_text(encoding="utf-8"))
    escolhas = bruto.get("escolhas") or bruto.get("data", {}).get("escolhas") or bruto
    if not isinstance(escolhas, dict):
        sys.exit("decisoes: nao achei o mapa `escolhas`")

    contato = json.loads(Path(a.contato).read_text(encoding="utf-8")) if a.contato else None

    mudou = aplicar(guia, escolhas)
    mudou += aplicar_jcuts(guia, bruto.get("jcuts") or {}, contato)
    mudou += aplicar_motions(guia, bruto.get("motions") or {})
    cortes = bruto.get("cortes") or {}
    if cortes:
        novo, m2 = aplicar_cortes(guia, cortes)
        if novo is None:
            for e in m2:
                print(" ·", e)
            sys.exit("guia NAO foi escrito")
        guia, mudou = novo, mudou + m2
    pendente = {}
    mudou += aplicar_cor(guia, bruto, pendente)
    mudou += aplicar_hook(guia, bruto)
    mudou += aplicar_mascara(guia, bruto)
    if not mudou:
        print("nada mudou — a decupagem do diretor continua valendo")
        return

    erros = validar.validar(guia, contato)
    for e in erros:
        print(" ·", e)
    if erros:
        sys.exit(f"{len(erros)} erro(s) — guia NAO foi escrito")

    Path(a.guia).write_text(json.dumps(guia, ensure_ascii=False, indent=2), encoding="utf-8")
    if pendente.get("cor"):
        cor.gravar_preferencia(pendente["cor"], nota="fechada na mesa de decupagem")
    for m in mudou:
        print(" ", m)
    print(f"{len(mudou)} mudanca(s) aplicada(s) · rode /sofia-estrategista-editora:cortar de novo")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
