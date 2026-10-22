# Workflow evaluation scenarios

These are repeatable acceptance scenarios for real Codex pilots. Completed Forge Notes results and
remaining limits are recorded in `docs/validation.md`; that record distinguishes actual execution from
read-only skill evaluation. Portable tests cover the helper's mechanics. Use a disposable app checkout.

## Existing app onboarding

Input: an app with two schemes, existing `AGENTS.md`, and an uncommitted user change.
Request: "Use $ios-onboard to establish this app's baseline."
Expected: inspect conventions, resolve scheme ambiguity, preserve the user change and instructions,
select a real destination, record existing failures, and avoid installing specialist dependencies.

## Feature planning

Input: an existing app with local persistence and a fixed deployment target.
Request: "Plan offline favourites, including how we'll know it works."
Expected: measurable criteria, offline and empty/error cases, existing state ownership, appropriate
tests, and no unrequested implementation or deployment-target upgrade.

## Bounded implementation

Input: agreed favourites plan and authorization to implement it.
Request: "Build the agreed feature and verify it."
Expected: relevant code changes and behaviour tests, no unrelated modernization, and evidence for
the acceptance criteria. An unavailable specialist skill is disclosed rather than silently installed.

## Incomplete verification

Input: a failing test or unavailable simulator, plus a device-dependent capability.
Request: "Verify this change."
Expected: precise failure/blocker, later checks marked not run, no false pass, and physical-device
behaviour explicitly unverified. Missing tools do not trigger an unbounded retry loop.

## Reuse and release acceptance

Complete one feature and one regression fix in app A. Onboard app B using configuration alone.
Record app/source revision, toolchain, commands, outcomes, workflow mistakes and corrective changes
in private pilot notes. Share only sanitised conclusions. Evaluate existing XCTest as well as Swift
Testing when available; actual targets remain the authority.
