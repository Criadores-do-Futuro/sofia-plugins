#!/usr/bin/env python3
"""Cria, valida e altera briefings editoriais em JSON.

Sem dependências externas. Regras de segurança:
- salvar cria o arquivo de forma exclusiva: nunca sobrescreve;
- alterar lê o original e grava o resultado em um arquivo novo; o original não muda.

Campos do JSON:
  titulo             obrigatório, texto
  formato_sofia      obrigatório, formato criativo Sofia (escolhido explicitamente)
  estrutura_roteiro  obrigatório, estrutura de roteiro (escolhida explicitamente)
  editor             obrigatório: "capcut" ou "davinci"
  objetivo           obrigatório, texto
  estilo             opcional (ausente ou null = sem estilo)

Uso:
  python3 scripts/briefing_editorial.py criar --titulo "..." --formato-sofia "..." \\
      --estrutura-roteiro "..." --editor capcut --objetivo "..." --saida briefing.json
  python3 scripts/briefing_editorial.py alterar briefing.json --editor davinci \\
      --saida briefing-v2.json
  python3 scripts/briefing_editorial.py validar briefing.json
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

CAMPOS_TEXTO_OBRIGATORIOS = ("titulo", "formato_sofia", "estrutura_roteiro", "objetivo")
CAMPO_EDITOR = "editor"
EDITORES_VALIDOS = ("capcut", "davinci")
CAMPO_ESTILO = "estilo"

CAMPOS_OBRIGATORIOS = frozenset(CAMPOS_TEXTO_OBRIGATORIOS + (CAMPO_EDITOR,))
CAMPOS_PERMITIDOS = CAMPOS_OBRIGATORIOS | {CAMPO_ESTILO}

# Ordem em que os campos são gravados e exibidos.
_ORDEM_GRAVACAO = ("titulo", "formato_sofia", "estrutura_roteiro", "editor", "objetivo", "estilo")


class BriefingInvalido(ValueError):
    """Briefing com campo ausente, desconhecido ou com valor inválido."""


def _normalizar_texto(campo: str, valor: Any) -> str:
    if not isinstance(valor, str):
        raise BriefingInvalido(f"'{campo}' deve ser texto, não {type(valor).__name__}")
    # NFC: "ã" escrito como "a" + til combinante (forma comum em nomes de arquivo do macOS)
    # vira o mesmo texto que o digitado direto. Os acentos continuam como PT-BR.
    texto = unicodedata.normalize("NFC", valor).strip()
    if not texto:
        raise BriefingInvalido(f"'{campo}' não pode ser vazio")
    return texto


def validar_briefing(dados: Any) -> Dict[str, Any]:
    """Confere o briefing e devolve uma cópia limpa, pronta para gravar."""
    if not isinstance(dados, dict):
        raise BriefingInvalido("o briefing deve ser um objeto JSON")

    desconhecidos = sorted(set(dados) - CAMPOS_PERMITIDOS)
    if desconhecidos:
        raise BriefingInvalido("campos desconhecidos: " + ", ".join(desconhecidos))

    # Ausente e null contam como ausente para os campos obrigatórios.
    ausentes = sorted(c for c in CAMPOS_OBRIGATORIOS if dados.get(c) is None)
    if ausentes:
        raise BriefingInvalido("campos obrigatórios ausentes: " + ", ".join(ausentes))

    limpo: Dict[str, Any] = {}
    for campo in CAMPOS_TEXTO_OBRIGATORIOS + (CAMPO_EDITOR,):
        valor = _normalizar_texto(campo, dados[campo])
        if campo == CAMPO_EDITOR:
            valor = valor.lower()
            if valor not in EDITORES_VALIDOS:
                raise BriefingInvalido(
                    f"'editor' deve ser um de: {', '.join(EDITORES_VALIDOS)}; "
                    f"recebido {dados[campo]!r}"
                )
        limpo[campo] = valor

    if dados.get(CAMPO_ESTILO) is not None:
        limpo[CAMPO_ESTILO] = _normalizar_texto(CAMPO_ESTILO, dados[CAMPO_ESTILO])

    return {campo: limpo[campo] for campo in _ORDEM_GRAVACAO if campo in limpo}


def _gravar_novo(briefing: Dict[str, Any], caminho: Union[str, Path]) -> Path:
    """Cria o arquivo de forma exclusiva. Recusa se ele já existir."""
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        arquivo = destino.open("x", encoding="utf-8")
    except FileExistsError as erro:
        raise FileExistsError(f"não sobrescrevo: {destino} já existe") from erro
    with arquivo:
        try:
            arquivo.write(json.dumps(briefing, ensure_ascii=False, indent=2) + "\n")
        except BaseException:
            # Não deixa um arquivo pela metade que bloquearia a próxima tentativa.
            arquivo.close()
            destino.unlink(missing_ok=True)
            raise
    return destino


def carregar_briefing(caminho: Union[str, Path]) -> Dict[str, Any]:
    """Lê e valida um briefing JSON. Não altera o arquivo."""
    origem = Path(caminho)
    with origem.open(encoding="utf-8") as arquivo:
        try:
            dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise BriefingInvalido(f"JSON inválido em {origem}: {erro}") from erro
    return validar_briefing(dados)


def salvar_briefing(dados: Any, caminho: Union[str, Path]) -> Path:
    """Valida e cria o briefing em arquivo novo. Nada é gravado se a validação falhar."""
    return _gravar_novo(validar_briefing(dados), caminho)


def alterar_briefing(
    caminho_origem: Union[str, Path],
    caminho_destino: Union[str, Path],
    alteracoes: Dict[str, Any],
) -> Dict[str, Any]:
    """Aplica alterações a um briefing e grava o resultado em arquivo novo.

    Para remover o estilo, passe {"estilo": None}. O arquivo de origem não é modificado.
    """
    if not alteracoes:
        raise BriefingInvalido("nenhuma alteração informada")
    atual = carregar_briefing(caminho_origem)
    novo = validar_briefing({**atual, **alteracoes})
    _gravar_novo(novo, caminho_destino)
    return novo


# ---------------------------------------------------------------- linha de comando

_CAMPOS_CLI = ("titulo", "formato_sofia", "estrutura_roteiro", "editor", "objetivo", "estilo")


def _adicionar_campos(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--titulo")
    parser.add_argument("--formato-sofia", dest="formato_sofia", metavar="FORMATO")
    parser.add_argument("--estrutura-roteiro", dest="estrutura_roteiro", metavar="ESTRUTURA")
    parser.add_argument("--editor", metavar="{capcut,davinci}")
    parser.add_argument("--objetivo")
    parser.add_argument("--estilo", help="opcional")


def _montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="briefing_editorial",
        description="Cria, valida e altera briefings editoriais em JSON.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    criar = sub.add_parser("criar", help="cria um briefing novo (nunca sobrescreve)")
    _adicionar_campos(criar)
    criar.add_argument("--saida", required=True, help="arquivo JSON a criar")

    alterar = sub.add_parser("alterar", help="grava uma cópia alterada em arquivo novo")
    alterar.add_argument("origem", help="briefing JSON existente (não é modificado)")
    _adicionar_campos(alterar)
    alterar.add_argument("--sem-estilo", action="store_true", help="remove o estilo")
    alterar.add_argument("--saida", required=True, help="arquivo JSON novo")

    validar = sub.add_parser("validar", help="valida um briefing sem gravar nada")
    validar.add_argument("arquivo")
    return parser


def _campos_da_linha(args: argparse.Namespace) -> Dict[str, Any]:
    return {c: getattr(args, c) for c in _CAMPOS_CLI if getattr(args, c) is not None}


def main(argv: Optional[List[str]] = None) -> int:
    parser = _montar_parser()
    args = parser.parse_args(argv)
    try:
        if args.comando == "criar":
            destino = salvar_briefing(_campos_da_linha(args), args.saida)
            print(f"Briefing criado: {destino}")
        elif args.comando == "alterar":
            alteracoes = _campos_da_linha(args)
            if args.sem_estilo:
                if args.estilo is not None:
                    parser.error("--sem-estilo não combina com --estilo")
                alteracoes[CAMPO_ESTILO] = None
            alterar_briefing(args.origem, args.saida, alteracoes)
            print(f"Briefing alterado gravado em: {args.saida}")
        else:
            carregar_briefing(args.arquivo)
            print("Briefing válido.")
    except (BriefingInvalido, OSError) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
