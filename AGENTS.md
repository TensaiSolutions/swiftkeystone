# iOS Forge

This repository distributes Codex skills and dependency-free Python helpers for iOS projects.
Keep app-specific data and operational evidence outside this repository.

- Preserve existing app architecture, deployment targets, and user instructions.
- Keep skills self-contained after installation into `.agents/skills/`.
- Never install upstream skills or alter global settings implicitly.
- CLI command arguments are arrays, never shell command strings.
- Existing profiles and differing installed skills must not be overwritten.
- Run `python3 -m unittest discover -s tests -v` and `python3 scripts/check_distribution.py` after changes.
- Report Xcode/device checks separately from portable tests; do not imply device validation from mocks.
