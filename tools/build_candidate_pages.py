#!/usr/bin/env python3
"""Build preview candidate detail pages from the research store.

Reads one cycle of compact records and rewrites the Level 3 pages for
candidates who do not already have a 2026 officials deeper-dive page.
Sitting legislators stay linked from the county pages; this script does
not touch those links or the officials pages.

Compact data lives at preview/data/candidate-research/<cycle>/part-NN.json.
A future cycle (2024 or 2028) is a new JSON file plus:

    python3 tools/build_candidate_pages.py --cycle 2028-primary

To compile that JSON from a research archive (people/ and cycles/<cycle>/):

    python3 tools/build_candidate_pages.py --archive /path/to/archive --cycle 2026-primary

General election views read data/candidate-research/<cycle>/general.json and
update the preview pages only:

    python3 tools/build_candidate_pages.py --general

The archive's "not found" notes are dropped. Ranks and lean bands are not
written. Coefficients are not part of the store.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
INDEX = PREVIEW / "data" / "candidates-2026-primary.json"
DATA_DIR = ROOT / "data" / "candidate-research"
SHARD_LIMIT = 450_000
PAGES = PREVIEW / "candidates" / "2026-primary" / "c"
OFFICIALS = PREVIEW / "officials"

BLANK = {
    "",
    "not found",
    "none found",
    "none documented",
    "no website yet",
    "no website",
    "none",
    "unknown",
    "n/a",
    "na",
}
WYOFILE_NOTE = "Source: WyoFile election guide, as of Oct 29, 2026."
BACK_SCRIPT = r"""<script>
      (function () {
        var link = document.getElementById("cand-back");
        if (!link) return;
        function countyName(slug) {
          return slug.split("-").map(function (word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
          }).join(" ");
        }
        function useCounty(slug) {
          if (!/^[a-z]+(?:-[a-z]+)*$/.test(slug)) return false;
          var general = new URLSearchParams(location.search).get("e") === "general";
          link.setAttribute("href", "../" + slug + ".html" + (general ? "?e=general" : ""));
          link.textContent = "\u2190 Back to " + countyName(slug) + " County";
          return true;
        }
        var from = new URLSearchParams(location.search).get("from");
        if (from && useCounty(from)) return;
        if (!document.referrer) return;
        var ref;
        try { ref = new URL(document.referrer); } catch (error) { return; }
        if (ref.origin !== location.origin) return;
        var path = ref.pathname.replace(/\/+$/, "");
        var match = path.match(/\/candidates\/2026-primary\/([a-z]+(?:-[a-z]+)*)(?:\.html)?$/);
        if (!match) return;
        useCounty(match[1]);
      })();
    </script>"""


def clean(value) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.split("googletag")[0].strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    if text.lower().rstrip(".") in BLANK:
        return None
    return text or None


def fact_value(node) -> str | None:
    if isinstance(node, str):
        return clean(node)
    if isinstance(node, dict):
        return clean(node.get("value")) if isinstance(node.get("value"), str) else None
    return None


def sources_of(node) -> list[dict]:
    if isinstance(node, dict):
        raw = node.get("sources") or []
    elif isinstance(node, list):
        raw = node
    else:
        raw = []
    found = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or "").strip()
        name = (item.get("name") or "").strip()
        if url.startswith(("http://", "https://")) and name:
            found.append({"name": name, "url": url})
    return found


def money(amount) -> str | None:
    if not isinstance(amount, (int, float)):
        return None
    if abs(amount - round(amount)) < 0.001:
        return f"${int(round(amount)):,}"
    return f"${amount:,.2f}"


def pretty_date(text: str | None) -> str | None:
    if not text or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text or None
    return datetime.strptime(text, "%Y-%m-%d").strftime("%b. %-d, %Y").replace("May.", "May")


def ordinal(place: int) -> str:
    if 10 <= place % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(place % 10, "th")
    return f"{place}{suffix}"


def office_label(office: str, district: str | None) -> str:
    digits = "".join(ch for ch in (district or "") if ch.isdigit())
    if office == "State Senator" and digits:
        return f"Senate District {int(digits)}"
    if office == "State Representative" and digits:
        return f"House District {int(digits)}"
    if office == "U.S. Representative":
        return "United States Representative"
    if office == "U.S. Senator":
        return "United States Senator"
    return office


def website_href(value: str) -> str:
    if value.startswith(("http://", "https://")):
        return value
    return "https://" + value.lstrip("/")


def endorsements_text(value: str | None) -> str | None:
    text = clean(value)
    if not text:
        return None
    marker = "recommendations."
    if marker in text:
        rest = text.split(marker, 1)[1].strip(" .")
        return rest or None
    return text


def offices_text(node) -> str | None:
    if isinstance(node, dict):
        return None
    if not isinstance(node, list):
        return None
    lines = []
    for item in node:
        if not isinstance(item, dict):
            continue
        office = clean(item.get("office"))
        if not office:
            continue
        start = clean(str(item.get("start"))) if item.get("start") else None
        end = clean(str(item.get("end"))) if item.get("end") else None
        if start and end:
            lines.append(f"{office}, {start}–{end}")
        elif start:
            lines.append(f"{office}, {start}")
        else:
            lines.append(office)
    return "; ".join(lines) if lines else None


def display_name(person: dict, cycle: dict) -> str:
    if person.get("person_id") == "WY-PEARSON-LAURA":
        return "Laura Taliaferro (formerly Pearson)"
    return cycle.get("name_on_ballot") or person.get("full_name") or ""


def match_names(person: dict, cycle: dict) -> list[str]:
    names = [display_name(person, cycle), cycle.get("name_on_ballot"), person.get("full_name")]
    names.extend(person.get("aliases") or [])
    for value in (person.get("ballot_names") or {}).values():
        names.append(value)
    seen = []
    for name in names:
        if name and name not in seen:
            seen.append(name)
    return seen


def general_record(node) -> dict | None:
    if not isinstance(node, dict):
        return None
    outcome = clean(node.get("outcome") or "")
    if not outcome or outcome.casefold() in {"did not advance", "did not appear"}:
        return None
    return {
        "outcome": outcome,
        "votes": node.get("votes") if isinstance(node.get("votes"), int) else None,
        "pct": node.get("pct") if isinstance(node.get("pct"), (int, float)) else None,
        "place": node.get("place") if isinstance(node.get("place"), int) else None,
        "field": node.get("candidates_in_race") if isinstance(node.get("candidates_in_race"), int) and node.get("candidates_in_race") else None,
        "note": clean(node.get("note") or ""),
    }


def compile_record(person: dict, cycle: dict) -> dict:
    sources: list[dict] = []

    def add_sources(node):
        for item in sources_of(node):
            if not any(have["url"] == item["url"] for have in sources):
                sources.append(item)

    residence_bits = []
    city = (person.get("residence") or {}).get("city")
    county = (person.get("residence") or {}).get("county")
    if fact_value(city):
        residence_bits.append(fact_value(city))
        add_sources(city)
    if fact_value(county):
        residence_bits.append(f"{fact_value(county)} County")
        add_sources(county)
    residence = ", ".join(residence_bits) if residence_bits else None

    occupation = fact_value(person.get("occupation"))
    if occupation:
        add_sources(person.get("occupation"))
    education = fact_value(person.get("education"))
    if education:
        add_sources(person.get("education"))
    military = fact_value(person.get("military_service"))
    if military:
        add_sources(person.get("military_service"))

    prior = offices_text(person.get("offices_held"))
    if prior and isinstance(person.get("offices_held"), list):
        for item in person["offices_held"]:
            add_sources(item)

    web = (person.get("web") or {}).get("campaign_website")
    website = None
    if fact_value(web) and "." in fact_value(web):
        shown = fact_value(web)
        website = {"text": shown, "href": website_href(shown)}
        add_sources(web)

    background = []
    for note in cycle.get("background_notes") or []:
        text = fact_value(note)
        if text:
            background.append(text)
            add_sources(note)
    statement = (person.get("residence") or {}).get("statement_2026")
    statement_text = fact_value(statement)
    if statement_text and statement_text not in background:
        if not background:
            background.append(statement_text)
            add_sources(statement)

    positions = []
    raw_positions = cycle.get("positions")
    if isinstance(raw_positions, list):
        for item in raw_positions:
            if not isinstance(item, dict):
                continue
            topic = clean(item.get("topic"))
            text = clean(item.get("text"))
            if topic and text:
                positions.append({"topic": topic, "text": text})
                add_sources(item)

    endorse = endorsements_text((cycle.get("endorsements") or {}).get("value") if isinstance(cycle.get("endorsements"), dict) else None)
    if endorse:
        add_sources(cycle.get("endorsements"))

    finance = cycle.get("finance") if isinstance(cycle.get("finance"), dict) else {}
    fundraising = None
    if money(finance.get("raised")) or money(finance.get("spent")):
        contributors = []
        for donor in (finance.get("top_contributors") or [])[:5]:
            if not isinstance(donor, dict):
                continue
            name = clean(donor.get("name"))
            amount = money(donor.get("amount"))
            if name and amount:
                contributors.append(f"{name} ({amount})")
        fundraising = {
            "raised": money(finance.get("raised")),
            "spent": money(finance.get("spent")),
            "period": clean(finance.get("period")),
            "through": pretty_date(finance.get("through")),
            "primary_raised": money(finance.get("primary_raised")),
            "primary_spent": money(finance.get("primary_spent")),
            "contributors": contributors,
            "wyofile": "WyoFile" in (finance.get("committee_source") or ""),
        }
        add_sources(finance)
        if fundraising["raised"] == fundraising["primary_raised"] and fundraising["spent"] == fundraising["primary_spent"]:
            fundraising["primary_raised"] = None
            fundraising["primary_spent"] = None

    result = cycle.get("result") if isinstance(cycle.get("result"), dict) else {}
    outcome = clean(result.get("outcome"))
    result_out = None
    if outcome:
        result_out = {
            "outcome": outcome,
            "votes": result.get("votes") if isinstance(result.get("votes"), int) else None,
            "pct": result.get("pct") if isinstance(result.get("pct"), (int, float)) else None,
            "place": result.get("place") if isinstance(result.get("place"), int) else None,
            "field": result.get("candidates_in_race") if isinstance(result.get("candidates_in_race"), int) and result.get("candidates_in_race") else None,
            "note": clean(result.get("note")),
            "party": cycle.get("party"),
        }
        add_sources(result)

    return {
        "person_id": person["person_id"],
        "name": cycle.get("name_on_ballot") or person.get("full_name"),
        "blurb": clean(cycle.get("blurb")),
        "office": office_label(cycle.get("office_sought") or "", cycle.get("district")),
        "party": cycle.get("party"),
        "incumbent": bool(cycle.get("incumbent")),
        "residence": residence,
        "occupation": occupation,
        "background": background,
        "education": education,
        "military": military,
        "prior_offices": prior,
        "website": website,
        "positions": positions,
        "endorsements": endorse,
        "fundraising": fundraising,
        "result": result_out,
        "general": general_record(cycle.get("general_result")),
        "sources": sources,
        "display_name": display_name(person, cycle),
        "match_names": match_names(person, cycle),
    }


def load_archive(archive: Path, cycle: str) -> list[dict]:
    people = archive / "people"
    cycles = archive / "cycles" / cycle
    records = []
    for path in sorted(cycles.glob("*.json")):
        cycle_row = json.loads(path.read_text(encoding="utf-8"))
        person = json.loads((people / f"{path.stem}.json").read_text(encoding="utf-8"))
        records.append(compile_record(person, cycle_row))
    return records


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def result_sentence(result: dict) -> str:
    parts = [result["outcome"]]
    if result.get("votes") is not None:
        vote = f"{result['votes']:,} votes"
        if result.get("pct") is not None:
            vote += f" ({result['pct']:g}%)"
        parts.append(vote)
    if result.get("place") and result.get("field"):
        parts.append(f"{ordinal(result['place'])} of {result['field']}")
    text = ". ".join(parts[:1] + [", ".join(parts[1:])]) if len(parts) > 1 else parts[0]
    if len(parts) > 1:
        text = parts[0] + ", " + ", ".join(parts[1:])
    else:
        text = parts[0]
    if result.get("note"):
        note = result["note"][0].upper() + result["note"][1:]
        text += ". " + note
    if not text.endswith("."):
        text += "."
    return text


def fundraising_sentence(row: dict) -> str:
    bits = []
    if row.get("raised"):
        bits.append(f"Raised {row['raised']}")
    if row.get("spent"):
        bits.append(f"Spent {row['spent']}")
    sentence = ". ".join(bits) + "." if bits else ""
    when = []
    if row.get("period"):
        when.append(row["period"])
    if row.get("through"):
        when.append(f"through {row['through']}")
    if when:
        sentence += " " + ", ".join(when) + "."
    if row.get("primary_raised") or row.get("primary_spent"):
        primary = []
        if row.get("primary_raised"):
            primary.append(f"raised {row['primary_raised']}")
        if row.get("primary_spent"):
            primary.append(f"spent {row['primary_spent']}")
        sentence += " Primary election: " + ", ".join(primary) + "."
    if row.get("contributors"):
        sentence += " Largest reported contributors: " + "; ".join(row["contributors"]) + "."
    if row.get("wyofile"):
        sentence += " " + WYOFILE_NOTE
    return sentence.strip()


def table_rows(record: dict) -> list[tuple[str, str]]:
    rows = []
    if record.get("residence"):
        rows.append(("Residence", esc(record["residence"])))
    if record.get("occupation"):
        rows.append(("Occupation", esc(record["occupation"])))
    if record.get("background"):
        body = "".join(f"<p>{esc(part)}</p>" for part in record["background"])
        rows.append(("Background", body))
    if record.get("education"):
        rows.append(("Education", esc(record["education"])))
    if record.get("military"):
        rows.append(("Military", esc(record["military"])))
    if record.get("prior_offices"):
        rows.append(("Prior offices", esc(record["prior_offices"])))
    if record.get("website"):
        site = record["website"]
        rows.append(("Website", f'<a href="{esc(site["href"])}">{esc(site["text"])}</a>'))
    if record.get("positions"):
        chunks = []
        for item in record["positions"]:
            chunks.append(f'<p class="cand-topic">{esc(item["topic"])}</p><p>{esc(item["text"])}</p>')
        rows.append(("Issue positions", "".join(chunks)))
    if record.get("endorsements"):
        rows.append(("Endorsements", esc(record["endorsements"])))
    if record.get("fundraising"):
        rows.append(("Fundraising", esc(fundraising_sentence(record["fundraising"]))))
    if record.get("result"):
        rows.append(("2026 primary result", esc(result_sentence(record["result"]))))
    return rows


def research_html(record: dict) -> str:
    rows = table_rows(record)
    parts = ['<section class="cand-research" aria-labelledby="h-research">', '            <h2 id="h-research">Research</h2>']
    if rows:
        parts.append('            <table class="cand-facts">')
        for label, value in rows:
            parts.append(f'              <tr><th scope="row">{esc(label)}</th><td>{value}</td></tr>')
        parts.append("            </table>")
    if record.get("sources"):
        parts.append('            <h2 id="h-sources">Sources</h2>')
        parts.append('            <ul class="cand-sources">')
        for source in record["sources"]:
            parts.append(f'              <li><a href="{esc(source["url"])}">{esc(source["name"])}</a></li>')
        parts.append("            </ul>")
    parts.append("          </section>")
    return "\n".join(parts)


def page_body(record: dict) -> str:
    lines = []
    if record.get("blurb"):
        lines.append(f'          <p class="cand-blurb">{esc(record["blurb"])}</p>')
    meta = f'{esc(record["office"])} · {esc(record["party"])}'
    if record.get("incumbent"):
        meta += ' <span class="cand-inc">Incumbent</span>'
    lines.append(f'          <p class="cand-meta">{meta}</p>')
    if record.get("result"):
        lines.append(f'          <p class="cand-res">Primary result: {esc(record["result"]["outcome"])}</p>')
    lines.append("          " + research_html(record).replace("\n", "\n          ").strip())
    return "\n".join(lines)


def officials_slugs() -> dict[str, str]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    linked = {}
    for cand in index["candidates"]:
        off = cand.get("off")
        if off and (OFFICIALS / f"{off}-deep.html").is_file():
            linked[cand["name"].casefold()] = cand["slug"]
    return linked


def slug_for(name: str, index_by_name: dict) -> str | None:
    row = index_by_name.get(name.casefold())
    return row["slug"] if row else None


def update_back_script(text: str) -> str:
    if 'new URLSearchParams(location.search).get("from")' in text:
        return text
    start = text.find('<script>')
    end = text.find('</script>')
    if start == -1 or end == -1 or 'cand-back' not in text[start:end]:
        raise SystemExit("back script missing")
    return text[:start] + BACK_SCRIPT + text[end + len("</script>"):]


def write_pages(records: list[dict]) -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    by_name = {row["name"].casefold(): row for row in index["candidates"]}
    sitting = officials_slugs()
    updated = 0
    for record in records:
        key = record["name"].casefold()
        if key in sitting:
            continue
        slug = slug_for(record["name"], by_name)
        if not slug:
            raise SystemExit(f"no page slug for {record['name']}")
        path = PAGES / f"{slug}.html"
        if not path.is_file():
            raise SystemExit(f"missing page {path}")
        text = path.read_text(encoding="utf-8")
        description = record.get("blurb") or f"{record['name']}, {record['office']}, 2026 primary."
        description = re.sub(r"\s+", " ", description)[:180]
        text = re.sub(
            r'(<meta name="description" content=").*?(")',
            lambda m: m.group(1) + esc(description) + m.group(2),
            text,
            count=1,
        )
        body = (
            '      <section class="page-body">\n'
            '        <div class="wrap">\n'
            f"{page_body(record)}\n"
            "        </div>\n"
            "      </section>\n"
            "    </main>"
        )
        text, n = re.subn(
            r"      <section class=\"page-body\">.*?</main>",
            lambda m: body,
            text,
            count=1,
            flags=re.S,
        )
        if n != 1:
            raise SystemExit(f"could not replace body of {slug}")
        text = update_back_script(text)
        path.write_text(text, encoding="utf-8")
        updated += 1
    return updated


def write_shards(records: list[dict], cycle: str) -> None:
    folder = DATA_DIR / cycle
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.json"):
        old.unlink()
    single = DATA_DIR / f"{cycle}.json"
    if single.is_file():
        single.unlink()
    shards: list[list[dict]] = []
    current: list[dict] = []
    size = 2
    for record in records:
        encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        extra = len(encoded.encode("utf-8")) + 1
        if current and size + extra > SHARD_LIMIT:
            shards.append(current)
            current = []
            size = 2
        current.append(record)
        size += extra
    if current:
        shards.append(current)
    for index, shard in enumerate(shards, 1):
        path = folder / f"part-{index:02d}.json"
        path.write_text(json.dumps(shard, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size} bytes, {len(shard)} records)")


def read_shards(cycle: str) -> list[dict]:
    folder = DATA_DIR / cycle
    records = []
    paths = sorted(folder.glob("part-*.json"))
    single = DATA_DIR / f"{cycle}.json"
    if single.is_file():
        paths.append(single)
    if not paths:
        raise SystemExit(f"no research data for {cycle}")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(payload if isinstance(payload, list) else [payload])
    return records


COUNTY_ORDER = [
    "Albany", "Big Horn", "Campbell", "Carbon", "Converse", "Crook", "Fremont",
    "Goshen", "Hot Springs", "Johnson", "Laramie", "Lincoln", "Natrona",
    "Niobrara", "Park", "Platte", "Sheridan", "Sublette", "Sweetwater", "Teton",
    "Uinta", "Washakie", "Weston",
]
FED_ORDER = ["U.S. Senator", "U.S. Representative"]
STATE_ORDER = [
    "Governor", "Secretary of State", "State Auditor", "State Treasurer",
    "Superintendent of Public Instruction",
]
PARTY_RANK = {"Republican": 0, "Democratic": 1}
HOW_TO = (
    "<strong>How to use this page.</strong> Races are grouped by office. "
    "Click any candidate's name to see their details. Districts that cross "
    "county lines appear on every county they cover."
)


def county_slug(name: str) -> str:
    return name.lower().replace(" ", "-")


def person_slug(name: str) -> str:
    if name == "Laura Taliaferro (formerly Pearson)":
        return "laura-taliaferro"
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return slug


def box_title(office: str, district: str | None) -> str:
    digits = "".join(ch for ch in (district or "") if ch.isdigit())
    if office in {"U.S. President", "President"}:
        return "U.S. President"
    if office == "U.S. Senator":
        return "U.S. Senate"
    if office == "U.S. Representative":
        return "U.S. House"
    if office == "State Auditor":
        return "Auditor"
    if office == "State Treasurer":
        return "Treasurer"
    if office == "Superintendent of Public Instruction":
        return "Superintendent"
    if office == "State Senator" and digits:
        return f"State Senate SD{int(digits):02d}"
    if office == "State Representative" and digits:
        return f"State House HD{int(digits):02d}"
    return office


def group_name(office: str) -> str:
    if office in FED_ORDER:
        return "Federal"
    if office in STATE_ORDER:
        return "Statewide"
    if office == "State Senator":
        return "State Senate"
    if office == "State Representative":
        return "State House"
    return "Other"


def party_abbr(party: str) -> str:
    return {
        "Republican": "(R)",
        "Democratic": "(D)",
        "Libertarian": "(L)",
        "Constitution": "(C)",
        "Independent": "(I)",
    }.get(party, f"({party})")


def officials_index() -> dict[str, str]:
    found = {}
    for path in OFFICIALS.glob("*-deep.html"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", text)
        if not match:
            continue
        name = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        found[name.casefold()] = path.name.replace("-deep.html", "")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    for cand in index["candidates"]:
        off = cand.get("off")
        if off and (OFFICIALS / f"{off}-deep.html").is_file():
            found.setdefault(cand["name"].casefold(), off)
    found.setdefault("laura taliaferro (formerly pearson)", "taliaferro")
    found.setdefault("laura taliaferro", "taliaferro")
    found.setdefault("laura pearson", "taliaferro")
    found.setdefault("laura taliaferro pearson", "taliaferro")
    return found


def sitting_slug(record: dict, officials: dict[str, str]) -> str | None:
    if record.get("person_id") == "WY-PEARSON-LAURA":
        return "taliaferro"
    for name in record.get("match_names") or [record.get("display_name"), record.get("name")]:
        if name and name.casefold() in officials:
            return officials[name.casefold()]
    return None


def preview_shell(title: str, description: str, depth: int, body: str, current: str = "candidates") -> str:
    # depth is the number of directories under preview/.
    root = "../" * depth
    css = "../" * (depth + 1) + "css/styles.css"
    preview_css = root + "preview.css"
    assets = root + "assets/img/surveyor-icon.png"
    home = root + "index.html"

    def nav(name, href, key):
        current_attr = ' aria-current="page"' if key == current else ""
        return f'<li><a href="{href}"{current_attr}>{name}</a></li>'

    links = [
        nav("Home", home, "home"),
        nav("Archive", root + "archive.html", "archive"),
        nav("Candidates", root + "candidates.html", "candidates"),
        nav("Committees", root + "archive/committees.html", "committees"),
        nav("Counties", root + "archive/counties.html", "counties"),
        nav("Officials", root + "officials.html", "officials"),
        nav("Research", root + "research.html", "research"),
    ]
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="icon" href="{assets}" type="image/png">
    <link rel="stylesheet" href="{css}">
    <link rel="stylesheet" href="{preview_css}">
  </head>
  <body class="cand-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <p class="preview-banner" role="status">PREVIEW, not the live site</p>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="brand" href="{home}">
          <img src="{assets}" alt="" width="135" height="152">
          <span class="site-name">WyoVote</span>
        </a>
        <nav class="site-nav" aria-label="Site">
          <ul>
            {"".join(links)}
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
    {BACK_SCRIPT if depth == 3 else ""}
  </body>
</html>
"""


def archive_detail_inner(record: dict, officials_slug: str | None) -> str:
    lines = []
    if record.get("blurb"):
        lines.append(f'<p class="cand-blurb">{esc(record["blurb"])}</p>')
    place = record.get("party") or ""
    if record.get("residence"):
        place = f"{place} · {record['residence']}" if place else record["residence"]
    if place:
        lines.append(f'<p class="cand-meta">{esc(place)}</p>')
    if record.get("result"):
        lines.append(f'<p class="cand-res">Primary result: {esc(result_sentence(record["result"]))}</p>')
    if record.get("general"):
        lines.append(f'<p class="cand-res">General result: {esc(result_sentence(record["general"]))}</p>')
    if officials_slug:
        lines.append(
            f'<p><a href="../../../officials/{esc(officials_slug)}-deep.html">Officials deeper dive</a></p>'
        )
    rows = []
    if record.get("occupation"):
        rows.append(("Occupation", esc(record["occupation"])))
    if record.get("background"):
        rows.append(("Background", "".join(f"<p>{esc(part)}</p>" for part in record["background"])))
    if record.get("education"):
        rows.append(("Education", esc(record["education"])))
    if record.get("military"):
        rows.append(("Military", esc(record["military"])))
    if record.get("prior_offices"):
        rows.append(("Prior offices", esc(record["prior_offices"])))
    if record.get("positions"):
        chunks = "".join(
            f'<p class="cand-topic">{esc(item["topic"])}</p><p>{esc(item["text"])}</p>'
            for item in record["positions"]
        )
        rows.append(("Positions", chunks))
    if record.get("endorsements"):
        rows.append(("Endorsements", esc(record["endorsements"])))
    if record.get("fundraising"):
        rows.append(("Fundraising", esc(fundraising_sentence(record["fundraising"]))))
    if record.get("website"):
        site = record["website"]
        rows.append(("Website", f'<a href="{esc(site["href"])}">{esc(site["text"])}</a>'))
    if rows or record.get("sources"):
        lines.append('<section class="cand-research" aria-labelledby="h-research">')
        if rows:
            lines.append('<h2 id="h-research">Research</h2>')
            lines.append('<table class="cand-facts">')
            lines.extend(f'<tr><th scope="row">{esc(label)}</th><td>{value}</td></tr>' for label, value in rows)
            lines.append("</table>")
        if record.get("sources"):
            lines.append('<h2 id="h-sources">Sources</h2>')
            lines.append('<ul class="cand-sources">')
            lines.extend(
                f'<li><a href="{esc(source["url"])}">{esc(source["name"])}</a></li>'
                for source in record["sources"]
            )
            lines.append("</ul>")
        lines.append("</section>")
    return "\n".join("          " + line for line in lines)


def generate_archive(records: list[dict], cycle: str) -> dict[str, int]:
    year = cycle.split("-")[0]
    primary_dates = {"2024": "August 20, 2024", "2022": "August 16, 2022", "2026": "August 18, 2026"}
    date_line = primary_dates.get(year, year)
    officials = officials_index()
    folder = PREVIEW / "candidates" / cycle
    detail_dir = folder / "c"
    detail_dir.mkdir(parents=True, exist_ok=True)
    used: dict[str, str] = {}
    prepared = []
    for record in records:
        name = record.get("display_name") or record["name"]
        slug = person_slug(name)
        if slug in used and used[slug] != record["person_id"]:
            slug = f"{slug}-{record['person_id'].split('-')[-1].lower()}"
        used[slug] = record["person_id"]
        prepared.append((record, name, slug, sitting_slug(record, officials)))
    by_county: dict[str, list] = {county: [] for county in COUNTY_ORDER}
    for record, name, slug, official in prepared:
        counties = record.get("counties") or ["Statewide"]
        targets = COUNTY_ORDER if counties == ["Statewide"] else [c for c in counties if c in by_county]
        for county in targets:
            by_county[county].append((record, name, slug))
        body = (
            '      <div class="wrap back-wrap">\n'
            f'        <p class="back-row"><a class="back-btn" id="cand-back" href="../../../candidates.html">← Back to Candidates</a></p>\n'
            "      </div>\n"
            '      <section class="page-hero"><div class="wrap">\n'
            f"          <h1>{esc(name)}</h1>\n"
            "      </div></section>\n"
            '      <section class="page-body"><div class="wrap">\n'
            f"{archive_detail_inner(record, official)}\n"
            "      </div></section>"
        )
        page = preview_shell(
            f"{name} — {year} Primary — WyoVote",
            record.get("blurb") or f"{name}, {record.get('office')}, {year} primary.",
            3,
            body,
        )
        (detail_dir / f"{slug}.html").write_text(page, encoding="utf-8")
    for county in COUNTY_ORDER:
        races: dict[tuple, list] = {}
        for record, name, slug in by_county[county]:
            key = (record.get("_office") or record.get("office"), record.get("_district"))
            races.setdefault(key, []).append((record, name, slug))
        groups = []
        for title, offices in (
            ("Federal", FED_ORDER),
            ("Statewide", STATE_ORDER),
            ("State Senate", ["State Senator"]),
            ("State House", ["State Representative"]),
        ):
            keys = [key for key in races if key[0] in offices]
            keys.sort(key=lambda item: (offices.index(item[0]) if item[0] in offices else 99, int("".join(ch for ch in (item[1] or "0") if ch.isdigit()) or 0)))
            if not keys:
                continue
            blocks = []
            for key in keys:
                people = races[key]
                people.sort(key=lambda item: (PARTY_RANK.get(item[0].get("party"), 9), item[1]))
                items = []
                for record, name, slug in people:
                    result = (record.get("result") or {}).get("outcome") or ""
                    items.append(
                        f'<li><a href="c/{esc(slug)}.html?from={county_slug(county)}">{esc(name)}</a> '
                        f'<span class="cand-abbr">{esc(party_abbr(record.get("party") or ""))}</span> '
                        f'<span class="cand-res">{esc(result)}</span></li>'
                    )
                blocks.append(
                    '<section class="cand-race">\n'
                    f"            <h3>{esc(box_title(key[0], key[1]))}</h3>\n"
                    '            <ul class="cand-names">\n              '
                    + "\n              ".join(items)
                    + "\n            </ul>\n          </section>"
                )
            groups.append(
                '<section class="cand-group">\n'
                f'          <h2 class="cand-group-title">{title}</h2>\n'
                '          <div class="cand-race-grid">\n            '
                + "\n            ".join(blocks)
                + "\n          </div>\n        </section>"
            )
        body = (
            '      <div class="wrap back-wrap">\n'
            '        <p class="back-row"><a class="back-btn" href="index.html">← Back to '
            f"{year} Primary</a></p>\n"
            "      </div>\n"
            '      <section class="page-hero"><div class="wrap">\n'
            f"          <h1>{esc(county)} County</h1>\n"
            "      </div></section>\n"
            '      <section class="page-body"><div class="wrap">\n'
            f"          <p>{esc(date_line)} primary.</p>\n"
            f'          <p class="cand-how">{HOW_TO}</p>\n          '
            + "\n          ".join(groups)
            + "\n      </div></section>"
        )
        page = preview_shell(
            f"{county} County — {year} Primary — WyoVote",
            f"{year} primary candidates in {county} County.",
            2,
            body,
        )
        (folder / f"{county_slug(county)}.html").write_text(page, encoding="utf-8")
    county_items = "\n".join(
        f'            <li><a href="{county_slug(name)}.html">{esc(name)}</a></li>'
        for name in COUNTY_ORDER
    )
    grid = (
        '      <div class="wrap back-wrap">\n'
        '        <p class="back-row"><a class="back-btn" href="../../candidates.html">← Back to Candidates</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{year} Primary</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"          <p>{esc(date_line)}. Federal, statewide, and legislative races. Choose a county.</p>\n"
        f'          <ul class="cand-counties">\n{county_items}\n          </ul>\n'
        "      </div></section>"
    )
    (folder / "index.html").write_text(
        preview_shell(
            f"{year} Primary — WyoVote",
            f"{year} Wyoming primary candidates by county.",
            2,
            grid,
        ),
        encoding="utf-8",
    )
    return {"counties": len(COUNTY_ORDER), "details": len(prepared), "index": 1}


GENERAL_CYCLES = ("2026-primary", "2024-primary", "2022-primary")
GENERAL_FED = ["U.S. President", "U.S. Senator", "U.S. Representative"]
HOW_GENERAL = (
    "<strong>How to use this page.</strong> Races are grouped by office. "
    "Click any candidate's name to see their details. A check mark shows the winner. "
    "Districts that cross county lines appear on every county they cover."
)
HEAD_ELECTION = """<script>
      document.documentElement.classList.toggle("cand-general", new URLSearchParams(location.search).get("e") === "general");
      if (document.documentElement.classList.contains("cand-general") && document.title.indexOf("Primary") !== -1) {
        document.title = document.title.replace("Primary", "General");
      }
    </script>"""
ARIA_ELECTION = """<script>
      (function () {
        var general = document.documentElement.classList.contains("cand-general");
        var nodes = document.querySelectorAll(".cand-election-btn");
        for (var i = 0; i < nodes.length; i++) {
          var on = nodes[i].getAttribute("data-election") === (general ? "general" : "primary");
          if (on) nodes[i].setAttribute("aria-current", "true");
          else nodes[i].removeAttribute("aria-current");
        }
      })();
    </script>"""


def certification_label(status: str) -> str:
    hidden = "" if status != "certified" else " hidden"
    return f'<p class="cand-unofficial"{hidden}>Unofficial, awaiting canvass</p>'


def test_certification_label() -> None:
    unofficial = certification_label("unofficial")
    official = certification_label("certified")
    if "hidden" in unofficial or "Unofficial, awaiting canvass" not in unofficial:
        raise SystemExit("unofficial label test failed")
    if " hidden" not in official or "Unofficial, awaiting canvass" not in official:
        raise SystemExit("certified label test failed")
    print("certification label test: PASS")


def long_date(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%B %-d, %Y")


def fmt_pct(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return str(value)


def general_sentence(candidate: dict, office: str, district: str | None) -> str:
    bits = [box_title(office, district), candidate.get("party") or ""]
    votes = candidate.get("votes")
    pct = candidate.get("pct")
    if isinstance(votes, int):
        vote = f"{votes:,} votes"
        if isinstance(pct, (int, float)):
            vote += f" ({fmt_pct(pct)}%)"
        bits.append(vote)
    bits.append(candidate.get("outcome") or "")
    return ", ".join(bit for bit in bits if bit) + "."


def norm_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold().replace(".", "")).strip()


def with_general_query(chunk: str) -> str:
    def repl(match: re.Match) -> str:
        href = match.group(1)
        if "e=general" in href or href.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        joiner = "&" if "?" in href else "?"
        return f'href="{href}{joiner}e=general"'

    return re.sub(r'href="([^"]+)"', repl, chunk)


def election_buttons(filename: str) -> str:
    return (
        '<div class="cand-election" role="group" aria-label="Election">\n'
        f'            <a class="cand-election-btn" data-election="primary" href="{esc(filename)}">Primary</a>\n'
        f'            <a class="cand-election-btn" data-election="general" href="{esc(filename)}?e=general">General</a>\n'
        "          </div>"
    )


def ensure_election_script(text: str) -> str:
    text = re.sub(
        r"\s*<script>\s*document\.documentElement\.classList\.toggle\(\"cand-general\".*?</script>",
        "",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\s*<script>\s*\(function \(\) \{\s*var general = document\.documentElement\.classList\.contains\(\"cand-general\"\);.*?</script>",
        "",
        text,
        flags=re.S,
    )
    text = text.replace("</head>", "\n    " + HEAD_ELECTION.strip() + "\n  </head>", 1)
    text = text.replace("</body>", "\n    " + ARIA_ELECTION.strip() + "\n  </body>", 1)
    return text


def switch_h1(text: str) -> str:
    if re.search(r"<h1><span class=\"cand-view-primary\">", text):
        return text
    match = re.search(r"<h1>([^<]+)</h1>", text)
    if not match or "Primary" not in match.group(1):
        return text
    label = match.group(1)
    general = label.replace("Primary", "General")
    repl = (
        f'<h1><span class="cand-view-primary">{label}</span>'
        f'<span class="cand-view-general">{general}</span></h1>'
    )
    return text[: match.start()] + repl + text[match.end() :]


def add_general_back(text: str) -> str:
    if "back-btn cand-view-general" in text:
        return text
    match = re.search(r'<p class="back-row"><a class="back-btn" href="([^"]+)">([^<]+)</a></p>', text)
    if not match or "Home" in match.group(2):
        return text
    href, label = match.group(1), match.group(2)
    joiner = "&" if "?" in href else "?"
    repl = (
        '<p class="back-row">'
        f'<a class="back-btn cand-view-primary" href="{href}">{label}</a>'
        f'<a class="back-btn cand-view-general" href="{href}{joiner}e=general">{label.replace("Primary", "General")}</a>'
        "</p>"
    )
    return text[: match.start()] + repl + text[match.end() :]


def insert_buttons(text: str, filename: str) -> str:
    if 'class="cand-election"' in text:
        return text
    token = '<section class="page-body">'
    start = text.find(token)
    if start < 0:
        raise SystemExit("page body missing")
    wrap = text.find('<div class="wrap">', start)
    if wrap < 0:
        raise SystemExit("page body wrap missing")
    end = wrap + len('<div class="wrap">')
    return text[:end] + "\n          " + election_buttons(filename) + text[end:]


def insert_general_line(text: str, sentence: str) -> str:
    line = f'<p class="cand-res cand-general-line">General result: {esc(sentence)}</p>'
    pattern = r"[ \t]*<p class=\"cand-res(?: cand-general-line)?\">General result:.*?</p>\n?"
    if re.search(pattern, text):
        return re.sub(pattern, "          " + line + "\n", text, count=1)
    for marker in (
        r"(<p class=\"cand-res\">Primary result:.*?</p>)",
        r"(<p class=\"cand-meta\">.*?</p>)",
        r"(<p class=\"cand-blurb\">.*?</p>)",
    ):
        if re.search(marker, text):
            return re.sub(marker, r"\1\n          " + line, text, count=1)
    raise SystemExit("could not place general result line")


def patch_back_script(text: str) -> str:
    old = 'link.setAttribute("href", "../" + slug + ".html");'
    new = (
        'var general = new URLSearchParams(location.search).get("e") === "general";\n'
        '          link.setAttribute("href", "../" + slug + ".html" + (general ? "?e=general" : ""));'
    )
    if old in text:
        return text.replace(old, new, 1)
    return text


def load_name_slugs(detail_dir: Path) -> dict[str, str]:
    found = {}
    if not detail_dir.is_dir():
        return found
    for path in detail_dir.glob("*.html"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
        if not match:
            continue
        name = html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        found[norm_name(name)] = path.stem
    return found


def shard_name_index(cycle: str) -> dict[str, tuple[dict, list[str]]]:
    try:
        records = read_shards(cycle)
    except SystemExit:
        return {}
    found = {}
    for record in records:
        names = [record.get("display_name"), record.get("name")]
        names.extend(record.get("match_names") or [])
        found[record["person_id"]] = (record, [name for name in names if name])
    return found


def resolve_slug(person_id: str, ballot: str, shards: dict, slugs: dict[str, str], used: dict[str, str]) -> str:
    if person_id == "WY-PEARSON-LAURA":
        return "laura-taliaferro"
    record, names = shards.get(person_id, ({}, []))
    for name in list(names) + [ballot]:
        key = norm_name(name)
        if key in slugs:
            return slugs[key]
    slug = person_slug(ballot if person_id != "WY-PEARSON-LAURA" else "Laura Taliaferro (formerly Pearson)")
    if slug in used and used[slug] != person_id:
        slug = f"{slug}-{person_id.split('-')[-1].lower()}"
    return slug


def general_only_inner(candidate: dict, office: str, district: str | None, when: str) -> str:
    name = candidate["name_on_ballot"]
    if candidate["person_id"] == "WY-PEARSON-LAURA":
        name = "Laura Taliaferro (formerly Pearson)"
    party = candidate.get("party") or ""
    outcome = candidate.get("outcome") or ""
    title = box_title(office, district)
    if outcome == "Unopposed":
        blurb = f"{name} ({party}). Unopposed in the {when} general election for {title}"
    elif outcome == "Won":
        blurb = f"{name} ({party}). Won the {when} general election for {title}"
    else:
        blurb = f"{name} ({party}). Lost the {when} general election for {title}"
    if isinstance(candidate.get("votes"), int) and isinstance(candidate.get("pct"), (int, float)):
        blurb += f" with {candidate['votes']:,} votes ({fmt_pct(candidate['pct'])}%)"
    blurb += "."
    sources = []
    for source in candidate.get("sources") or []:
        url = (source.get("url") or "").strip()
        label = (source.get("name") or "").strip()
        if url.startswith(("http://", "https://")) and label:
            sources.append(f'            <li><a href="{esc(url)}">{esc(label)}</a></li>')
    source_html = ""
    if sources:
        source_html = (
            '          <h2 id="h-sources">Sources</h2>\n'
            '          <ul class="cand-sources">\n'
            + "\n".join(sources)
            + "\n          </ul>"
        )
    return (
        f'          <p class="cand-blurb">{esc(blurb)}</p>\n'
        f'          <p class="cand-meta">{esc(party)}</p>\n'
        f'          <p class="cand-res cand-general-line">General result: {esc(general_sentence(candidate, office, district))}</p>\n'
        + source_html
    )


def write_missing_detail(cycle: str, slug: str, candidate: dict, office: str, district: str | None, when: str, shards: dict, officials: dict) -> None:
    folder = PREVIEW / "candidates" / cycle / "c"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{slug}.html"
    name = candidate["name_on_ballot"]
    if candidate["person_id"] == "WY-PEARSON-LAURA":
        name = "Laura Taliaferro (formerly Pearson)"
    year = cycle.split("-")[0]
    record = shards.get(candidate["person_id"], ({}, []))[0]
    if record:
        if cycle == "2026-primary":
            inner = page_body(record)
        else:
            inner = archive_detail_inner(record, sitting_slug(record, officials))
        inner = insert_general_line(inner, general_sentence(candidate, office, district))
        if cycle == "2026-primary":
            official = sitting_slug(record, officials)
            if official and "officials/" not in inner:
                link = f'<p><a href="../../../officials/{esc(official)}-deep.html">Officials deeper dive</a></p>'
                inner = inner.replace(
                    '<p class="cand-res cand-general-line">',
                    link + '\n          <p class="cand-res cand-general-line">',
                    1,
                )
        description = record.get("blurb") or f"{name}, {record.get('office')}, {year}."
    else:
        inner = general_only_inner(candidate, office, district, when)
        description = re.sub(r"<[^>]+>", "", inner.split("</p>", 1)[0])
        description = html.unescape(re.sub(r"\s+", " ", description)).strip()
    description = re.sub(r"\s+", " ", description)[:180]
    back_href = "../../../candidates.html" if cycle == "2026-primary" else "../index.html"
    body = (
        '      <div class="wrap back-wrap">\n'
        f'        <p class="back-row"><a class="back-btn" id="cand-back" href="{back_href}">← Back to Candidates</a></p>\n'
        "      </div>\n"
        '      <section class="page-hero"><div class="wrap">\n'
        f"          <h1>{esc(name)}</h1>\n"
        "      </div></section>\n"
        '      <section class="page-body"><div class="wrap">\n'
        f"{inner}\n"
        "      </div></section>"
    )
    path.write_text(
        preview_shell(f"{name} — {year} Primary — WyoVote", description, 3, body),
        encoding="utf-8",
    )


def render_general_groups(races: list[dict], county: str, slug_of: dict[str, str]) -> str:
    blocks_by_title = []
    for title, offices in (
        ("Federal", GENERAL_FED),
        ("Statewide", STATE_ORDER),
        ("State Senate", ["State Senator"]),
        ("State House", ["State Representative"]),
    ):
        picked = [race for race in races if race.get("office_sought") in offices]
        picked.sort(
            key=lambda race: (
                offices.index(race["office_sought"]),
                int("".join(ch for ch in (race.get("district") or "0") if ch.isdigit()) or 0),
            )
        )
        if not picked:
            continue
        race_html = []
        for race in picked:
            people = sorted(
                race["candidates"],
                key=lambda cand: (
                    cand.get("place") if isinstance(cand.get("place"), int) else 99,
                    cand.get("name_on_ballot") or "",
                ),
            )
            items = []
            for cand in people:
                slug = slug_of[cand["person_id"]]
                win = ' <span class="cand-win" aria-label="Winner">✔</span>' if cand.get("winner") else ""
                items.append(
                    f'<li><a href="c/{esc(slug)}.html?from={county_slug(county)}&amp;e=general">{esc(cand["name_on_ballot"] if cand["person_id"] != "WY-PEARSON-LAURA" else "Laura Taliaferro (formerly Pearson)")}</a> '
                    f'<span class="cand-abbr">{esc(party_abbr(cand.get("party") or ""))}</span>{win}</li>'
                )
            race_html.append(
                '<section class="cand-race">\n'
                f"            <h3>{esc(box_title(race['office_sought'], race.get('district')))}</h3>\n"
                '            <ul class="cand-names">\n              '
                + "\n              ".join(items)
                + "\n            </ul>\n          </section>"
            )
        blocks_by_title.append(
            '<section class="cand-group">\n'
            f'          <h2 class="cand-group-title">{title}</h2>\n'
            '          <div class="cand-race-grid">\n            '
            + "\n            ".join(race_html)
            + "\n          </div>\n        </section>"
        )
    return "\n          ".join(blocks_by_title)


def install_level1(text: str, intro: str, label: str) -> str:
    if "<!-- election-views -->" in text:
        return text
    match = re.search(
        r"(<p>.*?</p>\s*)(<p>Past elections:.*?</p>\s*)?(<ul class=\"cand-counties\">.*?</ul>)",
        text,
        re.S,
    )
    if not match:
        raise SystemExit("county grid missing")
    past = match.group(2) or ""
    block = (
        "<!-- election-views -->\n          "
        '<div class="cand-view cand-view-primary">\n          '
        + match.group(1)
        + past
        + match.group(3)
        + '\n          </div>\n          <div class="cand-view cand-view-general">\n          '
        + label
        + "\n          "
        + f"<p>{esc(intro)}</p>\n          "
        + with_general_query(past)
        + with_general_query(match.group(3))
        + "\n          </div>"
    )
    return text[: match.start()] + block + text[match.end() :]


COUNTY_BODY = re.compile(
    r"(<p>[^<]*</p>\s*)"
    r'(<p class="cand-how">.*?</p>\s*)'
    r'((?:<!--.*?-->\s*)?(?:<div class="punch-list" hidden>.*?</div>\s*)?)'
    r'(<section class="cand-group">.*</section>)'
    r"(\s*</div>\s*</section>)",
    re.S,
)


def install_county(text: str, when: str, label: str, groups: str) -> str:
    general = (
        "<!-- general-view -->\n"
        '          <div class="cand-view cand-view-general">\n'
        f"          {label}\n"
        f"          <p>{esc(when)} general.</p>\n"
        f'          <p class="cand-how">{HOW_GENERAL}</p>\n          '
        + groups
        + "\n          </div>\n          <!-- /general-view -->"
    )
    if "<!-- general-view -->" in text:
        return re.sub(
            r"<!-- general-view -->.*?<!-- /general-view -->",
            general,
            text,
            count=1,
            flags=re.S,
        )
    match = COUNTY_BODY.search(text)
    if not match:
        raise SystemExit("county body missing")
    primary = (
        '<div class="cand-view cand-view-primary">\n          '
        + match.group(1)
        + match.group(2)
        + match.group(3)
        + match.group(4)
        + "\n          </div>\n          "
        + general
    )
    return text[: match.start()] + primary + match.group(5) + text[match.end() :]


def apply_general(cycle: str) -> dict[str, int]:
    path = DATA_DIR / cycle / "general.json"
    if not path.is_file():
        raise SystemExit(f"missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    when = long_date(data["election_date"])
    label = certification_label((data.get("certification") or {}).get("status") or "")
    detail_dir = PREVIEW / "candidates" / cycle / "c"
    slugs = load_name_slugs(detail_dir)
    shards = shard_name_index(cycle)
    officials = officials_index()
    used = {slug: "existing" for slug in slugs.values()}
    slug_of = {}
    created = 0
    updated = 0
    seen = set()
    for race in data["races"]:
        for cand in race["candidates"]:
            person_id = cand["person_id"]
            if person_id in seen:
                continue
            seen.add(person_id)
            slug = resolve_slug(person_id, cand["name_on_ballot"], shards, slugs, used)
            slug_of[person_id] = slug
            used[slug] = person_id
            slugs.setdefault(norm_name(cand["name_on_ballot"]), slug)
            page = detail_dir / f"{slug}.html"
            sentence = general_sentence(cand, race["office_sought"], race.get("district"))
            if page.is_file():
                text = patch_back_script(page.read_text(encoding="utf-8"))
                text = insert_general_line(text, sentence)
                page.write_text(text, encoding="utf-8")
                updated += 1
            else:
                write_missing_detail(cycle, slug, cand, race["office_sought"], race.get("district"), when, shards, officials)
                created += 1
    by_county = {county: [] for county in COUNTY_ORDER}
    for race in data["races"]:
        for county in race.get("district_counties") or []:
            if county in by_county:
                by_county[county].append(race)
    for county in COUNTY_ORDER:
        county_path = PREVIEW / "candidates" / cycle / f"{county_slug(county)}.html"
        if not county_path.is_file():
            raise SystemExit(f"missing county page {county_path}")
        text = county_path.read_text(encoding="utf-8")
        text = ensure_election_script(text)
        text = add_general_back(text)
        text = insert_buttons(text, f"{county_slug(county)}.html")
        groups = render_general_groups(by_county[county], county, slug_of)
        text = install_county(text, when, label, groups)
        county_path.write_text(text, encoding="utf-8")
    if cycle == "2026-primary":
        level1 = PREVIEW / "candidates.html"
        filename = "candidates.html"
    else:
        level1 = PREVIEW / "candidates" / cycle / "index.html"
        filename = "index.html"
    text = level1.read_text(encoding="utf-8")
    text = ensure_election_script(text)
    text = switch_h1(text)
    text = add_general_back(text)
    text = insert_buttons(text, filename)
    text = install_level1(text, f"{when}. Federal, statewide, and legislative races. Choose a county.", label)
    level1.write_text(text, encoding="utf-8")
    if " hidden" not in label:
        raise SystemExit(f"{cycle} is not certified; the live preview should hide the unofficial label")
    return {"candidates": len(seen), "details_updated": updated, "details_created": created, "counties": len(COUNTY_ORDER)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", default=None)
    parser.add_argument("--archive", type=Path, help="research archive with people/ and cycles/")
    parser.add_argument("--general", action="store_true", help="add the general election view to preview pages")
    args = parser.parse_args()
    if args.general:
        test_certification_label()
        cycles = [args.cycle] if args.cycle else list(GENERAL_CYCLES)
        for cycle in cycles:
            print(f"{cycle}: {apply_general(cycle)}")
        return
    if not args.cycle:
        args.cycle = "2026-primary"
    if args.archive:
        records = load_archive(args.archive, args.cycle)
        # Keep the raw office and district for the county map. compile_record
        # stores the display office in "office", so reload the race key here.
        raw = {}
        for path in sorted((args.archive / "cycles" / args.cycle).glob("*.json")):
            row = json.loads(path.read_text(encoding="utf-8"))
            raw[row["person_id"]] = row
        for record in records:
            source = raw[record["person_id"]]
            record["_office"] = source.get("office_sought")
            record["_district"] = source.get("district")
            record["counties"] = source.get("district_counties") or ["Statewide"]
        write_shards(records, args.cycle)
    else:
        records = read_shards(args.cycle)
    if args.cycle == "2026-primary":
        print(f"updated {write_pages(records)} preview candidate pages")
    else:
        counts = generate_archive(records, args.cycle)
        print(f"{args.cycle}: {counts}")


if __name__ == "__main__":
    main()
