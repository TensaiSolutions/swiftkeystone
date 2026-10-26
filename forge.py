#!/usr/bin/env python3
"""SwiftKeystone: dependency-free project setup and verification evidence."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

from keystone_common import ForgeError, inventory, write_json, source_fingerprint, private_output

VERSION = "0.4.0"
PUBLISHED_VERSION = "0.3.0"
ROOT = Path(__file__).resolve().parent
SKILLS = ("ios-onboard", "ios-plan-feature", "ios-build-feature", "ios-verify")


def load_profile(path):
    """Validate the same closed structure described by schemas/app-profile.schema.json."""
    data = json.loads(path.read_text())
    required = {"schema_version", "name", "project", "scheme", "destination", "checks", "timeout_seconds"}
    optional = {"deployment_target", "swift_version", "architecture", "specialist_skills", "baseline_expectations"}
    if not isinstance(data, dict) or set(data) - required - optional or required - set(data):
        raise ForgeError("Profile has missing or unknown fields; see docs/profile.md.")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ForgeError("schema_version must be 1.")
    for key in ("name", "project", "scheme", "destination"):
        if not isinstance(data[key], str) or not data[key].strip() or "\x00" in data[key]:
            raise ForgeError(f"{key} must be a nonempty string without NUL characters.")
    project = Path(data["project"])
    if project.is_absolute() or ".." in project.parts or project.suffix not in (".xcodeproj", ".xcworkspace"):
        raise ForgeError("project must be a relative .xcodeproj or .xcworkspace path inside the app.")
    if type(data["timeout_seconds"]) is not int or not 1 <= data["timeout_seconds"] <= 7200:
        raise ForgeError("timeout_seconds must be an integer from 1 to 7200.")
    checks = data["checks"]
    if not isinstance(checks, list) or not checks or any(c not in ("build", "test") for c in checks) or len(set(checks)) != len(checks):
        raise ForgeError("checks must contain build and/or test, without duplicates.")
    for key in ("deployment_target", "swift_version", "architecture"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            raise ForgeError(f"{key} must be a nonempty string.")
    if "specialist_skills" in data and (not isinstance(data["specialist_skills"], list) or any(not isinstance(s, str) or not s.strip() for s in data["specialist_skills"])):
        raise ForgeError("specialist_skills must be an array of nonempty strings.")
    if "baseline_expectations" in data:
        from keystone_expectations import validate_expectations
        validate_expectations(data["baseline_expectations"], checks)
    return data


def app_path(value):
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise ForgeError(f"App directory does not exist: {path}")
    return path


def contained(path, root):
    if not path.resolve().is_relative_to(root):
        raise ForgeError(f"Path escapes the app directory: {path}")
    return path


def init(args):
    app = app_path(args.app)
    target = contained(app / ".ios-forge" / "app.json", app)
    if target.exists():
        raise ForgeError("App profile already exists; edit it in place. Nothing was overwritten.")
    data = {
        "schema_version": 1, "name": args.name, "project": args.project,
        "scheme": args.scheme, "destination": args.destination,
        "checks": ["build", "test"], "timeout_seconds": 900,
    }
    # Validate before creating anything in the user's app.
    with tempfile.TemporaryDirectory() as directory:
        candidate = Path(directory) / "app.json"
        candidate.write_text(json.dumps(data))
        load_profile(candidate)
    contained(app / args.project, app)
    write_json(target, data)
    print(f"Created {target}. Confirm its scheme and destination before verification.")


def validate(args):
    load_profile(Path(args.profile))
    print("Profile is valid (schema version 1).")


def install(args):
    app = app_path(args.app)
    destination = contained(app / ".agents" / "skills", app)
    decisions = []
    # Preflight every skill before writing any of them. Existing skills are never replaced.
    for name in SKILLS:
        source = ROOT / "skills" / name
        if not source.is_dir():
            raise ForgeError(f"Distribution is missing skill {name}.")
        target = contained(destination / name, app)
        expected = inventory(source)
        if target.is_symlink():
            raise ForgeError(f"Refusing a linked destination: {target}")
        if target.exists():
            if not target.is_dir() or inventory(target) != expected:
                raise ForgeError(f"Skill already exists and differs: {target}. No skills installed; review manually.")
            decisions.append((source, target, "unchanged"))
        else:
            decisions.append((source, target, "install"))
    for source, target, action in decisions:
        print(f"{action}: {target}")
    if args.dry_run:
        return
    for source, target, action in decisions:
        if action == "install":
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
    print("Project skills installed. Existing AGENTS.md and global settings were preserved.")


def doctor(args):
    app = app_path(args.app)
    findings = {"system": platform.system(), "python": platform.python_version(), "app": str(app)}
    for binary in ("git", "xcodebuild", "xcrun"):
        findings[binary] = shutil.which(binary)
    profile = app / ".ios-forge" / "app.json"
    findings["profile"] = "missing"
    if profile.exists():
        load_profile(profile)
        findings["profile"] = "valid"
    ready = findings["system"] == "Darwin" and all(findings[b] for b in ("git", "xcodebuild", "xcrun")) and findings["profile"] == "valid"
    findings["prerequisites_found"] = ready
    findings["note"] = "Executable discovery only; verify Xcode selection, scheme and destination with ios-onboard."
    print(json.dumps(findings, indent=2))
    return 0 if ready else 1


def commands(profile, app, output):
    project = contained(app / profile["project"], app)
    kind = "-workspace" if project.suffix == ".xcworkspace" else "-project"
    for check in profile["checks"]:
        command = ["xcodebuild", kind, str(project), "-scheme", profile["scheme"],
                   "-destination", profile["destination"], "-derivedDataPath", str(output / "DerivedData")]
        if check == "test":
            command += ["-resultBundlePath", str(output / "Tests.xcresult")]
        yield check, command + [check]


def toolchain_info():
    try:
        result = subprocess.run(["xcodebuild", "-version"], capture_output=True, text=True, timeout=15)
        return {"xcode": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr.strip()[:1000] if result.returncode else None}
    except (OSError, subprocess.SubprocessError) as error:
        return {"xcode": None, "error": str(error)}


def read_test_summary(bundle):
    if not bundle.is_dir():
        return {"error": "Xcode did not produce the configured test result bundle."}
    try:
        result = subprocess.run(["xcrun", "xcresulttool", "get", "test-results", "summary", "--path", str(bundle), "--compact"],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            return {"error": "Could not read Xcode test summary: " + (result.stderr or result.stdout).strip()[:1500]}
        data = json.loads(result.stdout)
        keys = ("totalTestCount", "passedTests", "failedTests", "skippedTests", "expectedFailures")
        if not isinstance(data, dict) or any(type(data.get(key)) is not int or data[key] < 0 for key in keys):
            return {"error": "Xcode test summary has missing or invalid test counts."}
        return {key: data[key] for key in (*keys, "result", "devicesAndConfigurations", "testFailures") if key in data}
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {"error": f"Could not read Xcode test summary: {error}"}


def read_test_targets(bundle):
    from keystone_expectations import target_counts
    try:
        result = subprocess.run(["xcrun", "xcresulttool", "get", "test-results", "tests", "--path", str(bundle), "--compact"],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            return {"error": "Could not read Xcode test targets."}
        return {"executed_by_target": target_counts(json.loads(result.stdout))}
    except (OSError, ValueError, RecursionError, subprocess.SubprocessError):
        return {"error": "Could not interpret Xcode test target evidence."}


def failure_diagnostic(log):
    try:
        with log.open("rb") as handle:
            handle.seek(max(0, log.stat().st_size - 131072))
            lines = handle.read().decode("utf-8", errors="replace").splitlines()
        matches = [line.strip() for line in lines if re.search(r"error:|Expectation failed|Testing failed:", line)]
        if matches:
            return matches[0][:2000]
        for index, line in enumerate(lines):
            if line.strip() == "The following build commands failed:":
                step = next((item.strip() for item in lines[index + 1:] if item.strip()), None)
                if step:
                    return ("Xcode build step failed: " + step)[:2000]
        return "Check failed; inspect its private log for details."
    except OSError as error:
        return f"Could not read check log: {error}"


def verify(args):
    app = app_path(args.app)
    profile_path = contained(app / ".ios-forge" / "app.json", app)
    profile = load_profile(profile_path)
    output_base = Path(args.output_dir).expanduser().resolve()
    # Evidence and build outputs belong outside the source checkout.
    if output_base.is_relative_to(app):
        raise ForgeError("Use an output directory outside the app checkout for private evidence.")
    planned = list(commands(profile, app, output_base / "RUN_ID"))
    if args.dry_run:
        print(json.dumps({"dry_run": True, "checks": [{"name": name, "argv": argv} for name, argv in planned]}, indent=2))
        return 0
    if platform.system() != "Darwin" or not shutil.which("xcodebuild"):
        raise ForgeError("Verification needs macOS and full Xcode. Use --dry-run to inspect commands.")
    if not (app / profile["project"]).exists():
        raise ForgeError("Configured Xcode project/workspace does not exist.")
    output_base.mkdir(parents=True, exist_ok=True, mode=0o700)
    run = Path(tempfile.mkdtemp(prefix=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ-"), dir=output_base))
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=app, capture_output=True, text=True, timeout=15)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=app, capture_output=True, text=True, timeout=15)
    report = {"forge_version": VERSION, "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "app": profile["name"], "commit": git.stdout.strip() if git.returncode == 0 else None,
              "dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
              "source_fingerprint": source_fingerprint(app), "toolchain": toolchain_info(),
              "profile_sha256": hashlib.sha256(profile_path.read_bytes()).hexdigest(),
              "configuration": {key: profile[key] for key in ("project", "scheme", "destination", "checks")},
              "status": "running", "checks": [],
              "verification_scope": "Configured commands and Xcode test summary; inspect test cases for behaviour coverage.",
              "not_verified": ["User journeys beyond configured tests", "Other devices, hardware, and OS versions",
                               "Accessibility beyond configured automated checks", "Release readiness"]}
    if "test" not in profile["checks"]:
        report["not_verified"].append("Automated tests (not configured)")
    if "baseline_expectations" in profile:
        report["baseline_expectations"] = profile["baseline_expectations"]
    evidence = run / "report.json"
    write_json(evidence, report)
    for name, argv in commands(profile, app, run):
        entry = {"name": name, "argv": argv, "log": str(run / f"{name}.log")}
        report["checks"].append(entry)
        try:
            with open(entry["log"], "w") as log:
                # A process group lets timeout cleanup reach xcodebuild's child processes too.
                process = subprocess.Popen(argv, cwd=app, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=profile["timeout_seconds"])
                except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
                    import signal
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
                    entry["status"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "timed_out"
                    entry["failure_reason"] = ("Interrupted; terminated the check's process group."
                                               if isinstance(error, KeyboardInterrupt) else
                                               f"Timed out after {profile['timeout_seconds']} seconds; terminated the check's process group.")
                    code = None
            entry["exit_code"] = code
            entry.setdefault("status", "passed" if code == 0 else "failed")
        except OSError as error:
            entry.update(status="failed", error=str(error), exit_code=None)
        if name == "test" and entry.get("exit_code") is not None:
            summary = read_test_summary(run / "Tests.xcresult")
            entry["test_summary"] = summary
            if entry["status"] == "passed":
                reason = summary.get("error")
                if not reason and (summary["totalTestCount"] == 0 or summary["totalTestCount"] <= summary["skippedTests"]):
                    reason = "No tests executed; a successful command with only skipped or zero tests is not verification."
                if not reason and (summary["failedTests"] or summary.get("result") != "Passed"):
                    reason = "The Xcode result bundle does not report passing tests."
                if reason:
                    entry.update(status="failed", failure_reason=reason)
        if name == "test" and "baseline_expectations" in profile and entry.get("exit_code") is not None:
            from keystone_expectations import assess
            targets = read_test_targets(run / "Tests.xcresult") if profile["baseline_expectations"].get("required_test_targets") else {}
            if targets:
                entry["test_targets"] = targets
            assessment = assess(profile["baseline_expectations"], entry.get("test_summary", {}), targets.get("executed_by_target"))
            entry["baseline_assessment"] = assessment
            if assessment["status"] != "passed" and entry["status"] == "passed":
                entry.update(status="failed", failure_reason="Baseline expectations were not met: " + ", ".join(assessment["findings"]))
        if entry["status"] != "passed":
            failures = entry.get("test_summary", {}).get("testFailures", [])
            if not isinstance(failures, list):
                failures = []
            test_failure = next((failure.get("failureText") for failure in failures
                                 if isinstance(failure, dict) and isinstance(failure.get("failureText"), str)
                                 and failure["failureText"].strip()), None)
            entry["diagnostic"] = entry.get("failure_reason") or entry.get("error") or (test_failure[:2000] if test_failure else None) or failure_diagnostic(Path(entry["log"]))
            print(f"{name}: {entry['status']}: {entry['diagnostic']}")
        write_json(evidence, report)
        if entry["status"] != "passed":
            break
    executed = {entry["name"] for entry in report["checks"]}
    for name in profile["checks"]:
        if name not in executed:
            report["checks"].append({"name": name, "status": "not_run"})
    report["status"] = "passed" if all(c["status"] == "passed" for c in report["checks"]) else "failed"
    report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(evidence, report)
    print(f"{report['status']}: {evidence}")
    if "test" not in profile["checks"]:
        print("Scope: build only; automated tests were not configured or run.")
    for entry in report["checks"]:
        summary = entry.get("test_summary", {})
        if "totalTestCount" in summary:
            print(f"Tests: {summary['passedTests']} passed, {summary['failedTests']} failed, {summary['skippedTests']} skipped ({summary['totalTestCount']} total).")
    return 0 if report["status"] == "passed" else 1


def audit_command(args):
    from keystone_audit import audit
    app = app_path(args.app)
    profile = load_profile(contained(app / ".ios-forge" / "app.json", app))
    result = audit(app, profile, args.reference_report)
    result["forge_version"] = VERSION
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        private_output(args.output, text, (app, ROOT))
    print(text, end="")
    return 1 if result["status"] == "findings" else 0


def update_command(args):
    from keystone_updates import stage_update
    app = app_path(args.app)
    result = stage_update(app, Path(args.from_release).expanduser(), ROOT, SKILLS,
                          args.output_dir, args.dry_run)
    result["forge_version"] = VERSION
    print(json.dumps(result, indent=2))
    return 1 if result["conflicts"] or not result.get("candidate_entrypoints_present", True) else 0


def compare_command(args):
    from keystone_evidence import compare
    result = compare(args.before, args.after, args.restored)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        private_output(args.output, text, (ROOT,))
    print(text, end="")
    return 1 if result["status"] == "needs_review" else 0


def summary_command(args):
    from keystone_evidence import summarize
    text, comparison = summarize(args.report, args.baseline, args.regression)
    if args.output:
        private_output(args.output, text, (ROOT,))
    print(text, end="")
    return 1 if comparison and (comparison["status"] == "needs_review" or
                               (args.regression and not comparison["regression_cycle_supported"])) else 0


def main(argv=None):
    if sys.version_info < (3, 10):
        print("swiftkeystone: Python 3.10+ is required. Select a supported interpreter; "
              "macOS /usr/bin/python3 may be older. Nothing was changed.", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("init", help="Create an app profile without overwriting existing files")
    setup.add_argument("--app", required=True)
    for key in ("name", "project", "scheme", "destination"):
        setup.add_argument(f"--{key}", required=True)
    setup.set_defaults(func=init)
    check = sub.add_parser("validate", help="Validate an app profile")
    check.add_argument("profile")
    check.set_defaults(func=validate)
    for name, function in (("install", install), ("doctor", doctor), ("verify", verify)):
        command = sub.add_parser(name)
        command.add_argument("--app", required=True)
        command.set_defaults(func=function)
        if name in ("install", "verify"):
            command.add_argument("--dry-run", action="store_true")
        if name == "verify":
            command.add_argument("--output-dir", required=True)
    command = sub.add_parser("audit", help="Inspect static test wiring and local evidence; no builds or fetches")
    command.add_argument("--app", required=True)
    command.add_argument("--reference-report")
    command.add_argument("--output")
    command.set_defaults(func=audit_command)
    command = sub.add_parser("update", help="Stage a three-way skill update and backup; never replace installed skills")
    command.add_argument("--app", required=True)
    command.add_argument("--from-release", required=True)
    command.add_argument("--output-dir", required=True)
    command.add_argument("--dry-run", action="store_true")
    command.set_defaults(func=update_command)
    command = sub.add_parser("compare", help="Compare completed verification reports")
    command.add_argument("before")
    command.add_argument("after")
    command.add_argument("--restored")
    command.add_argument("--output")
    command.set_defaults(func=compare_command)
    command = sub.add_parser("summary", help="Draft a bounded PR verification summary without private diagnostics")
    command.add_argument("report")
    command.add_argument("--baseline")
    command.add_argument("--regression")
    command.add_argument("--output")
    command.set_defaults(func=summary_command)
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except (ForgeError, OSError, ValueError, RecursionError, subprocess.SubprocessError) as error:
        print(f"swiftkeystone: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
