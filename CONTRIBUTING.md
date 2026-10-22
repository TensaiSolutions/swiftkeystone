# Contributing

Keep changes focused on a demonstrated iOS development workflow. Describe the problem, changed
behaviour, and evidence. Preserve backwards compatibility for version-1 app profiles or explicitly
version the contract. Do not include real app profiles, raw crash logs, credentials, or personal paths.

Use Python 3.10+ and run the two checks in `AGENTS.md`. Test observable invariants such as preserving
existing files or correctly reporting a failed command. Keep portable runner tests distinct from real
Xcode and device evidence. If canonical profile/verification docs change, update their bundled copies
under `skills/`; distribution checks enforce consistency.

New skills need a precise trigger, self-contained resources, and realistic evaluation scenarios.
Do not add specialist content already maintained upstream without a reason and license review.
Contributions are made under the repository's MIT license.
