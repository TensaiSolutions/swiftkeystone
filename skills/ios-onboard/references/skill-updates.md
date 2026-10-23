# Safe skill update staging

`install` remains conflict-safe: it does not overwrite differing installed skills. `update` adds a
three-way review stage, comparing an explicitly supplied previous distribution, installed files, and
this helper's incoming bundle. Verify downloaded release checksums before selecting those inputs.
The staging tool fingerprints their skill contents; it does not authenticate a release or execute the
old helper. No third-party skill is installed.

```sh
python3 forge.py update --app "/path/to/App" \
  --from-release "/path/to/swiftkeystone-0.2.0" \
  --output-dir "/path/to/private/skill-updates" --dry-run
python3 forge.py update --app "/path/to/App" \
  --from-release "/path/to/swiftkeystone-0.2.0" \
  --output-dir "/path/to/private/skill-updates"
```

The preview writes nothing. Staging creates a unique private directory outside the app and both
input distributions. It contains a manifest, a content/permission `backup` of installed files, the raw `incoming`
bundle, and a `candidate`. The app, profile, installed skills, and unrelated skills remain untouched.

- Files still equal to the previous distribution can take incoming changes or removals in the candidate.
- Local-only edits, extra files, and deletions are retained when the incoming file is unchanged.
- Concurrent upstream/local edits become conflicts. The candidate keeps the local choice, while the
  incoming copy and all three content hashes/permission modes remain available for review. No conflict is silently resolved.

A stage without conflicts still requires review. Missing candidate entrypoints or conflicts return exit 1;
invalid inputs return 2. Symlinked skill roots/files, escaping paths, and output inside inputs are refused.
A failed copy leaves an `incomplete` manifest and never touches the app. Repeated staging creates new
directories rather than replacing old backups. Concurrent edits/installations are unsupported; rerun
staging if inputs change. This is not an automatic or transactional in-place updater.

## Explicit activation and rollback

After reviewing candidate changes, conflicts, references, and local customizations, preserve the
original installed skill directories in a separate archive before activating the candidate into newly
vacant destinations. Do not copy over existing directories. Check that installed hashes still match
the manifest before moving anything. If a candidate is identical to the incoming distribution, the
ordinary installer can populate the vacant destinations; otherwise explicitly copy the reviewed merged
candidate without overwriting paths. Preserve profiles, instructions, unrelated skills, and the old helper.

If activation is interrupted or validation fails, inspect the actual directories and restore the archived
originals into vacant destinations. Do not delete an unexpected directory or replace a newer edit.
The manifest/backup support recovery, but staging does not perform activation or rollback for you.

Finally validate profile and installed references, run `audit`, inspect `verify --dry-run`, and establish
native build/test evidence using the new helper. Compare that evidence with the old baseline. A
successful staged diff alone does not prove a working upgrade, independent user adoption, or native UI
behavior. Legacy `ios-*` names and schema-version-1 profiles remain supported.
