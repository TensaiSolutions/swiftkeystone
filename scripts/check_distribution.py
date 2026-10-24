#!/usr/bin/env python3
"""Check installable resources and documentation contracts without dependencies."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import forge


def readme_errors(text, version):
    """Keep the adoption entry point aligned with the helper being packaged."""
    errors = []
    start = text.split("## Start here\n", 1)
    if len(start) != 2:
        return ["README: missing adoption entry point"]
    adoption = start[1].split("## Everyday workflow", 1)[0]
    versions = re.findall(r"swiftkeystone-(\d+\.\d+\.\d+)", adoption)
    release_versions = re.findall(r"/releases/tag/v(\d+\.\d+\.\d+)", adoption)
    if not versions or any(value != version for value in versions + release_versions):
        errors.append("README: download, extraction, and helper paths must match the packaged version")
    if f"swiftkeystone-{version}.zip.sha256" not in adoption or not release_versions:
        errors.append("README: missing versioned release/checksum instructions")
    return errors


def main():
    errors = readme_errors((ROOT / "README.md").read_text(), forge.VERSION)
    for name in forge.SKILLS:
        directory = ROOT / "skills" / name
        text = (directory / "SKILL.md").read_text()
        if not text.startswith(f"---\nname: {name}\ndescription: "):
            errors.append(f"{name}: missing or inconsistent frontmatter")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in link and not (directory / link).is_file():
                errors.append(f"{name}: missing reference {link}")
        metadata = (directory / "agents" / "openai.yaml").read_text()
        if f"${name}" not in metadata:
            errors.append(f"{name}: metadata prompt must name its skill")
    for skill, document in (("ios-onboard", "profile"), ("ios-onboard", "new-project"), ("ios-verify", "profile"), ("ios-verify", "verification"), ("ios-onboard", "macos"), ("ios-verify", "macos"), ("ios-onboard", "baseline-audit"), ("ios-onboard", "skill-updates"), ("ios-verify", "evidence-comparison")):
        if (ROOT / "docs" / f"{document}.md").read_bytes() != (ROOT / "skills" / skill / "references" / f"{document}.md").read_bytes():
            errors.append(f"{skill}: {document} reference differs from canonical docs")
    for example in ("app-profile.json", "macos-app-profile.json"):
        forge.load_profile(ROOT / "examples" / example)
    json.loads((ROOT / "schemas" / "app-profile.schema.json").read_text())
    registry = json.loads((ROOT / "upstream" / "registry.json").read_text())
    if any(c["status"] != "candidate" or c["revision"] is not None for c in registry["candidates"]):
        errors.append("Update dependency audit policy before promoting candidates")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Distribution checks passed: {len(forge.SKILLS)} self-contained skills, example, schema, registry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
