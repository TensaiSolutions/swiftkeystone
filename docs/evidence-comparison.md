# Evidence comparison and PR summaries

Commands accept completed SwiftKeystone reports, including v0.2.0 reports. They read JSON, not log
instructions, and never execute recorded command arguments or mutate app code.

```sh
python3 forge.py compare "/private/before/report.json" "/private/after/report.json"
python3 forge.py compare "/private/green/report.json" "/private/red/report.json" \
  --restored "/private/restored/report.json" --output "/private/comparison.json"
python3 forge.py summary "/private/restored/report.json" \
  --baseline "/private/green/report.json" --regression "/private/red/report.json" \
  --output "/private/pr-verification.md"
```

Comparison validates report outcomes and test counts, checks scheme/destination/project and Xcode
context, and identifies source/profile/check-selection changes. v0.3.0 verification reports include an
explicit configuration snapshot. Older context is inferred from argument arrays: only a project basename
is available, so exact project-path equivalence remains unverified. Missing or incompatible provenance
needs review. There is no remote fetch or automatic check execution.

A supported detected-failure/restoration cycle requires a changed source fingerprint, actual test
failures between passing runs, comparable test context, and restoration of the original source/profile
hashes and check selection. Changing a profile to skip tests cannot establish restoration. This is a
comparison of supplied reports, not independent execution, an authenticity attestation, or proof that
a particular mutation caused the failure. Record the intentional mutation and inspect the named
failures separately. Never let this command create or restore a mutation for you.

`summary` drafts Markdown with configured outcomes, test counts, a well-formed recorded commit hash, dirty
state, and comparison limits. It deliberately omits app names, absolute paths, argv, device identifiers,
raw failure text, and diagnostics. It does not copy arbitrary `not_verified` strings from reports. Review
acceptance criteria and privacy before posting; it never creates a PR, comment, approval, or merge.
A report alone cannot prove journeys, hosted CI, physical devices, manual accessibility, or distribution
readiness. Build-only and unreadable test coverage remain explicit.

`compare` exits 1 for incomparable evidence or an unverified requested restoration. `summary` exits 1
when its optional comparison needs review or a requested regression cycle is not established. A plain
summary can successfully describe a failed run: its exit 0 means text generation, not passing tests.
Invalid/inconsistent input exits 2. Output files are exclusive/private and never replace existing files.


The v0.4.0 helper reports signed changes in total, executed, passed, failed and skipped
counts. Executed means passed plus failed; skipped cases do not compensate for decreased execution.
A decrease sets comparison status to `needs_review` (exit 1), even when both native runs passed.
Increases are visible but do not prove improved coverage. Missing readable counts produce an unknown
delta. Changed baseline contracts also require review; older reports have no declared contract.
Comparisons still consume supplied reports and cannot authenticate their contents. Passing reports
that contradict their recorded baseline contract are rejected. Summary text reports numeric contract
outcomes and count changes without copying arbitrary target names or diagnostics.
