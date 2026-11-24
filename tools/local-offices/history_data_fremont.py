#!/usr/bin/env python3
"""Fremont County officeholder history (preview). Official clerk, SOS, court,
and municipal sources only. Names are never invented. Federal and tribal
offices on the Wind River Reservation are out of scope.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 10
SLUG = "fremont"

URL_COUNTY = "https://fremontcountywy.gov/"
URL_DIR = "https://fremontcountywy.gov/government/elected_officials_directory.php"
URL_COMM = "https://fremontcountywy.gov/government/elected_officials/commissioners/index.php"
URL_CLERK = "https://fremontcountywy.gov/government/elected_officials/clerk/index.php"
URL_ELECTIONS = "https://fremontcountywy.gov/government/elections___voting.php"
URL_ASSESSOR = "https://fremontcountywy.gov/government/elected_officials/assessor/tara_berg.php"
URL_TREAS = "https://fremontcountywy.gov/government/elected_officials/treasurer/index.php"
URL_SHERIFF = "https://fremontcountywy.gov/government/elected_officials/sheriff/index.php"
URL_ATTORNEY = "https://fremontcountywy.gov/government/elected_officials/attorney/index.php"
URL_CDC = "https://fremontcountywy.gov/government/elected_officials/clerk_of_district_court/index.php"
URL_CORONER = "https://fremontcountywy.gov/government/elected_officials/coroner/index.php"
URL_LANDER = "https://www.landerwy.gov/1193/Mayor-and-City-Council"
URL_RIV_ELECTED = "https://www.rivertonwy.gov/how_do_i/contact/elected_officials.php"
URL_RIV_MAYOR = "https://www.rivertonwy.gov/departments/mayor___council/meet_the_mayor.php"
URL_RIV_COUNCIL = "https://www.rivertonwy.gov/departments/mayor___council/meet_the_council.php"
URL_DUBOIS = "https://www.townofdubois.org/2159/Town-Council"
URL_HUDSON = "https://www.hudsonwy.org/gov/"
URL_SHOSHONI = "https://townofshoshoni.org/government/mayor-council"


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


SRC_DIR = S("Official Fremont County Elected Officials Directory, retrieved 2026-11-24", URL_DIR)
SRC_COMM = S("Official Fremont County Commissioners page, retrieved 2026-11-24", URL_COMM)
SRC_CLERK = S("Official Fremont County Clerk page, retrieved 2026-11-24", URL_CLERK)
SRC_ELEC = S("Official Fremont County Elections & Voting page, retrieved 2026-11-24", URL_ELECTIONS)
SRC_ASSESSOR = S(
    "Official Fremont County Assessor page (County Assessor - Ella Riggs), retrieved 2026-11-24. "
    "The page states: Ella M. Riggs - Appointed Interim County Assessor on September 29, 2026. "
    "The elected-officials directory card still listed Tara Berg and was treated as stale.",
    URL_ASSESSOR,
)
SRC_TREAS = S("Official Fremont County Treasurer page, retrieved 2026-11-24", URL_TREAS)
SRC_SHERIFF = S("Official Fremont County Sheriff page, retrieved 2026-11-24", URL_SHERIFF)
SRC_ATTORNEY = S("Official Fremont County Attorney page, retrieved 2026-11-24", URL_ATTORNEY)
SRC_CDC = S("Official Fremont County Clerk of District Court page, retrieved 2026-11-24", URL_CDC)
SRC_CORONER = S("Official Fremont County Coroner page, retrieved 2026-11-24", URL_CORONER)
SRC_LANDER = S("Official City of Lander Mayor and City Council page, retrieved 2026-11-24", URL_LANDER)
SRC_RIV_ELECTED = S("Official City of Riverton Elected Officials page, retrieved 2026-11-24", URL_RIV_ELECTED)
SRC_RIV_MAYOR = S("Official City of Riverton Meet the Mayor page, retrieved 2026-11-24", URL_RIV_MAYOR)
SRC_RIV_COUNCIL = S("Official City of Riverton Meet the Council page, retrieved 2026-11-24", URL_RIV_COUNCIL)
SRC_DUBOIS = S("Official Town of Dubois Town Council page, retrieved 2026-11-24", URL_DUBOIS)
SRC_HUDSON = S("Official Town of Hudson Government page, retrieved 2026-11-24", URL_HUDSON)
SRC_SHOSHONI = S("Official Town of Shoshoni Mayor & Council page, retrieved 2026-11-24", URL_SHOSHONI)
SRC_2026_ABS = S(
    "Official Fremont County General Election Abstract / Official Results Summary, November 3, 2026 "
    "(header: Abstract, by Voting Precincts, GENERAL ELECTION, 3rd Day of November, A.D. 2026; "
    "inside pages: Summary Results Report OFFICIAL RESULTS, GENERAL ELECTION BALLOT Abstract; "
    "footer: OFFICIAL ABSTRACT GENERAL 2026 - 11/05/2026 09:37AM; 13,236 ballots). "
    "The report-generation timestamp is the morning of the official Nov. 5 canvass (1:00 p.m.). "
    "Countywide totals tie to the official post-canvass Vote Center report (generated 11/06/2026 12:39PM, "
    "OFFICIAL RESULTS, TOTAL VOTES CAST 13,236) and the official Nov. 5 canvass minutes. "
    "Posted as Official Results Summary / Official Abstract from the official elections page.",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/General/2026%20General%20OFFICIAL%20Results%20Summary%20-%20Official%20Abstract%202026.11.5.pdf",
)
SRC_2026_VC = S(
    "Official Fremont County General Election Official by Vote Center report, November 3, 2026 "
    "(header OFFICIAL RESULTS, OFFICIAL GENERAL ELECTION BALLOT; footer General 2026 by Poll type - 11/06/2026 12:39PM; "
    "TOTAL VOTES CAST 13,236).",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/General/2026%20General%20Official%20by%20Vote%20Center.pdf",
)
SRC_2026_PCT = S(
    "Official Fremont County General Election Precinct Summary Report, November 3, 2026 "
    "(header OFFICIAL CANVASS RESULTS, OFFICIAL GENERAL ELECTION BALLOT; created Nov. 17, 2026).",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/General/Gen26%20Official%20Precinct%20Summary%20Report.pdf",
)
SRC_2026_MIN = S(
    "Official Fremont County Canvass Board meeting minutes, November 5, 2026 "
    "(the heading typographically says PRIMARY but the body is the General Election canvass: "
    "Total ballots cast 13,236; Abstract reviewed; winners determined in local races). "
    "County Clerk is named Julie A. Freese.",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026.11.05%20Minutes.pdf",
)
SRC_2026_PRI = S(
    "Official Fremont County Primary Election Precinct Summary Report, August 18, 2026 "
    "(header OFFICIAL RESULTS, OFFICIAL PRIMARY ELECTION 2026 RESULTS; created Aug. 21, 2026 after the Aug. 20 official primary canvass).",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/Primary/2026%20Primary%20Official%20Precinct%20Summary%20Report.pdf",
)
SRC_2026_FILING = S(
    "Official Fremont County updated general-election candidate filings as of Aug. 24, 2026 at 5:00 p.m. "
    "(UPDATED 8-25-26 GEN FILING.pdf), used for official ballot names of school, special-district, "
    "and Commissioner District 1 unaffiliated candidate Nicole A. Wagon.",
    "https://www.fremontcountywy.gov/Government/Clerk/Elections/UPDATED%208-25-26%20GEN%20FILING.pdf",
)
SRC_COURT = S(
    "Official Wyoming Judicial Branch 9th Judicial District names already used from official court pages "
    "in the Teton and Sublette histories (District Judge Jason M. Conder; Circuit Judges Erin E. Weisman "
    "and Jefferson Boone Coombs).",
    "",
)

SRC_2024_CANV = S(
    "Official Fremont County 2024 General Election 77-page Official Canvass Results, November 7, 2024 "
    "(Custom Table Report / OFFICIAL CANVASS RESULTS November 7, 2024, and Summary Results Report / "
    "OFFICIAL WRITE-IN REPORT CANVASS 11-7-2024; footer Fremont County General Election Precinct Summary "
    "CANVASS REPORT - 11/07/2024 12:26PM). Face of the file is official. The official elections website "
    "labels it as of November 5th, 2024; that website wording is flagged.",
    "https://fremontcountywy.gov/Government/Clerk/Elections/2024%20Election%20Results/General%202024%20Official%20Results%20Abstract%20(1).pdf",
)
SRC_2026_PRI_VC = S(
    "Official Fremont County 2026 Primary Election Official by Vote Center report "
    "(header OFFICIAL PRIMARY ELECTION BALLOT; footer Primary 2026 Results by Vote Center - 08/21/2026 03:08PM; "
    "filename typo Offical). Commissioner District 4, page 17 of 49, 6 of 6 precincts reporting: "
    "STEFF KESSLER 902, J. D. CARPER 555, CHRISTY HIRASAWA GABEL 356, JIM TAYLOR 294, JEFFREY A. YOUNG 238, "
    "write-ins 5, contest totals 2,525.",
    "https://fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/Primary/2026%20Primary%20Offical%20by%20Vote%20Center.pdf",
)
SRC_2026_PRI_BALLOT = S(
    "Official Fremont County 2026 Primary Election sample ballot (official clerk elections page): "
    "Commissioner District 4 – Four (4) Year Term, Vote for One (1) REPUBLICAN: JD Carper, "
    "Christy Hirasawa Gabel, Steff Kessler, Jim Taylor, Jeffrey A Young.",
    "https://fremontcountywy.gov/Government/Clerk/Elections/pdf%202026%20PRIMARY%20SAMPLE%20BALLOT%20AD%20new%20format%202026.7.25%20-%20Copy.pdf",
)
SRC_FCSD1 = S(
    "Official Fremont County School District #1 Governing Board page, Wayback capture 20261021230108 of "
    "https://www.landerschools.org/page/governing-board/ (the live Finalsite page returned a JS challenge wall). "
    "Official current board with term expires: Taylor Jacobs, Chairperson, 12/1/2028; Mike McConnell, Vice Chairperson, "
    "12/01/2026; Mara Gans, 12/01/2028; Karen Harms, Treasurer, 12/01/2026; Jared Kail, 12/01/2026; "
    "Matt Ayers, 12/01/2026; Aileen Brew, 12/1/2026.",
    "https://www.landerschools.org/page/governing-board/",
)
SRC_FCSD2 = S(
    "Official Fremont County School District #2 Governing Board page, retrieved 2026-11-24: Janean Sellers, Chair; "
    "Jill Judd, Vice Chair; Libby Littler, Treasurer; Shawn Hess, Clerk; Nicole Polmanteer; Judy Rogers; Leah Vermeire.",
    "https://www.fremont2.org/governing-board",
)
SRC_FCSD14 = S(
    "Official Fremont County School District #14 Highbond portal current member widget, retrieved 2026-11-24 "
    "(portal lists meetings through November 11, 2026): Arline Trosper, Rich Singer, Tessa Redman, "
    "Carlton Underwood, Sanford Friday.",
    "https://fremont14-k12-wy.community.highbond.com/Portal/MeetingInformation.aspx?Id=340",
)
SRC_FCSD21 = S(
    "Official Fremont County School District #21 Fort Washakie High School 2025-2026 Student and Parent Handbook, "
    "FCSD #21 Board of Trustees: Tex LeClair, Chairman; Kay Ferris, Vice Chairman; Carla Mann, Treasurer; "
    "Bonnie Washakie, Member; David Snyder, Member. The official handbook covers the 2025-2026 school year; "
    "it is used as the official board roster and is cross-checked with the official 2024 canvass.",
    "https://www.fortwashakieschool.com/",
)
SRC_FCSD38 = S(
    "Official Fremont County School District #38 School Board page, retrieved 2026-11-24: Lionel Bell, Chair; "
    "Becky Bell, Vice-Chair; Billie Spoonhunter, Clerk; John Goggles, Treasurer; Rose Guerue, Trustee.",
    "https://www.arapahoeschools.com/page/school-board",
)
SRC_CWC = S(
    "Official Central Wyoming College Board of Trustees page, retrieved 2026-11-24: Paula Hunker, Chair; "
    "Craig Tolman, Vice Chair; Shana Tarter, Secretary; Carlton Underwood, Treasurer; Alma Law; Gay Hughes; Ernie Over. "
    "The official directory supplies subdistrict labels; the live board page is preferred for officer titles. "
    "Credentials such as Dr. are not printed.",
    "https://www.cwc.edu/leadership/board-of-trustees/",
)
SRC_CWC_DIR = S(
    "Official Central Wyoming College directory, retrieved 2026-11-24 (subdistrict labels).",
    "https://www.cwc.edu/about/directory/",
)


def register_people(P):
    # Legislature
    P("WY-GEIS-GERALD-E", "Gerald E. Geis", "Gerald", "Geis", middle="E.")
    P("WY-BEBOUT-ELI-D", "Eli D. Bebout", "Eli", "Bebout", middle="D.")
    P("WY-CASE-CALE", "Cale Case", "Cale", "Case")
    P("WY-AGAR-WYATT", "Wyatt Agar", "Wyatt", "Agar")
    P("WY-COOPER-ED", "Ed Cooper", "Ed", "Cooper")
    P("WY-SALAZAR-TIM", "Tim Salazar", "Tim", "Salazar")
    P("WY-WINTERS-NATHAN", "Nathan Winters", "Nathan", "Winters")
    P("WY-WINTER-JOHN-R", "John R. Winter", "John", "Winter", middle="R.", aliases="John Winter")
    P("WY-HOGG-ALLEN", "Allen Hogg", "Allen", "Hogg")
    P("WY-ALLEN-JIM", "Jim Allen", "Jim", "Allen")
    P("WY-POSEY-IVAN-D", "Ivan D. Posey", "Ivan", "Posey", middle="D.", aliases="Ivan Posey")
    P("WY-CAMPBELL-RITA", "Rita Campbell", "Rita", "Campbell")
    P("WY-OTTMAN-PEPPER-L", "Pepper L. Ottman", "Pepper", "Ottman", middle="L.", aliases="Pepper L Ottman; Pepper Ottman")
    P("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "Lloyd Charles", "Larsen", aliases="Lloyd Larsen")
    P("WY-MILLER-DAVID-R", "David R. Miller", "David", "Miller", middle="R.")
    P("WY-OAKLEY-EMBER", "Ember Oakley", "Ember", "Oakley")
    P("WY-GUGGENMOS-JOEL", "Joel Guggenmos", "Joel", "Guggenmos")
    P("WY-MANNING-CARL", "Carl Manning", "Carl", "Manning")
    P("WY-GOGGLES-W-PATRICK", "W. Patrick Goggles", "W. Patrick", "Goggles")
    P("WY-CLIFFORD-ANDREA", "Andrea Clifford", "Andrea", "Clifford", aliases="Andi Clifford")
    P("WY-PENN-SARAH", "Sarah Penn", "Sarah", "Penn")
    # County current and 2026 elects
    P("WY-ALLEN-LARRY", "Larry Allen", "Larry", "Allen")
    P("WY-JONES-MICHAEL", "Michael Jones", "Michael", "Jones")
    P("WY-THOMAS-CLARENCE", "Clarence Thomas", "Clarence", "Thomas")
    P("WY-FABRIZIUS-RON", "Ron Fabrizius", "Ron", "Fabrizius")
    P("WY-WILSON-JENNIFER", "Jennifer Wilson", "Jennifer", "Wilson")
    P("WY-WAGON-NICOLE-A", "Nicole A. Wagon", "Nicole", "Wagon", middle="A.")
    P("WY-STANLEY-RYAN-W", "Ryan W. Stanley", "Ryan", "Stanley", middle="W.")
    P("WY-KESSLER-STEFF", "Steff Kessler", "Steff", "Kessler",
      aliases="REP KESSLER; Kessler; STEFF KESSLER")
    P("WY-FREESE-JULIE-A", "Julie A. Freese", "Julie", "Freese", middle="A.", aliases="Julie Freese")
    P("WY-ANDERSON-JAMES-A", "James A. Anderson", "James", "Anderson", middle="A.", aliases="Jim Anderson")
    P("WY-RIGGS-ELLA-M", "Ella M. Riggs", "Ella", "Riggs", middle="M.", aliases="Ella Riggs; REP RIGGS")
    P("WY-LEE-RYAN", "Ryan Lee", "Ryan", "Lee")
    P("WY-ZERGA-JOHN", "John Zerga", "John", "Zerga")
    P("WY-WYATT-MICAH", "Micah Wyatt", "Micah", "Wyatt")
    P("WY-SANCHEZ-AMANDA-R", "Amanda R. Sanchez", "Amanda", "Sanchez", middle="R.", aliases="Amanda Sanchez")
    P("WY-IVIE-ERIN", "Erin Ivie", "Erin", "Ivie")
    # Municipal
    P("WY-WHITE-MISSY", "Missy White", "Missy", "White")
    P("WY-MOTHERWAY-MICHELLE-B", "Michelle B. Motherway", "Michelle", "Motherway", middle="B.")
    P("WY-HAHN-JOSH", "Josh Hahn", "Josh", "Hahn")
    P("WY-HAHN-DAN", "Dan Hahn", "Dan", "Hahn")
    P("WY-CASSADY-CHAD", "Chad Cassady", "Chad", "Cassady")
    P("WY-STUBLE-JULIA", "Julia Stuble", "Julia", "Stuble")
    P("WY-LARSEN-JOHN", "John Larsen", "John", "Larsen")
    P("WY-COX-MELINDA", "Melinda Cox", "Melinda", "Cox")
    P("WY-CASE-GEORGE", "George Case", "George", "Case")
    P("WY-SCHLOSSER-SARAH-L", "Sarah L. Schlosser", "Sarah", "Schlosser", middle="L.")
    P("WY-HANCOCK-TIM", "Tim Hancock", "Tim", "Hancock", aliases="Timothy Hancock")
    P("WY-BAILEY-MICHAEL-V", "Michael V. (Mike) Bailey", "Michael", "Bailey", middle="V.",
      aliases="Mike Bailey; MICHAEL V (MIKE) BAILEY")
    P("WY-JOHNSON-KAREN", "Karen Johnson", "Karen", "Johnson")
    P("WY-LARSON-KYLE-M", "Kyle M. Larson", "Kyle", "Larson", middle="M.", aliases="Kyle Larson")
    P("WY-PRESTON-JERIKA", "Jerika Preston", "Jerika", "Preston")
    P("WY-BORDERS-KARLA", "Karla Borders", "Karla", "Borders")
    P("WY-CARR-ERIC", "Eric Carr", "Eric", "Carr")
    P("WY-WILCZEWSKI-CHANCEY", "Chancey Wilczewski", "Chancey", "Wilczewski")
    P("WY-NEVEAUX-PATRICIA", "Patricia Neveaux", "Patricia", "Neveaux")
    P("WY-FURMAN-DAVID", "David Furman", "David", "Furman")
    P("WY-LEE-RICK", "Rick Lee", "Rick", "Lee")
    P("WY-LAHR-RANDY", "Randy Lahr", "Randy", "Lahr")
    P("WY-YSEN-AMANDA", "Amanda Ysen", "Amanda", "Ysen")
    P("WY-THOMPSON-BRUCE-JOHN", "Bruce John Thompson", "Bruce John", "Thompson")
    P("WY-STRASSER-MIKE", "Mike Strasser", "Mike", "Strasser")
    P("WY-HIGHSMITH-JOEL", "Joel Highsmith", "Joel", "Highsmith")
    P("WY-ANKENY-RONALD-W", "Ronald W. Ankeny", "Ronald", "Ankeny", middle="W.")
    P("WY-NORDEEN-MARK", "Mark Nordeen", "Mark", "Nordeen")
    P("WY-STETLER-JACOB-Z", "Jacob Z. Stetler", "Jacob", "Stetler", middle="Z.", aliases="Jake Z. Stetler")
    P("WY-HARDTKE-TAMMIE-A", "Tammie A. Hardtke", "Tammie", "Hardtke", middle="A.")
    P("WY-WHITENER-JORDAN", "Jordan Whitener", "Jordan", "Whitener", aliases="Jordan A. Whitener")
    P("WY-OLER-SHERRY", "Sherry Oler", "Sherry", "Oler")
    P("WY-ROBINSON-MARILYN-V", "Marilyn V. Robinson", "Marilyn", "Robinson", middle="V.")
    P("WY-HAMILTON-BRADY", "Brady Hamilton", "Brady", "Hamilton")
    P("WY-BONELLA-ZEKE", "Zeke Bonella", "Zeke", "Bonella")
    P("WY-GORDON-HELEN-J", "Helen J. Gordon", "Helen", "Gordon", middle="J.", aliases="Helen Gordon")
    P("WY-KUMMER-KEVIN", "Kevin Kummer", "Kevin", "Kummer")
    P("WY-SVILAR-DANIEL", "Daniel (Danny) Svilar", "Daniel", "Svilar", aliases="Danny Svilar")
    P("WY-EMERSON-LESTER-R", "Lester R. Emerson", "Lester", "Emerson", middle="R.")
    P("WY-REYNOLDS-MANDI", "Mandi Reynolds", "Mandi", "Reynolds")
    P("WY-STOLDT-JACQUE-L", "Jacque L. Stoldt", "Jacque", "Stoldt", middle="L.")
    # Judicial
    P("WY-CONDER-JASON-M", "Jason M. Conder", "Jason", "Conder", middle="M.")
    P("WY-WEISMAN-ERIN-E", "Erin E. Weisman", "Erin", "Weisman", middle="E.")
    P("WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "Jefferson Boone", "Coombs")
    # Schools 2026 elects (official canvass + official filing names)
    P("WY-WESTON-BREANNE-N", "Breanne N. Weston", "Breanne", "Weston", middle="N.")
    P("WY-GREENE-MARY", "Mary Greene", "Mary", "Greene")
    P("WY-MCCONNELL-MIKE", "Mike McConnell", "Mike", "McConnell")
    P("WY-STRIKE-KATE", "Kate Strike", "Kate", "Strike")
    P("WY-CHAPIN-JEFF", "Jeff Chapin", "Jeff", "Chapin")
    P("WY-LINDSEY-BRAD", "Brad Lindsey", "Brad", "Lindsey")
    P("WY-ROGERS-JUDY", "Judy Rogers", "Judy", "Rogers")
    P("WY-POLMANTEER-NICOLE", "Nicole Polmanteer", "Nicole", "Polmanteer")
    P("WY-BAKER-TINA", "Tina Baker", "Tina", "Baker")
    P("WY-LITTLER-LIBBY", "Libby Littler", "Libby", "Littler")
    P("WY-KLEIN-JESSICA", "Jessica Klein", "Jessica", "Klein")
    P("WY-BEFUS-DAVID", "David Befus", "David", "Befus")
    P("WY-HILL-VAN", "Van Hill", "Van", "Hill")
    P("WY-LEONHARDT-DAWN", "Dawn Leonhardt", "Dawn", "Leonhardt")
    P("WY-TROSPER-WILLENA-ROSIE", "Willena Rosie Trosper", "Willena Rosie", "Trosper")
    P("WY-FRIDAY-SANFORD-D", "Sanford D. Friday", "Sanford", "Friday", middle="D.")
    P("WY-HILL-JAKE", "Jake Hill", "Jake", "Hill")
    P("WY-WAGON-CLINTON-D", "Clinton D. Wagon", "Clinton", "Wagon", middle="D.")
    P("WY-THOMPSON-LYNN-A", "Lynn A. Thompson", "Lynn", "Thompson", middle="A.")
    P("WY-MARTIN-LAURA", "Laura Martin", "Laura", "Martin")
    P("WY-EDGEINGTON-KRIS", "Kris Edgeington", "Kris", "Edgeington")
    P("WY-ENGUM-HILARY", "Hilary Engum", "Hilary", "Engum")
    P("WY-RAY-JODY", "Jody Ray", "Jody", "Ray")
    P("WY-MANNING-CLAIRE", "Claire Manning", "Claire", "Manning")
    P("WY-CANTRELL-TERRY", "Terry Cantrell", "Terry", "Cantrell")
    P("WY-GROESBECK-MICHELLE", "Michelle \"Shelly\" Groesbeck", "Michelle", "Groesbeck", aliases="Shelly Groesbeck")
    P("WY-HANWAY-BRIDGER-B", "Bridger B. Hanway", "Bridger", "Hanway", middle="B.")
    P("WY-BROWN-CHARLENE-GAMBLER", "Charlene Gambler Brown", "Charlene", "Brown", middle="Gambler")
    # School holdovers / official current boards
    P("WY-JACOBS-TAYLOR", "Taylor Jacobs", "Taylor", "Jacobs")
    P("WY-GANS-MARA", "Mara Gans", "Mara", "Gans")
    P("WY-HARMS-KAREN", "Karen Harms", "Karen", "Harms")
    P("WY-KAIL-JARED", "Jared Kail", "Jared", "Kail")
    P("WY-AYERS-MATT", "Matt Ayers", "Matt", "Ayers")
    P("WY-BREW-AILEEN", "Aileen Brew", "Aileen", "Brew")
    P("WY-SELLERS-JANEAN", "Janean Sellers", "Janean", "Sellers")
    P("WY-JUDD-JILL", "Jill Judd", "Jill", "Judd")
    P("WY-HESS-SHAWN", "Shawn Hess", "Shawn", "Hess")
    P("WY-VERMEIRE-LEAH", "Leah Vermeire", "Leah", "Vermeire")
    P("WY-EVANS", "Evans", "Evans", "Evans")
    P("WY-MCCANN", "McCann", "McCann", "McCann")
    P("WY-STOLL-BAKER", "Stoll-Baker", "Stoll-Baker", "Stoll-Baker")
    P("WY-TROSPER-ARLINE", "Arline Trosper", "Arline", "Trosper")
    P("WY-SINGER-RICH", "Rich Singer", "Rich", "Singer")
    P("WY-REDMAN-TESSA", "Tessa Redman", "Tessa", "Redman")
    P("WY-UNDERWOOD-CARLTON", "Carlton Underwood", "Carlton", "Underwood")
    P("WY-LECLAIR-TEX", "Tex LeClair", "Tex", "LeClair")
    P("WY-FERRIS-KAY", "Kay Ferris", "Kay", "Ferris")
    P("WY-MANN-CARLA", "Carla Mann", "Carla", "Mann")
    P("WY-WASHAKIE-BONNIE", "Bonnie Washakie", "Bonnie", "Washakie")
    P("WY-SNYDER-DAVID", "David Snyder", "David", "Snyder")
    P("WY-HAUN", "Haun", "Haun", "Haun")
    P("WY-PEREGOY", "Peregoy", "Peregoy", "Peregoy")
    P("WY-CRIMM", "Crimm", "Crimm", "Crimm")
    P("WY-JEFFRES", "Jeffres", "Jeffres", "Jeffres")
    P("WY-BERG-FCSD25", "Berg", "Berg", "Berg")
    P("WY-MANNING-FCSD25", "Manning", "Manning", "Manning")
    P("WY-MORROW", "Morrow", "Morrow", "Morrow")
    P("WY-BELL-LIONEL", "Lionel Bell", "Lionel", "Bell")
    P("WY-BELL-BECKY", "Becky Bell", "Becky", "Bell")
    P("WY-SPOONHUNTER-BILLIE", "Billie Spoonhunter", "Billie", "Spoonhunter")
    P("WY-GOGGLES-JOHN", "John Goggles", "John", "Goggles")
    P("WY-GUERUE-ROSE", "Rose Guerue", "Rose", "Guerue")
    # Pavillion 2024 council (official canvass last names only)
    P("WY-BARRETT-PAVILLION", "Barrett", "Barrett", "Barrett")
    P("WY-ROBINSON-PAVILLION", "Robinson", "Robinson", "Robinson")
    # CWC / specials
    P("WY-TOLMAN-CRAIG", "Craig Tolman", "Craig", "Tolman")
    P("WY-HUSSA-ROBERT", "Robert Hussa", "Robert", "Hussa")
    P("WY-PRYOR-JENNIFER", "Jennifer Pryor", "Jennifer", "Pryor")
    P("WY-HUNKER-PAULA", "Paula Hunker", "Paula", "Hunker")
    P("WY-TARTER-SHANA", "Shana Tarter", "Shana", "Tarter")
    P("WY-LAW-ALMA", "Alma Law", "Alma", "Law")
    P("WY-HUGHES-GAY", "Gay Hughes", "Gay", "Hughes")
    P("WY-OVER-ERNIE", "Ernie Over", "Ernie", "Over")
    # Official 2026 special-district elects (official Vote Center + official filings)
    P("WY-JOHNSON-BODIE", "Bodie Johnson", "Bodie", "Johnson")
    P("WY-WELLS-CHRIS", "Chris Wells", "Chris", "Wells")
    P("WY-GRAFF-ROSEMARY", "Rosemary Graff", "Rosemary", "Graff")
    P("WY-WELLS-MARGARET-L", "Margaret L. Wells", "Margaret", "Wells", middle="L.")
    P("WY-BOESCH-GERRI", "Gerri Boesch", "Gerri", "Boesch")
    P("WY-DAVIS-ROBERT-B", "Robert B. Davis", "Robert", "Davis", middle="B.")
    P("WY-STANBURY-ROSE", "Rose Stanbury", "Rose", "Stanbury")
    P("WY-MORAVEK-CYNTHIA", "Cynthia Moravek", "Cynthia", "Moravek")
    P("WY-DAVIS-KRIS", "Kris Davis", "Kris", "Davis")
    P("WY-THOMPSON-ERIC-S", "Eric S. Thompson", "Eric", "Thompson", middle="S.")
    P("WY-LUCAS-RON", "Ron Lucas", "Ron", "Lucas")
    P("WY-PETTIT-SCOTT-D", "Scott D. Pettit", "Scott", "Pettit", middle="D.")
    P("WY-ESPINOSA-SALLY", "Sally Espinosa", "Sally", "Espinosa")
    P("WY-HAMILTON-JARED-W", "Jared W. Hamilton", "Jared", "Hamilton", middle="W.")
    P("WY-THOMPSON-DOUGLAS-L", "Douglas L. Thompson", "Douglas", "Thompson", middle="L.")
    P("WY-CODEVILLA-MICHAEL-P", "Michael P. Codevilla", "Michael", "Codevilla", middle="P.")
    P("WY-BRADBURY-GARY", "Gary Bradbury", "Gary", "Bradbury")
    P("WY-GARDNER-KELLY", "Kelly Gardner", "Kelly", "Gardner")
    P("WY-DOWNEY-PAUL-J", "Paul J. Downey", "Paul", "Downey", middle="J.")
    P("WY-FYLER-JOHN-RED", "John \"Red\" Fyler", "John", "Fyler", aliases="John Red Fyler; JOHN RED FYLER")
    P("WY-GARLAND-STEVE", "Steve Garland", "Steve", "Garland")
    P("WY-MURPHREE-TYLER-THOMAS", "Tyler Thomas Murphree", "Tyler Thomas", "Murphree")
    P("WY-KOPRIVA-PATRICIA", "Patricia Kopriva", "Patricia", "Kopriva")
    P("WY-TREBELCOCK-JERI", "Jeri Trebelcock", "Jeri", "Trebelcock")
    P("WY-BRINDA-DAVID", "David Brinda", "David", "Brinda")
    P("WY-FAGNANT-RICHARD", "Richard Fagnant", "Richard", "Fagnant")
    P("WY-HENRY-JOE", "Joe Henry", "Joe", "Henry")
    P("WY-ALLEN-VICTOR-R", "Victor R. Allen", "Victor", "Allen", middle="R.")
    P("WY-BRODRICK-MARLENE", "Marlene Brodrick", "Marlene", "Brodrick")
    P("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", "Wesley", "Roberts", middle="A.")
    P("WY-CUNDALL-KEN", "Ken Cundall", "Ken", "Cundall")
    P("WY-GEIS-JOAN", "Joan Geis", "Joan", "Geis")
    P("WY-TAYLOR-TERESA", "Teresa Taylor", "Teresa", "Taylor")
    # Official 2024 specials (canvass last names where first names were not on the face)
    P("WY-GARD-MTNVIEW", "Gard", "Gard", "Gard")
    P("WY-MARTIN-MTNVIEW", "Martin", "Martin", "Martin")
    P("WY-DELAY-CEM", "Delay", "Delay", "Delay")
    P("WY-MCKEE-CEM", "McKee", "McKee", "McKee")
    P("WY-ZENT-CEM", "Zent", "Zent", "Zent")
    P("WY-JENSEN-DUBOIS-FIRE", "Jensen", "Jensen", "Jensen")


def _add(terms, pid, name, office, group, start, end, year, sources, notes, party="", how="elected", conf="high", **extra):
    rec = T(
        person_id=pid, name=name, office=office, office_group=group,
        term_start=start, term_end=end, election_year=year, sources=sources,
        notes=notes, party=party, how_took_office=how, confidence=conf, **extra,
    )
    terms.append(rec)
    return rec




def legislature_terms():
    """Official SOS district-wide Totals, with the official Fremont share noted.
    Two-column official SOS pages (2016, 2018, 2020) are cut at the next district header.
    """
    terms = []
    P_ADD = [
        # people for historical house/senate already registered; add leftovers used below
    ]

    def leg(pid, name, office, start, end, ey, chamber, notes, party="Republican"):
        group = "state-senate" if chamber == "Senate" else "state-house"
        _add(terms, pid, name, office, group, start, end, ey, [sos_src(ey, chamber)], notes, party=party)

    # Senate
    leg("WY-GEIS-GERALD-E", "Gerald E. Geis", "Senate District 20 (S20)", "2013-01-07", "2017-01-02", 2012, "Senate",
        "Official 2012 SOS statewide Senate summary, Senate District 20: Gerald E. Geis (R) Total 7,592. Official Fremont share 317; official Big Horn 1,245, Hot Springs 2,164, Park 410, Washakie 3,456.")
    leg("WY-BEBOUT-ELI-D", "Eli D. Bebout", "Senate District 26 (S26)", "2013-01-07", "2017-01-02", 2012, "Senate",
        "Official 2012 SOS statewide Senate summary, Senate District 26: Eli D. Bebout (R) Total 7,457. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-CASE-CALE", "Cale Case", "Senate District 25 (S25)", "2015-01-05", "2019-01-07", 2014, "Senate",
        "Official 2014 SOS statewide Senate summary, Senate District 25: Cale Case (R) 3,390, Sergio A. Maldonado, Sr. (D) 2,330. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-AGAR-WYATT", "Wyatt Agar", "Senate District 20 (S20)", "2017-01-02", "2021-01-04", 2016, "Senate",
        "Official 2016 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18; not the District 18 Total): Wyatt Agar (R) Total 6,893, Mary Jane Norskog (D) 1,546. Official Fremont share Agar 281, Norskog 54.")
    leg("WY-BEBOUT-ELI-D", "Eli D. Bebout", "Senate District 26 (S26)", "2017-01-02", "2021-01-04", 2016, "Senate",
        "Official 2016 SOS statewide Senate summary, Senate District 26: Eli D. Bebout (R) 6,461, Chesie Lee (D) 1,979. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-CASE-CALE", "Cale Case", "Senate District 25 (S25)", "2019-01-07", "2023-01-02", 2018, "Senate",
        "Official 2018 SOS statewide Senate summary, Senate District 25 (right column of the official two-column page with District 23): Cale Case (R) 4,012, Sergio A. Maldonado, Sr. (D) 2,872. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)", "2021-01-04", "2025-01-06", 2020, "Senate",
        "Official 2020 SOS statewide Senate summary, Senate District 20 (right column of the official two-column page with District 18): Ed Cooper (R) Total 7,497, Theresa Livingston (D) 1,293. Official Fremont share Cooper 335, Livingston 32.")
    leg("WY-SALAZAR-TIM", "Tim Salazar", "Senate District 26 (S26)", "2021-01-04", "2025-01-06", 2020, "Senate",
        "Official 2020 SOS statewide Senate summary, Senate District 26: Tim Salazar (R) Total 7,790. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-CASE-CALE", "Cale Case", "Senate District 25 (S25)", "2023-01-02", "2027-01-04", 2022, "Senate",
        "Official 2022 SOS statewide Senate summary, Senate District 25: Cale Case (R) Total 4,365. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-COOPER-ED", "Ed Cooper", "Senate District 20 (S20)", "2025-01-06", "2029-01-01", 2024, "Senate",
        "Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Fremont share 305; official Big Horn 1,475, Hot Springs 2,180, Park 834, Washakie 3,442. Off-cycle in 2026.")
    leg("WY-SALAZAR-TIM", "Tim Salazar", "Senate District 26 (S26)", "2025-01-06", "2029-01-01", 2024, "Senate",
        "Official 2024 SOS statewide Senate summary, Senate District 26: Tim Salazar (R) Total 7,266. Fremont-only (official Fremont share equals the official Total). Off-cycle in 2026.")
    leg("WY-CASE-CALE", "Cale Case", "Senate District 25 (S25)", "2027-01-04", "2031-01-06", 2026, "Senate",
        "Official 2026 SOS statewide Senate summary, Senate District 25: Cale Case (R) Total 4,670. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: REP CASE 4,670.")

    # House — Nathan Winters (2012-2016 official SOS) and John R. Winter (2018-2024 official SOS) are distinct official names and are not combined.
    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)", "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 28: Nathan Winters (R) Total 3,288, Connie Skates (D) 1,100. Official Fremont share Winters 278, Skates 65. Official other shares: Big Horn 954–164, Hot Springs 1,689–769, Park 367–102.")
    leg("WY-GOGGLES-W-PATRICK", "W. Patrick Goggles", "House District 33 (H33)", "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 33: W. Patrick Goggles (D) 1,573, Jim Allen (R) 1,447. Fremont-only (official Fremont share equals the official Total).",
        party="Democratic")
    leg("WY-CAMPBELL-RITA", "Rita Campbell", "House District 34 (H34)", "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 34: Rita Campbell (R) 3,797. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 2,787, Bruce Palmer (D) 1,946, Ryan Jefferson Jones (L) 161. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-MILLER-DAVID-R", "David R. Miller", "House District 55 (H55)", "2013-01-07", "2015-01-05", 2012, "House",
        "Official 2012 SOS statewide House summary, House District 55: David R. Miller (R) 2,374, Sherry Shelley (D) 1,473, Bethany K. Baldes (L) 227. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)", "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 28: Nathan Winters (R) Total 2,989. Official Fremont share 241; official Big Horn 831, Hot Springs 1,615, Park 302.")
    leg("WY-ALLEN-JIM", "Jim Allen", "House District 33 (H33)", "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 33: Jim Allen (R) 1,149, Andrea Clifford (D) 1,019. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-CAMPBELL-RITA", "Rita Campbell", "House District 34 (H34)", "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 34: Rita Campbell (R) 2,494. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 2,778. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-MILLER-DAVID-R", "David R. Miller", "House District 55 (H55)", "2015-01-05", "2017-01-02", 2014, "House",
        "Official 2014 SOS statewide House summary, House District 55: David R. Miller (R) 2,469. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTERS-NATHAN", "Nathan Winters", "House District 28 (H28)", "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): Nathan Winters (R) Total 3,510, Howard Samelson (D) 980. Official Fremont share Winters 295, Samelson 39.")
    leg("WY-ALLEN-JIM", "Jim Allen", "House District 33 (H33)", "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 33 (left column of the official two-column page with District 34): Jim Allen (R) 1,534, Sergio A. Maldonado, Sr. (D) 1,467. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-SALAZAR-TIM", "Tim Salazar", "House District 34 (H34)", "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 34 (right column of the official two-column page with District 33): Tim Salazar (R) 3,890. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 54 (right column of the official two-column page with District 53): Lloyd Charles Larsen (R) 2,780, Julia Stuble (D) 2,120. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-MILLER-DAVID-R", "David R. Miller", "House District 55 (H55)", "2017-01-02", "2019-01-07", 2016, "House",
        "Official 2016 SOS statewide House summary, House District 55 (left column of the official two-column page with District 56): David R. Miller (R) 3,384. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)", "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 28: John R. Winter (R) Total 2,906, Howie Samelson (D) 954. Official Fremont share Winter 278, Samelson 39. Official other shares: Big Horn 846–110, Hot Springs 1,471–743, Park 311–62. Official SOS name John R. Winter is not combined with earlier official SOS name Nathan Winters.")
    leg("WY-CLIFFORD-ANDREA", "Andrea Clifford", "House District 33 (H33)", "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 33 (left column): Andrea Clifford (D) 1,317, Jim Allen (R) 1,259. Fremont-only (official Fremont share equals the official Total).",
        party="Democratic")
    leg("WY-SALAZAR-TIM", "Tim Salazar", "House District 34 (H34)", "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 34 (right column of the official two-column page with District 33): Tim Salazar (R) 3,105. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 2,305, Mark Calhoun (D) 2,073. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-MILLER-DAVID-R", "David R. Miller", "House District 55 (H55)", "2019-01-07", "2021-01-04", 2018, "House",
        "Official 2018 SOS statewide House summary, House District 55: David R. Miller (R) 1,645, Bethany Baldes (L) 1,592. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)", "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 28 (right column of the official two-column page with District 27): John R. Winter (R) Total 3,769, Levi J. Shinkle (D) 816. Official Fremont share Winter 330, Shinkle 32.")
    leg("WY-CLIFFORD-ANDREA", "Andi Clifford", "House District 33 (H33)", "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 33 (left column): Andi Clifford (D) 1,434, Valaira Whiteman (R) 1,338, Clinton D. Wagon (I) 375. Fremont-only (official Fremont share equals the official Total). Official 2020 SOS prints Andi Clifford; official 2014 and 2018 SOS printed Andrea Clifford. Kept as one person with both official ballot names.",
        party="Democratic")
    leg("WY-OTTMAN-PEPPER-L", "Pepper L. Ottman", "House District 34 (H34)", "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 34 (right column of the official two-column page with District 33): Pepper L. Ottman (R) 4,070. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 54 (right column of the official two-column page with District 53): Lloyd Charles Larsen (R) 3,148, Kevin Wilson (D) 2,244. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-OAKLEY-EMBER", "Ember Oakley", "House District 55 (H55)", "2021-01-04", "2023-01-02", 2020, "House",
        "Official 2020 SOS statewide House summary, House District 55: Ember Oakley (R) 2,058, Bethany Baldes (L) 2,026. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)", "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,139, Kimberly M. Bartlett (D) 855. Official Fremont share Winter 259, Bartlett 32. Official other shares: Big Horn 644–90, Hot Springs 1,582–590, Park 654–143.")
    leg("WY-PENN-SARAH", "Sarah Penn", "House District 33 (H33)", "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 33: Sarah Penn (R) 1,077, Andi LeBeau (D) 867. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-OTTMAN-PEPPER-L", "Pepper L. Ottman", "House District 34 (H34)", "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 34: Pepper L. Ottman (R) 3,407. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 2,645, Jeff Martin (I) 1,560. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-OAKLEY-EMBER", "Ember Oakley", "House District 55 (H55)", "2023-01-02", "2025-01-06", 2022, "House",
        "Official 2022 SOS statewide House summary, House District 55: Ember Oakley (R) 1,798, Bethany Baldes (L) 1,175. Fremont-only (official Fremont share equals the official Total).")

    leg("WY-WINTER-JOHN-R", "John R. Winter", "House District 28 (H28)", "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Fremont share Winter 279, Alwin 45. Official other shares: Big Horn 920–85, Hot Springs 1,979–574, Park 808–153.")
    leg("WY-POSEY-IVAN-D", "Ivan D. Posey", "House District 33 (H33)", "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 33: Ivan D. Posey (D) 1,675, Sarah Penn (R) 1,210. Fremont-only (official Fremont share equals the official Total).",
        party="Democratic")
    leg("WY-OTTMAN-PEPPER-L", "Pepper L. Ottman", "House District 34 (H34)", "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 34: Pepper L. Ottman (R) 4,117. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 3,821. Fremont-only (official Fremont share equals the official Total).")
    leg("WY-GUGGENMOS-JOEL", "Joel Guggenmos", "House District 55 (H55)", "2025-01-06", "2027-01-04", 2024, "House",
        "Official 2024 SOS statewide House summary, House District 55: Joel Guggenmos (R) 2,858. Fremont-only (official Fremont share equals the official Total).")

    # 2026 elects (take office January 2027)
    leg("WY-HOGG-ALLEN", "Allen Hogg", "House District 28 (H28)", "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 28: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504. Official Fremont share Hogg 237, Alwin 22. Official other shares: Big Horn 655–66, Hot Springs 1,725–343, Park 692–73. Official Fremont clerk abstract: REP HOGG 237, DEM ALWIN 22.")
    leg("WY-POSEY-IVAN-D", "Ivan D. Posey", "House District 33 (H33)", "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 33: Ivan D. Posey (D) 1,383, Justin Morgan (R) 741. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: DEM POSEY 1,383, REP MORGAN 741.",
        party="Democratic")
    leg("WY-OTTMAN-PEPPER-L", "Pepper L. Ottman", "House District 34 (H34)", "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 34: Pepper L. Ottman (R) 2,930. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: REP OTTMAN 2,930.")
    leg("WY-LARSEN-LLOYD-CHARLES", "Lloyd Charles Larsen", "House District 54 (H54)", "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 3,156, Holly M. Butler (L) 794. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: REP LARSEN 3,156, LIB BUTLER 794.")
    leg("WY-MANNING-CARL", "Carl Manning", "House District 55 (H55)", "2027-01-04", "2029-01-01", 2026, "House",
        "Official 2026 SOS statewide House summary, House District 55: Carl Manning (R) 2,334. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: REP MANNING 2,334.")
    return terms


def county_terms():
    """Current holders from official county pages. 2026 elects from the official clerk abstract.
    Mid-term county history from 2016-2024 official canvasses is not fully keyed in this preview
    (the official 2024 abstract is a 77-page scan; earlier official canvasses are in the ARCA archive).
    Current terms are bounded through January 2027 where the official 2026 canvass elects a successor,
    or through the next odd-year January if the office was not on the 2026 ballot.
    """
    terms = []
    # Five-member commission, districts 1-5. 2026 ballot: districts 1, 3, and 4 only.
    # Official current page (retrieved 2026-11-24): D1 Clarence Thomas, D2 Chairman Larry Allen,
    # D3 Ron Fabrizius, D4 Vice-Chairman Michael Jones, D5 Jennifer Wilson.
    _add(terms, "WY-THOMAS-CLARENCE", "Clarence Thomas", "County Commissioner, District 1", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM, SRC_DIR],
         "Official commissioners page, retrieved 2026-11-24: Clarence Thomas, District 1. Official 2026 general elects Nicole A. Wagon. Exact 2022 canvass totals are not yet keyed from an official prior-year clerk abstract.",
         party="Republican", conf="medium")
    _add(terms, "WY-ALLEN-LARRY", "Larry Allen", "County Commissioner, District 2", "county",
         "2025-01-06", "2029-01-01", 2024, [SRC_COMM, SRC_DIR],
         "Official commissioners page, retrieved 2026-11-24: Larry Allen, Chairman, District 2. Not on the official 2026 general ballot. Exact 2024 canvass totals are not yet keyed from the official 2024 clerk abstract (77-page official canvass scan).",
         party="Republican", conf="medium")
    _add(terms, "WY-FABRIZIUS-RON", "Ron Fabrizius", "County Commissioner, District 3", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM, SRC_DIR],
         "Official commissioners page, retrieved 2026-11-24: Ron Fabrizius, District 3. Official 2026 general elects Ryan W. Stanley.",
         party="Republican", conf="medium")
    _add(terms, "WY-JONES-MICHAEL", "Michael Jones", "County Commissioner, District 4", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_COMM, SRC_DIR],
         "Official commissioners page, retrieved 2026-11-24: Michael Jones, Vice-Chairman, District 4. Official 2026 general elects Steff Kessler (official abstract REP KESSLER; official first name from the official 2026 primary Vote Center page 17, STEFF KESSLER 902, and the official 2026 primary sample ballot).",
         party="Republican", conf="medium")
    _add(terms, "WY-WILSON-JENNIFER", "Jennifer Wilson", "County Commissioner, District 5", "county",
         "2025-01-06", "2029-01-01", 2024, [SRC_COMM, SRC_DIR],
         "Official commissioners page, retrieved 2026-11-24: Jennifer Wilson, District 5. Not on the official 2026 general ballot.",
         party="Republican", conf="medium")
    _add(terms, "WY-WAGON-NICOLE-A", "Nicole A. Wagon", "County Commissioner, District 1", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, Commissioner District 1: IND WAGON 810, REP MOSSBURG 576, write-ins 16, contest totals 1,613. Official general filing list names Nicole A. Wagon (UAF). Takes office January 2027.",
         party="Independent")
    _add(terms, "WY-STANLEY-RYAN-W", "Ryan W. Stanley", "County Commissioner, District 3", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_PRI],
         "Official 2026 Fremont clerk abstract, Commissioner District 3: REP STANLEY 2,050, write-ins 62, contest totals 2,479. Official 2026 primary precinct summary names Ryan W. Stanley. Takes office January 2027.",
         party="Republican")
    _add(terms, "WY-KESSLER-STEFF", "Steff Kessler", "County Commissioner, District 4", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_PRI_VC, SRC_2026_PRI_BALLOT],
         "Official 2026 Fremont clerk abstract, Commissioner District 4: REP KESSLER 2,561, write-ins 75, contest totals 3,310. Official first name Steff is from the official 2026 primary Vote Center (page 17 of 49, OFFICIAL PRIMARY ELECTION BALLOT, 6 of 6 precincts reporting, footer 08/21/2026 03:08PM): STEFF KESSLER 902, J. D. CARPER 555, CHRISTY HIRASAWA GABEL 356, JIM TAYLOR 294, JEFFREY A. YOUNG 238, write-ins 5, contest totals 2,525, and from the official 2026 primary sample ballot listing Steff Kessler. Takes office January 2027.",
         party="Republican")

    _add(terms, "WY-FREESE-JULIE-A", "Julie A. Freese", "County Clerk", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CLERK, SRC_DIR, SRC_2026_MIN],
         "Official clerk page and official directory, retrieved 2026-11-24, name Julie Freese. Official Nov. 5, 2026 canvass minutes name County Clerk Julie A. Freese. Official 2026 general: REP FREESE 10,919, re-elected.",
         party="Republican")
    _add(terms, "WY-FREESE-JULIE-A", "Julie A. Freese", "County Clerk", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, County Clerk: REP FREESE 10,919, write-ins 147, contest totals 13,236.",
         party="Republican")
    _add(terms, "WY-ANDERSON-JAMES-A", "James A. Anderson", "County Treasurer", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_TREAS, SRC_DIR],
         "Official treasurer page, retrieved 2026-11-24, names James A. Anderson (also Jim Anderson). Official 2026 general: REP ANDERSON 10,339, re-elected.",
         party="Republican")
    _add(terms, "WY-ANDERSON-JAMES-A", "James A. Anderson", "County Treasurer", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, County Treasurer: REP ANDERSON 10,339, write-ins 108, contest totals 13,236.",
         party="Republican")
    _add(terms, "WY-RIGGS-ELLA-M", "Ella M. Riggs", "County Assessor", "county",
         "2026-09-29", "2027-01-04", 2026, [SRC_ASSESSOR],
         "Official assessor page, retrieved 2026-11-24: Ella M. Riggs - Appointed Interim County Assessor on September 29, 2026. The official directory card still listed Tara Berg and was treated as stale. Official 2026 general elects Ella M. Riggs.",
         party="Republican", how="appointed")
    _add(terms, "WY-RIGGS-ELLA-M", "Ella M. Riggs", "County Assessor", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, County Assessor: REP RIGGS 10,373, write-ins 102, contest totals 13,236.",
         party="Republican")
    _add(terms, "WY-LEE-RYAN", "Ryan Lee", "County Sheriff", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_SHERIFF],
         "Official sheriff page, retrieved 2026-11-24: Sheriff Ryan Lee was elected and sworn into Office on January 7, 2019, as the 25th Sheriff of Fremont County. Still the official current sheriff as of 2026-11-24. Official 2026 general elects John Zerga. The 2023 start date follows the ordinary four-year sheriff cycle after the 2022 general; the official 2022 canvass totals are not yet keyed.",
         party="Republican", conf="medium")
    _add(terms, "WY-ZERGA-JOHN", "John Zerga", "County Sheriff", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_PRI],
         "Official 2026 Fremont clerk abstract, County Sheriff: REP ZERGA 10,656, write-ins 314, contest totals 13,236. Official 2026 primary precinct summary names John Zerga. Takes office January 2027.",
         party="Republican")
    _add(terms, "WY-WYATT-MICAH", "Micah Wyatt", "County Attorney", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_ATTORNEY, SRC_DIR],
         "Official attorney page and official directory, retrieved 2026-11-24, name Micah Wyatt, County Attorney. Official 2026 general: REP WYATT 10,078, re-elected.",
         party="Republican", conf="medium")
    _add(terms, "WY-WYATT-MICAH", "Micah Wyatt", "County Attorney", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, County Attorney: REP WYATT 10,078, write-ins 191, contest totals 13,236.",
         party="Republican")
    _add(terms, "WY-SANCHEZ-AMANDA-R", "Amanda R. Sanchez", "Clerk of District Court", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CDC, SRC_DIR],
         "Official CDC page and official directory, retrieved 2026-11-24, name Amanda Sanchez. Official 2026 primary precinct summary uses AMANDA R. SANCHEZ. Official 2026 general: REP SANCHEZ 10,288, re-elected.",
         party="Republican", conf="medium")
    _add(terms, "WY-SANCHEZ-AMANDA-R", "Amanda R. Sanchez", "Clerk of District Court", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_PRI],
         "Official 2026 Fremont clerk abstract, Clerk of District Court: REP SANCHEZ 10,288, write-ins 81, contest totals 13,236.",
         party="Republican")
    _add(terms, "WY-IVIE-ERIN", "Erin Ivie", "County Coroner", "county",
         "2023-01-02", "2027-01-04", 2022, [SRC_CORONER, SRC_DIR],
         "Official coroner page and official directory, retrieved 2026-11-24, name Erin Ivie. Official 2026 general: REP IVIE 10,825, re-elected.",
         party="Republican", conf="medium")
    _add(terms, "WY-IVIE-ERIN", "Erin Ivie", "County Coroner", "county",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, County Coroner: REP IVIE 10,825, write-ins 87, contest totals 13,236.",
         party="Republican")
    return terms


def judicial_terms():
    terms = []
    # 9th JD, shared with Sublette and Teton. Official Fremont 2026 named retention.
    # Use 2027-01-04 / 2031-01-06 for the new retention term (standard).
    _add(terms, "WY-CONDER-JASON-M", "Jason M. Conder", "District Judge, 9th Judicial District", "judicial",
         "2023-01-02", "2027-01-04", 2022, [SRC_COURT],
         "Official Wyoming Judicial Branch 9th Judicial District (Fremont) names Jason M. Conder, already used from official court pages in the Sublette and Teton histories. Official 2026 Fremont clerk abstract, JDG A DIST CRT CONDER: YES 8,527, NO 2,343, contest totals 13,236.",
         conf="high")
    _add(terms, "WY-CONDER-JASON-M", "Jason M. Conder", "District Judge, 9th Judicial District", "judicial",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_COURT],
         "Official 2026 Fremont clerk abstract, JDG A DIST CRT CONDER: YES 8,527, NO 2,343. Retained. Full name Jason M. Conder is from the official 9th Judicial District court page (also used in official Sublette and Teton histories).")
    _add(terms, "WY-WEISMAN-ERIN-E", "Erin E. Weisman", "Circuit Judge, 9th Judicial District", "judicial",
         "2023-01-02", "2027-01-04", 2022, [SRC_COURT],
         "Official court page name Erin E. Weisman, already used in the official Teton and Sublette histories. Official 2026 Fremont clerk abstract, CIRCUIT CRT WEISMAN: YES 8,229, NO 2,355.",
         conf="high")
    _add(terms, "WY-WEISMAN-ERIN-E", "Erin E. Weisman", "Circuit Judge, 9th Judicial District", "judicial",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_COURT],
         "Official 2026 Fremont clerk abstract, CIRCUIT CRT WEISMAN: YES 8,229, NO 2,355. Retained. Full name Erin E. Weisman is from the official court page.")
    _add(terms, "WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "Circuit Judge, 9th Judicial District", "judicial",
         "2023-01-02", "2027-01-04", 2022, [SRC_COURT],
         "Official court page name Jefferson Boone Coombs, already used in the official Teton and Sublette histories. Official 2026 Fremont clerk abstract, CIRCUIT CRT COOMBS: YES 8,014, NO 2,496.",
         conf="high")
    _add(terms, "WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "Circuit Judge, 9th Judicial District", "judicial",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_COURT],
         "Official 2026 Fremont clerk abstract, CIRCUIT CRT COOMBS: YES 8,014, NO 2,496. Retained. Full name Jefferson Boone Coombs is from the official court page.")
    return terms


def municipal_terms():
    terms = []
    # Municipal elects use 2027-01-04 so the shared live-JSON helper pairs them. Official Lander and Hudson pages print terms expiring 12/2026 or 12/31/2026.

    # Lander — official council page
    _add(terms, "WY-WHITE-MISSY", "Missy White", "City of Lander Mayor", "municipal",
         "2025-03-01", "2027-01-04", 2025, [SRC_LANDER],
         "Official City of Lander Mayor and City Council page, retrieved 2026-11-24: Missy White, Mayor, Elected 03/2025, Term Expires 12/2026. Exact March 2025 start day is not printed; 2025-03-01 is used only as a start no later than the official election month. Official 2026 general elects Michelle B. Motherway.",
         conf="medium")
    _add(terms, "WY-MOTHERWAY-MICHELLE-B", "Michelle B. Motherway", "City of Lander Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, Lander Mayor: MICHELLE B. MOTHERWAY 1,535, MISSY WHITE 1,355, write-ins 14, contest totals 2,983. Takes office January 2027.")
    _add(terms, "WY-HAHN-JOSH", "Josh Hahn", "City of Lander Council Ward 1", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: Josh Hahn, Council Member, Ward 1, Elected 11/2022, Term Expires 12/2026. Official 2026 general elects George Case in Ward 1.",
         conf="medium")
    _add(terms, "WY-CASE-GEORGE", "George Case", "City of Lander Council Ward 1", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Lander Council Ward 1: GEORGE CASE 524, JENNY YOUNG 303, write-ins 7, contest totals 893.")
    _add(terms, "WY-HAHN-DAN", "Dan Hahn", "City of Lander Council Ward 1", "municipal",
         "2025-01-06", "2029-01-01", 2020, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: Dan Hahn, Council Member, Ward 1, Elected 11/2020, Term Expires 12/2028. The 2025-01-06 start used here is the January after the 2024 mid-cycle point; the official page gives the November 2020 election and December 2028 expiration only.",
         conf="medium")
    _add(terms, "WY-CASSADY-CHAD", "Chad Cassady", "City of Lander Council Ward 2", "municipal",
         "2025-05-13", "2027-01-04", 2025, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: Chad Cassady, Council Member, Ward 2, Oath of Office 5/13/25, Term Expires 12/2026. Official 2026 general: CHAD CASSADY 407, re-elected.",
         conf="high")
    _add(terms, "WY-CASSADY-CHAD", "Chad Cassady", "City of Lander Council Ward 2", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Lander Council Ward 2: CHAD CASSADY 407, JESSE T. GROSINGER 298, write-ins 8, contest totals 879.")
    _add(terms, "WY-STUBLE-JULIA", "Julia Stuble", "City of Lander Council Ward 2", "municipal",
         "2025-01-06", "2029-01-01", 2020, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: Julia Stuble, Council Member, Ward 2, Elected 11/2020, Term Expires 12/2028.",
         conf="medium")
    _add(terms, "WY-LARSEN-JOHN", "John Larsen", "City of Lander Council Ward 3", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: John Larsen, Council Member, Ward 3, Elected 11/2022, Term Expires 12/2026. Official 2026 general elects Sarah L. Schlosser.",
         conf="medium")
    _add(terms, "WY-SCHLOSSER-SARAH-L", "Sarah L. Schlosser", "City of Lander Council Ward 3", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, Lander Council Ward 3: SARAH L. SCHLOSSER 594, MICHAEL KUSIEK 331, write-ins 56, contest totals 1,211. The official Vote Center totals 331 / 594 confirm the alignment (OCR of the scanned abstract initially garbled Kusiek's total).")
    _add(terms, "WY-COX-MELINDA", "Melinda Cox", "City of Lander Council Ward 3", "municipal",
         "2025-01-06", "2029-01-01", 2020, [SRC_LANDER],
         "Official Lander page, retrieved 2026-11-24: Melinda Cox, Council Member, Ward 3, Elected 11/2020, Term Expires 12/2028.",
         conf="medium")

    # Riverton
    _add(terms, "WY-HANCOCK-TIM", "Tim Hancock", "City of Riverton Mayor", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_RIV_MAYOR, SRC_RIV_ELECTED],
         "Official Meet the Mayor page, retrieved 2026-11-24: Mayor Tim Hancock, Current Term 2023-2026. Official Elected Officials page names Mayor Timothy Hancock. Official 2026 general elects Michael V. (Mike) Bailey; Hancock won Riverton Ward 3 council.",
         conf="high")
    _add(terms, "WY-BAILEY-MICHAEL-V", "Michael V. (Mike) Bailey", "City of Riverton Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Riverton Mayor: MICHAEL V (MIKE) BAILEY 1,530, DARYL WEST 1,067, write-ins 38, contest totals 2,781.")
    _add(terms, "WY-JOHNSON-KAREN", "Karen Johnson", "City of Riverton Council Ward 1", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_RIV_COUNCIL, SRC_RIV_ELECTED],
         "Official Meet the Council page, retrieved 2026-11-24: Ward 1 Council Member Karen Johnson, Current Term 2025-2028.",
         conf="high")
    _add(terms, "WY-LARSON-KYLE-M", "Kyle M. Larson", "City of Riverton Council Ward 1", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_RIV_COUNCIL],
         "Official Meet the Council page, retrieved 2026-11-24: Ward 1 Council Member Kyle Larson, Current Term 2023-2026. Official 2026 general: KYLE M. LARSON 344, re-elected.",
         conf="high")
    _add(terms, "WY-LARSON-KYLE-M", "Kyle M. Larson", "City of Riverton Council Ward 1", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Riverton Ward 1: KYLE M. LARSON 344, PIRAM DURAN 219, write-ins 4, contest totals 634.")
    _add(terms, "WY-PRESTON-JERIKA", "Jerika Preston", "City of Riverton Council Ward 2", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_RIV_COUNCIL],
         "Official Meet the Council page, retrieved 2026-11-24: Ward 2 Council Member Jerika Preston, Current Term 2025-2028.",
         conf="high")
    _add(terms, "WY-BORDERS-KARLA", "Karla Borders", "City of Riverton Council Ward 2", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_RIV_COUNCIL],
         "Official Meet the Council page, retrieved 2026-11-24: Ward 2 Council Member Karla Borders, Current Term 2023-2026. Official 2026 general elects Chancey Wilczewski.",
         conf="high")
    _add(terms, "WY-WILCZEWSKI-CHANCEY", "Chancey Wilczewski", "City of Riverton Council Ward 2", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Riverton Ward 2: CHANCEY WILCZEWSKI 698, write-ins 8, contest totals 938.")
    _add(terms, "WY-BAILEY-MICHAEL-V", "Michael V. (Mike) Bailey", "City of Riverton Council Ward 3", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_RIV_COUNCIL, SRC_RIV_ELECTED],
         "Official Meet the Council and Elected Officials pages, retrieved 2026-11-24: Ward 3 Council Member Mike Bailey, Current Term 2023-2026. Official 2026 general elects Bailey mayor and Tim Hancock to Ward 3.",
         conf="high")
    _add(terms, "WY-HANCOCK-TIM", "Tim Hancock", "City of Riverton Council Ward 3", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Riverton Ward 3: TIM HANCOCK 924, write-ins 39, contest totals 1,209.")
    _add(terms, "WY-CARR-ERIC", "Eric Carr", "City of Riverton Council Ward 3", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_RIV_COUNCIL],
         "Official Meet the Council page, retrieved 2026-11-24: Ward 3 Council Member Eric Carr, Current Term 2025-2028.",
         conf="high")

    # Dubois
    _add(terms, "WY-NEVEAUX-PATRICIA", "Patricia Neveaux", "Town of Dubois Mayor", "municipal",
         "2023-01-02", "2027-01-04", None, [SRC_DUBOIS],
         "Official Town of Dubois Town Council page, retrieved 2026-11-24, Governing Body: Patricia Neveaux, Mayor. Official 2026 general elects David Furman. The official page does not print a term start; the end date is the January after the official 2026 mayoral canvass.",
         conf="medium")
    _add(terms, "WY-FURMAN-DAVID", "David Furman", "Town of Dubois Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk Vote Center / abstract, Dubois Mayor: DAVID FURMAN 213, PATRICIA NEVEAUX 202, contest totals 421. The scanned-abstract OCR dropped a digit (printing 23); the official born-digital Vote Center totals 213–202 are used.")
    for pid, name in (("WY-LEE-RICK", "Rick Lee"), ("WY-LAHR-RANDY", "Randy Lahr"),
                      ("WY-YSEN-AMANDA", "Amanda Ysen"), ("WY-THOMPSON-BRUCE-JOHN", "Bruce John Thompson")):
        _add(terms, pid, name, "Town of Dubois Council", "municipal",
             "2023-01-02", "2027-01-04", None, [SRC_DUBOIS],
             "Official Town of Dubois Town Council page, retrieved 2026-11-24, Governing Body council members: Rick Lee, Randy Lahr, Amanda Ysen, and Bruce John Thompson. Official 2026 general (vote for 2) elects Mike Strasser 327 and Amanda Ysen 255. Which two of the other three official current members were on the expiring cycle is not printed on the official 2026 ballot, so all four current official members are bounded through January 2027 and only the two official 2026 winners are encoded as January 2027 elects.",
             conf="medium")
    _add(terms, "WY-STRASSER-MIKE", "Mike Strasser", "Town of Dubois Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Dubois Council (vote for 2): MIKE STRASSER 327, AMANDA YSEN 255, write-ins 12, contest totals 842.")
    _add(terms, "WY-YSEN-AMANDA", "Amanda Ysen", "Town of Dubois Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Dubois Council (vote for 2): AMANDA YSEN 255, MIKE STRASSER 327.")

    # Shoshoni
    _add(terms, "WY-HIGHSMITH-JOEL", "Joel Highsmith", "Town of Shoshoni Mayor", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_SHOSHONI],
         "Official Town of Shoshoni Mayor & Council page, retrieved 2026-11-24: Joel Highsmith, Mayor, Term: 2023-2027. Official 2026 general elects Ronald W. Ankeny.",
         conf="high")
    _add(terms, "WY-ANKENY-RONALD-W", "Ronald W. Ankeny", "Town of Shoshoni Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Shoshoni Mayor: RONALD W. ANKENY 105, JORDAN A. WHITENER 92, write-ins 1, contest totals 202.")
    _add(terms, "WY-NORDEEN-MARK", "Mark Nordeen", "Town of Shoshoni Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_SHOSHONI],
         "Official Shoshoni Mayor & Council page, retrieved 2026-11-24: Mark Nordeen, Council Member, Term: 2025-2029.",
         conf="high")
    _add(terms, "WY-WHITENER-JORDAN", "Jordan Whitener", "Town of Shoshoni Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_SHOSHONI],
         "Official Shoshoni Mayor & Council page, retrieved 2026-11-24: Jordan Whitener, Council Member, Term: 2025-2029. Official 2026 general lists JORDAN A. WHITENER as a mayoral candidate (92 votes); the council term continues.",
         conf="high")
    _add(terms, "WY-STETLER-JACOB-Z", "Jacob Z. Stetler", "Town of Shoshoni Council", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_SHOSHONI],
         "Official Shoshoni page, retrieved 2026-11-24: Jake Z. Stetler, Council Member, Term: 2023-2027. Official 2026 general: JACOB Z STETLER 120, re-elected.",
         conf="high")
    _add(terms, "WY-STETLER-JACOB-Z", "Jacob Z. Stetler", "Town of Shoshoni Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract / Vote Center, Shoshoni Council (vote for 2): JACOB Z STETLER 120, TAMMIE A. HARDTKE 94, LINDA (KAT) MANZ 73, JENNIFER Y SCHANNO 51, write-ins 7, contest totals 404. The scanned-abstract OCR dropped a digit on Hardtke (printing 4); the official Vote Center total 94 is used.")
    _add(terms, "WY-HARDTKE-TAMMIE-A", "Tammie A. Hardtke", "Town of Shoshoni Council", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_SHOSHONI],
         "Official Shoshoni page, retrieved 2026-11-24: Tammie Hardtke, Council Member, Term: 2023-2027. Official 2026 general: TAMMIE A. HARDTKE 94, re-elected.",
         conf="high")
    _add(terms, "WY-HARDTKE-TAMMIE-A", "Tammie A. Hardtke", "Town of Shoshoni Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk Vote Center, Shoshoni Council (vote for 2): TAMMIE A. HARDTKE 94, JACOB Z STETLER 120.")

    # Hudson — official hudsonwy.org (not the Massachusetts CivicPlus site townofhudson.org)
    _add(terms, "WY-OLER-SHERRY", "Sherry Oler", "Town of Hudson Mayor", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_HUDSON],
         "Official Town of Hudson Government page, retrieved 2026-11-24: Mayor Sherry Oler, Term expires 12/31/2026. Official 2026 general elects Marilyn V. Robinson.",
         conf="high")
    _add(terms, "WY-ROBINSON-MARILYN-V", "Marilyn V. Robinson", "Town of Hudson Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Hudson Mayor: MARILYN V. ROBINSON 95, write-ins 15, contest totals 142.")
    _add(terms, "WY-HAMILTON-BRADY", "Brady Hamilton", "Town of Hudson Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_HUDSON],
         "Official Town of Hudson Government page, retrieved 2026-11-24: Brady Hamilton, Council President, Term expires 12/31/2028.",
         conf="high")
    _add(terms, "WY-KUMMER-KEVIN", "Kevin Kummer", "Town of Hudson Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_HUDSON],
         "Official Town of Hudson Government page, retrieved 2026-11-24: Councilman Kevin Kummer, Term expires 12/31/2028.",
         conf="high")
    _add(terms, "WY-BONELLA-ZEKE", "Zeke Bonella", "Town of Hudson Council", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_HUDSON],
         "Official Town of Hudson Government page, retrieved 2026-11-24: Councilman Zeke Bonella, Term expires 12/31/2026. Official 2026 general elects Daniel (Danny) Svilar and re-elects Helen J. Gordon (vote for 2).",
         conf="high")
    _add(terms, "WY-GORDON-HELEN-J", "Helen J. Gordon", "Town of Hudson Council", "municipal",
         "2023-01-02", "2027-01-04", 2022, [SRC_HUDSON],
         "Official Town of Hudson Government page, retrieved 2026-11-24: Councilwoman Helen Gordon, Term expires 12/31/2026. Official 2026 general: HELEN J GORDON 67, re-elected.",
         conf="high")
    _add(terms, "WY-GORDON-HELEN-J", "Helen J. Gordon", "Town of Hudson Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract / Vote Center, Hudson Council (vote for 2): HELEN J GORDON 67, DANIEL (DANNY) SVILAR 67, JERRICA B FLOM 52, JERRY D. TUCKER 47, write-ins 3, contest totals 284. Official Vote Center totals are used for Tucker's 47 (scanned-abstract OCR was unreliable on that figure).")
    _add(terms, "WY-SVILAR-DANIEL", "Daniel (Danny) Svilar", "Town of Hudson Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract / Vote Center, Hudson Council (vote for 2): DANIEL (DANNY) SVILAR 67, HELEN J GORDON 67.")

    # Pavillion — no official town website was found. Official 2024 canvass: mayor-style 2-year contest is write-in only with no certified named winner (current mayor stays Not yet collected). Official 2024 council (vote for 2): BARRETT 54, ROBINSON 52 (last names only on the official table). Official 2026 elects are encoded.
    _add(terms, "WY-BARRETT-PAVILLION", "Barrett", "Town of Pavillion Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 Fremont clerk canvass, Pavillion Council (vote for 2): BARRETT 54, ROBINSON 52, write-ins 3, undervotes 79, contest totals 188 (Custom Table Report page of the official 77-page canvass). The official canvass prints last names only; first names were not found on an official 2022 canvass, official county minutes, or official municipal canvass in this pass. Official ARCA 2022 clerk canvass was not successfully pulled.")
    _add(terms, "WY-ROBINSON-PAVILLION", "Robinson", "Town of Pavillion Council", "municipal",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 Fremont clerk canvass, Pavillion Council (vote for 2): ROBINSON 52, BARRETT 54. Distinct from Marilyn V. Robinson (Town of Hudson). Official canvass last name only.")
    _add(terms, "WY-EMERSON-LESTER-R", "Lester R. Emerson", "Town of Pavillion Mayor", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Pavillion Mayor: LESTER R EMERSON 46, write-ins 8, contest totals 65. The official 2024 canvass Pavillion 2-year contest is write-in only with no certified named winner. No official Town of Pavillion website was found. Official ARCA 2022 clerk canvass was not successfully pulled. The current mayor through January 2027 stays Not yet collected.")
    _add(terms, "WY-STOLDT-JACQUE-L", "Jacque L. Stoldt", "Town of Pavillion Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, Pavillion Council (vote for 2): JACQUE L STOLDT 46, MANDI REYNOLDS 35, write-ins 3, contest totals 130. The two 2024 council winners (Barrett, Robinson) are holdovers; these 2026 elects take the seats that were up in 2026.")
    _add(terms, "WY-REYNOLDS-MANDI", "Mandi Reynolds", "Town of Pavillion Council", "municipal",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS],
         "Official 2026 Fremont clerk abstract, Pavillion Council (vote for 2): MANDI REYNOLDS 35, JACQUE L STOLDT 46.")
    return terms


def school_terms():
    """Official current boards (district pages, Wayback, official handbook, Highbond)
    cross-checked with the official 2024 canvass, plus official 2026 elects.
    Official 2022 ARCA canvass was not successfully pulled. Names are never invented.
    """
    terms = []
    # ----- FCSD #1 Lander (official 7-member board; official page term expires 12/01/2026 or 12/1/2028,
    # mapped to January 2027 / January 2029 in the same way other Fremont municipal pages that print December are handled)
    _add(terms, "WY-JACOBS-TAYLOR", "Taylor Jacobs", "Fremont County School District #1 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD1, SRC_2024_CANV],
         "Official FCSD #1 Governing Board page (Wayback 2026-10-21): Taylor Jacobs, Chairperson, term expires 12/1/2028. Official 2024 canvass, School Trustees Lander #1 (vote for 3): JACOBS 2,842, JENSEN 2,732, GANS 2,652, TILTON 2,475, ARBERRY 2,280, MCCLANE or as printed 2,177, write-ins 48, contest totals 18,735.")
    _add(terms, "WY-GANS-MARA", "Mara Gans", "Fremont County School District #1 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD1, SRC_2024_CANV],
         "Official FCSD #1 Governing Board page (Wayback 2026-10-21): Mara Gans, term expires 12/01/2028. Official 2024 canvass winner GANS 2,652.")
    _add(terms, "WY-MCCONNELL-MIKE", "Mike McConnell", "Fremont County School District #1 Trustee", "schools",
         "2023-01-02", "2027-01-04", 2022, [SRC_FCSD1],
         "Official FCSD #1 Governing Board page (Wayback 2026-10-21): Mike McConnell, Vice Chairperson, term expires 12/01/2026. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Re-elected on the official 2026 canvass.",
         conf="medium")
    for pid, name in (
        ("WY-HARMS-KAREN", "Karen Harms"),
        ("WY-KAIL-JARED", "Jared Kail"),
        ("WY-AYERS-MATT", "Matt Ayers"),
        ("WY-BREW-AILEEN", "Aileen Brew"),
    ):
        _add(terms, pid, name, "Fremont County School District #1 Trustee", "schools",
             "2023-01-02", "2027-01-04", 2022, [SRC_FCSD1],
             f"Official FCSD #1 Governing Board page (Wayback 2026-10-21): {name}, term expires 12/01/2026. Not among the official 2026 winners. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Official page expiration is printed 12/01/2026 and is mapped to January 2027 for pairing with 2026 elects.",
             conf="medium")
    # 2026 elects
    _add(terms, "WY-WESTON-BREANNE-N", "Breanne N. Weston", "Fremont County School District #1 Trustee", "schools",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustee Lander #1 2-year: BREANNE N. WESTON 3,262, write-ins 42, contest totals 5,050. Official filing lists the office as Trustee-2 YR UNEXPIRED.")
    for pid, name, votes in (
        ("WY-GREENE-MARY", "Mary Greene", "2,515"),
        ("WY-MCCONNELL-MIKE", "Mike McConnell", "2,125"),
        ("WY-STRIKE-KATE", "Kate Strike", "2,060"),
        ("WY-CHAPIN-JEFF", "Jeff Chapin", "2,004"),
    ):
        _add(terms, pid, name, "Fremont County School District #1 Trustee", "schools",
             "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING, SRC_2026_VC],
             "Official 2026 Fremont clerk abstract, School Trustees Lander #1 (vote for 4): Mary Greene 2,515, Mike McConnell 2,125, Kate Strike 2,060, Jeff Chapin 2,004, Matt Ayers 1,920, Sarah M. Adams 1,629, Austin Shields 1,019, Zachary Hamilton Mahlum 752, Rebekah Lynn Hoyt 697, write-ins 63, contest totals 20,200. Official Vote Center totals are used where scanned-abstract OCR dropped digits (Hoyt 697, Mahlum 752). "
             f"This term is the official winner {name} ({votes}).")

    # ----- FCSD #2 Dubois (official 7-member board)
    _add(terms, "WY-SELLERS-JANEAN", "Janean Sellers", "Fremont County School District #2 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD2, SRC_2024_CANV],
         "Official FCSD #2 Governing Board page: Janean Sellers, Chair. Official 2024 canvass, School Trustees Dubois #2 (vote for 3): VERMEIRE 715, SELLERS 688, NIELSEN 687, write-ins 25, contest totals 3,657. Nielsen is not on the official current board page and is not listed as a current holder.")
    _add(terms, "WY-VERMEIRE-LEAH", "Leah Vermeire", "Fremont County School District #2 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD2, SRC_2024_CANV],
         "Official FCSD #2 Governing Board page: Leah Vermeire. Official 2024 canvass winner VERMEIRE 715.")
    _add(terms, "WY-POLMANTEER-NICOLE", "Nicole Polmanteer", "Fremont County School District #2 Trustee", "schools",
         "2025-01-06", "2027-01-04", 2024, [SRC_FCSD2, SRC_2024_CANV],
         "Official FCSD #2 Governing Board page: Nicole Polmanteer. Official 2024 canvass, Dubois #2 2-year term (vote for 2): POLMANTEER 748 and a second named winner, contest totals 2,438. Re-elected to a four-year term on the official 2026 canvass.")
    for pid, name, year, conf in (
        ("WY-LITTLER-LIBBY", "Libby Littler", 2022, "medium"),
        ("WY-ROGERS-JUDY", "Judy Rogers", 2022, "medium"),
        ("WY-JUDD-JILL", "Jill Judd", 2022, "medium"),
        ("WY-HESS-SHAWN", "Shawn Hess", 2022, "medium"),
    ):
        _add(terms, pid, name, "Fremont County School District #2 Trustee", "schools",
             "2023-01-02", "2027-01-04", year, [SRC_FCSD2],
             f"Official FCSD #2 Governing Board page: {name}. Not a named official 2024 four-year winner. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Littler and Rogers were re-elected on the official 2026 canvass; Judd and Hess were not.",
             conf=conf)
    _add(terms, "WY-LINDSEY-BRAD", "Brad Lindsey", "Fremont County School District #2 Trustee", "schools",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustee Dubois #2 2-year unexpired (vote for 1): BRAD LINDSEY 410, ALI JO HEDGES 318, write-ins 5, total votes cast 733.")
    for pid, name, votes in (
        ("WY-ROGERS-JUDY", "Judy Rogers", "593"),
        ("WY-POLMANTEER-NICOLE", "Nicole Polmanteer", "544"),
        ("WY-BAKER-TINA", "Tina Baker", "498"),
        ("WY-LITTLER-LIBBY", "Libby Littler", "453"),
    ):
        _add(terms, pid, name, "Fremont County School District #2 Trustee", "schools",
             "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
             "Official 2026 Fremont clerk abstract, School Trustees Dubois #2 (vote for 4): Judy Rogers 593, Nicole Polmanteer 544, Tina Baker 498, Libby Littler 453. "
             f"This term is the official winner {name} ({votes}).")

    # ----- FCSD #6 Wind River (official 2024 last names; official board page was a JS challenge wall; official 2022 canvass not pulled)
    _add(terms, "WY-EVANS", "Evans", "Fremont County School District #6 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Wind River #6 (vote for 4): EVANS 691, STOLL-BAKER 660, MCCANN 537, write-ins 92, undervotes 2,304, contest totals 4,284. Only three named candidates were printed; a handwritten annotation on the official table (Lindsay Curran 45) is not a certified printed winner and is not used. Official canvass last name only; an official first name was not confirmed from an archived official district board page (live Finalsite page was a JS challenge wall).")
    _add(terms, "WY-STOLL-BAKER", "Stoll-Baker", "Fremont County School District #6 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Wind River #6: STOLL-BAKER 660. Official canvass last name only.")
    _add(terms, "WY-MCCANN", "McCann", "Fremont County School District #6 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Wind River #6: MCCANN 537. Official canvass last name only.")
    _add(terms, "WY-KLEIN-JESSICA", "Jessica Klein", "Fremont County School District #6 Trustee", "schools",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustee Wind River #6 2-year: JESSICA KLEIN 600.")
    for pid, name, votes in (
        ("WY-LEONHARDT-DAWN", "Dawn Leonhardt", "481"),
        ("WY-BEFUS-DAVID", "David Befus", "444"),
        ("WY-HILL-VAN", "Van Hill", "429"),
    ):
        _add(terms, pid, name, "Fremont County School District #6 Trustee", "schools",
             "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
             "Official 2026 Fremont clerk abstract, School Trustees Wind River #6 (vote for 3): Dawn Leonhardt 481, David Befus 444, Van Hill 429. "
             f"This term is the official winner {name} ({votes}).")

    # ----- FCSD #14 (official Highbond current five; official 2024 winners match Redman, Singer, Underwood)
    _add(terms, "WY-UNDERWOOD-CARLTON", "Carlton Underwood", "Fremont County School District #14 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD14, SRC_2024_CANV],
         "Official FCSD #14 Highbond current member widget: Carlton Underwood. Official 2024 canvass, School Trustees WY Indian #14 (vote for 3): UNDERWOOD 227, SINGER 203, REDMAN 174, SAGE 165, WHITE 154, SHAKESPEARE 148, ROBINSON 143, CRAIG 96, LEBEAUX or as printed 94, write-ins 20, contest totals 1,773. The same official name also appears on the official CWC board.")
    _add(terms, "WY-SINGER-RICH", "Rich Singer", "Fremont County School District #14 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD14, SRC_2024_CANV],
         "Official FCSD #14 Highbond current member widget: Rich Singer. Official 2024 canvass winner SINGER 203.")
    _add(terms, "WY-REDMAN-TESSA", "Tessa Redman", "Fremont County School District #14 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD14, SRC_2024_CANV],
         "Official FCSD #14 Highbond current member widget: Tessa Redman. Official 2024 canvass winner REDMAN 174.")
    _add(terms, "WY-FRIDAY-SANFORD-D", "Sanford D. Friday", "Fremont County School District #14 Trustee", "schools",
         "2023-01-02", "2027-01-04", 2022, [SRC_FCSD14],
         "Official FCSD #14 Highbond current member widget: Sanford Friday. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Re-elected on the official 2026 canvass (Sanford D. Friday).",
         conf="medium")
    _add(terms, "WY-TROSPER-ARLINE", "Arline Trosper", "Fremont County School District #14 Trustee", "schools",
         "2023-01-02", "2027-01-04", 2022, [SRC_FCSD14],
         "Official FCSD #14 Highbond current member widget: Arline Trosper. Kept distinct from 2026 elect Willena Rosie Trosper. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium).",
         conf="medium")
    _add(terms, "WY-TROSPER-WILLENA-ROSIE", "Willena Rosie Trosper", "Fremont County School District #14 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees WY Indian #14 (vote for 2): WILLENA ROSIE TROSPER and SANFORD D. FRIDAY. Kept distinct from Arline Trosper.")
    _add(terms, "WY-FRIDAY-SANFORD-D", "Sanford D. Friday", "Fremont County School District #14 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees WY Indian #14: SANFORD D. FRIDAY, re-elected.")

    # ----- FCSD #21 Fort Washakie (official 2025-2026 handbook five; official 2024 winners Ferris, Snyder, Washakie)
    _add(terms, "WY-FERRIS-KAY", "Kay Ferris", "Fremont County School District #21 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD21, SRC_2024_CANV],
         "Official FCSD #21 2025-2026 handbook: Kay Ferris, Vice Chairman. Official 2024 canvass, School Trustees Ft Washakie #21 (vote for 3): WASHAKIE 189, SNYDER 182, FERRIS 142, WEED 136, LARGE 122, HILL 119, HEREFORD 99, a second FERRIS 83, LAMBERT 76, write-ins 20, contest totals 1,542.")
    _add(terms, "WY-SNYDER-DAVID", "David Snyder", "Fremont County School District #21 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD21, SRC_2024_CANV],
         "Official FCSD #21 2025-2026 handbook: David Snyder, Member. Official 2024 canvass winner SNYDER 182.")
    _add(terms, "WY-WASHAKIE-BONNIE", "Bonnie Washakie", "Fremont County School District #21 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD21, SRC_2024_CANV],
         "Official FCSD #21 2025-2026 handbook: Bonnie Washakie, Member. Official 2024 canvass winner WASHAKIE 189.")
    _add(terms, "WY-LECLAIR-TEX", "Tex LeClair", "Fremont County School District #21 Trustee", "schools",
         "2023-01-02", "2027-01-04", 2022, [SRC_FCSD21],
         "Official FCSD #21 2025-2026 handbook: Tex LeClair, Chairman. Not a named official 2024 winner. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). The official handbook is for the 2025-2026 school year and is the latest official board roster collected.",
         conf="medium")
    _add(terms, "WY-MANN-CARLA", "Carla Mann", "Fremont County School District #21 Trustee", "schools",
         "2023-01-02", "2027-01-04", 2022, [SRC_FCSD21],
         "Official FCSD #21 2025-2026 handbook: Carla Mann, Treasurer. Not a named official 2024 winner. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium).",
         conf="medium")
    _add(terms, "WY-HILL-JAKE", "Jake Hill", "Fremont County School District #21 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees Ft Washakie #21 (vote for 2): JAKE HILL and CLINTON D. WAGON. Kept distinct from Van Hill (FCSD #6).")
    _add(terms, "WY-WAGON-CLINTON-D", "Clinton D. Wagon", "Fremont County School District #21 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees Ft Washakie #21: CLINTON D. WAGON. Kept distinct from Nicole A. Wagon.")

    # ----- FCSD #24 Shoshoni (official 2024 last names; official BoardDocs/Highbond pages did not yield a current roster)
    _add(terms, "WY-HAUN", "Haun", "Fremont County School District #24 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Shoshoni #24 (vote for 3): HAUN 425, PEREGOY 385, CRIMM 370, KONIJA 283, write-ins 8, contest totals 2,160. Official canvass last name only; official BoardDocs and Highbond pages did not yield a current first-name roster.")
    _add(terms, "WY-PEREGOY", "Peregoy", "Fremont County School District #24 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Shoshoni #24: PEREGOY 385. Official canvass last name only.")
    _add(terms, "WY-CRIMM", "Crimm", "Fremont County School District #24 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Shoshoni #24: CRIMM 370. Official canvass last name only.")
    for pid, name, votes in (
        ("WY-THOMPSON-LYNN-A", "Lynn A. Thompson", "379"),
        ("WY-MARTIN-LAURA", "Laura Martin", "358"),
        ("WY-EDGEINGTON-KRIS", "Kris Edgeington", "304"),
        ("WY-ENGUM-HILARY", "Hilary Engum", "229"),
    ):
        _add(terms, pid, name, "Fremont County School District #24 Trustee", "schools",
             "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
             "Official 2026 Fremont clerk abstract, School Trustees Shoshoni #24 (vote for 4): Lynn A. Thompson 379, Laura Martin 358, Kris Edgeington 304, Hilary Engum 229. Laura Martin is not Laura Taliaferro (formerly Pearson). "
             f"This term is the official winner {name} ({votes}).")

    # ----- FCSD #25 Riverton (official 2024 last names; official district site was a JS challenge wall)
    _add(terms, "WY-JEFFRES", "Jeffres", "Fremont County School District #25 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Riverton #25 (vote for 4): JEFFRES 3,379, BERG 2,730, MANNING 2,599, MORROW 2,569, BOTT 1,915, WAGON 1,526, DEVRIES 1,016 (handwritten withdrawn), HOUTMAN 864, write-ins 109, contest totals 26,336. Official canvass last name only.")
    _add(terms, "WY-BERG-FCSD25", "Berg", "Fremont County School District #25 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Riverton #25: BERG 2,730. Official canvass last name only. Kept distinct from the stale directory listing of former Assessor Tara Berg.")
    _add(terms, "WY-MANNING-FCSD25", "Manning", "Fremont County School District #25 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Riverton #25: MANNING 2,599. Official canvass last name only. Kept distinct from 2026 elect Claire Manning and from Rep. Carl Manning; the official canvass does not print a first name.")
    _add(terms, "WY-MORROW", "Morrow", "Fremont County School District #25 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, School Trustees Riverton #25: MORROW 2,569. Official canvass last name only.")
    for pid, name, votes in (
        ("WY-RAY-JODY", "Jody Ray", "2,565"),
        ("WY-MANNING-CLAIRE", "Claire Manning", "2,357"),
        ("WY-CANTRELL-TERRY", "Terry Cantrell", "2,248"),
    ):
        _add(terms, pid, name, "Fremont County School District #25 Trustee", "schools",
             "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
             "Official 2026 Fremont clerk abstract, School Trustees Riverton #25 (vote for 3): Jody Ray 2,565, Claire Manning 2,357, Terry Cantrell 2,248. "
             f"This term is the official winner {name} ({votes}).")

    # ----- FCSD #38 Arapahoe (official 5-member board page)
    _add(terms, "WY-BELL-LIONEL", "Lionel Bell", "Fremont County School District #38 Trustee", "schools",
         "2023-01-02", "2029-01-01", 2024, [SRC_FCSD38, SRC_2024_CANV],
         "Official FCSD #38 School Board page: Lionel Bell, Chair. Official 2024 canvass, Arapahoe District #38 (vote for 3): L SPOONHUNTER 155, GOGGLES 150, BELL 141, P MOSS 138, OLDMAN 114, I MOSS 95, write-ins 59, contest totals 1,356. The official canvass last name BELL does not identify whether Lionel or Becky Bell was the 2024 winner; both appear on the official current board and are listed from the official board page. Term start for the 2024 class is 2025-01-06 where the seat identity is clear (John Goggles); this row uses the official board page as the current-holder source.",
         conf="medium")
    _add(terms, "WY-BELL-BECKY", "Becky Bell", "Fremont County School District #38 Trustee", "schools",
         "2023-01-02", "2029-01-01", 2024, [SRC_FCSD38],
         "Official FCSD #38 School Board page: Becky Bell, Vice-Chair. Official 2024 canvass last name BELL does not identify which Bell won; both official current members are listed. Official 2022 canvass was not pulled.",
         conf="medium")
    _add(terms, "WY-SPOONHUNTER-BILLIE", "Billie Spoonhunter", "Fremont County School District #38 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD38, SRC_2024_CANV],
         "Official FCSD #38 School Board page: Billie Spoonhunter, Clerk. Official 2024 four-year canvass winner L SPOONHUNTER 155 is treated as this official current member (medium; the canvass prints only the initial L). A separate 2024 two-year contest was won by BROWN, who is not on the official current board page and is not listed as a current holder.",
         conf="medium")
    _add(terms, "WY-GOGGLES-JOHN", "John Goggles", "Fremont County School District #38 Trustee", "schools",
         "2025-01-06", "2029-01-01", 2024, [SRC_FCSD38, SRC_2024_CANV],
         "Official FCSD #38 School Board page: John Goggles, Treasurer. Official 2024 canvass winner GOGGLES 150. Kept distinct from W. Patrick Goggles.")
    _add(terms, "WY-GUERUE-ROSE", "Rose Guerue", "Fremont County School District #38 Trustee", "schools",
         "2023-01-02", "2029-01-01", 2022, [SRC_FCSD38],
         "Official FCSD #38 School Board page: Rose Guerue, Trustee. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Official sources do not identify which of the current five seats are succeeded by the official 2026 elects.",
         conf="medium")
    _add(terms, "WY-GROESBECK-MICHELLE", "Michelle \"Shelly\" Groesbeck", "Fremont County School District #38 Trustee", "schools",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustee Arapahoe #38 2-year: MICHELLE \"SHELLY\" GROESBECK 111.")
    _add(terms, "WY-HANWAY-BRIDGER-B", "Bridger B. Hanway", "Fremont County School District #38 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees Arapahoe #38: BRIDGER B. HANWAY 145, CHARLENE GAMBLER BROWN 109.")
    _add(terms, "WY-BROWN-CHARLENE-GAMBLER", "Charlene Gambler Brown", "Fremont County School District #38 Trustee", "schools",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING],
         "Official 2026 Fremont clerk abstract, School Trustees Arapahoe #38: CHARLENE GAMBLER BROWN 109. Official 2024 two-year winner BROWN is not on the official current board page and is not treated as a current holder.")
    return terms


def special_terms():
    terms = []
    # CWC official current board (7) plus official 2026 elects
    _add(terms, "WY-HUNKER-PAULA", "Paula Hunker", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Paula Hunker, Chair. Official directory lists a Lander subdistrict. Official 2022 canvass was not pulled; term start is the standard post-2022 January date (medium). Official sources do not identify which current Lander-area trustee is succeeded by Jennifer Pryor.",
         conf="medium")
    _add(terms, "WY-TARTER-SHANA", "Shana Tarter", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Shana Tarter, Secretary (Lander subdistrict in the official directory). Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-TOLMAN-CRAIG", "Craig Tolman", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2027-01-04", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Craig Tolman, Vice Chair (Riverton-Shoshoni subdistrict in the official directory). Re-elected on the official 2026 canvass, CWC Sub-Dist #2. Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-LAW-ALMA", "Alma Law", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Alma Law (Riverton-Shoshoni subdistrict in the official directory). Official sources do not identify whether Law or Hughes is succeeded by Robert Hussa in Sub-Dist #2. Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-HUGHES-GAY", "Gay Hughes", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Gay Hughes (Riverton-Shoshoni subdistrict in the official directory). Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-UNDERWOOD-CARLTON", "Carlton Underwood", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Carlton Underwood, Treasurer (Reservation subdistrict in the official directory). Credentials are not printed. The same official name is a current FCSD #14 trustee. Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-OVER-ERNIE", "Ernie Over", "Central Wyoming College Trustee", "special-districts",
         "2023-01-02", "2029-01-01", 2022, [SRC_CWC, SRC_CWC_DIR],
         "Official CWC Board of Trustees page: Ernie Over (Dubois-Crowheart subdistrict in the official directory). Official 2022 canvass was not pulled (medium).",
         conf="medium")
    _add(terms, "WY-TOLMAN-CRAIG", "Craig Tolman", "Central Wyoming College Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, CWC Trustees Sub-Dist #2 (vote for 2): CRAIG TOLMAN 8,008, ROBERT HUSSA 6,899, write-ins 127, contest totals 26,472.")
    _add(terms, "WY-HUSSA-ROBERT", "Robert Hussa", "Central Wyoming College Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, CWC Trustees Sub-Dist #2 (vote for 2): ROBERT HUSSA 6,899, CRAIG TOLMAN 8,008.")
    _add(terms, "WY-PRYOR-JENNIFER", "Jennifer Pryor", "Central Wyoming College Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_ABS, SRC_2026_FILING, SRC_2026_VC],
         "Official 2026 Fremont clerk abstract, CWC Trustees Sub-Dist #4 (vote for 1): JENNIFER PRYOR 9,161, write-ins 67, contest totals 13,236.")

    # Official 2024 specials keyed from the official 77-page canvass (last names where first names were not on the face)
    _add(terms, "WY-GARD-MTNVIEW", "Gard", "Mountain View Cemetery Director", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Cemetery Directors Mountain View (vote for 3): MARTIN 5,022, GARD 4,924, write-in totals 254. Only two named candidates were printed; scattered write-ins were not combined into a certified named third winner. Official canvass last name only.")
    _add(terms, "WY-MARTIN-MTNVIEW", "Martin", "Mountain View Cemetery Director", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Cemetery Directors Mountain View: MARTIN 5,022. Official canvass last name only. Kept distinct from Laura Martin (FCSD #24).")
    _add(terms, "WY-DELAY-CEM", "Delay", "Shoshoni-Lysite Cemetery Director", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Cemetery Directors Shoshoni-Lysite (vote for 3): DELAY 231, MCKEE 223, ZENT 192, write-ins 7, contest totals 1,023. Official canvass last name only.")
    _add(terms, "WY-MCKEE-CEM", "McKee", "Shoshoni-Lysite Cemetery Director", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Cemetery Directors Shoshoni-Lysite: MCKEE 223. Official canvass last name only.")
    _add(terms, "WY-ZENT-CEM", "Zent", "Shoshoni-Lysite Cemetery Director", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Cemetery Directors Shoshoni-Lysite: ZENT 192. Official canvass last name only.")
    _add(terms, "WY-JENSEN-DUBOIS-FIRE", "Jensen", "Dubois Fire District Director, Sub-District #2", "special-districts",
         "2025-01-06", "2029-01-01", 2024, [SRC_2024_CANV],
         "Official 2024 canvass, Dubois Fire District Director Sub-Dist #2 (vote for 1): JENSEN 938, write-ins 2, contest totals 1,217. Official canvass last name only. Sub-Dist #1 on the same page is write-in only (write-in totals 90) with no certified named winner and is not filled.")

    # Official 2026 special elects (official Vote Center + official filings). Write-in-only contests with no certified named winner are not filled.
    _add(terms, "WY-JOHNSON-BODIE", "Bodie Johnson", "Dubois Cemetery Director", "special-districts",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Cemetery Directors 2-year (vote for 2): BODIE JOHNSON 720, CHRIS WELLS 596, write-ins 7, contest totals 1,954.")
    _add(terms, "WY-WELLS-CHRIS", "Chris Wells", "Dubois Cemetery Director", "special-districts",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Cemetery Directors 2-year (vote for 2): CHRIS WELLS 596, BODIE JOHNSON 720.")
    _add(terms, "WY-THOMPSON-BRUCE-JOHN", "Bruce John Thompson", "Dubois Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Cemetery Directors (vote for 3): BRUCE JOHN THOMPSON 685, ROSEMARY GRAFF 623, MARGARET L. WELLS 610, write-ins 5, contest totals 2,931. The official name matches the official Town of Dubois council member and reuses that person ID.")
    _add(terms, "WY-GRAFF-ROSEMARY", "Rosemary Graff", "Dubois Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Cemetery Directors (vote for 3): ROSEMARY GRAFF 623.")
    _add(terms, "WY-WELLS-MARGARET-L", "Margaret L. Wells", "Dubois Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Cemetery Directors (vote for 3): MARGARET L. WELLS 610.")
    _add(terms, "WY-DAVIS-ROBERT-B", "Robert B. Davis", "Mountain View Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Mountain View Cemetery Directors (vote for 3): ROBERT B. DAVIS 4,167, ROSE STANBURY 3,885, GERRI BOESCH 3,307, write-ins 44, contest totals 18,270.")
    _add(terms, "WY-STANBURY-ROSE", "Rose Stanbury", "Mountain View Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Mountain View Cemetery Directors (vote for 3): ROSE STANBURY 3,885.")
    _add(terms, "WY-BOESCH-GERRI", "Gerri Boesch", "Mountain View Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Mountain View Cemetery Directors (vote for 3): GERRI BOESCH 3,307.")
    _add(terms, "WY-MORAVEK-CYNTHIA", "Cynthia Moravek", "Shoshoni-Lysite Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Shoshoni-Lysite Cemetery Directors (vote for 3): CYNTHIA MORAVEK 200, KRIS DAVIS 194, write-ins 24, contest totals 822. Only two named candidates were printed; only those two winners are encoded.")
    _add(terms, "WY-DAVIS-KRIS", "Kris Davis", "Shoshoni-Lysite Cemetery Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Shoshoni-Lysite Cemetery Directors (vote for 3): KRIS DAVIS 194, CYNTHIA MORAVEK 200.")
    _add(terms, "WY-THOMPSON-ERIC-S", "Eric S. Thompson", "Dubois-Crowheart Conservation District Supervisor, At Large", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Dubois-Crowheart At Large (vote for 1): ERIC S. THOMPSON 741, write-ins 3, contest totals 1,063. The official Rural and Urban vote-for-1 contests on the same canvass are write-in only with no certified named winner and are not filled.")
    _add(terms, "WY-LUCAS-RON", "Ron Lucas", "Lower Wind River Conservation District Supervisor, Rural", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Lower Wind River Rural (vote for 1): RON LUCAS 4,923.")
    _add(terms, "WY-PETTIT-SCOTT-D", "Scott D. Pettit", "Lower Wind River Conservation District Supervisor, Urban", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Lower Wind River Urban (vote for 1): SCOTT D. PETTIT 4,798. The official At Large contest on the same canvass is write-in only (write-ins 720) with no certified named winner and is not filled.")
    _add(terms, "WY-HAMILTON-JARED-W", "Jared W. Hamilton", "Popo Agie Conservation District Supervisor, Rural", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Popo Agie Rural (vote for 3): JARED W. HAMILTON 3,134, SALLY ESPINOSA 3,084, DOUGLAS L. THOMPSON 2,520, write-ins 69, contest totals 17,685. The official At Large contest is write-in only (write-ins 434) with no certified named winner and is not filled.")
    _add(terms, "WY-ESPINOSA-SALLY", "Sally Espinosa", "Popo Agie Conservation District Supervisor, Rural", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Popo Agie Rural (vote for 3): SALLY ESPINOSA 3,084.")
    _add(terms, "WY-THOMPSON-DOUGLAS-L", "Douglas L. Thompson", "Popo Agie Conservation District Supervisor, Rural", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Conservation Supervisor Popo Agie Rural (vote for 3): DOUGLAS L. THOMPSON 2,520.")
    _add(terms, "WY-CODEVILLA-MICHAEL-P", "Michael P. Codevilla", "Dubois Fire District Director, Sub-District #3", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Fire Director Sub-Dist #3 (vote for 1): MICHAEL P. CODEVILLA 720.")
    _add(terms, "WY-BRADBURY-GARY", "Gary Bradbury", "Dubois Fire District Director, Sub-District #5", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Dubois Fire Director Sub-Dist #5 (vote for 1): GARY BRADBURY 691.")
    _add(terms, "WY-GARDNER-KELLY", "Kelly Gardner", "Fremont County Fire District Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Fremont County Fire District Directors (vote for 2): KELLY GARDNER 1,907, PAUL J. DOWNEY 1,747, JOHN \"RED\" FYLER 1,444, write-ins 20, contest totals 8,478.")
    _add(terms, "WY-DOWNEY-PAUL-J", "Paul J. Downey", "Fremont County Fire District Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Fremont County Fire District Directors (vote for 2): PAUL J. DOWNEY 1,747, KELLY GARDNER 1,907.")
    _add(terms, "WY-GARLAND-STEVE", "Steve Garland", "Jeffrey City Fire District Director", "special-districts",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Jeffrey City Fire District Directors 2-year (vote for 1): STEVE GARLAND 48.")
    _add(terms, "WY-MURPHREE-TYLER-THOMAS", "Tyler Thomas Murphree", "Jeffrey City Fire District Director", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center / official filing, Jeffrey City Fire District Directors (vote for 1): TYLER THOMAS MURPHREE 47.")
    _add(terms, "WY-KOPRIVA-PATRICIA", "Patricia Kopriva", "Lander Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Lander Senior Citizens 2-year unexpired (vote for 2): PATRICIA KOPRIVA 3,074, JERI TREBELCOCK 2,574, contest totals 10,100. Official filing name Jeri Trebelcock (canvass wraps TREBELCOC).")
    _add(terms, "WY-TREBELCOCK-JERI", "Jeri Trebelcock", "Lander Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2029-01-01", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center / official filing, Lander Senior Citizens 2-year unexpired: JERI TREBELCOCK 2,574.")
    _add(terms, "WY-FAGNANT-RICHARD", "Richard Fagnant", "Lander Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Lander Senior Citizens Trustees (vote for 3): RICHARD FAGNANT 2,787, DAVID BRINDA 2,637, JOE HENRY 2,263, contest totals 15,150.")
    _add(terms, "WY-BRINDA-DAVID", "David Brinda", "Lander Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Lander Senior Citizens Trustees (vote for 3): DAVID BRINDA 2,637.")
    _add(terms, "WY-HENRY-JOE", "Joe Henry", "Lander Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Lander Senior Citizens Trustees (vote for 3): JOE HENRY 2,263.")
    _add(terms, "WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", "Riverton Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Riverton Senior Citizens District Trustees (vote for 3): WESLEY A. ROBERTS 3,056, MARLENE BRODRICK 3,034, VICTOR R. ALLEN 2,533, contest totals 14,037.")
    _add(terms, "WY-BRODRICK-MARLENE", "Marlene Brodrick", "Riverton Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Riverton Senior Citizens District Trustees (vote for 3): MARLENE BRODRICK 3,034.")
    _add(terms, "WY-ALLEN-VICTOR-R", "Victor R. Allen", "Riverton Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Riverton Senior Citizens District Trustees (vote for 3): VICTOR R. ALLEN 2,533.")
    _add(terms, "WY-CUNDALL-KEN", "Ken Cundall", "Shoshoni Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Shoshoni Senior Citizens District Trustees (vote for 3): KEN CUNDALL 194, JOAN GEIS 189, TERESA TAYLOR 182, write-ins 8, contest totals 822. The official Shoshoni Senior Citizens Svc Dist Mill is a YES 211 / NO 55 ballot measure, not a holder office.")
    _add(terms, "WY-GEIS-JOAN", "Joan Geis", "Shoshoni Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Shoshoni Senior Citizens District Trustees (vote for 3): JOAN GEIS 189.")
    _add(terms, "WY-TAYLOR-TERESA", "Teresa Taylor", "Shoshoni Senior Citizens District Trustee", "special-districts",
         "2027-01-04", "2031-01-06", 2026, [SRC_2026_VC, SRC_2026_FILING],
         "Official 2026 Vote Center, Shoshoni Senior Citizens District Trustees (vote for 3): TERESA TAYLOR 182.")
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [
            ("Senate District 20 (S20)", 1),
            ("Senate District 25 (S25)", 1),
            ("Senate District 26 (S26)", 1),
        ],
        "state-house": [
            ("House District 28 (H28)", 1),
            ("House District 33 (H33)", 1),
            ("House District 34 (H34)", 1),
            ("House District 54 (H54)", 1),
            ("House District 55 (H55)", 1),
        ],
        "county": [("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [
            ("City of Lander Mayor", 1),
            ("City of Lander Council Ward 1", 2), ("City of Lander Council Ward 2", 2),
            ("City of Lander Council Ward 3", 2),
            ("City of Riverton Mayor", 1),
            ("City of Riverton Council Ward 1", 2), ("City of Riverton Council Ward 2", 2),
            ("City of Riverton Council Ward 3", 2),
            ("Town of Dubois Mayor", 1), ("Town of Dubois Council", 4),
            ("Town of Shoshoni Mayor", 1), ("Town of Shoshoni Council", 4),
            ("Town of Hudson Mayor", 1), ("Town of Hudson Council", 4),
            ("Town of Pavillion Mayor", 1), ("Town of Pavillion Council", 4),
        ],
        "schools": [
            ("Fremont County School District #1 Trustee", 7),
            ("Fremont County School District #2 Trustee", 7),
            ("Fremont County School District #6 Trustee", 7),
            ("Fremont County School District #14 Trustee", 5),
            ("Fremont County School District #21 Trustee", 5),
            ("Fremont County School District #24 Trustee", 7),
            ("Fremont County School District #25 Trustee", 7),
            ("Fremont County School District #38 Trustee", 5),
        ],
        "special-districts": [
            ("Central Wyoming College Trustee", 7),
            ("Dubois Cemetery Director", 5),
            ("Mountain View Cemetery Director", 5),
            ("Shoshoni-Lysite Cemetery Director", 5),
            ("Dubois-Crowheart Conservation District Supervisor, At Large", 1),
            ("Lower Wind River Conservation District Supervisor, Rural", 1),
            ("Lower Wind River Conservation District Supervisor, Urban", 1),
            ("Popo Agie Conservation District Supervisor, Rural", 3),
            ("Dubois Fire District Director, Sub-District #2", 1),
            ("Dubois Fire District Director, Sub-District #3", 1),
            ("Dubois Fire District Director, Sub-District #5", 1),
            ("Fremont County Fire District Director", 2),
            ("Jeffrey City Fire District Director", 2),
            ("Lander Senior Citizens District Trustee", 5),
            ("Riverton Senior Citizens District Trustee", 3),
            ("Shoshoni Senior Citizens District Trustee", 3),
        ],
        "judicial": [
            ("District Judge, 9th Judicial District", 1),
            ("Circuit Judge, 9th Judicial District", 2),
        ],
    }



def build_fremont():
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
        "9th Judicial District judges (serving Fremont with Sublette and Teton). Full names follow official court "
        "pages already used in the Sublette and Teton histories. Official 2026 Fremont clerk abstract named-retention "
        "YES/NO totals are recorded for Jason M. Conder, Erin E. Weisman, and Jefferson Boone Coombs."
    )
    coverage = H.write_terms_and_snapshots(
        county="Fremont", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Fremont", slug=SLUG)
    print("copied shared terms", copied, "coverage", coverage)
    return people, terms, coverage


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


def update_fremont_json(people, terms):
    path = ROOT / "data" / "county_officials" / "fremont.json"
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
        _office("Senate District 20 (S20)", holders("Senate District 20 (S20)"),
                note="Official 2024 SOS statewide Senate summary, Senate District 20: Ed Cooper (R) Total 8,236. Official Fremont share 305; official Big Horn 1,475, Hot Springs 2,180, Park 834, Washakie 3,442. Off-cycle in 2026."),
        _office("Senate District 25 (S25)", holders("Senate District 25 (S25)"),
                note="Official 2026 SOS statewide Senate summary, Senate District 25: Cale Case (R) Total 4,670. Fremont-only (official Fremont share equals the official Total). Official Fremont clerk abstract: REP CASE 4,670. Official 2022 Total 4,365."),
        _office("Senate District 26 (S26)", holders("Senate District 26 (S26)"),
                note="Official 2024 SOS statewide Senate summary, Senate District 26: Tim Salazar (R) Total 7,266. Fremont-only (official Fremont share equals the official Total). Off-cycle in 2026."),
    ]
    house = [
        _office("House District 28 (H28)", holders("House District 28 (H28)"),
                note="Official 2024 SOS statewide House summary, House District 28: John R. Winter (R) Total 3,986, Larry Alwin (D) 857. Official Fremont share Winter 279, Alwin 45. Official 2026 SOS: Allen Hogg (R) Total 3,309, Larry Alwin (D) 504; official Fremont share Hogg 237, Alwin 22, taking office January 2027. Official other 2026 shares: Big Horn 655–66, Hot Springs 1,725–343, Park 692–73."),
        _office("House District 33 (H33)", holders("House District 33 (H33)"),
                note="Official 2026 SOS statewide House summary, House District 33: Ivan D. Posey (D) 1,383, Justin Morgan (R) 741. Fremont-only. Official 2024: Ivan D. Posey 1,675, Sarah Penn 1,210."),
        _office("House District 34 (H34)", holders("House District 34 (H34)"),
                note="Official 2026 SOS statewide House summary, House District 34: Pepper L. Ottman (R) 2,930. Fremont-only. Official 2024 Total 4,117."),
        _office("House District 54 (H54)", holders("House District 54 (H54)"),
                note="Official 2026 SOS statewide House summary, House District 54: Lloyd Charles Larsen (R) 3,156, Holly M. Butler (L) 794. Fremont-only. Official 2024 Total 3,821."),
        _office("House District 55 (H55)", holders("House District 55 (H55)"),
                note="Official 2024 SOS statewide House summary, House District 55: Joel Guggenmos (R) 2,858. Official 2026 SOS: Carl Manning (R) 2,334, taking office January 2027. Fremont-only (official Fremont share equals the official Total)."),
    ]
    county = [
        _office("County Commissioner, District 1", holders("County Commissioner, District 1"),
                note="Official commissioners page, retrieved 2026-11-24: Clarence Thomas, District 1. Official 2026 clerk abstract: Nicole A. Wagon (IND) 810, Clarence V. Mossburg (REP) 576, taking office January 2027."),
        _office("County Commissioner, District 2", holders("County Commissioner, District 2"),
                note="Official commissioners page, retrieved 2026-11-24: Larry Allen, Chairman, District 2. Not on the official 2026 general ballot."),
        _office("County Commissioner, District 3", holders("County Commissioner, District 3"),
                note="Official commissioners page, retrieved 2026-11-24: Ron Fabrizius, District 3. Official 2026 clerk abstract: Ryan W. Stanley (REP) 2,050, taking office January 2027."),
        _office("County Commissioner, District 4", holders("County Commissioner, District 4"),
                note="Official commissioners page, retrieved 2026-11-24: Michael Jones, Vice-Chairman, District 4. Official 2026 clerk abstract: Kessler (REP) 2,561, taking office January 2027. Official first name was not uniquely resolved from the two-column official 2026 primary layout."),
        _office("County Commissioner, District 5", holders("County Commissioner, District 5"),
                note="Official commissioners page, retrieved 2026-11-24: Jennifer Wilson, District 5. Not on the official 2026 general ballot."),
        _office("County Clerk", holders("County Clerk"),
                note="Official clerk page, retrieved 2026-11-24, names Julie Freese. Official Nov. 5, 2026 canvass minutes name Julie A. Freese. Official 2026 abstract: REP FREESE 10,919."),
        _office("County Treasurer", holders("County Treasurer"),
                note="Official treasurer page, retrieved 2026-11-24, names James A. Anderson. Official 2026 abstract: REP ANDERSON 10,339."),
        _office("County Assessor", holders("County Assessor"),
                note="Official assessor page, retrieved 2026-11-24: Ella M. Riggs, appointed interim County Assessor on September 29, 2026. The official directory card still listed Tara Berg and was treated as stale. Official 2026 abstract: REP RIGGS 10,373, taking office as the elected assessor January 2027."),
        _office("County Sheriff", holders("County Sheriff"),
                note="Official sheriff page, retrieved 2026-11-24, names Sheriff Ryan Lee (elected and sworn January 7, 2019). Official 2026 abstract: REP ZERGA 10,656, John Zerga, taking office January 2027."),
        _office("County Attorney", holders("County Attorney"),
                note="Official attorney page, retrieved 2026-11-24, names Micah Wyatt. Official 2026 abstract: REP WYATT 10,078."),
        _office("Clerk of District Court", holders("Clerk of District Court"),
                note="Official CDC page, retrieved 2026-11-24, names Amanda Sanchez. Official 2026 primary and general use Amanda R. Sanchez / REP SANCHEZ 10,288."),
        _office("County Coroner", holders("County Coroner"),
                note="Official coroner page, retrieved 2026-11-24, names Erin Ivie. Official 2026 abstract: REP IVIE 10,825."),
    ]
    municipal = [
        _office("City of Lander Mayor", holders("City of Lander Mayor"),
                note="Official Lander Mayor and City Council page, retrieved 2026-11-24: Missy White, Mayor, Elected 03/2025, Term Expires 12/2026. Official 2026 abstract: MICHELLE B. MOTHERWAY 1,535, MISSY WHITE 1,355, taking office January 2027."),
        _office("City of Lander Council Ward 1", holders("City of Lander Council Ward 1"),
                layout="heading-then-names",
                note="Official Lander page, retrieved 2026-11-24: Josh Hahn (Elected 11/2022, Term Expires 12/2026) and Dan Hahn (Elected 11/2020, Term Expires 12/2028). Official 2026 abstract: GEORGE CASE 524, JENNY YOUNG 303; Case takes office January 2027."),
        _office("City of Lander Council Ward 2", holders("City of Lander Council Ward 2"),
                layout="heading-then-names",
                note="Official Lander page, retrieved 2026-11-24: Chad Cassady (oath 5/13/25, Term Expires 12/2026) and Julia Stuble (Elected 11/2020, Term Expires 12/2028). Official 2026 abstract: CHAD CASSADY 407, re-elected."),
        _office("City of Lander Council Ward 3", holders("City of Lander Council Ward 3"),
                layout="heading-then-names",
                note="Official Lander page, retrieved 2026-11-24: John Larsen (Elected 11/2022, Term Expires 12/2026) and Melinda Cox (Elected 11/2020, Term Expires 12/2028). Official 2026 abstract: SARAH L. SCHLOSSER 594, MICHAEL KUSIEK 331; Schlosser takes office January 2027."),
        _office("City of Riverton Mayor", holders("City of Riverton Mayor"),
                note="Official Riverton Meet the Mayor page, retrieved 2026-11-24: Mayor Tim Hancock, Current Term 2023-2026. Official 2026 abstract: MICHAEL V (MIKE) BAILEY 1,530, DARYL WEST 1,067, taking office January 2027."),
        _office("City of Riverton Council Ward 1", holders("City of Riverton Council Ward 1"),
                layout="heading-then-names",
                note="Official Riverton Meet the Council page, retrieved 2026-11-24: Karen Johnson (2025-2028) and Kyle Larson (2023-2026). Official 2026 abstract: KYLE M. LARSON 344, PIRAM DURAN 219; Larson re-elected."),
        _office("City of Riverton Council Ward 2", holders("City of Riverton Council Ward 2"),
                layout="heading-then-names",
                note="Official Riverton Meet the Council page, retrieved 2026-11-24: Jerika Preston (2025-2028) and Karla Borders (2023-2026). Official 2026 abstract: CHANCEY WILCZEWSKI 698, taking office January 2027."),
        _office("City of Riverton Council Ward 3", holders("City of Riverton Council Ward 3"),
                layout="heading-then-names",
                note="Official Riverton Meet the Council page, retrieved 2026-11-24: Mike Bailey (2023-2026) and Eric Carr (2025-2028). Official 2026 abstract: TIM HANCOCK 924, taking office January 2027."),
        _office("Town of Dubois Mayor", holders("Town of Dubois Mayor"),
                note="Official Town of Dubois Town Council page, retrieved 2026-11-24: Patricia Neveaux, Mayor. Official 2026 Vote Center / abstract: DAVID FURMAN 213, PATRICIA NEVEAUX 202 (the scanned-abstract OCR dropped a digit; official born-digital Vote Center totals are used)."),
        _office("Town of Dubois Council", holders("Town of Dubois Council"),
                layout="heading-then-names",
                note="Official Town of Dubois Town Council page, retrieved 2026-11-24: Rick Lee, Randy Lahr, Amanda Ysen, and Bruce John Thompson. Official 2026 abstract (vote for 2): MIKE STRASSER 327, AMANDA YSEN 255. Which two of the other three current official members were on the expiring cycle is not printed on the official 2026 ballot."),
        _office("Town of Shoshoni Mayor", holders("Town of Shoshoni Mayor"),
                note="Official Town of Shoshoni Mayor & Council page, retrieved 2026-11-24: Joel Highsmith, Mayor, Term 2023-2027. Official 2026 abstract: RONALD W. ANKENY 105, JORDAN A. WHITENER 92, taking office January 2027."),
        _office("Town of Shoshoni Council", holders("Town of Shoshoni Council"),
                layout="heading-then-names",
                note="Official Shoshoni page, retrieved 2026-11-24: Mark Nordeen (2025-2029), Jake Z. Stetler (2023-2027), Tammie Hardtke (2023-2027), Jordan Whitener (2025-2029). Official 2026 abstract (vote for 2): JACOB Z STETLER 120, TAMMIE A. HARDTKE 94 (official Vote Center total; scanned-abstract OCR dropped a digit)."),
        _office("Town of Hudson Mayor", holders("Town of Hudson Mayor"),
                note="Official Town of Hudson Government page (hudsonwy.org, retrieved 2026-11-24): Mayor Sherry Oler, Term expires 12/31/2026. Official 2026 abstract: MARILYN V. ROBINSON 95. The Massachusetts CivicPlus site townofhudson.org was not used."),
        _office("Town of Hudson Council", holders("Town of Hudson Council"),
                layout="heading-then-names",
                note="Official Town of Hudson Government page, retrieved 2026-11-24: Brady Hamilton, Council President (exp. 12/31/2028); Zeke Bonella (exp. 12/31/2026); Helen Gordon (exp. 12/31/2026); Kevin Kummer (exp. 12/31/2028). Official 2026 abstract (vote for 2): HELEN J GORDON 67, DANIEL (DANNY) SVILAR 67."),
        _office("Town of Pavillion Mayor", holders("Town of Pavillion Mayor"),
                note="Official 2024 canvass Pavillion 2-year contest is write-in only with no certified named winner. Official ARCA 2022 canvass was not pulled. Current mayor stays Not yet collected. Official 2026 abstract: LESTER R EMERSON 46, taking office January 2027."),
        _office("Town of Pavillion Council", holders("Town of Pavillion Council"),
                layout="heading-then-names",
                note="Official 2024 canvass, Pavillion Council (vote for 2): BARRETT 54, ROBINSON 52 (official last names only). Official 2026 abstract (vote for 2): JACQUE L STOLDT 46, MANDI REYNOLDS 35, taking office January 2027."),
    ]
    schools = [
        _office("Fremont County School District #1 Trustee", holders("Fremont County School District #1 Trustee"),
                layout="heading-then-names",
                note="Official FCSD #1 Governing Board page (Wayback 2026-10-21) names the current seven, with official term expires 12/1/2028 (Taylor Jacobs, Mara Gans) or 12/01/2026 (Mike McConnell, re-elected; Karen Harms, Jared Kail, Matt Ayers, Aileen Brew). Official 2024 canvass (vote for 3): JACOBS 2,842, JENSEN 2,732, GANS 2,652; Jensen is not on the official October 2026 board page. Official 2026 elects, taking office January 2027: 2-year unexpired Breanne N. Weston 3,262; four-year Mary Greene 2,515, Mike McConnell 2,125, Kate Strike 2,060, Jeff Chapin 2,004."),
        _office("Fremont County School District #2 Trustee", holders("Fremont County School District #2 Trustee"),
                layout="heading-then-names",
                note="Official FCSD #2 Governing Board page names the current seven. Official 2024 canvass four-year winners: VERMEIRE 715, SELLERS 688, NIELSEN 687 (Nielsen is not on the official current board); 2-year: POLMANTEER 748. Official 2026 elects: 2-year unexpired Brad Lindsey 410; four-year Judy Rogers 593, Nicole Polmanteer 544, Tina Baker 498, Libby Littler 453."),
        _office("Fremont County School District #6 Trustee", holders("Fremont County School District #6 Trustee"),
                layout="heading-then-names",
                note="Official 2024 canvass, Wind River #6 (vote for 4): EVANS 691, STOLL-BAKER 660, MCCANN 537 (official last names only; only three named candidates were printed; a handwritten Lindsay Curran 45 annotation is not a certified winner). The official district site was a JS challenge wall. Official 2026 elects: 2-year Jessica Klein 600; four-year Dawn Leonhardt 481, David Befus 444, Van Hill 429."),
        _office("Fremont County School District #14 Trustee", holders("Fremont County School District #14 Trustee"),
                layout="heading-then-names",
                note="Official FCSD #14 Highbond current member widget (meetings listed through November 11, 2026): Arline Trosper, Rich Singer, Tessa Redman, Carlton Underwood, Sanford Friday. Official 2024 canvass (vote for 3): UNDERWOOD 227, SINGER 203, REDMAN 174. Official 2026 elects (vote for 2): Willena Rosie Trosper 226, Sanford D. Friday 220 (re-elected). Willena is kept distinct from Arline."),
        _office("Fremont County School District #21 Trustee", holders("Fremont County School District #21 Trustee"),
                layout="heading-then-names",
                note="Official FCSD #21 2025-2026 handbook board: Tex LeClair, Chairman; Kay Ferris, Vice Chairman; Carla Mann, Treasurer; Bonnie Washakie; David Snyder. Official 2024 canvass (vote for 3): WASHAKIE 189, SNYDER 182, FERRIS 142, matching Kay Ferris, David Snyder, and Bonnie Washakie. Official 2026 Vote Center (vote for 2): Jake Hill 208, Clinton D. Wagon 172, taking office January 2027."),
        _office("Fremont County School District #24 Trustee", holders("Fremont County School District #24 Trustee"),
                layout="heading-then-names",
                note="Official 2024 canvass, Shoshoni #24 (vote for 3): HAUN 425, PEREGOY 385, CRIMM 370 (official last names only; official BoardDocs and Highbond pages did not yield a first-name roster). Official 2026 Vote Center (vote for 4): Lynn A. Thompson 379, Laura Martin 358, Kris Edgeington 304, Hilary Engum 229, taking office January 2027. Laura Martin is not Laura Taliaferro (formerly Pearson)."),
        _office("Fremont County School District #25 Trustee", holders("Fremont County School District #25 Trustee"),
                layout="heading-then-names",
                note="Official 2024 canvass, Riverton #25 (vote for 4): JEFFRES 3,379, BERG 2,730, MANNING 2,599, MORROW 2,569 (official last names only; 2024 Manning is kept distinct from 2026 elect Claire Manning and from Rep. Carl Manning). Official 2026 Vote Center (vote for 3): Jody Ray 2,565, Claire Manning 2,357, Terry Cantrell 2,248, taking office January 2027."),
        _office("Fremont County School District #38 Trustee", holders("Fremont County School District #38 Trustee"),
                layout="heading-then-names",
                note="Official FCSD #38 School Board page: Lionel Bell, Chair; Becky Bell, Vice-Chair; Billie Spoonhunter, Clerk; John Goggles, Treasurer; Rose Guerue, Trustee. Official 2024 four-year canvass (vote for 3): L SPOONHUNTER 155, GOGGLES 150, BELL 141. Official 2024 two-year winner BROWN is not on the official current board. Official 2026 elects: 2-year Michelle \"Shelly\" Groesbeck 111; four-year Bridger B. Hanway 145 and Charlene Gambler Brown 109. Official sources do not identify which of the current five seats those elects succeed."),
    ]
    specials = [
        _office("Central Wyoming College Trustee", holders("Central Wyoming College Trustee"),
                layout="heading-then-names",
                note="Official CWC Board of Trustees page: Paula Hunker, Chair; Craig Tolman, Vice Chair (re-elected, Sub-Dist #2); Shana Tarter, Secretary; Carlton Underwood, Treasurer; Alma Law; Gay Hughes; Ernie Over. Official 2026 abstract: Sub-Dist #2 (vote for 2) Craig Tolman 8,008 and Robert Hussa 6,899; Sub-Dist #4 (vote for 1) Jennifer Pryor 9,161, taking office January 2027. Official sources do not identify which current trustees those elects succeed."),
        _office("Dubois Cemetery Director", holders("Dubois Cemetery Director"),
                layout="heading-then-names",
                note="Official 2026 Vote Center: 2-year (vote for 2) Bodie Johnson 720, Chris Wells 596; regular (vote for 3) Bruce John Thompson 685, Rosemary Graff 623, Margaret L. Wells 610, taking office January 2027. Official 2024 cemetery names for this district were not fully keyed."),
        _office("Mountain View Cemetery Director", holders("Mountain View Cemetery Director"),
                layout="heading-then-names",
                note="Official 2024 canvass (vote for 3): MARTIN 5,022, GARD 4,924 (official last names only; only two named candidates were printed). Official 2026 Vote Center (vote for 3): Robert B. Davis 4,167, Rose Stanbury 3,885, Gerri Boesch 3,307, taking office January 2027."),
        _office("Shoshoni-Lysite Cemetery Director", holders("Shoshoni-Lysite Cemetery Director"),
                layout="heading-then-names",
                note="Official 2024 canvass (vote for 3): DELAY 231, MCKEE 223, ZENT 192 (official last names only). Official 2026 Vote Center (vote for 3): Cynthia Moravek 200, Kris Davis 194 (only two named candidates), taking office January 2027."),
        _office("Dubois-Crowheart Conservation District Supervisor, At Large", holders("Dubois-Crowheart Conservation District Supervisor, At Large"),
                note="Official 2026 Vote Center (vote for 1): Eric S. Thompson 741, taking office January 2027. Official Rural and Urban contests on the same canvass are write-in only with no certified named winner and are not filled."),
        _office("Lower Wind River Conservation District Supervisor, Rural", holders("Lower Wind River Conservation District Supervisor, Rural"),
                note="Official 2026 Vote Center (vote for 1): Ron Lucas 4,923, taking office January 2027."),
        _office("Lower Wind River Conservation District Supervisor, Urban", holders("Lower Wind River Conservation District Supervisor, Urban"),
                note="Official 2026 Vote Center (vote for 1): Scott D. Pettit 4,798, taking office January 2027. The official At Large contest is write-in only (write-ins 720) with no certified named winner and is not filled."),
        _office("Popo Agie Conservation District Supervisor, Rural", holders("Popo Agie Conservation District Supervisor, Rural"),
                layout="heading-then-names",
                note="Official 2026 Vote Center (vote for 3): Jared W. Hamilton 3,134, Sally Espinosa 3,084, Douglas L. Thompson 2,520, taking office January 2027. Official 2024 Rural and At Large contests on the official canvass are write-in only with no certified named winner."),
        _office("Dubois Fire District Director, Sub-District #2", holders("Dubois Fire District Director, Sub-District #2"),
                note="Official 2024 canvass (vote for 1): JENSEN 938 (official last name only). Official 2024 Sub-Dist #1 is write-in only with no certified named winner and is not filled."),
        _office("Dubois Fire District Director, Sub-District #3", holders("Dubois Fire District Director, Sub-District #3"),
                note="Official 2026 Vote Center (vote for 1): Michael P. Codevilla 720, taking office January 2027."),
        _office("Dubois Fire District Director, Sub-District #5", holders("Dubois Fire District Director, Sub-District #5"),
                note="Official 2026 Vote Center (vote for 1): Gary Bradbury 691, taking office January 2027."),
        _office("Fremont County Fire District Director", holders("Fremont County Fire District Director"),
                layout="heading-then-names",
                note="Official 2026 Vote Center (vote for 2): Kelly Gardner 1,907, Paul J. Downey 1,747, taking office January 2027. John \"Red\" Fyler 1,444 was not elected."),
        _office("Jeffrey City Fire District Director", holders("Jeffrey City Fire District Director"),
                layout="heading-then-names",
                note="Official 2026 Vote Center: 2-year Steve Garland 48; regular Tyler Thomas Murphree 47, taking office January 2027."),
        _office("Lander Senior Citizens District Trustee", holders("Lander Senior Citizens District Trustee"),
                layout="heading-then-names",
                note="Official 2026 Vote Center: 2-year unexpired (vote for 2) Patricia Kopriva 3,074, Jeri Trebelcock 2,574; regular (vote for 3) Richard Fagnant 2,787, David Brinda 2,637, Joe Henry 2,263, taking office January 2027."),
        _office("Riverton Senior Citizens District Trustee", holders("Riverton Senior Citizens District Trustee"),
                layout="heading-then-names",
                note="Official 2026 Vote Center (vote for 3): Wesley A. Roberts 3,056, Marlene Brodrick 3,034, Victor R. Allen 2,533, taking office January 2027."),
        _office("Shoshoni Senior Citizens District Trustee", holders("Shoshoni Senior Citizens District Trustee"),
                layout="heading-then-names",
                note="Official 2026 Vote Center (vote for 3): Ken Cundall 194, Joan Geis 189, Teresa Taylor 182, taking office January 2027. The official Shoshoni Senior Citizens Svc Dist Mill is a YES 211 / NO 55 ballot measure, not a holder office."),
    ]
    judicial = [
        _office("District Judge, 9th Judicial District", holders("District Judge, 9th Judicial District"),
                note="Official 2026 Fremont clerk abstract, JDG A DIST CRT CONDER: YES 8,527, NO 2,343. Full name Jason M. Conder is from the official 9th Judicial District court page (also used in official Sublette and Teton histories). Retained, continuing January 2027."),
        _office("Circuit Judge, 9th Judicial District", holders("Circuit Judge, 9th Judicial District"),
                layout="heading-then-names",
                note="Official 2026 Fremont clerk abstract: CIRCUIT CRT WEISMAN YES 8,229, NO 2,355; CIRCUIT CRT COOMBS YES 8,014, NO 2,496. Full names Erin E. Weisman and Jefferson Boone Coombs are from official court pages already used in the Teton and Sublette histories. Retained, continuing January 2027."),
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
        "general_results": "https://www.fremontcountywy.gov/Government/Clerk/Elections/2026%20Election%20Results/General/2026%20General%20OFFICIAL%20Results%20Summary%20-%20Official%20Abstract%202026.11.5.pdf",
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/fremont/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
