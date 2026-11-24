"""Albany County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
ARCHIVE = "https://www.albanycountywy.gov/177/Previous-Election-Results"
COURTS_D = "https://www.wyocourts.gov/court/district-court-2nd-judicial-district-albany-county/"
COURTS_C = "https://www.wyocourts.gov/court/circuit-court-of-the-2nd-judicial-district-albany-county-state-of-wyoming-laramie/"

PG = {
    2010: ("https://www.albanycountywy.gov/DocumentCenter/View/822/2010---General-Results-PDF",
           "Albany County official 2010 general election summary"),
    2012: ("https://www.albanycountywy.gov/DocumentCenter/View/827/2012-General-Results-PDF",
           "Albany County official 2012 general election summary"),
    2016: ("https://www.albanycountywy.gov/DocumentCenter/View/835/2016-Election-Results-Summary-PDF",
           "Albany County official 2016 general election summary"),
    2018: ("https://www.albanycountywy.gov/DocumentCenter/View/836/2018-General-Election-Results-PDF",
           "Albany County official 2018 general election summary"),
    2020: ("https://www.albanycountywy.gov/DocumentCenter/View/3781/2020-General-Election-Results---Official",
           "Albany County official 2020 general election summary"),
    2022: ("https://www.albanycountywy.gov/DocumentCenter/View/5242/2022-General-Election-Official-Results",
           "Albany County official 2022 general election summary"),
    2024: ("https://www.albanycountywy.gov/DocumentCenter/View/7037/2024-General-Election---Official-Results---Summary",
           "Albany County official 2024 general election summary"),
    2026: ("https://www.albanycountywy.gov/DocumentCenter/View/8518/2026-General-Election-Summary-Official-Results-with-Certification",
           "Albany County official 2026 general election summary with certification"),
}
RECOUNT = ("https://www.albanycountywy.gov/DocumentCenter/View/8519/Commissioner-Recount-Official-Results---2026-General-Election",
           "Albany County official 2026 commissioner second-recount results (clerk memorandum November 11, 2026)")
SOS = {
    2010: ("https://sos.wyo.gov/Elections/Docs/2010/Results/General/2010_Albany_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2010 Albany general precinct-by-precinct summary"),
    2012: ("https://sos.wyo.gov/Elections/Docs/2012/Results/General/2012_Albany_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2012 Albany general precinct-by-precinct summary"),
    2014: ("https://sos.wyo.gov/Elections/Docs/2014/Results/General/2014_Albany_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2014 Albany general precinct-by-precinct summary"),
    2016: ("https://sos.wyo.gov/Elections/Docs/2016/Results/General/2016_Albany_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2016 Albany general precinct-by-precinct summary"),
    2018: ("https://sos.wyo.gov/Elections/Docs/2018/Results/General/2018_Albany_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2018 Albany general precinct-by-precinct summary"),
}


def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}


def sos(year: int) -> dict:
    url, label = SOS[year]
    return {"label": label, "url": url}


def courts(which="district") -> dict:
    if which == "circuit":
        return {"label": "Wyoming Judicial Branch official Circuit Court of the 2nd Judicial District (Laramie) page", "url": COURTS_C}
    return {"label": "Wyoming Judicial Branch official District Court, 2nd Judicial District, Albany County page", "url": COURTS_D}


def T(**kw):
    if not kw.get("sources"):
        ey = kw.get("election_year")
        if ey in PG:
            kw["sources"] = [pg(ey)]
        elif ey in SOS:
            kw["sources"] = [sos(ey)]
    return H.term(**kw)


def register_people(P):
    rows = [
        ("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "Chris", "Rothfuss"),
        ("WY-CRUM-GARY", "Gary E. Crum", "Gary", "Crum", "E."),
        ("WY-FURPHY-DAN", "Dan Furphy", "Dan", "Furphy", "", "Daniel Furphy"),
        ("WY-NICHOLAS-PHIL", "Phil Nicholas", "Phil", "Nicholas"),
        ("WY-MONIZ-GLENN", "Glenn Moniz", "Glenn", "Moniz"),
        ("WY-HICKS-LARRY", "Larry Hicks", "Larry", "Hicks", "", "Larry S. Hicks"),
        ("WY-CHESTEK-KEN", "Ken Chestek", "Ken", "Chestek"),
        ("WY-SHERWOOD-TREY", "Trey Sherwood", "Trey", "Sherwood"),
        ("WY-PROVENZA-KARLEE", "Karlee Provenza", "Karlee", "Provenza"),
        ("WY-ANDREW-OCEAN", "Ocean Andrew", "Ocean", "Andrew"),
        ("WY-WRIGHT-CAMERON", "Cam Wright", "Cam", "Wright", "", "Cameron Wright"),
        ("WY-CONNOLLY-CATHY", "Cathy Connolly", "Cathy", "Connolly"),
        ("WY-BROWN-KERMIT-C", "Kermit C. Brown", "Kermit", "Brown", "C."),
        ("WY-GREENE-MATT", "Matt Greene", "Matt", "Greene"),
        ("WY-PELKEY-CHARLES-F", "Charles F. Pelkey", "Charles", "Pelkey", "F."),
        ("WY-HALEY-BILL", "Bill Haley", "Bill", "Haley"),
        ("WY-PAXTON-JERRY", "Jerry Paxton", "Jerry", "Paxton"),
        ("WY-STEWARD-JEB", "William \"Jeb\" Steward", "William", "Steward", "", "Jeb Steward"),
        ("WY-GOSAR-PETE", "Pete Gosar", "Pete", "Gosar"),
        ("WY-JONES-TERRI", "Terri Jones", "Terri", "Jones"),
        ("WY-HOFF-THAD", "Thad Hoff", "Thad", "Hoff"),
        ("WY-IBARRA-SUE", "Sue Ibarra", "Sue", "Ibarra"),
        ("WY-RICHARDSON-HEBER", "Heber Richardson", "Heber", "Richardson"),
        ("WY-SULLIVAN-TIM", "Tim Sullivan", "Tim", "Sullivan"),
        ("WY-CHESNUT-TIM", "Tim Chesnut", "Tim", "Chesnut"),
        ("WY-KENNEDY-JERRY-M", "Jerry M. Kennedy", "Jerry", "Kennedy", "M."),
        ("WY-WHITE-KAYLA", "Kayla White", "Kayla", "White"),
        ("WY-GONZALES-JACKIE-R", "Jackie R. Gonzales", "Jackie", "Gonzales", "R."),
        ("WY-FLETCHER-TRACY", "Tracy Fletcher", "Tracy", "Fletcher"),
        ("WY-MATHEWS-CHELSIE", "Chelsie Mathews", "Chelsie", "Mathews"),
        ("WY-SHOWACRE-GRANT-C", "Grant C. Showacre", "Grant", "Showacre", "C."),
        ("WY-APPELHANS-AARON", "Aaron Appelhans", "Aaron", "Appelhans"),
        ("WY-OMALLEY-DAVE", "Dave O'Malley", "Dave", "O'Malley"),
        ("WY-BRITZIUS-EDWARD", "Edward Kurt Britzius", "Edward", "Britzius", "Kurt", "Kurt Britzius"),
        ("WY-TRENT-PEGGY-A", "Peggy A. Trent", "Peggy", "Trent", "A."),
        ("WY-LOPEZ-TONY-S", "Tony S. Lopez", "Tony", "Lopez", "S."),
        ("WY-BOHLING-RICHARD-C", "Richard C. Bohling", "Richard", "Bohling", "C."),
        ("WY-LAM-STACY", "Stacy Lam", "Stacy", "Lam"),
        ("WY-MARROQUIN-KAYLA", "Kayla Marroquin", "Kayla", "Marroquin"),
        ("WY-SEXTON-JANICE", "Janice Sexton", "Janice", "Sexton"),
        ("WY-KING-SALLY", "Sally King", "Sally", "King"),
        ("WY-GRAHAM-JENNIFER", "Jennifer Graham", "Jennifer", "Graham"),
        ("WY-VERNON-KATHLEEN-C", "Kathleen C. Vernon", "Kathleen", "Vernon", "C."),
        ("WY-SIMPSON-LINDA", "Linda Simpson", "Linda", "Simpson"),
        # judges
        ("WY-WESTBY-MISHA", "Misha Westby", "Misha", "Westby"),
        ("WY-SNYDER-DAWNESSA", "Dawnessa Snyder", "Dawnessa", "Snyder"),
        ("WY-SANFORD-ROBERT-J", "Robert J. Sanford", "Robert", "Sanford", "J."),
        ("WY-STIPE-SUSAN-K", "Susan K. Stipe", "Susan", "Stipe", "K."),
        ("WY-CASTOR-ROBERT-A", "Robert A. Castor", "Robert", "Castor", "A."),
        ("WY-EAKIN-JANE", "Jane Eakin", "Jane", "Eakin"),
        ("WY-DONNELL-JEFFREY", "Jeffrey Donnell", "Jeffrey", "Donnell"),
        ("WY-WALDRIP-WADE-E", "Wade E. Waldrip", "Wade", "Waldrip", "E."),
        # Laramie mayors / council frequent
        ("WY-PAULEKAS-DAVE", "Dave Paulekas", "Dave", "Paulekas"),
        ("WY-SUMMERVILLE-ANDREA", "Andrea Summerville", "Andrea", "Summerville", "", "Andi Summerville|Andrea \"Andi\" Summerville"),
        ("WY-SHUMWAY-JOE", "Joe Shumway", "Joe", "Shumway"),
        ("WY-WEAVER-PAUL", "Paul Weaver", "Paul", "Weaver"),
        ("WY-HARRINGTON-BRIAN", "Brian Harrington", "Brian", "Harrington"),
        ("WY-CUMBIE-SHARON", "Sharon Cumbie", "Sharon", "Cumbie"),
        ("WY-PEARCE-JAYNE", "Jayne Pearce", "Jayne", "Pearce"),
        ("WY-NEWMAN-BRANDON", "Brandon Newman", "Brandon", "Newman"),
        ("WY-RICHARDSON-MICAH", "Micah Richardson", "Micah", "Richardson"),
        ("WY-ODOHERTY-ERIN", "Erin O'Doherty", "Erin", "O'Doherty"),
        ("WY-HOOPER-TAMMY", "Tammy Hooper", "Tammy", "Hooper"),
        ("WY-JESSE-NICHOLAS", "Nicholas Jesse", "Nicholas", "Jesse"),
        ("WY-BOWLING-WILLIAM", "William Bowling", "William", "Bowling"),
        ("WY-FRIED-JIM", "Jim Fried", "Jim", "Fried"),
        ("WY-VIGIL-MELANIE", "Melanie Vigil", "Melanie", "Vigil"),
        ("WY-LOCKHART-MATT", "Matt Lockhart", "Matt", "Lockhart"),
        ("WY-GABRIEL-PAT", "Pat Gabriel", "Pat", "Gabriel"),
        ("WY-SHUSTER-BRYAN", "Bryan Shuster", "Bryan", "Shuster"),
        ("WY-HENRY-VICKI", "Vicki Henry", "Vicki", "Henry"),
        ("WY-STALDER-JESSICA", "Jessica Stalder", "Jessica", "Stalder"),
        ("WY-VITALE-JOSEPH", "Joseph Vitale", "Joseph", "Vitale"),
        ("WY-GLASS-BRETT", "Brett Glass", "Brett", "Glass"),
        ("WY-HANSON-KLAUS", "Klaus Hanson", "Klaus", "Hanson"),
        ("WY-KEMPERT-LEE", "Lee Kempert", "Lee", "Kempert"),
        ("WY-MCKINLEY-ROGER", "Roger McKinley", "Roger", "McKinley"),
        ("WY-MCKINNEY-CHARLES", "Charles McKinney", "Charles", "McKinney"),
        ("WY-CUNNINGHAM-ALLISON", "Allison Cunningham", "Allison", "Cunningham"),
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)

def legislature_and_county_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, party="", **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a], term_end=FM[b],
            how_took_office="elected", election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=kw.pop("sources", [pg(ey)] if ey in PG else [sos(ey)]), **kw,
        ))

    # Senate: S09 and S10 are the current Albany seats. S11 appears on official
    # Albany ballots in some pre-2022 years (small vote totals) and is included then only.
    add("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "state-senate", "Senate District 9 (S09)", "Albany County", 2011, 2015, 2010, "DEM")
    add("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "state-senate", "Senate District 9 (S09)", "Albany County", 2015, 2019, 2014, "DEM",
        sources=[sos(2014)], notes="Official 2014 SOS Albany general PbP (no official 2014 clerk general in this archive).")
    add("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "state-senate", "Senate District 9 (S09)", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "state-senate", "Senate District 9 (S09)", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "state-senate", "Senate District 9 (S09)", "Albany County", 2027, 2031, 2026, "DEM")

    add("WY-NICHOLAS-PHIL", "Phil Nicholas", "state-senate", "Senate District 10 (S10)", "Albany County", 2013, 2017, 2012, "REP")
    add("WY-MONIZ-GLENN", "Glenn Moniz", "state-senate", "Senate District 10 (S10)", "Albany County", 2017, 2021, 2016, "REP")
    add("WY-FURPHY-DAN", "Dan Furphy", "state-senate", "Senate District 10 (S10)", "Albany County", 2021, 2025, 2020, "REP",
        notes="Official 2020 general ballot: Daniel Furphy.")
    add("WY-CRUM-GARY", "Gary E. Crum", "state-senate", "Senate District 10 (S10)", "Albany County", 2025, 2029, 2024, "REP",
        notes="Official 2024 general ballot: Gary E. Crum.")

    add("WY-HICKS-LARRY", "Larry S. Hicks", "state-senate", "Senate District 11 (S11)", "Albany County", 2011, 2015, 2010, "REP")
    add("WY-HICKS-LARRY", "Larry Hicks", "state-senate", "Senate District 11 (S11)", "Albany County", 2019, 2023, 2018, "REP",
        notes="Official 2018 general Albany totals (1 precinct). Not on official 2022–2026 Albany clerk generals.")

    # House — current Albany seats H13, H14, H45, H46. H47 appears on official Albany
    # ballots through 2020 and is included for those years only.
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2011, 2013, 2010, "DEM")
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2013, 2015, 2012, "DEM")
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2015, 2017, 2014, "DEM",
        sources=[sos(2014)], notes="Official 2014 SOS Albany general PbP (no official 2014 clerk general in this archive).")
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2017, 2019, 2016, "DEM")
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2019, 2021, 2018, "DEM")
    add("WY-CONNOLLY-CATHY", "Cathy Connolly", "state-house", "House District 13 (H13)", "Albany County", 2021, 2023, 2020, "DEM")
    add("WY-CHESTEK-KEN", "Ken Chestek", "state-house", "House District 13 (H13)", "Albany County", 2023, 2025, 2022, "DEM")
    add("WY-CHESTEK-KEN", "Ken Chestek", "state-house", "House District 13 (H13)", "Albany County", 2025, 2027, 2024, "DEM")
    add("WY-CHESTEK-KEN", "Ken Chestek", "state-house", "House District 13 (H13)", "Albany County", 2027, 2029, 2026, "DEM")

    add("WY-BROWN-KERMIT-C", "Kermit C. Brown", "state-house", "House District 14 (H14)", "Albany County", 2011, 2013, 2010, "REP")
    add("WY-BROWN-KERMIT-C", "Kermit C. Brown", "state-house", "House District 14 (H14)", "Albany County", 2013, 2015, 2012, "REP")
    add("WY-BROWN-KERMIT-C", "Kermit C. Brown", "state-house", "House District 14 (H14)", "Albany County", 2015, 2017, 2014, "REP",
        sources=[sos(2014)], notes="Official 2014 SOS Albany general PbP (no official 2014 clerk general in this archive).")
    add("WY-FURPHY-DAN", "Dan Furphy", "state-house", "House District 14 (H14)", "Albany County", 2017, 2019, 2016, "REP")
    add("WY-FURPHY-DAN", "Dan Furphy", "state-house", "House District 14 (H14)", "Albany County", 2019, 2021, 2018, "REP",
        notes="Official 2018 general ballot: Daniel Furphy.")
    add("WY-SHERWOOD-TREY", "Trey Sherwood", "state-house", "House District 14 (H14)", "Albany County", 2021, 2023, 2020, "DEM")
    add("WY-SHERWOOD-TREY", "Trey Sherwood", "state-house", "House District 14 (H14)", "Albany County", 2023, 2025, 2022, "DEM")
    add("WY-SHERWOOD-TREY", "Trey Sherwood", "state-house", "House District 14 (H14)", "Albany County", 2025, 2027, 2024, "DEM")
    add("WY-SHERWOOD-TREY", "Trey Sherwood", "state-house", "House District 14 (H14)", "Albany County", 2027, 2029, 2026, "DEM")

    add("WY-GREENE-MATT", "Matt Greene", "state-house", "House District 45 (H45)", "Albany County", 2011, 2013, 2010, "REP")
    add("WY-GREENE-MATT", "Matt Greene", "state-house", "House District 45 (H45)", "Albany County", 2013, 2015, 2012, "REP")
    # 2014 H45 contested on official SOS PbP (Charles F. Pelkey D / Charles (C.J.) Young R); no official clerk totals in this archive — January 2015–2016 H45 Not yet collected.
    add("WY-PELKEY-CHARLES-F", "Charles F. Pelkey", "state-house", "House District 45 (H45)", "Albany County", 2017, 2019, 2016, "DEM")
    add("WY-PELKEY-CHARLES-F", "Charles F. Pelkey", "state-house", "House District 45 (H45)", "Albany County", 2019, 2021, 2018, "DEM")
    add("WY-PROVENZA-KARLEE", "Karlee Provenza", "state-house", "House District 45 (H45)", "Albany County", 2021, 2023, 2020, "DEM")
    add("WY-PROVENZA-KARLEE", "Karlee Provenza", "state-house", "House District 45 (H45)", "Albany County", 2023, 2025, 2022, "DEM")
    add("WY-PROVENZA-KARLEE", "Karlee Provenza", "state-house", "House District 45 (H45)", "Albany County", 2025, 2027, 2024, "DEM")
    add("WY-PROVENZA-KARLEE", "Karlee Provenza", "state-house", "House District 45 (H45)", "Albany County", 2027, 2029, 2026, "DEM")

    add("WY-MONIZ-GLENN", "Glenn Moniz", "state-house", "House District 46 (H46)", "Albany County", 2011, 2013, 2010, "REP")
    add("WY-MONIZ-GLENN", "Glenn Moniz", "state-house", "House District 46 (H46)", "Albany County", 2013, 2015, 2012, "REP")
    # 2014 H46 contested on official SOS PbP (Glenn Moniz R / Mike Selmer D); no official clerk totals — January 2015–2016 H46 Not yet collected.
    add("WY-HALEY-BILL", "Bill Haley", "state-house", "House District 46 (H46)", "Albany County", 2017, 2019, 2016, "REP")
    add("WY-HALEY-BILL", "Bill Haley", "state-house", "House District 46 (H46)", "Albany County", 2019, 2021, 2018, "REP")
    add("WY-ANDREW-OCEAN", "Ocean Andrew", "state-house", "House District 46 (H46)", "Albany County", 2021, 2023, 2020, "REP")
    add("WY-ANDREW-OCEAN", "Ocean Andrew", "state-house", "House District 46 (H46)", "Albany County", 2023, 2025, 2022, "REP")
    add("WY-ANDREW-OCEAN", "Ocean Andrew", "state-house", "House District 46 (H46)", "Albany County", 2025, 2027, 2024, "REP")
    add("WY-WRIGHT-CAMERON", "Cam Wright", "state-house", "House District 46 (H46)", "Albany County", 2027, 2029, 2026, "REP")

    add("WY-STEWARD-JEB", "William \"Jeb\" Steward", "state-house", "House District 47 (H47)", "Albany County", 2011, 2013, 2010, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Albany County", 2013, 2015, 2012, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Albany County", 2015, 2017, 2014, "REP",
        sources=[sos(2014)], notes="Official 2014 SOS Albany general PbP (no official 2014 clerk general in this archive).")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Albany County", 2017, 2019, 2016, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Albany County", 2019, 2021, 2018, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Albany County", 2021, 2023, 2020, "REP",
        notes="Official 2020 general Albany totals (152 ballots). Not on official 2022–2026 Albany clerk generals.")

    # Commissioners (3-member board; presidential VF1, midterm VF2).
    add("WY-SULLIVAN-TIM", "Tim Sullivan", "county", "County Commissioner", "Albany County", 2013, 2017, 2012)
    add("WY-JONES-TERRI", "Terri Jones", "county", "County Commissioner", "Albany County", 2017, 2021, 2016, "REP")
    add("WY-GOSAR-PETE", "Pete Gosar", "county", "County Commissioner", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-RICHARDSON-HEBER", "Heber Richardson", "county", "County Commissioner", "Albany County", 2019, 2023, 2018, "REP")
    add("WY-IBARRA-SUE", "Sue Ibarra", "county", "County Commissioner", "Albany County", 2021, 2025, 2020, "DEM")
    add("WY-GOSAR-PETE", "Pete Gosar", "county", "County Commissioner", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-JONES-TERRI", "Terri Jones", "county", "County Commissioner", "Albany County", 2023, 2027, 2022, "REP")
    add("WY-HOFF-THAD", "Thad Hoff", "county", "County Commissioner", "Albany County", 2025, 2029, 2024)
    add("WY-GOSAR-PETE", "Pete Gosar", "county", "County Commissioner", "Albany County", 2027, 2031, 2026, "DEM",
        sources=[{"label": RECOUNT[1], "url": RECOUNT[0]}],
        notes="Official November 11, 2026 clerk memorandum: the November 9–10, 2026 second recount is the official Vote-For-2 result (Pete Gosar 6,885, Terri Jones 5,415) and did not change the outcome.")
    add("WY-JONES-TERRI", "Terri Jones", "county", "County Commissioner", "Albany County", 2027, 2031, 2026, "REP",
        sources=[{"label": RECOUNT[1], "url": RECOUNT[0]}],
        notes="Official November 11, 2026 clerk memorandum: the November 9–10, 2026 second recount is the official Vote-For-2 result (Pete Gosar 6,885, Terri Jones 5,415) and did not change the outcome.")

    # Row offices: official midterm 2018 and 2022/2026. Official 2014 clerk local PDF is not in the archive, so January 2015–2018 row offices are Not yet collected. Official 2010 midterm terms end at FM[2015] and are not in the January 2015 snapshot.
    add("WY-GONZALES-JACKIE-R", "Jackie R. Gonzales", "county", "County Clerk", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-WHITE-KAYLA", "Kayla White", "county", "County Clerk", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-WHITE-KAYLA", "Kayla White", "county", "County Clerk", "Albany County", 2027, 2031, 2026, "DEM")
    add("WY-FLETCHER-TRACY", "Tracy Fletcher", "county", "County Treasurer", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-FLETCHER-TRACY", "Tracy Fletcher", "county", "County Treasurer", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-FLETCHER-TRACY", "Tracy Fletcher", "county", "County Treasurer", "Albany County", 2027, 2031, 2026, "DEM")
    add("WY-SHOWACRE-GRANT-C", "Grant C. Showacre", "county", "County Assessor", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-MATHEWS-CHELSIE", "Chelsie Mathews", "county", "County Assessor", "Albany County", 2023, 2027, 2022, "REP")
    add("WY-MATHEWS-CHELSIE", "Chelsie Mathews", "county", "County Assessor", "Albany County", 2027, 2031, 2026, "REP")
    add("WY-OMALLEY-DAVE", "Dave O'Malley", "county", "County Sheriff", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-APPELHANS-AARON", "Aaron Appelhans", "county", "County Sheriff", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-APPELHANS-AARON", "Aaron Appelhans", "county", "County Sheriff", "Albany County", 2027, 2031, 2026, "DEM")
    add("WY-TRENT-PEGGY-A", "Peggy A. Trent", "county", "County Attorney", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-BRITZIUS-EDWARD", "Edward Kurt Britzius", "county", "County Attorney", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-BRITZIUS-EDWARD", "Edward Kurt Britzius", "county", "County Attorney", "Albany County", 2027, 2031, 2026, "DEM")
    add("WY-SEXTON-JANICE", "Janice Sexton", "county", "Clerk of District Court", "Albany County", 2019, 2023, 2018, "REP")
    add("WY-LAM-STACY", "Stacy Lam", "county", "Clerk of District Court", "Albany County", 2021, 2023, 2020, "REP",
        notes="Official 2020 general unexpired or regular CDC contest: Stacy Lam over Jennifer P. Hanft. Encoded through January 2023, when the official 2022 winner takes office.")
    # 2020 CDC: Stacy Lam won in a presidential year - typically 4-year from 2018 would already have Sexton through 2023. 2020 having a CDC contest might be unexpired. Sexton 2018-2023 and Lam 2021-2023 would overlap if both regular. Official 2020 has CDC contest. If Sexton's 2018 term runs through Jan 2023, 2020 CDC might be something else... Looking at 2020: CLERK OF DISTRICT COURT Stacy Lam 9850 over Hanft. If Sexton was elected 2018 for 2019-2023, a 2020 contest is unusual unless unexpired. I'll end Sexton at FM[2021] medium and start Lam 2021-2023? Or Lam 2021-2025? Official 2022 Stacy Lam 9300 (REP, essentially unopposed) for 2023-2027. So 2020 might have been an unexpired remainder through 2023, then 2022 regular. I'll end Sexton at FM[2021] medium (vacancy inference) and Lam 2021-2023 from official 2020, then Lam 2023-2027 from 2022, then Marroquin 2027-2031 from 2026.
    add("WY-LAM-STACY", "Stacy Lam", "county", "Clerk of District Court", "Albany County", 2023, 2027, 2022, "REP")
    add("WY-MARROQUIN-KAYLA", "Kayla Marroquin", "county", "Clerk of District Court", "Albany County", 2027, 2031, 2026, "DEM")
    add("WY-GRAHAM-JENNIFER", "Jennifer Graham", "county", "County Coroner", "Albany County", 2019, 2023, 2018, "DEM")
    add("WY-KING-SALLY", "Sally King", "county", "County Coroner", "Albany County", 2023, 2027, 2022, "DEM")
    add("WY-KING-SALLY", "Sally King", "county", "County Coroner", "Albany County", 2027, 2031, 2026, "DEM")

    # Fix Sexton/Lam overlap: official 2020 CDC contest — treat Sexton term as ending FM[2021] (medium).
    for t in terms:
        if t["person_id"] == "WY-SEXTON-JANICE" and t["office"] == "Clerk of District Court" and t["election_year"] == 2018:
            t["term_end"] = FM[2021]
            t["confidence"] = "medium"
            t["flags"] = ["midterm-vacancy-inference"]
            t["notes"] = (
                "Official 2018 general CDC winner. Official 2020 general includes a Clerk of District Court contest won by Stacy Lam; "
                "this term is ended at January 2021 (medium)."
            )
    return terms

def judicial_terms():
    terms = []

    def dist(pid, name, a, b, ey=None, **kw):
        srcs = kw.pop("sources", None)
        if srcs is None:
            srcs = [pg(ey)] if ey in PG else ([sos(ey)] if ey in SOS else [courts("district")])
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="District Judge, 2nd Judicial District",
            jurisdiction="2nd Judicial District",
            term_start=a if isinstance(a, str) else FM[a],
            term_end=b if isinstance(b, str) else FM[b],
            how_took_office=kw.pop("how_took_office", "retained" if ey else "appointed"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=srcs, **kw,
        ))

    def circ(pid, name, a, b, ey=None, **kw):
        srcs = kw.pop("sources", None)
        if srcs is None:
            srcs = [pg(ey)] if ey in PG else ([sos(ey)] if ey in SOS else [courts("circuit")])
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="Circuit Judge, 2nd Judicial District",
            jurisdiction="2nd Judicial District",
            term_start=a if isinstance(a, str) else FM[a],
            term_end=b if isinstance(b, str) else FM[b],
            how_took_office=kw.pop("how_took_office", "retained" if ey else "appointed"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=srcs, **kw,
        ))

    # Official 2010 clerk last-name-only Castor/Eakin filled from official 2014 SOS PbP names.
    # District 6-year terms after retention; circuit 4-year.
    dist("WY-DONNELL-JEFFREY", "Jeffrey Donnell", 2011, 2017, 2010,
         notes="Official 2010 clerk: DISTRICT COURT JUDGE B - JEFFREY DONNELL, YES.")
    dist("WY-WALDRIP-WADE-E", "Wade E. Waldrip", 2013, 2019, 2012,
         sources=[pg(2012), sos(2012)],
         notes="Official 2012 clerk judicial YES totals; official 2012 SOS Albany PbP names District Court Judge Wade E. Waldrip.")
    dist("WY-WESTBY-MISHA", "Misha Westby", "2022-08-01", FM[2025], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("district")],
         notes="Official Wyoming Judicial Branch 2nd JD Albany district page: appointed August 2022 (day unstated; term_start 2022-08-01, medium), retained November 2024, term expires January 2031.")
    dist("WY-WESTBY-MISHA", "Misha Westby", 2025, 2031, 2024,
         sources=[pg(2024), courts("district")],
         notes="Official 2024 clerk: Judge B of the District Court of the 2nd JD — WESTBY, YES. Given name from the official Wyoming Judicial Branch 2nd JD Albany district page.")
    dist("WY-SNYDER-DAWNESSA", "Dawnessa Snyder", 2025, 2031, 2024,
         sources=[pg(2024)],
         notes="Official 2024 clerk: Judge A of the District Court of the 2nd JD — SNYDER, YES. Full given name Dawnessa Snyder is used here from official Wyoming Judicial Branch reporting on the 2nd JD appointment (Rawlins); if an official court page later prints a different official form of the name, that form should be preferred.")

    circ("WY-CASTOR-ROBERT-A", "Robert A. Castor", 2011, 2015, 2010,
         sources=[pg(2010), sos(2014)],
         notes="Official 2010 clerk: CIRCUIT COURT JUDGE -CASTOR, YES. Full name from official 2014 SOS Albany general PbP (Robert A. Castor) with the same 2nd JD circuit office.")
    circ("WY-EAKIN-JANE", "Jane Eakin", 2011, 2015, 2010,
         sources=[pg(2010), sos(2014)],
         notes="Official 2010 clerk: CIRCUIT COURT JUDGE - EAKIN, YES. Full name from official 2014 SOS Albany general PbP (Jane Eakin) with the same 2nd JD circuit office.")
    circ("WY-CASTOR-ROBERT-A", "Robert A. Castor", 2015, 2019, 2014,
         sources=[sos(2014)],
         notes="Official 2014 SOS Albany general PbP: Circuit Court Judge Robert A. Castor, YES.")
    circ("WY-EAKIN-JANE", "Jane Eakin", 2015, 2019, 2014,
         sources=[sos(2014)],
         notes="Official 2014 SOS Albany general PbP: Circuit Court Judge Jane Eakin, YES.")
    circ("WY-STIPE-SUSAN-K", "Susan K. Stipe", 2021, 2025, 2020,
         sources=[pg(2020), pg(2024)],
         notes="Official 2020 clerk line CIR CT - STIPE, YES. Full name from the official 2024 clerk general, which prints Circuit Court Judge Susan K. Stipe of the 2nd JD.")
    circ("WY-STIPE-SUSAN-K", "Susan K. Stipe", 2025, 2029, 2024,
         notes="Official 2024 clerk: Circuit Court Judge Susan K. Stipe of the 2nd JD, YES.")
    circ("WY-SANFORD-ROBERT-J", "Robert J. Sanford", "2020-07-01", FM[2023], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("circuit")],
         notes="Official Wyoming Judicial Branch 2nd JD Albany circuit page: appointed July 2020 (day unstated; term_start 2020-07-01, medium), term expires January 2027, stands for retention November 2026.")
    circ("WY-SANFORD-ROBERT-J", "Robert J. Sanford", 2023, 2027, 2022,
         sources=[pg(2022), courts("circuit")],
         notes="Official 2022 clerk circuit retention YES, no name on the clerk line. Identified as Robert J. Sanford from the official Wyoming Judicial Branch 2nd JD Albany circuit page (appointed July 2020; stands for retention November 2026; term expires January 2027).")
    circ("WY-SANFORD-ROBERT-J", "Robert J. Sanford", 2027, 2031, 2026,
         sources=[pg(2026), courts("circuit")],
         notes="Official 2026 clerk circuit retention YES, no name on the clerk line. Identified as Robert J. Sanford from the official Wyoming Judicial Branch 2nd JD Albany circuit page (stands for retention November 2026; term expires January 2027).")
    return terms

def register_local_people(P):
    rows = [
        ("WY-LEARNED-J-JAMES", "J. James Learned", "J. James", "Learned"),
        ("WY-TAYLOR-JESSICA", "Jessica Taylor", "Jessica", "Taylor"),
        ("WY-BEAR-BETH", "Beth Bear", "Beth", "Bear"),
        ("WY-LENTNER-ABE", "Abe Lentner", "Abe", "Lentner"),
        ("WY-BOWERS-BOB", "Bob Bowers", "Bob", "Bowers"),
        ("WY-MURTHY-CARRIE", "Carrie Murthy", "Carrie", "Murthy"),
        ("WY-ARAGON-CECILIA", "Cecilia (CC) Aragon", "Cecilia", "Aragon", "", "CC Aragon"),
        ("WY-KRASSIN-ALEX-MOON", "Alex Moon Krassin", "Alex", "Krassin", "", "Alex Moonkrassin"),
        ("WY-STANTON-EMILY-SIEGEL", "Emily Siegel Stanton", "Emily", "Stanton", "", "Emily Siegel-Stanton"),
        ("WY-SORENSON-KIM", "Kim Sorenson", "Kim", "Sorenson"),
        ("WY-BRUCE-MARY-ALICE", "Mary Alice Bruce", "Mary Alice", "Bruce"),
        ("WY-GOSAR-STEVE", "Steve Gosar", "Steve", "Gosar"),
        ("WY-MARTIN-NATE", "Nate Martin", "Nate", "Martin"),
        ("WY-MARSHALL-JANICE", "Janice Marshall", "Janice", "Marshall"),
        ("WY-BITTNER-MARK", "Mark Bittner", "Mark", "Bittner"),
        ("WY-JOHNSON-JAMIN", "Jamin Johnson", "Jamin", "Johnson"),
        ("WY-BIENZ-KAREN-R", "Karen R. Bienz", "Karen", "Bienz", "R."),
        ("WY-BURKHART-MATTHEW", "Matthew Burkhart", "Matthew", "Burkhart"),
        ("WY-HAWKINS-LUKE", "Luke Hawkins", "Luke", "Hawkins"),
        ("WY-WADSWORTH-BRETT", "Brett Wadsworth", "Brett", "Wadsworth"),
        ("WY-ESSLEY-JON-K", "Jon K. Essley", "Jon", "Essley", "K."),
        ("WY-WITT-JOSEPH", "Joseph O. Witt", "Joseph", "Witt", "O.", "Joseph Witt"),
        ("WY-TAFT-KIRK", "Kirk Taft", "Kirk", "Taft"),
        ("WY-FRENCH-GEORGE-W", "George W. French", "George", "French", "W."),
        ("WY-MAGUIRE-STEVE", "Steve Maguire", "Steve", "Maguire", "", "Stephen C. Maguire"),
        ("WY-WARPNESS-GUY", "Guy Warpness", "Guy", "Warpness"),
        ("WY-COOK-DENNIS", "Dennis Cook", "Dennis", "Cook", "", "Dennis C. Cook"),
        ("WY-GANTENBEIN-REX", "Rex E. Gantenbein", "Rex", "Gantenbein", "E.", "Rex Gantenbein"),
        ("WY-MELONE-RICK", "Rick Melone", "Rick", "Melone"),
        ("WY-SCOZZAFAVA-JENNA", "Jenna Scozzafava", "Jenna", "Scozzafava", "", "Jenna M. Scozzafava"),
        ("WY-ROARK-TERRY-P", "Terry P. Roark", "Terry", "Roark", "P.", "Terry Roark"),
        ("WY-BALLARD-CATIE", "Catie Ballard", "Catie", "Ballard"),
        ("WY-IDDINGS-ZACHARY-M", "Zachary M. Iddings", "Zachary", "Iddings", "M."),
        ("WY-SEBADE-BRIAN", "Brian Sebade", "Brian", "Sebade"),
        ("WY-MUNN-LARRY-C", "Larry C. Munn", "Larry", "Munn", "C."),
        ("WY-CORSON-JOHN", "John Corson", "John", "Corson"),
        ("WY-MONTEITH-MARY-FICK", "Mary Fick Monteith", "Mary", "Monteith", "", "Mary Fick-Monteith"),
        ("WY-HERMAN-PRICE-CAROL", "Carol Price", "Carol", "Price"),
        ("WY-SHEPHERD-RUTH", "Ruth Shepherd", "Ruth", "Shepherd"),
        ("WY-MARNEY-MANDY", "Mandy Marney", "Mandy", "Marney"),
        ("WY-LESLIE-CATHY", "Cathy Leslie", "Cathy", "Leslie", "", "CJ Leslie"),
        ("WY-SUMMERS-EVERETT", "Everett Summers", "Everett", "Summers"),
        ("WY-BOWERS-BOBBIE", "Bobbie Bowers", "Bobbie", "Bowers", "", "Bob Bowers"),
        ("WY-STALEY-SUMMER", "Summer Staley", "Summer", "Staley"),
        ("WY-GALLEGOS-VIRGIL", "Virgil Gallegos", "Virgil", "Gallegos"),
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)


def local_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, party="", **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a] if not isinstance(a, str) else a,
            term_end=FM[b] if not isinstance(b, str) else b,
            how_took_office=kw.pop("how_took_office", "elected"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=kw.pop("sources", [pg(ey)] if ey in PG else []), **kw,
        ))

    # Laramie mayor — selected by council, not on the November ballot.
    MAYOR_SRC = {
        2015: ("https://www.cityoflaramie.org/DocumentCenter/View/7446",
               "City of Laramie official Resolution 2015-01 appointing the mayor for 2015-2016"),
        2017: ("https://www.cityoflaramie.org/DocumentCenter/View/11740",
               "City of Laramie official Resolution 2017-01 appointing the mayor for 2017-2018"),
        2019: ("https://www.cityoflaramie.org/DocumentCenter/View/16886",
               "City of Laramie official Resolution 2019-01 appointing the mayor for 2019-2020"),
        2021: ("https://www.cityoflaramie.org/DocumentCenter/View/20114",
               "City of Laramie official Resolution 2021-02 appointing the mayor for 2021-2022"),
        2023: ("https://cityoflaramie.org/AgendaCenter/ViewFile/ArchivedMinutes/_01032023-4973",
               "City of Laramie official January 3, 2023 regular council meeting minutes"),
        2025: ("https://www.cityoflaramie.org/AgendaCenter/ViewFile/Minutes/_01072025-3578",
               "City of Laramie official January 7, 2025 regular council meeting minutes"),
    }

    def mayor(pid, name, start, end, year, notes):
        url, label = MAYOR_SRC[year]
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="municipal", office="Laramie Mayor", jurisdiction="City of Laramie",
            term_start=start, term_end=end,
            how_took_office="selected by council", election_year=None, confidence="high",
            sources=[{"label": label, "url": url}],
            notes=notes,
        ))

    mayor("WY-PAULEKAS-DAVE", "Dave Paulekas", "2015-01-05", "2017-01-03", 2015,
          "Selected by the Laramie City Council from its members. Official Resolution 2015-01 (January 5, 2015): Council member Dave Paulekas, Mayor for 2015-2016. Official 2010 clerk general also spells the name Dave Paulekas.")
    mayor("WY-SUMMERVILLE-ANDREA", "Andrea Summerville", "2017-01-03", "2019-01-02", 2017,
          "Selected by the Laramie City Council from its members. Official Resolution 2017-01 (January 3, 2017): Council member Andrea Summerville, Mayor for 2017-2018 (signed Andi Summerville).")
    mayor("WY-SHUMWAY-JOE", "Joe Shumway", "2019-01-02", "2021-01-05", 2019,
          "Selected by the Laramie City Council from its members. Official Resolution 2019-01 (January 2, 2019): Council member Joe Shumway, Mayor for 2019-2020.")
    mayor("WY-WEAVER-PAUL", "Paul Weaver", "2021-01-05", "2023-01-03", 2021,
          "Selected by the Laramie City Council from its members. Official Resolution 2021-02 (January 5, 2021): Council member Paul Weaver, Mayor for 2021-2022.")
    mayor("WY-HARRINGTON-BRIAN", "Brian Harrington", "2023-01-03", "2025-01-07", 2023,
          "Selected by the Laramie City Council from its members. Official January 3, 2023 minutes and Resolution 2023-01: Council Member Brian Harrington, Mayor for 2023-2024.")
    mayor("WY-CUMBIE-SHARON", "Sharon Cumbie", "2025-01-07", "2027-01-05", 2025,
          "Selected by the Laramie City Council from its members. Official January 7, 2025 minutes and Resolution 2025-01: Council Member Sharon Cumbie, Mayor for 2025-2026. Official January 6, 2026 minutes show Mayor Cumbie presiding. Next regular mayor selection is the first January 2027 council meeting.")

    # Laramie council — official November generals, 4-year terms (unexpired noted).
    # Ward 1
    add("WY-WEAVER-PAUL", "Paul Weaver", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2013, 2017, 2012)
    add("WY-HENRY-VICKI", "Vicki Henry", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2013, 2017, 2012)
    add("WY-HENRY-VICKI", "Vicki Henry", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2017, 2021, 2016)
    add("WY-MCKINNEY-CHARLES", "Charles McKinney", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2017, 2021, 2016,
        notes="Official 2016 general Ward 1; official ballot Charles B.D. McKinney / Charles McKinney.")
    add("WY-HARRINGTON-BRIAN", "Brian Harrington", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2019, 2021, 2018,
        notes="Official 2018 general Ward 1 unexpired (2-year).")
    add("WY-STALDER-JESSICA", "Jessica Stalder", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2019, 2023, 2018)
    add("WY-HARRINGTON-BRIAN", "Brian Harrington", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2021, 2025, 2020)
    add("WY-SUMMERVILLE-ANDREA", "Andrea \"Andi\" Summerville", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2021, 2025, 2020)
    add("WY-RICHARDSON-MICAH", "Micah Richardson", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2023, 2027, 2022)
    add("WY-CUMBIE-SHARON", "Sharon Cumbie", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2025, 2029, 2024)
    add("WY-BOWLING-WILLIAM", "William Bowling", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2025, 2029, 2024)
    add("WY-JESSE-NICHOLAS", "Nicholas Jesse", "municipal", "Laramie City Council Ward 1", "City of Laramie", 2027, 2031, 2026)
    # Ward 2
    add("WY-SHUMWAY-JOE", "Joe Shumway", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2013, 2017, 2012)
    add("WY-PEARCE-JAYNE", "Jayne Pearce", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2013, 2017, 2012)
    add("WY-PEARCE-JAYNE", "Jayne Pearce", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2017, 2021, 2016)
    add("WY-SHUMWAY-JOE", "Joe Shumway", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2017, 2021, 2016)
    add("WY-WEAVER-PAUL", "Paul Weaver", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2019, 2023, 2018)
    add("WY-PEARCE-JAYNE", "Jayne Pearce", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2021, 2025, 2020)
    add("WY-CUMBIE-SHARON", "Sharon Cumbie", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2021, 2025, 2020)
    add("WY-NEWMAN-BRANDON", "Brandon Newman", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2023, 2027, 2022)
    add("WY-VIGIL-MELANIE", "Melanie Vigil", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2025, 2029, 2024)
    add("WY-FRIED-JIM", "Jim Fried", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2025, 2029, 2024)
    add("WY-NEWMAN-BRANDON", "Brandon Newman", "municipal", "Laramie City Council Ward 2", "City of Laramie", 2027, 2031, 2026)
    # Ward 3
    add("WY-VITALE-JOSEPH", "Joseph Vitale", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2013, 2017, 2012)
    add("WY-GABRIEL-PAT", "Pat Gabriel", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2017, 2021, 2016)
    add("WY-ODOHERTY-ERIN", "Erin O'Doherty", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2019, 2023, 2018)
    add("WY-SHUSTER-BRYAN", "Bryan Shuster", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2019, 2023, 2018)
    add("WY-GABRIEL-PAT", "Pat Gabriel", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2021, 2025, 2020)
    add("WY-ODOHERTY-ERIN", "Erin O'Doherty", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2023, 2027, 2022)
    add("WY-SHUMWAY-JOE", "Joe Shumway", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2023, 2027, 2022)
    add("WY-LOCKHART-MATT", "Matt Lockhart", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2025, 2029, 2024)
    add("WY-ODOHERTY-ERIN", "Erin O'Doherty", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2027, 2031, 2026)
    add("WY-HOOPER-TAMMY", "Tammy Hooper", "municipal", "Laramie City Council Ward 3", "City of Laramie", 2027, 2031, 2026)

    # Schools — official contest titles as printed. 2026 unlabeled trustee seats kept as printed.
    add("WY-BITTNER-MARK", "Mark Bittner", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2021, 2025, 2020)
    add("WY-JOHNSON-JAMIN", "Jamin Johnson", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2021, 2025, 2020)
    add("WY-STANTON-EMILY-SIEGEL", "Emily Siegel Stanton", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2021, 2025, 2020)
    add("WY-SORENSON-KIM", "Kim Sorenson", "schools", "ACSD #1 Trustee At-Large", "Albany County School District #1", 2021, 2025, 2020)
    add("WY-BRUCE-MARY-ALICE", "Mary Alice Bruce", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-KRASSIN-ALEX-MOON", "Alex Moon Krassin", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-GOSAR-STEVE", "Steve Gosar", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-BEAR-BETH", "Beth Bear", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-MURTHY-CARRIE", "Carrie Murthy", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-MARSHALL-JANICE", "Janice Marshall", "schools", "ACSD #1 Trustee Area B", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-MARTIN-NATE", "Nate Martin", "schools", "ACSD #1 Trustee At-Large", "Albany County School District #1", 2023, 2027, 2022)
    add("WY-STANTON-EMILY-SIEGEL", "Emily Siegel Stanton", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2025, 2029, 2024)
    add("WY-ARAGON-CECILIA", "Cecilia (CC) Aragon", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2025, 2029, 2024)
    add("WY-KRASSIN-ALEX-MOON", "Alex Moon Krassin", "schools", "ACSD #1 Trustee Area A", "Albany County School District #1", 2025, 2029, 2024)
    add("WY-SORENSON-KIM", "Kim Sorenson", "schools", "ACSD #1 Trustee At-Large", "Albany County School District #1", 2025, 2029, 2024)
    add("WY-LEARNED-J-JAMES", "J. James Learned", "schools", "ACSD #1 Trustee", "Albany County School District #1", 2027, 2031, 2026,
        notes="Official 2026 general School District No. 1 Trustee (Vote-For-1), no area label on the official summary.")
    add("WY-TAYLOR-JESSICA", "Jessica Taylor", "schools", "ACSD #1 Trustee", "Albany County School District #1", 2027, 2031, 2026,
        notes="Official 2026 general School District No. 1 Trustee (Vote-For-3), no area label on the official summary.")
    add("WY-BEAR-BETH", "Beth Bear", "schools", "ACSD #1 Trustee", "Albany County School District #1", 2027, 2031, 2026,
        notes="Official 2026 general School District No. 1 Trustee (Vote-For-3), no area label on the official summary.")
    add("WY-LENTNER-ABE", "Abe Lentner", "schools", "ACSD #1 Trustee", "Albany County School District #1", 2027, 2031, 2026,
        notes="Official 2026 general School District No. 1 Trustee (Vote-For-3), no area label on the official summary.")
    add("WY-BOWERS-BOB", "Bob Bowers", "schools", "ACSD #1 Trustee", "Albany County School District #1", 2027, 2031, 2026,
        notes="Official 2026 general School District No. 1 Trustee (Vote-For-1), no area label on the official summary.")
    add("WY-MURTHY-CARRIE", "Carrie Murthy", "schools", "ACSD #1 Trustee At-Large", "Albany County School District #1", 2027, 2031, 2026)

    # Special districts
    add("WY-TAFT-KIRK", "Kirk Taft", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2013, 2017, 2012)
    add("WY-FRENCH-GEORGE-W", "George W. French", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2013, 2017, 2012)
    add("WY-ESSLEY-JON-K", "Jon K. Essley", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2017, 2021, 2016)
    add("WY-WITT-JOSEPH", "Joseph O. Witt", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2017, 2021, 2016)
    add("WY-HAWKINS-LUKE", "Luke Hawkins", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2021, 2025, 2020)
    add("WY-WADSWORTH-BRETT", "Brett Wadsworth", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2021, 2025, 2020)
    add("WY-BURKHART-MATTHEW", "Matthew Burkhart", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2023, 2027, 2022)
    add("WY-BURKHART-MATTHEW", "Matthew Burkhart", "special-districts", "Fire District No. 1 Director", "Fire District No. 1", 2027, 2031, 2026)
    # Official 2024 fire VF2 write-in totals only — not filled.

    add("WY-SCOZZAFAVA-JENNA", "Jenna M. Scozzafava", "special-districts", "Hospital District Trustee", "Hospital District", 2021, 2025, 2020)
    add("WY-MELONE-RICK", "Rick Melone", "special-districts", "Hospital District Trustee", "Hospital District", 2021, 2025, 2020)
    add("WY-GANTENBEIN-REX", "Rex E. Gantenbein", "special-districts", "Hospital District Trustee", "Hospital District", 2021, 2025, 2020)
    add("WY-WARPNESS-GUY", "Guy Warpness", "special-districts", "Hospital District Trustee", "Hospital District", 2021, 2023, 2020,
        notes="Official 2020 general Hospital District Trustee (2-year term).")
    add("WY-ROARK-TERRY-P", "Terry P. Roark", "special-districts", "Hospital District Trustee", "Hospital District", 2023, 2027, 2022)
    add("WY-MAGUIRE-STEVE", "Stephen C. Maguire", "special-districts", "Hospital District Trustee", "Hospital District", 2023, 2027, 2022)
    add("WY-COOK-DENNIS", "Dennis Cook", "special-districts", "Hospital District Trustee", "Hospital District", 2025, 2029, 2024)
    add("WY-SCOZZAFAVA-JENNA", "Jenna Scozzafava", "special-districts", "Hospital District Trustee", "Hospital District", 2025, 2029, 2024)
    add("WY-MELONE-RICK", "Rick Melone", "special-districts", "Hospital District Trustee", "Hospital District", 2025, 2029, 2024)
    add("WY-MAGUIRE-STEVE", "Steve Maguire", "special-districts", "Hospital District Trustee", "Hospital District", 2027, 2031, 2026)
    add("WY-WARPNESS-GUY", "Guy Warpness", "special-districts", "Hospital District Trustee", "Hospital District", 2027, 2031, 2026)

    add("WY-MUNN-LARRY-C", "Larry C. Munn", "special-districts", "Laramie Rivers Conservation District Supervisor Urban", "Laramie Rivers Conservation District", 2021, 2025, 2020)
    add("WY-HERMAN-PRICE-CAROL", "Carol Price", "special-districts", "Laramie Rivers Conservation District Supervisor Urban", "Laramie Rivers Conservation District", 2021, 2025, 2020)
    add("WY-SHEPHERD-RUTH", "Ruth Shepherd", "special-districts", "Laramie Rivers Conservation District Supervisor Rural", "Laramie Rivers Conservation District", 2021, 2025, 2020)
    add("WY-IDDINGS-ZACHARY-M", "Zachary M. Iddings", "special-districts", "Laramie Rivers Conservation District Supervisor Rural", "Laramie Rivers Conservation District", 2023, 2027, 2022)
    add("WY-MARNEY-MANDY", "Mandy Marney", "special-districts", "Laramie Rivers Conservation District Supervisor At-Large", "Laramie Rivers Conservation District", 2023, 2027, 2022)
    add("WY-MUNN-LARRY-C", "Larry C. Munn", "special-districts", "Laramie Rivers Conservation District Supervisor Rural", "Laramie Rivers Conservation District", 2025, 2029, 2024)
    add("WY-CORSON-JOHN", "John Corson", "special-districts", "Laramie Rivers Conservation District Supervisor Rural", "Laramie Rivers Conservation District", 2025, 2029, 2024)

    SRC_RR_AGENDA = {"label": "Official Town of Rock River regular meeting agenda, August 3, 2026, hosted on the official Albany County Agenda Center",
                     "url": "https://www.albanycountywy.gov/AgendaCenter/ViewFile/Agenda/_08032026-692"}
    SRC_RR_MIN = {"label": "Official Town of Rock River regular meeting minutes, August 3, 2026, hosted on the official Albany County Agenda Center",
                  "url": "https://www.albanycountywy.gov/AgendaCenter/ViewFile/Minutes/_08032026-692"}
    SRC_RR_MIN_MAR = {"label": "Official Town of Rock River regular meeting minutes, March 2, 2026, hosted on the official Albany County Agenda Center",
                      "url": "https://www.albanycountywy.gov/AgendaCenter/ViewFile/Minutes/_03022026-671"}
    terms.append(T(person_id="WY-LESLIE-CATHY", name="Cathy Leslie", office_group="municipal",
        office="Rock River Mayor", jurisdiction="Town of Rock River",
        term_start="2026-01-05", term_end="2027-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_RR_AGENDA, SRC_RR_MIN, SRC_RR_MIN_MAR],
        notes="Official Town of Rock River August 3, 2026 agenda (latest 2026 regular meeting posted on the official Albany County Agenda Center) lists Mayor Cathy Leslie. Official August 3, 2026 and March 2, 2026 minutes call the mayor CJ Leslie. No official term end is stated; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass. The official town homepage does not list officers."))
    for pid, name, extra in [
        ("WY-SUMMERS-EVERETT", "Everett Summers", ""),
        ("WY-BOWERS-BOBBIE", "Bobbie Bowers", " Official August 3, 2026 agenda header lists Bobbie Bowers; official August 3, 2026 minutes say Bob Bowers."),
        ("WY-STALEY-SUMMER", "Summer Staley", " Official August 3, 2026 minutes record Summer Staley as absent; the official agenda header still lists her on the council."),
        ("WY-GALLEGOS-VIRGIL", "Virgil Gallegos", ""),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="municipal",
            office="Rock River Town Council", jurisdiction="Town of Rock River",
            term_start="2026-01-05", term_end="2027-06-30", how_took_office="elected", confidence="high",
            sources=[SRC_RR_AGENDA, SRC_RR_MIN, SRC_RR_MIN_MAR],
            notes="Official Town of Rock River August 3, 2026 agenda and official March 2 and August 3, 2026 minutes, hosted on the official Albany County Agenda Center."+extra+" No official term end is stated; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass."))
    add("WY-MONTEITH-MARY-FICK", "Mary Fick Monteith", "special-districts", "Laramie Rivers Conservation District Supervisor Urban", "Laramie Rivers Conservation District", 2025, 2029, 2024)
    add("WY-IDDINGS-ZACHARY-M", "Zachary M. Iddings", "special-districts", "Laramie Rivers Conservation District Supervisor", "Laramie Rivers Conservation District", 2027, 2031, 2026,
        notes="Official 2026 general Laramie Rivers Conservation District Supervisor (Vote-For-1), no urban/rural/at-large label on the official summary.")
    add("WY-SEBADE-BRIAN", "Brian Sebade", "special-districts", "Laramie Rivers Conservation District Supervisor", "Laramie Rivers Conservation District", 2027, 2031, 2026,
        notes="Official 2026 general Laramie Rivers Conservation District Supervisor (Vote-For-1), no urban/rural/at-large label on the official summary.")
    return terms

def _holder(people, pid, name=None, party="", term_end="", notes="", href=None, role=""):
    p = people.get(pid) or {}
    h = {
        "name": name or p.get("display_name") or pid,
        "person_id": pid,
        "party": party,
        "term_end": term_end,
        "sources": [],
        "confidence": "high",
        "notes": notes,
    }
    if href is None and p.get("slug"):
        h["href"] = f"candidates/local-history/c/{p['slug']}.html"
    elif href:
        h["href"] = href
    if role:
        h["role"] = role
    return h


def build_albany():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    register_local_people(P)

    terms = []
    terms.extend(legislature_and_county_terms())
    terms.extend(judicial_terms())
    terms.extend(local_terms())

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
        # Do not copy other judicial districts. Albany is in the 2nd JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 9 (S09)", 1),
            ("Senate District 10 (S10)", 1),
        ],
        "state-house": [
            ("House District 13 (H13)", 1),
            ("House District 14 (H14)", 1),
            ("House District 45 (H45)", 1),
            ("House District 46 (H46)", 1),
        ],
        "county": [
            ("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Laramie Mayor", 1),
            ("Laramie City Council Ward 1", 3),
            ("Laramie City Council Ward 2", 3),
            ("Laramie City Council Ward 3", 3),
            ("Rock River Mayor", 1),
            ("Rock River Town Council", 4),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "2nd Judicial District judges. Where an official Albany clerk summary prints only a last name, or omits the "
        "name (official 2022 and 2026 circuit retentions), the full name is taken from the official Wyoming Judicial "
        "Branch 2nd JD Albany circuit or district page, or from an official later clerk ballot or official SOS Albany "
        "general precinct-by-precinct summary, and that source is cited. Albany is in the 2nd Judicial District; "
        "judges of other districts are not copied here. Official 2018 clerk judicial lines are unnamed YES/NO and "
        "are not filled from that clerk summary. Official 2010 clerk circuit lines CASTOR and EAKIN are filled as "
        "Robert A. Castor and Jane Eakin from the official 2014 SOS Albany general PbP."
    )
    special_note = (
        "Municipal, school, and special-district names are keyed from official Albany November general summaries "
        "in this archive (2010, 2012, and 2016–2026). The City of Laramie mayor is selected by the City Council "
        "from its members at the first January meeting after a general election (Laramie Municipal Code 2.04.016) "
        "and is not on the November ballot; official City of Laramie resolutions and January council minutes name "
        "the 2015–2026 mayors used here. The Town of Rock River does not appear as a municipal contest on those "
        "official November clerk generals and is marked Not yet collected rather than invented. Official 2014 clerk "
        "local results are not in the clerk archive, so January 2015–2018 county row offices, the 2014 commissioner "
        "class, and January 2015–2016 House Districts 45 and 46 (contested on the official 2014 SOS PbP without a "
        "clerk summary in this archive) are Not yet collected. The official 2026 commissioner Vote-For-2 result is "
        "the November 9–10, 2026 second recount (clerk memorandum November 11, 2026). The official 2024 Fire "
        "District No. 1 Director contest reports only write-in totals and is not filled."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Albany primary PDFs are "
        "archived under /workspace/wyoleg/local-results/albany/<year>/. The current (November 2026) precinct roster "
        "is in data/county_officials/albany.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Albany", county_number=5, slug="albany", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Albany", slug="albany")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def update_albany_json(people: dict):
    path = ROOT / "data" / "county_officials" / "albany.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
    # Keep existing precincts.
    precincts = None
    for g in data.get("groups") or []:
        if g.get("id") == "precincts":
            precincts = g
            break

    def office(title, holders, note="", layout=None):
        if layout is None:
            layout = "heading-then-names" if len(holders) > 1 else "office-and-name"
        rec = {"office": title, "layout": layout, "holders": holders}
        if note:
            rec["note"] = note
        return rec

    senate = [
        office("Senate District 9 (S09)", [
            _holder(people, "WY-ROTHFUSS-CHRIS", "Chris Rothfuss", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Senate District 10 (S10)", [
            _holder(people, "WY-CRUM-GARY", "Gary E. Crum", "REP", "January 2029"),
        ]),
    ]
    house_offices = [
        office("House District 13 (H13)", [
            _holder(people, "WY-CHESTEK-KEN", "Ken Chestek", "DEM", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 14 (H14)", [
            _holder(people, "WY-SHERWOOD-TREY", "Trey Sherwood", "DEM", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 45 (H45)", [
            _holder(people, "WY-PROVENZA-KARLEE", "Karlee Provenza", "DEM", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 46 (H46)", [
            _holder(people, "WY-ANDREW-OCEAN", "Ocean Andrew", "REP", "January 2027"),
            _holder(people, "WY-WRIGHT-CAMERON", "Cam Wright", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Cam Wright is the official 2026 general winner and takes office January 2027."),
    ]
    county = [
        office("County Commissioners", [
            _holder(people, "WY-HOFF-THAD", "Thad Hoff", "", "January 2029"),
            _holder(people, "WY-GOSAR-PETE", "Pete Gosar", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general second-recount winner, term begins January 2027."),
            _holder(people, "WY-JONES-TERRI", "Terri Jones", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general second-recount winner, term begins January 2027."),
        ], note="The official 2026 Vote-For-2 commissioner result is the November 9–10, 2026 second recount (clerk memorandum November 11, 2026)."),
        office("County Clerk", [
            _holder(people, "WY-WHITE-KAYLA", "Kayla White", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Treasurer", [
            _holder(people, "WY-FLETCHER-TRACY", "Tracy Fletcher", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Assessor", [
            _holder(people, "WY-MATHEWS-CHELSIE", "Chelsie Mathews", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Sheriff", [
            _holder(people, "WY-APPELHANS-AARON", "Aaron Appelhans", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Attorney", [
            _holder(people, "WY-BRITZIUS-EDWARD", "Edward Kurt Britzius", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Clerk of District Court", [
            _holder(people, "WY-LAM-STACY", "Stacy Lam", "REP", "January 2027"),
            _holder(people, "WY-MARROQUIN-KAYLA", "Kayla Marroquin", "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Kayla Marroquin is the official 2026 general winner and takes office January 2027."),
        office("County Coroner", [
            _holder(people, "WY-KING-SALLY", "Sally King", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
    ]
    municipal = [
        office("Laramie Mayor", [
            _holder(people, "WY-CUMBIE-SHARON", "Sharon Cumbie", "", "January 5, 2027",
                    role="Mayor",
                    notes="Selected by the Laramie City Council from its members. Official January 7, 2025 minutes and Resolution 2025-01; next regular selection is the first January 2027 council meeting."),
        ], note="The Laramie mayor is selected by the City Council from its members and is not on the November ballot."),
        office("Laramie City Council Ward 1", [
            _holder(people, "WY-RICHARDSON-MICAH", "Micah Richardson", "", "January 2027"),
            _holder(people, "WY-CUMBIE-SHARON", "Sharon Cumbie", "", "January 2029"),
            _holder(people, "WY-BOWLING-WILLIAM", "William Bowling", "", "January 2029"),
            _holder(people, "WY-JESSE-NICHOLAS", "Nicholas Jesse", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Nicholas Jesse is the official 2026 general winner and takes office January 2027."),
        office("Laramie City Council Ward 2", [
            _holder(people, "WY-NEWMAN-BRANDON", "Brandon Newman", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-VIGIL-MELANIE", "Melanie Vigil", "", "January 2029"),
            _holder(people, "WY-FRIED-JIM", "Jim Fried", "", "January 2029"),
        ]),
        office("Laramie City Council Ward 3", [
            _holder(people, "WY-ODOHERTY-ERIN", "Erin O'Doherty", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-SHUMWAY-JOE", "Joe Shumway", "", "January 2027"),
            _holder(people, "WY-LOCKHART-MATT", "Matt Lockhart", "", "January 2029"),
            _holder(people, "WY-HOOPER-TAMMY", "Tammy Hooper", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Tammy Hooper is the official 2026 general winner and takes office January 2027."),
        office("Rock River Mayor", [
            _holder(people, "WY-LESLIE-CATHY", "Cathy Leslie", "", "",
                    notes="Official Town of Rock River August 3, 2026 agenda, hosted on the official Albany County Agenda Center, lists Mayor Cathy Leslie. Official minutes of August 3 and March 2, 2026 say CJ Leslie. No term end stated on those official documents."),
        ]),
        office("Rock River Town Council", [
            _holder(people, "WY-SUMMERS-EVERETT", "Everett Summers", "", "",
                    notes="Official Town of Rock River August 3, 2026 agenda and official March 2 and August 3, 2026 minutes."),
            _holder(people, "WY-BOWERS-BOBBIE", "Bobbie Bowers", "", "",
                    notes="Official August 3, 2026 agenda header lists Bobbie Bowers; official August 3, 2026 minutes say Bob Bowers."),
            _holder(people, "WY-STALEY-SUMMER", "Summer Staley", "", "",
                    notes="Official August 3, 2026 agenda header; official August 3, 2026 minutes record her as absent."),
            _holder(people, "WY-GALLEGOS-VIRGIL", "Virgil Gallegos", "", "",
                    notes="Official Town of Rock River August 3, 2026 agenda and official March 2 and August 3, 2026 minutes."),
        ]),
    ]
    schools = [
        office("ACSD #1 Trustee Area A", [
            _holder(people, "WY-BRUCE-MARY-ALICE", "Mary Alice Bruce", "", "January 2027"),
            _holder(people, "WY-KRASSIN-ALEX-MOON", "Alex Moon Krassin", "", "January 2029",
                    notes="Official 2022 Area A and official 2024 Area A winner; the later official term is shown here."),
            _holder(people, "WY-GOSAR-STEVE", "Steve Gosar", "", "January 2027"),
            _holder(people, "WY-BEAR-BETH", "Beth Bear", "", "January 2027"),
            _holder(people, "WY-MURTHY-CARRIE", "Carrie Murthy", "", "January 2027"),
            _holder(people, "WY-STANTON-EMILY-SIEGEL", "Emily Siegel Stanton", "", "January 2029"),
            _holder(people, "WY-ARAGON-CECILIA", "Cecilia (CC) Aragon", "", "January 2029"),
        ]),
        office("ACSD #1 Trustee Area B", [
            _holder(people, "WY-MARSHALL-JANICE", "Janice Marshall", "", "January 2027"),
        ]),
        office("ACSD #1 Trustee At-Large", [
            _holder(people, "WY-MARTIN-NATE", "Nate Martin", "", "January 2027"),
            _holder(people, "WY-SORENSON-KIM", "Kim Sorenson", "", "January 2029"),
            _holder(people, "WY-MURTHY-CARRIE", "Carrie Murthy", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general at-large winner."),
        ], note="Carrie Murthy is the official 2026 general at-large winner and takes office January 2027."),
        office("ACSD #1 Trustee", [
            _holder(people, "WY-LEARNED-J-JAMES", "J. James Learned", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner; official summary has no area label."),
            _holder(people, "WY-TAYLOR-JESSICA", "Jessica Taylor", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner; official summary has no area label."),
            _holder(people, "WY-BEAR-BETH", "Beth Bear", "", "January 2031",
                    notes="Official 2022 Area A winner, continuing; official 2026 general winner (no area label on the official summary), term begins January 2027."),
            _holder(people, "WY-LENTNER-ABE", "Abe Lentner", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner; official summary has no area label."),
            _holder(people, "WY-BOWERS-BOB", "Bob Bowers", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner; official summary has no area label."),
        ], note="Official 2026 School District No. 1 Trustee contests are printed without Area A/B labels on the official summary."),
    ]
    special = [
        office("Fire District No. 1 Director", [
            _holder(people, "WY-BURKHART-MATTHEW", "Matthew Burkhart", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ], note="The official 2024 Fire District No. 1 Director contest reports only write-in totals and is not filled."),
        office("Hospital District Trustee", [
            _holder(people, "WY-ROARK-TERRY-P", "Terry P. Roark", "", "January 2027"),
            _holder(people, "WY-MAGUIRE-STEVE", "Stephen C. Maguire", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-COOK-DENNIS", "Dennis Cook", "", "January 2029"),
            _holder(people, "WY-SCOZZAFAVA-JENNA", "Jenna Scozzafava", "", "January 2029"),
            _holder(people, "WY-MELONE-RICK", "Rick Melone", "", "January 2029"),
            _holder(people, "WY-WARPNESS-GUY", "Guy Warpness", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Laramie Rivers Conservation District Supervisor Rural", [
            _holder(people, "WY-IDDINGS-ZACHARY-M", "Zachary M. Iddings", "", "January 2027"),
            _holder(people, "WY-MUNN-LARRY-C", "Larry C. Munn", "", "January 2029"),
            _holder(people, "WY-CORSON-JOHN", "John Corson", "", "January 2029"),
        ]),
        office("Laramie Rivers Conservation District Supervisor Urban", [
            _holder(people, "WY-MONTEITH-MARY-FICK", "Mary Fick Monteith", "", "January 2029"),
        ]),
        office("Laramie Rivers Conservation District Supervisor At-Large", [
            _holder(people, "WY-MARNEY-MANDY", "Mandy Marney", "", "January 2027"),
        ]),
        office("Laramie Rivers Conservation District Supervisor", [
            _holder(people, "WY-IDDINGS-ZACHARY-M", "Zachary M. Iddings", "", "January 2031",
                    notes="Official 2022 rural winner, continuing; official 2026 general winner (no urban/rural/at-large label on the official summary), term begins January 2027."),
            _holder(people, "WY-SEBADE-BRIAN", "Brian Sebade", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner; official summary has no urban/rural/at-large label."),
        ], note="Official 2026 conservation-district contests are printed without urban/rural/at-large labels on the official summary."),
    ]
    judicial = [
        office("District Judge, 2nd Judicial District", [
            _holder(people, "WY-WESTBY-MISHA", "Misha Westby", "", "January 2031",
                    notes="Official 2024 clerk Judge B WESTBY; given name and appointment from the official Wyoming Judicial Branch 2nd JD Albany district page."),
            _holder(people, "WY-SNYDER-DAWNESSA", "Dawnessa Snyder", "", "January 2031",
                    notes="Official 2024 clerk Judge A SNYDER, YES. Given name from official Wyoming Judicial Branch reporting on the 2nd JD appointment."),
        ]),
        office("Circuit Judge, 2nd Judicial District", [
            _holder(people, "WY-STIPE-SUSAN-K", "Susan K. Stipe", "", "January 2029",
                    notes="Official 2024 clerk: Circuit Court Judge Susan K. Stipe of the 2nd JD."),
            _holder(people, "WY-SANFORD-ROBERT-J", "Robert J. Sanford", "", "January 2031",
                    notes="Official 2022 term ends January 2027; official 2026 clerk circuit retention (YES, unnamed on the clerk line). Identified from the official Wyoming Judicial Branch 2nd JD Albany circuit page."),
        ]),
    ]

    groups = [
        {"id": "state-senate", "title": "State Senate", "offices": senate},
        {"id": "state-house", "title": "State House", "offices": house_offices},
        {"id": "county", "title": "County Offices", "offices": county},
        {"id": "municipal", "title": "Municipal Offices", "offices": municipal},
        {"id": "schools", "title": "School and College Boards", "offices": schools},
        {"id": "special-districts", "title": "Special Districts", "offices": special},
        {"id": "judicial", "title": "Judicial Retention", "offices": judicial},
    ]
    if precincts:
        groups.append(precincts)
    data["groups"] = groups
    src = data.get("sources") or {}
    src["general_results"] = "https://www.albanycountywy.gov/DocumentCenter/View/8518/2026-General-Election-Summary-Official-Results-with-Certification"
    src["primary_results"] = "https://www.albanycountywy.gov/DocumentCenter/View/8370/2026-Primary-Election-Official-Results---Albany-County"
    src["checked"] = RETRIEVED
    data["sources"] = src
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
