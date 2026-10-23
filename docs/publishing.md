# Publish SwiftKeystone on GitHub

Repository: [TensaiSolutions/swiftkeystone](https://github.com/TensaiSolutions/swiftkeystone), public.
The v0.1.0 foundation preview is already published. Keep its tag, ZIP, and checksum unchanged.
The next prepared version is **v0.2.0 — iOS and macOS Foundation Preview**, still a prerelease.

The package scripts create local artifacts only. Preparing a release does not publish it or create a tag.

1. Review the version in `forge.py`, README download paths, changelog, validation record, and preview limits.
2. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/check_distribution.py`, and
   `git diff --check`. Build with `python3 scripts/package_release.py`.
3. Verify `outputs/swiftkeystone-0.2.0.zip.sha256`, inspect the archive allowlist, and test extraction,
   installation, profile setup, and dry-run verification from outside the source checkout. Retain
   private evidence separately. An extracted-package check is distinct from native Xcode app tests.
4. Merge the reviewed release-preparation PR only after current-head CI passes. The administrator
   exception can waive the second-person approval for a solo maintainer; required CI and conversation
   resolution remain enforced by the separate non-bypassable ruleset.
5. From a clean checkout of the exact merged commit, rerun the portable/distribution checks and rebuild
   the artifacts. Record that commit and SHA-256. Do not tag an unmerged candidate or publish its assets.
6. When publication is explicitly authorized, tag that commit `v0.2.0` and create a prerelease titled
   "SwiftKeystone 0.2.0 — iOS and macOS Foundation Preview". Use the reviewed release notes and attach
   only the generated ZIP and matching checksum. Read back the release, tag, and downloaded asset hash.

Do not upload app source, pilot patches, profiles, raw logs, result bundles, fixture data, or machine
identifiers as toolkit release assets. Operational evidence remains private unless separately reviewed
and explicitly authorized for sharing. Preserve physical-device, broader-platform, reboot/authorization,
manual accessibility, signing, and notarization limitations. Portable CI does not compile the pilot apps.

## Updating from v0.1.0

Extract v0.2.0 into a separate directory and point Codex at that helper. Profile paths and the four
`ios-*` skill names remain compatible. Preview installation first. Identical installed files are a no-op;
a differing SwiftKeystone skill stops the installer before any copying. There is no automatic upgrade.
Review and back up the existing skill directories, including local customizations, then explicitly
reconcile the new bundle. Do not delete or overwrite differing skills or profiles implicitly.
