#!/usr/bin/env python3
"""Analisa referências locais e prepara manual inicial, capa e evidências técnicas.

A leitura integral de quadros e trilhas não identifica por si só
legendas, efeitos, tracking, música ou intenção. Revise semanticamente depois.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from analisar_trilhas_audio import analisar_todas
from adicionar_audio_ao_manual import incorporar
from detectar_mudancas_visuais import detectar
from validar_manual_estilo import validar

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def run(*args: str) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"{Path(args[0]).name} falhou: {(result.stderr or result.stdout)[-2000:]}")


def gravar(path: Path, obj: object) -> None:
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def preparar(videos: list[Path], nome: str, destino: Path) -> dict:
    if not nome.strip() or not videos:
        raise ValueError('Informe nome e ao menos uma referência')
    fontes = [v.expanduser().resolve(strict=True) for v in videos]
    if any(not p.is_file() for p in fontes) or len(set(fontes)) != len(fontes):
        raise ValueError('Cada referência precisa ser um arquivo local distinto')
    destino = destino.expanduser().absolute()
    destino.mkdir(parents=False, exist_ok=False)
    fingerprints = [sha256(p) for p in fontes]
    relatorios, duracoes, quadros = [], [], []
    for i, fonte in enumerate(fontes, 1):
        arquivo_quadros = destino / f'ref-{i}-quadros.jsonl'
        run(sys.executable, str(ROOT / 'skills/sofia-editora/scripts/analisar_quadros.py'),
            str(fonte), '--saida', str(arquivo_quadros))
        todas = analisar_todas(fonte)
        gravar(destino / f'ref-{i}-trilhas-audio.json', todas)
        primeira = todas['trilhas'][0] if todas['trilhas'] else None
        audio = {'versao': 1, 'fonte': todas['fonte'], 'estado_fonte': todas['estado_fonte'],
                 'duracao_segundos': todas['duracao_segundos'], 'possui_audio': primeira is not None,
                 'processamento_sem_erro': primeira is not None, 'limiar_ruido_db': todas['limiar_ruido_db'],
                 'silencio_minimo_segundos': todas['silencio_minimo_segundos'],
                 'silencios': primeira['silencios'] if primeira else [],
                 'nivel_medio_dbfs': primeira['nivel_medio_dbfs'] if primeira else None}
        if primeira:
            audio['trilha'] = {'indice': primeira['indice_stream'],
                               'deslocamento_segundos': primeira['inicio_segundos'],
                               'deslocamento_verificado': primeira['inicio_verificado'],
                               'duracao_decodificada_segundos': primeira['duracao_decodificada_segundos']}
        gravar(destino / f'ref-{i}-audio.json', audio)
        cenas = detectar(arquivo_quadros)
        gravar(destino / f'ref-{i}-mudancas.json', cenas)
        duracoes.append(audio['duracao_segundos'])
        quadros.append(arquivo_quadros)
        relatorios.append(audio)
    argumentos = [sys.executable, str(ROOT / 'scripts/gerar_manual_medido.py'), *(str(q) for q in quadros)]
    for duracao in duracoes:
        argumentos.extend(('--duracao', str(duracao)))
    manual_temporario = destino / 'manual-visual.json'
    argumentos.extend(('--nome', nome, '--saida', str(manual_temporario)))
    run(*argumentos)
    manual = json.loads(manual_temporario.read_text(encoding='utf-8'))
    for i, audio in enumerate(relatorios, 1):
        manual = incorporar(manual, audio, f'ref-{i}')
    erros = validar(manual)
    if erros:
        raise ValueError('Manual inválido: ' + '; '.join(erros))
    gravar(destino / 'manual.json', manual)
    # A capa é um quadro extraído da primeira referência; não altera o original.
    run('ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-ss', str(duracoes[0] / 2),
        '-i', str(fontes[0]), '-frames:v', '1', '-n', str(destino / 'capa.jpg'))
    if not (destino / 'capa.jpg').is_file() or not (destino / 'capa.jpg').stat().st_size:
        raise ValueError('A extração da capa não produziu uma imagem')
    if any(sha256(fonte) != original for fonte, original in zip(fontes, fingerprints)):
        raise ValueError('Referência alterada durante a análise: não utilize o resultado parcial')
    registro = {'versao': 1, 'nome': nome, 'estado': 'medicao_tecnica_concluida',
                'referencias': [{'id': f'ref-{i}', 'fonte': str(p), 'sha256': fingerprints[i-1],
                                 'duracao_segundos': duracoes[i-1]} for i, p in enumerate(fontes, 1)],
                'manual': 'manual.json', 'capa': 'capa.jpg',
                'limites': ['Os quadros foram medidos, não interpretados semanticamente.',
                            'As trilhas de áudio são medidas individualmente; silêncio e nível não identificam música ou efeitos.',
                            'O manual inicial incorpora somente os dados da primeira trilha; consulte os relatórios para todas.',
                            'Projetos, fontes e parâmetros originais não foram recuperados; revise imagens e áudio.']}
    gravar(destino / 'analise.json', registro)
    return registro


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('videos', nargs='+', type=Path, help='Vídeos locais; arquivos não são copiados')
    parser.add_argument('--nome', required=True)
    parser.add_argument('--saida', required=True, type=Path, help='Pasta nova para os relatórios e manual')
    args = parser.parse_args()
    try:
        result = preparar(args.videos, args.nome, args.saida)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'Análise não concluída: {exc}. Se criada, a pasta de saída contém apenas resultados parciais.', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
