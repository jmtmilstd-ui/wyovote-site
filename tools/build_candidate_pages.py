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
DATA_DIR = PREVIEW / "data" / "candidate-research"
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
          link.setAttribute("href", "../" + slug + ".html");
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
        "sources": sources,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", default="2026-primary")
    parser.add_argument("--archive", type=Path, help="research archive with people/ and cycles/")
    args = parser.parse_args()
    if args.archive:
        records = load_archive(args.archive, args.cycle)
        write_shards(records, args.cycle)
    else:
        records = read_shards(args.cycle)
    updated = write_pages(records)
    print(f"updated {updated} preview candidate pages")


if __name__ == "__main__":
    main()
