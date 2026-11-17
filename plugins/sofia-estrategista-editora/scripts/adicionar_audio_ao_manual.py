#!/usr/bin/env python3
"""Acrescenta medições de áudio de uma referência a um novo manual de estilo.

O relatório deve ter sido produzido por analisar_audio.py para a mesma fonte.
Nunca sobrescreve o manual original nem interpreta silêncio como corte ou SFX.
"""
import argparse
import copy
import json
import math
import sys
from pathlib import Path

from analisar_audio import _estado_arquivo
from validar_manual_estilo import validar


def _real(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(valor)
    except OverflowError:
        return False


def incorporar(manual, relatorio, referencia_id):
    erros = validar(manual)
    if erros:
        raise ValueError("Manual inválido: " + "; ".join(erros))
    if not isinstance(relatorio, dict) or type(relatorio.get("versao")) is not int or relatorio["versao"] != 1:
        raise ValueError("Relatório de áudio inválido ou de versão não suportada")
    refs = [r for r in manual["referencias"] if r["id"] == referencia_id]
    if len(refs) != 1:
        raise ValueError("Referência não encontrada no manual")
    ref = refs[0]
    if not isinstance(relatorio.get("fonte"), str) or Path(relatorio["fonte"]).resolve() != Path(ref["fonte"]).resolve():
        raise ValueError("O relatório pertence a outra fonte")
    fonte = Path(ref["fonte"]).resolve(strict=True)
    if relatorio.get("estado_fonte") != _estado_arquivo(fonte):
        raise ValueError("A fonte mudou desde a análise de áudio; analise novamente")
    duracao = relatorio.get("duracao_segundos")
    if not _real(duracao) or duracao <= 0 or abs(duracao - ref["duracao_segundos"]) > 0.05:
        raise ValueError("A duração do relatório não corresponde à referência")
    if type(relatorio.get("possui_audio")) is not bool or type(relatorio.get("processamento_sem_erro")) is not bool:
        raise ValueError("Estado de áudio ausente ou inválido")
    resultado = copy.deepcopy(manual)
    ja_usados = {o["id"] for o in resultado["observacoes"]}
    prefixo = f"audio-{referencia_id}"

    def inserir(sufixo, aspecto, estado, descricao, evidencias, valor=None, tem_valor=False):
        obs_id = f"{prefixo}-{sufixo}"
        if obs_id in ja_usados:
            raise ValueError("A medição de áudio já existe no manual")
        obs = {"id": obs_id, "aspecto": aspecto, "estado": estado,
               "descricao": descricao, "evidencias": evidencias}
        if tem_valor:
            obs["valor"] = valor
        resultado["observacoes"].append(obs)
        ja_usados.add(obs_id)

    if not relatorio["possui_audio"]:
        if relatorio["processamento_sem_erro"] or relatorio.get("silencios") != []:
            raise ValueError("Relatório sem áudio contém medições inconsistentes")
        inserir("ausente", "áudio da referência", "indisponivel",
                "A referência não contém trilha de áudio; não há som a medir.", [])
    else:
        if not relatorio["processamento_sem_erro"]:
            raise ValueError("A análise do áudio não terminou com sucesso")
        trilha = relatorio.get("trilha")
        if not isinstance(trilha, dict) or type(trilha.get("deslocamento_verificado")) is not bool:
            raise ValueError("Metadados de sincronização da trilha ausentes")
        offset = trilha.get("deslocamento_segundos")
        audio_duracao = trilha.get("duracao_decodificada_segundos")
        if not _real(offset) or not _real(audio_duracao) or audio_duracao <= 0:
            raise ValueError("Tempos da trilha inválidos")
        if not trilha["deslocamento_verificado"]:
            inserir("sincronia", "medições temporais de áudio", "indisponivel",
                    "O início da trilha no contêiner é desconhecido; não há evidência temporal confiável.", [])
        else:
            inicio = max(0, offset)
            fim = min(ref["duracao_segundos"], offset + audio_duracao)
            if fim <= inicio:
                raise ValueError("O áudio não tem intervalo válido dentro da referência")
            ruidos = relatorio.get("ruido_db", relatorio.get("limiar_ruido_db"))
            silencio_minimo = relatorio.get("silencio_minimo_segundos")
            if not _real(ruidos) or not -120 <= ruidos <= 0 or not _real(silencio_minimo) or not 0.05 <= silencio_minimo <= 30:
                raise ValueError("Parâmetros de medição ausentes ou inválidos")
            intervalos = relatorio.get("silencios")
            if not isinstance(intervalos, list):
                raise ValueError("Intervalos de silêncio ausentes ou inválidos")
            fim_anterior = inicio
            for intervalo in intervalos:
                if not isinstance(intervalo, dict):
                    raise ValueError("Intervalo de silêncio inválido")
                a, z = intervalo.get("inicio_segundos"), intervalo.get("fim_segundos")
                if not _real(a) or not _real(z) or a < inicio - 0.00001 or z > fim + 0.00001 or z <= a or a < fim_anterior - 0.00001:
                    raise ValueError("Intervalo de silêncio fora da trilha ou fora de ordem")
                fim_anterior = z
            evidencia = [{"referencia_id": referencia_id, "inicio_segundos": round(inicio, 6),
                          "fim_segundos": round(fim, 6), "modalidade": "audio",
                          "nota": "Primeira trilha decodificada; sem classificação semântica."}]
            inserir("silencios", "intervalos abaixo do limiar de silêncio", "medido",
                    f"Medição FFmpeg: limiar {ruidos:g} dB, duração mínima {silencio_minimo:g} s; não identifica fala ou intenção.",
                    evidencia, intervalos, True)
            nivel = relatorio.get("nivel_medio_dbfs")
            if nivel is None:
                inserir("nivel", "nível médio do áudio", "indisponivel",
                        "O nível médio não foi reportado como número finito.", [])
            elif _real(nivel) and nivel <= 0:
                inserir("nivel", "nível médio do áudio", "medido",
                        "Nível médio do volumedetect do FFmpeg em dBFS, com precisão limitada pela análise em 16 bits.",
                        evidencia, nivel, True)
            else:
                raise ValueError("Nível médio inválido")
    erros = validar(resultado)
    if erros:
        raise ValueError("O manual gerado é inválido: " + "; ".join(erros))
    return resultado


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manual", type=Path)
    p.add_argument("relatorio", type=Path)
    p.add_argument("--referencia", required=True, help="ID da referência já existente no manual")
    p.add_argument("--saida", type=Path, required=True)
    args = p.parse_args()
    if args.saida.exists():
        p.error("O arquivo de saída já existe")
    try:
        def carregar(caminho):
            with caminho.open(encoding="utf-8") as f:
                return json.load(f, parse_constant=lambda v: (_ for _ in ()).throw(ValueError("Constante inválida: " + v)))
        resultado = incorporar(carregar(args.manual), carregar(args.relatorio), args.referencia)
        with args.saida.open("x", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("Não foi possível atualizar o manual: " + str(exc), file=sys.stderr)
        return 1
    print("Novo manual gerado com o estado do áudio e suas evidências disponíveis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
