#!/usr/bin/env python3
"""Build data/schedule.json and the Current Schedule pages from official sources.

One run writes schedule/index.html (Critical Dates, The Weekly, four buttons)
and the four category pages: schedule/state-offices.html, boards.html,
standing-committees.html, and other-committees.html.

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
                            office=BOARDS_HEADING,
                            section=BOARDS_ID,
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


WCSAB_PAGE = "https://edu.wyoming.gov/wyoming-charter-school-authorizing-board/"
WCSAB_NAME = "Wyoming Charter School Authorizing Board"


def fetch_wcsab_events(today: date) -> list[dict]:
    """Department of Education: the Charter School Authorizing Board posts an
    'Upcoming Meeting Dates' list (dates only)."""
    status, body = fetch(WCSAB_PAGE)
    if status != 200:
        raise RuntimeError("HTTP %s" % status)
    text = body.decode("utf-8", "replace")
    i = text.find("Upcoming Meeting Dates")
    if i < 0:
        raise RuntimeError("Upcoming Meeting Dates list not found")
    chunk = html.unescape(re.sub(r"<[^>]+>", "\n", text[i:i + 8000]))
    j = chunk.find("Past Meeting")
    if j > 0:
        chunk = chunk[:j]
    out = []
    for m in re.finditer(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s*(\d{4})", chunk):
        try:
            d = datetime.strptime("%s %s %s" % m.groups(), "%B %d %Y").date()
        except ValueError:
            continue
        if d < today:
            continue
        out.append(event_record(
            date_s=d.isoformat(), time_s="", office=BOARDS_HEADING, section=BOARDS_ID,
            title="%s meeting" % WCSAB_NAME, location="", source_url=WCSAB_PAGE,
            source_name="Wyoming Department of Education",
        ))
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
    out.append((JCC_ID, JCC_HEADING, "committee"))
    return out


JCC_ID = "committee-jcc"
JCC_HEADING = "Conference Committees"
JCC_RE = re.compile(r"^\s*(HB|SF|HJ|SJ)0*(\d+)JCC0*(\d+)\s*[-–]?\s*(.*)$", re.I)


def conference_title(name: str) -> str:
    """'HB0011JCC01 - Manufacturing sales...' -> 'HB 11 Conference Committee: Manufacturing sales...'.
    A second committee on the same bill is 'Conference Committee No. 2'."""
    m = JCC_RE.match(name or "")
    if not m:
        return ""
    kind, num, n, catch = m.group(1).upper(), int(m.group(2)), int(m.group(3)), m.group(4).strip().rstrip(".")
    t = "%s %d Conference Committee" % (kind, num)
    if n > 1:
        t += " No. %d" % n
    return t + (": " + catch if catch else "")


def floor_chamber(ev: dict, title_name: str) -> tuple[str, str] | None:
    """House or Senate floor session from the LSO calendar, else None."""
    name = (title_name or "").lower()
    mtype = (ev.get("meetingType") or "").strip().lower()
    if ev.get("meetingKind") == 1 or "floor session" in name:
        if "senate" in name or (mtype == "senate" and "house" not in name):
            return ("senate", "Senate")
        if "house" in name or mtype == "house":
            return ("house", "House")
    return None


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
        # Kind 1: House and Senate floor sessions (committeeId 0, no code).
        chamber = floor_chamber(ev, title_name)
        if chamber:
            sid, heading = chamber
            out.append(
                event_record(
                    date_s=start_d.isoformat(),
                    end_date=end_d.isoformat() if end_d != start_d else "",
                    time_s=lso_time_label(ev, start, utc),
                    office=heading,
                    section=sid,
                    title="%s floor session" % heading,
                    location=lso_location(ev),
                    source_url=lso_source_url(ev, start),
                    source_name="Wyoming Legislature calendar",
                    tentative=(ev.get("category") == "Tentative"),
                )
            )
            continue
        # Kind 4: holidays, boards, session convening
        if kind == 4 or ev.get("committeeId") in (0, None):
            jcc = conference_title(title_name)
            if jcc:
                out.append(
                    event_record(
                        date_s=start_d.isoformat(),
                        end_date=end_d.isoformat() if end_d != start_d else "",
                        time_s=lso_time_label(ev, start, utc),
                        office=JCC_HEADING,
                        section=JCC_ID,
                        title=jcc,
                        location=lso_location(ev),
                        source_url=lso_source_url(ev, start),
                        source_name="Wyoming Legislature calendar",
                        tentative=(ev.get("category") == "Tentative"),
                    )
                )
                continue
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


# ---------- Two-level pages: Schedule (level 1) and four category pages (level 2) ----------

WEEKLY_DAYS = 7  # today plus the next six calendar days
SESSION_PAGE_DAYS = 14  # category pages during a session: today plus the next 13 days


def page_days(during_session: bool) -> int:
    return SESSION_PAGE_DAYS if during_session else HORIZON_DAYS

# (page id, button/heading label, one-line description)
CATEGORIES = [
    ("state-offices", "State Offices",
     "The five elected state offices, the House, and the Senate."),
    ("boards", "Boards",
     "Boards and commissions the five statewide officials sit on, listed once."),
    ("standing-committees", "Standing Committees",
     "The Legislature's joint standing committees."),
    ("other-committees", "Other Committees",
     "Management Council, select committees, task forces, and working groups."),
]
CATEGORY_LABEL = {cid: label for cid, label, _ in CATEGORIES}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WD_SHORT = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
FOLD_MIN = 3  # fold a body's repeated meetings when there are at least this many in a row


def category_for(sid: str, kind: str) -> str:
    """Map a schedule section to one of the four level-2 pages."""
    if kind == "office":
        return "state-offices"
    if kind == "boards" or sid == BOARDS_ID:
        return "boards"
    if re.fullmatch(r"committee-j\d\d", sid):
        return "standing-committees"
    return "other-committees"


def short_note(ev: dict, heading: str) -> str:
    """Event title without the body name it repeats."""
    t = (ev.get("title") or "").strip()
    if heading and t.lower().startswith(heading.lower()):
        t = t[len(heading):].strip()
        t = re.sub(r"^meeting\b\s*", "", t, flags=re.I).strip()
    return t or "Meeting"


def short_time(t: str) -> str:
    return (t or "").replace(" MT", "")


def fold_repeats(items: list[dict]) -> list[dict]:
    """Fold runs of the same one-day meeting (same title, time, place) on
    consecutive days, weekends allowed as gaps, into one entry."""
    out: list[dict] = []
    i = 0
    while i < len(items):
        ev = items[i]
        run = [ev]
        if (ev.get("end_date") or ev["date"]) == ev["date"]:
            j = i + 1
            while j < len(items):
                nx = items[j]
                prev = parse_date(run[-1]["date"])
                d = parse_date(nx["date"])
                if (
                    (nx.get("end_date") or nx["date"]) == nx["date"]
                    and nx["title"] == ev["title"]
                    and nx["time"] == ev["time"]
                    and nx["location"] == ev["location"]
                    and d and prev and 1 <= (d - prev).days <= 3
                    and all((prev + timedelta(days=k)).weekday() >= 5 for k in range(1, (d - prev).days))
                ):
                    run.append(nx)
                    j += 1
                else:
                    break
        if len(run) >= FOLD_MIN:
            rec = dict(ev)
            rec["end_date"] = run[-1]["date"]
            rec["folded"] = len(run)
            rec["fold_weekdays_only"] = any(
                (parse_date(b["date"]) - parse_date(a["date"])).days > 1 for a, b in zip(run, run[1:])
            )
            out.append(rec)
            i += len(run)
        else:
            out.append(ev)
            i += 1
    return out


def page_shell(title: str, back_href: str, back_label: str, description: str, body: list[str]) -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "  <head>",
        '    <meta charset="utf-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1">',
        "    <title>%s — WyoVote</title>" % esc(title),
        '    <meta name="description" content="%s">' % esc(description),
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
        '            <li><a href="../candidates.html">Candidates</a></li>',
        '            <li><a href="../committees.html">Committees</a></li>',
        '            <li><a href="../counties.html">Counties</a></li>',
        '            <li><a href="../officials.html">Officials</a></li>',
        '            <li><a href="../people/index.html">Name Index</a></li>',
        '            <li><a href="../research.html">Research</a></li>',
        '            <li><a href="../archive.html">Archive</a></li>',
        "          </ul>",
        "        </nav>",
        "      </div>",
        "    </header>",
        "",
        '    <main id="main">',
        '      <div class="wrap back-wrap">',
        '        <p class="back-row"><a class="back-btn" href="%s">← Back to %s</a></p>' % (esc(back_href), esc(back_label)),
        "      </div>",
        '      <section class="page-hero">',
        '        <div class="wrap">',
        "          <h1>%s</h1>" % esc(title),
        "        </div>",
        "      </section>",
        '      <section class="page-body schedule-page">',
        '        <div class="wrap page-prose">',
    ]
    parts += ["          " + b for b in body if b is not None and b != ""]
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
        '            <li class="footer-guide"><a href="/guide/WyoVote-Users-Guide-v2.0.pdf">User\'s Guide</a></li>',
        "          </ul>",
        "        </nav>",
        "        <p>&copy; 2026 WyoVote. All rights reserved.</p>",
        "      </div>",
        "    </footer>",
        "  </body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def render_card(ev: dict) -> list[str]:
    d = parse_date(ev["date"])
    end = parse_date(ev.get("end_date") or "")
    if ev.get("folded"):
        when = "%s, %s" % (
            "Weekdays" if ev.get("fold_weekdays_only") else "Daily",
            label_range(d, end),
        )
    else:
        when = ("%s %s" % (WD_SHORT[d.weekday()], label_range(d, end))) if d else ev["date"]
    out = ['<li class="sched-item">', '<p class="sched-when"><span class="sched-date">%s</span>' % esc(when)]
    out[-1] += (' <span class="sched-time">%s</span></p>' % esc(ev["time"])) if ev.get("time") else "</p>"
    title_html = esc(ev["title"])
    if ev.get("unverified"):
        title_html += ' <span class="sched-unverified">(unverified)</span>'
    if ev.get("folded"):
        title_html += " (%d meetings)" % ev["folded"]
    out.append('<p class="sched-title">%s</p>' % title_html)
    if ev.get("location"):
        out.append('<p class="sched-loc">%s</p>' % esc(ev["location"]))
    if ev.get("source_url"):
        label = "Source (first meeting)" if ev.get("folded") else "Source"
        extra = " (%s)" % esc(ev["source_name"]) if ev.get("source_name") else ""
        out.append('<p class="sched-src"><a href="%s">%s</a>%s</p>' % (esc(ev["source_url"]), label, extra))
    out.append("</li>")
    return out


CARD_MAX = 4  # a body with more entries than this gets one table row per entry


def render_rows(items: list[dict]) -> list[str]:
    """Compact table for a body with many meetings (mostly during a session)."""
    out = ['<table class="sched-table sched-rows">',
           '<thead><tr><th scope="col">Date</th><th scope="col">Time</th><th scope="col">Meeting and place</th></tr></thead>',
           "<tbody>"]
    for ev in items:
        d = parse_date(ev["date"])
        end = parse_date(ev.get("end_date") or "")
        if ev.get("folded"):
            when = "%s, %s" % ("Weekdays" if ev.get("fold_weekdays_only") else "Daily", label_range(d, end))
        else:
            when = "%s %s" % (WD_SHORT[d.weekday()], label_range(d, end))
        what = esc(ev["title"])
        if ev.get("folded"):
            what += " (%d meetings)" % ev["folded"]
        if ev.get("location"):
            what += ". " + esc(ev["location"])
        if ev.get("source_url"):
            what += ' <a href="%s">Source</a>' % esc(ev["source_url"])
        out.append('<tr><td class="sched-d">%s</td><td class="sched-t">%s</td><td class="sched-note">%s</td></tr>' % (
            esc(when), esc(short_time(ev["time"])) or "—", what))
    out += ["</tbody>", "</table>"]
    return out


def updated_line(generated: datetime) -> str:
    return '<p class="schedule-updated">Last updated: %s</p>' % esc(label_updated(generated))


def time_sort_key(t: str) -> str:
    """Sort key for a time label: clock times in order, then all-day/blank."""
    m = re.search(r"(\d{1,2}):(\d{2})\s*(a\.m\.|p\.m\.)|(12:00 noon)", t or "")
    if not m:
        return "99:99"
    if m.group(4):
        return "12:00"
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "p.m." else 0)
    return "%02d:%s" % (h, m.group(2))


CRITICAL_TAG = '<strong class="crit-tag">CRITICAL</strong>'


def render_level1(generated: datetime, events: list[dict], sections, during_session: bool, today: date) -> str:
    head_of = {sid: h for sid, h, _ in sections}
    cat_of = {sid: category_for(sid, k) for sid, _, k in sections}
    crit = [e for e in events if e["section"] == "critical-dates"]
    reg = [e for e in events if e["section"] != "critical-dates" and e["section"] in head_of]
    last = today + timedelta(days=WEEKLY_DAYS - 1)
    body = [
        ("<p>Meetings and events posted by the five elected state offices, the boards they sit on, "
         "the House, the Senate, and the Legislature's formal committees. The Weekly lists today and "
         "the next six days and moves forward each day. The four buttons below list everything posted "
         "for the next %d days, with locations and sources. Past items are removed daily. "
         "Times are Mountain Time.</p>") % page_days(during_session),
    ]
    if during_session:
        body.append("<p>The Legislature is in session. Legislative listings show the floor and standard committee schedule.</p>")
    body.append(updated_line(generated))
    body.append('<h2 id="weekly">The Weekly</h2>')
    body.append('<p class="sched-legend">%s marks a critical date: legislators taking office, the start and end of a session, and other key dates. Select a name for details.</p>' % CRITICAL_TAG)

    def in_week(e):
        s = parse_date(e["date"])
        en = parse_date(e.get("end_date") or "") or s
        return bool(s and s <= last and en >= today)

    week = [e for e in crit + reg if in_week(e)]
    if not week:
        body.append('<p class="sched-none">Nothing posted for today or the next six days.</p>')
    else:
        body.append('<table class="sched-table sched-weekly">')
        body.append('<thead><tr><th scope="col">Time</th><th scope="col">Who</th><th scope="col">What</th></tr></thead>')
        days = defaultdict(list)
        for e in week:
            days[max(parse_date(e["date"]), today)].append(e)
        for day in sorted(days):
            label = "%s, %s" % (WEEKDAYS[day.weekday()], label_date(day))
            body.append('<tbody><tr class="sched-day"><th scope="rowgroup" colspan="3">%s</th></tr>' % esc(label))
            rows = sorted(days[day], key=lambda x: (0 if x["section"] == "critical-dates" else 1, time_sort_key(x["time"]), x.get("sort", 100), head_of.get(x["section"], "")))
            for e in rows:
                t = esc(short_time(e["time"])) or "—"
                en = parse_date(e.get("end_date") or "")
                span = " (%s)" % label_range(parse_date(e["date"]), en) if en and en > parse_date(e["date"]) else ""
                if e["section"] == "critical-dates":
                    what = esc(e["title"]) + (" (unverified)" if e.get("unverified") else "")
                    if e.get("location"):
                        what += ". " + esc(e["location"])
                    if e.get("source_url"):
                        what += ' <a href="%s">Source</a>' % esc(e["source_url"])
                    body.append('<tr class="sched-critical"><td class="sched-t">%s</td><td>%s</td><td class="sched-note">%s%s</td></tr>' % (t, CRITICAL_TAG, what, esc(span)))
                else:
                    h = head_of[e["section"]]
                    body.append('<tr><td class="sched-t">%s</td><td><a href="%s.html#%s">%s</a></td><td class="sched-note">%s</td></tr>' % (
                        t, cat_of[e["section"]], esc(e["section"]), esc(h), esc(short_note(e, h) + span)))
            body.append("</tbody>")
        body.append("</table>")
    counts = defaultdict(int)
    cutoff = (today + timedelta(days=page_days(during_session) - 1)).isoformat()
    for e in reg:
        if e["date"] <= cutoff:
            counts[cat_of[e["section"]]] += 1
    body.append('<h2 id="more">Next %d Days</h2>' % page_days(during_session))
    body.append('<ul class="sched-cat-btns">')
    for cid, label, _desc in CATEGORIES:
        n = counts.get(cid, 0)
        sub = "Nothing posted" if n == 0 else ("1 item posted" if n == 1 else "%d items posted" % n)
        body.append('<li><a class="sched-cat-btn" href="%s.html"><span class="sched-cat-name">%s</span><span class="sched-cat-count">%s</span></a></li>' % (cid, esc(label), sub))
    body.append("</ul>")
    later = [e for e in crit if parse_date(e["date"]) > last]
    body.append('<h2 id="critical-later">Later Critical Dates</h2>')
    if later:
        body.append('<ul class="sched-later">')
        for e in later:
            bits = "<strong>%s</strong>: %s" % (esc(label_date(parse_date(e["date"]))), esc(e["title"]))
            if e.get("unverified"):
                bits += " (unverified)"
            if e.get("time"):
                bits += ", " + esc(short_time(e["time"]))
            if e.get("source_url"):
                bits += ' <a href="%s">Source</a>' % esc(e["source_url"])
            body.append("<li>%s %s</li>" % (CRITICAL_TAG, bits))
        body.append("</ul>")
    else:
        body.append('<p class="sched-none">No later critical dates posted.</p>')
    return page_shell(
        "Current Schedule", "../index.html", "Home",
        "Current statewide meetings and events for Wyoming's five elected offices, their boards, the House, the Senate, and formal legislative committees.",
        body,
    )


def render_level2(cid: str, generated: datetime, events: list[dict], sections, during_session: bool, today: date | None = None) -> str:
    label = CATEGORY_LABEL[cid]
    desc = dict((c, d) for c, _, d in CATEGORIES)[cid]
    mine = [(sid, h) for sid, h, k in sections if sid != "critical-dates" and category_for(sid, k) == cid]
    days = page_days(during_session)
    if today is not None:
        cutoff = (today + timedelta(days=days - 1)).isoformat()
        events = [e for e in events if e["date"] <= cutoff]
    by = defaultdict(list)
    for e in events:
        by[e["section"]].append(e)
    body = [
        "<p>%s Everything posted for the next %d days. Past items are removed daily. Times are Mountain Time.</p>" % (esc(desc), days),
    ]
    if during_session and cid in ("state-offices", "standing-committees", "other-committees"):
        body.append("<p>The Legislature is in session. Legislative listings show the floor and standard committee schedule.</p>")
    body.append(updated_line(generated))
    with_ev = [(sid, h) for sid, h in mine if by.get(sid)]
    empty = [h for sid, h in mine if not by.get(sid)]
    if len(with_ev) > 3:
        body.append('<p class="sched-jumpline"><strong>On this page:</strong> ' + "; ".join(
            '<a href="#%s">%s</a>' % (esc(sid), esc(h)) for sid, h in with_ev) + ".</p>")
    if not with_ev:
        body.append('<p class="sched-none">Nothing posted for the next %d days.</p>' % days)
    for sid, h in with_ev:
        body.append('<section class="sched-section" id="%s" aria-labelledby="%s-h">' % (esc(sid), esc(sid)))
        body.append('<h2 id="%s-h">%s</h2>' % (esc(sid), esc(h)))
        items = fold_repeats(sorted(by[sid], key=lambda x: (x["date"], time_sort_key(x["time"]))))
        if len(items) <= CARD_MAX:
            body.append('<ul class="sched-list">')
            for ev in items:
                body += render_card(ev)
            body.append("</ul>")
        else:
            body += render_rows(items)
        body.append("</section>")
    if empty:
        body.append('<p class="sched-nothing"><strong>Nothing posted:</strong> %s.</p>' % "; ".join(esc(h) for h in empty))
    return page_shell(label, "index.html", "Schedule", "Current %s schedule on WyoVote." % label, body)


def write_pages(repo: Path, generated: datetime, events: list[dict], sections, during: bool, today: date) -> list[Path]:
    out_dir = repo / "schedule"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    p = out_dir / "index.html"
    p.write_text(render_level1(generated, events, sections, during, today))
    paths.append(p)
    for cid, _label, _d in CATEGORIES:
        p = out_dir / ("%s.html" % cid)
        p.write_text(render_level2(cid, generated, events, sections, during, today))
        paths.append(p)
    return paths


def label_updated(dt: datetime) -> str:
    return "%s, %s" % (label_date(dt.date()), format_time_mt(dt))


def render_only(repo: Path, today: date) -> int:
    """Rebuild the five pages from the saved data/schedule.json (no fetching).
    Past items are still dropped."""
    data = json.loads((repo / "data" / "schedule.json").read_text())
    generated = datetime.fromisoformat(data["generated_at"])
    sections = [(s["id"], s["heading"], s["kind"]) for s in data["section_order"]]
    until = today + timedelta(days=HORIZON_DAYS)
    events = [e for e in data["events"] if within_horizon(e, today, until)]
    paths = write_pages(repo, generated, events, sections, bool(data.get("in_session")), today)
    sys.path.insert(0, str(repo / "tools"))
    import mark_outside_links as mol
    print("outside-link markers", mol.apply_paths(paths))
    for pth in paths:
        print("wrote", pth)
    return 0


def schedule_date_arg() -> date | None:
    """--for-date YYYY-MM-DD builds the pages as of that day (a 10 PM crawl
    stages the next morning's pages)."""
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--for-date" and i + 1 < len(args):
            return date.fromisoformat(args[i + 1])
        if a.startswith("--for-date="):
            return date.fromisoformat(a.split("=", 1)[1])
    return None


def make_context(repo: Path, today: date) -> dict:
    critical_path = repo / "data" / "critical_dates.json"
    critical = load_critical_dates(critical_path, today)
    start, end = session_window(critical_path, today)
    during = in_legislative_session(today, start, end)
    year = committee_year_for(today)
    committees = load_committees(year)
    sections = section_defs(committees)
    print("today", today.isoformat(), "horizon", (today + timedelta(days=HORIZON_DAYS)).isoformat(),
          "in_session", during, "committee year", year)
    return {"repo": repo, "today": today, "critical": critical, "during": during,
            "year": year, "committees": committees, "sections": sections, "owner_full": {}}


def source_list(ctx: dict) -> list[tuple[str, str, str, object]]:
    """(source id, label, url, fetcher) for every official source the
    builder reads. The spider runs the same list."""
    today, during = ctx["today"], ctx["during"]

    def lso():
        raw = fetch_lso_months(today)
        evs, owner_full = assign_lso_events(raw, ctx["committees"], today, during)
        ctx["owner_full"].update(owner_full)
        return evs

    out = [("lso", "Legislature calendar (LSO API)", LSO + "/api/Calendar/Events/", lso)]
    if not during:
        out += [
            ("governor", "Governor public calendar (Google feed)", GOV_ICS, lambda: fetch_governor_events(today)),
            ("treasurer", "State Treasurer announcements", TREAS_HOME, lambda: fetch_treasurer_announcements(today)),
        ]
    out += [
        ("sbc", "State Building Commission", SBC_PAGE, lambda: fetch_sbc_events(today)),
        ("slib", "State Loan and Investment Board", SLIB_PAGE, lambda: fetch_slib_events(today)),
        ("sbe", "State Board of Education", SBE_PAGE, lambda: fetch_sbe_events(today)),
        ("wcsab", "Charter School Authorizing Board (Education)", WCSAB_PAGE, lambda: fetch_wcsab_events(today)),
    ]
    return out


def collect_sources(ctx: dict) -> dict:
    results = {}
    for sid, label, url, fn in source_list(ctx):
        t0 = time.time()
        try:
            evs = list(fn())
            results[sid] = {"label": label, "url": url, "ok": True, "error": "", "events": evs}
        except Exception as e:
            results[sid] = {"label": label, "url": url, "ok": False, "error": str(e)[:200], "events": []}
        results[sid]["seconds"] = round(time.time() - t0, 1)
        print("source %-10s %3d events %5.1fs %s" % (sid, len(results[sid]["events"]), results[sid]["seconds"],
                                                     "" if results[sid]["ok"] else "FAILED " + results[sid]["error"]))
    return results


def build_and_write(ctx: dict, events_from_sources: list[dict], generated: datetime, extra: dict | None = None) -> list[Path]:
    repo, today, during = ctx["repo"], ctx["today"], ctx["during"]
    sections = []
    for sid, heading, kind in ctx["sections"]:
        if kind == "committee" and sid.startswith("committee-"):
            owner = sid.split("committee-", 1)[1].upper()
            if owner in ctx["owner_full"]:
                heading = display_name_for(owner, heading, heading, ctx["owner_full"][owner])
        sections.append((sid, heading, kind))
    events = dedupe(list(ctx["critical"]) + list(events_from_sources))
    until = today + timedelta(days=HORIZON_DAYS)
    before = len(events)
    events = [e for e in events if within_horizon(e, today, until)]
    print("horizon through", until.isoformat(), "kept", len(events), "of", before)
    payload = {
        "generated_at": generated.isoformat(),
        "schedule_date": today.isoformat(),
        "timezone": TZ_NAME,
        "in_session": during,
        "committee_year": ctx["year"],
        "events": events,
        "section_order": [
            {"id": s, "heading": h, "kind": k, "category": ("" if s == "critical-dates" else category_for(s, k))}
            for s, h, k in sections
        ],
    }
    if extra:
        payload.update(extra)
    data_path = repo / "data" / "schedule.json"
    data_path.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", data_path, "events", len(events))
    paths = write_pages(repo, generated, events, sections, during, today)
    for pth in paths:
        print("wrote", pth)
    sys.path.insert(0, str(repo / "tools"))
    try:
        import mark_outside_links as mol
        print("outside-link markers", mol.apply_paths(paths))
    except Exception as e:
        print("warn: mark_outside_links:", e, file=sys.stderr)
    counts = counts_by_section(events, sections)
    print("\nEvent counts by section:")
    for sid, heading, kind in sections:
        n = counts.get(sid, 0)
        if n or kind != "committee":
            print("  %3d  %s (%s)" % (n, heading, sid))
    return [data_path] + paths


def main() -> int:
    repo = repo_root()
    today = schedule_date_arg() or today_denver()
    if "--render-only" in sys.argv[1:]:
        return render_only(repo, today)
    generated = now_denver()
    ctx = make_context(repo, today)
    results = collect_sources(ctx)
    evs = [e for r in results.values() for e in r["events"]]
    build_and_write(ctx, evs, generated)
    return 0


if __name__ == "__main__":
    sys.exit(main())
