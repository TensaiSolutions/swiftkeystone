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

If a native UI-test runner reports that it cannot enable automation mode, record an infrastructure
failure and do not count its runner error as an executed app journey. Do not repeatedly rerun it or
change system automation permissions implicitly. A desktop UI tool may provide separate journey
evidence; label that method explicitly. Keep any successful unit tests separate from blocked UI suites.
