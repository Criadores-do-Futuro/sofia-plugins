"""Transcrição palavra a palavra, com cache pelo CONTEÚDO do áudio.

    python3 transcrever.py <saida/> <take.mov> [<take2.mov> ...]
                           [--modelo large-v3] [--contexto "nomes próprios, ..."]
                           [--idioma pt] [--forcar]

Saída: `<saida>/<nome-do-take>.whisper.json` no formato que o resto do plugin
lê — `{language, duration, segments[], words[{word,start,end}]}` — mais um
campo `origem` com a identidade do áudio, o modelo e o contexto usados.

Por que este script existe:

  - No projeto 15 a transcrição inteira (3 takes, 8,7 min de áudio) rodou DUAS
    vezes, 7 min cada, porque o script de projeto não sabia que o áudio não
    tinha mudado. Aqui a chave é o conteúdo do arquivo: rodar de novo com o
    mesmo take devolve em 0,1 s.
  - O motor era o openai-whisper em FP32 na CPU (o aviso «FP16 is not
    supported on CPU» está no log). O `faster-whisper` (CTranslate2, int8) faz
    o mesmo modelo em uma fração do tempo e já está instalado, com o
    `large-v3` baixado. Se faltar, cai no whisper de sempre, com aviso.
  - A extração do áudio dos takes é I/O: sai em paralelo, uma thread por take.
    A transcrição em si é CPU e roda em fila — dois modelos grandes ao mesmo
    tempo numa máquina de 16 GB disputam memória e ficam mais lentos, não mais
    rápidos (medido).

O contexto (`--contexto`) é a lista de nomes próprios que o modelo vai errar
sem ajuda: produto, jogo, pessoa. No 15, «Cloud Code», «PayFive» e «Samadri»
foram o que sobrou sem ele — e o erro só aparece queimado na legenda.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oficina  # noqa: E402

MODELO_PADRAO = "large-v3-turbo"


def _wav(take, saida):
    """Áudio mono 16 kHz do take, só se ainda não existir para este conteúdo."""
    ident = oficina.identidade(take)
    wav = saida / f"{Path(take).stem}.{ident}.wav"
    if not wav.exists():
        oficina.ffmpeg("-i", str(take), "-vn", "-ac", "1", "-ar", "16000", str(wav))
    return wav, ident


def _motor(modelo):
    """O motor mais rápido que existir nesta máquina. Devolve (nome, transcrever).

    Ordem, medida no take 030 (148 s de áudio) com o mesmo `large-v3-turbo`:
      1. mlx-whisper  — roda na GPU do Apple Silicon; é a opção certa num Mac
      2. faster-whisper (CTranslate2 int8, CPU) — o large-v3 completo levou 359 s
         nesse take, mais lento que o openai-whisper turbo; só vale com modelo turbo
      3. openai-whisper (FP32 na CPU) — 167 s no mesmo take; é o que rodava antes
    """
    try:
        import mlx_whisper
        repo = modelo if "/" in modelo else f"mlx-community/whisper-{modelo}"

        def transcrever(wav, idioma, contexto):
            r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=repo, language=idioma,
                                       word_timestamps=True, initial_prompt=contexto or None,
                                       verbose=False)
            segmentos, palavras = [], []
            for s in r["segments"]:
                segmentos.append({"start": round(s["start"], 2), "end": round(s["end"], 2),
                                  "text": s["text"]})
                for w in s.get("words", []):
                    palavras.append({"word": w["word"], "start": round(w["start"], 2),
                                     "end": round(w["end"], 2)})
            return segmentos, palavras
        return f"mlx-whisper/{repo.split('/')[-1]}", transcrever
    except ImportError:
        pass
    try:
        from faster_whisper import WhisperModel
        import plataforma
        alvo = plataforma.transcricao()
        # CUDA float16 com NVIDIA; senão CPU int8 com todos os núcleos. O ctranslate2
        # sem CUDA compilado recusa "cuda": cai para a CPU em vez de parar
        try:
            if alvo["device"] != "cuda":
                raise ValueError("sem NVIDIA")
            m = WhisperModel(modelo, device="cuda", compute_type="float16")
        except (ValueError, RuntimeError):
            m = WhisperModel(modelo, device="cpu", compute_type="int8",
                             cpu_threads=os.cpu_count() or 4)

        def transcrever(wav, idioma, contexto):
            segs, _ = m.transcribe(str(wav), language=idioma, word_timestamps=True,
                                   initial_prompt=contexto or None, vad_filter=False,
                                   beam_size=5)
            segmentos, palavras = [], []
            for s in segs:
                segmentos.append({"start": round(s.start, 2), "end": round(s.end, 2),
                                  "text": s.text})
                for w in s.words or []:
                    palavras.append({"word": w.word, "start": round(w.start, 2),
                                     "end": round(w.end, 2)})
            return segmentos, palavras
        return f"faster-whisper/{modelo}", transcrever
    except ImportError:
        import whisper
        nome = "turbo" if modelo.startswith("large-v3") else modelo.split("/")[-1]
        m = whisper.load_model(nome)
        print("  aviso: faster-whisper ausente; usando openai-whisper em FP32 na CPU "
              "(3–4× mais lento). `pip install faster-whisper` resolve.", flush=True)

        def transcrever(wav, idioma, contexto):
            r = m.transcribe(str(wav), language=idioma, word_timestamps=True,
                             initial_prompt=contexto or None, verbose=False)
            segmentos, palavras = [], []
            for s in r["segments"]:
                segmentos.append({"start": round(s["start"], 2), "end": round(s["end"], 2),
                                  "text": s["text"]})
                for w in s.get("words", []):
                    palavras.append({"word": w["word"], "start": round(w["start"], 2),
                                     "end": round(w["end"], 2)})
            return segmentos, palavras
        return f"whisper/{nome}", transcrever


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("saida")
    ap.add_argument("takes", nargs="+")
    ap.add_argument("--modelo", default=MODELO_PADRAO)
    ap.add_argument("--contexto", default="")
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--forcar", action="store_true", help="ignora a cache")
    a = ap.parse_args()

    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    # a saída é `edicao/oficina/transcricao/`; a telemetria do projeto mora no pai dela
    with oficina.Cronometro(saida.parent, "transcrever",
                            args={"takes": len(a.takes), "modelo": a.modelo, "forcar": a.forcar}) as cron:
        cron.extra.update(takes=len(a.takes), palavras=0, daCache=0)
        _transcrever_takes(a, saida, cron)


def _transcrever_takes(a, saida, cron):
    t0 = time.time()

    # 1. o áudio de todos os takes, em paralelo (é I/O do ffmpeg, não CPU)
    with ThreadPoolExecutor(max_workers=min(4, len(a.takes))) as ex:
        wavs = list(ex.map(lambda t: _wav(t, saida), a.takes))

    # 2. quem já está transcrito com ESTE conteúdo, modelo e contexto, não roda
    pendentes = []
    for take, (wav, ident) in zip(a.takes, wavs):
        alvo = saida / f"{Path(take).stem}.whisper.json"
        if alvo.exists() and not a.forcar:
            try:
                o = json.loads(alvo.read_text(encoding="utf-8")).get("origem", {})
            except json.JSONDecodeError:
                o = {}
            if o.get("identidade") == ident and o.get("contexto", "") == a.contexto \
                    and o.get("modelo", "").endswith(a.modelo.split("/")[-1]):
                print(f"{alvo.name}: da cache ({o.get('modelo')})", flush=True)
                cron.extra["daCache"] += 1
                continue
        pendentes.append((take, wav, ident, alvo))
    if not pendentes:
        print(f"nada a transcrever · {time.time()-t0:.1f}s")
        return

    nome, transcrever = _motor(a.modelo)
    print(f"modelo {nome} carregado em {time.time()-t0:.0f}s", flush=True)
    for take, wav, ident, alvo in pendentes:
        t1 = time.time()
        segmentos, palavras = transcrever(wav, a.idioma, a.contexto)
        dur = palavras[-1]["end"] if palavras else 0
        alvo.write_text(json.dumps({
            "language": a.idioma, "duration": dur, "segments": segmentos, "words": palavras,
            "origem": {"arquivo": str(take), "identidade": ident, "modelo": nome,
                       "contexto": a.contexto},
        }, ensure_ascii=False), encoding="utf-8")
        cron.extra["palavras"] += len(palavras)
        print(f"{alvo.name}: {len(palavras)} palavras, {len(segmentos)} segmentos, "
              f"{dur:.0f}s de áudio em {time.time()-t1:.0f}s", flush=True)
    print(f"FIM · {time.time()-t0:.0f}s")


if __name__ == "__main__":
    import plataforma  # noqa: F401 — console em UTF-8 no Windows
    main()
