# Starting an iOS app from scratch

The Forge Notes pilot uses this path: establish the product journey, generate an Xcode project,
discover the actual scheme/destination, install Forge, establish a baseline, then implement features.
Forge itself does not install a project generator. XcodeGen 2.46.0 was already installed for the pilot.

## Create and generate

Use a new app directory outside the toolkit repository. Record its first user journey, deployment
target, architecture, persistence choice, and acceptance criteria in a short `PLAN.md` or the team's
existing planning format. For Forge Notes these were iOS 18, Swift 6, SwiftUI, atomic local JSON,
Swift Testing unit tests, and XCTest UI tests. Different apps may need different choices.

If XcodeGen is already available, put the app sources and tests in the new directory and describe
them in `project.yml`. The pilot's companion source archive includes the full project spec and generated
Xcode project. Generate it from the app directory with:

```sh
xcodegen generate --spec project.yml
```

An app target's `scheme.testTargets` must include the actual unit/UI test targets, not just the app.
Use a shared scheme. Set `SWIFT_VERSION` to the intended language mode; it is not the compiler version.
Simulator-only pilot targets disable signing explicitly. Do not copy that policy into an app's device
or release configuration without considering the app's requirements.

If no generator is installed, create the project in Xcode or obtain authorization for the chosen
generator. Do not silently add a new dependency or replace an existing project-generation convention.

## Inspect and onboard

From the app directory, use the selected Xcode installation:

```sh
xcodebuild -list -json -project ForgeNotes.xcodeproj
xcrun simctl list devices available
xcodebuild -showdestinations -project ForgeNotes.xcodeproj -scheme ForgeNotes
```

Choose an actual compatible simulator UUID. If several app schemes are plausible, resolve that
choice before running checks. A unit-only scheme may be useful for focused regression tests; the full
acceptance run must use the scheme that includes the intended UI tests.

Run `forge.py install` and `forge.py init` from the toolkit directory as described in README, using
absolute app paths. Inspect `verify --dry-run`, then run verification with an evidence directory outside
the app checkout. Create local version history before feature work so evidence can identify the baseline.

## Build and prove

Use `$ios-plan-feature`, `$ios-build-feature`, and `$ios-verify` in the app's Codex chat. Save material
decisions in the existing project plan/context; the next chat must be able to recover them from files.
Require behaviour evidence for acceptance criteria, not merely a successful compile.

For a new toolkit integration, deliberately break one assertion and one compilation unit, verify
the run fails, restore them, and rerun the full suite. An invalid scheme/destination and a zero-test
configuration must never be reported as successful verification. Keep mutations in a disposable app
and restore source/configuration after each case; do not inject faults into a user's working app.
