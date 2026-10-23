# Changelog

## Unreleased

- Extend the existing workflow descriptions to native macOS while preserving `ios-*` skill aliases.
- Add a native macOS profile example and guidance for local signing, document journeys, and separate UI schemes.
- Report Xcode's failed build step when a failure log has no useful error line.
- Keep evidence limits applicable to the selected destination rather than implying a Mac test used a simulator.

- Clarify release download/checksum verification, helper location, local schemes, and apps without tests.
- Explicitly report missing automated-test coverage for build-only profiles.

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
