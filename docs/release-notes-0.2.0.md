# SwiftKeystone 0.2.0 — iOS and macOS Foundation Preview

SwiftKeystone now includes native macOS workflow guidance alongside its iOS foundation workflows.
This remains a preview, with four installable Codex skills and a dependency-free Python helper.

## Changes since v0.1.0

- Native macOS destination guidance, a Mac profile example, and self-contained skill references for
  local signing, separate UI schemes, document persistence journeys, and automation troubleshooting.
- Better Xcode failure diagnostics when the log identifies a failed build step without a useful error line.
- Clearer download/checksum, helper-location, shared-scheme, and no-test-target adoption instructions.
- Explicit console and JSON reminders that a build-only profile has no automated-test coverage.

## Validation

The toolkit passes 23 portable tests, distribution checks, and reproducible archive extraction/installation
checks. Hosted package CI covers Linux/macOS and Python 3.10/3.13; those jobs do not build pilot apps.

Separate native pilot evidence covers iOS simulator journeys and a macOS app build, 112 app tests,
a detected-and-restored serialization regression, and four XCTest UI cases including document
open/edit/save/disk verification/terminate/reopen. Local pilot setup and test corrections are documented
in the [validation record](validation.md); the upstream macOS suite did not pass unchanged.

The earlier macOS UI-automation startup timeout did not recur. Its cause and behavior after reboot
remain unproven. Physical iPhone/iPad devices, broader hardware/OS compatibility, manual VoiceOver,
distribution signing, notarization, and App Store submission are not established by these results.

## Install or update

Download `swiftkeystone-0.2.0.zip` and its matching `.zip.sha256` asset. Verify the checksum, extract,
and follow the README. Keep the extracted helper at a stable path.

Existing `forge.py` commands, `.ios-forge/app.json` profiles, and `$ios-*` aliases remain compatible.
There is no automatic skill upgrade: preview installation, back up and review differing installed
skills, and explicitly reconcile them. The installer refuses to overwrite customizations or profiles.
Third-party candidate skills are not bundled or installed automatically.

Only the toolkit ZIP and checksum belong in this release. App-specific evidence remains private.
The original v0.1.0 release assets are unchanged.
