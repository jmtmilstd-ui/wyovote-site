# Current Schedule builder

Builds `data/schedule.json` and `schedule/index.html` from official sources.
Critical Dates are edited by hand in `data/critical_dates.json`. Past items
are dropped each run. Times are Mountain Time.

    python3 -B tools/schedule/build_schedule.py

Do not run this against the live site without Michael's explicit publish
approval. During a legislative session the script keeps only the standard
committee schedule in the legislative sections.
