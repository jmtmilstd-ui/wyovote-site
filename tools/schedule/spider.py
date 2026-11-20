#!/usr/bin/env python3
"""Daily schedule crawl, then build. One command for the refresh routine.

    python3 -B tools/schedule/spider.py [repo] [options]

Steps
  1. Fetch every official source the builder reads (plain HTTP; JSON, ICS,
     HTML). Each source's events get a fingerprint kept in a state file.
  2. Report what each source added, changed, or removed since the last run.
     A source that fails, or returns nothing after returning events, keeps
     its earlier (still upcoming) events and is flagged.
  3. Headless Chrome (a throwaway profile, not any signed-in browser) checks
     script-built pages: the wyoleg.gov meeting page for every Legislature
     meeting in The Weekly, the Governor's public-schedule page, and any
     Critical Date source that is script-built.
  4. Check that each Critical Date is still posted on its source.
  5. During a session, check for late posting (floor action with no bill
     action recorded for the day, or no floor schedule posted for the next
     legislative day).
  6. Crawl the county sources in data/county_sources.json (pilot: Weston
     and Crook) in the same run, with the same keep-and-flag rule.
  7. Build data/schedule.json and the five schedule pages; write
     data/county_schedule.json and The Weekly section on each pilot
     county page (counties/<slug>.html).

Options
  --for-date YYYY-MM-DD   build as of that day (default: today, MT)
  --stage                 10 PM run: build for tomorrow (same as --for-date tomorrow)
  --light                 morning re-check: skip the browser and Critical Date checks
  --no-build              crawl and report only
  --no-county             skip the county sources
  --state PATH            fingerprint state file
                          (default /workspace/github-exit/state/schedule-spider-state.json)
  --report PATH           also write the JSON report here

Exit codes: 0 ok; 10 late posting suspected (pages still built; re-run later);
            11 a source (state or county) failed or went empty (earlier events
               kept, pages built).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_schedule as B  # noqa: E402
import county as C  # noqa: E402

DEFAULT_STATE = Path("/workspace/github-exit/state/schedule-spider-state.json")
BROWSER_CAP = 40          # meeting pages checked per run
BROWSER_PARALLEL = 4
BROWSER_WAIT_MS = 5000
BILLS_API = "https://wyoleg.gov/LsoService/api/BillInformation/%d"
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def opt(name: str, default=None):
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == name and i + 1 < len(a):
            return a[i + 1]
        if x.startswith(name + "="):
            return x.split("=", 1)[1]
    return default


def flag(name: str) -> bool:
    return name in sys.argv[1:]


def ev_key(e: dict) -> str:
    return "|".join([e.get("section", ""), e.get("date", ""), e.get("title", "")])


def ev_detail(e: dict) -> str:
    return "|".join([e.get("end_date", ""), e.get("time", ""), e.get("location", ""), e.get("source_url", "")])


def fingerprint(events: list[dict]) -> str:
    rows = sorted(ev_key(e) + "#" + ev_detail(e) for e in events)
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()[:16]


def diff(prev: list[dict], cur: list[dict], today: date) -> dict:
    p = {ev_key(e): e for e in prev if (e.get("end_date") or e["date"]) >= today.isoformat()}
    c = {ev_key(e): e for e in cur}
    added = [k for k in c if k not in p]
    removed = [k for k in p if k not in c]
    changed = [k for k in c if k in p and ev_detail(c[k]) != ev_detail(p[k])]
    return {"added": added, "removed": removed, "changed": changed}


def page_text(url: str) -> tuple[str, str]:
    """Plain fetch; PDFs through pdftotext. Returns (text, how)."""
    status, body = B.fetch(url)
    if status != 200:
        raise RuntimeError("HTTP %s" % status)
    if body[:5] == b"%PDF-" or url.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(body)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60)
        return out.stdout.decode("utf-8", "replace"), "pdf"
    t = body.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    import html as H
    return re.sub(r"\s+", " ", H.unescape(t)), "fetch"


def render(urls: list[str]) -> dict:
    """Headless Chrome render of script-built pages -> {url: result}."""
    if not urls:
        return {}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(urls, f)
        lst = f.name
    try:
        outp = lst + ".out"
        subprocess.run(["node", str(HERE / "render_pages.mjs"), lst, str(BROWSER_PARALLEL), str(BROWSER_WAIT_MS), outp],
                       capture_output=True, timeout=170)
        res = json.loads(Path(outp).read_text() or "[]")
        Path(outp).unlink(missing_ok=True)
    except Exception as e:
        res = [{"url": u, "ok": False, "error": "browser: %s" % e} for u in urls]
    finally:
        Path(lst).unlink(missing_ok=True)
    return {r["url"]: r for r in res}


def date_forms(d: date) -> list[str]:
    m3 = B.MONTHS[d.month - 1]
    return [
        "%s %d" % (MONTHS_LONG[d.month - 1], d.day), "%s %d" % (m3, d.day), "%s %d" % (m3.rstrip("."), d.day),
        "%d/%d/%d" % (d.month, d.day, d.year), "%02d/%02d/%d" % (d.month, d.day, d.year), d.isoformat(),
    ]


def check_critical(items: list[dict], use_browser: bool) -> list[dict]:
    out, need_browser = [], {}
    for it in items:
        url = it.get("source_url") or ""
        rec = {"date": it["date"], "title": it["title"], "url": url, "status": "", "how": ""}
        if not url:
            rec["status"] = "no source"
            out.append(rec)
            continue
        try:
            text, how = page_text(url)
            rec["how"] = how
            if len(text) < 1500 and use_browser:
                need_browser[url] = rec
            rec["_text"] = text
        except Exception as e:
            rec["status"] = "fetch failed: %s" % e
        out.append(rec)
    if need_browser:
        for url, r in render(list(need_browser)).items():
            rec = need_browser[url]
            if r.get("ok"):
                rec["_text"], rec["how"] = r.get("text", ""), "browser"
    for rec in out:
        text = rec.pop("_text", None)
        if text is None:
            continue
        d = date.fromisoformat(rec["date"])
        words = [w for w in re.findall(r"[A-Za-z]{5,}", rec["title"]) if w.lower() not in {"legislators", "begin"}]
        has_date = any(f.lower() in text.lower() for f in date_forms(d))
        has_words = sum(1 for w in words if w.lower() in text.lower())
        if has_date:
            rec["status"] = "posted (date found)"
        elif has_words:
            rec["status"] = "page found, date not shown on it"
        else:
            rec["status"] = "NOT FOUND on source"
    return out


def check_meeting_pages(events: list[dict], today: date) -> dict:
    last = today + timedelta(days=B.WEEKLY_DAYS - 1)
    urls = []
    for e in events:
        u = e.get("source_url") or ""
        if "wyoleg.gov/Calendar/" in u and "id=" in u and e["date"] <= last.isoformat() and u not in urls:
            urls.append(u)
    urls = urls[:BROWSER_CAP]
    res = render(urls)
    good, bad = 0, []
    by_url = {}
    for e in events:
        by_url.setdefault(e.get("source_url"), e)
    for u in urls:
        r = res.get(u, {})
        d = date.fromisoformat(by_url[u]["date"])
        txt = r.get("text", "")
        if r.get("ok") and ("%d/%d" % (d.month, d.day) in txt or "%02d/%02d" % (d.month, d.day) in txt):
            good += 1
        else:
            bad.append({"url": u, "error": r.get("error", "date not on page")})
    return {"checked": len(urls), "ok": good, "problems": bad,
            "seconds": round(max([r.get("ms", 0) for r in res.values()] or [0]) / 1000, 1)}


def late_posting(ctx: dict, lso_events: list[dict], crawl_day: date) -> dict:
    """During a session: floor action on crawl_day but no bill action recorded,
    or no floor schedule posted for the next legislative day."""
    out = {"checked": False, "late": False, "reasons": []}
    if not ctx["during"]:
        return out
    out["checked"] = True
    floor_today = [e for e in lso_events if e["section"] in ("house", "senate") and e["date"] == crawl_day.isoformat()]
    if floor_today:
        try:
            bills = B.fetch_json(BILLS_API % crawl_day.year)
            n = sum(1 for b in bills if (b.get("lastActionDate") or "").startswith(crawl_day.isoformat()))
            out["bill_actions_today"] = n
            if n == 0:
                out["late"] = True
                out["reasons"].append("floor session on %s but no bill actions posted yet" % crawl_day.isoformat())
        except Exception as e:
            out["reasons"].append("bill list not read: %s" % e)
    nxt = crawl_day + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    floor_next = [e for e in lso_events if e["section"] in ("house", "senate") and e["date"] == nxt.isoformat()]
    any_next = [e for e in lso_events if e["date"] == nxt.isoformat()]
    out["next_day"] = nxt.isoformat()
    out["next_day_items"] = len(any_next)
    if floor_today and not floor_next:
        out["late"] = True
        out["reasons"].append("no floor schedule posted yet for %s" % nxt.isoformat())
    now = B.now_denver()
    if now.hour < 20 and now.date() == crawl_day:
        out["reasons"].append("crawl ran before 8 PM MT; postings may be incomplete")
    return out


def main() -> int:
    t_start = time.time()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vals = {opt(n) for n in ("--for-date", "--state", "--report")}
    args = [a for a in args if a not in vals]
    repo = Path(args[0]).resolve() if args else HERE.parents[1]
    crawl_day = B.today_denver()
    if opt("--for-date"):
        today = date.fromisoformat(opt("--for-date"))
    elif flag("--stage"):
        today = crawl_day + timedelta(days=1)
    else:
        today = crawl_day
    light = flag("--light")
    state_path = Path(opt("--state") or DEFAULT_STATE)
    state = json.loads(state_path.read_text()) if state_path.exists() else {"sources": {}}
    generated = B.now_denver()

    ctx = B.make_context(repo, today)
    results = B.collect_sources(ctx)

    report = {"started": generated.isoformat(), "schedule_date": today.isoformat(), "crawl_day": crawl_day.isoformat(),
              "mode": "light" if light else "full", "in_session": ctx["during"], "sources": {}, "flags": []}
    events = []
    for sid, r in results.items():
        prev = state["sources"].get(sid, {})
        prev_events = [e for e in prev.get("events", []) if (e.get("end_date") or e["date"]) >= today.isoformat()]
        cur = r["events"]
        status = "ok"
        if not r["ok"] or (not cur and prev_events):
            status = "FAILED, earlier events kept" if not r["ok"] else "EMPTY, earlier events kept"
            report["flags"].append("%s: %s" % (sid, status))
            for e in prev_events:
                e = dict(e)
                e["kept_from"] = prev.get("checked_at", "")
                events.append(e)
            d = {"added": [], "removed": [], "changed": []}
        else:
            d = diff(prev_events, cur, today)
            events.extend(cur)
            state["sources"][sid] = {"label": r["label"], "url": r["url"], "checked_at": generated.isoformat(),
                                     "fingerprint": fingerprint(cur), "events": cur}
        report["sources"][sid] = {
            "label": r["label"], "url": r["url"], "status": status, "error": r["error"],
            "seconds": r["seconds"], "events": len(cur),
            "fingerprint": fingerprint(cur), "previous": prev.get("fingerprint", ""),
            "added": d["added"], "changed": d["changed"], "removed": d["removed"],
        }

    if not light:
        t0 = time.time()
        report["meeting_pages"] = check_meeting_pages(results.get("lso", {}).get("events", []), today)
        gov = render([B.GOV_PAGE]).get(B.GOV_PAGE, {})
        report["governor_page"] = {"ok": gov.get("ok", False), "text_chars": len(gov.get("text", "")),
                                   "note": "calendar is an embedded Google calendar; events come from its public feed"}
        crit_items = json.loads((repo / "data" / "critical_dates.json").read_text()).get("items", [])
        crit_items = [i for i in crit_items if i.get("date", "") >= today.isoformat()]
        report["critical_dates"] = check_critical(crit_items, True)
        for c in report["critical_dates"]:
            if c["status"].startswith("NOT FOUND") or c["status"].startswith("fetch failed"):
                report["flags"].append("critical date %s: %s" % (c["date"], c["status"]))
        report["browser_seconds"] = round(time.time() - t0, 1)

    if not flag("--no-county"):
        t0 = time.time()
        county_data, cflags, crep = C.crawl(repo, today, state, generated, render)
        report["county_sources"] = crep
        report["flags"].extend(cflags)
        report["county_seconds"] = round(time.time() - t0, 1)

    report["late_posting"] = late_posting(ctx, results.get("lso", {}).get("events", []), crawl_day)
    if report["late_posting"].get("late"):
        report["flags"].append("late posting suspected: " + "; ".join(report["late_posting"]["reasons"]))

    if not flag("--no-build"):
        summary = {sid: {"status": s["status"], "events": s["events"], "fingerprint": s["fingerprint"]}
                   for sid, s in report["sources"].items()}
        B.build_and_write(ctx, events, generated, extra={"sources": summary})
        if not flag("--no-county"):
            C.write_all(repo, county_data, today)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=1) + "\n")
    report["seconds_total"] = round(time.time() - t_start, 1)

    print("\n=== Schedule crawl report (%s, schedule date %s, %s) ===" % (generated.strftime("%Y-%m-%d %H:%M MT"), today, report["mode"]))
    for sid, s in report["sources"].items():
        print("%-10s %-34s %-28s %3d events  +%d ~%d -%d  %4.1fs" % (sid, s["label"][:34], s["status"][:28], s["events"],
              len(s["added"]), len(s["changed"]), len(s["removed"]), s["seconds"]))
        for k in s["added"][:10]:
            print("   + " + k)
        for k in s["changed"][:10]:
            print("   ~ " + k)
        for k in s["removed"][:10]:
            print("   - " + k)
    if "meeting_pages" in report:
        m = report["meeting_pages"]
        print("wyoleg meeting pages (browser): %d checked, %d ok, %d problems" % (m["checked"], m["ok"], len(m["problems"])))
        print("Governor page (browser): %s, %d chars" % (report["governor_page"]["ok"], report["governor_page"]["text_chars"]))
        for c in report["critical_dates"]:
            print("critical %s %-45s %s (%s)" % (c["date"], c["title"][:45], c["status"], c["how"]))
    if "county_sources" in report:
        print("county sources (%.1fs):" % report["county_seconds"])
        for k, s in report["county_sources"].items():
            print("  %-22s %-40s %-30s posted %d, regular %d" % (k, s["label"][:40], s["status"][:30], s["posted"], s["regular"]))
            for x in s["added"][:6]:
                print("     + " + x)
            for x in s["removed"][:6]:
                print("     - " + x)
    lp = report["late_posting"]
    print("late-posting check:", "not in session" if not lp["checked"] else ("LATE: " + "; ".join(lp["reasons"]) if lp["late"] else "ok"))
    print("flags:", report["flags"] or "none")
    print("total %.1fs" % report["seconds_total"])
    rp = opt("--report")
    if rp:
        Path(rp).write_text(json.dumps(report, indent=1) + "\n")
    if report["late_posting"].get("late"):
        return 10
    if any("kept" in s["status"] or s["status"] == "FAILED"
           for s in list(report["sources"].values()) + list(report.get("county_sources", {}).values())):
        return 11
    return 0


if __name__ == "__main__":
    sys.exit(main())
