from pathlib import Path
import unittest

import forge
from scripts.check_distribution import readme_errors


class AdoptionDocumentationTests(unittest.TestCase):
    def test_stale_download_or_helper_path_fails_distribution_check(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        self.assertEqual(readme_errors(readme, forge.VERSION), [])
        for old, new in (
            (f"swiftkeystone-{forge.VERSION}.zip", "swiftkeystone-0.0.0.zip"),
            (f"swiftkeystone-{forge.VERSION}/forge.py", "swiftkeystone-0.0.0/forge.py"),
            (f"/releases/tag/v{forge.VERSION}", "/releases/tag/v0.0.0"),
        ):
            with self.subTest(stale=old):
                self.assertTrue(readme_errors(readme.replace(old, new), forge.VERSION))

    def test_missing_start_or_checksum_is_rejected(self):
        self.assertTrue(readme_errors("No adoption instructions", forge.VERSION))
        self.assertTrue(readme_errors(
            f"## Start here\nswiftkeystone-{forge.VERSION}.zip\n## Everyday workflow", forge.VERSION))
