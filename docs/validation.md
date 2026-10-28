# SwiftKeystone validation

Validated locally on 2026-10-22 and 2026-10-23 with Xcode 26.6 (17F113), Swift compiler 6.3.3,
Python 3.12.3, and macOS 26.6.2 on Apple silicon. The toolkit v0.1.0/v0.2.0 previews are published on GitHub;
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

## v0.3.0 candidate: baseline, evidence, and skill upgrade

The candidate's portable tests cover static target/plan selection, stale evidence, malformed or
contradictory reports, privacy-bounded summaries, and three-way update staging with local edits,
conflicts, file removals, permission modes, and link/output guards. Extracted-package tests exercise
new commands and installed references without access to the source checkout.

The existing LaRecette v0.2.0 installation was upgraded locally using an extracted v0.3.0 candidate.
Preview and staging left the app untouched; installed originals were archived explicitly before the
reviewed incoming files were installed into vacant destinations. The profile and Git-visible app source
were unchanged, all installed references resolved, and manual rollback/re-activation reproduced both
versions' file inventories. A separate customized-installation fixture retained a local conflict and an
extra local resource without replacing installed files. This is reviewed staging with manual activation,
not an automatic in-place updater.

The static audit flagged the actual original orphaned/disabled UI-test reference, resolved both targets
in the current default plan, and distinguished a new commit with matching source/profile contents from
changed evidence. New comparison/summary commands also processed the existing v0.2.0 passing,
failing, and restored native reports, preserving the check-selection and legacy-context qualifications.
No new deliberate app regression was needed for those report comparisons.

Separately, the extracted v0.3.0 helper built LaRecette and ran **23 native tests, 0 failures, 0 skipped**
on the existing iOS 26.5 simulator with Xcode 26.6. Its report records a clean source tree, the new helper
version, and an explicit configuration snapshot. Comparing old/new native reports confirmed unchanged
source/profile hashes and matching test context. Raw evidence and app-specific fixtures remain outside
this repository. This same-agent local pilot does not establish independent user adoption, hosted app
CI, new macOS-native coverage, physical devices, minimum-runtime behavior, or distribution signing.
The candidate was subsequently published as v0.3.0 from merged main; original v0.1.0/v0.2.0 assets remain unchanged.


## Published v0.3.0 clean-download adoption (2026-10-24)

The public v0.3.0 ZIP and checksum were downloaded again and verified in a new private directory.
A fresh ephemeral Codex session, without this development conversation, used only the published
bundle and an isolated existing SwiftUI/SpriteKit app checkout. It read the installed onboarding
instructions explicitly; automatic skill discovery in a newly opened desktop chat was not tested.
The app already had a shared scheme, unit tests, UI tests, and unrelated Spec Kit skills.

The published helper completed installation preview, installation, configuration discovery, profile
validation, static audit, verification preview, and native build/test execution. Repeat installation
was a no-op, and repeated profile creation was refused. The tracked app source and existing unrelated
skills were preserved. Local adoption files made the checkout dirty; a passing build is not evidence
of a clean Git tree. Raw reports, source fingerprints, diagnostics, and machine-specific paths remain private.

On Xcode 26.6 and an iOS 26.5 simulator, the native build passed and the complete scheme recorded
**52 passed tests, 1 failed, 0 skipped**. The helper returned failure and retained structured evidence;
a bounded summary also reported the failed baseline. The existing UI test failed while waiting for
its win-results screen. One run does not distinguish product behavior from test timing, and no app
source or test was changed to produce a green baseline. This is successful execution/reporting of the
adoption workflow with an unresolved app baseline finding, not a claim that the app's tests all pass.

The published README still directed users to v0.2.0 and called v0.3.0 unpublished. The fresh session
was explicitly asked to test v0.3.0 and continue with that bundle while recording the contradiction;
it therefore does not establish unaided success from the original README. Development documentation
now points to v0.3.0, and distribution checks reject mismatched adoption download, extraction, release,
and helper versions. Regression tests reproduce stale instructions, and the corrected development
package passes extracted distribution checks. An additional startup guard rejects Python below 3.10;
the actual system Python 3.9 was refused without writes, while Python 3.12 installed all four skills in a
separate fixture. Setup guidance also explains normal sandbox approvals, misleading simulator discovery,
and full-scheme versus CI coverage. All **51 portable tests** pass. Native execution above used the
published helper; it was not repeated after this startup-only guard. These changes do not replace the immutable published
ZIP or establish adoption of a future release. No new macOS-native or physical-device validation was run.


## Native macOS feature pilot (2026-10-25)

An isolated CotEditor 7.0.6 checkout used the verified published v0.3.0 helper and installed workflows
for a bounded Sort by Pattern feature: optionally ignore surrounding ASCII spaces/tabs in comparison
keys, defaulting off and preserving the original document text and line endings. The original macOS 15
target, Swift settings and app dependency lock were preserved. The feature and tests are reviewed in a
separate fork PR; app source, profiles, setup patches, logs and result bundles are not distributed here.

With the earlier scoped ad-hoc signing and test-entitlement corrections, the refreshed baseline passed
**111 app tests**, **9 LineSort package tests**, and **3 native UI tests**. The existing window-close
query correction remains an explicit separate test commit. Neither the original upstream test setup nor
its UI suite is represented as passing unchanged. Standalone package tests were pinned to the app's
reviewed build-plugin version after an unpinned resolution selected a newer version; that attempt was
interrupted rather than treated as permission to execute a different plugin.

The expanded LineSort suite passed **12 tests**. The full native UI suite passed **4 tests** through
the published helper, including checkbox default/on state, sorting, Undo, exact saved bytes, termination
and reopen. A temporary bypass of comparison-key normalization caused two package assertions and
the new UI sorting assertion to fail; the helper reported **3 UI passes and 1 failure**. Restoring exact
source bytes returned the package suite and all four UI tests to passing; the final app suite also passed
all 111 tests. Comparison of the helper's
passing/failing/restored reports verified matching restored source/profile inputs and comparable
configuration. This is recorded execution plus deliberate mutation, not independent adoption or a claim
that comparison alone proves causality or test coverage. The original app profile was archived before
creating a separate UI profile in its vacant location, then restored; app and UI evidence retain their distinct scopes.

UI testing exposed an empty menu accessibility title and sheet-resize timing; queries now use an
observed contained menu command and wait for layout/state changes. An app-level screenshot captured
the primary display while the app was on another monitor. Corrected window/sheet attachments were
exported and inspected; only those show the intended UI. Assertions and on-disk checks establish the
journey, independently of the screenshots. The bundled macOS reference now includes these lessons.

These results use Xcode 26.6 on the current Apple silicon Mac, with local configuration differences
recorded and excluded from the feature PR. No global policy changes, plugin-validation bypass, upstream
submission, non-English layout certification, other hardware/macOS validation, manual accessibility,
release signing or notarization are claimed. SwiftKeystone's installed v0.3.0 skills and published assets
were preserved; updated guidance is development work for a future release.


## v0.4.0 candidate: optional baseline expectations (2026-10-26)

The development helper adds an opt-in schema-version-1 contract for required test targets and a minimum
executed count. Existing profiles remain valid without migration. Portable tests cover profile refusal,
skipped-case exclusion, target-tree interpretation and inconsistent evidence, successful native-command
simulation rejected by the contract, preserved native failure diagnostics, report consistency/privacy,
count decreases, expectation/context changes, and extracted-package contract validation. All **63 portable
tests** and distribution checks pass; these are separate from the native results below.

Isolated copies of the existing iOS and macOS pilots used an extracted v0.4.0 candidate. The iOS profile
required both unit and UI targets and 23 executed cases. Its positive baseline passed **23 tests**.
Temporarily omitting the UI target from the default plan produced **17 passing cases**, native exit 0,
but verification exit 1 for the missing target and unmet minimum. Audit also rejected the missing suite.
Restoring exact plan bytes returned all 23 cases to passing with matching source/profile hashes.

The Mac profile required its UI target and four executed cases. Its UI baseline passed **4 tests**.
Temporarily selecting the app-only scheme produced **111 passing app cases**, native exit 0, but
verification exit 1 because the required UI target had not executed. Audit rejected this configuration
as well. Restoring the UI profile returned all four UI cases to passing with matching source/profile
hashes. The earlier local ad-hoc signing/test-entitlement setup remained scoped to the isolated clone.

Comparisons flagged the iOS six-case decrease and the Mac scheme/context change for review. The Mac's
larger count did not satisfy the missing-suite contract. Final summary presentation and report validation
were exercised against the recorded native evidence; code counts do not certify behavioral coverage.
These were expectation/exclusion checks, not deliberately failing app assertions or independent adoption.
The observed Xcode result-tree layouts are supported; unsupported layouts fail a declared target contract
rather than guessing execution. Raw reports, result bundles, target names and machine-specific inputs
remain outside the distribution. Existing working app checkouts, installed skills and released assets were
preserved. No v0.4.0 publication, minimum-runtime, other hardware, live-service or signing readiness is claimed.
