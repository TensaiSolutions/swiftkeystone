import contextlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

import forge


class ForgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.app = self.base / "An App"
        self.app.mkdir()
        self.project = self.app / "An App.xcodeproj"
        self.project.mkdir()
        self.output = self.base / "evidence"
        self.profile = self.app / ".ios-forge" / "app.json"
        self.data = {"schema_version": 1, "name": "An App", "project": "An App.xcodeproj",
                     "scheme": "An App", "destination": "platform=iOS Simulator,id=test-uuid",
                     "checks": ["build", "test"], "timeout_seconds": 5}
        forge.write_json(self.profile, self.data)
        self.summary = {"totalTestCount": 1, "passedTests": 1, "failedTests": 0, "skippedTests": 0,
                        "expectedFailures": 0, "result": "Passed"}
        self.summary_patch = patch("forge.read_test_summary", return_value=self.summary)
        self.summary_patch.start()
        self.addCleanup(self.summary_patch.stop)

    def call(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            result = forge.main(list(args))
        return result, out.getvalue(), err.getvalue()

    def save(self):
        forge.write_json(self.profile, self.data)

    def fake_xcode(self, body):
        binary = self.base / "bin" / "xcodebuild"
        binary.parent.mkdir()
        binary.write_text(f"#!{sys.executable}\nimport sys, time, json\nif '-version' in sys.argv:\n    print('Xcode Test Fixture'); sys.exit(0)\n{body}\n")
        binary.chmod(0o755)
        return patch.dict(os.environ, {"PATH": str(binary.parent) + os.pathsep + os.environ.get("PATH", "")})

    def report(self):
        return json.loads(next(self.output.glob("*/report.json")).read_text())

    def test_init_preserves_existing_profile(self):
        before = self.profile.read_bytes()
        code, _, _ = self.call("init", "--app", str(self.app), "--name", "Other", "--project", "Other.xcodeproj",
                               "--scheme", "Other", "--destination", "anything")
        self.assertEqual(code, 2)
        self.assertEqual(self.profile.read_bytes(), before)

    def test_init_creates_valid_profile_with_no_other_app_changes(self):
        self.profile.unlink()
        code, _, error = self.call("init", "--app", str(self.app), "--name", "An App", "--project", "An App.xcodeproj",
                                   "--scheme", "An App", "--destination", "platform=iOS Simulator,id=test-uuid")
        self.assertEqual(code, 0, error)
        self.assertEqual(forge.load_profile(self.profile), dict(self.data, timeout_seconds=900))
        self.assertFalse((self.app / "AGENTS.md").exists())
        self.assertFalse((self.app / ".agents").exists())

    def test_init_rejects_invalid_input_without_creating_profile(self):
        self.profile.unlink()
        code, _, _ = self.call("init", "--app", str(self.app), "--name", "Other", "--project", "../Other.xcodeproj",
                               "--scheme", "Other", "--destination", "anything")
        self.assertEqual(code, 2)
        self.assertFalse(self.profile.exists())

    def test_validate_rejects_bad_values(self):
        for field, value in (("schema_version", True), ("timeout_seconds", True), ("timeout_seconds", 0),
                             ("checks", []), ("checks", ["build", "build"]), ("checks", ["archive"]),
                             ("project", "../Secret.xcodeproj"), ("scheme", "  "), ("surprise", "ignored")):
            with self.subTest(field=field, value=value):
                candidate = dict(self.data, **{field: value})
                forge.write_json(self.profile, candidate)
                self.assertEqual(self.call("validate", str(self.profile))[0], 2)

    def test_install_is_idempotent_and_preserves_instructions(self):
        instructions = self.app / "AGENTS.md"
        instructions.write_text("Keep my conventions.\n")
        self.assertEqual(self.call("install", "--app", str(self.app))[0], 0)
        before = forge.inventory(self.app / ".agents" / "skills")
        self.assertEqual(self.call("install", "--app", str(self.app))[0], 0)
        self.assertEqual(before, forge.inventory(self.app / ".agents" / "skills"))
        self.assertEqual(instructions.read_text(), "Keep my conventions.\n")
        for name in forge.SKILLS:
            self.assertTrue((self.app / ".agents" / "skills" / name / "SKILL.md").is_file())

    def test_conflict_preflight_prevents_partial_install(self):
        conflict = self.app / ".agents" / "skills" / forge.SKILLS[-1]
        conflict.mkdir(parents=True)
        (conflict / "SKILL.md").write_text("User's skill")
        self.assertEqual(self.call("install", "--app", str(self.app))[0], 2)
        self.assertFalse((conflict.parent / forge.SKILLS[0]).exists())
        self.assertEqual((conflict / "SKILL.md").read_text(), "User's skill")

    def test_install_rejects_escaping_symlink(self):
        external = self.base / "outside"
        external.mkdir()
        (self.app / ".agents").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.call("install", "--app", str(self.app))[0], 2)
        self.assertEqual(list(external.iterdir()), [])

    def test_dry_runs_have_no_writes(self):
        self.assertEqual(self.call("install", "--app", str(self.app), "--dry-run")[0], 0)
        self.assertFalse((self.app / ".agents").exists())
        code, out, _ = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output), "--dry-run")
        self.assertEqual(code, 0)
        command = json.loads(out)["checks"][0]["argv"]
        self.assertEqual(command[command.index("-project") + 1], str(self.project.resolve()))
        self.assertFalse(self.output.exists())

    def test_output_and_project_cannot_escape_boundaries(self):
        self.assertEqual(self.call("verify", "--app", str(self.app), "--output-dir", str(self.app / "logs"), "--dry-run")[0], 2)
        other = self.base / "External.xcodeproj"
        other.mkdir()
        self.project.rmdir()
        self.project.symlink_to(other, target_is_directory=True)
        self.assertEqual(self.call("verify", "--app", str(self.app), "--output-dir", str(self.output), "--dry-run")[0], 2)

    def test_success_records_commands_and_private_run(self):
        # Use a real child process but a fake executable: these are runner tests, not Xcode tests.
        self.data["scheme"] = "App; $(touch DO_NOT_CREATE)"
        self.save()
        with self.fake_xcode("print(json.dumps(sys.argv[1:]))"), patch("forge.platform.system", return_value="Darwin"):
            code, _, error = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))
        self.assertEqual(code, 0, error)
        report = self.report()
        self.assertEqual(report["status"], "passed")
        self.assertEqual([c["status"] for c in report["checks"]], ["passed", "passed"])
        log = json.loads(Path(report["checks"][0]["log"]).read_text())
        self.assertIn(self.data["scheme"], log)
        self.assertFalse((self.app / "DO_NOT_CREATE").exists())
        self.assertTrue(report["not_verified"])
        self.assertEqual(stat.S_IMODE(next(self.output.iterdir()).stat().st_mode), 0o700)

    def test_failure_stops_later_checks(self):
        with self.fake_xcode("print('compiler error'); sys.exit(65)"), patch("forge.platform.system", return_value="Darwin"):
            code, _, _ = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))
        self.assertEqual(code, 1)
        report = self.report()
        self.assertEqual(report["checks"][0]["exit_code"], 65)
        self.assertEqual(report["checks"][1]["status"], "not_run")
        self.assertEqual(report["status"], "failed")

    def test_timeout_records_incomplete_checks(self):
        self.data["timeout_seconds"] = 1
        self.save()
        with self.fake_xcode("time.sleep(30)"), patch("forge.platform.system", return_value="Darwin"):
            code, _, _ = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))
        self.assertEqual(code, 1)
        report = self.report()
        self.assertEqual(report["checks"][0]["status"], "timed_out")
        self.assertIn("Timed out after 1 seconds", report["checks"][0]["diagnostic"])
        self.assertEqual(report["checks"][1]["status"], "not_run")

    def test_unsupported_host_does_not_create_evidence(self):
        with patch("forge.platform.system", return_value="Linux"):
            self.assertEqual(self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))[0], 2)
        self.assertFalse(self.output.exists())

    def test_zero_skipped_missing_and_failed_test_results_cannot_pass(self):
        self.data["checks"] = ["test"]
        self.save()
        with self.fake_xcode("sys.exit(0)"), patch("forge.platform.system", return_value="Darwin"):
            for summary in (
                dict(self.summary, totalTestCount=0, passedTests=0),
                dict(self.summary, skippedTests=1, passedTests=0),
                {"error": "Result bundle missing"},
                dict(self.summary, result="Failed", passedTests=0, failedTests=1),
            ):
                with self.subTest(summary=summary), patch("forge.read_test_summary", return_value=summary):
                    self.assertEqual(self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))[0], 1)

    def test_failure_reports_diagnostic(self):
        with self.fake_xcode("print('source.swift:1: error: cannot find type Missing'); sys.exit(65)"), patch("forge.platform.system", return_value="Darwin"):
            code, out, _ = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))
        self.assertEqual(code, 1)
        self.assertIn("cannot find type Missing", out)
        self.assertIn("cannot find type Missing", self.report()["checks"][0]["diagnostic"])

    def test_structured_test_failure_is_reported_when_log_has_no_error_text(self):
        self.data["checks"] = ["test"]
        self.save()
        summary = dict(self.summary, passedTests=0, failedTests=1, result="Failed",
                       testFailures=[{"failureText": "Large image URL did not match its input."}])
        with self.fake_xcode("print('Tests failed'); sys.exit(65)"), patch("forge.platform.system", return_value="Darwin"), patch("forge.read_test_summary", return_value=summary):
            code, out, _ = self.call("verify", "--app", str(self.app), "--output-dir", str(self.output))
        self.assertEqual(code, 1)
        self.assertIn("Large image URL did not match its input.", out)


if __name__ == "__main__":
    unittest.main()
