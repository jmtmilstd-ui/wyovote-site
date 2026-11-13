#!/usr/bin/env python3
"""Build one preview web page for each published WyoVote report PDF.

The PDF builders (ranking.py, build_counties.py, build_committees_year.py,
combined_ratings/build_combined.py) are not in this repository. These pages
read the tables those builders already published in reports/, so the web page
shows the same ranks and labels. The PDF file is left unchanged and is linked
only as Print (PDF).

    python3 tools/build_report_pages.py --kind county
    python3 tools/build_report_pages.py --kind committee
    python3 tools/build_report_pages.py --kind ratings
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
REPORTS = ROOT / "reports"
OUT = PREVIEW / "reports"
CURRENT_YEAR = "2026"

NAV = """
            <li><a href="{root}index.html"{home}>Home</a></li>
            <li><a href="{root}archive.html"{archive}>Archive</a></li>
            <li><a href="{root}candidates.html">Candidates</a></li>
            <li><a href="{root}committees.html"{committees}>Committees</a></li>
            <li><a href="{root}counties.html"{counties}>Counties</a></li>
            <li><a href="{root}officials.html">Officials</a></li>
            <li><a href="{root}research.html">Research</a></li>
            <li><a class="site-map-link" href="{root}site-map.html">Site Map</a></li>
"""


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def pdf_words(path: Path) -> list[list[tuple[float, float, str]]]:
    """One list of (x, y, word) lines for each page."""
    raw = subprocess.check_output(["pdftotext", "-tsv", str(path), "-"], text=True, errors="replace")
    pages: list[list[tuple[float, float, str]]] = []
    words: list[tuple[float, float, str]] = []
    for line in raw.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        text = parts[11].strip()
        if not text or text.startswith("###"):
            if text == "###PAGE###" and words:
                pages.append(_cluster(words))
                words = []
            continue
        words.append((float(parts[6]), float(parts[7]), text))
    if words:
        pages.append(_cluster(words))
    return pages


def _cluster(words: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    return sorted(words, key=lambda item: (item[1], item[0]))


def lines_of(words: list[tuple[float, float, str]], gap: float = 3.0) -> list[list[tuple[float, str]]]:
    if not words:
        return []
    rows: list[list[tuple[float, str]]] = []
    current: list[tuple[float, str]] = []
    top = words[0][1]
    for left, y, text in words:
        if current and y - top > gap:
            rows.append(sorted(current))
            current = []
        current.append((left, text))
        top = y if not current[:-1] else top
        if len(current) == 1:
            top = y
    if current:
        rows.append(sorted(current))
    return rows


def line_text(row: list[tuple[float, str]]) -> str:
    return " ".join(text for _left, text in row)


def layout_text(path: Path) -> str:
    return subprocess.check_output(["pdftotext", "-layout", str(path), "-"], text=True, errors="replace")


def kind_of(path: Path) -> str | None:
    """Published wyovote_* reports. Older one-off filenames are handled later."""
    name = path.name
    if not name.startswith("wyovote_"):
        return None
    if re.search(r"County_\d+_", name) or "Counties_All" in name:
        return "county"
    if "Committee_" in name or "Committees_All" in name:
        return "committee"
    if "Ratings_" in name:
        return "ratings"
    return None


def is_summary_pdf(path: Path) -> bool:
    name = path.name
    return "Counties_All" in name or "Committees_All" in name


def slug_for(path: Path, kind: str) -> tuple[str, str]:
    """Return (year, filename stem under reports/year/kind/)."""
    year = path.parent.name if path.parent.name.isdigit() else "2023"
    stem = path.stem
    match = re.search(r"(?:^|_)County_(\d+)_([A-Za-z0-9_]+)_113", stem)
    if match and "Committee_" not in stem:
        return year, match.group(1) + "-" + match.group(2).replace("_", "-").lower()
    if "Counties_All" in stem or "all-legislative-counties" in stem:
        return year, "all"
    if stem.startswith("2023-") and stem != "2023-all-legislative-counties":
        return "2023", stem.split("-", 1)[1]
    match = re.search(r"Committee_(\d+)_([A-Za-z0-9_]+)_112", stem)
    if match:
        return year, match.group(1) + "-" + match.group(2).replace("_", "-").lower()
    if "Committees_All" in stem or stem == "committees":
        return year, "all"
    if re.match(r"\d\d-", stem):
        return year, stem
    if "Ranked_1p" in stem or "_105" in stem:
        return year, "ranked-one-page"
    if "Alpha_1p" in stem or "_106" in stem:
        return year, "alpha-one-page"
    if "Ranked" in stem or "_103" in stem:
        return year, "ranked"
    if "Alpha" in stem or "_104" in stem:
        return year, "alpha"
    return year, re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def page_path(pdf: Path, kind: str) -> Path:
    year, slug = slug_for(pdf, kind)
    folder = {"county": "county", "committee": "committee", "ratings": "ratings"}[kind]
    return OUT / year / folder / f"{slug}.html"


def load_officials() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in (PREVIEW / "officials").glob("*.html"):
        if path.name == "index.html" or path.name.endswith("-deep.html"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
        if not match:
            continue
        name = re.sub(r"<[^>]+>", "", match.group(1))
        name = re.sub(r"\s+", " ", html.unescape(name)).strip()
        found[norm(name)] = path
    return found


def linked_name(name: str, officials: dict[str, Path], page: Path) -> str:
    key = norm(name)
    target = officials.get(key)
    if target is None:
        hits = [path for label, path in officials.items() if label.endswith(" " + key) or label.endswith(key)]
        if len(hits) == 1:
            target = hits[0]
    if target is None:
        return esc(name)
    href = Path(os.path.relpath(target, page.parent)).as_posix()
    return f'<a href="{esc(href)}">{esc(name)}</a>'


def words_between(row: list[tuple[float, str]], start: float, end: float) -> str:
    chosen = [text for left, text in row if start <= left < end]
    return " ".join(chosen).strip()


def parse_member_sections(pages: list[list[tuple[float, float, str]]]) -> list[tuple[str, list[dict]]]:
    """House and Senate member tables from the county and committee PDFs."""
    lined: list[tuple[float, list[tuple[float, str]]]] = []
    for page in pages:
        words = sorted(page, key=lambda item: (item[1], item[0]))
        current: list[tuple[float, str]] = []
        top = None
        for left, y, text in words:
            if top is None or y - top > 3:
                if current:
                    lined.append((top, current))
                current = []
                top = y
            current.append((left, text))
        if current and top is not None:
            lined.append((top, current))

    committee = any(
        text in {"Member", "Chair", "Vice-Chair", "Co-Chair"} and 330 <= left < 420
        for _top, row in lined
        for left, text in row
    )
    anchors = []
    for top, row in lined:
        ranked = any(re.fullmatch(r"(?:NR|\d+)", text) and left < 95 for left, text in row)
        district = any(re.fullmatch(r"[HS]\d{1,3}", text) and 190 <= left < 270 for left, text in row)
        if ranked and district:
            anchors.append((top, row))
    extras: dict[int, list[tuple[float, str]]] = {index: [] for index in range(len(anchors))}
    for top, row in lined:
        if any(top == anchor_top for anchor_top, _row in anchors):
            continue
        text = line_text(row)
        if re.match(r"(House|Senate)\b", text) or text.startswith("How to read"):
            continue
        if not anchors:
            continue
        nearest = min(range(len(anchors)), key=lambda index: abs(anchors[index][0] - top))
        if abs(anchors[nearest][0] - top) <= 16:
            extras[nearest].extend(row)

    def cell(row: list[tuple[float, str]], start: float, end: float) -> str:
        return " ".join(text for left, text in row if start <= left < end).strip()

    sections: list[tuple[str, list[dict]]] = []
    current_title = ""
    current_rows: list[dict] = []
    anchor_index = 0
    for index, (top, row) in enumerate(lined):
        text = line_text(row)
        if re.match(r"(House|Senate)\b", text) and "member" in text.casefold():
            if current_rows:
                sections.append((current_title, current_rows))
            parts = [text.strip()]
            for _next_top, next_row in lined[index + 1:]:
                nxt = line_text(next_row).strip()
                if re.match(r"(?:Liberal|Conservative|Moderate)\b", nxt) or re.match(r"\d+\s+not ranked", nxt, re.I):
                    parts.append(nxt)
                    continue
                break
            current_title = re.sub(r"\s+", " ", " ".join(parts)).strip()
            current_rows = []
            continue
        if anchor_index >= len(anchors) or anchors[anchor_index][0] != top:
            continue
        extra = extras[anchor_index]
        anchor_index += 1
        flat = row + extra
        rank = cell(row, 0, 95)
        name = " ".join(text for left, text in flat if 95 <= left < 200)
        district = cell(row, 200, 258)
        party = cell(row, 258, 345 if not committee else 350)
        role = ""
        if committee:
            role = " ".join(text for left, text in flat if 340 <= left < 410 and text in {"Member", "Chair", "Vice", "Vice-Chair", "Co-Chair"})
            band = " ".join(text for left, text in row if 410 <= left < 510 and text in {"Conservative", "Moderate", "Liberal"})
            chamber = "".join(text for left, text in flat if left >= 510 and re.fullmatch(r"[HS]|\d+|NR", text))
            covers = ""
        else:
            band = " ".join(text for left, text in row if 330 <= left < 430 and text in {"Conservative", "Moderate", "Liberal"})
            chamber = "".join(text for left, text in row if 430 <= left < 475 and re.fullmatch(r"[HS]|\d+|NR", text))
            covers = " ".join(text for left, text in flat if left >= 475 and text not in {"–", "-"})
            own = cell(row, 475, 900)
            if own in {"–", "-", "—"} and not covers:
                covers = "—"
            elif covers:
                covers = re.sub(r"\s+,", ",", covers)
                covers = re.sub(r"\s+", " ", covers).strip(" ,")
            else:
                covers = "—"
        if rank == "NR":
            band = "Not ranked"
            chamber = "Not ranked"
        else:
            chamber = re.sub(r"([HS])(\d)", r"\1 \2", chamber)
        if not re.fullmatch(r"(?:NR|\d+)", rank) or not name.strip():
            continue
        current_rows.append({
            "rank": "Not ranked" if rank == "NR" else rank,
            "name": re.sub(r"\s+", " ", name).strip(),
            "district": district,
            "party": party,
            "role": role,
            "band": band,
            "chamber": chamber,
            "covers": covers,
        })
    if current_rows:
        sections.append((current_title, current_rows))
    return [(title, rows) for title, rows in sections if rows]


def summary_pairs(text: str, kind: str) -> list[tuple[str, str]]:
    flat = re.sub(r"\s+", " ", text)
    if kind == "county" and "County rank" in flat:
        match = re.search(
            r"County rank\s+Legislators\s+Average rank\s+Conservative\s+Moderate\s+Liberal\s+"
            r"(\d+ of \d+)\s+(.+?)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(\d+)",
            flat,
        )
        if match:
            return [
                ("County rank", match.group(1)),
                ("Legislators", match.group(2)),
                ("Average rank", match.group(3)),
                ("Conservative", match.group(4)),
                ("Moderate", match.group(5)),
                ("Liberal", match.group(6)),
            ]
    if kind == "committee":
        match = re.search(
            r"(\d+ of \d+)\s+(\d+ \(H.+?\))\s+([\d.]+)\*?\s+(\d+)\s+(\d+)\s+(\d+)",
            flat,
        )
        if match:
            return [
                ("Committee rank", match.group(1)),
                ("Members", match.group(2)),
                ("Average rank", match.group(3)),
                ("Conservative", match.group(4)),
                ("Moderate", match.group(5)),
                ("Liberal", match.group(6)),
            ]
    return []


def notes_of(text: str) -> list[str]:
    start = text.find("How to read")
    if start < 0:
        start = text.find("Minimum-vote rule")
    if start < 0:
        return []
    chunk = text[start:]
    chunk = re.split(r"\n\s*\d{3} ", chunk)[0]
    chunk = re.sub(r"©.*", "", chunk)
    paragraphs = []
    block: list[str] = []
    for line in chunk.splitlines():
        stripped = line.strip()
        if not stripped:
            if block:
                paragraphs.append(re.sub(r"\s+", " ", " ".join(block)).strip())
                block = []
            continue
        if stripped.startswith("Page "):
            continue
        block.append(stripped)
    if block:
        paragraphs.append(re.sub(r"\s+", " ", " ".join(block)).strip())
    return [item for item in paragraphs if item and not item.startswith("©")]


def title_of(path: Path, text: str) -> tuple[str, str]:
    head = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    if not head:
        return path.stem, ""
    main = head[0]
    index = 1
    while index < len(head):
        nxt = head[index]
        if re.match(r"^(Joint |County report|v\d|All |Legislators)", nxt):
            break
        if "Average" in nxt or nxt.startswith("Committee "):
            break
        main = f"{main} {nxt}"
        index += 1
        if index > 3:
            break
    subtitle = head[index] if index < len(head) else ""
    main = re.sub(r"^\d+\s*·\s*", "", main)
    return re.sub(r"\s+", " ", main).strip(), subtitle


def parse_summary_table(text: str) -> tuple[list[str], list[list[str]]]:
    """All-counties or all-committees sheet."""
    county_rows = []
    committee_rows = []
    name_bits: list[str] = []
    county_re = re.compile(
        r"^\s*(\d{2})\s+(.+?)\s{2,}(\d+)\s+(\d+\s*/\s*\d+)\s+([\d.]+)\*?\s+(\d+)\s+(\d+\s*/\s*\d+\s*/\s*\d+)\s+(\d+)\s*$"
    )
    named_re = re.compile(
        r"^\s*(\d{2})\s+([A-Za-z].+?)\s{2,}(\d+)\s+([\d.]+)\*?\s+(\d+)\s+(\d+/\d+/\d+)\s+(\S+)\s*$"
    )
    bare_re = re.compile(
        r"^\s*(\d{2})\s{2,}(\d+)\s+([\d.]+)\*?\s+(\d+)\s+(\d+/\d+/\d+)\s+(\S+)\s*$"
    )
    for raw in text.splitlines():
        line = raw.rstrip()
        if county_re.match(line):
            county_rows.append([re.sub(r"\s+", " ", item).strip() for item in county_re.match(line).groups()])
            name_bits = []
            continue
        named = named_re.match(line)
        if named and "Committee" not in line and "county" not in line.casefold():
            number, name, members, average, rank, bands, kept = named.groups()
            name = " ".join(name_bits + [name])
            committee_rows.append([number, re.sub(r"\s+", " ", name).strip(), members, average, rank, bands, kept])
            name_bits = []
            continue
        bare = bare_re.match(line)
        if bare:
            number, members, average, rank, bands, kept = bare.groups()
            committee_rows.append([number, re.sub(r"\s+", " ", " ".join(name_bits)).strip(), members, average, rank, bands, kept])
            name_bits = []
            continue
        stripped = line.strip()
        if stripped and re.match(r"[A-Za-z]", stripped) and not stripped.startswith("How ") and "Minimum" not in stripped and "Appendix" not in stripped and "shaded" not in stripped:
            name_bits.append(stripped)
    if len(county_rows) >= 20:
        headers = ["No.", "County", "Legislators", "House / Senate", "Average rank", "County rank", "Conservative / Moderate / Liberal", "Shared"]
        return headers, county_rows
    if len(committee_rows) >= 5:
        headers = ["No.", "Committee", "Members", "Average rank", "Committee rank", "Conservative / Moderate / Liberal", "Kept or new"]
        return headers, committee_rows
    return [], []


def parse_committee_index(path: Path) -> tuple[list[str], list[list[str]]]:
    """All-committees sheet. Wrapped names sit just above and below the number."""
    rows = []
    for page in pdf_words(path):
        numbers = [(y, text) for left, y, text in page if re.fullmatch(r"\d{2}", text) and left < 80]
        for y, number in numbers:
            name_words = sorted(
                ((yy, left, text) for left, yy, text in page if 80 <= left < 270 and abs(yy - y) <= 10),
            )
            name = " ".join(text for _yy, _left, text in name_words)
            stats = sorted((left, text) for left, yy, text in page if left >= 270 and abs(yy - y) <= 2)
            stat_text = " ".join(text for _left, text in stats)
            match = re.search(
                r"(\d+)\s+([\d.]+)\*?\s+(\d+)\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s+(\S+)",
                stat_text,
            )
            if not match or not name:
                continue
            members, average, rank, conservative, moderate, liberal, kept = match.groups()
            rows.append([
                number,
                re.sub(r"\s+", " ", name).strip(" ,"),
                members,
                average.rstrip("*"),
                rank,
                f"{conservative}/{moderate}/{liberal}",
                kept,
            ])
    headers = ["No.", "Committee", "Members", "Average rank", "Committee rank", "Conservative / Moderate / Liberal", "Kept or new"]
    return headers, rows


def _near(page: list[tuple[float, float, str]], y: float, start: float, end: float, slack: float = 10) -> str:
    words = sorted(
        (yy, left, text)
        for left, yy, text in page
        if start <= left < end and abs(yy - y) <= slack
    )
    return " ".join(text for _yy, _left, text in words).strip()


def parse_full_ratings(path: Path, alpha: bool) -> list[tuple[str, list[dict]]]:
    house: list[dict] = []
    senate: list[dict] = []
    for page in pdf_words(path):
        if alpha:
            anchors = [
                (y, text)
                for left, y, text in page
                if re.fullmatch(r"[HS]\d{1,3}", text) and 165 <= left < 210
            ]
        else:
            anchors = [
                (y, text)
                for left, y, text in page
                if re.fullmatch(r"[HS]\d{1,3}", text) and 280 <= left < 340
            ]
        for y, district in anchors:
            if alpha:
                name = _near(page, y, 40, 170)
                party = _near(page, y, 220, 310, 3)
                band = _near(page, y, 310, 400, 3)
                overall = _near(page, y, 400, 455, 3)
                chamber = _near(page, y, 455, 510, 3)
                votes = _near(page, y, 510, 580, 3)
            else:
                name = _near(page, y, 160, 290)
                party = _near(page, y, 340, 420, 3)
                band = _near(page, y, 420, 500, 3)
                overall = _near(page, y, 110, 165, 3)
                chamber = _near(page, y, 50, 110, 3)
                votes = _near(page, y, 510, 580, 3)
            band = band if band in {"Conservative", "Moderate", "Liberal"} else ("Not ranked" if "Not" in band or band == "" else band)
            row = {
                "rank": overall or "Not ranked",
                "name": re.sub(r"-\s+", "-", re.sub(r"\s+", " ", name)).strip(" -"),
                "district": district,
                "party": party,
                "role": "",
                "band": band or "Not ranked",
                "chamber": chamber or "Not ranked",
                "covers": votes,
            }
            if not row["name"]:
                continue
            (senate if district.startswith("S") else house).append(row)
    sections = []
    if house:
        sections.append(("House", house))
    if senate:
        sections.append(("Senate", senate))
    return sections


def parse_one_page(path: Path) -> list[dict]:
    """Three printed columns become one table."""
    columns = ((0, 200), (200, 390), (390, 700))
    rows = []
    for page in pdf_words(path):
        for start, end in columns:
            chosen = sorted((y, left, text) for left, y, text in page if start <= left < end)
            groups: list[list[tuple[float, str]]] = []
            bucket: list[tuple[float, str]] = []
            top = None
            for y, left, text in chosen:
                if top is None or y - top > 4:
                    if bucket:
                        groups.append(bucket)
                    bucket = []
                    top = y
                bucket.append((left, text))
            if bucket:
                groups.append(bucket)
            for words in groups:
                words = sorted(words)
                text = " ".join(word for _left, word in words)
                match = re.match(
                    r"(\d+|NR)\s+(\d+|NR)\s+(\d+)\s+([HS]\d{1,3})\s+(.+)$",
                    text,
                )
                if not match:
                    continue
                overall, chamber, votes, district, name = match.groups()
                rows.append({
                    "rank": overall,
                    "chamber": chamber,
                    "covers": votes,
                    "district": district,
                    "name": name.strip(),
                    "party": "",
                    "role": "",
                    "band": "House" if district.startswith("H") else "Senate",
                })
    return rows


def parse_report(path: Path, kind: str) -> dict:
    text = layout_text(path)
    title, subtitle = title_of(path, text)
    if kind == "ratings":
        alpha = "Alpha" in path.name
        one_page = "1p" in path.name or "_105" in path.name or "_106" in path.name
        year = path.parent.name
        if one_page and alpha:
            title, subtitle = f"{year} Alpha, one page", "House and Senate in one table, alphabetical by name"
        elif one_page:
            title, subtitle = f"{year} Ranked, one page", "House and Senate in one table, most to least conservative"
        elif alpha:
            title, subtitle = f"{year} Alpha", "House and Senate, alphabetical by name"
        else:
            title, subtitle = f"{year} Ranked", "House and Senate, most to least conservative"
        pack = ratings_pack(path, text, alpha, one_page)
        pack.update({
            "title": title,
            "subtitle": subtitle,
            "summary": [],
            "summary_table": ([], []),
            "notes": [],
            "kind": kind,
        })
        return pack
    if is_summary_pdf(path) and kind == "committee":
        headers, rows = parse_committee_index(path)
        return {
            "title": title,
            "subtitle": subtitle,
            "summary": [],
            "sections": [],
            "summary_table": (headers, rows),
            "notes": notes_of(text),
            "kind": kind,
        }
    if is_summary_pdf(path):
        headers, rows = parse_summary_table(text)
        return {
            "title": title,
            "subtitle": subtitle,
            "summary": [],
            "sections": [],
            "summary_table": (headers, rows),
            "notes": notes_of(text),
            "kind": kind,
        }
    pages = pdf_words(path)
    sections = parse_member_sections(pages)
    return {
        "title": title,
        "subtitle": subtitle,
        "summary": summary_pairs(text, kind),
        "sections": sections,
        "summary_table": ([], []),
        "notes": notes_of(text),
        "kind": kind,
    }


def table(headers: list[str], rows: list[list[str]], page: Path, officials: dict[str, Path], name_index: int | None) -> str:
    head = "".join(f"<th scope=\"col\">{esc(item)}</th>" for item in headers)
    body = []
    for row in rows:
        cells = []
        for index, value in enumerate(row):
            if name_index is not None and index == name_index:
                cells.append(f"<td>{linked_name(value, officials, page)}</td>")
            else:
                cells.append(f"<td>{esc(value)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<table class="report-table"><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).replace("–", "-").replace("—", "-").strip()


def _flat(text: str) -> str:
    """Join wrapped PDF lines and keep the printed en dashes."""
    return re.sub(r"\s+", " ", text).strip()


def ratings_howto(text: str) -> list[str]:
    first = _flat(text.split("\f")[0])
    match = re.search(r"How to read this report (.+?) Contents:", first)
    if not match:
        return []
    body = match.group(1).strip()
    body = re.split(r" House \(\d+\):", body)[0].strip()
    parts = re.split(r"(?=The bands group )|(?=Minimum-vote rule:)", body)
    return [part.strip() for part in parts if part.strip()]


def ratings_legend(text: str) -> list[list[str]]:
    first = _flat(text.split("\f")[0])
    rows = []
    span = r"\d+[–-]\d+"
    for band in ("Conservative", "Moderate", "Liberal"):
        match = re.search(
            rf"{band}\s+(\d+)\s+({span})\s+(\d+)\s*·\s*({span})\s+(\d+)\s*·\s*({span})",
            first,
        )
        if not match:
            continue
        count, overall, house_n, house_span, senate_n, senate_span = match.groups()
        rows.append([
            band,
            count,
            overall.replace("-", "–"),
            f"{house_n} · {house_span.replace('-', '–')}",
            f"{senate_n} · {senate_span.replace('-', '–')}",
        ])
    return rows


def ratings_meta(text: str) -> str:
    flat = _flat(text.split("\f")[0])
    match = re.search(
        r"(v1\.0 · votes through \d{4}-\d{2}-\d{2} · \d+ legislators(?: \([^)]*\))?)",
        flat,
    )
    return match.group(1) if match else ""


def ratings_copyright(text: str) -> str:
    match = re.search(r"©\s*\d{4}\s+MTR Research", text)
    return match.group(0) if match else "© 2026 MTR Research"


def ratings_nr_note(text: str) -> str:
    flat = _flat(text)
    match = re.search(r"(NR = Not ranked: .+?) \d{3} \d{4} Legislator", flat)
    return match.group(1) if match else ""


def ratings_one_note(text: str) -> str:
    flat = _flat(text)
    match = re.search(r"(Bands: .+?Votes through \d{4}-\d{2}-\d{2}\.)", flat)
    return match.group(1) if match else ""


def sibling_full(path: Path) -> Path | None:
    name = path.name
    if "Ranked_1p_105" in name:
        other = path.with_name(name.replace("Ranked_1p_105", "Ranked_103"))
    elif "Alpha_1p_106" in name:
        other = path.with_name(name.replace("Alpha_1p_106", "Alpha_104"))
    else:
        return None
    return other if other.is_file() else None


def ratings_pack(path: Path, text: str, alpha: bool, one_page: bool) -> dict:
    year = path.parent.name
    if one_page:
        rows = parse_one_page(path)
        full = sibling_full(path)
        by_district = {}
        if full is not None:
            for _title, members in parse_full_ratings(full, alpha):
                for member in members:
                    by_district[member["district"]] = member
        for row in rows:
            source = by_district.get(row["district"])
            if source:
                row["party"] = source["party"]
                row["band"] = source["band"]
                row["full_name"] = source["name"]
            elif row["rank"] == "NR":
                row["band"] = "Not ranked"
                row["full_name"] = row["name"]
            else:
                row["full_name"] = row["name"]
        house = [row for row in rows if row["district"].startswith("H")]
        senate = [row for row in rows if row["district"].startswith("S")]

        def sort_key(row: dict):
            if alpha:
                return row["name"].casefold()
            return int(row["rank"]) if str(row["rank"]).isdigit() else 999

        house.sort(key=sort_key)
        senate.sort(key=sort_key)
        sections = [("House", house), ("Senate", senate)]
        sheet = "one"
    else:
        sections = parse_full_ratings(path, alpha)
        sheet = "full"
    code = "106" if one_page and alpha else "105" if one_page else "104" if alpha else "103"
    label = "Alpha" if alpha else "Ranked"
    return {
        "sections": sections,
        "sheet": sheet,
        "alpha": alpha,
        "year": year,
        "howto": ratings_howto(text),
        "legend": ratings_legend(text),
        "meta": ratings_meta(text),
        "code": code,
        "copyright": ratings_copyright(text),
        "nr_note": "" if one_page else ratings_nr_note(text),
        "one_note": ratings_one_note(text) if one_page else "",
        "doc_title": f"{year} Legislator Ratings {label}",
        "doc_sub": (
            f"House and Senate · {year} session · alphabetical by last name"
            if alpha
            else f"House and Senate · {year} session · most to least conservative"
        ),
    }


def band_class(band: str) -> str:
    return {
        "Conservative": "is-conservative",
        "Moderate": "is-moderate",
        "Liberal": "is-liberal",
        "Not ranked": "is-unranked",
    }.get(band, "")


def party_class(party: str) -> str:
    name = party.casefold()
    if name.startswith("rep"):
        return "is-republican"
    if name.startswith("dem"):
        return "is-democrat"
    if name.startswith("ind"):
        return "is-independent"
    if name.startswith("lib"):
        return "is-libertarian"
    return ""


def section_blurb(title: str, rows: list[dict], alpha: bool) -> tuple[str, str]:
    ranked = [row for row in rows if row.get("band") in {"Conservative", "Moderate", "Liberal"}]
    counts = {band: sum(1 for row in ranked if row.get("band") == band) for band in ("Conservative", "Moderate", "Liberal")}
    order = "alphabetical by last name" if alpha else "most to least conservative"
    unranked = len(rows) - len(ranked)
    if unranked:
        heading = f"{title} · {len(rows)} legislators ({len(ranked)} ranked, {unranked} not ranked)"
    else:
        heading = f"{title} · {len(rows)} legislators"
    detail = (
        f"{title} members, {order}. Band counts here: "
        f"Conservative {counts['Conservative']}, Moderate {counts['Moderate']}, Liberal {counts['Liberal']}."
    )
    return heading, detail


def render_ratings(pdf: Path, parsed: dict, dest: Path, officials: dict[str, Path]) -> None:
    year = parsed["year"]
    depth = len(dest.relative_to(PREVIEW).parts) - 1
    root = "../" * depth
    current = ' aria-current="page"'
    nav = NAV.format(
        root=root,
        home="",
        archive=current,
        committees="",
        counties="",
    )
    if year == CURRENT_YEAR:
        # The ratings stair is under Ratings, not Archive. The back control still
        # returns to the reports list, which is where these sheets are linked.
        back_href = f"{root}archive/reports.html"
    else:
        back_href = f"{root}archive/reports.html"
    pdf_href = Path(os.path.relpath(pdf, dest.parent)).as_posix()
    seal = f"{root}assets/img/mtr-seal.png"
    word = f"{root}assets/img/mtr-wordmark.png"
    logo = f"{root}assets/img/surveyor-icon.png"

    def person(name: str, full: str | None = None, wrap: bool = False) -> str:
        linked = linked_name(full or name, officials, dest)
        shown = esc(name).replace("-", "-<wbr>") if wrap else esc(name)
        if "</a>" not in linked:
            return shown
        linked = re.sub(r">([^<]*)</a>", ">" + shown + "</a>", linked, count=1)
        return linked.replace("<a ", '<a class="wv-person" ', 1)

    if parsed["sheet"] == "full":
        legend_rows = []
        house_total = 0
        senate_total = 0
        all_total = 0
        for band, count, overall, house_span, senate_span in parsed["legend"]:
            legend_rows.append(
                f'<tr class="{band_class(band)}"><th scope="row">{esc(band)}</th>'
                f"<td>{esc(count)}</td><td>{esc(overall)}</td><td>{esc(house_span)}</td><td>{esc(senate_span)}</td></tr>"
            )
            all_total += int(count)
            house_total += int(house_span.split("·", 1)[0].strip() or 0)
            senate_total += int(senate_span.split("·", 1)[0].strip() or 0)

        def emphasize(part: str) -> str:
            shown = esc(part)
            shown = shown.replace("overall rank", "<strong>overall rank</strong>")
            shown = shown.replace("chamber rank", "<strong>chamber rank</strong>")
            shown = shown.replace("Minimum-vote rule:", "<strong>Minimum-vote rule:</strong>")
            return shown

        howto = "".join(f"<p>{emphasize(part)}</p>" for part in parsed["howto"])
        if parsed["alpha"]:
            title_html = esc(parsed["doc_title"])
        else:
            title_html = esc(parsed["doc_title"]).replace(" Ratings ", " Ratings<br>")

        def sheet_foot() -> str:
            return (
                '<footer class="wv-foot">'
                f'<img src="{seal}" alt="">'
                f"<p>{esc(parsed['code'])} {esc(parsed['doc_title'])} v1.0</p>"
                f"<p>{esc(parsed['copyright'])}</p></footer>"
            )

        parts = [
            '<header class="wv-cover">',
            f'<img class="wv-seal" src="{seal}" alt="MTR Research, Wyoming">',
            f'<h2 class="wv-title">{title_html}</h2>',
            f'<p class="wv-sub">{esc(parsed["doc_sub"])}</p>',
            f'<p class="wv-meta">{esc(parsed["meta"])}</p>',
            '<h3>How to read this report</h3>',
            howto,
            '<table class="wv-legend"><thead><tr>'
            '<th scope="col">Band</th>'
            f'<th scope="col">All {all_total}</th>'
            '<th scope="col">Overall ranks</th>'
            f'<th scope="col">House ({house_total}): number · ranks</th>'
            f'<th scope="col">Senate ({senate_total}): number · ranks</th>'
            "</tr></thead><tbody>",
            "".join(legend_rows),
            "</tbody></table>",
            "<p class=\"wv-contents\">Contents: House section, then Senate section.</p>",
            "</header>",
            sheet_foot(),
        ]
        for title, rows in parsed["sections"]:
            heading, detail = section_blurb(title, rows, parsed["alpha"])
            body = []
            for row in rows:
                band = row.get("band") or ""
                if parsed["alpha"]:
                    cells = [
                        f'<td class="wv-name">{person(row["name"], wrap=True)}</td>',
                        f'<td>{esc(row["district"])}</td>',
                        f'<td>{esc(row["party"])}</td>',
                        f'<td class="wv-band {band_class(band)}">{esc(band)}</td>',
                        f'<td>{esc(row["rank"])}</td>',
                        f'<td>{esc(row["chamber"])}</td>',
                        f'<td>{esc(row["covers"])}</td>',
                    ]
                else:
                    cells = [
                        f'<td>{esc(row["chamber"])}</td>',
                        f'<td>{esc(row["rank"])}</td>',
                        f'<td class="wv-name">{person(row["name"], wrap=True)}</td>',
                        f'<td>{esc(row["district"])}</td>',
                        f'<td>{esc(row["party"])}</td>',
                        f'<td class="wv-band {band_class(band)}">{esc(band)}</td>',
                        f'<td>{esc(row["covers"])}</td>',
                    ]
                body.append("<tr>" + "".join(cells) + "</tr>")
            if parsed["alpha"]:
                chamber_head = "Senate<br>rank" if title == "Senate" else "House<br>rank"
                cols = (
                    '<col class="wv-namecol"><col><col><col><col><col><col>'
                )
                head = (
                    "<th>Legislator</th><th>District</th><th>Party</th><th>Band</th>"
                    f"<th>Overall<br>rank</th><th>{chamber_head}</th><th>Votes</th>"
                )
            else:
                chamber_head = "Senate<br>rank" if title == "Senate" else "House<br>rank"
                cols = (
                    "<col><col><col class=\"wv-namecol\"><col><col><col><col>"
                )
                head = (
                    f"<th>{chamber_head}</th><th>Overall<br>rank</th><th>Legislator</th>"
                    "<th>District</th><th>Party</th><th>Band</th><th>Votes</th>"
                )
            note = parsed.get("nr_note") or ""
            footnote = ""
            if note and any(row["district"] and row["district"] in note for row in rows):
                footnote = f'<p class="wv-note">{esc(note)}</p>'
            parts.append(
                '<section class="wv-part wv-page">'
                f'<div class="wv-brand"><img class="wv-word" src="{word}" alt="MTR Research"></div>'
                f"<h3>{esc(heading)}</h3><p>{esc(detail)}</p>"
                f'<table class="wv-rate"><colgroup>{cols}</colgroup><thead><tr>{head}</tr></thead><tbody>'
                + "".join(body)
                + "</tbody></table>"
                + footnote
                + "</section>"
            )
            parts.append(sheet_foot())
    else:
        def column(rows: list[dict], chamber_word: str) -> str:
            lines = []
            for row in rows:
                band = row.get("band") or ""
                party = party_class(row.get("party") or "")
                lines.append(
                    '<div class="op-row">'
                    f'<span class="op-box {band_class(band)}">{esc(row["rank"])}</span>'
                    f'<span class="op-box {band_class(band)}">{esc(row["chamber"])}</span>'
                    f'<span class="op-votes">{esc(row["covers"])}</span>'
                    f'<span class="op-dist {party}">{esc(row["district"])}</span>'
                    f'<span class="op-name">{person(row["name"], row.get("full_name"))}</span>'
                    "</div>"
                )
            chamber_word = "Senate" if rows and rows[0]["district"].startswith("S") else "House"
            return (
                '<section class="op-col">'
                f'<p class="op-head"><span>of {ranked_of}</span><span>{esc(chamber_word)}</span>'
                "<span>#Votes</span><span>Dist</span><span>Legislator</span></p>"
                + "".join(lines)
                + "</section>"
            )
        house = parsed["sections"][0][1] if parsed["sections"] else []
        senate = parsed["sections"][1][1] if len(parsed["sections"]) > 1 else []
        split = (len(house) + 1) // 2
        ranked_of = sum(1 for row in house + senate if str(row["rank"]).isdigit())
        sort_note = "Alphabetical by last name" if parsed["alpha"] else "Sorted from MOST Conservative to Most Liberal"
        note = parsed.get("one_note") or ""
        if " NR =" in note:
            first, rest = note.split(" NR =", 1)
            note_html = f"<p>{esc(first)}</p><p>NR ={esc(rest)}</p>"
        elif note:
            note_html = f"<p>{esc(note)}</p>"
        else:
            note_html = ""
        parts = [
            '<header class="op-banner">',
            f'<h2>{esc("Legislators, by Name" if parsed["alpha"] else "Legislators, by Rank")}</h2>',
            f'<p class="op-sort">{esc(sort_note)}</p>',
            f'<p class="op-session">Session: <strong>{esc(year[-2:])}</strong></p>',
            "</header>",
            '<div class="op-grid">',
            f'<h3 class="op-bar op-span">Representatives: <span>{len(house)}</span></h3>',
            f'<h3 class="op-bar">Senators: <span>{len(senate)}</span></h3>',
            column(house[:split], "Representatives"),
            column(house[split:], "Representatives"),
            column(senate, "Senators"),
            "</div>",
            '<footer class="op-legend">',
            '<div class="op-brand">'
            f'<img src="{logo}" alt="" width="28" height="32">'
            "<span>WyoVote</span></div>",
            '<div class="op-keys"><p><span class="op-key">Parties:</span> '
            '<span class="op-chip"><i class="is-republican"></i> Republican</span> '
            '<span class="op-chip"><i class="is-democrat"></i> Democrat</span> '
            '<span class="op-chip"><i class="is-independent"></i> Independent</span> '
            '<span class="op-chip"><i class="is-libertarian"></i> Libertarian</span></p>'
            '<p><span class="op-key">Seq Rank:</span> '
            '<span class="op-chip"><i class="is-conservative"></i> Conservative</span> '
            '<span class="op-chip"><i class="is-moderate"></i> Moderate</span> '
            '<span class="op-chip"><i class="is-liberal"></i> Liberal</span> '
            '<span class="op-chip"><i class="is-unranked"></i> Not ranked</span></p></div>',
            f"<p class=\"op-code\">{esc(parsed['code'])}<br>v1.0</p>",
            f'<div class="op-note">{note_html}</div>',
            "</footer>",
        ]
    doc = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(parsed["title"])} — WyoVote</title>
    <meta name="description" content="{esc(parsed["doc_sub"])}">
    <link rel="icon" href="{root}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{root}../css/styles.css">
    <link rel="stylesheet" href="{root}preview.css">
  </head>
  <body>
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
{nav}
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="{root}archive/reports.html">← Back to Reports</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>{esc(parsed["title"])}</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap report-sheet wv-sheet">
          <p class="report-actions"><a class="print-pdf" data-print="1" href="{esc(pdf_href)}">Print (PDF)</a></p>
          {"".join(parts)}
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
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc, encoding="utf-8")
    if dest.stat().st_size > 500 * 1024:
        raise SystemExit(f"{dest} is over 500 KB")


def render(pdf: Path, parsed: dict, dest: Path, officials: dict[str, Path]) -> None:
    if parsed.get("kind") == "ratings":
        render_ratings(pdf, parsed, dest, officials)
        return
    year, _slug = slug_for(pdf, parsed["kind"])
    depth = len(dest.relative_to(PREVIEW).parts) - 1
    root = "../" * depth
    current = ' aria-current="page"'
    nav_flags = {"home": "", "archive": "", "committees": "", "counties": ""}
    if year == CURRENT_YEAR and parsed["kind"] == "county":
        nav_flags["counties"] = current
        back_href = f"{root}counties.html"
        back_label = "Counties"
    elif year == CURRENT_YEAR and parsed["kind"] == "committee":
        nav_flags["committees"] = current
        back_href = f"{root}committees.html"
        back_label = "Committees"
    elif year == CURRENT_YEAR and parsed["kind"] == "ratings":
        back_href = f"{root}archive/reports.html"
        back_label = "Reports"
        nav_flags["archive"] = current
    else:
        nav_flags["archive"] = current
        back_href = f"{root}archive/{'counties' if parsed['kind']=='county' else 'committees' if parsed['kind']=='committee' else 'reports'}.html"
        back_label = "Archive"
    pdf_href = Path(os.path.relpath(pdf, dest.parent)).as_posix()
    parts = []
    if parsed["summary"]:
        heads = "".join(f"<th scope=\"col\">{esc(label)}</th>" for label, _value in parsed["summary"])
        vals = "".join(f"<td>{esc(value)}</td>" for _label, value in parsed["summary"])
        parts.append(f'<table class="report-stats"><thead><tr>{heads}</tr></thead><tbody><tr>{vals}</tr></tbody></table>')
    headers, rows = parsed["summary_table"]
    if headers:
        name_at = parsed.get("name_column")
        if name_at is None and len(headers) > 1 and headers[1] == "Legislator":
            name_at = 1
        parts.append(table(headers, rows, dest, officials, name_at))
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
            headers.append("Votes" if parsed.get("votes_column") else "Also covers")
            keys.append("covers")
        body_rows = [[row.get(key, "") for key in keys] for row in members]
        parts.append(table(headers, body_rows, dest, officials, keys.index("name")))
    for note in parsed["notes"]:
        parts.append(f'<p class="report-note">{esc(note)}</p>')
    nav = NAV.format(root=root, **nav_flags)
    doc = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(parsed["title"])} — WyoVote</title>
    <meta name="description" content="{esc(parsed["subtitle"] or parsed["title"])}">
    <link rel="icon" href="{root}assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="{root}../css/styles.css">
    <link rel="stylesheet" href="{root}preview.css">
  </head>
  <body>
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
{nav}
          </ul>
        </nav>
      </div>
    </header>
    <main id="main">
      <div class="wrap back-wrap">
        <p class="back-row"><a class="back-btn" href="{back_href}">← Back to {esc(back_label)}</a></p>
      </div>
      <section class="page-hero">
        <div class="wrap">
          <h1>{esc(parsed["title"])}</h1>
        </div>
      </section>
      <section class="page-body">
        <div class="wrap report-sheet">
          <p class="report-kicker">{esc(parsed["subtitle"])}</p>
          <p class="report-actions"><a class="print-pdf" data-print="1" href="{esc(pdf_href)}">Print (PDF)</a></p>
          {"".join(parts)}
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
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc, encoding="utf-8")
    if dest.stat().st_size > 500 * 1024:
        raise SystemExit(f"{dest} is over 500 KB")


def rewrite_links(mapping: dict[Path, Path]) -> int:
    changed = 0
    by_name = {}
    for pdf, page in mapping.items():
        by_name.setdefault(pdf.name, page)
    for html_path in PREVIEW.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        original = text

        def replace(match: re.Match) -> str:
            tag = match.group(0)
            if 'data-print="1"' in tag:
                return tag
            href = match.group(1)
            target = (html_path.parent / href.split("#")[0].split("?")[0]).resolve()
            page = mapping.get(target)
            if page is None:
                page = by_name.get(Path(href).name)
            if page is None:
                return tag
            new_href = Path(os.path.relpath(page, html_path.parent)).as_posix()
            return tag.replace(href, new_href, 1)

        text = re.sub(r'<a\b[^>]*href="([^"]+\.pdf)"[^>]*>', replace, text)
        if text != original:
            html_path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def full_ratings_pdf(year: str, kind: str) -> Path:
    label = "Ranked_103" if kind == "ranked" else "Alpha_104"
    return ROOT / "reports" / year / f"wyovote_{year}_Ratings_{label}_v1.0.pdf"


def retarget_full_ratings() -> int:
    """Full Ranked and Alpha sheets stay PDFs. One-page sheets stay web pages."""
    changed = 0
    anchor = re.compile(r'<a\b([^>]*?)href="([^"]+)"([^>]*)>')
    for html_path in PREVIEW.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        original = text

        def replace(match: re.Match) -> str:
            before, href, after = match.group(1), match.group(2), match.group(3)
            path = href.split("#", 1)[0].split("?", 1)[0]
            found = re.search(r"(\d{4})/ratings/(ranked|alpha)\.html$", path)
            if not found:
                return match.group(0)
            year, kind = found.group(1), found.group(2)
            pdf = full_ratings_pdf(year, kind)
            if not pdf.is_file():
                return match.group(0)
            new_href = Path(os.path.relpath(pdf, html_path.parent)).as_posix()
            return f'<a{before}href="{new_href}"{after}>'

        text = anchor.sub(replace, text)
        if text != original:
            html_path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def reports_for(kind: str) -> list[Path]:
    found = []
    for path in sorted(REPORTS.rglob("*.pdf")):
        if kind_of(path) == kind:
            found.append(path)
    return found


def build(kind: str) -> int:
    officials = load_officials()
    mapping: dict[Path, Path] = {}
    count = 0
    for pdf in reports_for(kind):
        _year, slug = slug_for(pdf, kind)
        if kind == "ratings" and slug in {"ranked", "alpha"}:
            dest = page_path(pdf, kind)
            if dest.exists():
                dest.unlink()
            continue
        parsed = parse_report(pdf, kind)
        if not parsed["sections"] and not parsed["summary_table"][1] and not parsed["summary"]:
            raise SystemExit(f"no rows parsed from {pdf}")
        dest = page_path(pdf, kind)
        render(pdf, parsed, dest, officials)
        mapping[pdf.resolve()] = dest
        count += 1
        members = sum(len(rows) for _title, rows in parsed["sections"])
        summary_rows = len(parsed["summary_table"][1])
        if not is_summary_pdf(pdf) and members == 0 and summary_rows < 20:
            raise SystemExit(f"no legislators parsed from {pdf}")
        if is_summary_pdf(pdf) and summary_rows < 5:
            raise SystemExit(f"summary table too short in {pdf}: {summary_rows}")
    print(f"wrote {count} {kind} pages")
    print(f"relinked {rewrite_links(mapping)} preview pages")
    if kind == "ratings":
        print(f"pointed {retarget_full_ratings()} full Ranked/Alpha links at the PDFs")
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_site_map.py")])
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "mark_outside_links.py")])
    return count


LEGACY = [
    "reports/2023/2023-all-legislative-counties.pdf",
    "reports/2023/2023-natrona.pdf",
    "reports/2023/2023-niobrara.pdf",
    "reports/2023/2023-park.pdf",
    "reports/2023/2023-platte.pdf",
    "reports/2023/2023-sheridan.pdf",
    "reports/2023/2023-sublette.pdf",
    "reports/2023/2023-sweetwater.pdf",
    "reports/2023/2023-teton.pdf",
    "reports/2023/2023-uinta.pdf",
    "reports/2023/2023-washakie.pdf",
    "reports/2023/2023-weston.pdf",
    "reports/2023/01-01-judiciary.pdf",
    "reports/2023/02-02-appropriations.pdf",
    "reports/2023/03-03-revenue.pdf",
    "reports/2023/04-04-education.pdf",
    "reports/2023/05-05-agriculture.pdf",
    "reports/2023/06-06-travel.pdf",
    "reports/2023/07-07-corporations.pdf",
    "reports/2023/08-08-transportation.pdf",
    "reports/2023/09-09-minerals.pdf",
    "reports/2023/10-10-labor.pdf",
    "reports/2023/11-11-journal.pdf",
    "reports/2023/12-12-rules.pdf",
    "reports/2023/13-air-transport.pdf",
    "reports/2023/17-blockchain.pdf",
    "reports/2023/18-capital-financing.pdf",
    "reports/2023/19-legislative-facilities.pdf",
    "reports/2023/20-mental-health.pdf",
    "reports/2023/21-school-facilities.pdf",
    "reports/2023/22-tribal-relations.pdf",
    "reports/2023/23-federal-natural-resource.pdf",
    "reports/2023/25-select-water.pdf",
    "reports/2023/29-indian-child-welfare.pdf",
    "reports/2023/30-mental-health.pdf",
    "reports/2023/31-regulatory-reduction.pdf",
    "reports/2023/32-riverton-state-office.pdf",
    "reports/2023/33-state-shooting-complex.pdf",
    "reports/2023/26-management-council.pdf",
    "reports/2023/27-management-audit-committee.pdf",
    "reports/2023/15-capitol-interpretative.pdf",
    "reports/2023/34-capitol-governance.pdf",
    "reports/2023/35-legislator-ethics.pdf",
    "reports/2022/wc-committee.pdf",
    "reports/2022/22-wc-county.pdf",
    "reports/2021/committees.pdf",
    "reports/2021/l-county-rate.pdf",
]
NOTE = (
    "The printed sheet includes a numeric rating beside each name. "
    "This page lists the legislators and leaves that number off."
)


def legacy_rows(path: Path) -> list[tuple[str, str, str, str]]:
    """Name, district or party, and role. The numeric rating is dropped."""
    found = []
    for page in pdf_words(path):
        districts = [(left, y, text) for left, y, text in page if re.fullmatch(r"[HS]\d{1,3}", text)]
        parties = [(left, y, text) for left, y, text in page if text in {"Rep", "Dem", "Ind", "Lib"}]
        anchors = districts or parties
        for left, y, token in anchors:
            name_words = sorted(
                (yy, x, word)
                for x, yy, word in page
                if x < left - 8 and abs(yy - y) <= 6 and re.match(r"[A-Za-z]", word)
                and word not in {"Rep", "Dem", "Sen", "House", "Senate", "Legend", "Republican", "Democrat"}
            )
            # Keep the words on the nearest line only.
            if not name_words:
                continue
            nearest = min(abs(yy - y) for yy, _x, _word in name_words)
            chosen = [word for yy, _x, word in name_words if abs(abs(yy - y) - nearest) < 0.2 or abs(yy - y) <= nearest + 0.2]
            # simpler: words within 2pt
            chosen = [word for yy, x, word in sorted(name_words) if abs(yy - y) <= 2]
            name = " ".join(chosen).strip(" -")
            role = ""
            for role_word in ("Vice-Chair", "Chairman", "Chair"):
                if any(word == role_word and abs(yy - y) <= 2 and x < left for x, yy, word in page):
                    role = role_word
            if not name or name.lower() in {"county", "committee", "rating", "legend"}:
                continue
            section = "House" if token.startswith("H") else "Senate" if token.startswith("S") else "Committee"
            district = token if token[:1] in "HS" else token
            found.append((section, name, district, role))
    # Drop duplicates that come from two-column repeats of the same line.
    unique = []
    seen = set()
    for item in found:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def build_legacy() -> int:
    officials = load_officials()
    mapping: dict[Path, Path] = {}
    count = 0
    for rel in LEGACY:
        pdf = ROOT / rel
        rows = legacy_rows(pdf)
        if len(rows) < 1:
            raise SystemExit(f"too few names in {pdf}: {len(rows)}")
        year = pdf.parent.name
        dest = OUT / year / "legacy" / f"{pdf.stem}.html"
        sections: list[tuple[str, list[dict]]] = []
        grouped: dict[str, list[dict]] = {}
        for section, name, district, role in rows:
            grouped.setdefault(section, []).append({
                "rank": "",
                "name": name,
                "district": district if district[:1] in "HS" else "",
                "party": {"Rep": "Republican", "Dem": "Democrat", "Ind": "Independent", "Lib": "Libertarian"}.get(district, ""),
                "role": role,
                "band": "",
                "chamber": "",
                "covers": "",
            })
        for section, members in grouped.items():
            sections.append((section, members))
        title = pdf.stem.replace("-", " ")
        parsed = {
            "title": title,
            "subtitle": f"{year} archived sheet",
            "summary": [],
            "sections": sections,
            "summary_table": ([], []),
            "notes": [NOTE],
            "kind": "legacy",
        }
        render(pdf, parsed, dest, officials)
        mapping[pdf.resolve()] = dest
        count += 1
    print(f"wrote {count} legacy pages")
    print(f"relinked {rewrite_links(mapping)} preview pages")
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_site_map.py")])
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "mark_outside_links.py")])
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("county", "committee", "ratings", "legacy"), required=True)
    args = parser.parse_args()
    if args.kind == "legacy":
        build_legacy()
    else:
        build(args.kind)


if __name__ == "__main__":
    main()
