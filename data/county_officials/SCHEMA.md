# County officials data

One JSON file per county, named for the page slug (`weston.json` → `counties/weston.html`).

Build with:

    python3 tools/build_county_officials.py
    python3 tools/build_county_officials.py --county weston

The page keeps the existing county report at the top and adds the current-officeholders section below it. The page version is `page_version` (v2.0 for Weston).

Required keys: `county`, `county_number`, `page_version`, `report_pdf`, `groups`.

`groups` is the list of sections, in page order. Weston uses: Federal, Statewide, State Senate, State House, County Offices, Precincts.

Each office is either:

- `layout: "office-and-name"` — one line with the office title and the holder
- `layout: "heading-then-names"` — office title once, then just the names (for multi-member offices such as County Commissioners)

A holder may include `succeeding` when the person in office today will be replaced in January. List the current holder; do not invent names. If a name cannot be verified, use `Vacant / not found`.

`precincts` (optional, under the Precincts group) lists precinct committee officers the same way.

Standing page text should stay timeless (no current-year numbers). Ranks and labels only; never coefficients.
