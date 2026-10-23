---
name: ios-verify
description: Verify an iOS or macOS change with configured Xcode builds and tests plus relevant simulator, native Mac, or device evidence, distinguishing failures, skipped checks, and untested behaviour.
---

Read the app's instructions, profile, acceptance criteria, and changed code. Use [references/profile.md](references/profile.md) for the configuration contract and [references/verification.md](references/verification.md) for evidence reporting.

1. Establish the toolchain, scheme, destination, current revision and working-tree state. Check whether baseline failures were already recorded. Do not rewrite deployment targets, signing configuration, or tests to make a check pass.
2. If the SwiftKeystone CLI is available, inspect `verify --dry-run` first for a new configuration, then execute the configured checks with a private output directory outside the checkout. Otherwise use the app's established commands. Commands and result locations must be reproducible. Dependencies and Xcode build phases may execute project code: work only in a repository the user has authorized you to build.
3. Read failures and result bundles, not just command completion. Stop repeated attempts when the same environmental blocker recurs; distinguish environment failures from product defects. Report configured checks that were not run.
4. For changed interactions, exercise acceptance criteria through existing UI tests or an available simulator/desktop UI tool. Note host/device, OS/runtime and relevant state. Capture only useful evidence. Screenshots alone do not prove interaction, VoiceOver behaviour, or performance. Static accessibility review, automated checks, and manual assistive-technology testing are different evidence levels.
5. Identify capabilities needing a physical device or service environment. Do not report those as verified by simulator or mocked tests.

Report build/test status separately from user-journey and release readiness. Sanitise excerpts before sharing them externally. Never infer health from missing logs or missing tools. CLI result `passed` means only its configured commands passed; it does not mean all acceptance criteria or release checks passed.

For native macOS destinations, signing prerequisites, and separate UI-test schemes, read
[references/macos.md](references/macos.md). The legacy `ios-*` name remains for installed-skill compatibility.
