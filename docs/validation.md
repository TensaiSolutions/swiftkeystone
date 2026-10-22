# Foundation preview validation

Local validation on 2026-10-22 used Python 3.12.3 on macOS 26.6.2 (Apple silicon).

- 14 automated tests passed, covering profile creation/validation, file preservation, install conflict
  preflight, symlink boundaries, dry runs, command argument handling, successful/failed/timed-out child
  processes, stopped checks, evidence permissions, and reproducible archive extraction/installation.
- Distribution checks passed for four self-contained skill bundles, example configuration, schema
  syntax, candidate registry policy, local reference links, and bundled documentation consistency.
- Skill frontmatter and UI metadata were parsed as YAML with the system Ruby YAML parser.
  The Skill Creator's Python validator could not run because its PyYAML dependency was unavailable.

These checks used a fake `xcodebuild` executable. No real iOS project was compiled, no simulator
journey was exercised, no third-party skill was executed, and no App Store operation occurred.
The GitHub Actions matrix is configured but has not run on hosted infrastructure before publication.
Real Codex/app evaluation scenarios in `docs/evaluations.md` remain pending.

Re-run the checks from README after changes. This file records the initial foundation validation;
it is not a claim about arbitrary app compatibility or future revisions.
