#!/usr/bin/env python3
"""County schedules (pilot: Weston and Crook) for the daily schedule crawl.

Reads data/county_sources.json, collects each county's posted meetings, adds
regular-schedule meetings from rules the body itself posts, writes
data/county_schedule.json, and writes a rolling 7-day "The Weekly" section
into counties/<slug>.html between the county-weekly markers. The county
page builder (tools/build_county_officials.py) renders the same section, so
a county rebuild keeps it.
"""
from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import date, datetime, timedelta
from pathlib import Path

MARK_START = "<!-- county-weekly:start -->"
MARK_END = "<!-- county-weekly:end -->"
WEEKLY_DAYS = 7
HORIZON_DAYS = 60
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124 Safari/537.36 WyoVote-schedule")
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
MONTHS_SHORT = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WD = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
MONTH_RE = "(January|February|March|April|May|June|July|August|September|October|November|December)"


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def label_date(d: date) -> str:
    return "%s %d, %d" % (MONTHS_SHORT[d.month - 1], d.day, d.year)


def strip_tags(s: str) -> str:
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def fetch_page(fetch, url: str) -> str:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def dates_in(text: str) -> list[date]:
    """Dates written in link text or a file name."""
    out = []
    t = urllib.parse.unquote(text)
    for m in re.finditer(MONTH_RE + r"\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", t):
        out.append(date(int(m.group(3)), MONTHS_LONG.index(m.group(1)) + 1, int(m.group(2))))
    for m in re.finditer(r"(?<!\d)(\d{1,2})[-_/](\d{1,2})[-_/](\d{2,4})(?!\d)", t):
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        try:
            out.append(date(y, int(m.group(1)), int(m.group(2))))
        except ValueError:
            pass
    return out


def text_dates(text: str) -> list[tuple[date, str]]:
    """Dates in page text, including 'November 3 & 18, 2026'. Returns (date, time or '')."""
    out = []
    pat = (MONTH_RE + r"\s+(\d{1,2})(?:\s*(?:&|and)\s*(\d{1,2}))?,?\s+(\d{4})"
           r"(?:(?:(?!" + MONTH_RE[1:-1] + r")[^.]){0,30}?(\d{1,2}:\d{2}\s*[ap]\.?m\.?))?")
    for m in re.finditer(pat, text, flags=re.I):
        mon = MONTHS_LONG.index(m.group(1).capitalize()) + 1
        y = int(m.group(4))
        t = (m.group(5) or "").replace("am", "a.m.").replace("pm", "p.m.")
        for d in (m.group(2), m.group(3)):
            if d:
                try:
                    out.append((date(y, mon, int(d)), t))
                except ValueError:
                    pass
    return out


def nth_weekdays(year: int, month: int, weekday: int) -> list[date]:
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    out = []
    while d.month == month:
        out.append(d)
        d += timedelta(days=7)
    return out


def rule_dates(rule: dict, start: date, end: date) -> list[date]:
    out = []
    y, m = start.year, start.month
    while date(y, m, 1) <= end:
        days = nth_weekdays(y, m, WD[rule["weekday"]])
        nth = (rule.get("months") or {}).get(str(m), rule["nth"])
        for n in nth:
            try:
                d = days[n - 1] if n > 0 else days[n]
            except IndexError:
                continue
            for dd in ([d, d + timedelta(days=1)] if rule.get("also_next_day") else [d]):
                if start <= dd <= end:
                    out.append(dd)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return sorted(set(out))


def diligent_events(text: str, today: date) -> list[tuple[date, str]]:
    """Read meeting names from a Diligent Community month calendar (rendered text)."""
    m = re.search(MONTH_RE + r"\s+(\d{4})\s+SUN MON TUE WED THU FRI SAT(.*?)(Skip Side bar|SCHEDULE OF MEETINGS|$)", text, flags=re.S)
    if not m:
        return []
    mon, year, grid = MONTHS_LONG.index(m.group(1)) + 1, int(m.group(2)), m.group(3)
    out, last = [], 0
    for tok in re.finditer(r"(\d{1,2})(?:\s*\(Today\))?\s+((?:(?!\d{1,2}\b).)+)", grid):
        day, name = int(tok.group(1)), tok.group(2).strip()
        if day < last:
            break
        last = day
        if name:
            out.append((date(year, mon, day), name))
    return out


def collect_county(slug: str, cfg: dict, today: date, fetch, render) -> dict:
    """Return {source_id: {ok, error, events, status, ...}} for one county."""
    until = today + timedelta(days=HORIZON_DAYS)
    results = {}
    browser_urls = [s["url"] for s in cfg["sources"] if s.get("browser")]
    rendered = render(browser_urls) if browser_urls else {}
    for s in cfg["sources"]:
        res = {"body": s["body"], "url": s["url"], "method": s["method"], "ok": True, "error": "", "events": [],
               "posted": 0, "regular": 0}
        posted: list[dict] = []
        try:
            if s.get("browser"):
                r = rendered.get(s["url"], {})
                if not r.get("ok"):
                    raise RuntimeError(r.get("error") or "browser render failed")
                page_txt, links = r.get("text", ""), r.get("links", [])
                page_html = ""
            elif s["method"] != "status_only" or not s.get("not_online"):
                page_html = fetch_page(fetch, s["url"])
                page_txt = strip_tags(page_html)
                links = [(strip_tags(b), urllib.parse.urljoin(s["url"], html.unescape(a)))
                         for a, b in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page_html, flags=re.S)]
            else:
                page_html = fetch_page(fetch, s["url"])
                page_txt, links = strip_tags(page_html), []
            if s["method"] == "agenda_links":
                seen = set()
                for text, href in links:
                    ds = dates_in(text) or dates_in(href)
                    for d in ds[:1]:
                        if today <= d <= until and (d, href) not in seen:
                            seen.add((d, href))
                            note = "Agenda posted" + (" (special meeting)" if re.search("(?i)special", text + href) else "")
                            posted.append({"date": d.isoformat(), "time": "", "note": note, "url": href})
            elif s["method"] == "text_dates":
                for d, t in text_dates(page_txt):
                    if today <= d <= until:
                        posted.append({"date": d.isoformat(), "time": (t + " MT") if t else "",
                                       "note": s.get("title") or "Meeting posted", "url": s["url"]})
            elif s["method"] == "diligent_calendar":
                for d, name in diligent_events(page_txt, today):
                    if today <= d <= until:
                        posted.append({"date": d.isoformat(), "time": "", "note": name, "url": s["url"]})
            elif s["method"] == "status_only" and s.get("not_online"):
                res["status"] = "not online"
        except Exception as e:
            res["ok"] = False
            res["error"] = str(e)[:160]
            if s.get("not_online"):
                res["ok"], res["status"] = True, "not online"
        # de-duplicate posted items by date
        by_date = {}
        for p in posted:
            by_date.setdefault(p["date"], p)
        events = []
        for p in by_date.values():
            events.append({"county": slug, "source": s["id"], "body": s["body"], "date": p["date"],
                           "time": p["time"] or (s.get("regular") or {}).get("time", ""),
                           "location": s.get("location", ""), "note": p["note"], "url": p["url"], "kind": "posted"})
        rule = s.get("regular")
        if rule:
            for d in rule_dates(rule, today, until):
                if d.isoformat() in by_date:
                    continue
                events.append({"county": slug, "source": s["id"], "body": s["body"], "date": d.isoformat(),
                               "time": rule.get("time", ""), "location": s.get("location", ""),
                               "note": "Regular meeting (%s). Agenda not yet posted" % rule["rule_text"],
                               "url": rule.get("rule_url") or s["url"], "kind": "regular"})
        events.sort(key=lambda e: e["date"])
        res["events"] = events
        res["posted"] = sum(1 for e in events if e["kind"] == "posted")
        res["regular"] = sum(1 for e in events if e["kind"] == "regular")
        res.setdefault("status", "ok" if res["ok"] else "FAILED")
        res["note"] = s.get("not_online", "")
        res["posts"] = s.get("posts", "")
        results[s["id"]] = res
    return results


def time_key(t: str) -> str:
    m = re.search(r"(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)", t or "")
    if not m:
        return "99:99"
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "p.m." else 0)
    return "%02d:%s" % (h, m.group(2))


def weekly_block(slug: str, county: dict, today: date) -> str:
    """The Weekly section for a county page (between markers)."""
    last = today + timedelta(days=WEEKLY_DAYS - 1)
    evs = [e for e in county.get("events", []) if today.isoformat() <= e["date"] <= last.isoformat()]
    name = county.get("name", slug.title())
    out = [MARK_START, '          <section class="county-weekly schedule-county" id="the-weekly" aria-labelledby="the-weekly-h">',
           "            <h2 id=\"the-weekly-h\">The Weekly: %s County meetings</h2>" % esc(name),
           '            <p class="co-intro">Today and the next six days, from the county, school district, and town postings listed below. '
           "A regular meeting is shown from the body's posted schedule until its agenda is posted. Times are Mountain Time.</p>"]
    if county.get("updated"):
        out.append('            <p class="schedule-updated">Last updated: %s</p>' % esc(county["updated"]))
    if not evs:
        out.append('            <p class="sched-none">Nothing posted this week.</p>')
    else:
        out.append('            <table class="sched-table sched-weekly">')
        out.append('            <thead><tr><th scope="col">Time</th><th scope="col">Who</th><th scope="col">What</th></tr></thead>')
        days: dict = {}
        for e in evs:
            days.setdefault(e["date"], []).append(e)
        for ds in sorted(days):
            d = date.fromisoformat(ds)
            out.append('            <tbody><tr class="sched-day"><th scope="rowgroup" colspan="3">%s, %s</th></tr>' % (WEEKDAYS[d.weekday()], label_date(d)))
            for e in sorted(days[ds], key=lambda x: (time_key(x["time"]), x["body"])):
                what = esc(e["note"])
                if e.get("location"):
                    what += ". " + esc(e["location"])
                what += ' <a href="%s">%s</a>' % (esc(e["url"]), "Agenda" if e["kind"] == "posted" and e["url"] != "" else "Source")
                out.append('            <tr><td class="sched-t">%s</td><td>%s</td><td class="sched-note">%s</td></tr>'
                           % (esc((e["time"] or "").replace(" MT", "")) or "—", esc(e["body"]), what))
            out.append("            </tbody>")
        out.append("            </table>")
    src = county.get("sources", [])
    online = [s for s in src if s.get("status") != "not online"]
    offline = [s for s in src if s.get("status") == "not online"]
    if online:
        out.append('            <p class="sched-nothing"><strong>Sources:</strong> %s.</p>' % "; ".join(
            '<a href="%s">%s</a>' % (esc(s["url"]), esc(s["body"])) for s in online))
    if offline:
        out.append('            <p class="sched-nothing"><strong>Not online for automatic reading:</strong> %s.</p>' % "; ".join(
            "%s: %s" % (esc(s["body"]), esc(lower_first(s.get("note", "")).rstrip("."))) for s in offline))
    out += ["          </section>", "          " + MARK_END]
    return "\n".join(out)


def lower_first(t: str) -> str:
    return t[:1].lower() + t[1:] if t[:2] != t[:2].upper() else t


def load_schedule(repo: Path) -> dict:
    p = repo / "data" / "county_schedule.json"
    return json.loads(p.read_text()) if p.exists() else {}


def block_for(repo: Path, slug: str, today: date) -> str:
    """Used by tools/build_county_officials.py; '' when the county is not in the pilot."""
    data = load_schedule(repo)
    county = (data.get("counties") or {}).get(slug)
    if not county:
        return ""
    return weekly_block(slug, county, today)


def write_into_page(page: Path, block: str) -> bool:
    text = page.read_text(encoding="utf-8")
    if MARK_START in text:
        i = text.index(MARK_START)
        j = text.index(MARK_END) + len(MARK_END)
        new = text[:i] + block.lstrip() + text[j:]
    else:
        anchor = '<section class="county-officials" id="current-officeholders">'
        if anchor not in text:
            return False
        k = text.index(anchor)
        k = text.rfind("\n", 0, k) + 1
        new = text[:k] + block + "\n" + text[k:]
    if new != text:
        page.write_text(new, encoding="utf-8")
    return True


def updated_label(dt: datetime) -> str:
    h = dt.hour % 12 or 12
    return "%s, %d:%02d %s MT" % (label_date(dt.date()), h, dt.minute, "a.m." if dt.hour < 12 else "p.m.")


def crawl(repo: Path, today: date, state: dict, generated: datetime, render) -> tuple[dict, list[str], dict]:
    """Crawl every pilot county source in the same run as the state schedule.

    Keeps a source's earlier future agendas when it fails or comes back with
    none (same rule as the state sources). Returns (county_schedule data,
    flags, per-source report)."""
    import time as _t
    cfg = json.loads((repo / "data" / "county_sources.json").read_text())
    data = {"generated": generated.isoformat(), "schedule_date": today.isoformat(), "counties": {}}
    flags, rep = [], {}
    st = state.setdefault("sources", {})
    for slug, c in cfg["counties"].items():
        t0 = _t.time()
        res = collect_county(slug, c, today, None, render)
        secs = round(_t.time() - t0, 1)
        evs, srcs = [], []
        for sid, r in res.items():
            key = "county:" + sid
            prev = st.get(key, {})
            prev_posted = [e for e in prev.get("events", []) if e.get("kind") == "posted" and e["date"] >= today.isoformat()]
            cur = r["events"]
            status = r["status"]
            if r["status"] == "not online":
                pass
            elif not r["ok"] or (r["posted"] == 0 and prev_posted):
                status = ("FAILED, earlier agendas kept" if not r["ok"] else "EMPTY, earlier agendas kept") if prev_posted else (
                    "FAILED" if not r["ok"] else "ok")
                if prev_posted:
                    keep_dates = {e["date"] for e in prev_posted}
                    cur = prev_posted + [e for e in cur if e["kind"] == "regular" and e["date"] not in keep_dates]
                if status != "ok":
                    flags.append("county %s: %s%s" % (sid, status, (" (" + r["error"] + ")") if r["error"] else ""))
            if status in ("ok", "not online"):
                old = {e["date"] + " " + e["body"] + " " + e["kind"] for e in prev.get("events", []) if e["date"] >= today.isoformat()}
                new = {e["date"] + " " + e["body"] + " " + e["kind"] for e in cur}
                rep[key] = {"label": r["body"], "url": r["url"], "status": status, "error": r["error"], "seconds": secs,
                            "events": len(cur), "posted": r["posted"], "regular": r["regular"],
                            "added": sorted(new - old), "removed": sorted(old - new), "changed": []}
                st[key] = {"label": r["body"], "url": r["url"], "checked_at": generated.isoformat(), "events": cur}
            else:
                rep[key] = {"label": r["body"], "url": r["url"], "status": status, "error": r["error"], "seconds": secs,
                            "events": len(cur), "posted": r["posted"], "regular": r["regular"],
                            "added": [], "removed": [], "changed": []}
            evs.extend(cur)
            srcs.append({"id": sid, "body": r["body"], "url": r["url"], "status": status, "method": r["method"],
                         "posted": r["posted"], "regular": r["regular"], "note": r["note"], "posts": r["posts"]})
        evs.sort(key=lambda e: (e["date"], time_key(e["time"]), e["body"]))
        data["counties"][slug] = {"name": c["name"], "updated": updated_label(generated), "events": evs, "sources": srcs}
    return data, flags, rep


def write_all(repo: Path, data: dict, today: date) -> list[Path]:
    (repo / "data" / "county_schedule.json").write_text(json.dumps(data, indent=1) + "\n")
    out = [repo / "data" / "county_schedule.json"]
    for slug, county in data["counties"].items():
        page = repo / "counties" / (slug + ".html")
        if page.exists() and write_into_page(page, weekly_block(slug, county, today)):
            out.append(page)
    return out
