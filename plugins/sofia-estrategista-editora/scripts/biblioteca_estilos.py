#!/usr/bin/env python3
"""Biblioteca local de estilos, só com a biblioteca padrão do Python.

Cada estilo vive numa pasta própria dentro da raiz da biblioteca:

    <raiz>/<id>/estilo.json   metadados, origem e estado do manual
    <raiz>/<id>/manual.json   cópia do manual JSON de origem
    <raiz>/<id>/capa.<ext>    cópia da capa local (opcional)

Regras:
- o id é um slug seguro ([a-z0-9] separados por hífen), validado antes de qualquer
  caminho ser montado; nada de barra, ponto ou caminho relativo entra no nome da pasta;
- cadastrar cria a pasta com exclusividade e nunca sobrescreve um estilo existente;
- os arquivos de origem são só lidos e copiados para a biblioteca; a origem nunca é
  alterada nem apagada;
- links simbólicos de origem são recusados;
- nenhuma rede, nenhum subprocesso, nenhum segredo, nenhuma dependência externa.

Uso:
    python3 scripts/biblioteca_estilos.py [--raiz CAMINHO] cadastrar --id ID --nome NOME \
        --manual ARQUIVO.json [--descricao TEXTO] [--capa ARQUIVO.png]
    python3 scripts/biblioteca_estilos.py [--raiz CAMINHO] listar [--json]
    python3 scripts/biblioteca_estilos.py [--raiz CAMINHO] mostrar ID [--manual]
    python3 scripts/biblioteca_estilos.py [--raiz CAMINHO] atualizar ID --manual ARQUIVO.json --hash-esperado HASH

A raiz vem de --raiz, senão da variável BIBLIOTECA_ESTILOS_RAIZ, senão de
~/biblioteca-de-estilos.

Código de saída: 0 ok; 1 erro de uso, validação ou regra (ex.: id repetido);
2 erro de entrada/saída.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAIZ_PADRAO = Path.home() / "biblioteca-de-estilos"
VARIAVEL_RAIZ = "BIBLIOTECA_ESTILOS_RAIZ"
ARQUIVO_METADADOS = "estilo.json"
ARQUIVO_MANUAL = "manual.json"
EXTENSOES_CAPA = (".png", ".jpg", ".jpeg", ".webp")
TAMANHO_MAX_MANUAL = 5 * 1024 * 1024
TAMANHO_MAX_CAPA = 20 * 1024 * 1024
TAMANHO_MAX_ID = 64
TAMANHO_MAX_NOME = 120
TAMANHO_MAX_DESCRICAO = 2000
VERSAO_FORMATO = 1

_PADRAO_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_PADRAO_NOME_CAPA = re.compile(r"capa\.(png|jpg|jpeg|webp)")
_PADRAO_NOME_MANUAL = re.compile(r"manual-[0-9a-f]{64}\.json")
_PADRAO_HASH = re.compile(r"[0-9a-f]{64}")


class ErroBiblioteca(Exception):
    """Erro de uso, validação ou regra da biblioteca (exit 1)."""


# --------------------------------------------------------------------------- utilitários


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_bytes(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def _sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def _gravar_novo(caminho: Path, dados: bytes) -> None:
    """Grava arquivo novo; falha se já existir (modo 'xb')."""
    with caminho.open("xb") as f:
        f.write(dados)


# --------------------------------------------------------------------------- validação


def validar_id(id_estilo: str) -> str:
    """Aceita só slug seguro: minúsculas sem acento, números e hífens."""
    if not isinstance(id_estilo, str) or not id_estilo or len(id_estilo) > TAMANHO_MAX_ID:
        raise ErroBiblioteca(f"id inválido: use de 1 a {TAMANHO_MAX_ID} caracteres")
    if not _PADRAO_ID.fullmatch(id_estilo):
        raise ErroBiblioteca(
            "id inválido: use só letras minúsculas sem acento, números e hífens "
            "(ex.: 'neon-noturno')"
        )
    return id_estilo


def pasta_do_estilo(raiz: Path, id_estilo: str) -> Path:
    """Monta o caminho da pasta do estilo e garante que ele fica dentro da raiz."""
    validar_id(id_estilo)
    raiz_resolvida = raiz.resolve()
    entrada = raiz_resolvida / id_estilo
    if entrada.is_symlink():
        raise ErroBiblioteca("link simbólico na pasta do estilo não é aceito")
    destino = entrada.resolve()
    if destino.parent != raiz_resolvida:
        raise ErroBiblioteca("caminho do estilo fora da biblioteca")
    return destino


def _texto(valor: str | None, rotulo: str, limite: int, obrigatorio: bool) -> str:
    texto = (valor or "").strip()
    if obrigatorio and not texto:
        raise ErroBiblioteca(f"{rotulo} é obrigatório")
    if len(texto) > limite:
        raise ErroBiblioteca(f"{rotulo} passa de {limite} caracteres")
    if "\x00" in texto or (rotulo != "descrição" and "\n" in texto):
        raise ErroBiblioteca(f"{rotulo} contém caractere não permitido")
    return texto


def _arquivo_de_origem(caminho_texto: str, rotulo: str, tamanho_max: int) -> Path:
    """Confere que a origem é arquivo comum, sem link simbólico, e dentro do limite."""
    caminho = Path(caminho_texto).expanduser()
    if caminho.is_symlink():
        raise ErroBiblioteca(f"{rotulo}: link simbólico não é aceito ({caminho})")
    if not caminho.is_file():
        raise ErroBiblioteca(f"{rotulo}: arquivo não encontrado ({caminho})")
    if caminho.stat().st_size > tamanho_max:
        raise ErroBiblioteca(f"{rotulo}: arquivo maior que {tamanho_max} bytes")
    return caminho.resolve()


def _extensao_capa(origem: Path) -> str:
    extensao = origem.suffix.lower()
    if extensao not in EXTENSOES_CAPA:
        raise ErroBiblioteca(
            f"capa: extensão não suportada ({extensao or 'sem extensão'}); "
            f"use {', '.join(EXTENSOES_CAPA)}"
        )
    return extensao


def _ler_manual(dados: bytes) -> Any:
    try:
        def rejeitar(valor):
            raise ValueError(f"número não finito: {valor}")
        conteudo = json.loads(dados.decode("utf-8"), parse_constant=rejeitar)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ErroBiblioteca(f"manual não é JSON válido em UTF-8: {exc}") from exc
    if not isinstance(conteudo, (dict, list)):
        raise ErroBiblioteca("manual deve ser um objeto ou uma lista JSON")
    return conteudo


def _estado_manual(dados: bytes, conteudo: Any) -> dict[str, Any]:
    return {
        "valido": True,
        "tipo": "objeto" if isinstance(conteudo, dict) else "lista",
        "quantidade_de_itens": len(conteudo),
        "tamanho_bytes": len(dados),
        "sha256": _sha256_bytes(dados),
        "verificado_em": agora_iso(),
    }


# --------------------------------------------------------------------------- operações


def cadastrar_estilo(
    raiz: Path,
    *,
    id_estilo: str,
    nome: str,
    manual: str,
    descricao: str = "",
    capa: str | None = None,
) -> dict[str, Any]:
    """Cadastra um estilo novo. Nunca sobrescreve: id repetido vira erro."""
    validar_id(id_estilo)
    nome_limpo = _texto(nome, "nome", TAMANHO_MAX_NOME, obrigatorio=True)
    descricao_limpa = _texto(descricao, "descrição", TAMANHO_MAX_DESCRICAO, obrigatorio=False)

    # Tudo é lido e validado antes de criar qualquer pasta.
    origem_manual = _arquivo_de_origem(manual, "manual", TAMANHO_MAX_MANUAL)
    dados_manual = origem_manual.read_bytes()
    conteudo_manual = _ler_manual(dados_manual)
    from validar_manual_estilo import validar
    erros = validar(conteudo_manual)
    if erros:
        raise ErroBiblioteca("manual de estilo inválido: " + "; ".join(erros))

    origem_capa: Path | None = None
    dados_capa: bytes | None = None
    extensao_capa = ""
    if capa is not None:
        origem_capa = _arquivo_de_origem(capa, "capa", TAMANHO_MAX_CAPA)
        extensao_capa = _extensao_capa(origem_capa)
        dados_capa = origem_capa.read_bytes()

    pasta = pasta_do_estilo(raiz, id_estilo)
    raiz.mkdir(parents=True, exist_ok=True)
    try:
        pasta.mkdir()  # exclusivo: falha se a pasta já existe
    except FileExistsError as exc:
        raise ErroBiblioteca(
            f"já existe um estilo com id '{id_estilo}'; não sobrescrevo"
        ) from exc

    try:
        _gravar_novo(pasta / ARQUIVO_MANUAL, dados_manual)

        capa_meta: dict[str, Any] | None = None
        if dados_capa is not None and origem_capa is not None:
            nome_capa = f"capa{extensao_capa}"
            _gravar_novo(pasta / nome_capa, dados_capa)
            capa_meta = {
                "arquivo": nome_capa,
                "origem": str(origem_capa),
                "tamanho_bytes": len(dados_capa),
                "sha256": _sha256_bytes(dados_capa),
                "copiado_em": agora_iso(),
            }

        metadados: dict[str, Any] = {
            "formato": VERSAO_FORMATO,
            "id": id_estilo,
            "nome": nome_limpo,
            "descricao": descricao_limpa,
            "criado_em": agora_iso(),
            "origem": {
                "manual": str(origem_manual),
                "copiado_em": agora_iso(),
            },
            "manual": {
                "arquivo": ARQUIVO_MANUAL,
                "estado": _estado_manual(dados_manual, conteudo_manual),
            },
            "capa": capa_meta,
        }
        texto = json.dumps(metadados, ensure_ascii=False, indent=2) + "\n"
        _gravar_novo(pasta / ARQUIVO_METADADOS, texto.encode("utf-8"))
    except BaseException:
        # A pasta foi criada por esta chamada, então é seguro desfazer tudo.
        shutil.rmtree(pasta, ignore_errors=True)
        raise
    return metadados


def _nome_manual(metadados: dict[str, Any]) -> str:
    manual = metadados.get("manual")
    nome = manual.get("arquivo") if isinstance(manual, dict) else None
    if nome != ARQUIVO_MANUAL and (not isinstance(nome, str) or not _PADRAO_NOME_MANUAL.fullmatch(nome)):
        raise ErroBiblioteca("nome de arquivo do manual inválido")
    return nome


def _verificar_integridade(pasta: Path, metadados: dict[str, Any]) -> dict[str, Any]:
    """Confere os arquivos copiados. Só usa nomes fixos, nunca o que vem do JSON."""
    manual_meta = metadados.get("manual")
    esperado = None
    if isinstance(manual_meta, dict) and isinstance(manual_meta.get("estado"), dict):
        esperado = manual_meta["estado"].get("sha256")

    nome_manual = _nome_manual(metadados)
    if nome_manual != ARQUIVO_MANUAL and nome_manual != f"manual-{esperado}.json":
        raise ErroBiblioteca("nome e hash do manual não correspondem")
    manual = pasta / nome_manual
    if manual.is_symlink() or not manual.is_file():
        estado_manual = "ausente"
    else:
        estado_manual = "integro" if _sha256_arquivo(manual) == esperado else "alterado"

    estado_capa: str | None = None
    capa_meta = metadados.get("capa")
    if isinstance(capa_meta, dict):
        nome = capa_meta.get("arquivo")
        if not isinstance(nome, str) or not _PADRAO_NOME_CAPA.fullmatch(nome):
            estado_capa = "invalida"
        else:
            capa = pasta / nome
            if capa.is_symlink() or not capa.is_file():
                estado_capa = "ausente"
            else:
                estado_capa = (
                    "integro" if _sha256_arquivo(capa) == capa_meta.get("sha256") else "alterado"
                )
    return {"manual": estado_manual, "capa": estado_capa}


def ler_estilo(raiz: Path, id_estilo: str, *, com_manual: bool = False) -> dict[str, Any]:
    """Lê metadados de um estilo; com com_manual=True inclui o conteúdo do manual."""
    pasta = pasta_do_estilo(raiz, id_estilo)
    meta_path = pasta / ARQUIVO_METADADOS
    if meta_path.is_symlink() or not meta_path.is_file():
        raise ErroBiblioteca(f"estilo '{id_estilo}' não encontrado")
    try:
        metadados = json.loads(meta_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErroBiblioteca(f"estilo '{id_estilo}': estilo.json corrompido ({exc})") from exc
    if not isinstance(metadados, dict) or metadados.get("id") != id_estilo:
        raise ErroBiblioteca(f"estilo '{id_estilo}': id nos metadados não bate com a pasta")

    resultado = dict(metadados)
    resultado["caminho"] = str(pasta)
    resultado["integridade"] = _verificar_integridade(pasta, metadados)
    if com_manual:
        manual = pasta / _nome_manual(metadados)
        if resultado["integridade"]["manual"] != "integro":
            raise ErroBiblioteca(f"estilo '{id_estilo}': manual alterado ou ausente")
        if manual.is_symlink() or not manual.is_file():
            raise ErroBiblioteca(f"estilo '{id_estilo}': manual ausente")
        resultado["manual_conteudo"] = _ler_manual(manual.read_bytes())
    return resultado


def atualizar_manual(raiz: Path, id_estilo: str, manual: str, hash_esperado: str) -> dict[str, Any]:
    """Adiciona versão imutável e troca o ponteiro de metadados atomicamente.

    Exige hash que o chamador leu antes. O lock exclusivo serializa escritores
    deste utilitário; escritores externos precisam respeitar a mesma convenção.
    """
    if not isinstance(hash_esperado, str) or not _PADRAO_HASH.fullmatch(hash_esperado):
        raise ErroBiblioteca("hash esperado precisa conter 64 caracteres hexadecimais minúsculos")
    origem = _arquivo_de_origem(manual, "manual", TAMANHO_MAX_MANUAL)
    dados = origem.read_bytes()
    conteudo = _ler_manual(dados)
    from validar_manual_estilo import validar
    erros = validar(conteudo)
    if erros:
        raise ErroBiblioteca("manual de estilo inválido: " + "; ".join(erros))
    pasta = pasta_do_estilo(raiz, id_estilo)
    if not pasta.is_dir():
        raise ErroBiblioteca("estilo não encontrado")
    lock = pasta / ".atualizacao.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ErroBiblioteca("outra atualização está em andamento ou deixou um lock; verifique antes de tentar novamente") from exc
    os.close(descriptor)
    temp_path = None
    try:
        meta_path = pasta / ARQUIVO_METADADOS
        if meta_path.is_symlink() or not meta_path.is_file():
            raise ErroBiblioteca("metadados do estilo ausentes ou inválidos")
        meta_original = meta_path.read_bytes()
        atual = ler_estilo(raiz, id_estilo, com_manual=True)
        if atual["integridade"]["manual"] != "integro" or atual["manual"]["estado"]["sha256"] != hash_esperado:
            raise ErroBiblioteca("conflito: o manual atual mudou desde a leitura")
        atual.pop("integridade", None)
        atual.pop("caminho", None)
        atual.pop("manual_conteudo", None)
        anterior = atual["manual"]
        historico = atual.get("historico_manuais", [])
        if not isinstance(historico, list):
            raise ErroBiblioteca("histórico de manuais inválido")
        novo_hash = _sha256_bytes(dados)
        if novo_hash == hash_esperado:
            raise ErroBiblioteca("o novo manual é idêntico ao atual")
        novo_nome = f"manual-{novo_hash}.json"
        try:
            _gravar_novo(pasta / novo_nome, dados)
        except FileExistsError as exc:
            existente = pasta / novo_nome
            if existente.is_symlink() or not existente.is_file() or existente.read_bytes() != dados:
                raise ErroBiblioteca("arquivo de versão existente não corresponde ao novo manual") from exc
            # Reusa bytes idênticos, por exemplo após falha antes da troca
            # atômica dos metadados ou ao retornar a uma versão anterior.
        historico.append({"arquivo": anterior["arquivo"], "sha256": hash_esperado,
                          "registrado_em": agora_iso()})
        atual["historico_manuais"] = historico
        atual["manual"] = {"arquivo": novo_nome, "estado": _estado_manual(dados, conteudo),
                           "origem": str(origem), "atualizado_em": agora_iso()}
        texto = (json.dumps(atual, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
        with tempfile.NamedTemporaryFile(dir=pasta, prefix=".estilo-", suffix=".tmp", delete=False) as f:
            temp_path = Path(f.name)
            f.write(texto)
            f.flush()
            os.fsync(f.fileno())
        # Detecta intervenções externas observadas desde a leitura inicial.
        if meta_path.is_symlink() or meta_path.read_bytes() != meta_original or _sha256_arquivo(pasta / anterior["arquivo"]) != hash_esperado:
            raise ErroBiblioteca("conflito: metadados ou manual mudaram durante a atualização")
        os.replace(temp_path, meta_path)
        temp_path = None
        return atual
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def listar_estilos(raiz: Path) -> list[dict[str, Any]]:
    """Lista os estilos válidos. Pasta corrompida aparece com 'erro', sem derrubar a lista."""
    if not raiz.is_dir():
        return []
    itens: list[dict[str, Any]] = []
    for entrada in sorted(raiz.iterdir()):
        if entrada.is_symlink() or not entrada.is_dir():
            continue
        if not _PADRAO_ID.fullmatch(entrada.name) or not (entrada / ARQUIVO_METADADOS).is_file():
            continue
        try:
            completo = ler_estilo(raiz, entrada.name)
        except (ErroBiblioteca, OSError) as exc:
            itens.append({"id": entrada.name, "erro": str(exc)})
            continue
        itens.append(
            {
                "id": completo["id"],
                "nome": completo.get("nome", ""),
                "descricao": completo.get("descricao", ""),
                "criado_em": completo.get("criado_em", ""),
                "tem_capa": completo.get("capa") is not None,
                "capa_caminho": str(Path(completo["caminho"]) / completo["capa"]["arquivo"]) if completo.get("capa") and completo["integridade"]["capa"] == "integro" else None,
                "integridade": completo["integridade"],
            }
        )
    return itens


# --------------------------------------------------------------------------- CLI


def _resolver_raiz(valor: str | None) -> Path:
    if valor:
        return Path(valor).expanduser()
    ambiente = os.environ.get(VARIAVEL_RAIZ)
    if ambiente:
        return Path(ambiente).expanduser()
    return RAIZ_PADRAO


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Biblioteca local de estilos.")
    parser.add_argument("--raiz", help=f"pasta da biblioteca (padrão: ${VARIAVEL_RAIZ} ou {RAIZ_PADRAO})")
    sub = parser.add_subparsers(dest="comando", required=True)

    cad = sub.add_parser("cadastrar", help="cadastra um estilo novo (não sobrescreve)")
    cad.add_argument("--id", required=True, help="slug seguro, ex.: neon-noturno")
    cad.add_argument("--nome", required=True)
    cad.add_argument("--descricao", default="")
    cad.add_argument("--manual", required=True, help="caminho do manual JSON existente")
    cad.add_argument("--capa", help="caminho de uma capa local (png, jpg, jpeg ou webp)")

    lis = sub.add_parser("listar", help="lista os estilos cadastrados")
    lis.add_argument("--json", action="store_true", help="saída em JSON")

    mos = sub.add_parser("mostrar", help="mostra um estilo")
    mos.add_argument("id")
    mos.add_argument("--manual", action="store_true", help="inclui o conteúdo do manual")

    atu = sub.add_parser("atualizar", help="acrescenta uma versão do manual sem perder as anteriores")
    atu.add_argument("id")
    atu.add_argument("--manual", required=True, help="arquivo JSON com novo manual validado")
    atu.add_argument("--hash-esperado", required=True, help="SHA-256 do manual atual obtido em mostrar")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    raiz = _resolver_raiz(args.raiz)
    try:
        if args.comando == "cadastrar":
            meta = cadastrar_estilo(
                raiz,
                id_estilo=args.id,
                nome=args.nome,
                descricao=args.descricao,
                manual=args.manual,
                capa=args.capa,
            )
            print(json.dumps(meta, ensure_ascii=False, indent=2))
        elif args.comando == "listar":
            itens = listar_estilos(raiz)
            if args.json:
                print(json.dumps(itens, ensure_ascii=False, indent=2))
            elif not itens:
                print("Nenhum estilo cadastrado.")
            else:
                for item in itens:
                    if "erro" in item:
                        print(f"{item['id']}\tERRO: {item['erro']}")
                    else:
                        print(f"{item['id']}\t{item['nome']}\tmanual={item['integridade']['manual']}")
        elif args.comando == "mostrar":
            dados = ler_estilo(raiz, args.id, com_manual=args.manual)
            print(json.dumps(dados, ensure_ascii=False, indent=2))
        elif args.comando == "atualizar":
            dados = atualizar_manual(raiz, args.id, args.manual, args.hash_esperado)
            print(json.dumps(dados, ensure_ascii=False, indent=2))
    except ErroBiblioteca as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"erro de entrada/saída: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
