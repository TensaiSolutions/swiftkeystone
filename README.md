# iOS Forge

Reusable iOS development workflows for Codex: onboard an app, plan a feature,
implement a bounded change, and collect honest verification evidence.

**v0.1.0 — foundation preview.** Four installable skills and a dependency-free Python helper.
No account, service, API key, or global configuration change is required by Forge itself.
You use it within your existing Codex environment.

## Start here

Download a release archive or clone this repository and keep it in a stable location.
Commands below run from that iOS Forge directory. Python 3.10+ is required.
Actual app builds need macOS, full Xcode, and a compatible installed simulator runtime.
Xcode 16 or newer is required to read test-result summaries.

Preview installation into your app:

```sh
python3 forge.py install --app "/path/to/MyApp" --dry-run
python3 forge.py install --app "/path/to/MyApp"
```

This copies only Forge's four skills into the app's `.agents/skills/` directory.
It preserves `AGENTS.md`, unrelated skills, and global settings. An identical installation is a no-op;
a differing existing skill stops installation before any copying. Review updates manually in v0.1.
Do not install skills into repositories you do not trust without reading them.

Open your app in Codex and ask:

> Use $ios-onboard to discover this app's configuration and establish a verification baseline.

The onboarding skill discovers the real project/workspace, shared scheme, and available destination.
You can also create the configuration yourself after inspecting those values:

```sh
python3 forge.py init --app "/path/to/MyApp" \
  --name "MyApp" --project "MyApp.xcodeproj" --scheme "MyApp" \
  --destination "platform=iOS Simulator,id=YOUR_AVAILABLE_SIMULATOR_UUID"
python3 forge.py validate "/path/to/MyApp/.ios-forge/app.json"
python3 forge.py doctor --app "/path/to/MyApp"
```

Replace the sample values; Forge does not choose an arbitrary simulator or scheme.
`doctor` discovers executable prerequisites and a valid profile; it does not certify Xcode health.
See the [profile contract](docs/profile.md) and [example profile](examples/app-profile.json).

## Everyday workflow

1. **`$ios-onboard`** discovers the app's conventions and baseline.
2. **`$ios-plan-feature`** defines acceptance criteria, affected components, and verification.
3. **`$ios-build-feature`** implements authorized work using the app's existing architecture.
4. **`$ios-verify`** gathers build/test evidence and relevant simulator or device observations.

For example:

> Use $ios-plan-feature to plan offline favourites. Preserve this app's architecture and deployment target.

> Use $ios-build-feature to implement the agreed favourites feature, then use $ios-verify to check it.

Planning does not automatically start implementation. Already-authorized implementation does not need
another ceremonial approval. The workflows preserve the user's scope and existing app instructions.

## Collect build and test evidence

```sh
python3 forge.py verify --app "/path/to/MyApp" \
  --output-dir "/path/to/private-forge-evidence" --dry-run
python3 forge.py verify --app "/path/to/MyApp" \
  --output-dir "/path/to/private-forge-evidence"
```

Choose an output directory **outside the app checkout**. Each run gets its own build output,
logs, JSON report, and Xcode test result bundle when produced. A failed check stops later checks;
timeouts terminate the launched process group. Nonzero exit codes make failures usable in CI.
Reports include Xcode version, source/profile fingerprints, actual test counts and destinations,
and bounded failure diagnostics. Tests with no executed cases or unreadable result evidence cannot pass.
Reading test summaries requires Xcode 16 or newer.

`passed` means the configured commands and test-result evidence passed. UI journeys and automated
accessibility audits can run through the app's XCTest UI tests; inspect those tests for actual coverage.
Physical-device behaviour, manual accessibility, and release readiness require their own evidence.
Forge's CLI does not directly drive the simulator UI.
See [verification and evidence handling](docs/verification.md).

## Specialist skills

Forge works without third-party skills. The [candidate registry](upstream/registry.json) identifies
SwiftUI, concurrency, testing, and simulator projects worth evaluating. Nothing is bundled or installed
from these projects in this release. A profile's `specialist_skills` field is advisory.

Before adding a dependency, inspect its instructions/scripts, check its license and compatibility,
and record an exact revision. Load only skills relevant to the task. Preserve existing UIKit, XCTest,
Core Data, toolchain, deployment target, and architecture decisions.

## Development and validation

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_distribution.py
python3 scripts/package_release.py
```

Tests use temporary projects and a fake `xcodebuild` process to exercise the runner, failure paths,
timeouts, argument handling, and installation boundaries. They do **not** demonstrate an app building
in Xcode. CI is configured for Linux/macOS and Python 3.10/3.13; hosted results are available only after
publication. See the [validation record](docs/validation.md) and
[evaluation scenarios](docs/evaluations.md) for real Codex/app pilots.

## Boundaries of this release

- Skills are prompt workflows; code provides deterministic setup and command execution.
- No unattended sweeps, issue filing, PR creation, auto-merge, signing changes, or App Store submission.
- No crash provider, App Store Connect, simulator interaction, or scheduling integration yet.
- No automatic upstream installation/update, uninstall, custom shell commands, archive/export, or test-plan flags.
- Install preflight prevents known conflicts; it is not a transactional updater and concurrent installations are unsupported.
- Evidence retention is manual. Logs and test bundles are private until explicitly reviewed for sharing.
- Simulator validation covers a new Forge Notes app and the existing LaRecette app. Physical-device checks and broader compatibility remain outstanding.

For new projects, follow the [project creation and first-baseline workflow](docs/new-project.md).
Real-app pilot results and remaining validation limits are recorded in [validation](docs/validation.md).

## Publishing and attribution

See [GitHub publishing](docs/publishing.md), [contributing](CONTRIBUTING.md),
[changelog](CHANGELOG.md), and [acknowledgements](ACKNOWLEDGEMENTS.md).
Original iOS Forge material is MIT licensed. Third-party candidate projects retain their own licenses.
