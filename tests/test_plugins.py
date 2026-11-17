"""Verificações de contrato e execução local, sem rede nem serviços pagos."""

import importlib.util
import json
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

    def test_comment_data_does_not_keep_author_identifiers(self):
        path = ROOT / "plugins/sofia/scripts/collect-public.py"
        spec = importlib.util.spec_from_file_location("comment_collector", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = {"title": "A real input", "comments": [
            {"text": "First", "like_count": 2, "author": "Name", "author_id": "private"},
            {"text": "Second", "like_count": 8, "author_url": "https://private.invalid"}]}
        result = module.sanitize(data, 1)
        self.assertEqual(result["comentarios"], [{"texto": "Second", "curtidas": 8}])
        self.assertNotIn("author", json.dumps(result))
        self.assertNotIn("private", json.dumps(result))

    @unittest.skipUnless(shutil.which("node"), "Requer Node")
    def test_external_video_upload_requires_explicit_flag_before_loading_sdk(self):
        script = ROOT / "plugins/sofia/scripts/analyze-video-gemini.mjs"
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.mp4"
            source.write_bytes(b"local fixture")
            result = subprocess.run(["node", str(script), str(source), str(Path(temp) / "result.json")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("--allow-upload", result.stderr)
            self.assertNotIn("ERR_MODULE_NOT_FOUND", result.stderr)
            self.assertFalse((Path(temp) / "result.json").exists())


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Requer FFmpeg")
class VideoPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.silent = cls.root / "video with ' quote.mp4"
        cls.voiced = cls.root / "with-audio.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        "testsrc2=size=160x120:rate=10:duration=4", "-c:v", "mpeg4", str(cls.silent)],
                       check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(cls.silent), "-f", "lavfi",
                        "-i", "sine=frequency=440:duration=4", "-c:v", "copy", "-c:a", "aac", "-shortest",
                        str(cls.voiced)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_script(self, name, *args):
        script = ROOT / "plugins" / name / "scripts/prepare-visual-analysis.py"
        return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)

    def test_each_locale_respects_budget_window_and_actual_media(self):
        for name in NAMES:
            with self.subTest(plugin=name):
                dest = self.root / (name + "-silent")
                result = self.run_script(name, self.silent, "--output", dest,
                                         "--start", 1, "--end", 3, "--max-frames", 5)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads((dest / "manifest.json").read_text())
                self.assertEqual(len(data["frames"]), 5)
                times = [f["seconds"] for f in data["frames"]]
                self.assertEqual(times, sorted(times))
                self.assertTrue(all(1 <= t < 3 for t in times))
                self.assertEqual(times[0], 1)
                self.assertIsNone(data["audio"])
                self.assertTrue(data["contact_sheets"])
                self.assertTrue(data["limitations"])
                self.assertTrue(all(Path(frame["path"]).is_file() for frame in data["frames"]))

    def test_audio_is_only_reported_when_created(self):
        dest = self.root / "audio-output"
        result = self.run_script("sofia-english", self.voiced, "--output", dest, "--max-frames", 2)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((dest / "manifest.json").read_text())
        self.assertTrue(Path(data["audio"]).is_file())
        self.assertGreater(Path(data["audio"]).stat().st_size, 0)

    def test_refuses_mixed_output_instead_of_reporting_stale_frames(self):
        dest = self.root / "existing-output"
        dest.mkdir()
        marker = dest / "keep.txt"
        marker.write_text("preserve")
        result = self.run_script("sofia", self.silent, "--output", dest)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), "preserve")
        self.assertFalse((dest / "manifest.json").exists())

    def test_refuses_saving_user_data_inside_installation(self):
        for name in NAMES:
            with self.subTest(plugin=name):
                dest = ROOT / "plugins" / name / "must-not-be-created"
                result = self.run_script(name, self.silent, "--output", dest)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(dest.exists())

    def test_invalid_inputs_fail_before_download_or_output_creation(self):
        cases = [
            [str(self.silent), "--max-frames", "0"],
            [str(self.silent), "--start", "nan"],
            [str(self.silent), "--start", "3", "--end", "1"],
            ["https://www.youtube.com/watch?v=example"],
            ["https://youtube.com.evil.invalid/watch?v=example", "--allow-download"],
        ]
        for name in NAMES:
            for args in cases:
                with self.subTest(plugin=name, args=args):
                    result = self.run_script(name, *args)
                    self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
