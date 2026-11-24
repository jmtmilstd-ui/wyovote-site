#!/usr/bin/env python3
"""Big Horn County officeholder history (preview). Official clerk, SOS, court,
and municipal sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import ROOT, src_dict, term

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
CN = 9
SLUG = "big-horn"

URL_COUNTY = "https://bighorncountywy.gov/"
URL_ELEC = "https://bighorncountywy.gov/departments/clerk/elections"
URL_COMM = "https://bighorncountywy.gov/departments/commissioners"
URL_CLERK = "https://bighorncountywy.gov/departments/clerk"
URL_ASSESSOR = "https://bighorncountywy.gov/departments/assessor"
URL_TREAS = "https://bighorncountywy.gov/departments/treasurer"
URL_SHERIFF = "https://bighorncountywy.gov/departments/sheriff/staff"
URL_ATTORNEY = "https://bighorncountywy.gov/departments/attorney"
URL_CDC = "https://bighorncountywy.gov/departments/clerk-of-district-court"
URL_CORONER = "https://bighorncountywy.gov/departments/coroner"
URL_2026_GEN = "https://bighorncountywy.gov/images/Official_General_Election_Summary_Report_2026.pdf"
URL_2026_PRI = "https://bighorncountywy.gov/images/Official_BHC_Primary_Election_Summary_Report_2026.pdf"
URL_2024_GEN = "https://bighorncountywy.gov/images/Website_Official_General_Election_Summary_Report.pdf"
URL_2022_GEN = "https://bighorncountywy.gov/component/edocman/official-2022-general-election-results/viewdocument/772?Itemid="
URL_2026_FILING = "https://bighorncountywy.gov/images/Big_Horn_County_GENERAL_Candidate_Listpdf.pdf"


def S(label, url=""):
    return src_dict(label, url)


def sos_url(year, chamber):
    ch = "Senate" if chamber == "Senate" else "House"
    if year in (2012, 2014, 2018):
        return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Statewide_{ch}_Candidates_Summary.pdf"
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_General_Statewide_{ch}_Candidates_Summary.pdf"


def sos_src(year, chamber):
    return S(
        f"Official Wyoming SOS {year} statewide {chamber} candidates summary (district-wide Total row)",
        sos_url(year, chamber),
    )


def T(**kw):
    kw.setdefault("confidence", "high")
    kw.setdefault("how_took_office", "elected")
    if "sources" not in kw:
        kw["sources"] = []
    return term(**kw)


SRC_COMM = S("Official Big Horn County Commissioners page, retrieved 2026-11-24", URL_COMM)
SRC_CLERK = S("Official Big Horn County Clerk page / official 2026 canvass minutes naming County Clerk Lori Smallwood, retrieved 2026-11-24", URL_CLERK)
SRC_ASSESSOR = S("Official Big Horn County Assessor page, retrieved 2026-11-24: Cozette Winters, County Assessor", URL_ASSESSOR)
SRC_TREAS = S("Official Big Horn County Treasurer page, retrieved 2026-11-24: Nicole Vigil", URL_TREAS)
SRC_SHERIFF = S("Official Big Horn County Sheriff Staff page, retrieved 2026-11-24: Sheriff Jason Beal; Undersheriff Craig Shidler", URL_SHERIFF)
SRC_ATTORNEY = S("Official Big Horn County Attorney page, retrieved 2026-11-24: Marcia Bean, Big Horn County & Prosecuting Attorney", URL_ATTORNEY)
SRC_CDC = S("Official 2026 Big Horn clerk Official Results Summary, Clerk of District Court: REP SERENA K. LIPP 3,824", URL_2026_GEN)
SRC_CORONER = S("Official Big Horn County Coroner page, retrieved 2026-11-24: Michael K. Jameson", URL_CORONER)
SRC_ELEC = S("Official Big Horn County Clerk Elections page, retrieved 2026-11-24", URL_ELEC)
SRC_2026 = S(
    "Official Big Horn County General Election Summary Report, November 3, 2026 "
    "(header OFFICIAL RESULTS, GENERAL ELECTION; Precincts Complete 13 of 13; Ballots Cast - Total 4,200; "
    "footer Election Summary - 11/05/2026 04:26PM, Page 1 of 21). Born-digital official canvass. "
    "The official canvass certification is dated 11/5/2026 and signed by the County Clerk and canvassing board.",
    URL_2026_GEN,
)
SRC_2026_MIN = S(
    "Official Big Horn County Canvassing Board Minutes, General Election November 3, 2026, session November 5, 2026, 2:00 p.m. "
    "(County Clerk Lori Smallwood; post-election audit with no material errors).",
    "https://bighorncountywy.gov/images/2026_General_Canvass_Minutes.pdf",
)
SRC_2026_PRI = S(
    "Official Big Horn County Primary Election Summary, August 18, 2026 "
    "(header OFFICIAL RESULTS, Primary Election; footer Election Summary - 08/20/2026 04:50PM, Page 1 of 23; "
    "Ballots Cast - Total 3,973). Signed official canvass.",
    URL_2026_PRI,
)
SRC_2026_FILING = S("Official Big Horn County 2026 General Candidate Roster (official clerk filings)", URL_2026_FILING)
SRC_2024 = S(
    "Official Big Horn County General Election Summary, November 5, 2024 "
    "(header OFFICIAL RESULTS, General Election; Ballots Cast - Total 5,788; "
    "footer Election Summary - 11/08/2024 11:57AM, Page 1 of 15). Signed official canvass (Lori Smallwood; Deb Craft 11/8/24).",
    URL_2024_GEN,
)
SRC_2022 = S(
    "Official Big Horn County General Election Custom Table Report, November 8, 2022 "
    "(header OFFICIAL RESULTS, Big HornWY General Election 221108; footer Custom Table Report - 11/10/2022 09:16AM). "
    "Posted as Official 2022 General Election Results from the official elections page.",
    URL_2022_GEN,
)
SRC_COURT = S(
    "Official Wyoming Judicial Branch March 2026 roster titles already used in the official Park and Washakie histories: "
    "Fifth Judicial District Judge Bobbi Overfield (Big Horn/Hot Springs/Washakie); "
    "Fifth Judicial Circuit Judge Ed Luhm (Edward G. Luhm) (Big Horn/Hot Springs/Washakie); "
    "Fifth Judicial District Judge Bill Simpson (Park); Circuit Judge Joey Darrah (Park).",
    "",
)


def register_people(P):
    # Legislature
    P("WY-PETERSON-R", "R. Ray Peterson", "R. Ray", "Peterson")
    P("WY-KOST-RJ", "R. J. Kost", "R. J.", "Kost", aliases="R.J. Kost; RJ Kost; R. J. KOST")
    P("WY-LAURSEN-DAN", "Dan Laursen", "Dan", "Laursen")
    P("WY-GEIS-GERALD-E", "Gerald E. Geis", "Gerald", "Geis", middle="E.")
    P("WY-AGAR-WYATT", "Wyatt Agar", "Wyatt", "Agar")
    P("WY-COOPER-ED", "Ed Cooper", "Ed", "Cooper")
    P("WY-HARVEY-ELAINE-D", "Elaine D. Harvey", "Elaine", "Harvey", middle="D.")
    P("WY-COLLINS-JOYCE", "Joyce Collins", "Joyce", "Collins")
    P("WY-FLITNER-JAMIE", "Jamie Flitner", "Jamie", "Flitner")
    P("WY-BANKS-DALTON", "Dalton Banks", "Dalton", "Banks")
    P("WY-GREEAR-MIKE", "Mike Greear", "Mike", "Greear", aliases="Michael D. Greear")
    P("WY-LAWLEY-MARTHA", "Martha Lawley", "Martha", "Lawley")
    P("WY-WINTERS-NATHAN", "Nathan Winters", "Nathan", "Winters")
    P("WY-WINTER-JOHN-R", "John R. Winter", "John", "Winter", middle="R.", aliases="John Winter")
    P("WY-HOGG-ALLEN", "Allen Hogg", "Allen", "Hogg")
    # County
    P("WY-CRAFT-DEB", "Deb Craft", "Deb", "Craft")
    P("WY-JOLLEY-BRUCE-H", "Bruce H. Jolley", "Bruce", "Jolley", middle="H.")
    P("WY-NEVES-DAVE", "Dave Neves", "Dave", "Neves")
    P("WY-BOARDMAN-JARED", "Jared Boardman", "Jared", "Boardman")
    P("WY-LAIRD-MIKE", "Mike Laird", "Mike", "Laird")
    P("WY-SMALLWOOD-LORI", "Lori Smallwood", "Lori", "Smallwood")
    P("WY-VIGIL-NICOLE", "Nicole Vigil", "Nicole", "Vigil")
    P("WY-WINTERS-COZETTE", "Cozette Winters", "Cozette", "Winters")
    P("WY-BEAL-JASON", "Jason Beal", "Jason", "Beal")
    P("WY-SHIDLER-CRAIG-R", "Craig R. Shidler", "Craig", "Shidler", middle="R.", aliases="Craig Shidler")
    P("WY-BEAN-MARCIA-E", "Marcia E. Bean", "Marcia", "Bean", middle="E.", aliases="Marcia Bean")
    P("WY-LIPP-SERENA-K", "Serena K. Lipp", "Serena", "Lipp", middle="K.")
    P("WY-JAMESON-MICHAEL-K", "Michael K. Jameson", "Michael", "Jameson", middle="K.")
    # Judicial (reuse official IDs)
    P("WY-OVERFIELD-BOBBI", "Bobbi Overfield", "Bobbi", "Overfield")
    P("WY-LUHM-ED", "Ed Luhm", "Ed", "Luhm", aliases="Edward G. Luhm; EDWARD G. LUHM")
    P("WY-SIMPSON-BILL", "Bill Simpson", "Bill", "Simpson")
    P("WY-DARRAH-JOEY", "Joey Darrah", "Joey", "Darrah", aliases="S. Joseph Joey Darrah")
    # Municipal current and elects
    P("WY-DUNCAN-CJ", "CJ Duncan", "CJ", "Duncan")
    P("WY-HOPKIN-CHARLES", "Charles (Chuck) Hopkin", "Charles", "Hopkin", aliases="Chuck Hopkin; CHARLES (CHUCK) HOPKIN; Charles E. Hopkin; CHARLES E. HOPKIN")
    P("WY-DESROSIER-STUART", "Stuart Desrosier", "Stuart", "Desrosier")
    P("WY-TANNER-MICHAEL", "Michael Tanner", "Michael", "Tanner")
    P("WY-RILEY-JENNIFER-S", "Jennifer S. Riley", "Jennifer", "Riley", middle="S.")
    P("WY-DELLOS-MIKE", "Mike Dellos", "Mike", "Dellos")
    P("WY-WEEKS-LINDA", "Linda Weeks", "Linda", "Weeks")
    P("WY-GEORGE-GERALD", "Gerald \"Jerry\" George", "Gerald", "George", aliases="Jerry George")
    P("WY-BRUNKO-GARY", "Gary Brunko", "Gary", "Brunko")
    P("WY-HIBBERT-DON", "Don Hibbert", "Don", "Hibbert")
    P("WY-BOOTH-JENNY", "Jenny Booth", "Jenny", "Booth")
    P("WY-LEONHARDT-MELISSA", "Melissa Leonhardt", "Melissa", "Leonhardt")
    P("WY-HARRINGTON-MICHAEL-J", "Michael J. Harrington", "Michael", "Harrington", middle="J.")
    P("WY-HAMILTON-JESSIE", "Jessie Hamilton", "Jessie", "Hamilton")
    P("WY-CLARK-ALLAN-P", "Allan P. Clark", "Allan", "Clark", middle="P.", aliases="Allan Clark")
    P("WY-BRIGHTLY-MIKE", "Mike Brightly", "Mike", "Brightly")
    P("WY-SANDERS-KARMA", "Karma Sanders", "Karma", "Sanders")
    P("WY-HESSENTHALER-BRANDON", "Brandon Hessenthaler", "Brandon", "Hessenthaler")
    P("WY-ABRAHAM-SHAE-C", "Shae C. Abraham", "Shae", "Abraham", middle="C.")
    P("WY-PETERSON-JOEL", "Joel Peterson", "Joel", "Peterson")
    P("WY-WINTERS-STEPHEN", "Stephen Winters", "Stephen", "Winters")
    P("WY-LEWIS-MAX", "Max Lewis", "Max", "Lewis")
    P("WY-JOHNSON-ROB", "Rob Johnson", "Rob", "Johnson")
    P("WY-CROSBY-SCOTT", "Scott Crosby", "Scott", "Crosby")
    P("WY-WOODIS-DEXTER", "Dexter Woodis", "Dexter", "Woodis")
    P("WY-CAMP-BILL", "Bill Camp", "Bill", "Camp")
    P("WY-LOFTUS-NICK", "Nick Loftus", "Nick", "Loftus")
    P("WY-BEALL-ASPEN", "Aspen Beall", "Aspen", "Beall")
    P("WY-CROUCH-SHAUNA", "Shauna Crouch", "Shauna", "Crouch")
    P("WY-JAMES-KAYLA", "Kayla James", "Kayla", "James")
    P("WY-SPANN-KELLY", "Kelly Spann", "Kelly", "Spann")
    P("WY-RICHARDSON-STEVE", "Steve Richardson", "Steve", "Richardson")
    P("WY-FRESCOLN-GARRET-I", "Garret I. Frescoln", "Garret", "Frescoln", middle="I.")
    P("WY-GANOUNG-ROGER", "Roger Ganoung", "Roger", "Ganoung")
    P("WY-CLENDENEN-SHANG", "Shang Clendenen", "Shang", "Clendenen")
    P("WY-DESANTIS-GUY", "Guy DeSantis", "Guy", "DeSantis", aliases="GUY DESANTIS; Guy T. DeSantis")
    P("WY-POOLE-KEARA", "Keara Poole", "Keara", "Poole")
    P("WY-ELLIS-JOHN", "John Ellis", "John", "Ellis")
    P("WY-FOLEY-MYLES-R", "Myles R. Foley", "Myles", "Foley", middle="R.")
    P("WY-JOHNSTON-MICHAEL", "Michael Johnston", "Michael", "Johnston")
    P("WY-DOOLEY-CHRIS", "Chris Dooley", "Chris", "Dooley")
    P("WY-CRIST-GERALD", "Gerald Crist", "Gerald", "Crist")
    P("WY-SKILLMAN-ROBERT-C", "Robert C. Skillman Jr.", "Robert", "Skillman", middle="C.", aliases="ROBERT C. SKILLMAN JR.")
    P("WY-WILLIAMSON-BOB", "Bob Williamson", "Bob", "Williamson")
    P("WY-NEWMAN-TOM", "Tom Newman", "Tom", "Newman")
    P("WY-GRANT-MICHAEL-LEE", "Michael Lee Grant", "Michael Lee", "Grant")
    P("WY-MILLER-CAROL", "Carol Miller", "Carol", "Miller")
    P("WY-MANGUS-ROBERT", "Robert Mangus", "Robert", "Mangus")
    P("WY-ANDERSON-DANIEL-L", "Daniel L. Anderson", "Daniel", "Anderson", middle="L.")
    P("WY-PATRICK-ROD", "Rod Patrick", "Rod", "Patrick")
    P("WY-DUNCAN-WILLIAM-S", "William S. Duncan", "William", "Duncan", middle="S.")
    P("WY-SANFORD-SHARON", "Sharon Sanford", "Sharon", "Sanford")
    P("WY-SAUNDERS-THEA", "Thea Saunders", "Thea", "Saunders")
    P("WY-SAUNDERS-CHRISTOPHER-M", "Christopher M. Saunders", "Christopher", "Saunders", middle="M.", aliases="Christopher Saunders")
    P("WY-DRIVER-ALETA", "Aleta Driver", "Aleta", "Driver")
    P("WY-APPLEGARTH-HOWARD", "Howard Applegarth", "Howard", "Applegarth")
    # Schools
    P("WY-FULLER-WENDY", "Wendy Fuller", "Wendy", "Fuller")
    P("WY-RASMUSSEN-DICKSON-AJ", "AJ Rasmussen-Dickson", "AJ", "Rasmussen-Dickson")
    P("WY-JONES-CRAIG-A", "Craig A. Jones", "Craig", "Jones", middle="A.")
    P("WY-CHRISTENSEN-HIEDI-J", "Hiedi J. Christensen", "Hiedi", "Christensen", middle="J.")
    P("WY-MICHAELS-HOLLY", "Holly Michaels", "Holly", "Michaels")
    P("WY-LEONHARDT-EMILY-R", "Emily R. Leonhardt", "Emily", "Leonhardt", middle="R.")
    P("WY-ANGELL-C-TYLER", "C. Tyler Angell", "C. Tyler", "Angell")
    P("WY-ANDERSON-LANCE-E", "Lance E. Anderson", "Lance", "Anderson", middle="E.", aliases="Lance E. Anderson, DMD")
    P("WY-BAIR-STACY", "Stacy Bair", "Stacy", "Bair")
    P("WY-PETERSON-TESS-L", "Tess L. Peterson", "Tess", "Peterson", middle="L.")
    P("WY-WALKER-BEN", "Ben Walker", "Ben", "Walker")
    P("WY-LEITHEAD-KYLE", "Kyle Leithead", "Kyle", "Leithead")
    P("WY-JOLLEY-DANNY", "Danny Jolley", "Danny", "Jolley")
    P("WY-FELKINS-RYAN", "Ryan Felkins", "Ryan", "Felkins")
    P("WY-FLITNER-PAM", "Pam Flitner", "Pam", "Flitner")
    P("WY-DALIN-TODD", "Todd Dalin", "Todd", "Dalin")
    P("WY-JONES-BETTE-RAE", "Bette Rae Jones", "Bette Rae", "Jones")
    P("WY-WHALEY-MIKE", "Mike Whaley", "Mike", "Whaley")
    P("WY-ROBERTSON-WILLIAM-D", "William D. Robertson", "William", "Robertson", middle="D.")
    P("WY-MURRAY-LYNETTE", "Lynette Murray", "Lynette", "Murray")
    P("WY-ZELLER-LUKE-MAXSON", "Luke Maxson Zeller", "Luke Maxson", "Zeller")
    P("WY-OSMOND-LINDA", "Linda Osmond", "Linda", "Osmond")
    P("WY-HOPKIN-HEATH", "Heath Hopkin", "Heath", "Hopkin")
    P("WY-SCHLATTMANN-KRISTEN", "Kristen Schlattmann", "Kristen", "Schlattmann")
    P("WY-BUTCHER-PRICIE", "Pricie Butcher", "Pricie", "Butcher")
    P("WY-POWELL-MERRITA", "Merrita Powell", "Merrita", "Powell")
    P("WY-GLOY-GREGORY", "Gregory Gloy", "Gregory", "Gloy")
    P("WY-WOOD-BRENDA", "Brenda Wood", "Brenda", "Wood")
    P("WY-GODFREY-BRENT", "Brent Godfrey", "Brent", "Godfrey")
    P("WY-SIMMONS-EMILY-ANNE", "Emily Anne Simmons", "Emily Anne", "Simmons")
    P("WY-GILLETT-STEVE", "Steve Gillett", "Steve", "Gillett")
    P("WY-JOLLEY-BLAINE", "Blaine Jolley", "Blaine", "Jolley")
    P("WY-MIARS-DEAN-S", "Dean S. Miars", "Dean", "Miars", middle="S.")
    P("WY-BANKS-DAVID-V", "David V. Banks", "David", "Banks", middle="V.")
    register_special_people(P)


def _add(terms, pid, name, office, group, start, end, year, sources, notes, party="", how="elected", conf="high", **extra):
    rec = T(
        person_id=pid, name=name, office=office, office_group=group,
        term_start=start, term_end=end, election_year=year, sources=sources,
        notes=notes, party=party, how_took_office=how, confidence=conf, **extra,
    )
    terms.append(rec)
    return rec



def legislature_terms():
    """Official SOS district-wide Totals, with the official Big Horn share noted.
    Two-column official SOS pages are cut at the next district header; official
    totals already keyed in the Park, Washakie, and Fremont histories are reused.
    """
    terms = []
    def leg(pid, name, office, start, end, year, chamber, notes, party="Republican"):
        _add(terms, pid, name, office, "state-senate" if "Senate" in office else "state-house",
             start, end, year, [sos_src(year, chamber)], notes, party=party)

    # S19 (Big Horn + Park)
    leg("WY-PETERSON-R", "R. Ray Peterson", "Senate District 19 (S19)",
        "2015-01-05", "2019-01-07", 2014, "Senate",
        "Official 2014 SOS statewide Senate summary, Senate District 19: R. Ray Peterson (R) Total 4,847. Official Big Horn share 2,651; official Park share 2,196.")
    leg("WY-KOST-RJ", "R. J. Kost", "Senate District 19 (S19)",
        "2019-01-07", "2023-01-02", 2018, "Senate",
        "Official 2018 SOS statewide Senate summary, Senate District 19 (left column beside Senate District 21; that district's Total is not used): R. J. Kost (R) Total 5,569. Official Big Horn share 2,710; official Park share 2,859.")
    leg("WY-LAURSEN-DAN", "Dan Laursen", "Senate District 19 (S19)",
        "2023-01-02", "2027-01-04", 2022, "Senate",
        "Official 2022 SOS statewide Senate summary, Senate District 19: Dan Laursen (R) Total 5,538. Official Big Horn share 2,637; official Park share 2,901.")
    leg("WY-KOST-RJ", "R. J. Kost", "Senate District 19 (S19)",
        "2027-01-04", "2031-01-06", 2026, "Senate",
        "Official 2026 SOS statewide Senate summary, Senate District 19: R. J. Kost (R) Total 5,311. Official Big Horn share 2,562 (official clerk abstract same 2,562); official Park share 2,749. Takes office January 2027.")

    # S20 (Big Horn, Washakie, Hot Springs, Park, Fremont) — official Totals from sister-county official SOS notes
    leg("WY-GEIS-GERALD-E", "Gerald E. Geis", "Senate District 20 (S20)",
        "2013-01-07", "2017-01-02", 2012, "Senate",
        "Official 2012 SOS statewide Senate summary, Senate District 20: Gerald E. Geis (R) Total 7,592. Official Big Horn share 1,245; official Washakie 3,456, Hot Springs 2,164, Fremont 317, Park 410.")
    leg("WY-AGAR-WYATT", "Wyatt Agar", "Senate District 20 (S20)",
        "2017-01-02", "2021-01-04", 2016, "Senate",
        "Official 2016 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18; not the District 18 Total): Wyatt Agar (R) Total 6,893, Mary Jane Norskog (D) 1,546. Official Big Horn share Agar 1,225, Norskog 151.")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)",
        "2021-01-04", "2025-01-06", 2020, "Senate",
        "Official 2020 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18): Ed Cooper (R) Total 7,497, Theresa Livingston (D) 1,293. Official Big Horn share Cooper 1,358, Livingston 171.")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)",
        "2025-01-06", "2029-01-01", 2024, "Senate",
        "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Big Horn share 1,475 (official 2024 clerk canvass same 1,475); official Washakie 3,442, Hot Springs 2,180, Park 834, Fremont 305. Off-cycle in 2026.")

    # H26 (Big Horn + small Park share)
    leg("WY-HARVEY-ELAINE-D", "Elaine D. Harvey", "House District 26 (H26)",
        "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 26: Elaine D. Harvey (R) Total 3,446. Official Big Horn share 3,298; official Park share 148.")
    leg("WY-HARVEY-ELAINE-D", "Elaine D. Harvey", "House District 26 (H26)",
        "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 26: Elaine D. Harvey (R) Total 1,907, Joyce Collins (C) 1,179. Official Big Horn share Harvey 1,827, Collins 1,143; official Park Harvey 80, Collins 36.")
    leg("WY-FLITNER-JAMIE", "Jamie Flitner", "House District 26 (H26)",
        "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 26 (right column of a two-column official page): Jamie Flitner (R) Total 2,665, Jean Petty (D) 384, Joyce Collins (C) 1,001. Official Big Horn share Flitner 2,550, Petty 372, Collins 966; official Park Flitner 115, Petty 12, Collins 35.")
    leg("WY-FLITNER-JAMIE", "Jamie Flitner", "House District 26 (H26)",
        "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 26 (left column beside House District 27; that district's Total is not used): Jamie Flitner (R) Total 2,832. Official Big Horn share 2,714; official Park share 118.")
    leg("WY-FLITNER-JAMIE", "Jamie Flitner", "House District 26 (H26)",
        "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 26: Jamie Flitner (R) Total 3,959. Official Big Horn share 3,795; official Park share 164.")
    leg("WY-BANKS-DALTON", "Dalton Banks", "House District 26 (H26)",
        "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 26: Dalton Banks (R) Total 2,931. Official Big Horn share 2,636; official Park share 295.")
    leg("WY-BANKS-DALTON", "Dalton Banks", "House District 26 (H26)",
        "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 26: Dalton Banks (R) Total 3,942. Official Big Horn share 3,584; official Park share 358.")
    leg("WY-BANKS-DALTON", "Dalton Banks", "House District 26 (H26)",
        "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 26: Dalton Banks (R) Total 2,557, Ralph Nieder-Westermann (D) 571. Official Big Horn share Banks 2,301, Nieder-Westermann 538 (official clerk abstract same); official Park Banks 256, Nieder-Westermann 33. Re-elected.")

    # H27 (Big Horn + Washakie) — official Totals from the official Washakie history
    leg("WY-GREEAR-MIKE", "Mike Greear", "House District 27 (H27)",
        "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 27: Mike Greear (R) Total 3,627. Official Big Horn share 231; official Washakie 3,396.")
    leg("WY-GREEAR-MIKE", "Mike Greear", "House District 27 (H27)",
        "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 27: Mike Greear (R) Total 2,650. Official Big Horn share 166; official Washakie 2,484.")
    leg("WY-GREEAR-MIKE", "Mike Greear", "House District 27 (H27)",
        "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 27 (left column beside House District 28; that district's Total is not used): Michael D. Greear (R) 3,304, Robert D. McDonough, Jr. (D) 565. Official Big Horn share Greear 227, McDonough 24.")
    leg("WY-GREEAR-MIKE", "Mike Greear", "House District 27 (H27)",
        "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 27 (right column beside House District 26; that district's Total is not used): Mike Greear (R) Total 2,892. Official Big Horn share 179; official Washakie 2,713.")
    leg("WY-GREEAR-MIKE", "Mike Greear", "House District 27 (H27)",
        "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 27: Mike Greear (R) Total 3,763. Official Big Horn share 269; official Washakie 3,494.")
    leg("WY-LAWLEY-MARTHA", "Martha Lawley", "House District 27 (H27)",
        "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 27: Martha Lawley (R) Total 3,143. Official Big Horn share 430; official Washakie 2,713.")
    leg("WY-LAWLEY-MARTHA", "Martha Lawley", "House District 27 (H27)",
        "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 27: Martha Lawley (R) Total 3,918. Official Big Horn share 539; official Washakie 3,379.")
    leg("WY-LAWLEY-MARTHA", "Martha Lawley", "House District 27 (H27)",
        "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Big Horn share Lawley 418, Livingston 60 (official clerk abstract same); official Washakie Lawley 2,282, Livingston 430. Re-elected.")

    # H28 — official Totals from the official Fremont history
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 28: Nathan Winters (R) Total 3,288, Connie Skates (D) 1,100. Official Big Horn share Winters 954, Skates 164.")
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 28: Nathan Winters (R) Total 2,989. Official Big Horn share 831.")
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): Nathan Winters (R) Total 3,510, Howard Samelson (D) 980. Official Big Horn share Winters 1,017, Samelson 122.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 28: John R. Winter (R) Total 2,906, Howie Samelson (D) 954. Official Big Horn share Winter 846, Samelson 110. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): John R. Winter (R) Total 3,769, Levi J. Shinkle (D) 816. Official Big Horn share Winter 1,128, Shinkle 123.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,139, Kimberly M. Bartlett (D) 855. Official Big Horn share Winter 644, Bartlett 90.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Big Horn share Winter 920, Alwin 85.")
    leg("WY-HOGG-ALLEN", "Allen Hogg", "House District 28 (H28)",
        "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 28: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504. Official Big Horn share Hogg 655, Alwin 66 (official clerk abstract same 655-66). Takes office January 2027.")
    return terms


def county_terms():
    terms = []
    _add(terms, "WY-CRAFT-DEB", "Deb Craft", "County Commissioner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM],
         "Official commissioners page, retrieved 2026-11-24: Deb Craft, Commission Chairman. Official 2024 canvass elected only Bruce H. Jolley (at large). This seat is on the official 2026 ballot (vote for 2).",
         party="Republican")
    _add(terms, "WY-NEVES-DAVE", "Dave Neves", "County Commissioner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM],
         "Official commissioners page, retrieved 2026-11-24: Dave Neves. Official 2022 class (the official 2024 canvass elected only Bruce H. Jolley).",
         party="Republican")
    _add(terms, "WY-JOLLEY-BRUCE-H", "Bruce H. Jolley", "County Commissioner", "county",
         "2025-01-06", "2029-01-01", 2024, [SRC_COMM, SRC_2024],
         "Official commissioners page, retrieved 2026-11-24: Bruce H. Jolley. Official 2024 canvass, County Commissioner: REP BRUCE H. JOLLEY 5,081, write-ins 107, contest totals 5,788.",
         party="Republican")
    _add(terms, "WY-LAIRD-MIKE", "Mike Laird", "County Commissioner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_2026_FILING],
         "Official 2026 canvass, County Commissioner (vote for 2): REP MIKE LAIRD 3,159, REP JARED BOARDMAN 2,991, write-ins 76, contest totals 8,400. Takes office January 2027.",
         party="Republican")
    _add(terms, "WY-BOARDMAN-JARED", "Jared Boardman", "County Commissioner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_2026_FILING],
         "Official 2026 canvass, County Commissioner (vote for 2): REP JARED BOARDMAN 2,991, REP MIKE LAIRD 3,159. Official 2024 school trustee Area A winner; that school term is encoded separately.",
         party="Republican")

    def row(pid, name, office, src, note, year=2022, start="2023-01-02", end="2027-01-04", party="Republican"):
        _add(terms, pid, name, office, "county", start, end, year, src, note, party=party)
        _add(terms, pid, name, office, "county", "2027-01-04", "2031-01-06", 2026, [SRC_2026],
             note + " Official 2026 general: re-elected.", party=party)

    _add(terms, "WY-SMALLWOOD-LORI", "Lori Smallwood", "County Clerk", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CLERK, SRC_2026_MIN],
         "Official 2026 canvass minutes name County Clerk Lori Smallwood. Official 2026 general: REP LORI SMALLWOOD 3,789, re-elected.",
         party="Republican")
    _add(terms, "WY-SMALLWOOD-LORI", "Lori Smallwood", "County Clerk", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, County Clerk: REP LORI SMALLWOOD 3,789, write-ins 23, contest totals 4,200.",
         party="Republican")
    _add(terms, "WY-VIGIL-NICOLE", "Nicole Vigil", "County Treasurer", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_TREAS],
         "Official treasurer page, retrieved 2026-11-24: Nicole Vigil. Official 2026 general: REP NICOLE VIGIL 3,707, re-elected.",
         party="Republican")
    _add(terms, "WY-VIGIL-NICOLE", "Nicole Vigil", "County Treasurer", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, County Treasurer: REP NICOLE VIGIL 3,707, write-ins 34, contest totals 4,200.",
         party="Republican")
    _add(terms, "WY-WINTERS-COZETTE", "Cozette Winters", "County Assessor", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_ASSESSOR],
         "Official assessor page, retrieved 2026-11-24: Cozette Winters, County Assessor. Official 2026 general: REP COZETTE WINTERS 3,738, re-elected.",
         party="Republican")
    _add(terms, "WY-WINTERS-COZETTE", "Cozette Winters", "County Assessor", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, County Assessor: REP COZETTE WINTERS 3,738, write-ins 19, contest totals 4,200.",
         party="Republican")
    _add(terms, "WY-BEAL-JASON", "Jason Beal", "County Sheriff", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_SHERIFF],
         "Official Sheriff Staff page, retrieved 2026-11-24: Sheriff Jason Beal. Official 2026 general elects Craig R. Shidler (undersheriff on the same official staff page).",
         party="Republican")
    _add(terms, "WY-SHIDLER-CRAIG-R", "Craig R. Shidler", "County Sheriff", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_SHERIFF],
         "Official 2026 canvass, County Sheriff: REP CRAIG R. SHIDLER 3,702, write-ins 137, contest totals 4,200. Takes office January 2027.",
         party="Republican")
    _add(terms, "WY-BEAN-MARCIA-E", "Marcia E. Bean", "County Attorney", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_ATTORNEY],
         "Official attorney page, retrieved 2026-11-24: Marcia Bean, Big Horn County & Prosecuting Attorney. Official 2026 general: REP MARCIA E. BEAN 3,271, re-elected.",
         party="Republican")
    _add(terms, "WY-BEAN-MARCIA-E", "Marcia E. Bean", "County Attorney", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, County Attorney: REP MARCIA E. BEAN 3,271, write-ins 157, contest totals 4,200.",
         party="Republican")
    _add(terms, "WY-LIPP-SERENA-K", "Serena K. Lipp", "Clerk of District Court", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CDC],
         "Official 2026 canvass, Clerk of District Court: REP SERENA K. LIPP 3,824, re-elected.",
         party="Republican")
    _add(terms, "WY-LIPP-SERENA-K", "Serena K. Lipp", "Clerk of District Court", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, Clerk of District Court: REP SERENA K. LIPP 3,824, write-ins 15, contest totals 4,200.",
         party="Republican")
    _add(terms, "WY-JAMESON-MICHAEL-K", "Michael K. Jameson", "County Coroner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CORONER],
         "Official coroner page, retrieved 2026-11-24: Michael K. Jameson. Official 2026 general: REP MICHAEL K. JAMESON 3,768, re-elected. The official canvass and official page are used (not a longer unofficial expansion of the middle name).",
         party="Republican")
    _add(terms, "WY-JAMESON-MICHAEL-K", "Michael K. Jameson", "County Coroner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_CORONER],
         "Official 2026 canvass, County Coroner: REP MICHAEL K. JAMESON 3,768, write-ins 31, contest totals 4,200.",
         party="Republican")
    return terms


def judicial_terms():
    terms = []
    _add(terms, "WY-OVERFIELD-BOBBI", "Bobbi Overfield",
         "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2021-01-04", "2027-01-04", 2020, [SRC_COURT],
         "Official March 2026 judicial roster title already used in the official Park and Washakie histories. Official 2020 retention. Distinct from any other Overfield.")
    _add(terms, "WY-OVERFIELD-BOBBI", "Bobbi Overfield",
         "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2027-01-04", "2033-01-03", 2026, [SRC_2026, SRC_COURT],
         "Official 2026 Big Horn canvass, RETAIN JUDGE BOBBI OVERFIELD: YES 2,876, NO 722. Retained, continuing January 2027.")
    _add(terms, "WY-LUHM-ED", "Ed Luhm",
         "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2025-01-06", "2031-01-06", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Big Horn canvass, RETAIN JUDGE EDWARD G. LUHM: YES 4,081, NO 864. Official court/roster name used in the official Park and Washakie histories is Ed Luhm (Edward G. Luhm).")
    _add(terms, "WY-SIMPSON-BILL", "Bill Simpson",
         "District Judge, 5th Judicial District (Park)", "judicial",
         "2025-01-06", "2031-01-06", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Big Horn canvass, RETAIN JUDGE BILL SIMPSON: YES 4,155, NO 903. Official March 2026 roster names Bill Simpson, Park district judge (also used in official Park and Washakie histories).")
    _add(terms, "WY-DARRAH-JOEY", "Joey Darrah",
         "Circuit Judge, 5th Judicial District (Park)", "judicial",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Big Horn canvass, RETAIN JUDGE S. JOSEPH JOEY DARRAH: YES 4,097, NO 906. Official roster name Joey Darrah (Park circuit), already used in official Park and Washakie histories.")
    return terms


def municipal_terms():
    """Current mayors from official 2022 canvass (through January 2027) and official
    2026 elects; council holdovers from official 2024 canvass; 2-year seats as dated.
    Official 2022 Greybull Mayor confirmed visually on the official Custom Table Report,
    page 27 of 74 (two-column with Frannie Council 2yr): MYLES R. FOLEY 414, write-ins 43,
    contest total 560.
    """
    terms = []

    def cur4(pid, name, office, year, start, end, sources, notes):
        _add(terms, pid, name, office, "municipal", start, end, year, sources, notes)

    # --- Basin ---
    cur4("WY-DUNCAN-CJ", "CJ Duncan", "Basin Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Basin Mayor: CJ Duncan 288, Clayton John Draggoo 154.")
    cur4("WY-HOPKIN-CHARLES", "Charles (Chuck) Hopkin", "Basin Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Basin Mayor: Charles (Chuck) Hopkin 222, Carl R. Olson 213, write-ins 1, contest totals 451. Takes office January 2027.")
    cur4("WY-DELLOS-MIKE", "Mike Dellos", "Basin Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Basin Council (vote for 2): Mike Dellos 333, Linda Weeks 254 (Stuart Desrosier 216 lost 2024 and won a 2026 council seat).")
    cur4("WY-WEEKS-LINDA", "Linda Weeks", "Basin Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Basin Council (vote for 2): Linda Weeks 254, Mike Dellos 333.")
    cur4("WY-DESROSIER-STUART", "Stuart Desrosier", "Basin Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Basin Council (vote for 2): Stuart Desrosier 288, Michael Tanner 235, Jennifer S. Riley 202, Steve Vanderploeg 21. Takes office January 2027.")
    cur4("WY-TANNER-MICHAEL", "Michael Tanner", "Basin Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Basin Council (vote for 2): Michael Tanner 235, Stuart Desrosier 288.")
    cur4("WY-GODFREY-BRENT", "Brent Godfrey", "Basin Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Basin Council (vote for 2): Brent Godfrey 327, Charles E. Hopkin 254, Linda Harp 216.")
    cur4("WY-HOPKIN-CHARLES", "Charles (Chuck) Hopkin", "Basin Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Basin Council (vote for 2): Charles E. Hopkin 254, Brent Godfrey 327. Official 2026 canvass elects Charles (Chuck) Hopkin as Basin Mayor; same person.")

    # --- Burlington ---
    cur4("WY-GEORGE-GERALD", "Gerald \"Jerry\" George", "Burlington Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Burlington Mayor: Gerald \"Jerry\" George 95.")
    cur4("WY-BRUNKO-GARY", "Gary Brunko", "Burlington Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Burlington Mayor: Gary Brunko 98. Takes office January 2027.")
    cur4("WY-HIBBERT-DON", "Don Hibbert", "Burlington Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Burlington Council (vote for 2): Don Hibbert 129, Jenny Booth 122.")
    cur4("WY-BOOTH-JENNY", "Jenny Booth", "Burlington Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Burlington Council (vote for 2): Jenny Booth 122, Don Hibbert 129.")
    cur4("WY-LEONHARDT-MELISSA", "Melissa Leonhardt", "Burlington Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Burlington Council (vote for 2): Melissa Leonhardt 51, Michael J. Harrington 48, Jackie Cenker 45, Matt Walker 42. Takes office January 2027.")
    cur4("WY-HARRINGTON-MICHAEL-J", "Michael J. Harrington", "Burlington Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Burlington Council (vote for 2): Michael J. Harrington 48, Melissa Leonhardt 51.")
    cur4("WY-HAMILTON-JESSIE", "Jessie Hamilton", "Burlington Town Council (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
         "Official 2026 canvass, Burlington Council 2-year: Jessie Hamilton 60, Neal A. Wood 41. Takes office January 2027.")
    cur4("WY-BRUNKO-GARY", "Gary Brunko", "Burlington Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Burlington Council (vote for 2): Gary Brunko 83, Jessie Hamilton 75, Cortney Allen 47. Official 2026 canvass elects Gary Brunko as Burlington Mayor.")
    cur4("WY-HAMILTON-JESSIE", "Jessie Hamilton", "Burlington Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Burlington Council (vote for 2): Jessie Hamilton 75, Gary Brunko 83. Official 2026 canvass elects Jessie Hamilton to a 2-year council seat.")

    # --- Byron ---
    cur4("WY-CLARK-ALLAN-P", "Allan P. Clark", "Byron Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Byron Mayor: Allan Clark 124, Pam Hopkinson 88. Official 2026 canvass uses Allan P. Clark (same person).")
    cur4("WY-CLARK-ALLAN-P", "Allan P. Clark", "Byron Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Byron Mayor: Allan P. Clark 134, re-elected.")
    cur4("WY-BRIGHTLY-MIKE", "Mike Brightly", "Byron Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Byron Council (vote for 2): Mike Brightly 121, Karma Sanders 109.")
    cur4("WY-SANDERS-KARMA", "Karma Sanders", "Byron Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Byron Council (vote for 2): Karma Sanders 109, Mike Brightly 121.")
    cur4("WY-HESSENTHALER-BRANDON", "Brandon Hessenthaler", "Byron Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Byron Council (vote for 2): Brandon Hessenthaler 103, Shae C. Abraham 101, Taliesha Beech 46. Takes office January 2027.")
    cur4("WY-ABRAHAM-SHAE-C", "Shae C. Abraham", "Byron Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Byron Council (vote for 2): Shae C. Abraham 101, Brandon Hessenthaler 103.")
    cur4("WY-HESSENTHALER-BRANDON", "Brandon Hessenthaler", "Byron Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Byron Council (vote for 2): Brandon Hessenthaler 151, Shae Abraham 120, Toby Turnupseed 89. Official 2026 canvass re-elects Brandon Hessenthaler.")
    cur4("WY-ABRAHAM-SHAE-C", "Shae C. Abraham", "Byron Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Byron Council (vote for 2): Shae Abraham 120, Brandon Hessenthaler 151. Official 2026 canvass uses Shae C. Abraham (same person, re-elected).")

    # --- Cowley ---
    cur4("WY-PETERSON-JOEL", "Joel Peterson", "Cowley Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Cowley Mayor: Joel Peterson 256.")
    cur4("WY-WINTERS-STEPHEN", "Stephen Winters", "Cowley Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Cowley Mayor: Stephen Winters 153, KJ Blackburn 142. Takes office January 2027.")
    cur4("WY-LEWIS-MAX", "Max Lewis", "Cowley Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Cowley Council (vote for 2): Max Lewis 181, Rob Johnson 120. A 2024 loser listed as Dexter Woods on the official scan is not combined with official 2026 winner Dexter Woodis.")
    cur4("WY-JOHNSON-ROB", "Rob Johnson", "Cowley Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Cowley Council (vote for 2): Rob Johnson 120, Max Lewis 181.")
    cur4("WY-CROSBY-SCOTT", "Scott Crosby", "Cowley Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Cowley Council (vote for 2): Scott Crosby 216, Dexter Woodis 183, Rose Ames 97, Bryan Baird 62. Takes office January 2027.")
    cur4("WY-WOODIS-DEXTER", "Dexter Woodis", "Cowley Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Cowley Council (vote for 2): Dexter Woodis 183, Scott Crosby 216. Official 2026 spelling Woodis is used.")
    cur4("WY-CROSBY-SCOTT", "Scott Crosby", "Cowley Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Cowley Council (vote for 2): Emily Anne Simmons 205, Scott Crosby 172, Nathan Sponsel (Nick) 92, Diane R. Badget 79. Official 2026 canvass re-elects Scott Crosby.")
    cur4("WY-SIMMONS-EMILY-ANNE", "Emily Anne Simmons", "Cowley Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Cowley Council (vote for 2): Emily Anne Simmons 205, Scott Crosby 172.")

    # --- Deaver ---
    cur4("WY-CAMP-BILL", "Bill Camp", "Deaver Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Deaver Mayor: Bill Camp 49. Official 2026 canvass re-elects Bill Camp.")
    cur4("WY-CAMP-BILL", "Bill Camp", "Deaver Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Deaver Mayor: Bill Camp 43, re-elected.")
    cur4("WY-LOFTUS-NICK", "Nick Loftus", "Deaver Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Deaver Council (vote for 2): Nick Loftus 66, Aspen Beall 65.")
    cur4("WY-BEALL-ASPEN", "Aspen Beall", "Deaver Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Deaver Council (vote for 2): Aspen Beall 65, Nick Loftus 66.")
    cur4("WY-CROUCH-SHAUNA", "Shauna Crouch", "Deaver Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Deaver Council (vote for 2): Shauna Crouch 35, Kayla James 32. Takes office January 2027.")
    cur4("WY-JAMES-KAYLA", "Kayla James", "Deaver Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Deaver Council (vote for 2): Kayla James 32, Shauna Crouch 35.")
    cur4("WY-SPANN-KELLY", "Kelly Spann", "Deaver Town Council (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
         "Official 2026 canvass, Deaver Council 2-year: Kelly Spann 36. Takes office January 2027.")
    cur4("WY-JAMES-KAYLA", "Kayla James", "Deaver Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Deaver Council (vote for 2): Kayla James 45, Steve Gillett 44. Official 2026 canvass re-elects Kayla James.")
    cur4("WY-GILLETT-STEVE", "Steve Gillett", "Deaver Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Deaver Council (vote for 2): Steve Gillett 44, Kayla James 45.")

    # --- Frannie ---
    cur4("WY-RICHARDSON-STEVE", "Steve Richardson", "Frannie Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Frannie Mayor: Steve Richardson 26, R. Vance Peregoy 22.")
    cur4("WY-FRESCOLN-GARRET-I", "Garret I. Frescoln", "Frannie Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Frannie Mayor: Garret I. Frescoln 41. Takes office January 2027. The same official name also won the 2026 North Hospital Deaver-Frannie trustee seat; both official offices are recorded.")
    cur4("WY-GANOUNG-ROGER", "Roger Ganoung", "Frannie Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Frannie Council (vote for 2): Roger Ganoung 36, Shang Clendenen 35 (Guy T. DeSantis 29 lost 2024 and won a 2026 council seat).")
    cur4("WY-CLENDENEN-SHANG", "Shang Clendenen", "Frannie Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Frannie Council (vote for 2): Shang Clendenen 35, Roger Ganoung 36.")
    cur4("WY-POOLE-KEARA", "Keara Poole", "Frannie Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Frannie Council (vote for 2): Keara Poole 37, Guy DeSantis 36. Takes office January 2027.")
    cur4("WY-DESANTIS-GUY", "Guy DeSantis", "Frannie Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Frannie Council (vote for 2): Guy DeSantis 36, Keara Poole 37. Official 2022 canvass also named GUY DESANTIS as Frannie Council 2-year winner (44). Official 2024 loser Guy T. DeSantis is treated as the same official person.")
    cur4("WY-ELLIS-JOHN", "John Ellis", "Frannie Town Council (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
         "Official 2026 canvass, Frannie Council 2-year: John Ellis 35. Takes office January 2027.")
    cur4("WY-POOLE-KEARA", "Keara Poole", "Frannie Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Frannie Council 4-year (vote for 2): Keara Poole 45, Garret I. Frescoln 41. Official 2026 canvass re-elects Keara Poole.")
    cur4("WY-FRESCOLN-GARRET-I", "Garret I. Frescoln", "Frannie Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Frannie Council 4-year (vote for 2): Garret I. Frescoln 41, Keara Poole 45. Official 2026 canvass elects Garret I. Frescoln as Frannie Mayor.")

    # --- Greybull ---
    cur4("WY-FOLEY-MYLES-R", "Myles R. Foley", "Greybull Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 Custom Table Report page 27 of 74 (OFFICIAL RESULTS, visually confirmed on the two-column page with Frannie Council 2yr): Greybull Mayor, vote for 1, MYLES R. FOLEY 414, write-ins 43, Total Votes Cast 457, undervotes 103, contest total 560.")
    cur4("WY-JOHNSTON-MICHAEL", "Michael Johnston", "Greybull Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Greybull Mayor: Michael Johnston 378, Bill Brenner 201. Takes office January 2027.")
    cur4("WY-DOOLEY-CHRIS", "Chris Dooley", "Greybull Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Greybull Council 4-year (vote for 2): Chris Dooley 618, Gerald Crist 510.")
    cur4("WY-CRIST-GERALD", "Gerald Crist", "Greybull Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Greybull Council 4-year (vote for 2): Gerald Crist 510, Chris Dooley 618.")
    cur4("WY-FOLEY-MYLES-R", "Myles R. Foley", "Greybull Town Council (2-year)", 2024, "2025-01-06", "2027-01-04", [SRC_2024],
         "Official 2024 canvass, Greybull Council 2-year: Myles R. Foley 427, Bill Brenner 319. The official 2022 canvass also names Myles R. Foley as Greybull Mayor (current through January 2027); both official offices are recorded. The 2-year council term ends January 2027.")
    cur4("WY-WILLIAMSON-BOB", "Bob Williamson", "Greybull Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Greybull Council (vote for 2): Bob Williamson 400, Robert C. Skillman Jr. 397. Takes office January 2027.")
    cur4("WY-SKILLMAN-ROBERT-C", "Robert C. Skillman Jr.", "Greybull Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Greybull Council (vote for 2): Robert C. Skillman Jr. 397, Bob Williamson 400.")
    cur4("WY-JOLLEY-BLAINE", "Blaine Jolley", "Greybull Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Greybull Council 4-year (vote for 2): Blaine Jolley 370, Dean S. Miars 278, Jeremy Kottman 237.")
    cur4("WY-MIARS-DEAN-S", "Dean S. Miars", "Greybull Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Greybull Council 4-year (vote for 2): Dean S. Miars 278, Blaine Jolley 370.")

    # --- Lovell ---
    cur4("WY-NEWMAN-TOM", "Tom Newman", "Lovell Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Lovell Mayor: Tom Newman 597. Official 2026 canvass re-elects Tom Newman.")
    cur4("WY-NEWMAN-TOM", "Tom Newman", "Lovell Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Lovell Mayor: Tom Newman 546, re-elected.")
    cur4("WY-GRANT-MICHAEL-LEE", "Michael Lee Grant", "Lovell Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Lovell Council (vote for 2): Michael Lee Grant 456, Carol Miller 442.")
    cur4("WY-MILLER-CAROL", "Carol Miller", "Lovell Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Lovell Council (vote for 2): Carol Miller 442, Michael Lee Grant 456.")
    cur4("WY-MANGUS-ROBERT", "Robert Mangus", "Lovell Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Lovell Council (vote for 2): Robert Mangus 366, Daniel L. Anderson 338, Jason W. Sumaya 209, Jeffrey McCollam 166. Takes office January 2027.")
    cur4("WY-ANDERSON-DANIEL-L", "Daniel L. Anderson", "Lovell Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Lovell Council (vote for 2): Daniel L. Anderson 338, Robert Mangus 366.")
    cur4("WY-MANGUS-ROBERT", "Robert Mangus", "Lovell Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Lovell Council 4-year (vote for 2): Daniel L. Anderson 531, Bob Mangus 518. Official 2026 canvass re-elects Robert Mangus (same official person).")
    cur4("WY-ANDERSON-DANIEL-L", "Daniel L. Anderson", "Lovell Town Council", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Lovell Council 4-year (vote for 2): Daniel L. Anderson 531, Bob Mangus 518. Official 2026 canvass re-elects Daniel L. Anderson.")

    # --- Manderson ---
    cur4("WY-PATRICK-ROD", "Rod Patrick", "Manderson Mayor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
         "Official 2022 canvass, Manderson Mayor: Rod Patrick 30, Barbara Wall 16.")
    cur4("WY-DUNCAN-WILLIAM-S", "William S. Duncan", "Manderson Mayor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Manderson Mayor: William S. Duncan 27. Takes office January 2027.")
    cur4("WY-SAUNDERS-THEA", "Thea Saunders", "Manderson Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Manderson Council 4-year: Thea Saunders 21, Sharon Sanford 20. Official 2026 canvass also names Thea Saunders as a council elect (vote for 2); both official results are recorded.")
    cur4("WY-SANFORD-SHARON", "Sharon Sanford", "Manderson Town Council", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
         "Official 2024 canvass, Manderson Council 4-year: Sharon Sanford 20, Thea Saunders 21.")
    cur4("WY-SAUNDERS-CHRISTOPHER-M", "Christopher M. Saunders", "Manderson Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Manderson Council (vote for 2): Christopher M. Saunders 21, Thea Saunders 18, Howard Applegarth 16, Tim Patrick 13. Takes office January 2027.")
    cur4("WY-SAUNDERS-THEA", "Thea Saunders", "Manderson Town Council", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
         "Official 2026 canvass, Manderson Council (vote for 2): Thea Saunders 18, Christopher M. Saunders 21.")
    cur4("WY-DRIVER-ALETA", "Aleta Driver", "Manderson Town Council (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
         "Official 2026 canvass, Manderson Council 2-year: Aleta Driver 20, Jack Nielsen 15. Takes office January 2027.")
    return terms


def register_special_people(P):
    # Cemetery 2024 / 2026
    P("WY-AAGARD-TRENT-A", "Trent A. Aagard", "Trent", "Aagard", middle="A.")
    P("WY-RILEY-MIKE-L", "Mike L. Riley", "Mike", "Riley", middle="L.")
    P("WY-DAVIDSON-BARBARA", "Barbara Davidson", "Barbara", "Davidson")
    P("WY-DAVIDSON-JACOB", "Jacob Davidson", "Jacob", "Davidson")
    P("WY-PREATOR-NORMAN", "Norman Preator", "Norman", "Preator")
    P("WY-RASMUSSEN-KIMBERLY", "Kimberly Rasmussen", "Kimberly", "Rasmussen")
    P("WY-PREATOR-BRANDON", "Brandon Preator", "Brandon", "Preator")
    P("WY-HATCH-DON-A", "Don A. Hatch", "Don", "Hatch", middle="A.")
    P("WY-HESSENTHALER-JACK", "Jack Hessenthaler", "Jack", "Hessenthaler")
    P("WY-HOPKINSON-GLEN", "Glen Hopkinson", "Glen", "Hopkinson")
    P("WY-WAGNER-STEVEN-SHAINE", "Steven Shaine Wagner", "Steven Shaine", "Wagner")
    P("WY-GIFFORD-EDWARD", "Edward Gifford", "Edward", "Gifford")
    P("WY-NEVILLE-E-DENNEY", "E. Denney Neville", "E. Denney", "Neville")
    P("WY-PETERSON-CRESTA", "Cresta Peterson", "Cresta", "Peterson")
    P("WY-STROM-LYNNE-T", "Lynne T. Strom", "Lynne", "Strom", middle="T.")
    P("WY-HOFFMAN-LORI", "Lori Hoffman", "Lori", "Hoffman")
    P("WY-BLACKBURN-KEN", "Ken Blackburn", "Ken", "Blackburn")
    P("WY-LEONHARDT-GARY-D", "Gary D. Leonhardt", "Gary", "Leonhardt", middle="D.")
    P("WY-MINCHOW-DONALD-R", "Donald R. Minchow", "Donald", "Minchow", middle="R.")
    P("WY-SCHEELER-COLEEN", "Coleen Scheeler", "Coleen", "Scheeler")
    P("WY-ESTES-DALE-R", "Dale R. Estes", "Dale", "Estes", middle="R.")
    P("WY-TROUTMAN-ALICIA", "Alicia Troutman", "Alicia", "Troutman")
    P("WY-NEWTON-LONNIE", "Lonnie Newton", "Lonnie", "Newton")
    P("WY-KAWANO-BRENDA", "Brenda Kawano", "Brenda", "Kawano")
    P("WY-WAMBEKE-MELVYN", "Melvyn Wambeke", "Melvyn", "Wambeke")
    P("WY-CLINE-PATRICIA", "Patricia Cline", "Patricia", "Cline")
    P("WY-NOLAN-FRAN", "Fran Nolan", "Fran", "Nolan")
    P("WY-PREIS-KAREN", "Karen Preis", "Karen", "Preis")
    P("WY-WERBELOW-JULIE", "Julie Werbelow", "Julie", "Werbelow")
    P("WY-KELSO-GEORGE", "George Kelso", "George", "Kelso")
    P("WY-EDWARDS-CHRIS", "Chris Edwards", "Chris", "Edwards")
    P("WY-KUMMERFELDT-JANET", "Janet Kummerfeldt", "Janet", "Kummerfeldt")
    P("WY-HERMAN-ROBERT", "Robert Herman", "Robert", "Herman")
    P("WY-ZIEROLF-NANCY", "Nancy Zierolf", "Nancy", "Zierolf")
    P("WY-DARLING-KELLY", "Kelly Darling", "Kelly", "Darling")
    P("WY-THARP-JILL", "Jill Tharp", "Jill", "Tharp")
    P("WY-MERCER-KELLI", "Kelli Mercer", "Kelli", "Mercer")
    P("WY-NICHOLLS-JACK-W", "Jack W. Nicholls", "Jack", "Nicholls", middle="W.")
    P("WY-REASCH-BRENT", "Brent Reasch", "Brent", "Reasch")
    P("WY-FABER-LEONARD", "Leonard Faber", "Leonard", "Faber")
    P("WY-JAMESON-MICHAEL-K", "Michael K. Jameson", "Michael", "Jameson", middle="K.")  # already registered; ok if factory is idempotent
    P("WY-HERMAN-TODD", "Todd Herman", "Todd", "Herman")
    P("WY-WINLAND-RALPH", "Ralph Winland", "Ralph", "Winland")
    P("WY-CALL-JANALEE-JONES", "Janalee Jones Call", "Janalee", "Call")
    P("WY-TOLMAN-ANDREA", "Andrea Tolman", "Andrea", "Tolman")
    P("WY-SCHATZ-BEVIN", "Bevin Schatz", "Bevin", "Schatz")
    P("WY-HANCOCK-CAMILLA", "Camilla Hancock", "Camilla", "Hancock")
    P("WY-JONES-MICHELLE", "Michelle Jones", "Michelle", "Jones")
    P("WY-JONES-CARRINNE", "Carrinne Jones", "Carrinne", "Jones")
    P("WY-SPRAGG-CHARLES", "Charles Spragg", "Charles", "Spragg")
    P("WY-BURNS-MICHELLE-M", "Michelle M. Burns", "Michelle", "Burns", middle="M.")
    P("WY-HAWKINS-BOBBY", "Bobby Hawkins", "Bobby", "Hawkins")
    P("WY-LAIRD-BRIANNA", "Brianna Laird", "Brianna", "Laird")
    P("WY-MURDOCH-CLAUDINE", "Claudine Murdoch", "Claudine", "Murdoch")
    P("WY-WEIDENHAFT-DEBIE", "Debie Weidenhaft", "Debie", "Weidenhaft")
    P("WY-MCCHESNEY-ARTHUR", "Arthur McChesney", "Arthur", "McChesney")
    # Conservation
    P("WY-ELLIS-SPENCER", "Spencer Ellis", "Spencer", "Ellis")
    P("WY-TIPPETTS-BRAD", "Brad Tippetts", "Brad", "Tippetts")
    P("WY-GRANT-KEITH", "Keith Grant", "Keith", "Grant")
    P("WY-HESSENTHALER-DAVID", "David Hessenthaler", "David", "Hessenthaler")
    P("WY-GUCCION-ROBERT", "Robert Guccion", "Robert", "Guccion")
    P("WY-HAMILTON-LINDA", "Linda Hamilton", "Linda", "Hamilton")
    P("WY-HIBBERT-WALTER-W", "Walter W. Hibbert", "Walter", "Hibbert", middle="W.")
    P("WY-JOHNSON-EDDIE-L", "Eddie L. Johnson", "Eddie", "Johnson", middle="L.")
    P("WY-WILDMAN-HOWARD", "Howard Wildman", "Howard", "Wildman")
    # Fire
    P("WY-JOLLEY-BRUCE-H", "Bruce H. Jolley", "Bruce", "Jolley", middle="H.")
    P("WY-RAEL-GREG", "Greg Rael", "Greg", "Rael")
    P("WY-LEONHARDT-MICHAEL-H", "Michael H. Leonhardt", "Michael", "Leonhardt", middle="H.")
    P("WY-GREENE-BARBARA-ANNE", "Barbara Anne Greene", "Barbara Anne", "Greene")
    P("WY-FOSS-LUKE", "Luke Foss", "Luke", "Foss")
    P("WY-PAUMER-DAVE", "Dave Paumer", "Dave", "Paumer")
    P("WY-WILDMAN-JOE", "Joe Wildman", "Joe", "Wildman")
    P("WY-DAVIDSON-SUSAN", "Susan Davidson", "Susan", "Davidson")
    P("WY-HIBBERT-GARY", "Gary Hibbert", "Gary", "Hibbert")
    P("WY-GRIFFIN-KEVIN", "Kevin Griffin", "Kevin", "Griffin")
    P("WY-WAMBEKE-CHERIE", "Cherie Wambeke", "Cherie", "Wambeke")
    P("WY-WAMBEKE-KENDAL", "Kendal Wambeke", "Kendal", "Wambeke")
    P("WY-EASUM-ROGER", "Roger Easum", "Roger", "Easum")
    P("WY-MCCASLIN-MATT", "Matt McCaslin", "Matt", "McCaslin")
    P("WY-HENY-SCOTT", "Scott Heny", "Scott", "Heny")
    P("WY-BAGNELL-SCOTT", "Scott Bagnell", "Scott", "Bagnell")
    P("WY-MAY-GERALD-BEAR", "Gerald (Bear) May", "Gerald", "May", aliases="Gerald May; Bear May")
    P("WY-WORSTELL-HEATH", "Heath Worstell", "Heath", "Worstell")
    # Hospital / senior / rural health
    P("WY-LEWIS-MAX", "Max Lewis", "Max", "Lewis")
    P("WY-WINTERHOLLER-DAVID-A", "David A. Winterholler", "David", "Winterholler", middle="A.")
    P("WY-CRUMRINE-PATRICIA", "Patricia Crumrine", "Patricia", "Crumrine")
    P("WY-MORRISON-BRUCE", "Bruce Morrison", "Bruce", "Morrison")
    P("WY-CROSBY-BRETT", "Brett Crosby", "Brett", "Crosby")
    P("WY-CRAFT-TRUDY-E", "Trudy E. Craft", "Trudy", "Craft", middle="E.")
    P("WY-SCHERMAN-MICHAEL", "Michael Scherman", "Michael", "Scherman")
    P("WY-WERNER-FRED", "Fred Werner", "Fred", "Werner")
    P("WY-PETTY-JEFF", "Jeff Petty", "Jeff", "Petty")
    P("WY-CROSBY-EDIE", "Edie Crosby", "Edie", "Crosby")
    P("WY-PROSSER-ANNELLA", "Annella Prosser", "Annella", "Prosser")
    P("WY-SCHEFFLER-LORI", "Lori Scheffler", "Lori", "Scheffler")
    P("WY-TIPPETTS-PAULINE", "Pauline Tippetts", "Pauline", "Tippetts")
    P("WY-PARMER-PATRICIA", "Patricia Parmer", "Patricia", "Parmer")
    P("WY-MILLER-LINDA-JO", "Linda Jo Miller", "Linda Jo", "Miller")
    P("WY-BONNEL-PHILLIPS-KRISTI-L", "Kristi L. Bonnel-Phillips", "Kristi", "Bonnel-Phillips", middle="L.")
    P("WY-EMMETT-SHERRI", "Sherri Emmett", "Sherri", "Emmett")
    P("WY-NUTTALL-DIANE", "Diane Nuttall", "Diane", "Nuttall")
    P("WY-FOWLER-DEB", "Deb Fowler", "Deb", "Fowler")
    P("WY-RATHBUN-DEB", "Deb Rathbun", "Deb", "Rathbun")
    P("WY-NELSON-KENNETH", "Kenneth Nelson", "Kenneth", "Nelson")
    P("WY-TURNER-THERESA", "Theresa Turner", "Theresa", "Turner")
    P("WY-FOWLER-RUSSELL", "Russell Fowler", "Russell", "Fowler")


def school_terms():
    terms = []

    def sch(pid, name, office, year, start, end, sources, notes):
        _add(terms, pid, name, office, "schools", start, end, year, sources, notes)

    # BHSD #1
    sch("WY-FULLER-WENDY", "Wendy Fuller", "Big Horn County School District #1 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #1 At Large (vote for 1): Wendy Fuller 695, Holly Michaels 675.")
    sch("WY-BOARDMAN-JARED", "Jared Boardman", "Big Horn County School District #1 Trustee Area A",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #1 Area A: Jared Boardman 1,305. Official 2026 commissioner elect; both official offices are recorded.")
    sch("WY-RASMUSSEN-DICKSON-AJ", "AJ Rasmussen-Dickson", "Big Horn County School District #1 Trustee Area B",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #1 Area B: AJ Rasmussen-Dickson 763, Taliesha Beech 422.")
    sch("WY-JONES-CRAIG-A", "Craig A. Jones", "Big Horn County School District #1 Trustee Area C",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #1 Area C: Craig A. Jones 727, Julie Michaels 562. Official 2026 canvass re-elects Craig A. Jones.")
    sch("WY-JONES-CRAIG-A", "Craig A. Jones", "Big Horn County School District #1 Trustee Area C",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #1 Area C Burlington: Craig A. Jones 919, re-elected.")
    sch("WY-CHRISTENSEN-HIEDI-J", "Hiedi J. Christensen", "Big Horn County School District #1 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #1 At Large (vote for 2): Hiedi J. Christensen 712, Holly Michaels 568, Hunter Allen 318, contest totals 2,216. Takes office January 2027.")
    sch("WY-MICHAELS-HOLLY", "Holly Michaels", "Big Horn County School District #1 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #1 At Large (vote for 2): Holly Michaels 568, Hiedi J. Christensen 712.")
    sch("WY-LEONHARDT-EMILY-R", "Emily R. Leonhardt", "Big Horn County School District #1 Trustee Area D",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #1 Area D Cowley: Emily R. Leonhardt 525, Thomas Bridges 393. Takes office January 2027.")
    sch("WY-BANKS-DAVID-V", "David V. Banks", "Big Horn County School District #1 Trustee Area D",
        2022, "2023-01-02", "2027-01-04", [SRC_2022],
        "Official 2022 canvass, BHSD #1 Area D Cowley: David V. Banks 1,006.")

    # BHSD #2
    sch("WY-BAIR-STACY", "Stacy Bair", "Big Horn County School District #2 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #2 At Large (vote for 4): Stacy Bair 1,019.")
    sch("WY-ANDERSON-LANCE-E", "Lance E. Anderson", "Big Horn County School District #2 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #2 At Large (vote for 4): Lance E. Anderson (official canvass printed Lance E. Anderson, DMD; the credential is not used in the display name).")
    sch("WY-ANGELL-C-TYLER", "C. Tyler Angell", "Big Horn County School District #2 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #2 At Large (vote for 4): C. Tyler Angell 565.")
    sch("WY-PETERSON-TESS-L", "Tess L. Peterson", "Big Horn County School District #2 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #2 At Large (vote for 4): Tess L. Peterson 535 (Kyle Leithead 523 and Ryan Felkins 351 lost 2024; both won 2026 seats).")
    sch("WY-WALKER-BEN", "Ben Walker", "Big Horn County School District #2 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #2 At Large (vote for 3): Ben Walker 746, Kyle Leithead 688, Danny Jolley 598, Marianne Grant 573. Takes office January 2027.")
    sch("WY-LEITHEAD-KYLE", "Kyle Leithead", "Big Horn County School District #2 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #2 At Large (vote for 3): Kyle Leithead 688.")
    sch("WY-JOLLEY-DANNY", "Danny Jolley", "Big Horn County School District #2 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #2 At Large (vote for 3): Danny Jolley 598.")
    sch("WY-FELKINS-RYAN", "Ryan Felkins", "Big Horn County School District #2 Trustee At Large (2-year)",
        2026, "2027-01-04", "2029-01-01", [SRC_2026],
        "Official 2026 canvass, BHSD #2 At Large 2-year: Ryan Felkins 947. Takes office January 2027.")

    # BHSD #3
    sch("WY-FLITNER-PAM", "Pam Flitner", "Big Horn County School District #3 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #3 At Large (vote for 4): Pam Flitner 951.")
    sch("WY-DALIN-TODD", "Todd Dalin", "Big Horn County School District #3 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #3 At Large (vote for 4): Todd Dalin 842.")
    sch("WY-JONES-BETTE-RAE", "Bette Rae Jones", "Big Horn County School District #3 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #3 At Large (vote for 4): Bette Rae Jones 751.")
    sch("WY-WHALEY-MIKE", "Mike Whaley", "Big Horn County School District #3 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #3 At Large (vote for 4): Mike Whaley 708 (Sandra Menke 700, Mark Dewees 307 lose).")
    sch("WY-ROBERTSON-WILLIAM-D", "William D. Robertson", "Big Horn County School District #3 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #3 At Large (vote for 3): William D. Robertson 770, Lynette Murray 727, Luke Maxson Zeller 709. Takes office January 2027.")
    sch("WY-MURRAY-LYNETTE", "Lynette Murray", "Big Horn County School District #3 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #3 At Large (vote for 3): Lynette Murray 727.")
    sch("WY-ZELLER-LUKE-MAXSON", "Luke Maxson Zeller", "Big Horn County School District #3 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #3 At Large (vote for 3): Luke Maxson Zeller 709.")
    sch("WY-ROBERTSON-WILLIAM-D", "William D. Robertson", "Big Horn County School District #3 Trustee At Large",
        2022, "2023-01-02", "2027-01-04", [SRC_2022],
        "Official 2022 canvass, BHSD #3 At Large (vote for 4): Lynette Murray 861, William D. Robertson 730 were the named official winners (write-ins 234 are not combined into a certified name). Official 2026 canvass re-elects William D. Robertson.")
    sch("WY-MURRAY-LYNETTE", "Lynette Murray", "Big Horn County School District #3 Trustee At Large",
        2022, "2023-01-02", "2027-01-04", [SRC_2022],
        "Official 2022 canvass, BHSD #3 At Large (vote for 4): Lynette Murray 861, William D. Robertson 730. Official 2026 canvass re-elects Lynette Murray.")

    # BHSD #4
    sch("WY-OSMOND-LINDA", "Linda Osmond", "Big Horn County School District #4 Trustee At Large",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #4 At Large (vote for 1): Linda Osmond 894.")
    sch("WY-SCHLATTMANN-KRISTEN", "Kristen Schlattmann", "Big Horn County School District #4 Trustee Area J",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #4 Area J (vote for 2): Kristen Schlattmann 811, Heath Hopkin 756.")
    sch("WY-HOPKIN-HEATH", "Heath Hopkin", "Big Horn County School District #4 Trustee Area J",
        2024, "2025-01-06", "2029-01-01", [SRC_2024],
        "Official 2024 canvass, BHSD #4 Area J (vote for 2): Heath Hopkin 756, Kristen Schlattmann 811.")
    sch("WY-BUTCHER-PRICIE", "Pricie Butcher", "Big Horn County School District #4 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #4 At Large (vote for 2): Pricie Butcher 419, Merrita Powell 392, Enrika Rain Joy Potter 311. Takes office January 2027.")
    sch("WY-POWELL-MERRITA", "Merrita Powell", "Big Horn County School District #4 Trustee At Large",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #4 At Large (vote for 2): Merrita Powell 392.")
    sch("WY-GLOY-GREGORY", "Gregory Gloy", "Big Horn County School District #4 Trustee Area J",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #4 Area J Basin: Gregory Gloy 668. Takes office January 2027.")
    sch("WY-GLOY-GREGORY", "Gregory Gloy", "Big Horn County School District #4 Trustee Area J",
        2022, "2023-01-02", "2027-01-04", [SRC_2022],
        "Official 2022 canvass, BHSD #4 Area J Basin: Gregory Gloy 718. Official 2026 canvass re-elects Gregory Gloy.")
    sch("WY-WOOD-BRENDA", "Brenda Wood", "Big Horn County School District #4 Trustee Area K/L",
        2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, BHSD #4 Area K/L Manderson-Hyattville: Brenda Wood 691. Official 2024 Area K/L was write-in only (125 write-ins, no certified named winner) and is not filled. Takes office January 2027.")
    return terms


def special_terms():
    terms = []

    def sp(pid, name, office, year, start, end, sources, notes):
        _add(terms, pid, name, office, "special-districts", start, end, year, sources, notes)

    # Burlington Cemetery
    sp("WY-AAGARD-TRENT-A", "Trent A. Aagard", "Burlington Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Burlington Cemetery (vote for 3): Trent A. Aagard 288, Mike L. Riley 287, Barbara Davidson 279.")
    sp("WY-RILEY-MIKE-L", "Mike L. Riley", "Burlington Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Burlington Cemetery (vote for 3): Mike L. Riley 287.")
    sp("WY-DAVIDSON-BARBARA", "Barbara Davidson", "Burlington Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Burlington Cemetery (vote for 3): Barbara Davidson 279.")
    sp("WY-DAVIDSON-JACOB", "Jacob Davidson", "Burlington Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Burlington Cemetery (vote for 3): Jacob Davidson 196, Norman Preator 193, Kimberly Rasmussen 187. Takes office January 2027.")
    sp("WY-PREATOR-NORMAN", "Norman Preator", "Burlington Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Burlington Cemetery (vote for 3): Norman Preator 193.")
    sp("WY-RASMUSSEN-KIMBERLY", "Kimberly Rasmussen", "Burlington Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Burlington Cemetery (vote for 3): Kimberly Rasmussen 187.")
    sp("WY-PREATOR-BRANDON", "Brandon Preator", "Burlington Cemetery District Trustee (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, Burlington Cemetery 2-year: Brandon Preator 209. Takes office January 2027.")

    # Byron Cemetery
    sp("WY-HATCH-DON-A", "Don A. Hatch", "Byron Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Byron Cemetery (vote for 3): Don A. Hatch 231, Jack Hessenthaler 228, Glen Hopkinson 183.")
    sp("WY-HESSENTHALER-JACK", "Jack Hessenthaler", "Byron Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Byron Cemetery (vote for 3): Jack Hessenthaler 228.")
    sp("WY-HOPKINSON-GLEN", "Glen Hopkinson", "Byron Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Byron Cemetery (vote for 3): Glen Hopkinson 183.")
    sp("WY-WAGNER-STEVEN-SHAINE", "Steven Shaine Wagner", "Byron Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Byron Cemetery (vote for 3): Steven Shaine Wagner 154, Edward Gifford 153, E. Denney Neville 149. Takes office January 2027.")
    sp("WY-GIFFORD-EDWARD", "Edward Gifford", "Byron Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Byron Cemetery (vote for 3): Edward Gifford 153.")
    sp("WY-NEVILLE-E-DENNEY", "E. Denney Neville", "Byron Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Byron Cemetery (vote for 3): E. Denney Neville 149.")

    # Cowley Cemetery
    sp("WY-PETERSON-CRESTA", "Cresta Peterson", "Cowley Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Cowley Cemetery (vote for 3): Cresta Peterson 453, Lynne T. Strom 439, Lori Hoffman 429.")
    sp("WY-STROM-LYNNE-T", "Lynne T. Strom", "Cowley Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Cowley Cemetery (vote for 3): Lynne T. Strom 439.")
    sp("WY-HOFFMAN-LORI", "Lori Hoffman", "Cowley Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Cowley Cemetery (vote for 3): Lori Hoffman 429.")
    sp("WY-BLACKBURN-KEN", "Ken Blackburn", "Cowley Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Cowley Cemetery (vote for 3): Ken Blackburn 346, Gary D. Leonhardt 333, Donald R. Minchow 326. Takes office January 2027.")
    sp("WY-LEONHARDT-GARY-D", "Gary D. Leonhardt", "Cowley Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Cowley Cemetery (vote for 3): Gary D. Leonhardt 333.")
    sp("WY-MINCHOW-DONALD-R", "Donald R. Minchow", "Cowley Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Cowley Cemetery (vote for 3): Donald R. Minchow 326.")
    sp("WY-SCHEELER-COLEEN", "Coleen Scheeler", "Cowley Cemetery District Trustee (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, Cowley Cemetery 2-year: Coleen Scheeler 387. Takes office January 2027.")

    # Deaver-Frannie Cemetery
    sp("WY-ESTES-DALE-R", "Dale R. Estes", "Deaver-Frannie Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Deaver-Frannie Cemetery 4-year (vote for 3): Dale R. Estes 174, Alicia Troutman 167, Lonnie Newton 154.")
    sp("WY-TROUTMAN-ALICIA", "Alicia Troutman", "Deaver-Frannie Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Deaver-Frannie Cemetery 4-year: Alicia Troutman 167.")
    sp("WY-NEWTON-LONNIE", "Lonnie Newton", "Deaver-Frannie Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Deaver-Frannie Cemetery 4-year: Lonnie Newton 154.")
    sp("WY-KAWANO-BRENDA", "Brenda Kawano", "Deaver-Frannie Cemetery District Trustee (2-year)", 2024, "2025-01-06", "2027-01-04", [SRC_2024],
       "Official 2024 canvass, Deaver-Frannie Cemetery 2-year: Brenda Kawano 203. Official 2026 canvass elects Brenda Kawano to a 4-year seat.")
    sp("WY-WAMBEKE-MELVYN", "Melvyn Wambeke", "Deaver-Frannie Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Deaver-Frannie Cemetery (vote for 3): Melvyn Wambeke 132, Patricia Cline 126, Brenda Kawano 118. Takes office January 2027.")
    sp("WY-CLINE-PATRICIA", "Patricia Cline", "Deaver-Frannie Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Deaver-Frannie Cemetery (vote for 3): Patricia Cline 126.")
    sp("WY-KAWANO-BRENDA", "Brenda Kawano", "Deaver-Frannie Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Deaver-Frannie Cemetery (vote for 3): Brenda Kawano 118.")

    # Emblem Cemetery
    sp("WY-NOLAN-FRAN", "Fran Nolan", "Emblem Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Emblem Cemetery (vote for 3): Fran Nolan, Karen Preis, Julie Werbelow (official named winners; OCR totals 42 / 54 / 52 were not used as a locked ranking).")
    sp("WY-PREIS-KAREN", "Karen Preis", "Emblem Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Emblem Cemetery (vote for 3): Karen Preis.")
    sp("WY-WERBELOW-JULIE", "Julie Werbelow", "Emblem Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Emblem Cemetery (vote for 3): Julie Werbelow.")
    sp("WY-KELSO-GEORGE", "George Kelso", "Emblem Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Emblem Cemetery (vote for 3): George Kelso 52, Chris Edwards 43, Janet Kummerfeldt 39. Takes office January 2027.")
    sp("WY-EDWARDS-CHRIS", "Chris Edwards", "Emblem Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Emblem Cemetery (vote for 3): Chris Edwards 43.")
    sp("WY-KUMMERFELDT-JANET", "Janet Kummerfeldt", "Emblem Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Emblem Cemetery (vote for 3): Janet Kummerfeldt 39.")

    # Hyattville Cemetery — 2024 Kristine Robertson total was messy in OCR and is not encoded
    sp("WY-HERMAN-ROBERT", "Robert Herman", "Hyattville Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Hyattville Cemetery (vote for 3): Robert Herman 102, Nancy Zierolf 79. A third official 2024 named total (Kristine Robertson) was not locked because the official-scan OCR of that digit was messy.")
    sp("WY-ZIEROLF-NANCY", "Nancy Zierolf", "Hyattville Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Hyattville Cemetery: Nancy Zierolf 79.")
    sp("WY-DARLING-KELLY", "Kelly Darling", "Hyattville Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hyattville Cemetery (vote for 3): Kelly Darling 81, Jill Tharp 79, Kelli Mercer 60. Takes office January 2027.")
    sp("WY-THARP-JILL", "Jill Tharp", "Hyattville Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hyattville Cemetery (vote for 3): Jill Tharp 79.")
    sp("WY-MERCER-KELLI", "Kelli Mercer", "Hyattville Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hyattville Cemetery (vote for 3): Kelli Mercer 60.")

    # Lovell Cemetery
    sp("WY-NICHOLLS-JACK-W", "Jack W. Nicholls", "Lovell Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Lovell Cemetery (vote for 3): Jack W. Nicholls 1,245, Brent Reasch 1,213, Leonard Faber 991.")
    sp("WY-REASCH-BRENT", "Brent Reasch", "Lovell Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Lovell Cemetery (vote for 3): Brent Reasch 1,213.")
    sp("WY-FABER-LEONARD", "Leonard Faber", "Lovell Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Lovell Cemetery (vote for 3): Leonard Faber 991.")
    sp("WY-JAMESON-MICHAEL-K", "Michael K. Jameson", "Lovell Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Lovell Cemetery (vote for 3): Michael K. Jameson 910, Todd Herman 844, Ralph Winland 832. Same official name as the county coroner; one person ID is used. Takes office January 2027.")
    sp("WY-HERMAN-TODD", "Todd Herman", "Lovell Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Lovell Cemetery (vote for 3): Todd Herman 844.")
    sp("WY-WINLAND-RALPH", "Ralph Winland", "Lovell Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Lovell Cemetery (vote for 3): Ralph Winland 832.")

    # Otto Cemetery
    sp("WY-CALL-JANALEE-JONES", "Janalee Jones Call", "Otto Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Otto Cemetery (vote for 3): Janalee Jones Call 81, Andrea Tolman 79, Bevin Schatz 65.")
    sp("WY-TOLMAN-ANDREA", "Andrea Tolman", "Otto Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Otto Cemetery (vote for 3): Andrea Tolman 79.")
    sp("WY-SCHATZ-BEVIN", "Bevin Schatz", "Otto Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Otto Cemetery (vote for 3): Bevin Schatz 65.")
    sp("WY-HANCOCK-CAMILLA", "Camilla Hancock", "Otto Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Otto Cemetery (vote for 3): Camilla Hancock 54, Michelle Jones 51, Carrinne Jones 50. Takes office January 2027.")
    sp("WY-JONES-MICHELLE", "Michelle Jones", "Otto Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Otto Cemetery (vote for 3): Michelle Jones 51.")
    sp("WY-JONES-CARRINNE", "Carrinne Jones", "Otto Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Otto Cemetery (vote for 3): Carrinne Jones 50.")

    # South Central Special Cemetery
    sp("WY-SPRAGG-CHARLES", "Charles Spragg", "South Central Special Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Central Special Cemetery 4-year (vote for 3): Charles Spragg 818, Michelle M. Burns 626. Only two named winners were certified on the official canvass; the third seat is not filled.")
    sp("WY-BURNS-MICHELLE-M", "Michelle M. Burns", "South Central Special Cemetery District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Central Special Cemetery 4-year: Michelle M. Burns 626.")
    sp("WY-HAWKINS-BOBBY", "Bobby Hawkins", "South Central Special Cemetery District Trustee (2-year)", 2024, "2025-01-06", "2027-01-04", [SRC_2024],
       "Official 2024 canvass, South Central Special Cemetery 2-year (vote for 2): only Bobby Hawkins 919 was a named official winner.")
    sp("WY-LAIRD-BRIANNA", "Brianna Laird", "South Central Special Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Central Special Cemetery (vote for 3): Brianna Laird 415, Bobby Hawkins 362, Claudine Murdoch 356. Takes office January 2027.")
    sp("WY-HAWKINS-BOBBY", "Bobby Hawkins", "South Central Special Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Central Special Cemetery (vote for 3): Bobby Hawkins 362.")
    sp("WY-MURDOCH-CLAUDINE", "Claudine Murdoch", "South Central Special Cemetery District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Central Special Cemetery (vote for 3): Claudine Murdoch 356.")
    sp("WY-WEIDENHAFT-DEBIE", "Debie Weidenhaft", "South Central Special Cemetery District Trustee (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, South Central Special Cemetery 2-year: Debie Weidenhaft 550, Arthur McChesney 497. Takes office January 2027.")
    sp("WY-MCCHESNEY-ARTHUR", "Arthur McChesney", "South Central Special Cemetery District Trustee (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, South Central Special Cemetery 2-year: Arthur McChesney 497.")

    # Shoshone Conservation
    sp("WY-ELLIS-SPENCER", "Spencer Ellis", "Shoshone Conservation District Rural Supervisor", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Shoshone Conserv Rural (vote for 2): Spencer Ellis 2,114, Brad Tippetts 2,030.")
    sp("WY-TIPPETTS-BRAD", "Brad Tippetts", "Shoshone Conservation District Rural Supervisor", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Shoshone Conserv Rural (vote for 2): Brad Tippetts 2,030.")
    sp("WY-GRANT-KEITH", "Keith Grant", "Shoshone Conservation District Rural Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Shoshone Conserv Rural: Keith Grant 1,615. Takes office January 2027.")
    sp("WY-HESSENTHALER-DAVID", "David Hessenthaler", "Shoshone Conservation District Urban Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Shoshone Conserv Urban: David Hessenthaler 1,656. Takes office January 2027.")
    sp("WY-GUCCION-ROBERT", "Robert Guccion", "Shoshone Conservation District At-Large Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Shoshone Conserv At Large: Robert Guccion 1,582. Takes office January 2027.")

    # South Big Horn Conservation
    sp("WY-HAMILTON-LINDA", "Linda Hamilton", "South Big Horn Conservation District Rural Supervisor", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Big Horn Conserv Rural (vote for 2): Linda Hamilton 2,057, Walter W. Hibbert 1,997.")
    sp("WY-HIBBERT-WALTER-W", "Walter W. Hibbert", "South Big Horn Conservation District Rural Supervisor", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Big Horn Conserv Rural (vote for 2): Walter W. Hibbert 1,997.")
    sp("WY-KELSO-GEORGE", "George Kelso", "South Big Horn Conservation District Rural Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Big Horn Conserv Rural: George Kelso 1,925. Takes office January 2027. Same official name also won a 2026 Emblem Cemetery seat.")
    sp("WY-JOHNSON-EDDIE-L", "Eddie L. Johnson", "South Big Horn Conservation District Urban Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Big Horn Conserv Urban: Eddie L. Johnson 1,812. Takes office January 2027.")
    sp("WY-WILDMAN-HOWARD", "Howard Wildman", "South Big Horn Conservation District At-Large Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Big Horn Conserv At Large: Howard Wildman 1,754. Takes office January 2027.")

    # Fire districts
    sp("WY-JOLLEY-BRUCE-H", "Bruce H. Jolley", "Big Horn Fire District #1 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Protection Dist 1 Director (vote for 2): Bruce H. Jolley 693, Greg Rael 674. Same official name as the sitting commissioner.")
    sp("WY-RAEL-GREG", "Greg Rael", "Big Horn Fire District #1 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 1 Director (vote for 2): Greg Rael 674.")
    sp("WY-LEONHARDT-MICHAEL-H", "Michael H. Leonhardt", "Big Horn Fire District #1 Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Fire Dist 1 Director: Michael H. Leonhardt 584. Takes office January 2027.")
    sp("WY-CRAFT-DEB", "Deb Craft", "Big Horn Fire District #2 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 2 Director (vote for 2): Deb Craft 192, Barbara Anne Greene 168. Official 2026 Fire Dist 2 was write-in only (31 write-ins) and is not filled.")
    sp("WY-GREENE-BARBARA-ANNE", "Barbara Anne Greene", "Big Horn Fire District #2 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 2 Director (vote for 2): Barbara Anne Greene 168.")
    sp("WY-FOSS-LUKE", "Luke Foss", "Big Horn Fire District #3 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 3 Director (vote for 2): Luke Foss 95, Dave Paumer 86.")
    sp("WY-PAUMER-DAVE", "Dave Paumer", "Big Horn Fire District #3 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 3 Director (vote for 2): Dave Paumer 86.")
    sp("WY-WILDMAN-JOE", "Joe Wildman", "Big Horn Fire District #3 Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Fire Dist 3 Director: Joe Wildman 67. Takes office January 2027.")
    sp("WY-DAVIDSON-SUSAN", "Susan Davidson", "Big Horn Fire District #4 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 4 Director (vote for 2): Susan Davidson 398 was a clear official named winner. Other named totals and a large write-in figure on the official scan were not locked because of messy OCR, and no certified named write-in winner is recorded.")
    sp("WY-HIBBERT-GARY", "Gary Hibbert", "Big Horn Fire District #4 Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Fire Dist 4 Director: Gary Hibbert 314. Takes office January 2027.")
    sp("WY-GRIFFIN-KEVIN", "Kevin Griffin", "Big Horn Fire District #5 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 5 Director (vote for 2): Kevin Griffin 61, Cherie Wambeke 2.")
    sp("WY-WAMBEKE-CHERIE", "Cherie Wambeke", "Big Horn Fire District #5 Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist 5 Director (vote for 2): Cherie Wambeke 2.")
    sp("WY-WAMBEKE-KENDAL", "Kendal Wambeke", "Big Horn Fire District #5 Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Fire Dist 5 Director: Kendal Wambeke 53, Stephanie Wambeke 12. Takes office January 2027.")

    # Park County Fire Dist 1 (tiny official Big Horn sliver)
    sp("WY-EASUM-ROGER", "Roger Easum", "Park County Fire Protection District #1 Director 2", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 Big Horn canvass, Park Co Fire Prot Dist 1 Director 2: Roger Easum 6, Matt McCaslin 4 (tiny official Big Horn sliver). Whole-district official Park canvass, if later combined, is not re-keyed here.")
    sp("WY-MCCASLIN-MATT", "Matt McCaslin", "Park County Fire Protection District #1 Director 2", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 Big Horn canvass, Park Co Fire Prot Dist 1 Director 2: Matt McCaslin 4.")
    sp("WY-HENY-SCOTT", "Scott Heny", "Park County Fire Protection District #1 Director 4", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 Big Horn canvass, Park Co Fire Prot Dist 1 Director 4: Scott Heny.")
    sp("WY-BAGNELL-SCOTT", "Scott Bagnell", "Park County Fire Protection District #1 Director 1", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Park Co Fire Dist 1 Directors 1/3/5 (Big Horn sliver, contest totals 8): Scott Bagnell 7, Gerald (Bear) May 7, Heath Worstell 7. Takes office January 2027.")
    sp("WY-MAY-GERALD-BEAR", "Gerald (Bear) May", "Park County Fire Protection District #1 Director 3", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Park Co Fire Dist 1 Director 3 (Big Horn sliver): Gerald (Bear) May 7.")
    sp("WY-WORSTELL-HEATH", "Heath Worstell", "Park County Fire Protection District #1 Director 5", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Park Co Fire Dist 1 Director 5 (Big Horn sliver): Heath Worstell 7.")

    # North Hospital
    sp("WY-WINTERHOLLER-DAVID-A", "David A. Winterholler", "North Big Horn County Hospital District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Hospital At Large (vote for 2): David A. Winterholler 2,141, Max Lewis 1,802.")
    sp("WY-LEWIS-MAX", "Max Lewis", "North Big Horn County Hospital District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Hospital At Large (vote for 2): Max Lewis 1,802. Same official name also holds a Cowley council seat.")
    sp("WY-CRUMRINE-PATRICIA", "Patricia Crumrine", "North Big Horn County Hospital District Trustee Lovell", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Hospital Trustee Lovell: Patricia Crumrine 2,324.")
    sp("WY-MORRISON-BRUCE", "Bruce Morrison", "North Big Horn County Hospital District Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, North Hospital At Large (vote for 2): only Bruce Morrison 1,637 is a named official winner (write-ins 311 are not combined into a certified name). Takes office January 2027.")
    sp("WY-CROSBY-BRETT", "Brett Crosby", "North Big Horn County Hospital District Trustee Byron-Cowley", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, North Hospital Byron-Cowley: Brett Crosby 1,583. Takes office January 2027.")
    sp("WY-FRESCOLN-GARRET-I", "Garret I. Frescoln", "North Big Horn County Hospital District Trustee Deaver-Frannie", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, North Hospital Deaver-Frannie: Garret I. Frescoln 1,489. Takes office January 2027.")

    # South Hospital
    sp("WY-CRAFT-TRUDY-E", "Trudy E. Craft", "South Big Horn County Hospital District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Hospital At Large (vote for 3): Trudy E. Craft 2,088, Fred Werner 1,849, Michael Scherman 1,510.")
    sp("WY-WERNER-FRED", "Fred Werner", "South Big Horn County Hospital District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Hospital At Large (vote for 3): Fred Werner 1,849.")
    sp("WY-SCHERMAN-MICHAEL", "Michael Scherman", "South Big Horn County Hospital District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Hospital At Large (vote for 3): Michael Scherman 1,510.")
    sp("WY-PETTY-JEFF", "Jeff Petty", "South Big Horn County Hospital District Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, South Hospital At Large (vote for 2): only Jeff Petty 1,707 is a named official winner. Takes office January 2027.")

    # North Senior
    sp("WY-SCHEFFLER-LORI", "Lori Scheffler", "North Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Senior At Large (vote for 3): Lori Scheffler 2,077, Annella Prosser 1,879, Edie Crosby 1,842.")
    sp("WY-PROSSER-ANNELLA", "Annella Prosser", "North Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Senior At Large (vote for 3): Annella Prosser 1,879.")
    sp("WY-CROSBY-EDIE", "Edie Crosby", "North Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, North Senior At Large (vote for 3): Edie Crosby 1,842.")
    sp("WY-TIPPETTS-PAULINE", "Pauline Tippetts", "North Senior Citizen Service District Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, North Senior (vote for 2): Pauline Tippetts 1,518, Patricia Parmer 1,423. Takes office January 2027.")
    sp("WY-PARMER-PATRICIA", "Patricia Parmer", "North Senior Citizen Service District Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, North Senior (vote for 2): Patricia Parmer 1,423.")
    sp("WY-MILLER-LINDA-JO", "Linda Jo Miller", "North Senior Citizen Service District Trustee At Large (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, North Senior 2-year: Linda Jo Miller 1,601. Takes office January 2027.")

    # South Senior — 2026 regular and 2-year were write-in only and are not filled
    sp("WY-BONNEL-PHILLIPS-KRISTI-L", "Kristi L. Bonnel-Phillips", "South Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Senior At Large (vote for 3): Kristi L. Bonnel-Phillips 2,005, Diane Nuttall 1,909, Sherri Emmett 1,888. Official 2026 regular and 2-year South Senior contests were write-in only and are not filled.")
    sp("WY-NUTTALL-DIANE", "Diane Nuttall", "South Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Senior At Large (vote for 3): Diane Nuttall 1,909.")
    sp("WY-EMMETT-SHERRI", "Sherri Emmett", "South Senior Citizen Service District Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, South Senior At Large (vote for 3): Sherri Emmett 1,888.")

    # Rural Health Dist 1
    sp("WY-RATHBUN-DEB", "Deb Rathbun", "Rural Health District #1 Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Rural Health Dist 1 (vote for 2): Deb Rathbun 1,654, Deb Fowler 1,637.")
    sp("WY-FOWLER-DEB", "Deb Fowler", "Rural Health District #1 Trustee At Large", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Rural Health Dist 1 (vote for 2): Deb Fowler 1,637.")
    sp("WY-NELSON-KENNETH", "Kenneth Nelson", "Rural Health District #1 Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Rural Health Dist 1 (vote for 3): Kenneth Nelson 1,114, Theresa Turner 1,015, Russell Fowler 1,008. Takes office January 2027.")
    sp("WY-TURNER-THERESA", "Theresa Turner", "Rural Health District #1 Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Rural Health Dist 1 (vote for 3): Theresa Turner 1,015.")
    sp("WY-FOWLER-RUSSELL", "Russell Fowler", "Rural Health District #1 Trustee At Large", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Rural Health Dist 1 (vote for 3): Russell Fowler 1,008.")
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [
            ("Senate District 19 (S19)", 1),
            ("Senate District 20 (S20)", 1),
        ],
        "state-house": [
            ("House District 26 (H26)", 1),
            ("House District 27 (H27)", 1),
            ("House District 28 (H28)", 1),
        ],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "judicial": [
            ("District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", 1),
            ("Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", 1),
            ("District Judge, 5th Judicial District (Park)", 1),
            ("Circuit Judge, 5th Judicial District (Park)", 1),
        ],
        "municipal": [
            ("Basin Mayor", 1), ("Basin Town Council", 4),
            ("Burlington Mayor", 1), ("Burlington Town Council", 4), ("Burlington Town Council (2-year)", 1),
            ("Byron Mayor", 1), ("Byron Town Council", 4),
            ("Cowley Mayor", 1), ("Cowley Town Council", 4),
            ("Deaver Mayor", 1), ("Deaver Town Council", 4), ("Deaver Town Council (2-year)", 1),
            ("Frannie Mayor", 1), ("Frannie Town Council", 4), ("Frannie Town Council (2-year)", 1),
            ("Greybull Mayor", 1), ("Greybull Town Council", 4), ("Greybull Town Council (2-year)", 1),
            ("Lovell Mayor", 1), ("Lovell Town Council", 4),
            ("Manderson Mayor", 1), ("Manderson Town Council", 4), ("Manderson Town Council (2-year)", 1),
        ],
        "schools": [
            ("Big Horn County School District #1 Trustee At Large", 3),
            ("Big Horn County School District #1 Trustee Area A", 1),
            ("Big Horn County School District #1 Trustee Area B", 1),
            ("Big Horn County School District #1 Trustee Area C", 1),
            ("Big Horn County School District #1 Trustee Area D", 1),
            ("Big Horn County School District #2 Trustee At Large", 7),
            ("Big Horn County School District #2 Trustee At Large (2-year)", 1),
            ("Big Horn County School District #3 Trustee At Large", 7),
            ("Big Horn County School District #4 Trustee At Large", 3),
            ("Big Horn County School District #4 Trustee Area J", 3),
            ("Big Horn County School District #4 Trustee Area K/L", 1),
        ],
        "special-districts": [
            ("Burlington Cemetery District Trustee", 6),
            ("Burlington Cemetery District Trustee (2-year)", 1),
            ("Byron Cemetery District Trustee", 6),
            ("Cowley Cemetery District Trustee", 6),
            ("Cowley Cemetery District Trustee (2-year)", 1),
            ("Deaver-Frannie Cemetery District Trustee", 6),
            ("Deaver-Frannie Cemetery District Trustee (2-year)", 1),
            ("Emblem Cemetery District Trustee", 6),
            ("Hyattville Cemetery District Trustee", 6),
            ("Lovell Cemetery District Trustee", 6),
            ("Otto Cemetery District Trustee", 6),
            ("South Central Special Cemetery District Trustee", 6),
            ("South Central Special Cemetery District Trustee (2-year)", 2),
            ("Shoshone Conservation District Rural Supervisor", 3),
            ("Shoshone Conservation District Urban Supervisor", 1),
            ("Shoshone Conservation District At-Large Supervisor", 1),
            ("South Big Horn Conservation District Rural Supervisor", 3),
            ("South Big Horn Conservation District Urban Supervisor", 1),
            ("South Big Horn Conservation District At-Large Supervisor", 1),
            ("Big Horn Fire District #1 Director", 3),
            ("Big Horn Fire District #2 Director", 3),
            ("Big Horn Fire District #3 Director", 3),
            ("Big Horn Fire District #4 Director", 3),
            ("Big Horn Fire District #5 Director", 3),
            ("Park County Fire Protection District #1 Director 1", 1),
            ("Park County Fire Protection District #1 Director 2", 2),
            ("Park County Fire Protection District #1 Director 3", 1),
            ("Park County Fire Protection District #1 Director 4", 1),
            ("Park County Fire Protection District #1 Director 5", 1),
            ("North Big Horn County Hospital District Trustee At Large", 4),
            ("North Big Horn County Hospital District Trustee Lovell", 1),
            ("North Big Horn County Hospital District Trustee Byron-Cowley", 1),
            ("North Big Horn County Hospital District Trustee Deaver-Frannie", 1),
            ("South Big Horn County Hospital District Trustee At Large", 5),
            ("North Senior Citizen Service District Trustee At Large", 5),
            ("North Senior Citizen Service District Trustee At Large (2-year)", 1),
            ("South Senior Citizen Service District Trustee At Large", 3),
            ("South Senior Citizen Service District Trustee At Large (2-year)", 1),
            ("Rural Health District #1 Trustee At Large", 5),
        ],
    }



def _office(title, holders, *, layout="office-and-name", note=""):
    rec = {"office": title, "layout": layout, "holders": holders}
    if note:
        rec["note"] = note
    return rec


def _holder(people, pid, name, party, term_end, notes=""):
    rec = {"name": name, "person_id": pid, "party": party or "", "term_end": term_end}
    if notes:
        rec["notes"] = notes
    return rec


def _holders_for_office(terms, people, office, as_of="2026-11-24", elect_start="2027-01-04"):
    cur = [t for t in terms if t["office"] == office and t["term_start"] <= as_of < t["term_end"]]
    elects = [t for t in terms if t["office"] == office and t["term_start"] == elect_start]
    seen = set()
    out = []
    current_ids = {t["person_id"] for t in cur}

    def te(t):
        if t["term_end"][5:7] in {"05", "06", "07", "09"} and t["term_end"][5:10] != "01-04" and t["term_end"][5:7] != "01":
            months = {"05": "May", "06": "June", "07": "July", "09": "September"}
            return months.get(t["term_end"][5:7], "January") + " " + t["term_end"][:4]
        return "January " + t["term_end"][:4]

    def term_len(t):
        try:
            return int(t["term_end"][:4]) - int(t["term_start"][:4])
        except Exception:
            return 4

    departing = [t for t in cur if t["term_end"] == elect_start and t["person_id"] not in {e["person_id"] for e in elects}]
    new_elects = [e for e in elects if e["person_id"] not in current_ids]
    departing = sorted(departing, key=lambda t: (-term_len(t), t["name"]))
    new_elects = sorted(new_elects, key=lambda t: (-term_len(t), t["name"]))
    remaining_e = list(new_elects)
    paired = []
    used_e = set()
    for t in departing:
        match = next((e for e in remaining_e if e["person_id"] not in used_e and term_len(e) == term_len(t)), None)
        if match is None:
            match = next((e for e in remaining_e if e["person_id"] not in used_e), None)
        if match:
            paired.append((t, match))
            used_e.add(match["person_id"])
    departing = [t for t, _ in paired]
    new_elects = [e for _, e in paired]

    succ_map = {}
    for t, e in zip(departing, new_elects):
        succ_map[t["person_id"]] = e
        seen.add(e["person_id"])

    for t in elects:
        if t["person_id"] in current_ids and t["person_id"] not in seen:
            out.append(_holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or ""))
            seen.add(t["person_id"])
    for t in cur:
        if t["person_id"] in seen:
            continue
        h = _holder(people, t["person_id"], t["name"], t.get("party") or "", te(t), t.get("notes") or "")
        e = succ_map.get(t["person_id"])
        if e:
            h["succeeding"] = {
                "name": e["name"],
                "person_id": e["person_id"],
                "party": e.get("party") or "",
                "takes_office": "January",
            }
        out.append(h)
        seen.add(t["person_id"])
    leftover = [e for e in elects if e["person_id"] not in seen]
    if leftover and not cur:
        # Elects only: do not list them as if they already hold the seat.
        # Current holder stays Not yet collected; the official 2026 winner is the January elect.
        for e in leftover:
            h = {
                "name": "Not yet collected",
                "person_id": "",
                "party": "",
                "term_end": "",
                "notes": e.get("notes") or "",
                "succeeding": {
                    "name": e["name"],
                    "person_id": e["person_id"],
                    "party": e.get("party") or "",
                    "takes_office": "January",
                },
            }
            out.append(h)
            seen.add(e["person_id"])
    else:
        for e in leftover:
            h = _holder(people, e["person_id"], e["name"], e.get("party") or "", te(e), e.get("notes") or "")
            h["notes"] = ((h.get("notes") or "") + " Takes office January 2027.").strip()
            out.append(h)
            seen.add(e["person_id"])
    return out


def _nyc():
    return [{"name": "Not yet collected", "person_id": "", "party": "", "term_end": ""}]



def build_big_horn():
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
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "Fifth Judicial District and Circuit judges serving Big Horn with Hot Springs and Washakie (Bobbi Overfield, "
        "Ed Luhm / Edward G. Luhm) and the Park-seat judges (Bill Simpson, Joey Darrah), from official court roster "
        "titles already used in the official Park and Washakie histories. Official 2026 Big Horn canvass retention "
        "for Judge Bobbi Overfield is YES 2,876 / NO 722. Official 2026 RETAIN JUDGE BEN BURNINGHAM is the statewide "
        "Chancery Court retention already in the shared terms, not a Fifth Judicial District circuit office."
    )
    coverage = H.write_terms_and_snapshots(
        county="Big Horn", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Big Horn", slug=SLUG)
    print("copied shared terms", copied, "coverage", coverage)
    return people, terms, coverage


def update_big_horn_json(people, terms):
    path = ROOT / "data" / "county_officials" / "big-horn.json"
    data = json.loads(path.read_text())
    precincts = None
    for grp in data.get("groups") or []:
        if grp.get("id") == "precincts":
            precincts = grp
            break
    data["as_of"] = RETRIEVED
    data["county_number"] = CN
    data["term_switch_date"] = "2027-01-04"
    data["intro"] = (
        "Names are the people in office today. Where the latest general election chose a different person, "
        "that change is shown beside the name. Those elects take office in January."
    )
    exp = expected_offices()
    notes = {
        "Senate District 19 (S19)":
            "Official 2022 SOS statewide Senate summary, Senate District 19: Dan Laursen (R); official Big Horn share 2,637, official Park share 2,901. Official 2026 SOS: R. J. Kost (R); official Big Horn share 2,562 (official clerk abstract same), official Park share 2,749, taking office January 2027.",
        "Senate District 20 (S20)":
            "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Big Horn share 1,475 (official 2024 clerk canvass same 1,475); official Washakie 3,442, Hot Springs 2,180, Park 834, Fremont 305. Covers Big Horn, Hot Springs, Fremont, Park, and Washakie. Off-cycle in 2026.",
        "House District 26 (H26)":
            "Official 2026 SOS statewide House summary, House District 26: Dalton Banks (R) Total 2,557, Ralph Nieder-Westermann (D) 571. Official Big Horn share Banks 2,301, Nieder-Westermann 538 (official clerk abstract same); official Park Banks 256, Nieder-Westermann 33. Re-elected. Official 2024 Big Horn share Banks 3,584.",
        "House District 27 (H27)":
            "Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Big Horn share Lawley 418, Livingston 60 (official clerk abstract same); official Washakie Lawley 2,282, Livingston 430. Also covers Washakie. Re-elected.",
        "House District 28 (H28)":
            "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Big Horn share Winter 920, Alwin 85. Official 2026 SOS: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504; official Big Horn share Hogg 655, Alwin 66, taking office January 2027. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters.",
        "County Commissioner":
            "Official commissioners page, retrieved 2026-11-24: Deb Craft (Chair), Bruce H. Jolley, Dave Neves. Official 2024 canvass elected Bruce H. Jolley at large (5,081). Official 2026 canvass (vote for 2): Mike Laird 3,159, Jared Boardman 2,991, taking office January 2027. Incoming names are shown with the 2022-class commissioners, not as one-to-one seat replacements.",
        "County Clerk":
            "Official 2026 canvass minutes name County Clerk Lori Smallwood. Official 2026 general: REP LORI SMALLWOOD 3,789, re-elected.",
        "County Treasurer":
            "Official treasurer page, retrieved 2026-11-24: Nicole Vigil. Official 2026 general: REP NICOLE VIGIL 3,707, re-elected.",
        "County Assessor":
            "Official assessor page, retrieved 2026-11-24: Cozette Winters, County Assessor. Official 2026 general: REP COZETTE WINTERS 3,738, re-elected.",
        "County Sheriff":
            "Official Sheriff Staff page, retrieved 2026-11-24: Sheriff Jason Beal. Official 2026 canvass: REP CRAIG R. SHIDLER 3,702, taking office January 2027 (undersheriff on the same official staff page).",
        "County Attorney":
            "Official attorney page, retrieved 2026-11-24: Marcia Bean. Official 2026 canvass: REP MARCIA E. BEAN 3,271, re-elected.",
        "Clerk of District Court":
            "Official 2026 canvass, Clerk of District Court: REP SERENA K. LIPP 3,824, re-elected.",
        "County Coroner":
            "Official coroner page, retrieved 2026-11-24: Michael K. Jameson. Official 2026 canvass: REP MICHAEL K. JAMESON 3,768, re-elected.",
        "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)":
            "Official March 2026 judicial roster title already used in official Park and Washakie histories. Official 2026 Big Horn canvass, RETAIN JUDGE BOBBI OVERFIELD: YES 2,876 / NO 722. Retained, continuing January 2027.",
        "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)":
            "Official 2024 Big Horn canvass, RETAIN JUDGE EDWARD G. LUHM: YES 4,081 / NO 864. Official roster name Ed Luhm (Edward G. Luhm).",
        "District Judge, 5th Judicial District (Park)":
            "Official 2024 Big Horn canvass, RETAIN JUDGE BILL SIMPSON: YES 4,155 / NO 903. Official March 2026 roster names Bill Simpson (Park district judge).",
        "Circuit Judge, 5th Judicial District (Park)":
            "Official 2024 Big Horn canvass, RETAIN JUDGE S. JOSEPH JOEY DARRAH: YES 4,097 / NO 906. Official roster name Joey Darrah (Park circuit).",
        "Greybull Mayor":
            "Official 2022 Custom Table Report page 27 of 74 (visually confirmed): MYLES R. FOLEY 414, write-ins 43, contest total 560. Official 2026 canvass: Michael Johnston 378, Bill Brenner 201, taking office January 2027.",
        "Big Horn Fire District #2 Director":
            "Official 2024 canvass (vote for 2): Deb Craft 192, Barbara Anne Greene 168. Official 2026 Fire Dist 2 was write-in only (31 write-ins) and is not filled.",
        "South Senior Citizen Service District Trustee At Large":
            "Official 2024 canvass (vote for 3): Kristi L. Bonnel-Phillips 2,005, Diane Nuttall 1,909, Sherri Emmett 1,888. Official 2026 regular and 2-year contests were write-in only and are not filled.",
        "South Senior Citizen Service District Trustee At Large (2-year)":
            "Official 2026 South Senior 2-year contest was write-in only (186 write-ins) and is not filled.",
        "Big Horn County School District #4 Trustee Area K/L":
            "Official 2024 Area K/L was write-in only (125 write-ins, no certified named winner). Official 2026 canvass: Brenda Wood 691, taking office January 2027.",
        "North Big Horn County Hospital District Trustee At Large":
            "Official 2024 canvass (vote for 2): David A. Winterholler 2,141, Max Lewis 1,802. Official 2026 (vote for 2) named only Bruce Morrison 1,637 (write-ins 311 are not combined into a certified name).",
        "South Big Horn County Hospital District Trustee At Large":
            "Official 2024 canvass (vote for 3): Trudy E. Craft 2,088, Fred Werner 1,849, Michael Scherman 1,510. Official 2026 (vote for 2) named only Jeff Petty 1,707.",
    }

    def holders(office, n=1):
        h = _holders_for_office(terms, people, office)
        while len(h) < n:
            h.append({"name": "Not yet collected", "person_id": "", "party": "", "term_end": ""})
        return h if h else _nyc()

    def block(gid, layout_default="office-and-name"):
        out = []
        for title, n in exp[gid]:
            layout = "heading-then-names" if n > 1 else layout_default
            rec = _office(title, holders(title, n), layout=layout, note=notes.get(title, ""))
            out.append(rec)
        return out

    senate = block("state-senate")
    house = block("state-house")
    county = block("county")
    judicial = block("judicial")
    municipal = block("municipal")
    schools = block("schools")
    specials = block("special-districts")

    groups = [
        {"id": "state-senate", "title": "State Senate offices", "label": "Wyoming Senate", "offices": senate},
        {"id": "state-house", "title": "State House offices", "label": "Wyoming House", "offices": house},
        {"id": "county", "title": "County Offices", "label": "County offices", "offices": county},
        {"id": "municipal", "title": "Municipal offices", "label": "Municipal offices", "offices": municipal},
        {"id": "schools", "title": "School boards", "label": "School boards", "offices": schools},
        {"id": "special-districts", "title": "Special districts", "label": "Special districts", "offices": specials},
        {"id": "judicial", "title": "Judicial retention (district and circuit)", "label": "Judicial", "offices": judicial},
    ]
    for grp in (senate, house, county, municipal, schools, specials, judicial):
        for rec in grp:
            if not rec.get("holders"):
                rec["holders"] = _nyc()
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_2026_GEN,
        "primary_results": URL_2026_PRI,
        "clerk_archive": URL_ELEC,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/big-horn/SOURCES.md",
    }
    apply_to_groups(data["groups"], 'big-horn')
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
