# Current Schedule builder

Builds `data/schedule.json` and `schedule/index.html` from official sources.
Critical Dates are edited by hand in `data/critical_dates.json`. Past items
are dropped each run. Other events are limited to today through the next
60 days; Critical Dates are shown even when they fall later. Times are
Mountain Time.

    python3 -B tools/schedule/build_schedule.py

Do not run this against the live site without Michael's explicit publish
approval. During a legislative session the script keeps only the standard
committee schedule in the legislative sections.

Boards the five statewide officials sit on (State Loan and Investment
Board, State Building Commission, State Canvassing Board, and similar)
are listed once under "Boards of the Five Statewide Officials," not
repeated under each office. Legislator town halls are not collected.

TODO: After Management Council adopts the 2027 General Session calendar
(meeting Nov. 23, 2026), add the verified End of Session date to
`data/critical_dates.json`. Do not list a tentative date before then.
