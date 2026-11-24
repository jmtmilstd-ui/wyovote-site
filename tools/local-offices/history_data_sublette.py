#!/usr/bin/env python3
"""Sublette County officeholder history (preview). Official clerk, SOS, court,
and town sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 23
SLUG = "sublette"

URL_ELECTIONS = "https://www.sublettecountywy.gov/110/Election-Information"
URL_C26 = "https://www.sublettecountywy.gov/DocumentCenter/View/8211/Official-2026-General-Election-Results"
URL_P26 = "https://www.sublettecountywy.gov/DocumentCenter/View/8060/Official-Results-2026-Primary-Election"
URL_C26P = "https://www.sublettecountywy.gov/DocumentCenter/View/8210"
URL_C24 = "https://www.sublettecountywy.gov/DocumentCenter/View/6118/election-summary-official-2024"
URL_C24P = "https://www.sublettecountywy.gov/DocumentCenter/View/6119"
URL_C22P = "https://www.sublettecountywy.gov/DocumentCenter/View/7652/2022-OFFICIAL-GENERAL-RESULTS-BY-PRECINCT"
URL_C22 = "https://web.archive.org/web/20230208155721/https://www.sublettecountywy.gov/DocumentCenter/View/4109/General-Election-Summary"
URL_PROC = "https://www.sublettecountywy.gov/DocumentCenter/View/8156"
URL_CLERK = "https://www.sublettecountywy.gov/96/County-Clerk"
URL_COMM = "https://www.sublettecountywy.gov/231/Commissioner-Profiles"
URL_SHERIFF = "https://www.sublettecountywy.gov/442/Sheriff"
URL_PINEDALE = "https://www.townofpinedale.us/town-council"
URL_PINEDALE_ELEX = "https://www.townofpinedale.us/copy-of-political-signs"
URL_MARBLETON = "https://www.marbletonwyo.net/council"
URL_COURT_D = "https://www.wyocourts.gov/court/district-court-9th-judicial-district-sublette-county/"
URL_COURT_C = "https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-sublette-county-state-of-wyoming-pinedale/"
URL_COURT_TD = "https://www.wyocourts.gov/court/district-court-9th-judicial-district-teton-county/"
URL_COURT_TC = "https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-teton-county-state-of-wyoming-jackson/"
URL_COURT_FD = "https://www.wyocourts.gov/court/district-court-9th-judicial-district-fremont-county/"
URL_COURT_FC = "https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-fremont-county-state-of-wyoming-lander/"
URL_COURT_RV = "https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-fremont-county-state-of-wyoming-riverton/"
LINC_BASE = "https://www.lincolncountywy.gov/Documents/Government/Clerk/Election%20And%20Voting%20Information/Election%20Results%20And%20Upcoming%20Elections"
URL_LINC22 = f"{LINC_BASE}/PREVIOUS%20ELECTION%20OFFICIAL%20RESULTS/2022%20OFFICIAL%20GENERAL%20ELECTION%20SUMMARY.pdf"
URL_LINC24 = f"{LINC_BASE}/PREVIOUS%20ELECTION%20OFFICIAL%20RESULTS/2024/2024%20GENERAL%20ELECTION/summary%202024%20general.pdf"
URL_LINC26 = f"{LINC_BASE}/2026/OFFICIAL%20SUMMARY%202026%20GEN.pdf"


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


SRC_C26 = S("Official Sublette County 2026 general election summary (header OFFICIAL RESULTS, Election Summary - 11/05/2026 04:54PM, 8 of 8 precincts, 3,775 ballots)", URL_C26)
SRC_P26 = S("Official Sublette County 2026 primary election results", URL_P26)
SRC_C24 = S("Official Sublette County 2024 general election summary (header OFFICIAL RESULTS, Election Summary - 11/07/2024 12:05PM, 4,972 ballots)", URL_C24)
SRC_C22 = S("Official Sublette County 2022 general election summary (header OFFICIAL RESULTS, Election Summary - 11/11/2022 10:05 AM, 3,605 ballots). Archived from the official clerk DocumentCenter View/4109 via the Wayback Machine capture 20230208155721 after the live slug was removed.", URL_C22)
SRC_C22P = S("Official Sublette County 2022 general election precinct summary (header OFFICIAL RESULTS, General Precinct Summary - 11/11/2022 10:05AM, 17 pages)", URL_C22P)
SRC_PROC = S("Official 2026 Sublette County general election proclamation and amendment from 5 to 3 commissioners (official Word document)", URL_PROC)
SRC_CLERK = S("Official Sublette County Clerk page (https://www.sublettecountywy.gov/96/County-Clerk), retrieved 2026-11-24, and official Wayback captures of the same page", URL_CLERK)
SRC_COMM = S("Official Sublette County Commissioner Profiles page", URL_COMM)
SRC_SHERIFF = S("Official Sublette County Sheriff page", URL_SHERIFF)
SRC_PINEDALE = S("Official Town of Pinedale town council page", URL_PINEDALE)
SRC_PINEDALE_ELEX = S("Official Town of Pinedale 2026 municipal election results page", URL_PINEDALE_ELEX)
SRC_MARBLETON = S("Official Town of Marbleton council page", URL_MARBLETON)
SRC_COURT_D = S("Official Wyoming Judicial Branch, District Court of the 9th Judicial District, Sublette County", URL_COURT_D)
SRC_COURT_C = S("Official Wyoming Judicial Branch, Circuit Court of the 9th Judicial District, Sublette County (Pinedale)", URL_COURT_C)
SRC_COURT_TD = S("Official Wyoming Judicial Branch, District Court of the 9th Judicial District, Teton County", URL_COURT_TD)
SRC_COURT_TC = S("Official Wyoming Judicial Branch, Circuit Court of the 9th Judicial District, Teton County (Jackson)", URL_COURT_TC)
SRC_COURT_FD = S("Official Wyoming Judicial Branch, District Court of the 9th Judicial District, Fremont County", URL_COURT_FD)
SRC_COURT_FC = S("Official Wyoming Judicial Branch, Circuit Court of the 9th Judicial District, Fremont County (Lander)", URL_COURT_FC)
SRC_COURT_RV = S("Official Wyoming Judicial Branch, Circuit Court of the 9th Judicial District, Fremont County (Riverton)", URL_COURT_RV)
SRC_L22 = S("Official Lincoln County 2022 general election summary, Sublette County School District #9 sliver", URL_LINC22)
SRC_L24 = S("Official Lincoln County 2024 general election summary, Sublette County School District #9 sliver", URL_LINC24)
SRC_L26 = S("Official Lincoln County 2026 general election summary, Sublette County School District #9 sliver", URL_LINC26)
SRC_SOS12S = sos_src(2012, "Senate")
SRC_SOS12H = sos_src(2012, "House")
SRC_SOS14H = sos_src(2014, "House")
SRC_SOS16S = sos_src(2016, "Senate")
SRC_SOS16H = sos_src(2016, "House")
SRC_SOS18H = sos_src(2018, "House")
SRC_SOS20S = sos_src(2020, "Senate")
SRC_SOS20H = sos_src(2020, "House")
SRC_SOS22H = sos_src(2022, "House")
SRC_SOS24S = sos_src(2024, "Senate")
SRC_SOS24H = sos_src(2024, "House")
SRC_SOS26H = sos_src(2026, "House")


def register_people(P):
    P("WY-COOPER-STAN", "Stan Cooper", "Stan", "Cooper")
    P("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "Fred", "Baldwin", middle="A.", aliases="Fred Baldwin")
    P("WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "Laura", "Pearson",
      aliases="Laura Taliaferro Pearson; Laura Pearson; Laura Taliaferro", slug="laura-taliaferro")
    P("WY-SOMMERS-ALBERT", "Albert Sommers", "Albert", "Sommers")
    P("WY-SCHMID-MIKE", "Mike Schmid", "Mike", "Schmid")
    P("WY-HALVERSON-MARTI", "Marti Halverson", "Marti", "Halverson")
    P("WY-ROSCOE-JIM", "Jim Roscoe", "Jim", "Roscoe", aliases="Rosco")
    P("WY-BRADLEY-MACK", "Mack Bradley", "Mack", "Bradley")
    P("WY-VICKREY-DOUG", "Doug Vickrey", "Doug", "Vickrey", aliases="Douglas J. Vickrey; DOUGLAS J. VICKREY")
    P("WY-STEPHENS-DAVE", "Dave Stephens", "Dave", "Stephens")
    P("WY-WHITE-SAM", "Sam White", "Sam", "White")
    P("WY-BERNARD-LYNN-E", "Lynn E. Bernard", "Lynn", "Bernard", middle="E.", aliases="Lynn Bernard")
    P("WY-NELSON-ANDY", "Andy Nelson", "Andy", "Nelson")
    P("WY-SCHAMBER-ROBIN", "Robin Schamber", "Robin", "Schamber")
    P("WY-LONG-CARRIE-S", "Carrie S. Long", "Carrie", "Long", middle="S.", aliases="Carrie Long")
    P("WY-RICE-JESSICA", "Jessica Rice", "Jessica", "Rice")
    P("WY-PARAVICINI-EMILY-D", "Emily D. Paravicini", "Emily", "Paravicini", middle="D.", aliases="Emily Paravicini")
    P("WY-ILLOWAY-LAILA", "Laila Illoway", "Laila", "Illoway")
    P("WY-LEHR-KC", "K.C. Lehr", "K.C.", "Lehr", aliases="KC Lehr; KC LEHR")
    P("WY-HATCH-TOM", "Tom Hatch", "Tom", "Hatch")
    P("WY-MELINKOVICH-CLAYTON-M", "Clayton M. Melinkovich", "Clayton", "Melinkovich", middle="M.",
      aliases="Clayton Melinkovich")
    P("WY-MONTGOMERY-JANET-K", "Janet K. Montgomery", "Janet", "Montgomery", middle="K.",
      aliases="Janet K Montgomery")
    P("WY-COVILL-CURT", "Curt Covill", "Curt", "Covill")
    # 9th JD (reuse Teton/Fremont IDs)
    P("WY-YOUNG-NORMAN-E", "Norman E. Young", "Norman", "Young", middle="E.")
    P("WY-TYLER-MARVIN-L", "Marvin L. Tyler", "Marvin", "Tyler", middle="L.")
    P("WY-DAY-TIMOTHY-C", "Timothy C. Day", "Timothy", "Day", middle="C.")
    P("WY-OWENS-MELISSA-M", "Melissa M. Owens", "Melissa", "Owens", middle="M.")
    P("WY-CONDER-JASON-M", "Jason M. Conder", "Jason", "Conder", middle="M.")
    P("WY-MCKAY-KATHARINE-G", "Katharine G. McKay", "Katharine", "McKay", middle="G.",
      aliases="Katherine G. McKay; Kate G. McKay; KATHERINE G. MCKAY")
    P("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", "Wesley", "Roberts", middle="A.")
    P("WY-WEISMAN-ERIN-E", "Erin E. Weisman", "Erin", "Weisman", middle="E.")
    P("WY-DENHARDT-ROBERT-B", "Robert B. Denhardt", "Robert", "Denhardt", middle="B.")
    P("WY-HAWS-CURT-A", "Curt A. Haws", "Curt", "Haws", middle="A.")
    P("WY-RADDA-JAMES-L", "James L. Radda", "James", "Radda", middle="L.")
    P("WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "Jefferson Boone", "Coombs")
    P("WY-STEBNER-DANIEL-M", "Daniel M. Stebner", "Daniel", "Stebner", middle="M.")
    P("WY-LABUDA-JOHN", "John LaBuda", "John", "LaBuda", aliases="John Labuda; JOHN LABUDA")
    # Municipal
    P("WY-MURDOCK-MATT", "Matt Murdock", "Matt", "Murdock")
    P("WY-SWAFFORD-TYLER", "Tyler Swafford", "Tyler", "Swafford")
    P("WY-LOFTUS-DEAN", "Dean Loftus", "Dean", "Loftus")
    P("WY-BOYCE-JUDI", "Judi Boyce", "Judi", "Boyce")
    P("WY-KOSIBA-SCOTT", "Scott Kosiba", "Scott", "Kosiba")
    P("WY-ROBINSON-JIM", "Jim Robinson", "Jim", "Robinson")
    P("WY-MCCORMICK-JEFF", "Jeff McCormick", "Jeff", "McCormick")
    P("WY-MCMANNIS-ROGER", "Roger McMannis", "Roger", "McMannis")
    P("WY-MEADOR-BJ", "BJ Meador", "BJ", "Meador")
    P("WY-WENZ-KAREN", "Karen Wenz", "Karen", "Wenz")
    # Schools
    P("WY-NELSON-CHRIS", "Chris Nelson", "Chris", "Nelson")
    P("WY-MCGINNIS-JESSIE", "Jessie McGinnis", "Jessie", "McGinnis", aliases="Jesse McGinnis; JESSE MCGINNIS")
    P("WY-PRIOR-CHARLES-E", "Charles E. Prior", "Charles", "Prior", middle="E.")
    P("WY-ZIEGLER-JAMISON", "Jamison Ziegler", "Jamison", "Ziegler")
    P("WY-MURPHY-ANGIE", "Angie Murphy", "Angie", "Murphy")
    P("WY-OLSON-CLAYTON", "Clayton Olson", "Clayton", "Olson")
    P("WY-GOODRICH-CHAUNCEY", "Chauncey Goodrich", "Chauncey", "Goodrich")
    P("WY-BOLGIANO-TARA", "Tara Bolgiano", "Tara", "Bolgiano")
    P("WY-SLUYTER-MICKI", "Micki Sluyter", "Micki", "Sluyter")
    P("WY-VICKREY-ALAN", "Alan Vickrey", "Alan", "Vickrey")
    P("WY-CHEKAN-JOHN", "John Chekan", "John", "Chekan")
    P("WY-RAZA-CODY-W", "Cody W. Raza", "Cody", "Raza", middle="W.", aliases="Cody W Raza")
    P("WY-OTT-HAYDEN", "Hayden Ott", "Hayden", "Ott")
    P("WY-BANKS-JEREMY", "Jeremy Banks", "Jeremy", "Banks")
    P("WY-POLK-JESSICA-JOSETTE", "Jessica Josette Polk", "Jessica Josette", "Polk")
    P("WY-MCLAIN-BROCK-FORREST", "Brock Forrest McLain", "Brock Forrest", "McLain")
    # Specials
    P("WY-HITTLE-CARMEN", "Carmen Hittle", "Carmen", "Hittle")
    P("WY-SCHOOLEY-MARY-ELLEN", "Mary Ellen Schooley", "Mary Ellen", "Schooley")
    P("WY-THAYNE-HOLLY-S", "Holly S. Thayne", "Holly", "Thayne", middle="S.", aliases="Holly S Thayne")
    P("WY-ZIEGLER-SHARRON", "Sharron Ziegler", "Sharron", "Ziegler")
    P("WY-GOULETTE-JANET-K", "Janet K. Goulette", "Janet", "Goulette", middle="K.", aliases="Janet K Goulette")
    P("WY-DIBBEN-DWIGHT", "Dwight Dibben", "Dwight", "Dibben")
    P("WY-VAN-CINDY", "Cindy Van", "Cindy", "Van")
    P("WY-NOBLE-ZACHARY-M", "Zachary M. Noble", "Zachary", "Noble", middle="M.", aliases="Zachary M Noble")
    P("WY-PENTON-SALLY", "Sally Penton", "Sally", "Penton")
    P("WY-KOZEAL-MARGARET", "Margaret Kozeal", "Margaret", "Kozeal")
    P("WY-MORRISON-FRANK", "Frank Morrison", "Frank", "Morrison")
    P("WY-NICHOLS-SPENCER", "Spencer Nichols", "Spencer", "Nichols")
    P("WY-LEONARD-LINDA", "Linda Leonard", "Linda", "Leonard")
    P("WY-WILSON-BOB", "Bob Wilson", "Bob", "Wilson")
    P("WY-WILLIAMS-VALERIE-W", "Valerie W. Williams", "Valerie", "Williams", middle="W.")
    P("WY-LOCKWOOD-JEANNIE", "Jeannie Lockwood", "Jeannie", "Lockwood")
    P("WY-SPRINGMAN-TERRIE-A", "Terrie A. Springman", "Terrie", "Springman", middle="A.", aliases="Terrie A Springman")
    P("WY-BELL-DAVID-J", "David J. Bell", "David", "Bell", middle="J.")
    P("WY-TANNER-KENDA", "Kenda Tanner", "Kenda", "Tanner")
    P("WY-TATRO-ASHLI", "Ashli Tatro", "Ashli", "Tatro")
    P("WY-HOFFMAN-TONIA", "Tonia Hoffman", "Tonia", "Hoffman")
    P("WY-NOBLE-TOM", "Tom Noble", "Tom", "Noble")
    P("WY-TELFER-KELLY", "Kelly Telfer", "Kelly", "Telfer")
    P("WY-LANDERS-COKE", "Coke Landers", "Coke", "Landers")
    P("WY-WALKER-DARRELL", "Darrell Walker", "Darrell", "Walker")
    P("WY-PAPE-DAVID", "David Pape", "David", "Pape")
    P("WY-SMITH-MEGHANN", "Meghann Smith", "Meghann", "Smith")
    P("WY-LOCKWOOD-MILFORD", "Milford Lockwood", "Milford", "Lockwood")
    P("WY-STETSON-JEAN", "Jean Stetson", "Jean", "Stetson")


def legislature_terms():
    terms = []
    terms += [
        T(person_id="WY-COOPER-STAN", name="Stan Cooper", party="R", office_group="state-senate",
          office="Senate District 14 (S14)", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_SOS12S],
          notes="Official 2012 SOS statewide Senate summary, Senate District 14: Stan Cooper (R) Total 6,766, John Vincent Love (CTRY) 978. Official Sublette share Cooper 3,235, Love 325; official Lincoln 1,594–243; official Sweetwater 1,317–302; official Uinta 620–108."),
        T(person_id="WY-BALDWIN-FRED-A", name="Fred A. Baldwin", party="R", office_group="state-senate",
          office="Senate District 14 (S14)", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_SOS16S],
          notes="Official 2016 SOS statewide Senate summary, Senate District 14 (left column beside Senate District 16; that district's Total is not used): Fred A. Baldwin (R) 6,939, Sedey (D) 1,237. Official Sublette share Baldwin 3,110, Sedey 577; official Lincoln 1,663–225; official Sweetwater 1,560–329; official Uinta 606–106."),
        T(person_id="WY-BALDWIN-FRED-A", name="Fred A. Baldwin", party="R", office_group="state-senate",
          office="Senate District 14 (S14)", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_SOS20S],
          notes="Official 2020 SOS statewide Senate summary, Senate District 14: Fred A. Baldwin Total 7,779. Official Sublette share 3,740; official Lincoln 1,709; official Sweetwater 1,640; official Uinta 690 (3,740+1,709+1,640+690=7,779)."),
        T(person_id="WY-PEARSON-LAURA", name="Laura Taliaferro (formerly Pearson)", party="R",
          office_group="state-senate", office="Senate District 14 (S14)",
          term_start=FM[2025], term_end=FM[2029], election_year=2024,
          sources=[SRC_SOS24S, SRC_C24], ballot_name="Laura Taliaferro Pearson",
          notes="Official 2024 SOS statewide Senate summary, Senate District 14: official ballot name Laura Taliaferro Pearson (R) Total 8,025. Official Sublette share 3,965 (official 2024 Sublette clerk 3,965); official Lincoln 2,116; official Sweetwater 1,351; official Uinta 593 (sums to 8,025). Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA."),
    ]
    terms += [
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2013], term_end=FM[2015],
          election_year=2012, sources=[SRC_SOS12H],
          notes="Official 2012 SOS statewide House summary, House District 20: Albert Sommers Total 3,467 (Sublette-only on the official 2012 map)."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2015], term_end=FM[2017],
          election_year=2014, sources=[SRC_SOS14H],
          notes="Official 2014 SOS statewide House summary, House District 20: Albert Sommers Total 2,554 (Sublette-only on the official 2014 map)."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2017], term_end=FM[2019],
          election_year=2016, sources=[SRC_SOS16H],
          notes="Official 2016 SOS statewide House summary, House District 20 (right column beside House District 19; that district's Total is not used): Albert Sommers (R) 3,268, Brown (D) 504 (Sublette-only on the official 2016 map)."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_SOS18H],
          notes="Official 2018 SOS statewide House summary, House District 20 (right column): Albert Sommers Total 2,749 (Sublette-only on the official 2018 map)."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20H],
          notes="Official 2020 SOS statewide House summary, House District 20: Albert Sommers Total 3,939 (Sublette-only on the official 2020 map)."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2023], term_end=FM[2025],
          election_year=2022, sources=[SRC_SOS22H, SRC_C22],
          notes="Official 2022 SOS statewide House summary, House District 20 (after redistricting: Sublette and Lincoln): Albert Sommers Total 3,273. Official Sublette share 3,134; official Lincoln share 139 (3,134+139=3,273). Official 2022 Sublette clerk STATE REPRESENTATIVE Albert Sommers 3,134."),
        T(person_id="WY-SCHMID-MIKE", name="Mike Schmid", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2025], term_end=FM[2027],
          election_year=2024, sources=[SRC_SOS24H, SRC_C24],
          notes="Official 2024 SOS statewide House summary, House District 20: Mike Schmid Total 4,354. Official Sublette share 4,075; official Lincoln share 279. Official 2024 Sublette clerk H20 Mike Schmid 4,075."),
        T(person_id="WY-SOMMERS-ALBERT", name="Albert Sommers", party="R", office_group="state-house",
          office="House District 20 (H20)", term_start=FM[2027], term_end=FM[2029],
          election_year=2026, sources=[SRC_SOS26H, SRC_C26],
          notes="Official 2026 SOS statewide House summary, House District 20: Albert Sommers Total 3,349. Official Sublette share 3,195; official Lincoln share 154. Official 2026 Sublette clerk H20 Albert Sommers 3,195."),
    ]
    # H22 is on the official 2012–2020 Sublette map; official 2022+ SOS Sublette rows are blank (Lincoln+Teton only). End at January 2023 rather than inventing a holdover.
    terms += [
        T(person_id="WY-HALVERSON-MARTI", name="Marti Halverson", party="R", office_group="state-house",
          office="House District 22 (H22)", term_start=FM[2013], term_end=FM[2015],
          election_year=2012, sources=[SRC_SOS12H],
          notes="Official 2012 SOS statewide House summary, House District 22: Marti Halverson 2,407, Winney 1,927. Official Sublette share Halverson 234, Winney 175."),
        T(person_id="WY-HALVERSON-MARTI", name="Marti Halverson", party="R", office_group="state-house",
          office="House District 22 (H22)", term_start=FM[2015], term_end=FM[2017],
          election_year=2014, sources=[SRC_SOS14H],
          notes="Official 2014 SOS statewide House summary, House District 22: Marti Halverson 1,991, Macker 1,224. Official Sublette share Halverson 229, Macker 98."),
        T(person_id="WY-HALVERSON-MARTI", name="Marti Halverson", party="R", office_group="state-house",
          office="House District 22 (H22)", term_start=FM[2017], term_end=FM[2019],
          election_year=2016, sources=[SRC_SOS16H],
          notes="Official 2016 SOS statewide House summary, House District 22 (right column): Marti Halverson 2,942, Marylee White 2,157. Official Sublette share Halverson 300, White 143."),
        T(person_id="WY-ROSCOE-JIM", name="Jim Roscoe", party="I", office_group="state-house",
          office="House District 22 (H22)", term_start=FM[2019], term_end=FM[2021],
          election_year=2018, sources=[SRC_SOS18H],
          notes="Official 2018 SOS statewide House summary, House District 22 (right column): Jim Roscoe (I) 2,495, Marti Halverson 1,983. Official Sublette share Halverson 204, Roscoe 179."),
        T(person_id="WY-ROSCOE-JIM", name="Jim Roscoe", party="I", office_group="state-house",
          office="House District 22 (H22)", term_start=FM[2021], term_end=FM[2023],
          election_year=2020, sources=[SRC_SOS20H],
          notes="Official 2020 SOS statewide House summary, House District 22 (official heading Winney (R) / Rosco (I)): Jim Roscoe 3,191, Bill Winney 2,825. Official Sublette share Winney 191, Roscoe 285. After 2022 redistricting, official SOS Sublette rows for H22 are dashes (official 2022+ H22 is Lincoln and Teton). This term is ended at January 2023 rather than inventing a holdover."),
    ]
    return terms


def county_terms():
    terms = []
    # Official 2014–2020 clerk general canvasses were not found on the live /110/Election-Information page
    # or on the February 2023 Wayback capture of that page, so January 2015–2022 county seats stay Not yet collected.
    terms += [
        T(person_id="WY-BRADLEY-MACK", name="Mack Bradley", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_COMM],
          notes="Official 2022 Sublette clerk, County Commissioners Vote-For-2: Mack Bradley 2,585, Douglas J. Vickrey 2,493, Troy Bredthauer (IND) 849. Official Commissioner Profiles page: Mack Bradley, term expires 1/2/2027."),
        T(person_id="WY-VICKREY-DOUG", name="Doug Vickrey", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_COMM],
          notes="Official 2022 Sublette clerk, County Commissioners Vote-For-2: Mack Bradley 2,585, Douglas J. Vickrey 2,493. Official Commissioner Profiles page lists Doug Vickrey, term expires 1/2/2027."),
        T(person_id="WY-STEPHENS-DAVE", name="Dave Stephens", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_COMM],
          notes="Official 2024 Sublette clerk, County Commissioner Vote-For-3: Dave Stephens 3,255, Sam White 3,216, Lynn E. Bernard 3,094. Official Commissioner Profiles page: Dave Stephens, Vice Chairman, term expires 1/1/2029."),
        T(person_id="WY-WHITE-SAM", name="Sam White", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_COMM],
          notes="Official 2024 Sublette clerk, County Commissioner Vote-For-3: Dave Stephens 3,255, Sam White 3,216, Lynn E. Bernard 3,094. Official Commissioner Profiles page: Sam White, term expires 1/1/2029."),
        T(person_id="WY-BERNARD-LYNN-E", name="Lynn E. Bernard", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2025], term_end=FM[2029],
          election_year=2024, sources=[SRC_C24, SRC_COMM],
          notes="Official 2024 Sublette clerk, County Commissioner Vote-For-3: Dave Stephens 3,255, Sam White 3,216, Lynn E. Bernard 3,094. Official Commissioner Profiles page: Lynn Bernard, Chairman, term expires 1/1/2029."),
        T(person_id="WY-NELSON-ANDY", name="Andy Nelson", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_PROC],
          notes="Official 2026 Sublette clerk, County Commissioner Vote-For-2: Andy Nelson 2,088, Robin Schamber 1,831, David M. “Dave” Smith (IND) 1,620. Official 2026 proclamation placed a ballot question to reduce the board from five to three; official canvass REDUCING COMMISSIONERS FOR 1,009, AGAINST 2,659 (72.49%), so the question failed and the board remains five members."),
        T(person_id="WY-SCHAMBER-ROBIN", name="Robin Schamber", party="R", office_group="county",
          office="County Commissioner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Commissioner Vote-For-2: Andy Nelson 2,088, Robin Schamber 1,831, David M. “Dave” Smith (IND) 1,620."),
    ]
    terms += [
        T(person_id="WY-LONG-CARRIE-S", name="Carrie S. Long", party="R", office_group="county",
          office="County Clerk", term_start=FM[2023], term_end="2025-10-05",
          election_year=2022, sources=[SRC_C22, SRC_CLERK], confidence="medium",
          notes="Official 2022 Sublette clerk, County Clerk: Carrie S. Long 3,095. Official County Clerk page Wayback captures list Carrie Long as County Clerk from 2023-02-01 through 2025-04-05. The official page lists Jessica Rice as County Clerk on the 2025-10-05 capture. The official appointment or vacancy date between those official-page captures was not found; term_end uses the first official-page evidence that Jessica Rice is clerk (medium)."),
        T(person_id="WY-RICE-JESSICA", name="Jessica Rice", party="R", office_group="county",
          office="County Clerk", term_start="2025-10-05", term_end=FM[2027],
          election_year=2022, sources=[SRC_CLERK], confidence="medium", how_took_office="appointed",
          notes="Official County Clerk page, retrieved 2026-11-24 and official Wayback capture 2025-10-05: Jessica Rice, County Clerk. Official 2022 general winner was Carrie S. Long. The official appointment instrument and exact mid-term date were not found; term_start uses the first official-page evidence (medium). Continues through January 2027, then the official 2026 elective term."),
        T(person_id="WY-RICE-JESSICA", name="Jessica Rice", party="R", office_group="county",
          office="County Clerk", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26, SRC_CLERK],
          notes="Official 2026 Sublette clerk, County Clerk: Jessica Rice 3,356."),
        T(person_id="WY-PARAVICINI-EMILY-D", name="Emily D. Paravicini", party="R", office_group="county",
          office="County Treasurer", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, County Treasurer: Emily Paravicini 3,289."),
        T(person_id="WY-PARAVICINI-EMILY-D", name="Emily D. Paravicini", party="R", office_group="county",
          office="County Treasurer", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Treasurer: Emily D. Paravicini 3,319."),
        T(person_id="WY-ILLOWAY-LAILA", name="Laila Illoway", party="R", office_group="county",
          office="County Assessor", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, County Assessor: Laila Illoway 3,205."),
        T(person_id="WY-ILLOWAY-LAILA", name="Laila Illoway", party="R", office_group="county",
          office="County Assessor", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Assessor: Laila Illoway 3,315."),
        T(person_id="WY-LEHR-KC", name="K.C. Lehr", party="R", office_group="county",
          office="County Sheriff", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22, SRC_SHERIFF],
          notes="Official 2022 Sublette clerk, County Sheriff: KC Lehr 3,206. Official Sheriff page, retrieved 2026-11-24: Sheriff K.C. Lehr."),
        T(person_id="WY-HATCH-TOM", name="Tom Hatch", party="R", office_group="county",
          office="County Sheriff", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Sheriff: Tom Hatch 3,204."),
        T(person_id="WY-MELINKOVICH-CLAYTON-M", name="Clayton M. Melinkovich", party="R", office_group="county",
          office="County Attorney", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, County Attorney: Clayton M. Melinkovich 2,481, Clay Kainer (IND) 991."),
        T(person_id="WY-MELINKOVICH-CLAYTON-M", name="Clayton M. Melinkovich", party="R", office_group="county",
          office="County Attorney", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Attorney: Clayton M. Melinkovich 2,997."),
        T(person_id="WY-MONTGOMERY-JANET-K", name="Janet K. Montgomery", party="R", office_group="county",
          office="Clerk of District Court", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Clerk of District Court: Janet K. Montgomery 3,232."),
        T(person_id="WY-MONTGOMERY-JANET-K", name="Janet K. Montgomery", party="R", office_group="county",
          office="Clerk of District Court", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Clerk of District Court: Janet K Montgomery 3,331."),
        T(person_id="WY-COVILL-CURT", name="Curt Covill", party="R", office_group="county",
          office="County Coroner", term_start=FM[2023], term_end=FM[2027],
          election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, County Coroner: Curt Covill 3,307."),
        T(person_id="WY-COVILL-CURT", name="Curt Covill", party="R", office_group="county",
          office="County Coroner", term_start=FM[2027], term_end=FM[2031],
          election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, County Coroner: Curt Covill 3,371."),
    ]
    return terms


def judicial_terms():
    # Same 9th JD people and official court dates already used in the Teton history, with official Sublette retention totals where the official clerk named the judge.
    jd = "9th Judicial District"
    terms = []
    terms += [
        T(person_id="WY-YOUNG-NORMAN-E", name="Norman E. Young", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2011], term_end=FM[2017],
          election_year=2010, sources=[SRC_COURT_D, SRC_COURT_TD],
          notes="Official Wyoming Judicial Branch 9th JD district pages; official 2010 SOS retention of Norman E. Young (same term dates as the Teton history)."),
        T(person_id="WY-YOUNG-NORMAN-E", name="Norman E. Young", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2017], term_end=FM[2023],
          election_year=2016, sources=[SRC_COURT_D, SRC_COURT_TD],
          notes="Official 2016 SOS retention of Norman E. Young. Official Sublette 9th JD district page later lists Katharine G. McKay after January 2023."),
        T(person_id="WY-TYLER-MARVIN-L", name="Marvin L. Tyler", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2011], term_end=FM[2017],
          election_year=2010, sources=[SRC_COURT_FD],
          notes="Official Wyoming Judicial Branch 9th JD district pages; official 2010 SOS retention of Marvin L. Tyler."),
        T(person_id="WY-TYLER-MARVIN-L", name="Marvin L. Tyler", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2017], term_end=FM[2023],
          election_year=2016, sources=[SRC_COURT_FD],
          notes="Official 2016 SOS retention of Marvin L. Tyler. No official departure date after January 2023 is invented."),
        T(person_id="WY-DAY-TIMOTHY-C", name="Timothy C. Day", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2013], term_end=FM[2019],
          election_year=2012, sources=[SRC_COURT_TD],
          notes="Official 2012 SOS retention of Timothy C. Day."),
        T(person_id="WY-DAY-TIMOTHY-C", name="Timothy C. Day", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2019], term_end="2022-01-01",
          election_year=2018, sources=[SRC_COURT_TD],
          notes="Official 2018 SOS retention of Timothy C. Day. Official Wyoming Judicial Branch Teton 9th JD district page: succeeded in January 2022 (day unstated; term_end 2022-01-01, medium on the day)."),
        T(person_id="WY-OWENS-MELISSA-M", name="Melissa M. Owens", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start="2022-01-01", term_end="2031-01-06",
          election_year=2024, sources=[SRC_COURT_TD, SRC_C24], how_took_office="appointed",
          notes="Official Wyoming Judicial Branch Teton 9th JD district page: appointed January 2022 (day unstated; term_start 2022-01-01, medium on the day), retained November 2024. Official 2024 Sublette clerk: DISTRICT COURT JUDGE NINTH JUDICIAL DISTRICT MELISSA M. OWENS YES 3,300, NO 755."),
        T(person_id="WY-CONDER-JASON-M", name="Jason M. Conder", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start="2019-07-01", term_end=FM[2027],
          election_year=2020, sources=[SRC_COURT_FD], how_took_office="appointed",
          notes="Official Wyoming Judicial Branch Fremont 9th JD district page: appointed July 2019 (day unstated; term_start 2019-07-01, medium on the day)."),
        T(person_id="WY-CONDER-JASON-M", name="Jason M. Conder", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start=FM[2027], term_end="2031-01-06",
          election_year=2026, sources=[SRC_COURT_FD, SRC_C26],
          notes="Official 2026 Sublette clerk: JUDGE JASON M. CONDER YES 2,318, NO 638. Official Fremont 9th JD district page: Jason M. Conder, retained, continuing January 2027–2031."),
        T(person_id="WY-MCKAY-KATHARINE-G", name="Katharine G. McKay", office_group="judicial",
          office="District Judge, 9th Judicial District", term_start="2023-01-01", term_end="2031-01-06",
          election_year=2024, sources=[SRC_COURT_D, SRC_C24], how_took_office="appointed",
          notes="Official Wyoming Judicial Branch Sublette 9th JD district page: Honorable Kate G. McKay, appointed January 2023 (day unstated; term_start 2023-01-01, medium on the day), retained November 2024. Official 2024 Sublette clerk prints KATHERINE G. MCKAY YES 3,315, NO 709; display name follows the official court/SOS spelling Katharine G. McKay already used in the Teton history (person ID WY-MCKAY-KATHARINE-G)."),
    ]
    terms += [
        T(person_id="WY-ROBERTS-WESLEY-A", name="Wesley A. Roberts", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2011], term_end=FM[2015],
          election_year=2010, sources=[SRC_COURT_TC]),
        T(person_id="WY-ROBERTS-WESLEY-A", name="Wesley A. Roberts", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2015], term_end=FM[2019],
          election_year=2014, sources=[SRC_COURT_TC]),
        T(person_id="WY-ROBERTS-WESLEY-A", name="Wesley A. Roberts", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2019], term_end=FM[2023],
          election_year=2018, sources=[SRC_COURT_TC]),
        T(person_id="WY-ROBERTS-WESLEY-A", name="Wesley A. Roberts", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2023], term_end="2024-08-01",
          election_year=2022, sources=[SRC_COURT_TC, SRC_C22],
          notes="Official 2022 SOS names Wesley A. Roberts among 9th JD circuit retentions. Official 2022 Sublette clerk prints two unnamed “FOR JUDGE OF THE CIRCUIT COURT OF THE NINTH JUDICIAL DISTRICT FOR A REGULAR FOUR (4) YEAR TERM” contests (YES 2,590 / NO 490 and YES 2,483 / NO 527) and does not print the judges’ names; those official Sublette totals are not assigned to a named judge. Official Wyoming Judicial Branch Jackson circuit page: term ended August 2024 (day unstated; term_end 2024-08-01, medium on the day)."),
        T(person_id="WY-WEISMAN-ERIN-E", name="Erin E. Weisman", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start="2024-08-01", term_end=FM[2027],
          sources=[SRC_COURT_TC], how_took_office="appointed", confidence="medium",
          notes="Official Wyoming Judicial Branch Jackson circuit page: appointed August 2024 (day unstated; term_start 2024-08-01, medium on the day)."),
        T(person_id="WY-WEISMAN-ERIN-E", name="Erin E. Weisman", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2027], term_end="2031-01-06",
          election_year=2026, sources=[SRC_COURT_TC, SRC_C26],
          notes="Official 2026 Sublette clerk: CIRCUIT COURT JUDGE WEISMAN YES 2,275, NO 648. Full name Erin E. Weisman is from the official court page and official Teton clerk."),
        T(person_id="WY-DENHARDT-ROBERT-B", name="Robert B. Denhardt", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_COURT_FC]),
        T(person_id="WY-DENHARDT-ROBERT-B", name="Robert B. Denhardt", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_COURT_FC]),
        T(person_id="WY-DENHARDT-ROBERT-B", name="Robert B. Denhardt", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_COURT_FC],
          notes="Official 2020 SOS: Robert B. Denhardt."),
        T(person_id="WY-HAWS-CURT-A", name="Curt A. Haws", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_COURT_FC]),
        T(person_id="WY-HAWS-CURT-A", name="Curt A. Haws", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_COURT_FC]),
        T(person_id="WY-HAWS-CURT-A", name="Curt A. Haws", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_COURT_FC],
          notes="Official 2020 SOS: Curt A. Haws."),
        T(person_id="WY-RADDA-JAMES-L", name="James L. Radda", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2013], term_end=FM[2017],
          election_year=2012, sources=[SRC_COURT_RV]),
        T(person_id="WY-RADDA-JAMES-L", name="James L. Radda", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2017], term_end=FM[2021],
          election_year=2016, sources=[SRC_COURT_RV]),
        T(person_id="WY-RADDA-JAMES-L", name="James L. Radda", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2021], term_end=FM[2025],
          election_year=2020, sources=[SRC_COURT_RV],
          notes="Official 2020 SOS: James L. Radda."),
        T(person_id="WY-COOMBS-JEFFERSON-BOONE", name="Jefferson Boone Coombs", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start="2021-10-01", term_end=FM[2027],
          sources=[SRC_COURT_FC], how_took_office="appointed", confidence="medium",
          notes="Official Wyoming Judicial Branch Lander circuit page: Jefferson Coombs, appointed October 2021 (day unstated; term_start 2021-10-01, medium on the day)."),
        T(person_id="WY-COOMBS-JEFFERSON-BOONE", name="Jefferson Boone Coombs", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start=FM[2027], term_end="2031-01-06",
          election_year=2026, sources=[SRC_COURT_FC, SRC_C26],
          notes="Official 2026 Sublette clerk: CIRCUIT COURT JUDGE COOMBS YES 2,268, NO 612. Full name Jefferson Boone Coombs is from the official court page and official Teton clerk."),
        T(person_id="WY-STEBNER-DANIEL-M", name="Daniel M. Stebner", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start="2023-02-01", term_end=FM[2029],
          election_year=2024, sources=[SRC_COURT_RV, SRC_C24], how_took_office="appointed",
          notes="Official Wyoming Judicial Branch Riverton circuit page: appointed February 2023 (day unstated; term_start 2023-02-01, medium on the day). Official 2024 Sublette clerk: CIRCUIT COURT JUDGE NINTH JUDICIAL DISTRICT DANIEL M. STEBNER YES 3,348, NO 617."),
        T(person_id="WY-LABUDA-JOHN", name="John LaBuda", office_group="judicial",
          office="Circuit Judge, 9th Judicial District", term_start="2023-01-01", term_end=FM[2029],
          election_year=2024, sources=[SRC_COURT_C, SRC_C24], how_took_office="appointed",
          notes="Official Wyoming Judicial Branch Pinedale circuit page: appointed January 2023 (day unstated; term_start 2023-01-01, medium on the day). Official 2024 Sublette clerk: CIRCUIT COURT JUDGE NINTH JUDICIAL DISTRICT JOHN LABUDA YES 3,489, NO 724. Display name John LaBuda follows the official court page already used in the Teton history (person ID WY-LABUDA-JOHN)."),
    ]
    return terms


def municipal_terms():
    terms = []
    # Official Pinedale council page lists current terms ending May 31 of the stated year (4-year May terms).
    terms += [
        T(person_id="WY-MURDOCK-MATT", name="Matt Murdock", office_group="municipal",
          office="Pinedale Mayor", term_start="2026-06-01", term_end="2030-05-31",
          election_year=2026, sources=[SRC_PINEDALE, SRC_PINEDALE_ELEX],
          notes="Official Town of Pinedale council page: Mayor Matt Murdock, term expires May 31, 2030. Official 2026 municipal election results page: Mayor Matt Murdock 49 (write-in Chad Mitchell variants combined 20, not certified over Murdock). A prior official municipal canvass was not found, so a 2022–2026 term is not invented; January 2015–2026 snapshots therefore do not list this June 2026 term."),
        T(person_id="WY-SWAFFORD-TYLER", name="Tyler Swafford", office_group="municipal",
          office="Pinedale Council", term_start="2024-06-01", term_end="2028-05-31",
          election_year=2024, sources=[SRC_PINEDALE], confidence="medium",
          notes="Official Town of Pinedale council page: Tyler Swafford, term expires May 31, 2028. Official 2024 municipal canvass was not archived; term_start is inferred from the official four-year May term ending May 31, 2028 (medium)."),
        T(person_id="WY-BOYCE-JUDI", name="Judi Boyce", office_group="municipal",
          office="Pinedale Council", term_start="2024-06-01", term_end="2028-05-31",
          election_year=2024, sources=[SRC_PINEDALE], confidence="medium",
          notes="Official Town of Pinedale council page: Judi Boyce, term expires May 31, 2028. Official 2024 municipal canvass was not archived; term_start is inferred from the official four-year May term (medium)."),
        T(person_id="WY-LOFTUS-DEAN", name="Dean Loftus", office_group="municipal",
          office="Pinedale Council", term_start="2026-06-01", term_end="2030-05-31",
          election_year=2026, sources=[SRC_PINEDALE, SRC_PINEDALE_ELEX],
          notes="Official Town of Pinedale council page: Dean Loftus, term expires May 31, 2030. Official 2026 municipal election results page: council Dean Loftus 65, Scott Kosiba 51."),
        T(person_id="WY-KOSIBA-SCOTT", name="Scott Kosiba", office_group="municipal",
          office="Pinedale Council", term_start="2026-06-01", term_end="2030-05-31",
          election_year=2026, sources=[SRC_PINEDALE_ELEX], confidence="medium",
          notes="Official Town of Pinedale 2026 municipal election results page: council Dean Loftus 65, Scott Kosiba 51. Term end May 31, 2030 follows the official four-year council term used on the official council page for the same 2026 election (medium on the end date; the live official council HTML did not print the name Kosiba)."),
    ]
    # Official Marbleton council page states term-expire years only (no month/day).
    terms += [
        T(person_id="WY-ROBINSON-JIM", name="Jim Robinson", office_group="municipal",
          office="Marbleton Mayor", term_start="2025-06-01", term_end="2029-05-31",
          election_year=2025, sources=[SRC_MARBLETON], confidence="medium",
          notes="Official Town of Marbleton council page: Jim Robinson, Mayor, term expires 2029. Official page does not state the month or day; May 31 and a June 1 start are used for consistency with official Pinedale four-year May terms (medium)."),
        T(person_id="WY-MCCORMICK-JEFF", name="Jeff McCormick", office_group="municipal",
          office="Marbleton Council", term_start="2023-06-01", term_end="2027-05-31",
          election_year=2023, sources=[SRC_MARBLETON], confidence="medium",
          notes="Official Town of Marbleton council page: Jeff McCormick, Council Member, term expires 2027. Month/day not stated on the official page (medium)."),
        T(person_id="WY-MCMANNIS-ROGER", name="Roger McMannis", office_group="municipal",
          office="Marbleton Council", term_start="2023-06-01", term_end="2027-05-31",
          election_year=2023, sources=[SRC_MARBLETON], confidence="medium",
          notes="Official Town of Marbleton council page: Roger McMannis, Council Member, term expires 2027. Month/day not stated on the official page (medium)."),
        T(person_id="WY-MEADOR-BJ", name="BJ Meador", office_group="municipal",
          office="Marbleton Council", term_start="2025-06-01", term_end="2029-05-31",
          election_year=2025, sources=[SRC_MARBLETON], confidence="medium",
          notes="Official Town of Marbleton council page: BJ Meador, Council Member, term expires 2029. Month/day not stated on the official page (medium)."),
        T(person_id="WY-WENZ-KAREN", name="Karen Wenz", office_group="municipal",
          office="Marbleton Council", term_start="2025-06-01", term_end="2029-05-31",
          election_year=2025, sources=[SRC_MARBLETON], confidence="medium",
          notes="Official Town of Marbleton council page: Karen Wenz, Council Member, term expires 2029. Month/day not stated on the official page (medium)."),
    ]
    # Official Town of Big Piney site (bigpineywyoming.us) returned a Cloudflare challenge / 403 from this collection environment. No official town council page, official minutes, official canvass, or Wayback capture of an official town roster was retrieved, so Big Piney mayor and council stay Not yet collected. Secondary directories are not used.
    return terms


def school_terms():
    terms = []
    s1 = "Sublette County School District #1 Trustee"
    s9 = "Sublette County School District #9 Trustee"
    s9_2 = "Sublette County School District #9 Trustee (2-year)"
    terms += [
        T(person_id="WY-NELSON-CHRIS", name="Chris Nelson", office_group="schools", office=s1,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, School District #1 Trustees Vote-For-4: Chris Nelson 1,689, Jesse McGinnis 1,579, Jamison Ziegler 1,473, Charles E. Prior 1,320, Bill Winney 954."),
        T(person_id="WY-MCGINNIS-JESSIE", name="Jessie McGinnis", office_group="schools", office=s1,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk spelling is Jesse McGinnis (1,579). Official 2026 Sublette clerk spelling is Jessie McGinnis. One person, ID WY-MCGINNIS-JESSIE; current display follows the official 2026 ballot."),
        T(person_id="WY-ZIEGLER-JAMISON", name="Jamison Ziegler", office_group="schools", office=s1,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, School District #1 Trustees Vote-For-4: Jamison Ziegler 1,473."),
        T(person_id="WY-PRIOR-CHARLES-E", name="Charles E. Prior", office_group="schools", office=s1,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, School District #1 Trustees Vote-For-4: Charles E. Prior 1,320."),
        T(person_id="WY-MURPHY-ANGIE", name="Angie Murphy", office_group="schools", office=s1,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, School District #1 Trustees At Large Vote-For-3: Angie Murphy 2,222, Clayton Olson 2,168, Chauncey Goodrich 1,924."),
        T(person_id="WY-OLSON-CLAYTON", name="Clayton Olson", office_group="schools", office=s1,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, School District #1 Trustees At Large Vote-For-3: Angie Murphy 2,222, Clayton Olson 2,168, Chauncey Goodrich 1,924."),
        T(person_id="WY-GOODRICH-CHAUNCEY", name="Chauncey Goodrich", office_group="schools", office=s1,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, School District #1 Trustees At Large Vote-For-3: Angie Murphy 2,222, Clayton Olson 2,168, Chauncey Goodrich 1,924."),
        T(person_id="WY-BOLGIANO-TARA", name="Tara Bolgiano", office_group="schools", office=s1,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, School Distr. #1 At Large Vote-For-4: Tara Bolgiano 1,408, Micki Sluyter 1,312, Chris Nelson 929, Jessie McGinnis 784 (L. Jenny James 736 fifth)."),
        T(person_id="WY-SLUYTER-MICKI", name="Micki Sluyter", office_group="schools", office=s1,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, School Distr. #1 At Large Vote-For-4: Tara Bolgiano 1,408, Micki Sluyter 1,312, Chris Nelson 929, Jessie McGinnis 784."),
        T(person_id="WY-NELSON-CHRIS", name="Chris Nelson", office_group="schools", office=s1,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, School Distr. #1 At Large Vote-For-4: Chris Nelson 929 (reelected)."),
        T(person_id="WY-MCGINNIS-JESSIE", name="Jessie McGinnis", office_group="schools", office=s1,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, School Distr. #1 At Large Vote-For-4: Jessie McGinnis 784 (reelected)."),
    ]
    comb = "Official Lincoln sliver is combined into the official whole-district result; ranking is unchanged."
    terms += [
        T(person_id="WY-VICKREY-ALAN", name="Alan Vickrey", office_group="schools", office=s9,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22, SRC_L22],
          notes="Official 2022 Sublette clerk, School District #9 Trustees Vote-For-2: Alan Vickrey 667, John Chekan 501. Official 2022 Lincoln clerk sliver: Vickrey 219, Chekan 88. Combined whole-district: Vickrey 886, Chekan 589. " + comb),
        T(person_id="WY-CHEKAN-JOHN", name="John Chekan", office_group="schools", office=s9,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22, SRC_L22],
          notes="Official 2022 Sublette clerk, School District #9 Trustees Vote-For-2: Alan Vickrey 667, John Chekan 501. Combined with official Lincoln sliver: Vickrey 886, Chekan 589. " + comb),
        T(person_id="WY-RAZA-CODY-W", name="Cody W. Raza", office_group="schools", office=s9,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24, SRC_L24],
          notes="Official 2024 Sublette clerk, School District #9 Trustees At Large Vote-For-3: Cody W Raza 831, Hayden Ott 625, Jeremy Banks 496. Official 2024 Lincoln clerk sliver: Raza 202, Banks 162, Ott 120. Combined whole-district: Raza 1,033, Ott 745, Banks 658. " + comb),
        T(person_id="WY-OTT-HAYDEN", name="Hayden Ott", office_group="schools", office=s9,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24, SRC_L24],
          notes="Official 2024 combined Sublette+Lincoln CSD #9: Cody W. Raza 1,033, Hayden Ott 745, Jeremy Banks 658. " + comb),
        T(person_id="WY-BANKS-JEREMY", name="Jeremy Banks", office_group="schools", office=s9,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24, SRC_L24],
          notes="Official 2024 combined Sublette+Lincoln CSD #9: Cody W. Raza 1,033, Hayden Ott 745, Jeremy Banks 658. " + comb),
        T(person_id="WY-VICKREY-ALAN", name="Alan Vickrey", office_group="schools", office=s9,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26, SRC_L26],
          notes="Official 2026 Sublette clerk, School Distr. #9 At Large Vote-For-2: Alan Vickrey 463, Jessica Josette Polk 390, John Chekan 319. Official 2026 Lincoln clerk sliver: Vickrey 181, Polk 99 (no official Lincoln Chekan line). Combined: Vickrey 644, Polk 489, Chekan 319. " + comb),
        T(person_id="WY-POLK-JESSICA-JOSETTE", name="Jessica Josette Polk", office_group="schools", office=s9,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26, SRC_L26],
          notes="Official 2026 combined Sublette+Lincoln CSD #9 4-year: Alan Vickrey 644, Jessica Josette Polk 489, John Chekan 319. " + comb),
        T(person_id="WY-MCLAIN-BROCK-FORREST", name="Brock Forrest McLain", office_group="schools", office=s9_2,
          term_start=FM[2027], term_end=FM[2029], election_year=2026, sources=[SRC_C26, SRC_L26],
          notes="Official 2026 Sublette clerk, School Distr. #9 At Large 2YR: Brock Forrest McLain 455, Taylor Moceika 191. Official 2026 Lincoln clerk sliver: Moceika 128, McLain 92 (Lincoln portion alone had Moceika ahead). Combined whole-district: McLain 547, Moceika 319, ranking unchanged. The official 2-year seat is not tied to a named departing 2024 trustee."),
    ]
    return terms


def special_terms():
    terms = []
    ug = "Upper Green River Cemetery District Trustee"
    ug2 = "Upper Green River Cemetery District Trustee (2-year)"
    bp = "Big Piney Cemetery District Trustee"
    hosp = "Sublette County Hospital District Trustee"
    soil = "Soil Conservation District Supervisor"
    atlg = "Conservation District Supervisor At-Large"
    rural = "Conservation District Supervisor Rural"
    urban = "Conservation District Supervisor Urban"
    terms += [
        T(person_id="WY-THAYNE-HOLLY-S", name="Holly S. Thayne", office_group="special-districts", office=ug,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Holly S. Thayne 1,983, Carmen Hittle 1,834, Mary Ellen Schooley 1,745."),
        T(person_id="WY-HITTLE-CARMEN", name="Carmen Hittle", office_group="special-districts", office=ug,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Holly S. Thayne 1,983, Carmen Hittle 1,834, Mary Ellen Schooley 1,745."),
        T(person_id="WY-SCHOOLEY-MARY-ELLEN", name="Mary Ellen Schooley", office_group="special-districts", office=ug,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Holly S. Thayne 1,983, Carmen Hittle 1,834, Mary Ellen Schooley 1,745."),
        T(person_id="WY-ZIEGLER-SHARRON", name="Sharron Ziegler", office_group="special-districts", office=ug,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Sharron Ziegler 2,404, Dwight Dibben 2,327, Janet K Goulette 2,290."),
        T(person_id="WY-DIBBEN-DWIGHT", name="Dwight Dibben", office_group="special-districts", office=ug,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Sharron Ziegler 2,404, Dwight Dibben 2,327, Janet K Goulette 2,290."),
        T(person_id="WY-GOULETTE-JANET-K", name="Janet K. Goulette", office_group="special-districts", office=ug,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-3: Sharron Ziegler 2,404, Dwight Dibben 2,327, Janet K Goulette 2,290."),
        T(person_id="WY-VAN-CINDY", name="Cindy Van", office_group="special-districts", office=ug2,
          term_start=FM[2025], term_end=FM[2027], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Upper Green River Cemetery District Trustees Vote-For-1 (2-year): Cindy Van 2,860. No official 2026 2-year contest was on the official November general."),
        T(person_id="WY-THAYNE-HOLLY-S", name="Holly S. Thayne", office_group="special-districts", office=ug,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Trustee, Upper Green River Cemetery District Vote-For-3: Holly S Thayne 1,586, Zachary M Noble 1,556, Sally Penton 1,530 (Carmen Hittle 1,196 fourth)."),
        T(person_id="WY-NOBLE-ZACHARY-M", name="Zachary M. Noble", office_group="special-districts", office=ug,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Upper Green River Cemetery Vote-For-3: Holly S Thayne 1,586, Zachary M Noble 1,556, Sally Penton 1,530."),
        T(person_id="WY-PENTON-SALLY", name="Sally Penton", office_group="special-districts", office=ug,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Upper Green River Cemetery Vote-For-3: Holly S Thayne 1,586, Zachary M Noble 1,556, Sally Penton 1,530."),
    ]
    terms += [
        T(person_id="WY-KOZEAL-MARGARET", name="Margaret Kozeal", office_group="special-districts", office=bp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Margaret Kozeal 653, Spencer Nichols 646, Frank Morrison 579."),
        T(person_id="WY-NICHOLS-SPENCER", name="Spencer Nichols", office_group="special-districts", office=bp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Margaret Kozeal 653, Spencer Nichols 646, Frank Morrison 579."),
        T(person_id="WY-MORRISON-FRANK", name="Frank Morrison", office_group="special-districts", office=bp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Margaret Kozeal 653, Spencer Nichols 646, Frank Morrison 579."),
        T(person_id="WY-WILSON-BOB", name="Bob Wilson", office_group="special-districts", office=bp,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Bob Wilson 809, Valerie W. Williams 776, Linda Leonard 733."),
        T(person_id="WY-WILLIAMS-VALERIE-W", name="Valerie W. Williams", office_group="special-districts", office=bp,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Bob Wilson 809, Valerie W. Williams 776, Linda Leonard 733."),
        T(person_id="WY-LEONARD-LINDA", name="Linda Leonard", office_group="special-districts", office=bp,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Big Piney Cemetery District Trustees Vote-For-3: Bob Wilson 809, Valerie W. Williams 776, Linda Leonard 733."),
        T(person_id="WY-LOCKWOOD-JEANNIE", name="Jeannie Lockwood", office_group="special-districts", office=bp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Trustee, Big Piney Cemetery District Vote-For-3: Jeannie Lockwood 604, Terrie A Springman 594, Margaret Kozeal 567."),
        T(person_id="WY-SPRINGMAN-TERRIE-A", name="Terrie A. Springman", office_group="special-districts", office=bp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Big Piney Cemetery Vote-For-3: Jeannie Lockwood 604, Terrie A Springman 594, Margaret Kozeal 567."),
        T(person_id="WY-KOZEAL-MARGARET", name="Margaret Kozeal", office_group="special-districts", office=bp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Big Piney Cemetery Vote-For-3: Jeannie Lockwood 604, Terrie A Springman 594, Margaret Kozeal 567 (reelected)."),
    ]
    terms += [
        T(person_id="WY-TANNER-KENDA", name="Kenda Tanner", office_group="special-districts", office=hosp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Sublette County Hospital District Trustees Vote-For-3: Kenda Tanner 2,537, David J. Bell 2,455, Ashli Tatro 2,295."),
        T(person_id="WY-BELL-DAVID-J", name="David J. Bell", office_group="special-districts", office=hosp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Hospital District Trustees Vote-For-3: Kenda Tanner 2,537, David J. Bell 2,455, Ashli Tatro 2,295."),
        T(person_id="WY-TATRO-ASHLI", name="Ashli Tatro", office_group="special-districts", office=hosp,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Hospital District Trustees Vote-For-3: Kenda Tanner 2,537, David J. Bell 2,455, Ashli Tatro 2,295."),
        T(person_id="WY-HOFFMAN-TONIA", name="Tonia Hoffman", office_group="special-districts", office=hosp,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Sublette County Hospital District Trustees Vote-For-2: Tonia Hoffman 3,218, Jamison Ziegler 2,912."),
        T(person_id="WY-ZIEGLER-JAMISON", name="Jamison Ziegler", office_group="special-districts", office=hosp,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Hospital District Trustees Vote-For-2: Tonia Hoffman 3,218, Jamison Ziegler 2,912."),
        T(person_id="WY-TANNER-KENDA", name="Kenda Tanner", office_group="special-districts", office=hosp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Trustee, Sublette County Hospital District Vote-For-3: Kenda Tanner 2,438, Tom Noble 2,362, Kelly Telfer 2,000."),
        T(person_id="WY-NOBLE-TOM", name="Tom Noble", office_group="special-districts", office=hosp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Hospital District Vote-For-3: Kenda Tanner 2,438, Tom Noble 2,362, Kelly Telfer 2,000."),
        T(person_id="WY-TELFER-KELLY", name="Kelly Telfer", office_group="special-districts", office=hosp,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Hospital District Vote-For-3: Kenda Tanner 2,438, Tom Noble 2,362, Kelly Telfer 2,000."),
    ]
    terms += [
        T(person_id="WY-LANDERS-COKE", name="Coke Landers", office_group="special-districts", office=soil,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Soil Conservation District Supervisor Vote-For-1: Coke Landers 2,874. Official 2022 heading does not print Urban/Rural/At-Large, so this term is kept on the official generic title and is not mapped onto a later labeled seat."),
        T(person_id="WY-WALKER-DARRELL", name="Darrell Walker", office_group="special-districts", office=soil,
          term_start=FM[2023], term_end=FM[2027], election_year=2022, sources=[SRC_C22],
          notes="Official 2022 Sublette clerk, Soil Conservation District Supervisor Vote-For-1: Darrell Walker 2,961. Official 2022 heading does not print Urban/Rural/At-Large."),
        T(person_id="WY-PAPE-DAVID", name="David Pape", office_group="special-districts", office=atlg,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Conservation District Supervisor At Large Vote-For-1: David Pape 4,053."),
        T(person_id="WY-SMITH-MEGHANN", name="Meghann Smith", office_group="special-districts", office=rural,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Conservation District Supervisors Rural Vote-For-2: Meghann Smith 3,253, Milford Lockwood 3,176."),
        T(person_id="WY-LOCKWOOD-MILFORD", name="Milford Lockwood", office_group="special-districts", office=rural,
          term_start=FM[2025], term_end=FM[2029], election_year=2024, sources=[SRC_C24],
          notes="Official 2024 Sublette clerk, Conservation District Supervisors Rural Vote-For-2: Meghann Smith 3,253, Milford Lockwood 3,176."),
        T(person_id="WY-STETSON-JEAN", name="Jean Stetson", office_group="special-districts", office=urban,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Supervisor, Soil Conservation Dist. Urban Vote-For-1: Jean Stetson 2,843. No official named Urban supervisor is encoded as current through January 2027 because official 2022 headings were unlabeled."),
        T(person_id="WY-LANDERS-COKE", name="Coke Landers", office_group="special-districts", office=rural,
          term_start=FM[2027], term_end=FM[2031], election_year=2026, sources=[SRC_C26],
          notes="Official 2026 Sublette clerk, Supervisor, Soil Conservation Dist. Rural Vote-For-1: Coke Landers 2,919. Official 2024 rural seats of Meghann Smith and Milford Lockwood continue through January 2029; this 2026 rural contest is encoded as a January 2027 term and is not used to invent a vacancy in the official 2024 rural class."),
    ]
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 14 (S14)", 1)],
        "state-house": [("House District 20 (H20)", 1), ("House District 22 (H22)", 1)],
        "county": [("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [("Pinedale Mayor", 1), ("Pinedale Council", 4),
                      ("Marbleton Mayor", 1), ("Marbleton Council", 4),
                      ("Big Piney Mayor", 1), ("Big Piney Council", 4)],
        "schools": [("Sublette County School District #1 Trustee", 7),
                    ("Sublette County School District #9 Trustee", 5),
                    ("Sublette County School District #9 Trustee (2-year)", 1)],
        "special-districts": [
            ("Upper Green River Cemetery District Trustee", 6),
            ("Upper Green River Cemetery District Trustee (2-year)", 1),
            ("Big Piney Cemetery District Trustee", 6),
            ("Sublette County Hospital District Trustee", 5),
            ("Conservation District Supervisor At-Large", 1),
            ("Conservation District Supervisor Rural", 2),
            ("Conservation District Supervisor Urban", 1),
            ("Soil Conservation District Supervisor", 2),
        ],
        "judicial": [
            ("District Judge, 9th Judicial District", 3),
            ("Circuit Judge, 9th Judicial District", 4),
        ],
    }


def build_sublette():
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
        "Sublette clerk retentions for Justice Hill, Justice Jarosh, and Chancery Judge Burningham are those "
        "statewide retentions. Local rows are 9th Judicial District judges (Sublette, Teton, and Fremont). Full "
        "names and appointment dates are taken from official Wyoming Judicial Branch 9th JD court pages already "
        "used in the Teton history, and official Sublette named retentions are cited (2024 Melissa M. Owens, "
        "Katharine G. McKay — official clerk spelling KATHERINE G. MCKAY — Daniel M. Stebner, and John Labuda; "
        "2026 Jason M. Conder, Weisman, and Coombs). Official 2022 Sublette clerk prints two unnamed 9th JD circuit "
        "retentions (YES 2,590 / NO 490 and YES 2,483 / NO 527); those official totals are not assigned to a named "
        "judge. Judges of other districts are not copied here."
    )
    special_note = (
        "County, municipal, school, and special-district names are keyed from official Sublette clerk general "
        "summaries (official 2022 DocumentCenter View/4109 via Wayback after the live slug was removed; official "
        "2024 View/6118; official 2026 View/8211), official Town of Pinedale council and 2026 municipal results "
        "pages, and the official Town of Marbleton council page. Official 2014–2020 clerk general canvasses were "
        "not found on the live /110/Election-Information page or on the February 8, 2023 Wayback capture of that "
        "page, so January 2015–2022 county, municipal, school, and special-district rows are largely Not yet "
        "collected rather than invented. Multi-county legislative seats use official SOS district-wide Total rows, "
        "with the official Sublette share noted, for every keyed year (2012, 2016, 2020, and 2024 S14; 2012–2026 "
        "H20; 2012–2020 H22). Official SOS two-column pages were cut at the next district header. After 2022 "
        "redistricting, official SOS H22 Sublette rows are dashes (Lincoln and Teton only); official Sublette H22 "
        "is ended at January 2023 rather than inventing a holdover. Official Lincoln slivers for Sublette County "
        "School District #9 are combined into the official whole-district result in 2022, 2024, and 2026; ranking "
        "is unchanged, including the official 2026 2-year seat where the Lincoln portion alone had Taylor Moceika "
        "ahead of Brock Forrest McLain (combined McLain 547, Moceika 319). The official Town of Big Piney site "
        "returned a Cloudflare challenge from this collection environment, and no official council roster, minutes, "
        "canvass, or Wayback capture of an official town page was retrieved, so Big Piney mayor and council stay "
        "Not yet collected. Secondary directories are not used. Official 2022 soil-conservation headings are "
        "unlabeled (Urban/Rural/At-Large are not printed), so those two official 2022 winners stay on the generic "
        "title. The official 2026 proclamation placed a question to reduce the commission from five to three; "
        "official canvass AGAINST 2,659 (72.49%), so the board remains five members. Write-in-only official contests "
        "with no named certified winner are not seated."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct "
        "roster is in data/county_officials/sublette.json, from the official 2026 Sublette primary (named winners only; "
        "8 precincts; write-in-only contests without a named certified winner are not listed)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Sublette", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Sublette", slug=SLUG)
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
    remaining_d = []
    for t in departing:
        match = next((e for e in remaining_e if e["person_id"] not in used_e and term_len(e) == term_len(t)), None)
        if match:
            paired.append((t, match))
            used_e.add(match["person_id"])
        else:
            remaining_d.append(t)
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
    # Official January elects for a vacant labeled seat (no current holder) are listed with a takes-office note.
    if not out:
        for e in elects:
            h = _holder(people, e["person_id"], e["name"], e.get("party") or "", te(e), e.get("notes") or "")
            h["notes"] = ((h.get("notes") or "") + " Takes office January 2027.").strip()
            out.append(h)
    return out


def update_sublette_json(people, terms):
    path = ROOT / "data" / "county_officials" / "sublette.json"
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

    def office_note(office):
        for t in terms:
            if t["office"] == office and t.get("notes"):
                return t["notes"]
        return ""

    senate = [
        _office("Senate District 14 (S14)",
                _holders_for_office(terms, people, "Senate District 14 (S14)"),
                note="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Sublette portion: 3,965. Also covers Lincoln, Sweetwater, and Uinta. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA."),
    ]
    house = [
        _office("House District 20 (H20)",
                _holders_for_office(terms, people, "House District 20 (H20)"),
                note="Official 2024 SOS statewide House summary totals: Mike Schmid 4,354 (official Sublette share 4,075; official Lincoln share 279). Official 2026 SOS district-wide Total: Albert Sommers 3,349 (official Sublette share 3,195; official Lincoln share 154)."),
    ]
    county = [
        _office("County Commissioner",
                _holders_for_office(terms, people, "County Commissioner"),
                note="Five-member board. Official 2026 ballot question to reduce the board from five to three failed (AGAINST 2,659, 72.49%). Official Commissioner Profiles page lists current terms. Layout is heading-then-names.",
                layout="heading-then-names"),
        _office("County Clerk", _holders_for_office(terms, people, "County Clerk"),
                note="Official County Clerk page, retrieved 2026-11-24: Jessica Rice, County Clerk. Official 2022 winner was Carrie S. Long; official mid-term appointment date was not found."),
        _office("County Treasurer", _holders_for_office(terms, people, "County Treasurer")),
        _office("County Assessor", _holders_for_office(terms, people, "County Assessor")),
        _office("County Sheriff", _holders_for_office(terms, people, "County Sheriff"),
                note="Official Sheriff page, retrieved 2026-11-24: Sheriff K.C. Lehr. Official 2026 elect is Tom Hatch, taking office January 2027."),
        _office("County Attorney", _holders_for_office(terms, people, "County Attorney")),
        _office("Clerk of District Court", _holders_for_office(terms, people, "Clerk of District Court")),
        _office("County Coroner", _holders_for_office(terms, people, "County Coroner")),
    ]
    municipal = [
        _office("Pinedale Mayor", _holders_for_office(terms, people, "Pinedale Mayor"),
                note="Official Town of Pinedale council page: Mayor Matt Murdock, term expires May 31, 2030. Official 2026 municipal results: Matt Murdock 49."),
        _office("Pinedale Council",
                _holders_for_office(terms, people, "Pinedale Council"),
                note="Official Town of Pinedale council page and official 2026 municipal results (Dean Loftus 65, Scott Kosiba 51).",
                layout="heading-then-names"),
        _office("Marbleton Mayor", _holders_for_office(terms, people, "Marbleton Mayor"),
                note="Official Town of Marbleton council page: Mayor Jim Robinson, term expires 2029. Official page states the year only (medium on May 31)."),
        _office("Marbleton Council",
                _holders_for_office(terms, people, "Marbleton Council"),
                note="Official Town of Marbleton council page: Jeff McCormick and Roger McMannis, terms expire 2027; BJ Meador and Karen Wenz, terms expire 2029. Official page states the year only (medium on May 31).",
                layout="heading-then-names"),
        _office("Big Piney Mayor", []),
        _office("Big Piney Council", [], layout="heading-then-names"),
    ]
    schools = [
        _office("Sublette County School District #1 Trustee",
                _holders_for_office(terms, people, "Sublette County School District #1 Trustee"),
                note="Official 2024 Sublette clerk Vote-For-3 and official 2026 Vote-For-4 (7-member board).",
                layout="heading-then-names"),
        _office("Sublette County School District #9 Trustee",
                _holders_for_office(terms, people, "Sublette County School District #9 Trustee"),
                note="Official Sublette totals are combined with official Lincoln slivers into official whole-district results. Official 2024 combined: Cody W. Raza 1,033, Hayden Ott 745, Jeremy Banks 658. Official 2026 4-year combined: Alan Vickrey 644, Jessica Josette Polk 489 (ranking unchanged).",
                layout="heading-then-names"),
        _office("Sublette County School District #9 Trustee (2-year)",
                _holders_for_office(terms, people, "Sublette County School District #9 Trustee (2-year)"),
                note="Official 2026 2-year combined official Sublette and official Lincoln totals: Brock Forrest McLain 547, Taylor Moceika 319. The official Lincoln portion alone had Moceika ahead (128–92); the whole-district ranking is unchanged."),
    ]
    specials = [
        _office("Upper Green River Cemetery District Trustee",
                _holders_for_office(terms, people, "Upper Green River Cemetery District Trustee"),
                layout="heading-then-names"),
        _office("Upper Green River Cemetery District Trustee (2-year)",
                _holders_for_office(terms, people, "Upper Green River Cemetery District Trustee (2-year)")),
        _office("Big Piney Cemetery District Trustee",
                _holders_for_office(terms, people, "Big Piney Cemetery District Trustee"),
                layout="heading-then-names"),
        _office("Sublette County Hospital District Trustee",
                _holders_for_office(terms, people, "Sublette County Hospital District Trustee"),
                layout="heading-then-names"),
        _office("Conservation District Supervisor At-Large",
                _holders_for_office(terms, people, "Conservation District Supervisor At-Large")),
        _office("Conservation District Supervisor Rural",
                _holders_for_office(terms, people, "Conservation District Supervisor Rural"),
                layout="heading-then-names"),
        _office("Conservation District Supervisor Urban",
                _holders_for_office(terms, people, "Conservation District Supervisor Urban"),
                note="Official 2026 elect Jean Stetson takes office January 2027. Official 2022 soil-conservation headings were unlabeled, so no official named Urban supervisor is encoded as current through January 2027."),
    ]
    judicial = [
        _office("District Judge, 9th Judicial District",
                _holders_for_office(terms, people, "District Judge, 9th Judicial District"),
                note=office_note("District Judge, 9th Judicial District"),
                layout="heading-then-names"),
        _office("Circuit Judge, 9th Judicial District",
                _holders_for_office(terms, people, "Circuit Judge, 9th Judicial District"),
                note=office_note("Circuit Judge, 9th Judicial District"),
                layout="heading-then-names"),
    ]
    groups = [
        {"id": "state-senate", "label": "Wyoming Senate", "offices": senate},
        {"id": "state-house", "label": "Wyoming House", "offices": house},
        {"id": "county", "label": "County offices", "offices": county},
        {"id": "municipal", "label": "Municipal offices", "offices": municipal},
        {"id": "schools", "label": "School boards", "offices": schools},
        {"id": "special-districts", "label": "Special districts", "offices": specials},
        {"id": "judicial", "label": "Judicial", "offices": judicial},
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
        "local_archive": "/workspace/wyoleg/local-results/sublette/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
