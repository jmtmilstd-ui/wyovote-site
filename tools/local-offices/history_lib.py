#!/usr/bin/env python3
"""Shared helpers for per-county effective-dated officeholder history.

January YYYY snapshot = in office on January 8 (after the first Monday and
after January 3 congressional terms, America/Denver). Snapshots are generated
from dated terms; they are not hand-edited.
"""
from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "data" / "county_officials" / "history"
SHARED_H = HISTORY / "shared"
PEOPLE_DIR = ROOT / "data" / "people"
PROFILE_DIR = ROOT / "candidates" / "local-history" / "c"
NAME_INDEX_PEOPLE = Path("/workspace/name-index/data/people.csv")

GROUP_META = [
    ("federal", "Federal offices", "heading-then-names"),
    ("statewide", "Statewide offices", "office-and-name"),
    ("state-senate", "State Senate", "office-and-name"),
    ("state-house", "State House", "office-and-name"),
    ("county", "County Offices", "office-and-name"),
    ("municipal", "Municipal offices", "office-and-name"),
    ("schools", "School boards", "heading-then-names"),
    ("special-districts", "Special districts", "heading-then-names"),
    ("judicial", "Judicial retention", "office-and-name"),
    ("precincts", "Precincts", "heading-then-names"),
]

SORT = {
    "federal": "A", "statewide": "B", "state-senate": "C", "state-house": "D",
    "county": "E", "municipal": "F", "schools": "G", "special-districts": "H",
    "judicial": "J3", "precincts": "P",
}


def first_monday(year: int) -> str:
    d = date(year, 1, 1)
    d = d + timedelta(days=(7 - d.weekday()) % 7)
    return d.isoformat()


FM = {y: first_monday(y) for y in range(2008, 2040)}
JAN3 = {y: f"{y}-01-03" for y in range(2008, 2040)}


def src_dict(label, url=""):
    return {"label": label, "url": url or ""}


def person_factory(people: dict):
    def person(pid, display, first, last, middle="", aliases="", minted=True, slug=""):
        if not slug:
            slug = re.sub(r"[^a-z0-9]+", "-", display.lower()).strip("-")
        rec = dict(
            person_id=pid, slug=slug, display_name=display,
            sort_name=f"{last}, {first}", first=first, middle=middle,
            last=last, suffix="", aliases=aliases,
            minted="Y" if minted else "N",
        )
        people[pid] = rec
        return pid
    return person


def term(**kw):
    rec = {
        "person_id": kw["person_id"],
        "name": kw["name"],
        "ballot_name": kw.get("ballot_name") or "",
        "party": kw.get("party") or "",
        "office_group": kw["office_group"],
        "office": kw["office"],
        "jurisdiction": kw.get("jurisdiction") or "",
        "role": kw.get("role") or "",
        "term_start": kw["term_start"],
        "term_end": kw["term_end"],
        "start_year": int(kw["term_start"][:4]),
        "end_year": int(kw["term_end"][:4]) - (0 if kw["term_end"][5:] > "01-01" else 1),
        "how_took_office": kw.get("how_took_office") or "elected",
        "election_year": kw.get("election_year"),
        "confidence": kw.get("confidence") or "high",
        "sources": kw.get("sources") or [],
        "notes": kw.get("notes") or "",
        "flags": kw.get("flags") or [],
        "href": kw.get("href") or "",
        "retention": kw.get("retention"),
    }
    return rec


def in_snapshot(t, year):
    """True if the person was in office on January 8 of year."""
    as_of = f"{year}-01-08"
    return t["term_start"] <= as_of < t["term_end"]


def holder_from_term(t, people: dict):
    p = people.get(t["person_id"], {})
    href = t.get("href") or ""
    if not href and p.get("slug"):
        href = f"candidates/local-history/c/{p['slug']}.html"
    h = {
        "name": t["name"],
        "person_id": t["person_id"],
        "party": t.get("party") or "",
        "term_end": "January " + t["term_end"][:4] if t.get("term_end") else "",
        "sources": t.get("sources") or [],
        "confidence": t.get("confidence"),
        "notes": t.get("notes") or "",
    }
    if href:
        h["href"] = href
    if t.get("ballot_name"):
        h["ballot_name"] = t["ballot_name"]
    if t.get("role"):
        h["role"] = t["role"]
    if t.get("retention"):
        h["retention"] = t["retention"]
    if t.get("flags"):
        h["flags"] = t["flags"]
    return h


def office_base(title):
    return re.sub(r"\s*\((2-year|unexpired)\)\s*$", "", title, flags=re.I).strip()


def build_snapshot(year, *, county, county_number, slug, terms, people, expected,
                   retrieved, judicial_note="", special_note="", precinct_note="",
                   precinct_note_early="", precinct_cutoff=2021):
    as_of = f"{year}-01-08"
    groups = []
    coverage = []
    active = [t for t in terms if in_snapshot(t, year)]
    for gid, title, default_layout in GROUP_META:
        gterms = [t for t in active if t["office_group"] == gid]
        by_off = defaultdict(list)
        for t in gterms:
            by_off[office_base(t["office"])].append(t)

        if gid == "precincts":
            precincts = []
            for off, ts in sorted(by_off.items()):
                holders = [holder_from_term(t, people) for t in ts]
                precincts.append({"office": off, "layout": "heading-then-names", "holders": holders})
            note = precinct_note
            if year < precinct_cutoff:
                note = precinct_note_early or (
                    "Precinct committee rosters for this January are not yet collected. "
                    "Official primary PDFs are archived."
                )
                precincts = []
            groups.append({"id": gid, "title": title, "note": note, "precincts": precincts, "sort_key": "P"})
            have = sum(len(p["holders"]) for p in precincts)
            coverage.append({
                "year": year, "group": gid, "have": have,
                "not_collected": "yes" if not precincts else ("partial" if have else "yes"),
            })
            continue

        expected_list = expected.get(gid, [])
        expected_map = {o: n for o, n in expected_list}
        all_offices = list(by_off.keys())
        for o, _n in expected_list:
            if o not in all_offices:
                all_offices.append(o)
        have_n = 0
        missing_n = 0
        offices = []
        for off in all_offices:
            ts = by_off.get(off, [])
            holders = [holder_from_term(t, people) for t in ts]
            need = expected_map.get(off)
            if need is not None and len(holders) < need:
                for _ in range(need - len(holders)):
                    holders.append({
                        "name": "Not yet collected",
                        "person_id": "",
                        "party": "",
                        "notes": "No official name collected for this seat in this January.",
                    })
                    missing_n += 1
            have_n += sum(1 for h in holders if h.get("person_id"))
            layout = "heading-then-names" if len(holders) != 1 or (need and need > 1) else "office-and-name"
            offices.append({"office": off, "layout": layout, "holders": holders})
        note = ""
        if gid == "judicial":
            note = judicial_note
        if gid == "special-districts":
            note = special_note
        groups.append({
            "id": gid, "title": title, "offices": offices,
            "note": note, "sort_key": SORT.get(gid, gid[:3].upper()),
        })
        coverage.append({"year": year, "group": gid, "have": have_n, "not_collected": missing_n})

    snap = {
        "county": county,
        "county_number": county_number,
        "snapshot_year": year,
        "as_of": as_of,
        "as_of_label": (
            f"January {year} (as of {as_of}, after the first Monday in January "
            "and after January 3 congressional terms, America/Denver)"
        ),
        "intro": f"Names are the people in office in January {year} (as of January 8).",
        "groups": groups,
        "generated_from": f"data/county_officials/history/{slug}/terms.json",
        "retrieved": retrieved,
    }
    return snap, coverage


PROFILE_TEMPLATE = """<!DOCTYPE html>
<html lang="en" class="cand-local">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Profile — WyoVote</title>
    <meta name="description" content="{desc}">
    <link rel="icon" href="../../../assets/img/surveyor-icon.png" type="image/png">
    <link rel="stylesheet" href="../../../css/styles.css">
    <link rel="stylesheet" href="../../../assets/css/site.css">
    <link rel="stylesheet" href="../../../officials/profile.css">
  </head>
  <body class="pf cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="../../../index.html">
          <img src="../../../assets/img/surveyor-icon.png" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            <li><a href="../../../index.html">Home</a></li>
            <li><a href="../../../candidates.html" aria-current="page">Candidates</a></li>
            <li><a href="../../../committees.html">Committees</a></li>
            <li><a href="../../../counties.html">Counties</a></li>
            <li><a href="../../../officials.html">Officials</a></li>
            <li><a href="../../../people/index.html">Name Index</a></li>
            <li><a href="../../../research.html">Research</a></li>
            <li><a href="../../../archive.html">Archive</a></li>
          </ul>
        </nav>
      </div>
    </header>
    <main id="main" class="profile">
      <div class="wrap">
        <p class="back-row"><a class="back-btn" href="../../../counties/{slug}.html">← Back to {county} County</a></p>
        <section class="pf-head" aria-labelledby="h-name">
          <h1 id="h-name">{title}</h1>
          <p class="pf-sub">Profile</p>
        </section>
        <p class="cand-blurb">{blurb}</p>
        <section class="pf-card cand-research" aria-labelledby="h-results">
          <h2 id="h-results">Results</h2>
          <table class="cand-facts">{rows}</table>
          <div class="cand-sources-block">
            <h2 id="h-results-sources">Sources</h2>
            <ul class="cand-sources">{sources}</ul>
          </div>
        </section>
        <section class="pf-card cand-research" aria-labelledby="h-research">
          <h2 id="h-research">Research</h2>
          <table class="cand-facts"><tr><th scope="row">Residence</th><td>{county} County</td></tr>
          <tr><th scope="row">Background</th><td>Public information found for this Profile is limited to official election results and the officeholder history compiled from those results.</td></tr></table>
        </section>
      </div>
    </main>
    <footer class="site-footer">
      <div class="wrap footer-inner">
        <nav aria-label="Footer">
          <ul class="footer-links">
            <li><a href="../../../about.html">About</a></li>
            <li><a href="../../../privacy.html">Privacy</a></li>
            <li><a href="../../../contact.html">Contact</a></li>
            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v2.0.pdf">User's Guide</a></li>
          </ul>
        </nav>
        <p>&copy; 2026 WyoVote. All rights reserved.</p>
      </div>
    </footer>
  </body>
</html>
"""


def esc(s):
    return html.escape(str(s or ""), quote=True)


def existing_people_ids():
    ids = set()
    for path in (NAME_INDEX_PEOPLE, PEOPLE_DIR / "people_additions.csv"):
        if path.is_file():
            with path.open(newline="") as f:
                for row in csv.DictReader(f):
                    pid = (row.get("person_id") or "").strip()
                    if pid:
                        ids.add(pid)
    return ids


def write_people_additions(people: dict) -> int:
    path = PEOPLE_DIR / "people_additions.csv"
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["person_id", "slug", "display_name", "sort_name", "first", "middle",
              "last", "suffix", "aliases", "minted"]
    rows = []
    have = existing_people_ids()
    if path.is_file():
        with path.open(newline="") as f:
            rows = list(csv.DictReader(f))
            for row in rows:
                have.add(row.get("person_id") or "")
        # keep existing fieldnames if present
        with path.open(newline="") as f:
            r = csv.DictReader(f)
            if r.fieldnames:
                fields = list(r.fieldnames)
    added = 0
    for pid, p in people.items():
        if pid in have:
            continue
        row = {k: p.get(k, "") for k in fields}
        rows.append(row)
        have.add(pid)
        added += 1
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return added


def write_offices_held(terms: list, people: dict) -> int:
    path = PEOPLE_DIR / "offices_held_additions.csv"
    PEOPLE_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["person_id", "office", "office_level", "jurisdiction", "county",
              "district", "party", "start_date", "end_date", "status", "source", "role"]
    rows = []
    have = set()
    if path.is_file():
        with path.open(newline="") as f:
            r = csv.DictReader(f)
            if r.fieldnames:
                fields = list(r.fieldnames)
            for row in r:
                rows.append(row)
                have.add((row.get("person_id"), row.get("office"),
                          row.get("start_date") or row.get("term_start"),
                          row.get("end_date") or row.get("term_end")))
    added = 0
    for t in terms:
        start = t["term_start"]
        end = t["term_end"]
        key = (t["person_id"], t["office"], start, end)
        if key in have:
            continue
        rec = {k: "" for k in fields}
        srcs = t.get("sources") or []
        src = "; ".join((s.get("url") or s.get("label") or "") for s in srcs if isinstance(s, dict))
        rec.update({
            "person_id": t["person_id"],
            "office": t["office"],
            "office_level": t.get("office_group") or "",
            "jurisdiction": t.get("jurisdiction") or "",
            "county": "",
            "district": "",
            "party": t.get("party") or "",
            "start_date": start,
            "end_date": end,
            "status": t.get("how_took_office") or "",
            "source": src,
            "role": t.get("role") or "",
        })
        # drop any keys not in fieldnames
        rec = {k: rec.get(k, "") for k in fields}
        rows.append(rec)
        have.add(key)
        added += 1
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return added


def write_profiles(terms: list, people: dict, *, county: str, slug: str) -> int:
    existing_slugs = set()
    for d in (ROOT / "candidates").glob("*/c/*.html"):
        existing_slugs.add(d.stem)
    written = 0
    by_pid = defaultdict(list)
    for t in terms:
        by_pid[t["person_id"]].append(t)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    for pid, ts in by_pid.items():
        p = people.get(pid)
        if not p:
            continue
        slug_p = p["slug"]
        if slug_p in existing_slugs:
            continue
        rows_html = []
        src_html = []
        seen_src = set()
        for t in ts:
            label = f"{t.get('election_year') or t['term_start'][:4]} · {t['office']}"
            val = f"In office {t['term_start']} to {t['term_end']}"
            if t.get("how_took_office"):
                val += f" ({t['how_took_office']})"
            rows_html.append(f"<tr><th scope=\"row\">{esc(label)}</th><td>{esc(val)}</td></tr>")
            for s in t.get("sources") or []:
                url = s.get("url") or ""
                lab = s.get("label") or url
                if url and url not in seen_src:
                    src_html.append(
                        f'<li><a href="{esc(url)}">{esc(lab)}</a> '
                        f'<span class="ext">(leaves WyoVote)</span></li>'
                    )
                    seen_src.add(url)
                elif lab and lab not in seen_src:
                    src_html.append(f"<li>{esc(lab)}</li>")
                    seen_src.add(lab)
        if not src_html:
            src_html.append("<li>Official election results cited in the county officeholder history.</li>")
        offices = sorted({t["office"] for t in ts})
        blurb = (
            f"{p['display_name']} served in {county} County as "
            + (", ".join(offices) if offices else "an officeholder")
            + ". This thin Profile lists dated terms compiled from official results."
        )
        html_out = PROFILE_TEMPLATE.format(
            title=esc(p["display_name"]),
            desc=esc(f"{p['display_name']} — {county} County officeholder history."),
            slug=slug,
            county=esc(county),
            blurb=esc(blurb),
            rows="\n          ".join(rows_html),
            sources="\n            ".join(src_html),
        )
        (PROFILE_DIR / f"{slug_p}.html").write_text(html_out)
        existing_slugs.add(slug_p)
        written += 1
    return written


def write_terms_and_snapshots(*, county, county_number, slug, terms, people, expected,
                              retrieved, judicial_note="", special_note="",
                              precinct_note="", precinct_note_early="", precinct_cutoff=2021):
    out_dir = HISTORY / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    SHARED_H.mkdir(parents=True, exist_ok=True)
    terms_path = out_dir / "terms.json"
    payload = {
        "county": county,
        "county_number": county_number,
        "schema": "effective-dated officeholder terms; January snapshots are generated from these records",
        "retrieved": retrieved,
        "terms": terms,
    }
    terms_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    coverage_all = []
    for year in range(2015, 2027):
        snap, cov = build_snapshot(
            year, county=county, county_number=county_number, slug=slug,
            terms=terms, people=people, expected=expected, retrieved=retrieved,
            judicial_note=judicial_note, special_note=special_note,
            precinct_note=precinct_note, precinct_note_early=precinct_note_early,
            precinct_cutoff=precinct_cutoff,
        )
        (out_dir / f"{year}.json").write_text(json.dumps(snap, indent=2, ensure_ascii=False) + "\n")
        coverage_all.extend(cov)
    cov_path = out_dir / "coverage.csv"
    with cov_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "group", "have", "not_collected"])
        w.writeheader()
        w.writerows(coverage_all)
    return terms_path, cov_path, coverage_all


def print_coverage(coverage_all):
    groups = [g for g, _, _ in GROUP_META]
    print("\nCOVERAGE year x group (have / not_collected)")
    header = f"{'year':>6} " + " ".join(f"{g[:10]:>10}" for g in groups)
    print(header)
    by = defaultdict(dict)
    for r in coverage_all:
        by[r["year"]][r["group"]] = r
    for year in range(2015, 2027):
        bits = [f"{year:>6}"]
        for g in groups:
            r = by[year].get(g, {})
            bits.append(f"{str(r.get('have', '-'))}/{str(r.get('not_collected', '-')):>4}")
        print(" ".join(f"{b:>10}" for b in bits))


def load_name_index_people():
    out = {}
    if NAME_INDEX_PEOPLE.is_file():
        with NAME_INDEX_PEOPLE.open(newline="") as f:
            for row in csv.DictReader(f):
                pid = (row.get("person_id") or "").strip()
                if pid:
                    out[pid] = row
    add = PEOPLE_DIR / "people_additions.csv"
    if add.is_file():
        with add.open(newline="") as f:
            for row in csv.DictReader(f):
                pid = (row.get("person_id") or "").strip()
                if pid and pid not in out:
                    out[pid] = row
    return out


def attach_people_from_terms(terms, people):
    """Ensure every term person_id has a PEOPLE record, using the name index when present."""
    index = load_name_index_people()
    person = person_factory(people)
    for t in terms:
        pid = t["person_id"]
        if pid in people:
            continue
        row = index.get(pid)
        if row:
            display = row.get("display_name") or t["name"]
            first = row.get("first") or display.split()[0]
            last = row.get("last") or display.split()[-1]
            person(
                pid, display, first, last,
                middle=row.get("middle") or "",
                aliases=row.get("aliases") or "",
                minted=False,
                slug=row.get("slug") or "",
            )
        else:
            name = t["name"]
            parts = name.replace(",", " ").split()
            first = parts[0] if parts else name
            last = parts[-1] if parts else name
            person(pid, name, first, last, minted=True)
