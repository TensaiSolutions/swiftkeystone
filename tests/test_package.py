import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import forge
from scripts.package_release import package


class PackageTests(unittest.TestCase):
    def test_reproducible_archive_is_self_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, checksum = package(root)
            self.assertEqual(archive.name, f"swiftkeystone-{forge.VERSION}.zip")
            first = archive.read_bytes()
            package(root)
            self.assertEqual(first, archive.read_bytes())
            self.assertEqual(checksum.read_text().split()[0], hashlib.sha256(first).hexdigest())
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertTrue(all(name.startswith(f"swiftkeystone-{forge.VERSION}/") for name in names))
                self.assertFalse(any("__pycache__" in name or "/.git/" in name or name.endswith(".log") for name in names))
                bundle.extractall(root / "extracted")
            extracted = next((root / "extracted").iterdir())
            result = subprocess.run([sys.executable, str(extracted / "scripts" / "check_distribution.py")],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            app = root / "pilot"
            app.mkdir()
            result = subprocess.run([sys.executable, str(extracted / "forge.py"), "install", "--app", str(app)],
                                    cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((app / ".agents" / "skills" / "ios-verify" / "references" / "profile.md").exists())
            self.assertTrue((app / ".agents" / "skills" / "ios-verify" / "references" / "macos.md").exists())

    def test_extracted_candidate_runs_new_commands_without_source_checkout(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive, _ = package(root)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(root / "extract")
            extracted = root / "extract" / f"swiftkeystone-{forge.VERSION}"
            helper = extracted / "forge.py"
            app = root / "app";app.mkdir()
            def run(arguments):
                result = subprocess.run([sys.executable, str(helper), *arguments], cwd=root,
                    capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout
            run(["install", "--app", str(app)])
            result = json.loads(run(["update", "--app", str(app), "--from-release", str(extracted),
                                    "--output-dir", str(root / "staging"), "--dry-run"]))
            self.assertEqual(result["conflicts"], 0)
            self.assertFalse((root / "staging").exists())
            profile = app / ".ios-forge/app.json"
            profile.parent.mkdir()
            profile.write_text(json.dumps({"schema_version": 1, "name": "Fixture", "project": "App.xcodeproj",
                "scheme": "App", "destination": "platform=macOS", "checks": ["test"], "timeout_seconds": 30,
                "baseline_expectations": {"minimum_executed_tests": 1, "required_test_targets": ["Unit"]}}))
            self.assertIn("Profile is valid", run(["validate", str(profile)]))

            report = root / "report.json"
            report.write_text(json.dumps({"status": "passed", "checks": [
                {"name": "build", "status": "passed", "exit_code": 0}]}))
            text = run(["summary", str(report)])
            self.assertIn("Build-only", text)
            for skill, reference in (("ios-onboard", "baseline-audit"), ("ios-onboard", "skill-updates"),
                                     ("ios-verify", "evidence-comparison")):
                self.assertEqual((app / ".agents/skills" / skill / "references" / (reference + ".md")).read_bytes(),
                                 (extracted / "docs" / (reference + ".md")).read_bytes())
