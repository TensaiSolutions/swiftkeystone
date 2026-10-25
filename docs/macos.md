# Native macOS verification

Use the existing Xcode project, shared scheme, deployment target, Swift mode, and architecture.
A native macOS target is different from an iOS app running as Designed for iPad on Mac.
Inspect supported destinations with the selected Xcode installation. For a native Mac scheme,
`platform=macOS` is an example destination; add `arch=arm64` or `arch=x86_64` only when appropriate
for the actual host and target. Do not substitute an iOS simulator destination.

The existing profile accepts this destination without new fields.
The distribution includes `examples/macos-app-profile.json` as a placeholder, not an app configuration. Initialize it with the helper
and the discovered project/scheme, validate it, inspect `verify --dry-run`, then run build/test.
Read the repository's local-development signing instructions. If a local signing change is required,
explain it and keep it scoped to the authorized checkout. Do not change global signing settings,
remove sandbox entitlements, disable package validation, or claim distribution signing from a local build.
If Xcode blocks an untrusted pinned build plugin, record the plugin/version and ask for explicit trust
approval before changing persistent Xcode trust records. Enable only that reviewed plugin; preserve validation.

Inspect the selected scheme's test action: it may run app tests while another shared scheme runs UI
tests or local-package tests. Name each suite and record separate evidence directories. The helper
uses one scheme per profile/run. Preserve the original profile before explicitly changing the scheme
for another run, restore it afterward, and retain both reports; do not silently replace existing profiles.
Use established native commands for suites or flags the helper does not support, and report them separately.
Do not imply that an app scheme's passing unit tests cover the separate UI-test scheme or package suites.

For document journeys, use disposable files. Verify opening, editing, saving, actual on-disk contents,
and reopening after app termination. Screenshots support the record but do not establish persistence.
Keep XCTest automation, manual/UI-tool observations, accessibility checks, and signing/notarization
as distinct evidence. A run on the current Mac does not establish other macOS versions or hardware.

Package resolution and first builds can take longer than incremental builds. Retain the private log,
report stalled or failed resolution as an environment baseline finding, and preserve pinned dependencies.
Do not repeatedly rebuild or change dependency versions merely to obtain a passing baseline.
A standalone `swift test` package can resolve a different build-plugin version from the app workspace
when it lacks its own lockfile. Inspect both resolutions before running it; preserve the app's reviewed
pin for the pilot and retain the standalone lockfile privately when repository policy excludes it.
Use resolved-version enforcement when supported. An earlier trust approval for one plugin version
does not approve another version, and a package-only baseline does not establish native app coverage.

If a native UI-test runner reports that it cannot enable automation mode, record an infrastructure
failure and do not count its runner error as an executed app journey. Do not repeatedly rerun it or
change system automation permissions implicitly. A desktop UI tool may provide separate journey
evidence; label that method explicitly. Keep any successful unit tests separate from blocked UI suites.

Investigate automation startup failures with the host's current authorization state and the original
XCTest log. A disabled idle automation state alone does not prove that the next test cannot start.
After a relevant environment change or explicit authorization, use one focused UI test to distinguish
runner startup from an app assertion. Surface the normal Xcode authorization flow when needed;
leave authentication to the user. Do not enable authentication-free automation or broader developer
policies as a shortcut. Record what actually changed; a later successful run does not establish why
an earlier timeout occurred or prove that authorization survives a restart.

Keep desktop interaction separate while XCTest drives the app. When a case reaches the UI and fails,
inspect its assertion and accessibility query before changing app behavior. Broad first-match queries
can resolve to another window after closing the original, and a button label can also match a Touch Bar
control. Scope queries to the intended window/dialog or a stable identifier, then verify the intended
observable outcome. Keep any pilot test correction explicit and rerun the affected case and relevant
suite; do not count the original upstream suite as passing unchanged.


SwiftUI sheets can resize when controls change. Wait for the selected state and layout to settle before
clicking a control whose position moved, and verify its resulting value. If a menu has an empty
accessibility title, inspect the captured hierarchy and use a meaningful contained item to identify it;
prefer that semantic query over screen coordinates, and do not infer an app defect from a failed label query.

For screenshot attachments, target the intended document window or sheet and inspect the exported
image. App-level captures on a multi-display Mac can show the primary display rather than the tested
window. A named attachment is not evidence that its pixels show the intended app. Keep incidental
content from other apps private; use assertions and on-disk checks as the authority for behavior.
