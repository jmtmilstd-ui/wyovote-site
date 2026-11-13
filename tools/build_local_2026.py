#!/usr/bin/env python3
"""Build the preview Local candidates page from the 2026 county-office files.

Reads preview/data/local/2026/ and writes preview/candidates/2026-local.html.
Also adds the Local button beside Primary and General on the 2026 Candidates pages.
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "preview" / "data" / "local" / "2026"
OUT = ROOT / "preview" / "candidates" / "2026-local.html"
PREVIEW = ROOT / "preview"

COUNTIES = [
    ("Albany", "albany", "albany"),
    ("Big Horn", "big-horn", "bighorn"),
    ("Campbell", "campbell", "campbell"),
    ("Carbon", "carbon", "carbon"),
    ("Converse", "converse", "converse"),
    ("Crook", "crook", "crook"),
    ("Fremont", "fremont", "fremont"),
    ("Goshen", "goshen", "goshen"),
    ("Hot Springs", "hot-springs", "hotsprings"),
    ("Johnson", "johnson", "johnson"),
    ("Laramie", "laramie", "laramie"),
    ("Lincoln", "lincoln", "lincoln"),
    ("Natrona", "natrona", "natrona"),
    ("Niobrara", "niobrara", "niobrara"),
    ("Park", "park", "park"),
    ("Platte", "platte", "platte"),
    ("Sheridan", "sheridan", "sheridan"),
    ("Sublette", "sublette", "sublette"),
    ("Sweetwater", "sweetwater", "sweetwater"),
    ("Teton", "teton", "teton"),
    ("Uinta", "uinta", "uinta"),
    ("Washakie", "washakie", "washakie"),
    ("Weston", "weston", "weston"),
]

OFFICES = [
    "County Commissioner",
    "County Clerk",
    "County Treasurer",
    "County Assessor",
    "County Sheriff",
    "County Attorney",
    "District Attorney",
    "County Coroner",
    "Clerk of District Court",
]

PARTIES = {
    "REP": "Republican",
    "DEM": "Democrat",
    "IND": "Independent",
    "LIB": "Libertarian",
}


def esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def party_name(code: str) -> str:
    code = (code or "").strip()
    if not code:
        return ""
    return PARTIES.get(code, code)


def vote_cell(votes: str, result: str, status: str) -> str:
    if (votes or "").strip():
        return esc(votes.strip())
    if (result or "").strip() == "withdrawn":
        return "Withdrawn"
    if (result or "").strip() == "not_on_ballot":
        return "Not on ballot"
    if (status or "").strip() in ("not_posted", "not_yet_posted", "unknown") or (result or "").strip() == "not_posted":
        return "Not posted"
    return "—"


def status_line(info: dict) -> str:
    kind = info.get("status") or ""
    primary = info.get("primary_status") or ""
    general = info.get("general_status") or ""
    if kind == "not_yet_posted":
        return "Not yet posted by the county clerk."
    if primary == "unofficial" and general == "unofficial":
        return "Unofficial. The county clerk posted unofficial summaries, not a canvassed result."
    if kind == "complete" and primary == "official" and general == "official":
        return "Official. The county clerk posted official primary and general results."

    def side(label: str, value: str) -> str:
        if value == "official":
            return f"{label} results are official."
        if value == "unofficial":
            return f"{label} results are unofficial."
        return f"{label} results were not posted."

    return "Partial. " + side("Primary", primary) + " " + side("General", general)


# Plain public notes. Collection problems stay in the status files, not on the page.
NOTES = {
    "Albany": "Official general county results were not posted as of November 13, 2026.",
    "Fremont": (
        "Commissioner seats on the ballot are Districts 1, 3, and 4. District 2 was not on the ballot. "
        "The general abstract lists the assessor as Riggs. The primary nominee is Tara M. Berg. "
        "The general abstract prints surnames only."
    ),
    "Johnson": "An official primary summary was not posted.",
    "Weston": "The commissioner surname Nessle was read from a vertical header.",
}


def source_links(info: dict, rows: list[dict]) -> list[tuple[str, str]]:
    sources = info.get("sources") or {}
    links = []
    seen = set()

    def add(label: str, url: str) -> None:
        url = (url or "").strip()
        if not url or url in seen or not url.startswith("http"):
            return
        seen.add(url)
        links.append((label, url))

    # A county that has not posted results gets the clerk page, not an unread file.
    if info.get("status") == "not_yet_posted":
        add("County clerk", sources.get("results_page") or "")
        return links

    add("Primary results", sources.get("primary") or "")
    add("General results", sources.get("general") or "")
    if not links:
        add("Candidate roster", sources.get("roster_primary") or sources.get("roster") or "")
        for row in rows:
            add("Primary results", row.get("source_primary_results_url") or "")
            add("General results", row.get("source_general_results_url") or "")
            add("Candidate roster", row.get("source_roster_url") or "")
    if not links:
        add("County clerk", sources.get("results_page") or "")
    return links


def office_heading(office: str, seat: str) -> str:
    seat = (seat or "").strip()
    if "District" in seat:
        district = seat.split("District", 1)[1].strip(" ,")
        return f"{office}, District {district}"
    return office


def is_writein(row: dict) -> bool:
    return (row.get("candidate_ballot_name") or "").strip().lower() == "write-in totals"


def row_html(row: dict) -> str:
    name = (row.get("candidate_ballot_name") or "").strip()
    writein = is_writein(row)
    if writein:
        party = party_name(row.get("party") or "")
        label = f"Write-ins, {party} primary" if party else "Write-ins"
        name_html = esc(label)
    else:
        shown = esc(name)
        if (row.get("winner") or "").strip() == "Y":
            name_html = f"<strong>{shown}</strong> <strong>(Winner)</strong>"
        elif (row.get("primary_result") or "").strip() == "withdrawn":
            name_html = f"{shown} <strong>(Withdrawn)</strong>"
        else:
            name_html = shown
    primary = vote_cell(row.get("primary_votes") or "", row.get("primary_result") or "", row.get("primary_status") or "")
    general = vote_cell(row.get("general_votes") or "", row.get("general_result") or "", row.get("general_status") or "")
    klass = "local-winner" if (row.get("winner") or "").strip() == "Y" else ""
    attr = f' class="{klass}"' if klass else ""
    return (
        f"<tr{attr}><td>{name_html}</td><td>{esc(party_name(row.get('party') or ''))}</td>"
        f'<td class="num">{primary}</td><td class="num">{general}</td></tr>'
    )


def table_html(office: str, seat: str, rows: list[dict]) -> str:
    named = [row for row in rows if not is_writein(row)]
    writeins = [row for row in rows if is_writein(row)]
    order = {"REP": 0, "DEM": 1, "IND": 2, "LIB": 3}
    named.sort(key=lambda row: (order.get((row.get("party") or "").strip(), 9), row.get("candidate_ballot_name") or ""))
    if not writeins and named and all(
        not (row.get("primary_votes") or "").strip() and not (row.get("general_votes") or "").strip()
        for row in named
    ):
        writeins = [
            {
                "candidate_ballot_name": "Write-In Totals",
                "party": "",
                "primary_votes": "",
                "general_votes": "",
                "primary_result": "",
                "general_result": "",
                "primary_status": "not_posted",
                "general_status": "not_posted",
                "winner": "",
            }
        ]
    body = "".join(row_html(row) for row in named + writeins)
    return (
        f'<h3 class="local-office">{esc(office_heading(office, seat))}</h3>'
        '<div class="local-scroll"><table class="local-table" border="1" cellpadding="8" cellspacing="0"><thead><tr>'
        "<th>Candidate</th><th>Party</th><th>Primary votes</th><th>General votes</th>"
        f"</tr></thead><tbody>{body}</tbody></table></div>"
    )


def county_html(name: str, slug: str, info: dict, rows: list[dict]) -> str:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row.get("office_normalized") or "", row.get("seat_or_term") or "")].append(row)
    tables = []
    for office in OFFICES:
        seats = sorted({seat for off, seat in groups if off == office})
        for seat in seats:
            tables.append(table_html(office, seat, groups[(office, seat)]))
    extra = NOTES.get(name, "")
    notes = f'<p class="local-note">{esc(extra)}</p>' if extra else ""
    links = source_links(info, rows)
    source = ""
    if links:
        bits = " · ".join(f'<a href="{esc(url)}">{esc(label)}</a>' for label, url in links)
        source = f'<p class="local-source">Source: {bits}</p>'
    body = "".join(tables) if tables else '<p class="local-note">No 2026 county-office results are posted yet.</p>'
    return (
        f'<section id="{esc(slug)}">'
        f'<h2 class="local-county">{esc(name)} County</h2>'
        f'<p class="local-status">{esc(status_line(info))}</p>'
        f"{notes}{source}{body}</section>"
    )


def page_html(sections: str, buttons: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>2026 Local — WyoVote</title>
    <meta name="description" content="2026 Wyoming county office results by county.">
    <link rel="icon" href="../assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="../../css/styles.css">
    <link rel="stylesheet" href="../preview.css">
  </head>
  <body class="cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <p class="preview-banner" role="status">PREVIEW, not the live site</p>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="../index.html">
          <img src="../assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="../index.html">Home</a></li>
            <li><a href="../archive.html">Archive</a></li>
            <li><a href="../candidates.html" aria-current="page">Candidates</a></li>
            <li><a href="../committees.html">Committees</a></li>
            <li><a href="../counties.html">Counties</a></li>
            <li><a href="../officials.html">Officials</a></li>
            <li><a href="../research.html">Research</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="../candidates.html">← Back to Candidates</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>2026 Local</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap">
          <div class="cand-election" role="group" aria-label="Election">
            <a class="cand-election-btn" data-election="primary" href="../candidates.html">Primary</a>
            <a class="cand-election-btn" data-election="general" href="../candidates.html?e=general">General</a>
            <a class="cand-election-btn" data-election="local" href="2026-local.html" aria-current="true">Local</a>
          </div>
          <p class="local-lead">November 3, 2026 county offices, with the August 18 primary. Choose a county. Earlier years will be added later.</p>
          <ul class="cand-counties">
{buttons}
          </ul>
{sections}
        </div>
      </section>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="../about.html">About</a></li>
            <li><a href="../privacy.html">Privacy</a></li>
            <li><a href="../contact.html">Contact</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""


def load_rows() -> list[dict]:
    path = DATA / "county_offices_2026.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_status(filename: str) -> dict:
    path = DATA / "status" / f"{filename}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_button(path: Path, href: str) -> None:
    text = path.read_text(encoding="utf-8")
    if 'data-election="local"' in text:
        return
    match = re.search(
        r'(<a class="cand-election-btn" data-election="general" href="[^"]+">General</a>)',
        text,
    )
    if not match:
        raise SystemExit(f"no General button in {path}")
    button = f'\n            <a class="cand-election-btn" data-election="local" href="{href}">Local</a>'
    path.write_text(text[: match.end()] + button + text[match.end() :], encoding="utf-8")


def main() -> None:
    rows = load_rows()
    by_county: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_county[row["county"]].append(row)
    sections = []
    buttons = []
    for name, slug, status_name in COUNTIES:
        info = load_status(status_name)
        sections.append(county_html(name, slug, info, by_county.get(name, [])))
        buttons.append(f'            <li><a href="#{slug}">{esc(name)}</a></li>')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page_html("\n".join(sections), "\n".join(buttons)), encoding="utf-8")
    size = OUT.stat().st_size
    if size > 500 * 1024:
        raise SystemExit(f"{OUT} is {size} bytes, over 500 KB")
    ensure_button(PREVIEW / "candidates.html", "candidates/2026-local.html")
    for _name, slug, _status in COUNTIES:
        ensure_button(PREVIEW / "candidates" / "2026-primary" / f"{slug}.html", f"../2026-local.html#{slug}")
    print(f"wrote {OUT.relative_to(ROOT)} ({size} bytes)")


if __name__ == "__main__":
    main()
