# App profile v1

An app stores configuration at `.ios-forge/app.json`, relative to its repository root.
Use `forge.py validate PATH` to check it; the corresponding editor schema lives in
`schemas/app-profile.schema.json`. The standalone CLI validator uses only Python's standard library.

Required fields:

- `schema_version`: integer `1`.
- `name`: app display name for reports.
- `project`: relative `.xcodeproj` or `.xcworkspace` path inside the app root. Parent traversal is rejected; resolved links may not escape the root.
- `scheme`: existing shared app scheme.
- `destination`: an Xcode destination string. Prefer an available simulator UUID to an ambiguous device name. Discover it through the selected Xcode installation.
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
plans, alternate build configurations, and signing/archive options are not CLI features in v0.1.
Use the app's existing tooling when those are required and record the evidence separately.
