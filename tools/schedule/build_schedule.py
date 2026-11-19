#!/usr/bin/env python3
"""Build data/schedule.json and schedule/index.html from official sources.

Events from today through the next 60 days (America/Denver). Past items are
dropped each run. Critical Dates come first from data/critical_dates.json
and are shown even when they fall more than 60 days out.

  python3 -B tools/schedule/build_schedule.py [repo]

During a legislative session, legislative sections keep the standard
committee (and floor) schedule only; statewide office events are still
included.

TODO: Once Management Council adopts the 2027 General Session calendar
(meeting Nov. 23, 2026), add the verified End of Session date to
data/critical_dates.json (date, time, location, source URL). Do not list
a tentative end date before then. The daily schedule rebuild will pick
it up automatically and show it under Critical Dates.
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore

DENVER = ZoneInfo("America/Denver")
UTC = timezone.utc
TZ_NAME = "America/Denver"
UA = "WyoVote schedule builder (+https://wyovote.com/)"
TIMEOUT = 30
RETRIES = 3

LSO = "https://lsoservice.wyoleg.gov"
LSO_WEB = "https://web.wyoleg.gov/LsoService"
WYOLEG = "https://www.wyoleg.gov"

MONTHS = [
    "Jan.", "Feb.", "March", "April", "May", "June",
    "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec.",
]

# Formal Wyoming legislative committees: joint standing, management, select.
FORMAL_TYPES = {"J", "M", "SE", "SU"}

# Joint standing committee display names, in chamber order.
JOINT_NAMES = {
    "J01": "Judiciary",
    "J02": "Appropriations",
    "J03": "Revenue",
    "J04": "Education",
    "J05": "Agriculture, State and Public Lands and Water Resources",
    "J06": "Travel, Recreation, Wildlife and Cultural Resources",
    "J07": "Corporations, Elections and Political Subdivisions",
    "J08": "Transportation, Highways and Military Affairs",
    "J09": "Minerals, Business and Economic Development",
    "J10": "Labor, Health and Social Services",
    "J11": "Journal",
    "J12": "Rules and Procedure",
}

HORIZON_DAYS = 60

# The five statewide elected offices (not including House/Senate).
FIVE_OFFICES = [
    ("governor", "Governor"),
    ("secretary-of-state", "Secretary of State"),
    ("auditor", "State Auditor"),
    ("treasurer", "State Treasurer"),
    ("superintendent", "Superintendent of Public Instruction"),
]
CHAMBERS = [
    ("house", "House"),
    ("senate", "Senate"),
]
# Combined list kept for any office-or-chamber lookups.
OFFICE_SECTIONS = FIVE_OFFICES + CHAMBERS

# Boards the five statewide officials sit on are listed once, in this section,
# not repeated under each office.
BOARDS_ID = "boards"
BOARDS_HEADING = "Boards of the Five Statewide Officials"

# Kind-4 LSO calendar titles that are not statewide public meetings we keep
# in office or committee sections (holidays, out-of-state councils).
SKIP_KIND4 = {
    "state holiday",
    "energy council",
}

# Session opening items are kept on Critical Dates only, not repeated below.
CRITICAL_KIND4 = {
    "general session convenes",
    "joint session",
    "budget session convenes",
}

GOV_ICS_ID = "wyo.gov_32333737343632343835@resource.calendar.google.com"
GOV_ICS = (
    "https://calendar.google.com/calendar/ical/"
    + urllib.parse.quote(GOV_ICS_ID, safe="")
    + "/public/basic.ics"
)
GOV_PAGE = "https://governor.wyo.gov/governors-public-schedule"
SBC_PAGE = "https://stateconstruction.wyo.gov/construction-management/state-building-commission"
SLIB_PAGE = "https://lands.wyo.gov/boards/state-loan-and-investment-board"
SBE_PAGE = "https://wyboardofeducation.org/106375_2"
TREAS_HOME = "https://statetreasurer.wyo.gov/"
TREAS_IFC = (
    "https://statetreasurer.wyo.gov/"
    "investment-funds-committee-selection-panel-special-meeting/"
)


def repo_root() -> Path:
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        return Path(sys.argv[1]).resolve()
    return Path(__file__).resolve().parents[2]


def today_denver() -> date:
    return datetime.now(DENVER).date()


def now_denver() -> datetime:
    return datetime.now(DENVER)


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def label_date(d: date) -> str:
    return "%s %d, %d" % (MONTHS[d.month - 1], d.day, d.year)


def label_range(start: date, end: date | None) -> str:
    if not end or end <= start:
        return label_date(start)
    if start.year == end.year and start.month == end.month:
        return "%s %d–%d, %d" % (MONTHS[start.month - 1], start.day, end.day, start.year)
    if start.year == end.year:
        return "%s %d–%s %d, %d" % (
            MONTHS[start.month - 1], start.day, MONTHS[end.month - 1], end.day, start.year,
        )
    return "%s–%s" % (label_date(start), label_date(end))


def format_time_mt(dt: datetime | None) -> str:
    if dt is None:
        return ""
    h = dt.strftime("%I").lstrip("0") or "12"
    m = dt.strftime("%M")
    ampm = "a.m." if dt.hour < 12 else "p.m."
    if dt.hour == 12 and m == "00":
        return "12:00 noon MT"
    return "%s:%s %s MT" % (h, m, ampm)


def parse_http_dt(value: str) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=DENVER)
    return dt.astimezone(DENVER)


def fetch(url: str, timeout: int = TIMEOUT, retries: int = RETRIES) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                last_err = e
                continue
            body = b""
            try:
                body = e.read()
            except Exception:
                pass
            return e.code, body
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError("fetch failed %s: %s" % (url, last_err))


def fetch_text(url: str) -> str:
    code, body = fetch(url)
    if code != 200:
        raise RuntimeError("HTTP %s for %s" % (code, url))
    return body.decode("utf-8", errors="replace")


def fetch_json(url: str):
    text = fetch_text(url)
    return json.loads(text)


def event_record(
    *,
    date_s: str,
    time_s: str,
    office: str,
    section: str,
    title: str,
    location: str,
    source_url: str,
    end_date: str = "",
    source_name: str = "",
    tentative: bool = False,
    unverified: bool = False,
) -> dict:
    rec = {
        "date": date_s,
        "end_date": end_date or date_s,
        "time": time_s or "",
        "office": office,
        "section": section,
        "title": title,
        "location": location or "",
        "source_url": source_url,
        "source_name": source_name,
        "tentative": bool(tentative),
        "unverified": bool(unverified),
    }
    return rec


def parse_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


# ---------- LSO calendar ----------

def committee_year_for(today: date) -> int:
    # Standing/interim committees are posted under the even year of the
    # biennium until the next year's list is published.
    for year in (today.year, today.year - 1, today.year + 1):
        try:
            data = fetch_json("%s/api/committees/%s" % (LSO_WEB, year))
        except Exception:
            continue
        if isinstance(data, list) and data:
            return year
    return today.year if today.year % 2 == 0 else today.year - 1


def load_committees(year: int) -> list[dict]:
    try:
        data = fetch_json("%s/api/committees/%s" % (LSO_WEB, year))
    except Exception as e:
        print("warn: committees %s: %s" % (year, e), file=sys.stderr)
        return []
    return data if isinstance(data, list) else []


def formal_committee_id(owner: str) -> str:
    return (owner or "").strip()


def is_formal_type(type_code: str) -> bool:
    return (type_code or "").strip().upper() in FORMAL_TYPES


def display_name_for(owner: str, short: str, comm_name: str, full: str = "") -> str:
    owner = formal_committee_id(owner)
    if owner in JOINT_NAMES:
        return JOINT_NAMES[owner]
    if full and len(full) > 3 and full.lower() not in ("joint", "house", "senate"):
        return full
    if comm_name and not re.match(r"^\d", comm_name):
        return comm_name
    return short or comm_name or owner or "Committee"


def fetch_lso_months(today: date, months: int = 8) -> list[dict]:
    by_id: dict = {}
    start = date(today.year, today.month, 1)
    for i in range(months):
        month = (start.month - 1 + i) % 12 + 1
        year = start.year + (start.month - 1 + i) // 12
        day = today if (year == today.year and month == today.month) else date(year, month, 1)
        key = day.strftime("%Y%m%d")
        url = "%s/api/Calendar/Events/%s" % (LSO, key)
        try:
            data = fetch_json(url)
        except Exception as e:
            print("warn: LSO Events %s: %s" % (key, e), file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        for ev in data:
            by_id[ev.get("id")] = ev
        if i > 0 and not data:
            # later empty months are normal after the posted horizon
            continue
    return list(by_id.values())



def lso_location(ev: dict) -> str:
    parts = [ev.get("address1") or "", ev.get("address2") or "", ev.get("address3") or ""]
    city = ev.get("city") or ""
    state = ev.get("state") or ""
    loc = ", ".join(p.strip() for p in parts if p and p.strip())
    tail = ", ".join(p for p in (city, state) if p)
    if loc and tail and tail.lower() not in loc.lower():
        loc = "%s, %s" % (loc, tail)
    elif not loc:
        loc = tail
    loc = re.sub(r"\s+", " ", loc).strip(" ,")
    loc = re.sub(r"(?i)\bOnline(?:,\s*Online)+", "Online", loc)
    loc = re.sub(r"(?i),\s*Online,\s*Wyoming$", "", loc)
    if re.fullmatch(r"(?i)online(?:,\s*wyoming)?", loc or ""):
        return "Online"
    return loc

def lso_start_end(ev: dict) -> tuple[datetime | None, datetime | None, bool]:
    start = parse_http_dt(ev.get("startDate") or "")
    end = parse_http_dt(ev.get("endTime") or ev.get("endDate") or "")
    raw = ev.get("startDate") or ""
    utc = raw.endswith("Z") or "+" in raw[10:]
    return start, end, utc


def lso_time_label(ev: dict, start: datetime | None, utc: bool) -> str:
    if start and utc:
        return format_time_mt(start)
    raw = (ev.get("startTime") or "").strip()
    if raw:
        return normalize_time_string(raw)
    if start:
        if start.hour == 0 and start.minute == 0 and not ev.get("startTime"):
            return ""
        return format_time_mt(start)
    return ""


def normalize_time_string(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    m = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*([AaPp])(?:\.?m\.?|\s*m\b)?",
        text,
    )
    if m:
        h = int(m.group(1))
        mins = int(m.group(2) or "0")
        ampm = m.group(3).lower()
        hour = h % 12
        if ampm == "p":
            hour += 12
        if h == 12 and ampm == "a":
            hour = 0
        if h == 12 and ampm == "p":
            hour = 12
        dt = datetime(2000, 1, 1, hour, mins, tzinfo=DENVER)
        return format_time_mt(dt)
    if re.search(r"\bMT\b|\bMST\b|\bMDT\b", text, re.I):
        return re.sub(r"\b(MST|MDT|Mountain Time)\b", "MT", text, flags=re.I)
    return "%s MT" % text

def lso_source_url(ev: dict, start: datetime | None) -> str:
    ev_id = ev.get("id")
    if start and ev_id and ev_id > 0:
        return "%s/Calendar/%s/Meeting?id=%s&type=committee" % (
            WYOLEG, start.strftime("%Y%m%d"), ev_id,
        )
    if start:
        return "%s/Calendar/%s/Meeting" % (WYOLEG, start.strftime("%Y%m%d"))
    return "%s/Calendar/" % WYOLEG


def owner_from_event(ev: dict, committees: list[dict]) -> str:
    comm = ev.get("committee") or {}
    code = (comm.get("code") or "").strip()
    cid = ev.get("committeeId") or comm.get("id")
    if code:
        # Standing joint codes in events are often "01" not "J01".
        if re.fullmatch(r"\d{2}", code):
            return "J" + code
        return code
    if cid:
        for c in committees:
            if c.get("commID") == cid or c.get("id") == cid:
                return formal_committee_id(c.get("ownerID") or "")
    return ""


# ---------- Governor ICS ----------

def unfold_ics(text: str) -> list[str]:
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith(" ") or line.startswith("\t"):
            if lines:
                lines[-1] += line[1:]
            continue
        lines.append(line)
    return lines


def parse_ics_events(text: str) -> list[dict]:
    events: list[dict] = []
    cur: dict | None = None
    for line in unfold_ics(text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur:
                events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            key, val = line.split(":", 1)
            cur[key] = val.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")
    return events


def ics_field(ev: dict, name: str) -> tuple[str, str]:
    for k, v in ev.items():
        if k.split(";")[0] == name:
            return k, v
    return "", ""


def ics_datetime(ev: dict, name: str) -> tuple[date | None, datetime | None, bool]:
    key, val = ics_field(ev, name)
    if not val:
        return None, None, False
    if "VALUE=DATE" in key or (len(val) == 8 and "T" not in val):
        d = datetime.strptime(val[:8], "%Y%m%d").date()
        return d, None, True
    if val.endswith("Z"):
        dt = datetime.strptime(val, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC).astimezone(DENVER)
        return dt.date(), dt, False
    tzid = "America/Denver"
    m = re.search(r"TZID=([^;]+)", key)
    if m:
        tzid = m.group(1)
    try:
        tz = ZoneInfo(tzid)
    except Exception:
        tz = DENVER
    dt = datetime.strptime(val[:15], "%Y%m%dT%H%M%S").replace(tzinfo=tz)
    if tz != DENVER:
        dt = dt.astimezone(DENVER)
    return dt.date(), dt, False


def fetch_governor_events(today: date) -> list[dict]:
    try:
        text = fetch_text(GOV_ICS)
    except Exception as e:
        print("warn: governor ICS: %s" % e, file=sys.stderr)
        return []
    out: list[dict] = []
    for ev in parse_ics_events(text):
        d, dt, all_day = ics_datetime(ev, "DTSTART")
        if not d or d < today:
            continue
        title = (ics_field(ev, "SUMMARY")[1] or "").strip()
        if not title or title.lower() == "office":
            continue
        loc = (ics_field(ev, "LOCATION")[1] or "").strip()
        end_d, _, _ = ics_datetime(ev, "DTEND")
        # ICS DATE end is exclusive
        end_s = ""
        if end_d and all_day:
            last = end_d - timedelta(days=1)
            if last > d:
                end_s = last.isoformat()
        elif end_d and end_d > d:
            end_s = end_d.isoformat()
        out.append(
            event_record(
                date_s=d.isoformat(),
                end_date=end_s,
                time_s="" if all_day else format_time_mt(dt),
                office="Governor",
                section="governor",
                title=title,
                location=loc,
                source_url=GOV_PAGE,
                source_name="Governor's Public Schedule",
            )
        )
    return out


# ---------- HTML board pages ----------

def soup_text(url: str) -> tuple[object, str]:
    if BeautifulSoup is None:
        raise RuntimeError("beautifulsoup4 is required")
    page = fetch_text(url)
    soup = BeautifulSoup(page, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup, soup.get_text("\n", strip=True)


MONTH_RE = (
    r"(January|Janurary|February|March|April|May|June|"
    r"July|August|September|October|November|December)"
)
MONTH_NUM = {
    "january": 1, "janurary": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8, "september": 9,
    "october": 10, "november": 11, "december": 12,
}


def parse_month_day_year(text: str, default_year: int | None = None) -> date | None:
    m = re.search(
        MONTH_RE + r"\s+(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(\d{4})",
        text,
        re.I,
    )
    if m:
        return date(int(m.group(3)), MONTH_NUM[m.group(1).lower()], int(m.group(2)))
    if default_year:
        m = re.search(MONTH_RE + r"\s+(\d{1,2})(?:st|nd|rd|th)?\b", text, re.I)
        if m:
            return date(default_year, MONTH_NUM[m.group(1).lower()], int(m.group(2)))
    return None


def fetch_sbc_events(today: date) -> list[dict]:
    try:
        _, text = soup_text(SBC_PAGE)
    except Exception as e:
        print("warn: SBC page: %s" % e, file=sys.stderr)
        return []
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
    out: list[dict] = []
    in_2027 = False
    for i, ln in enumerate(lines):
        if re.search(r"2027 Meeting Schedule", ln, re.I):
            in_2027 = True
            continue
        if in_2027 and re.search(r"2026 Meeting Schedule|2025 Meeting Schedule", ln, re.I):
            in_2027 = False
            continue
        if in_2027:
            d = parse_month_day_year(ln, 2027)
            if not d or d < today:
                continue
            out.append(
                event_record(
                    date_s=d.isoformat(),
                    time_s="",
                    office="State Building Commission",
                    section=BOARDS_ID,
                    title="State Building Commission meeting (tentative)",
                    location="Cheyenne (location to be posted)",
                    source_url=SBC_PAGE,
                    source_name="State Building Commission",
                    tentative=True,
                )
            )
    return out


def fetch_slib_events(today: date) -> list[dict]:
    try:
        _, text = soup_text(SLIB_PAGE)
    except Exception as e:
        print("warn: SLIB page: %s" % e, file=sys.stderr)
        return []
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
    out: list[dict] = []
    i = 0
    while i < len(lines):
        d = parse_month_day_year(lines[i])
        if d and d >= today:
            window = " ".join(lines[i:i + 6])
            if re.search(r"State Loan|& Investment Board|Land Commissioners", window, re.I):
                tm = ""
                m = re.search(r"(\d{1,2}:\d{2}\s*[ap]\.?m\.?)", window, re.I)
                if m:
                    tm = normalize_time_string(m.group(1))
                title = "State Loan and Investment Board / State Board of Land Commissioners"
                if re.search(r"Special", window, re.I):
                    title = "Special meeting, " + title
                loc = "Capitol Extension Auditorium, Cheyenne"
                mloc = re.search(r"Capitol[^\n|]{0,60}", window)
                if mloc:
                    loc = mloc.group(0).strip(" |")
                out.append(
                    event_record(
                        date_s=d.isoformat(),
                        time_s=tm,
                        office="State Loan and Investment Board",
                        section=BOARDS_ID,
                        title=title,
                        location=loc,
                        source_url=SLIB_PAGE,
                        source_name="Office of State Lands and Investments",
                    )
                )
        i += 1
    return out



def fetch_sbe_events(today: date) -> list[dict]:
    try:
        _, text = soup_text(SBE_PAGE)
    except Exception as e:
        print("warn: SBE page: %s" % e, file=sys.stderr)
        return []
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]
    blob = "\n".join(lines)
    featured_date = None
    featured_time = ""
    featured_loc = ""
    m = re.search(
        r"will meet in-person on " + MONTH_RE + r"\s+(\d{1,2}),\s+(\d{4})\s+at\s+(\d{1,2}:\d{2}\s*[ap](?:\.?m\.?)?)",
        blob,
        re.I,
    )
    if m:
        featured_date = date(int(m.group(3)), MONTH_NUM[m.group(1).lower()], int(m.group(2)))
        featured_time = normalize_time_string(m.group(4).strip())
        idx = next((i for i, ln in enumerate(lines) if "will meet in-person" in ln.lower()), None)
        if idx is not None:
            loc_parts = []
            for ln in lines[idx + 1:idx + 8]:
                if re.search(r"^Public may join virtually", ln, re.I):
                    break
                if re.search(r"register|phone:|contact ", ln, re.I):
                    continue
                if re.search(r"University|College|Campus|Drive|Street|Casper|Cheyenne|Room", ln, re.I):
                    loc_parts.append(ln)
            featured_loc = ", ".join(loc_parts)
    out: list[dict] = []
    in_list = False
    i = 0
    while i < len(lines):
        if re.search(r"SBE Meeting Dates", lines[i], re.I):
            in_list = True
            i += 1
            continue
        if in_list and re.search(r"Recordings of past|Learn more about public", lines[i], re.I):
            break
        if in_list:
            if re.search(r"^June\s+20\d{2}$", lines[i], re.I):
                i += 1
                continue
            d = parse_month_day_year(lines[i])
            if d and d >= today:
                loc = ""
                j = i + 1
                while j < len(lines) and lines[j] in {"-", "–", "—", ""}:
                    j += 1
                if j < len(lines) and not parse_month_day_year(lines[j]) and not re.search(r"^June\s+20\d{2}$", lines[j], re.I):
                    loc_line = lines[j]
                    if re.search(r"Virtual", loc_line, re.I):
                        loc = "Virtual"
                    elif re.search(r"Casper", loc_line, re.I):
                        loc = "Casper"
                    elif re.search(r"Buffalo", loc_line, re.I):
                        loc = "Buffalo"
                    elif re.search(r"Cheyenne", loc_line, re.I):
                        loc = "Cheyenne"
                    elif not re.search(r"Recordings of past|Learn more about public", loc_line, re.I):
                        loc = loc_line
                time_s = ""
                if featured_date == d:
                    time_s = featured_time
                    loc = featured_loc or loc
                if not any(e["date"] == d.isoformat() for e in out):
                    out.append(
                        event_record(
                            date_s=d.isoformat(),
                            time_s=time_s,
                            office="Superintendent of Public Instruction",
                            section="superintendent",
                            title="State Board of Education meeting",
                            location=loc,
                            source_url=SBE_PAGE,
                            source_name="Wyoming State Board of Education",
                        )
                    )
        i += 1
    return out


def fetch_treasurer_announcements(today: date) -> list[dict]:
    """Public meetings announced on the Treasurer's site (HTML news pages)."""
    out: list[dict] = []
    try:
        soup, text = soup_text(TREAS_IFC)
    except Exception as e:
        print("warn: Treasurer IFC page: %s" % e, file=sys.stderr)
        return out
    year = today.year
    m = re.search(MONTH_RE + r"\s+(\d{1,2}),\s+(\d{4})", text)
    if m:
        year = int(m.group(3))
    m = re.search(
        r"special meeting on \w+,\s*" + MONTH_RE + r",?\s*(\d{1,2})(?:st|nd|rd|th)?\s+at\s+(\d{1,2}(?::\d{2})?\s*[ap](?:\.?m\.?)?)",
        text,
        re.I,
    )
    if not m:
        return out
    d = date(year, MONTH_NUM[m.group(1).lower()], int(m.group(2)))
    if d < today:
        return out
    time_s = normalize_time_string(m.group(3))
    loc = "Zoom (open to the public)"
    if re.search(r"via Zoom", text, re.I):
        loc = "Zoom (open to the public); call 307-777-7408 for call-in information"
    out.append(
        event_record(
            date_s=d.isoformat(),
            time_s=time_s,
            office="State Treasurer",
            section="treasurer",
            title="Investment Funds Committee Selection Panel special meeting",
            location=loc,
            source_url=TREAS_IFC,
            source_name="Wyoming State Treasurer's Office",
        )
    )
    return out


def load_critical_dates(path: Path, today: date) -> list[dict]:
    data = json.loads(path.read_text())
    items = data.get("items") or []
    out: list[dict] = []
    for it in items:
        d = parse_date(it.get("date") or "")
        if not d or d < today:
            continue
        rec = event_record(
            date_s=d.isoformat(),
            time_s=(it.get("time") or "").strip(),
            office="Critical Dates",
            section="critical-dates",
            title=it.get("title") or "",
            location=it.get("location") or "",
            source_url=it.get("source_url") or "",
            source_name="",
            unverified=bool(it.get("unverified")),
        )
        rec["sort"] = it.get("sort", 100)
        out.append(rec)
    out.sort(key=lambda e: (e["date"], e.get("sort", 100), e["time"] or "99"))
    return out

def session_window(critical_path: Path, today: date) -> tuple[date | None, date | None]:
    data = json.loads(critical_path.read_text())
    start = end = None
    for it in data.get("items") or []:
        title = (it.get("title") or "").lower()
        d = parse_date(it.get("date") or "")
        if not d:
            continue
        if title.startswith("start of") and "session" in title:
            start = d
        if title.startswith("end of") and "session" in title:
            end = d
    return start, end


def in_legislative_session(today: date, start: date | None, end: date | None) -> bool:
    if not start:
        return False
    if today < start:
        return False
    if end:
        return today <= end
    # No adopted end date yet: treat the usual winter window as in session.
    last = date(start.year, 3, 15)
    return today <= last


# ---------- Assemble and write ----------

def section_defs(committees: list[dict]) -> list[tuple[str, str, str]]:
    """Return (section_id, heading, kind) in page order."""
    out = [("critical-dates", "Critical Dates", "critical")]
    for sid, heading in FIVE_OFFICES:
        out.append((sid, heading, "office"))
    out.append((BOARDS_ID, BOARDS_HEADING, "boards"))
    for sid, heading in CHAMBERS:
        out.append((sid, heading, "office"))
    # Joint standing in number order, then management, then select A-Z.
    joint: list[tuple[str, str]] = []
    management: list[tuple[str, str]] = []
    select: list[tuple[str, str]] = []
    seen = set()
    for c in committees:
        typ = (c.get("type") or "").strip().upper()
        if not is_formal_type(typ):
            continue
        owner = formal_committee_id(c.get("ownerID") or "")
        if not owner or owner in seen:
            continue
        seen.add(owner)
        name = display_name_for(owner, c.get("shortDesc") or "", c.get("commName") or "")
        sid = "committee-%s" % owner.lower()
        if typ == "J":
            joint.append((sid, name))
        elif typ == "M":
            management.append((sid, name))
        else:
            select.append((sid, name))
    joint.sort(key=lambda x: x[0])
    # Management Council first, then Management Audit
    def mkey(item: tuple[str, str]) -> str:
        return "0" if "council" in item[1].lower() else "1" + item[1].lower()
    management.sort(key=mkey)
    select.sort(key=lambda x: x[1].lower())
    for sid, name in joint + management + select:
        out.append((sid, name, "committee"))
    return out


def assign_lso_events(
    raw: list[dict],
    committees: list[dict],
    today: date,
    during_session: bool,
) -> list[dict]:
    owner_type = {
        formal_committee_id(c.get("ownerID") or ""): (c.get("type") or "").strip().upper()
        for c in committees
    }
    # Prefer fuller names from events
    owner_full: dict[str, str] = {}
    out: list[dict] = []
    for ev in raw:
        start, end, utc = lso_start_end(ev)
        if not start:
            continue
        start_d = start.date()
        if start_d < today:
            continue
        end_d = end.date() if end else start_d
        # endTime is often 23:59 of the last day; keep that date
        if end and end.hour == 0 and end.minute == 0 and end_d > start_d:
            end_d = end_d - timedelta(days=1)
        comm = ev.get("committee") or {}
        title_name = (comm.get("fullName") or comm.get("displayName") or comm.get("shortName") or "").strip()
        kind = ev.get("meetingKind")
        # Kind 4: holidays, boards, session convening
        if kind == 4 or ev.get("committeeId") in (0, None):
            key = title_name.lower()
            if key in SKIP_KIND4 or not title_name:
                continue
            if key in CRITICAL_KIND4:
                continue
            if "state loan" in key or "investment board" in key or "land commissioners" in key:
                board_title = title_name
            elif "state building commission" in key:
                board_title = title_name
            elif "canvass" in key:
                board_title = title_name
            else:
                # Unrecognized kind-4 item: skip rather than misfile
                print("skip kind4:", title_name, file=sys.stderr)
                continue
            out.append(
                event_record(
                    date_s=start_d.isoformat(),
                    end_date=end_d.isoformat() if end_d != start_d else "",
                    time_s=lso_time_label(ev, start, utc),
                    office=BOARDS_HEADING,
                    section=BOARDS_ID,
                    title=board_title,
                    location=lso_location(ev),
                    source_url=lso_source_url(ev, start),
                    source_name="Wyoming Legislature calendar",
                    tentative=(ev.get("category") == "Tentative"),
                )
            )
            continue

        owner = owner_from_event(ev, committees)
        typ = owner_type.get(owner, "")
        if during_session:
            # Standard committee schedule only (standing, management, select).
            if not is_formal_type(typ) and typ:
                continue
        else:
            if owner and typ and not is_formal_type(typ):
                continue
        if owner and title_name:
            owner_full[owner] = title_name
        heading = display_name_for(owner, comm.get("shortName") or "", comm.get("fullName") or "", title_name)
        tentative = ev.get("category") == "Tentative"
        title = "%s meeting" % heading
        if tentative:
            title += " (tentative)"
        section = "committee-%s" % owner.lower() if owner else "committee-unknown"
        out.append(
            event_record(
                date_s=start_d.isoformat(),
                end_date=end_d.isoformat() if end_d != start_d else "",
                time_s=lso_time_label(ev, start, utc),
                office=heading,
                section=section,
                title=title,
                location=lso_location(ev),
                source_url=lso_source_url(ev, start),
                source_name="Wyoming Legislature calendar",
                tentative=tentative,
            )
        )
    return out, owner_full



def within_horizon(ev: dict, today: date, until: date) -> bool:
    """Critical Dates are kept whenever they are still upcoming.
    Other events must overlap today through today + HORIZON_DAYS."""
    start = parse_date(ev.get("date") or "")
    if not start or start < today:
        return False
    if ev.get("section") == "critical-dates":
        return True
    end = parse_date(ev.get("end_date") or "") or start
    return start <= until and end >= today


def _board_family(title: str) -> str:
    t = (title or "").lower()
    if "state loan" in t or "investment board" in t or "land commissioners" in t:
        return "slib"
    if "state building commission" in t:
        return "sbc"
    if "canvass" in t:
        return "canvass"
    return ""


def dedupe(events: list[dict]) -> list[dict]:
    # Collapse the same board meeting listed from two official pages, once
    # in the boards section.
    best: dict = {}
    leftover = []
    for ev in events:
        family = _board_family(ev.get("title") or "")
        if family and ev["section"] in {BOARDS_ID, "sbc", "slib", "canvass"}:
            key = (BOARDS_ID, ev["date"], family)
            prev = best.get(key)
            if prev is None or len(ev.get("title") or "") > len(prev.get("title") or ""):
                rec = dict(ev)
                rec["section"] = BOARDS_ID
                rec["office"] = BOARDS_HEADING
                best[key] = rec
            continue
        leftover.append(ev)
    events = leftover + list(best.values())
    seen = set()
    out = []
    for ev in events:
        key = (ev["section"], ev["date"], ev.get("end_date"), ev["time"], ev["title"], ev["location"])
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    out.sort(key=lambda e: (e["date"], e.get("end_date") or e["date"], e.get("sort", 100), e["time"] or "99", e["title"]))
    return out

def counts_by_section(events: list[dict], sections: list[tuple[str, str, str]]) -> dict:
    c = defaultdict(int)
    for ev in events:
        c[ev["section"]] += 1
    return {sid: c.get(sid, 0) for sid, _, _ in sections}


def render_page(
    repo: Path,
    generated: datetime,
    events: list[dict],
    sections: list[tuple[str, str, str]],
    during_session: bool,
) -> str:
    by = defaultdict(list)
    for ev in events:
        by[ev["section"]].append(ev)

    jump_bits = []
    for sid, heading, _kind in sections:
        if sid == "critical-dates" or by.get(sid):
            jump_bits.append(
                '<li><a href="#%s">%s</a></li>' % (esc(sid), esc(heading))
            )

    session_note = ""
    if during_session:
        session_note = (
            "<p>The Legislature is in session. The House, Senate, and committee "
            "sections show the standard committee schedule.</p>"
        )

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "  <head>",
        '    <meta charset="utf-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1">',
        "    <title>Current Schedule — WyoVote</title>",
        '    <meta name="description" content="Current statewide meetings and events for Wyoming\'s five elected offices, the House, the Senate, and formal legislative committees.">',
        '    <link rel="icon" href="../assets/img/surveyor-icon.png" type="image/png">',
        '    <link rel="stylesheet" href="../css/styles.css">',
        '    <link rel="stylesheet" href="../assets/css/site.css">',
        "  </head>",
        "  <body>",
        '    <a class="skip-link" href="#main">Skip to content</a>',
        '    <header class="site-header">',
        '      <div class="wrap header-inner">',
        '        <a class="brand" href="../index.html">',
        '          <img src="../assets/img/surveyor-icon.png" alt="" width="135" height="152">',
        '          <span class="site-name">WyoVote</span>',
        "        </a>",
        '        <nav class="site-nav" aria-label="Site">',
        "          <ul>",
        '            <li><a href="../index.html">Home</a></li>',
        '            <li><a href="../archive.html">Archive</a></li>',
        '            <li><a href="../candidates.html">Candidates</a></li>',
        '            <li><a href="../committees.html">Committees</a></li>',
        '            <li><a href="../counties.html">Counties</a></li>',
        '            <li><a href="../officials.html">Officials</a></li>',
        '            <li><a href="../people/index.html">Name Index</a></li>',
        '            <li><a href="../research.html">Research</a></li>',
        "          </ul>",
        "        </nav>",
        "      </div>",
        "    </header>",
        "",
        '    <main id="main">',
        '      <div class="wrap back-wrap">',
        '        <p class="back-row"><a class="back-btn" href="../index.html">← Back to Home</a></p>',
        "      </div>",
        '      <section class="page-hero">',
        '        <div class="wrap">',
        "          <h1>Current Schedule</h1>",
        "        </div>",
        "      </section>",
        '      <section class="page-body schedule-page">',
        '        <div class="wrap page-prose">',
        "          <p>Statewide meetings and events posted for the next 60 days, for the five elected state offices, the boards those offices sit on, the House, the Senate, and the Legislature's current formal committees. Critical Dates are listed even when they fall later. Past items are removed daily. Times are Mountain Time.</p>",
        session_note,
        '          <p class="schedule-updated">Last updated: %s</p>' % esc(label_updated(generated)),
        '          <nav class="schedule-jump" aria-label="On this page">',
        "            <p>On this page</p>",
        "            <ol>",
        *["              " + b for b in jump_bits],
        "            </ol>",
        "          </nav>",
    ]

    for sid, heading, _kind in sections:
        items = by.get(sid) or []
        parts.append('          <section class="sched-section" id="%s" aria-labelledby="%s-h">' % (esc(sid), esc(sid)))
        parts.append('            <h2 id="%s-h">%s</h2>' % (esc(sid), esc(heading)))
        if not items:
            parts.append('            <p class="sched-empty">No scheduled events posted.</p>')
        else:
            parts.append('            <ul class="sched-list">')
            for ev in items:
                d = parse_date(ev["date"])
                end = parse_date(ev.get("end_date") or "")
                date_l = label_range(d, end) if d else ev["date"]
                parts.append('              <li class="sched-item">')
                parts.append('                <p class="sched-when"><span class="sched-date">%s</span>' % esc(date_l))
                if ev.get("time"):
                    parts.append('                <span class="sched-time">%s</span></p>' % esc(ev["time"]))
                else:
                    parts.append("                </p>")
                title_html = esc(ev["title"])
                if ev.get("unverified"):
                    title_html += ' <span class="sched-unverified">(unverified)</span>'
                parts.append('                <p class="sched-title">%s</p>' % title_html)
                if ev.get("location"):
                    parts.append('                <p class="sched-loc">%s</p>' % esc(ev["location"]))
                if ev.get("source_url"):
                    parts.append(
                        '                <p class="sched-src"><a href="%s">Source</a></p>'
                        % esc(ev["source_url"])
                    )
                parts.append("              </li>")
            parts.append("            </ul>")
        parts.append("          </section>")

    parts += [
        "        </div>",
        "      </section>",
        "    </main>",
        "",
        '    <footer class="site-footer">',
        '      <div class="wrap footer-inner">',
        '        <nav aria-label="Footer">',
        '          <ul class="footer-links">',
        '            <li><a href="../about.html">About</a></li>',
        '            <li><a href="../privacy.html">Privacy</a></li>',
        '            <li><a href="../contact.html">Contact</a></li>',
        '            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v1.2.pdf">User\'s Guide</a></li>',
        "          </ul>",
        "        </nav>",
        "        <p>&copy; 2026 WyoVote. All rights reserved.</p>",
        "      </div>",
        "    </footer>",
        "  </body>",
        "</html>",
        "",
    ]
    # drop empty strings from session_note when not in session
    return "\n".join(p for p in parts if p is not None)


def label_updated(dt: datetime) -> str:
    return "%s, %s" % (label_date(dt.date()), format_time_mt(dt))


def main() -> int:
    repo = repo_root()
    today = today_denver()
    generated = now_denver()
    critical_path = repo / "data" / "critical_dates.json"

    critical = load_critical_dates(critical_path, today)
    start, end = session_window(critical_path, today)
    during = in_legislative_session(today, start, end)
    print("today", today.isoformat(), "horizon", (today + timedelta(days=HORIZON_DAYS)).isoformat(), "in_session", during)

    year = committee_year_for(today)
    print("committee year", year)
    committees = load_committees(year)
    sections = section_defs(committees)
    # Apply fuller names later if events provide them.

    raw = fetch_lso_months(today)
    print("LSO raw events", len(raw))
    lso_events, owner_full = assign_lso_events(raw, committees, today, during)
    # Upgrade section headings with fuller official names from events.
    upgraded = []
    for sid, heading, kind in sections:
        if kind == "committee" and sid.startswith("committee-"):
            owner = sid.split("committee-", 1)[1].upper()
            if owner in owner_full:
                heading = display_name_for(owner, heading, heading, owner_full[owner])
        upgraded.append((sid, heading, kind))
    sections = upgraded

    events: list[dict] = list(critical)
    events.extend(lso_events)

    if not during:
        gov = fetch_governor_events(today)
        print("governor ICS upcoming", len(gov))
        events.extend(gov)
        # Treasurer public announcements (not tracked on a calendar feed)
        treas = fetch_treasurer_announcements(today)
        print("treasurer announcements", len(treas))
        events.extend(treas)
    else:
        print("in session: skipping non-committee special-event scrapes (offices still get boards)")

    sbc = fetch_sbc_events(today)
    print("SBC upcoming", len(sbc))
    events.extend(sbc)
    slib = fetch_slib_events(today)
    print("SLIB upcoming", len(slib))
    events.extend(slib)
    sbe = fetch_sbe_events(today)
    print("SBE upcoming", len(sbe))
    events.extend(sbe)

    events = dedupe(events)
    until = today + timedelta(days=HORIZON_DAYS)
    before = len(events)
    events = [e for e in events if within_horizon(e, today, until)]
    print("horizon through", until.isoformat(), "kept", len(events), "of", before)

    payload = {
        "generated_at": generated.isoformat(),
        "timezone": TZ_NAME,
        "in_session": during,
        "committee_year": year,
        "events": events,
        "section_order": [{"id": s, "heading": h, "kind": k} for s, h, k in sections],
    }
    data_path = repo / "data" / "schedule.json"
    data_path.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", data_path, "events", len(events))

    page = render_page(repo, generated, events, sections, during)
    page_path = repo / "schedule" / "index.html"
    page_path.write_text(page)
    print("wrote", page_path)

    # Mark outside links the same way as the rest of the site, on this page only.
    sys.path.insert(0, str(repo / "tools"))
    try:
        import mark_outside_links as mol
        totals = mol.apply_paths([page_path])
        print("outside-link markers", totals)
    except Exception as e:
        print("warn: mark_outside_links:", e, file=sys.stderr)

    counts = counts_by_section(events, sections)
    print("\nEvent counts by section:")
    for sid, heading, _ in sections:
        n = counts.get(sid, 0)
        if n or sid in {s for s, _, k in sections if k != "committee"}:
            print("  %3d  %s (%s)" % (n, heading, sid))
    formal_empty = sum(1 for sid, _, k in sections if k == "committee" and counts.get(sid, 0) == 0)
    formal_with = sum(1 for sid, _, k in sections if k == "committee" and counts.get(sid, 0) > 0)
    print("formal committees with events", formal_with, "empty", formal_empty, "total", formal_with + formal_empty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
