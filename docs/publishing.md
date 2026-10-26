# Publish SwiftKeystone on GitHub

Repository: [TensaiSolutions/swiftkeystone](https://github.com/TensaiSolutions/swiftkeystone), public.
The v0.1.0, v0.2.0, and **v0.3.0 — Adoption and Evidence Preview** releases are published.
Keep their tags, ZIPs, and checksums unchanged. The checklist below records the v0.3.0 procedure;
substitute the intended version when preparing a future release.

Before merging release preparation, make the README download, extraction, helper-path, and command
availability guidance match the intended version. Run the distribution checks against the extracted
archive as well as the source. Recheck those instructions after publication; do not leave the new release
described as unpublished. Published archives are immutable: documentation corrections ship in a new
release, with a correction linked from the affected release notes.

The current source helper is the **v0.4.0 development candidate**. `forge.VERSION` selects the candidate
archive/report version; `forge.PUBLISHED_VERSION` keeps the documented public adoption instructions
on v0.3.0 until a new release is prepared. Review both explicitly during release preparation. New optional
baseline fields require the v0.4.0 helper and must not be added to profiles still used by v0.3.0.

The package scripts create local artifacts only. Preparing a release does not publish it or create a tag.

1. Review the version in `forge.py`, README download paths, changelog, validation record, and preview limits.
2. Run `python3 -m unittest discover -s tests -v`, `python3 scripts/check_distribution.py`, and
   `git diff --check`. Build with `python3 scripts/package_release.py`.
3. Verify `outputs/swiftkeystone-0.3.0.zip.sha256`, inspect the archive allowlist, and test extraction,
   installation, profile setup, and dry-run verification from outside the source checkout. Retain
   private evidence separately. An extracted-package check is distinct from native Xcode app tests.
4. Merge the reviewed release-preparation PR only after current-head CI passes. The administrator
   exception can waive the second-person approval for a solo maintainer; required CI and conversation
   resolution remain enforced by the separate non-bypassable ruleset.
5. From a clean checkout of the exact merged commit, rerun the portable/distribution checks and rebuild
   the artifacts. Record that commit and SHA-256. Do not tag an unmerged candidate or publish its assets.
6. When publication is explicitly authorized, tag that commit `v0.3.0` and create a prerelease titled
   "SwiftKeystone 0.3.0 — Adoption and Evidence Preview". Use the reviewed release notes and attach
   only the generated ZIP and matching checksum. Read back the release, tag, and downloaded asset hash.

Do not upload app source, pilot patches, profiles, raw logs, result bundles, fixture data, or machine
identifiers as toolkit release assets. Operational evidence remains private unless separately reviewed
and explicitly authorized for sharing. Preserve physical-device, broader-platform, reboot/authorization,
manual accessibility, signing, and notarization limitations. Portable CI does not compile the pilot apps.

## Updating from v0.2.0

Use the [safe update staging workflow](skill-updates.md). The updater produces a candidate, backup,
and conflict manifest without changing the app. Review and explicitly archive originals before
activation into vacant destinations. Preserve local customizations and the existing profile, audit the
configuration, and verify with the extracted new helper. Compare native evidence with the old baseline;
do not equate successful staging or portable tests with app behavior.
