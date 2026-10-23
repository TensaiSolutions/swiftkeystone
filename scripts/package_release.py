#!/usr/bin/env python3
"""Create a reproducible source archive from an explicit distribution allowlist."""
import hashlib
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import forge

DIRECTORIES = ("skills", "schemas", "examples", "docs", "upstream", "scripts", "tests", ".github")
FILES = ("forge.py", "keystone_common.py", "keystone_audit.py", "keystone_evidence.py", "keystone_updates.py", "README.md", "AGENTS.md", "LICENSE", "ACKNOWLEDGEMENTS.md", "CONTRIBUTING.md", "CHANGELOG.md", ".gitignore")


def package(destination):
    paths = [ROOT / file for file in FILES]
    paths += [path for directory in DIRECTORIES for path in (ROOT / directory).rglob("*")
              if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo")]
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"swiftkeystone-{forge.VERSION}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(paths):
            if path.is_symlink():
                raise forge.ForgeError(f"Refusing a symbolic link in the distribution: {path}")
            entry = zipfile.ZipInfo(f"swiftkeystone-{forge.VERSION}/" + path.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, path.read_bytes())
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n")
    return archive, checksum


if __name__ == "__main__":
    for path in package(ROOT / "outputs"):
        print(path)
