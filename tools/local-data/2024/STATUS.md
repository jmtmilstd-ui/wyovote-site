# Wyoming 2024 local results — coverage status

Generated 2026-11-13 (America/Denver). Data only; nothing published.

- county_offices_2024.csv: 187 candidate rows; races_2024.csv: 81 race rows
- precinct_committee_2024.csv: 3303 rows (primary only; precinct committee seats are not on the general ballot)
- Rows flagged CHECK: 0 PC, 0 county-office
- PC rows flagged Unreconciled (OCR dropped a totals line): 18
- Sources: sources/sources.csv (URL per document) and sources/<county>/ (PDF + extracted text).

## County offices

| County | Status | Primary | General | Races P/G | Checks ok/failed | Notes |
|---|---|---|---|---|---|---|
| Albany | complete | official | official | 2/1 | 2/0 |  |
| Big Horn | complete | official | official | 2/1 | 3/0 |  |
| Campbell | partial | official | unofficial | 2/1 | 3/0 | General: only an UNOFFICIAL election-night summary is posted on the county site. |
| Carbon | complete | official | official | 2/1 | 3/0 |  |
| Converse | complete | official | official | 2/1 | 3/0 |  |
| Crook | complete | official | official | 2/1 | 3/0 |  |
| Fremont | partial | not_found | official | 0/3 | 3/0 | General: official scanned abstract (Totals rows; names printed as surnames only). Primary: only in the ARCA records portal (needs a browser). |
| Goshen | complete | official | official | 2/1 | 3/0 |  |
| Hot Springs | complete | official | official | 4/2 | 6/0 |  |
| Johnson | partial | unofficial | official | 4/2 | 6/0 | Primary: only the UNOFFICIAL summary is posted (county Election Archives Drive folder). General: official county-offices summary. County Clerk was on the 2024 ballot (off-cycle; the report prints no term, so the 4-yr label is a default and may be an unexpired term). |
| Laramie | complete | official | official | 4/2 | 6/0 | Keyed from the official summaries; every candidate value re-checked against the PDFs retrieved via their Wayback Machine raw captures (county host returns 403). |
| Lincoln | complete | official | official | 2/1 | 1/0 |  |
| Natrona | complete | official | official | 2/1 | 3/0 |  |
| Niobrara | complete | official | official | 2/1 | 3/0 |  |
| Park | complete | official | official | 2/1 | 3/0 |  |
| Platte | complete | official | official | 2/1 | 3/0 |  |
| Sheridan | complete | official | official | 4/2 | 2/0 |  |
| Sublette | complete | official | official | 2/1 | 1/0 |  |
| Sweetwater | complete | official | official | 2/1 | 1/0 |  |
| Teton | complete | official | official | 2/1 | 3/0 |  |
| Uinta | complete | official | official | 2/1 | 3/0 |  |
| Washakie | complete | official | official | 2/1 | 3/0 |  |
| Weston | complete | official | official | 2/1 | 3/0 |  |

## Precinct committee (primary)

| County | Status | Rows | Contests | Reconciled / failed / n/a | Notes |
|---|---|---|---|---|---|
| Albany | official | 107 | 41 | 38 / 0 / 3 | OCR; 3 contests unreconciled because OCR dropped a totals line (rows flagged). |
| Big Horn | official-ocr | 79 | 51 | 40 / 0 / 12 | OCR; 12 contests unreconciled because OCR dropped a totals line (rows flagged 'Unreconciled'). |
| Campbell | official | 272 | 146 | 146 / 0 / 0 |  |
| Carbon | official | 93 | 76 | 76 / 0 / 0 |  |
| Converse | official | 126 | 76 | 76 / 0 / 0 | Keyed by hand from page images (text layer unusable); all 76 contests reconcile. |
| Crook | official | 108 | 68 | 68 / 0 / 0 |  |
| Fremont | not_found | 0 | 0 | 0 / 0 / 0 | Not found: 2024 primary is only in ARCA (needs a browser). |
| Goshen | official | 89 | 56 | 56 / 0 / 0 |  |
| Hot Springs | official | 39 | 20 | 20 / 0 / 0 | Keyed by hand from page images; all 20 contests reconcile. |
| Johnson | unofficial | 116 | 64 | 64 / 0 / 0 | UNOFFICIAL summary only (county Election Archives Drive folder). |
| Laramie | official | 353 | 160 | 160 / 0 / 0 | Official REP/DEM precinct-committee PDFs saved from Wayback raw captures (county host 403s). |
| Lincoln | official | 113 | 60 | 0 / 0 / 60 | source prints no over/under or contest totals, so n/a contests cannot be reconciled |
| Natrona | official | 412 | 184 | 184 / 0 / 0 |  |
| Niobrara | official | 43 | 24 | 24 / 0 / 0 |  |
| Park | official | 225 | 88 | 88 / 0 / 0 |  |
| Platte | official | 55 | 32 | 32 / 0 / 0 |  |
| Sheridan | official | 395 | 116 | 0 / 0 / 0 | From 29 official per-precinct primary PDFs (county summary omits PC races). |
| Sublette | official | 33 | 22 | 0 / 0 / 22 | source prints no over/under or contest totals, so n/a contests cannot be reconciled |
| Sweetwater | official | 232 | 140 | 0 / 0 / 140 | source prints no over/under or contest totals, so n/a contests cannot be reconciled |
| Teton | official | 168 | 68 | 68 / 0 / 0 |  |
| Uinta | official | 143 | 40 | 40 / 0 / 0 |  |
| Washakie | official | 51 | 20 | 20 / 0 / 0 |  |
| Weston | official | 51 | 32 | 32 / 0 / 0 |  |

## Method notes

- Names are kept as printed (including quirks such as Hot Springs 'J W', Converse 'McKENNA SMITH').
- Results: top N by votes = nominated (primary) / elected (general); 'Write-In Totals' rows carry the aggregate write-in count; named write-in lines are dropped.
- Reconciliation: named + write-ins = Total Votes Cast, or named + write-ins + over + under = Contest Totals.
- OCR via tesseract (300 dpi) for scanned PDFs; values that failed reconciliation were re-read from page images and patched (tools/manual_overrides.py, tools/build_precinct.py PATCHES, tools/manual_pc.py).
- Fremont 2024 general county offices come from the scanned official abstract (Totals rows; candidate names printed as surnames only).
