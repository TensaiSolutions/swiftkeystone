# SwiftKeystone validation

Validated locally on 2026-10-22 and 2026-10-23 with Xcode 26.6 (17F113), Swift compiler 6.3.3,
Python 3.12.3, and macOS 26.6.2 on Apple silicon. The toolkit v0.1.0 is published on GitHub;
app pilots are local validation work and have not been submitted to the App Store.

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

At the original iOS milestone, all **20 portable tests** passed. The v0.2.0 candidate passes **23 portable tests**. Distribution checks passed for four self-contained skill bundles,
references, example profile, schema syntax, candidate registry, and reproducible archive extraction/installation.
YAML frontmatter/metadata were parsed with the system Ruby YAML parser; the optional Skill Creator
Python validator was unavailable because PyYAML was not installed. No dependency was installed to bypass that.

Physical devices, manual VoiceOver, dark mode/full device and text-size coverage, LaRecette on its exact
minimum runtime, live backend behavior, third-party specialist skill execution, and release
signing/submission remain unvalidated.
Hosted package CI has since passed on Linux/macOS with Python 3.10/3.13; it does not build pilot apps.
This is evidence for the stated foundation-preview environments, not universal Apple-platform compatibility.
The companion source archive includes the generated Xcode project and tests, but excludes local profiles,
Git history, raw logs, result bundles, and application/test data. See docs/new-project.md to repeat the workflow.

## Published-release adoption check

The public v0.1.0 ZIP and SHA-256 asset were downloaded into a clean directory and used to onboard
a third, isolated existing app. Extraction, dry-run installation, repeated installation, profile setup,
and command discovery passed. The app built on an iOS 26.5 simulator destination without source or
Xcode setting changes. It had no test target: the default build/test baseline correctly failed its test
action, while an explicitly selected build-only baseline passed.

This exposed unclear first-run guidance and a missing build-only scope reminder. Fixes included in v0.2.0
clarify download/checksum steps, helper location, scheme portability, and apps without tests; the
console and JSON now explicitly identify absent automated-test coverage. The updated helper also
passed the real build-only check. All 21 portable tests at that milestone passed. The v0.1.0 assets remain unchanged.

This same-agent clean-artifact check is not independent user research, automatic skill-discovery UI
validation, or behavioral coverage of the app. Private evidence remains outside this repository.

## Native macOS pilot (v0.2.0)

A pinned CotEditor 7.0.6 checkout exercised a native macOS destination on the current Apple silicon
Mac. The original macOS 15 target, Swift settings, Xcode project, dependency lock, and production app
source were preserved. Upstream's documented ad-hoc signing configuration was selected locally;
test bundles also needed a scoped correction for a nonexistent entitlement file. This is local build
coverage, not distribution-signing or notarization evidence.

The initial build correctly stopped at a pinned SwiftLint plugin trust gate. The user explicitly
approved that plugin/version in Xcode; validation was not disabled. The native app then built, and
111 existing app tests passed with corrected local test setup. The separate XCTest UI runner failed
while enabling automation mode, before any app journey executed. A later follow-up established actual UI coverage as described below.

A desktop UI tool separately demonstrated opening, editing, saving exact file bytes, quitting, and
relaunching the app with the saved content visible. A pilot document serialization round-trip case
brought the native app suite to 112 passes. A temporary extra byte in the production serializer made
the helper CLI fail with 111 passes and one failure; its diagnostic identified the 64-versus-63-byte
mismatch. Restoring the source and profile returned all 112 tests to passing. The before/after green
source fingerprints match, and no production mutation remains.

App test runs used both the helper CLI and explicit native Xcode commands with reused build output;
private evidence records which method was used. Separate local-package test suites were not all run.
The v0.2.0 toolkit adds macOS workflow scope, bundled guidance and a profile example, and a
fallback diagnostic from Xcode's failed-build-step summary. All 23 portable tests pass.

On 2026-10-23 the native XCTest runner successfully started, without an authentication prompt or
explicit change to global automation/developer policies. The earlier timeout did not recur; the cause
and authorization behavior after reboot remain unproven. A focused upstream typing test reached UI
actions but its first-window query could resolve to another window after closing the intended one.
A local correction checks the window-count decrease. A new document journey initially matched a
Touch Bar Open control; targeting the native dialog button identifier corrected that selector.

With those explicit local test corrections, the complete UI scheme passed **4 tests, 0 failures,
0 skipped**: launch performance, Settings panes, typing/window close, and document open/edit/save,
exact on-disk content verification, termination, relaunch, and reopen. The original upstream UI suite
did not pass unchanged. Production document code remains byte-for-byte upstream. Raw logs, result
bundles, fixture files, and pilot patches remain outside the distribution.

This establishes native XCTest UI coverage on the current Mac, separately from the earlier desktop UI
tool observation. It does not establish other hardware/OS versions, manual VoiceOver, or release
signing/submission. The published v0.1.0 archive remains unchanged.

## v0.2.0 release-candidate package check

A locally built v0.2.0 ZIP passed checksum verification, allowlist inspection, and clean extraction
outside the source checkout. From that extracted helper, separate iOS and macOS fixture profiles
passed installation preview, first/repeated installation, profile creation/validation, and verification
command previews. Existing profiles, instructions, and deliberately customized installed skills were
preserved; conflicting installation and repeated profile creation were refused as expected.

These were portable adoption checks against fixture project directories, not Xcode app builds,
independent user research, or a download of a published v0.2.0 asset. The native app/UI results above
remain separate evidence. Publication requires rebuilding from the reviewed merged commit and
checking the actual downloaded assets afterward.
