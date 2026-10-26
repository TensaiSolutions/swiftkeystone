"""Portable static audit of Xcode test wiring and local evidence provenance.

It never invokes Xcode, resolves packages, fetches Git remotes, or edits a project.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from keystone_common import ForgeError, source_fingerprint
from keystone_evidence import read_report, source


TOKEN = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|[{}()=;,]|[^\s{}()=;,"]+', re.S)


def openstep(text):
    """Parse the dictionary/array subset used by .pbxproj; fail closed on unsupported syntax."""
    tokens = []
    position = 0
    for match in TOKEN.finditer(text):
        if text[position:match.start()].strip():
            raise ValueError("Unsupported project token")
        position = match.end()
        token = match.group()
        if token.startswith(("/*", "//")):
            continue
        tokens.append(token)
    if text[position:].strip():
        raise ValueError("Unsupported project token")
    index = 0

    def parse(depth=0):
        nonlocal index
        if depth > 128 or index >= len(tokens):
            raise ValueError("Truncated or deeply nested project syntax")
        token = tokens[index]
        index += 1
        if token == "{":
            result = {}
            while index < len(tokens) and tokens[index] != "}":
                key = tokens[index]
                key = json.loads(key) if key.startswith('"') else key
                index += 1
                if key in result or index >= len(tokens) or tokens[index] != "=":
                    raise ValueError("Invalid or duplicate project key")
                index += 1
                result[key] = parse(depth + 1)
                if index >= len(tokens) or tokens[index] != ";":
                    raise ValueError("Missing project field separator")
                index += 1
            if index >= len(tokens):
                raise ValueError("Unclosed project dictionary")
            index += 1
            return result
        if token == "(":
            result = []
            while index < len(tokens) and tokens[index] != ")":
                result.append(parse(depth + 1))
                if index < len(tokens) and tokens[index] == ",":
                    index += 1
                elif index >= len(tokens) or tokens[index] != ")":
                    raise ValueError("Missing project array separator")
            if index >= len(tokens):
                raise ValueError("Unclosed project array")
            index += 1
            return result
        if token in ("}", ")", "=", ";", ","):
            raise ValueError("Unexpected project delimiter")
        return json.loads(token) if token.startswith('"') else token

    result = parse()
    if index != len(tokens) or not isinstance(result, dict):
        raise ValueError("Invalid project root")
    return result


def git(app, *arguments):
    try:
        result = subprocess.run(["git", *arguments], cwd=app, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def audit(app, profile, reference=None):
    app = Path(app).resolve()
    findings = []
    def finding(code, detail, severity="error"):
        findings.append({"code": code, "severity": severity, "detail": detail})
    def inside(path):
        path = Path(path)
        if path.is_symlink() or not path.resolve().is_relative_to(app):
            raise ValueError("External or linked project references are not followed")
        return path
    def relative(path):
        return str(Path(path).relative_to(app))
    configured = inside(app / profile["project"])
    projects = []
    if configured.suffix == ".xcodeproj":
        projects = [configured]
    elif configured.suffix == ".xcworkspace":
        try:
            xml = ET.parse(inside(configured / "contents.xcworkspacedata")).getroot()
            def visit(element, base):
                for child in element:
                    location = child.get("location", "")
                    if not location:
                        visit(child, base)
                        continue
                    kind, _, name = location.partition(":")
                    if kind not in ("group", "container"):
                        finding("unsupported_workspace_reference", "Inspect nonlocal workspace references manually.")
                        continue
                    path = inside((base if kind == "group" else configured.parent) / name)
                    if child.tag == "Group":
                        visit(child, path)
                    elif child.tag == "FileRef" and path.suffix == ".xcodeproj":
                        projects.append(path)
                    else:
                        finding("unsupported_workspace_reference", "Inspect nested or unsupported workspace references manually.", "warning")
            visit(xml, configured.parent)
        except (OSError, ValueError, ET.ParseError):
            finding("unreadable_workspace", "Could not fully inspect the configured workspace.")
    targets = {}
    for project in sorted(set(projects)):
        try:
            path = inside(project / "project.pbxproj")
            if path.stat().st_size > 8 * 1024 * 1024:
                raise ValueError("Project too large")
            data = openstep(path.read_text())
            objects = data["objects"]
            root = objects[data["rootObject"]]
            if not isinstance(root, dict):
                raise ValueError("Invalid project target owner")
            if not isinstance(root.get("targets"), list):
                raise ValueError("Missing target list")
            for identifier in root["targets"]:
                target = objects.get(identifier)
                if not isinstance(target, dict):
                    finding("missing_project_target", "The project lists a target with no object definition.")
                    continue
                if target.get("isa") == "PBXNativeTarget":
                    targets[(project.resolve(), identifier)] = {"project": relative(project), "id": identifier,
                        "name": target.get("name"), "product_type": target.get("productType")}
        except (OSError, ValueError, KeyError, TypeError):
            finding("unreadable_project", "Could not fully parse native targets in " + relative(project) + ".")
    # Shared schemes can live in the workspace or one of its selected projects.
    shared, local = [], []
    for container in set([configured, *projects]):
        shared.extend(p for p in (container / "xcshareddata" / "xcschemes").glob("*.xcscheme") if p.stem == profile["scheme"])
        local.extend(p for p in (container / "xcuserdata").glob("*/xcschemes/*.xcscheme") if p.stem == profile["scheme"])
    schemes = shared or local
    scheme_info = {"name": profile["scheme"], "shared": bool(shared), "path": None}
    references, effective = [], []
    if len(schemes) != 1:
        finding("scheme_missing_or_ambiguous", "Select one available scheme; static discovery found zero or multiple matching schemes.")
    else:
        scheme = schemes[0]
        scheme_info["path"] = relative(scheme)
        if not shared:
            finding("scheme_not_shared", "The selected scheme is local to a user checkout.", "warning")
        owner = max((c for c in [configured, *projects] if scheme.is_relative_to(c)), key=lambda c: len(c.parts))
        def resolve_reference(container):
            if not isinstance(container, str) or not container.startswith("container:"):
                raise ValueError("Unsupported test reference")
            return inside(owner.parent / container[len("container:"):])
        def inspect(identifier, name, container, enabled, origin):
            project = resolve_reference(container)
            entry = {"id": identifier, "name": name, "enabled": enabled, "origin": origin,
                     "project": relative(project)}
            target = targets.get((project.resolve(), identifier))
            entry["exists"] = target is not None
            entry["resolved_name"] = target.get("name") if target else None
            if not target:
                finding("orphaned_test_reference", "A " + origin + " test reference does not resolve to a native target.")
            elif target["product_type"] not in ("com.apple.product-type.bundle.unit-test", "com.apple.product-type.bundle.ui-testing"):
                finding("not_a_test_target", "A test reference resolves to a non-test native target.")
            if not enabled:
                finding("disabled_test_reference", "A " + origin + " test reference is disabled.", "warning")
            references.append(entry)
            return entry
        try:
            xml = ET.parse(inside(scheme)).getroot()
            for item in xml.findall("./TestAction/Testables/TestableReference"):
                ref = item.find("BuildableReference")
                if ref is None:
                    raise ValueError("Missing buildable test reference")
                entry = inspect(ref.get("BlueprintIdentifier"), ref.get("BlueprintName"), ref.get("ReferencedContainer"),
                                item.get("skipped", "NO") != "YES", "scheme")
                effective.append(entry)
            plans = xml.findall("./TestAction/TestPlans/TestPlanReference")
            if plans:
                defaults = [p for p in plans if p.get("default") == "YES"]
                selected = defaults if defaults else plans if len(plans) == 1 else []
                effective = []  # The default plan, not legacy scheme Testables, owns execution selection.
                if len(selected) != 1:
                    finding("ambiguous_test_plan", "Inspect the scheme's default test-plan selection.")
                else:
                    path = resolve_reference(selected[0].get("reference"))
                    data = json.loads(inside(path).read_text())
                    if not isinstance(data, dict):
                        raise ValueError("Invalid test-plan root")
                    plan_targets = data.get("testTargets")
                    if not isinstance(plan_targets, list):
                        raise ValueError("Missing plan testTargets")
                    for item in plan_targets:
                        ref = item["target"]
                        if not isinstance(ref, dict):
                            raise ValueError("Invalid plan target")
                        entry = inspect(ref.get("identifier"), ref.get("name"), ref.get("containerPath"),
                                        item.get("enabled", True) is not False and item.get("skipped", False) is not True, "default_plan")
                        effective.append(entry)
                        if item.get("skippedTests") or "selectedTests" in item:
                            finding("test_selection_filter", "A default-plan target has test selection filters; inspect its actual executed coverage.", "warning")
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
            finding("unreadable_test_configuration", "Could not fully inspect the scheme/default test plan.")
    if "test" not in profile["checks"]:
        finding("build_only_profile", "Automated tests are not configured in this profile.", "warning")
    elif not any(t["enabled"] and t["exists"] for t in effective):
        finding("no_effective_test_targets", "No enabled, resolved test targets were found in the selected test action.")
    expectations = profile.get("baseline_expectations", {})
    for name in expectations.get("required_test_targets", []):
        matches = [t for t in effective if t["resolved_name"] == name and t["enabled"] and t["exists"]]
        if len(matches) != 1:
            finding("required_test_target_missing_or_ambiguous", "A required test target is not uniquely enabled and resolved: " + name)
    head, dirty = git(app, "rev-parse", "HEAD"), git(app, "status", "--porcelain")
    upstream = git(app, "rev-parse", "--symbolic-full-name", "@{upstream}")
    tracking = {"ref": upstream, "commit": git(app, "rev-parse", "@{upstream}") if upstream else None,
                "counts": git(app, "rev-list", "--left-right", "--count", "HEAD...@{upstream}") if upstream else None,
                "freshness": "Local tracking cache only; no fetch or remote freshness check was performed."}
    counts = (tracking["counts"] or "").split()
    if len(counts) == 2 and all(v.isdecimal() for v in counts):
        tracking.update(ahead=int(counts[0]), behind=int(counts[1]))
        if tracking["behind"]:
            finding("behind_local_tracking", "HEAD is behind its locally cached upstream ref; remote freshness is unverified.", "warning")
    fingerprint = source_fingerprint(app)
    if not fingerprint.get("sha256"):
        finding("source_provenance_unavailable", "Git-visible source fingerprint is unavailable.", "warning")
    prior = None
    if reference:
        report, _ = read_report(reference)
        profile_hash = hashlib.sha256((app / ".ios-forge" / "app.json").read_bytes()).hexdigest()
        matches = source(report) is not None and source(report) == fingerprint.get("sha256") and report.get("profile_sha256") == profile_hash
        prior = {"source_and_profile_match": matches, "same_commit": head is not None and report.get("commit") == head,
                 "reported_status": report["status"], "note": "Matching inputs do not expand the earlier report's coverage or refresh remote state."}
        if not matches:
            finding("stale_or_unmatched_evidence", "Earlier evidence does not match the current source and profile.", "warning")
    return {"schema_version": 1, "kind": "static_baseline_audit", "status": "findings" if any(f["severity"] == "error" for f in findings) else "review" if findings else "inspected",
            "project": profile["project"], "scheme": scheme_info, "native_targets": list(targets.values()),
            "test_references": references, "effective_tests": effective, "findings": findings,
            "git": {"commit": head, "dirty": bool(dirty) if dirty is not None else None, "tracking": tracking},
            "source_fingerprint": fingerprint, "reference_evidence": prior,
            "not_verified": ["Native compilation and test execution", "Runtime/device availability", "Package resolution and plugin trust", "Remote branch freshness", "Signing and release readiness"]}
