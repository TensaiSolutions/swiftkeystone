# Publish SwiftKeystone on GitHub

Chosen repository name: `swiftkeystone`. Intended owner: `TensaiSolutions`.
Availability checks found no public repository at that address; creation is still required.
Suggested description: "A workflow framework for Swift apps with Codex: onboard, plan, build, and verify."
Suggested topics: `ios`, `swift`, `swiftui`, `codex`, `agent-skills`, `developer-tools`.

The working folder is the repository root. Review README, MIT copyright attribution, package contents,
and the foundation-preview limitations before publishing. No remote or GitHub release is created by
the package scripts. Choose the destination account/organisation and visibility explicitly.

1. Run the test suite and distribution checks described in README.
2. Build the archive with `python3 scripts/package_release.py`; inspect `outputs/swiftkeystone-0.1.0.zip`
   and its `.zip.sha256` file. The archive contains a `swiftkeystone-0.1.0/` root directory.
3. Create a GitHub repository using the chosen owner/name and visibility. Push the local `main` branch.
4. Let package CI run. Its Linux/macOS jobs test the helper; they do not compile an iOS app.
5. After CI passes, tag the reviewed commit `v0.1.0` and create a prerelease titled
   "SwiftKeystone 0.1.0 — Foundation Preview". Attach the generated ZIP and SHA-256 checksum.
6. Use the 0.1.0 changelog section as release notes. Attach the companion Forge Notes source archive and
   sanitised validation summary when publishing the pilot. Review any existing-app source or patch
   separately before sharing it. Retain the physical-device, broader-platform, and hosted-CI
   limitations rather than describing the preview as universally validated.

Do not mark this release as production-proven until the pilot scenarios have actual recorded results.
Building an archive is not proof it has been published or that hosted CI has run.
