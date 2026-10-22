import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import forge


class EvidenceTests(unittest.TestCase):
    def test_summary_reader_rejects_malformed_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            for content in ("not JSON", "[]", '{"totalTestCount": true}'):
                response = subprocess.CompletedProcess([], 0, content, "")
                with patch("forge.subprocess.run", return_value=response):
                    self.assertIn("error", forge.read_test_summary(Path(directory)))

    def test_summary_reader_preserves_counts_and_destination(self):
        data = {"totalTestCount": 9, "passedTests": 8, "failedTests": 1, "skippedTests": 0,
                "expectedFailures": 0, "result": "Failed", "devicesAndConfigurations": [{"device": {"osVersion": "18.0"}}]}
        with tempfile.TemporaryDirectory() as directory:
            response = subprocess.CompletedProcess([], 0, json.dumps(data), "")
            with patch("forge.subprocess.run", return_value=response):
                self.assertEqual(forge.read_test_summary(Path(directory)), data)

    def test_dirty_source_changes_fingerprint_without_following_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Model.swift"
            source.write_text("before")
            (root / "link").symlink_to(root / "outside-missing")
            response = subprocess.CompletedProcess([], 0, b"Model.swift\x00link\x00", b"")
            with patch("forge.subprocess.run", return_value=response):
                first = forge.source_fingerprint(root)["sha256"]
                source.write_text("after")
                second = forge.source_fingerprint(root)["sha256"]
                self.assertIsNotNone(first)
                self.assertNotEqual(first, second)
