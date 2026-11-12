#!/usr/bin/env python3
"""Stamp the preview Site Map and the small header trail.

The full diagram and the trail on each preview page come from the same
page structure. Run this after adding preview pages:

    python3 tools/build_site_map.py

tools/build_candidate_pages.py runs it at the end, so a candidate rebuild
picks up the trail on new pages.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"

# Levels only. Repeating pages are one box, not one box per name.
TREE = (
    "Home",
    [
        (
            "Archive",
            [
                ("Articles", [("Article", [])]),
                ("Committees", []),
                ("Counties", []),
                ("Reports", []),
                ("Officials", []),
                ("Research", []),
                ("Candidates", []),
            ],
        ),
        (
            "Candidates",
            [("Year", [("County", [("Candidate", [])])])],
        ),
        (
            "Officials",
            [("Session", [("Official", [("Deeper Dive", [])])])],
        ),
        ("Research", []),
        ("News", [("Article", [])]),
        (
            "Ratings",
            [
                ("How the Ratings Work", []),
                ("Committee ratings", []),
                ("County ratings", []),
                ("Legislative ratings", []),
                ("Historical ratings", []),
            ],
        ),
        ("About", []),
        ("Privacy", []),
        ("Contact", []),
    ],
)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def page_h1(text: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if not match:
        return ""
    name = re.sub(r"<[^>]+>", "", match.group(1))
    return re.sub(r"\s+", " ", html.unescape(name)).strip()


def county_name(text: str) -> str:
    match = re.search(r"Back to ([A-Za-z][A-Za-z .'-]*?) County", text)
    return match.group(1) if match else ""


def year_label(folder: str) -> str:
    year = folder.split("-")[0]
    if folder.endswith("-primary"):
        return f"{year} Primary"
    return year


def crumbs(rel: str, text: str) -> list[str]:
    """Levels from Home down to this page. At most four, nearest the page."""
    path = Path(rel)
    parts = path.parts
    name = path.name
    title = page_h1(text) or path.stem.replace("-", " ").title()
    chain = ["Home"]

    if rel in {"index.html"}:
        return chain
    if rel == "site-map.html":
        chain.append("Site Map")
    elif rel == "404.html":
        chain.append("Page not found")
    elif parts[0] == "archive":
        chain.append("Archive")
        labels = {
            "articles.html": "Articles",
            "committees.html": "Committees",
            "counties.html": "Counties",
            "reports.html": "Reports",
            "officials.html": "Officials",
            "research.html": "Research",
            "candidates.html": "Candidates",
        }
        chain.append(labels.get(name, title))
    elif parts[0] == "articles":
        chain.extend(["Archive", "Articles", title])
    elif parts[0] == "news":
        chain.append("News")
        chain.append("Archive" if name == "archive.html" else title)
    elif rel == "candidates.html" or parts[0] == "candidates":
        chain.append("Candidates")
        if rel != "candidates.html":
            year = year_label(parts[1])
            if name == "index.html":
                chain.append(year)
            elif "c" in parts:
                if not parts[1].startswith("2026"):
                    chain.append(year)
                chain.append(county_name(text) or "County")
                chain.append(title)
            else:
                if not parts[1].startswith("2026"):
                    chain.append(year)
                chain.append(title.removesuffix(" County"))
    elif rel == "officials.html" or parts[0] == "officials":
        chain.append("Officials")
        if rel != "officials.html":
            if len(parts) > 2 and parts[1] != path.name:
                chain.append(parts[-2] if name == "index.html" else parts[1])
            if name == "index.html":
                pass
            elif name.endswith("-deep.html"):
                chain.append(title)
                chain.append("Deeper Dive")
            else:
                chain.append(title)
    else:
        chain.append(title)

    if len(chain) > 4:
        chain = chain[-4:]
    return chain


def trail_label(label: str) -> str:
    """Year-index labels follow the Primary/General switch, the same as the h1."""
    match = re.fullmatch(r"(\d{4}) Primary", label)
    if not match:
        return esc(label)
    year = match.group(1)
    return (
        f'<span class="cand-view-primary">{year} Primary</span>'
        f'<span class="cand-view-general">{year} General</span>'
    )


def trail_html(labels: list[str]) -> str:
    rows = ['<div class="page-trail" aria-label="Where this page sits">', "  <ol>"]
    for index, label in enumerate(labels):
        if index:
            rows.append('    <li class="trail-join" aria-hidden="true"></li>')
        kind = "site-box is-current" if index == len(labels) - 1 else "site-box"
        rows.append(f'    <li><span class="{kind}">{trail_label(label)}</span></li>')
    rows.append("  </ol>")
    rows.append("</div>")
    return "\n".join(rows)


def root_prefix(rel: str) -> str:
    return "../" * (len(Path(rel).parts) - 1)


def insert_nav(text: str, rel: str) -> str:
    text = re.sub(r"\s*<li><a class=\"site-map-link\".*?</li>", "", text, flags=re.S)
    current = ' aria-current="page"' if rel == "site-map.html" else ""
    item = f'<li><a class="site-map-link" href="{root_prefix(rel)}site-map.html"{current}>Site Map</a></li>'
    match = re.search(r'(<a href="[^"]*research\.html"[^>]*>Research</a></li>)', text)
    if not match:
        return text
    return text[: match.end()] + "\n            " + item + text[match.end() :]


def insert_trail(text: str, labels: list[str]) -> str:
    block = trail_html(labels)
    text = re.sub(r"\s*<!-- page-trail -->.*?<!-- /page-trail -->", "", text, flags=re.S)
    wrapped = "<!-- page-trail -->\n" + block + "\n<!-- /page-trail -->"
    hero = re.search(r'(<section class="page-hero"[^>]*>\s*<div class="wrap">)', text)
    if hero:
        end = text.find("</div>", hero.end())
        if end != -1:
            return text[:end] + "\n" + wrapped + "\n        " + text[end:]
    profile = re.search(r'(<section class="pf-head"[^>]*>)', text)
    if profile:
        return text[: profile.end()] + "\n" + wrapped + text[profile.end() :]
    header = re.search(r'(<div class="wrap header-inner">)', text)
    if header:
        # Keep the trail with the header on pages that have no green title band.
        close = text.find("</div>", header.end())
        if close != -1:
            return text[:close] + "\n" + wrapped + "\n      " + text[close:]
    return text


def render_tree(node: tuple) -> str:
    label, children = node
    inner = f'<span class="site-box">{esc(label)}</span>'
    if children:
        inner += '<ul>' + "".join(f"<li>{render_tree(child)}</li>" for child in children) + "</ul>"
    return inner


def write_site_map_page() -> None:
    diagram = f'<div class="map-diagram" role="img" aria-label="Site map diagram. Information only, not links."><ul class="map-tree"><li>{render_tree(TREE)}</li></ul></div>'
    page = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Site Map — WyoVote</title>
    <meta name="description" content="A diagram of the WyoVote pages and how they are nested.">
    <link rel="icon" href="assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="../css/styles.css">
    <link rel="stylesheet" href="preview.css">
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <p class="preview-banner" role="status">PREVIEW, not the live site</p>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="index.html">
          <img src="assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="index.html">Home</a></li>
            <li><a href="archive.html">Archive</a></li>
            <li><a href="candidates.html">Candidates</a></li>
            <li><a href="archive/committees.html">Committees</a></li>
            <li><a href="archive/counties.html">Counties</a></li>
            <li><a href="officials.html">Officials</a></li>
            <li><a href="research.html">Research</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="index.html">← Back to Home</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>Site Map</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap page-prose">
          <p>This diagram shows how the pages are nested. Repeating pages are shown once, by level. The boxes are information only.</p>
          {diagram}
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="about.html">About</a></li>
            <li><a href="privacy.html">Privacy</a></li>
            <li><a href="contact.html">Contact</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""
    (PREVIEW / "site-map.html").write_text(page, encoding="utf-8")


def stamp(path: Path) -> None:
    rel = path.relative_to(PREVIEW).as_posix()
    text = path.read_text(encoding="utf-8")
    text = insert_nav(text, rel)
    text = insert_trail(text, crumbs(rel, text))
    path.write_text(text, encoding="utf-8")


def main() -> None:
    write_site_map_page()
    pages = sorted(PREVIEW.rglob("*.html"))
    for path in pages:
        stamp(path)
    print(f"stamped {len(pages)} preview pages")


if __name__ == "__main__":
    main()
