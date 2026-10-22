# Verification evidence

Every executed CLI run gets a unique directory outside the checkout with:

- `report.json`: Forge version, UTC timestamps, app name, source commit, dirty state, profile hash,
  commands, per-check outcomes, and explicit unverified categories.
- `build.log` and/or `test.log`: full command output for diagnosis.
- `Tests.xcresult` when Xcode produces a test result bundle.
- `DerivedData/`: build output isolated from other runs.

Checks run in configured order. After a failure, timeout, or interrupted check, later checks are `not_run`.
Timeouts and keyboard interrupts terminate the launched process group; interrupted checks fail the run.
The CLI returns 0 for passing configured checks, 1 for failed/timed-out checks, and 2 for configuration
or environment errors. A dry run returns 0 without running Xcode or creating evidence.
An interrupted process can leave a `running` report; treat it as incomplete, never as passed.

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
