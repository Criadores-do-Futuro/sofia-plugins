#!/usr/bin/env python3
"""Valida um manual de estilo sem dependências externas.

Além do schema, verifica referências cruzadas, IDs únicos e tempos dentro da mídia.
Essas verificações não demonstram que as observações são verdadeiras.
"""
import argparse
import json
import math
import sys


def validar(manual):
    erros = []

    def objeto(valor, caminho, obrigatorios, opcionais=()):
        if not isinstance(valor, dict):
            erros.append(f"{caminho}: esperado objeto")
            return False
        for chave in sorted(set(obrigatorios) - valor.keys()):
            erros.append(f"{caminho}.{chave}: campo obrigatório")
        for chave in sorted(valor.keys() - set(obrigatorios) - set(opcionais)):
            erros.append(f"{caminho}.{chave}: campo desconhecido")
        return True

    def texto(valor, caminho):
        if not isinstance(valor, str) or not valor.strip():
            erros.append(f"{caminho}: esperado texto não vazio")
            return False
        return True

    def numero(valor, caminho, minimo=0, maximo=None, exclusivo=False):
        try:
            finito = not isinstance(valor, bool) and isinstance(valor, (int, float)) and math.isfinite(valor)
        except OverflowError:
            finito = False
        if not finito:
            erros.append(f"{caminho}: esperado número finito")
            return False
        if valor < minimo or (exclusivo and valor == minimo) or (maximo is not None and valor > maximo):
            erros.append(f"{caminho}: fora do intervalo permitido")
            return False
        return True

    if not objeto(manual, "$", ("versao", "nome", "referencias", "observacoes")):
        return erros
    if type(manual.get("versao")) is not int or manual["versao"] != 1:
        erros.append("$.versao: esperada versão 1")
    texto(manual.get("nome"), "$.nome")
    refs = manual.get("referencias")
    duracoes = {}
    if not isinstance(refs, list) or not refs:
        erros.append("$.referencias: esperada lista não vazia")
        refs = []
    for i, ref in enumerate(refs):
        p = f"$.referencias[{i}]"
        if not objeto(ref, p, ("id", "fonte", "duracao_segundos")):
            continue
        id_valido = texto(ref.get("id"), p + ".id")
        texto(ref.get("fonte"), p + ".fonte")
        tempo_valido = numero(ref.get("duracao_segundos"), p + ".duracao_segundos", exclusivo=True)
        if id_valido:
            if ref["id"] in duracoes:
                erros.append(p + ".id: referência duplicada")
            else:
                duracoes[ref["id"]] = ref.get("duracao_segundos") if tempo_valido else None
    observacoes = manual.get("observacoes")
    ids = set()
    if not isinstance(observacoes, list) or not observacoes:
        erros.append("$.observacoes: esperada lista não vazia")
        observacoes = []
    for i, obs in enumerate(observacoes):
        p = f"$.observacoes[{i}]"
        if not objeto(obs, p, ("id", "aspecto", "estado", "descricao", "evidencias"), ("valor", "confianca")):
            continue
        if texto(obs.get("id"), p + ".id"):
            if obs["id"] in ids:
                erros.append(p + ".id: observação duplicada")
            ids.add(obs["id"])
        texto(obs.get("aspecto"), p + ".aspecto")
        texto(obs.get("descricao"), p + ".descricao")
        estado = obs.get("estado")
        if estado not in ("medido", "inferido", "indisponivel"):
            erros.append(p + ".estado: esperado medido, inferido ou indisponivel")
        if "confianca" in obs:
            numero(obs["confianca"], p + ".confianca", maximo=1)
        evidencias = obs.get("evidencias")
        if not isinstance(evidencias, list):
            erros.append(p + ".evidencias: esperada lista")
            continue
        if estado in ("medido", "inferido") and not evidencias:
            erros.append(p + ".evidencias: observação exige evidência temporal")
        if estado == "indisponivel" and (evidencias or "valor" in obs):
            erros.append(p + ": aspecto indisponível não pode ter valor ou evidências")
        for j, ev in enumerate(evidencias):
            q = f"{p}.evidencias[{j}]"
            if not objeto(ev, q, ("referencia_id", "inicio_segundos", "fim_segundos", "modalidade"), ("nota",)):
                continue
            ref_id = ev.get("referencia_id")
            if texto(ref_id, q + ".referencia_id") and ref_id not in duracoes:
                erros.append(q + ".referencia_id: referência inexistente")
            inicio = ev.get("inicio_segundos")
            fim = ev.get("fim_segundos")
            inicio_ok = numero(inicio, q + ".inicio_segundos")
            fim_ok = numero(fim, q + ".fim_segundos")
            if inicio_ok and fim_ok:
                if inicio > fim:
                    erros.append(q + ": início posterior ao fim")
                if isinstance(ref_id, str) and ref_id in duracoes and duracoes[ref_id] is not None and fim > duracoes[ref_id]:
                    erros.append(q + ": tempo excede duração da referência")
            if ev.get("modalidade") not in ("video", "audio", "audiovisual"):
                erros.append(q + ".modalidade: modalidade inválida")
            if "nota" in ev and not isinstance(ev["nota"], str):
                erros.append(q + ".nota: esperado texto")
    return erros


def main():
    parser = argparse.ArgumentParser(description="Valida a estrutura e a proveniência temporal do manual de estilo.")
    parser.add_argument("arquivo", help="Caminho do manual JSON")
    args = parser.parse_args()
    try:
        with open(args.arquivo, encoding="utf-8") as arquivo:
            manual = json.load(arquivo, parse_constant=lambda valor: (_ for _ in ()).throw(ValueError(f"constante inválida: {valor}")))
        erros = validar(manual)
    except (OSError, UnicodeError, ValueError) as exc:
        erros = [f"Não foi possível ler o JSON: {exc}"]
    print(json.dumps({"valido": not erros, "erros": erros}, ensure_ascii=False, indent=2))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
