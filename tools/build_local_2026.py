#!/usr/bin/env python3
"""Build the preview Local candidate pages in the Primary/General format.

Reads preview/data/local/2026/ and writes the Local hub, one county page per
county, and a simple detail page for each named candidate. The markup uses the
same classes as preview/candidates/2026-primary/.
"""

from __future__ import annotations

import csv
import html
import importlib.util
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import build_candidate_pages as cand

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "preview" / "data" / "local" / "2026"
OUT = ROOT / "preview" / "candidates" / "2026-local.html"
LOCAL_DIR = ROOT / "preview" / "candidates" / "2026-local"
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


def title_token(token: str) -> str:
    if not token:
        return token
    if "-" in token:
        return "-".join(title_token(part) for part in token.split("-"))
    apostrophe = "'" if "'" in token else ("’" if "’" in token else "")
    if apostrophe:
        head, tail = token.split(apostrophe, 1)
        return title_token(head) + apostrophe + title_token(tail)
    if re.fullmatch(r"[A-Za-z]\.", token):
        return token[0].upper() + "."
    if re.fullmatch(r"[A-Za-z]", token):
        return token.upper()
    lower = token.lower()
    if lower in {"jr", "sr"}:
        return lower[:1].upper() + lower[1:]
    if lower in {"ii", "iii", "iv"}:
        return lower.upper()
    if lower.startswith("mc") and len(lower) > 2 and lower[2].isalpha():
        return "Mc" + lower[2].upper() + lower[3:]
    return lower[:1].upper() + lower[1:]


def display_name(name: str, county: str) -> str:
    """Title-case all-caps clerk names. Fremont's one-word surnames stay as printed."""
    raw = (name or "").strip()
    letters = [char for char in raw if char.isalpha()]
    if not raw or not letters or raw != raw.upper():
        return raw
    if county == "Fremont" and " " not in raw:
        return raw
    particles = {"de", "da", "del", "della", "di", "la", "le", "van", "von", "der", "den", "ten", "ter"}
    words = []
    for index, word in enumerate(raw.split()):
        if index and word.lower() in particles:
            words.append(word.lower())
        else:
            words.append(title_token(word))
    return " ".join(words)


def result_word(row: dict) -> str:
    primary = (row.get("primary_result") or "").strip()
    general = (row.get("general_result") or "").strip()
    if primary == "withdrawn":
        return "Withdrawn"
    if (row.get("winner") or "").strip() == "Y" or general == "elected":
        return "Won"
    if general == "defeated":
        return "Lost"
    if primary == "nominated":
        return "Nominated"
    if primary == "defeated":
        return "Lost"
    return ""


def shell(title: str, description: str, depth: int, body: str) -> str:
    """Same header as the 2026 Primary county pages, with Local selected."""
    root = "../" * depth
    css = "../" * (depth + 1) + "css/styles.css"
    return f"""<!DOCTYPE html>
<html lang="en" class="cand-local">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="icon" href="{root}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{css}">
    <link rel="stylesheet" href="{root}preview.css">
  </head>
  <body class="cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <p class="preview-banner" role="status">PREVIEW, not the live site</p>
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
            <li><a href="{root}candidates.html" aria-current="page">Candidates</a></li>
            <li><a href="{root}committees.html">Committees</a></li>
            <li><a href="{root}counties.html">Counties</a></li>
            <li><a href="{root}officials.html">Officials</a></li>
            <li><a href="{root}research.html">Research</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
{body}
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="{root}about.html">About</a></li>
            <li><a href="{root}privacy.html">Privacy</a></li>
            <li><a href="{root}contact.html">Contact</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""


def election_buttons(primary_href: str, general_href: str, local_href: str) -> str:
    return (
        '          <div class="cand-election" role="group" aria-label="Election">\n'
        f'            <a class="cand-election-btn" data-election="primary" href="{esc(primary_href)}">Primary</a>\n'
        f'            <a class="cand-election-btn" data-election="general" href="{esc(general_href)}">General</a>\n'
        f'            <a class="cand-election-btn" data-election="local" href="{esc(local_href)}" aria-current="true">Local</a>\n'
        "          </div>"
    )


def source_html(links: list[tuple[str, str]]) -> str:
    if not links:
        return ""
    bits = " · ".join(f'<a href="{esc(url)}">{esc(label)}</a>' for label, url in links)
    return f"          <p>Source: {bits}</p>"


def list_item(name: str, party: str, result: str, winner: bool, href: str | None) -> str:
    abbr = cand.party_abbr(party) if party else ""
    abbr_html = f' <span class="cand-abbr">{esc(abbr)}</span>' if abbr else ""
    result_html = f' <span class="cand-res">{esc(result)}</span>' if result else ""
    win_html = ' <span class="cand-win" aria-label="Winner">✔</span>' if winner else ""
    if href:
        label = f'<a href="{esc(href)}">{esc(name)}</a>'
    else:
        label = esc(name)
    return f"              <li>{label}{abbr_html}{result_html}{win_html}</li>"


def race_block(title: str, items: list[str]) -> str:
    return (
        '            <section class="cand-race">\n'
        f"            <h3>{esc(title)}</h3>\n"
        '            <ul class="cand-names">\n'
        + "\n".join(items)
        + "\n            </ul>\n"
        "          </section>"
    )


def assign_slugs(rows: list[dict]) -> dict[tuple[str, str], str]:
    used: dict[str, tuple[str, str]] = {}
    slugs: dict[tuple[str, str], str] = {}
    for row in rows:
        if is_writein(row):
            continue
        county = row.get("county") or ""
        name = display_name(row.get("candidate_ballot_name") or "", county)
        key = (county, row.get("candidate_ballot_name") or "")
        slug = cand.person_slug(name)
        if slug in used and used[slug] != key:
            slug = f"{slug}-{county.lower().replace(' ', '-')}"
        used[slug] = key
        slugs[key] = slug
    return slugs


def detail_sentence(name: str, party: str, office: str, row: dict) -> str:
    bits = f"{name} ({party})." if party else f"{name}."
    votes = (row.get("general_votes") or "").strip()
    primary_votes = (row.get("primary_votes") or "").strip()
    general_result = (row.get("general_result") or "").strip()
    primary_result = (row.get("primary_result") or "").strip()
    if general_result == "elected" and votes:
        bits += f" Won the November 3, 2026 general election for {office} with {votes} votes."
    elif general_result == "defeated" and votes:
        bits += f" Lost the November 3, 2026 general election for {office} with {votes} votes."
    elif primary_result == "withdrawn":
        bits += f" Withdrew from the August 18, 2026 primary for {office}."
    elif primary_result == "nominated" and primary_votes:
        bits += f" Won the August 18, 2026 primary for {office} with {primary_votes} votes."
    elif primary_result == "defeated" and primary_votes:
        bits += f" Lost the August 18, 2026 primary for {office} with {primary_votes} votes."
    return bits


def detail_page(row: dict, county_slug: str, county: str, office: str, links: list[tuple[str, str]]) -> str:
    name = display_name(row.get("candidate_ballot_name") or "", county)
    party = party_name(row.get("party") or "")
    primary = vote_cell(row.get("primary_votes") or "", row.get("primary_result") or "", row.get("primary_status") or "")
    general = vote_cell(row.get("general_votes") or "", row.get("general_result") or "", row.get("general_status") or "")
    blurb = detail_sentence(name, party, office, row)
    facts = (
        '<table class="cand-facts">'
        f'<tr><th scope="row">Primary votes</th><td>{primary}</td></tr>'
        f'<tr><th scope="row">General votes</th><td>{general}</td></tr>'
        "</table>"
    )
    sources = ""
    if links:
        items = "\n".join(
            f'                        <li><a href="{esc(url)}">{esc(label)}</a></li>' for label, url in links
        )
        sources = (
            '                      <h2 id="h-sources">Sources</h2>\n'
            '                      <ul class="cand-sources">\n'
            f"{items}\n"
            "                      </ul>"
        )
    meta = f"{office} · {party}" if party else office
    return (
        '      <div class="wrap back-wrap">\n'
        f'        <p class="back-row"><a class="back-btn" href="../{esc(county_slug)}.html">← Back to {esc(county)} County</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{esc(name)}</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f'          <p class="cand-blurb">{esc(blurb)}</p>\n'
        f'          <p class="cand-meta">{esc(meta)}</p>\n'
        f"{result_lines(row, office)}"
        '          <section class="cand-research" aria-labelledby="h-research">\n'
        '                      <h2 id="h-research">Results</h2>\n'
        f"                      {facts}\n"
        f"{sources}\n"
        "                    </section>\n"
        "      </div></section>"
    )


def result_lines(row: dict, office: str) -> str:
    primary_votes = (row.get("primary_votes") or "").strip()
    general_votes = (row.get("general_votes") or "").strip()
    primary_result = (row.get("primary_result") or "").strip()
    general_result = (row.get("general_result") or "").strip()
    if primary_result == "withdrawn":
        primary_text = "Withdrawn."
    elif primary_result == "nominated" and primary_votes:
        primary_text = f"Won, {primary_votes} votes."
    elif primary_result == "defeated" and primary_votes:
        primary_text = f"Lost, {primary_votes} votes."
    elif primary_votes:
        primary_text = f"{primary_votes} votes."
    else:
        primary_text = vote_cell("", primary_result, row.get("primary_status") or "") + "."
    if general_result == "elected" and general_votes:
        general_text = f"{office}, {general_votes} votes, Won."
    elif general_result == "defeated" and general_votes:
        general_text = f"{office}, {general_votes} votes, Lost."
    elif general_result == "not_on_ballot":
        general_text = "Not on ballot."
    else:
        general_text = vote_cell("", general_result, row.get("general_status") or "") + "."
    return (
        f'          <p class="cand-res">Primary result: {esc(primary_text)}</p>\n'
        f'          <p class="cand-res cand-general-line">General result: {esc(general_text)}</p>\n'
    )


def county_races(rows: list[dict], county: str, slugs: dict[tuple[str, str], str]) -> str:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row.get("office_normalized") or "", row.get("seat_or_term") or "")].append(row)
    races = []
    for office in OFFICES:
        seats = sorted(seat for off, seat in groups if off == office)
        for seat in seats:
            members = groups[(office, seat)]
            named = [row for row in members if not is_writein(row)]
            writeins = [row for row in members if is_writein(row)]
            order = {"REP": 0, "DEM": 1, "IND": 2, "LIB": 3}
            named.sort(key=lambda row: (order.get((row.get("party") or "").strip(), 9), display_name(row.get("candidate_ballot_name") or "", county)))
            items = []
            for row in named:
                name = display_name(row.get("candidate_ballot_name") or "", county)
                slug = slugs[(county, row.get("candidate_ballot_name") or "")]
                items.append(
                    list_item(
                        name,
                        party_name(row.get("party") or ""),
                        result_word(row),
                        (row.get("winner") or "").strip() == "Y",
                        f"c/{slug}.html",
                    )
                )
            for row in writeins:
                party = party_name(row.get("party") or "")
                label = f"Write-ins, {party} primary" if party else "Write-ins"
                items.append(list_item(label, "", "", False, None))
            if items:
                races.append(race_block(office_heading(office, seat), items))
    if not races:
        return '          <p class="cand-how">No 2026 county-office results are posted yet.</p>'
    return (
        '          <section class="cand-group">\n'
        '          <h2 class="cand-group-title">County offices</h2>\n'
        '          <div class="cand-race-grid">\n'
        + "\n".join(races)
        + "\n          </div>\n"
        "        </section>"
    )


def county_body(name: str, slug: str, info: dict, rows: list[dict], slugs: dict[tuple[str, str], str]) -> str:
    note = NOTES.get(name, "")
    note_html = f"          <p>{esc(note)}</p>\n" if note else ""
    return (
        '      <div class="wrap back-wrap">\n'
        '        <p class="back-row"><a class="back-btn" href="../../candidates.html">← Back to Candidates</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{esc(name)} County</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"{election_buttons(f'../2026-primary/{slug}.html', f'../2026-primary/{slug}.html?e=general', f'{slug}.html')}\n"
        "          <p>2026 Local, November 3, 2026. August 18 primary included.</p>\n"
        f"          <p>{esc(status_line(info))}</p>\n"
        f"{note_html}"
        f"{source_html(source_links(info, rows))}\n"
        '          <p class="cand-how"><strong>How to use this page.</strong> Races are grouped by office. Click any candidate\'s name to see their details.</p>\n'
        f"{county_races(rows, name, slugs)}\n"
        "      </div></section>"
    )


def hub_body(buttons: str) -> str:
    return (
        '      <div class="wrap back-wrap">\n'
        '        <p class="back-row"><a class="back-btn" href="../candidates.html">← Back to Candidates</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        "          <h1>2026 Local</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"{election_buttons('../candidates.html', '../candidates.html?e=general', '2026-local.html')}\n"
        "          <p>November 3, 2026 county offices, with the August 18 primary. Choose a county. Earlier years will be added later.</p>\n"
        '          <ul class="cand-counties">\n'
        f"{buttons}\n"
        "          </ul>\n"
        "      </div></section>"
    )


def mark_file(path: Path) -> None:
    marker_path = Path(__file__).with_name("mark_outside_links.py")
    spec = importlib.util.spec_from_file_location("mark_outside_links", marker_path)
    marker = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(marker)
    updated, _counts = marker.apply_text(path.read_text(encoding="utf-8"))
    path.write_text(updated, encoding="utf-8")


def ensure_button(path: Path, href: str) -> None:
    text = path.read_text(encoding="utf-8")
    if 'data-election="local"' in text:
        text = re.sub(
            r'(<a class="cand-election-btn" data-election="local" href=")[^"]+(">)',
            rf"\1{href}\2",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        return
    match = re.search(
        r'(<a class="cand-election-btn" data-election="general" href="[^"]+">General</a>)',
        text,
    )
    if not match:
        raise SystemExit(f"no General button in {path}")
    button = f'\n            <a class="cand-election-btn" data-election="local" href="{href}">Local</a>'
    path.write_text(text[: match.end()] + button + text[match.end() :], encoding="utf-8")


def load_rows() -> list[dict]:
    with (DATA / "county_offices_2026.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_status(filename: str) -> dict:
    return json.loads((DATA / "status" / f"{filename}.json").read_text(encoding="utf-8"))


def main() -> None:
    rows = load_rows()
    by_county: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_county[row["county"]].append(row)
    slugs = assign_slugs(rows)
    if LOCAL_DIR.exists():
        shutil.rmtree(LOCAL_DIR)
    LOCAL_DIR.mkdir(parents=True)
    (LOCAL_DIR / "c").mkdir()
    buttons = []
    pages = 0
    for name, slug, status_name in COUNTIES:
        info = load_status(status_name)
        county_rows = by_county.get(name, [])
        links = source_links(info, county_rows)
        county_path = LOCAL_DIR / f"{slug}.html"
        county_path.write_text(
            shell(
                f"{name} County — 2026 Local — WyoVote",
                f"2026 county office candidates in {name} County.",
                2,
                county_body(name, slug, info, county_rows, slugs),
            ),
            encoding="utf-8",
        )
        mark_file(county_path)
        pages += 1
        seen = set()
        for row in county_rows:
            if is_writein(row):
                continue
            key = (name, row.get("candidate_ballot_name") or "")
            if key in seen:
                continue
            seen.add(key)
            office = office_heading(row.get("office_normalized") or "", row.get("seat_or_term") or "")
            detail_path = LOCAL_DIR / "c" / f"{slugs[key]}.html"
            detail_path.write_text(
                shell(
                    f"{display_name(row.get('candidate_ballot_name') or '', name)} — 2026 Local — WyoVote",
                    detail_sentence(
                        display_name(row.get("candidate_ballot_name") or "", name),
                        party_name(row.get("party") or ""),
                        office,
                        row,
                    )[:180],
                    3,
                    detail_page(row, slug, name, office, links),
                ),
                encoding="utf-8",
            )
            mark_file(detail_path)
            pages += 1
        buttons.append(f'            <li><a href="2026-local/{slug}.html">{esc(name)}</a></li>')
    OUT.write_text(
        shell(
            "2026 Local — WyoVote",
            "2026 Wyoming county office candidates by county.",
            1,
            hub_body("\n".join(buttons)),
        ),
        encoding="utf-8",
    )
    mark_file(OUT)
    ensure_button(PREVIEW / "candidates.html", "candidates/2026-local.html")
    for _name, slug, _status in COUNTIES:
        ensure_button(
            PREVIEW / "candidates" / "2026-primary" / f"{slug}.html",
            f"../2026-local/{slug}.html",
        )
    print(f"wrote {pages + 1} local pages")


if __name__ == "__main__":
    main()


