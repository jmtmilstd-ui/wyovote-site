# County officials data

One JSON file per county, named for the page slug (`weston.json` → `counties/weston.html`, `big-horn.json` → `counties/big-horn.html`). All 23 counties have a file.

Build with:

    python3 tools/build_county_officials.py
    python3 tools/build_county_officials.py --county weston
    python3 tools/build_county_officials.py --county weston --as-of 2027-01-04

Each build writes, for every county, `counties/<slug>.html` (county report on top, then State Senate, State House and County Offices as a grid of office boxes) and `counties/<slug>-precincts.html` (precinct committee people, with a Back link to the county page). It also rewrites the Federal and Statewide box at the top of `counties.html`, between the `county-officials:federal-statewide` start and end comments. The page version is `page_version` (v2.0). Print report stays the v1.1 legislative county-report PDF. The 114 County Officeholders PDF (`reports/2026/wyovote_2026_County_{nn}_{Name}_114_v1.0.pdf`) is linked from a Print officeholders (PDF) control under Current officeholders. 113 PDFs are kept.

Required keys: `county`, `county_number`, `page_version`, `report_pdf`, `groups`.

`groups` is the list of sections, in page order. Every county uses: State Senate, State House, County Offices, Precincts. Federal and statewide officials serve every county, so they live once in `shared/federal-statewide.json` (same group shape, plus `title`, `intro`, `intro_after_switch`, `term_switch_date`) and are shown only on the Counties page; each county page links to them. An optional top-level `sources` object records the county's official general and primary results links and the date they were checked.

Each office is either:

- `layout: "office-and-name"` — one office, one holder
- `layout: "heading-then-names"` — office title once, then the names (multi-member offices such as County Commissioners)

Both render as one box: the office title, then each holder. A January change is on the same line as the holder ("Name (R); in January: Name (R)").

A holder may include `succeeding` when the person in office today will be replaced when the new term begins. List the current holder; do not invent names. If a name cannot be verified, use `Not yet confirmed` (or `Vacant / not found` for a known vacancy). A holder may also carry `notes` (not shown on the page) and `ballot_name` when the ballot spelling differs. Appointees may set `role` (for example `interim`).

## Term switch date

`term_switch_date` is an ISO date (`YYYY-MM-DD`). For Weston it is `2027-01-04`, the day the new terms begin.

The generator compares that date to the America/Denver calendar:

- A rebuild *before* the date shows today's holder, with "; in January: Name" beside each holder that has a `succeeding` entry.
- A rebuild *on or after* the date promotes the elect to the holder and drops the "In January" line.

An individual `succeeding` entry may set `switch_date` to override the county date for that office only.

`--as-of YYYY-MM-DD` builds as of a given Denver date instead of today, so the January switch can be checked without waiting. After the switch, the page uses `intro_after_switch` when present (otherwise "Names are the people in office today.").

`precincts` (optional, under the Precincts group) lists precinct committee officers the same way.

Standing page text should stay timeless (no current-year numbers). The switch date belongs in the data file and this schema, not on the page. Ranks and labels only; never coefficients.

## Additional office types (municipal, schools, special districts, judicial)

Added for the 114 County Officeholders report (Weston first; structure ready for all 23 counties).

Optional groups may appear in a county file after Precincts, in this order:

| Group `id` | Title | What it holds |
|---|---|---|
| `municipal` | Municipal offices | Elected city and town offices (mayor, council). Use `jurisdiction` in the election CSVs (city or town name). |
| `schools` | School boards | Elected school-district boards. |
| `special-districts` | Special districts | Elected special-district boards, when an official results source lists them. If none appear, the group may be present with `offices: []` and a `note`. Ballot questions (mill levies, taxes) are not officeholders. |
| `judicial` | Judicial retention (district and circuit) | Judges who appeared on that county's ballot and sit on a district or circuit court. |

Statewide judicial officers (Wyoming Supreme Court, Chancery Court) serve every county and live once in `shared/judicial-statewide.json`, in the same group shape as `shared/federal-statewide.json`. A county report includes that shared file plus the county `judicial` group. Retention figures may be stored on a holder as `retention` (`year`, `yes`, `no`, `yes_pct`, `no_pct`, `result`, `source`, optional `county`).

New optional holder fields, used when known: `person_id` (WY-LAST-FIRST), `sort_key` (alphanumeric 0-9A-Z), `term_end`, `retention`. Party is omitted or set to empty for nonpartisan contests (municipal, school, judicial); do not invent a party.

Election results for these offices are not added to Phase 1 `county_offices_YYYY.csv`. They live in:

| File | Role |
|---|---|
| `tools/local-data/YYYY/municipal_YYYY.csv` | City and town candidates, same core columns as Phase 2, plus `person_id` |
| `tools/local-data/YYYY/school_YYYY.csv` | School-board candidates |
| `tools/local-data/YYYY/judicial_retention_YYYY.csv` | Retention contests; uses `yes_votes` / `no_votes` |
| `data/people/people_additions.csv` | Person records (existing IDs reused; new IDs minted) |
| `data/people/offices_held_additions.csv` | Current and incoming offices |
| `data/people/candidacies_additions.csv` | General-election candidacies |

Weston is populated. Other counties can drop in the same groups when their official rosters are compiled; do not invent names. If a seat cannot be confirmed, use `Not yet collected`.

## Officeholder history (effective-dated records and January snapshots)

Added after Michael approved keeping every year and backfilling 12 years, 2015–2026 (Weston first).

The current county JSON (`weston.json` and the shared federal, statewide, and judicial files) remains the live, as-of roster for the website. History is stored beside it, not by copying that file every year.

### Dated records (source of truth)

Each officeholder term is one record in `data/county_officials/history/<county>/terms.json`, plus shared dated records in `data/county_officials/history/shared/`. A person who is re-elected gets a new term record. Required fields:

| Field | Meaning |
|---|---|
| `person_id` | Standard `WY-LAST-FIRST` form. Existing IDs are reused. New IDs are minted only when no match exists, including maiden or nickname variants. A colliding ID for a different person is not reused; a distinct ID is minted and the collision is noted. |
| `name` | Display name. `ballot_name` is added when the official results spelling differs. |
| `office_group` | `federal`, `statewide`, `state-senate`, `state-house`, `county`, `municipal`, `schools`, `special-districts`, `judicial`, `precincts` |
| `office` | Office title, stable across years (for example `County Clerk`, `Newcastle Mayor`). |
| `jurisdiction` | County, city, town, school district, court, or precinct as applicable. |
| `party` | `R`, `D`, or empty for nonpartisan offices. Do not invent a party. |
| `term_start`, `term_end` | ISO dates. County and municipal terms use the first Monday in January after the election, which is the usual swearing-in date. School-board members in Wyoming take office at the first regular meeting in December after the election; they are still included in the next January snapshot. U.S. Senate and House terms use January 3. `term_end` is the day the successor takes office (or an earlier resignation or death date when an official source gives one). |
| `start_year`, `end_year` | Convenience copies of the January-snapshot years this term covers (inclusive). A term that ends on or before January 8 of 2019 is in the 2018 snapshot and not in 2019. |
| `how_took_office` | `elected`, `appointed`, `retained`, or `acting` |
| `election_year` | The election that began the term, when applicable. |
| `confidence` | `high` — official election results or an official roster naming the person and the term. `medium` — official source plus a documented inference (for example, a mid-session replacement whose exact appointment date is not yet collected). `low` — a secondary source. |
| `sources` | A list of `{label, url}` objects. Every row has at least one source. |
| `notes`, `flags`, `role` | Optional. `flags` may include `results_do_not_tie` when named votes and write-ins do not match a printed total, `write_in_winner_not_named`, or `ocr`. |

Do not invent a name. If a seat cannot be confirmed, the snapshot lists `Not yet collected` for that seat.

### January snapshots

A frozen copy for January of year YYYY is written to `data/county_officials/history/<county>/<YYYY>.json`. It is generated from the dated records, not hand-edited. It lists every officeholder whose term includes January 8 of that year (America/Denver). January 8 is after the first Monday in January and after January 3 congressional terms, so a mid-term handoff on January 2–3 is not shown twice.

The snapshot uses the same group and holder shape as the live county JSON, so the 114 report builder can load it with `--year YYYY`. Shared federal, statewide, and statewide-judicial holders for that January are included in the snapshot file.

Rebuild snapshots after editing `terms.json`:

    python3 tools/local-offices/build_weston_history.py

Weston is filled for 2015–2026. Other counties can use the same layout when their official results are compiled.

Official election source PDFs are stored under `/workspace/wyoleg/local-results/<county>/<year>/` and listed in that folder's source index. They are not deleted.
