#!/usr/bin/env python3
"""iOS Forge: dependency-free project setup and verification evidence."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
SKILLS = ("ios-onboard", "ios-plan-feature", "ios-build-feature", "ios-verify")


class ForgeError(Exception):
    pass


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def load_profile(path):
    """Validate the same closed structure described by schemas/app-profile.schema.json."""
    data = json.loads(path.read_text())
    required = {"schema_version", "name", "project", "scheme", "destination", "checks", "timeout_seconds"}
    optional = {"deployment_target", "swift_version", "architecture", "specialist_skills"}
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


def inventory(directory):
    """Fingerprint regular files; reject links rather than follow them into another tree."""
    found = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ForgeError(f"Skill contains a symbolic link: {path}")
        if path.is_file():
            found[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


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
    findings["note"] = "Executable discovery only; verify Xcode selection, scheme and simulator with ios-onboard."
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
              "profile_sha256": hashlib.sha256(profile_path.read_bytes()).hexdigest(),
              "status": "running", "checks": [],
              "not_verified": ["Simulator user journeys", "Physical device behavior", "Accessibility", "Release readiness"]}
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
                    code = None
            entry["exit_code"] = code
            entry.setdefault("status", "passed" if code == 0 else "failed")
        except OSError as error:
            entry.update(status="failed", error=str(error), exit_code=None)
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
    return 0 if report["status"] == "passed" else 1


def main(argv=None):
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
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except (ForgeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"ios-forge: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
