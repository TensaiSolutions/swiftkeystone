from pathlib import Path
import unittest

import forge
from scripts.check_distribution import readme_errors


class AdoptionDocumentationTests(unittest.TestCase):
    def test_stale_download_or_helper_path_fails_distribution_check(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
        self.assertEqual(readme_errors(readme, forge.PUBLISHED_VERSION), [])
        for old, new in (
            (f"swiftkeystone-{forge.PUBLISHED_VERSION}.zip", "swiftkeystone-0.0.0.zip"),
            (f"swiftkeystone-{forge.PUBLISHED_VERSION}/forge.py", "swiftkeystone-0.0.0/forge.py"),
            (f"/releases/tag/v{forge.PUBLISHED_VERSION}", "/releases/tag/v0.0.0"),
        ):
            with self.subTest(stale=old):
                self.assertTrue(readme_errors(readme.replace(old, new), forge.PUBLISHED_VERSION))

    def test_missing_start_or_checksum_is_rejected(self):
        self.assertTrue(readme_errors("No adoption instructions", forge.PUBLISHED_VERSION))
        self.assertTrue(readme_errors(
            f"## Start here\nswiftkeystone-{forge.PUBLISHED_VERSION}.zip\n## Everyday workflow", forge.PUBLISHED_VERSION))
