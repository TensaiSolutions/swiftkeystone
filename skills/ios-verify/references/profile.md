# App profile v1

An app stores configuration at `.ios-forge/app.json`, relative to its repository root.
Use `forge.py validate PATH` to check it; the corresponding editor schema lives in
`schemas/app-profile.schema.json`. The standalone CLI validator uses only Python's standard library.

Required fields:

- `schema_version`: integer `1`.
- `name`: app display name for reports.
- `project`: relative `.xcodeproj` or `.xcworkspace` path inside the app root. Parent traversal is rejected; resolved links may not escape the root.
- `scheme`: existing app scheme. Prefer a committed shared scheme for reproducible team/CI use.
- `destination`: an Xcode destination string. Prefer an available simulator UUID to an ambiguous device name. Discover it through the selected Xcode installation. For native macOS, use a discovered `platform=macOS` destination instead; no simulator UUID is required.
- `checks`: a nonempty ordered array of `build` and/or `test`, without duplicates.
- `timeout_seconds`: integer from 1 through 7200, per check.

Optional fields `deployment_target`, `swift_version`, and `architecture` document conventions;
they do not override Xcode settings. `specialist_skills` names independently installed skills;
it never downloads or executes them. Unknown fields are rejected so misspellings cannot silently
disable a check. Profiles contain no credentials or custom shell commands.

The CLI takes `--app` as the app's repository root; profile paths are relative to that root,
not the profile file. Onboarding must inspect the project rather than blindly accept the example.
An `init` profile is a starting configuration, not proof that the project or scheme exists.

The default is build followed by test. Existing XCTest and Swift Testing targets are both supported
through the scheme. UI tests run only if that scheme's test configuration includes them. Custom test
plans, alternate build configurations, and signing/archive options are not CLI features in this preview.
Use the app's existing tooling when those are required and record the evidence separately.

A default test plan selected by the existing shared scheme is honored by Xcode without adding a
profile field. The CLI does not override that selection with a `-testPlan` option. Confirm that every
intended test target exists and is enabled in that plan; an orphaned scheme reference adds no coverage.

If no test target or test action exists, record that gap before verification. After explicit review,
`"checks": ["build"]` establishes a compilation-only baseline. Never silently remove a failing test
check to get a green result. `init` does not inspect test availability and keeps its build/test default.


## Optional baseline expectations (v0.4.0 development)

Existing schema-version-1 profiles remain valid without changes. The v0.4.0 helper additionally accepts:

```json
"baseline_expectations": {
  "required_test_targets": ["AppTests", "AppUITests"],
  "minimum_executed_tests": 12
}
```

Either field can be used alone. The object must be nonempty, target names must be unique and nonempty,
and the minimum must be a positive integer. Expectations require a `test` check; build-only profiles
cannot declare them. Choose the contract from reviewed coverage, not an arbitrary example or a failing
run you want to silence. The published v0.3.0 helper does not understand this new optional field.

`audit` requires each named native target to resolve uniquely and be enabled in the selected scheme's
default plan/test action. `verify` separately requires executed cases for each exact Xcode result-bundle
target name, and at least the declared number of passed plus failed cases across the test run. Skipped
cases do not count. An expected-failure case is included in Xcode's executed counts; this is not proof
of a successful acceptance criterion. Missing, unreadable, inconsistent or unsupported target evidence
fails the declared contract. When no targets are declared, only the summary is needed for a minimum.
The target reader counts test-case nodes rather than parameter iterations and requires its executed
count to agree with the summary; unsupported result layouts require review rather than a guessed pass.

A native command can exit zero while verification exits 1 because coverage expectations were not met.
The private report stores the contract, actual target counts and assessment. PR summaries show numeric
expectation outcomes without echoing private target names. Passing expectations do not certify behavior.
Older reports without expectations remain readable; comparisons flag contract changes for review.
Use a separate explicit profile/run for separate app, UI or package suites. Preserve originals before
reconciliation; the helper never rewrites a profile or silently learns a lower minimum.


### Adoption checklist

1. Verify the intended distribution checksum and helper version. For an upgrade, preserve installed
   originals and review staged skill differences; never copy over differing installed skills or profiles.
2. Inspect the selected scheme/default plan and actual Xcode target evidence. Record which app, UI and
   package suites belong in this profile and why; a minimum is a floor, not a coverage percentage.
3. Preserve the existing profile and explicitly reconcile the optional contract with reviewed targets and
   counts. Run `validate`, `audit`, and `verify --dry-run`; inspect findings before the native baseline.
4. Run `verify` outside the checkout. Inspect the native exit code, executed/skipped counts and baseline
   assessment separately. Prove a deliberate missing-suite or reduced-count case is refused in an isolated
   copy, restore source/profile inputs, and retain the restored baseline.
5. Run `compare` and `summary` against the baseline. Review count decreases and contract changes even
   when native commands passed. Keep reports private and state unverified behavior in the PR.
