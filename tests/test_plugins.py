"""Verificações de contrato, sem rede nem serviços pagos."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_plugins import NAMES, validate_all, validate_plugin
from package_plugins import package

# O diretório da Anthropic só aceita texto e imagens de organizações não verificadas.
ALLOWED_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
ALLOWED_NAMES = {"LICENSE", ".gitignore"}


class PackageContractTests(unittest.TestCase):
    def test_all_packages_have_valid_structure_and_matching_catalogs(self):
        for report in validate_all():
            with self.subTest(plugin=report["plugin"]):
                self.assertEqual(report["errors"], [])
                self.assertTrue(report["skills"])

    def test_broken_reference_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "sofia-english"
            shutil.copytree(ROOT / "plugins/sofia-english", dest)
            (dest / "skills/sofia-english/references/principles.md").unlink()
            report = validate_plugin(dest)
            self.assertFalse(report["structure_valid"])
            self.assertTrue(any("principles.md" in e for e in report["errors"]))

    def test_archives_round_trip_through_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            inventory = package(Path(temp))
            self.assertEqual(len(inventory), 3)
            self.assertTrue(all(row["structure_valid"] for row in inventory))
            self.assertTrue(all(len(row["sha256"]) == 64 for row in inventory))
            self.assertTrue(all(not row["publication_ready"] for row in inventory))

    def test_submission_gate_rejects_missing_listing_material(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "Listagem incompleta"):
                package(Path(temp), require_submission=True)

    def test_plugins_ship_text_only(self):
        for name in NAMES:
            for path in (ROOT / "plugins" / name).rglob("*"):
                if not path.is_file() or path.name in ALLOWED_NAMES:
                    continue
                with self.subTest(plugin=name, path=str(path.relative_to(ROOT))):
                    self.assertIn(path.suffix.lower(), ALLOWED_SUFFIXES)
                    self.assertNotEqual(path.read_bytes()[:2], b"#!")

    def test_every_plugin_shows_the_same_name_to_people(self):
        import json
        for name in NAMES:
            for manifest in ("plugin.json", ".codex-plugin/plugin.json"):
                with self.subTest(plugin=name, manifest=manifest):
                    data = json.loads((ROOT / "plugins" / name / manifest).read_text(encoding="utf-8"))
                    display = data.get("displayName") or data.get("interface", {}).get("displayName")
                    if display is not None:
                        self.assertEqual(display, "Sofia")


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Requer FFmpeg")
class DocumentedVideoCommandsTests(unittest.TestCase):
    """Roda os comandos que as instruções mandam executar, com o mesmo formato."""

    def test_frames_audio_and_contact_sheets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            video = root / "video with ' quote.mp4"
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                            "testsrc2=size=160x120:rate=10:duration=4", "-f", "lavfi",
                            "-i", "sine=frequency=440:duration=4", "-c:v", "mpeg4", "-c:a", "aac",
                            "-shortest", str(video)], check=True, capture_output=True)
            out = root / "analise-01"
            (out / "frames").mkdir(parents=True)
            (out / "contacts").mkdir()
            probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                    "format=duration:stream=codec_type,width,height,r_frame_rate",
                                    "-of", "json", str(video)], check=True, capture_output=True, text=True)
            self.assertIn('"audio"', probe.stdout)
            base = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error"]
            subprocess.run(base + ["-i", str(video), "-vf", "fps=1/1,scale='min(960,iw)':-2",
                                   "-frames:v", "4", "-q:v", "3", str(out / "frames/t-%05d.jpg")], check=True)
            subprocess.run(base + ["-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "libmp3lame",
                                   "-b:a", "64k", str(out / "audio.mp3")], check=True)
            subprocess.run(base + ["-framerate", "1", "-i", str(out / "frames/t-%05d.jpg"), "-vf",
                                   "scale=240:-2,tile=5x4:padding=8:margin=8",
                                   str(out / "contacts/timeline-%03d.jpg")], check=True)
            self.assertEqual(len(list((out / "frames").glob("*.jpg"))), 4)
            self.assertGreater((out / "audio.mp3").stat().st_size, 0)
            self.assertTrue(list((out / "contacts").glob("*.jpg")))


if __name__ == "__main__":
    unittest.main()
