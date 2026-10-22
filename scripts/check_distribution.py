#!/usr/bin/env python3
"""Check installable resources and documentation contracts without dependencies."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import forge


def main():
    errors = []
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
    for skill, document in (("ios-onboard", "profile"), ("ios-verify", "profile"), ("ios-verify", "verification")):
        if (ROOT / "docs" / f"{document}.md").read_bytes() != (ROOT / "skills" / skill / "references" / f"{document}.md").read_bytes():
            errors.append(f"{skill}: {document} reference differs from canonical docs")
    forge.load_profile(ROOT / "examples" / "app-profile.json")
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
