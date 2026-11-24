#!/usr/bin/env python3
"""Washakie County officeholder history (preview). Official clerk, SOS, court,
city, and town sources only. Names are never invented. Official 2022 clerk
general listed under Official Election Results is an election-night unofficial
scan (header UNOFFICIAL RESULTS) and is not used as a canvass.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
CN = 20
SLUG = "washakie"

URL_ELECTIONS = "https://www.washakiecountywy.gov/196/Elections"
URL_CLERK = "https://www.washakiecountywy.gov/195/Clerk"
URL_COMM = "https://www.washakiecountywy.gov/169/Commissioners"
URL_ASSESSOR = "https://www.washakiecountywy.gov/183/Assessor"
URL_ATTORNEY = "https://www.washakiecountywy.gov/193/Attorney"
URL_CDC = "https://www.washakiecountywy.gov/204/Clerk-of-District-Court"
URL_CORONER = "https://www.washakiecountywy.gov/205/Coroner"
URL_SHERIFF = "https://www.washakiecountywy.gov/225/Sheriff"
URL_TREASURER = "https://www.washakiecountywy.gov/226/Treasurer"
URL_C16 = "https://www.washakiecountywy.gov/DocumentCenter/View/308"
URL_C18 = "https://www.washakiecountywy.gov/DocumentCenter/View/311"
URL_C20 = "https://www.washakiecountywy.gov/DocumentCenter/View/312"
URL_C24 = "https://www.washakiecountywy.gov/DocumentCenter/View/309"
URL_C26 = "https://www.washakiecountywy.gov/DocumentCenter/View/633"
URL_C26P = "https://www.washakiecountywy.gov/DocumentCenter/View/634"
URL_P26 = "https://www.washakiecountywy.gov/DocumentCenter/View/605"
URL_WORLAND = "https://www.cityofworlandwy.gov/mayorandcouncil"
URL_WORLAND_FAQ = "https://www.cityofworlandwy.gov/electionfaqs"
URL_TS_JAN = "https://townoftensleep.com/download/january-6-2026-meeting-minutes/"
URL_TS_OCT = "https://townoftensleep.com/download/october-6-2026-meeting-minutes/?wpdmdl=1221"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-5th-judicial-district-washakie-county/"

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

SRC_C16 = S("Official Washakie County 2016 general (header OFFICIAL RESULTS, November 8, 2016, 3,865 ballots, 5 of 5 precincts)", URL_C16)
SRC_C18 = S("Official Washakie County 2018 general (header EL45 OFFICIAL RESULTS, November 6, 2018, run date 11/08/18 10:33 AM, 3,145 ballots, 5 of 5 precincts)", URL_C18)
SRC_C20 = S("Official Washakie County 2020 general (header OFFICIAL RESULTS, November 3, 2020, Election Summary 11/05/2020 10:10 AM, 4,082 ballots, 5 of 5 precincts)", URL_C20)
SRC_C24 = S("Official Washakie County 2024 general Precinct Summary (header OFFICIAL RESULTS, Precinct Summary - 11/07/2024 03:29PM, 21 pages, 5 official precincts). Countywide totals are the sum of official precinct rows.", URL_C24)
SRC_C26 = S("Official Washakie County 2026 general (header OFFICIAL RESULTS, WASHAKIE COUNTY GENERAL ELECTION November 3, 2026, Election Summary - 11/05/2026 02:40PM, 2,819 ballots). Official PDF is image-only; totals read from official rendered pages.", URL_C26)
SRC_C26P = S("Official Washakie County 2026 general precinct report (DocumentCenter View/634, 34 pages)", URL_C26P)
SRC_P26 = S("Official Washakie County 2026 primary official results (DocumentCenter View/605)", URL_P26)
SRC_COMM = S("Official Washakie County Commissioners page, retrieved 2026-11-24", URL_COMM)
SRC_CLERK = S("Official Washakie County Clerk page, retrieved 2026-11-24", URL_CLERK)
SRC_TREAS = S("Official Washakie County Treasurer page, retrieved 2026-11-24", URL_TREASURER)
SRC_ASSESSOR = S("Official Washakie County Assessor page, retrieved 2026-11-24 (contact block does not name a current assessor)", URL_ASSESSOR)
SRC_ATTORNEY = S("Official Washakie County Attorney page, retrieved 2026-11-24", URL_ATTORNEY)
SRC_CDC = S("Official Washakie County Clerk of District Court page, retrieved 2026-11-24", URL_CDC)
SRC_CORONER = S("Official Washakie County Coroner page, retrieved 2026-11-24", URL_CORONER)
SRC_SHERIFF = S("Official Washakie County Sheriff page, retrieved 2026-11-24", URL_SHERIFF)
SRC_WORLAND = S("Official City of Worland Mayor and Council page and official people API, retrieved 2026-11-24", URL_WORLAND)
SRC_WORLAND_FAQ = S("Official City of Worland Election FAQs (four-year terms; municipal races are on the November general)", URL_WORLAND_FAQ)
SRC_TS_JAN = S("Official Town of Ten Sleep council minutes, January 6, 2026", URL_TS_JAN)
SRC_TS_OCT = S("Official Town of Ten Sleep council minutes, October 6, 2026", URL_TS_OCT)
SRC_COURT = S("Official Wyoming Judicial Branch 5th Judicial District court pages and official March 2026 roster (same official sources already used in the Park history)", URL_COURT_D)
SRC_SOS12S, SRC_SOS12H = sos_src(2012, "Senate"), sos_src(2012, "House")
SRC_SOS14H = sos_src(2014, "House")
SRC_SOS16S, SRC_SOS16H = sos_src(2016, "Senate"), sos_src(2016, "House")
SRC_SOS18H = sos_src(2018, "House")
SRC_SOS20S, SRC_SOS20H = sos_src(2020, "Senate"), sos_src(2020, "House")
SRC_SOS22H = sos_src(2022, "House")
SRC_SOS24S, SRC_SOS24H = sos_src(2024, "Senate"), sos_src(2024, "House")
SRC_SOS26H = sos_src(2026, "House")

NOTE_2022 = (
    "The file listed as 2022 Official General Election Results on the official Elections page "
    "(DocumentCenter View/316) has header UNOFFICIAL RESULTS, created election night "
    "November 8, 2022, 7:55 PM, Precincts Partially Reported 0 of 5, and is not used as an official canvass."
)
NOTE_MUNI_JAN = (
    "Official City of Worland Election FAQs: four-year terms; municipal elections are on the November general. "
    "The official start day is not printed; January first-Monday after the election year is used (medium)."
)

def register_people(P):
    P("WY-GEIS-GERALD", "Gerald E. Geis", "Gerald", "Geis", middle="E.", aliases="Gerald Geis")
    P("WY-AGAR-WYATT", "Wyatt Agar", "Wyatt", "Agar")
    P("WY-COOPER-ED", "Ed Cooper", "Ed", "Cooper")
    P("WY-GREEAR-MICHAEL-D", "Michael D. Greear", "Michael", "Greear", middle="D.",
      aliases="Mike Greear; MIKE GREEAR; Michael Greear")
    P("WY-LAWLEY-MARTHA", "Martha Lawley", "Martha", "Lawley")
    P("WY-ANDERSON-AARON-J", "Aaron J. Anderson", "Aaron", "Anderson", middle="J.",
      aliases="Aaron Anderson; AARON ANDERSON")
    P("WY-FRANDSON-FRED-W", "Fred W. Frandson", "Fred", "Frandson", middle="W.",
      aliases="Fred Frandson; FRED WFRANDSON")
    P("WY-WOLF-TERRENCE-D", "Terrence D. Wolf", "Terrence", "Wolf", middle="D.",
      aliases="Terry Wolf; TERRENCE DWOLF; Terrence D Wolf")
    P("WY-MARTINEZ-MORGAN", "Morgan Martinez", "Morgan", "Martinez")
    P("WY-SCHMELTZER-TOM", "Tom Schmeltzer", "Tom", "Schmeltzer")
    P("WY-STRAUCH-MARY-GRACE", "Mary Grace Strauch", "Mary Grace", "Strauch")
    P("WY-PARRA-LILY-RAKNESS", "Lily Rakness Parra", "Lily", "Parra", aliases="Lily Rakness Parra")
    P("WY-KERN-DORIS", "Doris Kern", "Doris", "Kern")
    P("WY-TREANOR-KATHRYN", "Kathryn Treanor", "Kathryn", "Treanor")
    P("WY-SWALSTAD-BOBBY", "Bobby Swalstad", "Bobby", "Swalstad")
    P("WY-RAKNESS-STEVEN-R", "Steven R. Rakness", "Steven", "Rakness", middle="R.", aliases="Steven R Rakness")
    P("WY-BROOKWELL-AUSTIN-T", "Austin T. Brookwell", "Austin", "Brookwell", middle="T.",
      aliases="Austin Brookwell")
    P("WY-WORRALL-JOHN-P", "John P. Worrall", "John", "Worrall", middle="P.", aliases="John P Worrall")
    P("WY-BARTON-ANTHONY-J", "Anthony J. Barton", "Anthony", "Barton", middle="J.",
      aliases="Anthony Barton")
    P("WY-WHITLOCK-SUZANN", "Suzann Whitlock", "Suzann", "Whitlock")
    P("WY-HANSEN-MIRIAN", "Mirian Hansen", "Mirian", "Hansen")
    P("WY-LAPP-JEFFREY-D", "Jeffrey D. Lapp", "Jeffrey", "Lapp", middle="D.",
      aliases="Jeff Lapp; JEFF LAPP; Jeffrey Lapp")
    P("WY-SKAR-ROBERT-E", "Robert E. Skar", "Robert", "Skar", middle="E.")
    P("WY-WATERS-BRUCE-B", "Bruce B. Waters", "Bruce", "Waters", middle="B.")
    P("WY-OVERFIELD-BOBBI", "Bobbi Overfield", "Bobbi", "Overfield")
    P("WY-LUHM-ED", "Ed Luhm", "Ed", "Luhm", aliases="Edward G. Luhm; EDWARD G. LUHM")
    P("WY-SIMPSON-BILL", "Bill Simpson", "Bill", "Simpson")
    P("WY-DARRAH-JOEY", "Joey Darrah", "Joey", "Darrah", aliases="S. Joseph Joey Darrah; S. JOSEPH JOEY DARRAH")
    P("WY-GILL-JIM", "Jim Gill", "Jim", "Gill")
    P("WY-MCDONALD-KEITH-A", "Keith A. McDonald", "Keith", "McDonald", middle="A.")
    P("WY-GEORGE-REBECCA", "Rebecca George", "Rebecca", "George")
    P("WY-FERNANDEZ-LISA", "Lisa Fernandez", "Lisa", "Fernandez")
    P("WY-GENTZLER-KEITH-A", "Keith A. Gentzler", "Keith", "Gentzler", middle="A.")
    P("WY-ERNEST-JACQUELYN", "Jacquelyn Ernest", "Jacquelyn", "Ernest")
    P("WY-GERBER-GARY-W", "Gary W. Gerber", "Gary", "Gerber", middle="W.", aliases="Gary WGERBER")
    P("WY-RENNER-DELAYNE-M", "Delayne M. Renner", "Delayne", "Renner", middle="M.")
    P("WY-MARTINEZ-ADAM-G", "Adam G. Martinez", "Adam", "Martinez", middle="G.",
      aliases="Adam Martinez")
    P("WY-SCHAEFFER-SCOTT", "Scott Schaeffer", "Scott", "Schaeffer")
    P("WY-BROOKWELL-BARBARA", "Barbara Brookwell", "Barbara", "Brookwell")
    P("WY-GLANZ-BILL", "Bill Glanz", "Bill", "Glanz")
    P("WY-KOCH-DENNIS-A", "Dennis A. Koch", "Dennis", "Koch", middle="A.")
    P("WY-HORATH-MANDY", "Mandy Horath", "Mandy", "Horath")
    P("WY-SCHNEIDER-CHRISTY-R", "Christy R. Schneider", "Christy", "Schneider", middle="R.")
    P("WY-FREDRICKS-WENDY", "Wendy Fredricks", "Wendy", "Fredricks")
    P("WY-LEY-SHERYL", "Sheryl Ley", "Sheryl", "Ley")
    P("WY-BRINKERHOFF-LORESA", "Loresa Brinkerhoff", "Loresa", "Brinkerhoff")
    P("WY-NEUFER-MIKE", "Mike Neufer", "Mike", "Neufer")
    P("WY-LOMBARD-KREG", "Kreg Lombard", "Kreg", "Lombard")
    P("WY-RIVERA-MELISSA", "Melissa Rivera", "Melissa", "Rivera")
    P("WY-SANCHEZ-MICHAEL", "Michael Sanchez", "Michael", "Sanchez")
    P("WY-WORLEY-WILLIAM", "William Worley", "William", "Worley")
    P("WY-PIKE-JACQUELINE", "Jacqueline Pike", "Jacqueline", "Pike", aliases="Jacque Pike")
    P("WY-WALKER-DARR-LEA", "Darr Lea Walker", "Darr Lea", "Walker")
    P("WY-BECKLEY-ERNIE", "Ernie Beckley", "Ernie", "Beckley")
    P("WY-DEWITT-BART", "Bart DeWitt", "Bart", "DeWitt")
    P("WY-SWEENEY-CONNIE", "Connie Sweeney", "Connie", "Sweeney")
    P("WY-TRUMAN-AMY", "Amy Truman", "Amy", "Truman")
    P("WY-LYNEMA-NICHOLE", "Nichole Lynema", "Nichole", "Lynema", aliases="Councilwoman Lynema")
    P("WY-TOMMERUP-DAVID-R", "David R. Tommerup", "David", "Tommerup", middle="R.")
    P("WY-BISHOP-JOE", "Joe Bishop", "Joe", "Bishop")
    P("WY-DUPREE-DEAN", "Dean Dupree", "Dean", "Dupree")
    P("WY-BRYANT-DON", "Don Bryant", "Don", "Bryant")
    P("WY-LUNGREN-SARAH", "Sarah Lungren", "Sarah", "Lungren")
    P("WY-WHITLOCK-DUANE-S", "Duane S. Whitlock", "Duane", "Whitlock", middle="S.")
    P("WY-LOGAN-TERRI", "Terri Logan", "Terri", "Logan")
    P("WY-ARGERIS-BRETT", "Brett Argeris", "Brett", "Argeris")
    P("WY-HAKE-JONATHAN", "Jonathan Hake", "Jonathan", "Hake")
    P("WY-DOOLEY-BECKY", "Becky Dooley", "Becky", "Dooley")
    P("WY-MERCADO-KATHY", "Kathy Mercado", "Kathy", "Mercado")
    P("WY-MERTZ-JAIME", "Jaime Mertz", "Jaime", "Mertz")
    P("WY-LYMAN-JARED-C", "Jared C. Lyman", "Jared", "Lyman", middle="C.", aliases="Jared Lyman")
    P("WY-POWELL-CHARLES-B", "Charles B. Powell", "Charles", "Powell", middle="B.")
    P("WY-MILLS-TERRIL-J", "Terril J. Mills", "Terril", "Mills", middle="J.",
      aliases="Terril Mills; TERRIL MILLS")
    P("WY-GREET-TESSIA", "Tessia Greet", "Tessia", "Greet")
    P("WY-TRUMAN-MEGAN", "Megan Truman", "Megan", "Truman")
    P("WY-SINDELAR-MONA", "Mona Sindelar", "Mona", "Sindelar")
    P("WY-ANDERSON-SARAH", "Sarah Anderson", "Sarah", "Anderson")
    P("WY-BLUTT-ERIN-K", "Erin K. Blutt", "Erin", "Blutt", middle="K.", aliases="Erin Blutt")
    P("WY-HARSTAD-SHANA", "Shana Harstad", "Shana", "Harstad")
    P("WY-MURPHY-BILL", "Bill Murphy", "Bill", "Murphy")
    P("WY-LESTER-BRYONY-A", "Bryony A. Lester", "Bryony", "Lester", middle="A.")
    P("WY-DEBOLT-TAD-E", "Tad E. Debolt", "Tad", "Debolt", middle="E.")
    P("WY-JORDAN-DON", "Don Jordan", "Don", "Jordan")
    P("WY-TOLLEY-ALLEN-B", "Allen B. Tolley", "Allen", "Tolley", middle="B.")
    P("WY-BERRYMAN-LANCE-M", "Lance M. Berryman", "Lance", "Berryman", middle="M.",
      aliases="Lance M Berryman; LANCE MBERRYMAN")
    P("WY-HORATH-BRAD", "Brad Horath", "Brad", "Horath")
    P("WY-GROSS-EDWARD", "Edward Gross", "Edward", "Gross", aliases="Edward J. Gross III")
    P("WY-SURAT-TIM", "Tim Surat", "Tim", "Surat")
    P("WY-LOMBARD-KENT", "Kent Lombard", "Kent", "Lombard")
    P("WY-WITT-RAY", "Ray Witt", "Ray", "Witt")
    P("WY-PENNINGTON-SUSAN-D", "Susan D. Pennington", "Susan", "Pennington", middle="D.",
      aliases="Susan Pennington; SUSAN O. PENNINGTON; Susan O. Pennington")
    P("WY-SLOVER-DAVID-W", "David W. Slover", "David", "Slover", middle="W.", aliases="David Slover")
    P("WY-ORCHARD-CHARLEY", "Charley Orchard", "Charley", "Orchard", aliases="Charles Orchard")
    P("WY-RICE-DAN", "Dan Rice", "Dan", "Rice")
    P("WY-LUNGREN-VANCE-SR", "Vance Lungren Sr.", "Vance", "Lungren", aliases="Vance Lungren Sr")
    P("WY-MILLS-ANDREW", "Andrew Mills", "Andrew", "Mills")
    P("WY-FIRNEKAS-RANDALL", "Randall Firnekas", "Randall", "Firnekas")
    P("WY-MICHAEL-JANICE", "Janice Michael", "Janice", "Michael", aliases="Jan Michael")
    P("WY-COMPTON-ROBERT", "Robert Compton", "Robert", "Compton")
    P("WY-DRAKE-FREDERICK-A", "Frederick A. Drake", "Frederick", "Drake", middle="A.",
      aliases="FREDERICK ADRAKE")
    P("WY-HAGGERTY-JF", "J. F. Haggerty", "J. F.", "Haggerty", aliases="J F HAGGERTY")
    P("WY-GERTSCH-LARA", "Lara Gertsch", "Lara", "Gertsch")
    P("WY-GREET-DANIEL", "Daniel Greet", "Daniel", "Greet")

def legislature_terms():
    terms = []
    terms += [
        T(person_id="WY-GEIS-GERALD", name="Gerald E. Geis", party="R", office_group="state-senate",
          office="Senate District 20 (S20)", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_SOS12S],
          notes="Official 2012 SOS statewide Senate summary, Senate District 20: Gerald E. Geis (R) Total 7,592. Official Washakie share 3,456; official Big Horn 1,245; official Hot Springs 2,164; official Fremont 317; official Park 410 (1,245+2,164+317+410+3,456=7,592)."),
        T(person_id="WY-AGAR-WYATT", name="Wyatt Agar", party="R", office_group="state-senate",
          office="Senate District 20 (S20)", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_SOS16S, SRC_C16],
          notes="Official 2016 SOS statewide Senate summary, Senate District 20 (right column beside Senate District 18; that district's Total is not used): Wyatt Agar (R) 6,893, Mary Jane Norskog (D) 1,546. Official Washakie share Agar 3,157, Norskog 570 (official 2016 clerk same Washakie figures); official Big Horn 1,225-151; official Hot Springs 1,817-714; official Fremont 281-54; official Park 413-57."),
        T(person_id="WY-COOPER-ED", name="Ed Cooper", party="R", office_group="state-senate",
          office="Senate District 20 (S20)", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_SOS20S, SRC_C20],
          notes="Official 2020 SOS statewide Senate summary, Senate District 20 (right column beside Senate District 18; that district's Total is not used): Ed Cooper (R) 7,497, Theresa Livingston (D) 1,293. Official Washakie share Cooper 3,368, Livingston 543; official Big Horn 1,358-171; official Hot Springs 2,031-472; official Fremont 335-32; official Park 405-75 (sums to the official Totals)."),
        T(person_id="WY-COOPER-ED", name="Ed Cooper", party="R", office_group="state-senate",
          office="Senate District 20 (S20)", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_SOS24S, SRC_C24],
          notes="Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Washakie share 3,442 (sum of official 2024 clerk precinct rows, 5 of 5 precincts); official Big Horn 1,475; official Hot Springs 2,180; official Park 834; official Fremont 305 (1,475+2,180+834+305+3,442=8,236). S20 is off-cycle in 2026."),
    ]
    terms += [
        T(person_id="WY-GREEAR-MICHAEL-D", name="Michael D. Greear", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2013], term_end=FM[2015],
          election_year=2012, sources=[SRC_SOS12H],
          notes="Official 2012 SOS statewide House summary, House District 27: Mike Greear (R) Total 3,627. Official Washakie share 3,396; official Big Horn share 231."),
        T(person_id="WY-GREEAR-MICHAEL-D", name="Michael D. Greear", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2015], term_end=FM[2017],
          election_year=2014, sources=[SRC_SOS14H],
          notes="Official 2014 SOS statewide House summary, House District 27: Mike Greear (R) Total 2,650. Official Washakie share 2,484; official Big Horn share 166."),
        T(person_id="WY-GREEAR-MICHAEL-D", name="Michael D. Greear", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2017], term_end=FM[2019],
          election_year=2016, sources=[SRC_SOS16H, SRC_C16],
          notes="Official 2016 SOS statewide House summary, House District 27 (left column beside House District 28; that district's Total is not used): Michael D. Greear (R) 3,304, Robert D. McDonough, Jr. (D) 565. Official Washakie share Greear 3,077, McDonough 541 (official 2016 clerk same Washakie figures); official Big Horn 227-24."),
        T(person_id="WY-GREEAR-MICHAEL-D", name="Michael D. Greear", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_SOS18H, SRC_C18],
          notes="Official 2018 SOS statewide House summary, House District 27 (right column beside House District 26; that district's Total is not used): Mike Greear (R) Total 2,892. Official Washakie share 2,713 (official 2018 clerk 2,713); official Big Horn share 179."),
        T(person_id="WY-GREEAR-MICHAEL-D", name="Michael D. Greear", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20H, SRC_C20],
          notes="Official 2020 SOS statewide House summary, House District 27: Mike Greear (R) Total 3,763. Official Washakie share 3,494; official Big Horn share 269."),
        T(person_id="WY-LAWLEY-MARTHA", name="Martha Lawley", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_SOS22H],
          notes="Official 2022 SOS statewide House summary, House District 27: Martha Lawley (R) Total 3,143. Official Washakie share 2,713; official Big Horn share 430. Official SOS is used for this legislative seat; the official clerk's View/316 file is unofficial (election-night) and is not used as a canvass."),
        T(person_id="WY-LAWLEY-MARTHA", name="Martha Lawley", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2025], term_end=FM[2027],
          election_year=2024, sources=[SRC_SOS24H, SRC_C24],
          notes="Official 2024 SOS statewide House summary, House District 27: Martha Lawley (R) Total 3,918. Official Washakie share 3,379 (sum of official 2024 clerk precinct rows); official Big Horn share 539."),
        T(person_id="WY-LAWLEY-MARTHA", name="Martha Lawley", party="R", office_group="state-house",
          office="House District 27 (H27)", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_SOS26H, SRC_C26],
          notes="Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Washakie share Lawley 2,282, Livingston 430, write-ins 18 (official 2026 clerk same Washakie figures); official Big Horn 418-60."),
    ]
    return terms


def county_terms():
    terms = []
    terms += [
        T(person_id="WY-ANDERSON-AARON-J", name="Aaron J. Anderson", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_C16],
          notes="Official 2016 general County Commissioner Vote For 1: Aaron J. Anderson (R) 3,273."),
        T(person_id="WY-FRANDSON-FRED-W", name="Fred W. Frandson", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_C18],
          notes="Official 2018 general County Commissioner Vote For 2: Fred W. Frandson (R) 2,403, Terrence D. Wolf (R) 2,263 (3,145 ballots; vote-for-2 total 6,290)."),
        T(person_id="WY-WOLF-TERRENCE-D", name="Terrence D. Wolf", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_C18],
          notes="Official 2018 general County Commissioner Vote For 2: Terrence D. Wolf (R) 2,263 (ballot TERRENCE DWOLF). Official commissioners page lists Terry Wolf."),
        T(person_id="WY-ANDERSON-AARON-J", name="Aaron J. Anderson", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 general County Commissioner Vote For 1: Aaron Anderson (R) 3,405."),
        T(person_id="WY-SCHMELTZER-TOM", name="Tom Schmeltzer", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_COMM],
          notes="Official 2024 general Precinct Summary, County Commissioner Vote For 1, sum of official precinct rows (5 of 5): Tom Schmeltzer (R) 3,435. Official commissioners page lists Tom Schmeltzer as a current commissioner."),
        T(person_id="WY-WOLF-TERRENCE-D", name="Terrence D. Wolf", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, confidence="medium", sources=[SRC_COMM, SRC_C24, SRC_C26],
          notes="Continuing term. Official commissioners page lists Terry Wolf as a current commissioner; official 2024 Vote For 1 did not include this seat; official 2026 general re-elected Terrence D. Wolf. " + NOTE_2022 + " January 2023 start is inferred from the official four-year commissioner cycle (medium)."),
        T(person_id="WY-MARTINEZ-MORGAN", name="Morgan Martinez", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, confidence="medium", sources=[SRC_COMM, SRC_C24, SRC_C26],
          notes="Official commissioners page lists Morgan Martinez, Commissioner/Chairman, as current; official 2024 Vote For 1 did not include this seat; official 2026 general re-elected Morgan Martinez. " + NOTE_2022 + " January 2023 start is inferred from the official four-year commissioner cycle (medium)."),
        T(person_id="WY-WOLF-TERRENCE-D", name="Terrence D. Wolf", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 general County Commissioner Vote For 2: Terrence D. Wolf 2,024, Morgan Martinez 1,981, write-ins 112."),
        T(person_id="WY-MARTINEZ-MORGAN", name="Morgan Martinez", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 general County Commissioner Vote For 2: Morgan Martinez 1,981 (with Terrence D. Wolf 2,024)."),
    ]
    def row(pid, name, office, start, end, year, sources, notes, conf="high", party="R"):
        terms.append(T(person_id=pid, name=name, party=party, office_group="county", office=office,
                       term_start=start, term_end=end, election_year=year, sources=sources,
                       notes=notes, confidence=conf))
    row("WY-STRAUCH-MARY-GRACE", "Mary Grace Strauch", "County Clerk", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Clerk: Mary Grace Strauch (R) 2,866.")
    row("WY-KERN-DORIS", "Doris Kern", "County Treasurer", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Treasurer: Doris Kern (R) 2,895.")
    row("WY-TREANOR-KATHRYN", "Kathryn Treanor", "County Assessor", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Assessor: Kathryn Treanor (R) 2,772.")
    row("WY-RAKNESS-STEVEN-R", "Steven R. Rakness", "County Sheriff", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Sheriff: Steven R. Rakness (R) 2,803.")
    row("WY-WORRALL-JOHN-P", "John P. Worrall", "County Attorney", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Attorney: John P. Worrall (R) 2,657.")
    row("WY-WHITLOCK-SUZANN", "Suzann Whitlock", "Clerk of District Court", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general Clerk of District Court: Suzann Whitlock (R) 2,762.")
    row("WY-LAPP-JEFFREY-D", "Jeffrey D. Lapp", "County Coroner", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Coroner: Jeff Lapp (R) 2,876. Official 2026 ballot Jeffrey D. Lapp; official coroner page Jeff Lapp.")
    med = NOTE_2022 + " January 2023 start is inferred from the official four-year cycle and official current office pages plus official 2026 re-election (medium)."
    row("WY-PARRA-LILY-RAKNESS", "Lily Rakness Parra", "County Clerk", FM[2023], FM[2027], 2022,
        [SRC_CLERK, SRC_C26], "Official Clerk page names Lily Rakness Parra, Washakie County Clerk. Official 2026 general re-elected Lily Rakness Parra 2,537. " + med, "medium")
    row("WY-KERN-DORIS", "Doris Kern", "County Treasurer", FM[2023], FM[2027], 2022,
        [SRC_TREAS, SRC_C26], "Official Treasurer page names Doris Kern. Official 2026 general re-elected Doris Kern 2,593. " + med, "medium")
    row("WY-BROOKWELL-AUSTIN-T", "Austin T. Brookwell", "County Sheriff", FM[2023], FM[2027], 2022,
        [SRC_SHERIFF, SRC_C26], "Official Sheriff page names Austin T. Brookwell. Official 2026 general re-elected Austin T. Brookwell 2,562. " + med, "medium")
    row("WY-BARTON-ANTHONY-J", "Anthony J. Barton", "County Attorney", FM[2023], FM[2027], 2022,
        [SRC_ATTORNEY, SRC_C26], "Official Attorney page names Anthony J. Barton, County Attorney. Official 2026 general re-elected Anthony Barton 2,369. " + med, "medium")
    row("WY-HANSEN-MIRIAN", "Mirian Hansen", "Clerk of District Court", FM[2023], FM[2027], 2022,
        [SRC_CDC, SRC_C26], "Official Clerk of District Court page names Mirian Hansen (official spelling Mirian). Official 2026 general re-elected Mirian Hansen 2,442. " + med, "medium")
    row("WY-LAPP-JEFFREY-D", "Jeffrey D. Lapp", "County Coroner", FM[2023], FM[2027], 2022,
        [SRC_CORONER, SRC_C26], "Official coroner page names Jeff Lapp. Official 2026 general re-elected Jeffrey D. Lapp 2,592. " + med, "medium")
    row("WY-PARRA-LILY-RAKNESS", "Lily Rakness Parra", "County Clerk", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Clerk: Lily Rakness Parra 2,537.")
    row("WY-KERN-DORIS", "Doris Kern", "County Treasurer", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Treasurer: Doris Kern 2,593.")
    row("WY-SWALSTAD-BOBBY", "Bobby Swalstad", "County Assessor", FM[2027], FM[2031], 2026,
        [SRC_C26, SRC_ASSESSOR], "Official 2026 general County Assessor elect: Bobby Swalstad 2,415. Official assessor page contact block does not name the current assessor; the 2023-2027 holder is not yet collected from an official source (Phase-1 Nancy Quinn is not copied without official confirmation).")
    row("WY-BROOKWELL-AUSTIN-T", "Austin T. Brookwell", "County Sheriff", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Sheriff: Austin T. Brookwell 2,562.")
    row("WY-BARTON-ANTHONY-J", "Anthony J. Barton", "County Attorney", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Attorney: Anthony Barton 2,369.")
    row("WY-HANSEN-MIRIAN", "Mirian Hansen", "Clerk of District Court", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general Clerk of District Court: Mirian Hansen 2,442.")
    row("WY-LAPP-JEFFREY-D", "Jeffrey D. Lapp", "County Coroner", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Coroner: Jeffrey D. Lapp 2,592.")
    return terms

def judicial_terms():
    terms = []
    def retain(pid, name, office, start, end, year, notes, sources=None):
        terms.append(T(person_id=pid, name=name, office_group="judicial", office=office,
                       jurisdiction="5th Judicial District", term_start=start, term_end=end,
                       election_year=year, how_took_office="retained", party="",
                       sources=sources or [SRC_COURT], notes=notes))
    retain("WY-SKAR-ROBERT-E", "Robert E. Skar",
           "District Judge, 5th Judicial District (historical official 2016 named retention)",
           FM[2017], FM[2021], 2016,
           "Official 2016 Washakie general named retention ROBERT E. SKAR. Full name and 5th JD assignment from official Wyoming Judicial Branch sources already used in the Park history.",
           [SRC_C16, SRC_COURT])
    retain("WY-WATERS-BRUCE-B", "Bruce B. Waters",
           "Circuit Judge, 5th Judicial District (historical official 2018 named retention)",
           FM[2019], FM[2023], 2018,
           "Official 2018 Washakie general RETAIN JUDGE BRUCE B. WATERS YES 2,307 / NO 368.",
           [SRC_C18, SRC_COURT])
    retain("WY-OVERFIELD-BOBBI", "Bobbi Overfield",
           "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
           FM[2021], FM[2027], 2020,
           "Official 2020 Washakie general DIST CT - OVERFIELD, visually confirmed official YES 3,102. Official March 2026 roster title: Fifth Judicial District Judge - Big Horn/Hot Springs/Washakie. Distinct from Commissioner Dossie Overfield.",
           [SRC_C20, SRC_COURT])
    retain("WY-LUHM-ED", "Ed Luhm",
           "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
           FM[2021], FM[2025], 2020,
           "Official 2020 Washakie general CIR CT - LUHM (official named retention). Official March 2026 roster title: Fifth Judicial Circuit Judge - Big Horn/Hot Springs/Washakie. Official 2024 ballot Edward G. Luhm.",
           [SRC_C20, SRC_COURT])
    retain("WY-SIMPSON-BILL", "Bill Simpson",
           "District Judge, 5th Judicial District (Park)",
           FM[2025], FM[2031], 2024,
           "Official 2024 Washakie Precinct Summary RETAIN JUDGE BILL SIMPSON, sum of official precinct rows: YES 2,817 / NO 493. Official March 2026 roster names Bill Simpson, term expiring 2030 (January 2031 used, consistent with the Park history).",
           [SRC_C24, SRC_COURT])
    retain("WY-DARRAH-JOEY", "Joey Darrah",
           "Circuit Judge, 5th Judicial District (Park)",
           FM[2025], FM[2029], 2024,
           "Official 2024 Washakie Precinct Summary RETAIN JUDGE S. JOSEPH JOEY DARRAH, sum of official precinct rows: YES 2,750 / NO 507. Official March 2026 roster names Joey Darrah, term expiring 2028 (January 2029 used, consistent with the Park history).",
           [SRC_C24, SRC_COURT])
    retain("WY-LUHM-ED", "Ed Luhm",
           "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
           FM[2025], FM[2029], 2024,
           "Official 2024 Washakie Precinct Summary RETAIN JUDGE EDWARD G. LUHM, sum of official precinct rows: YES 2,911 / NO 529. Official March 2026 roster term expiring 2028 (January 2029).",
           [SRC_C24, SRC_COURT])
    retain("WY-OVERFIELD-BOBBI", "Bobbi Overfield",
           "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
           FM[2027], FM[2033], 2026,
           "Official 2026 Washakie general RETAIN JUDGE BOBBI OVERFIELD YES 2,038 / NO 479. Official March 2026 roster (Park history) used January 2033 for this retention cycle.",
           [SRC_C26, SRC_COURT])
    return terms


def municipal_terms():
    terms = []
    terms += [
        T(person_id="WY-GILL-JIM", name="Jim Gill", office_group="municipal", office="Worland Mayor",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, party="", confidence="medium",
          sources=[SRC_C16, SRC_WORLAND_FAQ],
          notes="Official 2016 general MAYOR: Jim Gill 1,320, Keith A. McDonald 844. " + NOTE_MUNI_JAN),
        T(person_id="WY-GILL-JIM", name="Jim Gill", office_group="municipal", office="Worland Mayor",
          term_start=FM[2021], term_end=FM[2025], election_year=2020, party="", confidence="medium",
          sources=[SRC_C20, SRC_WORLAND_FAQ],
          notes="Official 2020 general MAYOR - CITY OF WORLAND: Jim Gill 1,470, Keith A. McDonald 694, write-ins 8. " + NOTE_MUNI_JAN),
        T(person_id="WY-GEORGE-REBECCA", name="Rebecca George", office_group="municipal", office="Worland Mayor",
          term_start=FM[2025], term_end=FM[2029], election_year=2024, party="", confidence="medium",
          sources=[SRC_C24, SRC_WORLAND, SRC_WORLAND_FAQ],
          notes="Official 2024 Precinct Summary MAYOR - CITY OF WORLAND, sum of official Worland precinct rows: Rebecca George 1,373, Jim Gill 764. Official city bio: Rebecca George was elected as Mayor of the City of Worland on November 5, 2024. " + NOTE_MUNI_JAN),
    ]
    terms += [
        T(person_id="WY-FERNANDEZ-LISA", name="Lisa Fernandez", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2017], term_end=FM[2019], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 1 (2-year): Lisa Fernandez 652. " + NOTE_MUNI_JAN),
        T(person_id="WY-GENTZLER-KEITH-A", name="Keith A. Gentzler", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 1 (4-year) Vote For 2: Keith A. Gentzler 605, Jacquelyn Ernest 371. " + NOTE_MUNI_JAN),
        T(person_id="WY-ERNEST-JACQUELYN", name="Jacquelyn Ernest", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 1 (4-year) Vote For 2: Jacquelyn Ernest 371. " + NOTE_MUNI_JAN),
        T(person_id="WY-GERBER-GARY-W", name="Gary W. Gerber", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2019], term_end=FM[2021], election_year=2018, confidence="medium", sources=[SRC_C18],
          notes="Official 2018 Worland Council Ward 1 (2-year): Gary W. Gerber 545. " + NOTE_MUNI_JAN),
        T(person_id="WY-RENNER-DELAYNE-M", name="Delayne M. Renner", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2019], term_end=FM[2023], election_year=2018, confidence="medium", sources=[SRC_C18],
          notes="Official 2018 Worland Council Ward 1 (4-year): Delayne M. Renner 318, Gerald Alexander 281. " + NOTE_MUNI_JAN),
        T(person_id="WY-MARTINEZ-ADAM-G", name="Adam G. Martinez", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2021], term_end=FM[2023], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 1 (2-year): Adam Martinez 487, Kenneth Shearer 292. " + NOTE_MUNI_JAN),
        T(person_id="WY-SCHAEFFER-SCOTT", name="Scott Schaeffer", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2021], term_end=FM[2025], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 1 (4-year): Scott Schaeffer elected (official named winner). " + NOTE_MUNI_JAN),
        T(person_id="WY-GLANZ-BILL", name="Bill Glanz", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2025], term_end=FM[2029], election_year=2024, confidence="medium", sources=[SRC_C24, SRC_WORLAND],
          notes="Official 2024 Precinct Summary WORLAND COUNCILMEMBER WARD 1, official precinct total: Bill Glanz 433, Jeff Pomeroy 275. Official current council lists Bill Glanz. " + NOTE_MUNI_JAN),
        T(person_id="WY-BROOKWELL-BARBARA", name="Barbara Brookwell", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2023], term_end=FM[2027], election_year=2022, confidence="medium", sources=[SRC_WORLAND, SRC_C26],
          notes="Official current Ward 1 council lists Barbara Brookwell. Official 2026 general Ward 1 Vote For 2 re-elected Barbara Brookwell 371 and Adam G. Martinez 329. " + NOTE_2022 + " " + NOTE_MUNI_JAN),
        T(person_id="WY-MARTINEZ-ADAM-G", name="Adam G. Martinez", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2023], term_end=FM[2027], election_year=2022, confidence="medium", sources=[SRC_WORLAND, SRC_C26],
          notes="Official current Ward 1 council lists Adam Martinez. Official 2026 general Ward 1 Vote For 2: Adam G. Martinez 329 (with Barbara Brookwell 371). " + NOTE_2022 + " " + NOTE_MUNI_JAN),
        T(person_id="WY-BROOKWELL-BARBARA", name="Barbara Brookwell", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2027], term_end=FM[2031], election_year=2026, confidence="medium", sources=[SRC_C26],
          notes="Official 2026 general Worland Council Ward 1 Vote For 2: Barbara Brookwell 371, Adam G. Martinez 329 (Kent Foulger 204, Christopher O'Neal 93). " + NOTE_MUNI_JAN),
        T(person_id="WY-MARTINEZ-ADAM-G", name="Adam G. Martinez", office_group="municipal", office="Worland Council Ward 1",
          term_start=FM[2027], term_end=FM[2031], election_year=2026, confidence="medium", sources=[SRC_C26],
          notes="Official 2026 general Worland Council Ward 1 Vote For 2: Adam G. Martinez 329. " + NOTE_MUNI_JAN),
    ]
    terms += [
        T(person_id="WY-KOCH-DENNIS-A", name="Dennis A. Koch", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 2 Vote For 2: Dennis A. Koch 589, Mandy Horath 505. " + NOTE_MUNI_JAN),
        T(person_id="WY-HORATH-MANDY", name="Mandy Horath", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 2 Vote For 2: Mandy Horath 505. " + NOTE_MUNI_JAN),
        T(person_id="WY-SCHNEIDER-CHRISTY-R", name="Christy R. Schneider", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2019], term_end=FM[2023], election_year=2018, confidence="medium", sources=[SRC_C18],
          notes="Official 2018 Worland Council Ward 2 Vote For 1: Christy R. Schneider 415, Melissa Johnston 177. " + NOTE_MUNI_JAN),
        T(person_id="WY-FREDRICKS-WENDY", name="Wendy Fredricks", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2021], term_end=FM[2025], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 2 (4-year) Vote For 2: Wendy Fredricks and Mandy Horath were the official named winners (Kody Lynn Demunbrun and Morgan Muller also appeared). " + NOTE_MUNI_JAN),
        T(person_id="WY-HORATH-MANDY", name="Mandy Horath", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2021], term_end=FM[2025], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 2 (4-year) Vote For 2: Mandy Horath official named winner. " + NOTE_MUNI_JAN),
        T(person_id="WY-FREDRICKS-WENDY", name="Wendy Fredricks", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2025], term_end=FM[2029], election_year=2024, confidence="medium", sources=[SRC_C24, SRC_WORLAND],
          notes="Official 2024 Precinct Summary WORLAND COUNCILMEMBER WARD 2 4YR Vote For 2, official precinct total: Wendy Fredricks 546, Mandy Horath 297, Lawrence Meier 288, Kassie Nolting 266. " + NOTE_MUNI_JAN),
        T(person_id="WY-HORATH-MANDY", name="Mandy Horath", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2025], term_end=FM[2029], election_year=2024, confidence="medium", sources=[SRC_C24, SRC_WORLAND],
          notes="Official 2024 Precinct Summary Ward 2 4YR Vote For 2: Mandy Horath 297 (official second-place named winner). " + NOTE_MUNI_JAN),
        T(person_id="WY-LEY-SHERYL", name="Sheryl Ley", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2025], term_end=FM[2027], election_year=2024, confidence="medium", sources=[SRC_C24, SRC_WORLAND],
          notes="Official 2024 Precinct Summary WORLAND COUNCILMEMBER WARD 2 2YR Vote For 1: Sheryl Ley 397, Terry Batt 365. Official current council lists Sheryl Ley. " + NOTE_MUNI_JAN),
        T(person_id="WY-LEY-SHERYL", name="Sheryl Ley", office_group="municipal", office="Worland Council Ward 2",
          term_start=FM[2027], term_end=FM[2031], election_year=2026, confidence="medium", sources=[SRC_C26],
          notes="Official 2026 general Worland Council Ward 2 Vote For 1: Sheryl Ley 323, Barbara Burgess 258. " + NOTE_MUNI_JAN),
    ]
    terms += [
        T(person_id="WY-BRINKERHOFF-LORESA", name="Loresa Brinkerhoff", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2017], term_end=FM[2019], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 3 (2-year): Loresa Brinkerhoff 259, Cain Torrez 237. " + NOTE_MUNI_JAN),
        T(person_id="WY-NEUFER-MIKE", name="Mike Neufer", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2017], term_end=FM[2021], election_year=2016, confidence="medium", sources=[SRC_C16],
          notes="Official 2016 Worland Council Ward 3 (4-year): Mike Neufer 326, Marcus Ron Sanchez 188. " + NOTE_MUNI_JAN),
        T(person_id="WY-RIVERA-MELISSA", name="Melissa Rivera", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2019], term_end=FM[2023], election_year=2018, confidence="medium", sources=[SRC_C18],
          notes="Official 2018 Worland Council Ward 3 Vote For 2: Melissa Rivera 270, Kreg Lombard 238. " + NOTE_MUNI_JAN),
        T(person_id="WY-LOMBARD-KREG", name="Kreg Lombard", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2019], term_end=FM[2023], election_year=2018, confidence="medium", sources=[SRC_C18],
          notes="Official 2018 Worland Council Ward 3 Vote For 2: Kreg Lombard 238. " + NOTE_MUNI_JAN),
        T(person_id="WY-NEUFER-MIKE", name="Mike Neufer", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2021], term_end=FM[2023], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 3 (2-year): Mike Neufer 463. " + NOTE_MUNI_JAN),
        T(person_id="WY-WORLEY-WILLIAM", name="William Worley", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2021], term_end=FM[2025], election_year=2020, confidence="medium", sources=[SRC_C20],
          notes="Official 2020 Worland Council Ward 3 (4-year): William Worley 283, Michael Sanchez 202, write-ins 5 (visually confirmed official totals). " + NOTE_MUNI_JAN),
        T(person_id="WY-WORLEY-WILLIAM", name="William Worley", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2025], term_end=FM[2029], election_year=2024, confidence="medium", sources=[SRC_C24, SRC_WORLAND],
          notes="Official 2024 Precinct Summary WORLAND COUNCILMEMBER WARD 3 Vote For 1, official precinct total: William Worley 237, Tony Wartman 235. Official current council lists William Worley. " + NOTE_MUNI_JAN),
        T(person_id="WY-PIKE-JACQUELINE", name="Jacqueline Pike", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2023], term_end=FM[2027], election_year=2022, confidence="medium", sources=[SRC_WORLAND, SRC_C26],
          notes="Official current Ward 3 council lists Jacque Pike. Official 2026 general Ward 3 Vote For 2 re-elected Jacqueline Pike 218 and elected Darr Lea Walker 169 (Tony Wartman 130, Tony Brown 52). " + NOTE_2022 + " " + NOTE_MUNI_JAN),
        T(person_id="WY-NEUFER-MIKE", name="Mike Neufer", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2023], term_end=FM[2027], election_year=2022, confidence="medium", sources=[SRC_WORLAND],
          notes="Official current Ward 3 council lists Mike Neufer. Official 2026 Ward 3 Vote For 2 elected Jacqueline Pike and Darr Lea Walker; the official source does not identify which of Neufer or Worley (if either) departs, and that name is not invented. " + NOTE_2022 + " " + NOTE_MUNI_JAN),
        T(person_id="WY-PIKE-JACQUELINE", name="Jacqueline Pike", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2027], term_end=FM[2031], election_year=2026, confidence="medium", sources=[SRC_C26],
          notes="Official 2026 general Worland Council Ward 3 Vote For 2: Jacqueline Pike 218, Darr Lea Walker 169. " + NOTE_MUNI_JAN),
        T(person_id="WY-WALKER-DARR-LEA", name="Darr Lea Walker", office_group="municipal", office="Worland Council Ward 3",
          term_start=FM[2027], term_end=FM[2031], election_year=2026, confidence="medium", sources=[SRC_C26],
          notes="Official 2026 general Worland Council Ward 3 Vote For 2: Darr Lea Walker 169 (second-place official named winner). The official current council still lists Jacque Pike, Mike Neufer, and William Worley; the departing member is not identified and is not invented. " + NOTE_MUNI_JAN),
    ]
    terms += [
        T(person_id="WY-BECKLEY-ERNIE", name="Ernie Beckley", office_group="municipal", office="Ten Sleep Mayor",
          term_start="2026-01-06", term_end="2027-01-04", election_year=0, how_took_office="unknown",
          confidence="medium", party="", sources=[SRC_TS_JAN, SRC_TS_OCT],
          notes="Official Town of Ten Sleep council minutes, January 6, 2026 and October 6, 2026, name Mayor Ernie Beckley among those attending. Official town pages do not print a roster or term end; the end date is left at the January 2027 switch so the live roster includes the official current mayor. A later official election or appointment date was not found."),
        T(person_id="WY-DEWITT-BART", name="Bart DeWitt", office_group="municipal", office="Ten Sleep Council",
          term_start="2026-01-06", term_end="2027-01-04", election_year=0, how_took_office="unknown",
          confidence="medium", sources=[SRC_TS_JAN, SRC_TS_OCT],
          notes="Official January 6 and October 6, 2026 Ten Sleep minutes list Councilperson Bart DeWitt. Official term end was not found."),
        T(person_id="WY-SWEENEY-CONNIE", name="Connie Sweeney", office_group="municipal", office="Ten Sleep Council",
          term_start="2026-01-06", term_end="2027-01-04", election_year=0, how_took_office="unknown",
          confidence="medium", sources=[SRC_TS_JAN, SRC_TS_OCT],
          notes="Official January 6 and October 6, 2026 Ten Sleep minutes list Councilperson Connie Sweeney. Official term end was not found."),
        T(person_id="WY-TRUMAN-AMY", name="Amy Truman", office_group="municipal", office="Ten Sleep Council",
          term_start="2026-01-06", term_end="2027-01-04", election_year=0, how_took_office="unknown",
          confidence="medium", sources=[SRC_TS_JAN, SRC_TS_OCT],
          notes="Official January 6 and October 6, 2026 Ten Sleep minutes list Councilperson Amy Truman. Official term end was not found."),
        T(person_id="WY-LYNEMA-NICHOLE", name="Nichole Lynema", office_group="municipal", office="Ten Sleep Council",
          term_start="2026-10-06", term_end="2027-01-04", election_year=0, how_took_office="unknown",
          confidence="medium", sources=[SRC_TS_OCT, SRC_TS_JAN],
          notes="Official October 6, 2026 Ten Sleep minutes list Councilwoman Lynema attending via Zoom. Official January 6, 2026 minutes list Nichole Lynema under others attending, not as council. Appointment or election date is not printed; term_start is the first official minutes date that styles her Councilwoman (medium). Official term end was not found."),
    ]
    return terms

def school_terms():
    terms = []
    o1 = "Washakie County School District #1 Trustee"
    o2 = "Washakie County School District #2 Trustee"
    for pid, name, note in [
        ("WY-TOMMERUP-DAVID-R", "David R. Tommerup", "Official 2016 CSD #1 Trustee Vote For 3: David R. Tommerup 1,855, Joe Bishop 1,664, Dean Dupree 1,582 (Julie Haun 1,570 finished fourth and is not seated)."),
        ("WY-BISHOP-JOE", "Joe Bishop", "Official 2016 CSD #1 Trustee Vote For 3: Joe Bishop 1,664."),
        ("WY-DUPREE-DEAN", "Dean Dupree", "Official 2016 CSD #1 Trustee Vote For 3: Dean Dupree 1,582."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o1,
                       term_start=FM[2017], term_end=FM[2021], election_year=2016, sources=[SRC_C16], notes=note))
    for pid, name, note in [
        ("WY-BRYANT-DON", "Don Bryant", "Official 2018 CSD #1 Trustee Vote For 4: Don Bryant 1,984, Sarah Lungren 1,981, Duane S. Whitlock 1,805, Terri Logan 1,647 (Anna Venable 1,279 finished fifth and is not seated)."),
        ("WY-LUNGREN-SARAH", "Sarah Lungren", "Official 2018 CSD #1 Trustee Vote For 4: Sarah Lungren 1,981."),
        ("WY-WHITLOCK-DUANE-S", "Duane S. Whitlock", "Official 2018 CSD #1 Trustee Vote For 4: Duane S. Whitlock 1,805."),
        ("WY-LOGAN-TERRI", "Terri Logan", "Official 2018 CSD #1 Trustee Vote For 4: Terri Logan 1,647."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o1,
                       term_start=FM[2019], term_end=FM[2023], election_year=2018, sources=[SRC_C18], notes=note))
    for pid, name, note in [
        ("WY-TOMMERUP-DAVID-R", "David R. Tommerup", "Official 2020 CSD #1 Trustee Vote For 3, visually confirmed official totals: David R. Tommerup 2,251, Brett Argeris 2,066, Jonathan Hake 1,609 (Tim Wright 1,237, Tami Young 1,008)."),
        ("WY-ARGERIS-BRETT", "Brett Argeris", "Official 2020 CSD #1 Trustee Vote For 3: Brett Argeris 2,066."),
        ("WY-HAKE-JONATHAN", "Jonathan Hake", "Official 2020 CSD #1 Trustee Vote For 3: Jonathan Hake 1,609."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o1,
                       term_start=FM[2021], term_end=FM[2025], election_year=2020, sources=[SRC_C20], notes=note))
    for pid, name, note in [
        ("WY-TOMMERUP-DAVID-R", "David R. Tommerup", "Official 2024 Precinct Summary CSD #1 Vote For 3, sum of official precinct rows (4 Worland-area precincts): David R. Tommerup 2,165, Brett Argeris 1,767, Becky Dooley 1,622 (Jonathan Hake 1,603 finished fourth and is not seated)."),
        ("WY-ARGERIS-BRETT", "Brett Argeris", "Official 2024 CSD #1 Vote For 3 precinct sum: Brett Argeris 1,767."),
        ("WY-DOOLEY-BECKY", "Becky Dooley", "Official 2024 CSD #1 Vote For 3 precinct sum: Becky Dooley 1,622."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o1,
                       term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24], notes=note))
    for pid, name, note in [
        ("WY-MERCADO-KATHY", "Kathy Mercado", "Official 2026 general Washakie Co School Dist 1 Trustee Vote For 4: Kathy Mercado 1,768, Jonathan Hake 1,713, Terri Logan 1,543, Jaime Mertz 1,401. Official 2022 clerk file is unofficial; departing 2022-class members are not yet collected."),
        ("WY-HAKE-JONATHAN", "Jonathan Hake", "Official 2026 CSD #1 Vote For 4: Jonathan Hake 1,713."),
        ("WY-LOGAN-TERRI", "Terri Logan", "Official 2026 CSD #1 Vote For 4: Terri Logan 1,543."),
        ("WY-MERTZ-JAIME", "Jaime Mertz", "Official 2026 CSD #1 Vote For 4: Jaime Mertz 1,401."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o1,
                       term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26], notes=note))
    for pid, name, start, end, year, src, note in [
        ("WY-LYMAN-JARED-C", "Jared C. Lyman", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 CSD #2 Trustee (4-year) Vote For 3: Jared C. Lyman 351, Charles B. Powell 299, Terril Mills 250 (Dan Rice 221 finished fourth)."),
        ("WY-POWELL-CHARLES-B", "Charles B. Powell", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 CSD #2 (4-year) Vote For 3: Charles B. Powell 299."),
        ("WY-MILLS-TERRIL-J", "Terril J. Mills", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 CSD #2 (4-year) Vote For 3: Terril Mills 250."),
        ("WY-GREET-TESSIA", "Tessia Greet", FM[2017], FM[2019], 2016, SRC_C16,
         "Official 2016 CSD #2 Trustee (2-year): Tessia Greet 310, Mandy Lowry 137."),
        ("WY-TRUMAN-MEGAN", "Megan Truman", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 CSD #2 Trustee Vote For 2: Megan Truman 245, Mona Sindelar 182."),
        ("WY-SINDELAR-MONA", "Mona Sindelar", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 CSD #2 Trustee Vote For 2: Mona Sindelar 182."),
        ("WY-ANDERSON-SARAH", "Sarah Anderson", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 CSD #2 Trustee Vote For 3, visually confirmed official totals: Sarah Anderson 338, Jared Lyman 278, Erin Blutt 246 (C. J. Grimes 158, Brandon Weddle 146)."),
        ("WY-LYMAN-JARED-C", "Jared C. Lyman", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 CSD #2 Vote For 3: Jared Lyman 278."),
        ("WY-BLUTT-ERIN-K", "Erin K. Blutt", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 CSD #2 Vote For 3: Erin Blutt 246."),
        ("WY-LYMAN-JARED-C", "Jared C. Lyman", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 Precinct Summary CSD #2 Vote For 3 (official Ten Sleep precinct 03-01 only): Jared Lyman 368, Erin K. Blutt 318, Shana Harstad 317."),
        ("WY-BLUTT-ERIN-K", "Erin K. Blutt", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 CSD #2 Vote For 3 precinct total: Erin K. Blutt 318."),
        ("WY-HARSTAD-SHANA", "Shana Harstad", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 CSD #2 Vote For 3 precinct total: Shana Harstad 317."),
        ("WY-MURPHY-BILL", "Bill Murphy", FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 general Washakie Co School Dist 2 Trustee Vote For 2: Bill Murphy 272, Bryony A. Lester 267. Official 2022 clerk file is unofficial; departing 2022-class members are not yet collected."),
        ("WY-LESTER-BRYONY-A", "Bryony A. Lester", FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 CSD #2 Vote For 2: Bryony A. Lester 267."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="schools", office=o2,
                       term_start=start, term_end=end, election_year=year, sources=[src], notes=note))
    return terms


def special_terms():
    terms = []
    fire = "Worland Fire Protection District Director"
    cem = "Ten Sleep Cemetery District Trustee"
    rural = "Washakie County Conservation District Supervisor Rural"
    urban = "Washakie County Conservation District Supervisor Urban"
    atlg = "Washakie County Conservation District Supervisor At-Large"
    tsfire = "Ten Sleep Fire Protection District Trustee"
    for pid, name, start, end, year, src, note in [
        ("WY-DEBOLT-TAD-E", "Tad E. Debolt", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 Worland Fire Protection Dist 1 Director Vote For 3: Tad E. Debolt 2,230, Don Jordan 2,049, Allen B. Tolley 1,840."),
        ("WY-JORDAN-DON", "Don Jordan", FM[2017], FM[2021], 2016, SRC_C16, "Official 2016 fire Vote For 3: Don Jordan 2,049."),
        ("WY-TOLLEY-ALLEN-B", "Allen B. Tolley", FM[2017], FM[2021], 2016, SRC_C16, "Official 2016 fire Vote For 3: Allen B. Tolley 1,840."),
        ("WY-HORATH-BRAD", "Brad Horath", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 Worland Fire Protection Dist 1 Director Vote For 2: Brad Horath 1,397, Lance M. Berryman 1,332 (Dale Link 1,059, Edward J. Gross III 461)."),
        ("WY-BERRYMAN-LANCE-M", "Lance M. Berryman", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 fire Vote For 2: Lance M. Berryman 1,332."),
        ("WY-DEBOLT-TAD-E", "Tad E. Debolt", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 Worland Fire Dist One Director Vote For 3, visually confirmed official totals: Tad E. Debolt 2,445, Tim Surat 2,000, Edward Gross 1,902."),
        ("WY-SURAT-TIM", "Tim Surat", FM[2021], FM[2025], 2020, SRC_C20, "Official 2020 fire Vote For 3: Tim Surat 2,000."),
        ("WY-GROSS-EDWARD", "Edward Gross", FM[2021], FM[2025], 2020, SRC_C20, "Official 2020 fire Vote For 3: Edward Gross 1,902."),
        ("WY-LOMBARD-KENT", "Kent Lombard", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 Precinct Summary Worland Fire Protection Dist Vote For 3, sum of official precinct rows: Kent Lombard 2,342, Tad E. Debolt 2,159, Tim Surat 1,949."),
        ("WY-DEBOLT-TAD-E", "Tad E. Debolt", FM[2025], FM[2029], 2024, SRC_C24, "Official 2024 fire precinct sum: Tad E. Debolt 2,159."),
        ("WY-SURAT-TIM", "Tim Surat", FM[2025], FM[2029], 2024, SRC_C24, "Official 2024 fire precinct sum: Tim Surat 1,949."),
        ("WY-BERRYMAN-LANCE-M", "Lance M. Berryman", FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 general Worland Fire Protection Dist 1 Director Vote For 2: Lance M. Berryman 1,830, Ray Witt 1,690. Official 2022 clerk file is unofficial; departing 2022-class members are not yet collected."),
        ("WY-WITT-RAY", "Ray Witt", FM[2027], FM[2031], 2026, SRC_C26, "Official 2026 fire Vote For 2: Ray Witt 1,690."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="special-districts", office=fire,
                       term_start=start, term_end=end, election_year=year, sources=[src], notes=note))
    for pid, name, office, start, end, year, src, note in [
        ("WY-PENNINGTON-SUSAN-D", "Susan D. Pennington", atlg, FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 Conservation at-large: Susan Pennington 3,058."),
        ("WY-SLOVER-DAVID-W", "David W. Slover", rural, FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 Conservation Rural: David Slover 3,106."),
        ("WY-ORCHARD-CHARLEY", "Charley Orchard", rural, FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 Conservation Trustee Rural Vote For 2: Charles Orchard 2,368, Dan Rice 2,316."),
        ("WY-RICE-DAN", "Dan Rice", rural, FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 Conservation Rural Vote For 2: Dan Rice 2,316."),
        ("WY-LUNGREN-VANCE-SR", "Vance Lungren Sr.", urban, FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 Conservation Trustee Urban Vote For 1: Vance Lungren Sr. 2,451."),
        ("WY-PENNINGTON-SUSAN-D", "Susan D. Pennington", atlg, FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 Conservation at-large: Susan D. Pennington 3,351, write-ins 24 (visually confirmed)."),
        ("WY-SLOVER-DAVID-W", "David W. Slover", rural, FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 Conservation Rural: David W. Slover (official named winner)."),
        ("WY-MILLS-ANDREW", "Andrew Mills", atlg, FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 Precinct Summary Washakie Co Conservation Dist Vote For 2, sum of official precinct rows: Andrew Mills 2,524, Susan D. Pennington 2,465. Official 2024 contest title is not split rural/urban; both official named winners are recorded as at-large."),
        ("WY-PENNINGTON-SUSAN-D", "Susan D. Pennington", atlg, FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 Conservation Vote For 2 precinct sum: Susan D. Pennington 2,465."),
        ("WY-ORCHARD-CHARLEY", "Charley Orchard", rural, FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 general Washakie Supervisor Rural Vote For 2: Charley Orchard 2,361, write-ins 85 only. The second seat is write-in-only with no named certified winner and is not filled."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="special-districts", office=office,
                       term_start=start, term_end=end, election_year=year, sources=[src], notes=note))
    for pid, name, start, end, year, src, note in [
        ("WY-FIRNEKAS-RANDALL", "Randall Firnekas", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 Ten Sleep Cemetery Vote For 2: Randall Firnekas 392, Janice Michael 339."),
        ("WY-MICHAEL-JANICE", "Janice Michael", FM[2017], FM[2021], 2016, SRC_C16,
         "Official 2016 Ten Sleep Cemetery Vote For 2: Janice Michael 339."),
        ("WY-COMPTON-ROBERT", "Robert Compton", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 Ten Sleep Cemetery Dist Vote For 3: J. F. Haggerty 313, Robert Compton 311, Frederick A. Drake 297."),
        ("WY-HAGGERTY-JF", "J. F. Haggerty", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 cemetery Vote For 3: J. F. Haggerty 313."),
        ("WY-DRAKE-FREDERICK-A", "Frederick A. Drake", FM[2019], FM[2023], 2018, SRC_C18,
         "Official 2018 cemetery Vote For 3: Frederick A. Drake 297."),
        ("WY-FIRNEKAS-RANDALL", "Randall Firnekas", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 Ten Sleep Cemetery Dist Trustee Vote For 2: Randall Firnekas and Janice Michael (official named winners; Janice Michael official total 360)."),
        ("WY-MICHAEL-JANICE", "Janice Michael", FM[2021], FM[2025], 2020, SRC_C20,
         "Official 2020 cemetery Vote For 2: Janice Michael 360."),
        ("WY-MILLS-TERRIL-J", "Terril J. Mills", FM[2025], FM[2027], 2024, SRC_C24,
         "Official 2024 Precinct Summary Ten Sleep Cemetery Dist Trustee 2YR Vote For 1 (official precinct 03-01): Terril Mills 402."),
        ("WY-MICHAEL-JANICE", "Janice Michael", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 Ten Sleep Cemetery Dist Trustee 4YR Vote For 2 (official precinct 03-01): Jan Michael 378, Randall Firnekas 344."),
        ("WY-FIRNEKAS-RANDALL", "Randall Firnekas", FM[2025], FM[2029], 2024, SRC_C24,
         "Official 2024 cemetery 4YR Vote For 2: Randall Firnekas 344."),
        ("WY-GERTSCH-LARA", "Lara Gertsch", FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 general Ten Sleep Cemetery Dist Trustee 4YR Vote For 3: Lara Gertsch 291, Terril J. Mills 281, write-ins 15. The third seat is write-in-only with no named certified winner and is not filled."),
        ("WY-MILLS-TERRIL-J", "Terril J. Mills", FM[2027], FM[2031], 2026, SRC_C26,
         "Official 2026 cemetery Vote For 3: Terril J. Mills 281."),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="special-districts", office=cem,
                       term_start=start, term_end=end, election_year=year, sources=[src], notes=note))
    terms.append(T(person_id="WY-GREET-DANIEL", name="Daniel Greet", office_group="special-districts",
                   office=tsfire, term_start=FM[2027], term_end=FM[2031], election_year=2026,
                   confidence="medium", sources=[SRC_C26],
                   notes="Official 2026 general page 8, TEN SLEEP SENIOR CENTER 3-1, Ten Sleep Fire Trustee 4YR: Daniel Greet 224, write-ins 2, contest totals 251. Treated as the whole-district result because this is the only official precinct reported for the contest (medium)."))
    return terms

def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 20 (S20)", 1)],
        "state-house": [("House District 27 (H27)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [("Worland Mayor", 1), ("Worland Council Ward 1", 3),
                      ("Worland Council Ward 2", 3), ("Worland Council Ward 3", 3),
                      ("Ten Sleep Mayor", 1), ("Ten Sleep Council", 4)],
        "schools": [("Washakie County School District #1 Trustee", 7),
                    ("Washakie County School District #2 Trustee", 5)],
        "special-districts": [
            ("Worland Fire Protection District Director", 5),
            ("Washakie County Conservation District Supervisor At-Large", 2),
            ("Washakie County Conservation District Supervisor Rural", 2),
            ("Washakie County Conservation District Supervisor Urban", 1),
            ("Ten Sleep Cemetery District Trustee", 5),
            ("Ten Sleep Fire Protection District Trustee", 1),
        ],
        "judicial": [
            ("District Judge, 5th Judicial District (Park)", 1),
            ("District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", 1),
            ("Circuit Judge, 5th Judicial District (Park)", 1),
            ("Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)", 1),
        ],
    }


def build_washakie():
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
        "Washakie clerk retentions for Justice Bridget Hill (YES 1,977 / NO 440), Justice Robert C. Jarosh "
        "(YES 1,944 / NO 470), and Chancery Judge Ben Burningham (YES 1,979 / NO 413) are those statewide retentions. "
        "Local rows are 5th Judicial District judges (Park, Big Horn, Hot Springs, and Washakie). Full names and term "
        "dates follow official Wyoming Judicial Branch 5th JD pages and the official March 2026 roster already used "
        "in the Park history. Official Washakie named retentions are cited (2024 Bill Simpson YES 2,817 / NO 493, "
        "S. Joseph Joey Darrah YES 2,750 / NO 507, Edward G. Luhm YES 2,911 / NO 529; 2026 Bobbi Overfield YES 2,038 / NO 479)."
    )
    coverage = H.write_terms_and_snapshots(
        county="Washakie", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Washakie", slug=SLUG)
    print("copied shared terms", copied, "coverage", coverage)
    return people, terms, coverage


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
    cur = [t for t in terms if t["office"] == office and t["term_start"] <= as_of < t["term_end"]]
    elects = [t for t in terms if t["office"] == office and t["term_start"] == elect_start]
    seen = set()
    out = []
    current_ids = {t["person_id"] for t in cur}

    def te(t):
        if t["term_end"][5:7] == "05" or t["term_end"][5:7] == "06":
            return "May " + t["term_end"][:4]
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
    for e in elects:
        if e["person_id"] in seen:
            continue
        h = _holder(people, e["person_id"], e["name"], e.get("party") or "", te(e), e.get("notes") or "")
        h["notes"] = ((h.get("notes") or "") + " Takes office January 2027.").strip()
        out.append(h)
        seen.add(e["person_id"])
    return out

def update_washakie_json(people, terms):
    path = ROOT / "data" / "county_officials" / "washakie.json"
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
    senate = [
        _office("Senate District 20 (S20)",
                _holders_for_office(terms, people, "Senate District 20 (S20)"),
                note="Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Washakie share 3,442. Also covers Big Horn, Hot Springs, Fremont, and Park. Off-cycle in 2026."),
    ]
    house = [
        _office("House District 27 (H27)",
                _holders_for_office(terms, people, "House District 27 (H27)"),
                note="Official 2026 SOS statewide House summary, House District 27: Martha Lawley (R) 2,700, Theresa Livingston (D) 490. Official Washakie share Lawley 2,282, Livingston 430. Also covers Big Horn."),
    ]
    assessor_h = _holders_for_office(terms, people, "County Assessor")
    if not any(h.get("name") == "Not yet collected" for h in assessor_h):
        assessor_h = [{"name": "Not yet collected", "party": "", "term_end": ""}] + assessor_h
    county = [
        _office("County Commissioner",
                _holders_for_office(terms, people, "County Commissioner"),
                layout="heading-then-names",
                note="Three-member board. Official commissioners page lists Tom Schmeltzer, Terry Wolf, and Morgan Martinez (Chairman). Official 2026 general Vote For 2 re-elected Terrence D. Wolf and Morgan Martinez (take office January 2027). Display name Terrence D. Wolf follows the official 2026 ballot; official page alias Terry Wolf."),
        _office("County Clerk", _holders_for_office(terms, people, "County Clerk")),
        _office("County Treasurer", _holders_for_office(terms, people, "County Treasurer")),
        _office("County Assessor", assessor_h,
                note="Official 2026 general elect Bobby Swalstad (2,415) takes office January 2027. Official assessor page contact block does not name the current assessor; that holder is not yet collected from an official source."),
        _office("County Sheriff", _holders_for_office(terms, people, "County Sheriff")),
        _office("County Attorney", _holders_for_office(terms, people, "County Attorney")),
        _office("Clerk of District Court", _holders_for_office(terms, people, "Clerk of District Court"),
                note="Official spelling Mirian Hansen (not Miriam)."),
        _office("County Coroner", _holders_for_office(terms, people, "County Coroner"),
                note="Official 2026 ballot Jeffrey D. Lapp; official coroner page Jeff Lapp."),
    ]
    municipal = [
        _office("Worland Mayor", _holders_for_office(terms, people, "Worland Mayor"),
                note="Official city bio: Rebecca George was elected as Mayor of the City of Worland on November 5, 2024. Official 2024 precinct-sum totals: George 1,373, Jim Gill 764."),
        _office("Worland Council Ward 1", _holders_for_office(terms, people, "Worland Council Ward 1"),
                layout="heading-then-names",
                note="Official current council (Mayor and Council people API): Barbara Brookwell, Bill Glanz, Adam Martinez. Official 2026 Vote For 2 re-elected Barbara Brookwell and Adam G. Martinez."),
        _office("Worland Council Ward 2", _holders_for_office(terms, people, "Worland Council Ward 2"),
                layout="heading-then-names",
                note="Official current council: Wendy Fredricks, Mandy Horath, Sheryl Ley. Official 2026 Vote For 1 re-elected Sheryl Ley."),
        _office("Worland Council Ward 3", _holders_for_office(terms, people, "Worland Council Ward 3"),
                layout="heading-then-names",
                note="Official current council: Jacque Pike, Mike Neufer, William Worley. Official 2026 Vote For 2 elected Jacqueline Pike and Darr Lea Walker. The departing current member is not identified on an official source and is not invented. Darr Lea Walker takes office January 2027."),
        _office("Ten Sleep Mayor", _holders_for_office(terms, people, "Ten Sleep Mayor"),
                note="Official Town of Ten Sleep January 6 and October 6, 2026 council minutes name Mayor Ernie Beckley. Official town pages do not print a roster. Ten Sleep mayor/council races do not appear on the official November county general 2016-2026."),
        _office("Ten Sleep Council", _holders_for_office(terms, people, "Ten Sleep Council"),
                layout="heading-then-names",
                note="Official January 6, 2026 minutes: councilpersons Bart DeWitt, Connie Sweeney, and Amy Truman. Official October 6, 2026 minutes also list Councilwoman Lynema (Nichole Lynema) via Zoom."),
    ]
    schools = [
        _office("Washakie County School District #1 Trustee",
                _holders_for_office(terms, people, "Washakie County School District #1 Trustee"),
                layout="heading-then-names",
                note="Official 2024 Vote For 3 (precinct sum): David R. Tommerup, Brett Argeris, Becky Dooley. Official 2026 Vote For 4 elects Kathy Mercado, Jonathan Hake, Terri Logan, and Jaime Mertz, taking office January 2027. Official 2022 clerk file is unofficial; 2022-class members are not yet collected."),
        _office("Washakie County School District #2 Trustee",
                _holders_for_office(terms, people, "Washakie County School District #2 Trustee"),
                layout="heading-then-names",
                note="Official 2024 Vote For 3 (Ten Sleep precinct): Jared Lyman, Erin K. Blutt, Shana Harstad. Official 2026 Vote For 2 elects Bill Murphy and Bryony A. Lester, taking office January 2027."),
    ]
    specials = [
        _office("Worland Fire Protection District Director",
                _holders_for_office(terms, people, "Worland Fire Protection District Director"),
                layout="heading-then-names",
                note="Official 2024 Vote For 3 (precinct sum): Kent Lombard, Tad E. Debolt, Tim Surat. Official 2026 Vote For 2 elects Lance M. Berryman and Ray Witt, taking office January 2027."),
        _office("Washakie County Conservation District Supervisor At-Large",
                _holders_for_office(terms, people, "Washakie County Conservation District Supervisor At-Large"),
                layout="heading-then-names",
                note="Official 2024 Vote For 2 (precinct sum; contest title not split rural/urban): Andrew Mills 2,524, Susan D. Pennington 2,465."),
        _office("Washakie County Conservation District Supervisor Rural",
                _holders_for_office(terms, people, "Washakie County Conservation District Supervisor Rural"),
                layout="heading-then-names",
                note="Official 2026 Rural Vote For 2: Charley Orchard 2,361; the second seat is write-in-only (85 write-ins) with no named certified winner and is not filled. Official 2022 clerk file is unofficial."),
        _office("Washakie County Conservation District Supervisor Urban",
                _holders_for_office(terms, people, "Washakie County Conservation District Supervisor Urban"),
                note="Official 2026 Urban Vote For 1 is write-in-only (Write-In Totals 206, 100.00 percent, undervotes 2,613) with no named candidate; no winner is seated. Official 2022 clerk file is unofficial."),
        _office("Ten Sleep Cemetery District Trustee",
                _holders_for_office(terms, people, "Ten Sleep Cemetery District Trustee"),
                layout="heading-then-names",
                note="Official 2026 Vote For 3: Lara Gertsch 291, Terril J. Mills 281; the third seat is write-in-only (15 write-ins) and is not filled."),
        _office("Ten Sleep Fire Protection District Trustee",
                _holders_for_office(terms, people, "Ten Sleep Fire Protection District Trustee"),
                note="Official 2026 page 8 (Ten Sleep Senior Center 3-1): Daniel Greet 224, write-ins 2, 251 ballots. Treated as the whole-district result because only that official precinct is reported (medium). Takes office January 2027."),
    ]
    judicial = [
        _office("District Judge, 5th Judicial District (Park)",
                _holders_for_office(terms, people, "District Judge, 5th Judicial District (Park)"),
                note="Official 2024 Washakie retention, precinct sum: RETAIN JUDGE BILL SIMPSON YES 2,817 / NO 493."),
        _office("District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
                _holders_for_office(terms, people, "District Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)"),
                note="Official 2026 Washakie retention: RETAIN JUDGE BOBBI OVERFIELD YES 2,038 / NO 479."),
        _office("Circuit Judge, 5th Judicial District (Park)",
                _holders_for_office(terms, people, "Circuit Judge, 5th Judicial District (Park)"),
                note="Official 2024 Washakie retention, precinct sum: RETAIN JUDGE S. JOSEPH JOEY DARRAH YES 2,750 / NO 507."),
        _office("Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)",
                _holders_for_office(terms, people, "Circuit Judge, 5th Judicial District (Big Horn / Hot Springs / Washakie)"),
                note="Official 2024 Washakie retention, precinct sum: RETAIN JUDGE EDWARD G. LUHM YES 2,911 / NO 529."),
    ]
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
                rec["holders"] = [{"name": "Not yet collected", "party": "", "term_end": ""}]
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_C26,
        "primary_results": URL_P26,
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/washakie/SOURCES.md",
    }
    apply_to_groups(data["groups"], 'washakie')
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
