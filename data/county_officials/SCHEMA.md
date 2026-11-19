# County officials data

One JSON file per county, named for the page slug (`weston.json` → `counties/weston.html`, `big-horn.json` → `counties/big-horn.html`). All 23 counties have a file.

Build with:

    python3 tools/build_county_officials.py
    python3 tools/build_county_officials.py --county weston
    python3 tools/build_county_officials.py --county weston --as-of 2027-01-04

Each build writes, for every county, `counties/<slug>.html` (county report on top, then State Senate, State House and County Offices as a grid of office boxes) and `counties/<slug>-precincts.html` (precinct committee people, with a Back link to the county page). It also rewrites the Federal and Statewide box at the top of `counties.html`, between the `county-officials:federal-statewide` start and end comments. The page version is `page_version` (v2.0 for Weston). Print report stays the v1.1 county-report PDF. There is no v2.0 PDF.

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
