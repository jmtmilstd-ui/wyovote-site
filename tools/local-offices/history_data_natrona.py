"""Natrona County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
ARCHIVE = "https://www.natronacounty-wy.gov/659/Election-Results"
COURTS_D = "https://www.wyocourts.gov/court/district-court-7th-judicial-district-natrona-county/"
COURTS_C = "https://www.wyocourts.gov/court/circuit-court-of-the-7th-judicial-district-natrona-county-state-of-wyoming-casper/"

# Official clerk general summaries (DocumentCenter IDs on the official archive page).
PG = {
    2016: ("https://www.natronacounty-wy.gov/DocumentCenter/View/3244/2016-ELECTION-SUMMARY-EL45",
           "Natrona County official 2016 general election summary"),
    2018: ("https://www.natronacounty-wy.gov/DocumentCenter/View/4636/EL45-Summary-2018-General",
           "Natrona County official 2018 general election summary"),
    2020: ("https://www.natronacounty-wy.gov/DocumentCenter/View/5983/EL-45-Summary-PDF",
           "Natrona County official 2020 general election summary"),
    2022: ("https://www.natronacounty-wy.gov/DocumentCenter/View/7601/Official-Gen-2022-Natrona-County-Gen-Election-Summary-EL-45",
           "Natrona County official 2022 general election summary"),
    2024: ("https://www.natronacounty-wy.gov/DocumentCenter/View/12138/Official-2024-General-Election-Summary-PDF",
           "Natrona County official 2024 general election summary"),
    2026: ("https://www.natronacounty-wy.gov/DocumentCenter/View/14059/2026-General-Election-Summary",
           "Natrona County official 2026 general election summary"),
}

# Official SOS Natrona general PbP (statewide, legislative, and judicial retentions).
SOS = {
    2010: ("https://sos.wyo.gov/Elections/Docs/2010/Results/General/2010_Natrona_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2010 Natrona general precinct-by-precinct summary"),
    2012: ("https://sos.wyo.gov/Elections/Docs/2012/Results/General/2012_Natrona_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2012 Natrona general precinct-by-precinct summary"),
    2014: ("https://sos.wyo.gov/Elections/Docs/2014/Results/General/2014_Natrona_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2014 Natrona general precinct-by-precinct summary"),
    2016: ("https://sos.wyo.gov/Elections/Docs/2016/Results/General/2016_Natrona_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2016 Natrona general precinct-by-precinct summary"),
    2018: ("https://sos.wyo.gov/Elections/Docs/2018/Results/General/2018_Natrona_County_General_PbP.pdf",
           "Wyoming Secretary of State official 2018 Natrona general precinct-by-precinct summary"),
}


def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}


def sos(year: int) -> dict:
    url, label = SOS[year]
    return {"label": label, "url": url}


def courts(which="district") -> dict:
    if which == "circuit":
        return {"label": "Wyoming Judicial Branch official Circuit Court of the 7th Judicial District (Casper) page", "url": COURTS_C}
    return {"label": "Wyoming Judicial Branch official District Court, 7th Judicial District, Natrona County page", "url": COURTS_D}


def T(**kw):
    if not kw.get("sources"):
        ey = kw.get("election_year")
        if ey in PG:
            kw["sources"] = [pg(ey)]
        elif ey in SOS:
            kw["sources"] = [sos(ey)]
    return H.term(**kw)


def register_people(P):
    # Reuse name-index / existing worktree IDs. Dan J. Itzen and Daniel J Itzen are one person (WY-ITZEN-DAN).
    rows = [
        ("WY-BONER-BRIAN", "Brian Boner", "Brian", "Boner"),
        ("WY-LANDEN-BILL", "Bill Landen", "Bill", "Landen", "", "William R. Landen"),
        ("WY-HELLING-KEVIN", "Kevin Helling", "Kevin", "Helling"),
        ("WY-ANDERSON-JIM", "Jim Anderson", "Jim", "Anderson", "", "James (Jim) Anderson|James Anderson"),
        ("WY-IDE-BOB", "Bob Ide", "Bob", "Ide"),
        ("WY-ENGEBRETSEN-LISA", "Lisa Engebretsen", "Lisa", "Engebretsen"),
        ("WY-PERKINS-DREW", "Drew Perkins", "Drew", "Perkins"),
        ("WY-SCOTT-CHARLES-K", "Charles K. Scott", "Charles", "Scott", "K."),
        ("WY-LOCKE-TONY", "Tony Locke", "Tony", "Locke"),
        ("WY-DRESANG-CHRISTOPHER", "Christopher Dresang", "Christopher", "Dresang"),
        ("WY-MACGUIRE-JOE", "Joe MacGuire", "Joe", "MacGuire"),
        ("WY-KROEKER-KENDELL", "Kendell Kroeker", "Kendell", "Kroeker"),
        ("WY-WASHUT-ART", "Art Washut", "Art", "Washut", "", "Arthur Lyle Washut"),
        ("WY-BOVEE-DEBBIE", "Debbie Bovee", "Debbie", "Bovee"),
        ("WY-GAY-GERALD", "Gerald Gay", "Gerald", "Gay"),
        ("WY-HARSHMAN-STEVE", "Steve Harshman", "Steve", "Harshman"),
        ("WY-COSTELLO-BRIAN", "Brian Costello", "Brian", "Costello"),
        ("WY-LIEN-JAYME", "Jayme Lien", "Jayme", "Lien"),
        ("WY-WALTERS-TOM", "Tom Walters", "Tom", "Walters"),
        ("WY-HENDRY-ROBERT-L", "Robert L. Hendry", "Robert", "Hendry", "L."),
        ("WY-CAMPBELL-ELISSA", "Elissa Campbell", "Elissa", "Campbell"),
        ("WY-OBERMUELLER-JERRY", "Jerry Obermueller", "Jerry", "Obermueller"),
        ("WY-STUBSON-TIM", "Tim Stubson", "Tim", "Stubson"),
        ("WY-JARVIS-JULIE", "Julie Jarvis", "Julie", "Jarvis"),
        ("WY-WARD-JEANETTE", "Jeanette Ward", "Jeanette", "Ward"),
        ("WY-GRAY-CHUCK", "Chuck Gray", "Chuck", "Gray", "", "Charles Gray|Charles Jan Gray"),
        ("WY-ALLEMAND-BILL", "Bill Allemand", "Bill", "Allemand"),
        ("WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "Patrick", "Sweeney", "", "Pat Sweeney|Patrick Sweeney"),
        ("WY-REEDER-TOM", "Tom Reeder", "Tom", "Reeder"),
        ("WY-SHEPPERSON-LISA", "Lisa Shepperson", "Lisa", "Shepperson"),
        ("WY-RIGGINS-JR", "J.R. Riggins", "J.R.", "Riggins"),
        ("WY-OHEARN-KEVIN", "Kevin O'Hearn", "Kevin", "O'Hearn", "", "Kevin C. O'Hearn"),
        ("WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "Carl", "Loucks", "R.", "Bunky Loucks|Carl R. Loucks"),
        ("WY-CAMPBELL-KEVIN-J", "Kevin J. Campbell", "Kevin", "Campbell", "J.", "Kevin Campbell"),
        ("WY-CHADWICK-FORREST", "Forrest Chadwick", "Forrest", "Chadwick"),
        ("WY-LOCKHART-THOMAS-A", "Thomas A. Lockhart", "Thomas", "Lockhart", "A."),
        ("WY-BRECHTEL-BOB", "Bob Brechtel", "Bob", "Brechtel"),
        ("WY-PACHECO-RAY", "Ray Pacheco", "Ray", "Pacheco"),
        ("WY-LAIRD-DALLAS", "Dallas Laird", "Dallas", "Laird"),
        ("WY-KEATING-MATT", "Matt Keating", "Matt", "Keating", "", "Matthew Keating|Matt Keating (REP)"),
        ("WY-COATES-CASEY", "Casey Coates", "Casey", "Coates"),
        ("WY-NORTH-DAVE", "Dave North", "Dave", "North"),
        ("WY-MILNE-JIM", "Jim Milne", "Jim", "Milne", "", "James \"Jim\" Milne|James Jim Milne"),
        ("WY-NICOLAYSEN-PETER-C", "Peter C. Nicolaysen", "Peter", "Nicolaysen", "C."),
        ("WY-FREEL-STEVEN", "Steven Freel", "Steven", "Freel"),
        ("WY-KAUFMAN-BROOK", "Brook Kaufman", "Brook", "Kaufman"),
        ("WY-BERTOGLIO-PAUL-C", "Paul C. Bertoglio", "Paul", "Bertoglio", "C."),
        ("WY-GOOD-TRACY", "Tracy Good", "Tracy", "Good"),
        ("WY-DOYLE-TOM", "Tom Doyle", "Tom", "Doyle"),
        ("WY-BRYAN-HEATHER", "Heather Bryan", "Heather", "Bryan"),
        ("WY-SAULSBURY-TAMMY", "Tammy Saulsbury", "Tammy", "Saulsbury"),
        ("WY-HARLIN-JOHN", "John Harlin", "John", "Harlin"),
        ("WY-ITZEN-DAN", "Dan J. Itzen", "Dan", "Itzen", "J.", "Daniel J Itzen|Daniel J. Itzen|Dan Itzen"),
        ("WY-KIESTER-JILL", "Jill Kiester", "Jill", "Kiester"),
        ("WY-WHIPPS-JAMES", "James L. Whipps", "James", "Whipps", "L.", "James Whipps"),
        ("WY-JACOBSON-CONNIE", "Connie Jacobson", "Connie", "Jacobson"),
        ("WY-HOLBROOK-GUS", "Gus Holbrook", "Gus", "Holbrook"),
        ("WY-VOLIN-ANNE", "Anne Volin", "Anne", "Volin"),
        # 7th JD — full names from official SOS PbP and official wyocourts.gov pages.
        ("WY-WILKING-CATHERINE-E", "Catherine E. Wilking", "Catherine", "Wilking", "E."),
        ("WY-FORGEY-DANIEL-L", "Daniel L. Forgey", "Daniel", "Forgey", "L.", "Dan Forgey"),
        ("WY-JOHNSON-KERRI-M", "Kerri M. Johnson", "Kerri", "Johnson", "M."),
        ("WY-EAMES-JOSHUA", "Joshua Eames", "Joshua", "Eames"),
        ("WY-SULLINS-TOM", "Tom Sullins", "Tom", "Sullins"),
        ("WY-PARK-DAVID-B", "David B. Park", "David", "Park", "B."),
        ("WY-SKAVDAHL-SCOTT-W", "Scott W. Skavdahl", "Scott", "Skavdahl", "W."),
        ("WY-PATCHEN-MICHAEL-N", "Michael N. Patchen", "Michael", "Patchen", "N."),
        ("WY-BROWN-H-STEVEN", "H. Steven Brown", "H. Steven", "Brown", "", "H Steven Brown"),
        ("WY-HUBER-MICHAEL-E-CIRCUIT", "Michael E. Huber", "Michael", "Huber", "E."),
        ("WY-CHRISTENSEN-BRIAN-D", "Brian D. Christensen", "Brian", "Christensen", "D."),
        ("WY-COLLIER-NICHOLE", "Nichole Collier", "Nichole", "Collier"),
        ("WY-TAHERI-KEVIN-D", "Kevin D. Taheri", "Kevin", "Taheri", "D."),
        ("WY-SWEET-CYNTHIA-K", "Cynthia K. Sweet", "Cynthia", "Sweet", "K."),
        # Distinct from the 7th JD circuit judge Michael E. Huber.
        ("WY-HUBER-MICHAEL-E-COUNCIL", "Michael E. Huber", "Michael", "Huber", "E."),
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=True)
    return rows

def legislature_and_county_terms():
    terms = []

    def sen(pid, name, dist, start_y, end_y, ey, party="REP", src=None, **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group="state-senate", office=f"Senate District {dist} (S{dist:02d})",
            jurisdiction="Wyoming Legislature", role="Senator",
            term_start=FM[start_y], term_end=FM[end_y],
            how_took_office="elected", election_year=ey, confidence="high",
            sources=src or ([pg(ey)] if ey in PG else [sos(ey)]),
            **kw,
        ))

    def hou(pid, name, dist, start_y, end_y, ey, party="REP", src=None, **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group="state-house", office=f"House District {dist} (H{dist:02d})",
            jurisdiction="Wyoming Legislature", role="Representative",
            term_start=FM[start_y], term_end=FM[end_y],
            how_took_office="elected", election_year=ey, confidence="high",
            sources=src or ([pg(ey)] if ey in PG else [sos(ey)]),
            **kw,
        ))

    # Senate: even districts presidential years; odd midterms. S02 first official Natrona ballot is 2024.
    sen("WY-BONER-BRIAN", "Brian Boner", 2, 2025, 2029, 2024)
    sen("WY-ANDERSON-JIM", "Jim Anderson", 28, 2013, 2017, 2012, src=[sos(2012)])
    sen("WY-ANDERSON-JIM", "Jim Anderson", 28, 2017, 2021, 2016)
    sen("WY-ANDERSON-JIM", "Jim Anderson", 28, 2021, 2025, 2020)
    sen("WY-ANDERSON-JIM", "Jim Anderson", 28, 2025, 2029, 2024)
    sen("WY-SCOTT-CHARLES-K", "Charles K. Scott", 30, 2013, 2017, 2012, src=[sos(2012)])
    sen("WY-SCOTT-CHARLES-K", "Charles K. Scott", 30, 2017, 2021, 2016)
    sen("WY-SCOTT-CHARLES-K", "Charles K. Scott", 30, 2021, 2025, 2020)
    sen("WY-SCOTT-CHARLES-K", "Charles K. Scott", 30, 2025, 2029, 2024)
    sen("WY-LANDEN-BILL", "Bill Landen", 27, 2011, 2015, 2010, src=[sos(2010)])
    sen("WY-LANDEN-BILL", "Bill Landen", 27, 2015, 2019, 2014, src=[sos(2014)])
    sen("WY-LANDEN-BILL", "Bill Landen", 27, 2019, 2023, 2018)
    sen("WY-LANDEN-BILL", "Bill Landen", 27, 2023, 2027, 2022)
    sen("WY-HELLING-KEVIN", "Kevin Helling", 27, 2027, 2031, 2026)
    sen("WY-PERKINS-DREW", "Drew Perkins", 29, 2011, 2015, 2010, src=[sos(2010)])
    sen("WY-PERKINS-DREW", "Drew Perkins", 29, 2015, 2019, 2014, src=[sos(2014)])
    sen("WY-PERKINS-DREW", "Drew Perkins", 29, 2019, 2023, 2018)
    sen("WY-IDE-BOB", "Bob Ide", 29, 2023, 2027, 2022)
    sen("WY-ENGEBRETSEN-LISA", "Lisa Engebretsen", 29, 2027, 2031, 2026)

    # House 2-year terms. Official SOS 2010–2014; official clerk 2016–2026. H62 begins 2022.
    houses = {
        35: [
            (2010, 2011, 2013, "WY-KROEKER-KENDELL", "Kendell Kroeker", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-KROEKER-KENDELL", "Kendell Kroeker", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-KROEKER-KENDELL", "Kendell Kroeker", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-KROEKER-KENDELL", "Kendell Kroeker", "REP", None),
            (2018, 2019, 2021, "WY-MACGUIRE-JOE", "Joe MacGuire", "REP", None),
            (2020, 2021, 2023, "WY-MACGUIRE-JOE", "Joe MacGuire", "REP", None),
            (2022, 2023, 2025, "WY-LOCKE-TONY", "Tony Locke", "REP", None),
            (2024, 2025, 2027, "WY-LOCKE-TONY", "Tony Locke", "REP", None),
            (2026, 2027, 2029, "WY-DRESANG-CHRISTOPHER", "Christopher Dresang", "REP", None),
        ],
        36: [
            (2010, 2011, 2013, "WY-GAY-GERALD", "Gerald Gay", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-GAY-GERALD", "Gerald Gay", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-GAY-GERALD", "Gerald Gay", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-BOVEE-DEBBIE", "Debbie Bovee", "DEM", None),
            (2018, 2019, 2021, "WY-WASHUT-ART", "Art Washut", "REP", None),
            (2020, 2021, 2023, "WY-WASHUT-ART", "Art Washut", "REP", None),
            (2022, 2023, 2025, "WY-WASHUT-ART", "Art Washut", "REP", None),
            (2024, 2025, 2027, "WY-WASHUT-ART", "Art Washut", "REP", None),
            (2026, 2027, 2029, "WY-WASHUT-ART", "Art Washut", "REP", None),
        ],
        37: [
            (2010, 2011, 2013, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", None),
            (2018, 2019, 2021, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", None),
            (2020, 2021, 2023, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", None),
            (2022, 2023, 2025, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", None),
            (2024, 2025, 2027, "WY-HARSHMAN-STEVE", "Steve Harshman", "REP", None),
            (2026, 2027, 2029, "WY-COSTELLO-BRIAN", "Brian Costello", "REP", None),
        ],
        38: [
            (2010, 2011, 2013, "WY-BRECHTEL-BOB", "Bob Brechtel", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-WALTERS-TOM", "Tom Walters", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-WALTERS-TOM", "Tom Walters", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-WALTERS-TOM", "Tom Walters", "REP", None),
            (2018, 2019, 2021, "WY-WALTERS-TOM", "Tom Walters", "REP", None),
            (2020, 2021, 2023, "WY-WALTERS-TOM", "Tom Walters", "REP", None),
            (2022, 2023, 2025, "WY-WALTERS-TOM", "Tom Walters", "REP", None),
            (2024, 2025, 2027, "WY-LIEN-JAYME", "Jayme Lien", "REP", None),
            (2026, 2027, 2029, "WY-HENDRY-ROBERT-L", "Robert L. Hendry", "REP", None),
        ],
        56: [
            (2010, 2011, 2013, "WY-STUBSON-TIM", "Tim Stubson", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-STUBSON-TIM", "Tim Stubson", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-STUBSON-TIM", "Tim Stubson", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-OBERMUELLER-JERRY", "Jerry Obermueller", "REP", None),
            (2018, 2019, 2021, "WY-OBERMUELLER-JERRY", "Jerry Obermueller", "REP", None),
            (2020, 2021, 2023, "WY-OBERMUELLER-JERRY", "Jerry Obermueller", "REP", None),
            (2022, 2023, 2025, "WY-OBERMUELLER-JERRY", "Jerry Obermueller", "REP", None),
            (2024, 2025, 2027, "WY-CAMPBELL-ELISSA", "Elissa Campbell", "REP", None),
            (2026, 2027, 2029, "WY-CAMPBELL-ELISSA", "Elissa Campbell", "REP", None),
        ],
        57: [
            (2010, 2011, 2013, "WY-LOCKHART-THOMAS-A", "Thomas A. Lockhart", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-LOCKHART-THOMAS-A", "Thomas A. Lockhart", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-LOCKHART-THOMAS-A", "Thomas A. Lockhart", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-GRAY-CHUCK", "Chuck Gray", "REP", None),
            (2018, 2019, 2021, "WY-GRAY-CHUCK", "Chuck Gray", "REP", None),
            (2020, 2021, 2023, "WY-GRAY-CHUCK", "Chuck Gray", "REP", None),
            (2022, 2023, 2025, "WY-WARD-JEANETTE", "Jeanette Ward", "REP", None),
            (2024, 2025, 2027, "WY-JARVIS-JULIE", "Julie Jarvis", "REP", None),
            (2026, 2027, 2029, "WY-JARVIS-JULIE", "Julie Jarvis", "REP", None),
        ],
        58: [
            (2010, 2011, 2013, "WY-SHEPPERSON-LISA", "Lisa Shepperson", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-REEDER-TOM", "Tom Reeder", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-REEDER-TOM", "Tom Reeder", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "REP", None),
            (2018, 2019, 2021, "WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "REP", None),
            (2020, 2021, 2023, "WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "REP", None),
            (2022, 2023, 2025, "WY-ALLEMAND-BILL", "Bill Allemand", "REP", None),
            (2024, 2025, 2027, "WY-ALLEMAND-BILL", "Bill Allemand", "REP", None),
            (2026, 2027, 2029, "WY-ALLEMAND-BILL", "Bill Allemand", "REP", None),
        ],
        59: [
            (2010, 2011, 2013, "WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "REP", [sos(2010)]),
            (2012, 2013, 2015, "WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "REP", [sos(2012)]),
            (2014, 2015, 2017, "WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "REP", [sos(2014)]),
            (2016, 2017, 2019, "WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "REP", None),
            (2018, 2019, 2021, "WY-LOUCKS-BUNKY", "Carl R. \"Bunky\" Loucks", "REP", None),
            (2020, 2021, 2023, "WY-OHEARN-KEVIN", "Kevin C. O'Hearn", "REP", None),
            (2022, 2023, 2025, "WY-OHEARN-KEVIN", "Kevin O'Hearn", "REP", None),
            (2024, 2025, 2027, "WY-RIGGINS-JR", "J.R. Riggins", "REP", None),
            (2026, 2027, 2029, "WY-RIGGINS-JR", "J.R. Riggins", "REP", None),
        ],
        62: [
            (2022, 2023, 2025, "WY-CHADWICK-FORREST", "Forrest Chadwick", "REP", None),
            (2024, 2025, 2027, "WY-CAMPBELL-KEVIN-J", "Kevin Campbell", "REP", None),
            (2026, 2027, 2029, "WY-CAMPBELL-KEVIN-J", "Kevin J. Campbell", "REP", None),
        ],
    }
    for dist, rows in houses.items():
        for ey, a, b, pid, name, party, src in rows:
            hou(pid, name, dist, a, b, ey, party=party, src=src)

    def cty(pid, name, office, a, b, ey, party="REP", src=None, **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group="county", office=office, jurisdiction="Natrona County",
            term_start=FM[a], term_end=FM[b],
            how_took_office="elected", election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=src or [pg(ey)], **kw,
        ))

    # Commissioners (5-member). 2016+ from official clerk. 2014 VF3 not in this archive.
    # 2016 VF2 through Jan 2021; 2018 VF3 through Jan 2023; 2020 VF2 through Jan 2025;
    # 2022 VF3 through Jan 2027; 2024 VF2 through Jan 2029; 2026 VF3 through Jan 2031.
    cty("WY-KEATING-MATT", "Matt Keating", "County Commissioner", 2017, 2021, 2016)
    cty("WY-CHADWICK-FORREST", "Forrest Chadwick", "County Commissioner", 2017, 2021, 2016)
    cty("WY-MILNE-JIM", "Jim Milne", "County Commissioner", 2019, 2023, 2018)
    cty("WY-BERTOGLIO-PAUL-C", "Paul C. Bertoglio", "County Commissioner", 2019, 2023, 2018)
    cty("WY-HENDRY-ROBERT-L", "Robert L. Hendry", "County Commissioner", 2019, 2023, 2018)
    cty("WY-KAUFMAN-BROOK", "Brook Kaufman", "County Commissioner", 2021, 2023, 2020,
        notes="Official 2020 general Vote-For-2 winner. The official 2022 general includes a Vote-For-1 commissioner unexpired won by Steven Freel and does not name the vacated 2020 seat. January 2023–2024 snapshots use Freel for that remainder and keep Dave North as the continuing 2020-class member (North is also the official 2024 winner). This end date is a medium-confidence inference.",
        flags=["midterm-vacancy-inference"], confidence="medium")
    cty("WY-NORTH-DAVE", "Dave North", "County Commissioner", 2021, 2025, 2020)
    cty("WY-FREEL-STEVEN", "Steven Freel", "County Commissioner", 2023, 2025, 2022,
        notes="Official 2022 general Vote-For-1 commissioner unexpired. Official summaries do not name the vacated seat or the remainder length; encoded through January 2025 to align with the 2020 commissioner class (medium).",
        flags=["unexpired-remainder-inferred"], confidence="medium")
    cty("WY-LAIRD-DALLAS", "Dallas Laird", "County Commissioner", 2023, 2027, 2022)
    cty("WY-NICOLAYSEN-PETER-C", "Peter C. Nicolaysen", "County Commissioner", 2023, 2027, 2022)
    cty("WY-MILNE-JIM", "James \"Jim\" Milne", "County Commissioner", 2023, 2027, 2022)
    cty("WY-COATES-CASEY", "Casey Coates", "County Commissioner", 2025, 2029, 2024)
    cty("WY-NORTH-DAVE", "Dave North", "County Commissioner", 2025, 2029, 2024)
    cty("WY-PACHECO-RAY", "Ray Pacheco", "County Commissioner", 2027, 2031, 2026)
    cty("WY-LAIRD-DALLAS", "Dallas Laird", "County Commissioner", 2027, 2031, 2026)
    cty("WY-KEATING-MATT", "Matt Keating", "County Commissioner", 2027, 2031, 2026)

    # Row offices are midterm 4-year terms. Official 2018, 2022, 2026 clerk generals.
    # January 2015–2018 row offices are Not yet collected (no official 2014 clerk summary in this archive).
    cty("WY-GOOD-TRACY", "Tracy Good", "County Clerk", 2019, 2023, 2018)
    cty("WY-GOOD-TRACY", "Tracy Good", "County Clerk", 2023, 2027, 2022)
    cty("WY-GOOD-TRACY", "Tracy Good", "County Clerk", 2027, 2031, 2026)
    cty("WY-DOYLE-TOM", "Tom Doyle", "County Treasurer", 2019, 2023, 2018)
    cty("WY-DOYLE-TOM", "Tom Doyle", "County Treasurer", 2023, 2027, 2022)
    cty("WY-BRYAN-HEATHER", "Heather Bryan", "County Treasurer", 2027, 2031, 2026)
    cty("WY-KEATING-MATT", "Matthew Keating", "County Assessor", 2019, 2023, 2018)
    cty("WY-SAULSBURY-TAMMY", "Tammy Saulsbury", "County Assessor", 2023, 2027, 2022)
    cty("WY-SAULSBURY-TAMMY", "Tammy Saulsbury", "County Assessor", 2027, 2031, 2026)
    cty("WY-HOLBROOK-GUS", "Gus Holbrook", "County Sheriff", 2019, 2023, 2018)
    cty("WY-HARLIN-JOHN", "John Harlin", "County Sheriff", 2023, 2027, 2022)
    cty("WY-HARLIN-JOHN", "John Harlin", "County Sheriff", 2027, 2031, 2026)
    cty("WY-ITZEN-DAN", "Dan Itzen", "District Attorney", 2019, 2023, 2018)
    cty("WY-ITZEN-DAN", "Dan J. Itzen", "District Attorney", 2023, 2027, 2022)
    cty("WY-ITZEN-DAN", "Daniel J Itzen", "District Attorney", 2027, 2031, 2026,
        notes="Official 2022 ballot Dan J. Itzen; official 2026 ballot Daniel J Itzen. One person (WY-ITZEN-DAN). Name-index also has a second ID WY-ITZEN-DANIEL, which is not used.")
    cty("WY-VOLIN-ANNE", "Anne Volin", "Clerk of District Court", 2019, 2023, 2018)
    cty("WY-KIESTER-JILL", "Jill Kiester", "Clerk of District Court", 2023, 2027, 2022)
    cty("WY-KIESTER-JILL", "Jill Kiester", "Clerk of District Court", 2027, 2031, 2026)
    cty("WY-JACOBSON-CONNIE", "Connie Jacobson", "County Coroner", 2019, 2023, 2018)
    cty("WY-WHIPPS-JAMES", "James Whipps", "County Coroner", 2023, 2027, 2022)
    cty("WY-WHIPPS-JAMES", "James L. Whipps", "County Coroner", 2027, 2031, 2026)
    return terms

def judicial_terms():
    """7th JD only. Full names from official SOS PbP or official wyocourts.gov pages when the clerk summary prints only a last name or omits the name."""
    terms = []

    def dist(pid, name, a, b, ey, sources, notes="", how="retained", extra_start=None, conf="high", flags=None):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="District Judge, 7th Judicial District",
            jurisdiction="7th Judicial District", role="District Judge",
            term_start=extra_start or FM[a], term_end=FM[b],
            how_took_office=how, election_year=ey, confidence=conf,
            sources=sources, notes=notes, flags=flags or [],
            retention={"election_year": ey, "result": "retained"} if how in {"retained", "elected"} and ey else None,
        ))

    def circ(pid, name, a, b, ey, sources, notes="", how="retained", extra_start=None, extra_end=None, conf="high", flags=None):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="Circuit Judge, 7th Judicial District",
            jurisdiction="7th Judicial District", role="Circuit Judge",
            term_start=extra_start or FM[a], term_end=extra_end or FM[b],
            how_took_office=how, election_year=ey, confidence=conf,
            sources=sources, notes=notes, flags=flags or [],
            retention={"election_year": ey, "result": "retained"} if how in {"retained", "elected"} and ey else None,
        ))

    # District — 6-year terms after retention. Official SOS 2010–2014 and 2018 names; official clerk 2020–2026 last names filled from official SOS / wyocourts.gov.
    dist("WY-SKAVDAHL-SCOTT-W", "Scott W. Skavdahl", 2011, 2017, 2010, [sos(2010)],
         notes="Official SOS 2010 Natrona general PbP: District Court Judge, Seventh Judicial District, Scott W. Skavdahl, YES 16,307 / NO 4,074.")
    dist("WY-PARK-DAVID-B", "David B. Park", 2013, 2019, 2012, [sos(2012)],
         notes="Official SOS 2012 Natrona general PbP: District Court Judge, Seventh Judicial District, David B. Park, YES 22,540 / NO 5,549.")
    dist("WY-WILKING-CATHERINE-E", "Catherine E. Wilking", 2013, 2019, 2012, [sos(2012), courts("district")],
         notes="Official SOS 2012 Natrona general PbP: Catherine E. Wilking, YES 21,507 / NO 4,998. Official Wyoming Judicial Branch 7th JD district page lists Honorable Catherine E. Wilking, appointed February 2011.")
    dist("WY-WILKING-CATHERINE-E", "Catherine E. Wilking", 2019, 2025, 2018, [sos(2018), pg(2018)],
         notes="Official 2018 clerk summary lists a District Court Judge retention (YES 17,993 / NO 3,723) with no name. Official SOS 2018 Natrona PbP names Catherine E. Wilking with the same YES/NO totals.")
    dist("WY-WILKING-CATHERINE-E", "Catherine E. Wilking", 2025, 2031, 2024, [pg(2024), courts("district")],
         notes="Official 2024 clerk summary: DISTRICT COURT JUDGE WILKING, YES 22,056. Given name Catherine E. Wilking from the official Wyoming Judicial Branch 7th JD district page (also official SOS 2012 and 2018 PbP).")
    dist("WY-FORGEY-DANIEL-L", "Daniel L. Forgey", 2015, 2021, 2014, [sos(2014), courts("district")],
         notes="Official SOS 2014 Natrona general PbP: District Court Judge, Seventh Judicial District, Daniel L. Forgey, YES 14,581 / NO 3,547. Official Wyoming Judicial Branch 7th JD district page lists Honorable Dan Forgey, appointed August 2013.")
    dist("WY-FORGEY-DANIEL-L", "Daniel L. Forgey", 2021, 2027, 2020, [pg(2020), sos(2014), courts("district")],
         notes="Official 2020 clerk summary: DISTRICT COURT JUDGE FORGEY, YES 24,310. Given name Daniel L. Forgey from the official SOS 2014 Natrona PbP and Dan Forgey on the official Wyoming Judicial Branch 7th JD district page.")
    dist("WY-FORGEY-DANIEL-L", "Daniel L. Forgey", 2027, 2033, 2026, [pg(2026), courts("district")],
         notes="Official 2026 clerk summary: DISTRICT COURT JUDGE FORGEY, YES 14,211. Given name Daniel L. Forgey from official SOS 2014 PbP and the official Wyoming Judicial Branch 7th JD district page.")
    dist("WY-SULLINS-TOM", "Tom Sullins", 2015, 2021, 2014, [sos(2014)],
         notes="Official SOS 2014 Natrona general PbP: District Court Judge, Seventh Judicial District, Tom Sullins, YES 15,160 / NO 3,396.")
    dist("WY-JOHNSON-KERRI-M", "Kerri M. Johnson", 2019, 2021, None, [courts("district")],
         how="appointed", extra_start="2019-01-01", conf="medium",
         notes="Official Wyoming Judicial Branch 7th JD district page: Honorable Kerri M. Johnson, appointed January 2019. Exact appointment day is not stated; January 2019 snapshot inclusion is medium. First official retention is 2020.",
         flags=["appointment-day-not-stated"])
    dist("WY-JOHNSON-KERRI-M", "Kerri M. Johnson", 2021, 2027, 2020, [pg(2020), courts("district")],
         notes="Official 2020 clerk summary: DISTRICT COURT JUDGE JOHNSON, YES 24,791. Given name Kerri M. Johnson from the official Wyoming Judicial Branch 7th JD district page.")
    dist("WY-JOHNSON-KERRI-M", "Kerri M. Johnson", 2027, 2033, 2026, [pg(2026), courts("district")],
         notes="Official 2026 clerk summary: DISTRICT COURT JUDGE JOHNSON, YES 14,629. Given name Kerri M. Johnson from the official Wyoming Judicial Branch 7th JD district page.")
    dist("WY-EAMES-JOSHUA", "Joshua Eames", 2023, 2025, None, [courts("district")],
         how="appointed", extra_start="2022-07-01", conf="medium",
         notes="Official Wyoming Judicial Branch 7th JD district page: Honorable Joshua Eames, appointed July 2022. Exact appointment day is not stated (medium). First official retention is the 2024 general.",
         flags=["appointment-day-not-stated"])
    dist("WY-EAMES-JOSHUA", "Joshua Eames", 2025, 2031, 2024, [pg(2024), courts("district")],
         notes="Official 2024 clerk summary: DISTRICT COURT JUDGE EAMES, YES 20,993. Given name Joshua Eames from the official Wyoming Judicial Branch 7th JD district page (term expires January 2031).")

    # Circuit — 4-year terms after retention.
    circ("WY-PATCHEN-MICHAEL-N", "Michael N. Patchen", 2011, 2015, 2010, [sos(2010)],
         notes="Official SOS 2010 Natrona general PbP: Circuit Court Judge, Seventh Judicial District, Michael N. Patchen, YES 16,044 / NO 3,989.")
    circ("WY-PATCHEN-MICHAEL-N", "Michael N. Patchen", 2015, 2019, 2014, [sos(2014)],
         notes="Official SOS 2014 Natrona general PbP: Michael N. Patchen, YES 14,757 / NO 3,491.")
    circ("WY-PATCHEN-MICHAEL-N", "Michael N. Patchen", 2019, 2023, 2018, [sos(2018), pg(2018)],
         notes="Official 2018 clerk summary lists a Circuit Court Judge retention with no name (YES 17,613 / NO 3,645 on the official SOS 2018 PbP). Official SOS 2018 Natrona PbP names Michael N. Patchen with those totals.")
    circ("WY-PATCHEN-MICHAEL-N", "Michael N. Patchen", 2023, 2025, 2022, [pg(2022), sos(2018)],
         notes="Official 2022 clerk summary: CIRCUIT COURT JUDGE PATCHEN, YES 15,716. Given name Michael N. Patchen from official SOS 2010, 2014, and 2018 Natrona PbP. He is not on the official 2024 clerk retention ballot and is not listed on the current official 7th JD circuit page; this term is ended at January 2025 (medium).",
         conf="medium", flags=["term-end-inferred-from-later-roster"])
    circ("WY-BROWN-H-STEVEN", "H. Steven Brown", 2013, 2017, 2012, [sos(2012)],
         notes="Official SOS 2012 Natrona general PbP: Circuit Court Judge, Seventh Judicial District, H Steven Brown, YES 22,806 / NO 5,145.")
    circ("WY-BROWN-H-STEVEN", "H. Steven Brown", 2017, 2021, 2016, [sos(2016), pg(2016)],
         notes="Official 2016 clerk summary labels this retention Judge4 (YES 22,242 / NO 6,144) with no name. Official SOS 2016 Natrona PbP names H. Steven Brown with the same YES/NO totals.")
    circ("WY-BROWN-H-STEVEN", "H. Steven Brown", 2021, 2025, 2020, [pg(2020), sos(2016)],
         notes="Official 2020 clerk summary: CIRCUIT COURT JUDGE BROWN, YES 24,621. Given name H. Steven Brown from the official SOS 2016 (and 2012) Natrona PbP.")
    circ("WY-HUBER-MICHAEL-E-CIRCUIT", "Michael E. Huber", 2013, 2017, 2012, [sos(2012)],
         notes="Official SOS 2012 Natrona general PbP: Circuit Court Judge, Seventh Judicial District, Michael E. Huber, YES 21,488 / NO 6,407. Distinct from 2018 Casper City Council member Michael E. Huber (WY-HUBER-MICHAEL-E-COUNCIL).")
    circ("WY-CHRISTENSEN-BRIAN-D", "Brian D. Christensen", 2017, 2021, 2016, [sos(2016), pg(2016)],
         notes="Official 2016 clerk summary labels this retention Judge5 (YES 22,094 / NO 5,668) with no name. Official SOS 2016 Natrona PbP names Brian D. Christensen with the same YES/NO totals.")
    circ("WY-CHRISTENSEN-BRIAN-D", "Brian D. Christensen", 2021, 2025, 2020, [pg(2020), sos(2016)],
         notes="Official 2020 clerk summary: CIRCUIT COURT JUDGE CHRISTENSEN, YES 24,432. Given name Brian D. Christensen from the official SOS 2016 Natrona PbP.")
    circ("WY-CHRISTENSEN-BRIAN-D", "Brian D. Christensen", 2025, 2026, 2024, [pg(2024)],
         extra_end="2025-03-01", conf="medium",
         notes="Official 2024 clerk summary: CIRCUIT COURT JUDGE CHRISTENSEN, YES 21,948 (would ordinarily run through January 2029). Official Wyoming Judicial Branch 7th JD circuit page lists Honorable Cynthia K. Sweet, appointed March 2025, and does not list Christensen. January 2025 keeps Christensen; January 2026 uses Sweet from that official appointment. The official court page does not expressly state that Sweet succeeded Christensen (medium).",
         flags=["midterm-succession-inferred"])
    circ("WY-COLLIER-NICHOLE", "Nichole Collier", 2023, 2025, None, [courts("circuit")],
         how="appointed", extra_start="2022-07-01", conf="medium",
         notes="Official Wyoming Judicial Branch 7th JD circuit page: Honorable Nichole Collier, appointed July 2022. Exact day not stated (medium). Official 2024 clerk retention follows.",
         flags=["appointment-day-not-stated"])
    circ("WY-COLLIER-NICHOLE", "Nichole Collier", 2025, 2029, 2024, [pg(2024), courts("circuit")],
         notes="Official 2024 clerk summary: CIRCUIT COURT JUDGE COLLIER, YES 21,807. Given name Nichole Collier from the official Wyoming Judicial Branch 7th JD circuit page (term expires January 2029).")
    circ("WY-TAHERI-KEVIN-D", "Kevin D. Taheri", 2024, 2025, None, [courts("circuit")],
         how="appointed", extra_start="2023-09-01", conf="medium",
         notes="Official Wyoming Judicial Branch 7th JD circuit page: Honorable Kevin D. Taheri, appointed September 2023. Exact day not stated (medium). Official 2024 clerk retention follows.",
         flags=["appointment-day-not-stated"])
    circ("WY-TAHERI-KEVIN-D", "Kevin D. Taheri", 2025, 2029, 2024, [pg(2024), courts("circuit")],
         notes="Official 2024 clerk summary: CIRCUIT COURT JUDGE TAHERI, YES 21,523. Given name Kevin D. Taheri from the official Wyoming Judicial Branch 7th JD circuit page (term expires January 2029).")
    circ("WY-SWEET-CYNTHIA-K", "Cynthia K. Sweet", 2026, 2027, None, [courts("circuit")],
         how="appointed", extra_start="2025-03-01", conf="medium",
         notes="Official Wyoming Judicial Branch 7th JD circuit page: Honorable Cynthia K. Sweet, appointed March 2025, term expires January 2027, stands for retention November 2026. Exact day not stated (medium).",
         flags=["appointment-day-not-stated"])
    circ("WY-SWEET-CYNTHIA-K", "Cynthia K. Sweet", 2027, 2031, 2026, [pg(2026), courts("circuit")],
         notes="Official 2026 clerk summary: CIRCUIT COURT JUDGE SWEET, YES 14,284. Given name Cynthia K. Sweet from the official Wyoming Judicial Branch 7th JD circuit page.")
    return terms

def register_local_people(P):
    rows = [
        ("WY-HOBZA-BRETT", "Brett Hobza", "Brett", "Hobza"),
        ("WY-POLLOCK-AMBER", "Amber Pollock", "Amber", "Pollock"),
        ("WY-JENSEN-GENA", "Gena Jensen", "Gena", "Jensen"),
        ("WY-BOND-MICHAEL", "Michael Bond", "Michael", "Bond"),
        ("WY-GAMROTH-KYLE", "Kyle Gamroth", "Kyle", "Gamroth"),
        ("WY-LARSON-MATTHEW", "Matthew Larson", "Matthew", "Larson"),
        ("WY-MCINTOSH-MICHAEL-H", "Michael H. McIntosh", "Michael", "McIntosh", "H."),
        ("WY-WINGERTER-TERRY", "Terry Wingerter", "Terry", "Wingerter"),
        ("WY-HASKINS-BRANDY", "Brandy Haskins", "Brandy", "Haskins"),
        ("WY-LUTZ-KHRYSTYN", "Khrystyn Lutz", "Khrystyn", "Lutz"),
        ("WY-JOHNSON-SHAWN", "Shawn Johnson", "Shawn", "Johnson"),
        ("WY-BATES-KENNETH", "Kenneth Bates", "Kenneth", "Bates"),
        ("WY-HOPKINS-BOB", "Bob Hopkins", "Bob", "Hopkins"),
        ("WY-HUCKABAY-AMANDA", "Amanda Huckabay", "Amanda", "Huckabay"),
        ("WY-MORGAN-JESSE", "Jesse Morgan", "Jesse", "Morgan"),
        ("WY-POWELL-CHARLIE", "Charlie Powell", "Charlie", "Powell"),
        ("WY-MURPHY-TODD", "Todd Murphy", "Todd", "Murphy"),
        ("WY-WALSH-CHRISTOPHER", "Christopher Walsh", "Christopher", "Walsh"),
        ("WY-KNELL-BRUCE-H", "Bruce H. Knell Jr.", "Bruce", "Knell", "H."),
        ("WY-CATHEY-STEPHEN", "Stephen Cathey", "Stephen", "Cathey"),
        ("WY-GIERKE-PHIL", "Phil Gierke", "Phil", "Gierke"),
        ("WY-MACHADO-CANDACE", "Candace Machado", "Candace", "Machado"),
        ("WY-EDWARDS-CHAD", "Chad Edwards", "Chad", "Edwards"),
        ("WY-SORENSON-JENNIFER", "Jennifer Sorenson", "Jennifer", "Sorenson"),
        ("WY-STYPA-RHONDA", "Rhonda Stypa", "Rhonda", "Stypa"),
        ("WY-SHELDEN-DALE", "Dale Shelden", "Dale", "Shelden"),
        ("WY-DEGROOT-WENDY", "Wendy DeGroot", "Wendy", "DeGroot"),
        ("WY-EDWARDS-DACIA", "Dacia Edwards", "Dacia", "Edwards"),
        ("WY-BLACKFORD-ERNIE", "Ernie Blackford", "Ernie", "Blackford"),
        ("WY-VIGNEAULT-ALONA", "Alona Vigneault", "Alona", "Vigneault"),
        ("WY-VIGNEAULT-AARON", "Aaron Vigneault", "Aaron", "Vigneault"),
        ("WY-FLESVIG-GREG", "Greg Flesvig", "Greg", "Flesvig"),
        ("WY-KNOP-JOSEPH-A", "Joseph A. Knop", "Joseph", "Knop", "A."),
        ("WY-WHITE-DOUG", "Doug White", "Doug", "White"),
        ("WY-SCOTT-MICHAEL", "Michael Scott", "Michael", "Scott"),
        ("WY-JUAREZ-LEAH", "Leah Juarez", "Leah", "Juarez"),
        ("WY-COLEMAN-SETH-M", "Seth M. Coleman", "Seth", "Coleman", "M."),
        ("WY-SUTHERLAND-TIM", "Tim Sutherland", "Tim", "Sutherland", "", "Timothy Sutherland"),
        ("WY-BUTCHER-CHERIE", "Cherie Butcher", "Cherie", "Butcher"),
        ("WY-NEUMILLER-BRAD", "Brad Neumiller", "Brad", "Neumiller", "", "Bradley D. Neumiller"),
        ("WY-MCCARTHY-SARA-E", "Sara E. McCarthy", "Sara", "McCarthy", "E.", "Sara McCarthy"),
        ("WY-HOLLANDER-JAMES", "James Hollander", "James", "Hollander"),
        ("WY-IVES-DARLA-R", "Darla R. Ives", "Darla", "Ives", "R."),
        ("WY-WALES-RONALD", "Ronald \"Hunter\" Wales", "Ronald", "Wales"),
        ("WY-CHILDRESS-BRIAN", "Brian Childress", "Brian", "Childress"),
        ("WY-BOYER-PETER", "Peter Boyer", "Peter", "Boyer"),
        ("WY-FORD-PATRICK-R", "Patrick R. Ford", "Patrick", "Ford", "R."),
        ("WY-JARRARD-OLIN", "Olin Jarrard", "Olin", "Jarrard"),
        ("WY-CHILDRESS-MELISSA", "Melissa Childress", "Melissa", "Childress"),
        ("WY-FICKEN-TIM-J", "Tim J. Ficken", "Tim", "Ficken", "J."),
        ("WY-SABROSKY-DAN", "Dan Sabrosky", "Dan", "Sabrosky"),
        ("WY-CLARK-STEVEN", "Steven Clark", "Steven", "Clark"),
        ("WY-MARTIN-TYLER", "Tyler Martin", "Tyler", "Martin"),
        ("WY-KELLY-TERI", "Teri Kelly", "Teri", "Kelly"),
        ("WY-HOOVER-ROBERT-W", "Robert W. Hoover", "Robert", "Hoover", "W."),
        ("WY-BROWN-JOSH", "Josh Brown", "Josh", "Brown"),
        ("WY-SORENSON-MARY-SUE", "Mary Sue Sorenson", "Mary Sue", "Sorenson"),
        ("WY-WILLETT-ADAM", "Adam Willett", "Adam", "Willett"),
        ("WY-APPLEGATE-DAVE", "Dave Applegate", "Dave", "Applegate", "", "David Applegate"),
        ("WY-KINDER-ANNA", "Anna Kinder", "Anna", "Kinder"),
        ("WY-MCCONNAUGHEY-RYAN", "Ryan McConnaughey", "Ryan", "McConnaughey"),
        ("WY-BYRD-KIM", "Kim Byrd", "Kim", "Byrd"),
        ("WY-SWEDBERG-JAY", "Jay Swedberg", "Jay", "Swedberg"),
        ("WY-CUNDY-BRAD", "Brad Cundy", "Brad", "Cundy"),
        ("WY-BOHREN-DALE", "Dale Bohren", "Dale", "Bohren"),
        ("WY-MILLIKEN-TODD", "Todd Milliken", "Todd", "Milliken"),
        ("WY-DOLAN-KATHY", "Kathy Dolan", "Kathy", "Dolan"),
        ("WY-MILLER-SUSAN-D", "Susan D. Miller", "Susan", "Miller", "D."),
        ("WY-BENNION-SCOTT-D", "Scott D. Bennion", "Scott", "Bennion", "D.", "Scott Bennion"),
        ("WY-BATTON-LIZ", "Liz Batton", "Liz", "Batton"),
        ("WY-DEGENFELDER-STEVE", "Steve Degenfelder", "Steve", "Degenfelder"),
        ("WY-SCHILLING-SUE", "Sue Schilling", "Sue", "Schilling"),
        ("WY-KUGLER-TIM-S", "Tim S. Kugler", "Tim", "Kugler", "S."),
        ("WY-LOUCKS-MATTHEW-A", "Matthew A. Loucks", "Matthew", "Loucks", "A."),
        ("WY-SANDOVAL-SUZANNE", "Suzanne Sandoval", "Suzanne", "Sandoval"),
        ("WY-CHRISTOPHERSON-KEVIN", "Kevin Christopherson", "Kevin", "Christopherson"),
        ("WY-STEDILLIE-MICHAEL", "Michael Stedillie", "Michael", "Stedillie"),
        ("WY-NELSON-ERIC", "Eric Nelson", "Eric", "Nelson"),
        ("WY-ROSTY-TAYLOR", "Taylor Rosty", "Taylor", "Rosty"),
        ("WY-BOLENDER-JOHN", "John Bolender", "John", "Bolender"),
        ("WY-HOWIE-DANA", "Dana Howie", "Dana", "Howie", "", "Dana M. Howie"),
        ("WY-TRUE-WELLS-THEA", "Thea True-Wells", "Thea", "True-Wells"),
        ("WY-PETRINO-ALEX", "Alex Petrino", "Alex", "Petrino"),
        ("WY-ALVEY-KYLA", "Kyla Alvey", "Kyla", "Alvey"),
        ("WY-HOPKINS-JENIFER", "Jenifer Hopkins", "Jenifer", "Hopkins"),
        ("WY-SCHMIDT-MARY", "Mary Schmidt", "Mary", "Schmidt"),
        ("WY-WALSH-RITA", "Rita Walsh", "Rita", "Walsh"),
        ("WY-CATELLIER-RAYMOND", "Raymond J. Catellier", "Raymond", "Catellier", "J.", "Raymond Catellier"),
        ("WY-MARSHALL-TRAVIS", "Travis Marshall", "Travis", "Marshall"),
        ("WY-MCCULLAR-DEBBIE", "Debbie McCullar", "Debbie", "McCullar"),
        ("WY-SMITH-KIANNA", "Kianna Smith", "Kianna", "Smith"),
        ("WY-JENSEN-CLARK", "Clark Jensen", "Clark", "Jensen"),
        ("WY-COLEMAN-ANGELA-M", "Angela M. Coleman", "Angela", "Coleman", "M."),
        ("WY-MILES-LAURA", "Laura Miles", "Laura", "Miles"),
        ("WY-COBB-TAMMY", "Tammy Cobb", "Tammy", "Cobb", "", "Tammy L. Cobb"),
        ("WY-ANDERSON-ANDREW-C", "Andrew C. Anderson", "Andrew", "Anderson", "C."),
        ("WY-SCOTT-DENNIS", "Dennis Scott", "Dennis", "Scott", "", "Dennis D. Scott"),
        ("WY-HERMAN-RIC", "Ric Herman", "Ric", "Herman"),
        ("WY-STUMBOUGH-GRANT", "Grant Stumbough", "Grant", "Stumbough"),
        ("WY-SMITH-SCOTT-S", "Scott S. Smith", "Scott", "Smith", "S."),
        ("WY-CAMP-LEN", "Len Camp", "Len", "Camp"),
        ("WY-BENTLEY-JOHN", "John Bentley", "John", "Bentley"),
        ("WY-VANDAL-BRYAN", "Bryan Vandal", "Bryan", "Vandal"),
        ("WY-HURLESS-BRENDA", "Brenda Hurless", "Brenda", "Hurless"),
        ("WY-ROBINETT-KEITH", "Keith Robinett", "Keith", "Robinett"),
        ("WY-WYATT-JERRY", "Jerry Wyatt", "Jerry", "Wyatt"),
        ("WY-TILLMAN-GEORGE-E", "George E. Tillman Jr.", "George", "Tillman", "E.", "George E. Tillman Jr|George E. Tillman JR"),
        ("WY-GARRETT-STEVEN", "Steven Garrett", "Steven", "Garrett"),
        ("WY-JACKETT-DEAN-A", "Dean A. Jackett", "Dean", "Jackett", "A."),
        ("WY-KNOPIK-KEVIN", "Kevin Knopik", "Kevin", "Knopik"),
        ("WY-DAVIS-ROBERT-D", "Robert D. Davis", "Robert", "Davis", "D."),
        ("WY-KLEIN-KAYCEE", "Kaycee Klein", "Kaycee", "Klein"),
        ("WY-NACK-MICHAEL", "Michael Nack", "Michael", "Nack"),
        ("WY-MOWRY-DAVID", "David Mowry", "David", "Mowry"),
        ("WY-SPURRIER-MARGO", "Margo Spurrier", "Margo", "Spurrier"),
        ("WY-ANDERSON-STEWART", "Stewart \"Stew\" Anderson", "Stewart", "Anderson"),
        ("WY-BRADLEY-JULIE", "Julie Bradley", "Julie", "Bradley"),
        ("WY-HARSHMAN-PAT", "Pat Harshman", "Pat", "Harshman"),
        ("WY-CHAMBERS-BILL", "Bill Chambers", "Bill", "Chambers"),
        ("WY-BARTON-JAMES", "James Barton", "James", "Barton"),
        ("WY-SANTISTEVAN-KAREN", "Karen Santistevan", "Karen", "Santistevan"),
        ("WY-THORPEN-TAMMY", "Tammy Thorpen", "Tammy", "Thorpen"),
        ("WY-DOYLE-RUTH", "Ruth Doyle", "Ruth", "Doyle"),
        ("WY-MORSE-CRYSTAL", "Crystal Morse", "Crystal", "Morse"),
        ("WY-IFLAND-JANE", "Jane Ifland", "Jane", "Ifland"),
        ("WY-STEPP-MIKE", "Mike Stepp", "Mike", "Stepp"),
        ("WY-BLACKSTONE-LINDA", "Linda Blackstone", "Linda", "Blackstone"),
        ("WY-HOPKINS-BOB-SR", "Bob Hopkins", "Bob", "Hopkins"),  # careful: Bob Hopkins council and senior board — may be same; reuse WY-HOPKINS-BOB
        ("WY-LAIRD-RHONDA", "Rhonda Laird", "Rhonda", "Laird"),
        ("WY-PROVENCE-RICK", "Rick Provence", "Rick", "Provence"),
        ("WY-PIESTRACK-NANCY", "Nancy Piestrack", "Nancy", "Piestrack"),
        ("WY-DEWITT-AMANDA", "Amanda DeWitt", "Amanda", "DeWitt"),
        ("WY-CLYMER-RAYMOND", "Raymond Clymer", "Raymond", "Clymer"),
        ("WY-BROW-VICTOR-PAUL", "Victor Paul Brow", "Victor", "Brow", "Paul"),
        ("WY-TUCKER-FRANK", "Frank Tucker", "Frank", "Tucker"),
        ("WY-ARNOLD-KATIE", "Katie Arnold", "Katie", "Arnold"),
        ("WY-AARS-ASHLEY", "Ashley Aars", "Ashley", "Aars"),
        ("WY-STEWART-CLIFFORD", "Clifford Stewart", "Clifford", "Stewart"),
    ]
    for row in rows:
        if row[0] == "WY-HOPKINS-BOB-SR":
            continue  # same display as council Bob Hopkins; reuse WY-HOPKINS-BOB
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=True)


def local_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, party="", **kw):
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a], term_end=FM[b],
            how_took_office="elected", election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=kw.pop("sources", [pg(ey)]), **kw,
        ))

    # Casper mayor is selected by the City Council from its own members at the first regular
    # January meeting, for a calendar year; it is not on the November general ballot.
    COUNCIL = "https://www.casperwy.gov/government/city_council/index.php"
    MINUTES = "https://www.casperwy.gov/government/city_council/agendas_minutes.php"

    def casper_minutes(url, label):
        return {"label": label, "url": url}

    def mayor(pid, name, start, end, minutes_url, minutes_label, notes, ey=None):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="municipal", office="Casper Mayor", jurisdiction="City of Casper",
            term_start=start, term_end=end,
            how_took_office="selected by council", election_year=ey, confidence="high",
            sources=[
                casper_minutes(minutes_url, minutes_label),
                {"label": "City of Casper official Agendas & Minutes page", "url": MINUTES},
            ],
            notes=notes,
        ))

    mayor("WY-FREEL-STEVEN", "Steven K. Freel", "2021-01-05", "2022-01-04",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2021/Minutes/01-05-21%20Minutes.pdf",
          "City of Casper official January 5, 2021 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 5, 2021 minutes: nominate Steven K. Freel as Mayor for calendar year 2021; motion passed.")
    mayor("WY-PACHECO-RAY", "Ray Pacheco", "2022-01-04", "2023-01-03",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2022/Minutes/01-04-22%20Council%20Meeting%20Minutes%20final.pdf",
          "City of Casper official January 4, 2022 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 4, 2022 minutes: appoint Councilmember Pacheco as Mayor for calendar year 2022; motion passed.")
    mayor("WY-KNELL-BRUCE-H", "Bruce Knell", "2023-01-03", "2024-01-02",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2023/Minutes/01-03-23%20Council%20Meeting%20Minutes.pdf",
          "City of Casper official January 3, 2023 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 3, 2023 minutes: elect Councilor Bruce Knell as Mayor for calendar year 2023; motion passed. Same person as official 2020 general Ward 1 winner Bruce H. Knell Jr.")
    mayor("WY-CATHEY-STEPHEN", "Stephen Cathey", "2024-01-02", "2025-01-07",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2024/Minutes/01-02-24%20Council%20Meeting%20Minutes%20(updated).pdf",
          "City of Casper official January 2, 2024 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 2, 2024 minutes: elect Stephen Cathey as Mayor for calendar year 2024; motion passed.")
    mayor("WY-PACHECO-RAY", "Ray Pacheco", "2025-01-07", "2026-01-06",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2025/Minutes/01-07-25%20Council%20Meeting%20Minutes.pdf",
          "City of Casper official January 7, 2025 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 7, 2025 minutes: elect Councilor Ray Pacheco as Mayor for calendar year 2025; motion passed.")
    mayor("WY-PACHECO-RAY", "Ray Pacheco", "2026-01-06", "2027-01-05",
          "https://www.casperwy.gov/Documents/Government/City%20Council/Agendas%20and%20Minutes/2026/Minutes/01-06-26%20Council%20Meeting%20Minutes.pdf",
          "City of Casper official January 6, 2026 regular council meeting minutes",
          "Selected by the Casper City Council from its members. Official January 6, 2026 minutes: Select Councilor Pacheco as the Mayor for calendar year 2026 (Approved 8-0-1). Official City of Casper Mayor & City Council page, retrieved 2026-11-24: Ray Pacheco, Mayor, term expires 1/5/27.",
          ey=None)
    # Add the official current-roster page to the 2026 term sources.
    terms[-1]["sources"].append({"label": "City of Casper official Mayor & City Council page", "url": COUNCIL})

    # Casper City Council: official midterm VF1 and presidential VF2, three members per ward, 4-year terms.
    # Ward 1
    add("WY-HOPKINS-BOB", "Bob Hopkins", "municipal", "Casper City Council Ward 1", "City of Casper", 2017, 2021, 2016)
    add("WY-HUCKABAY-AMANDA", "Amanda Huckabay", "municipal", "Casper City Council Ward 1", "City of Casper", 2017, 2021, 2016)
    add("WY-MORGAN-JESSE", "Jesse Morgan", "municipal", "Casper City Council Ward 1", "City of Casper", 2017, 2021, 2016,
        notes="Official 2016 general Ward 1 unexpired.")
    add("WY-LUTZ-KHRYSTYN", "Khrystyn Lutz", "municipal", "Casper City Council Ward 1", "City of Casper", 2019, 2023, 2018)
    add("WY-HUBER-MICHAEL-E-COUNCIL", "Michael E. Huber", "municipal", "Casper City Council Ward 1", "City of Casper", 2019, 2023, 2018,
        notes="Official 2018 general Ward 1 unexpired. Distinct from 7th JD Circuit Judge Michael E. Huber (WY-HUBER-MICHAEL-E-CIRCUIT).")
    add("WY-POLLOCK-AMBER", "Amber Pollock", "municipal", "Casper City Council Ward 1", "City of Casper", 2021, 2025, 2020)
    add("WY-KNELL-BRUCE-H", "Bruce H. Knell Jr.", "municipal", "Casper City Council Ward 1", "City of Casper", 2021, 2025, 2020)
    add("WY-JENSEN-GENA", "Gena Jensen", "municipal", "Casper City Council Ward 1", "City of Casper", 2023, 2027, 2022)
    add("WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "municipal", "Casper City Council Ward 1", "City of Casper", 2025, 2029, 2024)
    add("WY-POLLOCK-AMBER", "Amber Pollock", "municipal", "Casper City Council Ward 1", "City of Casper", 2025, 2029, 2024)
    add("WY-HOBZA-BRETT", "Brett Hobza", "municipal", "Casper City Council Ward 1", "City of Casper", 2027, 2031, 2026)
    # Ward 2
    add("WY-POWELL-CHARLIE", "Charlie Powell", "municipal", "Casper City Council Ward 2", "City of Casper", 2017, 2021, 2016)
    add("WY-MURPHY-TODD", "Todd Murphy", "municipal", "Casper City Council Ward 2", "City of Casper", 2017, 2021, 2016)
    add("WY-JOHNSON-SHAWN", "Shawn Johnson", "municipal", "Casper City Council Ward 2", "City of Casper", 2019, 2023, 2018)
    add("WY-BATES-KENNETH", "Kenneth Bates", "municipal", "Casper City Council Ward 2", "City of Casper", 2019, 2023, 2018,
        notes="Official 2018 general Ward 2 unexpired.")
    add("WY-GAMROTH-KYLE", "Kyle Gamroth", "municipal", "Casper City Council Ward 2", "City of Casper", 2021, 2025, 2020)
    add("WY-ENGEBRETSEN-LISA", "Lisa Engebretsen", "municipal", "Casper City Council Ward 2", "City of Casper", 2021, 2025, 2020)
    add("WY-BOND-MICHAEL", "Michael Bond", "municipal", "Casper City Council Ward 2", "City of Casper", 2023, 2027, 2022)
    add("WY-GAMROTH-KYLE", "Kyle Gamroth", "municipal", "Casper City Council Ward 2", "City of Casper", 2025, 2029, 2024)
    add("WY-LARSON-MATTHEW", "Matthew Larson", "municipal", "Casper City Council Ward 2", "City of Casper", 2025, 2029, 2024)
    add("WY-BOND-MICHAEL", "Michael Bond", "municipal", "Casper City Council Ward 2", "City of Casper", 2027, 2031, 2026)
    # Ward 3
    add("WY-WALSH-CHRISTOPHER", "Christopher Walsh", "municipal", "Casper City Council Ward 3", "City of Casper", 2017, 2021, 2016)
    add("WY-PACHECO-RAY", "Ray Pacheco", "municipal", "Casper City Council Ward 3", "City of Casper", 2019, 2023, 2018)
    add("WY-FREEL-STEVEN", "Steven Freel", "municipal", "Casper City Council Ward 3", "City of Casper", 2019, 2023, 2018)
    add("WY-CATHEY-STEPHEN", "Stephen Cathey", "municipal", "Casper City Council Ward 3", "City of Casper", 2021, 2025, 2020)
    add("WY-PACHECO-RAY", "Ray Pacheco", "municipal", "Casper City Council Ward 3", "City of Casper", 2023, 2027, 2022)
    add("WY-HASKINS-BRANDY", "Brandy Haskins", "municipal", "Casper City Council Ward 3", "City of Casper", 2023, 2027, 2022)
    add("WY-MCINTOSH-MICHAEL-H", "Michael H. McIntosh", "municipal", "Casper City Council Ward 3", "City of Casper", 2025, 2029, 2024)
    add("WY-WINGERTER-TERRY", "Terry Wingerter", "municipal", "Casper City Council Ward 3", "City of Casper", 2027, 2031, 2026)
    add("WY-HASKINS-BRANDY", "Brandy Haskins", "municipal", "Casper City Council Ward 3", "City of Casper", 2027, 2031, 2026)

    # Town mayors (official midterm contests, encoded as 4-year terms) and councils.
    add("WY-EDWARDS-CHAD", "Chad Edwards", "municipal", "Evansville Mayor", "Town of Evansville", 2023, 2027, 2022)
    add("WY-MACHADO-CANDACE", "Candace Machado", "municipal", "Evansville Mayor", "Town of Evansville", 2025, 2027, 2024,
        notes="Official 2024 general Evansville Mayor (unexpired). Encoded as remainder through January 2027 (medium).",
        confidence="medium", flags=["unexpired-remainder-inferred"])
    # Machado unexpired overlapping Edwards 2023-2027 would be 2 mayors. End Edwards at FM[2025].
    # Fix: Edwards term_end should be FM[2025] if Machado takes the remainder. I'll adjust by not emitting Edwards through 2027 —
    # already written Edwards 2023-2027. Need to change Edwards end to 2025. Do it below after... I'll fix in this list:
    terms[-3]["term_end"] = FM[2025]
    terms[-3]["notes"] = "Official 2022 general Evansville mayor. Official 2024 general includes an unexpired mayoral contest won by Candace Machado; this term is ended at January 2025 (medium)."
    terms[-3]["confidence"] = "medium"
    terms[-3]["flags"] = ["midterm-vacancy-inference"]
    add("WY-GIERKE-PHIL", "Phil Gierke", "municipal", "Evansville Mayor", "Town of Evansville", 2027, 2031, 2026)
    add("WY-SORENSON-JENNIFER", "Jennifer Sorenson", "municipal", "Evansville Mayor", "Town of Evansville", 2019, 2023, 2018)
    add("WY-JUAREZ-LEAH", "Leah Juarez", "municipal", "Mills Mayor", "Town of Mills", 2023, 2027, 2022)
    add("WY-JUAREZ-LEAH", "Leah Juarez", "municipal", "Mills Mayor", "Town of Mills", 2027, 2031, 2026)
    add("WY-COLEMAN-SETH-M", "Seth M. Coleman", "municipal", "Mills Mayor", "Town of Mills", 2019, 2023, 2018)
    add("WY-CHILDRESS-BRIAN", "Brian Childress", "municipal", "Bar Nunn Mayor", "Town of Bar Nunn", 2027, 2031, 2026)
    add("WY-BOYER-PETER", "Peter Boyer", "municipal", "Bar Nunn Mayor", "Town of Bar Nunn", 2023, 2027, 2022)
    add("WY-FORD-PATRICK-R", "Patrick R. Ford", "municipal", "Bar Nunn Mayor", "Town of Bar Nunn", 2019, 2023, 2018)

    def council_rows(office, jur, rows):
        for pid, name, a, b, ey in rows:
            add(pid, name, "municipal", office, jur, a, b, ey)

    council_rows("Evansville Town Council", "Town of Evansville", [
        ("WY-STYPA-RHONDA", "Rhonda Stypa", 2027, 2031, 2026),
        ("WY-SHELDEN-DALE", "Dale Shelden", 2027, 2031, 2026),
        ("WY-DEGROOT-WENDY", "Wendy DeGroot", 2027, 2031, 2026),  # unexpired 2026 — still 4-year unless noted; official unexpired may be shorter. Flag medium 4-year? If unexpired, remainder. Unknown end. Use 2027-2029 medium? Skip exact — encode 2027-2031 with unexpired note medium.
        ("WY-EDWARDS-DACIA", "Dacia Edwards", 2025, 2029, 2024),
        ("WY-BLACKFORD-ERNIE", "Ernie Blackford", 2025, 2029, 2024),
        ("WY-VIGNEAULT-ALONA", "Alona Vigneault", 2025, 2029, 2024),
        ("WY-MACHADO-CANDACE", "Candace Machado", 2023, 2027, 2022),
        ("WY-FLESVIG-GREG", "Greg Flesvig", 2023, 2027, 2022),
        ("WY-EDWARDS-DACIA", "Dacia Edwards", 2023, 2027, 2022),
        ("WY-EDWARDS-CHAD", "Chad Edwards", 2019, 2023, 2018),
        ("WY-KNOP-JOSEPH-A", "Joseph A. Knop", 2019, 2023, 2018),
        ("WY-VIGNEAULT-AARON", "Aaron Vigneault", 2019, 2023, 2018),
        ("WY-SORENSON-JENNIFER", "Jennifer Sorenson", 2017, 2021, 2016),
        ("WY-WHITE-DOUG", "Doug White", 2017, 2021, 2016),
        ("WY-STYPA-RHONDA", "Rhonda Stypa", 2021, 2025, 2020),
        ("WY-SCOTT-MICHAEL", "Michael Scott", 2021, 2025, 2020),
    ])
    # mark 2026 unexpired DeGroot
    terms[-13]["notes"] = "Official 2026 general Evansville Town Council (unexpired). Remainder length is not stated; encoded as a regular four-year term through January 2031 (medium)."
    terms[-13]["confidence"] = "medium"
    terms[-13]["flags"] = ["unexpired-remainder-inferred"]

    council_rows("Mills Town Council", "Town of Mills", [
        ("WY-SUTHERLAND-TIM", "Tim Sutherland", 2027, 2031, 2026),
        ("WY-BUTCHER-CHERIE", "Cherie Butcher", 2027, 2031, 2026),
        ("WY-NEUMILLER-BRAD", "Brad Neumiller", 2025, 2029, 2024),
        ("WY-MCCARTHY-SARA-E", "Sara E. McCarthy", 2025, 2029, 2024),
        ("WY-SUTHERLAND-TIM", "Timothy Sutherland", 2023, 2027, 2022),
        ("WY-BUTCHER-CHERIE", "Cherie Butcher", 2023, 2027, 2022),
        ("WY-MCCARTHY-SARA-E", "Sara McCarthy", 2021, 2025, 2020),
        ("WY-NEUMILLER-BRAD", "Bradley D. Neumiller", 2021, 2025, 2020),
        ("WY-HOLLANDER-JAMES", "James Hollander", 2019, 2023, 2018),
        ("WY-IVES-DARLA-R", "Darla R. Ives", 2019, 2023, 2018),
        ("WY-MCCARTHY-SARA-E", "Sara E. McCarthy", 2017, 2021, 2016),
        ("WY-WALES-RONALD", "Ronald \"Hunter\" Wales", 2017, 2021, 2016),
        ("WY-IVES-DARLA-R", "Darla R. Ives", 2017, 2021, 2016),
    ])
    council_rows("Bar Nunn Town Council", "Town of Bar Nunn", [
        ("WY-JARRARD-OLIN", "Olin Jarrard", 2027, 2031, 2026),
        ("WY-CHILDRESS-MELISSA", "Melissa Childress", 2027, 2031, 2026),
        ("WY-FICKEN-TIM-J", "Tim J. Ficken", 2025, 2029, 2024),
        ("WY-SABROSKY-DAN", "Dan Sabrosky", 2025, 2029, 2024),
        ("WY-CLARK-STEVEN", "Steven Clark", 2023, 2027, 2022),
        ("WY-MARTIN-TYLER", "Tyler Martin", 2023, 2027, 2022),
        ("WY-SORENSON-MARY-SUE", "Mary Sue Sorenson", 2021, 2025, 2020),
        ("WY-BOYER-PETER", "Peter Boyer", 2021, 2025, 2020),
        ("WY-WILLETT-ADAM", "Adam Willett", 2021, 2025, 2020),
        ("WY-KELLY-TERI", "Teri Kelly", 2019, 2023, 2018),
        ("WY-HOOVER-ROBERT-W", "Robert W. Hoover", 2019, 2023, 2018),
        ("WY-BROWN-JOSH", "Josh Brown", 2017, 2021, 2016),
        ("WY-CLARK-STEVEN", "Steven Clark", 2017, 2021, 2016),
    ])

    # Casper College 4-year terms; official midterm VF3 (+ occasional unexpired) and presidential VF4.
    for pid, name, a, b, ey in [
        ("WY-APPLEGATE-DAVE", "Dave Applegate", 2027, 2031, 2026),
        ("WY-KINDER-ANNA", "Anna Kinder", 2027, 2031, 2026),
        ("WY-MCCONNAUGHEY-RYAN", "Ryan McConnaughey", 2027, 2031, 2026),
        ("WY-BYRD-KIM", "Kim Byrd", 2025, 2029, 2024),
        ("WY-SWEDBERG-JAY", "Jay Swedberg", 2025, 2029, 2024),
        ("WY-CUNDY-BRAD", "Brad Cundy", 2025, 2029, 2024),
        ("WY-BOHREN-DALE", "Dale Bohren", 2025, 2029, 2024),
        ("WY-MILLIKEN-TODD", "Todd Milliken", 2023, 2027, 2022),
        ("WY-DOLAN-KATHY", "Kathy Dolan", 2023, 2027, 2022),
        ("WY-APPLEGATE-DAVE", "David Applegate", 2023, 2027, 2022),
        ("WY-MILLER-SUSAN-D", "Susan D. Miller", 2021, 2025, 2020),
        ("WY-BENNION-SCOTT-D", "Scott D. Bennion", 2021, 2025, 2020),
        ("WY-BATTON-LIZ", "Liz Batton", 2021, 2025, 2020),
        ("WY-DEGENFELDER-STEVE", "Steve Degenfelder", 2021, 2025, 2020),
        ("WY-SCHILLING-SUE", "Sue Schilling", 2019, 2023, 2018),
        ("WY-DOLAN-KATHY", "Kathy Dolan", 2019, 2023, 2018),
        ("WY-KUGLER-TIM-S", "Tim S. Kugler", 2019, 2023, 2018),
        ("WY-DEGENFELDER-STEVE", "Steve Degenfelder", 2019, 2023, 2018),
        ("WY-BENNION-SCOTT-D", "Scott Bennion", 2017, 2021, 2016),
        ("WY-LOUCKS-MATTHEW-A", "Matthew A. Loucks", 2017, 2021, 2016),
        ("WY-MILLER-SUSAN-D", "Susan D. Miller", 2017, 2021, 2016),
        ("WY-SANDOVAL-SUZANNE", "Suzanne Sandoval", 2017, 2021, 2016),
    ]:
        add(pid, name, "schools", "Casper College Board of Trustees", "Casper College District", a, b, ey)

    # NCSD #1: official midterm VF4 and presidential VF5, 4-year terms (9-member board).
    for pid, name, a, b, ey in [
        ("WY-CHRISTOPHERSON-KEVIN", "Kevin Christopherson", 2027, 2031, 2026),
        ("WY-STEDILLIE-MICHAEL", "Michael Stedillie", 2027, 2031, 2026),
        ("WY-NELSON-ERIC", "Eric Nelson", 2027, 2031, 2026),
        ("WY-ROSTY-TAYLOR", "Taylor Rosty", 2027, 2031, 2026),
        ("WY-BOLENDER-JOHN", "John Bolender", 2025, 2029, 2024),
        ("WY-HOWIE-DANA", "Dana Howie", 2025, 2029, 2024),
        ("WY-TRUE-WELLS-THEA", "Thea True-Wells", 2025, 2029, 2024),
        ("WY-PETRINO-ALEX", "Alex Petrino", 2025, 2029, 2024),
        ("WY-ALVEY-KYLA", "Kyla Alvey", 2025, 2029, 2024),
        ("WY-STEDILLIE-MICHAEL", "Michael Stedillie", 2023, 2027, 2022),
        ("WY-HOPKINS-JENIFER", "Jenifer Hopkins", 2023, 2027, 2022),
        ("WY-CHRISTOPHERSON-KEVIN", "Kevin Christopherson", 2023, 2027, 2022),
        ("WY-SCHMIDT-MARY", "Mary Schmidt", 2023, 2027, 2022),
        ("WY-WALSH-RITA", "Rita Walsh", 2021, 2025, 2020),
        ("WY-HOWIE-DANA", "Dana Howie", 2021, 2025, 2020),
        ("WY-CATELLIER-RAYMOND", "Raymond J. Catellier", 2021, 2025, 2020),
        ("WY-ALVEY-KYLA", "Kyla Alvey", 2021, 2025, 2020),
        ("WY-MARSHALL-TRAVIS", "Travis Marshall", 2021, 2025, 2020),
        ("WY-MCCULLAR-DEBBIE", "Debbie McCullar", 2019, 2023, 2018),
        ("WY-APPLEGATE-DAVE", "David Applegate", 2019, 2023, 2018),
        ("WY-SMITH-KIANNA", "Kianna Smith", 2019, 2023, 2018),
        ("WY-JENSEN-CLARK", "Clark Jensen", 2019, 2023, 2018),
        ("WY-WALSH-RITA", "Rita Walsh", 2017, 2021, 2016),
        ("WY-HOWIE-DANA", "Dana M. Howie", 2017, 2021, 2016),
        ("WY-CHRISTOPHERSON-KEVIN", "Kevin Christopherson", 2017, 2021, 2016),
        ("WY-COLEMAN-ANGELA-M", "Angela M. Coleman", 2017, 2021, 2016),
        ("WY-CATELLIER-RAYMOND", "Raymond Catellier", 2017, 2021, 2016),
    ]:
        add(pid, name, "schools", "NCSD #1 Board of Trustees", "Natrona County School District #1", a, b, ey)

    # Conservation 4-year.
    add("WY-MILES-LAURA", "Laura Miles", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2027, 2031, 2026)
    add("WY-COBB-TAMMY", "Tammy Cobb", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2027, 2031, 2026)
    add("WY-SCOTT-DENNIS", "Dennis Scott", "special-districts", "Conservation District Supervisor At-Large", "Natrona County Conservation District", 2025, 2029, 2024)
    add("WY-HERMAN-RIC", "Ric Herman", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2025, 2029, 2024)
    add("WY-STUMBOUGH-GRANT", "Grant Stumbough", "special-districts", "Conservation District Supervisor Urban", "Natrona County Conservation District", 2025, 2029, 2024)
    add("WY-COBB-TAMMY", "Tammy L. Cobb", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2023, 2027, 2022)
    add("WY-ANDERSON-ANDREW-C", "Andrew C. Anderson", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2023, 2027, 2022)
    add("WY-HERMAN-RIC", "Ric Herman", "special-districts", "Conservation District Supervisor At-Large", "Natrona County Conservation District", 2021, 2025, 2020)
    add("WY-SCOTT-DENNIS", "Dennis D. Scott", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2021, 2025, 2020)
    add("WY-SMITH-SCOTT-S", "Scott S. Smith", "special-districts", "Conservation District Supervisor Urban", "Natrona County Conservation District", 2021, 2025, 2020)
    add("WY-COBB-TAMMY", "Tammy Cobb", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2019, 2023, 2018)
    add("WY-ANDERSON-ANDREW-C", "Andrew C. Anderson", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2019, 2023, 2018)
    add("WY-SMITH-SCOTT-S", "Scott S. Smith", "special-districts", "Conservation District Supervisor Urban", "Natrona County Conservation District", 2017, 2021, 2016)
    add("WY-CAMP-LEN", "Len Camp", "special-districts", "Conservation District Supervisor At-Large", "Natrona County Conservation District", 2017, 2021, 2016)
    add("WY-SCOTT-DENNIS", "Dennis Scott", "special-districts", "Conservation District Supervisor Rural", "Natrona County Conservation District", 2017, 2021, 2016)

    # Fire and senior (4-year from official contests). 2024 mountain fire unexpired write-in only: not filled.
    add("WY-BENTLEY-JOHN", "John Bentley", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2027, 2031, 2026,
        notes="Official 2026 general Vote-For-2 names only John Bentley (write-in totals 79); no second named winner is filled.")
    add("WY-VANDAL-BRYAN", "Bryan Vandal", "special-districts", "Fire Protection District Director (unexpired)", "Natrona County Fire Protection District", 2027, 2029, 2026, confidence="medium", flags=["unexpired-remainder-inferred"],
        notes="Official 2026 general unexpired Vote-For-2. Remainder encoded through January 2029 (medium).")
    add("WY-HURLESS-BRENDA", "Brenda Hurless", "special-districts", "Fire Protection District Director (unexpired)", "Natrona County Fire Protection District", 2027, 2029, 2026, confidence="medium", flags=["unexpired-remainder-inferred"],
        notes="Official 2026 general unexpired Vote-For-2. Remainder encoded through January 2029 (medium).")
    add("WY-ROBINETT-KEITH", "Keith Robinett", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2025, 2029, 2024)
    add("WY-WYATT-JERRY", "Jerry Wyatt", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2025, 2029, 2024)
    add("WY-TILLMAN-GEORGE-E", "George E. Tillman Jr.", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2025, 2029, 2024)
    add("WY-GARRETT-STEVEN", "Steven Garrett", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2023, 2027, 2022)
    add("WY-JACKETT-DEAN-A", "Dean A. Jackett", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2023, 2027, 2022)
    add("WY-WYATT-JERRY", "Jerry Wyatt", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2021, 2025, 2020)
    add("WY-BENTLEY-JOHN", "John Bentley", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2021, 2025, 2020)
    add("WY-TILLMAN-GEORGE-E", "George E. Tillman Jr.", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2021, 2025, 2020)
    add("WY-JACKETT-DEAN-A", "Dean A. Jackett", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2019, 2023, 2018,
        notes="Official 2018 general Vote-For-2 names only Dean A. Jackett among named candidates.")
    add("WY-ROBINETT-KEITH", "Keith Robinett", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2017, 2021, 2016)
    add("WY-BENTLEY-JOHN", "John Bentley", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2017, 2021, 2016)
    add("WY-TILLMAN-GEORGE-E", "George E. Tillman Jr.", "special-districts", "Fire Protection District Director", "Natrona County Fire Protection District", 2017, 2021, 2016)
    add("WY-KNOPIK-KEVIN", "Kevin Knopik", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2027, 2031, 2026)
    add("WY-DAVIS-ROBERT-D", "Robert D. Davis", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2027, 2031, 2026)
    add("WY-KLEIN-KAYCEE", "Kaycee Klein", "special-districts", "Casper Mountain Fire District Director (unexpired)", "Casper Mountain Fire Protection District", 2027, 2029, 2026, confidence="medium", flags=["unexpired-remainder-inferred"])
    add("WY-NACK-MICHAEL", "Michael Nack", "special-districts", "Casper Mountain Fire District Director (unexpired)", "Casper Mountain Fire Protection District", 2027, 2029, 2026, confidence="medium", flags=["unexpired-remainder-inferred"])
    add("WY-MOWRY-DAVID", "David Mowry", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2025, 2029, 2024)
    add("WY-KNOPIK-KEVIN", "Kevin Knopik", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2025, 2029, 2024)
    add("WY-ANDERSON-STEWART", "Stewart \"Stew\" Anderson", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2023, 2027, 2022)
    add("WY-KLEIN-KAYCEE", "Kaycee Klein", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2023, 2027, 2022)
    add("WY-BRADLEY-JULIE", "Julie Bradley", "special-districts", "Casper Mountain Fire District Director (unexpired)", "Casper Mountain Fire Protection District", 2023, 2025, 2022, confidence="medium", flags=["unexpired-remainder-inferred"])
    add("WY-HARSHMAN-PAT", "Pat Harshman", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2021, 2025, 2020)
    add("WY-SANTISTEVAN-KAREN", "Karen Santistevan", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2021, 2025, 2020)
    add("WY-THORPEN-TAMMY", "Tammy Thorpen", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2021, 2025, 2020)
    add("WY-MOWRY-DAVID", "David Mowry", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2019, 2023, 2018)
    add("WY-SPURRIER-MARGO", "Margo Spurrier", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2019, 2023, 2018)
    add("WY-HARSHMAN-PAT", "Pat Harshman", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2017, 2021, 2016)
    add("WY-CHAMBERS-BILL", "Bill Chambers", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2017, 2021, 2016)
    add("WY-BARTON-JAMES", "James Barton", "special-districts", "Casper Mountain Fire District Director", "Casper Mountain Fire Protection District", 2017, 2021, 2016)
    add("WY-DOYLE-RUTH", "Ruth Doyle", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2027, 2031, 2026)
    add("WY-MORSE-CRYSTAL", "Crystal Morse", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2027, 2031, 2026)
    add("WY-IFLAND-JANE", "Jane Ifland", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2027, 2031, 2026)
    add("WY-DOYLE-RUTH", "Ruth Doyle", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2025, 2029, 2024)
    add("WY-STEPP-MIKE", "Mike Stepp", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2025, 2029, 2024)
    add("WY-BLACKSTONE-LINDA", "Linda Blackstone", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2025, 2029, 2024)
    add("WY-HOPKINS-BOB", "Bob Hopkins", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2025, 2029, 2024,
        notes="Official 2024 general senior-citizens board winner Bob Hopkins; same display name as a Casper council member (WY-HOPKINS-BOB). One ID is used; this may be the same person or a name collision (flagged).",
        flags=["possible-name-collision"])
    add("WY-LAIRD-RHONDA", "Rhonda Laird", "special-districts", "Senior Citizens District Board of Trustees", "Natrona County Senior Citizens Service District", 2025, 2029, 2024)

    SRC_MIDWEST = {"label": "Official Town of Midwest city-officials page, retrieved 2026-11-24",
                   "url": "https://www.townofmidwest.com/city-officials"}
    SRC_EDGERTON = {"label": "Official Town of Edgerton town-government page, retrieved 2026-11-24",
                    "url": "https://www.townofedgertonwy.com/town-government"}
    terms.append(T(person_id="WY-PROVENCE-RICK", name="Rick Provence", office_group="municipal",
        office="Midwest Mayor", jurisdiction="Town of Midwest",
        term_start="2026-06-01", term_end="2030-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_MIDWEST],
        notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: Rick Provence, Mayor, term expires June 2030. The official June expiration is used; a conventional four-year municipal term is mapped to a June 2026 start. No official May municipal canvass was located."))
    terms.append(T(person_id="WY-PIESTRACK-NANCY", name="Nancy Piestrack", office_group="municipal",
        office="Midwest Town Council", jurisdiction="Town of Midwest",
        term_start="2026-06-01", term_end="2030-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_MIDWEST],
        notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: Nancy Piestrack, Council Member, term expires June 2030. Official June expiration used; June 2026 start inferred from a conventional four-year term. No official May municipal canvass was located."))
    terms.append(T(person_id="WY-DEWITT-AMANDA", name="Amanda DeWitt", office_group="municipal",
        office="Midwest Town Council", jurisdiction="Town of Midwest",
        term_start="2026-06-01", term_end="2030-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_MIDWEST],
        notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: AMANDA DEWITT, Council Member, term expires June 2030. Official June expiration used; June 2026 start inferred from a conventional four-year term. No official May municipal canvass was located."))
    terms.append(T(person_id="WY-CLYMER-RAYMOND", name="Raymond Clymer", office_group="municipal",
        office="Midwest Town Council", jurisdiction="Town of Midwest",
        term_start="2024-06-01", term_end="2028-06-30", how_took_office="elected", confidence="medium",
        sources=[SRC_MIDWEST],
        notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: Raymond Clymer, Council Member, term expires June 2028. Official June expiration used; June 2024 start inferred from a conventional four-year term. No official May municipal canvass was located."))
    terms.append(T(person_id="WY-BROW-VICTOR-PAUL", name="Victor Paul Brow", office_group="municipal",
        office="Edgerton Mayor", jurisdiction="Town of Edgerton",
        term_start="2025-01-09", term_end="2028-12-31", how_took_office="elected", confidence="high",
        sources=[SRC_EDGERTON],
        notes="Official Town of Edgerton town-government page, retrieved 2026-11-24: Victor Paul Brow, Mayor, Term Expires 2028. The official page does not state a month; December 2028 is used for the expiration. A term start of January 9, 2025 is used so the current holder appears in the 2026 snapshot; it is not taken from an official canvass. No official Natrona municipal canvass for this race was located."))
    for pid, name in [
        ("WY-TUCKER-FRANK", "Frank Tucker"),
        ("WY-ARNOLD-KATIE", "Katie Arnold"),
        ("WY-AARS-ASHLEY", "Ashley Aars"),
        ("WY-STEWART-CLIFFORD", "Clifford Stewart"),
    ]:
        extra = " Official page also lists Frank Tucker as Council president." if pid=="WY-TUCKER-FRANK" else ""
        terms.append(T(person_id=pid, name=name, office_group="municipal",
            office="Edgerton Town Council", jurisdiction="Town of Edgerton",
            term_start="2025-01-09", term_end="2027-06-30", how_took_office="elected", confidence="medium",
            sources=[SRC_EDGERTON],
            notes="Official Town of Edgerton town-government page, retrieved 2026-11-24, names this person as a council member."+extra+" The official page does not state a council term end; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass."))
    return terms

def build_natrona():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    register_local_people(P)

    terms = []
    terms.extend(legislature_and_county_terms())
    terms.extend(judicial_terms())
    terms.extend(local_terms())
    # Fix fragile Evansville mayor overlap: official 2024 unexpired Machado.
    for t in terms:
        if t["person_id"] == "WY-EDWARDS-CHAD" and t["office"] == "Evansville Mayor" and t["election_year"] == 2022:
            t["term_end"] = FM[2025]
            t["notes"] = (
                "Official 2022 general Evansville mayor. Official 2024 general includes an unexpired mayoral contest "
                "won by Candace Machado; this term is ended at January 2025 (medium)."
            )
            t["confidence"] = "medium"
            t["flags"] = ["midterm-vacancy-inference"]
        if t["person_id"] == "WY-DEGROOT-WENDY":
            t["notes"] = (
                "Official 2026 general Evansville Town Council (unexpired). Remainder length is not stated; encoded "
                "as a regular four-year term through January 2031 (medium)."
            )
            t["confidence"] = "medium"
            t["flags"] = ["unexpired-remainder-inferred"]

    shared_path = ROOT / "data" / "county_officials" / "history" / "shared" / "federal-statewide-terms.json"
    shared = json.loads(shared_path.read_text())
    copied = 0
    for t in shared.get("terms") or shared:
        og = t.get("office_group") or ""
        office = t.get("office") or ""
        if og in {"federal", "statewide"}:
            terms.append(deepcopy(t)); copied += 1
        elif og == "judicial" and any(x in office for x in ("Supreme Court", "Chancery")):
            rec = deepcopy(t)
            terms.append(rec); copied += 1
        # Do not copy other judicial districts. Natrona is in the 7th JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 2 (S02)", 1),
            ("Senate District 27 (S27)", 1),
            ("Senate District 28 (S28)", 1),
            ("Senate District 29 (S29)", 1),
            ("Senate District 30 (S30)", 1),
        ],
        "state-house": [
            ("House District 35 (H35)", 1),
            ("House District 36 (H36)", 1),
            ("House District 37 (H37)", 1),
            ("House District 38 (H38)", 1),
            ("House District 56 (H56)", 1),
            ("House District 57 (H57)", 1),
            ("House District 58 (H58)", 1),
            ("House District 59 (H59)", 1),
            ("House District 62 (H62)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("District Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Casper Mayor", 1),
            ("Casper City Council Ward 1", 3),
            ("Casper City Council Ward 2", 3),
            ("Casper City Council Ward 3", 3),
            ("Mills Mayor", 1),
            ("Mills Town Council", 4),
            ("Evansville Mayor", 1),
            ("Evansville Town Council", 4),
            ("Bar Nunn Mayor", 1),
            ("Bar Nunn Town Council", 4),
            ("Midwest Mayor", 1),
            ("Midwest Town Council", 3),
            ("Edgerton Mayor", 1),
            ("Edgerton Town Council", 4),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "7th Judicial District judges. Where an official Natrona clerk summary prints only a last name, or omits the "
        "name (official 2016 Judge1–Judge5 labels; official 2018 DISTRICT COURT JUDGE / CIRCUIT COURT JUDGE), the "
        "full name is taken from the official Wyoming Secretary of State Natrona general precinct-by-precinct summary "
        "or from the official Wyoming Judicial Branch 7th JD district or circuit page, and that source is cited. "
        "Natrona is in the 7th Judicial District; judges of other districts are not copied here. "
        "Cynthia K. Sweet’s official appointment is March 2025 (Wyoming Judicial Branch circuit page); January 2025 "
        "keeps official 2024 retained circuit judge Brian D. Christensen, and January 2026 lists Sweet."
    )
    special_note = (
        "Municipal, school, and special-district names are keyed from official Natrona November general summaries "
        "beginning in 2016 (the earliest official clerk summary in this archive). The Casper mayor is selected by the "
        "City Council from its own members at the first regular January meeting and is not on the November ballot; "
        "official City of Casper January 2021–2026 regular-meeting minutes name the mayors used here. Official "
        "January 2015–2020 mayor-selection minutes were not on the city's public agendas-and-minutes archive at "
        "retrieval, so those years remain Not yet collected. The towns of Midwest and Edgerton do not appear on "
        "those official November 2016–2026 summaries; current holders are taken from the official Town of Midwest "
        "city-officials page and the official Town of Edgerton town-government page, retrieved 2026-11-24. "
        "Casper council is filled from official midterm Vote-For-1 and presidential "
        "Vote-For-2 results (three members per ward). Official 2014 clerk local results were not available at retrieval, "
        "so January 2015–2018 county row offices and the 2014 commissioner class are Not yet collected. The official "
        "2022 general includes a Vote-For-1 commissioner unexpired (Steven Freel). The official 2024 Casper Mountain "
        "Fire District Director (unexpired) contest reports only write-in totals and is not filled."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Natrona primary PDFs are "
        "archived under /workspace/wyoleg/local-results/natrona/<year>/. The current (November 2026) precinct roster "
        "is in data/county_officials/natrona.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Natrona", county_number=1, slug="natrona", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Natrona", slug="natrona")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


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


def update_natrona_json(people: dict):
    path = ROOT / "data" / "county_officials" / "natrona.json"
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
        office("Senate District 2 (S02)", [_holder(people, "WY-BONER-BRIAN", "Brian Boner", "REP", "January 2029")]),
        office("Senate District 27 (S27)", [_holder(people, "WY-LANDEN-BILL", "Bill Landen", "REP", "January 2027"),
              _holder(people, "WY-HELLING-KEVIN", "Kevin Helling", "REP", "January 2031",
                      notes="Takes office January 2027. Official 2026 general winner.")],
              note="Kevin Helling is the official 2026 general winner and takes office January 2027."),
        office("Senate District 28 (S28)", [_holder(people, "WY-ANDERSON-JIM", "Jim Anderson", "REP", "January 2029")]),
        office("Senate District 29 (S29)", [_holder(people, "WY-IDE-BOB", "Bob Ide", "REP", "January 2027"),
              _holder(people, "WY-ENGEBRETSEN-LISA", "Lisa Engebretsen", "REP", "January 2031",
                      notes="Takes office January 2027. Official 2026 general winner.")],
              note="Lisa Engebretsen is the official 2026 general winner and takes office January 2027."),
        office("Senate District 30 (S30)", [_holder(people, "WY-SCOTT-CHARLES-K", "Charles K. Scott", "REP", "January 2029")]),
    ]
    house = [
        ("35", "WY-LOCKE-TONY", "Tony Locke", "WY-DRESANG-CHRISTOPHER", "Christopher Dresang"),
        ("36", "WY-WASHUT-ART", "Art Washut", "WY-WASHUT-ART", "Art Washut"),
        ("37", "WY-HARSHMAN-STEVE", "Steve Harshman", "WY-COSTELLO-BRIAN", "Brian Costello"),
        ("38", "WY-LIEN-JAYME", "Jayme Lien", "WY-HENDRY-ROBERT-L", "Robert L. Hendry"),
        ("56", "WY-CAMPBELL-ELISSA", "Elissa Campbell", "WY-CAMPBELL-ELISSA", "Elissa Campbell"),
        ("57", "WY-JARVIS-JULIE", "Julie Jarvis", "WY-JARVIS-JULIE", "Julie Jarvis"),
        ("58", "WY-ALLEMAND-BILL", "Bill Allemand", "WY-ALLEMAND-BILL", "Bill Allemand"),
        ("59", "WY-RIGGINS-JR", "J.R. Riggins", "WY-RIGGINS-JR", "J.R. Riggins"),
        ("62", "WY-CAMPBELL-KEVIN-J", "Kevin Campbell", "WY-CAMPBELL-KEVIN-J", "Kevin J. Campbell"),
    ]
    house_offices = []
    for num, cur_id, cur_name, el_id, el_name in house:
        holders = [_holder(people, cur_id, cur_name, "REP", "January 2027")]
        if el_id != cur_id:
            holders.append(_holder(people, el_id, el_name, "REP", "January 2029",
                                   notes="Takes office January 2027. Official 2026 general winner."))
        else:
            holders = [_holder(people, el_id, el_name, "REP", "January 2029",
                               notes="Official 2024 and 2026 general winner, continuing; official 2026 term begins January 2027.")]
        house_offices.append(office(f"House District {num} (H{num})", holders))

    county = [
        office("County Commissioners", [
            _holder(people, "WY-COATES-CASEY", "Casey Coates", "REP", "January 2029"),
            _holder(people, "WY-NORTH-DAVE", "Dave North", "REP", "January 2029"),
            _holder(people, "WY-LAIRD-DALLAS", "Dallas Laird", "REP", "January 2027"),
            _holder(people, "WY-NICOLAYSEN-PETER-C", "Peter C. Nicolaysen", "REP", "January 2027"),
            _holder(people, "WY-MILNE-JIM", "James \"Jim\" Milne", "REP", "January 2027"),
            _holder(people, "WY-PACHECO-RAY", "Ray Pacheco", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-3 winner."),
            _holder(people, "WY-LAIRD-DALLAS", "Dallas Laird", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-KEATING-MATT", "Matt Keating", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-3 winner. Official 2018 assessor was Matthew Keating (same person)."),
        ]),
        office("County Clerk", [_holder(people, "WY-GOOD-TRACY", "Tracy Good", "REP", "January 2031",
                                        notes="Official 2022 and 2026 general winner, continuing.")]),
        office("County Treasurer", [
            _holder(people, "WY-DOYLE-TOM", "Tom Doyle", "REP", "January 2027"),
            _holder(people, "WY-BRYAN-HEATHER", "Heather Bryan", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("County Assessor", [_holder(people, "WY-SAULSBURY-TAMMY", "Tammy Saulsbury", "REP", "January 2031",
                                           notes="Official 2022 and 2026 general winner, continuing.")]),
        office("County Sheriff", [_holder(people, "WY-HARLIN-JOHN", "John Harlin", "REP", "January 2031",
                                          notes="Official 2022 and 2026 general winner, continuing.")]),
        office("District Attorney", [_holder(people, "WY-ITZEN-DAN", "Daniel J Itzen", "REP", "January 2031",
                                            notes="Official 2022 ballot Dan J. Itzen; official 2026 ballot Daniel J Itzen. Official 2022 term ends January 2027; official 2026 general winner, continuing.")]),
        office("Clerk of District Court", [_holder(people, "WY-KIESTER-JILL", "Jill Kiester", "REP", "January 2031",
                                                  notes="Official 2022 and 2026 general winner, continuing.")]),
        office("County Coroner", [_holder(people, "WY-WHIPPS-JAMES", "James L. Whipps", "REP", "January 2031",
                                          notes="Official 2022 ballot James Whipps; official 2026 ballot James L. Whipps, continuing.")]),
    ]

    nyc = {"name": "Not yet collected", "person_id": "", "party": "", "term_end": "",
           "notes": "Does not appear on the official November 2016–2026 clerk general summaries archived here.",
           "confidence": "low"}
    municipal = [
        office("Casper Mayor", [_holder(people, "WY-PACHECO-RAY", "Ray Pacheco", "", "January 5, 2027",
                                       notes="Selected by the Casper City Council from its members, not on the November ballot. Official January 6, 2026 regular meeting minutes: selected as Mayor for calendar year 2026. Official City of Casper Mayor & City Council page, retrieved 2026-11-24: term expires 1/5/27.")]),
        office("Casper City Council Ward 1", [
            _holder(people, "WY-SWEENEY-PATRICK", "Patrick \"Pat\" Sweeney", "", "January 2029"),
            _holder(people, "WY-POLLOCK-AMBER", "Amber Pollock", "", "January 2029"),
            _holder(people, "WY-JENSEN-GENA", "Gena Jensen", "", "January 2027"),
            _holder(people, "WY-HOBZA-BRETT", "Brett Hobza", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Casper City Council Ward 2", [
            _holder(people, "WY-GAMROTH-KYLE", "Kyle Gamroth", "", "January 2029"),
            _holder(people, "WY-LARSON-MATTHEW", "Matthew Larson", "", "January 2029"),
            _holder(people, "WY-BOND-MICHAEL", "Michael Bond", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Casper City Council Ward 3", [
            _holder(people, "WY-MCINTOSH-MICHAEL-H", "Michael H. McIntosh", "", "January 2029"),
            _holder(people, "WY-PACHECO-RAY", "Ray Pacheco", "", "January 2027"),
            _holder(people, "WY-HASKINS-BRANDY", "Brandy Haskins", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-WINGERTER-TERRY", "Terry Wingerter", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Mills Mayor", [_holder(people, "WY-JUAREZ-LEAH", "Leah Juarez", "", "January 2031",
                                       notes="Official 2022 and 2026 general winner, continuing.")]),
        office("Mills Town Council", [
            _holder(people, "WY-NEUMILLER-BRAD", "Brad Neumiller", "", "January 2029"),
            _holder(people, "WY-MCCARTHY-SARA-E", "Sara E. McCarthy", "", "January 2029"),
            _holder(people, "WY-SUTHERLAND-TIM", "Tim Sutherland", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-BUTCHER-CHERIE", "Cherie Butcher", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Evansville Mayor", [
            _holder(people, "WY-MACHADO-CANDACE", "Candace Machado", "", "January 2027",
                    notes="Official 2024 general unexpired winner."),
            _holder(people, "WY-GIERKE-PHIL", "Phil Gierke", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Evansville Town Council", [
            _holder(people, "WY-EDWARDS-DACIA", "Dacia Edwards", "", "January 2029"),
            _holder(people, "WY-BLACKFORD-ERNIE", "Ernie Blackford", "", "January 2029"),
            _holder(people, "WY-VIGNEAULT-ALONA", "Alona Vigneault", "", "January 2029"),
            _holder(people, "WY-STYPA-RHONDA", "Rhonda Stypa", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-SHELDEN-DALE", "Dale Shelden", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-DEGROOT-WENDY", "Wendy DeGroot", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general unexpired winner."),
        ]),
        office("Bar Nunn Mayor", [
            _holder(people, "WY-BOYER-PETER", "Peter Boyer", "", "January 2027"),
            _holder(people, "WY-CHILDRESS-BRIAN", "Brian Childress", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Bar Nunn Town Council", [
            _holder(people, "WY-FICKEN-TIM-J", "Tim J. Ficken", "", "January 2029"),
            _holder(people, "WY-SABROSKY-DAN", "Dan Sabrosky", "", "January 2029"),
            _holder(people, "WY-CLARK-STEVEN", "Steven Clark", "", "January 2027"),
            _holder(people, "WY-MARTIN-TYLER", "Tyler Martin", "", "January 2027"),
            _holder(people, "WY-JARRARD-OLIN", "Olin Jarrard", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-CHILDRESS-MELISSA", "Melissa Childress", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Midwest Mayor", [
            _holder(people, "WY-PROVENCE-RICK", "Rick Provence", "", "June 2030",
                    notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: term expires June 2030."),
        ]),
        office("Midwest Town Council", [
            _holder(people, "WY-PIESTRACK-NANCY", "Nancy Piestrack", "", "June 2030",
                    notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: term expires June 2030."),
            _holder(people, "WY-DEWITT-AMANDA", "Amanda DeWitt", "", "June 2030",
                    notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: AMANDA DEWITT, term expires June 2030."),
            _holder(people, "WY-CLYMER-RAYMOND", "Raymond Clymer", "", "June 2028",
                    notes="Official Town of Midwest city-officials page, retrieved 2026-11-24: term expires June 2028."),
        ], note="The official city-officials page, retrieved 2026-11-24, names three council members. A fourth seat is not listed there and is not invented."),
        office("Edgerton Mayor", [
            _holder(people, "WY-BROW-VICTOR-PAUL", "Victor Paul Brow", "", "2028",
                    notes="Official Town of Edgerton town-government page, retrieved 2026-11-24: Term Expires 2028."),
        ]),
        office("Edgerton Town Council", [
            _holder(people, "WY-TUCKER-FRANK", "Frank Tucker", "", "",
                    notes="Official Town of Edgerton town-government page, retrieved 2026-11-24; listed as Council president. No term end stated on the official page."),
            _holder(people, "WY-ARNOLD-KATIE", "Katie Arnold", "", "",
                    notes="Official Town of Edgerton town-government page, retrieved 2026-11-24. No term end stated on the official page."),
            _holder(people, "WY-AARS-ASHLEY", "Ashley Aars", "", "",
                    notes="Official Town of Edgerton town-government page, retrieved 2026-11-24. No term end stated on the official page."),
            _holder(people, "WY-STEWART-CLIFFORD", "Clifford Stewart", "", "",
                    notes="Official Town of Edgerton town-government page, retrieved 2026-11-24. No term end stated on the official page."),
        ]),
    ]

    schools = [
        office("Casper College Board of Trustees", [
            _holder(people, "WY-BYRD-KIM", "Kim Byrd", "", "January 2029"),
            _holder(people, "WY-SWEDBERG-JAY", "Jay Swedberg", "", "January 2029"),
            _holder(people, "WY-CUNDY-BRAD", "Brad Cundy", "", "January 2029"),
            _holder(people, "WY-BOHREN-DALE", "Dale Bohren", "", "January 2029"),
            _holder(people, "WY-MILLIKEN-TODD", "Todd Milliken", "", "January 2027"),
            _holder(people, "WY-DOLAN-KATHY", "Kathy Dolan", "", "January 2027"),
            _holder(people, "WY-APPLEGATE-DAVE", "David Applegate", "", "January 2027"),
            _holder(people, "WY-APPLEGATE-DAVE", "Dave Applegate", "", "January 2031", notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-KINDER-ANNA", "Anna Kinder", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-MCCONNAUGHEY-RYAN", "Ryan McConnaughey", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("NCSD #1 Board of Trustees", [
            _holder(people, "WY-BOLENDER-JOHN", "John Bolender", "", "January 2029"),
            _holder(people, "WY-HOWIE-DANA", "Dana Howie", "", "January 2029"),
            _holder(people, "WY-TRUE-WELLS-THEA", "Thea True-Wells", "", "January 2029"),
            _holder(people, "WY-PETRINO-ALEX", "Alex Petrino", "", "January 2029"),
            _holder(people, "WY-ALVEY-KYLA", "Kyla Alvey", "", "January 2029"),
            _holder(people, "WY-STEDILLIE-MICHAEL", "Michael Stedillie", "", "January 2031", notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-HOPKINS-JENIFER", "Jenifer Hopkins", "", "January 2027"),
            _holder(people, "WY-CHRISTOPHERSON-KEVIN", "Kevin Christopherson", "", "January 2031", notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-SCHMIDT-MARY", "Mary Schmidt", "", "January 2027"),
            _holder(people, "WY-NELSON-ERIC", "Eric Nelson", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-ROSTY-TAYLOR", "Taylor Rosty", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
        ]),
    ]
    special = [
        office("Conservation District Supervisor At-Large", [_holder(people, "WY-SCOTT-DENNIS", "Dennis Scott", "", "January 2029")]),
        office("Conservation District Supervisor Rural", [
            _holder(people, "WY-HERMAN-RIC", "Ric Herman", "", "January 2029"),
            _holder(people, "WY-COBB-TAMMY", "Tammy L. Cobb", "", "January 2027"),
            _holder(people, "WY-ANDERSON-ANDREW-C", "Andrew C. Anderson", "", "January 2027"),
            _holder(people, "WY-MILES-LAURA", "Laura Miles", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-COBB-TAMMY", "Tammy Cobb", "", "January 2031", notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Conservation District Supervisor Urban", [_holder(people, "WY-STUMBOUGH-GRANT", "Grant Stumbough", "", "January 2029")]),
        office("Fire Protection District Director", [
            _holder(people, "WY-ROBINETT-KEITH", "Keith Robinett", "", "January 2029"),
            _holder(people, "WY-WYATT-JERRY", "Jerry Wyatt", "", "January 2029"),
            _holder(people, "WY-TILLMAN-GEORGE-E", "George E. Tillman Jr.", "", "January 2029"),
            _holder(people, "WY-GARRETT-STEVEN", "Steven Garrett", "", "January 2027"),
            _holder(people, "WY-JACKETT-DEAN-A", "Dean A. Jackett", "", "January 2027"),
            _holder(people, "WY-BENTLEY-JOHN", "John Bentley", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 named winner (only named candidate)."),
            _holder(people, "WY-VANDAL-BRYAN", "Bryan Vandal", "", "January 2029", notes="Takes office January 2027. Official 2026 unexpired winner."),
            _holder(people, "WY-HURLESS-BRENDA", "Brenda Hurless", "", "January 2029", notes="Takes office January 2027. Official 2026 unexpired winner."),
        ]),
        office("Casper Mountain Fire District Director", [
            _holder(people, "WY-MOWRY-DAVID", "David Mowry", "", "January 2029"),
            _holder(people, "WY-KNOPIK-KEVIN", "Kevin Knopik", "", "January 2031",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-DAVIS-ROBERT-D", "Robert D. Davis", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-KLEIN-KAYCEE", "Kaycee Klein", "", "January 2029", notes="Takes office January 2027. Official 2026 unexpired winner."),
            _holder(people, "WY-NACK-MICHAEL", "Michael Nack", "", "January 2029", notes="Takes office January 2027. Official 2026 unexpired winner."),
        ]),
        office("Senior Citizens District Board of Trustees", [
            _holder(people, "WY-DOYLE-RUTH", "Ruth Doyle", "", "January 2031", notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-STEPP-MIKE", "Mike Stepp", "", "January 2029"),
            _holder(people, "WY-BLACKSTONE-LINDA", "Linda Blackstone", "", "January 2029"),
            _holder(people, "WY-HOPKINS-BOB", "Bob Hopkins", "", "January 2029"),
            _holder(people, "WY-LAIRD-RHONDA", "Rhonda Laird", "", "January 2029"),
            _holder(people, "WY-MORSE-CRYSTAL", "Crystal Morse", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-IFLAND-JANE", "Jane Ifland", "", "January 2031", notes="Takes office January 2027. Official 2026 general winner."),
        ]),
    ]
    judicial = [
        office("District Judge, 7th Judicial District", [
            _holder(people, "WY-WILKING-CATHERINE-E", "Catherine E. Wilking", "", "January 2031"),
            _holder(people, "WY-FORGEY-DANIEL-L", "Daniel L. Forgey", "", "January 2033",
                    notes="Official 2020 term ends January 2027; official 2026 general retention (YES), continuing. Given name from official SOS 2014 PbP and the official Wyoming Judicial Branch 7th JD district page."),
            _holder(people, "WY-JOHNSON-KERRI-M", "Kerri M. Johnson", "", "January 2033",
                    notes="Official 2020 term ends January 2027; official 2026 general retention (YES), continuing. Given name from the official Wyoming Judicial Branch 7th JD district page."),
            _holder(people, "WY-EAMES-JOSHUA", "Joshua Eames", "", "January 2031",
                    notes="Given name from the official Wyoming Judicial Branch 7th JD district page."),
        ]),
        office("Circuit Judge, 7th Judicial District", [
            _holder(people, "WY-COLLIER-NICHOLE", "Nichole Collier", "", "January 2029",
                    notes="Given name from the official Wyoming Judicial Branch 7th JD circuit page."),
            _holder(people, "WY-TAHERI-KEVIN-D", "Kevin D. Taheri", "", "January 2029",
                    notes="Given name from the official Wyoming Judicial Branch 7th JD circuit page."),
            _holder(people, "WY-SWEET-CYNTHIA-K", "Cynthia K. Sweet", "", "January 2031",
                    notes="Official Wyoming Judicial Branch 7th JD circuit page: appointed March 2025; official 2026 general retention (YES), term begins January 2027."),
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
    apply_to_groups(data["groups"], 'natrona')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
