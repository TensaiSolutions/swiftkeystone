---
name: ios-onboard
description: Onboard a new or existing iOS app into iOS Forge by discovering its Xcode configuration, conventions, and verification baseline.
---

Establish how this app is built and verified before changing its code.

1. Read applicable `AGENTS.md` instructions and inspect the repository's current state. Distinguish an existing app from a request to create one. For a new app, establish the product's first user journey, platform requirements, and persistence needs before scaffolding.
   For project generation and first-baseline decisions, read [references/new-project.md](references/new-project.md). Use an existing generator or Xcode; do not silently install one.
2. Discover `.xcodeproj` / `.xcworkspace`, shared schemes, package dependencies, test targets/plans, deployment target, Swift language mode, architecture, and CI configuration. Exclude dependency checkouts and generated build output. Prefer existing workspace and CI conventions. If several app schemes are plausible, present the concrete choices and resolve the ambiguity before running expensive checks.
3. Use the selected Xcode toolchain to inspect schemes and available simulator destinations. Record unavailable tools as gaps; do not guess a simulator UUID or raise the deployment target to match a skill's preferences.
4. Create or reconcile `.ios-forge/app.json` using the profile contract in [references/profile.md](references/profile.md). Preserve an existing profile; explain material changes. If the Forge CLI is available, its `init` command creates a profile without replacing one. Specialist skill names are routing hints, not proof that a skill is installed.
5. Identify appropriate baseline checks. Invoke `$ios-verify` if available, or follow existing build/test commands and preserve their evidence. Existing failures are baseline findings, not permission for unrelated repairs.

Deliver the selected project/workspace, scheme, destination, relevant versions and conventions, the baseline outcome, and unresolved choices. Keep raw logs and personal paths out of public issues and the shared toolkit. Do not overwrite `AGENTS.md`, install third-party skills, or change signing settings as a side effect of onboarding.
