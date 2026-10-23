"""Three-way skill update staging. This module never writes into the app."""
import hashlib
import json
import os
import stat
from pathlib import Path
import tempfile

from keystone_common import ForgeError, inventory, write_json


def tree(root):
    if root.is_symlink() or (root.exists() and not root.is_dir()):
        raise ForgeError("Skill roots must be real directories, not links or files.")
    files = inventory(root) if root.exists() else {}
    return {name: {"sha256": checksum, "mode": stat.S_IMODE((root / name).stat().st_mode) & 0o777}
            for name, checksum in files.items()}


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def copy_checked(source, destination, expected):
    for name, fingerprint in expected.items():
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ForgeError("An input changed while staging; inspect the incomplete stage and retry.")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != fingerprint["sha256"] or (stat.S_IMODE(path.stat().st_mode) & 0o777) != fingerprint["mode"]:
            raise ForgeError("An input changed while staging; inspect the incomplete stage and retry.")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)
        os.chmod(target, fingerprint["mode"])


def stage_update(app, previous, incoming, names, output, dry_run=False):
    app, previous, incoming = (Path(p).resolve() for p in (app, previous, incoming))
    for release in (previous, incoming):
        if (release / "skills").is_symlink():
            raise ForgeError("Linked distribution skill roots are not supported.")
    destination = app / ".agents" / "skills"
    # Reject even inward-pointing links: there is no linked-tree update mode.
    for path in (app / ".agents", destination):
        if path.is_symlink():
            raise ForgeError("Linked skill installation roots are not supported.")
    output = Path(output).expanduser().resolve()
    if any(output.is_relative_to(root) for root in (app, previous, incoming)):
        raise ForgeError("Stage updates outside the app and both distribution inputs.")
    snapshots, decisions = {}, []
    for name in names:
        roots = {"previous": previous / "skills" / name, "installed": destination / name,
                 "incoming": incoming / "skills" / name}
        for key in ("previous", "incoming"):
            if not roots[key].is_dir():
                raise ForgeError(f"Missing distribution skill: {name}")
        for root in roots.values():
            if not root.resolve().is_relative_to(app if root == roots["installed"] else
                                               previous if root == roots["previous"] else incoming):
                raise ForgeError("A skill path escapes its input tree.")
        maps = {key: tree(root) for key, root in roots.items()}
        snapshots[name] = (roots, maps)
        for path in sorted(set().union(*[set(m) for m in maps.values()])):
            old, current, new = (maps[key].get(path) for key in ("previous", "installed", "incoming"))
            if current == new:
                action, choice = "unchanged", "installed"
            elif current == old:
                action, choice = "update", "incoming"
            elif new == old:
                action, choice = "preserve_local", "installed"
            else:
                action, choice = "conflict", "installed"
            decisions.append({"skill": name, "file": path, "action": action, "candidate_from": choice,
                              "previous_sha256": old["sha256"] if old else None,
                              "installed_sha256": current["sha256"] if current else None,
                              "incoming_sha256": new["sha256"] if new else None,
                              "previous_mode": old["mode"] if old else None,
                              "installed_mode": current["mode"] if current else None,
                              "incoming_mode": new["mode"] if new else None})
    conflicts = sum(d["action"] == "conflict" for d in decisions)
    report = {"schema_version": 1, "operation": "stage_only", "app_changed": False,
              "conflicts": conflicts, "status": "conflicts" if conflicts else "review_required",
              "files": decisions,
              "input_fingerprints": {name: {key: digest(files) for key, files in maps.items()}
                                     for name, (_, maps) in snapshots.items()},
              "note": "Review candidate and conflicts before manual activation. Originals and profiles are never replaced. Concurrent edits/installations are unsupported."}
    report["candidate_entrypoints_present"] = all(any(d["skill"] == name and d["file"] == "SKILL.md"
        and d[d["candidate_from"] + "_sha256"] is not None for d in decisions) for name in names)
    if dry_run:
        return report
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix="skill-update-", dir=output))
    # An incomplete marker survives a copy failure. No app mutation or cleanup of user files occurs.
    write_json(stage / "manifest.json", dict(report, status="incomplete"))
    for name, (roots, maps) in snapshots.items():
        copy_checked(roots["installed"], stage / "backup" / name, maps["installed"])
        copy_checked(roots["incoming"], stage / "incoming" / name, maps["incoming"])
        chosen = {"installed": {}, "incoming": {}}
        for decision in decisions:
            if decision["skill"] != name:
                continue
            key = decision["candidate_from"]
            checksum = maps[key].get(decision["file"])
            if checksum is not None:
                chosen[key][decision["file"]] = checksum
        for key, files in chosen.items():
            copy_checked(roots[key], stage / "candidate" / name, files)
        for key, root in roots.items():
            if tree(root) != maps[key]:
                raise ForgeError("An input changed while staging; the app was not modified.")
    report["candidate_entrypoints_present"] = all((stage / "candidate" / name / "SKILL.md").is_file() for name in names)
    report["stage"] = str(stage)
    write_json(stage / "manifest.json", report)
    return report
