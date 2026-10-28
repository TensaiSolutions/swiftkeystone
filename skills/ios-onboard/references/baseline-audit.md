# Static baseline audit

Use `audit` before changing an existing app, especially when earlier pilot evidence is available:

```sh
python3 forge.py audit --app "/path/to/App" --output "/path/to/private/audit.json"
python3 forge.py audit --app "/path/to/App" \
  --reference-report "/path/to/private/earlier/report.json"
```

The existing profile selects the project/workspace and scheme. The dependency-free audit parses local
Xcode project targets, shared or user-local schemes, workspace project references, and the default
test plan. It identifies missing/ambiguous schemes, unresolved or disabled test references, selection
filters, and test actions without effective targets. Default-plan selection takes precedence over legacy
scheme Testables. Unsupported/external references or unreadable syntax require manual inspection.
It does not follow external projects or search dependency checkouts.

The audit records HEAD, dirty state, and locally cached upstream ahead/behind information. It never
fetches a remote. Cached tracking data cannot establish current GitHub state. An optional earlier
verification report is compared with the current Git-visible source fingerprint and profile hash;
a different commit with identical contents is distinguished from changed inputs. Matching inputs do
not expand the old run's coverage. Ignored files and symlink targets are outside the source fingerprint.

Exit 0 means the static inspection found no blocking configuration errors; warnings still need review.
Exit 1 means static errors were found. Exit 2 means invalid input or an operational error. `inspected`
is not a passing native baseline: the command never runs Xcode, resolves dependencies, authorizes
plugins, or certifies a destination. Establish native build/test evidence separately with `verify`.

Keep baseline repairs separate from feature implementation. Record the original failure before fixing
it, preserve deployment/signing/architecture choices, then rerun the reconciled baseline. A passing
unit suite does not establish UI coverage merely because a UI target appears in the project.

Output files are private, must be outside both the app and helper distribution, and are never replaced.


With v0.4.0 development profiles, `baseline_expectations.required_test_targets` requires a unique,
enabled native target by its resolved project name in the effective test selection. Missing/disabled
requirements are errors even if another suite is enabled. Static wiring cannot prove execution or the
minimum count; those expectations are separately enforced against Xcode evidence by `verify`.
