# Verification evidence

Every executed CLI run gets a unique directory outside the checkout with:

- `report.json`: SwiftKeystone version, UTC timestamps, app name, source commit, dirty state, Git-visible source
  fingerprint, profile hash, Xcode version, commands, per-check outcomes, test counts and destinations
  from Xcode's result bundle, and explicit unverified categories.
- `build.log` and/or `test.log`: full command output for diagnosis.
- `Tests.xcresult` when Xcode produces a test result bundle.
- `DerivedData/`: build output isolated from other runs.

Checks run in configured order. After a failure, timeout, or interrupted check, later checks are `not_run`.
Timeouts and keyboard interrupts terminate the launched process group; interrupted checks fail the run.
The CLI returns 0 for passing configured checks, 1 for failed/timed-out checks, and 2 for configuration
or environment errors. A dry run returns 0 without running Xcode or creating evidence.
Test checks require a readable result summary with executed tests and a passing result. A zero-test,
all-skipped, unreadable, missing, or failing summary fails verification even if the command returned 0.
The summary reader uses Xcode 16+ `xcresulttool get test-results summary`.
Failures include a bounded diagnostic excerpt; when no error line exists, the runner uses Xcode's
failed-build-step summary if available; the full private log remains the authority.
A force-killed parent can leave a `running` report; treat it as incomplete, never as passed.

The source fingerprint covers Git-visible file paths and contents, including untracked files and missing
tracked files. It does not dereference symbolic links or cover ignored inputs, submodule contents,
external dependencies, environment variables, or every possible build input. It supplements commit/dirty
state rather than certifying a hermetic build. The app profile has its own hash because it may be ignored.

Evidence is private operational data. Directories created for individual runs use private permissions,
but parent directory policies and user sharing choices still apply. Logs and result bundles may include
personal paths, application data, signing information, or secrets emitted by build scripts.
Do not upload them automatically. Retention and deletion are manual in v0.1.

An agent's final report should state:

1. Changed behaviour and acceptance criteria covered.
2. Configured command outcomes, source revision/dirty state, and private evidence paths.
3. Simulator journeys actually exercised, including runtime/device and observed outcomes.
4. Device, accessibility, performance, or release checks still outstanding.

No result field certifies App Store readiness. A passing build/test run remains useful when some
manual checks are outstanding, as long as those limits are explicit.

For a build-only profile, the console explicitly states that automated tests were not configured or run,
and `report.json` lists automated tests under `not_verified`. A passing status retains its meaning:
only the selected checks passed. Existing v0.1.0 reports do not have this additional build-only reminder.
