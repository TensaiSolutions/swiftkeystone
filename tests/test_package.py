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
