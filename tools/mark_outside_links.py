#!/usr/bin/env python3
"""Mark preview links that leave WyoVote, and open them in the same tab.

Outside links (http or https to a host other than wyovote.com) lose
target="_blank" and rel="noopener"/"noreferrer", then gain a plain
"(leaves WyoVote)" marker. mailto links are left unmarked. Internal
PDF and Print links that used target="_blank" lose it too, with no
marker, so Back still returns to the page.

A button-styled outside link also gains class "btn-out" so the preview
stylesheet can color it. The marker text and its place after the link
stay as they are.

Run after a preview rebuild:

    python3 tools/mark_outside_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
MARKER = '<span class="ext">(leaves WyoVote)</span>'
A_RE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)
HREF_RE = re.compile(r"""href\s*=\s*(['"])(.*?)\1""", re.I)
TARGET_RE = re.compile(r"""\s+target\s*=\s*(['"])_blank\1""", re.I)
REL_RE = re.compile(r"""\s+rel\s*=\s*(['"])(.*?)\1""", re.I)
OWN_HOSTS = {"wyovote.com", "www.wyovote.com"}
BUTTON_CLASSES = {
    "official-btn",
    "pf-btn",
    "pf-dive-btn",
    "jump-btn",
    "back-btn",
    "cand-election-btn",
    "how-ratings-btn",
    "archive-hub-btn",
    "report-link",
}
CLASS_RE = re.compile(r"""class\s*=\s*(['"])(.*?)\1""", re.I)


def host_of(href: str) -> str:
    text = href.strip()
    if text.startswith("//"):
        text = "https:" + text
    return (urlparse(text).hostname or "").lower()


def is_outside(href: str) -> bool:
    text = href.strip()
    if not text.lower().startswith(("http://", "https://", "//")):
        return False
    host = host_of(text)
    return bool(host) and host not in OWN_HOSTS and not host.endswith(".wyovote.com")


def is_internal_pdf_or_print(href: str, attrs: str, inner: str) -> bool:
    if is_outside(href) or href.strip().lower().startswith(("mailto:", "tel:", "javascript:")):
        return False
    path = href.split("#", 1)[0].split("?", 1)[0].lower()
    if path.endswith(".pdf"):
        return True
    blob = (attrs + inner).lower()
    return "print-pdf" in blob or ">print" in blob or "print (pdf)" in blob


def strip_new_tab(attrs: str) -> str:
    attrs = TARGET_RE.sub("", attrs)

    def rel_sub(match: re.Match) -> str:
        quote, value = match.group(1), match.group(2)
        tokens = [token for token in value.split() if token.lower() not in {"noopener", "noreferrer"}]
        if not tokens:
            return ""
        return f" rel={quote}{' '.join(tokens)}{quote}"

    return REL_RE.sub(rel_sub, attrs)


def already_marked(text: str, end: int) -> bool:
    rest = text[end : end + 80]
    return bool(re.match(r"\s*<span class=\"ext\">", rest))


def with_btn_out(attrs: str) -> str:
    """Add btn-out to a button-styled outside link. Leave other links alone."""
    match = CLASS_RE.search(attrs)
    if not match:
        return attrs
    tokens = match.group(2).split()
    if "btn-out" in tokens or not BUTTON_CLASSES.intersection(tokens):
        return attrs
    tokens.append("btn-out")
    quote = match.group(1)
    replacement = f"class={quote}{' '.join(tokens)}{quote}"
    return attrs[: match.start()] + replacement + attrs[match.end() :]


def apply_text(text: str) -> tuple[str, dict[str, int]]:
    counts = {"outside_blank": 0, "markers": 0, "pdf_blank": 0, "btn_out": 0}
    pieces = []
    cursor = 0
    for match in A_RE.finditer(text):
        attrs, inner = match.group(1), match.group(2)
        href_match = HREF_RE.search(attrs)
        if not href_match:
            continue
        href = href_match.group(2)
        outside = is_outside(href)
        pdf_print = is_internal_pdf_or_print(href, attrs, inner)
        had_blank = bool(TARGET_RE.search(attrs))
        if not outside and not (pdf_print and had_blank):
            continue
        pieces.append(text[cursor : match.start()])
        new_attrs = strip_new_tab(attrs) if outside or pdf_print else attrs
        if outside:
            stamped = with_btn_out(new_attrs)
            if stamped != new_attrs:
                counts["btn_out"] += 1
                new_attrs = stamped
        pieces.append(f"<a{new_attrs}>{inner}</a>")
        if outside:
            if had_blank:
                counts["outside_blank"] += 1
            nxt = text[match.end() : match.end() + 1]
            gap = "" if nxt.isspace() or nxt == "" else " "
            if not already_marked(text, match.end()):
                pieces.append(" " + MARKER + gap)
                counts["markers"] += 1
        elif pdf_print and had_blank:
            counts["pdf_blank"] += 1
        cursor = match.end()
    pieces.append(text[cursor:])
    updated = "".join(pieces)
    updated = re.sub(
        r'(<span class="ext">\(leaves WyoVote\)</span>)(?=\S)',
        r"\1 ",
        updated,
    )
    return updated, counts


def apply_tree(root: Path = PREVIEW) -> dict[str, int]:
    totals = {"files": 0, "outside_blank": 0, "markers": 0, "pdf_blank": 0, "btn_out": 0}
    for path in sorted(root.rglob("*.html")):
        original = path.read_text(encoding="utf-8")
        updated, counts = apply_text(original)
        if updated == original:
            continue
        path.write_text(updated, encoding="utf-8")
        totals["files"] += 1
        for key in ("outside_blank", "markers", "pdf_blank", "btn_out"):
            totals[key] += counts[key]
    return totals


def main() -> None:
    totals = apply_tree()
    print(
        f"updated {totals['files']} preview pages; "
        f"removed target=_blank from {totals['outside_blank']} outside links; "
        f"added {totals['markers']} markers; "
        f"removed target=_blank from {totals['pdf_blank']} internal PDF or Print links; "
        f"added btn-out to {totals['btn_out']} button-styled outside links"
    )


if __name__ == "__main__":
    sys.exit(main())
