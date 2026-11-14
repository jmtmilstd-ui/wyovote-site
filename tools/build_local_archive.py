#!/usr/bin/env python3
"""Build the preview 2024 and 2022 Local pages with the 2026 entry format.

County chooser, one page per county, and a detail page for each named
candidate. Missing counties get a plain note instead of an empty section.
Does not write the live root.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import build_local_2026 as local

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
DATA_ROOT = PREVIEW / "data" / "local"
MISSING_NOTE = "Results not yet available from the county"

YEARS = {
    "2022": {"primary": "August 16, 2022", "general": "November 8, 2022"},
    "2024": {"primary": "August 20, 2024", "general": "November 5, 2024"},
}

SOURCE_LABELS = {
    "primary": "Primary results",
    "general": "General results",
    "primary-precinct": "Primary precinct results",
    "primary-precinct2": "Primary precinct results",
    "primary-precincts": "Primary precinct results",
    "general-precinct": "General precinct results",
    "primary-b": "Primary results",
    "primary-alt": "Primary results",
    "general-alt": "General results",
    "primary-recount": "Primary recount",
    "primary-pc": "Precinct committee results",
    "primary-pc-dem": "Democratic precinct committee results",
    "primary-pc-rep": "Republican precinct committee results",
    "primary-pc-recount": "Precinct committee recount",
}

# Counties whose whole Local year, or one side of it, was not posted.
# A missing side is a note, not an empty race list.
GAPS = {
    "2022": {"Fremont": "all", "Sublette": "committee"},
    "2024": {"Fremont": "primary-committee"},
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_offices(year: str) -> list[dict]:
    return read_csv(DATA_ROOT / year / f"county_offices_{year}.csv")


def load_precinct(year: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    folder = DATA_ROOT / year
    paths = sorted(folder.glob(f"precinct_committee_{year}*.csv"))
    for path in paths:
        for row in read_csv(path):
            grouped[row["county"]].append(row)
    return grouped


def load_sources(year: str) -> dict[str, list[tuple[str, str]]]:
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    path = DATA_ROOT / year / "sources" / "sources.csv"
    seen: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(path):
        url = (row.get("url") or "").strip()
        if not url.startswith("http") or url in seen[row["county"]]:
            continue
        seen[row["county"]].add(url)
        label = SOURCE_LABELS.get(row.get("document") or "", "Results")
        grouped[row["county"]].append((label, url))
    return grouped


def archive_shell(title: str, description: str, depth: int, body: str) -> str:
    """Archive header, with the same Local page classes as 2026."""
    root = "../" * depth
    css = "../" * (depth + 1) + "css/styles.css"
    return f"""<!DOCTYPE html>
<html lang="en" class="cand-local">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{local.esc(title)}</title>
    <meta name="description" content="{local.esc(description)}">
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
            <li><a href="{root}archive/committees.html">Committees</a></li>
            <li><a href="{root}archive/counties.html">Counties</a></li>
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


def field_status(rows: list[dict], field: str) -> str:
    values = {(row.get(field) or "").strip() for row in rows}
    values.discard("")
    if not values:
        return "not_posted"
    if values <= {"official"}:
        return "official"
    if "unofficial" in values:
        return "unofficial"
    if values <= {"not_posted", "not_found", "not_yet_posted"}:
        return "not_posted"
    return "official"


def county_info(rows: list[dict]) -> dict:
    primary = field_status(rows, "primary_status")
    general = field_status(rows, "general_status")
    if primary == "official" and general == "official":
        kind = "complete"
    elif primary == "not_posted" and general == "not_posted":
        kind = "not_yet_posted"
    else:
        kind = "partial"
    return {"status": kind, "primary_status": primary, "general_status": general}


def line_votes(row: dict) -> str:
    """Vote total that belongs on the Won/Lost line. Blank when the sheet printed none."""
    word = local.result_word(row)
    general = (row.get("general_votes") or "").strip()
    primary = (row.get("primary_votes") or "").strip()
    general_result = (row.get("general_result") or "").strip()
    if word in {"Won", "Lost"} and general_result in {"elected", "defeated"}:
        return general
    if word in {"Won", "Lost", "Nominated", "Withdrawn"}:
        return primary
    return general or primary


def county_section(rows: list[dict], county: str, slugs: dict[tuple[str, str], str]) -> str:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if local.is_writein(row):
            continue
        groups[(row.get("office_normalized") or "", row.get("seat_or_term") or "")].append(row)
    races = []
    for office in local.OFFICES:
        seats = sorted(seat for off, seat in groups if off == office)
        for seat in seats:
            members = groups[(office, seat)]
            order = {"REP": 0, "DEM": 1, "IND": 2, "LIB": 3, "CST": 4}
            members.sort(
                key=lambda row: (
                    order.get((row.get("party") or "").strip(), 9),
                    local.display_name(row.get("candidate_ballot_name") or "", county),
                )
            )
            items = []
            for row in members:
                name = local.display_name(row.get("candidate_ballot_name") or "", county)
                slug = slugs[(county, row.get("candidate_ballot_name") or "")]
                items.append(
                    local.list_item(
                        name,
                        local.party_name(row.get("party") or ""),
                        local.result_word(row),
                        f"c/{slug}.html",
                        line_votes(row) or None,
                    )
                )
            if items:
                races.append(local.race_block(local.office_heading(office, seat), items))
    if not races:
        return ""
    return (
        '          <section class="cand-group">\n'
        '          <h2 class="cand-group-title">County offices</h2>\n'
        '          <div class="cand-race-grid">\n'
        + "\n".join(races)
        + "\n          </div>\n"
        "        </section>"
    )


def missing_section(title: str) -> str:
    return (
        '          <section class="cand-group">\n'
        f'          <h2 class="cand-group-title">{local.esc(title)}</h2>\n'
        f"          <p>{MISSING_NOTE}</p>\n"
        "        </section>"
    )


def precinct_blocks(county: str, rows: list[dict]) -> str:
    unofficial = any("unofficial" in (row.get("notes") or "").lower() for row in rows)
    label = "Unofficial." if unofficial else "Official."
    url = ""
    for row in rows:
        url = (row.get("source_url") or "").strip()
        if url.startswith("http"):
            break
    link_label = "Unofficial primary results" if unofficial else "Official primary results"
    source = ""
    if url.startswith("http"):
        source = (
            f'          <p>Source: <a href="{local.esc(url)}">{link_label}</a></p>\n'
        )
    grouped: dict[str, dict[str, dict[str, list[dict]]]] = {}
    for row in rows:
        precinct = row.get("precinct") or ""
        party = row.get("party") or ""
        seat = row.get("seat") or ""
        grouped.setdefault(precinct, {})
        grouped[precinct].setdefault(party, {})
        grouped[precinct][party].setdefault(seat, []).append(row)
    blocks = [
        '          <section class="cand-group">\n'
        '          <h2 class="cand-group-title">Precinct Committee</h2>\n'
        f"          <p>{local.esc(label)} As of November 13, 2026.</p>\n"
        f"{source}"
        "        </section>"
    ]
    for precinct, parties in grouped.items():
        cards = []
        for party, seats in parties.items():
            party_title = local.PARTY_TITLE.get(party, party)
            for seat, members in seats.items():
                cards.append(
                    local.race_block(
                        f"{party_title} {seat}",
                        [local.precinct_item(row, county) for row in members],
                    )
                )
        blocks.append(
            '          <section class="cand-group">\n'
            f'          <h2 class="cand-group-title">Precinct {local.esc(precinct)}</h2>\n'
            '          <div class="cand-race-grid">\n'
            + "\n".join(cards)
            + "\n          </div>\n"
            "        </section>"
        )
    return "\n".join(blocks)


def source_bits(source_key: str, sources: dict[str, list[tuple[str, str]]], info: dict) -> str:
    links = []
    for label, url in sources.get(source_key, []):
        shown = label
        if info.get("primary_status") == "unofficial" and label == "Primary results":
            shown = "Unofficial primary results"
        if info.get("general_status") == "unofficial" and label == "General results":
            shown = "Unofficial general results"
        links.append((shown, url))
    html = local.source_html(links)
    return f"{html}\n" if html else ""


def county_body(
    year: str,
    name: str,
    slug: str,
    rows: list[dict],
    precinct: list[dict],
    slugs: dict[tuple[str, str], str],
    sources: dict[str, list[tuple[str, str]]],
    source_key: str,
) -> str:
    dates = YEARS[year]
    gap = GAPS[year].get(name, "")
    info = county_info(rows) if rows else {"status": "not_yet_posted", "primary_status": "not_posted", "general_status": "not_posted"}
    primary_href = f"../{year}-primary/{slug}.html"
    general_href = f"../{year}-primary/{slug}.html?e=general"
    note = ""
    if name == "Fremont" and rows:
        note = "          <p>Fremont's general results list surnames only.</p>\n"
    parts = [
        '      <div class="wrap back-wrap">\n'
        f'        <p class="back-row"><a class="back-btn" href="../{year}-local.html">← Back to {year} Local</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{local.esc(name)} County</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"{local.election_buttons(primary_href, general_href, f'{slug}.html')}\n"
        f"          <p>{year} Local, {dates['general']}. {dates['primary']} primary included.</p>\n"
    ]
    if gap == "all" or not rows and not precinct:
        parts.append(f"          <p>{MISSING_NOTE}</p>\n")
        parts.append(source_bits(source_key, sources, info))
        parts.append("      </div></section>")
        return "".join(parts)
    if rows:
        parts.append(f"          <p>{local.esc(local.status_line(info))}</p>\n")
    parts.append(note)
    parts.append(source_bits(source_key, sources, info))
    parts.append(
        '          <p class="cand-how"><strong>How to use this page.</strong> '
        "Races are grouped by office. Click any candidate's name to see their details.</p>\n"
    )
    if gap in {"primary-committee"} and field_status(rows, "primary_status") == "not_posted":
        parts.append(f"          <p>{MISSING_NOTE}</p>\n")
    if rows:
        parts.append(county_section(rows, name, slugs) + "\n")
    else:
        parts.append(missing_section("County offices") + "\n")
    if precinct and gap not in {"committee", "primary-committee", "all"}:
        parts.append(precinct_blocks(name, precinct) + "\n")
    else:
        parts.append(missing_section("Precinct Committee") + "\n")
    parts.append("      </div></section>")
    return "".join(parts)


def hub_body(year: str) -> str:
    dates = YEARS[year]
    buttons = "\n".join(
        f'            <li><a href="{year}-local/{slug}.html">{local.esc(name)}</a></li>'
        for name, slug, _status in local.COUNTIES
    )
    return (
        '      <div class="wrap back-wrap">\n'
        '        <p class="back-row"><a class="back-btn" href="../archive/candidates.html">← Back to Archive</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{year} Local</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"{local.election_buttons(f'{year}-primary/index.html', f'{year}-primary/index.html?e=general', f'{year}-local.html')}\n"
        f"          <p>{dates['general']} county offices, with the {dates['primary']} primary. Choose a county.</p>\n"
        '          <ul class="cand-counties">\n'
        f"{buttons}\n"
        "          </ul>\n"
        "      </div></section>"
    )


def build_year(year: str) -> int:
    rows, _notes = local.prepare_rows(load_offices(year))
    by_county: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_county[row["county"]].append(row)
    precinct = load_precinct(year)
    sources = load_sources(year)
    slugs = local.assign_slugs(rows)
    dates = YEARS[year]
    local_dir = PREVIEW / "candidates" / f"{year}-local"
    local_dir.mkdir(parents=True, exist_ok=True)
    (local_dir / "c").mkdir(exist_ok=True)
    pages = 0
    hub = PREVIEW / "candidates" / f"{year}-local.html"
    hub.write_text(
        archive_shell(
            f"{year} Local — WyoVote",
            f"{year} Wyoming county office candidates by county.",
            1,
            hub_body(year),
        ),
        encoding="utf-8",
    )
    local.mark_file(hub)
    pages += 1
    for name, slug, source_key in local.COUNTIES:
        county_rows = by_county.get(name, [])
        path = local_dir / f"{slug}.html"
        path.write_text(
            archive_shell(
                f"{name} County — {year} Local — WyoVote",
                f"{year} county office candidates in {name} County.",
                2,
                county_body(
                    year,
                    name,
                    slug,
                    county_rows,
                    precinct.get(name, []),
                    slugs,
                    sources,
                    source_key,
                ),
            ),
            encoding="utf-8",
        )
        local.mark_file(path)
        pages += 1
        seen = set()
        links = list(sources.get(source_key, []))
        for row in county_rows:
            if local.is_writein(row):
                continue
            key = (name, row.get("candidate_ballot_name") or "")
            if key in seen:
                continue
            seen.add(key)
            office = local.office_heading(row.get("office_normalized") or "", row.get("seat_or_term") or "")
            detail = local_dir / "c" / f"{slugs[key]}.html"
            shown = local.display_name(row.get("candidate_ballot_name") or "", name)
            detail.write_text(
                archive_shell(
                    f"{shown} — {year} Local — WyoVote",
                    local.detail_sentence(
                        shown,
                        local.party_name(row.get("party") or ""),
                        office,
                        row,
                        dates["primary"],
                        dates["general"],
                    )[:180],
                    3,
                    local.detail_page(
                        row,
                        slug,
                        name,
                        office,
                        links,
                        dates["primary"],
                        dates["general"],
                    ),
                ),
                encoding="utf-8",
            )
            local.mark_file(detail)
            pages += 1
    return pages


def add_local_tabs() -> int:
    changed = 0
    for year in YEARS:
        folder = PREVIEW / "candidates" / f"{year}-primary"
        for path in sorted(folder.glob("*.html")):
            text = path.read_text(encoding="utf-8")
            if 'data-election="local"' in text:
                continue
            if path.name == "index.html":
                local_href = f"../{year}-local.html"
                general = 'href="index.html?e=general"'
            else:
                local_href = f"../{year}-local/{path.name}"
                general = f'href="{path.name}?e=general"'
            needle = f'<a class="cand-election-btn" data-election="general" {general}>General</a>'
            insert = (
                needle
                + f'\n            <a class="cand-election-btn" data-election="local" href="{local_href}">Local</a>'
            )
            if needle not in text:
                raise SystemExit(f"no General button in {path}")
            path.write_text(text.replace(needle, insert, 1), encoding="utf-8")
            changed += 1
    archive = PREVIEW / "archive" / "candidates.html"
    text = archive.read_text(encoding="utf-8")
    if "2024-local.html" in text and "2022-local.html" in text:
        return changed
    text2 = text.replace(
        '<a href="../candidates/2024-primary/index.html?e=general">2024 General</a>',
        '<a href="../candidates/2024-primary/index.html?e=general">2024 General</a> · <a href="../candidates/2024-local.html">2024 Local</a>',
    ).replace(
        '<a href="../candidates/2022-primary/index.html?e=general">2022 General</a>',
        '<a href="../candidates/2022-primary/index.html?e=general">2022 General</a> · <a href="../candidates/2022-local.html">2022 Local</a>',
    )
    if text2 == text:
        raise SystemExit("archive candidate links were not updated")
    archive.write_text(text2, encoding="utf-8")
    changed += 1
    return changed


def main() -> None:
    pages = 0
    for year in YEARS:
        count = build_year(year)
        print(f"{year}: {count} local pages")
        pages += count
    tabs = add_local_tabs()
    print(f"updated {tabs} existing preview pages")
    print(f"wrote {pages} local pages")


if __name__ == "__main__":
    main()
