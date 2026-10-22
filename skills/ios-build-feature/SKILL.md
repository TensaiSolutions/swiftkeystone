---
name: ios-build-feature
description: Implement an authorized, bounded iOS feature using the app's conventions, relevant installed Swift skills, and behaviour-based verification.
---

Read the requested outcome, acceptance criteria or existing plan, app profile, and applicable project instructions. If the request leaves a material product decision unresolved, progress on independent work and resolve that decision before dependent implementation. Do not require a new approval when implementation is already authorized.

Inspect existing state ownership and feature boundaries. Select only relevant installed specialist skills. Check their advice against the app's actual deployment target, toolchain, architecture, and the user's request. If a skill is unavailable, report that limitation and use supported tools and authoritative references; do not silently install dependencies or claim the skill was used.

Implement in a branch/worktree when isolation is needed, preserving unrelated user edits. Use separate build output and avoid competing jobs on a shared simulator. Preserve existing UIKit, XCTest, persistence, and architecture choices unless the requested change requires otherwise.

Add meaningful tests for changed behaviour. Cover relevant navigation and failure states. For a bug fix, reproduce the defect where practical and demonstrate the regression test detects it. Avoid broad modernization and tests that merely repeat the implementation.

Use `$ios-verify` when available, otherwise run the repository's established verification. A build does not establish acceptance of a user journey. Deliver what changed, which criteria have evidence, what remains unverified, and any material limitations. Creating/pushing PRs follows the user's authorization; this skill does not grant publication or release permission.
