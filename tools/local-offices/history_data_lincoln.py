"""Lincoln County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
CLERK = "https://www.lincolncountywy.gov/government/clerk/elections_voting_information/election_results.php"
BASE = "https://www.lincolncountywy.gov/Documents/Government/Clerk/Election%20And%20Voting%20Information/Election%20Results%20And%20Upcoming%20Elections"

COURTS = {
    "lincoln-d": ("https://www.wyocourts.gov/court/district-court-3rd-judicial-district-lincoln-county/",
                  "Wyoming Judicial Branch official District Court, 3rd Judicial District, Lincoln County page"),
    "sweetwater-d": ("https://www.wyocourts.gov/court/district-court-3rd-judicial-district-sweetwater-county/",
                     "Wyoming Judicial Branch official District Court, 3rd Judicial District, Sweetwater County page"),
    "uinta-d": ("https://www.wyocourts.gov/court/district-court-3rd-judicial-district-uinta-county/",
                "Wyoming Judicial Branch official District Court, 3rd Judicial District, Uinta County page"),
    "rs-c": ("https://www.wyocourts.gov/court/circuit-court-of-the-3rd-judicial-district-sweetwater-county-state-of-wyoming-rock-springs/",
             "Wyoming Judicial Branch official Circuit Court of the 3rd Judicial District (Rock Springs) page"),
}

def sos_url(year: int) -> str:
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Lincoln_County_General_PbP.pdf"

def sos_house(year: int) -> dict:
    if year in (2014, 2018):
        url = f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Statewide_House_Candidates_Summary.pdf"
    else:
        url = f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_General_Statewide_House_Candidates_Summary.pdf"
    return {"label": f"Wyoming Secretary of State official {year} statewide House candidates summary", "url": url}

def sos_senate(year: int) -> dict:
    if year in (2014, 2018):
        url = f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Statewide_Senate_Candidates_Summary.pdf"
    else:
        url = f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_General_Statewide_Senate_Candidates_Summary.pdf"
    return {"label": f"Wyoming Secretary of State official {year} statewide Senate candidates summary", "url": url}

PG = {
    2022: (f"{BASE}/PREVIOUS%20ELECTION%20OFFICIAL%20RESULTS/2022%20OFFICIAL%20GENERAL%20ELECTION%20SUMMARY.pdf",
           "Lincoln County official 2022 general election summary"),
    2024: (f"{BASE}/PREVIOUS%20ELECTION%20OFFICIAL%20RESULTS/2024/2024%20GENERAL%20ELECTION/summary%202024%20general.pdf",
           "Lincoln County official 2024 general election summary"),
    2026: (f"{BASE}/2026/OFFICIAL%20SUMMARY%202026%20GEN.pdf",
           "Lincoln County official 2026 general election summary"),
}

def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}

def sos(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} Lincoln general precinct-by-precinct summary", "url": sos_url(year)}

def courts(which: str) -> dict:
    url, label = COURTS[which]
    return {"label": label, "url": url}

def T(**kw):
    if not kw.get("sources"):
        ey = kw.get("election_year")
        if ey in PG:
            kw["sources"] = [pg(ey)]
        elif ey:
            kw["sources"] = [sos(int(ey))]
    return H.term(**kw)

def register_people(P):
    rows = [
        ("WY-COOPER-STAN", "Stan Cooper", "Stan", "Cooper"),
        ("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "Fred", "Baldwin", "A.", "Fred Baldwin"),
        ("WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "Laura", "Pearson", "", "Laura Taliaferro Pearson; Laura Pearson; Laura Taliaferro"),
        ("WY-DOCKSTADER-DAN", "Dan Dockstader", "Dan", "Dockstader"),
        ("WY-CRANK-THOMAS-D", "Thomas D. Crank", "Thomas", "Crank", "D."),
        ("WY-HEINER-SCOTT", "Scott Heiner", "Scott", "Heiner"),
        ("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "Kenneth", "Roberts", "D."),
        ("WY-SOMMERS-ALBERT", "Albert Sommers", "Albert", "Sommers"),
        ("WY-SCHMID-MIKE", "Mike Schmid", "Mike", "Schmid"),
        ("WY-MCKIM-ROBERT", "Robert McKim", "Robert", "McKim"),
        ("WY-SIMPSON-EVAN-J", "Evan J. Simpson", "Evan", "Simpson", "J."),
        ("WY-ALLRED-LANE", "Lane Allred", "Lane", "Allred"),
        ("WY-ERICKSON-MCKAY-L", "McKay L. Erickson", "McKay", "Erickson", "L.", "McKay Erickson"),
        ("WY-HALVERSON-MARTI", "Marti Halverson", "Marti", "Halverson"),
        ("WY-ROSCOE-JIM", "Jim Roscoe", "Jim", "Roscoe"),
        ("WY-BYRON-ANDREW", "Andrew Byron", "Andrew", "Byron", "", "Andrew P. Byron"),
        ("WY-BOWERS-TERI", "Teri Bowers", "Teri", "Bowers"),
        ("WY-CONNELLY-KENT", "Kent Connelly", "Kent", "Connelly"),
        ("WY-SHUMWAY-MEL", "Mel Shumway", "Mel", "Shumway"),
        ("WY-LONG-JAKE", "Jake Long", "Jake", "Long"),
        ("WY-LOZIER-JESICA", "Jesica Lozier", "Jesica", "Lozier"),
        ("WY-SCHWAB-DAIN", "Dain Schwab", "Dain", "Schwab"),
        ("WY-ALLRED-SPENCER-L", "Spencer L. Allred", "Spencer", "Allred", "L.", "Spencer Allred"),
        ("WY-JOHNSON-M-SHANE", "M. Shane Johnson", "Shane", "Johnson", "", "Shane Johnson; M Shane Johnson"),
        ("WY-BRUNSKI-APRIL", "April Brunski", "April", "Brunski"),
        ("WY-GREENFIELD-JERRY-L", "Jerry L. Greenfield", "Jerry", "Greenfield", "L.", "Jerry Greenfield"),
        ("WY-ANTILLA-JOEY-K", "Joey K. Antilla", "Joey", "Antilla", "K."),
        ("WY-LARSON-DEBBIE", "Debbie Larson", "Debbie", "Larson"),
        ("WY-ROSAS-JASON", "Jason Rosas", "Jason", "Rosas"),
        ("WY-CLARKE-JENNY", "Jenny Clarke", "Jenny", "Clarke"),
        ("WY-JENSEN-JEFFREY", "Jeffrey Jensen", "Jeffrey", "Jensen"),
        ("WY-BOWEN-ROBERT", "Robert Bowen", "Robert", "Bowen"),
        ("WY-BACKMAN-ERIC", "Eric Backman", "Eric", "Backman"),
        ("WY-BOWEN-CLINT-M", "Clint M. Bowen", "Clint", "Bowen", "M."),
        ("WY-HALL-MARY-O", "Mary O. Hall", "Mary", "Hall", "O."),
        ("WY-RITZDORF-ANTHONY-J", "Anthony J. Ritzdorf", "Anthony", "Ritzdorf", "J."),
        ("WY-HINSON-RALPH", "Ralph Hinson", "Ralph", "Hinson"),
        ("WY-STEPP-LARRY", "Larry Stepp", "Larry", "Stepp"),
        ("WY-LARSEN-JEREMY", "Jeremy Larsen", "Jeremy", "Larsen"),
        ("WY-GREEN-ERIC", "Eric Green", "Eric", "Green"),
        ("WY-SIMPSON-DEVIN", "Devin Simpson", "Devin", "Simpson"),
        ("WY-PECK-COLBY-MARTIN", "Colby Martin Peck", "Colby", "Peck", "", "Colby Peck; Colby Martin Peck"),
        ("WY-THOMPSON-STANLEY-JR", "Stanley Thompson Jr.", "Stanley", "Thompson"),
        ("WY-ROK-RUZENA", "Ruzena Rok", "Ruzena", "Rok"),
        ("WY-BUYERS-KATHLEEN", "Kathleen Buyers", "Kathleen", "Buyers"),
        ("WY-JAMES-NENA", "Nena James", "Nena", "James"),
        ("WY-LAVERY-RICHARD-L", "Richard L. Lavery", "Richard", "Lavery", "L."),
        ("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "Joseph", "Bluemel", "B."),
        ("WY-KASTE-JAMES-C", "James C. Kaste", "James", "Kaste", "C."),
        ("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "Suzannah", "Robinson", "G."),
        ("WY-JONES-CRAIG-L", "Craig L. Jones", "Craig", "Jones", "L."),
        ("WY-PROKOS-JOHN-R", "John R. Prokos", "John", "Prokos", "R.", "John Prokos"),
        ("WY-ZEBRE-FRANK-J", "Frank J. Zebre", "Frank", "Zebre", "J."),
        ("WY-GREER-MICHAEL-L", "Michael L. Greer", "Michael", "Greer", "L."),
        ("WY-CORPENING-GREGORY-S", "Gregory S. Corpening", "Gregory", "Corpening", "S."),
        ("WY-GUINTA-KIMBERLY", "Kimberly Guinta", "Kimberly", "Guinta"),
        ("WY-WALKER-AARIKA", "Aarika Walker", "Aarika", "Walker"),
        ("WY-PETERNAL-ROBERT-J", "Robert J. Peternal", "Robert", "Peternal", "J."),
        ("WY-WAGNER-JASON-S", "Jason S. Wagner", "Jason", "Wagner", "S."),
        ("WY-DEARDEN-KRISTI", "Kristi Dearden", "Kristi", "Dearden"),
        ("WY-GRANDY-BRAD", "Brad Grandy", "Brad", "Grandy"),
        ("WY-LAMBORN-DON", "Don Lamborn", "Don", "Lamborn"),
        ("WY-DRANEY-LANNY-D", "Lanny D. Draney", "Lanny", "Draney", "D."),
        ("WY-DAY-CONNIE-W", "Connie W. Day", "Connie", "Day", "W."),
        ("WY-BENNETT-HOMER", "Homer Bennett", "Homer", "Bennett"),
        ("WY-ENGLAND-SPENCER", "Spencer England", "Spencer", "England"),
        ("WY-WILKES-KADE-W", "Kade W. Wilkes", "Kade", "Wilkes", "W."),
        ("WY-CALL-LYNN-A", "Lynn A. Call", "Lynn", "Call", "A.", "Lynn Call"),
        ("WY-ADAMS-PAIGE-W", "Paige W. Adams", "Paige", "Adams", "W."),
        ("WY-JENKINS-DAVID", "David Jenkins", "David", "Jenkins"),
        ("WY-JOHNSON-JED", "Jed Johnson", "Jed", "Johnson"),
        ("WY-SIMPSON-DARNELL", "Darnell Simpson", "Darnell", "Simpson"),
        ("WY-ARCHIBALD-MICHAEL-L", "Michael L. Archibald", "Michael", "Archibald", "L."),
        ("WY-PEAVLER-BARBARA", "Barbara Peavler", "Barbara", "Peavler"),
        ("WY-SPEARS-KEN", "Ken Spears", "Ken", "Spears"),
        ("WY-PRICE-BILL", "Bill Price", "Bill", "Price"),
        ("WY-MCCONKIE-DAVID", "David McConkie", "David", "McConkie"),
        ("WY-POPP-BRANTLEY", "Brantley Popp", "Brantley", "Popp"),
        ("WY-BATISTA-MARLIN", "Marlin Batista", "Marlin", "Batista"),
        ("WY-QUINN-MARK", "Mark Quinn", "Mark", "Quinn"),
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
            term_start=FM[a] if not isinstance(a, str) else a,
            term_end=FM[b] if not isinstance(b, str) else b,
            how_took_office=kw.pop("how_took_office", "elected"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=kw.pop("sources", [pg(ey)] if ey in PG else [sos(ey)] if ey else []), **kw,
        ))

    # S14 (Lincoln + Sublette + Sweetwater + Uinta). Even-numbered; presidential-cycle elections.
    add("WY-COOPER-STAN", "Stan Cooper", "state-senate", "Senate District 14 (S14)", "Lincoln County", 2013, 2017, 2012, "REP",
        sources=[sos(2012)], confidence="medium",
        notes="Official 2012 SOS Lincoln PbP totals: Stan Cooper 1,594, John Vincent Love 243. Official 2012 SOS Sublette PbP Total: Cooper 3,235, Love 325. Official 2012 SOS Uinta PbP Total: Cooper 620, Love 108. Official 2012 Sweetwater SOS S14 Total was not cleanly extracted from the two-column official report. Encoded from the official county reports that were extracted, all of which Cooper leads.")
    add("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-senate", "Senate District 14 (S14)", "Lincoln County", 2017, 2021, 2016, "REP",
        sources=[sos_senate(2016), sos(2016)],
        notes="Official 2016 SOS statewide Senate summary totals: Fred A. Baldwin 6,939, Sedey 1,237. Official 2016 Lincoln portion: Baldwin 1,663, Sedey 225.")
    add("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-senate", "Senate District 14 (S14)", "Lincoln County", 2021, 2025, 2020, "REP",
        sources=[sos_senate(2020), sos(2020)],
        notes="Official 2020 SOS statewide Senate summary totals: Fred A. Baldwin 7,779. Official 2020 Lincoln portion: Baldwin 1,709.")
    add("WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "state-senate", "Senate District 14 (S14)", "Lincoln County", 2025, 2029, 2024, "REP",
        sources=[sos_senate(2024), pg(2024)],
        notes="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025. Official 2024 Lincoln clerk portion: Pearson 2,116.")

    # S16 (Lincoln + Teton). Official SOS district-wide totals.
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Lincoln County", 2013, 2017, 2012, "REP",
        sources=[sos(2012)],
        notes="Official 2012 Teton clerk and official later SOS lines continue Dan Dockstader in S16; official 2012 Lincoln SOS is used with the official multi-county series. Also covers Teton County.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Lincoln County", 2017, 2021, 2016, "REP",
        sources=[sos_senate(2016), sos(2016)],
        notes="Official 2016 SOS statewide Senate summary totals: Dan Dockstader 7,208, Richard Kusaba 1,989. Official 2016 Lincoln portion: Dockstader 6,017, Kusaba 790.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Lincoln County", 2021, 2025, 2020, "REP",
        sources=[sos_senate(2020), sos(2020)],
        notes="Official 2020 SOS statewide Senate summary totals: Dan Dockstader 9,231. Official 2020 Lincoln portion: Dockstader 7,565.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Lincoln County", 2025, 2029, 2024, "REP",
        sources=[sos_senate(2024), pg(2024)],
        notes="Official 2024 SOS statewide Senate summary totals: Dan Dockstader 8,830. Official 2024 Lincoln clerk portion: Dockstader 7,355.")

    # H18 (Lincoln + Sweetwater + Uinta)
    add("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-house", "House District 18 (H18)", "Lincoln County", 2015, 2017, 2014, "REP",
        sources=[sos_house(2014), sos(2014)],
        notes="Official 2014 SOS statewide House summary totals: Fred A. Baldwin 2,297, Michele Irwin 719. Official 2014 Lincoln portion: Baldwin 1,107, Irwin 254.")
    add("WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Lincoln County", 2017, 2019, 2016, "REP",
        sources=[sos_house(2016), sos(2016)],
        notes="Official 2016 SOS statewide House summary totals: Thomas D. Crank 3,595, Michele Irwin 880. Official 2016 Lincoln portion: Crank 1,593, Irwin 287. An official 2016 House District 18 special is archived on the Sweetwater clerk site; no official Lincoln special PDF was found on the current Lincoln clerk site, so January snapshots do not invent a mid-2016 Lincoln start.")
    add("WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Lincoln County", 2019, 2021, 2018, "REP",
        sources=[sos_house(2018)],
        notes="Official 2018 SOS statewide House summary totals: Thomas D. Crank 3,088. Official 2018 Lincoln portion: Crank 1,356.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Lincoln County", 2021, 2023, 2020, "REP",
        sources=[sos_house(2020), sos(2020)],
        notes="Official 2020 SOS statewide House summary totals: Scott Heiner 3,981. Official 2020 Lincoln portion: Heiner 1,662.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Lincoln County", 2023, 2025, 2022, "REP",
        sources=[sos_house(2022), pg(2022)],
        notes="Official 2022 SOS statewide House summary totals: Scott Heiner 2,689, Dennis B. Laughlin 590. Official 2022 Lincoln clerk portion: Heiner 1,405, Laughlin 208.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Lincoln County", 2025, 2027, 2024, "REP",
        sources=[sos_house(2024), pg(2024)],
        notes="Official 2024 SOS statewide House summary totals: Scott Heiner 3,781. Official 2024 Lincoln clerk portion: Heiner 1,853.")
    add("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "state-house", "House District 18 (H18)", "Lincoln County", 2027, 2029, 2026, "REP",
        sources=[sos_house(2026), pg(2026)],
        notes="Official 2026 SOS statewide House summary totals: Kenneth D. Roberts 2,691. Official 2026 Lincoln clerk portion: Roberts 1,412. Roberts is also the official 2022 Lincoln Clerk of District Court (term ends January 2027).")

    # H20 (Sublette, plus a Lincoln sliver after the 2022 redistricting). Official SOS district-wide.
    add("WY-SOMMERS-ALBERT", "Albert Sommers", "state-house", "House District 20 (H20)", "Lincoln County", 2023, 2025, 2022, "REP",
        sources=[sos_house(2022), pg(2022)],
        notes="Official 2022 SOS statewide House summary totals: Albert Sommers 3,273. Official 2022 Lincoln clerk portion: Sommers 139 (Sublette 3,134). Official 2014–2020 statewide House summaries show a dash for Lincoln in H20; this seat appears on official Lincoln ballots beginning in 2022.")
    add("WY-SCHMID-MIKE", "Mike Schmid", "state-house", "House District 20 (H20)", "Lincoln County", 2025, 2027, 2024, "REP",
        sources=[sos_house(2024), pg(2024)],
        notes="Official 2024 SOS statewide House summary totals: Mike Schmid 4,354. Official 2024 Lincoln clerk portion: Schmid 279.")
    add("WY-SOMMERS-ALBERT", "Albert Sommers", "state-house", "House District 20 (H20)", "Lincoln County", 2027, 2029, 2026, "REP",
        sources=[sos_house(2026), pg(2026)],
        notes="Official 2026 SOS statewide House summary totals: Albert Sommers 3,349. Official 2026 Lincoln clerk portion: Sommers 154.")

    # H21 (Lincoln only on official statewide summaries)
    add("WY-MCKIM-ROBERT", "Robert McKim", "state-house", "House District 21 (H21)", "Lincoln County", 2015, 2017, 2014, "REP",
        sources=[sos_house(2014)], notes="Official 2014 SOS statewide House summary totals: Robert McKim 2,606 (Lincoln-only).")
    add("WY-MCKIM-ROBERT", "Robert McKim", "state-house", "House District 21 (H21)", "Lincoln County", 2017, 2019, 2016, "REP",
        sources=[sos_house(2016)], notes="Official 2016 SOS statewide House summary totals: Robert McKim 3,832, Fogle 344 (Lincoln-only).")
    add("WY-SIMPSON-EVAN-J", "Evan J. Simpson", "state-house", "House District 21 (H21)", "Lincoln County", 2019, 2021, 2018, "REP",
        sources=[sos_house(2018)], notes="Official 2018 SOS statewide House summary totals: Evan J. Simpson 3,184 (Lincoln-only).")
    add("WY-SIMPSON-EVAN-J", "Evan J. Simpson", "state-house", "House District 21 (H21)", "Lincoln County", 2021, 2023, 2020, "REP",
        sources=[sos_house(2020)], notes="Official 2020 SOS statewide House summary totals: Evan J. Simpson 4,705 (Lincoln-only).")
    add("WY-ALLRED-LANE", "Lane Allred", "state-house", "House District 21 (H21)", "Lincoln County", 2023, 2025, 2022, "REP",
        sources=[sos_house(2022), pg(2022)], notes="Official 2022 SOS statewide House / official 2022 Lincoln clerk: Lane Allred 3,066.")
    add("WY-ERICKSON-MCKAY-L", "McKay L. Erickson", "state-house", "House District 21 (H21)", "Lincoln County", 2025, 2027, 2024, "REP",
        sources=[sos_house(2024), pg(2024)], notes="Official 2024 SOS statewide House / official 2024 Lincoln clerk: McKay L. Erickson 4,947.")
    add("WY-ERICKSON-MCKAY-L", "McKay L. Erickson", "state-house", "House District 21 (H21)", "Lincoln County", 2027, 2029, 2026, "REP",
        sources=[sos_house(2026), pg(2026)], notes="Official 2026 SOS statewide House / official 2026 Lincoln clerk: McKay L. Erickson 3,159.")

    # H22 (Lincoln + Teton; official 2014 statewide also includes Sublette)
    add("WY-HALVERSON-MARTI", "Marti Halverson", "state-house", "House District 22 (H22)", "Lincoln County", 2015, 2017, 2014, "REP",
        sources=[sos_house(2014)],
        notes="Official 2014 SOS statewide House summary totals: Marti Halverson 1,991, Natalia Macker 1,224 (Lincoln 1,192–377; Teton 570–749; Sublette 229–98).")
    add("WY-HALVERSON-MARTI", "Marti Halverson", "state-house", "House District 22 (H22)", "Lincoln County", 2017, 2019, 2016, "REP",
        sources=[sos_house(2016)],
        notes="Official 2016 SOS statewide House summary totals: Marti Halverson 2,942, Marylee White 2,157. Official 2016 Lincoln portion: Halverson 1,860, White 767.")
    add("WY-ROSCOE-JIM", "Jim Roscoe", "state-house", "House District 22 (H22)", "Lincoln County", 2019, 2021, 2018, "IND",
        sources=[sos_house(2018)],
        notes="Official 2018 SOS statewide House summary totals: Jim Roscoe 2,495, Marti Halverson 1,983. Official 2018 Lincoln portion: Halverson 1,269, Roscoe 935.")
    add("WY-ROSCOE-JIM", "Jim Roscoe", "state-house", "House District 22 (H22)", "Lincoln County", 2021, 2023, 2020, "IND",
        sources=[sos_house(2020)],
        notes="Official 2020 SOS statewide House summary totals: Jim Roscoe 3,191, Bill Winney 2,825. Official 2020 Lincoln portion: Winney 1,999, Roscoe 1,227.")
    add("WY-BYRON-ANDREW", "Andrew Byron", "state-house", "House District 22 (H22)", "Lincoln County", 2023, 2025, 2022, "REP",
        sources=[sos_house(2022), pg(2022)],
        notes="Official 2022 SOS statewide House summary totals: Andrew Byron 2,235, Bob Strobel 1,681. Official 2022 Lincoln clerk portion: Byron 1,362, Strobel 743.")
    add("WY-BYRON-ANDREW", "Andrew P. Byron", "state-house", "House District 22 (H22)", "Lincoln County", 2025, 2027, 2024, "REP",
        sources=[sos_house(2024), pg(2024)],
        notes="Official 2024 SOS statewide House summary totals: Andrew Byron 4,189. Official 2024 Lincoln clerk portion: Andrew P. Byron 2,435.")
    add("WY-BYRON-ANDREW", "Andrew Byron", "state-house", "House District 22 (H22)", "Lincoln County", 2027, 2029, 2026, "REP",
        sources=[sos_house(2026), pg(2026)],
        notes="Official 2026 SOS statewide House summary totals: Andrew Byron 3,055. Official 2026 Lincoln clerk portion: Byron 1,656.")

    # Commissioners: 3-member board. Official clerks: midterm VF2, presidential VF1.
    # Official clerk generals for 2014–2020 are not on the current official Lincoln clerk site; official SOS Lincoln PbPs for those years do not include county offices. January 2015–2022 commissioner seats are Not yet collected except as filled below.
    add("WY-CONNELLY-KENT", "Kent Connelly", "county", "County Commissioner", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-BOWERS-TERI", "Teri Bowers", "county", "County Commissioner", "Lincoln County", 2023, 2027, 2022, "REP",
        notes="Official 2022 Lincoln clerk Vote-For-2: Kent Connelly 5,041, Teri Bowers 5,039. The 2020 Vote-For-1 class was not found in official sources in this archive, so January 2023–2024 is short one of three commissioner seats.")
    add("WY-SHUMWAY-MEL", "Mel Shumway", "county", "County Commissioner", "Lincoln County", 2025, 2029, 2024, "REP",
        notes="Official 2024 Lincoln clerk Vote-For-1: Mel Shumway 9,354.")
    add("WY-LONG-JAKE", "Jake Long", "county", "County Commissioner", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-LOZIER-JESICA", "Jesica Lozier", "county", "County Commissioner", "Lincoln County", 2027, 2031, 2026, "REP",
        notes="Official 2026 Lincoln clerk Vote-For-2: Jake Long 5,424, Jesica Lozier 4,602.")

    # Row offices, midterm 4-year, from official 2022 and 2026 clerks. 2014 and 2018 official clerk generals were not on the current official site.
    add("WY-BRUNSKI-APRIL", "April Brunski", "county", "County Clerk", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-BRUNSKI-APRIL", "April Brunski", "county", "County Clerk", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-GREENFIELD-JERRY-L", "Jerry L. Greenfield", "county", "County Treasurer", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-ANTILLA-JOEY-K", "Joey K. Antilla", "county", "County Treasurer", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-LARSON-DEBBIE", "Debbie Larson", "county", "County Assessor", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-ROSAS-JASON", "Jason Rosas", "county", "County Assessor", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-JOHNSON-M-SHANE", "Shane Johnson", "county", "County Sheriff", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-JOHNSON-M-SHANE", "M. Shane Johnson", "county", "County Sheriff", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-ALLRED-SPENCER-L", "Spencer Allred", "county", "County Attorney", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-ALLRED-SPENCER-L", "Spencer L. Allred", "county", "County Attorney", "Lincoln County", 2027, 2031, 2026, "REP")
    add("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "county", "Clerk of District Court", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-CLARKE-JENNY", "Jenny Clarke", "county", "Clerk of District Court", "Lincoln County", 2027, 2031, 2026, "REP",
        notes="Official 2026 Lincoln clerk prints JENNY CLARKE.")
    add("WY-SCHWAB-DAIN", "Dain Schwab", "county", "County Coroner", "Lincoln County", 2023, 2027, 2022, "REP")
    add("WY-SCHWAB-DAIN", "Dain Schwab", "county", "County Coroner", "Lincoln County", 2027, 2031, 2026, "REP")
    return terms
def judicial_terms():
    terms = []

    def jt(pid, name, office, start, end, ey=None, how="retained", conf="high", src=None, notes=""):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office=office, jurisdiction="3rd Judicial District",
            term_start=start, term_end=end, how_took_office=how,
            election_year=ey, confidence=conf, sources=src or ([sos(ey)] if ey and ey not in PG else [pg(ey)] if ey in PG else []),
            notes=notes,
        ))

    dist = "District Judge, 3rd Judicial District"
    circ = "Circuit Judge, 3rd Judicial District"

    jt("WY-JAMES-NENA", "Nena James", dist, FM[2015], FM[2021], 2014, "retained", "high",
       [sos(2014)], "Official 2014 SOS Lincoln general PbP: retained Nena James, District Court Judge, Third Judicial District.")
    jt("WY-LAVERY-RICHARD-L", "Richard L. Lavery", dist, FM[2015], FM[2021], 2014, "retained", "high",
       [sos(2014)], "Official 2014 SOS Lincoln general PbP: retained Richard L. Lavery.")
    jt("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", dist, "2015-01-01", FM[2023], None, "appointed", "medium",
       [courts("lincoln-d")],
       "Official Wyoming Judicial Branch Lincoln 3rd JD district page: Honorable Joseph B. Bluemel, appointed January 2015 (day unstated; term_start 2015-01-01, medium), retained November 2022, term expires January 2029.")
    # Fix: official page appointed January 2015 — use 2015-01-01 medium, retained 2022 through Jan 2029
    # I'll replace the Bluemel first term below by writing a single term 2015-01-01 to FM[2029] with 2022 retain.
    jt("WY-KASTE-JAMES-C", "James C. Kaste", dist, "2022-10-01", FM[2031], 2024, "appointed", "medium",
       [courts("uinta-d"), pg(2024), sos(2024)],
       "Official Wyoming Judicial Branch Uinta 3rd JD district page: Honorable James C. Kaste, appointed October 2022 (day unstated; term_start 2022-10-01, medium), retained November 2024, term expires January 2031. Official 2024 Lincoln clerk last-name DIST CT - KASTE filled from that court page and official SOS.")
    jt("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", dist, "2019-10-01", FM[2027], 2020, "appointed", "medium",
       [courts("sweetwater-d"), sos(2020)],
       "Official Wyoming Judicial Branch Sweetwater 3rd JD district page: Honorable Suzannah G. Robinson, appointed October 2019 (day unstated; term_start 2019-10-01, medium), retained November 2020, term expires January 2027, stands November 2026.")
    jt("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", dist, FM[2027], FM[2031], 2026, "retained", "high",
       [pg(2026), courts("sweetwater-d")],
       "Official 2026 Lincoln clerk: RETAIN JUDGE C DIST CT JUDGE ROBINSON, YES, continuing January 2027–2031. Full name from the official Sweetwater 3rd JD district page.")
    jt("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", dist, FM[2023], FM[2029], 2022, "retained", "high",
       [pg(2022), courts("lincoln-d")],
       "Official 2022 Lincoln clerk DIST CT - BLUEMEL, YES, filled as Joseph B. Bluemel from the official Lincoln 3rd JD district page and official SOS. Term expires January 2029.")

    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, FM[2015], FM[2019], 2014, "retained", "high",
       [sos(2014)], "Official 2014 SOS Lincoln general PbP: retained Craig L. Jones.")
    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, FM[2019], FM[2023], 2018, "retained", "high", [sos(2018)])
    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, FM[2023], FM[2027], 2022, "retained", "high",
       [pg(2022), sos(2022)], "Official 2022 Lincoln clerk CIRCUIT CT - JONES, YES, filled as Craig L. Jones from official 2014/2018 SOS and later official clerk lines.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, FM[2015], FM[2019], 2014, "retained", "high",
       [sos(2014), courts("rs-c")], "Official 2014 SOS Lincoln general PbP: retained John R. Prokos. Official Rock Springs 3rd JD circuit page: appointed June 2013.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, FM[2019], FM[2023], 2018, "retained", "high", [sos(2018)])
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, FM[2023], FM[2027], 2022, "retained", "high",
       [pg(2022)], "Official 2022 Lincoln clerk CIRCUIT CT - PROKOS, YES.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, FM[2027], FM[2031], 2026, "retained", "high",
       [pg(2026), courts("rs-c")], "Official 2026 Lincoln clerk RETAIN CIRCUIT COURT JUDGE PROKOS, YES, continuing January 2027–2031.")
    jt("WY-ZEBRE-FRANK-J", "Frank J. Zebre", circ, FM[2015], FM[2019], 2014, "retained", "high",
       [sos(2014)], "Official 2014 SOS Lincoln general PbP: retained Frank J. Zebre.")
    jt("WY-GREER-MICHAEL-L", "Michael L. Greer", circ, FM[2025], FM[2029], 2024, "retained", "high",
       [pg(2024)], "Official 2024 Lincoln clerk CIRCUIT CT - GREER, YES, filled as Michael L. Greer from official 2024 clerk/SOS and official 3rd JD circuit pages used in the Sweetwater archive.")
    jt("WY-CORPENING-GREGORY-S", "Gregory S. Corpening", circ, FM[2025], FM[2029], 2024, "retained", "high",
       [pg(2024)], "Official 2024 Lincoln clerk CIRCUIT CT - CORPENING, YES, filled as Gregory S. Corpening from official 2024 clerk/SOS.")
    # Remove the first short Bluemel appointed term that used FM[2015]-FM[2023] overlapping the retain — I'll filter in build or fix here.
    return terms


def local_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, **kw):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a] if not isinstance(a, str) else a,
            term_end=FM[b] if not isinstance(b, str) else b,
            how_took_office=kw.pop("how_took_office", "elected"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=kw.pop("sources", [pg(ey)] if ey in PG else []), **kw,
        ))

    # Mayors appear on official November clerk ballots (not council-selected).
    # Midterm 4-year cycle (official 2022 and 2026 clerks): Afton, Alpine, Thayne, Star Valley Ranch, Diamondville, Opal, LaBarge.
    # Kemmerer mayor appears on the official 2024 clerk (presidential 4-year cycle), not on official 2022 or 2026 clerks.
    # Cokeville mayor appears on official 2022, 2024, and 2026 clerks (2-year cycle).
    add("WY-BOWEN-CLINT-M", "Clint M. Bowen", "municipal", "Diamondville Mayor", "Town of Diamondville", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Clint M. Bowen 135, Charles \"Mark\" Langley 86.")
    add("WY-BACKMAN-ERIC", "Eric Backman", "municipal", "Diamondville Mayor", "Town of Diamondville", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Eric Backman 171.")
    add("WY-RITZDORF-ANTHONY-J", "Anthony J. Ritzdorf", "municipal", "Opal Mayor", "Town of Opal", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Anthony J. Ritzdorf 20, Donald Clayton 16.")
    add("WY-HALL-MARY-O", "Mary O. Hall", "municipal", "Opal Mayor", "Town of Opal", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Mary O. Hall 26, Robert Chapin 15.")
    add("WY-STEPP-LARRY", "Larry Stepp", "municipal", "LaBarge Mayor", "Town of LaBarge", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Larry Stepp 110.")
    add("WY-HINSON-RALPH", "Ralph Hinson", "municipal", "LaBarge Mayor", "Town of LaBarge", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Ralph Hinson 84, Taylor Moceika 80.")
    add("WY-JENSEN-JEFFREY", "Jeffrey Jensen", "municipal", "Afton Mayor", "Town of Afton", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Jeffrey Jensen 621.")
    add("WY-JENSEN-JEFFREY", "Jeffrey Jensen", "municipal", "Afton Mayor", "Town of Afton", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Jeffrey Jensen 331, Jay Conley 274.")
    add("WY-GREEN-ERIC", "Eric Green", "municipal", "Alpine Mayor", "Town of Alpine", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Eric Green 230, W. Kennis Lutz 162.")
    add("WY-LARSEN-JEREMY", "Jeremy Larsen", "municipal", "Alpine Mayor", "Town of Alpine", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Jeremy Larsen 265, William J. Saks 171.")
    add("WY-SIMPSON-DEVIN", "Devin Simpson", "municipal", "Thayne Mayor", "Town of Thayne", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Devin Simpson 78.")
    add("WY-SIMPSON-DEVIN", "Devin Simpson", "municipal", "Thayne Mayor", "Town of Thayne", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Devin Simpson 80.")
    add("WY-THOMPSON-STANLEY-JR", "Stanley Thompson Jr.", "municipal", "Cokeville Mayor", "Town of Cokeville", 2023, 2025, 2022,
        notes="Official 2022 Lincoln clerk: Stanley Thompson Jr. 113, Alek Gilmore 97. Official 2022, 2024, and 2026 clerks all have a Cokeville mayor contest, so these terms are encoded as two-year terms.")
    add("WY-PECK-COLBY-MARTIN", "Colby Martin Peck", "municipal", "Cokeville Mayor", "Town of Cokeville", 2025, 2027, 2024,
        notes="Official 2024 Lincoln clerk: Colby Martin Peck 169. Official 2024 clerk notes candidate Alek R. Gilmore withdrawn.")
    add("WY-PECK-COLBY-MARTIN", "Colby Martin Peck", "municipal", "Cokeville Mayor", "Town of Cokeville", 2027, 2029, 2026,
        notes="Official 2026 Lincoln clerk: Colby Martin Peck 117, Theresa Lee Lewis 42.")
    add("WY-BUYERS-KATHLEEN", "Kathleen Buyers", "municipal", "Star Valley Ranch Mayor", "Town of Star Valley Ranch", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Kathleen Buyers 404, Don Baillie 387.")
    add("WY-ROK-RUZENA", "Ruzena Rok", "municipal", "Star Valley Ranch Mayor", "Town of Star Valley Ranch", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Ruzena Rok 410, Keith Jackson 355.")
    add("WY-BOWEN-ROBERT", "Robert Bowen", "municipal", "Kemmerer Mayor", "City of Kemmerer", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk: Robert Bowen 781, Rachelle Points 411. No mayor contest on official 2022 or 2026 clerks, consistent with a four-year presidential cycle. The Kemmerer mayor is elected on the official November ballot, not selected by the council.")

    # Schools — official 2022, 2024, 2026 clerks. Pre-2022 official clerk generals were not on the current official site.
    add("WY-PETERNAL-ROBERT-J", "Robert J. Peternal", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2023, 2027, 2022)
    add("WY-WALKER-AARIKA", "Aarika Walker", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk Vote-For-2: Robert J. Peternal 709, Aarika Walker 610.")
    add("WY-DEARDEN-KRISTI", "Kristi Dearden", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2025, 2029, 2024)
    add("WY-GRANDY-BRAD", "Brad Grandy", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2025, 2029, 2024)
    add("WY-LAMBORN-DON", "Don Lamborn", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk Vote-For-3 (read from the official scan): Kristi Dearden 1,344, Brad Grandy 1,221, Don Lamborn 1,136.")
    add("WY-GUINTA-KIMBERLY", "Kimberly Guinta", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2027, 2031, 2026)
    add("WY-WALKER-AARIKA", "Aarika Walker", "schools", "LCSD #1 Trustee", "Lincoln County School District #1", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk Vote-For-2: Kimberly Guinta 810, Aarika Walker 653, over Jillian Fox 607.")
    add("WY-DAY-CONNIE-W", "Connie W. Day", "schools", "LCSD #2 Trustee At-Large", "Lincoln County School District #2", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Connie W. Day 2,163.")
    add("WY-LONG-JAKE", "Jake Long", "schools", "LCSD #2 Trustee At-Large", "Lincoln County School District #2", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk: Jake Long 4,852, Homer Bennett 2,535. The same person is the official 2026 county commissioner elect (takes office January 2027).")
    add("WY-DRANEY-LANNY-D", "Lanny D. Draney", "schools", "LCSD #2 Trustee At-Large", "Lincoln County School District #2", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Lanny D. Draney 2,785, Eileen Merritt 2,072.")
    add("WY-CALL-LYNN-A", "Lynn Call", "schools", "LCSD #2 Trustee Area 2", "Lincoln County School District #2", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: Lynn Call 2,674, Brenda Robinson 2,042.")
    add("WY-CALL-LYNN-A", "Lynn A. Call", "schools", "LCSD #2 Trustee Area 2", "Lincoln County School District #2", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Lynn A. Call 2,964, Val Nelson 1,613.")
    add("WY-JENKINS-DAVID", "David Jenkins", "schools", "LCSD #2 Trustee Area 5", "Lincoln County School District #2", 2023, 2027, 2022,
        notes="Official 2022 Lincoln clerk: David Jenkins 4,609.")
    add("WY-ADAMS-PAIGE-W", "Paige W. Adams", "schools", "LCSD #2 Trustee Area 5", "Lincoln County School District #2", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Paige W. Adams 4,232.")
    add("WY-WILKES-KADE-W", "Kade W. Wilkes", "schools", "LCSD #2 Trustee Area 1", "Lincoln County School District #2", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk: Kade W. Wilkes 4,092, Lenn Johnson 2,858.")
    add("WY-ENGLAND-SPENCER", "Spencer England", "schools", "LCSD #2 Trustee Area 1", "Lincoln County School District #2", 2027, 2031, 2026,
        notes="Official 2026 Lincoln clerk: Spencer England 2,335, Lenn Johnson 2,217.")
    add("WY-JOHNSON-JED", "Jed Johnson", "schools", "LCSD #2 Trustee Area 3", "Lincoln County School District #2", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk (official scan): Jed Johnson 3,180, Tom McKinney 2,469, Logan Probst 1,027.")
    add("WY-SIMPSON-DARNELL", "Darnell Simpson", "schools", "LCSD #2 Trustee Area 4", "Lincoln County School District #2", 2025, 2029, 2024,
        notes="Official 2024 Lincoln clerk: Darnell Simpson 6,773.")
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


def build_lincoln():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    register_more_people(P)

    terms = []
    terms.extend(legislature_and_county_terms())
    terms.extend(judicial_terms())
    terms.extend(local_terms())
    terms.extend(council_and_special_terms())

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
        # Do not copy other judicial districts. Lincoln is in the 3rd JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 14 (S14)", 1),
            ("Senate District 16 (S16)", 1),
        ],
        "state-house": [
            ("House District 18 (H18)", 1),
            ("House District 20 (H20)", 1),
            ("House District 21 (H21)", 1),
            ("House District 22 (H22)", 1),
        ],
        "county": [
            ("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Kemmerer Mayor", 1),
            ("Afton Mayor", 1),
            ("Alpine Mayor", 1),
            ("Thayne Mayor", 1),
            ("Cokeville Mayor", 1),
            ("Star Valley Ranch Mayor", 1),
            ("Diamondville Mayor", 1),
            ("Opal Mayor", 1),
            ("LaBarge Mayor", 1),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "3rd Judicial District judges (Lincoln, Sweetwater, and Uinta). Where an official Lincoln clerk summary prints "
        "only a last name (official 2022 DIST CT - BLUEMEL / CIRCUIT CT - JONES / PROKOS; official 2024 DIST CT - KASTE / "
        "CIRCUIT CT - GREER / CORPENING; official 2026 JUDGE C DIST CT JUDGE ROBINSON / JUDGE PROKOS), the full name is "
        "taken from an official SOS line or official Wyoming Judicial Branch 3rd JD page, and that source is cited. "
        "Judges of other districts are not copied here."
    )
    special_note = (
        "Municipal, school, and special-district names for 2022–2026 are keyed from official Lincoln clerk November "
        "general results in this archive (official 2024 general is an official scan; names and totals were read from "
        "that official PDF). Official 2010–2020 Lincoln clerk general summaries are not posted on the current official "
        "clerk election-results page, and official SOS Lincoln precinct-by-precinct summaries for those years do not "
        "include county, municipal, or school offices, so those earlier January local rows are Not yet collected rather "
        "than invented. Mayors of Afton, Alpine, Thayne, Star Valley Ranch, Diamondville, Opal, LaBarge, Cokeville, and "
        "Kemmerer appear on official November clerk ballots and are not council-selected. Kemmerer mayor is on the "
        "official 2024 clerk (four-year presidential cycle). Cokeville mayor appears on official 2022, 2024, and 2026 "
        "clerks and is encoded as two-year terms. Official 2026 certified write-ins (Lincoln County Canvassing Board, "
        "November 5, 2026) name additional local winners and are archived. House District 20 appears on official Lincoln "
        "ballots beginning in 2022. Official mid-term vacancies are not invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Lincoln primary PDFs are "
        "archived under /workspace/wyoleg/local-results/lincoln/<year>/. The current (November 2026) precinct roster is "
        "in data/county_officials/lincoln.json, from the official 2026 primary (named winners only; 13 precincts / 51 holders)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Lincoln", county_number=12, slug="lincoln", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Lincoln", slug="lincoln")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def update_lincoln_json(people: dict):
    path = ROOT / "data" / "county_officials" / "lincoln.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
    data["county_number"] = 12
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
        office("Senate District 14 (S14)", [
            _holder(people, "WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "REP", "January 2029",
                    notes="Official 2024 winner. Also covers Sublette, Sweetwater, and Uinta. Official SOS district-wide totals are used for this multi-county seat."),
        ], note="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official 2024 Lincoln clerk portion: 2,116. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA."),
        office("Senate District 16 (S16)", [
            _holder(people, "WY-DOCKSTADER-DAN", "Dan Dockstader", "REP", "January 2029",
                    notes="Official 2024 winner; not on the 2026 ballot. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat."),
        ]),
    ]
    house_offices = [
        office("House District 18 (H18)", [
            _holder(people, "WY-HEINER-SCOTT", "Scott Heiner", "REP", "January 2027"),
            _holder(people, "WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official SOS district-wide totals: Roberts 2,691. Official 2026 Lincoln clerk portion: 1,412. Also covers Sweetwater and Uinta."),
        ], note="Kenneth D. Roberts is the official 2026 general winner and takes office January 2027. Official SOS district-wide totals are used for this multi-county seat."),
        office("House District 20 (H20)", [
            _holder(people, "WY-SCHMID-MIKE", "Mike Schmid", "REP", "January 2027"),
            _holder(people, "WY-SOMMERS-ALBERT", "Albert Sommers", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official SOS district-wide totals: Sommers 3,349. Official 2026 Lincoln clerk portion: 154. Also covers Sublette."),
        ], note="Albert Sommers is the official 2026 general winner and takes office January 2027. Official SOS district-wide totals are used for this multi-county seat."),
        office("House District 21 (H21)", [
            _holder(people, "WY-ERICKSON-MCKAY-L", "McKay L. Erickson", "REP", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 22 (H22)", [
            _holder(people, "WY-BYRON-ANDREW", "Andrew Byron", "REP", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027. Also covers Teton County. Official SOS district-wide totals are used for this multi-county seat."),
        ]),
    ]
    county = [
        office("County Commissioner", [
            _holder(people, "WY-BOWERS-TERI", "Teri Bowers", "REP", "January 2027"),
            _holder(people, "WY-CONNELLY-KENT", "Kent Connelly", "REP", "January 2027"),
            _holder(people, "WY-SHUMWAY-MEL", "Mel Shumway", "REP", "January 2029"),
            _holder(people, "WY-LONG-JAKE", "Jake Long", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-LOZIER-JESICA", "Jesica Lozier", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Jake Long and Jesica Lozier are official 2026 general winners and take office January 2027. Teri Bowers and Kent Connelly's official 2022 terms end January 2027. Mel Shumway continues."),
        office("County Clerk", [
            _holder(people, "WY-BRUNSKI-APRIL", "April Brunski", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Treasurer", [
            _holder(people, "WY-GREENFIELD-JERRY-L", "Jerry L. Greenfield", "REP", "January 2027"),
            _holder(people, "WY-ANTILLA-JOEY-K", "Joey K. Antilla", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Joey K. Antilla is the official 2026 general winner and takes office January 2027."),
        office("County Assessor", [
            _holder(people, "WY-LARSON-DEBBIE", "Debbie Larson", "REP", "January 2027"),
            _holder(people, "WY-ROSAS-JASON", "Jason Rosas", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Jason Rosas is the official 2026 general winner and takes office January 2027."),
        office("County Sheriff", [
            _holder(people, "WY-JOHNSON-M-SHANE", "M. Shane Johnson", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Attorney", [
            _holder(people, "WY-ALLRED-SPENCER-L", "Spencer L. Allred", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Clerk of District Court", [
            _holder(people, "WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "REP", "January 2027"),
            _holder(people, "WY-CLARKE-JENNY", "Jenny Clarke", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 Lincoln clerk prints JENNY CLARKE."),
        ], note="Jenny Clarke is the official 2026 general winner and takes office January 2027."),
        office("County Coroner", [
            _holder(people, "WY-SCHWAB-DAIN", "Dain Schwab", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
    ]
    municipal = [
        office("Kemmerer Mayor", [
            _holder(people, "WY-BOWEN-ROBERT", "Robert Bowen", "", "January 2029",
                    notes="Official 2024 general winner. The Kemmerer mayor is elected on the official November ballot, not selected by the council."),
        ]),
        office("Afton Mayor", [
            _holder(people, "WY-JENSEN-JEFFREY", "Jeffrey Jensen", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Alpine Mayor", [
            _holder(people, "WY-GREEN-ERIC", "Eric Green", "", "January 2027"),
            _holder(people, "WY-LARSEN-JEREMY", "Jeremy Larsen", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Jeremy Larsen is the official 2026 general winner and takes office January 2027."),
        office("Thayne Mayor", [
            _holder(people, "WY-SIMPSON-DEVIN", "Devin Simpson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Cokeville Mayor", [
            _holder(people, "WY-PECK-COLBY-MARTIN", "Colby Martin Peck", "", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027. Official 2022–2026 clerks all have a Cokeville mayor contest (two-year terms)."),
        ]),
        office("Star Valley Ranch Mayor", [
            _holder(people, "WY-BUYERS-KATHLEEN", "Kathleen Buyers", "", "January 2027"),
            _holder(people, "WY-ROK-RUZENA", "Ruzena Rok", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Ruzena Rok is the official 2026 general winner and takes office January 2027."),
        office("Diamondville Mayor", [
            _holder(people, "WY-BOWEN-CLINT-M", "Clint M. Bowen", "", "January 2027"),
            _holder(people, "WY-BACKMAN-ERIC", "Eric Backman", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Eric Backman is the official 2026 general winner and takes office January 2027."),
        office("Opal Mayor", [
            _holder(people, "WY-RITZDORF-ANTHONY-J", "Anthony J. Ritzdorf", "", "January 2027"),
            _holder(people, "WY-HALL-MARY-O", "Mary O. Hall", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Mary O. Hall is the official 2026 general winner and takes office January 2027."),
        office("LaBarge Mayor", [
            _holder(people, "WY-STEPP-LARRY", "Larry Stepp", "", "January 2027"),
            _holder(people, "WY-HINSON-RALPH", "Ralph Hinson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Ralph Hinson is the official 2026 general winner and takes office January 2027."),
        office("Kemmerer Council", [
            _holder(people, "WY-BATISTA-MARLIN", "Marlin Batista", "", "January 2027"),
            _holder(people, "WY-BOWEN-ROBERT", "Robert Bowen", "", "January 2027",
                    notes="Official 2022 council term ends January 2027. Also the official 2024 Kemmerer mayor."),
            _holder(people, "WY-QUINN-MARK", "Mark Quinn", "", "January 2027"),
            _holder(people, "WY-PRICE-BILL", "Bill Price", "", "January 2029"),
            _holder(people, "WY-MCCONKIE-DAVID", "David McConkie", "", "January 2029"),
            _holder(people, "WY-POPP-BRANTLEY", "Brantley Popp", "", "January 2029"),
            _holder(people, "WY-PEAVLER-BARBARA", "Barbara Peavler", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-SPEARS-KEN", "Ken Spears", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-ARCHIBALD-MICHAEL-L", "Michael L. Archibald", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Barbara Peavler, Ken Spears, and Michael L. Archibald are official 2026 general winners and take office January 2027."),
        office("Diamondville Council", [
            _holder(people, "WY-BACKMAN-ERIC", "Eric Backman", "", "January 2027"),
            _holder(people, "WY-SLOAN-SHERROL", "Sherrol Sloan", "", "January 2027"),
            _holder(people, "WY-SAWAYA-ROBERT", "Robert Sawaya", "", "January 2029"),
            _holder(people, "WY-PETERSEN-NICOLE", "Nicole Petersen", "", "January 2029"),
            _holder(people, "WY-CLARK-CASEY", "Casey Clark", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-SAWAYA-ROBERT", "Robert Sawaya", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 certified write-in (Lincoln County Canvassing Board, November 5, 2026)."),
            _holder(people, "WY-HOUSLEY-DIANE", "Diane Housley", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner, two-year term."),
        ], note="Casey Clark, official certified write-in Robert Sawaya, and Diane Housley take office January 2027."),
        office("Opal Council", [
            _holder(people, "WY-BEEHLER-MICHALE", "Michale Beehler", "", "January 2031",
                    notes="Official 2022 term, continuing; official 2026 general winner, term begins January 2027. Official spelling Michale."),
            _holder(people, "WY-RITZDORF-MAXINE-R", "Maxine R. Ritzdorf", "", "January 2027"),
            _holder(people, "WY-PALANO-STEPHEN", "Stephen Palano", "", "January 2029"),
            _holder(people, "WY-WHITEFORD-DANIEL-SR", "Daniel Whiteford Sr.", "", "January 2029"),
            _holder(people, "WY-BIENZ-ELLIE", "Ellie Bienz", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("LaBarge Council", [
            _holder(people, "WY-HINSON-RALPH", "Ralph Hinson", "", "January 2027"),
            _holder(people, "WY-HOWARD-SCOTT", "Scott Howard", "", "January 2027"),
            _holder(people, "WY-HEADRICK-ROWDY-L", "Rowdy L. Headrick", "", "January 2029"),
            _holder(people, "WY-VILOS-JAKE-J", "Jake J. Vilos", "", "January 2029"),
            _holder(people, "WY-BRANDT-JENNIFER", "Jennifer Brandt", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-MARQUARDT-RICK", "Rick Marquardt", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Afton Council", [
            _holder(people, "WY-HILLYARD-DIRK", "Dirk Hillyard", "", "January 2029",
                    notes="Official 2022 four-year term ends January 2027; official 2026 two-year winner, term begins January 2027."),
            _holder(people, "WY-WILKES-WILLIAM", "William Wilkes", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-BUTLER-MICHAEL-F", "Michael F. Butler", "", "January 2029"),
            _holder(people, "WY-GRIFFITH-SCOTT-E", "Scott E. Griffith", "", "January 2029"),
            _holder(people, "WY-BROWN-BROCK", "Brock Brown", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Alpine Council", [
            _holder(people, "WY-CASTILLO-EMILY", "Emily Castillo", "", "January 2027"),
            _holder(people, "WY-LARSEN-JEREMY", "Jeremy Larsen", "", "January 2027"),
            _holder(people, "WY-SCAFFIDE-SHAY", "Shay Scaffide", "", "January 2029"),
            _holder(people, "WY-BURCHARD-ANDREA", "Andrea Burchard", "", "January 2029"),
            _holder(people, "WY-WIERDA-AMY", "Amy Wierda", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-HARRIS-KEN", "Ken Harris", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Thayne Council", [
            _holder(people, "WY-HEWARD-JOE", "Joe Heward", "", "January 2027"),
            _holder(people, "WY-PASSEY-NIKOLE", "Nikole Passey", "", "January 2029"),
            _holder(people, "WY-ALLRED-MICHAEL", "Michael Allred", "", "January 2029"),
            _holder(people, "WY-PASSEY-TANNER", "Tanner Passey", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-VISSER-JUSTIN-C", "Justin C. Visser", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-VEIGEL-SPENCER", "Spencer Veigel", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner, two-year term."),
            _holder(people, "WY-DENIZ-MALINDA-JAN", "Malinda Jan DeNiz", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 certified write-in, two-year unexpired (Lincoln County Canvassing Board, November 5, 2026)."),
        ]),
        office("Cokeville Council", [
            _holder(people, "WY-LEWIS-THERESA", "Theresa Lewis", "", "January 2027"),
            _holder(people, "WY-HARMON-WAYNE", "Wayne Harmon", "", "January 2027"),
            _holder(people, "WY-NATE-BRAD-SHANE", "Brad Shane Nate", "", "January 2029"),
            _holder(people, "WY-DAYTON-CHARLES", "Charles Dayton", "", "January 2029"),
            _holder(people, "WY-FISCUS-SUSAN", "Susan Fiscus", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-BIRD-CAMERON-JOHN", "Cameron John Bird", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Star Valley Ranch Council", [
            _holder(people, "WY-MERRILL-KIRSTEN", "Kirsten Merrill", "", "January 2027"),
            _holder(people, "WY-ROK-RUZENA", "Ruzena Rok", "", "January 2027"),
            _holder(people, "WY-TOOLSON-KATIE", "Katie Toolson", "", "January 2029"),
            _holder(people, "WY-ELLIS-TAYLOR", "Taylor Ellis", "", "January 2029"),
            _holder(people, "WY-ROBERTS-DAVE", "Dave Roberts", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-HOWE-GORDON-T", "Gordon T. Howe", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
    ]
    schools = [
        office("LCSD #1 Trustee", [
            _holder(people, "WY-PETERNAL-ROBERT-J", "Robert J. Peternal", "", "January 2027"),
            _holder(people, "WY-WALKER-AARIKA", "Aarika Walker", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-DEARDEN-KRISTI", "Kristi Dearden", "", "January 2029"),
            _holder(people, "WY-GRANDY-BRAD", "Brad Grandy", "", "January 2029"),
            _holder(people, "WY-LAMBORN-DON", "Don Lamborn", "", "January 2029"),
            _holder(people, "WY-GUINTA-KIMBERLY", "Kimberly Guinta", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Kimberly Guinta is an official 2026 general winner and takes office January 2027. Aarika Walker continues."),
        office("LCSD #2 Trustee At-Large", [
            _holder(people, "WY-DAY-CONNIE-W", "Connie W. Day", "", "January 2027"),
            _holder(people, "WY-LONG-JAKE", "Jake Long", "", "January 2029"),
            _holder(people, "WY-DRANEY-LANNY-D", "Lanny D. Draney", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Lanny D. Draney is the official 2026 general winner and takes office January 2027."),
        office("LCSD #2 Trustee Area 1", [
            _holder(people, "WY-WILKES-KADE-W", "Kade W. Wilkes", "", "January 2029"),
            _holder(people, "WY-ENGLAND-SPENCER", "Spencer England", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Spencer England is the official 2026 general winner and takes office January 2027."),
        office("LCSD #2 Trustee Area 2", [
            _holder(people, "WY-CALL-LYNN-A", "Lynn A. Call", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("LCSD #2 Trustee Area 3", [
            _holder(people, "WY-JOHNSON-JED", "Jed Johnson", "", "January 2029",
                    notes="Official 2024 Lincoln clerk (official scan): Jed Johnson 3,180."),
        ]),
        office("LCSD #2 Trustee Area 4", [
            _holder(people, "WY-SIMPSON-DARNELL", "Darnell Simpson", "", "January 2029"),
        ]),
        office("LCSD #2 Trustee Area 5", [
            _holder(people, "WY-JENKINS-DAVID", "David Jenkins", "", "January 2027"),
            _holder(people, "WY-ADAMS-PAIGE-W", "Paige W. Adams", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Paige W. Adams is the official 2026 general winner and takes office January 2027."),
        office("Sublette CSD #9 Trustee (Lincoln portion)", [
            _holder(people, "WY-VICKREY-ALAN", "Alan Vickrey", "", "January 2031",
                    notes="Official 2022 Lincoln-portion winner, continuing; official 2026 Lincoln-portion winner, term begins January 2027."),
            _holder(people, "WY-CHEKAN-JOHN", "John Chekan", "", "January 2027"),
            _holder(people, "WY-RAZA-CODY-W", "Cody W. Raza", "", "January 2029"),
            _holder(people, "WY-BANKS-JEREMY", "Jeremy Banks", "", "January 2029"),
            _holder(people, "WY-OTT-HAYDEN", "Hayden Ott", "", "January 2029"),
            _holder(people, "WY-POLK-JESSICA-JOSETTE", "Jessica Josette Polk", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Lincoln clerk winner."),
            _holder(people, "WY-MOCEIKA-TAYLOR", "Taylor Moceika", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 Lincoln clerk two-year winner."),
        ], note="These totals are the official Lincoln County portion of Sublette County School District #9. District-wide school totals were not used."),
    ]
    special = [
        office("South Lincoln Hospital Trustee", [
            _holder(people, "WY-BALL-WILLIAM-W", "William W. Ball", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-YOUNG-CHUCK", "Chuck Young", "", "January 2027"),
            _holder(people, "WY-NELSON-MICHAEL-E", "Michael E. Nelson", "", "January 2027"),
            _holder(people, "WY-POLLARD-MICHELLE", "Michelle Pollard", "", "January 2029"),
            _holder(people, "WY-BOWLING-PAULA", "Paula Bowling", "", "January 2029"),
            _holder(people, "WY-CHAMBERS-RILEY-JO", "Riley Jo Chambers", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-WILBERT-JOSH", "Josh Wilbert", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("North Lincoln Hospital Trustee", [
            _holder(people, "WY-SCHERBEL-MARLOWE-A", "Marlowe A. Scherbel", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-LYMAN-MINDY", "Mindy Lyman", "", "January 2027"),
            _holder(people, "WY-HELM-COLE", "Cole Helm", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-ERICKSON-CLINT", "Clint Erickson", "", "January 2029"),
            _holder(people, "WY-ENGLAND-JEFF", "Jeff England", "", "January 2029"),
            _holder(people, "WY-MERRITT-SHAWN", "Shawn Merritt", "", "January 2029"),
            _holder(people, "WY-HALE-TIM", "Tim Hale", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-HIRSCHI-HEATH", "Heath Hirschi", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Cokeville Hospital Trustee", [
            _holder(people, "WY-PETERSEN-KENNETH", "Kenneth Petersen", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-GROLL-ZANE-T", "Zane T. Groll", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-CARMICHAEL-LOU-ANN", "Lou Ann Carmichael", "", "January 2029"),
            _holder(people, "WY-THOMAS-JULIA", "Julia Thomas", "", "January 2029"),
            _holder(people, "WY-HUNTER-RANDY-S", "Randy S. Hunter", "", "January 2029"),
        ]),
        office("Lincoln Conservation District Rural Supervisor", [
            _holder(people, "WY-ESTERHOLDT-ERICK", "Erick Esterholdt", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-PETERNAL-ROBERT-J", "Robert J. Peternal", "", "January 2029"),
            _holder(people, "WY-PETERSEN-STEWART-LANDON", "Stewart Landon Petersen", "", "January 2029"),
        ]),
        office("Lincoln Conservation District Urban Supervisor", [
            _holder(people, "WY-BOWLING-PAULA", "Paula Bowling", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Lincoln Conservation District At-Large Supervisor", [
            _holder(people, "WY-CLARK-PAUL", "Paul Clark", "", "January 2029"),
        ]),
        office("Star Valley Conservation District At-Large Supervisor", [
            _holder(people, "WY-CROOK-SHANE-R", "Shane Ronald Crook", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Star Valley Conservation District Rural Supervisor", [
            _holder(people, "WY-HELM-COLE", "Cole Helm", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-GARDNER-ROLLIN", "Rollin Gardner", "", "January 2029"),
            _holder(people, "WY-ERICKSON-DANIEL-C", "Daniel C. Erickson", "", "January 2029"),
        ]),
        office("Star Valley Conservation District Urban Supervisor", [
            _holder(people, "WY-JOHNSON-JEFF-L", "Jeff L. Johnson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("South Lincoln Cemetery Director", [
            _holder(people, "WY-HARWOOD-ALLAN", "Allan Harwood", "", "January 2027"),
            _holder(people, "WY-THEK-BILL", "Bill Thek", "", "January 2027"),
            _holder(people, "WY-NEWMAN-WANDA", "Wanda Newman", "", "January 2029"),
            _holder(people, "WY-WELSH-JULIE-FAILONI", "Julie Failoni Welsh", "", "January 2029"),
            _holder(people, "WY-MUIR-MICHELLE", "Michelle Muir", "", "January 2029"),
        ]),
        office("Cokeville Cemetery Director", [
            _holder(people, "WY-THOMPSON-MICHAEL", "Michael Thompson", "", "January 2027"),
            _holder(people, "WY-DAYTON-JANET", "Janet Dayton", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-REED-JOHN", "John Reed", "", "January 2029"),
            _holder(people, "WY-METCALFE-JOHN", "John Metcalfe", "", "January 2029"),
            _holder(people, "WY-THOMSPON-BETTY", "Betty Thomspon", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 certified write-in; official abstract spelling Thomspon."),
            _holder(people, "WY-TOOMER-BRIAN", "Brian Toomer", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-THOMAS-SCOTT", "Scott Thomas", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 certified write-in."),
        ]),
        office("South Lincoln Fire Director", [
            _holder(people, "WY-HALPAIN-DENNIS-J", "Dennis J. Halpain", "", "January 2029"),
            _holder(people, "WY-HARTMAN-RICHARD", "Richard Hartman", "", "January 2029"),
            _holder(people, "WY-HARTMAN-VIRGINIA", "Virginia Hartman", "", "January 2029"),
            _holder(people, "WY-ASHLIMAN-COREY", "Corey Ashliman", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-SMITH-JASON-L", "Jason L. Smith", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-BALDWIN-FRED", "Fred Baldwin", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 certified write-in."),
        ], note="The official 2022 South Lincoln Fire Vote-For-2 contest was write-in only with no certified named winner on the official general, so that class is not filled."),
        office("Upper Valley Fire Director", [
            _holder(people, "WY-ERICKSON-RYAN-J", "Ryan J. Erickson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-VEIGEL-LYNN", "Lynn Veigel", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-MCDONALD-DENNIS", "Dennis McDonald", "", "January 2029"),
        ]),
        office("Mid-Valley Fire Director", [
            _holder(people, "WY-SKINNER-LANCE", "Lance Skinner", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-HALVERSON-MARTI", "Marti Halverson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-VOYLES-KEVIN", "Kevin Voyles", "", "January 2029"),
        ]),
        office("Alpine Fire Director", [
            _holder(people, "WY-CAMERON-MARK-D", "Mark D. Cameron", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner, two-year term."),
            _holder(people, "WY-JORGENSEN-JOHN", "John Jorgensen", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-CLAUSON-BOBBI", "Bobbi Clauson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Bear River Fire Director", [
            _holder(people, "WY-WALKER-KEVIN-D", "Kevin D. Walker", "", "January 2027"),
            _holder(people, "WY-PROWS-DOUGLAS-A", "Douglas A. Prows", "", "January 2027"),
            _holder(people, "WY-FORREST-LYLE", "Lyle Forrest", "", "January 2029"),
            _holder(people, "WY-LUTHI-KAYDELL", "Kaydell Luthi", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 certified write-in, two-year unexpired."),
            _holder(people, "WY-CHADWICK-CRAIG", "Craig Chadwick", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-DURAN-MICHAEL-L", "Michael L. Duran", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Kemmerer Senior Citizens District Trustee", [
            _holder(people, "WY-KILLIAN-CHRISTY", "Christy Killian", "", "January 2027"),
            _holder(people, "WY-SARGENT-DENISE", "Denise Sargent", "", "January 2027"),
            _holder(people, "WY-CARTWRIGHT-TERRI", "Terri Cartwright", "", "January 2029"),
            _holder(people, "WY-MILLER-CINDY-H", "Cindy H. Miller", "", "January 2029"),
        ]),
    ]
    judicial = [
        office("District Judge, 3rd Judicial District", [
            _holder(people, "WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "", "January 2029",
                    notes="Official Wyoming Judicial Branch Lincoln 3rd JD district page: appointed January 2015, retained November 2022, term expires January 2029."),
            _holder(people, "WY-KASTE-JAMES-C", "James C. Kaste", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Uinta 3rd JD district page: appointed October 2022, retained November 2024, term expires January 2031. Official 2024 clerk DIST CT - KASTE."),
            _holder(people, "WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Sweetwater 3rd JD district page: appointed October 2019; official 2026 Lincoln clerk JUDGE C DIST CT JUDGE ROBINSON, YES, continuing January 2027–2031."),
        ]),
        office("Circuit Judge, 3rd Judicial District", [
            _holder(people, "WY-JONES-CRAIG-L", "Craig L. Jones", "", "January 2027",
                    notes="Official 2022 Lincoln clerk CIRCUIT CT - JONES, YES, filled as Craig L. Jones from official SOS."),
            _holder(people, "WY-PROKOS-JOHN-R", "John R. Prokos", "", "January 2031",
                    notes="Official 2022 term; official 2026 Lincoln clerk RETAIN CIRCUIT COURT JUDGE PROKOS, YES, continuing January 2027–2031."),
            _holder(people, "WY-GREER-MICHAEL-L", "Michael L. Greer", "", "January 2029",
                    notes="Official 2024 Lincoln clerk CIRCUIT CT - GREER, YES, filled as Michael L. Greer."),
            _holder(people, "WY-CORPENING-GREGORY-S", "Gregory S. Corpening", "", "January 2029",
                    notes="Official 2024 Lincoln clerk CIRCUIT CT - CORPENING, YES, filled as Gregory S. Corpening."),
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
    src["general_results"] = f"{BASE}/2026/OFFICIAL%20SUMMARY%202026%20GEN.pdf"
    src["primary_results"] = f"{BASE}/2026/Primary/OFFICIAL%20SUMMARY%202026%20PRIMARY.pdf"
    src["checked"] = RETRIEVED
    data["sources"] = src
    apply_to_groups(data["groups"], 'lincoln')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")

def wi():
    return {
        "label": "Lincoln County official 2026 general certified write-ins (Lincoln County Canvassing Board, November 5, 2026)",
        "url": f"{BASE}/2026/2026%20GENERAL%20CERTIFIED%20WRITE-INS.pdf",
    }


def register_more_people(P):
    rows = [
        ("WY-CLARK-CASEY", "Casey Clark", "Casey", "Clark"),
        ("WY-SAWAYA-ROBERT", "Robert Sawaya", "Robert", "Sawaya"),
        ("WY-HOUSLEY-DIANE", "Diane Housley", "Diane", "Housley"),
        ("WY-PETERSEN-NICOLE", "Nicole Petersen", "Nicole", "Petersen"),
        ("WY-SLOAN-SHERROL", "Sherrol Sloan", "Sherrol", "Sloan"),
        ("WY-SCHAECHTERLE-KATHY", "Kathy Schaechterle", "Kathy", "Schaechterle"),
        ("WY-BEEHLER-MICHALE", "Michale Beehler", "Michale", "Beehler"),
        ("WY-BIENZ-ELLIE", "Ellie Bienz", "Ellie", "Bienz"),
        ("WY-RITZDORF-MAXINE-R", "Maxine R. Ritzdorf", "Maxine", "Ritzdorf", "R."),
        ("WY-PALANO-STEPHEN", "Stephen Palano", "Stephen", "Palano"),
        ("WY-WHITEFORD-DANIEL-SR", "Daniel Whiteford Sr.", "Daniel", "Whiteford"),
        ("WY-BRANDT-JENNIFER", "Jennifer Brandt", "Jennifer", "Brandt"),
        ("WY-MARQUARDT-RICK", "Rick Marquardt", "Rick", "Marquardt"),
        ("WY-HEADRICK-ROWDY-L", "Rowdy L. Headrick", "Rowdy", "Headrick", "L."),
        ("WY-VILOS-JAKE-J", "Jake J. Vilos", "Jake", "Vilos", "J."),
        ("WY-HOWARD-SCOTT", "Scott Howard", "Scott", "Howard"),
        ("WY-BROWN-BROCK", "Brock Brown", "Brock", "Brown"),
        ("WY-WILKES-WILLIAM", "William Wilkes", "William", "Wilkes"),
        ("WY-HILLYARD-DIRK", "Dirk Hillyard", "Dirk", "Hillyard"),
        ("WY-BUTLER-MICHAEL-F", "Michael F. Butler", "Michael", "Butler", "F."),
        ("WY-GRIFFITH-SCOTT-E", "Scott E. Griffith", "Scott", "Griffith", "E."),
        ("WY-DAY-JUSTIN", "Justin Day", "Justin", "Day"),
        ("WY-HUNT-LYNN", "Lynn Hunt", "Lynn", "Hunt"),
        ("WY-WIERDA-AMY", "Amy Wierda", "Amy", "Wierda"),
        ("WY-HARRIS-KEN", "Ken Harris", "Ken", "Harris"),
        ("WY-SCAFFIDE-SHAY", "Shay Scaffide", "Shay", "Scaffide"),
        ("WY-BURCHARD-ANDREA", "Andrea Burchard", "Andrea", "Burchard"),
        ("WY-CASTILLO-EMILY", "Emily Castillo", "Emily", "Castillo"),
        ("WY-PASSEY-TANNER", "Tanner Passey", "Tanner", "Passey"),
        ("WY-VISSER-JUSTIN-C", "Justin C. Visser", "Justin", "Visser", "C."),
        ("WY-VEIGEL-SPENCER", "Spencer Veigel", "Spencer", "Veigel"),
        ("WY-DENIZ-MALINDA-JAN", "Malinda Jan DeNiz", "Malinda", "DeNiz", "", "Malinda Jan DeNiz"),
        ("WY-PASSEY-NIKOLE", "Nikole Passey", "Nikole", "Passey"),
        ("WY-ALLRED-MICHAEL", "Michael Allred", "Michael", "Allred"),
        ("WY-HEWARD-JOE", "Joe Heward", "Joe", "Heward"),
        ("WY-FISCUS-SUSAN", "Susan Fiscus", "Susan", "Fiscus"),
        ("WY-BIRD-CAMERON-JOHN", "Cameron John Bird", "Cameron", "Bird", "", "Cameron Bird"),
        ("WY-NATE-BRAD-SHANE", "Brad Shane Nate", "Brad", "Nate", "", "Bradley S. Nate"),
        ("WY-DAYTON-CHARLES", "Charles Dayton", "Charles", "Dayton"),
        ("WY-LEWIS-THERESA", "Theresa Lewis", "Theresa", "Lewis"),
        ("WY-HARMON-WAYNE", "Wayne Harmon", "Wayne", "Harmon"),
        ("WY-ROBERTS-DAVE", "Dave Roberts", "Dave", "Roberts"),
        ("WY-HOWE-GORDON-T", "Gordon T. Howe", "Gordon", "Howe", "T.", "Gordon T Howe"),
        ("WY-TOOLSON-KATIE", "Katie Toolson", "Katie", "Toolson"),
        ("WY-ELLIS-TAYLOR", "Taylor Ellis", "Taylor", "Ellis"),
        ("WY-HANSEN-LEE-R", "Lee R. Hansen", "Lee", "Hansen", "R."),
        ("WY-MERRILL-KIRSTEN", "Kirsten Merrill", "Kirsten", "Merrill"),
        ("WY-VICKREY-ALAN", "Alan Vickrey", "Alan", "Vickrey"),
        ("WY-POLK-JESSICA-JOSETTE", "Jessica Josette Polk", "Jessica", "Polk"),
        ("WY-CHEKAN-JOHN", "John Chekan", "John", "Chekan"),
        ("WY-MOCEIKA-TAYLOR", "Taylor Moceika", "Taylor", "Moceika"),
        ("WY-RAZA-CODY-W", "Cody W. Raza", "Cody", "Raza", "W.", "Cody W Raza"),
        ("WY-BANKS-JEREMY", "Jeremy Banks", "Jeremy", "Banks"),
        ("WY-OTT-HAYDEN", "Hayden Ott", "Hayden", "Ott"),
        ("WY-BALL-WILLIAM-W", "William W. Ball", "William", "Ball", "W."),
        ("WY-YOUNG-CHUCK", "Chuck Young", "Chuck", "Young"),
        ("WY-NELSON-MICHAEL-E", "Michael E. Nelson", "Michael", "Nelson", "E."),
        ("WY-CHAMBERS-RILEY-JO", "Riley Jo Chambers", "Riley", "Chambers"),
        ("WY-WILBERT-JOSH", "Josh Wilbert", "Josh", "Wilbert"),
        ("WY-POLLARD-MICHELLE", "Michelle Pollard", "Michelle", "Pollard"),
        ("WY-BOWLING-PAULA", "Paula Bowling", "Paula", "Bowling"),
        ("WY-SCHERBEL-MARLOWE-A", "Marlowe A. Scherbel", "Marlowe", "Scherbel", "A."),
        ("WY-LYMAN-MINDY", "Mindy Lyman", "Mindy", "Lyman"),
        ("WY-HELM-COLE", "Cole Helm", "Cole", "Helm"),
        ("WY-HALE-TIM", "Tim Hale", "Tim", "Hale"),
        ("WY-HIRSCHI-HEATH", "Heath Hirschi", "Heath", "Hirschi"),
        ("WY-ERICKSON-CLINT", "Clint Erickson", "Clint", "Erickson"),
        ("WY-ENGLAND-JEFF", "Jeff England", "Jeff", "England"),
        ("WY-MERRITT-SHAWN", "Shawn Merritt", "Shawn", "Merritt"),
        ("WY-GROLL-ZANE-T", "Zane T. Groll", "Zane", "Groll", "T.", "Zane Groll"),
        ("WY-PETERSEN-KENNETH", "Kenneth Petersen", "Kenneth", "Petersen", "", "Kenny Petersen"),
        ("WY-CARMICHAEL-LOU-ANN", "Lou Ann Carmichael", "Lou Ann", "Carmichael"),
        ("WY-THOMAS-JULIA", "Julia Thomas", "Julia", "Thomas"),
        ("WY-HUNTER-RANDY-S", "Randy S. Hunter", "Randy", "Hunter", "S."),
        ("WY-ESTERHOLDT-ERICK", "Erick Esterholdt", "Erick", "Esterholdt"),
        ("WY-PETERSEN-STEWART-LANDON", "Stewart Landon Petersen", "Stewart", "Petersen"),
        ("WY-CLARK-PAUL", "Paul Clark", "Paul", "Clark"),
        ("WY-CROOK-SHANE-R", "Shane Ronald Crook", "Shane", "Crook", "", "Shane R. Crook; Shane Ronald Crook"),
        ("WY-LUTHI-BRYAN-TY", "Bryan Ty Luthi", "Bryan", "Luthi"),
        ("WY-ERICKSON-DANIEL-C", "Daniel C. Erickson", "Daniel", "Erickson", "C."),
        ("WY-GARDNER-ROLLIN", "Rollin Gardner", "Rollin", "Gardner"),
        ("WY-JOHNSON-JEFF-L", "Jeff L. Johnson", "Jeff", "Johnson", "L.", "Jeff Johnson"),
        ("WY-DAYTON-JANET", "Janet Dayton", "Janet", "Dayton"),
        ("WY-TOOMER-BRIAN", "Brian Toomer", "Brian", "Toomer"),
        ("WY-THOMAS-SCOTT", "Scott Thomas", "Scott", "Thomas"),
        ("WY-THOMSPON-BETTY", "Betty Thomspon", "Betty", "Thomspon"),
        ("WY-THOMPSON-MICHAEL", "Michael Thompson", "Michael", "Thompson"),
        ("WY-HARMON-KALBIE", "Kalbie Harmon", "Kalbie", "Harmon"),
        ("WY-WELSH-JULIE-FAILONI", "Julie Failoni Welsh", "Julie", "Welsh"),
        ("WY-HARWOOD-ALLAN", "Allan Harwood", "Allan", "Harwood"),
        ("WY-THEK-BILL", "Bill Thek", "Bill", "Thek"),
        ("WY-NEWMAN-WANDA", "Wanda Newman", "Wanda", "Newman"),
        ("WY-MUIR-MICHELLE", "Michelle Muir", "Michelle", "Muir"),
        ("WY-REED-JOHN", "John Reed", "John", "Reed"),
        ("WY-METCALFE-JOHN", "John Metcalfe", "John", "Metcalfe"),
        ("WY-ASHLIMAN-COREY", "Corey Ashliman", "Corey", "Ashliman"),
        ("WY-SMITH-JASON-L", "Jason L. Smith", "Jason", "Smith", "L.", "Jason L Smith"),
        ("WY-BALDWIN-FRED", "Fred Baldwin", "Fred", "Baldwin"),
        ("WY-HALPAIN-DENNIS-J", "Dennis J. Halpain", "Dennis", "Halpain", "J."),
        ("WY-HARTMAN-RICHARD", "Richard Hartman", "Richard", "Hartman"),
        ("WY-HARTMAN-VIRGINIA", "Virginia Hartman", "Virginia", "Hartman"),
        ("WY-ERICKSON-RYAN-J", "Ryan J. Erickson", "Ryan", "Erickson", "J."),
        ("WY-VEIGEL-LYNN", "Lynn Veigel", "Lynn", "Veigel"),
        ("WY-MCDONALD-DENNIS", "Dennis McDonald", "Dennis", "McDonald"),
        ("WY-SKINNER-LANCE", "Lance Skinner", "Lance", "Skinner"),
        ("WY-VOYLES-KEVIN", "Kevin Voyles", "Kevin", "Voyles"),
        ("WY-CAMERON-MARK-D", "Mark D. Cameron", "Mark", "Cameron", "D."),
        ("WY-CLAUSON-BOBBI", "Bobbi Clauson", "Bobbi", "Clauson"),
        ("WY-JORGENSEN-JOHN", "John Jorgensen", "John", "Jorgensen"),
        ("WY-CHADWICK-CRAIG", "Craig Chadwick", "Craig", "Chadwick"),
        ("WY-DURAN-MICHAEL-L", "Michael L. Duran", "Michael", "Duran", "L."),
        ("WY-LUTHI-KAYDELL", "Kaydell Luthi", "Kaydell", "Luthi"),
        ("WY-PROWS-DOUGLAS-A", "Douglas A. Prows", "Douglas", "Prows", "A.", "Douglas Prows"),
        ("WY-WALKER-KEVIN-D", "Kevin D. Walker", "Kevin", "Walker", "D."),
        ("WY-FORREST-LYLE", "Lyle Forrest", "Lyle", "Forrest"),
        ("WY-KILLIAN-CHRISTY", "Christy Killian", "Christy", "Killian"),
        ("WY-SARGENT-DENISE", "Denise Sargent", "Denise", "Sargent"),
        ("WY-CARTWRIGHT-TERRI", "Terri Cartwright", "Terri", "Cartwright"),
        ("WY-MILLER-CINDY-H", "Cindy H. Miller", "Cindy", "Miller", "H."),
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)


def council_and_special_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, notes="", sources=None, how="elected"):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a], term_end=FM[b],
            how_took_office=how, election_year=ey, confidence="high",
            sources=sources or [pg(ey)],
            notes=notes,
        ))

    n = "Official Lincoln clerk."
    # ---- Councils (official November clerk ballots) ----
    # Kemmerer (3 seats each even year, 4-year terms)
    add("WY-BATISTA-MARLIN", "Marlin Batista", "municipal", "Kemmerer Council", "City of Kemmerer", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-3: Marlin Batista 710, Robert Bowen 594, Mark Quinn 553.")
    add("WY-BOWEN-ROBERT", "Robert Bowen", "municipal", "Kemmerer Council", "City of Kemmerer", 2023, 2027, 2022, "Official 2022 Lincoln clerk. Robert Bowen later is the official 2024 Kemmerer mayor.")
    add("WY-QUINN-MARK", "Mark Quinn", "municipal", "Kemmerer Council", "City of Kemmerer", 2023, 2027, 2022)
    add("WY-PRICE-BILL", "Bill Price", "municipal", "Kemmerer Council", "City of Kemmerer", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Bill Price 695, David McConkie 648, Brantley Popp 638.")
    add("WY-MCCONKIE-DAVID", "David McConkie", "municipal", "Kemmerer Council", "City of Kemmerer", 2025, 2029, 2024)
    add("WY-POPP-BRANTLEY", "Brantley Popp", "municipal", "Kemmerer Council", "City of Kemmerer", 2025, 2029, 2024)
    add("WY-PEAVLER-BARBARA", "Barbara Peavler", "municipal", "Kemmerer Council", "City of Kemmerer", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-3: Barbara Peavler 486, Ken Spears 474, Michael L. Archibald 454.")
    add("WY-SPEARS-KEN", "Ken Spears", "municipal", "Kemmerer Council", "City of Kemmerer", 2027, 2031, 2026)
    add("WY-ARCHIBALD-MICHAEL-L", "Michael L. Archibald", "municipal", "Kemmerer Council", "City of Kemmerer", 2027, 2031, 2026)

    add("WY-BACKMAN-ERIC", "Eric Backman", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Eric Backman 156, Sherrol Sloan 141.")
    add("WY-SLOAN-SHERROL", "Sherrol Sloan", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2023, 2027, 2022)
    add("WY-PETERSEN-NICOLE", "Nicole Petersen", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Robert Sawaya 217, Nicole Petersen 201.")
    add("WY-SAWAYA-ROBERT", "Robert Sawaya", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2025, 2029, 2024)
    add("WY-CLARK-CASEY", "Casey Clark", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Casey Clark 180.")
    add("WY-SAWAYA-ROBERT", "Robert Sawaya", "municipal", "Diamondville Council (4-year)", "Town of Diamondville", 2027, 2031, 2026,
        "Official 2026 certified write-in: Robert Sawaya (3 write-in votes), Lincoln County Canvassing Board, November 5, 2026.",
        sources=[pg(2026), wi()], how="elected")
    add("WY-HOUSLEY-DIANE", "Diane Housley", "municipal", "Diamondville Council (2-year)", "Town of Diamondville", 2027, 2029, 2026, "Official 2026 Lincoln clerk: Diane Housley 166.")

    add("WY-BEEHLER-MICHALE", "Michale Beehler", "municipal", "Opal Council (4-year)", "Town of Opal", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Maxine R. Ritzdorf 19, Michale Beehler 18. Official spelling Michale.")
    add("WY-RITZDORF-MAXINE-R", "Maxine R. Ritzdorf", "municipal", "Opal Council (4-year)", "Town of Opal", 2023, 2027, 2022)
    add("WY-HALL-MARY-O", "Mary O. Hall", "municipal", "Opal Council (2-year)", "Town of Opal", 2023, 2025, 2022, "Official 2022 Lincoln clerk: Mary O. Hall 22, Stephen Palano 14.")
    add("WY-PALANO-STEPHEN", "Stephen Palano", "municipal", "Opal Council (4-year)", "Town of Opal", 2025, 2029, 2024, "Official 2024 Lincoln clerk certified write-ins, Vote-For-2: Stephen Palano 19, Daniel Whiteford Sr. 17 (Mary O. Hall 16 was third).")
    add("WY-WHITEFORD-DANIEL-SR", "Daniel Whiteford Sr.", "municipal", "Opal Council (4-year)", "Town of Opal", 2025, 2029, 2024)
    add("WY-BEEHLER-MICHALE", "Michale Beehler", "municipal", "Opal Council (4-year)", "Town of Opal", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Michale Beehler 27, Ellie Bienz 26.")
    add("WY-BIENZ-ELLIE", "Ellie Bienz", "municipal", "Opal Council (4-year)", "Town of Opal", 2027, 2031, 2026)

    add("WY-HINSON-RALPH", "Ralph Hinson", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Ralph Hinson 79, Scott Howard 68.")
    add("WY-HOWARD-SCOTT", "Scott Howard", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2023, 2027, 2022)
    add("WY-HEADRICK-ROWDY-L", "Rowdy L. Headrick", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Rowdy L. Headrick 92, Jake J. Vilos 78.")
    add("WY-VILOS-JAKE-J", "Jake J. Vilos", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2025, 2029, 2024)
    add("WY-BRANDT-JENNIFER", "Jennifer Brandt", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Jennifer Brandt 98, Rick Marquardt 74.")
    add("WY-MARQUARDT-RICK", "Rick Marquardt", "municipal", "LaBarge Council (4-year)", "Town of LaBarge", 2027, 2031, 2026)

    add("WY-HILLYARD-DIRK", "Dirk Hillyard", "municipal", "Afton Council (4-year)", "Town of Afton", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Dirk Hillyard 519, William Wilkes 280.")
    add("WY-WILKES-WILLIAM", "William Wilkes", "municipal", "Afton Council (4-year)", "Town of Afton", 2023, 2027, 2022)
    add("WY-BUTLER-MICHAEL-F", "Michael F. Butler", "municipal", "Afton Council (2-year)", "Town of Afton", 2023, 2025, 2022, "Official 2022 Lincoln clerk: Michael F. Butler 360, Lynn Hunt 249.")
    add("WY-BUTLER-MICHAEL-F", "Michael F. Butler", "municipal", "Afton Council (4-year)", "Town of Afton", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Michael F. Butler 692, Scott E. Griffith 642.")
    add("WY-GRIFFITH-SCOTT-E", "Scott E. Griffith", "municipal", "Afton Council (4-year)", "Town of Afton", 2025, 2029, 2024)
    add("WY-BROWN-BROCK", "Brock Brown", "municipal", "Afton Council (4-year)", "Town of Afton", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Brock Brown 404, William Wilkes 386.")
    add("WY-WILKES-WILLIAM", "William Wilkes", "municipal", "Afton Council (4-year)", "Town of Afton", 2027, 2031, 2026)
    add("WY-HILLYARD-DIRK", "Dirk Hillyard", "municipal", "Afton Council (2-year)", "Town of Afton", 2027, 2029, 2026, "Official 2026 Lincoln clerk: Dirk Hillyard 491, Lynk Nield 119.")

    add("WY-CASTILLO-EMILY", "Emily Castillo", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Emily Castillo 242, Jeremy Larsen 207.")
    add("WY-LARSEN-JEREMY", "Jeremy Larsen", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2023, 2027, 2022)
    add("WY-SCAFFIDE-SHAY", "Shay Scaffide", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2025, 2029, 2024, "Official 2024 Lincoln clerk (official scan) Vote-For-2: Shay Scaffide 284, Andrea Burchard 275.")
    add("WY-BURCHARD-ANDREA", "Andrea Burchard", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2025, 2029, 2024)
    add("WY-WIERDA-AMY", "Amy Wierda", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Amy Wierda 223, Ken Harris 209.")
    add("WY-HARRIS-KEN", "Ken Harris", "municipal", "Alpine Council (4-year)", "Town of Alpine", 2027, 2031, 2026)

    add("WY-HEWARD-JOE", "Joe Heward", "municipal", "Thayne Council (4-year)", "Town of Thayne", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2 lists Joe Heward 86 as the only named candidate. The second seat is not filled from a named or certified winner on that official general.")
    add("WY-PASSEY-NIKOLE", "Nikole Passey", "municipal", "Thayne Council (4-year)", "Town of Thayne", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Nikole Passey 152 plus official certified write-in Michael Allred 4.")
    add("WY-ALLRED-MICHAEL", "Michael Allred", "municipal", "Thayne Council (4-year)", "Town of Thayne", 2025, 2029, 2024)
    add("WY-PASSEY-TANNER", "Tanner Passey", "municipal", "Thayne Council (4-year)", "Town of Thayne", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Tanner Passey 70, Justin C. Visser 69.")
    add("WY-VISSER-JUSTIN-C", "Justin C. Visser", "municipal", "Thayne Council (4-year)", "Town of Thayne", 2027, 2031, 2026)
    add("WY-VEIGEL-SPENCER", "Spencer Veigel", "municipal", "Thayne Council (2-year)", "Town of Thayne", 2027, 2029, 2026, "Official 2026 Lincoln clerk: Spencer Veigel 84.")
    add("WY-DENIZ-MALINDA-JAN", "Malinda Jan DeNiz", "municipal", "Thayne Council (2-year unexpired)", "Town of Thayne", 2027, 2029, 2026,
        "Official 2026 certified write-in, 2-year unexpired: Malinda Jan DeNiz (4 write-in votes), Lincoln County Canvassing Board, November 5, 2026.",
        sources=[pg(2026), wi()])

    add("WY-LEWIS-THERESA", "Theresa Lewis", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Theresa Lewis 103, Wayne Harmon 95.")
    add("WY-HARMON-WAYNE", "Wayne Harmon", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2023, 2027, 2022)
    add("WY-NATE-BRAD-SHANE", "Brad Shane Nate", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Brad Shane Nate 150, Charles Dayton 137.")
    add("WY-DAYTON-CHARLES", "Charles Dayton", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2025, 2029, 2024)
    add("WY-FISCUS-SUSAN", "Susan Fiscus", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Susan Fiscus 142, Cameron John Bird 133.")
    add("WY-BIRD-CAMERON-JOHN", "Cameron John Bird", "municipal", "Cokeville Council (4-year)", "Town of Cokeville", 2027, 2031, 2026)

    add("WY-MERRILL-KIRSTEN", "Kirsten Merrill", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Kirsten Merrill 494, Ruzena Rok 468.")
    add("WY-ROK-RUZENA", "Ruzena Rok", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2023, 2027, 2022)
    add("WY-TOOLSON-KATIE", "Katie Toolson", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Katie Toolson 534, Taylor Ellis 471.")
    add("WY-ELLIS-TAYLOR", "Taylor Ellis", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2025, 2029, 2024)
    add("WY-ROBERTS-DAVE", "Dave Roberts", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Dave Roberts 404, Gordon T. Howe 359.")
    add("WY-HOWE-GORDON-T", "Gordon T. Howe", "municipal", "Star Valley Ranch Council (4-year)", "Town of Star Valley Ranch", 2027, 2031, 2026)

    # Schools: Sublette CSD #9 appears on official Lincoln ballots (Lincoln portion only; district-wide school totals are not invented).
    s9 = "Official Lincoln clerk totals are the Lincoln County portion of Sublette County School District #9. District-wide school totals were not used."
    add("WY-VICKREY-ALAN", "Alan Vickrey", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Alan Vickrey 219, John Chekan 88. " + s9)
    add("WY-CHEKAN-JOHN", "John Chekan", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2023, 2027, 2022, s9)
    add("WY-RAZA-CODY-W", "Cody W. Raza", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Cody W. Raza 202, Jeremy Banks 162, Hayden Ott 120. " + s9)
    add("WY-BANKS-JEREMY", "Jeremy Banks", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2025, 2029, 2024, s9)
    add("WY-OTT-HAYDEN", "Hayden Ott", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2025, 2029, 2024, s9)
    add("WY-VICKREY-ALAN", "Alan Vickrey", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Alan Vickrey 181, Jessica Josette Polk 99. " + s9)
    add("WY-POLK-JESSICA-JOSETTE", "Jessica Josette Polk", "schools", "Sublette CSD #9 Trustee (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2027, 2031, 2026, s9)
    add("WY-MOCEIKA-TAYLOR", "Taylor Moceika", "schools", "Sublette CSD #9 Trustee 2-year (Lincoln portion)", "Sublette County School District #9 (Lincoln portion)", 2027, 2029, 2026, "Official 2026 Lincoln clerk: Taylor Moceika 128, Brock Forrest McLain 92. " + s9)

    # Hospitals
    add("WY-BALL-WILLIAM-W", "William W. Ball", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-3: William W. Ball 1,202, Chuck Young 1,044, Michael E. Nelson 1,012.")
    add("WY-YOUNG-CHUCK", "Chuck Young", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2023, 2027, 2022)
    add("WY-NELSON-MICHAEL-E", "Michael E. Nelson", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2023, 2027, 2022)
    add("WY-POLLARD-MICHELLE", "Michelle Pollard", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Michelle Pollard 1,480, Paula Bowling 1,430.")
    add("WY-BOWLING-PAULA", "Paula Bowling", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2025, 2029, 2024)
    add("WY-BALL-WILLIAM-W", "William W. Ball", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-3: William W. Ball 1,163, Riley Jo Chambers 885, Josh Wilbert 861.")
    add("WY-CHAMBERS-RILEY-JO", "Riley Jo Chambers", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2027, 2031, 2026)
    add("WY-WILBERT-JOSH", "Josh Wilbert", "special-districts", "South Lincoln Hospital Trustee", "South Lincoln Hospital District", 2027, 2031, 2026)

    add("WY-SCHERBEL-MARLOWE-A", "Marlowe A. Scherbel", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-4: Marlowe A. Scherbel 3,190, Mindy Lyman 3,178, Cole Helm 3,004. The official general lists 543 write-in votes with no certified named fourth winner, so the fourth seat is not filled here.")
    add("WY-LYMAN-MINDY", "Mindy Lyman", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2023, 2027, 2022)
    add("WY-HELM-COLE", "Cole Helm", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2023, 2027, 2022)
    add("WY-ERICKSON-CLINT", "Clint Erickson", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Clint Erickson 3,346, Jeff England 2,783, Shawn Merritt 2,746.")
    add("WY-ENGLAND-JEFF", "Jeff England", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2025, 2029, 2024)
    add("WY-MERRITT-SHAWN", "Shawn Merritt", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2025, 2029, 2024)
    add("WY-HALE-TIM", "Tim Hale", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-4: Tim Hale 3,161, Heath Hirschi 2,939, Cole Helm 2,856, Marlowe A. Scherbel 2,810.")
    add("WY-HIRSCHI-HEATH", "Heath Hirschi", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2027, 2031, 2026)
    add("WY-HELM-COLE", "Cole Helm", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2027, 2031, 2026)
    add("WY-SCHERBEL-MARLOWE-A", "Marlowe A. Scherbel", "special-districts", "North Lincoln Hospital Trustee", "North Lincoln Hospital District", 2027, 2031, 2026)

    add("WY-PETERSEN-KENNETH", "Kenneth Petersen", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Kenny Petersen 286, Zane Groll 279.")
    add("WY-GROLL-ZANE-T", "Zane T. Groll", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2023, 2027, 2022)
    add("WY-CARMICHAEL-LOU-ANN", "Lou Ann Carmichael", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Lou Ann Carmichael 302, Julia Thomas 272, Randy S. Hunter 209.")
    add("WY-THOMAS-JULIA", "Julia Thomas", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2025, 2029, 2024)
    add("WY-HUNTER-RANDY-S", "Randy S. Hunter", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2025, 2029, 2024)
    add("WY-GROLL-ZANE-T", "Zane T. Groll", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Zane T. Groll 252, Kenneth Petersen 237.")
    add("WY-PETERSEN-KENNETH", "Kenneth Petersen", "special-districts", "Cokeville Hospital Trustee", "Cokeville Hospital District", 2027, 2031, 2026)

    # Conservation
    add("WY-ESTERHOLDT-ERICK", "Erick Esterholdt", "special-districts", "Lincoln Conservation District Rural Supervisor", "Lincoln Conservation District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Erick Esterholdt 1,550.")
    add("WY-BOWLING-PAULA", "Paula Bowling", "special-districts", "Lincoln Conservation District Urban Supervisor", "Lincoln Conservation District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Paula Bowling 1,598.")
    add("WY-PETERNAL-ROBERT-J", "Robert J. Peternal", "special-districts", "Lincoln Conservation District Rural Supervisor", "Lincoln Conservation District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Robert J. Peternal 1,845, Stewart Landon Petersen 1,593.")
    add("WY-PETERSEN-STEWART-LANDON", "Stewart Landon Petersen", "special-districts", "Lincoln Conservation District Rural Supervisor", "Lincoln Conservation District", 2025, 2029, 2024)
    add("WY-CLARK-PAUL", "Paul Clark", "special-districts", "Lincoln Conservation District At-Large Supervisor", "Lincoln Conservation District", 2025, 2029, 2024, "Official 2024 Lincoln clerk: Paul Clark 1,938.")
    add("WY-ESTERHOLDT-ERICK", "Erick Esterholdt", "special-districts", "Lincoln Conservation District Rural Supervisor", "Lincoln Conservation District", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Erick Esterholdt 1,477.")
    add("WY-BOWLING-PAULA", "Paula Bowling", "special-districts", "Lincoln Conservation District Urban Supervisor", "Lincoln Conservation District", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Paula Bowling 1,519.")
    add("WY-CROOK-SHANE-R", "Shane R. Crook", "special-districts", "Star Valley Conservation District At-Large Supervisor", "Star Valley Conservation District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Shane R. Crook 4,407.")
    add("WY-HELM-COLE", "Cole Helm", "special-districts", "Star Valley Conservation District Rural Supervisor", "Star Valley Conservation District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Cole Helm 4,344.")
    add("WY-JOHNSON-JEFF-L", "Jeff L. Johnson", "special-districts", "Star Valley Conservation District Urban Supervisor", "Star Valley Conservation District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Jeff L. Johnson 4,249.")
    add("WY-GARDNER-ROLLIN", "Rollin Gardner", "special-districts", "Star Valley Conservation District Rural Supervisor", "Star Valley Conservation District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Rollin Gardner 4,850, Daniel C. Erickson 4,385.")
    add("WY-ERICKSON-DANIEL-C", "Daniel C. Erickson", "special-districts", "Star Valley Conservation District Rural Supervisor", "Star Valley Conservation District", 2025, 2029, 2024)
    add("WY-CROOK-SHANE-R", "Shane Ronald Crook", "special-districts", "Star Valley Conservation District At-Large Supervisor", "Star Valley Conservation District", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Shane Ronald Crook 4,162.")
    add("WY-HELM-COLE", "Cole Helm", "special-districts", "Star Valley Conservation District Rural Supervisor", "Star Valley Conservation District", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Cole Helm 2,827, Bryan Ty Luthi 1,326.")
    add("WY-JOHNSON-JEFF-L", "Jeff Johnson", "special-districts", "Star Valley Conservation District Urban Supervisor", "Star Valley Conservation District", 2027, 2031, 2026, "Official 2026 Lincoln clerk: Jeff Johnson 4,052.")

    # Cemetery, fire, senior
    add("WY-WELSH-JULIE-FAILONI", "Julie Failoni Welsh", "special-districts", "South Lincoln Cemetery Director (2-year)", "South Lincoln Cemetery District", 2023, 2025, 2022, "Official 2022 Lincoln clerk: Julie Failoni Welsh 1,357.")
    add("WY-HARWOOD-ALLAN", "Allan Harwood", "special-districts", "South Lincoln Cemetery Director (4-year)", "South Lincoln Cemetery District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Allan Harwood 1,192, Bill Thek 1,091.")
    add("WY-THEK-BILL", "Bill Thek", "special-districts", "South Lincoln Cemetery Director (4-year)", "South Lincoln Cemetery District", 2023, 2027, 2022)
    add("WY-NEWMAN-WANDA", "Wanda Newman", "special-districts", "South Lincoln Cemetery Director (4-year)", "South Lincoln Cemetery District", 2025, 2029, 2024, "Official 2024 Lincoln clerk certified write-in, Vote-For-1: Wanda Newman 30.")
    add("WY-WELSH-JULIE-FAILONI", "Julie Failoni Welsh", "special-districts", "South Lincoln Cemetery Director (2-year)", "South Lincoln Cemetery District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Julie Failoni Welsh 1,639 plus official certified write-ins Wanda Newman 14 and Michelle Muir 11. The official 2024 clerk heading prints a 2-year contest; the three official named/certified winners are encoded here.")
    add("WY-NEWMAN-WANDA", "Wanda Newman", "special-districts", "South Lincoln Cemetery Director (2-year)", "South Lincoln Cemetery District", 2025, 2029, 2024)
    add("WY-MUIR-MICHELLE", "Michelle Muir", "special-districts", "South Lincoln Cemetery Director (2-year)", "South Lincoln Cemetery District", 2025, 2029, 2024)

    add("WY-HARMON-KALBIE", "Kalbie Harmon", "special-districts", "Cokeville Cemetery Director (2-year)", "Cokeville Cemetery District", 2023, 2025, 2022, "Official 2022 Lincoln clerk: Kalbie Harmon 302.")
    add("WY-THOMPSON-MICHAEL", "Michael Thompson", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-3: Michael Thompson 283, Janet Dayton 278. No certified named third winner on the official general.")
    add("WY-DAYTON-JANET", "Janet Dayton", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2023, 2027, 2022)
    add("WY-REED-JOHN", "John Reed", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: John Reed 386 plus official certified write-in John Metcalfe 4. No additional certified named winner was printed.")
    add("WY-METCALFE-JOHN", "John Metcalfe", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2025, 2029, 2024)
    add("WY-THOMSPON-BETTY", "Betty Thomspon", "special-districts", "Cokeville Cemetery Director (2-year unexpired)", "Cokeville Cemetery District", 2027, 2029, 2026,
        "Official 2026 certified write-in: Betty Thomspon (5 write-in votes), official spelling as printed, Lincoln County Canvassing Board, November 5, 2026.",
        sources=[pg(2026), wi()])
    add("WY-TOOMER-BRIAN", "Brian Toomer", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-3: Brian Toomer 248, Janet Dayton 246, plus official certified write-in Scott Thomas (4 write-in votes).")
    add("WY-DAYTON-JANET", "Janet Dayton", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2027, 2031, 2026)
    add("WY-THOMAS-SCOTT", "Scott Thomas", "special-districts", "Cokeville Cemetery Director (4-year)", "Cokeville Cemetery District", 2027, 2031, 2026,
        "Official 2026 certified write-in: Scott Thomas (4 write-in votes), Lincoln County Canvassing Board, November 5, 2026.",
        sources=[pg(2026), wi()])

    # 2022 So Lincoln Fire VF2 is write-in only with no certified named winner — not encoded.
    add("WY-HALPAIN-DENNIS-J", "Dennis J. Halpain", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-3: Dennis J. Halpain 1,245, Richard Hartman 1,162, Virginia Hartman 1,074.")
    add("WY-HARTMAN-RICHARD", "Richard Hartman", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2025, 2029, 2024)
    add("WY-HARTMAN-VIRGINIA", "Virginia Hartman", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2025, 2029, 2024)
    add("WY-ASHLIMAN-COREY", "Corey Ashliman", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-3: Corey Ashliman 945, Jason L. Smith 940, plus official certified write-in Fred Baldwin (7 write-in votes).")
    add("WY-SMITH-JASON-L", "Jason L. Smith", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2027, 2031, 2026)
    add("WY-BALDWIN-FRED", "Fred Baldwin", "special-districts", "South Lincoln Fire Director", "South Lincoln Fire District", 2027, 2031, 2026,
        "Official 2026 certified write-in: Fred Baldwin (7 write-in votes), Lincoln County Canvassing Board, November 5, 2026. Encoded under the official abstract spelling, not assumed to be the same person as Fred A. Baldwin.",
        sources=[pg(2026), wi()])

    add("WY-ERICKSON-RYAN-J", "Ryan J. Erickson", "special-districts", "Upper Valley Fire Director", "Upper Valley Fire District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Lynn Veigel 1,099, Ryan J. Erickson 1,079.")
    add("WY-VEIGEL-LYNN", "Lynn Veigel", "special-districts", "Upper Valley Fire Director", "Upper Valley Fire District", 2023, 2027, 2022)
    add("WY-MCDONALD-DENNIS", "Dennis McDonald", "special-districts", "Upper Valley Fire Director", "Upper Valley Fire District", 2025, 2029, 2024, "Official 2024 Lincoln clerk: Dennis McDonald 2,091.")
    add("WY-VEIGEL-LYNN", "Lynn Veigel", "special-districts", "Upper Valley Fire Director", "Upper Valley Fire District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Lynn Veigel 1,138, Ryan J. Erickson 1,026.")
    add("WY-ERICKSON-RYAN-J", "Ryan J. Erickson", "special-districts", "Upper Valley Fire Director", "Upper Valley Fire District", 2027, 2031, 2026)

    add("WY-SKINNER-LANCE", "Lance Skinner", "special-districts", "Mid-Valley Fire Director (4-year)", "Mid-Valley Fire District", 2023, 2027, 2022, "Official 2022 Lincoln clerk: Lance Skinner 940, Marti Halverson 776.")
    add("WY-HALVERSON-MARTI", "Marti Halverson", "special-districts", "Mid-Valley Fire Director (4-year)", "Mid-Valley Fire District", 2023, 2027, 2022)
    add("WY-VOYLES-KEVIN", "Kevin Voyles", "special-districts", "Mid-Valley Fire Director (2-year)", "Mid-Valley Fire District", 2023, 2025, 2022, "Official 2022 Lincoln clerk: Kevin Voyles 992.")
    add("WY-VOYLES-KEVIN", "Kevin Voyles", "special-districts", "Mid-Valley Fire Director (4-year)", "Mid-Valley Fire District", 2025, 2029, 2024, "Official 2024 Lincoln clerk: Kevin Voyles 1,447.")
    add("WY-SKINNER-LANCE", "Lance Skinner", "special-districts", "Mid-Valley Fire Director (4-year)", "Mid-Valley Fire District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Lance Skinner 870, Marti Halverson 678.")
    add("WY-HALVERSON-MARTI", "Marti Halverson", "special-districts", "Mid-Valley Fire Director (4-year)", "Mid-Valley Fire District", 2027, 2031, 2026)

    add("WY-CAMERON-MARK-D", "Mark D. Cameron", "special-districts", "Alpine Fire Director (2-year)", "Alpine Fire District", 2027, 2029, 2026, "Official 2026 Lincoln clerk: Mark D. Cameron 710.")
    add("WY-JORGENSEN-JOHN", "John Jorgensen", "special-districts", "Alpine Fire Director (4-year)", "Alpine Fire District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: John Jorgensen 600, Bobbi Clauson 508.")
    add("WY-CLAUSON-BOBBI", "Bobbi Clauson", "special-districts", "Alpine Fire Director (4-year)", "Alpine Fire District", 2027, 2031, 2026)

    add("WY-WALKER-KEVIN-D", "Kevin D. Walker", "special-districts", "Bear River Fire Director", "Bear River Fire District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-2: Kevin D. Walker 274, Douglas A. Prows 270.")
    add("WY-PROWS-DOUGLAS-A", "Douglas A. Prows", "special-districts", "Bear River Fire Director", "Bear River Fire District", 2023, 2027, 2022)
    add("WY-FORREST-LYLE", "Lyle Forrest", "special-districts", "Bear River Fire Director", "Bear River Fire District", 2025, 2029, 2024, "Official 2024 Lincoln clerk: Lyle Forrest 366.")
    add("WY-LUTHI-KAYDELL", "Kaydell Luthi", "special-districts", "Bear River Fire Director (2-year unexpired)", "Bear River Fire District", 2027, 2029, 2026,
        "Official 2026 certified write-in, 2-year unexpired: Kaydell Luthi (5 write-in votes), Lincoln County Canvassing Board, November 5, 2026.",
        sources=[pg(2026), wi()])
    add("WY-CHADWICK-CRAIG", "Craig Chadwick", "special-districts", "Bear River Fire Director", "Bear River Fire District", 2027, 2031, 2026, "Official 2026 Lincoln clerk Vote-For-2: Craig Chadwick 193, Michael L. Duran 182.")
    add("WY-DURAN-MICHAEL-L", "Michael L. Duran", "special-districts", "Bear River Fire Director", "Bear River Fire District", 2027, 2031, 2026)

    add("WY-KILLIAN-CHRISTY", "Christy Killian", "special-districts", "Kemmerer Senior Citizens District Trustee", "Kemmerer Senior Citizens District", 2023, 2027, 2022, "Official 2022 Lincoln clerk Vote-For-3: Christy Killian 1,079, Denise Sargent 1,033. No certified named third winner on the official general.")
    add("WY-SARGENT-DENISE", "Denise Sargent", "special-districts", "Kemmerer Senior Citizens District Trustee", "Kemmerer Senior Citizens District", 2023, 2027, 2022)
    add("WY-CARTWRIGHT-TERRI", "Terri Cartwright", "special-districts", "Kemmerer Senior Citizens District Trustee", "Kemmerer Senior Citizens District", 2025, 2029, 2024, "Official 2024 Lincoln clerk Vote-For-2: Terri Cartwright 1,365, Cindy H. Miller 1,205.")
    add("WY-MILLER-CINDY-H", "Cindy H. Miller", "special-districts", "Kemmerer Senior Citizens District Trustee", "Kemmerer Senior Citizens District", 2025, 2029, 2024)

    return terms
