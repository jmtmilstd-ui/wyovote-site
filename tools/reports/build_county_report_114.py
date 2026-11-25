#!/usr/bin/env python3
"""114 County Officeholders — compact summary + Profiles.

Reads the standard officeholder, election, person, and Profile files in the
site tree. Parameterized by county slug (Weston, Crook, and later counties).

Does not publish, merge, or edit the live site.
"""
from __future__ import annotations

import argparse
import csv
import html as htmlmod
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, CondPageBreak, Image, Flowable,
)
from reportlab.pdfbase.pdfmetrics import stringWidth

SITE_DEFAULT = Path("/workspace/wyovote-114")
OUT_DIR_DEFAULT = Path("/workspace/county-report")
WYOLEG = Path("/workspace/wyoleg")
sys.path.insert(0, str(WYOLEG))
sys.path.insert(0, str(SITE_DEFAULT / "tools"))
import mtr_brand as BR
from numbered_canvas import make_numbered_canvas
from booklet_pad import pad_pdf
from rank_chart import chart_svg, bands_from_ranking
import ranking

FD = "/usr/share/fonts/truetype/liberation/"
for a, f in (("DV", "Regular"), ("DVB", "Bold"), ("DVI", "Italic")):
    pdfmetrics.registerFont(TTFont(a, FD + f"LiberationSans-{f}.ttf"))
addMapping("DV", 0, 0, "DV")
addMapping("DV", 1, 0, "DVB")
addMapping("DV", 0, 1, "DVI")
addMapping("DV", 1, 1, "DVB")

PW, PH = 8.5 * inch, 14 * inch
ML = MR = 0.75 * inch
MB = 0.95 * inch
MT = max(0.75 * inch, BR.HEADER_CLEAR)
FW = PW - ML - MR
FH = PH - MT - MB

DKG = HexColor("#14501A")
NAVY = HexColor("#1f3a68")
INK = HexColor("#111111")
HEAD_BG = HexColor("#d7e6d7")
ZEBRA = HexColor("#eef6ee")
GRID = HexColor("#5a5a5a")
RED = HexColor("#9b0000")

MINF, TBL, BASE = 14, 12, 14
AUTHOR = "MTR Research"
RUN = "2026-11-23"
RANK_LEGEND = "Rank: 1 = MOST Conservative"

# Office, Name, Pty, Term ends, Rank. No Profile-number column (Michael t833u).
COLS = [1.90 * inch, 3.20 * inch, 0.40 * inch, 0.98 * inch, 0.52 * inch]
assert abs(sum(COLS) - FW) < 1, sum(COLS)
HEADERS = ["Office", "Name", "Pty", "Term ends", "Rank"]
PCOLS = [1.70 * inch, 2.65 * inch, 2.65 * inch]
assert abs(sum(PCOLS) - FW) < 1
PHEAD = ["Precinct", "Committeemen", "Committeewomen"]

# Group order for the report (alphanumeric sort keys; I is skipped).
GROUP_ORDER = {
    "federal": "A", "statewide": "B", "state-senate": "C", "state-house": "D",
    "county": "E", "municipal": "F", "schools": "G", "special-districts": "H",
    "supreme-court": "J1", "chancery-court": "J2", "judicial": "J3", "precincts": "P",
}


def S(nm, **k):
    d = dict(fontName="DV", fontSize=BASE, leading=18, textColor=INK, spaceAfter=6)
    d.update(k)
    return ParagraphStyle(nm, **d)


body = S("body")
center = S("center", alignment=TA_CENTER)
h1 = S("h1", fontName="DVB", fontSize=22, leading=26, textColor=NAVY, spaceBefore=0, spaceAfter=6)
h2 = S("h2", fontName="DVB", fontSize=14, leading=17, textColor=DKG, spaceBefore=8, spaceAfter=3)
h3 = S("h3", fontName="DVB", fontSize=16, leading=20, textColor=NAVY, spaceBefore=2, spaceAfter=4)
note = S("note", fontSize=12, leading=15, spaceAfter=4)
draftst = S("draftst", fontName="DVB", fontSize=14, leading=17, textColor=RED, alignment=TA_CENTER, spaceAfter=8)
cell = S("cell", fontSize=TBL, leading=14.5, spaceAfter=0)
cellc = S("cellc", fontSize=TBL, leading=14.5, spaceAfter=0, alignment=TA_CENTER)
cellb = S("cellb", fontName="DVB", fontSize=TBL, leading=14.5, spaceAfter=0, textColor=DKG)
cellbc = S("cellbc", fontName="DVB", fontSize=TBL, leading=14.5, spaceAfter=0, textColor=DKG, alignment=TA_CENTER)
pbody = S("pbody", fontSize=14, leading=18, spaceAfter=6)
psmall = S("psmall", fontSize=12, leading=15, spaceAfter=3)
pth = S("pth", fontName="DVB", fontSize=12, leading=15, spaceAfter=0, textColor=DKG)


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def short_term(term: str | None) -> str:
    if not term:
        return "—"
    return term.replace("January ", "Jan ").replace("January", "Jan")


def pty_of(holder: dict) -> str:
    p = (holder.get("party") or "").strip()
    if not p or p.lower() in {"np", "n", "nonpartisan", "non-partisan", "non partisan"}:
        return "—"
    return p[0].upper() if len(p) > 1 else p.upper()


def person_key(holder: dict) -> str:
    return holder.get("person_id") or holder.get("name") or ""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def office_label(office_title: str, holder: dict | None = None) -> str:
    """Compact office title for the summary first column. Roles are not included;
    they follow the name (Michael t836u)."""
    title = office_title
    # Compact a few long titles
    title = title.replace("U.S. Senators", "U.S. Senate")
    title = title.replace("U.S. Representative", "U.S. House")
    title = title.replace("Superintendent of Public Instruction", "Supt. of Public Instruction")
    title = title.replace("Weston County School District #1 Board, at-large", "School Dist. #1 Board")
    title = title.replace("Weston County School District #7 Board, at-large", "School Dist. #7 Board")
    title = title.replace("Newcastle City Council, at-large", "Newcastle Council member")
    title = title.replace("Upton Town Council, at-large", "Upton Council member")
    title = title.replace("CCSD #1 Trustee, Hulett", "CCSD #1 Hulett")
    title = title.replace("CCSD #1 Trustee, Moorcroft", "CCSD #1 Moorcroft")
    title = title.replace("CCSD #1 Trustee, Sundance", "CCSD #1 Sundance")
    title = title.replace("CCSD #1 Trustee, at-large", "CCSD #1 at-large")
    title = title.replace("CCMSD Trustee, at-large", "CCMSD at-large")
    title = title.replace("CCMSD Trustee, Hulett", "CCMSD Hulett")
    title = title.replace("CCMSD Trustee, Moorcroft", "CCMSD Moorcroft")
    title = title.replace("CCMSD Trustee, Sundance", "CCMSD Sundance")
    title = title.replace("Museum District Trustee", "Museum District")
    title = title.replace("CCSCSD Trustee", "Senior District")
    title = title.replace("CCNRD Rural", "CCNRD Rural")
    title = title.replace("CCNRD Urban", "CCNRD Urban")
    title = title.replace("CCNRD At-large", "CCNRD at-large")
    title = title.replace("Sundance Town Council", "Sundance Council member")
    title = title.replace("Moorcroft Town Council", "Moorcroft Council member")
    title = title.replace("Pine Haven Town Council", "Pine Haven Council member")
    title = title.replace("Hulett Town Council", "Hulett Council member")
    title = title.replace("Gillette Councilperson W1", "Gillette Council W1")
    title = title.replace("Gillette Councilperson W2", "Gillette Council W2")
    title = title.replace("Gillette Councilperson W3", "Gillette Council W3")
    title = title.replace("Gillette Councilperson Ward 1", "Gillette Council W1")
    title = title.replace("Gillette Councilperson Ward 3", "Gillette Council W3")
    title = title.replace("Wright Councilperson at-large", "Wright Council member")
    title = title.replace("Wright Councilperson At-large", "Wright Council member")
    title = title.replace("Wright Councilperson At Large", "Wright Council member")
    title = title.replace("Wright Town Council", "Wright Council member")
    title = title.replace("Campbell County School District", "Campbell School Board")
    title = title.replace("CCSD #1 Trustee", "Campbell School Board")
    title = title.replace("Gillette Community College District", "Gillette College Board")
    title = title.replace("Campbell County Cemetery District", "Cemetery District")
    title = title.replace("Campbell County Conservation District Rural", "Conservation Rural")
    title = title.replace("Campbell County Conservation District Urban", "Conservation Urban")
    title = title.replace("Campbell County Conservation District At-large", "Conservation at-large")
    title = title.replace("Campbell County Conservation District", "Conservation District")
    title = title.replace("Campbell County Hospital District", "Hospital District")
    title = title.replace("Senate District 23 (S23)", "Senate S23")
    title = title.replace("Senate District 24 (S24)", "Senate S24")
    title = title.replace("House District 3 (H03)", "House H03")
    title = title.replace("House District 31 (H31)", "House H31")
    title = title.replace("House District 32 (H32)", "House H32")
    title = title.replace("House District 52 (H52)", "House H52")
    title = title.replace("House District 53 (H53)", "House H53")
    title = title.replace("Senate District 21 (S21)", "Senate S21")
    title = title.replace("Senate District 22 (S22)", "Senate S22")
    title = title.replace("House District 29 (H29)", "House H29")
    title = title.replace("House District 30 (H30)", "House H30")
    title = title.replace("House District 40 (H40)", "House H40")
    title = title.replace("House District 51 (H51)", "House H51")
    title = title.replace("Sheridan City Councilmember at-large", "Sheridan City Council")
    title = title.replace("Sheridan Councilmember at-large", "Sheridan City Council")
    title = title.replace("Dayton Councilmember", "Dayton Council member")
    title = title.replace("Ranchester Councilmember", "Ranchester Council member")
    title = title.replace("Sheridan County School District No. 1", "School District 1")
    title = title.replace("Sheridan County School District No. 2", "School District 2")
    title = title.replace("Sheridan County School District No. 3", "School District 3")
    title = title.replace("Sheridan Community College District", "Sheridan College Board")
    title = title.replace("Northern Wyoming Community College District", "Sheridan College Board")
    title = title.replace("Sheridan County Conservation District", "Conservation District")
    title = title.replace("Sheridan County Senior Citizens Service District", "Senior Citizens District")
    title = title.replace("Senate District 18 (S18)", "Senate S18")
    title = title.replace("Senate District 19 (S19)", "Senate S19")
    title = title.replace("Senate District 20 (S20)", "Senate S20")
    title = title.replace("House District 27 (H27)", "House H27")
    title = title.replace("Worland Council Ward 1", "Worland Council W1")
    title = title.replace("Worland Council Ward 2", "Worland Council W2")
    title = title.replace("Worland Council Ward 3", "Worland Council W3")
    title = title.replace("Washakie County School District #1 Trustee", "School Dist. #1 Board")
    title = title.replace("Washakie County School District #2 Trustee", "School Dist. #2 Board")
    title = title.replace("Worland Fire Protection District Director", "Worland Fire Director")
    title = title.replace("Washakie County Conservation District Supervisor At-Large", "Conservation At-Large")
    title = title.replace("Washakie County Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Washakie County Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Ten Sleep Cemetery District Trustee", "Ten Sleep Cemetery")
    title = title.replace("Ten Sleep Fire Protection District Trustee", "Ten Sleep Fire Trustee")
    title = title.replace("House District 24 (H24)", "House H24")
    title = title.replace("House District 25 (H25)", "House H25")
    title = title.replace("House District 26 (H26)", "House H26")
    title = title.replace("House District 28 (H28)", "House H28")
    title = title.replace("House District 50 (H50)", "House H50")
    title = title.replace("Cody City Council Ward 1", "Cody Council W1")
    title = title.replace("Cody City Council Ward 2", "Cody Council W2")
    title = title.replace("Cody City Council Ward 3", "Cody Council W3")
    title = title.replace("Powell City Council Ward 1", "Powell Council W1")
    title = title.replace("Powell City Council Ward 2", "Powell Council W2")
    title = title.replace("Powell City Council Ward 3", "Powell Council W3")
    title = title.replace("Meeteetse Town Council", "Meeteetse Council")
    title = title.replace("Frannie Town Council", "Frannie Council")
    title = title.replace("Park County School District #1 Trustee", "School District 1")
    title = title.replace("Park County School District #6 Trustee", "School District 6")
    title = title.replace("Park County School District #16 Trustee (2-year)", "School District 16 (2-yr)")
    title = title.replace("Park County School District #16 Trustee", "School District 16")
    title = title.replace("Big Horn School District #1 Trustee Area A (Deaver/Frannie)", "BHSD #1 Area A")
    title = title.replace("Big Horn School District #1 Trustee Area E (At-Large)", "BHSD #1 Area E")
    title = title.replace("Northwest College Trustee Subdistrict A (Powell)", "NW College Subdist. A")
    title = title.replace("Northwest College Trustee Subdistrict B (Cody)", "NW College Subdist. B")
    title = title.replace("Northwest College Trustee Subdistrict C (Meeteetse)", "NW College Subdist. C")
    title = title.replace("Cody Fire District #2 Directors", "Cody Fire District")
    title = title.replace("Powell Fire District #1 Directors", "Powell Fire District")
    title = title.replace("Meeteetse Fire District #3 Directors", "Meeteetse Fire District")
    title = title.replace("Clark Fire District #4 Directors", "Clark Fire District")
    title = title.replace("Big Horn Fire District #5 Directors", "Big Horn Fire District")
    title = title.replace("Bennett Butte Cemetery District Trustees", "Bennett Butte Cemetery")
    title = title.replace("Crown Hill Cemetery District Trustees", "Crown Hill Cemetery")
    title = title.replace("Deaver-Frannie Cemetery District Trustees", "Deaver-Frannie Cemetery")
    title = title.replace("Meeteetse Cemetery District Trustees", "Meeteetse Cemetery")
    title = title.replace("Riverside Cemetery District Trustees", "Riverside Cemetery")
    title = title.replace("Cody Conservation District Supervisors", "Cody Conservation Dist.")
    title = title.replace("Meeteetse Conservation District Supervisors", "Meeteetse Conservation")
    title = title.replace("Powell Clarks Fork Conservation District Supervisors", "Powell Conservation Dist.")
    title = title.replace("Powell Hospital District Trustees", "Powell Hospital Dist.")
    title = title.replace("West Park Hospital District Trustees", "West Park Hospital Dist.")
    title = title.replace("Meeteetse Museum District Trustees", "Meeteetse Museum Dist.")
    title = title.replace("District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "District Judge, 5th JD (BH/HS/Wash.)")
    title = title.replace("District Judge, 5th Judicial District (Park)", "District Judge, 5th JD")
    title = title.replace("Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "Circuit Judge, 5th JD (BH/HS/Wash.)")
    title = title.replace("Circuit Judge, 5th Judicial District (Park)", "Circuit Judge, 5th JD")
    title = title.replace("County Commissioners", "Commissioner")
    title = title.replace("Senate District 1 (S01)", "Senate S01")
    title = title.replace("Senate District 3 (S03)", "Senate S03")
    title = title.replace("House District 1 (H01)", "House H01")
    title = title.replace("House District 2 (H02)", "House H02")
    title = title.replace("House District 5 (H05)", "House H05")
    title = title.replace("Justice of the Wyoming Supreme Court", "Supreme Court Justice")
    title = title.replace("District Judge, 6th Judicial District", "District Judge, 6th JD")
    title = title.replace("Circuit Judge, 6th Judicial District", "Circuit Judge, 6th JD")
    title = title.replace("Senate District 4 (S04)", "Senate S04")
    title = title.replace("Senate District 5 (S05)", "Senate S05")
    title = title.replace("Senate District 6 (S06)", "Senate S06")
    title = title.replace("Senate District 7 (S07)", "Senate S07")
    title = title.replace("Senate District 8 (S08)", "Senate S08")
    title = title.replace("Senate District 31 (S31)", "Senate S31")
    title = title.replace("House District 4 (H04)", "House H04")
    title = title.replace("House District 7 (H07)", "House H07")
    title = title.replace("House District 8 (H08)", "House H08")
    title = title.replace("House District 9 (H09)", "House H09")
    title = title.replace("House District 10 (H10)", "House H10")
    title = title.replace("House District 11 (H11)", "House H11")
    title = title.replace("House District 12 (H12)", "House H12")
    title = title.replace("House District 41 (H41)", "House H41")
    title = title.replace("House District 42 (H42)", "House H42")
    title = title.replace("House District 43 (H43)", "House H43")
    title = title.replace("House District 44 (H44)", "House H44")
    title = title.replace("House District 61 (H61)", "House H61")
    title = title.replace("Cheyenne City Council Ward 1", "Cheyenne Council W1")
    title = title.replace("Cheyenne City Council Ward 2", "Cheyenne Council W2")
    title = title.replace("Cheyenne City Council Ward 3", "Cheyenne Council W3")
    title = title.replace("Pine Bluffs Town Council", "Pine Bluffs Council")
    title = title.replace("Laramie County Community College Board of Trustees", "LCCC Board")
    title = title.replace("LCSD #1 Board Trustee At-Large", "LCSD #1 at-large")
    title = title.replace("LCSD #1 Board Trustee Area 1", "LCSD #1 Area 1")
    title = title.replace("LCSD #1 Board Trustee Area 2", "LCSD #1 Area 2")
    title = title.replace("LCSD #1 Board Trustee Area 3", "LCSD #1 Area 3")
    title = title.replace("LCSD #2 Board Trustee At-Large", "LCSD #2 at-large")
    title = title.replace("LCSD #2 Board Trustee Area C", "LCSD #2 Area C")
    title = title.replace("LCSD #2 Board Trustee Area D", "LCSD #2 Area D")
    title = title.replace("LCSD #2 Board Trustee Area E", "LCSD #2 Area E")
    title = title.replace("LCSD #2 Board Trustee Area F", "LCSD #2 Area F")
    title = title.replace("Laramie County Conservation District Supervisor At-Large", "Conservation at-large")
    title = title.replace("Laramie County Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Laramie County Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Laramie County Conservation District Rural Board Member (unexpired)", "Conservation Rural (unexp.)")
    title = title.replace("Chugwater Fire District Director", "Chugwater Fire District")
    title = title.replace("District Judge, 1st Judicial District", "District Judge, 1st JD")
    title = title.replace("Circuit Judge, 1st Judicial District", "Circuit Judge, 1st JD")
    title = title.replace("Senate District 2 (S02)", "Senate S02")
    title = title.replace("House District 6 (H06)", "House H06")
    title = title.replace("House District 4 (H04)", "House H04")
    title = title.replace("Senate District 27 (S27)", "Senate S27")
    title = title.replace("Senate District 28 (S28)", "Senate S28")
    title = title.replace("Senate District 29 (S29)", "Senate S29")
    title = title.replace("Senate District 30 (S30)", "Senate S30")
    title = title.replace("House District 35 (H35)", "House H35")
    title = title.replace("House District 36 (H36)", "House H36")
    title = title.replace("House District 37 (H37)", "House H37")
    title = title.replace("House District 38 (H38)", "House H38")
    title = title.replace("House District 56 (H56)", "House H56")
    title = title.replace("House District 57 (H57)", "House H57")
    title = title.replace("House District 58 (H58)", "House H58")
    title = title.replace("House District 59 (H59)", "House H59")
    title = title.replace("House District 62 (H62)", "House H62")
    title = title.replace("Casper City Council Ward 1", "Casper Council W1")
    title = title.replace("Casper City Council Ward 2", "Casper Council W2")
    title = title.replace("Casper City Council Ward 3", "Casper Council W3")
    title = title.replace("Mills Town Council", "Mills Council")
    title = title.replace("Evansville Town Council", "Evansville Council")
    title = title.replace("Bar Nunn Town Council", "Bar Nunn Council")
    title = title.replace("Casper College Board of Trustees", "Casper College Board")
    title = title.replace("NCSD #1 Board of Trustees", "NCSD #1 Board")
    title = title.replace("Conservation District Supervisor At-Large", "Conservation at-large")
    title = title.replace("Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Fire Protection District Director (unexpired)", "Fire District (unexp.)")
    title = title.replace("Fire Protection District Director", "Fire District Director")
    title = title.replace("Casper Mountain Fire District Director (unexpired)", "Casper Mtn Fire (unexp.)")
    title = title.replace("Casper Mountain Fire District Director", "Casper Mountain Fire")
    title = title.replace("Senior Citizens District Board of Trustees", "Senior Citizens Board")
    title = title.replace("District Judge, 7th Judicial District", "District Judge, 7th JD")
    title = title.replace("Circuit Judge, 7th Judicial District", "Circuit Judge, 7th JD")
    title = title.replace("District Attorney", "District Attorney")
    title = title.replace("Clerk of District Court", "Clerk of Dist. Court")
    title = title.replace("Senate District 9 (S09)", "Senate S09")
    title = title.replace("Senate District 10 (S10)", "Senate S10")
    title = title.replace("Senate District 11 (S11)", "Senate S11")
    title = title.replace("House District 13 (H13)", "House H13")
    title = title.replace("House District 14 (H14)", "House H14")
    title = title.replace("House District 45 (H45)", "House H45")
    title = title.replace("House District 46 (H46)", "House H46")
    title = title.replace("House District 47 (H47)", "House H47")
    title = title.replace("Laramie City Council Ward 1", "Laramie Council W1")
    title = title.replace("Laramie City Council Ward 2", "Laramie Council W2")
    title = title.replace("Laramie City Council Ward 3", "Laramie Council W3")
    title = title.replace("ACSD #1 Trustee At-Large", "ACSD #1 at-large")
    title = title.replace("ACSD #1 Trustee Area A", "ACSD #1 Area A")
    title = title.replace("ACSD #1 Trustee Area B", "ACSD #1 Area B")
    title = title.replace("ACSD #1 Trustee", "ACSD #1 Trustee")
    title = title.replace("Laramie Rivers Conservation District Supervisor At-Large", "Conservation at-large")
    title = title.replace("Laramie Rivers Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Laramie Rivers Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Laramie Rivers Conservation District Supervisor", "Conservation Supervisor")
    title = title.replace("Fire District No. 1 Director", "Fire District Director")
    title = title.replace("Hospital District Trustee", "Hospital District Trustee")
    title = title.replace("District Judge, 2nd Judicial District", "District Judge, 2nd JD")
    title = title.replace("Circuit Judge, 2nd Judicial District", "Circuit Judge, 2nd JD")
    title = title.replace("County Attorney", "County Attorney")
    title = title.replace("Senate District 12 (S12)", "Senate S12")
    title = title.replace("Senate District 13 (S13)", "Senate S13")
    title = title.replace("Senate District 14 (S14)", "Senate S14")
    title = title.replace("House District 15 (H15)", "House H15")
    title = title.replace("House District 17 (H17)", "House H17")
    title = title.replace("House District 18 (H18)", "House H18")
    title = title.replace("House District 39 (H39)", "House H39")
    title = title.replace("House District 48 (H48)", "House H48")
    title = title.replace("House District 60 (H60)", "House H60")
    title = title.replace("Green River City Council Ward 1", "Green River Council W1")
    title = title.replace("Green River City Council Ward 2", "Green River Council W2")
    title = title.replace("Green River City Council Ward 3", "Green River Council W3")
    title = title.replace("Rock Springs City Council Ward 1", "Rock Springs Council W1")
    title = title.replace("Rock Springs City Council Ward 2", "Rock Springs Council W2")
    title = title.replace("Rock Springs City Council Ward 3", "Rock Springs Council W3")
    title = title.replace("Rock Springs City Council Ward 4", "Rock Springs Council W4")
    title = title.replace("Granger Town Council", "Granger Council")
    title = title.replace("Wamsutter Town Council", "Wamsutter Council")
    title = title.replace("Superior Town Council", "Superior Council")
    title = title.replace("Western Wyoming College Trustee At-Large", "WWCC at-large")
    title = title.replace("Western Wyoming College Trustee District #1", "WWCC District #1")
    title = title.replace("Western Wyoming College Trustee District #2", "WWCC District #2")
    title = title.replace("Western Wyoming College Trustee", "WWCC Trustee")
    title = title.replace("Western Wyoming School District #1 Trustee", "WWSD #1 Trustee")
    title = title.replace("SWSD #1 Trustee Rock Springs Area", "SWSD #1 Rock Springs")
    title = title.replace("SWSD #1 Trustee Farson Area", "SWSD #1 Farson")
    title = title.replace("SWSD #2 Trustee", "SWSD #2 Trustee")
    title = title.replace("Castle Rock Hospital District Trustee", "Castle Rock Hospital")
    title = title.replace("Sweetwater County Conservation District Supervisor At-Large", "Conservation at-large")
    title = title.replace("Sweetwater County Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Sweetwater County Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Sweetwater County Conservation District Supervisor", "Conservation Supervisor")
    title = title.replace("Sweetwater County Fire District #1 Director", "Fire District #1")
    title = title.replace("District Judge, 3rd Judicial District", "District Judge, 3rd JD")
    title = title.replace("Circuit Judge, 3rd Judicial District", "Circuit Judge, 3rd JD")
    title = title.replace("Senate District 16 (S16)", "Senate S16")
    title = title.replace("Senate District 17 (S17)", "Senate S17")
    title = title.replace("House District 16 (H16)", "House H16")
    title = title.replace("House District 22 (H22)", "House H22")
    title = title.replace("House District 23 (H23)", "House H23")
    title = title.replace("Jackson Town Council", "Jackson Council")
    title = title.replace("Jackson Mayor", "Jackson Mayor")
    title = title.replace("TCSD #1 Trustee", "TCSD #1 Trustee")
    title = title.replace("St. John's Hospital District Trustee (2-year unexpired)", "St. John's Hospital (unexp.)")
    title = title.replace("St. John's Hospital District Trustee", "St. John's Hospital")
    title = title.replace("Teton Conservation District Supervisor At-Large", "Conservation at-large")
    title = title.replace("Teton Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Teton Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Teton Conservation District Supervisor", "Conservation Supervisor")
    title = title.replace("District Judge, 9th Judicial District", "District Judge, 9th JD")
    title = title.replace("Circuit Judge, 9th Judicial District", "Circuit Judge, 9th JD")
    title = title.replace("County Attorney", "County Attorney")
    title = title.replace("Senate District 14 (S14)", "Senate S14")
    title = title.replace("House District 18 (H18)", "House H18")
    title = title.replace("House District 20 (H20)", "House H20")
    title = title.replace("House District 21 (H21)", "House H21")
    title = title.replace("Kemmerer Mayor", "Kemmerer Mayor")
    title = title.replace("Star Valley Ranch Mayor", "Star Valley Ranch Mayor")
    title = title.replace("Diamondville Mayor", "Diamondville Mayor")
    title = title.replace("Cokeville Mayor", "Cokeville Mayor")
    title = title.replace("LaBarge Mayor", "LaBarge Mayor")
    title = title.replace("LCSD #1 Trustee", "LCSD #1 Trustee")
    title = title.replace("LCSD #2 Trustee At-Large", "LCSD #2 at-large")
    title = title.replace("LCSD #2 Trustee Area 1", "LCSD #2 Area 1")
    title = title.replace("LCSD #2 Trustee Area 2", "LCSD #2 Area 2")
    title = title.replace("LCSD #2 Trustee Area 3", "LCSD #2 Area 3")
    title = title.replace("LCSD #2 Trustee Area 4", "LCSD #2 Area 4")
    title = title.replace("LCSD #2 Trustee Area 5", "LCSD #2 Area 5")
    title = title.replace("District Judge, 3rd Judicial District", "District Judge, 3rd JD")
    title = title.replace("Circuit Judge, 3rd Judicial District", "Circuit Judge, 3rd JD")
    title = title.replace("Kemmerer Council", "Kemmerer Council")
    title = title.replace("Diamondville Council (4-year)", "Diamondville Council 4yr")
    title = title.replace("Diamondville Council (2-year)", "Diamondville Council 2yr")
    title = title.replace("Opal Council (4-year)", "Opal Council 4yr")
    title = title.replace("Opal Council (2-year)", "Opal Council 2yr")
    title = title.replace("LaBarge Council (4-year)", "LaBarge Council 4yr")
    title = title.replace("Afton Council (4-year)", "Afton Council 4yr")
    title = title.replace("Afton Council (2-year)", "Afton Council 2yr")
    title = title.replace("Alpine Council (4-year)", "Alpine Council 4yr")
    title = title.replace("Thayne Council (4-year)", "Thayne Council 4yr")
    title = title.replace("Thayne Council (2-year unexpired)", "Thayne Council 2yr unexp.")
    title = title.replace("Thayne Council (2-year)", "Thayne Council 2yr")
    title = title.replace("Cokeville Council (4-year)", "Cokeville Council 4yr")
    title = title.replace("Star Valley Ranch Council (4-year)", "Star Valley Ranch Council 4yr")
    title = title.replace("Sublette CSD #9 Trustee 2-year (Lincoln portion)", "Sublette #9 2yr (Lincoln)")
    title = title.replace("Sublette CSD #9 Trustee (Lincoln portion)", "Sublette #9 (Lincoln)")
    title = title.replace("South Lincoln Hospital Trustee", "South Lincoln Hospital")
    title = title.replace("North Lincoln Hospital Trustee", "North Lincoln Hospital")
    title = title.replace("Cokeville Hospital Trustee", "Cokeville Hospital")
    title = title.replace("Lincoln Conservation District Rural Supervisor", "Lincoln Cons. Rural")
    title = title.replace("Lincoln Conservation District Urban Supervisor", "Lincoln Cons. Urban")
    title = title.replace("Lincoln Conservation District At-Large Supervisor", "Lincoln Cons. at-large")
    title = title.replace("Star Valley Conservation District At-Large Supervisor", "SV Cons. at-large")
    title = title.replace("Star Valley Conservation District Rural Supervisor", "SV Cons. Rural")
    title = title.replace("Star Valley Conservation District Urban Supervisor", "SV Cons. Urban")
    title = title.replace("South Lincoln Cemetery Director (4-year)", "So. Lincoln Cemetery 4yr")
    title = title.replace("South Lincoln Cemetery Director (2-year)", "So. Lincoln Cemetery 2yr")
    title = title.replace("South Lincoln Cemetery Director", "So. Lincoln Cemetery")
    title = title.replace("Cokeville Cemetery Director (2-year unexpired)", "Cokeville Cemetery 2yr unexp.")
    title = title.replace("Cokeville Cemetery Director (4-year)", "Cokeville Cemetery 4yr")
    title = title.replace("Cokeville Cemetery Director (2-year)", "Cokeville Cemetery 2yr")
    title = title.replace("South Lincoln Fire Director", "South Lincoln Fire")
    title = title.replace("Upper Valley Fire Director", "Upper Valley Fire")
    title = title.replace("Mid-Valley Fire Director (4-year)", "Mid-Valley Fire 4yr")
    title = title.replace("Mid-Valley Fire Director (2-year)", "Mid-Valley Fire 2yr")
    title = title.replace("Mid-Valley Fire Director", "Mid-Valley Fire")
    title = title.replace("Alpine Fire Director (2-year)", "Alpine Fire 2yr")
    title = title.replace("Alpine Fire Director (4-year)", "Alpine Fire 4yr")
    title = title.replace("Bear River Fire Director (2-year unexpired)", "Bear River Fire 2yr unexp.")
    title = title.replace("Bear River Fire Director", "Bear River Fire")
    title = title.replace("Kemmerer Senior Citizens District Trustee", "Kemmerer Senior Dist.")
    title = title.replace("Senate District 15 (S15)", "Senate S15")
    title = title.replace("House District 19 (H19)", "House H19")
    title = title.replace("House District 49 (H49)", "House H49")
    title = title.replace("Evanston City Council Ward 1", "Evanston Council Ward 1")
    title = title.replace("Evanston City Council Ward 2", "Evanston Council Ward 2")
    title = title.replace("Evanston City Council Ward 3", "Evanston Council Ward 3")
    title = title.replace("Mountain View Town Council", "Mountain View Council")
    title = title.replace("Bear River Town Council", "Bear River Council")
    title = title.replace("Lyman Town Council", "Lyman Council")
    title = title.replace("UCSD #1 Trustee", "UCSD #1 Trustee")
    title = title.replace("UCSD #4 Trustee", "UCSD #4 Trustee")
    title = title.replace("UCSD #6 Trustee", "UCSD #6 Trustee")
    title = title.replace("Uinta Conservation District Rural Supervisor", "Uinta Cons. Rural")
    title = title.replace("Uinta Conservation District Urban Supervisor", "Uinta Cons. Urban")
    title = title.replace("Uinta Conservation District At-Large Supervisor", "Uinta Cons. at-large")
    title = title.replace("Uinta County Rural Fire District Director", "Uinta Rural Fire")
    title = title.replace("Baggs Mayor", "Baggs Mayor")
    title = title.replace("Baggs Council", "Baggs Council")
    title = title.replace("Dixon Mayor", "Dixon Mayor")
    title = title.replace("Dixon Council", "Dixon Council")
    title = title.replace("Elk Mountain Mayor", "Elk Mountain Mayor")
    title = title.replace("Elk Mountain Council", "Elk Mountain Council")
    title = title.replace("Encampment Mayor", "Encampment Mayor")
    title = title.replace("Encampment Council", "Encampment Council")
    title = title.replace("Hanna Mayor", "Hanna Mayor")
    title = title.replace("Hanna Council", "Hanna Council")
    title = title.replace("Medicine Bow Mayor", "Medicine Bow Mayor")
    title = title.replace("Medicine Bow Council", "Medicine Bow Council")
    title = title.replace("Rawlins Mayor", "Rawlins Mayor")
    title = title.replace("Rawlins City Council Ward 1", "Rawlins Council W1")
    title = title.replace("Rawlins City Council Ward 2", "Rawlins Council W2")
    title = title.replace("Rawlins City Council Ward 3", "Rawlins Council W3")
    title = title.replace("Rawlins City Council At-Large", "Rawlins Council At-Large")
    title = title.replace("Riverside Mayor", "Riverside Mayor")
    title = title.replace("Riverside Council", "Riverside Council")
    title = title.replace("Saratoga Mayor", "Saratoga Mayor")
    title = title.replace("Saratoga Council", "Saratoga Council")
    title = title.replace("Sinclair Mayor", "Sinclair Mayor")
    title = title.replace("Sinclair Council", "Sinclair Council")
    title = title.replace("Goshen County School District #1 Trustee", "GCSD #1 Trustee")
    title = title.replace("Eastern Wyoming College Trustee", "EWC Trustee")
    title = title.replace("Lingle-Fort Laramie Conservation District At-Large Supervisor", "LFL Conservation at-large")
    title = title.replace("Lingle-Fort Laramie Conservation District Rural Supervisor", "LFL Conservation rural")
    title = title.replace("Lingle-Fort Laramie Conservation District Urban Supervisor", "LFL Conservation urban")
    title = title.replace("North Platte Valley Conservation District At-Large Supervisor", "NPV Conservation at-large")
    title = title.replace("North Platte Valley Conservation District Rural Supervisor", "NPV Conservation rural")
    title = title.replace("North Platte Valley Conservation District Urban Supervisor", "NPV Conservation urban")
    title = title.replace("South Goshen Conservation District At-Large Supervisor", "South Goshen Cons. at-large")
    title = title.replace("South Goshen Conservation District Rural Supervisor", "South Goshen Cons. rural")
    title = title.replace("South Goshen Conservation District Urban Supervisor", "South Goshen Cons. urban")
    title = title.replace("Senior Citizen Service District Trustee", "Senior District")
    title = title.replace("Chugwater Cemetery District Director", "Chugwater Cemetery")
    title = title.replace("Chugwater Fire District Director", "Chugwater Fire Dist.")
    title = title.replace("Torrington Council", "Torrington Council member")
    title = title.replace("Lingle Council", "Lingle Council member")
    title = title.replace("Fort Laramie Council", "Fort Laramie Council member")
    title = title.replace("La Grange Council", "La Grange Council member")
    title = title.replace("Converse County School District #1 Trustee", "CCSD #1 Trustee")
    title = title.replace("Converse County School District #2 Trustee", "CCSD #2 Trustee")
    title = title.replace("Conservation District At-Large Supervisor", "Conservation at-large")
    title = title.replace("Conservation District Urban Supervisor, 2-year", "Conservation urban 2yr")
    title = title.replace("Conservation District Urban Supervisor", "Conservation urban")
    title = title.replace("Conservation District Rural Supervisor", "Conservation rural")
    title = title.replace("Senior Citizens Service District Trustee", "Senior District")
    title = title.replace("Cemetery District Trustee", "Cemetery District")
    title = title.replace("Hospital District Trustee, 2-year", "Hospital District 2yr")
    title = title.replace("Hospital District Trustee", "Hospital District")
    title = title.replace("Sundance Meadows Special Improvement District Trustee", "Sundance Meadows Dist.")
    title = title.replace("District Judge, 8th Judicial District", "District Judge, 8th JD")
    title = title.replace("Circuit Judge, 8th Judicial District", "Circuit Judge, 8th JD")
    title = title.replace("Town of Lusk Mayor", "Lusk Mayor")
    title = title.replace("Town of Lusk Council", "Lusk Council")
    title = title.replace("Town of Manville Mayor", "Manville Mayor")
    title = title.replace("Town of Manville Council", "Manville Council")
    title = title.replace("City of Buffalo Mayor", "Buffalo Mayor")
    title = title.replace("City of Buffalo Council", "Buffalo Council")
    title = title.replace("Town of Kaycee Mayor", "Kaycee Mayor")
    title = title.replace("Town of Kaycee Council", "Kaycee Council")
    title = title.replace("Johnson County School District #1 Trustee", "JCSD #1 Trustee")
    title = title.replace("Johnson County Hospital Board Trustee", "Hospital Board Trustee")
    title = title.replace("Johnson County Fire District #1 Director", "Fire District #1 Director")
    title = title.replace("Clear Creek Conservation District Supervisor", "Conservation Supervisor")
    title = title.replace("Johnson County Senior Citizen Service District Trustee", "Senior Citizens Trustee")
    title = title.replace("District Judge, 4th Judicial District", "District Judge, 4th JD")
    title = title.replace("Circuit Judge, 4th Judicial District", "Circuit Judge, 4th JD")
    title = title.replace("Cemetery District Trustee", "Cemetery District")
    title = title.replace("Clear Creek Conservation District Rural", "Clear Creek Conserv. Rural")
    title = title.replace("Clear Creek Conservation District At Large", "Clear Creek Conserv. At-Large")
    title = title.replace("Clear Creek Conservation District Urban", "Clear Creek Conserv. Urban")
    title = title.replace("Powder River Conservation District Rural", "Powder River Conserv. Rural")
    title = title.replace("Powder River Conservation District At Large", "Powder River Conserv. At-Large")
    title = title.replace("Powder River Conservation District Urban", "Powder River Conserv. Urban")
    title = title.replace("Johnson County Fire District #1 Trustee", "Fire Dist. #1 Trustee")
    title = title.replace("Powder River Fire District Trustee", "Powder River Fire Trustee")
    title = title.replace("Hospital District Trustee", "Hospital District")
    title = title.replace("Rural Health Care District Trustee", "Rural Health Care Trustee")
    title = title.replace("Senior Citizen Service District Trustee", "Senior Citizens Trustee")
    title = title.replace("Town of Van Tassell Mayor", "Van Tassell Mayor")
    title = title.replace("Town of Van Tassell Council", "Van Tassell Council")
    title = title.replace("Niobrara County School District #1 Trustee", "NCSD #1 Trustee")
    title = title.replace("Niobrara County Hospital District Trustee", "Hospital District Trustee")
    title = title.replace("Niobrara County Conservation District Supervisor At-Large", "Conservation At-Large")
    title = title.replace("Niobrara County Conservation District Supervisor Rural", "Conservation Rural")
    title = title.replace("Niobrara County Conservation District Supervisor Urban", "Conservation Urban")
    title = title.replace("Niobrara County Rural Fire District Director", "Rural Fire Director")
    title = title.replace("Niobrara County Senior Citizens Service District Trustee", "Senior Citizens Trustee")
    title = title.replace("Douglas Council", "Douglas Council member")
    title = title.replace("Glenrock Council", "Glenrock Council member")
    title = title.replace("Rolling Hills Council", "Rolling Hills Council member")
    title = title.replace("Lost Springs Council", "Lost Springs Council member")
    title = title.replace("Carbon County School District #1 Trustee", "CCSD #1 Trustee")
    title = title.replace("Carbon County School District #2 Area 1 Trustee", "CCSD #2 Area 1")
    title = title.replace("Carbon County School District #2 Area 2 Trustee", "CCSD #2 Area 2")
    title = title.replace("Carbon County School District #2 Area 3 Trustee", "CCSD #2 Area 3")
    title = title.replace("Carbon County School District #2 Area 4 Trustee", "CCSD #2 Area 4")
    title = title.replace("Little Snake River Conservation District Rural Supervisor", "LSR Cons. Rural")
    title = title.replace("Little Snake River Conservation District Urban Supervisor", "LSR Cons. Urban")
    title = title.replace("Little Snake River Conservation District At-Large Supervisor", "LSR Cons. at-large")
    title = title.replace("Medicine Bow Conservation District Rural Supervisor", "Med. Bow Cons. Rural")
    title = title.replace("Medicine Bow Conservation District Urban Supervisor", "Med. Bow Cons. Urban")
    title = title.replace("Medicine Bow Conservation District At-Large Supervisor", "Med. Bow Cons. at-large")
    title = title.replace("Saratoga-Encampment-Rawlins Conservation District Rural Supervisor", "SER Cons. Rural")
    title = title.replace("Saratoga-Encampment-Rawlins Conservation District Urban Supervisor", "SER Cons. Urban")
    title = title.replace("Saratoga-Encampment-Rawlins Conservation District At-Large Supervisor", "SER Cons. at-large")
    title = title.replace("Baggs Cemetery District Trustee", "Baggs Cemetery")
    title = title.replace("Reader Cemetery District Trustee", "Reader Cemetery")
    title = title.replace("Saratoga Cemetery District Trustee", "Saratoga Cemetery")
    title = title.replace("Little Snake River Museum District Trustee", "LSR Museum")
    title = title.replace("Saratoga-Ryan Park Museum District Trustee", "Saratoga-Ryan Park Museum")
    title = title.replace("Little Snake River Rural Health Care District Trustee", "LSR Rural Health")
    title = title.replace("Medicine Bow Rural Health Care District Trustee", "Med. Bow Rural Health")
    title = title.replace("Carbon County Fire Protection District Director", "Carbon Fire Protection")
    return title


def role_label(role: str | None) -> str:
    """Short role for the name column, e.g. Chairman -> Chair."""
    if not role:
        return ""
    raw = role.strip()
    return {
        "chairman": "Chair",
        "board chair": "Chair",
        "board chairman": "Chair",
        "vice chair": "Vice Chair",
        "vice-chair": "Vice Chair",
        "vice chairman": "Vice Chair",
        "board vice-chair": "Vice Chair",
        "board vice chair": "Vice Chair",
        "board vice-chairman": "Vice Chair",
    }.get(raw.lower(), raw)


def name_cell(holder: dict) -> str:
    name = holder.get("name") or "Not yet collected"
    role = role_label(holder.get("role"))
    if role:
        name = f"{name} ({role})"
    bits = [esc(name)]
    r = holder.get("retention") or {}
    if r:
        pct = r.get("yes_pct") or ""
        year = r.get("year") or ""
        extra = f"retained {year}" if year else "retained"
        if pct:
            extra += f", {pct} Yes"
        bits.append(f"<i>{esc(extra)}</i>")
    nxt = holder.get("succeeding")
    if nxt and nxt.get("name"):
        bits.append(f"in January: {esc(nxt['name'])}")
    return "<br/>".join(bits)


class ProfileMark(Flowable):
    def __init__(self, key: str):
        super().__init__()
        self.profile_key = key
        self.width = 0
        self.height = 0

    def draw(self):
        return


class ReportDoc(BaseDocTemplate):
    def __init__(self, *a, pages_map=None, **k):
        super().__init__(*a, **k)
        self.pages_map = pages_map if pages_map is not None else {}

    def afterFlowable(self, flowable):
        key = getattr(flowable, "profile_key", None)
        if key and key not in self.pages_map:
            self.pages_map[key] = self.page


def section_table(title, rows, cols=None, headers=None, office_groups=None):
    """If office_groups is a list of [start, end] row indices (0-based, not
    counting the header), the office cell is spanned so each office appears once."""
    cols = cols or COLS
    headers = headers or HEADERS
    data = [[Paragraph(h, cellbc if i else cellb) for i, h in enumerate(headers)]] + rows
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.6, GRID),
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    if office_groups:
        for i, (a, b) in enumerate(office_groups):
            bg = white if i % 2 == 0 else ZEBRA
            cmds.append(("BACKGROUND", (0, a + 1), (-1, b + 1), bg))
            if a != b:
                cmds.append(("SPAN", (0, a + 1), (0, b + 1)))
    else:
        cmds.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ZEBRA]))
    t = Table(data, colWidths=cols, repeatRows=1)
    t.setStyle(TableStyle(cmds))
    return [Paragraph(title, h2), t]


def row_cells(office, name, pty, term, rank):
    return [
        Paragraph(office, cell),
        Paragraph(name, cell),
        Paragraph(pty, cellc),
        Paragraph(term, cellc),
        Paragraph(str(rank), cellc),
    ]


# ---------- data walk ----------

def iter_groups(county: dict, federal: dict, judicial: dict):
    items = []
    for g in (federal or {}).get("groups") or []:
        items.append(g)
    for g in county.get("groups") or []:
        if g["id"] == "judicial":
            # Statewide judicial first (J1, J2), then the county district/circuit group.
            for sg in (judicial or {}).get("groups") or []:
                items.append(sg)
        items.append(g)
    # If the county has no judicial group, still include statewide judicial at the end of elected offices, before precincts.
    if not any(g.get("id") == "judicial" for g in county.get("groups") or []):
        for sg in (judicial or {}).get("groups") or []:
            items.append(sg)
    items.sort(key=lambda g: g.get("sort_key") or GROUP_ORDER.get(g.get("id"), "Z"))
    return items


def ranks_index():
    """full_name -> {year: (rank_all, n_ranked, band, chamber_rank, chamber, district)}"""
    out = {}
    bands = {}
    for year in range(2008, 2027):
        try:
            d = ranking.load(year)
        except Exception:
            continue
        bands[year] = bands_from_ranking(d)
        for r in d["ranked"]:
            name = r.get("full_name") or r.get("legislator")
            if not name:
                continue
            out.setdefault(name, {})[year] = (
                r["rank_all"], d["n_ranked"], r.get("band"), r.get("rank_ch"),
                r.get("chamber"), r.get("district"),
            )
    return out, bands


RANKS, BANDS = ranks_index()


def latest_rank(name: str, district: str | None = None) -> str:
    rec = RANKS.get(name) or {}
    if not rec:
        return "—"
    year = max(rec)
    rank, n, band, rch, ch, dist = rec[year]
    if year != 2026:
        return "—"
    if district:
        want = district.upper().replace("SENATE DISTRICT ", "S").replace("HOUSE DISTRICT ", "H")
        want = re.sub(r"[()]", "", want)
        # accept S01 or 1
        if dist and want and want not in {str(dist).upper(), "S" + str(dist).upper().lstrip("S"), "H" + str(dist).upper().lstrip("H")}:
            # still allow if name is unique
            if name in ("JD Williams",) and str(dist).upper() not in {"H02", "2"}:
                return "—"
    return str(rank)


def district_from_office(title: str) -> str | None:
    m = re.search(r"\b([SH]\d{2})\b", title)
    return m.group(1) if m else None


def load_county_bundle(site: Path, slug: str, year: int | None = None):
    """Load the live county file, or a frozen January snapshot when year is set."""
    if year:
        hist = site / "data/county_officials/history" / slug / f"{year}.json"
        if not hist.is_file():
            raise SystemExit(f"No January {year} snapshot at {hist}")
        snap = load_json(hist)
        # Snapshot already contains federal, statewide, and judicial groups.
        return snap, {}, {}
    county = load_json(site / "data/county_officials" / f"{slug}.json")
    federal = load_json(site / "data/county_officials/shared/federal-statewide.json")
    jpath = site / "data/county_officials/shared/judicial-statewide.json"
    judicial = load_json(jpath) if jpath.is_file() else {}
    return county, federal, judicial


def walk_holders(groups):
    """Yield (group, office_title, holder) in report order, then succeeding elects."""
    for g in groups:
        offices = list(g.get("offices") or [])
        for o in offices:
            for h in o.get("holders") or []:
                yield g, o.get("office") or "", h
                if h.get("succeeding") and h["succeeding"].get("name"):
                    yield g, o.get("office") or "", {**h["succeeding"], "_elect": True}


def build_summary_and_people(groups):
    """Build summary section rows and the unique-person list for Part 2."""
    sections = []  # (title, rows_spec, notes)
    people = []    # unique, in first-seen order
    seen = set()
    bucket = None
    current_rows = None
    current_notes = []

    def flush():
        nonlocal bucket, current_rows, current_notes
        if bucket is not None:
            sections.append((bucket, current_rows, current_notes))
        bucket, current_rows, current_notes = None, None, []

    def bucket_title(g):
        gid = g.get("id")
        if gid in {"federal", "statewide"}:
            return "Federal and statewide"
        if gid in {"state-senate", "state-house"}:
            return "Legislature"
        if gid == "county":
            return "County offices"
        if gid in {"municipal", "schools", "special-districts"}:
            return "Municipal, schools, and special districts"
        if gid in {"supreme-court", "chancery-court", "judicial"}:
            return "Judicial retention"
        if gid == "precincts":
            return "Precincts"
        return g.get("title") or gid

    # Non-precinct first (skip the precincts group even when its list is empty)
    for g in groups:
        if g.get("id") == "precincts" or g.get("precincts"):
            continue
        title = bucket_title(g)
        if title != bucket:
            flush()
            bucket = title
            current_rows = []
        if g.get("note"):
            current_notes.append(g["note"])
        for o in g.get("offices") or []:
            if o.get("note"):
                current_notes.append(o["note"])
            holders = o.get("holders") or []
            if not holders and not g.get("offices"):
                continue
            for h in holders:
                key = person_key(h)
                if key and key not in seen:
                    seen.add(key)
                    people.append({**h, "_offices": [o.get("office") or ""]})
                elif key:
                    for pe in people:
                        if person_key(pe)==key:
                            pe.setdefault("_offices", []).append(o.get("office") or "")
                            break
                nxt = h.get("succeeding")
                if nxt and nxt.get("name"):
                    nk = person_key(nxt)
                    if nk and nk not in seen:
                        seen.add(nk)
                        people.append({**nxt, "_elect": True, "_offices": [o.get("office") or ""]})
                    elif nk:
                        for pe in people:
                            if person_key(pe)==nk:
                                pe.setdefault("_offices", []).append(o.get("office") or "")
                                break
                office = office_label(o.get("office") or "", h)
                # Rank only for legislative offices (and not for elects who have not yet served, unless they have a 2026 rank under this name).
                dist = district_from_office(o.get("office") or "")
                rank = latest_rank(h.get("name") or "", dist) if dist else "—"
                term = short_term(h.get("term_end"))
                current_rows.append({
                    "office": office, "name_html": name_cell(h), "pty": pty_of(h),
                    "term": term, "rank": rank, "key": key,
                    "elect_key": person_key(nxt) if nxt and nxt.get("name") else "",
                })
    flush()

    # Precinct compact table (include the group when it only has a “not yet collected” note)
    for g in groups:
        if g.get("id") != "precincts" and not g.get("precincts"):
            continue
        rows = []
        notes = [g["note"]] if g.get("note") else []
        for prec in g["precincts"]:
            men, women = [], []
            for o in prec.get("offices") or []:
                title = (o.get("office") or "").lower()
                target = women if "women" in title or "committeewoman" in title else men
                for h in o.get("holders") or []:
                    key = person_key(h)
                    if key and key not in seen:
                        seen.add(key)
                        people.append({**h, "_precinct": True, "_precinct_name": prec.get("name"),
                                       "_offices": [prec.get("name") or "Precinct"]})
                    elif key and key in seen:
                        for pe in people:
                            if person_key(pe)==key:
                                pe.setdefault("_offices", []).append(prec.get("name") or "Precinct")
                                break
                    target.append((h.get("name") or "", key))
            rows.append({
                "precinct": prec.get("name") or prec.get("id"),
                "men": men, "women": women,
            })
        sections.append(("Precincts", rows, notes))
    return sections, people


# ---------- Profile extraction ----------

def parse_html_profile(path: Path) -> dict:
    out = {"research": [], "results": [], "sources": [], "subtitle": "", "blurb": ""}
    if not path or not path.is_file():
        return out
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    sub = soup.select_one(".pf-sub")
    if sub:
        out["subtitle"] = sub.get_text(" ", strip=True)
    blurb = soup.select_one(".cand-blurb")
    if blurb:
        out["blurb"] = blurb.get_text(" ", strip=True)

    def table_after(hid):
        h = soup.find(id=hid)
        if not h:
            return []
        sec = h.find_parent("section") or h.parent
        rows = []
        for tr in (sec.find_all("tr") if sec else []):
            th, td = tr.find("th"), tr.find("td")
            if th and td:
                k = th.get_text(" ", strip=True)
                v = td.get_text(" ", strip=True)
                if k and v:
                    rows.append((k, v))
        return rows

    out["research"] = table_after("h-research")
    out["results"] = table_after("h-results")
    sources = []
    for hid in ("h-sources", "h-results-sources"):
        h = soup.find(id=hid)
        if not h:
            continue
        block = h.find_parent("div") or h.parent
        for a in block.find_all("a"):
            lab = a.get_text(" ", strip=True)
            href = a.get("href") or ""
            if lab:
                sources.append((lab, href))
    # unique preserve order
    seen = set()
    uniq = []
    for lab, href in sources:
        if (lab, href) not in seen:
            seen.add((lab, href))
            uniq.append((lab, href))
    out["sources"] = uniq
    return out


def standing_research(site: Path, pid: str) -> tuple[list, list]:
    path = site / "data/candidate-research/standing" / f"{pid}.json"
    if not path.is_file():
        return [], []
    d = json.loads(path.read_text(encoding="utf-8"))
    fields = []
    for key, label in (
        ("residence", "Residence"), ("occupation", "Occupation"),
        ("education", "Education"), ("military", "Military"),
        ("prior_offices", "Prior offices"),
    ):
        v = d.get(key)
        if v:
            fields.append((label, v if isinstance(v, str) else "; ".join(v)))
    bg = d.get("background")
    if bg:
        text = " ".join(bg) if isinstance(bg, list) else str(bg)
        # Keep this short: first two sentences.
        parts = re.split(r"(?<=\.)\s+", text.strip())
        fields.append(("Background", " ".join(parts[:2])))
    sources = []
    for s in d.get("sources") or []:
        if isinstance(s, dict):
            sources.append((s.get("name") or s.get("label") or s.get("url") or "", s.get("url") or ""))
        elif s:
            sources.append((str(s), ""))
    return fields, sources


def rank_series(name: str):
    rec = RANKS.get(name) or {}
    if len(rec) < 2:
        return None, None
    years = sorted(rec)
    lo, hi = years[0], years[-1]
    series = []
    bands = {}
    for y in range(lo, hi + 1):
        if y in rec:
            rank, n, band, *_ = rec[y]
            series.append((y, rank, n, band))
            bands[y] = BANDS[y]
        else:
            series.append((y, None, None, None))
            if y in BANDS:
                bands[y] = BANDS[y]
    ranked_years = [s for s in series if s[1] is not None]
    if len(ranked_years) < 2:
        return None, None
    return series, bands


def make_rank_png(name: str, tmp: Path) -> Path | None:
    series, bands = rank_series(name)
    if not series:
        return None
    svg = chart_svg(name, series, bands)
    out = tmp / (re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") + "-rank.png")
    try:
        import pymupdf
        from PIL import Image as PILImage
        import io
        doc = pymupdf.open(stream=svg.encode("utf-8"), filetype="svg")
        pix = doc[0].get_pixmap(dpi=160, alpha=False)
        pix.save(str(out))
        doc.close()
        # Flatten any leftover transparency onto white.
        im = PILImage.open(out)
        if im.mode == "RGBA":
            bg = PILImage.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            bg.save(out)
        return out if out.is_file() and out.stat().st_size > 1000 else None
    except Exception:
        return None


def resolve_href(site: Path, href: str | None) -> Path | None:
    if not href:
        return None
    p = site / href
    return p if p.is_file() else None


# ---------- story ----------

def cover(county_name: str, number: int, year: int | None = None, draft: bool = True):
    c = lambda nm, **k: S(nm, alignment=TA_CENTER, **k)
    source_note = (
        "Names are from the WyoVote officeholder files, official election results, and official government pages cited in the sources. "
        "Where a current holder has not been compiled, the row says “Not yet collected.” No names were invented."
    )
    if draft:
        disclaimer = "DRAFT — not a published report. " + source_note
        color = RED
    else:
        disclaimer = source_note
        color = INK
    year_line = f"January {year} roster" if year else ""
    doc_line = f"114 County Officeholders {number:02d} {county_name}" + (f" · {year}" if year else "")
    sub = (f"A compact summary of elected offices as of January {year}."
           if year else
           "A compact summary of elected offices, followed by one Profile per official.")
    return [
        BR.seal(2.1),
        Spacer(1, 0.7 * inch),
        Paragraph("WyoVote", c("t0", fontName="DVB", fontSize=26, leading=31, textColor=DKG, spaceAfter=8)),
        Paragraph("County Officeholders", c("t1", fontName="DVB", fontSize=36, leading=42, textColor=NAVY, spaceAfter=6)),
        Paragraph(f"{number:02d} {county_name} County", c("t1b", fontName="DVB", fontSize=24, leading=29, textColor=NAVY, spaceAfter=14)),
        Paragraph(doc_line, c("t2", fontSize=16, leading=20, spaceAfter=10)),
        Paragraph(year_line, c("t2", fontSize=16, leading=20, spaceAfter=10)) if year_line else Spacer(1, 0),
        Paragraph(sub, c("t2b", fontSize=14, leading=18, spaceAfter=36)),
        Paragraph("MTR Research", c("t3", fontSize=16, leading=21, spaceAfter=40)),
        Paragraph(disclaimer, c("t6", fontName="DVB", fontSize=16, leading=20, textColor=color, spaceAfter=12)),
        PageBreak(),
    ]


def summary_flowables(sections, pages_map, county_name, year: int | None = None, draft: bool = True):
    if year:
        how = (
            f"How to read. Each office is listed once; the people who hold it are on separate lines, with party, term end, and rank beside each name. "
            f"Names are the people in office in January {year}. "
            f"{RANK_LEGEND}. A dash means no legislative rank is on file for that office. "
            "Term ends come from official appointment, retirement, or election dates when those are on file; otherwise they are taken from the last election and the ordinary term length. "
            "Federal, statewide, and statewide judicial officers serve every county and are listed with this county’s report."
        )
    else:
        how = (
            "How to read. Each office is listed once; the people who hold it are on separate lines, with party, term end, and rank beside each name. Names are the people in office now. Where the latest general election chose a different person, that change is shown as “in January:” under the current name; those elects take office in January 2027. "
            f"{RANK_LEGEND}. A dash means no legislative rank is on file for that office. "
            "Part 2 has one Profile per person, in the same order as this summary. A person who holds more than one office has one Profile. "
            "Term ends for statewide offices come from the WyoVote statewide officials file. Other term ends are taken from the last election and the ordinary term length (House 2 years, Senate, county, municipal, and school offices 4 years, U.S. Senate 6 years, U.S. House 2 years). "
            "Judicial rows show this county’s 2026 retention result instead of a term end, because a post-retention term end is not in the file. "
            "Federal, statewide, and statewide judicial officers serve every county and are listed with this county’s report. "
            "Municipal, school-board, and judicial records are stored in the standard officeholder, election, and Profile files."
        )
    E = []
    if draft:
        E.append(Paragraph("DRAFT — preview only.", draftst))
    E += [
        Paragraph(f"{county_name} County — elected offices" + (f" · January {year}" if year else ""), h1),
        Paragraph(how, note),
    ]
    for title, rows, notes in sections:
        if title == "Precincts":
            if rows:
                E.append(PageBreak())
            E.append(Paragraph("Precinct committee people", h1))
            for n in notes:
                E.append(Paragraph(esc(n), note))
            if rows:
                E.append(Paragraph(
                    "Each name is on its own line. People who also hold another office still have one Profile in Part 2, in the same order as Part 1.",
                    note,
                ))
            table_rows = []
            for r in rows:
                def fmt(pairs):
                    bits = [esc(name) for name, _key in pairs]
                    return "<br/>".join(bits) if bits else "—"
                table_rows.append([
                    Paragraph(esc(r["precinct"]), cell),
                    Paragraph(fmt(r["men"]), cell),
                    Paragraph(fmt(r["women"]), cell),
                ])
            if table_rows:
                E += section_table("Precincts", table_rows, cols=PCOLS, headers=PHEAD)
            continue
        table_rows = []
        office_groups = []
        prev = object()
        for r in rows:
            if r["office"] == prev:
                table_rows.append(row_cells("", r["name_html"], r["pty"], r["term"], r["rank"]))
                office_groups[-1][1] = len(table_rows) - 1
            else:
                table_rows.append(row_cells(r["office"], r["name_html"], r["pty"], r["term"], r["rank"]))
                office_groups.append([len(table_rows) - 1, len(table_rows) - 1])
                prev = r["office"]
        if table_rows:
            E += section_table(title, table_rows, office_groups=office_groups)
        for n in notes:
            if n.lower().startswith("also covers"):
                continue
            E.append(Paragraph(esc(n), note))
    return E


def profile_flowables(people, site: Path, tmp: Path, county_name: str, draft: bool = True):
    E = [PageBreak()]
    if draft:
        E.append(Paragraph("DRAFT — preview only.", draftst))
    E += [
         Paragraph("Part 2 — Profiles", h1),
         Paragraph(
             "One Profile per person, in the same order as Part 1. Empty sections are omitted. "
             "Band History and long vote or veto tables are omitted. "
             f"Where a rank graph appears, {RANK_LEGEND}, and the graph is shown only when two or more ranked years are on file.",
             note,
         )]
    for h in people:
        name = h.get("name") or "Unknown"
        key = person_key(h)
        href = resolve_href(site, h.get("href"))
        parsed = parse_html_profile(href) if href else {"research": [], "results": [], "sources": [], "subtitle": "", "blurb": ""}
        research, rsrc = standing_research(site, h.get("person_id") or "")
        allow = {"residence", "occupation", "education", "military", "prior offices", "background"}
        def clean_fields(rows):
            out = []
            for k, v in rows:
                if k.strip().lower() not in allow:
                    continue
                if "contact removed" in (v or "").lower() or "notify us of updates" in (v or "").lower():
                    continue
                if k.strip().lower() == "background":
                    parts = re.split(r"(?<=\.)\s+", v.strip())
                    v = " ".join(parts[:2])
                    if len(v) > 700:
                        v = v[:697].rsplit(" ", 1)[0] + "..."
                out.append((k, v))
            return out
        fields = clean_fields(parsed["research"]) or clean_fields(research)
        results = parsed["results"]
        offices_held = [x for x in (h.get("_offices") or []) if x]
        non_precinct = [x for x in offices_held if "precinct" not in x.lower()]
        def precinct_row(k, v):
            blob = f"{k} {v}".lower()
            return "precinct" in blob or "committeeman" in blob or "committeewoman" in blob
        if non_precinct and results:
            kept = [(k, v) for k, v in results if not precinct_row(k, v)]
            results = kept  # drop precinct-committee rows from a non-precinct official's Results
        sources = parsed["sources"] or rsrc or []
        if not sources:
            for s in h.get("sources") or []:
                if isinstance(s, dict):
                    sources.append((s.get("label") or s.get("url") or "", s.get("url") or ""))
        offices = []
        if h.get("_elect"):
            offices.append("Takes office in January")
        if h.get("role"):
            offices.append(h["role"])
        for o in offices_held[:4]:
            if "precinct" in o.lower():
                offices.append(o)
            else:
                offices.append(office_label(o, h))
        # unique short office labels
        seen_o, labels = set(), []
        for lab in offices:
            if lab and lab not in seen_o:
                seen_o.add(lab)
                labels.append(lab)
        mark = ProfileMark(key)
        block = [CondPageBreak(3.8 * inch), mark, Paragraph(esc(name), h3)]
        subline = " · ".join(labels)
        if h.get("ballot_name") and h["ballot_name"].lower() != name.lower():
            subline = (subline + " · " if subline else "") + f"Ballot: {h['ballot_name']}"
        if subline:
            block.append(Paragraph(esc(subline), psmall))
        if fields:
            block.append(Paragraph("Research", h2))
            data = [[Paragraph(esc(k), pth), Paragraph(esc(v), psmall)] for k, v in fields]
            t = Table(data, colWidths=[1.5 * inch, FW - 1.5 * inch])
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            block.append(t)
        if results:
            block.append(Paragraph("Results", h2))
            data = [[Paragraph(esc(k), pth), Paragraph(esc(v), psmall)] for k, v in results]
            t = Table(data, colWidths=[2.4 * inch, FW - 2.4 * inch])
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            block.append(t)
        # retention as a results line when not already in a results table
        r = h.get("retention")
        if r and not results:
            block.append(Paragraph("Results", h2))
            yes, no = r.get("yes"), r.get("no")
            try:
                yn = f"Yes {int(yes):,} / No {int(no):,}"
            except (TypeError, ValueError):
                yn = f"Yes {yes} / No {no}"
            if r.get("yes_pct"):
                yn += f" ({r['yes_pct']} Yes)"
            block.append(Paragraph(
                esc(f"{county_name} County {r.get('year','')} general, retention: {r.get('result','retained').capitalize()}, {yn}."),
                psmall,
            ))
        # rank line + graph (legislative ranks only; never coefficients)
        rec = RANKS.get(name) or {}
        if 2026 in rec:
            rank, n, band, rch, ch, dist = rec[2026]
            chs = "House" if ch == "H" else "Senate" if ch == "S" else (ch or "")
            line = f"2026 legislative rank: {rank} of {n} (all chambers)."
            if rch and chs:
                line += f" {chs} {rch}."
            line += f" {RANK_LEGEND}."
            block.append(Paragraph("Rank", h2))
            block.append(Paragraph(esc(line), psmall))
        png = make_rank_png(name, tmp)
        if png:
            img = Image(str(png), width=FW, height=FW * 740 / 1140 * 0.88)
            img.hAlign = "CENTER"
            cap = Paragraph(
                "The graph shows overall rank as a percent of that year’s list, 0 (MOST Conservative, #1) at the top. "
                "It is included only when two or more ranked years are on file.",
                psmall,
            )
            block.append(KeepTogether([img, cap]))
        if sources:
            block.append(Paragraph("Sources", h2))
            for lab, url in sources[:8]:
                if url and url.startswith("http"):
                    block.append(Paragraph(f'<link href="{esc(url)}">{esc(lab)}</link>', psmall))
                else:
                    block.append(Paragraph(esc(lab), psmall))
        if not fields and not results and not rec and not sources:
            block.append(Paragraph(
                "Public information found for this Profile is limited to the official roster or official election results cited in Part 1.",
                psmall,
            ))
        E.extend(block)
        E.append(Spacer(1, 0.18 * inch))
    return E


def footer_factory(doc_label: str, draft: bool = True, run: str | None = None):
    run = run or RUN
    run_line = f"Run {run}  ·  DRAFT" if draft else f"Run {run}"
    def footer(cv, n, total):
        cv.saveState()
        if n > 1:
            BR.header(cv, PW, PH, ML, MR)
        cv.setFillColor(INK)
        cv.setFont("DV", 12)
        cv.setStrokeColor(GRID)
        cv.setLineWidth(0.6)
        cv.line(ML, 0.76 * inch, PW - MR, 0.76 * inch)
        cv.drawString(ML, 0.50 * inch, doc_label)
        cv.drawRightString(PW - MR, 0.50 * inch, f"Page {n} of {total}")
        cv.drawString(ML, 0.28 * inch, run_line)
        BR.copyright(cv, PW - MR, 0.28 * inch, "DV", 12, INK)
        cv.restoreState()
    return footer


def counts_report(sections, people, county):
    """have / not-collected by office group, for the agent's report-back."""
    lines = []
    have = 0
    missing = 0
    for g in county["groups"]:
        n = 0
        miss = 0
        elects = 0
        for o in g.get("offices") or []:
            hs = o.get("holders") or []
            if not hs:
                continue
            for h in hs:
                if h.get("name") and h["name"] != "Not yet collected":
                    n += 1
                else:
                    miss += 1
                if h.get("succeeding") and h["succeeding"].get("name"):
                    elects += 1
        if g.get("precincts"):
            for prec in g["precincts"]:
                for o in prec.get("offices") or []:
                    for h in o.get("holders") or []:
                        if h.get("name"):
                            n += 1
                        else:
                            miss += 1
        lines.append((g.get("title") or g["id"], n, miss, elects, bool(g.get("note") and not (g.get("offices") or g.get("precincts")))))
        have += n
        missing += miss
    return lines, have, missing, len(people)


def render_pngs(pdf: Path, outdir: Path, people, pages_map, name_suffix: str = "114-DRAFT",
                slug: str = "weston", county_name: str = "Weston"):
    import fitz
    doc = fitz.open(pdf)
    # After booklet padding, trailing pages may be blank; only render content.
    # Cover is page 1. Summary starts page 2 and continues until Part 2.
    # We don't know exact summary page count from here; detect "Part 2" text.
    summary_pages = []
    part2 = None
    for i, page in enumerate(doc, start=1):
        text = page.get_text() or ""
        if ("Part 2 — Profiles" in text or "Part 2 - Profiles" in text) and part2 is None:
            part2 = i
        if i > 1 and part2 is None:
            summary_pages.append(i)
        if i == 1:
            pix = page.get_pixmap(dpi=150)
            pix.save(str(outdir / f"{slug}-cover-{name_suffix}.png"))
    for idx, pno in enumerate(summary_pages, start=1):
        pix = doc[pno - 1].get_pixmap(dpi=150)
        suffix = "precincts" if "Precinct committee" in (doc[pno - 1].get_text() or "") else f"p{idx}"
        pix.save(str(outdir / f"{slug}-summary-{suffix}-{name_suffix}.png"))
    # Sample profiles (county-specific, plus a shared statewide justice if present)
    samples = {
        "weston": [("Nathan Todd", "nathan-todd"), ("Tyrel Owens", "tyrel-owens"), ("Bridget Hill", "bridget-hill")],
        "crook": [("DaNece Day", "danece-day"), ("Brad Marchant", "brad-marchant"),
                  ("Melissa Jones", "melissa-jones"), ("Bridget Hill", "bridget-hill")],
        "campbell": [("Cindy J. Lovelace", "cindy-j-lovelace"), ("Shay Lundvall", "shay-lundvall"),
                     ("Scott Clem", "scott-clem"), ("Bridget Hill", "bridget-hill")],
        "sheridan": [("Eda Schunk Thompson", "eda-schunk-thompson"), ("Richard Bridger", "richard-bridger"),
                     ("Christi Burgess Haswell", "christi-burgess-haswell"), ("Bridget Hill", "bridget-hill")],
        "park": [("Colleen Renner", "colleen-renner"), ("Lee Ann Reiter", "lee-ann-reiter"),
                 ("Scott Mangold", "scott-mangold"), ("Bridget Hill", "bridget-hill")],
        "laramie": [("Gunnar Malm", "gunnar-malm"), ("Debra Lee", "debra-lee"),
                    ("Patrick Collins", "patrick-collins"), ("Bridget Hill", "bridget-hill")],
        "natrona": [("Dallas Laird", "dallas-laird"), ("Tracy Good", "tracy-good"),
                    ("Art Washut", "art-washut"), ("Bridget Hill", "bridget-hill")],
        "albany": [("Kayla White", "kayla-white"), ("Pete Gosar", "pete-gosar"),
                   ("Trey Sherwood", "trey-sherwood"), ("Bridget Hill", "bridget-hill")],
        "sweetwater": [("Island Richards", "island-richards"), ("Stacy Jones", "stacy-jones"),
                       ("Max Mickelson", "max-mickelson"), ("Bridget Hill", "bridget-hill")],
        "teton": [("Luther Propst", "luther-propst"), ("Mike Gierau", "mike-gierau"),
                  ("Arne Olaus Jorgensen", "arne-olaus-jorgensen"), ("Bridget Hill", "bridget-hill")],
        "lincoln": [("Laura Taliaferro (formerly Pearson)", "laura-taliaferro"), ("McKay L. Erickson", "mckay-l-erickson"),
                    ("Robert Bowen", "robert-bowen"), ("Bridget Hill", "bridget-hill")],
        "uinta": [("Laura Taliaferro (formerly Pearson)", "laura-taliaferro"), ("Kenneth D. Roberts", "kenneth-d-roberts"),
                  ("Jesse Lind", "jesse-lind"), ("Bridget Hill", "bridget-hill")],
        "carbon": [("Bob Davis", "bob-davis"), ("Pamela Thayer", "pamela-thayer"),
                   ("Jacquelin R. Wells", "jacquelin-r-wells"), ("Chuck Davis", "chuck-davis")],
        "converse": [("Brian Boner", "brian-boner"), ("Tomi Strock", "tomi-strock"),
                     ("Brad Jenkins", "brad-jenkins"), ("Bridget Hill", "bridget-hill")],
        "goshen": [("Cheri E. Steinmetz", "cheri-e-steinmetz"), ("JD Williams", "jd-williams"),
                   ("Herb Doby", "herb-doby"), ("Bridget Hill", "bridget-hill")],
        "platte": [("Taft Love", "taft-love"), ("Jeremy Haroldson", "jeremy-haroldson"),
                   ("Brandon R. Graves", "brandon-r-graves"), ("Bridget Hill", "bridget-hill")],
        "sublette": [("Laura Taliaferro (formerly Pearson)", "laura-taliaferro"),
                     ("Albert Sommers", "albert-sommers"),
                     ("Matt Murdock", "matt-murdock"), ("Bridget Hill", "bridget-hill")],
        "washakie": [("Ed Cooper", "ed-cooper"),
                     ("Martha Lawley", "martha-lawley"),
                     ("Rebecca George", "rebecca-george"), ("Bridget Hill", "bridget-hill")],
        "niobrara": [("Cheri E. Steinmetz", "cheri-e-steinmetz"),
                     ("JD Williams", "jd-williams"),
                     ("Becky L. Freeman", "becky-l-freeman"), ("Bridget Hill", "bridget-hill")],
        "johnson": [("Barry Crago", "barry-crago"),
                    ("Marilyn F Connolly", "marilyn-f-connolly"),
                    ("Shane J. Schrader", "shane-j-schrader"), ("Bridget Hill", "bridget-hill")],
        "fremont": [("Cale Case", "cale-case"),
                    ("Ivan D. Posey", "ivan-d-posey"),
                    ("Julie A. Freese", "julie-a-freese"), ("Bridget Hill", "bridget-hill")],
        "big-horn": [("Ed Cooper", "ed-cooper"),
                     ("Martha Lawley", "martha-lawley"),
                     ("Lori Smallwood", "lori-smallwood"),
                     ("Dalton Banks", "dalton-banks")],
        "hot-springs": [("Ed Cooper", "ed-cooper"),
                        ("Becky Kersten", "becky-kersten"),
                        ("Jerimie Kraushaar", "jerimie-kraushaar"),
                        ("Adam R. Estenson", "adam-r-estenson")],
    }
    wanted = samples.get(slug, [("Bridget Hill", "bridget-hill")])
    for name, person_slug in wanted:
        key = None
        for h in people:
            if h.get("name") == name:
                key = person_key(h)
                break
        pno = pages_map.get(key)
        if not pno:
            continue
        pix = doc[pno - 1].get_pixmap(dpi=150)
        pix.save(str(outdir / f"{slug}-profile-{person_slug}-{name_suffix}.png"))
    print("pages", doc.page_count, "part2_starts", part2)
    doc.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--county", default="weston", help="County slug.")
    ap.add_argument("--site", default=str(SITE_DEFAULT), help="Site root (worktree).")
    ap.add_argument("--out", default="", help="Output PDF path.")
    ap.add_argument("--year", type=int, default=0, help="Build the January YYYY roster from the history snapshot. 0 = live file.")
    ap.add_argument("--summary-only", action="store_true", help="Write the Seal cover and summary pages only, no Part 2 Profiles.")
    ap.add_argument("--final", action="store_true", help="Write the published 114 PDF (no DRAFT stamp) under reports/2026/.")
    args = ap.parse_args()
    site = Path(args.site)
    year = args.year or None
    slug = args.county
    county, federal, judicial = load_county_bundle(site, slug, year=year)
    groups = iter_groups(county, federal, judicial)
    sections, people = build_summary_and_people(groups)
    name = county["county"]
    number = int(county["county_number"])
    year_bit = f" {year}" if year else ""
    title = f"114 County Officeholders {number:02d} {name}{year_bit}"
    if args.final:
        suffix = f"114-{year}" if year else "114"
        default_name = f"wyovote_{year or 2026}_County_{number:02d}_{name.replace(' ', '_')}_114_v1.0.pdf"
        default_dir = site / "reports" / str(year or 2026)
        doc_label = title
        png_dir = Path("/workspace/county-report")
        png_suffix = f"114-{year}-FINAL" if year else "114-FINAL"
    else:
        suffix = f"114-{year}-DRAFT" if year else "114-DRAFT"
        default_name = f"{slug}-county-report-{suffix}.pdf"
        default_dir = OUT_DIR_DEFAULT
        doc_label = f"{title} DRAFT"
        png_dir = None
        png_suffix = suffix
    out = Path(args.out) if args.out else default_dir / default_name
    out.parent.mkdir(parents=True, exist_ok=True)
    if png_dir is None:
        png_dir = out.parent

    pages_map = {}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        draft = not args.final
        run = datetime.now(ZoneInfo("America/Denver")).strftime("%Y-%m-%d") if args.final else RUN
        def story():
            parts = cover(name, number, year=year, draft=draft) + summary_flowables(sections, pages_map, f"{number:02d} {name}", year=year, draft=draft)
            if not args.summary_only:
                parts = parts + profile_flowables(people, site, tmp, name, draft=draft)
            return parts

        doc2 = ReportDoc(
            str(out), pagesize=(PW, PH),
            leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
            title=title, author=AUTHOR, pages_map=pages_map,
        )
        doc2.addPageTemplates([PageTemplate("p", frames=[Frame(ML, MB, FW, FH, 0, 0, 0, 0)])])
        doc2.build(story(), canvasmaker=make_numbered_canvas(footer_factory(doc_label, draft=draft, run=run)))
        content_pages = doc2.page
        # Booklet pad (blank pages at the end; page labels count content only)
        c, p = pad_pdf(out)
        lines, have, missing, nprof = counts_report(sections, people, county)
        # also count shared
        shared_holders = 0
        for g in (federal.get("groups") or []) + (judicial.get("groups") or []):
            for o in g.get("offices") or []:
                shared_holders += len(o.get("holders") or [])
        render_pngs(out, png_dir, people, pages_map, name_suffix=png_suffix, slug=slug, county_name=name)
        print("wrote", out, "content_pages", content_pages, "padded", p)
        print("profiles", nprof, "have_named", have, "not_collected", missing, "shared_holders", shared_holders)
        for title_, n, miss, elects, empty_note in lines:
            print(f"  group {title_}: have={n} not_collected={miss} january_elects={elects} empty_note={empty_note}")
        # people missing a page
        miss_p = [person_key(h) for h in people if person_key(h) not in pages_map]
        if miss_p:
            print("WARN profiles without page", miss_p[:10], "n", len(miss_p))


if __name__ == "__main__":
    main()
