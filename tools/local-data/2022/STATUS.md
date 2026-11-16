# Wyoming 2022 local results — coverage status

Generated 2026-11-13 (America/Denver). Data only; nothing published.

- county_offices_2022.csv: 907 candidate rows; races_2022.csv: 528 race rows
- precinct_committee_2022.csv: 3504 rows (primary only; precinct committee seats are not on the general ballot)
- Rows flagged CHECK: 0 PC, 0 county-office
- PC rows flagged Unreconciled (OCR dropped a totals line): 0
- Sources: sources/sources.csv (URL per document) and sources/<county>/ (PDF + extracted text).

## County offices

| County | Status | Primary | General | Races P/G | Checks ok/failed | Notes |
|---|---|---|---|---|---|---|
| Albany | complete | official | official | 16/8 | 24/0 |  |
| Big Horn | complete | official | official | 16/8 | 24/0 |  |
| Campbell | complete | official | official | 16/8 | 24/0 |  |
| Carbon | complete | official | official | 16/8 | 24/0 |  |
| Converse | complete | official | official | 16/8 | 23/0 | Primary commissioner results come from the official Commissioners Recount Report (DocumentCenter 4724). Source text layer is OCR-quality; names/values cross-checked against Total Votes Cast. |
| Crook | complete | official | official | 16/8 | 24/0 |  |
| Fremont | not_found | not_found | not_found | 0/0 | 0/0 | Not found: pre-2026 results are only in the ARCA records portal (needs a browser). |
| Goshen | complete | official | official | 16/8 | 16/0 |  |
| Hot Springs | complete | official | official | 16/8 | 24/0 |  |
| Johnson | partial | unofficial | official | 16/8 | 24/0 | Primary: only the UNOFFICIAL election-night summary is posted (county Election Archives Drive folder). General: official canvass (scanned; OCR); coroner write-in total read as 41 from the printed percentage and Total Votes Cast. |
| Laramie | complete | official | official | 16/8 | 24/0 | Keyed from the official summaries; every candidate value re-checked against the PDFs retrieved via their Wayback Machine raw captures (county host returns 403). |
| Lincoln | complete | official | official | 16/8 | 24/0 |  |
| Natrona | complete | official | official | 16/8 | 24/0 |  |
| Niobrara | complete | official | official | 16/8 | 24/0 | Official summaries found on niobraracounty.org (_pdfs/2022). |
| Park | complete | official | official | 16/8 | 24/0 |  |
| Platte | complete | official | official | 16/8 | 24/0 |  |
| Sheridan | complete | official | official | 16/8 | 0/0 |  |
| Sublette | complete | official | official | 16/8 | 8/0 | 2022 primary county totals were summed from the official per-precinct summary (scanned; OCR); the report prints no Total Votes Cast/undervote lines, so sums could not be cross-checked against a county total. |
| Sweetwater | complete | official | official | 16/8 | 8/0 |  |
| Teton | complete | official | official | 16/8 | 24/0 |  |
| Uinta | complete | official | official | 16/8 | 24/0 |  |
| Washakie | partial | unofficial | unofficial | 16/8 | 24/0 | UNOFFICIAL election-night summaries only (no official canvass posted); keyed by hand from page images. |
| Weston | complete | official | official | 16/8 | 24/0 |  |

## Precinct committee (primary)

| County | Status | Rows | Contests | Reconciled / failed / n/a | Notes |
|---|---|---|---|---|---|
| Albany | official-ocr | 154 | 44 | 44 / 0 / 0 |  |
| Big Horn | official | 80 | 52 | 52 / 0 / 0 |  |
| Campbell | official | 356 | 148 | 148 / 0 / 0 |  |
| Carbon | official | 100 | 76 | 76 / 0 / 0 |  |
| Converse | official | 134 | 74 | 74 / 0 / 0 | Text layer is OCR-quality; merged with fresh OCR; 7 contests verified by eye. |
| Crook | official | 113 | 68 | 68 / 0 / 0 |  |
| Fremont | not_found | 0 | 0 | 0 / 0 / 0 | Not found: Fremont posts pre-2026 results only through its ARCA records portal (needs a browser). |
| Goshen | official | 103 | 56 | 56 / 0 / 0 |  |
| Hot Springs | official | 38 | 20 | 20 / 0 / 0 |  |
| Johnson | unofficial | 124 | 64 | 64 / 0 / 0 | UNOFFICIAL summary only (county Election Archives Drive folder). |
| Laramie | official | 406 | 160 | 160 / 0 / 0 | Official REP/DEM precinct-committee PDFs saved from Wayback raw captures (county host 403s). The 4-01/5-03 committeemen recount matches. |
| Lincoln | official | 144 | 60 | 60 / 0 / 0 |  |
| Natrona | official | 501 | 184 | 184 / 0 / 0 |  |
| Niobrara | official | 40 | 24 | 24 / 0 / 0 |  |
| Park | official | 238 | 116 | 116 / 0 / 0 |  |
| Platte | official | 62 | 32 | 32 / 0 / 0 |  |
| Sheridan | official | 305 | 116 | 0 / 0 / 116 | source prints no over/under or contest totals, so n/a contests cannot be reconciled |
| Sublette | not_posted | 0 | 0 | 0 / 0 / 0 | Not posted: the official 2022 primary reports on the county site omit precinct committee races. |
| Sweetwater | official | 217 | 140 | 0 / 0 / 140 | source prints no over/under or contest totals, so n/a contests cannot be reconciled |
| Teton | official | 135 | 68 | 68 / 0 / 0 |  |
| Uinta | official | 142 | 40 | 40 / 0 / 0 |  |
| Washakie | unofficial | 53 | 20 | 20 / 0 / 0 | UNOFFICIAL election-night summary (no canvass posted); keyed by hand from page images; all 20 contests reconcile. |
| Weston | official | 59 | 32 | 32 / 0 / 0 |  |

## Method notes

- Names are kept as printed (including quirks such as Hot Springs 'J W', Converse 'McKENNA SMITH').
- Results: top N by votes = nominated (primary) / elected (general); 'Write-In Totals' rows carry the aggregate write-in count; named write-in lines are dropped.
- Reconciliation: named + write-ins = Total Votes Cast, or named + write-ins + over + under = Contest Totals.
- OCR via tesseract (300 dpi) for scanned PDFs; values that failed reconciliation were re-read from page images and patched (tools/manual_overrides.py, tools/build_precinct.py PATCHES, tools/manual_pc.py).
- Fremont 2024 general county offices come from the scanned official abstract (Totals rows; candidate names printed as surnames only).
