#!/usr/bin/env python3
"""Build county pages that keep the existing county report and add current officeholders.

Data lives in data/county_officials/<slug>.json (see weston.json). Each county file
is the source of truth for that county's officeholder list. Running this script
writes counties/<slug>.html for every JSON file, or for one county with --county.

    python3 tools/build_county_officials.py
    python3 tools/build_county_officials.py --county weston

The existing county report (v1.1 PDF) is rendered at the top of the page. The new
officeholders section is below it, and the page version comes from the JSON
(page_version, currently v2.0). Other counties can be added later by dropping in
a JSON file with the same shape; no generator change is required.

Does not write the production manifest, open a pull request, or publish.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "county_officials"
OUT = ROOT / "counties"

# Reuse the published report parser so the top of the page matches the PDF.
_SPEC = importlib.util.spec_from_file_location(
    "build_report_pages", ROOT / "tools" / "build_report_pages.py"
)
_REPORTS = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_REPORTS)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def party_suffix(party: str | None) -> str:
    if not party:
        return ""
    letter = party.strip()
    if len(letter) > 1:
        letter = letter[0]
    return f" ({esc(letter)})"


def href_from(page: Path, href: str | None) -> str | None:
    if not href:
        return None
    if href.startswith(("http://", "https://", "/", "#")):
        return href
    target = (ROOT / href).resolve()
    return Path(os.path.relpath(target, page.parent)).as_posix()


def holder_name_html(holder: dict, page: Path) -> str:
    name = esc(holder["name"])
    link = href_from(page, holder.get("href"))
    if link:
        name = f'<a href="{esc(link)}">{name}</a>'
    role = holder.get("role")
    role_html = f', {esc(role)}' if role else ""
    return f"{name}{party_suffix(holder.get('party'))}{role_html}"


def succeeding_html(holder: dict) -> str:
    nxt = holder.get("succeeding")
    if not nxt:
        return ""
    when = nxt.get("takes_office") or "January"
    return (
        f'<span class="co-next">In {esc(when)}: '
        f'{esc(nxt["name"])}{party_suffix(nxt.get("party"))}</span>'
    )


def render_office(office: dict, page: Path) -> str:
    layout = office.get("layout") or "office-and-name"
    holders = office.get("holders") or []
    note = office.get("note")
    note_html = f'<p class="co-office-note">{esc(note)}</p>' if note else ""
    if layout == "heading-then-names":
        items = []
        for holder in holders:
            items.append(
                "<li>"
                + holder_name_html(holder, page)
                + succeeding_html(holder)
                + "</li>"
            )
        return (
            f'<div class="co-office co-office-group">'
            f'<h4 class="co-office-heading">{esc(office["office"])}</h4>'
            f'<ul class="co-names">{"".join(items)}</ul>'
            f'{note_html}'
            f"</div>"
        )
    # Single-line office + name. Multi-holder offices still stack names under the label.
    rows = []
    for holder in holders:
        rows.append(
            '<div class="co-line">'
            f'<span class="co-label">{esc(office["office"])}</span>'
            f'<span class="co-value">{holder_name_html(holder, page)}{succeeding_html(holder)}</span>'
            "</div>"
        )
    return f'<div class="co-office">{"".join(rows)}{note_html}</div>'


def render_group(group: dict, page: Path) -> str:
    parts = [f'<section class="co-group" id="co-{esc(group["id"])}">']
    parts.append(f'<h3>{esc(group["title"])}</h3>')
    if group.get("note"):
        parts.append(f'<p class="co-group-note">{esc(group["note"])}</p>')
    if group.get("offices"):
        for office in group["offices"]:
            parts.append(render_office(office, page))
    for precinct in group.get("precincts") or []:
        parts.append(
            f'<div class="co-precinct" id="co-pct-{esc(precinct["id"])}">'
            f'<h4 class="co-precinct-name">{esc(precinct["name"])}</h4>'
        )
        for office in precinct.get("offices") or []:
            parts.append(render_office(office, page))
        parts.append("</div>")
    parts.append("</section>")
    return "\n".join(parts)


def report_fragment(pdf: Path, dest: Path) -> str:
    parsed = _REPORTS.parse_report(pdf, "county")
    officials = _REPORTS.load_officials()
    parts: list[str] = []
    if parsed["summary"]:
        heads = "".join(f'<th scope="col">{esc(label)}</th>' for label, _value in parsed["summary"])
        vals = "".join(f"<td>{esc(value)}</td>" for _label, value in parsed["summary"])
        parts.append(
            f'<table class="report-stats"><thead><tr>{heads}</tr></thead>'
            f"<tbody><tr>{vals}</tr></tbody></table>"
        )
    headers, rows = parsed["summary_table"]
    if headers:
        name_at = parsed.get("name_column")
        if name_at is None and len(headers) > 1 and headers[1] == "Legislator":
            name_at = 1
        parts.append(_REPORTS.table(headers, rows, dest, officials, name_at))
    for title, members in parsed["sections"]:
        parts.append(f"<h2>{esc(title)}</h2>")
        if any(row.get("rank") for row in members):
            headers = ["Rank", "Legislator", "District", "Party"]
            keys = ["rank", "name", "district", "party"]
        else:
            headers = ["Legislator", "District", "Party"]
            keys = ["name", "district", "party"]
        if any(row.get("role") for row in members):
            headers.append("Role")
            keys.append("role")
        headers.extend(["Band", "Chamber rank"])
        keys.extend(["band", "chamber"])
        if any(row.get("covers") for row in members):
            headers.append("Also covers")
            keys.append("covers")
        body_rows = [[row.get(key, "") for key in keys] for row in members]
        parts.append(_REPORTS.table(headers, body_rows, dest, officials, keys.index("name")))
    for note in parsed["notes"]:
        parts.append(f'<p class="report-note">{esc(note)}</p>')
    subtitle = parsed.get("subtitle") or ""
    pdf_href = Path(os.path.relpath(pdf, dest.parent)).as_posix()
    return {
        "title": parsed.get("title") or pdf.stem,
        "subtitle": subtitle,
        "body": "\n          ".join(parts),
        "pdf_href": pdf_href,
    }


def page_html(data: dict, dest: Path) -> str:
    number = data["county_number"]
    county = data["county"]
    version = data.get("page_version") or "v2.0"
    title = f"{number:02d} {county} County"
    pdf = ROOT / data["report_pdf"]
    if not pdf.is_file():
        raise SystemExit(f"Missing county report PDF: {pdf}")
    report = report_fragment(pdf, dest)
    groups = "\n        ".join(render_group(group, dest) for group in data["groups"])
    intro = data.get("intro") or ""
    root = "../"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)} — WyoVote</title>
    <meta name="description" content="County report and current officeholders for {esc(county)} County, Wyoming.">
    <link rel="icon" href="{root}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{root}css/styles.css">
    <link rel="stylesheet" href="{root}assets/css/site.css">
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="{root}index.html">
          <img src="{root}assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="{root}index.html">Home</a></li>
            <li><a href="{root}archive.html">Archive</a></li>
            <li><a href="{root}candidates.html">Candidates</a></li>
            <li><a href="{root}committees.html">Committees</a></li>
            <li><a href="{root}counties.html" aria-current="page">Counties</a></li>
            <li><a href="{root}officials.html">Officials</a></li>
            <li><a href="{root}people/index.html">Name Index</a></li>
            <li><a href="{root}research.html">Research</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="{root}counties.html">← Back to Counties</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>{esc(title)}</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap report-sheet county-page">
          <p class="report-kicker">County page · {esc(version)}</p>
          <p class="report-actions"><a class="print-pdf" data-print="1" href="{esc(report['pdf_href'])}">Print report (PDF)</a></p>
          {report['body']}
          <section class="county-officials" id="current-officeholders">
            <h2>Current officeholders</h2>
            <p class="co-intro">{esc(intro)}</p>
            <div class="co-grid">
        {groups}
            </div>
          </section>
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="{root}about.html">About</a></li>
            <li><a href="{root}privacy.html">Privacy</a></li>
            <li><a href="{root}contact.html">Contact</a></li>
            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v1.2.pdf">User's Guide</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""


def load_county(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("county", "county_number", "report_pdf", "groups"):
        if key not in data:
            raise SystemExit(f"{path} is missing {key}")
    return data


def build_one(path: Path) -> Path:
    slug = path.stem
    dest = OUT / f"{slug}.html"
    data = load_county(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page_html(data, dest), encoding="utf-8")
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--county", help="Build only this county slug (filename without .json).")
    args = parser.parse_args()
    files = sorted(DATA.glob("*.json"))
    if args.county:
        files = [DATA / f"{args.county}.json"]
        if not files[0].is_file():
            raise SystemExit(f"No data file at {files[0]}")
    if not files:
        raise SystemExit(f"No county JSON files in {DATA}")
    for path in files:
        dest = build_one(path)
        print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
