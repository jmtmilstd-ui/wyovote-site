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
import sys
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
    "Fremont": "Fremont's general results list surnames only.",
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


def list_item(name: str, party: str, result: str, href: str | None) -> str:
    abbr = cand.party_abbr(party) if party else ""
    abbr_html = f' <span class="cand-abbr">{esc(abbr)}</span>' if abbr else ""
    result_html = f' <span class="cand-res">{esc(result)}</span>' if result else ""
    if href:
        label = f'<a href="{esc(href)}">{esc(name)}</a>'
    else:
        label = esc(name)
    return f"              <li>{label}{abbr_html}{result_html}</li>"


PRECINCT_CSVS = (
    DATA / "precinct_committee_2026_part1.csv",
    DATA / "precinct_committee_2026_part2.csv",
)
PRECINCT_MISSING = {"Johnson", "Laramie", "Platte"}
PRECINCT_LABEL = {"Fremont": "Partial.", "Goshen": "Unofficial."}
PRECINCT_AS_OF = "November 13, 2026"
PARTY_TITLE = {"REP": "Republican", "DEM": "Democratic"}


def precinct_rows() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for path in PRECINCT_CSVS:
        if not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                grouped[row["county"]].append(row)
    return grouped


def write_in_total(name: str) -> bool:
    folded = re.sub(r"[^a-z]", "", (name or "").casefold())
    return folded in {"writeintotals", "writeintotal"}


def being_verified(notes: str) -> bool:
    low = (notes or "").lower()
    return (
        "uncertain" in low
        or "confirm spelling" in low
        or "confirm against" in low
        or "seat inferred" in low
    )


def precinct_item(row: dict) -> str:
    verified = ' <span class="cand-res">being verified</span>' if being_verified(row.get("notes") or "") else ""
    if write_in_total(row.get("candidate_name") or ""):
        votes = (row.get("votes") or "").strip()
        return f"              <li>Write-in (not named): {esc(votes)}{verified}</li>"
    bits = [esc(row.get("candidate_name") or "")]
    votes = (row.get("votes") or "").strip()
    if votes:
        bits.append(f'<span class="cand-res">{esc(votes)}</span>')
    if (row.get("result") or "").strip() == "elected":
        bits.append('<span class="cand-res">Elected</span>')
    if being_verified(row.get("notes") or ""):
        bits.append('<span class="cand-res">being verified</span>')
    return "              <li>" + " ".join(bits) + "</li>"


def precinct_section(county: str, rows: list[dict] | None = None) -> str:
    """Precinct committee races, in the same cards as the county offices."""
    if rows is None:
        rows = precinct_rows().get(county, [])
    if county in PRECINCT_MISSING or not rows:
        return (
            '          <section class="cand-group">\n'
            '          <h2 class="cand-group-title">Precinct Committee</h2>\n'
            "          <p>Precinct committee results not yet posted by the county.</p>\n"
            "        </section>"
        )
    label = PRECINCT_LABEL.get(county, "Official.")
    url = (rows[0].get("source_url") or "").strip()
    link_label = "Unofficial primary results" if county == "Goshen" else "Official primary results"
    source = ""
    if url:
        source = (
            f'          <p>Source: <a href="{esc(url)}">{esc(link_label)}</a> '
            '<span class="ext">(leaves WyoVote)</span></p>\n'
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
        f"          <p>{esc(label)} As of {PRECINCT_AS_OF}.</p>\n"
        f"{source}"
        "        </section>"
    ]
    for precinct, parties in grouped.items():
        cards = []
        for party, seats in parties.items():
            party_title = PARTY_TITLE.get(party, party)
            for seat, members in seats.items():
                cards.append(race_block(f"{party_title} {seat}", [precinct_item(row) for row in members]))
        blocks.append(
            '          <section class="cand-group">\n'
            f"          <h2 class=\"cand-group-title\">Precinct {esc(precinct)}</h2>\n"
            '          <div class="cand-race-grid">\n'
            + "\n".join(cards)
            + "\n          </div>\n"
            "        </section>"
        )
    return "\n".join(blocks)


def race_block(title: str, items: list[str]) -> str:
    return (
        '            <section class="cand-race">\n'
        f"            <h3>{esc(title)}</h3>\n"
        '            <ul class="cand-names">\n'
        + "\n".join(items)
        + "\n            </ul>\n"
        "          </section>"
    )


NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}


def name_tokens(name: str) -> list[str]:
    tokens = []
    for raw in name.replace(".", " ").split():
        token = raw.strip(".")
        if token and token.lower() not in NAME_SUFFIXES:
            tokens.append(token)
    return tokens


def given_compatible(left: list[str], right: list[str]) -> bool:
    if not left or not right:
        return False
    short, long = (left, right) if len(left) <= len(right) else (right, left)
    for index, token in enumerate(short):
        other = long[index]
        if token.casefold() == other.casefold():
            continue
        if len(token) == 1 and other[:1].casefold() == token.casefold():
            continue
        if len(other) == 1 and token[:1].casefold() == other.casefold():
            continue
        return False
    return True


def same_person(left: str, right: str) -> bool:
    left_tokens, right_tokens = name_tokens(left), name_tokens(right)
    if len(left_tokens) < 2 or len(right_tokens) < 2:
        return False
    if left_tokens[-1].casefold() != right_tokens[-1].casefold():
        return False
    return given_compatible(left_tokens[:-1], right_tokens[:-1])


def fuller_name(left: str, right: str) -> str:
    if len(name_tokens(left)) != len(name_tokens(right)):
        return left if len(name_tokens(left)) > len(name_tokens(right)) else right
    return left if len(left) >= len(right) else right


def fill_result(row: dict, other: dict) -> None:
    for field in ("primary_votes", "general_votes"):
        if not (row.get(field) or "").strip() and (other.get(field) or "").strip():
            row[field] = other[field]
    if (row.get("primary_result") or "") in {"", "n/a", "not_on_ballot"} and (other.get("primary_result") or "") in {
        "nominated",
        "defeated",
        "withdrawn",
    }:
        row["primary_result"] = other["primary_result"]
        row["primary_status"] = other.get("primary_status") or row.get("primary_status")
    if (row.get("general_result") or "") in {"", "n/a", "not_on_ballot"} and (other.get("general_result") or "") in {
        "elected",
        "defeated",
    }:
        row["general_result"] = other["general_result"]
        row["general_status"] = other.get("general_status") or row.get("general_status")
    if (other.get("winner") or "").strip() == "Y":
        row["winner"] = "Y"


# Full names from the Fremont primary ballot. Wagon and Riggs stay surnames.
FREMONT_PRIMARY_NAMES = {
    ("County Commissioner", "REP", "mossburg"): "David Mossburg",
    ("County Commissioner", "REP", "stanley"): "Shanell Stanley",
    ("County Commissioner", "REP", "kessler"): "Steff Kessler",
    ("County Clerk", "REP", "freese"): "Julie A Freese",
    ("County Treasurer", "REP", "anderson"): "James A. Anderson",
    ("County Sheriff", "REP", "zerga"): "John Zerga",
    ("County Attorney", "REP", "wyatt"): "Micah Wyatt",
    ("County Coroner", "REP", "ivie"): "Erin Ivie",
    ("Clerk of District Court", "REP", "sanchez"): "Amanda R. Sanchez",
}


def fremont_full_name(row: dict, peers: list[dict]) -> str | None:
    tokens = name_tokens(row.get("candidate_ballot_name") or "")
    if row.get("county") != "Fremont" or len(tokens) != 1:
        return None
    surname = tokens[0].casefold()
    mapped = FREMONT_PRIMARY_NAMES.get(((row.get("office_normalized") or ""), (row.get("party") or ""), surname))
    if mapped:
        return mapped
    matches = []
    for other in peers:
        if other is row or is_writein(other):
            continue
        if (other.get("party") or "") != (row.get("party") or ""):
            continue
        if (other.get("primary_result") or "") != "nominated":
            continue
        other_tokens = name_tokens(other.get("candidate_ballot_name") or "")
        if len(other_tokens) < 2 or other_tokens[-1].casefold() != surname:
            continue
        matches.append(other.get("candidate_ballot_name") or "")
    if len(matches) == 1:
        return matches[0]
    return None


def merge_race(members: list[dict]) -> tuple[list[dict], list[str]]:
    """Fold same-person variants and an unambiguous Fremont surname into one row."""
    notes = []
    remaining = [dict(row) for row in members if not is_writein(row)]
    folded = []
    for row in remaining:
        full = fremont_full_name(row, remaining)
        if not full:
            continue
        target = next((other for other in remaining if other is not row and other.get("candidate_ballot_name") == full), None)
        if target is None:
            notes.append(
                f"{row.get('county')} {row.get('office_normalized')}: "
                f"{row.get('candidate_ballot_name')} -> {full}"
            )
            row["candidate_ballot_name"] = full
            continue
        fill_result(target, row)
        folded.append(row)
        notes.append(
            f"{row.get('county')} {row.get('office_normalized')}: "
            f"{row.get('candidate_ballot_name')} + {full} -> {full}"
        )
    remaining = [row for row in remaining if row not in folded]
    consumed: set[int] = set()
    partners: dict[int, list[dict]] = defaultdict(list)
    for index, left in enumerate(remaining):
        for right in remaining[index + 1 :]:
            if (left.get("party") or "") != (right.get("party") or ""):
                continue
            if same_person(left.get("candidate_ballot_name") or "", right.get("candidate_ballot_name") or ""):
                partners[id(left)].append(right)
                partners[id(right)].append(left)
    ranked = sorted(
        remaining,
        key=lambda row: (
            -len(name_tokens(row.get("candidate_ballot_name") or "")),
            -len(row.get("candidate_ballot_name") or ""),
        ),
    )
    merged = []
    for row in ranked:
        if id(row) in consumed:
            continue
        current = dict(row)
        for mate in partners[id(row)]:
            if id(mate) in consumed:
                continue
            rivals = [other for other in partners[id(mate)] if other is not row and id(other) not in consumed]
            if rivals:
                continue
            short = mate.get("candidate_ballot_name") or ""
            full = fuller_name(current.get("candidate_ballot_name") or "", short)
            if full == short:
                current, mate = dict(mate), current
                short = mate.get("candidate_ballot_name") or ""
            fill_result(current, mate)
            current["candidate_ballot_name"] = full
            notes.append(
                f"{row.get('county')} {row.get('office_normalized')}: {short} + {full} -> {full}"
            )
            consumed.add(id(mate))
        consumed.add(id(row))
        merged.append(current)
    return merged, notes


def prepare_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if is_writein(row):
            continue
        grouped[(row.get("county") or "", row.get("office_normalized") or "", row.get("seat_or_term") or "")].append(row)
    prepared = []
    notes = []
    for members in grouped.values():
        merged, race_notes = merge_race(members)
        prepared.extend(merged)
        notes.extend(race_notes)
    return prepared, notes


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
            members = [row for row in groups[(office, seat)] if not is_writein(row)]
            order = {"REP": 0, "DEM": 1, "IND": 2, "LIB": 3}
            members.sort(key=lambda row: (order.get((row.get("party") or "").strip(), 9), display_name(row.get("candidate_ballot_name") or "", county)))
            items = []
            for row in members:
                name = display_name(row.get("candidate_ballot_name") or "", county)
                slug = slugs[(county, row.get("candidate_ballot_name") or "")]
                items.append(
                    list_item(
                        name,
                        party_name(row.get("party") or ""),
                        result_word(row),
                        f"c/{slug}.html",
                    )
                )
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
        f"{precinct_section(name)}\n"
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


def insert_precinct_sections() -> None:
    """Add the Precinct Committee section to county pages already on disk."""
    token = "      </div></section>\n    </main>"
    pages = 0
    for name, slug, _status in COUNTIES:
        path = LOCAL_DIR / f"{slug}.html"
        text = path.read_text(encoding="utf-8")
        if token not in text:
            raise SystemExit(f"no insert point in {path}")
        block = precinct_section(name)
        start = text.find('          <section class="cand-group">\n          <h2 class="cand-group-title">Precinct Committee</h2>')
        if start != -1:
            end = text.find(token, start)
            text = text[:start] + block + "\n" + text[end:]
        else:
            text = text.replace(token, block + "\n" + token, 1)
        path.write_text(text, encoding="utf-8")
        mark_file(path)
        pages += 1
    print(f"added precinct committee to {pages} county pages")


def main() -> None:
    rows, merge_notes = prepare_rows(load_rows())
    for note in merge_notes:
        print("merge:", note)
    if not merge_notes:
        print("merge: none")
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
    if "--precinct-only" in sys.argv:
        insert_precinct_sections()
    else:
        main()


