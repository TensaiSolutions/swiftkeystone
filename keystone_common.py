"""Shared dependency-free filesystem and source-evidence helpers."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

class ForgeError(Exception):
    pass


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def inventory(directory):
    """Fingerprint regular files; reject links rather than follow them into another tree."""
    found = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ForgeError(f"Skill contains a symbolic link: {path}")
        if path.is_file():
            found[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def source_fingerprint(app):
    """Hash Git-visible file contents, including untracked work, without storing their contents."""
    try:
        result = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                                cwd=app, capture_output=True, check=True, timeout=15)
        digest = hashlib.sha256()
        for name in sorted(set(result.stdout.split(b"\x00")) - {b""}):
            path = app / os.fsdecode(name)
            if path.is_symlink():
                contents = b"symlink:" + os.fsencode(os.readlink(path))
            elif path.is_file():
                contents = path.read_bytes()
            else:
                contents = b"missing-or-nonregular"
            digest.update(name + b"\x00" + hashlib.sha256(contents).digest())
        return {"sha256": digest.hexdigest(), "scope": "Git-visible files; ignored files and link targets excluded"}
    except (OSError, subprocess.SubprocessError) as error:
        return {"sha256": None, "error": str(error)}


def private_output(path, text, forbidden=()):
    """Create a new private artifact; never replace an existing path or write into inputs."""
    requested = Path(path).expanduser()
    if requested.is_symlink():
        raise ForgeError("Refusing a linked output file.")
    target = requested.resolve()
    if any(target.is_relative_to(Path(root).resolve()) for root in forbidden):
        raise ForgeError("Keep operational artifacts outside the app and distribution inputs.")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as handle:
        handle.write(text)
    return target
