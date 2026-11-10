# Site rules

## Report versions

Only the current version of each report stays on the site.

When a new version is published:

- Give it a new file name. Do not reuse the name of the file it replaces.
- Remove the superseded file in the same pull request that adds the new one.
- Keep the superseded file in git history and in the baseline tags and zips. It does not stay in the published tree.

Do not overwrite an existing live file. Replacing the bytes of a file that is already on the site needs Michael's approval. A new version is a new file. The old file is deleted in that same pull request, not overwritten.

This applies to rating PDFs and to every other report file the site publishes.
