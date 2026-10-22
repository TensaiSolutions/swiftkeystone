# SwiftKeystone validation

Validated locally on 2026-10-22 with Xcode 26.6 (17F113), Swift compiler 6.3.3,
Python 3.12.3, and macOS 26.6.2 on Apple silicon. Nothing has been published to GitHub or the App Store.

## New app: Forge Notes

Forge Notes was created from a product brief and a saved acceptance plan, using the four installed
SwiftKeystone workflows. XcodeGen 2.46.0, already installed on the machine, generated a shared-scheme Xcode
project. The app targets iOS 18 and uses SwiftUI, a main-actor observable store, and atomic JSON files.
No third-party app library or remote service was added. Operational evidence remains outside this repository.

- Initial scaffold: real build, one Swift Testing baseline test, and one XCTest UI launch test passed.
- Final iPhone 17 Pro / iOS 26.5: build passed; **14 tests passed, 0 failed, 0 skipped**.
- Final iPhone 16 Pro / iOS 18.0: build passed; **14 tests passed, 0 failed, 0 skipped**.
- Both final runs used the same clean source revision and source fingerprint; machine-specific
  simulator configuration is hashed separately. Full Xcode result bundles and logs are retained privately.

The final suite includes nine model/persistence tests and five UI tests. It covers create/edit/cancel,
favourite filtering and unstar, termination/relaunch persistence, blank-title validation, corrupt-file
preservation, failed-save state/draft retention, and automated accessibility audits of empty, populated,
and editor screens. Automated audit coverage is not a manual VoiceOver certification.

## Deliberate failures

Seven isolated fault scenarios were detected as expected, with source/profile restored after every case:

1. Incorrect assertion: the nine-test unit suite reported eight passes and one failure.
2. Compilation error: build failed; the later test check was not run.
3. Nonexistent scheme: failed with the native scheme diagnostic.
4. Unavailable simulator UUID: failed with the native destination diagnostic.
5. Favourite persistence regression: the existing reload test failed when favourite state was lost on disk.
6. One-second timeout: the real build process group was terminated; later checks were not run.
7. All-skipped test scheme: Xcode rejected its test action and reported zero tests; SwiftKeystone reported failure.

The native empty-scheme case returned a nonzero Xcode exit code. Separate portable tests also prove
that SwiftKeystone rejects a synthetic successful command paired with zero, all-skipped, missing, unreadable,
or failing test-result evidence. We do not claim that Xcode returned a false success in the native case.

## Issues found and fixed

- The real accessibility audits found contrast and large-text clipping issues. Explicit contrast styling,
  expandable text layout, and flexible editor actions resolved the observed findings. iOS 18 exposed a
  further section-heading contrast difference; moving the headings into labelled form content fixed it.
- An editing UI test assumed a cursor position. It now verifies the entered draft is the value saved
  and reloaded without depending on where a tap places the insertion point.
- SwiftKeystone reports previously exposed only command outcomes. They now include actual result-bundle test
  counts/destinations, Xcode version, source/profile fingerprints, and failure diagnostics. Missing or
  zero-execution evidence cannot produce a passing test check; timeout diagnostics name the configured limit.
- The onboarding skill now includes a documented project-generation and first-baseline reference.

## Installation and fresh context

A separate local repository demonstrated a no-write dry run, identical repeated installation, preservation
of AGENTS.md and uncommitted edits, unchanged branch/HEAD, and refusal to overwrite a customized skill.
An independent fresh-context agent used only the installed onboarding/planning skills and project files
to recover app conventions and produce a bounded feature plan. It performed no builds or implementation;
this is evidence for context recovery and planning, not unattended development across fresh sessions.

## Existing app: LaRecette

An isolated clone of the existing SwiftUI/SwiftData app exercised the installed workflows against its
native Xcode project and default test plan. Swift 5 language mode, iOS 18.2 deployment target, original
app/unit target settings, and signing settings were preserved. Changes remain on a local pilot branch.

- The original app built, but its tests failed to compile because they imported an internal SwiftUI module.
  Replacing that import with Foundation allowed all 11 original tests to pass twice.
- Onboarding found an orphaned, disabled UI-target reference. Restoring the target and adding deterministic,
  offline UI journeys provided populated, empty, and failed-request coverage.
- Three regression tests failed before their fixes: two incorrect large-image URL mappings and a loading
  indicator that never ended after a request failed. The fixes address both product defects.
- Final iPhone 17 Pro / iOS 26.5: **17 tests passed, 0 failed, 0 skipped**, twice on the same clean revision.
- A Release simulator build passed; the resulting binaries excluded the Debug-only fixture hooks/data.
- Test persistence now uses explicit in-memory contexts with an isolation check. Original tests already
  passed twice; this improvement is not evidence of reproduced persistence flakiness.

The pilot also exposed a SwiftKeystone diagnostic gap: structured result-bundle failures now supply the useful
message when the text log lacks one. Onboarding now explicitly checks that test-plan targets exist and
are enabled. App-specific evidence, source archives, and the reviewable patch remain outside tracked
SwiftKeystone distribution files. Simulator results do not establish physical-device or live-service behavior.

## Portable checks and limits

All **20 portable tests** passed. Distribution checks passed for four self-contained skill bundles,
references, example profile, schema syntax, candidate registry, and reproducible archive extraction/installation.
YAML frontmatter/metadata were parsed with the system Ruby YAML parser; the optional Skill Creator
Python validator was unavailable because PyYAML was not installed. No dependency was installed to bypass that.

Physical devices, manual VoiceOver, dark mode/full device and text-size coverage, LaRecette on its exact
minimum runtime, live backend behavior, third-party specialist skill execution, hosted CI, and release
signing/submission remain unvalidated.
This is evidence for a simulator-tested foundation preview, not universal iOS compatibility.
The companion source archive includes the generated Xcode project and tests, but excludes local profiles,
Git history, raw logs, result bundles, and application/test data. See docs/new-project.md to repeat the workflow.
