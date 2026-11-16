#!/usr/bin/env python3
"""Mark a STAGING copy of the site as a review build.

Single tree since 2026-11-15: the repository holds only the live pages, and
there is no in-site preview/ folder. For review, copy the tree somewhere
outside the repo, run this on the copy, and deploy the copy to a Cloudflare
branch preview (BRANCH=<name> /workspace/cloudflare/deploy_pages.sh with
SRC_DIR=<copy>). Never run it on the repository itself, and never deploy a
marked copy with BRANCH=main.

    python3 tools/to_preview.py /tmp/review-copy

Adds <meta name="robots" content="noindex"> and the PREVIEW banner to every
HTML page. Links and stylesheets are left unchanged, because the branch
preview serves the same paths as the live site.
"""
import sys
from pathlib import Path

NOINDEX = '    <meta name="robots" content="noindex">\n'
VIEWPORT = '    <meta name="viewport" content="width=device-width, initial-scale=1">\n'
SKIP = '    <a class="skip-link" href="#main">Skip to content</a>\n'
BANNER = '    <p class="preview-banner" role="status">PREVIEW, not the live site</p>\n'


def to_preview(t: str, depth: int = 0) -> str:
    """depth is kept for old callers; it is no longer used."""
    del depth
    if NOINDEX not in t:
        t = t.replace(VIEWPORT, NOINDEX + VIEWPORT, 1)
    if BANNER not in t:
        t = t.replace(SKIP, SKIP + BANNER, 1)
    return t


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    root = Path(argv[1]).resolve()
    if (root / ".git").exists() or (root / "tools" / "to_preview.py").resolve() == Path(__file__).resolve():
        print("refusing to mark the repository itself; run this on a staging copy", file=sys.stderr)
        return 2
    count = 0
    for path in root.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        new = to_preview(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            count += 1
    print(f"marked {count} pages as PREVIEW in {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
