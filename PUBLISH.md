# Publishing WyoVote

The live site is https://wyovote.com, served by Cloudflare Pages (project
`wyovote`, direct upload). GitHub Pages was retired on 2026-11-15.

## One tree (since 2026-11-15)

The repository holds only the live pages, at their live paths. There is no
in-site `preview/` folder any more, and `tools/publish_check.py` fails if one
comes back. Old `https://wyovote.com/preview/...` links are sent to the live
page by `_redirects`.

Generators (`tools/build_*.py`, `tools/mark_outside_links.py`,
`tools/stamp_deeper_dive.py`, `tools/assemble.py`) write the live paths
directly. Source data that is not a site page lives under `tools/`, which is
never deployed (for example `tools/local-data/` for the Local builders).

## Review a change before it goes live

1. Make the change on a branch or in a local copy of the repository.
2. Run `python3 tools/publish_check.py`. It must say `Result: PASS`.
3. Deploy that tree to a Cloudflare branch preview, never to production:

   ```bash
   BRANCH=<short-name> W=work_<short-name> SRC_DIR=<tree> \
     /workspace/cloudflare/deploy_pages.sh prepare <commit-sha>
   ```

   then the usual upload and create-deployment steps from
   `/workspace/cloudflare/DEPLOY.md`. The preview is at
   `https://<short-name>.wyovote.pages.dev`, with the same paths as the live
   site. Branch names must be DNS-safe (`pr-77`, `officials-2008`).
4. Optional: to show a PREVIEW banner and `noindex` on the review copy, run
   `python3 tools/to_preview.py <staging-copy>` on a copy outside the
   repository before deploying it. Never commit those changes and never deploy a
   marked copy to production.
5. Send the `*.wyovote.pages.dev` link for review. Branch previews are public
   to anyone with the link, so do not put private drafts there.

## Publish

Only after Michael's own "publish":

1. Open a pull request to `main`. The Publish check workflow runs
   `tools/publish_check.py` on it.
2. Merge it.
3. Deploy the merge commit to production with `BRANCH=main` (see
   `/workspace/cloudflare/DEPLOY.md`), then verify links and redirects.

## Limits the publish check enforces

| Check | Limit |
| --- | --- |
| Deploy files (Cloudflare Pages Free plan) | 20,000 |
| Any single file | 500 KB unless allow-listed |
| Tracked repository size | 500 MB |
| `_redirects` | 2,000 static + 100 dynamic rules (Cloudflare limit; check by hand) |
| Files under `preview/` | none |

Do not add a `CNAME` file. The custom domain is set in Cloudflare Pages.
