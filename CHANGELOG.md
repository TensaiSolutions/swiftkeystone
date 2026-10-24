# Changelog

## Unreleased

- Correct published-release adoption instructions to use v0.3.0, and check download/helper version consistency during packaging.
- Reject Python versions below 3.10 before command dispatch; explain interpreter selection, normal sandbox approvals, and local-scheme versus CI coverage.
- Record fresh-session adoption against an existing app, including an honestly failed native UI baseline.

## 0.3.0 — adoption and evidence preview

- Add a portable static audit of project/workspace targets, scheme/default-plan wiring, local tracking state, and earlier source/profile evidence.
- Compare completed v0.2/v0.3 reports and detected-failure/restoration inputs; draft bounded PR verification summaries without private diagnostics.
- Stage three-way skill updates, exact backups, preserved local edits/deletions, and explicit conflicts without overwriting installed skills or profiles.
- Keep legacy skills and schema-version-1 profiles compatible; bundle the new workflow references.
- Expand portable coverage to 48 tests; validate a local LaRecette upgrade with 23 native tests and unchanged app/profile inputs.

## 0.2.0 — iOS and macOS foundation preview

- Extend the existing workflow descriptions to native macOS while preserving `ios-*` skill aliases.
- Add a native macOS profile example and guidance for local signing, document journeys, and separate UI schemes.
- Report Xcode's failed build step when a failure log has no useful error line.
- Keep evidence limits applicable to the selected destination rather than implying a Mac test used a simulator.
- Clarify release download/checksum verification, helper location, local schemes, and apps without tests.
- Explicitly report missing automated-test coverage for build-only profiles.
- Add macOS XCTest startup and selector troubleshooting based on a native UI pilot.
- Validate a document open/edit/save/disk-check/terminate/reopen journey with native XCTest.
- Preserve existing profile paths, skill aliases, conflict-safe installation, and original v0.1.0 assets.

## 0.1.0 — foundation preview

- Renamed iOS Forge to SwiftKeystone; release archives use `swiftkeystone-0.1.0`.
- Retained `forge.py`, `.ios-forge/app.json`, and existing skill commands for compatibility.
- The broader name does not expand this preview beyond its validated iOS workflows.

- Four Codex workflows: onboarding, feature planning, feature implementation, and verification.
- Project-scoped installation with conflict preflight and dry-run support.
- Versioned app profile, JSON schema, and dependency-free validation.
- Sequential Xcode build/test runner with unique evidence directories and timeouts.
- Optional upstream candidate registry; no automatic third-party installation.
- Portable regression tests, package checks, release packaging, and pilot scenarios.
- Real Forge Notes integration pilot using Xcode, Swift Testing, and XCTest UI automation.
- Xcode/result-bundle test counts, source fingerprints, and failure diagnostics in verification reports.
- Verification rejects missing/unreadable result summaries and zero/all-skipped test runs.
- Documented new-project generation and first-baseline workflow.

- Existing LaRecette pilot preserves its native project, default test plan, Swift 5 mode, and iOS 18.2 target.
- Structured test-failure diagnostics and onboarding checks for orphaned or disabled test targets.

Physical-device validation and unattended maintenance remain future milestones.
