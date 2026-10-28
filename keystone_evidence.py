"""Validate, compare, and summarize local verification reports without executing their contents."""
import hashlib
import json
from pathlib import Path
import re

from keystone_common import ForgeError

HASH = re.compile(r"[0-9a-f]{64}\Z")
STATUSES = {"passed", "failed", "not_run", "timed_out", "interrupted"}


def hash_value(value):
    return value if isinstance(value, str) and HASH.fullmatch(value) else None


def read_report(path):
    raw = Path(path).read_bytes()
    if len(raw) > 8 * 1024 * 1024:
        raise ForgeError("Report exceeds the 8 MiB comparison limit.")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ForgeError("Report contains duplicate JSON keys.")
            result[key] = value
        return result
    data = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(data, dict) or data.get("status") not in ("passed", "failed"):
        raise ForgeError("Comparison requires a completed verification report.")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ForgeError("Report has no configured checks.")
    found = set()
    for check in checks:
        if not isinstance(check, dict) or check.get("name") not in ("build", "test") or check["name"] in found:
            raise ForgeError("Report contains invalid or duplicate checks.")
        found.add(check["name"])
        if check.get("status") not in STATUSES:
            raise ForgeError("Report contains an incomplete or unknown check status.")
        if check["status"] == "passed" and (type(check.get("exit_code")) is not int or check["exit_code"] != 0):
            raise ForgeError("A passing check must record exit code zero.")
        summary = check.get("test_summary")
        if check["name"] == "test":
            if isinstance(summary, dict) and "error" not in summary:
                keys = ("totalTestCount", "passedTests", "failedTests", "skippedTests", "expectedFailures")
                if any(type(summary.get(k)) is not int or summary[k] < 0 for k in keys):
                    raise ForgeError("Report contains invalid test counts.")
                if summary["expectedFailures"] > summary["totalTestCount"] or summary["passedTests"] + summary["failedTests"] + summary["skippedTests"] != summary["totalTestCount"]:
                    raise ForgeError("Test counts do not sum to the total.")
            if check["status"] == "passed" and (not isinstance(summary, dict) or "error" in summary or
                    summary.get("result") != "Passed" or not summary.get("passedTests") or summary.get("failedTests")):
                raise ForgeError("Passing tests require readable evidence of executed passing cases.")
    if (data["status"] == "passed") != all(c["status"] == "passed" for c in checks):
        raise ForgeError("Report outcome contradicts its checks.")
    if "baseline_expectations" in data:
        from keystone_expectations import validate_expectations, assess
        validate_expectations(data["baseline_expectations"], list(found))
        for check in checks:
            if check["name"] != "test" or check["status"] == "not_run":
                continue
            targets = check.get("test_targets", {}).get("executed_by_target") if isinstance(check.get("test_targets", {}), dict) else None
            if targets is not None and (not isinstance(targets, dict) or any(not isinstance(k, str) or not k.strip() or type(v) is not int or v < 0 for k, v in targets.items())):
                raise ForgeError("Invalid recorded test-target counts.")
            assessment = assess(data["baseline_expectations"], check.get("test_summary", {}), targets)
            if check["status"] == "passed" and (assessment["status"] != "passed" or check.get("baseline_assessment") != assessment):
                raise ForgeError("Passing evidence contradicts its baseline expectations.")
    return data, hashlib.sha256(raw).hexdigest()


def context(report):
    """Read v0.3 snapshots or conservatively infer older context from argv; never run argv."""
    values = report.get("configuration")
    contexts = []
    for check in report["checks"]:
        argv = check.get("argv")
        if check["status"] == "not_run":
            continue
        if not isinstance(argv, list) or not all(isinstance(v, str) for v in argv):
            return None
        value = {}
        for key, flags in (("project", ("-project", "-workspace")), ("scheme", ("-scheme",)),
                           ("destination", ("-destination",))):
            pairs = [argv[i + 1] for i, flag in enumerate(argv[:-1]) if flag in flags]
            if len(pairs) != 1:
                return None
            value[key] = Path(pairs[0]).name if key == "project" else pairs[0]
        contexts.append(value)
    inferred = contexts[0] if contexts and all(c == contexts[0] for c in contexts) else None
    if values is None:
        return inferred
    if not isinstance(values, dict) or not all(isinstance(values.get(k), str) and values[k] for k in ("project", "scheme", "destination")):
        return None
    if values.get("checks") != [c["name"] for c in report["checks"]]:
        return None
    explicit = {k: values[k] for k in ("project", "scheme", "destination")}
    normalized = dict(explicit, project=Path(explicit["project"]).name)
    return explicit if inferred == normalized else None


def source(report):
    value = report.get("source_fingerprint")
    return hash_value(value.get("sha256")) if isinstance(value, dict) else None


def tests(report):
    for check in report["checks"]:
        if check["name"] == "test":
            summary = check.get("test_summary")
            if isinstance(summary, dict) and "error" not in summary:
                return {k: summary[k] for k in ("totalTestCount", "passedTests", "failedTests", "skippedTests")}
    return None


def comparable(left, right):
    a, b = context(left), context(right)
    # Legacy reports have only a project basename. This does not establish an exact project path.
    legacy = not isinstance(left.get("configuration"), dict) or not isinstance(right.get("configuration"), dict)
    if a and b and legacy:
        a, b = dict(a, project=Path(a["project"]).name), dict(b, project=Path(b["project"]).name)
    tool_a, tool_b = left.get("toolchain"), right.get("toolchain")
    xcode_a = tool_a.get("xcode") if isinstance(tool_a, dict) else None
    xcode_b = tool_b.get("xcode") if isinstance(tool_b, dict) else None
    return bool(left.get("baseline_expectations", {}) == right.get("baseline_expectations", {}) and a and b and a == b and isinstance(xcode_a, str) and xcode_a and xcode_a == xcode_b), legacy


def compare(before_path, after_path, restored_path=None):
    before, before_hash = read_report(before_path)
    after, after_hash = read_report(after_path)
    compatible, legacy = comparable(before, after)
    a, b = source(before), source(after)
    profiles = [hash_value(r.get("profile_sha256")) for r in (before, after)]
    result = {"schema_version": 1, "transition": before["status"] + "_to_" + after["status"],
              "comparable_configuration": compatible, "legacy_context_inferred": legacy,
              "source_changed": a != b if a and b else None,
              "profile_changed": profiles[0] != profiles[1] if all(profiles) else None,
              "check_selection_changed": [c["name"] for c in before["checks"]] != [c["name"] for c in after["checks"]],
              "before_tests": tests(before), "after_tests": tests(after),
              "input_report_sha256": {"before": before_hash, "after": after_hash},
              "restoration_verified": None, "regression_cycle_supported": None,
              "note": "Report comparison is not independent execution or a causal proof. Counts and hashes do not establish user-journey coverage."}
    left_counts, right_counts = tests(before), tests(after)
    result["baseline_expectations_changed"] = before.get("baseline_expectations", {}) != after.get("baseline_expectations", {})
    result["test_count_delta"] = None
    result["executed_test_count_decreased"] = None
    if left_counts is not None and right_counts is not None:
        result["test_count_delta"] = {key: right_counts[key] - left_counts[key] for key in left_counts}
        result["test_count_delta"]["executedTests"] = (right_counts["passedTests"] + right_counts["failedTests"] - left_counts["passedTests"] - left_counts["failedTests"])
        result["executed_test_count_decreased"] = result["test_count_delta"]["executedTests"] < 0
    if restored_path:
        restored, restored_hash = read_report(restored_path)
        restored_compatible, restored_legacy = comparable(before, restored)
        profile = hash_value(restored.get("profile_sha256"))
        result["input_report_sha256"]["restored"] = restored_hash
        result["restored_tests"] = tests(restored)
        result["restoration_verified"] = bool(a and source(restored) == a and profiles[0] and profile == profiles[0]
            and restored_compatible and before["status"] == restored["status"] == "passed"
            and [c["name"] for c in before["checks"]] == [c["name"] for c in restored["checks"]])
        result["regression_cycle_supported"] = bool(compatible and a and b and a != b and tests(before)
            and tests(before)["passedTests"] and tests(after) and tests(after)["failedTests"]
            and before["status"] == "passed" and after["status"] == "failed"
            and result["restoration_verified"] and tests(restored) and tests(restored)["passedTests"])
        result["legacy_context_inferred"] |= restored_legacy
    result["status"] = "comparable" if compatible and a and b and all(profiles) else "needs_review"
    if result["executed_test_count_decreased"]:
        result["status"] = "needs_review"
    if restored_path and not result["restoration_verified"]:
        result["status"] = "needs_review"
    return result


def summarize(report_path, baseline=None, regression=None):
    report, _ = read_report(report_path)
    if regression and not baseline:
        raise ForgeError("A regression summary needs both --baseline and --regression reports.")
    lines = ["## Verification summary", "", "Configured checks: **" + report["status"] + "**.", ""]
    for check in report["checks"]:
        lines.append("- " + check["name"] + ": " + check["status"] + ".")
    count = tests(report)
    if count:
        lines += ["", f"Tests: {count['passedTests']} passed, {count['failedTests']} failed, {count['skippedTests']} skipped ({count['totalTestCount']} total)."]
    else:
        lines += ["", "No readable automated-test counts are available in this report."]
    if "test" not in {c["name"] for c in report["checks"]}:
        lines += ["", "Build-only evidence: automated tests were not configured."]
    if "baseline_expectations" in report:
        from keystone_expectations import assess
        check = next(c for c in report["checks"] if c["name"] == "test")
        target_evidence = check.get("test_targets", {})
        assessment = assess(report["baseline_expectations"], check.get("test_summary", {}), target_evidence.get("executed_by_target") if isinstance(target_evidence, dict) else None)
        lines += ["", "Baseline expectations: " + (assessment["status"] if check["status"] != "not_run" else "not evaluated") + "."]
        if assessment["minimum_executed_tests"] is not None:
            lines.append(f"Minimum executed tests: {assessment['minimum_executed_tests']}.")
        lines.append(f"Required target count: {len(report['baseline_expectations'].get('required_test_targets', []))}; missing execution evidence: {len(assessment['missing_test_targets'])}.")
    version = report.get("forge_version")
    if isinstance(version, str) and re.fullmatch(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", version):
        lines += ["", "Recorded SwiftKeystone version: `" + version + "`."]
    commit = report.get("commit")
    if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40,64}", commit):
        lines += ["", "Source commit: `" + commit + "`."]
    lines += ["", "Source state: " + ("dirty" if report.get("dirty") is True else "clean" if report.get("dirty") is False else "unknown") + "."]
    comparison = compare(baseline, regression, report_path) if regression else compare(baseline, report_path) if baseline else None
    if comparison:
        lines += ["", "Evidence comparison: " + comparison["status"] + "."]
        if not comparison["comparable_configuration"]:
            lines.append("Run context or baseline expectations differ or are unavailable; count changes need contextual review.")
        delta = comparison["test_count_delta"]
        if delta is not None:
            lines.append(f"Test-count changes: executed {delta['executedTests']:+d}, total {delta['totalTestCount']:+d}, passed {delta['passedTests']:+d}, failed {delta['failedTests']:+d}, skipped {delta['skippedTests']:+d}.")
            if comparison["executed_test_count_decreased"]:
                lines.append("Executed test count decreased; review coverage before accepting this baseline.")
        else:
            lines.append("Test-count change is unavailable because readable counts are missing.")
        if comparison["baseline_expectations_changed"]:
            lines.append("Baseline expectations changed; the runs require review.")
        if comparison["check_selection_changed"]:
            lines.append("Configured check selection changed between the compared runs.")
        if regression:
            lines.append("Detected-failure/restoration cycle: " + ("supported by reports" if comparison["regression_cycle_supported"] else "not established") + ".")
        if comparison["legacy_context_inferred"]:
            lines.append("Older report context was inferred from command arguments; exact project-path equivalence is unverified.")
    lines += ["", "Scope: configured commands and result summaries only. User journeys require inspection of the actual tests; other hardware/OS versions, manual accessibility, live services, signing, and release readiness are not established.",
              "", "Private paths, command arguments, diagnostics, app names, device identifiers, and failure text are omitted. Review this text alongside actual acceptance criteria before posting; this command does not publish it."]
    return "\n".join(lines) + "\n", comparison
