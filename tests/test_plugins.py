"""Verificações de contrato, sem rede nem serviços pagos."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_plugins import COMPLETE, INTERNAL, NAMES, validate_all, validate_complete, validate_plugin
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

    def test_openai_archive_carries_root_manifests_and_leaves_claude_files_out(self):
        import json
        import zipfile
        with tempfile.TemporaryDirectory() as temp:
            inventory = package(Path(temp))
            for row in inventory:
                with self.subTest(plugin=row["plugin"]), zipfile.ZipFile(Path(temp) / row["openai_archive"]) as archive:
                    names = set(archive.namelist())
                    self.assertIn("plugin.json", names)
                    self.assertIn("mcp.json", names)
                    self.assertIn(f"skills/{row['plugin']}/SKILL.md", names)
                    self.assertIn(f"skills/{row['plugin']}/references/checks.json", names)
                    self.assertFalse(any(n.split("/")[0] in {".claude-plugin", ".codex-plugin", "agents"} for n in names))
                    manifest = json.loads(archive.read("plugin.json"))
                    self.assertNotIn("requires_local_executor", manifest["extensions"]["com.openai"])
                    self.assertIs(manifest["extensions"]["com.openai"]["review"]["commerce"], False)
                    servers = json.loads(archive.read("mcp.json"))["mcpServers"]
                    self.assertEqual(len(servers), 1)

    def test_submission_gate_reports_missing_listing_material(self):
        import validate_plugins
        original = validate_plugins.listing

        def sem_site(name):
            data = original(name)
            data["extensions"]["com.openai"]["interface"].pop("websiteURL")
            return data

        with mock.patch.object(validate_plugins, "listing", sem_site):
            report = validate_plugin(ROOT / "plugins/sofia-english")
        self.assertIn("websiteURL", report["missing_listing_fields"])

        # Hoje só falta o vídeo de demonstração, que a revisão inicial do MCP exige.
        for name in NAMES:
            with self.subTest(plugin=name):
                self.assertEqual(validate_plugin(ROOT / "plugins" / name)["missing_listing_fields"],
                                 ["review.demo_recording_url"])

        def com_video(name):
            data = original(name)
            data["extensions"]["com.openai"]["review"]["demo_recording_url"] = "https://example.com/demo.mp4"
            return data

        with mock.patch.object(validate_plugins, "listing", com_video), tempfile.TemporaryDirectory() as temp:
            inventory = package(Path(temp), require_submission=True)
            self.assertTrue(all(row["missing_listing_fields"] == [] for row in inventory))

    def test_base_listing_fields_must_be_english(self):
        import validate_plugins
        original = validate_plugins.listing

        def em_portugues(name):
            data = original(name)
            data["extensions"]["com.openai"]["interface"]["shortDescription"] = "Roteiros e análise de vídeos"
            data["extensions"]["com.openai"]["interface"]["capabilities"][0] = "Escrever roteiros de criação"
            return data

        with mock.patch.object(validate_plugins, "listing", em_portugues):
            report = validate_plugin(ROOT / "plugins/sofia-br")
        self.assertTrue(any("fora do inglês" in e for e in report["errors"]))

    def test_slow_regex_is_rejected(self):
        from validate_plugins import js_regex_errors
        lentas = js_regex_errors([["(?:^|[.!?\\n]\\s*)y está bien", "i"], ["^\\s*[-*•]\\s+", "m"]])
        self.assertEqual(len(lentas), 2)
        self.assertTrue(all("ms num texto" in e for e in lentas))
        self.assertEqual(js_regex_errors([["^[ \\t]*[-*•][ \\t]+", "m"]]), [])

    def test_openai_archive_rejects_links_to_folders_it_leaves_out(self):
        from package_plugins import package_openai
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "sofia-english"
            shutil.copytree(ROOT / "plugins/sofia-english", dest)
            readme = dest / "README.md"
            readme.write_text(readme.read_text() + "\n[critic](agents/critic.md)\n")
            # O empacotador inspeciona o ZIP e se recusa a entregá-lo com o link quebrado.
            with self.assertRaises(ValueError) as erro:
                package_openai("sofia-english", dest, Path(temp))
            self.assertIn("agents/critic.md", str(erro.exception))

    def test_plugins_ship_text_only(self):
        for name in NAMES:
            for path in (ROOT / "plugins" / name).rglob("*"):
                if not path.is_file() or path.name in ALLOWED_NAMES:
                    continue
                with self.subTest(plugin=name, path=str(path.relative_to(ROOT))):
                    self.assertIn(path.suffix.lower(), ALLOWED_SUFFIXES)
                    self.assertNotEqual(path.read_bytes()[:2], b"#!")

    def test_portal_rules_catch_every_problem_the_directory_reported(self):
        from validate_plugins import autofix, portal_issues
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "sofia-english"
            shutil.copytree(ROOT / "plugins/sofia-english", dest)
            self.assertEqual(portal_issues(dest), [])
            (dest / "plugin.json").write_text("{}")
            (dest / "scripts").mkdir()
            (dest / "scripts/prepare.py").write_text("#!/usr/bin/env python3\n")
            (dest / "templates").mkdir()
            (dest / "templates/dashboard.html").write_text("<html></html>")
            (dest / "package.json").write_text("{}")
            shutil.copy(dest / "assets/icon.png", dest / ".claude-plugin/icon.png")
            (dest / "setup.md").write_text("Read `GEMINI_API_KEY` from the environment.")
            readme = dest / "README.md"
            # Tira a palavra Privacy de qualquer rótulo de link ([Privacy], [Privacy Policy] …).
            readme.write_text(re.sub(r"\[([^\]]*?)Privacy([^\]]*)\]", r"[\1Privacidade\2]", readme.read_text()))
            skill = dest / "skills/sofia-english/SKILL.md"
            text = skill.read_text()
            skill.write_text(text.replace("description: ", "description: wrapped\n  ", 1))
            found = "\n".join(portal_issues(dest))
            for expected in ("plugin.json agent-plugins", "prepare.py", "dashboard.html", "package.json",
                             ".claude-plugin/icon.png", "setup.md", "Frontmatter", "Privacy"):
                with self.subTest(expected=expected):
                    self.assertIn(expected, found)
            self.assertTrue(autofix(dest))
            self.assertNotIn("Frontmatter", "\n".join(portal_issues(dest)))

    def test_plugins_have_no_agent_plugins_manifest_or_unused_icon(self):
        for name in NAMES:
            with self.subTest(plugin=name):
                folder = ROOT / "plugins" / name
                self.assertFalse((folder / "plugin.json").exists())
                self.assertFalse((folder / ".claude-plugin/icon.png").exists())

    def test_internal_plugins_follow_the_package_standard_but_never_ship_publicly(self):
        reports = {report["plugin"]: report for report in validate_all()}
        for name in INTERNAL:
            with self.subTest(plugin=name):
                self.assertNotIn(name, NAMES)
                self.assertEqual(reports[name]["errors"], [])
                self.assertTrue(reports[name]["skills"])
                self.assertEqual(reports[name]["missing_listing_fields"], [])
                folder = ROOT / "plugins" / name
                self.assertFalse((folder / "plugin.json").exists())
                self.assertTrue((folder / ".mcp.json").exists())
        with tempfile.TemporaryDirectory() as temp:
            inventory = package(Path(temp))
            self.assertEqual([row["plugin"] for row in inventory], list(NAMES))
            produced = {path.name for path in Path(temp).glob("*.zip")}
            self.assertFalse(any(name in zipped for name in INTERNAL for zipped in produced))

    def test_sofia_estrategista_lives_in_the_criadores_do_futuro_marketplace(self):
        # Desde a 2.0.0 a Sofia Estrategista fica em Criadores-do-Futuro/sofia-estrategista
        # (marketplace criadores-do-futuro). Aqui fica só a referência para lá.
        import json
        self.assertEqual(COMPLETE, ())
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        for catalog in (claude, codex):
            self.assertFalse(any(p["name"].startswith("sofia-estrategista") for p in catalog["plugins"]))
        self.assertFalse(list((ROOT / "plugins").glob("sofia-estrategista*")))
        self.assertIn("Criadores-do-Futuro/sofia-estrategista", claude["description"])
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for snippet in ("claude plugin marketplace add Criadores-do-Futuro/sofia-estrategista",
                        "claude plugin install sofia-estrategista@criadores-do-futuro"):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, readme)

    def test_complete_check_rejects_a_path_the_upload_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "sofia-english"
            shutil.copytree(ROOT / "plugins/sofia-english", dest)
            # Uma Sofia completa traz o conector; a cópia de exemplo ganha um para a checagem chegar aos caminhos.
            (dest / ".mcp.json").write_text('{"mcpServers": {"exemplo": {"url": "https://example.com/mcp"}}}')
            (dest / "assets/Fonte[wght].ttf").write_bytes(b"x")
            report = validate_complete(dest)
            self.assertTrue(any("Fonte[wght].ttf" in e for e in report["errors"]))

    def test_every_plugin_shows_the_same_name_to_people(self):
        import json
        for name in NAMES:
            for manifest in (ROOT / "listings" / f"{name}.json", ROOT / "plugins" / name / ".codex-plugin/plugin.json"):
                with self.subTest(plugin=name, manifest=manifest.name):
                    data = json.loads(manifest.read_text(encoding="utf-8"))
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
