# Wyoming 2026 county-office results schema

Cycle: 2026 (August 18 primary, November 3 general).
Scope: county commissioners and county row offices only (clerk, treasurer, assessor, sheriff, county attorney / district attorney, coroner, clerk of district court). Municipal, school, college, special-district, judicial-retention, precinct-committee, and ballot-question races are out of scope for this Phase 1 file.

Official county clerk results only. The Wyoming Secretary of State does not publish local/county results. If a clerk has posted only unofficial results, `primary_status` / `general_status` is `unofficial`. Incumbent is filled only when an official source states it; it is not inferred from current officeholder lists.

Retrieved date for this collection pass: 2026-11-13 (America/Denver).

## Files

| Path | Role |
|------|------|
| `county_offices_2026.csv` | One row per named candidate (primary and/or general), plus a Write-In Totals row for each race that reports write-ins |
| `races_2026.csv` | One row per race / election / party (primary is by party; general is the combined contest) with cross-checks |
| `status/<county>.json` | Per-county collection status: `complete`, `partial`, or `not_yet_posted` |
| `STATUS.md` | Roll-up table |
| `raw/<county>/` | Unaltered official PDFs / XLSX and `.layout.txt` from `pdftotext -layout` |
| `scripts/build_dataset.py` | Electionware summary parser and builders for Weston (keyed from official scans) and Laramie (roster only) |

## Candidate columns (`county_offices_2026.csv`)

| Column | Notes |
|--------|--------|
| cycle | `2026` |
| county | Full county name, e.g. `Laramie`, `Big Horn`, `Hot Springs` |
| office | Office title as printed on the source (e.g. `CO. COMMISSIONER`, `CLERK OF COURT`, `District Attorney`) |
| office_normalized | One of: `County Commissioner`, `County Clerk`, `County Treasurer`, `County Assessor`, `County Sheriff`, `County Attorney`, `District Attorney`, `County Coroner`, `Clerk of District Court` |
| seat_or_term | `4-yr` unless an official source labels an unexpired / 2-year seat. Fremont commissioners use `4-yr, District N` (Districts 1, 3, and 4 were on the 2026 ballot). |
| vote_for | Integer N from "Vote For N" (how many are nominated in that party primary, or elected in the general) |
| party | As printed (`REP`, `DEM`, `IND`, `LIB`, …). Blank on a general Write-In Totals row |
| candidate_ballot_name | Name as printed on the ballot / results. Prefer the general printed form when both exist; the other spelling is noted |
| incumbent | `Y` only if an official roster or results file marks the person an incumbent; otherwise blank |
| primary_votes, primary_vote_pct | Official primary total (use the TOTAL column when reports also print Election Day / Absentee / Early). Percent as printed when given |
| primary_result | `nominated`, `defeated`, `withdrawn`, `write-in-only`, `not_on_ballot`, `n/a` |
| primary_status | `official`, `unofficial`, `not_posted` |
| general_votes, general_vote_pct | Same rules as primary |
| general_result | `elected`, `defeated`, `not_on_ballot`, `n/a` |
| general_status | `official`, `unofficial`, `not_posted` |
| winner | `Y` if `general_result` is `elected`, else blank |
| writein_total_primary, writein_total_general | Race-level write-in totals, repeated on each candidate row of that race; also stored on the Write-In Totals row |
| source_roster_url, source_primary_results_url, source_general_results_url | Official clerk URLs used for that row |
| retrieved_date | ISO date the source was retrieved |
| notes | Withdrawals, name-spelling variants, write-in-nominee caveats, stale URL slugs, etc. |
| votes_named_plus_writeins_primary / _general | Sum of named candidates plus Write-In Totals |
| pdf_total_votes_cast_primary / _general | "Total Votes Cast" from the PDF when printed; otherwise Contest Totals − Overvotes − Undervotes when those three are present |
| check_ok_primary / _general | `Y` if named+write-ins equals the PDF total (or reconstructed total); `N` if it does not; blank if no total is available to check |

## Race columns (`races_2026.csv`)

cycle, county, office, office_normalized, seat_or_term, vote_for, election (`primary` or `general`), party, status, writein_total, named_votes_sum, votes_named_plus_writeins, pdf_total_votes_cast, overvotes, undervotes, contest_totals, check_ok, check_notes, source_url, retrieved_date, notes

## Cross-check rule

Per race, the sum of named-candidate votes plus Write-In Totals must equal the PDF "Total Votes Cast" when that line is present. When it is omitted, the same sum plus Overvotes plus Undervotes must equal Contest Totals, and `pdf_total_votes_cast` is stored as Contest Totals − Overvotes − Undervotes. "Not Assigned" write-in breakdowns are not added a second time. Multi-column Teton/Uinta/Campbell reports use the TOTAL column only. For Vote-For-N races, Contest Totals are typically N × ballots; overvotes are vote-units, not ballots.

Winner / nominated: the top N *named* candidates are marked nominated (primary, within that party contest) or elected (general). An aggregate Write-In Totals line is not treated as a winning person unless the clerk lists a certified named write-in. If aggregate write-ins exceed the last named winner, that fact is noted and is not used to flip the result.

Write-in-only party primaries generally produce no named general nominee unless a clerk roster or certified write-in list shows someone accepted. Those general candidates, if they later appear, are flagged in notes rather than given invented primary vote totals.

## Office-title aliases seen on 2026 clerk reports

`CO COMMISSIONER` / `CO. COMMISSIONER` / `CNTY COMMISSIONER` (Crook) / `COUNTY COMMISSIONERS` / `REP COMMISSIONER REP` (Carbon primary style); `CO CLERK` / `CO. CLERK` / `CNTY CLERK` / `REP CLERK REP`; `CO CLERK OF DISTR. COURT` / `CLERK OF COURT` / `CLERK OF DIST. COURT` / `CLERK OF THE DISTRICT COURT` / `DIST COURT CLERK` (Crook); `CO ATTORNEY` / `COUNTY AND PROSECUTING ATTORNEY`; Laramie uses `District Attorney` (normalized separately from County Attorney).

## What is not in this schema

SOS statewide/legislative files, inferred incumbency, news or Ballot Brief totals, and any contact with clerks. No repo or site changes.
