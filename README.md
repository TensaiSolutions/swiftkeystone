# SwiftKeystone

A reusable development workflow framework for Swift apps with Codex: onboard an app, plan a feature,
implement a bounded change, and collect honest verification evidence.

**v0.3.0 — Adoption and Evidence Preview.** Four installable skills and a dependency-free Python helper.
The latest published release is [v0.3.0](https://github.com/TensaiSolutions/swiftkeystone/releases/tag/v0.3.0).
It includes baseline audit, evidence comparison/PR-summary drafts, and safe update staging.
No account, service, API key, or global configuration change is required by SwiftKeystone itself.
You use it within your existing Codex environment.

The name reflects the goal: connect planning, implementation, and verification into a dependable
pattern for Swift app development. This preview covers iOS and native macOS workflows;
see the validation record for the actual environments, pilot corrections, and results.
Support and validation for additional Apple platforms remain future work.

The project was previously called iOS Forge. For compatibility, the framework keeps the `forge.py` entry point,
`.ios-forge/app.json` profile, and `$ios-*` skill names. Existing profiles need no migration.
Updated skill bundles still require manual review when they differ from an installed copy;
the installer will not overwrite them.

The published archive is `swiftkeystone-0.3.0.zip`, containing a `swiftkeystone-0.3.0/` directory.

## Start here

Download `swiftkeystone-0.3.0.zip` and `swiftkeystone-0.3.0.zip.sha256` from the
[v0.3.0 release](https://github.com/TensaiSolutions/swiftkeystone/releases/tag/v0.3.0).
Use those named assets, rather than GitHub's automatically generated source archives, for these steps.
In the download directory on macOS, verify and extract:

```sh
shasum -a 256 -c swiftkeystone-0.3.0.zip.sha256
unzip swiftkeystone-0.3.0.zip
cd swiftkeystone-0.3.0
```

Stop if the checksum does not match. Keep the extracted directory in a stable location.
Cloning this repository is an alternative; it gives you the current branch rather than necessarily v0.3.0.
Commands below run from that SwiftKeystone directory. Python 3.10+ is required.
Check `python3 --version` before setup. macOS `/usr/bin/python3` may be older; select an
already installed Python 3.10+ interpreter and use that same executable for every command below.
If none is installed, stop and arrange installation explicitly. SwiftKeystone does not install Python
or change your system interpreter. The original v0.3.0 helper does not enforce this minimum at startup;
the development helper now rejects older interpreters before dispatching commands.
App builds need macOS and full Xcode. iOS simulator runs also need a compatible installed runtime.
Xcode 16 or newer is required to read test-result summaries.

Preview installation into your app:

```sh
python3 forge.py install --app "/path/to/MyApp" --dry-run
python3 forge.py install --app "/path/to/MyApp"
```

This copies only SwiftKeystone's four skills into the app's `.agents/skills/` directory.
It preserves `AGENTS.md`, unrelated skills, and global settings. An identical installation is a no-op;
a differing existing skill stops installation before any copying. v0.3.0 includes reviewed
[three-way update staging](docs/skill-updates.md); activation remains explicit and preserves originals.
Do not install skills into repositories you do not trust without reading them.

Open your app in Codex and ask:

> Use $ios-onboard to discover this app's configuration and establish a verification baseline. The SwiftKeystone helper is at /absolute/path/to/swiftkeystone-0.3.0/forge.py.

Replace that helper path with the location you extracted. Installation copies skills, not the Python
helper, into the app. If a skill is not discovered, reopen the app's Codex chat and confirm its
`.agents/skills/ios-onboard/SKILL.md` exists; you can also ask Codex to read that file explicitly.

The onboarding skill discovers the real project/workspace, scheme, and available destination.
For reproducible team/CI use, share the intended scheme in Xcode and commit its scheme file;
locally generated schemes can work without being portable to another checkout.
You can also create the configuration yourself after inspecting those values:

```sh
python3 forge.py init --app "/path/to/MyApp" \
  --name "MyApp" --project "MyApp.xcodeproj" --scheme "MyApp" \
  --destination "platform=iOS Simulator,id=YOUR_AVAILABLE_SIMULATOR_UUID"
python3 forge.py validate "/path/to/MyApp/.ios-forge/app.json"
python3 forge.py doctor --app "/path/to/MyApp"
```

Replace the sample values; SwiftKeystone does not choose an arbitrary simulator or scheme.
`doctor` discovers executable prerequisites and a valid profile; it does not certify Xcode health.
See the [profile contract](docs/profile.md) and [example profile](examples/app-profile.json).

### Apps without tests

`init` starts with `"checks": ["build", "test"]`. Inspect the scheme's test action before running it.
If the app has no test target, record that coverage gap. For an explicitly build-only baseline, edit
`.ios-forge/app.json` to use `"checks": ["build"]`, validate it, and then run verification.
A passing build-only baseline proves compilation, not tested behavior. Do not remove existing tests
from a profile to hide failures. Add or restore tests as a separate, scoped task.

The profile contains a machine-specific destination. Review your app's ignore policy before committing
it; the installer does not edit `.gitignore`. Installed skills may be committed for the team or kept local.

### Permissions and baseline scope

Codex may require normal approval to write project-local `.agents/skills/` or access Xcode and
CoreSimulator beyond its sandbox. If installation reports `Operation not permitted`, use the normal
approval flow for that scoped write. Simulator discovery can exit successfully while its output reports
CoreSimulator connection or permission errors and lists only placeholder destinations. Treat that output
as blocked discovery; retry with normal approved Xcode access before choosing an actual available device.
Do not disable sandboxing, plugin validation, or authentication, or change global settings to get past it.

Compare the selected scheme's enabled tests with the app's documented CI command. This preview cannot
express `-only-testing`, custom configurations, or arbitrary build-setting overrides. A full-scheme local
baseline can therefore include tests that CI excludes; record that difference instead of claiming CI parity
or silently dropping tests. A baseline failure is a finding, not permission to rewrite the app or tests.
The `summary` command can successfully generate text for a failed run; inspect its reported status and
counts rather than treating summary exit code 0 as a passing verification.

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
SwiftKeystone's CLI does not directly drive the simulator UI.
See [verification and evidence handling](docs/verification.md).

## Native macOS projects

The four workflows also cover native macOS projects; the `ios-*` skill names are
compatibility aliases. Use an actual Mac scheme and a discovered macOS destination, rather than an
iOS simulator. See [macOS verification](docs/macos.md) and the
[example Mac profile](examples/macos-app-profile.json). Native macOS guidance and the example
are included starting with v0.2.0; the original v0.1.0 assets remain unchanged.

## Baseline audit, evidence comparison, and updates (v0.3.0)

- [`audit`](docs/baseline-audit.md) inspects local Xcode test wiring and earlier evidence against current source/profile hashes, without building or fetching remotes.
- [`compare` and `summary`](docs/evidence-comparison.md) compare completed reports, qualify restoration checks, and draft bounded PR evidence text without private diagnostics.
- [`update`](docs/skill-updates.md) stages a three-way skill candidate, backup, and conflict inventory; it never replaces installed skills or profiles.

These commands are included in the published v0.3.0 helper. Use the verified download above;
installation copies skills into the app, while these commands run from the extracted distribution.
A static audit, staged update, or generated summary does not establish native behavior or grant merge approval.

## Specialist skills

SwiftKeystone works without third-party skills. The [candidate registry](upstream/registry.json) identifies
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
in Xcode. CI is configured for Linux/macOS and Python 3.10/3.13; the [hosted checks](https://github.com/TensaiSolutions/swiftkeystone/actions) report toolkit results. See the [validation record](docs/validation.md) and
[evaluation scenarios](docs/evaluations.md) for real Codex/app pilots.

## Boundaries of this release

- Skills are prompt workflows; code provides deterministic setup and command execution.
- No unattended sweeps, issue filing, PR creation, auto-merge, signing changes, or App Store submission.
- No crash provider, App Store Connect, simulator interaction, or scheduling integration yet.
- No automatic upstream installation, in-place skill replacement, uninstall, custom shell commands, archive/export, or test-plan flags.
- Install preflight prevents known conflicts; it is not a transactional updater and concurrent installations are unsupported.
- Evidence retention is manual. Logs and test bundles are private until explicitly reviewed for sharing.
- Validation covers Forge Notes and LaRecette on iOS simulators, plus a native CotEditor macOS pilot. The Mac pilot passed app tests and four XCTest UI cases after explicit local test corrections, including document save/reopen. The earlier automation-startup timeout did not recur; its cause and reboot persistence remain unproven. iPhone/iPad hardware and broader compatibility remain outstanding.

For new projects, follow the [project creation and first-baseline workflow](docs/new-project.md).
Real-app pilot results and remaining validation limits are recorded in [validation](docs/validation.md).

## Publishing and attribution

See [GitHub publishing](docs/publishing.md), [contributing](CONTRIBUTING.md),
[changelog](CHANGELOG.md), and [acknowledgements](ACKNOWLEDGEMENTS.md).
Original SwiftKeystone material is MIT licensed. Third-party candidate projects retain their own licenses.
