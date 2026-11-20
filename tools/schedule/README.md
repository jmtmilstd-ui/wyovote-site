# Current Schedule builder

Builds `data/schedule.json` and the five Current Schedule pages from
official sources in one run:

- `schedule/index.html`: Critical Dates, The Weekly (today and the next six
  days, grouped by day), and four buttons.
- `schedule/state-offices.html`, `schedule/boards.html`,
  `schedule/standing-committees.html`, `schedule/other-committees.html`:
  everything posted for the next 60 days, with full details, grouped by body.
  Bodies with nothing posted share one "Nothing posted:" line. A body's
  repeated meetings (same title, time, and place on consecutive days,
  weekends allowed as gaps, three or more) are folded into one entry.

The Weekly at the top of the Schedule page covers today and the next six
days and moves forward each run. Critical Dates in that window appear in
it with a boxed CRITICAL tag and a heavy dark left rule; later Critical
Dates are listed under the four buttons. House and Senate floor sessions
come from the Legislature calendar and appear under State Offices.

Daily crawl and build (one command):

    python3 -B tools/schedule/spider.py            # crawl, report, build
    python3 -B tools/schedule/spider.py --stage    # 10 PM: build for tomorrow
    python3 -B tools/schedule/spider.py --light    # morning re-check, no browser

The spider keeps per-source fingerprints in a state file outside the site,
reports added, changed and removed items, keeps a source's earlier events
when it fails or goes empty (exit 11), checks Legislature meeting pages and
the Governor page in a throwaway headless Chrome, checks each Critical Date
on its source, and flags late posting during a session (exit 10).

`--render-only` rebuilds the five pages from the saved `data/schedule.json`
without fetching.
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

## Session window and conference committees

- During a session the four category pages list today plus the next 13 days
  (14 days); outside a session they list 60 days. The Weekly is always 7 days.
- Conference committees (LSO names such as `HB0011JCC01 - ...`) are listed under
  Other Committees as "HB 11 Conference Committee: <catch title>"
  ("... Conference Committee No. 2" for JCC02).

## County schedules (pilot: Weston and Crook)

- `data/county_sources.json` lists each county's posting places (commission,
  school districts, towns, other boards), how each is read
  (`agenda_links`, `text_dates`, `diligent_calendar`, `status_only`), the regular
  meeting rule the body itself posts, and sources that are not online.
- `tools/schedule/county.py` does the reading. `spider.py` crawls these sources in
  the same run (`--no-county` skips them); a source that fails or loses its
  agendas keeps its earlier upcoming agendas and gives exit code 11.
- Output: `data/county_schedule.json` and a 7-day "The Weekly" section on
  `counties/weston.html` and `counties/crook.html` (between the
  `county-weekly` markers, before Current officeholders).
  `tools/build_county_officials.py` renders the same section from
  `data/county_schedule.json`, so a county rebuild keeps it.
- A regular meeting is shown from the body's posted rule until its agenda is
  posted; then the agenda link replaces it.
