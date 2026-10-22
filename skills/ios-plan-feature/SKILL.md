---
name: ios-plan-feature
description: Plan an iOS or macOS app feature with observable acceptance criteria, affected screens and data, compatibility constraints, and a proportionate verification plan.
---

Read project instructions, the app profile when present, and the code that owns the affected journey. If the app has not been onboarded, discover the minimum configuration needed or use `$ios-onboard` when available.

Turn the request into a bounded implementation plan covering:

- The user outcome and acceptance criteria, including relevant loading, empty, error, offline, and permission states.
- Affected views, navigation, state ownership, persistence, and integrations. State whether data migration or backward compatibility is involved.
- The app's deployment target and toolchain constraints. Preserve architecture unless the request calls for changing it.
- Tests tied to behaviour: unit/integration tests for logic, UI tests, native Mac journeys, or simulator journeys for interaction, and device checks where simulator evidence is insufficient.
- A sequence of small implementation steps, the specialist skills needed, and decisions that cannot be inferred from the repository.

Use [references/feature-plan.md](references/feature-plan.md) when a saved plan would help sustained work. Extend existing planning conventions instead of adding parallel documents. Separate established facts from assumptions. For optional capabilities, propose scope explicitly rather than silently expanding the feature. Planning alone does not authorize implementation, external writes, purchases, or release actions; existing user authorization still applies.
