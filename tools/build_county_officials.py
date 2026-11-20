#!/usr/bin/env python3
"""Build county pages that keep the existing county report and add current officeholders.

Data lives in data/county_officials/<slug>.json (see weston.json). Each county file
is the source of truth for that county's officeholder list. Running this script
writes counties/<slug>.html and counties/<slug>-precincts.html for every JSON
file (or one county with --county), and rewrites the Federal and Statewide box
on counties.html from data/county_officials/shared/federal-statewide.json.

    python3 tools/build_county_officials.py
    python3 tools/build_county_officials.py --county weston
    python3 tools/build_county_officials.py --county weston --as-of 2027-01-04

The existing county report (the v1.1 PDF) is rendered at the top of the page
and remains the Print report; there is no v2.0 PDF. The officeholders section
is below it. The page version comes from the JSON (page_version, currently v2.0).

Holders who will be replaced have a `succeeding` entry. Before `term_switch_date`
(2027-01-04 for Weston, the day the new terms begin), the page shows today's
holder with "; in January: Name" on the same line. A rebuild on or after that date, using
the America/Denver calendar (or `--as-of`), promotes the elect to the holder
and drops the January line. See data/county_officials/SCHEMA.md.

Other counties can be added later by dropping in a JSON file with the same
shape; no generator change is required.

Does not write the production manifest, open a pull request, or publish.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DENVER = ZoneInfo("America/Denver")

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


def denver_today() -> date:
    return datetime.now(DENVER).date()


def parse_iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid {label}: {value!r}") from exc


def switch_reached(switch: str | None, as_of: date) -> bool:
    """True when as_of is on or after the ISO switch date (Denver calendar)."""
    if not switch:
        return False
    return as_of >= parse_iso_date(switch, "term_switch_date")


def promote_holder(holder: dict, default_switch: str | None, as_of: date) -> dict:
    """If the term-switch date has arrived, the elect becomes the holder."""
    nxt = holder.get("succeeding")
    if not nxt:
        return holder
    switch = nxt.get("switch_date") or default_switch
    if not switch_reached(switch, as_of):
        return holder
    promoted = {
        "name": nxt["name"],
        "sources": nxt.get("sources") or holder.get("sources") or [],
    }
    if nxt.get("party") or holder.get("party"):
        promoted["party"] = nxt.get("party") or holder.get("party")
    if nxt.get("href"):
        promoted["href"] = nxt["href"]
    if nxt.get("role"):
        promoted["role"] = nxt["role"]
    if nxt.get("ballot_name"):
        promoted["ballot_name"] = nxt["ballot_name"]
    return promoted


def apply_term_switch(data: dict, as_of: date) -> dict:
    """Return a copy of the county data with elects promoted when due.

    On or after term_switch_date, each holder who has a succeeding entry is
    replaced by that person and the succeeding (In January) line is dropped.
    An office may set succeeding.switch_date to override the county date.
    """
    data = deepcopy(data)
    default_switch = data.get("term_switch_date")

    def map_offices(offices: list[dict] | None) -> None:
        for office in offices or []:
            office["holders"] = [
                promote_holder(holder, default_switch, as_of)
                for holder in office.get("holders") or []
            ]

    pending = False
    for group in data.get("groups") or []:
        map_offices(group.get("offices"))
        for precinct in group.get("precincts") or []:
            map_offices(precinct.get("offices"))
        for office in (group.get("offices") or []) + [
            office
            for precinct in group.get("precincts") or []
            for office in precinct.get("offices") or []
        ]:
            for holder in office.get("holders") or []:
                if holder.get("succeeding"):
                    pending = True

    if pending:
        data["intro"] = data.get("intro") or ""
    else:
        data["intro"] = data.get("intro_after_switch") or "Names are the people in office today."
    return data


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
        f'<span class="co-next">; in {esc(when)}: '
        f'{esc(nxt["name"])}{party_suffix(nxt.get("party"))}</span>'
    )


def render_office(office: dict, page: Path) -> str:
    """One office box: the office title, then each holder with any January change on the same line."""
    holders = office.get("holders") or []
    note = office.get("note")
    note_html = f'<p class="co-office-note">{esc(note)}</p>' if note else ""
    items = "".join(
        f"<li>{holder_name_html(holder, page)}{succeeding_html(holder)}</li>" for holder in holders
    )
    return (
        '<div class="co-box">'
        f'<h4 class="co-box-title">{esc(office["office"])}</h4>'
        f'<ul class="co-names">{items}</ul>'
        f"{note_html}"
        "</div>"
    )


def render_group(group: dict, page: Path) -> str:
    """A titled section whose office boxes sit in a multi-column grid."""
    parts = [f'<section class="co-group" id="co-{esc(group["id"])}">']
    parts.append(f'<h3>{esc(group["title"])}</h3>')
    if group.get("note"):
        parts.append(f'<p class="co-group-note">{esc(group["note"])}</p>')
    boxes = [render_office(office, page) for office in group.get("offices") or []]
    for precinct in group.get("precincts") or []:
        inner = "".join(
            f'<h5 class="co-box-sub">{esc(office["office"])}</h5>'
            f'<ul class="co-names">'
            + "".join(f"<li>{holder_name_html(h, page)}{succeeding_html(h)}</li>" for h in office.get("holders") or [])
            + "</ul>"
            for office in precinct.get("offices") or []
        )
        boxes.append(
            f'<div class="co-box co-precinct" id="co-pct-{esc(precinct["id"])}">'
            f'<h4 class="co-box-title">{esc(precinct["name"])}</h4>{inner}</div>'
        )
    if boxes:
        parts.append('<div class="co-boxes">' + "\n".join(boxes) + "</div>")
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


SHARED = DATA / "shared" / "federal-statewide.json"
SHARED_IDS = {"federal", "statewide"}
COUNTIES_PAGE = ROOT / "counties.html"
MARK_START = "<!-- county-officials:federal-statewide:start -->"
MARK_END = "<!-- county-officials:federal-statewide:end -->"


def page_shell(title: str, description: str, back_href: str, back_label: str, body: str) -> str:
    root = "../"
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)} — WyoVote</title>
    <meta name="description" content="{esc(description)}">
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
            <li><a href="{root}candidates.html">Candidates</a></li>
            <li><a href="{root}committees.html">Committees</a></li>
            <li><a href="{root}counties.html" aria-current="page">Counties</a></li>
            <li><a href="{root}officials.html">Officials</a></li>
            <li><a href="{root}people/index.html">Name Index</a></li>
            <li><a href="{root}research.html">Research</a></li>
            <li><a href="{root}archive.html">Archive</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="{esc(back_href)}">← {esc(back_label)}</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>{esc(title)}</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap report-sheet county-page">
{body}
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
            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v2.0.pdf">User's Guide</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""


def county_title(data: dict) -> str:
    return f"{data['county_number']:02d} {data['county']} County"


def county_weekly(slug: str, as_of: date) -> str:
    """The Weekly section for pilot counties (tools/schedule/county.py); empty otherwise."""
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "tools" / "schedule"))
    import county as _county
    block = _county.block_for(ROOT, slug, as_of)
    return "\n" + block if block else ""


def page_html(data: dict, dest: Path, as_of: date, slug: str) -> str:
    """County page: report on top, then legislators and county offices in box grids."""
    data = apply_term_switch(data, as_of)
    county = data["county"]
    version = data.get("page_version") or "v2.0"
    title = county_title(data)
    pdf = ROOT / data["report_pdf"]
    if not pdf.is_file():
        raise SystemExit(f"Missing county report PDF: {pdf}")
    report = report_fragment(pdf, dest)
    groups = [g for g in data["groups"] if g["id"] not in SHARED_IDS and not g.get("precincts")]
    has_precincts = any(g.get("precincts") for g in data["groups"])
    rendered = "\n".join(render_group(group, dest) for group in groups)
    # Large, easy-to-find buttons (precinct page first, most prominent).
    buttons = []
    if has_precincts:
        buttons.append(f'<a class="co-btn co-btn-primary" href="{esc(slug)}-precincts.html">'
                       f'{esc(county)} County precinct committee people</a>')
    buttons.append('<a class="co-btn" href="../counties.html#federal-statewide">Federal and statewide officials</a>')
    links = [f'<nav class="co-btns" aria-label="More officeholders">{"".join(buttons)}</nav>']
    body = f"""          <p class="report-kicker">County page · {esc(version)}</p>
          <p class="report-actions"><a class="print-pdf" data-print="1" href="{esc(report['pdf_href'])}">Print report (PDF)</a></p>
          {report['body']}{county_weekly(slug, as_of)}
          <section class="county-officials" id="current-officeholders">
            <h2>Current officeholders</h2>
            <p class="co-intro">{esc(data.get("intro") or "")}</p>
            {"".join(links)}
{rendered}
          </section>"""
    return page_shell(title, f"County report and current officeholders for {county} County, Wyoming.",
                      "../counties.html", "Back to Counties", body)


def precinct_page_html(data: dict, dest: Path, as_of: date, slug: str) -> str | None:
    data = apply_term_switch(data, as_of)
    groups = [g for g in data["groups"] if g.get("precincts")]
    if not groups:
        return None
    county = data["county"]
    title = f"{county_title(data)} Precinct Committee People"
    rendered = "\n".join(render_group(group, dest) for group in groups)
    body = f"""          <section class="county-officials" id="precinct-committee-people">
            <nav class="co-btns" aria-label="Back to county"><a class="co-btn co-btn-primary" href="{esc(slug)}.html">← Back to the {esc(county)} County page</a></nav>
{rendered}
          </section>"""
    return page_shell(title, f"Precinct committee people for {county} County, Wyoming.",
                      f"{slug}.html", f"Back to {county} County", body)


def shared_block(as_of: date) -> str:
    data = json.loads(SHARED.read_text(encoding="utf-8"))
    data = apply_term_switch(data, as_of)
    if not any(h.get("succeeding") for g in data["groups"] for o in g.get("offices") or [] for h in o.get("holders") or []):
        data["intro"] = data.get("intro_after_switch") or data.get("intro") or ""
    rendered = "\n".join(render_group(group, COUNTIES_PAGE) for group in data["groups"])
    return (
        f"{MARK_START}\n"
        f'          <section class="county-officials co-shared" id="federal-statewide">\n'
        f'            <h2>{esc(data.get("title") or "Federal and statewide officials")}</h2>\n'
        f'            <p class="co-intro">{esc(data.get("intro") or "")}</p>\n'
        f"{rendered}\n"
        f"          </section>\n"
        f"          {MARK_END}"
    )


def write_counties_page(as_of: date) -> Path:
    text = COUNTIES_PAGE.read_text(encoding="utf-8")
    block = shared_block(as_of)
    if MARK_START in text:
        i = text.index(MARK_START)
        j = text.index(MARK_END) + len(MARK_END)
        text = text[:i] + block + text[j:]
    else:
        anchor = '<section class="page-body">\n'
        if anchor not in text:
            raise SystemExit("counties.html: page-body section not found")
        text = text.replace(anchor, anchor + '        <div class="wrap report-sheet co-shared-wrap">\n          ' + block + "\n        </div>\n", 1)
    COUNTIES_PAGE.write_text(text, encoding="utf-8")
    return COUNTIES_PAGE


def load_county(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("county", "county_number", "report_pdf", "groups"):
        if key not in data:
            raise SystemExit(f"{path} is missing {key}")
    return data


def build_one(path: Path, as_of: date) -> Path:
    slug = path.stem
    dest = OUT / f"{slug}.html"
    data = load_county(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page_html(data, dest, as_of, slug), encoding="utf-8")
    pdest = OUT / f"{slug}-precincts.html"
    ptext = precinct_page_html(data, pdest, as_of, slug)
    if ptext:
        pdest.write_text(ptext, encoding="utf-8")
    elif pdest.exists():
        pdest.unlink()
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--county", help="Build only this county slug (filename without .json).")
    parser.add_argument(
        "--as-of",
        metavar="YYYY-MM-DD",
        help="Build as of this America/Denver date instead of today. "
        "Use to preview or apply the term switch (Weston: 2027-01-04).",
    )
    args = parser.parse_args()
    as_of = parse_iso_date(args.as_of, "--as-of") if args.as_of else denver_today()
    files = sorted(DATA.glob("*.json"))
    if args.county:
        files = [DATA / f"{args.county}.json"]
        if not files[0].is_file():
            raise SystemExit(f"No data file at {files[0]}")
    if not files:
        raise SystemExit(f"No county JSON files in {DATA}")
    for path in files:
        dest = build_one(path, as_of)
        print(f"wrote {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes) as of {as_of.isoformat()}")
    if SHARED.is_file():
        print(f"wrote {write_counties_page(as_of).relative_to(ROOT)} (federal and statewide box)")


if __name__ == "__main__":
    main()
