#!/usr/bin/env python3
"""Hot Springs County officeholder history (preview). Official clerk, SOS, court,
town, and school-board sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 15
SLUG = "hot-springs"

URL_COUNTY = "https://hscounty.com/"
URL_ELEC = "https://hscounty.com/elections"
URL_COMM = "https://hscounty.com/government/commissioners"
URL_CLERK = "https://hscounty.com/departments/clerk"
URL_ASSESSOR = "https://hscounty.com/departments/assessor"
URL_TREAS = "https://hscounty.com/departments/treasurer"
URL_SHERIFF = "https://hscounty.com/departments/sheriff"
URL_ATTORNEY = "https://hscounty.com/departments/attorney"
URL_CDC = "https://hscounty.com/departments/clerk-of-court"
URL_2026_GEN = "https://hscounty.com/component/edocman/2026-hot-springs-co-general-election-offical-results/download?Itemid=100"
URL_2026_PRI = "https://hscounty.com/component/edocman/2026-hot-springs-co-primary-election-official-results/download?Itemid=100"
URL_2024_GEN = "https://hscounty.com/component/edocman/2024-hot-springs-co-general-election-official-results-2/download?Itemid=100"
URL_2022_GEN = "https://hscounty.com/component/edocman/2022-county-general-official-results/download?Itemid=100"
URL_THERM = "https://thermopoliswy.gov/about/mayor-and-town-council/"
URL_HS1 = "https://www.hotsprings1.org/apps/pages/index.jsp?uREC_ID=3692288&type=d"


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


SRC_COMM = S("Official Hot Springs County Commissioners page, retrieved 2026-11-24: Chairman Bob Aguiar; Commissioners Paul Galovich and Tom Ryan", URL_COMM)
SRC_CLERK = S("Official Hot Springs County Clerk page, retrieved 2026-11-24: Becky Kersten (official photo alt). Official post-election audit notice dated November 9, 2026, also names Becky Kersten, Hot Springs County Clerk.", URL_CLERK)
SRC_ASSESSOR = S("Official Hot Springs County Assessor page, retrieved 2026-11-24: Daniel Webber", URL_ASSESSOR)
SRC_TREAS = S("Official Hot Springs County Treasurer page, retrieved 2026-11-24: Julie Mortimore", URL_TREAS)
SRC_SHERIFF = S("Official Hot Springs County Sheriff page, retrieved 2026-11-24: Jerimie Kraushaar, Sheriff", URL_SHERIFF)
SRC_ATTORNEY = S("Official Hot Springs County Attorney page, retrieved 2026-11-24: Jill Logan", URL_ATTORNEY)
SRC_CDC = S("Official Hot Springs County Clerk of District Court page, retrieved 2026-11-24: Kris McNeff", URL_CDC)
SRC_ELEC = S("Official Hot Springs County Elections page and Election Results & Archives, retrieved 2026-11-24", URL_ELEC)
SRC_2026 = S(
    "Official Hot Springs County General Election Summary, November 3, 2026 "
    "(header OFFICIAL RESULTS, GENERAL ELECTION; Precincts Complete 5 of 5; Ballots Cast - Total 2,155; "
    "handwritten Canvass 11-5-2026, signed including Becky Kersten; footer County - General Election Summary - 11/05/2026 02:26PM, Page 1 of 8). "
    "The official elections archive filename uses the typo OFFICAL; the face of the file is official and is used as the canvass.",
    URL_2026_GEN,
)
SRC_2026_PRI = S(
    "Official Hot Springs County Primary Election Summary, August 18, 2026 "
    "(header OFFICIAL RESULTS, PRIMARY ELECTION; Precincts Complete 5 of 5; Ballots Cast - Total 1,833; "
    "handwritten Canvass 8-20-26, signed including Becky Kersten; footer 08/20/2026 03:07PM, Page 1 of 13).",
    URL_2026_PRI,
)
SRC_2026_FILING = S(
    "Official Hot Springs County 2026 General Election Candidate Roster, Final - Updated (official clerk filings, created August 31, 2026).",
    "https://hscounty.com/component/edocman/2026-general-candidate-filing-final-amended/download?Itemid=100",
)
SRC_2026_PROC = S(
    "Official Hot Springs County Amended 2026 General Election Proclamation (August 14, 2026): School District #1 Trustee, three 4-year terms and one 2-year unexpired term.",
    "https://hscounty.com/component/edocman/amended-general-proclamation-2026/download?Itemid=100",
)
SRC_2024 = S(
    "Official Hot Springs County General Election Summary, November 5, 2024 "
    "(header OFFICIAL RESULTS, GENERAL ELECTION; Precincts Complete 5 of 5; Ballots Cast - Total 2,643; "
    "signed official canvass including Becky Kersten; footer County - General Election Summary - 11/07/2024 02:46PM, Page 1 of 5). "
    "The official PDF also includes precinct pages; countywide totals are taken from the official 5-page summary.",
    URL_2024_GEN,
)
SRC_2022 = S(
    "Official Hot Springs County General Election Summary, November 8, 2022 "
    "(header OFFICIAL RESULTS, GENERAL ELECTION; Precincts Complete 5 of 5; Ballots Cast - Total 2,213; "
    "footer County - General Election Summary - 11/14/2022 9:00 AM). Born-digital official canvass, 13 pages.",
    URL_2022_GEN,
)
SRC_THERM = S(
    "Official Town of Thermopolis Mayor and Town Council page, retrieved 2026-11-24: Mayor Adam R. Estenson; Council Members Rachel Hughes, Tony Larson, Dusty Lewis, and John Dorman Sr.",
    URL_THERM,
)
SRC_HS1 = S(
    "Official Hot Springs County School District #1 Board of Trustees page, retrieved 2026-11-24. "
    "A seven-member board: Jennifer Axtell (Chair, term expires 12/2026), Chauncy Johnson (Treasurer, 12/2026), "
    "Marshall Keller (Vice-Chairman, 12/2028), Jean Skelton (12/2028), Sherman Skelton (12/2026), "
    "Bethany Webber (12/2026), Nichole Weyer (Board Clerk, 12/2028). Official December expirations are mapped to January for pairing, with the official December date noted.",
    URL_HS1,
)
SRC_COURT = S(
    "Official Wyoming Judicial Branch March 2026 roster titles already used in the official Park, Washakie, and Big Horn histories: "
    "Fifth Judicial District Judge Bobbi Overfield (Big Horn/Hot Springs/Washakie); "
    "Fifth Judicial Circuit Judge Ed Luhm (Edward G. Luhm) (Big Horn/Hot Springs/Washakie); "
    "Fifth Judicial District Judge Bill Simpson (Park); Circuit Judge Joey Darrah (Park).",
    "",
)


def register_people(P):
    P("WY-GEIS-GERALD-E", "Gerald E. Geis", "Gerald", "Geis", middle="E.")
    P("WY-AGAR-WYATT", "Wyatt Agar", "Wyatt", "Agar")
    P("WY-COOPER-ED", "Ed Cooper", "Ed", "Cooper")
    P("WY-WINTERS-NATHAN", "Nathan Winters", "Nathan", "Winters")
    P("WY-WINTER-JOHN-R", "John R. Winter", "John", "Winter", middle="R.", aliases="John Winter")
    P("WY-HOGG-ALLEN", "Allen Hogg", "Allen", "Hogg")
    P("WY-AGUIAR-BOB", "Bob Aguiar", "Bob", "Aguiar")
    P("WY-GALOVICH-PAUL-M", "Paul M. Galovich", "Paul", "Galovich", middle="M.", aliases="Paul Galovich")
    P("WY-RYAN-THOMAS-J", "Thomas J. Ryan", "Thomas", "Ryan", middle="J.", aliases="Tom Ryan")
    P("WY-AXTELL-CHIP", "Chip Axtell", "Chip", "Axtell")
    P("WY-SCHEEL-PHILLIP", "Phillip Scheel", "Phillip", "Scheel")
    P("WY-KERSTEN-BECKY", "Becky Kersten", "Becky", "Kersten")
    P("WY-MORTIMORE-JULIE", "Julie Mortimore", "Julie", "Mortimore")
    P("WY-NOORDA-STACIA", "Stacia Noorda", "Stacia", "Noorda")
    P("WY-WEBBER-DANIEL", "Daniel Webber", "Daniel", "Webber")
    P("WY-KRAUSHAAR-JERIMIE", "Jerimie Kraushaar", "Jerimie", "Kraushaar")
    P("WY-LOGAN-JILL", "Jill Logan", "Jill", "Logan")
    P("WY-CORNELLA-TERRI", "Terri Cornella", "Terri", "Cornella")
    P("WY-MCNEFF-KRIS", "Kris McNeff", "Kris", "McNeff")
    P("WY-MORTIMORE-MARK", "Mark Mortimore", "Mark", "Mortimore")
    P("WY-OVERFIELD-BOBBI", "Bobbi Overfield", "Bobbi", "Overfield")
    P("WY-LUHM-ED", "Ed Luhm", "Ed", "Luhm", aliases="Edward G. Luhm; EDWARD G. LUHM")
    P("WY-SIMPSON-BILL", "Bill Simpson", "Bill", "Simpson")
    P("WY-DARRAH-JOEY", "Joey Darrah", "Joey", "Darrah", aliases="S. Joseph Joey Darrah")
    P("WY-ESTENSON-ADAM-R", "Adam R. Estenson", "Adam", "Estenson", middle="R.", aliases="Adam Ryan Estenson; ADAM RYAN ESTENSON")
    P("WY-HUGHES-RACHEL", "Rachel Hughes", "Rachel", "Hughes")
    P("WY-DORMAN-JOHN-SR", "John Dorman Sr.", "John", "Dorman", aliases="John D. Dorman; JOHN D. DORMAN; John Dorman SR.")
    P("WY-LARSON-TONY", "Tony Larson", "Tony", "Larson")
    P("WY-LEWIS-DUSTY", "Dusty Lewis", "Dusty", "Lewis")
    P("WY-SHINKLE-LEVI", "Levi Shinkle", "Levi", "Shinkle")
    P("WY-HOLBERT-GARY-J", "Gary J. Holbert", "Gary", "Holbert", middle="J.", aliases="Gary Holbert; Write-In: Gary Holbert")
    P("WY-BUSH-DOLORES", "Dolores Bush", "Dolores", "Bush")
    P("WY-LACKEY-DEBRA-K", "Debra K. Lackey", "Debra", "Lackey", middle="K.")
    P("WY-MCDONALD-SID", "Sid McDonald", "Sid", "McDonald")
    P("WY-MUSIC-JULIE-DODDS", "Julie Dodds Music", "Julie", "Music", aliases="JULIE DODDS MUSIC")
    P("WY-JOHNSTON-COREY", "Corey Johnston", "Corey", "Johnston")
    P("WY-HAMMOND-GEORGEANNE", "Georgeanne Hammond", "Georgeanne", "Hammond")
    P("WY-SLAGLE-JESSICA", "Jessica Slagle", "Jessica", "Slagle")
    P("WY-RODRIGUEZ-NATHANIEL", "Nathaniel Rodriguez", "Nathaniel", "Rodriguez")
    P("WY-GRAHAM-KIMBERLY", "Kimberly Graham", "Kimberly", "Graham")
    P("WY-CREES-ZACHARY", "Zachary Crees", "Zachary", "Crees")
    P("WY-KEASLING-TINA-L", "Tina L. Keasling", "Tina", "Keasling", middle="L.")
    P("WY-ELLEDGE-CYNTHIA", "Cynthia Elledge", "Cynthia", "Elledge")
    P("WY-SLAGLE-CAROL", "Carol Slagle", "Carol", "Slagle")
    P("WY-SKELTON-SHERMAN", "Sherman Skelton", "Sherman", "Skelton")
    P("WY-AXTELL-JENNIFER", "Jennifer Axtell", "Jennifer", "Axtell")
    P("WY-WEBBER-BETHANY", "Bethany Webber", "Bethany", "Webber", aliases="Bethany Rose Webber; BETHANY ROSE WEBBER")
    P("WY-JOHNSON-CHAUNCY", "Chauncy Johnson", "Chauncy", "Johnson")
    P("WY-BUDD-JUSTIN", "Justin Budd", "Justin", "Budd")
    P("WY-KELLER-MARSHALL", "Marshall Keller", "Marshall", "Keller")
    P("WY-SKELTON-JEAN", "Jean Skelton", "Jean", "Skelton")
    P("WY-WEYER-NICHOLE", "Nichole Weyer", "Nichole", "Weyer")
    P("WY-BOREN-STEPHANIE", "Stephanie Boren", "Stephanie", "Boren")
    P("WY-WILSON-JIM", "Jim Wilson", "Jim", "Wilson")
    P("WY-WARD-PAUL", "Paul Ward", "Paul", "Ward")
    P("WY-NORSWORTHY-JASON", "Jason Norsworthy", "Jason", "Norsworthy")
    P("WY-JONES-WESTON", "Weston Jones", "Weston", "Jones")
    P("WY-SAYERS-DANITA", "Danita Sayers", "Danita", "Sayers")
    P("WY-SORENSEN-BASIL", "Basil Sorensen", "Basil", "Sorensen", aliases="Basil Sorenson")
    P("WY-READY-MERRILL-J", "Merrill J. Ready", "Merrill", "Ready", middle="J.", aliases="Merrill Ready")
    P("WY-KRAUSHAAR-STAN", "Stan Kraushaar", "Stan", "Kraushaar")
    P("WY-DEVRIES-CINDY", "Cindy DeVries", "Cindy", "DeVries")
    P("WY-STANSILL-MARGARET", "Margaret Stansill", "Margaret", "Stansill")
    P("WY-VIETTI-BARBARA-TOMES", "Barbara Tomes Vietti", "Barbara", "Vietti")
    P("WY-JACKSON-MARSHALL", "Marshall Jackson", "Marshall", "Jackson")
    P("WY-MORTIMORE-MIKE", "Mike Mortimore", "Mike", "Mortimore")
    P("WY-OBRIEN-KEITH", "Keith O'Brien", "Keith", "O'Brien")
    P("WY-BYRD-JAMES", "James Byrd", "James", "Byrd")
    P("WY-HUCKFELDT-CLINT", "Clint Huckfeldt", "Clint", "Huckfeldt")
    P("WY-BYRD-MICHAEL", "Michael Byrd", "Michael", "Byrd")
    P("WY-JOHNSON-MELISSA-MCCUMBER", "Melissa McCumber Johnson", "Melissa", "Johnson")
    P("WY-KAY-AIMEE", "Aimee Kay", "Aimee", "Kay")
    P("WY-BENEFIEL-JESSICA", "Jessica Benefiel", "Jessica", "Benefiel")
    P("WY-ANDERSON-JOHN", "John Anderson", "John", "Anderson")
    P("WY-FENTON-JOHN-V", "John V. Fenton", "John", "Fenton", middle="V.")
    P("WY-HUCKFELDT-BRENNA", "Brenna Huckfeldt", "Brenna", "Huckfeldt")
    P("WY-DANIELS-TROY", "Troy Daniels", "Troy", "Daniels")
    P("WY-SHAFFER-RAYMOND-E", "Raymond E. Shaffer", "Raymond", "Shaffer", middle="E.")
    P("WY-SORENSEN-KATHY", "Kathy Sorensen", "Kathy", "Sorensen")
    P("WY-NIELSEN-MARVIN", "Marvin Nielsen", "Marvin", "Nielsen")
    P("WY-BLACK-KIMBERLY-JOY", "Kimberly Joy Black", "Kimberly Joy", "Black")
    P("WY-CHENEY-CURTIS", "Curtis Cheney", "Curtis", "Cheney")


def _add(terms, pid, name, office, group, start, end, year, sources, notes, party="", how="elected", conf="high", **extra):
    rec = T(
        person_id=pid, name=name, office=office, office_group=group,
        term_start=start, term_end=end, election_year=year, sources=sources,
        notes=notes, party=party, how_took_office=how, confidence=conf, **extra,
    )
    terms.append(rec)
    return rec


def legislature_terms():
    """Official SOS district-wide Totals, with the official Hot Springs share noted.
    Official totals already keyed in the Washakie, Fremont, and Big Horn histories are reused.
    Official SOS name Nathan Winters is not combined with official SOS name John R. Winter.
    """
    terms = []
    def leg(pid, name, office, start, end, year, chamber, notes, party="Republican"):
        _add(terms, pid, name, office, "state-senate" if "Senate" in office else "state-house",
             start, end, year, [sos_src(year, chamber)], notes, party=party)

    # S20 (Hot Springs, Washakie, Big Horn, Park, Fremont)
    leg("WY-GEIS-GERALD-E", "Gerald E. Geis", "Senate District 20 (S20)",
        "2013-01-07", "2017-01-02", 2012, "Senate",
        "Official 2012 SOS statewide Senate summary, Senate District 20: Gerald E. Geis (R) Total 7,592. Official Hot Springs share 2,164; official Washakie 3,456, Big Horn 1,245, Fremont 317, Park 410.")
    leg("WY-AGAR-WYATT", "Wyatt Agar", "Senate District 20 (S20)",
        "2017-01-02", "2021-01-04", 2016, "Senate",
        "Official 2016 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18; not the District 18 Total): Wyatt Agar (R) Total 6,893, Mary Jane Norskog (D) 1,546. Official Hot Springs share Agar 1,817, Norskog 714 (official 2016 SOS Hot Springs County PbP Total).")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)",
        "2021-01-04", "2025-01-06", 2020, "Senate",
        "Official 2020 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18): Ed Cooper (R) Total 7,497, Theresa Livingston (D) 1,293. Official Hot Springs share Cooper 2,031, Livingston 472.")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)",
        "2025-01-06", "2029-01-01", 2024, "Senate",
        "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Hot Springs share 2,180 (official 2024 clerk canvass same 2,180); official Washakie 3,442, Big Horn 1,475, Park 834, Fremont 305. Also covers Washakie, Big Horn, Fremont, and Park. Off-cycle in 2026.")

    # H28
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 28: Nathan Winters (R) Total 3,288, Connie Skates (D) 1,100. Official Hot Springs share Winters 1,689, Skates 769.")
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 28: Nathan Winters (R) Total 2,989. Official Hot Springs share 1,615.")
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)",
        "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): Nathan Winters (R) Total 3,510, Howard Samelson (D) 980. Official Hot Springs share Winters 1,791, Samelson 760 (official 2016 SOS Hot Springs County PbP Total).")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 28: John R. Winter (R) Total 2,906, Howie Samelson (D) 954. Official Hot Springs share Winter 1,471, Samelson 743. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): John R. Winter (R) Total 3,769, Levi J. Shinkle (D) 816. Official Hot Springs share Winter 1,902, Shinkle 595 (official 2020 SOS Hot Springs County PbP Total).")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,139, Kimberly M. Bartlett (D) 855. Official Hot Springs share Winter 1,582, Bartlett 590.")
    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)",
        "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Hot Springs share Winter 1,979, Alwin 574 (official 2024 clerk canvass same 1,979-574).")
    leg("WY-HOGG-ALLEN", "Allen Hogg", "House District 28 (H28)",
        "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 28: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504. Official Hot Springs share Hogg 1,725, Alwin 343 (official clerk canvass same 1,725-343). Takes office January 2027.")
    return terms


def county_terms():
    terms = []
    _add(terms, "WY-GALOVICH-PAUL-M", "Paul M. Galovich", "County Commissioner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM, SRC_2022],
         "Official commissioners page, retrieved 2026-11-24: Paul Galovich. Official 2022 canvass, County Commissioner (vote for 2): REP PAUL M. GALOVICH 1,517, REP THOMAS J. RYAN 1,407, contest totals 4,426.",
         party="Republican")
    _add(terms, "WY-RYAN-THOMAS-J", "Thomas J. Ryan", "County Commissioner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM, SRC_2022],
         "Official commissioners page, retrieved 2026-11-24: Tom Ryan. Official 2022 canvass, County Commissioner (vote for 2): REP THOMAS J. RYAN 1,407, REP PAUL M. GALOVICH 1,517.",
         party="Republican")
    _add(terms, "WY-AGUIAR-BOB", "Bob Aguiar", "County Commissioner", "county",
         "2025-01-06", "2029-01-01", 2024, [SRC_COMM, SRC_2024],
         "Official commissioners page, retrieved 2026-11-24: Chairman Bob Aguiar. Official 2024 canvass, County Commissioner (vote for 1): REP BOB AGUIAR 1,306, IND JACK T. BAIRD 1,201, write-ins 24, total votes cast 2,531.",
         party="Republican")
    _add(terms, "WY-AXTELL-CHIP", "Chip Axtell", "County Commissioner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_2026_FILING],
         "Official 2026 canvass, County Commissioner (vote for 2): REP CHIP AXTELL 1,774, REP PHILLIP SCHEEL 1,285, write-ins 144, contest totals 4,310. Takes office January 2027. Official 2024 canvass also elected Chip Axtell as Conservation District Rural Supervisor; both official offices are recorded.",
         party="Republican")
    _add(terms, "WY-SCHEEL-PHILLIP", "Phillip Scheel", "County Commissioner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_2026_FILING],
         "Official 2026 canvass, County Commissioner (vote for 2): REP PHILLIP SCHEEL 1,285, REP CHIP AXTELL 1,774. Takes office January 2027.",
         party="Republican")

    def reelect(pid, name, office, src, note):
        _add(terms, pid, name, office, "county", "2023-01-02", "2027-01-04", 2022, src, note, party="Republican")
        _add(terms, pid, name, office, "county", "2027-01-04", "2031-01-06", 2026, [SRC_2026],
             note + " Official 2026 general: re-elected.", party="Republican")

    reelect("WY-KERSTEN-BECKY", "Becky Kersten", "County Clerk", [SRC_CLERK, SRC_2022],
            "Official clerk page, retrieved 2026-11-24: Becky Kersten. Official 2022 canvass: REP BECKY KERSTEN 2,008. Official 2026 canvass: REP BECKY KERSTEN 1,916.")
    _add(terms, "WY-MORTIMORE-JULIE", "Julie Mortimore", "County Treasurer", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_TREAS, SRC_2022],
         "Official treasurer page, retrieved 2026-11-24: Julie Mortimore. Official 2022 canvass: REP JULIE MORTIMORE 2,019. Official 2026 general elects Stacia Noorda.",
         party="Republican")
    _add(terms, "WY-NOORDA-STACIA", "Stacia Noorda", "County Treasurer", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026, SRC_2026_FILING],
         "Official 2026 canvass, County Treasurer: REP STACIA NOORDA 1,864, write-ins 26, contest totals 2,155. Takes office January 2027.",
         party="Republican")
    reelect("WY-WEBBER-DANIEL", "Daniel Webber", "County Assessor", [SRC_ASSESSOR, SRC_2022],
            "Official assessor page, retrieved 2026-11-24: Daniel Webber. Official 2022 canvass: REP DANIEL WEBBER 1,944. Official 2026 canvass: REP DANIEL WEBBER 1,832.")
    reelect("WY-KRAUSHAAR-JERIMIE", "Jerimie Kraushaar", "County Sheriff", [SRC_SHERIFF, SRC_2022],
            "Official sheriff page, retrieved 2026-11-24: Sheriff Jerimie Kraushaar. Official 2022 canvass: REP JERIMIE KRAUSHAAR 1,920. Official 2026 canvass: REP JERIMIE KRAUSHAAR 1,276, IND MATT WHEELER 793.")
    reelect("WY-LOGAN-JILL", "Jill Logan", "County Attorney", [SRC_ATTORNEY, SRC_2022],
            "Official attorney page, retrieved 2026-11-24: Jill Logan. Official 2022 canvass: REP JILL LOGAN 1,854. Official 2026 canvass: REP JILL LOGAN 1,723.")
    _add(terms, "WY-CORNELLA-TERRI", "Terri Cornella", "Clerk of District Court", "county",
         "2023-01-02", "2025-01-06", 2022, [SRC_2022],
         "Official 2022 canvass, Clerk of District Court: REP TERRI CORNELLA 1,952. Official 2024 canvass elected Kris McNeff (the official clerk-of-court page names Kris McNeff as the current holder).",
         party="Republican")
    _add(terms, "WY-MCNEFF-KRIS", "Kris McNeff", "Clerk of District Court", "county",
         "2025-01-06", "2027-01-04", 2024, [SRC_CDC, SRC_2024],
         "Official clerk-of-court page, retrieved 2026-11-24: Kris McNeff. Official 2024 canvass: REP KRIS MCNEFF 2,232, write-ins 31, total votes cast 2,263 (a mid-cycle contest after the official 2022 winner Terri Cornella).",
         party="Republican")
    _add(terms, "WY-MCNEFF-KRIS", "Kris McNeff", "Clerk of District Court", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026],
         "Official 2026 canvass, Clerk of District Court: REP KRIS MCNEFF 1,850, write-ins 14, contest totals 2,155.",
         party="Republican")
    reelect("WY-MORTIMORE-MARK", "Mark Mortimore", "County Coroner", [SRC_2022],
            "Official 2022 canvass: REP MARK MORTIMORE 1,929. Official 2026 canvass: REP MARK MORTIMORE 1,850. Official 2026 candidate roster also names Mark Mortimore, County Coroner (the official coroner department path returns 404).")
    return terms


def judicial_terms():
    terms = []
    _add(terms, "WY-OVERFIELD-BOBBI", "Bobbi Overfield",
         "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2021-01-04", "2027-01-04", 2020, [SRC_COURT],
         "Official March 2026 judicial roster title already used in the official Park, Washakie, and Big Horn histories.")
    _add(terms, "WY-OVERFIELD-BOBBI", "Bobbi Overfield",
         "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2027-01-04", "2033-01-03", 2026, [SRC_2026, SRC_COURT],
         "Official 2026 Hot Springs canvass, DC OVERFIELD: YES 1,654, NO 261. Retained, continuing January 2027.")
    _add(terms, "WY-LUHM-ED", "Ed Luhm",
         "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", "judicial",
         "2025-01-06", "2031-01-06", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Hot Springs canvass, CC JUDGE LUHM: YES 1,772, NO 434. Official roster name Ed Luhm (Edward G. Luhm).")
    _add(terms, "WY-SIMPSON-BILL", "Bill Simpson",
         "District Judge, 5th Judicial District (Park)", "judicial",
         "2025-01-06", "2031-01-06", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Hot Springs canvass, DC JUDGE SIMPSON: YES 1,844, NO 397. Official March 2026 roster names Bill Simpson (Park district judge).")
    _add(terms, "WY-DARRAH-JOEY", "Joey Darrah",
         "Circuit Judge, 5th Judicial District (Park)", "judicial",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024, SRC_COURT],
         "Official 2024 Hot Springs canvass, CC JUDGE DARRAH: YES 1,768, NO 403. Official roster name Joey Darrah (Park circuit).")
    return terms


def municipal_terms():
    terms = []
    def cur(pid, name, office, year, start, end, sources, notes):
        _add(terms, pid, name, office, "municipal", start, end, year, sources, notes)

    # Thermopolis
    cur("WY-ESTENSON-ADAM-R", "Adam R. Estenson", "Thermopolis Mayor", 2022, "2023-01-02", "2027-01-04",
        [SRC_THERM, SRC_2022],
        "Official Town of Thermopolis Mayor and Town Council page, retrieved 2026-11-24: Mayor Adam R. Estenson. Official 2022 canvass, Mayor Thermopolis: ADAM RYAN ESTENSON 650, MIKE CHIMENTI 552.")
    cur("WY-ESTENSON-ADAM-R", "Adam R. Estenson", "Thermopolis Mayor", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026, SRC_THERM],
        "Official 2026 canvass, Thermopolis Mayor: ADAM RYAN ESTENSON 574, RACHEL HUGHES 537, write-ins 9, contest totals 1,152. Re-elected.")
    cur("WY-DORMAN-JOHN-SR", "John Dorman Sr.", "Thermopolis Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_THERM, SRC_2022],
        "Official town page: Council Member John Dorman Sr. Official 2022 canvass, Councilperson Thermopolis (vote for 2): JOHN DORMAN SR. 748, RACHEL HUGHES 612, TONY LARSON 598, BRADYN HARVEY 145.")
    cur("WY-HUGHES-RACHEL", "Rachel Hughes", "Thermopolis Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_THERM, SRC_2022],
        "Official town page: Council Member Rachel Hughes. Official 2022 canvass: RACHEL HUGHES 612. Official 2026 canvass: she ran for mayor and finished second.")
    cur("WY-LARSON-TONY", "Tony Larson", "Thermopolis Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_THERM, SRC_2024],
        "Official town page: Council Member Tony Larson. Official 2024 canvass, Thermopolis Town Council (vote for 2): TONY LARSON 858, DUSTY LEWIS 814, WILLIAM H. MALLOY 547.")
    cur("WY-LEWIS-DUSTY", "Dusty Lewis", "Thermopolis Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_THERM, SRC_2024],
        "Official town page: Council Member Dusty Lewis. Official 2024 canvass: DUSTY LEWIS 814, TONY LARSON 858.")
    cur("WY-DORMAN-JOHN-SR", "John Dorman Sr.", "Thermopolis Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, Thermopolis Council (vote for 2): JOHN D. DORMAN 719, LEVI SHINKLE 451, JOSHUA THOREN 427, BOB VAN MAARTH 240, contest totals 2,304. Re-elected.")
    cur("WY-SHINKLE-LEVI", "Levi Shinkle", "Thermopolis Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, Thermopolis Council (vote for 2): LEVI SHINKLE 451, JOHN D. DORMAN 719. Takes office January 2027.")

    # East Thermopolis
    cur("WY-HOLBERT-GARY-J", "Gary J. Holbert", "East Thermopolis Mayor", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Mayor East Thermopolis: certified write-in Gary Holbert 40, JACK KUIPER 27, JEREMIAH RAMSEY 26. The official canvass names the write-in winner.")
    cur("WY-HOLBERT-GARY-J", "Gary J. Holbert", "East Thermopolis Mayor", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, East Thermopolis Mayor: GARY J HOLBERT 64, write-ins 2, contest totals 88. Re-elected.")
    cur("WY-BUSH-DOLORES", "Dolores Bush", "East Thermopolis Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Councilperson East Thermopolis (vote for 2): DOLORES BUSH 64, DEBRA K. LACKEY 55, JULIE DODDS MUSIC 39.")
    cur("WY-LACKEY-DEBRA-K", "Debra K. Lackey", "East Thermopolis Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Councilperson East Thermopolis (vote for 2): DEBRA K. LACKEY 55, DOLORES BUSH 64.")
    cur("WY-MCDONALD-SID", "Sid McDonald", "East Thermopolis Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_2024],
        "Official 2024 canvass, East Thermopolis Council (vote for 2): SID MCDONALD 79, JULIE DODDS MUSIC 75.")
    cur("WY-MUSIC-JULIE-DODDS", "Julie Dodds Music", "East Thermopolis Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_2024],
        "Official 2024 canvass, East Thermopolis Council (vote for 2): JULIE DODDS MUSIC 75, SID MCDONALD 79.")
    cur("WY-JOHNSTON-COREY", "Corey Johnston", "East Thermopolis Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, East Thermopolis Council (vote for 2): COREY JOHNSTON 51, GEORGEANNE HAMMOND 45, STEVE THOMAS 38, contest totals 176. Takes office January 2027.")
    cur("WY-HAMMOND-GEORGEANNE", "Georgeanne Hammond", "East Thermopolis Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, East Thermopolis Council (vote for 2): GEORGEANNE HAMMOND 45, COREY JOHNSTON 51.")

    # Kirby
    cur("WY-SLAGLE-JESSICA", "Jessica Slagle", "Kirby Mayor", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Mayor Kirby: JESSICA SLAGLE 21, write-ins 2, contest totals 31.")
    cur("WY-SLAGLE-JESSICA", "Jessica Slagle", "Kirby Mayor", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, Kirby Mayor: JESSICA SLAGLE 26, write-ins 11, contest totals 38. Re-elected.")
    cur("WY-RODRIGUEZ-NATHANIEL", "Nathaniel Rodriguez", "Kirby Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Councilperson Kirby (vote for 2): NATHANIEL RODRIGUEZ 21, KIMBERLY GRAHAM 19, BARRIE LYNN BRYANT JR. 12.")
    cur("WY-GRAHAM-KIMBERLY", "Kimberly Graham", "Kirby Town Council", 2022, "2023-01-02", "2027-01-04",
        [SRC_2022],
        "Official 2022 canvass, Councilperson Kirby (vote for 2): KIMBERLY GRAHAM 19, NATHANIEL RODRIGUEZ 21.")
    cur("WY-CREES-ZACHARY", "Zachary Crees", "Kirby Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_2024],
        "Official 2024 canvass, Kirby Council 4-year (vote for 2): ZACHARY CREES 26, TINA L. KEASLING 24.")
    cur("WY-KEASLING-TINA-L", "Tina L. Keasling", "Kirby Town Council", 2024, "2025-01-06", "2029-01-01",
        [SRC_2024],
        "Official 2024 canvass, Kirby Council 4-year (vote for 2): TINA L. KEASLING 24, ZACHARY CREES 26.")
    cur("WY-ELLEDGE-CYNTHIA", "Cynthia Elledge", "Kirby Town Council (2-year)", 2024, "2025-01-06", "2027-01-04",
        [SRC_2024],
        "Official 2024 canvass, Kirby Council 2-year: CYNTHIA ELLEDGE 28, write-ins 11, total votes cast 39. Official 2026 canvass elects Cynthia Elledge to a regular council seat.")
    cur("WY-ELLEDGE-CYNTHIA", "Cynthia Elledge", "Kirby Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, Kirby Council (vote for 2): CYNTHIA ELLEDGE 24, CAROL SLAGLE 21, EMMA LEA 17, contest totals 76.")
    cur("WY-SLAGLE-CAROL", "Carol Slagle", "Kirby Town Council", 2026, "2027-01-04", "2031-01-06",
        [SRC_2026],
        "Official 2026 canvass, Kirby Council (vote for 2): CAROL SLAGLE 21, CYNTHIA ELLEDGE 24. Takes office January 2027.")
    return terms


def school_terms():
    terms = []
    def sch(pid, name, year, start, end, sources, notes, office="Hot Springs County School District #1 Trustee"):
        _add(terms, pid, name, office, "schools", start, end, year, sources, notes)

    sch("WY-SKELTON-SHERMAN", "Sherman Skelton", 2022, "2023-01-02", "2027-01-04", [SRC_2022, SRC_HS1],
        "Official HSCSD #1 Board of Trustees page, retrieved 2026-11-24: Sherman Skelton, term expires 12/2026. Official 2022 canvass, HSCSD #1 Trustees (vote for 3): SHERMAN SKELTON 1,054, JENNIFER AXTELL 1,031, BETHANY ROSE WEBBER 921.")
    sch("WY-AXTELL-JENNIFER", "Jennifer Axtell", 2022, "2023-01-02", "2027-01-04", [SRC_2022, SRC_HS1],
        "Official board page: Jennifer Axtell, Board Chairman, term expires 12/2026. Official 2022 canvass: JENNIFER AXTELL 1,031. Official 2026 canvass elects Jennifer Axtell to the official 2-year unexpired trustee seat.")
    sch("WY-WEBBER-BETHANY", "Bethany Webber", 2022, "2023-01-02", "2027-01-04", [SRC_2022, SRC_HS1],
        "Official board page: Bethany Webber, term expires 12/2026. Official 2022 canvass: BETHANY ROSE WEBBER 921.")
    sch("WY-JOHNSON-CHAUNCY", "Chauncy Johnson", 2022, "2023-01-02", "2027-01-04", [SRC_HS1],
        "Official HSCSD #1 Board of Trustees page, retrieved 2026-11-24: Chauncy Johnson, Board Treasurer, term expires 12/2026. The official December expiration is mapped to January 2027. He was not a named top-three winner on the official 2022 at-large canvass; the official current board page is used for the current holder.")
    sch("WY-KELLER-MARSHALL", "Marshall Keller", 2024, "2025-01-06", "2029-01-01", [SRC_2024, SRC_HS1],
        "Official board page: Marshall Keller, Board Vice-Chairman, term expires 12/2028. Official 2024 canvass, HSCSD #1 (vote for 4): JUSTIN BUDD 1,368, JEAN SKELTON 1,256, MARSHALL KELLER 1,116, NICHOLE WEYER 998 (BETH LEWIS 974 finished fifth).")
    sch("WY-SKELTON-JEAN", "Jean Skelton", 2024, "2025-01-06", "2029-01-01", [SRC_2024, SRC_HS1],
        "Official board page: Jean Skelton, term expires 12/2028. Official 2024 canvass: JEAN SKELTON 1,256.")
    sch("WY-WEYER-NICHOLE", "Nichole Weyer", 2024, "2025-01-06", "2029-01-01", [SRC_2024, SRC_HS1],
        "Official board page: Nichole Weyer, Board Clerk, term expires 12/2028. Official 2024 canvass: NICHOLE WEYER 998.")
    sch("WY-WEBBER-BETHANY", "Bethany Webber", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, HSCSD #1 Trustee 4-year (vote for 3): BETHANY WEBBER 1,245, SHERMAN SKELTON 1,125, STEPHANIE BOREN 1,056, CINDY GLASSON 792, SEAN RYAN 739, contest totals 6,455. Re-elected.")
    sch("WY-SKELTON-SHERMAN", "Sherman Skelton", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, HSCSD #1 Trustee 4-year (vote for 3): SHERMAN SKELTON 1,125, BETHANY WEBBER 1,245, STEPHANIE BOREN 1,056. Re-elected.")
    sch("WY-BOREN-STEPHANIE", "Stephanie Boren", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
        "Official 2026 canvass, HSCSD #1 Trustee 4-year (vote for 3): STEPHANIE BOREN 1,056. Takes office January 2027.")
    sch("WY-AXTELL-JENNIFER", "Jennifer Axtell", 2026, "2027-01-04", "2029-01-01", [SRC_2026, SRC_2026_PROC],
        "Official 2026 canvass, HSCSD #1 Trustee 2-year: JENNIFER AXTELL 1,213, ANDREA MILLER 748, contest totals 2,155. Official amended proclamation described this seat as a 2-year unexpired term.",
        office="Hot Springs County School District #1 Trustee (2-year)")
    return terms


def special_terms():
    terms = []
    def sp(pid, name, office, year, start, end, sources, notes):
        _add(terms, pid, name, office, "special-districts", start, end, year, sources, notes)

    # Conservation
    sp("WY-WILSON-JIM", "Jim Wilson", "Hot Springs Conservation District Rural Supervisor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass, Conservation Dist Rural Supervisor (vote for 2): JIM WILSON 1,828. The official canvass also certifies write-in Chip Axtell as elected to this rural board.")
    sp("WY-WARD-PAUL", "Paul Ward", "Hot Springs Conservation District At-Large Supervisor", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass certified write-in: Paul Ward has been elected Hot Springs Conservation Dist At-Large Supervisor.")
    sp("WY-AXTELL-CHIP", "Chip Axtell", "Hot Springs Conservation District Rural Supervisor", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Conservation Dist Rural (vote for 1): CHIP AXTELL 2,213, write-ins 19, total votes cast 2,232. Official 2022 canvass also certified write-in Chip Axtell as elected Rural Supervisor; the official 2024 term (through January 2029) is used for the current holder.")
    sp("WY-NORSWORTHY-JASON", "Jason Norsworthy", "Hot Springs Conservation District Rural Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Conservation Dist Rural (vote for 2): JASON NORSWORTHY 1,407, WESTON JONES 1,392, contest totals 4,310. Takes office January 2027.")
    sp("WY-JONES-WESTON", "Weston Jones", "Hot Springs Conservation District Rural Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Conservation Dist Rural (vote for 2): WESTON JONES 1,392, JASON NORSWORTHY 1,407.")
    sp("WY-SAYERS-DANITA", "Danita Sayers", "Hot Springs Conservation District At-Large Supervisor", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Conservation Dist At Large: DANITA SAYERS 1,563, write-ins 11, contest totals 2,155. Takes office January 2027.")

    # Cemetery
    sp("WY-SORENSEN-BASIL", "Basil Sorensen", "Hot Springs County Cemetery District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass, Cemetery Dist Director (vote for 3): BASIL SORENSEN 1,604, MERRILL J. READY 1,396, STAN KRAUSHAAR 1,393.")
    sp("WY-READY-MERRILL-J", "Merrill J. Ready", "Hot Springs County Cemetery District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass: MERRILL J. READY 1,396. Official 2026 canvass certifies Merrill Ready as a write-in winner of a new term.")
    sp("WY-KRAUSHAAR-STAN", "Stan Kraushaar", "Hot Springs County Cemetery District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass: STAN KRAUSHAAR 1,393.")
    sp("WY-DEVRIES-CINDY", "Cindy DeVries", "Hot Springs County Cemetery District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Cemetery (vote for 3): CINDY DEVRIES 1,607, MARGARET STANSILL 1,575, BARBARA TOMES VIETTI 1,558.")
    sp("WY-STANSILL-MARGARET", "Margaret Stansill", "Hot Springs County Cemetery District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: MARGARET STANSILL 1,575.")
    sp("WY-VIETTI-BARBARA-TOMES", "Barbara Tomes Vietti", "Hot Springs County Cemetery District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: BARBARA TOMES VIETTI 1,558.")
    sp("WY-SORENSEN-BASIL", "Basil Sorensen", "Hot Springs County Cemetery District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Cemetery (vote for 3): BASIL SORENSEN 1,817, write-ins 108, contest totals 6,465. Re-elected.")
    sp("WY-READY-MERRILL-J", "Merrill J. Ready", "Hot Springs County Cemetery District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, county-wide certified write-in (initialed and dated 11/5/26 on the official summary): Merrill Ready 23. Official canvassing-board certification of the named write-in is used.")
    sp("WY-JACKSON-MARSHALL", "Marshall Jackson", "Hot Springs County Cemetery District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, county-wide certified write-in (initialed and dated 11/5/26 on the official summary): Marshall Jackson 9.")
    sp("WY-MORTIMORE-MIKE", "Mike Mortimore", "Hot Springs County Cemetery District Director (2-year)", 2026, "2027-01-04", "2029-01-01", [SRC_2026],
       "Official 2026 canvass, Cemetery 2-year was write-in only (154 write-ins). The official summary certifies write-in Mike Mortimore 5 (initialed and dated 11/5/26). Takes office January 2027.")

    # Fire
    sp("WY-OBRIEN-KEITH", "Keith O'Brien", "Hot Springs Rural Fire Protection District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass, Rural Fire Prot Dist Director (vote for 2): KEITH O'BRIEN 593, JAMES BYRD 584, contest totals 1,696.")
    sp("WY-BYRD-JAMES", "James Byrd", "Hot Springs Rural Fire Protection District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass: JAMES BYRD 584. Official 2026 winner Michael Byrd is not combined with this official 2022 name.")
    sp("WY-HUCKFELDT-CLINT", "Clint Huckfeldt", "Hot Springs Rural Fire Protection District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Fire Dist Hot Springs (vote for 1): CLINT HUCKFELDT 764, write-ins 3, total votes cast 767.")
    sp("WY-OBRIEN-KEITH", "Keith O'Brien", "Hot Springs Rural Fire Protection District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Rural Fire (vote for 2): KEITH O'BRIEN 629, MICHAEL BYRD 613, contest totals 1,754. Re-elected.")
    sp("WY-BYRD-MICHAEL", "Michael Byrd", "Hot Springs Rural Fire Protection District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Rural Fire (vote for 2): MICHAEL BYRD 613, KEITH O'BRIEN 629. Not combined with official 2022 name James Byrd.")

    # Hospital
    sp("WY-JOHNSON-MELISSA-MCCUMBER", "Melissa McCumber Johnson", "Hot Springs Hospital District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass, Hospital Dist Director 4-year (vote for 3): MELISSA MCCUMBER JOHNSON 1,589, AIMEE KAY 1,564, JESSICA BENEFIEL 1,418.")
    sp("WY-KAY-AIMEE", "Aimee Kay", "Hot Springs Hospital District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass: AIMEE KAY 1,564. Official 2026 canvass re-elects Aimee Kay.")
    sp("WY-BENEFIEL-JESSICA", "Jessica Benefiel", "Hot Springs Hospital District Director", 2022, "2023-01-02", "2027-01-04", [SRC_2022],
       "Official 2022 canvass: JESSICA BENEFIEL 1,418.")
    sp("WY-ANDERSON-JOHN", "John Anderson", "Hot Springs Hospital District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Hospital (vote for 2): JOHN ANDERSON 1,662, JOHN V FENTON 1,288.")
    sp("WY-FENTON-JOHN-V", "John V. Fenton", "Hot Springs Hospital District Director", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: JOHN V FENTON 1,288.")
    sp("WY-KAY-AIMEE", "Aimee Kay", "Hot Springs Hospital District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hospital Dist (vote for 3): AIMEE KAY 1,304, BRENNA HUCKFELDT 1,075, TROY DANIELS 945, JENNIFER CHENEY 879, ROBIN MARIE VAN MAARTH 438, contest totals 6,465. Re-elected.")
    sp("WY-HUCKFELDT-BRENNA", "Brenna Huckfeldt", "Hot Springs Hospital District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hospital Dist (vote for 3): BRENNA HUCKFELDT 1,075.")
    sp("WY-DANIELS-TROY", "Troy Daniels", "Hot Springs Hospital District Director", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Hospital Dist (vote for 3): TROY DANIELS 945. Takes office January 2027.")

    # Senior
    sp("WY-SHAFFER-RAYMOND-E", "Raymond E. Shaffer", "Hot Springs Senior Citizen District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass, Senior Citizen District (vote for 5): RAYMOND E. SHAFFER 1,534, KATHY SORENSEN 1,300, MARVIN NIELSEN 1,260, KIMBERLY JOY BLACK 992, CURTIS CHENEY 801 (TED BROWN 724 and GARY J. HOLBERT 707 finished sixth and seventh), total votes cast 7,929.")
    sp("WY-SORENSEN-KATHY", "Kathy Sorensen", "Hot Springs Senior Citizen District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: KATHY SORENSEN 1,300. Official 2026 canvass re-elects Kathy Sorensen.")
    sp("WY-NIELSEN-MARVIN", "Marvin Nielsen", "Hot Springs Senior Citizen District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: MARVIN NIELSEN 1,260. Official 2026 canvass re-elects Marvin Nielsen.")
    sp("WY-BLACK-KIMBERLY-JOY", "Kimberly Joy Black", "Hot Springs Senior Citizen District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: KIMBERLY JOY BLACK 992.")
    sp("WY-CHENEY-CURTIS", "Curtis Cheney", "Hot Springs Senior Citizen District Trustee", 2024, "2025-01-06", "2029-01-01", [SRC_2024],
       "Official 2024 canvass: CURTIS CHENEY 801. Official 2026 canvass re-elects Curtis Cheney.")
    sp("WY-SORENSEN-KATHY", "Kathy Sorensen", "Hot Springs Senior Citizen District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Senior Citizen Dist (vote for 3): KATHY SORENSEN 1,551, MARVIN NIELSEN 1,412, CURTIS CHENEY 1,300, contest totals 6,465. Re-elected.")
    sp("WY-NIELSEN-MARVIN", "Marvin Nielsen", "Hot Springs Senior Citizen District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Senior Citizen Dist (vote for 3): MARVIN NIELSEN 1,412.")
    sp("WY-CHENEY-CURTIS", "Curtis Cheney", "Hot Springs Senior Citizen District Trustee", 2026, "2027-01-04", "2031-01-06", [SRC_2026],
       "Official 2026 canvass, Senior Citizen Dist (vote for 3): CURTIS CHENEY 1,300.")
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 20 (S20)", 1)],
        "state-house": [("House District 28 (H28)", 1)],
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
            ("Thermopolis Mayor", 1), ("Thermopolis Town Council", 4),
            ("East Thermopolis Mayor", 1), ("East Thermopolis Town Council", 4),
            ("Kirby Mayor", 1), ("Kirby Town Council", 4), ("Kirby Town Council (2-year)", 1),
        ],
        "schools": [
            ("Hot Springs County School District #1 Trustee", 7),
            ("Hot Springs County School District #1 Trustee (2-year)", 1),
        ],
        "special-districts": [
            ("Hot Springs Conservation District Rural Supervisor", 3),
            ("Hot Springs Conservation District At-Large Supervisor", 1),
            ("Hot Springs Conservation District Urban Supervisor", 1),
            ("Hot Springs County Cemetery District Director", 6),
            ("Hot Springs County Cemetery District Director (2-year)", 1),
            ("Hot Springs Rural Fire Protection District Director", 3),
            ("Hot Springs Hospital District Director", 5),
            ("Hot Springs Senior Citizen District Trustee", 5),
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




def build_hot_springs():
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
        "Fifth Judicial District and Circuit judges serving Hot Springs with Big Horn and Washakie (Bobbi Overfield, "
        "Ed Luhm / Edward G. Luhm) and the Park-seat judges (Bill Simpson, Joey Darrah), from official court roster "
        "titles already used in the official Park, Washakie, and Big Horn histories. Official 2026 Hot Springs canvass "
        "retention for Judge Bobbi Overfield is YES 1,654 / NO 261. Official 2026 CHC BURNINGHAM is the statewide "
        "Chancery Court retention already in the shared terms, not a Fifth Judicial District circuit office."
    )
    coverage = H.write_terms_and_snapshots(
        county="Hot Springs", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Hot Springs", slug=SLUG)
    print("copied shared terms", copied, "coverage", coverage)
    return people, terms, coverage


def update_hot_springs_json(people, terms):
    path = ROOT / "data" / "county_officials" / "hot-springs.json"
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
        "Senate District 20 (S20)":
            "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Hot Springs share 2,180 (official 2024 clerk canvass same 2,180); official Washakie 3,442, Big Horn 1,475, Park 834, Fremont 305. Also covers Washakie, Big Horn, Fremont, and Park. Off-cycle in 2026.",
        "House District 28 (H28)":
            "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Hot Springs share Winter 1,979, Alwin 574. Official 2026 SOS: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504; official Hot Springs share Hogg 1,725, Alwin 343, taking office January 2027. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters. Also covers Big Horn, Fremont, and Park.",
        "County Commissioner":
            "Official commissioners page, retrieved 2026-11-24: Chairman Bob Aguiar, Paul Galovich, and Tom Ryan. Official 2024 canvass elected Bob Aguiar (1,306) over Jack T. Baird (1,201). Official 2026 canvass (vote for 2): Chip Axtell 1,774, Phillip Scheel 1,285, taking office January 2027. Incoming names are shown with the 2022-class commissioners, not as one-to-one seat replacements.",
        "County Clerk":
            "Official clerk page, retrieved 2026-11-24: Becky Kersten. Official 2026 canvass: REP BECKY KERSTEN 1,916, re-elected.",
        "County Treasurer":
            "Official treasurer page, retrieved 2026-11-24: Julie Mortimore. Official 2026 canvass: REP STACIA NOORDA 1,864, taking office January 2027.",
        "County Assessor":
            "Official assessor page, retrieved 2026-11-24: Daniel Webber. Official 2026 canvass: REP DANIEL WEBBER 1,832, re-elected.",
        "County Sheriff":
            "Official sheriff page, retrieved 2026-11-24: Sheriff Jerimie Kraushaar. Official 2026 canvass: REP JERIMIE KRAUSHAAR 1,276, IND MATT WHEELER 793, re-elected.",
        "County Attorney":
            "Official attorney page, retrieved 2026-11-24: Jill Logan. Official 2026 canvass: REP JILL LOGAN 1,723, re-elected.",
        "Clerk of District Court":
            "Official clerk-of-court page, retrieved 2026-11-24: Kris McNeff. Official 2024 canvass: REP KRIS MCNEFF 2,232. Official 2026 canvass: REP KRIS MCNEFF 1,850, continuing January 2027.",
        "County Coroner":
            "Official 2022 and 2026 canvasses: REP MARK MORTIMORE (2026: 1,850), re-elected. The official coroner department path returns 404.",
        "Thermopolis Mayor":
            "Official Town of Thermopolis Mayor and Town Council page, retrieved 2026-11-24: Mayor Adam R. Estenson. Official 2026 canvass: ADAM RYAN ESTENSON 574, RACHEL HUGHES 537, re-elected.",
        "Hot Springs County School District #1 Trustee":
            "Official HSCSD #1 Board of Trustees page, retrieved 2026-11-24 (seven members). Official 2026 canvass 4-year (vote for 3): Bethany Webber 1,245, Sherman Skelton 1,125, Stephanie Boren 1,056. Official 2024 canvass named Justin Budd among the vote-for-4 winners; he is not listed on the official current board page and is not shown as a current holder.",
        "Hot Springs Conservation District Urban Supervisor":
            "Official 2024 canvass, Conservation Dist Urban (vote for 1) was write-in only (208 write-ins) with no certified named winner on the official summary, and is not filled.",
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
        "local_archive": "/workspace/wyoleg/local-results/hot-springs/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
