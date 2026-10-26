import json
from pathlib import Path
import tempfile
import unittest

import forge
from keystone_expectations import assess, target_counts
from keystone_evidence import read_report, summarize, compare
from keystone_common import ForgeError
from keystone_expectations import validate_expectations


class ExpectationTests(unittest.TestCase):
    def test_invalid_contracts_fail_closed(self):
        for value in ({}, {"unknown": 1}, {"minimum_executed_tests": True},
                      {"minimum_executed_tests": 0}, {"required_test_targets": []},
                      {"required_test_targets": ["Tests", "Tests"]},
                      {"required_test_targets": ["\x00"]}, {"required_test_targets": [False]}):
            with self.subTest(value=value), self.assertRaises(ForgeError):
                validate_expectations(value, ["test"])
        with self.assertRaises(ForgeError):
            validate_expectations({"minimum_executed_tests": 1}, ["build"])

    def test_skipped_cases_do_not_meet_execution_contract(self):
        e = {"minimum_executed_tests": 4, "required_test_targets": ["Unit", "UI"]}
        summary = {"passedTests": 3, "failedTests": 0, "skippedTests": 20}
        a = assess(e, summary, {"Unit": 3, "UI": 0})
        self.assertEqual(a["executed_tests"], 3)
        self.assertEqual(a["status"], "failed")
        self.assertEqual(a["missing_test_targets"], ["UI"])
        self.assertEqual(len(a["findings"]), 2)
        self.assertEqual(assess(e, {"passedTests": 4, "failedTests": 0}, {"Unit": 3, "UI": 1})["status"], "passed")
        self.assertIn("target_counts_do_not_match_summary", assess(e, {"passedTests": 4, "failedTests": 0}, {"Unit": 4, "UI": 1})["findings"])

    def test_tree_counts_cases_not_suites_or_parameter_iterations(self):
        tree = {"testNodes": [{"nodeType": "Test Plan", "children": [
            {"nodeType": "UI test bundle", "name": "UI", "children": [
                {"nodeType": "Test Case", "result": "Passed", "children": [
                    {"nodeType": "Test Case Run", "result": "Passed"}]},
                {"nodeType": "Test Case", "result": "Skipped"}]}]}]}
        self.assertEqual(target_counts(tree), {"UI": 1})
        tree["testNodes"][0]["children"][0]["children"][0]["result"] = "Unknown"
        with self.assertRaises(ValueError):
            target_counts(tree)
        with self.assertRaises(ValueError):
            target_counts({})

    def test_forged_success_is_rejected_and_summary_hides_target_names(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "report.json"
            summary = {"totalTestCount": 3, "passedTests": 3, "failedTests": 0,
                       "skippedTests": 0, "expectedFailures": 0, "result": "Passed"}
            e = {"minimum_executed_tests": 4, "required_test_targets": ["PRIVATE-TARGET"]}
            report = {"status": "passed", "baseline_expectations": e, "checks": [
                {"name": "test", "status": "passed", "exit_code": 0, "test_summary": summary}]}
            p.write_text(json.dumps(report))
            with self.assertRaises(ForgeError):
                read_report(p)
            report["status"] = "failed";report["checks"][0]["status"] = "failed"
            p.write_text(json.dumps(report))
            text, _ = summarize(p)
            self.assertIn("Baseline expectations: failed", text)
            self.assertNotIn("PRIVATE-TARGET", text)

    def test_count_drop_needs_review_and_increase_is_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def save(name, n):
                r = {"status": "passed", "profile_sha256": "a" * 64,
                     "source_fingerprint": {"sha256": "b" * 64}, "toolchain": {"xcode": "Xcode Fixture"},
                     "checks": [{"name": "test", "status": "passed", "exit_code": 0,
                     "argv": ["xcodebuild", "-project", "App.xcodeproj", "-scheme", "App", "-destination", "platform=macOS", "test"],
                     "test_summary": {"totalTestCount": n, "passedTests": n, "failedTests": 0, "skippedTests": 0, "expectedFailures": 0, "result": "Passed"}}]}
                p = root / name;p.write_text(json.dumps(r));return p
            a, b = save("before.json", 4), save("after.json", 3)
            self.assertEqual(compare(a, b)["status"], "needs_review")
            self.assertEqual(compare(a, b)["test_count_delta"]["executedTests"], -1)
            text, _ = summarize(a, b)
            self.assertIn("executed +1", text)
            self.assertEqual(compare(b, a)["status"], "comparable")
            r = json.loads(a.read_text())
            r["checks"][0]["test_summary"].update(passedTests=3, skippedTests=1)
            c = root / "skipped.json";c.write_text(json.dumps(r))
            change = compare(a, c)
            self.assertEqual(change["status"], "needs_review")
            self.assertEqual(change["test_count_delta"]["totalTestCount"], 0)
            self.assertEqual(change["test_count_delta"]["executedTests"], -1)
            self.assertEqual(change["test_count_delta"]["skippedTests"], 1)
            r["checks"][0]["argv"][4] = "PRIVATE-SCHEME"
            c.write_text(json.dumps(r))
            text, _ = summarize(c, a)
            self.assertIn("Run context or baseline expectations differ", text)
            self.assertNotIn("PRIVATE-SCHEME", text)

    def test_contract_change_requires_review_even_when_both_runs_meet_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for minimum in (1, 2):
                e = {"minimum_executed_tests": minimum}
                summary = {"totalTestCount": 3, "passedTests": 3, "failedTests": 0, "skippedTests": 0, "expectedFailures": 0, "result": "Passed"}
                report = {"status": "passed", "baseline_expectations": e, "profile_sha256": "a" * 64,
                          "source_fingerprint": {"sha256": "b" * 64}, "toolchain": {"xcode": "Xcode Fixture"},
                          "checks": [{"name": "test", "status": "passed", "exit_code": 0,
                          "argv": ["xcodebuild", "-project", "App.xcodeproj", "-scheme", "App", "-destination", "platform=macOS", "test"],
                          "test_summary": summary, "baseline_assessment": assess(e, summary)}]}
                p = root / str(minimum);p.write_text(json.dumps(report));paths.append(p)
            self.assertTrue(compare(*paths)["baseline_expectations_changed"])
            self.assertEqual(compare(*paths)["status"], "needs_review")
