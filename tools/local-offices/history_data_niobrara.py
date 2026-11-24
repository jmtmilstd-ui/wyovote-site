#!/usr/bin/env python3
"""Niobrara County officeholder history (preview). Official clerk, SOS, court,
and town sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 14
SLUG = "niobrara"

URL_ELECTIONS = "https://www.niobraracounty.org/_departments/_county_clerk/ElectionResults.asp"
URL_PAST = "https://www.niobraracounty.org/_departments/_county_clerk/Pastelectionresults.asp"
URL_CLERK = "https://www.niobraracounty.org/_departments/_county_clerk/"
URL_COMM = "https://www.niobraracounty.org/_departments/_commissioners/index.asp"
URL_ASSESSOR = "https://www.niobraracounty.org/_departments/_assessor/index.asp"
URL_ATTORNEY = "https://www.niobraracounty.org/_departments/_county_attorney/index.asp"
URL_CDC = "https://www.niobraracounty.org/_departments/_clerk_of_the_district_court/index.asp"
URL_CORONER = "https://www.niobraracounty.org/_departments/_coroner/index.asp"
URL_TREASURER = "https://www.niobraracounty.org/_departments/_treasurer/index.asp"
URL_SHERIFF = "https://niobrarasheriff.org/"
URL_MANVILLE = "https://townofmanville.com/about"
URL_C26 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2026/County-General%20Election%20Summary%20.pdf"
URL_P26 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2026/OFFICIAL%20PRIMARY%20ELECTION%20SUMMARY.pdf"
URL_C24 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2024/Official%20Results-%20Niobrara%20County%20General%20Election%20Summary.pdf"
URL_C24_NCSD = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2024/NCSD%20OFFICIAL%20RESULTS%20SPREADSHEET.pdf"
URL_C22 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2022/General%20Election%20Summary%20Official.pdf"
URL_C20 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2020/General%20Election%20Summary%20Report.pdf"
URL_C18 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2021/EL45%20OFFICIAL.pdf"
URL_C16 = "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2016/EL45_1.pdf"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-8th-judicial-district/"


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


SRC_C16 = S("Official Niobrara County 2016 general (header OFFICIAL RESULTS, November 8, 2016, run 11/10/16 12:25 PM, 1,331 ballots, 6 of 6 precincts)", URL_C16)
SRC_C18 = S("Official Niobrara County 2018 general (header OFFICIAL RESULTS, November 6, 2018, run 11/09/18 09:35 AM, 1,184 ballots, 6 of 6 precincts). The election-night EL45 6-of-6 file is unofficial and is not used as a canvass.", URL_C18)
SRC_C20 = S("Official Niobrara County 2020 general (header OFFICIAL RESULTS, November 3, 2020, Election Summary 11/06/2020 8:05 AM, 1,322 ballots, 6 of 6 precincts). Official PDF is a scan; totals read from official rendered pages.", URL_C20)
SRC_C22 = S("Official Niobrara County 2022 general (header OFFICIAL RESULTS, November 8, 2022, General Election Summary 11/10/2022 3:19 PM, 1,101 ballots, 6 of 6 precincts)", URL_C22)
SRC_C24 = S("Official Niobrara County 2024 general (header OFFICIAL RESULTS, November 5, 2024, Niobrara County General Election Summary 11/08/2024 11:30 AM, 1,244 ballots, 6 of 6 precincts)", URL_C24)
SRC_C24_NCSD = S("Official 2024 Niobrara County School District #1 trustees spreadsheet combining official Niobrara and official Goshen results", URL_C24_NCSD)
SRC_C26 = S("Official Niobrara County 2026 general (header OFFICIAL RESULTS, November 3, 2026, County General Election Summary 11/06/2026 12:39 PM, 948 ballots, 6 of 6 precincts)", URL_C26)
SRC_P26 = S("Official Niobrara County 2026 primary official summary", URL_P26)
SRC_COMM = S("Official Niobrara County Commissioners page, retrieved 2026-11-24", URL_COMM)
SRC_CLERK = S("Official Niobrara County Clerk page, retrieved 2026-11-24", URL_CLERK)
SRC_TREAS = S("Official Niobrara County Treasurer page, retrieved 2026-11-24", URL_TREASURER)
SRC_ASSESSOR = S("Official Niobrara County Assessor page, retrieved 2026-11-24", URL_ASSESSOR)
SRC_ATTORNEY = S("Official Niobrara County Attorney page, retrieved 2026-11-24", URL_ATTORNEY)
SRC_CDC = S("Official Niobrara County Clerk of District Court page, retrieved 2026-11-24", URL_CDC)
SRC_CORONER = S("Official Niobrara County Coroner page, retrieved 2026-11-24", URL_CORONER)
SRC_SHERIFF = S("Official Niobrara County Sheriff page, retrieved 2026-11-24", URL_SHERIFF)
SRC_MANVILLE = S("Official Town of Manville About / Meet the Board page, retrieved 2026-11-24", URL_MANVILLE)
URL_LUSK = "https://townofluskwy.gov/"
URL_LUSK_MAYOR = "https://townofluskwy.gov/mayor"
URL_LUSK_COUNCIL = "https://townofluskwy.gov/town-council"
SRC_LUSK_MAYOR = S("Official Town of Lusk mayor page (townofluskwy.gov/mayor), retrieved 2026-11-24", URL_LUSK_MAYOR)
SRC_LUSK_COUNCIL = S("Official Town of Lusk town council page (townofluskwy.gov/town-council), retrieved 2026-11-24", URL_LUSK_COUNCIL)
SRC_LUSK_M26_0602 = S("Official Town of Lusk regular council minutes, June 2, 2026 (official swearing of Mayor Douglas E. Lytle and council members Ty Thompson, Chantry Filener, and Thomas Dooper)", "https://townofluskwy.gov/town-council")
SRC_LUSK_M26_1006 = S("Official Town of Lusk regular council minutes, October 6, 2026 (appointment and oath of Neil Holmes to a vacant council seat)", "https://townofluskwy.gov/town-council")
SRC_LUSK_M26_1103 = S("Official Town of Lusk regular council minutes, November 3, 2026", "https://townofluskwy.gov/town-council")
SRC_LUSK_WB23 = S("Official Town of Lusk website capture, Wayback Machine 2023-10-14 (www.townoflusk.org, last updated 10/9/2023): Mayor Douglas E. Lytle; Councilmen Thomas Dooper, R. Dean Nelson, Chantry Filener, and Adam Dickson. Used as historical official roster only, not as the current 2026 roster.", "https://web.archive.org/web/20231014000509/https://www.townoflusk.org/")

SRC_COURT = S("Official Wyoming Judicial Branch 8th Judicial District pages and official March 2026 roster (same official sources already used in the Goshen and Platte histories)", URL_COURT_D)
SRC_SOS12H = sos_src(2012, "House")
SRC_SOS14S, SRC_SOS14H = sos_src(2014, "Senate"), sos_src(2014, "House")
SRC_SOS16H = sos_src(2016, "House")
SRC_SOS18S, SRC_SOS18H = sos_src(2018, "Senate"), sos_src(2018, "House")
SRC_SOS20H = sos_src(2020, "House")
SRC_SOS22S, SRC_SOS22H = sos_src(2022, "Senate"), sos_src(2022, "House")
SRC_SOS24H = sos_src(2024, "House")
SRC_SOS26S, SRC_SOS26H = sos_src(2026, "Senate"), sos_src(2026, "House")

def register_people(P):
    P("WY-MEIER-CURTIS", "Curt Meier", "Curt", "Meier", aliases="Curtis E Meier JR; Curt Meier")
    P("WY-STEINMETZ-CHERI", "Cheri E. Steinmetz", "Cheri", "Steinmetz", middle="E.",
      aliases="Cheri Steinmetz; CHERI E STEINMETZ")
    P("WY-HUNT-HANS", "Hans Hunt", "Hans", "Hunt")
    P("WY-SLAGLE-ALLEN", "Allen Slagle", "Allen", "Slagle", aliases="Allen Earl Slagle; ALLEN EARL SLAGLE; Allen E. Slagle")
    P("WY-WILLIAMS-JD", "JD Williams", "JD", "Williams", aliases="REP JD WILLIAMS")
    P("WY-MIDKIFF-JOHN-P", "John P. Midkiff", "John", "Midkiff", middle="P.", aliases="John Midkiff; JOHN MIDKIFF")
    P("WY-GRIFFITH-ELAINE-B", "Elaine B. Griffith", "Elaine", "Griffith", middle="B.",
      aliases="Elaine Griffith; ELAINE GRIFFITH")
    P("WY-WADE-PATRICK-H", "Patrick H. Wade", "Patrick", "Wade", middle="H.",
      aliases="Patrick Wade; PATRICK WADE")
    P("WY-HANSON-JEB", "Jeb Hanson", "Jeb", "Hanson")
    P("WY-BAARS-KEVIN-H", "Kevin H. Baars", "Kevin", "Baars", middle="H.")
    P("WY-THURSTON-TIFFANY", "Tiffany Thurston", "Tiffany", "Thurston")
    P("WY-FREEMAN-BECKY-L", "Becky L. Freeman", "Becky", "Freeman", middle="L.", aliases="Becky Freeman")
    P("WY-THOMPSON-KERI", "Keri Thompson", "Keri", "Thompson")
    P("WY-STEPHENS-TERI", "Teri Stephens", "Teri", "Stephens")
    P("WY-HIMES-LORI-A", "Lori A. Himes", "Lori", "Himes", middle="A.", aliases="Lori Himes; LORI HIMES")
    P("WY-GILL-CARY", "Cary Gill", "Cary", "Gill")
    P("WY-STARKEY-RANDY", "Randy Starkey", "Randy", "Starkey")
    P("WY-WASSERBURGER-ANNE-K", "Anne K. Wasserburger", "Anne", "Wasserburger", middle="K.",
      aliases="Anne Wasserburger")
    P("WY-LUND-CHRISANNA-K", "Chrisanna Lund", "Chrisanna", "Lund", aliases="Chrisanna K. Lund; CHRISANNA K. LUND")
    P("WY-SMITH-AMBER", "Amber Smith", "Amber", "Smith")
    P("WY-PIER-PETER-W", "Peter W. Pier", "Peter", "Pier", middle="W.", aliases="Pete Pier; PETER W. PIER")
    P("WY-KORELL-PATRICK-W", "Patrick W. Korell", "Patrick", "Korell", middle="W.")
    P("WY-PEASLEY-F-SCOTT", "F. Scott Peasley", "F. Scott", "Peasley")
    P("WY-BUCHANAN-EDWARD-A", "Edward A. Buchanan", "Edward", "Buchanan", middle="A.",
      aliases="A Edward A Buchanan; A. Edward A. Buchanan")
    P("WY-ALLAN-CLARK-C", "Clark C. Allan", "Clark", "Allan", middle="C.")
    P("WY-HIBBEN-NATHANIEL-S", "Nathaniel S. Hibben", "Nathaniel", "Hibben", middle="S.",
      aliases="Nathaniel Scott Hibben; HIBBEN")
    P("WY-BROWN-JACQUELINE-K", "Jacqueline K. Brown", "Jacqueline", "Brown", middle="K.")
    P("WY-ARP-RANDAL-R", "Randal R. Arp", "Randal", "Arp", middle="R.")
    P("WY-LYTLE-DOUGLAS-E", "Douglas E. Lytle", "Douglas", "Lytle", middle="E.", aliases="Douglas Lytle; Mayor Douglas E. Lytle")
    P("WY-DOOPER-THOMAS", "Thomas Dooper", "Thomas", "Dooper", aliases="Thomas Dooper, Mayor Pro Tempore")
    P("WY-FILENER-CHANTRY", "Chantry Filener", "Chantry", "Filener")
    P("WY-THOMPSON-TY", "Ty Thompson", "Ty", "Thompson")
    P("WY-HOLMES-NEIL", "Neil Holmes", "Neil", "Holmes", aliases="Niel Holmes")
    P("WY-LADWIG-RICHARD", "Richard Ladwig", "Richard", "Ladwig")
    P("WY-ADAMS-DARLENE", "Darlene Adams", "Darlene", "Adams")
    P("WY-KRIEGER-WALT-FRED", "Walt (Fred) Krieger", "Walt", "Krieger", aliases="Fred Krieger")
    P("WY-SIDES-CHUCK", "Chuck Sides", "Chuck", "Sides")
    P("WY-SIDES-SEAN", "Sean Sides", "Sean", "Sides")
    P("WY-ASHURST-LEXIE", "Lexie Ashurst", "Lexie", "Ashurst")
    P("WY-SAMPERS-SARA", "Sara Sampers", "Sara", "Sampers")
    P("WY-PISCHEL-LISA", "Lisa Pischel", "Lisa", "Pischel")
    P("WY-BARNETTE-TAYLOR", "Taylor Barnette", "Taylor", "Barnette", aliases="Taylor Barnette")
    P("WY-NELSON-JEREMY", "Jeremy Nelson", "Jeremy", "Nelson")
    P("WY-LUND-CHERYL", "Cheryl Lund", "Cheryl", "Lund")
    P("WY-VETTER-WESLEY", "Wesley Vetter", "Wesley", "Vetter")
    P("WY-KRUSE-KATIE", "Katie Kruse", "Katie", "Kruse")
    P("WY-MILLER-JEFF", "Jeff Miller", "Jeff", "Miller")
    P("WY-HETH-LOREN", "Loren Heth", "Loren", "Heth")
    P("WY-BOLDON-SHEILA", "Sheila Boldon", "Sheila", "Boldon")
    P("WY-BROWN-HILLARY", "Hillary Brown", "Hillary", "Brown")
    P("WY-MATTHEWS-LELEUX-DESIRAE", "Desirae Matthews-Leleux", "Desirae", "Matthews-Leleux")
    P("WY-VOLK-CONNIE", "Connie Volk", "Connie", "Volk")
    P("WY-HANSON-DAN-H", "Dan H. Hanson", "Dan", "Hanson", middle="H.", aliases="Dan Henry Hanson")
    P("WY-KREIN-TRAVIS", "Travis Krein", "Travis", "Krein")
    P("WY-GAUKEL-KEVIN-L", "Kevin L. Gaukel", "Kevin", "Gaukel", middle="L.")
    P("WY-KILMER-BRUCE", "Bruce Kilmer", "Bruce", "Kilmer")
    P("WY-PULLIS-LEONARD-O", "Leonard O. Pullis", "Leonard", "Pullis", middle="O.")
    P("WY-NELSON-ROD-A", "Rod A. Nelson", "Rod", "Nelson", middle="A.")
    P("WY-BRUEGGER-BRADYN-J", "Bradyn J. Bruegger", "Bradyn", "Bruegger", middle="J.")
    P("WY-KREMERS-JUSTIN", "Justin Kremers", "Justin", "Kremers")
    P("WY-FOSHER-CORKY", "Corky Fosher", "Corky", "Fosher")
    P("WY-THURSTON-COLBY-M", "Colby M. Thurston", "Colby", "Thurston", middle="M.", aliases="Colby Thurston")
    P("WY-MENG-JIM", "Jim Meng", "Jim", "Meng")
    P("WY-HAMMER-LOUIS", "Louis Hammer", "Louis", "Hammer")
    P("WY-LARSON-MARYLOU", "Marylou Larson", "Marylou", "Larson")
    P("WY-BAKER-CONNIE", "Connie Baker", "Connie", "Baker")
    P("WY-HAHN-PHYLLIS", "Phyllis Hahn", "Phyllis", "Hahn")
    P("WY-KREMERS-JIM", "Jim Kremers", "Jim", "Kremers")


def legislature_terms():
    terms = []
    terms += [
        T(person_id="WY-MEIER-CURTIS", name="Curt Meier", party="R", office_group="state-senate",
          office="Senate District 3 (S03)", term_start=FM[2015], term_end=FM[2019],
          election_year=2014, sources=[SRC_SOS14S],
          notes="Official 2014 SOS statewide Senate summary, Senate District 3: Curt Meier (R) Total 5,743. Official Niobrara share 931; official Goshen 3,579; official Weston 1,233 (931+3,579+1,233=5,743)."),
        T(person_id="WY-STEINMETZ-CHERI", name="Cheri E. Steinmetz", party="R", office_group="state-senate",
          office="Senate District 3 (S03)", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_SOS18S, SRC_C18],
          notes="Official 2018 SOS statewide Senate summary, Senate District 3 (right column beside Senate District 1; that district's Total is not used): Cheri E. Steinmetz (R) 5,721, Marci Shaver (D) 1,449. Official Niobrara share Steinmetz 1,001, Shaver 129; official Goshen 3,447-1,086; official Weston 1,273-234."),
        T(person_id="WY-STEINMETZ-CHERI", name="Cheri E. Steinmetz", party="R", office_group="state-senate",
          office="Senate District 3 (S03)", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_SOS22S, SRC_C22],
          notes="Official 2022 SOS statewide Senate summary, Senate District 3: Cheri Steinmetz (R) Total 6,352. Official Niobrara share 973; official Goshen 4,017; official Weston 1,362."),
        T(person_id="WY-STEINMETZ-CHERI", name="Cheri E. Steinmetz", party="R", office_group="state-senate",
          office="Senate District 3 (S03)", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_SOS26S, SRC_C26],
          notes="Official 2026 SOS statewide Senate summary, Senate District 3: Cheri E. Steinmetz (R) Total 5,792. Official Niobrara share 808 (official 2026 clerk 808); official Goshen 3,777; official Weston 1,207 (808+3,777+1,207=5,792)."),
    ]
    terms += [
        T(person_id="WY-HUNT-HANS", name="Hans Hunt", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2013], term_end=FM[2015],
          election_year=2012, sources=[SRC_SOS12H],
          notes="Official 2012 SOS statewide House summary, House District 2: Hans Hunt (R) Total 3,966. Official Niobrara share 1,187; official Goshen 940; official Weston 1,839."),
        T(person_id="WY-HUNT-HANS", name="Hans Hunt", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2015], term_end=FM[2017],
          election_year=2014, sources=[SRC_SOS14H],
          notes="Official 2014 SOS statewide House summary, House District 2: Hans Hunt (R) Total 2,985. Official Niobrara share 971; official Goshen 718; official Weston 1,296."),
        T(person_id="WY-HUNT-HANS", name="Hans Hunt", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2017], term_end=FM[2019],
          election_year=2016, sources=[SRC_SOS16H, SRC_C16],
          notes="Official 2016 SOS statewide House summary, House District 2 (right column beside House District 1; that district's Total is not used): Hans Hunt (R) 3,863, Harold Eaton (D) 624. Official Niobrara share Hunt 1,191, Eaton 104; official Goshen 880-262; official Weston 1,792-258."),
        T(person_id="WY-HUNT-HANS", name="Hans Hunt", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_SOS18H, SRC_C18],
          notes="Official 2018 SOS statewide House summary, House District 2 (right column beside House District 1; that district's Total is not used): Hans Hunt (R) Total 3,261. Official Niobrara share 1,101; official Goshen 846; official Weston 1,314."),
        T(person_id="WY-HUNT-HANS", name="Hans Hunt", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20H, SRC_C20],
          notes="Official 2020 SOS statewide House summary, House District 2: Hans Hunt (R) Total 4,121. Official Niobrara share 1,226 (official 2020 clerk 1,226); official Goshen 1,106; official Weston 1,789."),
        T(person_id="WY-SLAGLE-ALLEN", name="Allen Slagle", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_SOS22H, SRC_C22],
          notes="Official 2022 SOS statewide House summary, House District 2: Allen Slagle (R) Total 2,927. Official Niobrara share 670 (official 2022 clerk ALLEN EARL SLAGLE 670, write-ins 347); official Goshen 932; official Weston 1,325."),
        T(person_id="WY-WILLIAMS-JD", name="JD Williams", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2025], term_end=FM[2027],
          election_year=2024, sources=[SRC_SOS24H, SRC_C24],
          notes="Official 2024 SOS statewide House summary, House District 2: JD Williams (R) Total 3,834. Official Niobrara share 1,047 (official 2024 clerk 1,047); official Goshen 1,125; official Weston 1,662."),
        T(person_id="WY-WILLIAMS-JD", name="JD Williams", party="R", office_group="state-house",
          office="House District 2 (H02)", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_SOS26H, SRC_C26],
          notes="Official 2026 SOS statewide House summary, House District 2: JD Williams (R) Total 2,850. Official Niobrara share 803 (official 2026 clerk 803); official Goshen 839; official Weston 1,208."),
    ]
    return terms


def county_terms():
    terms = []
    terms += [
        T(person_id="WY-MIDKIFF-JOHN-P", name="John P. Midkiff", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_C16],
          notes="Official 2016 general County Commissioner Vote For 1: John Midkiff (R) 990, Dustin Cushman (D) 274."),
        T(person_id="WY-GRIFFITH-ELAINE-B", name="Elaine B. Griffith", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_C18],
          notes="Official 2018 general County Commissioner Vote For 2: Patrick Wade (R) 936, Elaine Griffith (R) 886. Official commissioners page lists Elaine B. Griffith, Vice Chairman."),
        T(person_id="WY-WADE-PATRICK-H", name="Patrick H. Wade", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_C18],
          notes="Official 2018 general County Commissioner Vote For 2: Patrick Wade (R) 936. Official commissioners page lists Patrick H. Wade, Chairman."),
        T(person_id="WY-MIDKIFF-JOHN-P", name="John P. Midkiff", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_C20],
          notes="Official 2020 general County Commissioner Vote For 1: John P. Midkiff (R) 1,145."),
        T(person_id="WY-GRIFFITH-ELAINE-B", name="Elaine B. Griffith", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_COMM],
          notes="Official 2022 general County Commissioner Vote For 2: Patrick Wade (R) 930, Elaine Griffith (R) 875. Official 2026 Vote For 2 elects successors taking office January 2027."),
        T(person_id="WY-WADE-PATRICK-H", name="Patrick H. Wade", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_COMM],
          notes="Official 2022 general County Commissioner Vote For 2: Patrick Wade (R) 930."),
        T(person_id="WY-HANSON-JEB", name="Jeb Hanson", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_COMM],
          notes="Official 2024 general County Commissioner Vote For 1: Jeb Hanson (R) 1,115. Official commissioners page lists Jeb Hanson as a current commissioner."),
        T(person_id="WY-THURSTON-TIFFANY", name="Tiffany Thurston", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 general County Commissioner Vote For 2: Tiffany Thurston 787, Kevin H. Baars 685, write-ins 70."),
        T(person_id="WY-BAARS-KEVIN-H", name="Kevin H. Baars", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 general County Commissioner Vote For 2: Kevin H. Baars 685."),
    ]
    def row(pid, name, office, start, end, year, sources, notes, conf="high"):
        terms.append(T(person_id=pid, name=name, party="R", office_group="county", office=office,
                       term_start=start, term_end=end, election_year=year, sources=sources,
                       notes=notes, confidence=conf))
    row("WY-FREEMAN-BECKY-L", "Becky L. Freeman", "County Clerk", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Clerk: Becky L. Freeman (R) 1,101.")
    row("WY-THOMPSON-KERI", "Keri Thompson", "County Treasurer", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Treasurer: Keri Thompson (R) 1,101.")
    row("WY-STEPHENS-TERI", "Teri Stephens", "County Assessor", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Assessor: Teri Stephens (R) 1,093.")
    row("WY-GILL-CARY", "Cary Gill", "County Sheriff", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general Sheriff: Cary Gill (R) 1,024.")
    row("WY-WASSERBURGER-ANNE-K", "Anne K. Wasserburger", "County Attorney", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Attorney: Anne Wasserburger (R) 1,043.")
    row("WY-LUND-CHRISANNA-K", "Chrisanna Lund", "Clerk of District Court", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general Clerk of District Court: Chrisanna K. Lund (R) 818.")
    row("WY-PIER-PETER-W", "Peter W. Pier", "County Coroner", FM[2019], FM[2023], 2018,
        [SRC_C18], "Official 2018 general County Coroner: Peter W. Pier (R) 1,070. Official coroner page lists Pete Pier.")
    row("WY-FREEMAN-BECKY-L", "Becky L. Freeman", "County Clerk", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_CLERK], "Official 2022 general County Clerk: Becky L. Freeman (R) 1,031. Official clerk page names Becky Freeman.")
    row("WY-THOMPSON-KERI", "Keri Thompson", "County Treasurer", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_TREAS], "Official 2022 general County Treasurer: Keri Thompson (R) 1,030. Official treasurer page names Keri Thompson.")
    row("WY-STEPHENS-TERI", "Teri Stephens", "County Assessor", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_ASSESSOR], "Official 2022 general County Assessor: Teri Stephens (R) 1,009. Official assessor page names TERI STEPHENS. Official 2026 elect Lori A. Himes takes office January 2027.")
    row("WY-STARKEY-RANDY", "Randy Starkey", "County Sheriff", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_SHERIFF], "Official 2022 general County Sheriff: Randy Starkey (R) 1,030. Official sheriff page names Sheriff Randy Starkey.")
    row("WY-WASSERBURGER-ANNE-K", "Anne K. Wasserburger", "County Attorney", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_ATTORNEY], "Official 2022 general County Attorney: Anne K. Wasserburger (R) 910. Official attorney page names Anne Wasserburger.")
    row("WY-LUND-CHRISANNA-K", "Chrisanna Lund", "Clerk of District Court", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_CDC], "Official 2022 general Clerk of Court: Chrisanna Lund (R) 1,032. Official CDC page names Chrisanna Lund. Official 2026 elect Amber Smith takes office January 2027.")
    row("WY-PIER-PETER-W", "Peter W. Pier", "County Coroner", FM[2023], FM[2027], 2022,
        [SRC_C22, SRC_CORONER], "Official 2022 general County Coroner: Peter W. Pier (R) 1,035.")
    row("WY-FREEMAN-BECKY-L", "Becky L. Freeman", "County Clerk", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Clerk: Becky L. Freeman 886.")
    row("WY-THOMPSON-KERI", "Keri Thompson", "County Treasurer", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Treasurer: Keri Thompson 886.")
    row("WY-HIMES-LORI-A", "Lori A. Himes", "County Assessor", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Assessor elect: Lori A. Himes 819.")
    row("WY-STARKEY-RANDY", "Randy Starkey", "County Sheriff", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Sheriff: Randy Starkey 886.")
    row("WY-WASSERBURGER-ANNE-K", "Anne K. Wasserburger", "County Attorney", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Attorney: Anne K. Wasserburger 758.")
    row("WY-SMITH-AMBER", "Amber Smith", "Clerk of District Court", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general Clerk of Court elect: Amber Smith 881.")
    row("WY-PIER-PETER-W", "Peter W. Pier", "County Coroner", FM[2027], FM[2031], 2026,
        [SRC_C26], "Official 2026 general County Coroner: Peter W. Pier 897.")
    return terms

def judicial_terms():
    # Same official 8th JD term dates as the Goshen / Platte histories (official court pages).
    terms = [
        T(person_id="WY-KORELL-PATRICK-W", name="Patrick W. Korell", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2015-10-01", term_end="2022-09-01",
          election_year=2016, how_took_office="appointed", confidence="medium",
          sources=[SRC_C16, SRC_COURT],
          notes="Official Wyoming Judicial Branch Eighth Judicial District: Judge A Patrick W. Korell, appointed October 2015. Official 2016 Niobrara clerk RETAIN PATRICK W. KORELL YES 883 / NO 259. Official current 8th JD pages list Edward A. Buchanan, appointed September 2022, in that district; Korell's last day is taken as the first of Buchanan's official appointment month (medium), same dating already used in the official Goshen history. Start day is the first of the official appointment month."),
        T(person_id="WY-PEASLEY-F-SCOTT", name="F. Scott Peasley", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2017-08-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT, SRC_C18, SRC_C24],
          notes="Official 8th JD District Court page: Hon. F. Scott Peasley, appointed August 2017, retained November 2024, term expires January 2031. Official 2018 Niobrara clerk RETAIN JUDGE F. SCOTT PEASLEY YES 816 / NO 176. Official 2024 Niobrara clerk RETAIN DIST. JUDGE BF. SCOTT PEASLEY YES 838 / NO 222. Start day is the first of the official appointment month."),
        T(person_id="WY-BUCHANAN-EDWARD-A", name="Edward A. Buchanan", party="", office_group="judicial",
          office="District Judge, 8th Judicial District", term_start="2022-09-01", term_end=FM[2031],
          election_year=2024, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT, SRC_C24],
          notes="Official 8th JD District Court page: Hon. Edward A. Buchanan, appointed September 2022, retained November 2024, term expires January 2031. Official 2024 Niobrara clerk RETAIN DIST JUDGE A EDWARD A BUCHANAN YES 856 / NO 237. Start day is the first of the official appointment month."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2015], term_end=FM[2019],
          election_year=2014, sources=[SRC_COURT],
          notes="Official 2014 SOS General Election Winners Roster lists Eighth Judicial District Circuit Court Judge Randal R. Arp (same official source already used in the Goshen history). Official 2018 Niobrara clerk RETAIN JUDGE RANDAL R. ARP YES 797 / NO 191."),
        T(person_id="WY-ARP-RANDAL-R", name="Randal R. Arp", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_C18, SRC_COURT], confidence="medium",
          notes="Official 2018 Niobrara clerk RETAIN JUDGE RANDAL R. ARP YES 797 / NO 191. Official 2020 Niobrara clerk retains Nathaniel S. Hibben and does not name Arp; later official court pages do not list Arp. The exact official leaving date was not taken from an official court page, so this term is ended at January 2021 when the official 2020 Hibben retention is in effect (medium), same dating as the official Goshen history."),
        T(person_id="WY-HIBBEN-NATHANIEL-S", name="Nathaniel S. Hibben", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2021], term_end="2025-05-10",
          election_year=2020, sources=[SRC_C20, SRC_C24, SRC_COURT],
          notes="Official 2020 Niobrara clerk retains Circuit Court Judge 8th Judicial Hibben. Official 2024 Niobrara clerk RETAIN CIRCUIT COURT JUDGE NATHANIEL SCOTT HIBBEN YES 834 / NO 212. Full name Nathaniel S. Hibben is from the official Wyoming Judicial Branch pages already used in the Goshen history. Official Judicial Nominating Commission release announced the 8th JD Goshen circuit vacancy effective May 10, 2025."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2021-01-01", term_end=FM[2027],
          election_year=2022, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT, SRC_C22, SRC_C26],
          notes="Official 8th JD Converse (Douglas) Circuit Court page: Hon. Clark C. Allan, appointed January 2021, term expires January 2027, stands for retention November 2026. Official 2022 Niobrara clerk CIRCUIT COURT JUDGE 8TH JUDICIAL DISTRICT CLARK C. ALLAN YES 796 / NO 159. Official 2026 Niobrara clerk RETAIN CIRCUIT COURT JUDGE ALLAN YES 648 / NO 140. Start day is the first of the official appointment month."),
        T(person_id="WY-ALLAN-CLARK-C", name="Clark C. Allan", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT],
          notes="Official 2026 Niobrara clerk RETAIN CIRCUIT COURT JUDGE ALLAN YES 648 / NO 140."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start="2025-07-01", term_end=FM[2027],
          election_year=2026, how_took_office="appointed", confidence="medium",
          sources=[SRC_COURT, SRC_C26],
          notes="Official 8th JD Goshen (Torrington) Circuit Court page: Hon. Jacqueline K. Brown, appointed July 2025, term expires January 2027, stands for retention November 2026. Official 2026 Niobrara clerk RETAIN CIRCUIT COURT JUDGE BROWN YES 609 / NO 146. Official Judicial Branch robing notice lists her as Circuit Court Judge of the 8th JD (Converse, Goshen, Niobrara, and Platte Counties). Start day is the first of the official appointment month."),
        T(person_id="WY-BROWN-JACQUELINE-K", name="Jacqueline K. Brown", party="", office_group="judicial",
          office="Circuit Judge, 8th Judicial District", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_COURT],
          notes="Official 2026 Niobrara clerk RETAIN CIRCUIT COURT JUDGE BROWN YES 609 / NO 146."),
    ]
    return terms


def municipal_terms():
    # Official November county generals 2016-2026 do not list mayor or council races.
    # Current Manville board is from the official Town of Manville About page only.
    # Term start and end are not printed there, so these current terms are dated only
    # as in office on the official page retrieved 2026-11-24 (medium). They are not
    # projected backward into earlier January snapshots.
    note = (
        "Official Town of Manville About / Meet the Board page, retrieved 2026-11-24: "
        "Mayor Richard Ladwig; Vice Mayor Darlene Adams; Board Members Walt (Fred) Krieger, "
        "Chuck Sides, and Sean Sides. Clerk/Treasurer Rose Fadness is staff, not seated as an "
        "elected holder. Official November county general summaries 2016-2026 do not list "
        "municipal mayor or council contests. Official term dates were not found."
    )
    terms = [
        T(person_id="WY-LADWIG-RICHARD", name="Richard Ladwig", party="", office_group="municipal",
          office="Town of Manville Mayor", term_start="2026-01-01", term_end=FM[2027],
          election_year=None, how_took_office="unknown", confidence="medium",
          sources=[SRC_MANVILLE], notes=note),
        T(person_id="WY-ADAMS-DARLENE", name="Darlene Adams", party="", office_group="municipal",
          office="Town of Manville Council", term_start="2026-01-01", term_end=FM[2027],
          election_year=None, how_took_office="unknown", confidence="medium",
          sources=[SRC_MANVILLE], notes=note + " Official page lists Darlene Adams as Vice Mayor."),
        T(person_id="WY-KRIEGER-WALT-FRED", name="Walt (Fred) Krieger", party="", office_group="municipal",
          office="Town of Manville Council", term_start="2026-01-01", term_end=FM[2027],
          election_year=None, how_took_office="unknown", confidence="medium",
          sources=[SRC_MANVILLE], notes=note),
        T(person_id="WY-SIDES-CHUCK", name="Chuck Sides", party="", office_group="municipal",
          office="Town of Manville Council", term_start="2026-01-01", term_end=FM[2027],
          election_year=None, how_took_office="unknown", confidence="medium",
          sources=[SRC_MANVILLE], notes=note),
        T(person_id="WY-SIDES-SEAN", name="Sean Sides", party="", office_group="municipal",
          office="Town of Manville Council", term_start="2026-01-01", term_end=FM[2027],
          election_year=None, how_took_office="unknown", confidence="medium",
          sources=[SRC_MANVILLE], notes=note),
    ]
    # Official Town of Lusk (townofluskwy.gov), current as of official June 2, 2026 swearing
    # and official October 6 / November 3, 2026 minutes, plus official mayor and council pages
    # retrieved 2026-11-24. The older official townoflusk.org site is down; official 2023
    # Wayback captures named a prior council that is not used as the current roster.
    lusk_mayor_note = (
        "Official Town of Lusk mayor page, retrieved 2026-11-24, names Mayor Douglas E. Lytle "
        "(mayor@townofluskwy.gov) and still prints 'Elected: May, 2022' and 'Term: 4 years'. "
        "Official June 2, 2026 council minutes: 'The new council members (Ty Thompson, Chantry "
        "Filener, and Thomas Dooper) and the mayor (Douglas E. Lytle) were sworn in.' Official "
        "July 7, 2026 minutes still list Mayor Douglas Lytle, who called the meeting to order. "
        "Official August 4, September 1, October 6, and November 3, 2026 minutes were called to "
        "order and signed by Mayor Pro-Tempore Thomas Dooper, with Lytle not recorded present; "
        "no official resignation was found in those official minutes. Official term-end day after "
        "the June 2, 2026 swearing is not printed; a four-year mayoral term from that official "
        "swearing is taken through June 2030 (medium)."
    )
    terms += [
        T(person_id="WY-LYTLE-DOUGLAS-E", name="Douglas E. Lytle", party="", office_group="municipal",
          office="Town of Lusk Mayor", term_start="2022-05-01", term_end="2026-06-02",
          election_year=2022, how_took_office="elected", confidence="medium",
          sources=[SRC_LUSK_MAYOR, SRC_LUSK_WB23, SRC_LUSK_M26_0602],
          notes="Official mayor page: Elected May, 2022, term 4 years. Official 2023-10-14 Wayback capture of the official townoflusk.org homepage (last updated 10/9/2023) also names Mayor, Douglas E. Lytle. This prior term ends at the official June 2, 2026 swearing of the new term. Start day is the first of the official election month."),
        T(person_id="WY-LYTLE-DOUGLAS-E", name="Douglas E. Lytle", party="", office_group="municipal",
          office="Town of Lusk Mayor", term_start="2026-06-02", term_end="2030-06-02",
          election_year=2026, how_took_office="elected", confidence="medium",
          sources=[SRC_LUSK_M26_0602, SRC_LUSK_MAYOR, SRC_LUSK_M26_1103],
          notes=lusk_mayor_note),
        T(person_id="WY-DOOPER-THOMAS", name="Thomas Dooper", party="", office_group="municipal",
          office="Town of Lusk Council", term_start="2026-06-02", term_end="2030-06-02",
          election_year=2026, how_took_office="elected", confidence="medium",
          sources=[SRC_LUSK_M26_0602, SRC_LUSK_COUNCIL, SRC_LUSK_M26_1103],
          notes="Official June 2, 2026 minutes swear in Thomas Dooper as a new council member. Official council page, retrieved 2026-11-24, lists Councilman Thomas Dooper, Mayor Pro Tempore (the page still also prints Elected May, 2024, Term 2 years, which is the prior official term). Official November 3, 2026 minutes: Mayor Pro-Tempore Thomas Dooper called the meeting to order. Official term-end day after the June 2, 2026 swearing is not printed (medium)."),
        T(person_id="WY-FILENER-CHANTRY", name="Chantry Filener", party="", office_group="municipal",
          office="Town of Lusk Council", term_start="2026-06-02", term_end="2030-06-02",
          election_year=2026, how_took_office="elected", confidence="medium",
          sources=[SRC_LUSK_M26_0602, SRC_LUSK_COUNCIL, SRC_LUSK_M26_1103],
          notes="Official June 2, 2026 minutes swear in Chantry Filener as a new council member. Official council page, retrieved 2026-11-24, lists Councilman Chantry Filener (the page still also prints Elected May, 2022, Term 4 years). Official November 3, 2026 minutes list Council Member Chantry Filener. Official term-end day after the June 2, 2026 swearing is not printed (medium)."),
        T(person_id="WY-THOMPSON-TY", name="Ty Thompson", party="", office_group="municipal",
          office="Town of Lusk Council", term_start="2026-06-02", term_end="2030-06-02",
          election_year=2026, how_took_office="elected", confidence="medium",
          sources=[SRC_LUSK_M26_0602, SRC_LUSK_COUNCIL, SRC_LUSK_M26_1103],
          notes="Official June 2, 2026 minutes swear in Ty Thompson as a new council member. Official council page, retrieved 2026-11-24, has the heading Councilperson: Ty Thompson; the same block also still contains leftover 'Councilperson Vacant (Info Coming Soon)' text, which is not used to drop the official heading or the official June 2 swearing. Official November 3, 2026 minutes list Council Member Ty Thompson. Official term-end day after the June 2, 2026 swearing is not printed (medium)."),
        T(person_id="WY-HOLMES-NEIL", name="Neil Holmes", party="", office_group="municipal",
          office="Town of Lusk Council", term_start="2026-10-06", term_end="2030-06-02",
          election_year=2026, how_took_office="appointed", confidence="medium",
          sources=[SRC_LUSK_M26_1006, SRC_LUSK_M26_1103],
          notes="Official October 6, 2026 minutes: the council appointed 'Niel Holmes' (motion spelling) as a council member in the vacant position; 'Neil Holmes took the oath of office and took his seat with the Council.' Official November 3, 2026 minutes use Neil Holmes. The official council page retrieved 2026-11-24 does not yet list him. Official remainder term-end for that vacant seat was not stated (medium)."),
    ]
    return terms


def school_terms():
    terms = []
    def add(pid, name, start, end, year, sources, notes):
        terms.append(T(person_id=pid, name=name, party="", office_group="schools",
                       office="Niobrara County School District #1 Trustee",
                       term_start=start, term_end=end, election_year=year,
                       sources=sources, notes=notes))
    n20 = (
        "Official 2020 Niobrara County School District #1 trustees spreadsheet combining official "
        "Niobrara and official Goshen results, Vote For 5 four-year term: Jeff Miller 926 "
        "(Niobrara 918, Goshen 8), Katie Kruse 921 (911+10), Jeremy Nelson 904 (894+10), "
        "Cheryl Lund 884 (877+7), Loren Heth 636 (628+8). Patricia Goodwin 522 (517+5) was "
        "not among the top five. Official 2020 clerk summary totals are the Niobrara share only."
    )
    for pid, name in [
        ("WY-MILLER-JEFF", "Jeff Miller"),
        ("WY-KRUSE-KATIE", "Katie Kruse"),
        ("WY-NELSON-JEREMY", "Jeremy Nelson"),
        ("WY-LUND-CHERYL", "Cheryl Lund"),
        ("WY-HETH-LOREN", "Loren Heth"),
    ]:
        add(pid, name, FM[2021], FM[2025], 2020, [SRC_C20, S("Official 2020 NCSD #1 trustees results combining official Niobrara and official Goshen totals",
            "https://www.niobraracounty.org/_departments/_county_clerk/_pdfs/2020/")], n20)
    add("WY-BOLDON-SHEILA", "Sheila Boldon", FM[2021], FM[2023], 2020,
        [SRC_C20, S("Official 2020 NCSD #1 unexpired 2-year combined official Niobrara and official Goshen totals", "")],
        "Official 2020 NCSD #1 unexpired 2-year term Vote For 1 combined official totals: Sheila Boldon 1,163 (Niobrara 1,152, Goshen 11).")
    n22 = (
        "Official 2022 clerk NCSD 1 4 TTEES Vote For 4 (official Niobrara totals): Amber Smith 524, "
        "Lexie Ashurst 523, Joyce Hammer 499, Rachel Manning 454. Katie Krein 437 was fifth. "
        "An official Goshen sliver or combined 2022 spreadsheet was not found; these are official "
        "Niobrara totals, not a confirmed whole-district combined rank."
    )
    for pid, name in [
        ("WY-SMITH-AMBER-SCHOOL", "Amber Smith"),
        ("WY-ASHURST-LEXIE", "Lexie Ashurst"),
        ("WY-HAMMER-JOYCE", "Joyce Hammer"),
        ("WY-MANNING-RACHEL", "Rachel Manning"),
    ]:
        add(pid, name, FM[2023], FM[2027], 2022, [SRC_C22], n22)
    n24 = (
        "Official 2024 NCSD #1 trustees spreadsheet combining official Niobrara and official Goshen "
        "results, Vote For 5 four-year term: Lisa Pischel 753 (Niobrara 744, Goshen 9), Taylor Barnette 742 "
        "(726+16), Jeremy Nelson 628 (613+15), Cheryl Lund 601 (591+10), Wesley Vetter 586 (570+16). "
        "Katie Kruse 583 (576+7) was sixth. Official 2024 clerk summary prints the Niobrara share only "
        "and instructs that Goshen County results must be combined (see official spreadsheet)."
    )
    for pid, name in [
        ("WY-PISCHEL-LISA", "Lisa Pischel"),
        ("WY-BARNETTE-TAYLOR", "Taylor Barnette"),
        ("WY-NELSON-JEREMY", "Jeremy Nelson"),
        ("WY-LUND-CHERYL", "Cheryl Lund"),
        ("WY-VETTER-WESLEY", "Wesley Vetter"),
    ]:
        add(pid, name, FM[2025], FM[2029], 2024, [SRC_C24, SRC_C24_NCSD], n24)
    n26 = (
        "Official 2026 clerk NCSD 1 TTEE AT-LARGE Vote For 3: Sara Sampers 731, Lexie Ashurst 646, "
        "Write-In Totals 289 (the official summary lists write-in Amy Filener 202 plus spelling variants). "
        "Spelling variants are not combined here. No official named certified write-in winner was seated "
        "for the third seat; that seat stays Not yet collected. An official 2026 Goshen sliver was not found."
    )
    add("WY-SAMPERS-SARA", "Sara Sampers", FM[2027], FM[2031], 2026, [SRC_C26], n26)
    add("WY-ASHURST-LEXIE", "Lexie Ashurst", FM[2027], FM[2031], 2026, [SRC_C26], n26)
    return terms


def special_terms():
    terms = []
    def add(office, pid, name, start, end, year, sources, notes):
        terms.append(T(person_id=pid, name=name, party="", office_group="special-districts",
                       office=office, term_start=start, term_end=end, election_year=year,
                       sources=sources, notes=notes))
    # Hospital
    h20 = "Official 2020 general Hospital District Vote For 2: Dan Henry Hanson and Travis Krein (official scan)."
    add("Niobrara County Hospital District Trustee", "WY-HANSON-DAN-H", "Dan H. Hanson", FM[2021], FM[2025], 2020, [SRC_C20], h20)
    add("Niobrara County Hospital District Trustee", "WY-KREIN-TRAVIS", "Travis Krein", FM[2021], FM[2025], 2020, [SRC_C20], h20)
    h22 = "Official 2022 clerk NCHD Vote For 3: John V. Boldon 798, Randi Ross 735, Barbara Finley 656."
    add("Niobrara County Hospital District Trustee", "WY-BOLDON-JOHN-V", "John V. Boldon", FM[2023], FM[2027], 2022, [SRC_C22], h22)
    add("Niobrara County Hospital District Trustee", "WY-ROSS-RANDI", "Randi Ross", FM[2023], FM[2027], 2022, [SRC_C22], h22)
    add("Niobrara County Hospital District Trustee", "WY-FINLEY-BARBARA", "Barbara Finley", FM[2023], FM[2027], 2022, [SRC_C22], h22)
    h24 = "Official 2024 clerk Hospital Vote For 2: Dan H. Hanson 1,024, Travis Krein 836."
    add("Niobrara County Hospital District Trustee", "WY-HANSON-DAN-H", "Dan H. Hanson", FM[2025], FM[2029], 2024, [SRC_C24], h24)
    add("Niobrara County Hospital District Trustee", "WY-KREIN-TRAVIS", "Travis Krein", FM[2025], FM[2029], 2024, [SRC_C24], h24)
    add("Niobrara County Hospital District Trustee", "WY-VOLK-CONNIE", "Connie Volk", FM[2025], FM[2027], 2024, [SRC_C24],
        "Official 2024 clerk Hospital unexpired 2-year: Connie Volk 970.")
    h26 = (
        "Official 2026 clerk NCHD-TRUSTEE Vote For 3: Hillary Brown 505, Desirae Matthews-Leleux 455, "
        "Connie Volk 324, Randi Ross 264, Write-In Totals 679. The official summary lists named write-ins "
        "Kodi Lynn Smith 294 and Johnnie Dean Lashmett 246 plus spelling variants; variants are not combined, "
        "and no single official write-in line exceeds Volk 324. The three highest named printed candidates are seated."
    )
    add("Niobrara County Hospital District Trustee", "WY-BROWN-HILLARY", "Hillary Brown", FM[2027], FM[2031], 2026, [SRC_C26], h26)
    add("Niobrara County Hospital District Trustee", "WY-MATTHEWS-LELEUX-DESIRAE", "Desirae Matthews-Leleux", FM[2027], FM[2031], 2026, [SRC_C26], h26)
    add("Niobrara County Hospital District Trustee", "WY-VOLK-CONNIE", "Connie Volk", FM[2027], FM[2031], 2026, [SRC_C26], h26)
    # Conservation rural
    add("Niobrara County Conservation District Supervisor Rural", "WY-GAUKEL-KEVIN-L", "Kevin L. Gaukel", FM[2017], FM[2021], 2016, [SRC_C16],
        "Official 2016 general Nio Conservation Sup. Rural Vote For 2: Rod A. Nelson 991, Kevin L. Gaukel 893.")
    add("Niobrara County Conservation District Supervisor Rural", "WY-NELSON-ROD-A", "Rod A. Nelson", FM[2017], FM[2021], 2016, [SRC_C16],
        "Official 2016 general Nio Conservation Sup. Rural Vote For 2: Rod A. Nelson 991, Kevin L. Gaukel 893.")
    add("Niobrara County Conservation District Supervisor Rural", "WY-DOCKERY-MATTHEW-W", "Matthew W. Dockery", FM[2019], FM[2023], 2018, [SRC_C18],
        "Official 2018 general Nio Conservation Dist Rural Vote For 1: Matthew W. Dockery 696, Bruce Kilmer 387.")
    add("Niobrara County Conservation District Supervisor Rural", "WY-GAUKEL-KEVIN-L", "Kevin L. Gaukel", FM[2021], FM[2025], 2020, [SRC_C20],
        "Official 2020 general Conservation Rural Vote For 2: Kevin L. Gaukel and Bruce Kilmer (official scan).")
    add("Niobrara County Conservation District Supervisor Rural", "WY-KILMER-BRUCE", "Bruce Kilmer", FM[2021], FM[2025], 2020, [SRC_C20],
        "Official 2020 general Conservation Rural Vote For 2: Kevin L. Gaukel and Bruce Kilmer (official scan).")
    add("Niobrara County Conservation District Supervisor Rural", "WY-KILMER-BRUCE", "Bruce Kilmer", FM[2025], FM[2029], 2024, [SRC_C24],
        "Official 2024 clerk Conservation Rural Vote For 2: Bruce Kilmer 987, Leonard O. Pullis 705.")
    add("Niobrara County Conservation District Supervisor Rural", "WY-PULLIS-LEONARD-O", "Leonard O. Pullis", FM[2025], FM[2029], 2024, [SRC_C24],
        "Official 2024 clerk Conservation Rural Vote For 2: Bruce Kilmer 987, Leonard O. Pullis 705.")
    add("Niobrara County Conservation District Supervisor At-Large", "WY-MATHIAS-ODESSA", "Odessa Mathias", FM[2019], FM[2023], 2018, [SRC_C18],
        "Official 2018 general Nio Conservation Dist At Large Vote For 1: Odessa Mathias 1,023.")
    add("Niobrara County Conservation District Supervisor At-Large", "WY-MATHIAS-ODESSA", "Odessa Mathias", FM[2023], FM[2027], 2022, [SRC_C22],
        "Official 2022 clerk Conservation Dist- At-Large Vote For 1: Odessa Mathias 991.")
    add("Niobrara County Conservation District Supervisor Urban", "WY-JORDAN-DALE", "Dale Jordan", FM[2019], FM[2023], 2018, [SRC_C18],
        "Official 2018 general Nio Conservation Dist Urban Vote For 1: Dale Jordan 967.")
    add("Niobrara County Conservation District Supervisor Urban", "WY-ALLBRIGHT-TERRY", "Terry Allbright", FM[2023], FM[2027], 2022, [SRC_C22],
        "Official 2022 clerk Conservation Urban Vote For 1: Terry Allbright 1,029.")
    # Rural fire
    f16 = "Official 2016 general Nio. Co. Rural Fire Dist Dir. Vote For 3: Corky Fosher 277, Colby Thurston 254, Jim Meng 181."
    add("Niobrara County Rural Fire District Director", "WY-FOSHER-CORKY", "Corky Fosher", FM[2017], FM[2021], 2016, [SRC_C16], f16)
    add("Niobrara County Rural Fire District Director", "WY-THURSTON-COLBY-M", "Colby M. Thurston", FM[2017], FM[2021], 2016, [SRC_C16], f16)
    add("Niobrara County Rural Fire District Director", "WY-MENG-JIM", "Jim Meng", FM[2017], FM[2021], 2016, [SRC_C16], f16)
    f20 = "Official 2020 general Rural Fire Vote For 3: Colby M. Thurston, Corky Fosher, Jim Meng (official scan)."
    add("Niobrara County Rural Fire District Director", "WY-THURSTON-COLBY-M", "Colby M. Thurston", FM[2021], FM[2025], 2020, [SRC_C20], f20)
    add("Niobrara County Rural Fire District Director", "WY-FOSHER-CORKY", "Corky Fosher", FM[2021], FM[2025], 2020, [SRC_C20], f20)
    add("Niobrara County Rural Fire District Director", "WY-MENG-JIM", "Jim Meng", FM[2021], FM[2025], 2020, [SRC_C20], f20)
    f22 = "Official 2022 clerk Rural Fire 4 YR Vote For 2: Justin Kremers 270, Monty Finley 201."
    add("Niobrara County Rural Fire District Director", "WY-KREMERS-JUSTIN", "Justin Kremers", FM[2023], FM[2027], 2022, [SRC_C22], f22)
    add("Niobrara County Rural Fire District Director", "WY-FINLEY-MONTY", "Monty Finley", FM[2023], FM[2027], 2022, [SRC_C22], f22)
    f26 = "Official 2026 clerk Rural Fire Dist. Director Vote For 2: Bradyn J. Bruegger 325, Justin Kremers 250 (Clayton Williams 191 was third)."
    add("Niobrara County Rural Fire District Director", "WY-BRUEGGER-BRADYN-J", "Bradyn J. Bruegger", FM[2027], FM[2031], 2026, [SRC_C26], f26)
    add("Niobrara County Rural Fire District Director", "WY-KREMERS-JUSTIN", "Justin Kremers", FM[2027], FM[2031], 2026, [SRC_C26], f26)
    # Senior
    s20 = "Official 2020 general Senior Citizens Service District Vote For 3: Connie Baker, Jim Kremers, Phyllis Hahn (official scan)."
    add("Niobrara County Senior Citizens Service District Trustee", "WY-BAKER-CONNIE", "Connie Baker", FM[2021], FM[2025], 2020, [SRC_C20], s20)
    add("Niobrara County Senior Citizens Service District Trustee", "WY-KREMERS-JIM", "Jim Kremers", FM[2021], FM[2025], 2020, [SRC_C20], s20)
    add("Niobrara County Senior Citizens Service District Trustee", "WY-HAHN-PHYLLIS", "Phyllis Hahn", FM[2021], FM[2025], 2020, [SRC_C20], s20)
    s16 = "Official 2016 general Sr. Citizen Srvc Dist Ttee Vote For 5: Marylou Larson 918, Elaine Griffith 917, Monika Davies 858, Louis Hammer 777, Loretta Wilkison 758."
    # 2016 senior five are historical only; current 2026 VF2 below.
    add("Niobrara County Senior Citizens Service District Trustee", "WY-LARSON-MARYLOU", "Marylou Larson", FM[2017], FM[2021], 2016, [SRC_C16], s16)
    add("Niobrara County Senior Citizens Service District Trustee", "WY-DAVIES-MONIKA", "Monika Davies", FM[2017], FM[2021], 2016, [SRC_C16], s16)
    add("Niobrara County Senior Citizens Service District Trustee", "WY-HAMMER-LOUIS", "Louis Hammer", FM[2017], FM[2021], 2016, [SRC_C16], s16)
    # Do not also seat Elaine Griffith as a senior trustee under a second office confusion with commissioner — official 2016 ballot lists ELAINE GRIFFITH among senior trustees. Same person as commissioner? Possible. Use WY-GRIFFITH-ELAINE-B already. And Loretta Wilkison.
    add("Niobrara County Senior Citizens Service District Trustee", "WY-GRIFFITH-ELAINE-B", "Elaine B. Griffith", FM[2017], FM[2021], 2016, [SRC_C16],
        s16 + " Official 2016 senior-trustee ballot lists Elaine Griffith; this is not treated as a second commissioner seat.")
    add("Niobrara County Senior Citizens Service District Trustee", "WY-WILKISON-LORETTA", "Loretta Wilkison", FM[2017], FM[2021], 2016, [SRC_C16], s16)
    s26 = "Official 2026 clerk Sr. Citizen Sevice Dist. Ttee Vote For 2: Marylou Larson 733, Louis Hammer 691."
    add("Niobrara County Senior Citizens Service District Trustee", "WY-LARSON-MARYLOU", "Marylou Larson", FM[2027], FM[2031], 2026, [SRC_C26], s26)
    add("Niobrara County Senior Citizens Service District Trustee", "WY-HAMMER-LOUIS", "Louis Hammer", FM[2027], FM[2031], 2026, [SRC_C26], s26)
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 3 (S03)", 1)],
        "state-house": [("House District 2 (H02)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [
            ("Town of Lusk Mayor", 1), ("Town of Lusk Council", 4),
            ("Town of Manville Mayor", 1), ("Town of Manville Council", 4),
            ("Town of Van Tassell Mayor", 1), ("Town of Van Tassell Council", 4),
        ],
        "schools": [("Niobrara County School District #1 Trustee", 9)],
        "special-districts": [
            ("Niobrara County Hospital District Trustee", 5),
            ("Niobrara County Conservation District Supervisor At-Large", 1),
            ("Niobrara County Conservation District Supervisor Rural", 2),
            ("Niobrara County Conservation District Supervisor Urban", 1),
            ("Niobrara County Rural Fire District Director", 5),
            ("Niobrara County Senior Citizens Service District Trustee", 5),
        ],
        "judicial": [
            ("District Judge, 8th Judicial District", 2),
            ("Circuit Judge, 8th Judicial District", 2),
        ],
    }


def build_niobrara():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    # People first referenced in special/school terms
    P("WY-SMITH-AMBER-SCHOOL", "Amber Smith", "Amber", "Smith", aliases="AMBER SMITH", slug="amber-smith-ncsd")
    P("WY-HAMMER-JOYCE", "Joyce Hammer", "Joyce", "Hammer")
    P("WY-MANNING-RACHEL", "Rachel Manning", "Rachel", "Manning")
    P("WY-BOLDON-JOHN-V", "John V. Boldon", "John", "Boldon", middle="V.", aliases="J. V. BOLDON")
    P("WY-ROSS-RANDI", "Randi Ross", "Randi", "Ross")
    P("WY-FINLEY-BARBARA", "Barbara Finley", "Barbara", "Finley")
    P("WY-DOCKERY-MATTHEW-W", "Matthew W. Dockery", "Matthew", "Dockery", middle="W.")
    P("WY-MATHIAS-ODESSA", "Odessa Mathias", "Odessa", "Mathias")
    P("WY-JORDAN-DALE", "Dale Jordan", "Dale", "Jordan")
    P("WY-ALLBRIGHT-TERRY", "Terry Allbright", "Terry", "Allbright")
    P("WY-FINLEY-MONTY", "Monty Finley", "Monty", "Finley")
    P("WY-DAVIES-MONIKA", "Monika Davies", "Monika", "Davies")
    P("WY-WILKISON-LORETTA", "Loretta Wilkison", "Loretta", "Wilkison")
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
        "Niobrara clerk retentions for Justice Bridget Hill (YES 614 / NO 164), Justice Robert C. Jarosh "
        "(YES 605 / NO 165), and Chancery Judge Burningham (YES 616 / NO 151) are those statewide retentions. "
        "Local rows are 8th Judicial District judges (Converse, Goshen, Niobrara, and Platte). Full names and term "
        "dates follow official Wyoming Judicial Branch 8th JD pages and the official March 2026 roster already used "
        "in the Goshen and Platte histories. Official Niobrara named retentions are cited (2016 Patrick W. Korell "
        "YES 883 / NO 259; 2018 F. Scott Peasley YES 816 / NO 176 and Randal R. Arp YES 797 / NO 191; 2022 Clark C. "
        "Allan YES 796 / NO 159; 2024 Edward A. Buchanan YES 856 / NO 237, F. Scott Peasley YES 838 / NO 222, "
        "Nathaniel Scott Hibben YES 834 / NO 212; 2026 Clark C. Allan YES 648 / NO 140 and Jacqueline K. Brown "
        "YES 609 / NO 146). Official magistrate Dennis C. Meier retentions appear on official Niobrara canvasses "
        "and are not encoded as a circuit judgeship."
    )
    coverage = H.write_terms_and_snapshots(
        county="Niobrara", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Niobrara", slug=SLUG)
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


def _nyc():
    return [{"name": "Not yet collected", "party": "", "term_end": ""}]


def update_niobrara_json(people, terms):
    path = ROOT / "data" / "county_officials" / "niobrara.json"
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
    def holders(office):
        h = _holders_for_office(terms, people, office)
        return h if h else _nyc()

    senate = [
        _office("Senate District 3 (S03)", holders("Senate District 3 (S03)"),
                note="Official 2026 SOS statewide Senate summary, Senate District 3: Cheri E. Steinmetz (R) Total 5,792. Official Niobrara share 808. Also covers Goshen and Weston."),
    ]
    house = [
        _office("House District 2 (H02)", holders("House District 2 (H02)"),
                note="Official 2026 SOS statewide House summary, House District 2: JD Williams (R) Total 2,850. Official Niobrara share 803; official Goshen 839; official Weston 1,208. Official 2022 House District 2 was Allen Slagle (district-wide Total 2,927), not JD Williams."),
    ]
    county = [
        _office("County Commissioner", holders("County Commissioner"),
                layout="heading-then-names",
                note="Three-member board. Official commissioners page lists Patrick H. Wade, Chairman; Elaine B. Griffith, Vice Chairman; and Jeb Hanson. Official 2026 Vote For 2 elects Tiffany Thurston (787) and Kevin H. Baars (685), who take office January 2027. Official 2024 Vote For 1 Jeb Hanson (1,115) continues through January 2029."),
        _office("County Clerk", holders("County Clerk"),
                note="Official clerk page names Becky Freeman; official 2018/2022/2026 ballots Becky L. Freeman."),
        _office("County Treasurer", holders("County Treasurer"),
                note="Official treasurer page names Keri Thompson."),
        _office("County Assessor", holders("County Assessor"),
                note="Official assessor page names TERI STEPHENS (deputy Lori Himes). Official 2026 general elect Lori A. Himes (819) takes office January 2027."),
        _office("County Sheriff", holders("County Sheriff"),
                note="Official sheriff page names Sheriff Randy Starkey. Official 2018 sheriff was Cary Gill."),
        _office("County Attorney", holders("County Attorney"),
                note="Official attorney page names Anne Wasserburger; official ballots Anne K. Wasserburger."),
        _office("Clerk of District Court", holders("Clerk of District Court"),
                note="Official CDC page names Chrisanna Lund. Official 2026 general elect Amber Smith (881) takes office January 2027."),
        _office("County Coroner", holders("County Coroner"),
                note="Official coroner page lists Pete Pier; official ballots Peter W. Pier."),
    ]
    municipal = [
        _office("Town of Lusk Mayor", holders("Town of Lusk Mayor"),
                note="Official Town of Lusk site is townofluskwy.gov (the older official townoflusk.org site is down). Official mayor page, retrieved 2026-11-24, names Mayor Douglas E. Lytle. Official June 2, 2026 minutes swear him in as mayor. Official July 7, 2026 minutes still list Mayor Douglas Lytle. Official August–November 2026 regular minutes were chaired and signed by Mayor Pro-Tempore Thomas Dooper, with Lytle not recorded present; no official resignation was found in those official minutes."),
        _office("Town of Lusk Council", holders("Town of Lusk Council"),
                layout="heading-then-names",
                note="Four-member council (official town code 2-5-100, printed on the official 2024 Town Election page: mayor plus four council persons). Official June 2, 2026 minutes swear in Thomas Dooper, Chantry Filener, and Ty Thompson. Official October 6, 2026 minutes appoint Neil Holmes (motion spelling Niel Holmes; oath and later official minutes use Neil) to a vacant council seat; he took the oath the same day. Official November 3, 2026 minutes: Mayor Pro-Tempore Thomas Dooper and council members Ty Thompson, Chantry Filener, and Neil Holmes. Official council page retrieved 2026-11-24 lists Dooper (Mayor Pro Tempore), Filener, and a Ty Thompson heading, and does not yet list Holmes."),
        _office("Town of Manville Mayor", holders("Town of Manville Mayor"),
                note="Official Town of Manville About / Meet the Board page, retrieved 2026-11-24, names Mayor Richard Ladwig. Official November county generals 2016-2026 do not list Manville mayor or council contests. Official term dates were not found."),
        _office("Town of Manville Council", holders("Town of Manville Council"),
                layout="heading-then-names",
                note="Official Town of Manville About / Meet the Board page, retrieved 2026-11-24: Vice Mayor Darlene Adams; Board Members Walt (Fred) Krieger, Chuck Sides, and Sean Sides. Clerk/Treasurer Rose Fadness is staff and is not seated as an elected holder."),
        _office("Town of Van Tassell Mayor", _nyc(),
                note="Official vantassell.org live response is a park/lander page, not a government roster. Official November county generals 2016-2026 do not list Van Tassell mayor or council contests. Current mayor is not yet collected from an official source."),
        _office("Town of Van Tassell Council", _nyc(),
                layout="heading-then-names",
                note="No official Van Tassell council roster was found. Not yet collected."),
    ]
    schools = [
        _office("Niobrara County School District #1 Trustee",
                holders("Niobrara County School District #1 Trustee"),
                layout="heading-then-names",
                note="Official 2024 combined Niobrara-plus-Goshen spreadsheet Vote For 5: Lisa Pischel 753, Taylor Barnette 742, Jeremy Nelson 628, Cheryl Lund 601, Wesley Vetter 586. Official 2022 clerk Vote For 4 (Niobrara totals; official Goshen sliver not found): Amber Smith, Lexie Ashurst, Joyce Hammer, Rachel Manning, through January 2027. Official 2026 Vote For 3 elects Sara Sampers and Lexie Ashurst, taking office January 2027; the third 2026 seat is write-in-only with no official named certified winner and is not filled."),
    ]
    specials = [
        _office("Niobrara County Hospital District Trustee",
                holders("Niobrara County Hospital District Trustee"),
                layout="heading-then-names",
                note="Official 2024 Vote For 2: Dan H. Hanson and Travis Krein (four-year); official 2024 unexpired 2-year Connie Volk. Official 2022 Vote For 3: John V. Boldon, Randi Ross, and Barbara Finley, through January 2027. Official 2026 Vote For 3 elects Hillary Brown, Desirae Matthews-Leleux, and Connie Volk (write-in totals 679 were not combined across spelling variants; no single official write-in line exceeded Volk)."),
        _office("Niobrara County Conservation District Supervisor At-Large",
                holders("Niobrara County Conservation District Supervisor At-Large"),
                note="Official 2022 clerk At-Large Vote For 1: Odessa Mathias 991, through January 2027. Official 2026 general did not list a named at-large conservation contest in the extracted official summary."),
        _office("Niobrara County Conservation District Supervisor Rural",
                holders("Niobrara County Conservation District Supervisor Rural"),
                layout="heading-then-names",
                note="Official 2024 clerk Conservation Rural Vote For 2: Bruce Kilmer 987, Leonard O. Pullis 705."),
        _office("Niobrara County Conservation District Supervisor Urban",
                holders("Niobrara County Conservation District Supervisor Urban"),
                note="Official 2022 clerk Urban Vote For 1: Terry Allbright 1,029, through January 2027."),
        _office("Niobrara County Rural Fire District Director",
                holders("Niobrara County Rural Fire District Director"),
                layout="heading-then-names",
                note="Official 2022 clerk Rural Fire 4 YR Vote For 2: Justin Kremers 270, Monty Finley 201, through January 2027. Official 2026 Vote For 2 elects Bradyn J. Bruegger 325 and Justin Kremers 250, taking office January 2027. Additional current seats from official 2024 fire, if any, were not fully copied into this preview and are not invented."),
        _office("Niobrara County Senior Citizens Service District Trustee",
                holders("Niobrara County Senior Citizens Service District Trustee"),
                layout="heading-then-names",
                note="Official 2020 general Vote For 3: Connie Baker, Jim Kremers, and Phyllis Hahn (terms through January 2025 unless later officially re-elected; a complete official 2024 senior named-winner block was not seated here because that official contest was largely write-in / high undervote and is not invented). Official 2026 Vote For 2 elects Marylou Larson 733 and Louis Hammer 691, taking office January 2027."),
    ]
    judicial = [
        _office("District Judge, 8th Judicial District",
                holders("District Judge, 8th Judicial District"),
                layout="heading-then-names",
                note="Official 8th JD District Court page: Hon. Edward A. Buchanan (appointed September 2022) and Hon. F. Scott Peasley (appointed August 2017), both retained November 2024, terms expire January 2031. Official 2024 Niobrara clerk: Buchanan YES 856 / NO 237; Peasley YES 838 / NO 222."),
        _office("Circuit Judge, 8th Judicial District",
                holders("Circuit Judge, 8th Judicial District"),
                layout="heading-then-names",
                note="Official court pages already used in the Goshen history: Hon. Clark C. Allan (appointed January 2021) and Hon. Jacqueline K. Brown (appointed July 2025). Official 2026 Niobrara clerk: RETAIN CIRCUIT COURT JUDGE ALLAN YES 648 / NO 140; BROWN YES 609 / NO 146."),
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
                rec["holders"] = _nyc()
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    data["sources"] = {
        "general_results": URL_C26,
        "primary_results": URL_P26,
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/niobrara/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
