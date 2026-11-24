#!/usr/bin/env python3
"""Converse County officeholder history (preview). Official clerk, SOS, court,
commission minutes, and directory sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 13
SLUG = "converse"

URL_ELECTIONS = "https://www.conversecountywy.gov/187/Elections"
URL_C26 = "https://conversecountywy.gov/DocumentCenter/View/6589"
URL_P26 = "https://conversecountywy.gov/DocumentCenter/View/6486"
URL_C24 = "https://conversecountywy.gov/DocumentCenter/View/5775"
URL_C22 = "https://conversecountywy.gov/DocumentCenter/View/4890"
URL_C22R = "https://conversecountywy.gov/DocumentCenter/View/4724"
URL_C20 = "https://conversecountywy.gov/DocumentCenter/View/3289"
URL_C18 = "https://conversecountywy.gov/DocumentCenter/View/1517"
URL_C16 = "https://conversecountywy.gov/DocumentCenter/View/965"
URL_MIN_CDC = "https://conversecountywy.gov/AgendaCenter/ViewFile/Minutes/_04102026-925"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-8th-judicial-district-converse-county/"
URL_COURT_C = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-converse-county-state-of-wyoming-douglas/"
URL_COURT_G = "https://www.wyocourts.gov/court/circuit-court-of-the-8th-judicial-district-goshen-county-state-of-wyoming-torrington/"


def S(label, url=""):
    return src_dict(label, url)

SRC_C26 = S("Official Converse County 2026 general election summary (DocumentCenter 6589; header OFFICIAL RESULTS, Election Summary - 11/06/2026 12:44PM)", URL_C26)
SRC_C24 = S("Official Converse County 2024 general election summary (DocumentCenter 5775; header OFFICIAL RESULTS, 11/07/2024 02:35PM)", URL_C24)
SRC_C22 = S("Official Converse County 2022 general election summary (DocumentCenter 4890; header OFFICIAL RESULTS, 11/10/2022 11:56 AM)", URL_C22)
SRC_C22R = S("Official Converse County 2022 primary commissioners recount (DocumentCenter 4724; header OFFICIAL RESULTS, COMMISSIONERS RECOUNT REPORT, 08/19/2022 12:54 PM). This recount is of the official primary, not the general.", URL_C22R)
SRC_C20 = S("Official Converse County 2020 general election summary (DocumentCenter 3289; header OFFICIAL RESULTS, 11/05/2020 10:16 AM)", URL_C20)
SRC_C18 = S("Official Converse County 2018 general election summary (DocumentCenter 1517; header OFFICIAL RESULTS, RUN DATE 11/08/18 10:08 AM, REPORT-EL45)", URL_C18)
SRC_C16 = S("Official Converse County 2016 general election summary (DocumentCenter 965; scanned official summary, first-page header 2016 GENERAL ELECTION OFFICIAL RESULTS, RUN DATE 11/10/16 09:44 AM)", URL_C16)
SRC_MIN = S("Official approved minutes, Board of Commissioners of Converse County special meeting, April 10, 2026 (AgendaCenter minutes _04102026-925)", URL_MIN_CDC)
SRC_COURT_D = S("Official Wyoming Judicial Branch, District Court, 8th Judicial District, Converse County page", URL_COURT_D)
SRC_COURT_C = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Converse County (Douglas) page", URL_COURT_C)
SRC_COURT_G = S("Official Wyoming Judicial Branch, Circuit Court of the 8th Judicial District, Goshen County (Torrington) page", URL_COURT_G)


def sos_src(year, chamber):
    return S(
        f"Official Wyoming SOS {year} statewide {chamber} candidates summary (district-wide Total row)",
        "",
    )


def T(**kw):
    kw.setdefault("confidence", "high")
    kw.setdefault("how_took_office", "elected")
    if "sources" not in kw:
        kw["sources"] = []
    return term(**kw)


def register_people(P):
    """Reuse name-index / already-minted IDs; mint only new Converse-local people."""
    P("WY-BONER-BRIAN", "Brian Boner", "Brian", "Boner", aliases="Brian S. Boner|Brian S Boner|REP BRIAN BONER")
    P("WY-STROCK-TOMI", "Tomi Strock", "Tomi", "Strock", aliases="REP TOMI STROCK")
    P("WY-CAMPBELL-KEVIN", "Kevin J. Campbell", "Kevin", "Campbell", middle="J.", aliases="Kevin Campbell|REP KEVIN CAMPBELL|REP KEVIN J. CAMPBELL|Kevin J Campbell")
    P("WY-CHADWICK-FORREST", "Forrest Chadwick", "Forrest", "Chadwick", aliases="REP FORREST CHADWICK")
    P("WY-CLAUSEN-AARON", "Aaron Clausen", "Aaron", "Clausen")
    P("WY-CANNADY-RICHARD-L", "Richard L. Cannady", "Richard", "Cannady", middle="L.", aliases="Richard L Cannady")
    P("WY-KIRKBRIDE-DAN-R", "Dan R. Kirkbride", "Dan", "Kirkbride", middle="R.", aliases="Dan R Kirkbride")
    P("WY-HAROLDSON-JEREMY", "Jeremy Haroldson", "Jeremy", "Haroldson")
    P("WY-BARLOW-ERIC", "Eric Barlow", "Eric", "Barlow")
    P("WY-WASSERBURGER-JEFF", "Jeff Wasserburger", "Jeff", "Wasserburger")
    # County
    P("WY-KAUFMAN-TRENT", "Trent Kaufman", "Trent", "Kaufman", aliases="REP TRENT KAUFMAN")
    P("WY-MOORE-MACEY", "Macey Moore", "Macey", "Moore", aliases="REP MACEY MOORE")
    P("WY-TORGERSON-CODY", "Cody Torgerson", "Cody", "Torgerson", aliases="REP CODY TORGERSON")
    P("WY-BLACKBURN-DONALD-J", "Donald J. Blackburn", "Donald", "Blackburn", middle="J.", aliases="Donald J Blackburn|DONALD J BLACKBURN|REP DONALD J BLACKBURN")
    P("WY-GRANT-RICK", "Rick Grant", "Rick", "Grant", aliases="REP RICK GRANT")
    P("WY-WILLOX-JIM", "Jim Willox", "Jim", "Willox", aliases="James H. Willox|James H Willox|JIM WILLOX")
    P("WY-SHORT-ROBERT-G", "Robert G. Short", "Robert", "Short", middle="G.", aliases="Robert G Short|ROBERT GSHORT|ROBERT G. SHORT")
    P("WY-COLLING-MIKE", "Mike Colling", "Mike", "Colling", aliases="REP MIKE COLLING")
    P("WY-RIMMER-KAREN", "Karen Rimmer", "Karen", "Rimmer", aliases="REP KAREN RIMMER")
    P("WY-SCHELL-JOEL", "Joel Schell", "Joel", "Schell")
    P("WY-HUXTABLE-DIXIE-J", "Dixie J. Huxtable", "Dixie", "Huxtable", middle="J.", aliases="Dixie J Huxtable|DIXIE J HUXTABLE")
    P("WY-BECKER-CLINTON", "Clinton Becker", "Clinton", "Becker", aliases="Clint Becker|CLINT BECKER|CLINTON BECKER")
    P("WY-RICHARDSON-QUENTIN", "Quentin Richardson", "Quentin", "Richardson")
    P("WY-GORMAN-ROSCOE-J", 'Roscoe J. (Ross) Gorman', "Roscoe", "Gorman", middle="J.", aliases='Roscoe J. "Ross" Gorman|ROSCOE J. (ROSS) GORMAN|ROSCOE J ·ROSS· GORMAN|Ross Gorman')
    P("WY-HARRIS-BARBARA", "Barbara Harris", "Barbara", "Harris")
    P("WY-MCCULLOUGH-PAM", "Pam McCullough", "Pam", "McCullough", aliases="PAM McCULLOUGH|Pam McCullough")
    # Municipal
    P("WY-JENKINS-BRAD", "Brad Jenkins", "Brad", "Jenkins")
    P("WY-PEXTON-KIM", "Kim Pexton", "Kim", "Pexton")
    P("WY-KEMPER-RENE", "Rene' Kemper", "Rene'", "Kemper", aliases="RENE' KEMPER|Rene Kemper")
    P("WY-COLLING-JUDI", "Judi Colling", "Judi", "Colling")
    P("WY-ROUMELL-BRUCE", "Bruce Roumell", "Bruce", "Roumell")
    P("WY-MAINES-JON-O", "Jon O. Maines", "Jon", "Maines", middle="O.", aliases="Jon O Maines|JON O. MAINES")
    P("WY-STRINGHAM-ARTHUR", "Arthur Stringham", "Arthur", "Stringham")
    P("WY-WAGSTAFF-BRECK", "Breck Wagstaff", "Breck", "Wagstaff")
    P("WY-BURKE-SHEA", "Shea Burke", "Shea", "Burke")
    P("WY-WEEKS-JOEL-R", "Joel R. Weeks", "Joel", "Weeks", middle="R.", aliases="Joel R Weeks")
    P("WY-SCHMIDT-MATT", "Matt Schmidt", "Matt", "Schmidt")
    P("WY-MCNARE-RON", "Ron McNare", "Ron", "McNare")
    P("WY-HERSHBERGER-PERRY", "Perry Hershberger", "Perry", "Hershberger")
    P("WY-HERTZ-KARL", "Karl Hertz", "Karl", "Hertz")
    P("WY-BOPP-TRACIE", "Tracie Bopp", "Tracie", "Bopp")
    P("WY-KINCAID-ROY", "Roy Kincaid", "Roy", "Kincaid")
    P("WY-NUNN-MARGARET", "Margaret Nunn", "Margaret", "Nunn")
    P("WY-DALGARN-RUSS", "Russ Dalgarn", "Russ", "Dalgarn")
    P("WY-RIVERA-ANTHONY", "Anthony Rivera", "Anthony", "Rivera")
    P("WY-MONTGOMERY-KENNETH", "Kenneth Montgomery", "Kenneth", "Montgomery")
    P("WY-ETTLES-JODY", "Jody Ettles", "Jody", "Ettles")
    P("WY-WEAVER-DONNA", "Donna Weaver", "Donna", "Weaver")
    P("WY-CIELINSKI-LORI", "Lori Cielinski", "Lori", "Cielinski")
    P("WY-BOWDISH-CLIFTON", "Clifton Bowdish", "Clifton", "Bowdish")
    P("WY-BOWDISH-NELLIE", "Nellie Bowdish", "Nellie", "Bowdish")
    # Schools
    P("WY-BONER-TRENT", "Trent Boner", "Trent", "Boner")
    P("WY-MOORE-JOSH", "Josh Moore", "Josh", "Moore")
    P("WY-MCCARTY-DAX", "Dax McCarty", "Dax", "McCarty", aliases="DAX MCCARTY|DAX McCARTY")
    P("WY-CAMINO-ADAM", "Adam Camino", "Adam", "Camino")
    P("WY-STINSON-SHANE", "Shane Stinson", "Shane", "Stinson")
    P("WY-VOLLMAN-JARED", "Jared Vollman", "Jared", "Vollman")
    P("WY-TILLARD-TY", "Ty Tillard", "Ty", "Tillard")
    P("WY-REESE-BRAD", "Brad Reese", "Brad", "Reese")
    P("WY-DARR-JEREMIAH", "Jeremiah Darr", "Jeremiah", "Darr")
    P("WY-FORGEY-JOHN-JC", 'John "J.C." Forgey', "John", "Forgey", aliases="John J.C. Forgey|JOHN \"J.C.\" FORGEY")
    P("WY-HILL-STACI", "Staci Hill", "Staci", "Hill")
    P("WY-TILLARD-CASEY", "Casey Tillard", "Casey", "Tillard")
    P("WY-KINCAID-VIKI", "Viki Kincaid", "Viki", "Kincaid")
    P("WY-ALLEN-ROSS", "Ross Allen", "Ross", "Allen")
    P("WY-WILLIAMS-JARED", "Jared Williams", "Jared", "Williams")
    P("WY-GRANT-BRENDON", "Brendon Grant", "Brendon", "Grant")
    # Specials
    P("WY-MOORE-MORIAH", "Moriah Moore", "Moriah", "Moore")
    P("WY-SMITH-WAYNE", "Wayne Smith", "Wayne", "Smith")
    P("WY-WOLFLEY-KENNY", "Kenny Wolfley", "Kenny", "Wolfley")
    P("WY-FALKENBURG-SHELLY", "Shelly Falkenburg", "Shelly", "Falkenburg")
    P("WY-DOWNS-SUSAN", "Susan Downs", "Susan", "Downs")
    P("WY-BENGE-JACI", "Jaci Benge", "Jaci", "Benge")
    P("WY-RICKER-TIM", "Tim Ricker", "Tim", "Ricker")
    P("WY-LEHNER-CAROLYN", "Carolyn Lehner", "Carolyn", "Lehner")
    P("WY-SHERIDAN-CINDY", "Cindy Sheridan", "Cindy", "Sheridan")
    P("WY-WOLLEN-JB", "J.B. Wollen", "J.B.", "Wollen", aliases="JB Wollen|J.B. WOLLEN")
    P("WY-DOWNS-SALLY-J", "Sally J. Downs", "Sally", "Downs", middle="J.", aliases="Sally J Downs")
    P("WY-DAMPMAN-LYNN", "Lynn Dampman", "Lynn", "Dampman")
    P("WY-NUNN-ROBERT", "Robert Nunn", "Robert", "Nunn")
    P("WY-OHMAN-VICTOR-N", "Victor N. Ohman", "Victor", "Ohman", middle="N.", aliases="Victor N Ohman")
    P("WY-GOWING-SEAN", "Sean Gowing", "Sean", "Gowing")
    P("WY-MOULTON-KARIE", "Karie Moulton", "Karie", "Moulton")
    P("WY-COBB-JAMES-C", "James C. Cobb", "James", "Cobb", middle="C.", aliases="JAMES C COBB|James C Cobb")
    P("WY-COLLINS-LESLIE-C", "Leslie C. Collins", "Leslie", "Collins", middle="C.", aliases="LESLIE C COLLINS|Leslie C Collins")
    # Judicial 8th JD
    P("WY-PEASLEY-F-SCOTT", "F. Scott Peasley", "F. Scott", "Peasley", aliases="Hon. F. Scott Peasley|Scott Peasley")
    P("WY-BUCHANAN-EDWARD-A", "Edward A. Buchanan", "Edward", "Buchanan", middle="A.", aliases="Hon. Edward A. Buchanan|Edward Buchanan")
    P("WY-ALLAN-CLARK-C", "Clark C. Allan", "Clark", "Allan", middle="C.", aliases="Hon. Clark C. Allan|CLARK C. ALLAN")
    P("WY-HIBBEN-NATHANIEL-S", "Nathaniel S. Hibben", "Nathaniel", "Hibben", middle="S.", aliases="Nathaniel Hibben|HIBBEN")
    P("WY-BROWN-JACQUELINE-K", "Jacqueline K. Brown", "Jacqueline", "Brown", middle="K.", aliases="Hon. Jacqueline K. Brown|JACQUELINE K. BROWN")


def legislature_terms():
    """Whole-district official SOS totals, with the official Converse share in the note."""
    terms = []

    # Senate District 2 — 4-year, even years 2016/2020/2024. Official 2014 SOS has no S02 row (off-cycle). Official 2012 Senate winner is not keyed here.
    s02 = [
        (2016, "WY-BONER-BRIAN", "Brian Boner", "REP",
         "Official 2016 SOS statewide Senate summary Total: Brian S. Boner (R) 8,187, William B. Cullen III (D) 1,377. Official Converse portion: Boner 4,630, Cullen 551. Official Platte share: 3,557–826. Do not use the two-column Total, which also prints Senate District 4.",
         [sos_src(2016, "Senate")]),
        (2020, "WY-BONER-BRIAN", "Brian Boner", "REP",
         "Official 2020 SOS statewide Senate summary Total: Brian Boner (R) 9,372. Official Converse portion: 5,074. Official Platte share: 4,298. Do not use the two-column Total, which also prints Senate District 4.",
         [sos_src(2020, "Senate"), SRC_C20]),
        (2024, "WY-BONER-BRIAN", "Brian Boner", "REP",
         "Official 2024 SOS statewide Senate summary Total: Brian Boner (R) 7,712. Official Converse portion: 5,912 (matches official Converse clerk). Official Natrona share: 1,800. After 2022 redistricting the official SOS county rows are Converse and Natrona (Platte is no longer in S02).",
         [sos_src(2024, "Senate"), SRC_C24]),
    ]
    for year, pid, name, party, note, srcs in s02:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-senate",
                       office="Senate District 2 (S02)", term_start=FM[year + 1], term_end=FM[year + 5],
                       election_year=year, sources=srcs, notes=note))

    # Senate District 23 — official SOS shows a Converse sliver in 2014 and 2018 only. Official 2022 and 2026 SOS Converse rows are blank (redistricted out).
    s23 = [
        (2014, "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", "REP",
         "Official 2014 SOS statewide Senate summary Total: Jeff Wasserburger (R) 4,110. Official Converse portion: 677. Official Campbell share: 3,433.",
         [sos_src(2014, "Senate")]),
        (2018, "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", "REP",
         "Official 2018 SOS statewide Senate summary Total: Jeff Wasserburger (R) 5,116. Official Converse portion: 792 (matches official Converse clerk). Official Campbell share: 4,324. Do not use the two-column Total, which also prints Senate District 25.",
         [sos_src(2018, "Senate"), SRC_C18]),
    ]
    for year, pid, name, party, note, srcs in s23:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-senate",
                       office="Senate District 23 (S23)", term_start=FM[year + 1], term_end=FM[year + 5],
                       election_year=year, sources=srcs, notes=note))

    # House District 6 — official SOS Totals equal the official Converse row in 2014–2026 (Converse-only).
    h06 = [
        (2014, "WY-CANNADY-RICHARD-L", "Richard L. Cannady", "REP",
         "Official 2014 SOS statewide House summary Total: Richard L. Cannady (R) 2,341, Liz Batton (D) 494, all in Converse (official SOS Total equals the official Converse row).",
         [sos_src(2014, "House")]),
        (2016, "WY-CLAUSEN-AARON", "Aaron Clausen", "REP",
         "Official 2016 SOS statewide House summary, House District 6 county rows (do not use the two-column Total, which also prints House District 5): Aaron Clausen (R) 3,996, Shalyn C. Anderson (D) 565, all in Converse.",
         [sos_src(2016, "House")]),
        (2018, "WY-CLAUSEN-AARON", "Aaron Clausen", "REP",
         "Official 2018 SOS statewide House summary, House District 6 county rows (do not use the two-column Total, which also prints House District 5): Aaron Clausen (R) 2,942, all in Converse.",
         [sos_src(2018, "House")]),
        (2020, "WY-CLAUSEN-AARON", "Aaron Clausen", "REP",
         "Official 2020 SOS statewide House summary, House District 6 county rows (do not use the two-column Total, which also prints House District 5): Aaron Clausen (R) 4,296, all in Converse.",
         [sos_src(2020, "House")]),
        (2022, "WY-STROCK-TOMI", "Tomi Strock", "REP",
         "Official 2022 SOS statewide House summary Total: Tomi Strock (R) 2,266, Hank Szramkowski (D) 218, Bruce Jones (I) 1,079, all in Converse (official SOS Total equals the official Converse clerk).",
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-STROCK-TOMI", "Tomi Strock", "REP",
         "Official 2024 SOS statewide House summary Total: Tomi Strock (R) 3,742, all in Converse (official SOS Total equals the official Converse clerk).",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-STROCK-TOMI", "Tomi Strock", "REP",
         "Official 2026 SOS statewide House summary Total: Tomi Strock (R) 2,175, all in Converse (official SOS Total equals the official Converse clerk).",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h06:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 6 (H06)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    # House District 62 — created in 2022 redistricting; official SOS Totals are Converse + Natrona.
    h62 = [
        (2022, "WY-CHADWICK-FORREST", "Forrest Chadwick", "REP",
         "Official 2022 SOS statewide House summary Total: Forrest Chadwick (R) 2,518. Official Converse portion: 1,316 (matches official Converse clerk). Official Natrona share: 1,202.",
         [sos_src(2022, "House"), SRC_C22]),
        (2024, "WY-CAMPBELL-KEVIN", "Kevin J. Campbell", "REP",
         "Official 2024 SOS statewide House summary Total: Kevin Campbell (R) 3,496. Official Converse portion: 1,732 (matches official Converse clerk). Official Natrona share: 1,764.",
         [sos_src(2024, "House"), SRC_C24]),
        (2026, "WY-CAMPBELL-KEVIN", "Kevin J. Campbell", "REP",
         "Official 2026 SOS statewide House summary Total: Kevin J. Campbell (R) 2,297. Official Converse portion: 1,175 (matches official Converse clerk). Official Natrona share: 1,122.",
         [sos_src(2026, "House"), SRC_C26]),
    ]
    for year, pid, name, party, note, srcs in h62:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 62 (H62)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    # House District 3 — official SOS Converse sliver 2014–2020 with Campbell. Official 2022+ Converse row is blank.
    h03 = [
        (2014, "WY-BARLOW-ERIC", "Eric Barlow", "REP",
         "Official 2014 SOS statewide House summary Total: Eric Barlow (R) 2,222. Official Converse portion: 657. Official Campbell share: 1,565.",
         [sos_src(2014, "House")]),
        (2016, "WY-BARLOW-ERIC", "Eric Barlow", "REP",
         "Official 2016 SOS statewide House summary, House District 3 county rows (do not use the two-column Total, which also prints House District 4): Eric Barlow (R) 3,822. Official Converse portion: 1,107. Official Campbell share: 2,715.",
         [sos_src(2016, "House")]),
        (2018, "WY-BARLOW-ERIC", "Eric Barlow", "REP",
         "Official 2018 SOS statewide House summary, House District 3 county rows (do not use the two-column Total, which also prints House District 4): Eric Barlow (R) 2,811. Official Converse portion: 824. Official Campbell share: 1,987.",
         [sos_src(2018, "House")]),
        (2020, "WY-BARLOW-ERIC", "Eric Barlow", "REP",
         "Official 2020 SOS statewide House summary, House District 3 county rows (do not use the two-column Total, which also prints House District 4): Eric Barlow (R) 4,016. Official Converse portion: 1,184. Official Campbell share: 2,832.",
         [sos_src(2020, "House")]),
    ]
    for year, pid, name, party, note, srcs in h03:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 3 (H03)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))

    # House District 4 — official SOS Converse sliver 2014–2020 with Platte. Official 2022 and 2026 SOS Converse rows are blank.
    h04 = [
        (2014, "WY-KIRKBRIDE-DAN-R", "Dan R. Kirkbride", "REP",
         "Official 2014 SOS statewide House summary Total: Dan R. Kirkbride (R) 3,326. Official Converse portion: 327. Official Platte share: 2,999.",
         [sos_src(2014, "House")]),
        (2016, "WY-KIRKBRIDE-DAN-R", "Dan R. Kirkbride", "REP",
         "Official 2016 SOS statewide House summary, House District 4 county rows (do not use the two-column Total, which also prints House District 3): Dan R. Kirkbride (R) 3,652, Joe Michaels (C) 1,185. Official Converse portion: Kirkbride 448, Michaels 97. Official Platte share: 3,204–1,088.",
         [sos_src(2016, "House")]),
        (2018, "WY-KIRKBRIDE-DAN-R", "Dan R. Kirkbride", "REP",
         "Official 2018 SOS statewide House summary, House District 4 county rows (do not use the two-column Total, which also prints House District 3): Dan R. Kirkbride (R) 3,645. Official Converse portion: 386. Official Platte share: 3,259.",
         [sos_src(2018, "House")]),
        (2020, "WY-HAROLDSON-JEREMY", "Jeremy Haroldson", "REP",
         "Official 2020 SOS statewide House summary, House District 4 county rows (do not use the two-column Total, which also prints House District 3): Jeremy Haroldson (R) 4,227. Official Converse portion: 540. Official Platte share: 3,687.",
         [sos_src(2020, "House")]),
    ]
    for year, pid, name, party, note, srcs in h04:
        terms.append(T(person_id=pid, name=name, party=party, office_group="state-house",
                       office="House District 4 (H04)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=srcs, notes=note))
    return terms


def county_terms():
    terms = []
    # Commissioners, staggered 4-year. Official 2016 VF2 (OCR of official scanned summary), official 2020 VF2, official 2022 VF3, official 2024 VF2, official 2026 VF3.
    terms += [
        T(person_id="WY-GRANT-RICK", name="Rick Grant", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2017], term_end=FM[2021], election_year=2016,
          sources=[SRC_C16], notes="Official 2016 Converse clerk (scanned official summary), commissioner Vote-For-2: Rick Grant 4,508, Mike Colling 4,191."),
        T(person_id="WY-COLLING-MIKE", name="Mike Colling", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2017], term_end=FM[2021], election_year=2016,
          sources=[SRC_C16], notes="Official 2016 Converse clerk (scanned official summary), commissioner Vote-For-2: Rick Grant 4,508, Mike Colling 4,191."),
        T(person_id="WY-GRANT-RICK", name="Rick Grant", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Converse clerk, commissioner Vote-For-2: Rick Grant 4,469, Mike Colling 4,217, Darek J. Joppru 1,705."),
        T(person_id="WY-COLLING-MIKE", name="Mike Colling", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Converse clerk, commissioner Vote-For-2: Rick Grant 4,469, Mike Colling 4,217, Darek J. Joppru 1,705."),
        T(person_id="WY-KAUFMAN-TRENT", name="Trent Kaufman", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, commissioner Vote-For-3: Trent Kaufman 3,363, Robert G. Short 3,199, Jim Willox 2,794, Darek J. Joppru 1,909. Official DocumentCenter 4724 is the official 2022 primary commissioners recount, not a change to these general-election winners."),
        T(person_id="WY-SHORT-ROBERT-G", name="Robert G. Short", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk ballot line ROBERT GSHORT, 3,199; display name Robert G. Short."),
        T(person_id="WY-WILLOX-JIM", name="Jim Willox", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Jim Willox 2,794. Official April 10, 2026 commission minutes are signed James H. Willox, Chairman."),
        T(person_id="WY-BLACKBURN-DONALD-J", name="Donald J. Blackburn", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], notes="Official 2024 Converse clerk, commissioner Vote-For-2: Donald J Blackburn 5,025, Rick Grant 3,880."),
        T(person_id="WY-GRANT-RICK", name="Rick Grant", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], notes="Official 2024 Converse clerk, commissioner Vote-For-2: Donald J Blackburn 5,025, Rick Grant 3,880."),
        T(person_id="WY-TORGERSON-CODY", name="Cody Torgerson", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, commissioner Vote-For-3: Cody Torgerson 3,098, Trent Kaufman 2,867, Macey Moore 2,792."),
        T(person_id="WY-KAUFMAN-TRENT", name="Trent Kaufman", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, commissioner Vote-For-3: Cody Torgerson 3,098, Trent Kaufman 2,867, Macey Moore 2,792."),
        T(person_id="WY-MOORE-MACEY", name="Macey Moore", party="REP", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, commissioner Vote-For-3: Cody Torgerson 3,098, Trent Kaufman 2,867, Macey Moore 2,792."),
    ]

    # Row officers. Official 2020 had a clerk contest (Karen Rimmer) two years before the official 2022 4-year slate; that 2020 term is encoded through January 2023, when the official 2022 term begins.
    terms += [
        T(person_id="WY-RIMMER-KAREN", name="Karen Rimmer", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2021], term_end=FM[2023], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Converse clerk: Karen Rimmer 6,223. Official 2022 clerk contest starts a new term in January 2023."),
        T(person_id="WY-RIMMER-KAREN", name="Karen Rimmer", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Karen Rimmer 4,555."),
        T(person_id="WY-RIMMER-KAREN", name="Karen Rimmer", party="REP", office_group="county",
          office="County Clerk", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Karen Rimmer 3,946."),
        T(person_id="WY-SCHELL-JOEL", name="Joel Schell", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Joel Schell 4,458."),
        T(person_id="WY-SCHELL-JOEL", name="Joel Schell", party="REP", office_group="county",
          office="County Treasurer", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Joel Schell 3,945."),
        T(person_id="WY-HUXTABLE-DIXIE-J", name="Dixie J. Huxtable", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Dixie J Huxtable 4,500."),
        T(person_id="WY-HUXTABLE-DIXIE-J", name="Dixie J. Huxtable", party="REP", office_group="county",
          office="County Assessor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Dixie J. Huxtable 3,857."),
        T(person_id="WY-BECKER-CLINTON", name="Clinton Becker", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk ballot name CLINT BECKER, 4,261. Official 2026 ballot name is Clinton Becker; same person."),
        T(person_id="WY-BECKER-CLINTON", name="Clinton Becker", party="REP", office_group="county",
          office="County Sheriff", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Clinton Becker 3,729."),
        T(person_id="WY-RICHARDSON-QUENTIN", name="Quentin Richardson", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Quentin Richardson 4,365."),
        T(person_id="WY-RICHARDSON-QUENTIN", name="Quentin Richardson", party="REP", office_group="county",
          office="County Attorney", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Quentin Richardson 3,715."),
        T(person_id="WY-GORMAN-ROSCOE-J", name='Roscoe J. (Ross) Gorman', party="REP", office_group="county",
          office="County Coroner", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk: Roscoe J. (Ross) Gorman 4,614."),
        T(person_id="WY-GORMAN-ROSCOE-J", name='Roscoe J. (Ross) Gorman', party="REP", office_group="county",
          office="County Coroner", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Roscoe J. (Ross) Gorman 3,963."),
        # Clerk of District Court: official 2018 and 2022 Pam McCullough; official mid-term appointment of Barbara Harris April 10, 2026; official 2026 election for the term beginning January 4, 2027.
        T(person_id="WY-MCCULLOUGH-PAM", name="Pam McCullough", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2019], term_end=FM[2023], election_year=2018,
          sources=[SRC_C18], notes="Official 2018 Converse clerk: Pam McCullough (REP) 4,332."),
        T(person_id="WY-MCCULLOUGH-PAM", name="Pam McCullough", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2023], term_end="2026-04-10", election_year=2022,
          sources=[SRC_C22, SRC_MIN], notes="Official 2022 Converse clerk: Pam McCullough 4,490. Official April 10, 2026 commission minutes appoint Barbara Harris to the vacated office for a term from April 10, 2026, through January 4, 2027, and record that Harris was sworn in that day."),
        T(person_id="WY-HARRIS-BARBARA", name="Barbara Harris", party="REP", office_group="county",
          office="Clerk of District Court", term_start="2026-04-10", term_end=FM[2027], election_year=2026,
          how_took_office="appointed", sources=[SRC_MIN, SRC_COURT_D],
          notes="Official April 10, 2026 commission minutes: the board appointed Barbara Harris to the vacated Clerk of District Court office for a term from April 10, 2026, through January 4, 2027, and she was sworn in that day. Official 8th JD Converse District Court page lists Barbara Harris as clerk."),
        T(person_id="WY-HARRIS-BARBARA", name="Barbara Harris", party="REP", office_group="county",
          office="Clerk of District Court", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk: Barbara Harris 3,882."),
    ]
    return terms


def judicial_terms():
    terms = []
    terms += [
        T(person_id="WY-PEASLEY-F-SCOTT", name="F. Scott Peasley", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2017-08-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD Converse District Court page: Hon. F. Scott Peasley, appointed August 2017, retained November 2024, term expires January 2031. Official 2024 Converse clerk DISTRICT COURT - PEASLEY: YES 5,205, NO 925. Start day is the first of the official appointment month (the official court page gives the month only)."),
        T(person_id="WY-BUCHANAN-EDWARD-A", name="Edward A. Buchanan", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2022-09-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_D, SRC_C24],
          notes="Official Wyoming Judicial Branch 8th JD Converse District Court page: Hon. Edward A. Buchanan, appointed September 2022, retained November 2024, term expires January 2031. Official 2024 Converse clerk DISTRICT COURT - BUCHANAN: YES 4,784, NO 978. Start day is the first of the official appointment month."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2021-01-01", term_end=FM[2027],
          election_year=2022, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_C, SRC_C22],
          notes="Official Wyoming Judicial Branch 8th JD Converse (Douglas) Circuit Court page: Hon. Clark C. Allan, appointed January 2021, term expires January 2027, stands for retention November 2026. Official 2022 Converse clerk CIRCUIT JUDGE, CLARK C. ALLAN: YES 3,771, NO 736. Start day is the first of the official appointment month."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_C],
          notes="Official 2026 Converse clerk RETAIN JUDGE CLARK C. ALLAN: YES 2,932, NO 822."),
        T(person_id="WY-HIBBEN-NATHANIEL-S", name="Nathaniel S. Hibben", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2021], term_end="2025-05-10",
          election_year=2020, sources=[SRC_C20, SRC_C24],
          notes="Official 2020 Converse clerk CIRCUIT COURT - HIBBEN: YES 5,072, NO 941. Official 2024 Converse clerk CIRCUIT COURT - HIBBEN: YES 4,716, NO 953. Full name Nathaniel S. Hibben is from the official Wyoming Judicial Branch 1st JD page after his later appointment. Official Judicial Nominating Commission release announced the 8th JD Goshen circuit vacancy effective May 10, 2025. The official appointment date before the 2020 retention was not taken from an official court page here, so January 2015–2020 snapshots do not invent a start."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2025-07-01", term_end=FM[2027],
          election_year=2026, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT_G, SRC_C26],
          notes="Official Wyoming Judicial Branch 8th JD Goshen (Torrington) Circuit Court page: Hon. Jacqueline K. Brown, appointed July 2025, term expires January 2027, stands for retention November 2026. Official Judicial Branch robing notice lists her as Circuit Court Judge of the 8th JD (Converse, Goshen, Niobrara, and Platte Counties). Start day is the first of the official appointment month."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT_G],
          notes="Official 2026 Converse clerk RETAIN JUDGE JACQUELINE K. BROWN: YES 2,893, NO 799. Official 2026 Converse clerk also has RETAIN JUDGE BEN BURNINGHAM (YES 2,823, NO 841); that is the statewide Chancery Court retention copied from the shared judicial terms, not a local 8th JD seat."),
    ]
    return terms


def municipal_terms():
    terms = []
    # Official 2022, 2024, and 2026 clerk show mayor contests for all four municipalities in 2022 and 2026, and a Douglas mayor contest in 2024. Mayors are elected on the November ballot, not council-chosen.
    # Douglas mayor is on the official 2022, 2024, and 2026 ballots (2-year). Glenrock, Rolling Hills, and Lost Springs mayors are on the official 2022 and 2026 ballots (4-year).
    terms += [
        T(person_id="WY-KEMPER-RENE", name="Rene' Kemper", party="", office_group="municipal",
          office="Douglas Mayor", term_start=FM[2023], term_end=FM[2025], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Mayor Douglas: Rene' Kemper 1,725."),
        T(person_id="WY-PEXTON-KIM", name="Kim Pexton", party="", office_group="municipal",
          office="Douglas Mayor", term_start=FM[2025], term_end=FM[2027], election_year=2024,
          sources=[SRC_C24], notes="Official 2024 Converse clerk, Mayor Douglas: Kim Pexton 1,304, Tony Reynolds 1,249."),
        T(person_id="WY-JENKINS-BRAD", name="Brad Jenkins", party="", office_group="municipal",
          office="Douglas Mayor", term_start=FM[2027], term_end=FM[2029], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Mayor City of Douglas: Brad Jenkins 831, Kim Pexton 817."),
        T(person_id="WY-ROUMELL-BRUCE", name="Bruce Roumell", party="", office_group="municipal",
          office="Glenrock Mayor", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Mayor Glenrock: Bruce Roumell 424, Margaret Nunn 378."),
        T(person_id="WY-COLLING-JUDI", name="Judi Colling", party="", office_group="municipal",
          office="Glenrock Mayor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Mayor Town of Glenrock: Judi Colling 414, Bruce Roumell 300."),
        T(person_id="WY-MAINES-JON-O", name="Jon O. Maines", party="", office_group="municipal",
          office="Rolling Hills Mayor", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Mayor Rolling Hills: Jon O. Maines 139."),
        T(person_id="WY-MAINES-JON-O", name="Jon O. Maines", party="", office_group="municipal",
          office="Rolling Hills Mayor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Mayor Town of Rolling Hills: Jon O. Maines 121."),
        T(person_id="WY-STRINGHAM-ARTHUR", name="Arthur Stringham", party="", office_group="municipal",
          office="Lost Springs Mayor", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Mayor Town of Lost Springs: Arthur Stringham 3. Official 2022 Lost Springs mayor was write-in totals 3 with no official named certified winner and is left unfilled."),
    ]

    # Douglas council. Official 2022 labeled 4-year and 2-year seats. Official 2024 and 2026 council contests are unlabeled; 4-year terms follow the official 2022 4-year pattern (medium confidence on length only). Official 2024 Vote-For-1 is encoded as a 2-year seat, matching the official 2022 2-year Douglas council pattern.
    terms += [
        T(person_id="WY-PEXTON-KIM", name="Kim Pexton", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Douglas 4-year Vote-For-2: Kim Pexton 1,385, Perry Hershberger 1,339."),
        T(person_id="WY-HERSHBERGER-PERRY", name="Perry Hershberger", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Douglas 4-year Vote-For-2: Kim Pexton 1,385, Perry Hershberger 1,339."),
        T(person_id="WY-SCHMIDT-MATT", name="Matt Schmidt", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2023], term_end=FM[2025], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Douglas 2-year Vote-For-1: Matt Schmidt 940, Josh Valk 499."),
        T(person_id="WY-MCNARE-RON", name="Ron McNare", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Converse clerk, Councilperson Douglas Vote-For-2: Ron McNare 1,557, Karl Hertz 1,023, Perry Hershberger 1,005, Monty Gilbreath 939. Term length follows the official 4-year council pattern (medium confidence on length only)."),
        T(person_id="WY-HERTZ-KARL", name="Karl Hertz", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2021], term_end=FM[2025], election_year=2020,
          sources=[SRC_C20], notes="Official 2020 Converse clerk, Councilperson Douglas Vote-For-2: Ron McNare 1,557, Karl Hertz 1,023."),
        T(person_id="WY-SCHMIDT-MATT", name="Matt Schmidt", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Douglas Vote-For-2: Matt Schmidt 1,330, Ron McNare 1,289, Jacey Bauman 1,209. Official 2024 clerk did not print 2-year/4-year on this contest; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-MCNARE-RON", name="Ron McNare", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Douglas Vote-For-2: Matt Schmidt 1,330, Ron McNare 1,289, Jacey Bauman 1,209. Official 2024 clerk did not print 2-year/4-year on this contest; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-WEEKS-JOEL-R", name="Joel R. Weeks", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2025], term_end=FM[2027], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Douglas Vote-For-1: Joel R. Weeks 1,414, Josh Valk 882. Official 2024 clerk did not print 2-year/4-year; 2-year term follows the official 2022 2-year Douglas council pattern."),
        T(person_id="WY-WAGSTAFF-BRECK", name="Breck Wagstaff", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council City of Douglas Vote-For-2: Breck Wagstaff 1,011, Shea Burke 737, Mike Hagemann 612, Noah Milmont 568. Official 2026 clerk did not print 2-year/4-year; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-BURKE-SHEA", name="Shea Burke", party="", office_group="municipal",
          office="Douglas Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council City of Douglas Vote-For-2: Breck Wagstaff 1,011, Shea Burke 737."),
    ]

    terms += [
        T(person_id="WY-COLLING-JUDI", name="Judi Colling", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Glenrock 4-year Vote-For-2: Judi Colling 430, Roy Kincaid 430, Tim Morgan 351, Taylor Mae Flores 171."),
        T(person_id="WY-KINCAID-ROY", name="Roy Kincaid", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Glenrock 4-year Vote-For-2: Judi Colling 430, Roy Kincaid 430."),
        T(person_id="WY-NUNN-MARGARET", name="Margaret Nunn", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Glenrock Vote-For-2: Margaret Nunn 766, Russ Dalgarn 710. Official 2024 clerk did not print 2-year/4-year; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-DALGARN-RUSS", name="Russ Dalgarn", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Glenrock Vote-For-2: Margaret Nunn 766, Russ Dalgarn 710."),
        T(person_id="WY-BOPP-TRACIE", name="Tracie Bopp", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council Town of Glenrock Vote-For-2: Tracie Bopp 414, Roy Kincaid 396, Lonnie Sorenson 379. Official 2026 clerk did not print 2-year/4-year; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-KINCAID-ROY", name="Roy Kincaid", party="", office_group="municipal",
          office="Glenrock Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council Town of Glenrock Vote-For-2: Tracie Bopp 414, Roy Kincaid 396."),
        T(person_id="WY-MONTGOMERY-KENNETH", name="Kenneth Montgomery", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Rolling Hills 4-year Vote-For-2: Kenneth Montgomery 90, Lori Cielinski 66, Glenn R. Lewis 63, Breanna Maines 45."),
        T(person_id="WY-CIELINSKI-LORI", name="Lori Cielinski", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2023], term_end=FM[2027], election_year=2022,
          sources=[SRC_C22], notes="Official 2022 Converse clerk, Councilperson Rolling Hills 4-year Vote-For-2: Kenneth Montgomery 90, Lori Cielinski 66."),
        T(person_id="WY-ETTLES-JODY", name="Jody Ettles", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Rolling Hills Vote-For-2: Jody Ettles 115, Donna Weaver 114, Emily Mayne 83. Official 2024 clerk did not print 2-year/4-year; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-WEAVER-DONNA", name="Donna Weaver", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_C24], confidence="medium",
          notes="Official 2024 Converse clerk, Councilperson Rolling Hills Vote-For-2: Jody Ettles 115, Donna Weaver 114."),
        T(person_id="WY-RIVERA-ANTHONY", name="Anthony Rivera", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council Town of Rolling Hills Vote-For-2: Anthony Rivera 70, Kenneth Montgomery 69, Deanna Brow 50, Kim Martin 42. Official 2026 clerk did not print 2-year/4-year; 4-year term follows the official 2022 4-year pattern."),
        T(person_id="WY-MONTGOMERY-KENNETH", name="Kenneth Montgomery", party="", office_group="municipal",
          office="Rolling Hills Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], confidence="medium",
          notes="Official 2026 Converse clerk, Council Town of Rolling Hills Vote-For-2: Anthony Rivera 70, Kenneth Montgomery 69."),
        T(person_id="WY-BOWDISH-CLIFTON", name="Clifton Bowdish", party="", office_group="municipal",
          office="Lost Springs Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Council Town of Lost Springs Vote-For-2: Clifton Bowdish 3, Nellie Bowdish 3. Official 2026 Lost Springs 2-year council was write-in totals 0 and is left unfilled. Official 2022 and 2024 Lost Springs council contests were write-in-only without a named certified winner and are left unfilled."),
        T(person_id="WY-BOWDISH-NELLIE", name="Nellie Bowdish", party="", office_group="municipal",
          office="Lost Springs Council", term_start=FM[2027], term_end=FM[2031], election_year=2026,
          sources=[SRC_C26], notes="Official 2026 Converse clerk, Council Town of Lost Springs Vote-For-2: Clifton Bowdish 3, Nellie Bowdish 3."),
    ]
    return terms


def school_terms():
    terms = []
    # CCSD #1: official 2022 Vote-For-4 (4-year), official 2024 Vote-For-5, official 2026 Vote-For-4 including official itemized write-in Adam Camino as the fourth-place finisher (Not Assigned 0).
    for pid, name, votes in (
        ("WY-BONER-TRENT", "Trent Boner", "1,732"),
        ("WY-MOORE-JOSH", "Josh Moore", "1,687"),
        ("WY-STINSON-SHANE", "Shane Stinson", "1,550"),
        ("WY-VOLLMAN-JARED", "Jared Vollman", "1,522"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Converse County School District #1 Trustee", term_start=FM[2023], term_end=FM[2027],
                       election_year=2022, sources=[SRC_C22],
                       notes=f"Official 2022 Converse clerk, CCSD #1 4-year Vote-For-4: Trent Boner 1,732, Josh Moore 1,687, Shane Stinson 1,550, Jared Vollman 1,522 (Dax McCarty 1,086 was fifth). This row: {name} {votes}."))
    for pid, name, votes in (
        ("WY-TILLARD-TY", "Ty Tillard", "2,846"),
        ("WY-REESE-BRAD", "Brad Reese", "2,433"),
        ("WY-DARR-JEREMIAH", "Jeremiah Darr", "2,398"),
        ("WY-FORGEY-JOHN-JC", 'John "J.C." Forgey', "2,317"),
        ("WY-HILL-STACI", "Staci Hill", "2,021"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Converse County School District #1 Trustee", term_start=FM[2025], term_end=FM[2029],
                       election_year=2024, sources=[SRC_C24],
                       notes=f"Official 2024 Converse clerk, CCSD #1 Vote-For-5: Ty Tillard 2,846, Brad Reese 2,433, Jeremiah Darr 2,398, John \"J.C.\" Forgey 2,317, Staci Hill 2,021 (James A. Bolinger 1,762 was sixth). This row: {name} {votes}."))
    for pid, name, votes in (
        ("WY-BONER-TRENT", "Trent Boner", "2,167"),
        ("WY-MOORE-JOSH", "Josh Moore", "2,023"),
        ("WY-MCCARTY-DAX", "Dax McCarty", "1,897"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Converse County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Converse clerk, CCSD #1 Vote-For-4: Trent Boner 2,167, Josh Moore 2,023, Dax McCarty 1,897, and official itemized write-in Adam Camino 320 of 571 write-in totals (Not Assigned 0). This row: {name} {votes}."))
    terms.append(T(person_id="WY-CAMINO-ADAM", name="Adam Camino", party="", office_group="schools",
                   office="Converse County School District #1 Trustee", term_start=FM[2027], term_end=FM[2031],
                   election_year=2026, how_took_office="elected", confidence="medium", sources=[SRC_C26],
                   notes="Official 2026 Converse clerk, CCSD #1 Vote-For-4, official itemized write-in: Adam Camino 320 of 571 write-in totals, Not Assigned 0. He is the official fourth-place finisher behind the three named candidates. No separate certified-write-in certificate was posted; seating is from the official canvass itemization."))

    for pid, name, votes in (
        ("WY-ALLEN-ROSS", "Ross Allen", "864"),
        ("WY-WILLIAMS-JARED", "Jared Williams", "814"),
        ("WY-GRANT-BRENDON", "Brendon Grant", "735"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Converse County School District #2 Trustee", term_start=FM[2025], term_end=FM[2029],
                       election_year=2024, sources=[SRC_C24],
                       notes=f"Official 2024 Converse clerk, CCSD #2 Vote-For-3: Ross Allen 864, Jared Williams 814, Brendon Grant 735 (Cathy Holman 624 was fourth). This row: {name} {votes}."))
    for pid, name, votes in (
        ("WY-TILLARD-CASEY", "Casey Tillard", "1,009"),
        ("WY-KINCAID-VIKI", "Viki Kincaid", "856"),
    ):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Converse County School District #2 Trustee", term_start=FM[2027], term_end=FM[2031],
                       election_year=2026, sources=[SRC_C26],
                       notes=f"Official 2026 Converse clerk, CCSD #2 Vote-For-2: Casey Tillard 1,009, Viki Kincaid 856. This row: {name} {votes}."))
    return terms


def special_terms():
    terms = []
    terms += [
        T(person_id="WY-MOORE-MORIAH", name="Moriah Moore", party="", office_group="special-districts",
          office="Conservation District At-Large Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Conservation Dist At-Large Supervisor: Moriah Moore 1,810, Kent Hill 1,176, Stan Mitchem 513."),
        T(person_id="WY-RIVERA-ANTHONY", name="Anthony Rivera", party="", office_group="special-districts",
          office="Conservation District Urban Supervisor, 2-year", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Conservation Dist Urban Supervisor 2-year: Anthony Rivera 3,255."),
        T(person_id="WY-SMITH-WAYNE", name="Wayne Smith", party="", office_group="special-districts",
          office="Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Conservation Dist Rural Supervisor Vote-For-2: Wayne Smith 2,661, Kenny Wolfley 2,560."),
        T(person_id="WY-WOLFLEY-KENNY", name="Kenny Wolfley", party="", office_group="special-districts",
          office="Conservation District Rural Supervisor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Conservation Dist Rural Supervisor Vote-For-2: Wayne Smith 2,661, Kenny Wolfley 2,560."),
        T(person_id="WY-FALKENBURG-SHELLY", name="Shelly Falkenburg", party="", office_group="special-districts",
          office="Conservation District Rural Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Rural Supervisor: Shelly Falkenburg 4,241, J.B. Wollen 1,489."),
        T(person_id="WY-DOWNS-SUSAN", name="Susan Downs", party="", office_group="special-districts",
          office="Conservation District Urban Supervisor", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Urban Supervisor: Susan Downs 5,287."),
        T(person_id="WY-BENGE-JACI", name="Jaci Benge", party="", office_group="special-districts",
          office="Senior Citizens Service District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Senior Citizens Service Dist Trustee Vote-For-2: Jaci Benge 2,185, Tim Ricker 2,175, Don Luhrsen 1,334."),
        T(person_id="WY-RICKER-TIM", name="Tim Ricker", party="", office_group="special-districts",
          office="Senior Citizens Service District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Senior Citizens Service Dist Trustee Vote-For-2: Jaci Benge 2,185, Tim Ricker 2,175."),
        T(person_id="WY-SHERIDAN-CINDY", name="Cindy Sheridan", party="", office_group="special-districts",
          office="Senior Citizens Service District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Senior Citizen Trustee Vote-For-3: Cindy Sheridan 4,370, Carolyn Lehner 3,806, J.B. Wollen 3,194."),
        T(person_id="WY-LEHNER-CAROLYN", name="Carolyn Lehner", party="", office_group="special-districts",
          office="Senior Citizens Service District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Senior Citizen Trustee Vote-For-3: Cindy Sheridan 4,370, Carolyn Lehner 3,806, J.B. Wollen 3,194."),
        T(person_id="WY-WOLLEN-JB", name="J.B. Wollen", party="", office_group="special-districts",
          office="Senior Citizens Service District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Senior Citizen Trustee Vote-For-3: Cindy Sheridan 4,370, Carolyn Lehner 3,806, J.B. Wollen 3,194."),
        T(person_id="WY-DOWNS-SALLY-J", name="Sally J. Downs", party="", office_group="special-districts",
          office="Cemetery District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Cemetery District Trustee Vote-For-1: Sally J. Downs 563, Michael Colling 336, John H. Dehler 220. Official 2026 Cemetery District Trustee 2-year was write-in-only (173 votes, many split spellings) and is left unfilled."),
        T(person_id="WY-DAMPMAN-LYNN", name="Lynn Dampman", party="", office_group="special-districts",
          office="Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Cemetery District Trustee Vote-For-3: Robert Nunn 1,222, Victor N. Ohman 1,188, Lynn Dampman 1,172."),
        T(person_id="WY-NUNN-ROBERT", name="Robert Nunn", party="", office_group="special-districts",
          office="Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Cemetery District Trustee Vote-For-3: Robert Nunn 1,222, Victor N. Ohman 1,188, Lynn Dampman 1,172."),
        T(person_id="WY-OHMAN-VICTOR-N", name="Victor N. Ohman", party="", office_group="special-districts",
          office="Cemetery District Trustee", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Converse clerk, Cemetery District Trustee Vote-For-3: Robert Nunn 1,222, Victor N. Ohman 1,188, Lynn Dampman 1,172."),
        T(person_id="WY-GOWING-SEAN", name="Sean Gowing", party="", office_group="special-districts",
          office="Hospital District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Hospital District Trustee Vote-For-3: Sean Gowing 915, write-in totals 91 (top itemized write-in Roy Kincaid 18). Only the named candidate is seated; the other two Vote-For-3 seats are left unfilled. Official 2024 hospital Vote-For-2 was write-in totals 194 with no official named certified winner and is left unfilled."),
        T(person_id="WY-MOULTON-KARIE", name="Karie Moulton", party="", office_group="special-districts",
          office="Hospital District Trustee, 2-year", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Hospital District Trustee 2-year Vote-For-1: Karie Moulton 1,020."),
        T(person_id="WY-COBB-JAMES-C", name="James C. Cobb", party="", office_group="special-districts",
          office="Sundance Meadows Special Improvement District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Sundance Meadows Special Improv Dist Vote-For-2: James C Cobb 213, Leslie C Collins 212. Official 2026 2-year contest was write-in totals 23, Not Assigned 23, and is left unfilled."),
        T(person_id="WY-COLLINS-LESLIE-C", name="Leslie C. Collins", party="", office_group="special-districts",
          office="Sundance Meadows Special Improvement District Trustee", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Converse clerk, Sundance Meadows Special Improv Dist Vote-For-2: James C Cobb 213, Leslie C Collins 212."),
    ]
    return terms


def expected_offices():
    mayors_councils = [
        ("Douglas Mayor", 1), ("Douglas Council", 6),
        ("Glenrock Mayor", 1), ("Glenrock Council", 4),
        ("Rolling Hills Mayor", 1), ("Rolling Hills Council", 4),
        ("Lost Springs Mayor", 1), ("Lost Springs Council", 4),
    ]
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 2 (S02)", 1), ("Senate District 23 (S23)", 1)],
        "state-house": [("House District 6 (H06)", 1), ("House District 62 (H62)", 1),
                        ("House District 3 (H03)", 1), ("House District 4 (H04)", 1)],
        "county": [("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": mayors_councils,
        "schools": [
            ("Converse County School District #1 Trustee", 9),
            ("Converse County School District #2 Trustee", 5),
        ],
        "special-districts": [
            ("Conservation District At-Large Supervisor", 1),
            ("Conservation District Urban Supervisor", 1),
            ("Conservation District Urban Supervisor, 2-year", 1),
            ("Conservation District Rural Supervisor", 2),
            ("Senior Citizens Service District Trustee", 5),
            ("Cemetery District Trustee", 3),
            ("Hospital District Trustee", 3),
            ("Hospital District Trustee, 2-year", 1),
            ("Sundance Meadows Special Improvement District Trustee", 2),
        ],
        "judicial": [
            ("District Judge, 8th Judicial District", 2),
            ("Circuit Judge, 8th Judicial District", 2),
        ],
    }


def build_converse():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    terms = []
    terms.extend(legislature_terms())
    terms.extend(county_terms())
    terms.extend(judicial_terms())
    terms.extend(municipal_terms())
    terms.extend(school_terms())
    terms.extend(special_terms())
    shared_path = ROOT / "data" / "county_officials" / "history" / "shared" / "federal-statewide-terms.json"
    shared = json.loads(shared_path.read_text())
    copied = 0
    for t in shared.get("terms") or shared:
        og = t.get("office_group") or ""
        office = t.get("office") or ""
        if og in {"federal", "statewide"}:
            terms.append(deepcopy(t)); copied += 1
        elif og == "judicial" and any(x in office for x in ("Supreme Court", "Chancery")):
            terms.append(deepcopy(t)); copied += 1
    H.attach_people_from_terms(terms, people)
    expected = expected_offices()
    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Official 2026 "
        "Converse clerk RETAIN JUDGE BEN BURNINGHAM is that statewide Chancery retention, not a local 8th JD seat. "
        "Local rows are 8th Judicial District judges (Converse, Goshen, Niobrara, and Platte). Full names are taken "
        "from official Wyoming Judicial Branch 8th JD Converse District Court, Converse (Douglas) Circuit Court, and "
        "Goshen (Torrington) Circuit Court pages, plus official Converse clerk retention lines, and those sources are "
        "cited. Judges of other districts are not copied here."
    )
    special_note = (
        "County, municipal, school, and special-district names are keyed from official Converse clerk general summaries "
        "(2020, 2022, 2024, and 2026), the official 2018 general EL45 (Clerk of District Court), and the official 2016 "
        "scanned general summary (2016 commissioners). Official 2014 and parts of official 2016 and 2018 local canvasses "
        "are archived but were not fully keyed here, so January 2015–2019 local rows are largely Not yet collected rather "
        "than invented. Multi-county legislative seats use official SOS district-wide Total rows, with the official "
        "Converse share noted. Official 2014 and 2018 SOS show a Senate District 23 Converse sliver; official 2022 and "
        "2026 SOS Converse rows for S23 are blank after redistricting. Official 2014–2020 SOS show House District 3 and "
        "House District 4 Converse slivers; official 2022+ Converse rows for those districts are blank, and House District "
        "62 (Converse and Natrona) begins with the official 2022 SOS. Douglas, Glenrock, Rolling Hills, and Lost Springs "
        "mayors are elected on the official November ballot, not chosen by the council. Official mid-term: approved "
        "April 10, 2026 commission minutes appoint Barbara Harris Clerk of District Court from April 10, 2026, through "
        "January 4, 2027, after Pam McCullough vacated the office; official 2026 clerk results elect Harris beginning "
        "January 4, 2027. Official 2026 CCSD #1 fourth-place finisher Adam Camino is the official itemized write-in "
        "(medium confidence). Official write-in-only contests without a named certified winner (including official 2022 "
        "and 2024 Lost Springs council, official 2022 Lost Springs mayor, official 2024 and 2026 some hospital and "
        "cemetery 2-year seats, and official 2026 Lost Springs 2-year council write-in totals 0) are left unfilled. "
        "Official DocumentCenter 4724 is the official 2022 primary commissioners recount, not a general-election change."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct roster "
        "is in data/county_officials/converse.json, from the official 2026 Converse primary (named winners only; 17 precincts)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Converse", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Converse", slug=SLUG)
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def _office(title, holders, *, layout="office-and-name", note=""):
    rec = {"office": title, "layout": layout, "holders": holders}
    if note:
        rec["note"] = note
    return rec


def _holder(people, pid, name, party, term_end, notes=""):
    p = people.get(pid) or {}
    h = {
        "name": name,
        "person_id": pid,
        "party": party or "",
        "term_end": term_end,
    }
    slug = p.get("slug")
    if slug:
        h["href"] = f"candidates/local-history/c/{slug}.html"
    if notes:
        h["notes"] = notes
    return h


def _holders_for_office(terms, people, office, as_of="2026-11-24", elect_start="2027-01-04"):
    """Current holders plus January 2027 elects, official terms only."""
    cur = [t for t in terms if t["office"] == office and t["term_start"] <= as_of < t["term_end"]]
    elects = [t for t in terms if t["office"] == office and t["term_start"] == elect_start]
    seen = set()
    out = []
    current_ids = {t["person_id"] for t in cur}
    def te(t):
        return "January " + t["term_end"][:4]
    for t in elects:
        if t["person_id"] in current_ids:
            out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
            seen.add(t["person_id"])
    for t in cur:
        if t["person_id"] in seen:
            continue
        out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
        seen.add(t["person_id"])
    for t in elects:
        if t["person_id"] in seen:
            continue
        out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
        seen.add(t["person_id"])
    return out


def update_converse_json(people, terms):
    path = ROOT / "data" / "county_officials" / "converse.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["county_number"] = CN
    data["term_switch_date"] = "2027-01-04"
    precincts = None
    for g in data.get("groups") or []:
        if g.get("id") == "precincts":
            precincts = g
            break

    def office_note(office):
        ts = [t for t in terms if t["office"] == office and t.get("notes")]
        as_of = "2026-11-24"
        relevant = [t for t in ts if (t["term_start"] <= as_of < t["term_end"]) or t["term_start"] >= "2026-11-01"]
        pool = relevant or ts
        pool = sorted(pool, key=lambda t: (t.get("election_year") or int(t["term_start"][:4])), reverse=True)
        if not pool:
            return ""
        seen = []
        for t in pool:
            n = t["notes"]
            if n and n not in seen:
                seen.append(n)
            if len(seen) == 2:
                break
        return " ".join(seen)

    senate = [_office("Senate District 2 (S02)", _holders_for_office(terms, people, "Senate District 2 (S02)"),
                      note=office_note("Senate District 2 (S02)"))]
    house = [
        _office("House District 6 (H06)", _holders_for_office(terms, people, "House District 6 (H06)"),
                note=office_note("House District 6 (H06)")),
        _office("House District 62 (H62)", _holders_for_office(terms, people, "House District 62 (H62)"),
                note=office_note("House District 62 (H62)")),
    ]
    county_offices = [
        "County Commissioner", "County Clerk", "County Treasurer", "County Assessor",
        "County Sheriff", "County Attorney", "Clerk of District Court", "County Coroner",
    ]
    county = [_office(o, _holders_for_office(terms, people, o), note=office_note(o)) for o in county_offices]

    mun_offices = [
        "Douglas Mayor", "Douglas Council", "Glenrock Mayor", "Glenrock Council",
        "Rolling Hills Mayor", "Rolling Hills Council", "Lost Springs Mayor", "Lost Springs Council",
    ]
    municipal = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                         layout="heading-then-names" if "Council" in o else "office-and-name")
                 for o in mun_offices]
    school_offices = [
        "Converse County School District #1 Trustee",
        "Converse County School District #2 Trustee",
    ]
    schools = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                       layout="heading-then-names") for o in school_offices]
    special_offices = [
        "Conservation District At-Large Supervisor",
        "Conservation District Urban Supervisor",
        "Conservation District Urban Supervisor, 2-year",
        "Conservation District Rural Supervisor",
        "Senior Citizens Service District Trustee",
        "Cemetery District Trustee",
        "Hospital District Trustee",
        "Hospital District Trustee, 2-year",
        "Sundance Meadows Special Improvement District Trustee",
    ]
    specials = [_office(o, _holders_for_office(terms, people, o), note=office_note(o),
                        layout="heading-then-names" if "Trustee" in o or "Rural" in o else "office-and-name")
                for o in special_offices]
    judicial_offices = [
        "District Judge, 8th Judicial District",
        "Circuit Judge, 8th Judicial District",
    ]
    # Current judges only (do not list January 2027 elects as separate judicial rows unless already retained into a new term).
    judicial = [_office(o, _holders_for_office(terms, people, o), note=office_note(o)) for o in judicial_offices]

    groups = [
        {"id": "state-senate", "label": "Wyoming Senate", "offices": senate},
        {"id": "state-house", "label": "Wyoming House", "offices": house},
        {"id": "county", "label": "County offices", "offices": county},
        {"id": "municipal", "label": "Municipal offices", "offices": municipal},
        {"id": "schools", "label": "School boards", "offices": schools},
        {"id": "special-districts", "label": "Special districts", "offices": specials},
        {"id": "judicial", "label": "Judicial", "offices": judicial},
    ]
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_C26,
        "primary_results": URL_P26,
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/converse/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
