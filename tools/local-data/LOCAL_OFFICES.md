# Municipal, school, and judicial election files

These files extend the local-election collection beyond Phase 1 county offices.
They use the same core candidate columns as `county_offices_YYYY.csv` and Phase 2 municipal files,
plus `person_id`, `jurisdiction`, `office_kind`, and, for retention contests, `yes_votes` / `no_votes`.

`office_normalized` values: `Mayor`, `City Council`, `Town Council`, `School Board`,
`Supreme Court Retention`, `District Judge Retention`, `Circuit Judge Retention`, `Chancery Judge Retention`.

`office_kind` values: `mayor`, `city_council`, `town_council`, `school_board`, `judicial_retention`.

Weston County is populated for 2022, 2024, and 2026 (plus 2022 and 2024 judicial rows as historical results).
The same filenames are ready for the other 22 counties when official results are keyed. Do not invent names.

See `data/county_officials/SCHEMA.md` for the officeholder JSON groups that these files feed.

## Historical years (2012–2020)

Weston official general and primary results for 2012–2020 (needed to backfill terms that were current in January 2015–2021) are keyed into:

| File | Role |
|---|---|
| `tools/local-data/YYYY/municipal_YYYY.csv` | City and town candidates |
| `tools/local-data/YYYY/school_YYYY.csv` | School-board candidates |
| `tools/local-data/YYYY/judicial_retention_YYYY.csv` | Retention contests |
| `tools/local-data/YYYY/county_offices_YYYY.csv` | County officers (Weston rows) |
| `tools/local-data/YYYY/precinct_committee_YYYY.csv` | Precinct committee, when official primary results could be keyed |

These files follow the same columns as the 2022–2026 local files. See `data/county_officials/SCHEMA.md` (officeholder history) and `/workspace/wyoleg/local-results/weston/SOURCES.md`.
