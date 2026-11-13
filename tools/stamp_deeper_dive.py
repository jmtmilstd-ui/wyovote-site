#!/usr/bin/env python3
"""Put a large Deeper dive button under the name on preview official pages.

The button uses the same href as the existing link at the bottom of the page.
Run after rebuilding official pages:

    python3 tools/stamp_deeper_dive.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIALS = ROOT / "preview" / "officials"
DEEPER = re.compile(r'<p class="pf-deeper"><a href="([^"]+)">Deeper dive</a></p>')
HEAD = re.compile(
    r'(<section class="pf-head"[\s\S]*?</section>)(\s*)(<section class="pf-card")'
)


def button(href: str) -> str:
    return f'<p class="pf-dive"><a class="pf-dive-btn" href="{href}">Deeper dive →</a></p>'


def stamp(text: str) -> str | None:
    if 'class="pf-dive"' in text:
        return None
    found = DEEPER.search(text)
    if not found:
        return None
    updated, count = HEAD.subn(
        lambda match: match.group(1) + "\n        " + button(found.group(1)) + "\n" + match.group(2) + match.group(3),
        text,
        count=1,
    )
    if count != 1:
        return None
    return updated


def main() -> None:
    changed = 0
    for path in sorted(OFFICIALS.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        updated = stamp(text)
        if updated is None:
            continue
        path.write_text(updated, encoding="utf-8")
        changed += 1
    print(f"added the Deeper dive button on {changed} preview official pages")


if __name__ == "__main__":
    sys.exit(main())
