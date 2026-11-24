"""Sweetwater County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
ARCHIVE = "https://www.sweetwatercountywy.gov/departments/county_clerk/election_returns/index.php"
ARCHIVE_OLD = "https://www.sweetwatercountywy.gov/departments/county_clerk/election_archrives_results/index.php"
CMS = "https://cms7files.revize.com/sweetwaterwy24/"
COURTS_D = "https://www.wyocourts.gov/court/district-court-3rd-judicial-district-sweetwater-county/"
COURTS_C = "https://www.wyocourts.gov/court/circuit-court-of-the-3rd-judicial-district-sweetwater-county-state-of-wyoming-rock-springs/"
COURTS_KU = "https://www.wyocourts.gov/court/district-court-3rd-judicial-district-uinta-county/"
COURTS_KL = "https://www.wyocourts.gov/court/district-court-3rd-judicial-district-lincoln-county/"

def cms(name: str) -> str:
    from urllib.parse import quote
    return CMS + quote(name)

def doc(name: str) -> str:
    return cms("document_center/Departments/Clerk/Elections/" + name)

def sos_url(year: int) -> str:
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Sweetwater_County_General_PbP.pdf"

PG = {
    2010: (cms("2010 General Results.pdf"), "Sweetwater County official 2010 general election results"),
    2012: (doc("2012 General Election.pdf"), "Sweetwater County official 2012 general election results"),
    2014: (doc("2014 General Election.pdf"), "Sweetwater County official 2014 general election results"),
    2016: (doc("2016 General Election.pdf"), "Sweetwater County official 2016 general election results"),
    2018: (doc("2018 General Election Official Results.pdf"), "Sweetwater County official 2018 general election canvass"),
    2020: (cms("General Electiton Precinct Summary.pdf"), "Sweetwater County official 2020 general precinct summary (official filename typo: General Electiton Precinct Summary.pdf)"),
    2022: (cms("Sweetwater Summary Results Report Official.pdf"), "Sweetwater County official 2022 general election summary"),
    2024: (cms("General Election Summary.pdf"), "Sweetwater County official 2024 general election summary"),
    2026: (cms("Official Sweetwater Results.pdf"), "Sweetwater County official 2026 general election summary"),
}

def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}

def sos(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} Sweetwater general precinct-by-precinct summary", "url": sos_url(year)}

def courts(which="district") -> dict:
    urls = {
        "district": (COURTS_D, "Wyoming Judicial Branch official District Court, 3rd Judicial District, Sweetwater County page"),
        "circuit": (COURTS_C, "Wyoming Judicial Branch official Circuit Court of the 3rd Judicial District (Rock Springs) page"),
        "uinta-d": (COURTS_KU, "Wyoming Judicial Branch official District Court, 3rd Judicial District, Uinta County page"),
        "lincoln-d": (COURTS_KL, "Wyoming Judicial Branch official District Court, 3rd Judicial District, Lincoln County page"),
        "cdc": ("https://www.sweetwatercountywy.gov/departments/clerk_of_district_court/index.php", "Sweetwater County official Clerk of District Court department page"),
        "staff": ("https://www.sweetwatercountywy.gov/staff_directory/index.php", "Sweetwater County official staff directory"),
    }
    url, label = urls[which]
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
        ("WY-HICKS-LARRY", "Larry Hicks", "Larry", "Hicks"),
        ("WY-KOLB-JOHN-K", "John K. Kolb", "John", "Kolb", "K."),
        ("WY-JONES-STACY", "Stacy Jones", "Stacy", "Jones"),
        ("WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "Laura", "Pearson", "", "Laura Taliaferro Pearson; Laura Pearson; Laura Taliaferro"),
        ("WY-JAMES-TOM", "Tom James", "Tom", "James"),
        ("WY-HASTERT-JOHN-M", "John M. Hastert", "John", "Hastert", "M."),
        ("WY-ANSELMI-DALTON-LIISA", "Liisa Anselmi-Dalton", "Liisa", "Anselmi-Dalton"),
        ("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "Fred", "Baldwin", "A.", "Fred Baldwin"),
        ("WY-CRAFT-BERNADINE-L", "Bernadine L. Craft", "Bernadine", "Craft", "L."),
        ("WY-COOPER-STAN", "Stan Cooper", "Stan", "Cooper"),
        ("WY-THAYER-PAMELA", "Pamela Thayer", "Pamela", "Thayer", "", "Pam Thayer"),
        ("WY-BURKHART-DONALD", "Donald Burkhart", "Donald", "Burkhart"),
        ("WY-LARSON-JT", "J.T. Larson", "J.T.", "Larson", "", "Joshua Thomas (J.T.) Larson|Joshua Thomas Larson"),
        ("WY-BINGHAM-ELIZABETH", "Elizabeth Bingham", "Elizabeth", "Bingham"),
        ("WY-HEINER-SCOTT", "Scott Heiner", "Scott", "Heiner"),
        ("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "Kenneth", "Roberts", "D."),
        ("WY-CRANK-THOMAS-D", "Thomas D. Crank", "Thomas", "Crank", "D."),
        ("WY-WYLIE-CODY", "Cody Wylie", "Cody", "Wylie"),
        ("WY-BLAKE-STAN", "Stan Blake", "Stan", "Blake"),
        ("WY-BURT-MARSHALL-A", "Marshall A. Burt", "Marshall", "Burt", "A.", "Marshall Burt"),
        ("WY-DAVIS-BOB", "Bob Davis", "Bob", "Davis", "", 'Robert "Bob" Davis'),
        ("WY-OTOOLE-EAMON", "Eamon O'Toole", "Eamon", "O'Toole"),
        ("WY-PAXTON-JERRY", "Jerry Paxton", "Jerry", "Paxton"),
        ("WY-MCCANN-DARIN-M", "Darin M. McCann", "Darin", "McCann", "M.", "Darin McCann"),
        ("WY-WAMSLEY-JAMES", "James Wamsley", "James", "Wamsley"),
        ("WY-STITH-CLARK", "Clark Stith", "Clark", "Stith"),
        ("WY-BRADY-MARLENE", "Marlene Brady", "Marlene", "Brady"),
        ("WY-NIEMIEC-TONY", "Tony Niemiec", "Tony", "Niemiec"),
        ("WY-FREEMAN-JOHN-L", "John L. Freeman", "John", "Freeman", "L."),
        ("WY-DAYTON-JOANN", "Joann Dayton", "Joann", "Dayton", "", "JoAnn Dayton"),
        ("WY-WATT-STEPHEN", "Stephen Watt", "Stephen", "Watt"),
        ("WY-BAKER-MARK", "Mark Baker", "Mark", "Baker"),
        ("WY-JAGGI-ALLEN-M", "Allen M. Jaggi", "Allen", "Jaggi", "M."),
        ("WY-DAVISON-KATHLEEN", "Kathleen Davison", "Kathleen", "Davison", "", "Kathy Davison"),
        ("WY-BARBUTO-JOSEPH-M", "Joseph M. Barbuto", "Joseph", "Barbuto", "M.", "Joe M. Barbuto|Joe M Barbuto"),
        # county
        ("WY-SLAUGHTER-ROBB", "Robb Slaughter", "Robb", "Slaughter", "", "Robert D. Slaughter"),
        ("WY-RICHARDS-ISLAND", "Island Richards", "Island", "Richards"),
        ("WY-WEST-KEATON-D", "Keaton D. West", "Keaton", "West", "D."),
        ("WY-JONES-TAYLOR", "Taylor Jones", "Taylor", "Jones"),
        ("WY-THOMAN-MARY-E", "Mary E. Thoman", "Mary", "Thoman", "E."),
        ("WY-BUSHMAN-SHERRY", "Sherry Bushman", "Sherry", "Bushman"),
        ("WY-WENDLING-RANDAL", 'Randal "Doc" Wendling', "Randal", "Wendling", "", "Doc Wendling"),
        ("WY-KOLB-JOHN-K-COMM", "John K. Kolb", "John", "Kolb", "K."),  # same person as senator - MUST NOT use a second ID
        ("WY-WEST-REID-O", "Reid O. West", "Reid", "West", "O."),
        ("WY-SMITH-JEFFREY", "Jeffrey Smith", "Jeffrey", "Smith"),
        ("WY-LLOYD-ROY", "Roy Lloyd", "Roy", "Lloyd"),
        ("WY-SCHOENFELD-LAUREN", "Lauren Schoenfeld", "Lauren", "Schoenfeld"),
        ("WY-LANE-CINDY", "Cindy Lane", "Cindy", "Lane"),
        ("WY-DAVIS-DALE", "Dale Davis", "Dale", "Davis"),
        ("WY-COWAN-MARK", "S. Mark Cowan", "Mark", "Cowan", "S.", "Mark Cowan"),
        ("WY-DIVIS-DAVE", "Dave Divis", "Dave", "Divis"),
        ("WY-STACEY-MARIANNE", "Marianne Stacey", "Marianne", "Stacey"),
        ("WY-DRINKLE-PAT", "Pat Drinkle", "Pat", "Drinkle"),
        ("WY-RUBECK-PERRI", "Perri Rubeck", "Perri", "Rubeck"),
        ("WY-ERRAMOUSPE-DANIEL-E", "Daniel E. Erramouspe", "Daniel", "Erramouspe", "E.", "Dan Erramouspe|Daniel Erramouspe"),
        ("WY-GROSSNICKLE-JOHN", "John Grossnickle", "John", "Grossnickle"),
        ("WY-KAUMO-RICHARD-F", "Richard F. Kaumo", "Richard", "Kaumo", "F.", "Richard Kaumo"),
        ("WY-LOWELL-MIKE", "Mike Lowell", "Mike", "Lowell"),
        ("WY-CHETTERBOCK-AMANDA-L", "Amanda L. Chetterbock", "Amanda", "Chetterbock", "L.", "Amanda Chetterbock"),
        ("WY-BOBAK-DONNALEE", "Donnalee Bobak", "Donnalee", "Bobak"),
        ("WY-MAJHANOVICH-DALE-S", "Dale S. Majhanovich", "Dale", "Majhanovich", "S.", "Dale Majhanovich"),
        ("WY-SANDERS-TRAVIS-R", "Travis R. Sanders", "Travis", "Sanders", "R."),
        # judges
        ("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "Suzannah", "Robinson", "G."),
        ("WY-KASTE-JAMES-C", "James C. Kaste", "James", "Kaste", "C.", "James Kaste"),
        ("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "Joseph", "Bluemel", "B."),
        ("WY-LAVERY-RICHARD-L", "Richard L. Lavery", "Richard", "Lavery", "L."),
        ("WY-JAMES-NENA", "Nena James", "Nena", "James"),
        ("WY-PROKOS-JOHN-R", "John R. Prokos", "John", "Prokos", "R.", "John Prokos"),
        ("WY-JONES-CRAIG-L", "Craig L. Jones", "Craig", "Jones", "L."),
        ("WY-ZEBRE-FRANK-J", "Frank J. Zebre", "Frank", "Zebre", "J."),
        ("WY-GREER-MICHAEL-L", "Michael L. Greer", "Michael", "Greer", "L."),
        ("WY-CORPENING-GREGORY-S", "Gregory S. Corpening", "Gregory", "Corpening", "S."),
        ("WY-STOUT-E-DEAN", "E. Dean Stout", "E. Dean", "Stout"),
        ("WY-PETERSON-THAYNE-L", "Thayne L. Peterson", "Thayne", "Peterson", "L."),
        ("WY-DEERING-THOMAS", "Thomas Deering", "Thomas", "Deering"),
        # mayors / council frequent
        ("WY-BLAKE-STAN-MAYOR", "Stan Blake", "Stan", "Blake"),  # same person as H39 - reuse WY-BLAKE-STAN
        ("WY-RUST-PETE", "Pete Rust", "Pete", "Rust"),
        ("WY-MICKELSON-MAX", "Max Mickelson", "Max", "Mickelson"),
        ("WY-KAUMO-TIM", "Tim Kaumo", "Tim", "Kaumo"),
        ("WY-DEMSHAR-CARL-R", "Carl R. Demshar", "Carl", "Demshar", "R."),
        ("WY-PETERSON-MARK", "Mark Peterson", "Mark", "Peterson"),
        ("WY-VALERIO-ANSELMO", 'Anselmo "Hippy" Valerio', "Anselmo", "Valerio", "", "Hippy Valerio"),
        ("WY-STYVAR-JOHN", "John Styvar", "John", "Styvar"),
        ("WY-ALLEN-SANDY", "Sandy Allen", "Sandy", "Allen"),
        ("WY-MCCOLLUM-BRADLY", "Bradly McCollum", "Bradly", "McCollum"),
        ("WY-NIEMIEC-RICK", "Rick Niemiec", "Rick", "Niemiec"),
        ("WY-JERKE-KARLIN", "Karlin Jerke", "Karlin", "Jerke"),
        ("WY-RONEY-LARRY-CHIP", 'Larry "Chip" Roney', "Larry", "Roney", "", "Larry Chip Roney"),
        ("WY-ERICKSON-JOE", "Joe Erickson", "Joe", "Erickson"),
        ("WY-PHIPPS-ROBB", "Robb Phipps", "Robb", "Phipps"),
        ("WY-WILLIAMS-RONALD-L", "Ronald L. Williams", "Ronald", "Williams", "L."),
        ("WY-JOSEPH-JEAN", "Jean Joseph", "Jean", "Joseph"),
        ("WY-STEVENS-PAUL-D", "Paul D. Stevens", "Paul", "Stevens", "D."),
        ("WY-SHUTRAN-MICHAEL-S", "Michael S. Shutran", "Michael", "Shutran", "S.", "Michael Shane Shutran"),
        ("WY-KILLPACK-GARY", "Gary Killpack", "Gary", "Killpack"),
        ("WY-BERG-ROBERT-V", "Robert V. Berg", "Robert", "Berg", "V."),
        ("WY-MASER-JESSICA", "Jessica Maser", "Jessica", "Maser"),
        ("WY-ZIMMERMAN-JIM", "Jim Zimmerman", "Jim", "Zimmerman"),
        ("WY-DEMAS-JEANNIE", "Jeannie Demas", "Jeannie", "Demas", "", "Jeannie L. Demas"),
        ("WY-THOMPSON-DAVID-A", "David A. Thompson", "David", "Thompson", "A."),
        ("WY-PEDRI-DANIEL-J", "Daniel J. Pedri", "Daniel", "Pedri", "J."),
        ("WY-HANSON-RANDY", "Randy Hanson", "Randy", "Hanson"),
        ("WY-MILONAS-RICK", "Rick Milonas", "Rick", "Milonas"),
        ("WY-ZOTTI-ROBERT-B", "Robert B. Zotti", "Robert", "Zotti", "B.", "Rob Zotti"),
        ("WY-HICKERSON-LARRY", "Larry Hickerson", "Larry", "Hickerson"),
        ("WY-BETTOLO-BRENT", "Brent Bettolo", "Brent", "Bettolo"),
        ("WY-ALLEN-THOMAS", "Thomas Allen", "Thomas", "Allen"),
        ("WY-SAVAGE-TIMOTHY", "Timothy Savage", "Timothy", "Savage"),
        ("WY-HALTER-DAVID", "David Halter", "David", "Halter"),
        ("WY-MOSBEY-ROSE-M", "Rose M. Mosbey", "Rose", "Mosbey", "M."),
        ("WY-ARMSTRONG-JASON", "Jason Armstrong", "Jason", "Armstrong"),
    ]
    # Do not register WY-KOLB-JOHN-K-COMM or WY-BLAKE-STAN-MAYOR as separate people — fix below
    skip = {"WY-KOLB-JOHN-K-COMM", "WY-BLAKE-STAN-MAYOR"}
    for row in rows:
        if row[0] in skip:
            continue
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)

def legislature_and_county_terms():
    terms = []

    def add(pid, name, group, office, jur, a, b, ey, party="", **kw):
        srcs = kw.pop("sources", None)
        if srcs is None:
            srcs = [pg(ey)] if ey in PG else [sos(ey)]
        terms.append(T(
            person_id=pid, name=name, party=party,
            office_group=group, office=office, jurisdiction=jur,
            term_start=FM[a] if not isinstance(a, str) else a,
            term_end=FM[b] if not isinstance(b, str) else b,
            how_took_office=kw.pop("how_took_office", "elected"),
            election_year=ey, confidence=kw.pop("confidence", "high"),
            sources=srcs, **kw,
        ))

    # Senate: current Sweetwater seats S11, S12, S13, S14.
    add("WY-HICKS-LARRY", "Larry Hicks", "state-senate", "Senate District 11 (S11)", "Sweetwater County", 2015, 2019, 2014, "REP")
    add("WY-HICKS-LARRY", "Larry Hicks", "state-senate", "Senate District 11 (S11)", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-HICKS-LARRY", "Larry Hicks", "state-senate", "Senate District 11 (S11)", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-DAVIS-BOB", "Bob Davis", "state-senate", "Senate District 11 (S11)", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-CRAFT-BERNADINE-L", "Bernadine L. Craft", "state-senate", "Senate District 12 (S12)", "Sweetwater County", 2013, 2017, 2012, "DEM",
        sources=[sos(2012)], notes="Official 2012 SOS Sweetwater general PbP: Bernadine L. Craft (D), 5,260 to 152 write-ins.")
    add("WY-ANSELMI-DALTON-LIISA", "Liisa Anselmi-Dalton", "state-senate", "Senate District 12 (S12)", "Sweetwater County", 2017, 2021, 2016, "DEM",
        sources=[sos(2016)])
    add("WY-KOLB-JOHN-K", "John K. Kolb", "state-senate", "Senate District 12 (S12)", "Sweetwater County", 2021, 2025, 2020, "REP",
        sources=[sos(2020), pg(2020)])
    add("WY-KOLB-JOHN-K", "John K. Kolb", "state-senate", "Senate District 12 (S12)", "Sweetwater County", 2025, 2029, 2024, "REP")

    add("WY-HASTERT-JOHN-M", "John M. Hastert", "state-senate", "Senate District 13 (S13)", "Sweetwater County", 2011, 2015, 2010, "DEM",
        sources=[sos(2010)], notes="Official 2010 SOS Sweetwater general PbP names John M. Hastert (D) as the S13 candidate (write-ins only in opposition on that header).")
    add("WY-HASTERT-JOHN-M", "John M. Hastert", "state-senate", "Senate District 13 (S13)", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-JAMES-TOM", "Tom James", "state-senate", "Senate District 13 (S13)", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-JONES-STACY", "Stacy Jones", "state-senate", "Senate District 13 (S13)", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-JONES-STACY", "Stacy Jones", "state-senate", "Senate District 13 (S13)", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-COOPER-STAN", "Stan Cooper", "state-senate", "Senate District 14 (S14)", "Sweetwater County", 2013, 2017, 2012, "REP",
        sources=[sos(2012)], notes="Official 2012 SOS Sweetwater general PbP names Stan Cooper (R) and John Vincent Love (CTRY). Cooper is the official named Republican nominee; Sweetwater precincts on that PbP report Cooper leading. Encoded from the official SOS candidate header and precinct lines.")
    # Safer: I should not encode Cooper as winner if I didn't confirm totals. Let me check - I didn't extract S14 2012 totals. Leave 2013-2017 S14 only if totals exist.
    # I'll keep Cooper with a note only if I add totals later. For now I'll verify... I didn't have totals. REMOVE Cooper if uncertain?
    # Official SOS names both candidates. Without totals I should not declare a winner.
    # I'll delete the Cooper term after building this string - actually I'll leave a placeholder and remove if needed.
    add("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-senate", "Senate District 14 (S14)", "Sweetwater County", 2017, 2021, 2016, "REP",
        sources=[sos(2016)], notes="Official 2016 SOS statewide Senate summary totals: Fred Baldwin 6,939, Anselm Sedey 1,237. Official Sweetwater portion: Baldwin 1,560, Sedey 329.")
    add("WY-BALDWIN-FRED-A", "Fred Baldwin", "state-senate", "Senate District 14 (S14)", "Sweetwater County", 2021, 2025, 2020, "REP",
        sources=[sos(2020)], notes="Official 2020 SOS statewide Senate summary totals: Fred Baldwin 7,779. Official Sweetwater portion: 1,640.")
    add("WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "state-senate", "Senate District 14 (S14)", "Sweetwater County", 2025, 2029, 2024, "REP",
        notes="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Sweetwater portion: 1,351. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA.")

    # House
    add("WY-BURKHART-DONALD", "Donald Burkhart", "state-house", "House District 15 (H15)", "Sweetwater County", 2023, 2025, 2022, "REP",
        notes="Official 2022 SOS statewide House summary totals: Donald Burkhart 1,552, Gonzales 602. Official Sweetwater portion: Burkhart 37, Gonzales 2. Also covers Carbon County.")
    add("WY-THAYER-PAMELA", "Pamela Thayer", "state-house", "House District 15 (H15)", "Sweetwater County", 2025, 2027, 2024, "REP",
        notes="Official 2024 SOS statewide House summary totals: Pamela Thayer 2,790. Official Sweetwater portion: 46. Also covers Carbon County.")
    add("WY-THAYER-PAMELA", "Pamela Thayer", "state-house", "House District 15 (H15)", "Sweetwater County", 2027, 2029, 2026, "REP",
        notes="Official 2026 SOS statewide House summary totals: Pamela Thayer 1,499, Cheryl Hulme 398. Official Sweetwater portion: Thayer 28, Hulme 6. Also covers Carbon County.")

    add("WY-CRAFT-BERNADINE-L", "Bernadine L. Craft", "state-house", "House District 17 (H17)", "Sweetwater County", 2011, 2013, 2010, "DEM",
        sources=[sos(2010)], notes="Official 2010 SOS Sweetwater general PbP totals: Bernadine L. Craft (D) 1,244, Stephen Watt (R) 994.")
    add("WY-WATT-STEPHEN", "Stephen Watt", "state-house", "House District 17 (H17)", "Sweetwater County", 2013, 2015, 2012, "REP",
        sources=[pg(2012)], notes="Official 2012 clerk general: Stephen Watt (R) 1,680, Joann Dayton (D) 1,354.")
    add("WY-DAYTON-JOANN", "Joann Dayton", "state-house", "House District 17 (H17)", "Sweetwater County", 2015, 2017, 2014, "DEM")
    add("WY-DAYTON-JOANN", "JoAnn Dayton", "state-house", "House District 17 (H17)", "Sweetwater County", 2017, 2019, 2016, "DEM", sources=[sos(2016)])
    add("WY-DAYTON-JOANN", "Joann Dayton", "state-house", "House District 17 (H17)", "Sweetwater County", 2019, 2021, 2018, "DEM")
    add("WY-BANKS-CHAD-M", "Chad M. Banks", "state-house", "House District 17 (H17)", "Sweetwater County", 2021, 2023, 2020, "DEM", sources=[sos(2020)])
    add("WY-LARSON-JT", "J.T. Larson", "state-house", "House District 17 (H17)", "Sweetwater County", 2023, 2025, 2022, "REP")
    add("WY-LARSON-JT", "J.T. Larson", "state-house", "House District 17 (H17)", "Sweetwater County", 2025, 2027, 2024, "REP")
    add("WY-BINGHAM-ELIZABETH", "Elizabeth Bingham", "state-house", "House District 17 (H17)", "Sweetwater County", 2027, 2029, 2026, "REP")

    add("WY-JAGGI-ALLEN-M", "Allen M. Jaggi", "state-house", "House District 18 (H18)", "Sweetwater County", 2011, 2013, 2010, "REP", sources=[sos(2010)])
    add("WY-DAVISON-KATHLEEN", "Kathleen Davison", "state-house", "House District 18 (H18)", "Sweetwater County", 2013, 2015, 2012, "REP", sources=[sos(2012)])
    add("WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-house", "House District 18 (H18)", "Sweetwater County", 2015, 2017, 2014, "REP",
        notes="Official 2014 SOS statewide House summary totals: Fred A. Baldwin 2,297, Michele Irwin 719. Official Sweetwater portion: Baldwin 807, Irwin 360.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Sweetwater County", "2016-08-31", FM[2017], 2016, "REP",
        how_took_office="elected",
        sources=[{"label": "Sweetwater County official 2016 special election, House District 18",
                  "url": cms("document_center/Departments/Clerk/Elections/2016 Special Election HD 18.pdf")}],
        notes="Official August 31, 2016 special election (Republican ballot): Scott Heiner 72. Encoded from that official special through January 2017, when the official 2016 general winner takes office.")
    add("WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Sweetwater County", 2017, 2019, 2016, "REP", sources=[sos(2016)],
        notes="Official 2016 SOS statewide House summary totals: Thomas D. Crank 3,595, Michele Irwin 880. Official Sweetwater portion: Crank 1,427, Irwin 449.")
    add("WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Sweetwater County", 2019, 2021, 2018, "REP",
        notes="Official 2018 SOS statewide House summary totals: Thomas D. Crank 3,088. Official Sweetwater portion: 1,241.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Sweetwater County", 2021, 2023, 2020, "REP", sources=[sos(2020)],
        notes="Official 2020 SOS statewide House summary totals: Scott Heiner 3,981. Official Sweetwater portion: 1,621.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Sweetwater County", 2023, 2025, 2022, "REP",
        notes="Official 2022 SOS statewide House summary totals: Scott Heiner 2,689, Dennis B. Laughlin 590. Official Sweetwater portion: Heiner 855, Laughlin 319.")
    add("WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Sweetwater County", 2025, 2027, 2024, "REP",
        notes="Official 2024 SOS statewide House summary totals: Scott Heiner 3,781. Official Sweetwater portion: 1,342.")
    add("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "state-house", "House District 18 (H18)", "Sweetwater County", 2027, 2029, 2026, "REP",
        notes="Official 2026 SOS statewide House summary totals: Kenneth D. Roberts 2,691. Official Sweetwater portion: 879.")

    add("WY-BLAKE-STAN", "Stan Blake", "state-house", "House District 39 (H39)", "Sweetwater County", 2011, 2013, 2010, "DEM", sources=[sos(2010)])
    add("WY-BLAKE-STAN", "Stan Blake", "state-house", "House District 39 (H39)", "Sweetwater County", 2013, 2015, 2012, "DEM", sources=[sos(2012)])
    add("WY-BLAKE-STAN", "Stan Blake", "state-house", "House District 39 (H39)", "Sweetwater County", 2015, 2017, 2014, "DEM")
    add("WY-BLAKE-STAN", "Stan Blake", "state-house", "House District 39 (H39)", "Sweetwater County", 2017, 2019, 2016, "DEM", sources=[sos(2016)])
    add("WY-BLAKE-STAN", "Stan Blake", "state-house", "House District 39 (H39)", "Sweetwater County", 2019, 2021, 2018, "DEM")
    add("WY-BURT-MARSHALL-A", "Marshall A. Burt", "state-house", "House District 39 (H39)", "Sweetwater County", 2021, 2023, 2020, "LIB",
        sources=[sos(2020)], notes="Official 2020 SOS Sweetwater general PbP totals: Marshall A. Burt (L) 1,696, Stan Blake (D) 1,421.")
    add("WY-WYLIE-CODY", "Cody Wylie", "state-house", "House District 39 (H39)", "Sweetwater County", 2023, 2025, 2022, "REP")
    add("WY-WYLIE-CODY", "Cody Wylie", "state-house", "House District 39 (H39)", "Sweetwater County", 2025, 2027, 2024, "REP")
    add("WY-WYLIE-CODY", "Cody Wylie", "state-house", "House District 39 (H39)", "Sweetwater County", 2027, 2029, 2026, "REP")

    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Sweetwater County", 2013, 2015, 2012, "REP", sources=[sos(2012)])
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Sweetwater County", 2015, 2017, 2014, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Sweetwater County", 2017, 2019, 2016, "REP", sources=[sos(2016)])
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Sweetwater County", 2019, 2021, 2018, "REP")
    add("WY-PAXTON-JERRY", "Jerry Paxton", "state-house", "House District 47 (H47)", "Sweetwater County", 2021, 2023, 2020, "REP", sources=[sos(2020)])
    add("WY-DAVIS-BOB", 'Robert "Bob" Davis', "state-house", "House District 47 (H47)", "Sweetwater County", 2023, 2025, 2022, "REP")
    add("WY-DAVIS-BOB", "Bob Davis", "state-house", "House District 47 (H47)", "Sweetwater County", 2025, 2027, 2024, "REP")
    add("WY-OTOOLE-EAMON", "Eamon O'Toole", "state-house", "House District 47 (H47)", "Sweetwater County", 2027, 2029, 2026, "REP")

    add("WY-BARBUTO-JOSEPH-M", "Joseph M. Barbuto", "state-house", "House District 48 (H48)", "Sweetwater County", 2011, 2013, 2010, "DEM", sources=[sos(2010)])
    add("WY-BAKER-MARK", "Mark Baker", "state-house", "House District 48 (H48)", "Sweetwater County", 2015, 2017, 2014, "REP")
    add("WY-BAKER-MARK", "Mark Baker", "state-house", "House District 48 (H48)", "Sweetwater County", 2017, 2019, 2016, "REP", sources=[sos(2016)])
    add("WY-STITH-CLARK", "Clark Stith", "state-house", "House District 48 (H48)", "Sweetwater County", 2019, 2021, 2018, "REP")
    add("WY-STITH-CLARK", "Clark Stith", "state-house", "House District 48 (H48)", "Sweetwater County", 2021, 2023, 2020, "REP", sources=[sos(2020)])
    add("WY-STITH-CLARK", "Clark Stith", "state-house", "House District 48 (H48)", "Sweetwater County", 2023, 2025, 2022, "REP")
    add("WY-MCCANN-DARIN-M", "Darin M. McCann", "state-house", "House District 48 (H48)", "Sweetwater County", 2025, 2027, 2024, "REP")
    add("WY-WAMSLEY-JAMES", "James Wamsley", "state-house", "House District 48 (H48)", "Sweetwater County", 2027, 2029, 2026, "REP")
    # 2012 H48 Baker vs Barbuto — need totals before encoding 2013-2015. Official 2012 clerk had Baker 1,723 49.48% (from messy two-column). Close race. Don't encode 2013-2015 H48 without confirmed totals.

    add("WY-FREEMAN-JOHN-L", "John L. Freeman", "state-house", "House District 60 (H60)", "Sweetwater County", 2013, 2015, 2012, "DEM", sources=[sos(2012)])
    add("WY-FREEMAN-JOHN-L", "John L. Freeman", "state-house", "House District 60 (H60)", "Sweetwater County", 2015, 2017, 2014, "DEM")
    add("WY-FREEMAN-JOHN-L", "John L. Freeman", "state-house", "House District 60 (H60)", "Sweetwater County", 2017, 2019, 2016, "",
        sources=[sos(2016)], notes="Official 2016 SOS Sweetwater general PbP totals: John L. Freeman 3,088 to 116 write-ins. Official 2016 SOS header prints Freeman (R); official 2012 SOS and official 2014 and 2018 clerk ballots print John L. Freeman (D). Party is left blank here rather than choosing between official labels.")
    add("WY-FREEMAN-JOHN-L", "John L. Freeman", "state-house", "House District 60 (H60)", "Sweetwater County", 2019, 2021, 2018, "DEM")
    add("WY-BAKER-MARK", "Mark Baker", "state-house", "House District 60 (H60)", "Sweetwater County", 2021, 2023, 2020, "REP", sources=[sos(2020)])
    add("WY-NIEMIEC-TONY", "Tony Niemiec", "state-house", "House District 60 (H60)", "Sweetwater County", 2023, 2025, 2022, "REP")
    add("WY-BRADY-MARLENE", "Marlene Brady", "state-house", "House District 60 (H60)", "Sweetwater County", 2025, 2027, 2024, "REP")
    add("WY-NIEMIEC-TONY", "Tony Niemiec", "state-house", "House District 60 (H60)", "Sweetwater County", 2027, 2029, 2026, "REP")

    # Need Chad Banks registered
    # Commissioners (5-member; midterm VF3, presidential VF2). 2016 VF2 class not yet collected from the official 2016 scan.
    add("WY-KOLB-JOHN-K", "John K. Kolb", "county", "County Commissioner", "Sweetwater County", 2015, 2019, 2014, "REP")
    add("WY-WENDLING-RANDAL", 'Randal "Doc" Wendling', "county", "County Commissioner", "Sweetwater County", 2015, 2019, 2014, "IND")
    add("WY-WEST-REID-O", "Reid O. West", "county", "County Commissioner", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-WENDLING-RANDAL", 'Randal "Doc" Wendling', "county", "County Commissioner", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-SMITH-JEFFREY", "Jeffrey Smith", "county", "County Commissioner", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-LLOYD-ROY", "Roy Lloyd", "county", "County Commissioner", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-THOMAN-MARY-E", "Mary E. Thoman", "county", "County Commissioner", "Sweetwater County", 2021, 2025, 2020, "REP",
        sources=[pg(2020)], notes="Official 2020 general precinct summary Vote-For-2 totals: Mary E. Thoman 9,704 and Lauren Schoenfeld 9,053 (Republican columns).")
    add("WY-SCHOENFELD-LAUREN", "Lauren Schoenfeld", "county", "County Commissioner", "Sweetwater County", 2021, 2025, 2020, "REP",
        sources=[pg(2020)], notes="Official 2020 general precinct summary Vote-For-2 totals: Mary E. Thoman 9,704 and Lauren Schoenfeld 9,053 (Republican columns).")
    add("WY-SLAUGHTER-ROBB", "Robb Slaughter", "county", "County Commissioner", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-RICHARDS-ISLAND", "Island Richards", "county", "County Commissioner", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-WEST-KEATON-D", "Keaton D. West", "county", "County Commissioner", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-THOMAN-MARY-E", "Mary E. Thoman", "county", "County Commissioner", "Sweetwater County", 2025, 2029, 2024, "REP")
    add("WY-JONES-TAYLOR", "Taylor Jones", "county", "County Commissioner", "Sweetwater County", 2025, 2029, 2024, "REP")
    add("WY-WEST-KEATON-D", "Keaton D. West", "county", "County Commissioner", "Sweetwater County", 2027, 2031, 2026, "REP")
    add("WY-RICHARDS-ISLAND", "Island Richards", "county", "County Commissioner", "Sweetwater County", 2027, 2031, 2026, "REP")
    add("WY-BUSHMAN-SHERRY", "Sherry Bushman", "county", "County Commissioner", "Sweetwater County", 2027, 2031, 2026, "REP")

    # Row offices (midterm)
    add("WY-DAVIS-DALE", "Dale Davis", "county", "County Clerk", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-LANE-CINDY", "Cindy Lane", "county", "County Clerk", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-LANE-CINDY", "Cindy Lane", "county", "County Clerk", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-DAVIS-DALE", "Dale Davis", "county", "County Clerk", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-SLAUGHTER-ROBB", "Robb Slaughter", "county", "County Treasurer", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-SLAUGHTER-ROBB", "Robert D. Slaughter", "county", "County Treasurer", "Sweetwater County", 2019, 2023, 2018, "DEM")
    add("WY-COWAN-MARK", "Mark Cowan", "county", "County Treasurer", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-COWAN-MARK", "S. Mark Cowan", "county", "County Treasurer", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-DRINKLE-PAT", "Pat Drinkle", "county", "County Assessor", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-DIVIS-DAVE", "Dave Divis", "county", "County Assessor", "Sweetwater County", 2019, 2023, 2018, "DEM")
    add("WY-DIVIS-DAVE", "Dave Divis", "county", "County Assessor", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-STACEY-MARIANNE", "Marianne Stacey", "county", "County Assessor", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-LOWELL-MIKE", "Mike Lowell", "county", "County Sheriff", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-GROSSNICKLE-JOHN", "John Grossnickle", "county", "County Sheriff", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-GROSSNICKLE-JOHN", "John Grossnickle", "county", "County Sheriff", "Sweetwater County", 2023, 2027, 2022, "REP",
        notes="Official 2022 general winner. The official Sweetwater County staff directory retrieved 2026-11-24 lists the Sheriff office as Vacant and lists Rich Fischer as a Lieutenant, not as Sheriff. No official appointment of an interim sheriff was found. This official 2022 term is left in place through January 2027 for January snapshots.")
    add("WY-KAUMO-RICHARD-F", "Richard F. Kaumo", "county", "County Sheriff", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-ERRAMOUSPE-DANIEL-E", "Daniel Erramouspe", "county", "County Attorney", "Sweetwater County", 2015, 2019, 2014, "REP")
    add("WY-ERRAMOUSPE-DANIEL-E", "Daniel Erramouspe", "county", "County Attorney", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-ERRAMOUSPE-DANIEL-E", "Dan Erramouspe", "county", "County Attorney", "Sweetwater County", 2023, 2027, 2022, "REP")
    add("WY-ERRAMOUSPE-DANIEL-E", "Daniel E. Erramouspe", "county", "County Attorney", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-BOBAK-DONNALEE", "Donnalee Bobak", "county", "Clerk of District Court", "Sweetwater County", 2015, 2019, 2014, "REP")
    add("WY-BOBAK-DONNALEE", "Donnalee Bobak", "county", "Clerk of District Court", "Sweetwater County", 2019, 2023, 2018, "REP")
    add("WY-BOBAK-DONNALEE", "Donnalee Bobak", "county", "Clerk of District Court", "Sweetwater County", 2023, 2027, 2022, "REP",
        notes="Official 2022 general winner. Official Sweetwater County Clerk of District Court department page and official Wyoming Judicial Branch 3rd JD Sweetwater district page (retrieved 2026-11-24) name Amanda L. Chetterbock as the current clerk. No official appointment date for that mid-term change was found, so January snapshots keep the official 2022 elected term through January 2027.")
    add("WY-CHETTERBOCK-AMANDA-L", "Amanda L. Chetterbock", "county", "Clerk of District Court", "Sweetwater County", 2027, 2031, 2026, "REP")

    add("WY-MAJHANOVICH-DALE-S", "Dale S. Majhanovich", "county", "County Coroner", "Sweetwater County", 2015, 2019, 2014, "DEM")
    add("WY-MAJHANOVICH-DALE-S", "Dale S. Majhanovich", "county", "County Coroner", "Sweetwater County", 2019, 2023, 2018, "DEM")
    add("WY-MAJHANOVICH-DALE-S", "Dale S. Majhanovich", "county", "County Coroner", "Sweetwater County", 2023, 2027, 2022, "DEM")
    add("WY-SANDERS-TRAVIS-R", "Travis R. Sanders", "county", "County Coroner", "Sweetwater County", 2027, 2031, 2026, "REP")

    # Remove uncertain 2012 S14 Cooper term if I still included it — I'll delete it in a post-pass below
    terms = [t for t in terms if not (
        t.get("person_id") == "WY-COOPER-STAN" and t.get("office") == "Senate District 14 (S14)"
    )]
    return terms

def register_more_people(P):
    P("WY-BANKS-CHAD-M", "Chad M. Banks", "Chad", "Banks", "M.", aliases="", minted=True)
    rows = [
        ("WY-FREEZE-JACKIE-L", "Jackie L. Freeze", "Jackie", "Freeze", "L.", "Jackie Freeze"),
        ("WY-JESSEN-JAMES", "James Jessen", "James", "Jessen"),
        ("WY-TRAVIS-LINDSEY", "Lindsey Travis", "Lindsey", "Travis"),
        ("WY-NELSON-STACEY", "Stacey Nelson", "Stacey", "Nelson"),
        ("WY-GRAY-LEO", "Leo Gray", "Leo", "Gray"),
        ("WY-DEVRIES-DANELLA", "Danella DeVries", "Danella", "DeVries"),
        ("WY-HAGER-HEATHER", "Heather Hager", "Heather", "Hager"),
        ("WY-ROSSETTI-KORI-L", "Kori L. Rossetti", "Kori", "Rossetti", "L."),
        ("WY-WILSON-TOM", "Tom Wilson", "Tom", "Wilson"),
        ("WY-FLOM-DANIEL", "Daniel Flom", "Daniel", "Flom"),
        ("WY-SHONING-KENNY-JR", "Kenny Shoning Jr", "Kenny", "Shoning"),
        ("WY-SEPPIE-COLE", "Cole Seppie", "Cole", "Seppie"),
        ("WY-FRANKS-CHAD", "Chad Franks", "Chad", "Franks", "", "Dr. Chad Franks"),
        ("WY-WRIGHT-COLE", "Cole Wright", "Cole", "Wright"),
        ("WY-SORENSEN-JOSHUA-P", "Joshua P. Sorensen", "Joshua", "Sorensen", "P."),
        ("WY-GARDNER-MATTHEW", "Matthew Gardner", "Matthew", "Gardner"),
        ("WY-DRINKLE-MANDY", "Mandy Drinkle", "Mandy", "Drinkle"),
        ("WY-THOMAN-TOMMY", "Tommy Thoman", "Tommy", "Thoman"),
        ("WY-DAVIS-TATE", "Tate Davis", "Tate", "Davis"),
        ("WY-FOLEY-MICHELLE-J", "Michelle J. Foley", "Michelle", "Foley", "J."),
        ("WY-MARSHALL-TIFFANY", "Tiffany Marshall", "Tiffany", "Marshall"),
        ("WY-KNEZOVICH-OZZIE", "Ozzie Knezovich", "Ozzie", "Knezovich"),
        ("WY-LEE-ROBBIE", "Robbie Lee", "Robbie", "Lee"),
        ("WY-LORIMER-KENNETH", "Kenneth Lorimer", "Kenneth", "Lorimer"),
        ("WY-KOURBELAS-NEIL", "Neil Kourbelas", "Neil", "Kourbelas"),
        ("WY-ALLEN-STEPHEN-P", "Stephen P. Allen", "Stephen", "Allen", "P."),
        ("WY-DONALDSON-VERONICA-K", "Veronica K. Donaldson", "Veronica", "Donaldson", "K."),
        ("WY-MEREDITH-JENISSA", "Jenissa Meredith", "Jenissa", "Meredith"),
        ("WY-STANTON-DANIEL", "Daniel Stanton", "Daniel", "Stanton", "", "Daniel D. Stanton"),
        ("WY-GUNTER-SANDEE", "Sandee Gunter", "Sandee", "Gunter"),
        ("WY-HARGROVE-ROSS-M", "Ross M. Hargrove", "Ross", "Hargrove", "M."),
        ("WY-EDWARDS-JACLYN", "Jaclyn Edwards", "Jaclyn", "Edwards"),
        ("WY-GORDON-ROBERT-L", 'Robert L. "Bob" Gordon', "Robert", "Gordon", "L."),
        ("WY-ROBBINS-REED-W", "Reed W. Robbins", "Reed", "Robbins", "W."),
        ("WY-SORENSEN-PATSY-A", "Patsy A. Sorensen", "Patsy", "Sorensen", "A."),
        ("WY-DICKINSON-JEAN-M", "Jean M. Dickinson", "Jean", "Dickinson", "M."),
        ("WY-FOLKS-AARON", "Aaron Folks", "Aaron", "Folks"),
        ("WY-FOLKS-LARRY-B", "Larry B. Folks", "Larry", "Folks", "B."),
        ("WY-FLOYD-KEITH", "Keith Floyd", "Keith", "Floyd"),
        ("WY-FRITS-CHASE", "Chase Frits", "Chase", "Frits"),
        ("WY-BARELA-BARBARA", "Barbara Barela", "Barbara", "Barela"),
        ("WY-WALDNER-MARINDA", "Marinda Waldner", "Marinda", "Waldner"),
        ("WY-DAVIS-DUSTIN", "Dustin Davis", "Dustin", "Davis"),
        ("WY-GOFF-JENNIFER", "Jennifer Goff", "Jennifer", "Goff"),
        ("WY-MANSIR-DAWN", "Dawn Mansir", "Dawn", "Mansir"),
        ("WY-HOWEY-VERN", "Vern Howey", "Vern", "Howey"),
        ("WY-NYGAARD-KIMBERLY", "Kimberly Nygaard", "Kimberly", "Nygaard", "", "Kimberly G. Nygaard"),
        ("WY-MCCUNE-THOMAS", "Thomas McCune", "Thomas", "McCune"),
        ("WY-MERRITT-SANDRA-S", "Sandra S. Merritt", "Sandra", "Merritt", "S."),
        ("WY-WOLFE-DAVID-C", "David C. Wolfe", "David", "Wolfe", "C."),
        ("WY-DAVEY-JOANNE", "Joanne Davey", "Joanne", "Davey"),
        ("WY-ANDREWS-GEORGE", "George Andrews", "George", "Andrews"),
        ("WY-PERRY-ROBERT-A", "Robert A. Perry", "Robert", "Perry", "A."),
        ("WY-RAUCH-SETH-J", "Seth J. Rauch", "Seth", "Rauch", "J."),
        ("WY-LOCKHART-MATT", "Matt Lockhart", "Matt", "Lockhart"),
        ("WY-WILSON-ALLAN", "Allan Wilson", "Allan", "Wilson"),
        ("WY-BARNEY-TED-L", "Ted L. Barney", "Ted", "Barney", "L."),
        ("WY-ARMSTRONG-JASON", "Jason Armstrong", "Jason", "Armstrong"),
        ("WY-MOSBEY-ROSE-M", "Rose M. Mosbey", "Rose", "Mosbey", "M."),
        ("WY-NICHOLS-JUNE", "June Nichols", "June", "Nichols"),
        ("WY-BRANTLEY-SHERRY", "Sherry Brantley", "Sherry", "Brantley"),
        ("WY-DUNIVIN-SHANA-L", "Shana L. Dunivin", "Shana", "Dunivin", "L."),
        ("WY-SPICER-THOMAS-E", "Thomas E. Spicer", "Thomas", "Spicer", "E."),
        ("WY-BOETTCHER-DICK", "Dick Boettcher", "Dick", "Boettcher"),
        ("WY-JOST-GEORGE", "George Jost", "George", "Jost"),
        ("WY-ROBINSON-TIM-S", "Tim S. Robinson", "Tim", "Robinson", "S.", "Tim Robinson"),
        ("WY-HESTER-CARLA", "Carla Hester", "Carla", "Hester"),
        ("WY-CLARK-REGINA-M", "Regina M. Clark", "Regina", "Clark", "M."),
        ("WY-SUMMERS-ANDREA-R", "Andrea R. Summers", "Andrea", "Summers", "R."),
        ("WY-BURRIS-THOMAS-E", "Thomas E. Burris", "Thomas", "Burris", "E."),
        ("WY-ANDERSON-STEPHANIE", "Stephanie Anderson", "Stephanie", "Anderson"),
        ("WY-ROBISON-LISA", "Lisa Robison", "Lisa", "Robison"),
        ("WY-CLAWSON-LOWELL", "Lowell Clawson", "Lowell", "Clawson"),
        ("WY-THORNTON-ALAN", "Alan Thornton", "Alan", "Thornton"),
        ("WY-THORNTON-AUDRA", "Audra Thornton", "Audra", "Thornton"),
        ("WY-MCFALL-BUTCH", "Butch McFall", "Butch", "McFall"),
        ("WY-CHAVEZ-MICHELLE", "Michelle Chavez", "Michelle", "Chavez"),
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True)


def judicial_terms():
    terms = []

    def dist(pid, name, a, b, ey=None, **kw):
        srcs = kw.pop("sources", [pg(ey)] if ey in PG else [courts("district")])
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="District Judge, 3rd Judicial District",
            jurisdiction="3rd Judicial District",
            term_start=a if isinstance(a, str) else FM[a],
            term_end=b if isinstance(b, str) else FM[b],
            how_took_office=kw.pop("how_took_office", "retained" if ey else "appointed"),
            election_year=ey, confidence=kw.pop("confidence", "high"), sources=srcs, **kw,
        ))

    def circ(pid, name, a, b, ey=None, **kw):
        srcs = kw.pop("sources", [pg(ey)] if ey in PG else [courts("circuit")])
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office="Circuit Judge, 3rd Judicial District",
            jurisdiction="3rd Judicial District",
            term_start=a if isinstance(a, str) else FM[a],
            term_end=b if isinstance(b, str) else FM[b],
            how_took_office=kw.pop("how_took_office", "retained" if ey else "appointed"),
            election_year=ey, confidence=kw.pop("confidence", "high"), sources=srcs, **kw,
        ))

    dist("WY-LAVERY-RICHARD-L", "Richard L. Lavery", 2015, 2021, 2014,
         notes="Official 2014 clerk: JUDGE RICHARD L LAVERY, YES.")
    dist("WY-JAMES-NENA", "Nena James", 2015, 2021, 2014,
         notes="Official 2014 clerk: JUDGE NENA JAMES, YES.")
    dist("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "2019-10-01", FM[2021], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("district")],
         notes="Official Wyoming Judicial Branch 3rd JD Sweetwater district page: appointed October 2019 (day unstated; term_start 2019-10-01, medium), retained November 2020, term expires January 2027, stands for retention November 2026.")
    dist("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", 2021, 2027, 2020,
         sources=[sos(2020), courts("district")],
         notes="Official 2020 retention (stands for retention November 2020 on the official court page). Official 2026 clerk line FOR JUDGE C OF THE DISTRICT COURT, YES, is unnamed; identified as Suzannah G. Robinson from the official 3rd JD Sweetwater district page.")
    dist("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", 2027, 2033, 2026,
         sources=[pg(2026), courts("district")],
         notes="Official 2026 clerk: FOR JUDGE C OF THE DISTRICT COURT, YES, no given name on the clerk line. Identified as Suzannah G. Robinson from the official Wyoming Judicial Branch 3rd JD Sweetwater district page (stands for retention November 2026; term expires January 2027).")
    dist("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "2015-01-01", FM[2023], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("lincoln-d")],
         notes="Official Wyoming Judicial Branch 3rd JD Lincoln County district page: appointed January 2015 (day unstated; term_start 2015-01-01, medium), retained November 2022, term expires January 2029.")
    dist("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", 2023, 2029, 2022,
         sources=[pg(2022), courts("lincoln-d")],
         notes="Official 2022 clerk JUDGE A DISTRICT COURT, YES, unnamed on the clerk line. Identified as Joseph B. Bluemel from the official 3rd JD Lincoln County district page (retained November 2022, term expires January 2029).")
    dist("WY-KASTE-JAMES-C", "James C. Kaste", "2022-10-01", FM[2025], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("uinta-d")],
         notes="Official Wyoming Judicial Branch 3rd JD Uinta County district page: appointed October 2022 (day unstated; term_start 2022-10-01, medium), retained November 2024, term expires January 2031.")
    dist("WY-KASTE-JAMES-C", "James C. Kaste", 2025, 2031, 2024,
         sources=[pg(2024), courts("uinta-d")],
         notes="Official 2024 clerk: JAMES KASTE FOR JUDGE D OF THE DISTRICT COURT. Full name James C. Kaste from the official 3rd JD Uinta County district page.")
    dist("WY-STITH-CLARK", "Clark Stith", "2026-04-01", FM[2029], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("district")],
         notes="Official Wyoming Judicial Branch 3rd JD Sweetwater district page: appointed April 2026 (day unstated; term_start 2026-04-01, medium), term expires January 2029, stands for retention November 2028.")

    circ("WY-PROKOS-JOHN-R", "John R. Prokos", "2013-06-01", FM[2015], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("circuit")],
         notes="Official Wyoming Judicial Branch 3rd JD Rock Springs circuit page: appointed June 2013 (day unstated; term_start 2013-06-01, medium), term expires January 2027, stands for retention November 2026.")
    circ("WY-PROKOS-JOHN-R", "John R. Prokos", 2015, 2019, 2014)
    circ("WY-PROKOS-JOHN-R", "John R. Prokos", 2019, 2023, 2018)
    circ("WY-PROKOS-JOHN-R", "John R. Prokos", 2023, 2027, 2022)
    circ("WY-PROKOS-JOHN-R", "John R. Prokos", 2027, 2031, 2026,
         notes="Official 2026 clerk: JOHN R. PROKOS FOR CIRCUIT COURT JUDGE, YES. Official court page: term expires January 2027, stands for retention November 2026.")
    circ("WY-JONES-CRAIG-L", "Craig L. Jones", 2015, 2019, 2014,
         sources=[pg(2014), pg(2018)],
         notes="Official 2014 clerk line JUDGE JONES, YES. Full name from official 2018 clerk: RETAIN JUDGE CRAIG L JONES.")
    circ("WY-ZEBRE-FRANK-J", "Frank J. Zebre", 2015, 2019, 2014,
         sources=[pg(2014), sos(2010), pg(2018)],
         notes="Official 2014 clerk line JUDGE ZEBRE, YES. Full name Frank J. Zebre from official 2010 SOS Sweetwater PbP and official 2018 clerk RETAIN JUDGE FRANK J ZEBRE.")
    circ("WY-JONES-CRAIG-L", "Craig L. Jones", 2019, 2023, 2018)
    circ("WY-ZEBRE-FRANK-J", "Frank J. Zebre", 2019, 2023, 2018)
    circ("WY-JONES-CRAIG-L", "Craig L. Jones", 2023, 2027, 2022,
         sources=[pg(2022), pg(2018)],
         notes="Official 2022 clerk CIRCUIT COURT JUDGE - JONES, YES. Full name from official 2018 clerk RETAIN JUDGE CRAIG L JONES.")
    circ("WY-GREER-MICHAEL-L", "Michael L. Greer", 2025, 2029, 2024,
         notes="Official 2024 clerk: MICHAEL L. GREER FOR CIRCUIT COURT JUDGE, YES.")
    circ("WY-CORPENING-GREGORY-S", "Gregory S. Corpening", 2025, 2029, 2024,
         notes="Official 2024 clerk: GREGORY S. CORPENING FOR CIRCUIT COURT JUDGE, YES.")
    circ("WY-STOUT-E-DEAN", "E. Dean Stout", "2026-05-01", FM[2029], None,
         how_took_office="appointed", confidence="medium",
         sources=[courts("circuit")],
         notes="Official Wyoming Judicial Branch 3rd JD Rock Springs circuit page: appointed May 2026 (day unstated; term_start 2026-05-01, medium), term expires January 2029, stands for retention November 2028.")
    return terms


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

    # Mayors are on the official November ballot (2014, 2018, 2022, 2026), not council-selected.
    add("WY-RUST-PETE", "Pete Rust", "municipal", "Green River Mayor", "City of Green River", 2015, 2019, 2014)
    add("WY-RUST-PETE", "Pete Rust", "municipal", "Green River Mayor", "City of Green River", 2019, 2023, 2018)
    add("WY-RUST-PETE", "Pete Rust", "municipal", "Green River Mayor", "City of Green River", 2023, 2027, 2022)
    add("WY-BLAKE-STAN", "Stan Blake", "municipal", "Green River Mayor", "City of Green River", 2027, 2031, 2026)

    add("WY-DEMSHAR-CARL-R", "Carl R. Demshar", "municipal", "Rock Springs Mayor", "City of Rock Springs", 2015, 2019, 2014)
    add("WY-KAUMO-TIM", "Tim Kaumo", "municipal", "Rock Springs Mayor", "City of Rock Springs", 2019, 2023, 2018)
    add("WY-MICKELSON-MAX", "Max Mickelson", "municipal", "Rock Springs Mayor", "City of Rock Springs", 2023, 2027, 2022)
    add("WY-MICKELSON-MAX", "Max Mickelson", "municipal", "Rock Springs Mayor", "City of Rock Springs", 2027, 2031, 2026)

    add("WY-ALLEN-SANDY", "Sandy Allen", "municipal", "Granger Mayor", "Town of Granger", 2015, 2019, 2014)
    add("WY-MCCOLLUM-BRADLY", "Bradly McCollum", "municipal", "Granger Mayor", "Town of Granger", 2019, 2023, 2018)
    add("WY-STYVAR-JOHN", "John Styvar", "municipal", "Granger Mayor", "Town of Granger", 2023, 2027, 2022,
        notes="Official 2022 general: named candidate John Styvar 14; itemized write-ins for Anselmo/Hippy Valerio variants total 22 if combined, but the official canvass does not combine them (highest single write-in line is 13). Encoded as printed, with this flag.")
    add("WY-VALERIO-ANSELMO", 'Anselmo "Hippy" Valerio', "municipal", "Granger Mayor", "Town of Granger", 2027, 2031, 2026)

    add("WY-PHIPPS-ROBB", "Robb Phipps", "municipal", "Wamsutter Mayor", "Town of Wamsutter", 2015, 2019, 2014)
    add("WY-ERICKSON-JOE", "Joe Erickson", "municipal", "Wamsutter Mayor", "Town of Wamsutter", 2019, 2023, 2018)
    add("WY-RONEY-LARRY-CHIP", 'Larry "Chip" Roney', "municipal", "Wamsutter Mayor", "Town of Wamsutter", 2023, 2027, 2022)
    add("WY-JERKE-KARLIN", "Karlin Jerke", "municipal", "Wamsutter Mayor", "Town of Wamsutter", 2027, 2031, 2026)

    add("WY-NIEMIEC-RICK", "Rick Niemiec", "municipal", "Superior Mayor", "Town of Superior", 2027, 2031, 2026,
        notes="Official 2026 general is the first Superior mayoral contest in this official clerk archive. Earlier years remain Not yet collected.")

    # Official 2014 clerk council (digital summary).
    add("WY-WILSON-ALLAN", "Allan Wilson", "municipal", "Green River City Council Ward 1", "City of Green River", 2015, 2019, 2014)
    add("WY-BARNEY-TED-L", "Ted L. Barney", "municipal", "Green River City Council Ward 2", "City of Green River", 2015, 2019, 2014)
    add("WY-KILLPACK-GARY", "Gary Killpack", "municipal", "Green River City Council Ward 3", "City of Green River", 2015, 2019, 2014)
    add("WY-ARMSTRONG-JASON", "Jason Armstrong", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2015, 2019, 2014)
    add("WY-SAVAGE-TIMOTHY", "Tim Savage", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2015, 2019, 2014)
    add("WY-HALTER-DAVID", "David B. Halter", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2015, 2019, 2014)
    add("WY-MOSBEY-ROSE-M", "Rose M. Mosbey", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2015, 2019, 2014)
    add("WY-DAVIS-DUSTIN", "Dustin Davis", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2015, 2019, 2014)
    add("WY-ERICKSON-JOE", "Joseph Erickson", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2015, 2019, 2014)
    add("WY-NICHOLS-JUNE", "June Nichols", "municipal", "Granger Town Council", "Town of Granger", 2015, 2019, 2014)
    add("WY-BRANTLEY-SHERRY", "Sherry Brantley", "municipal", "Granger Town Council", "Town of Granger", 2015, 2019, 2014)
    add("WY-DUNIVIN-SHANA-L", "Shana L. Dunivin", "municipal", "Granger Town Council", "Town of Granger", 2015, 2017, 2014,
        notes="Official 2014 clerk second Granger Town Council contest, vote for not more than 1 (2-year term).")

    # Official 2020 general precinct summary council (mayors were not on that ballot).
    add("WY-BUSHMAN-SHERRY", "Sherry Bushman", "municipal", "Green River City Council Ward 1", "City of Green River", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-JOST-GEORGE", "George Jost", "municipal", "Green River City Council Ward 2", "City of Green River", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-BERG-ROBERT-V", "Robert Berg", "municipal", "Green River City Council Ward 3", "City of Green River", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-ROBINSON-TIM-S", "Tim S. Robinson", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-ZOTTI-ROBERT-B", "Rob Zotti", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-HICKERSON-LARRY", "Larry Hickerson", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2021, 2025, 2020, sources=[pg(2020)],
        notes="Official 2020 general precinct-summary totals: Larry Hickerson 753, Ryan Greene 671.")
    add("WY-BETTOLO-BRENT", "Brent Bettolo", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2021, 2025, 2020, sources=[pg(2020)],
        notes="Official 2020 general precinct-summary totals: Brent Bettolo 868, Rose M. Mosbey 816.")

    # Council: 2018, 2022, 2024, 2026 official.
    add("WY-ZIMMERMAN-JIM", "Jim Zimmerman", "municipal", "Green River City Council Ward 1", "City of Green River", 2019, 2023, 2018)
    add("WY-WILLIAMS-RONALD-L", "Ronald L. Williams", "municipal", "Green River City Council Ward 1", "City of Green River", 2023, 2027, 2022)
    add("WY-BUSHMAN-SHERRY", "Sherry Bushman", "municipal", "Green River City Council Ward 1", "City of Green River", 2025, 2029, 2024)
    add("WY-WILLIAMS-RONALD-L", "Ronald L. Williams", "municipal", "Green River City Council Ward 1", "City of Green River", 2027, 2031, 2026)
    add("WY-SHUTRAN-MICHAEL-S", "Michael S. Shutran", "municipal", "Green River City Council Ward 2", "City of Green River", 2019, 2023, 2018)
    add("WY-SHUTRAN-MICHAEL-S", "Michael S. Shutran", "municipal", "Green River City Council Ward 2", "City of Green River", 2023, 2027, 2022)
    add("WY-MASER-JESSICA", "Jessica Maser", "municipal", "Green River City Council Ward 2", "City of Green River", 2025, 2029, 2024)
    add("WY-JOSEPH-JEAN", "Jean Joseph", "municipal", "Green River City Council Ward 2", "City of Green River", 2027, 2031, 2026)
    add("WY-KILLPACK-GARY", "Gary Killpack", "municipal", "Green River City Council Ward 3", "City of Green River", 2019, 2023, 2018)
    add("WY-KILLPACK-GARY", "Gary Killpack", "municipal", "Green River City Council Ward 3", "City of Green River", 2023, 2027, 2022)
    add("WY-BERG-ROBERT-V", "Robert V. Berg", "municipal", "Green River City Council Ward 3", "City of Green River", 2025, 2029, 2024)
    add("WY-STEVENS-PAUL-D", "Paul D. Stevens", "municipal", "Green River City Council Ward 3", "City of Green River", 2027, 2031, 2026)

    add("WY-DEMAS-JEANNIE", "Jeannie L. Demas", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2019, 2023, 2018)
    add("WY-DEMAS-JEANNIE", "Jeannie Demas", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2023, 2027, 2022)
    add("WY-MILONAS-RICK", "Rick Milonas", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2025, 2029, 2024)
    add("WY-DEMAS-JEANNIE", "Jeannie Demas", "municipal", "Rock Springs City Council Ward 1", "City of Rock Springs", 2027, 2031, 2026)
    add("WY-SAVAGE-TIMOTHY", "Timothy Savage", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2019, 2023, 2018)
    add("WY-ALLEN-THOMAS", "Thomas Allen", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2023, 2027, 2022)
    add("WY-ZOTTI-ROBERT-B", "Robert B. Zotti", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2025, 2029, 2024)
    add("WY-THOMPSON-DAVID-A", "David A. Thompson", "municipal", "Rock Springs City Council Ward 2", "City of Rock Springs", 2027, 2031, 2026)
    add("WY-HALTER-DAVID", "David Halter", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2019, 2023, 2018)
    add("WY-PEDRI-DANIEL-J", "Daniel J. Pedri", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2023, 2027, 2022)
    add("WY-HICKERSON-LARRY", "Larry Hickerson", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2025, 2029, 2024)
    add("WY-PEDRI-DANIEL-J", "Daniel J. Pedri", "municipal", "Rock Springs City Council Ward 3", "City of Rock Springs", 2027, 2031, 2026)
    add("WY-WEST-KEATON-D", "Keaton D. West", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2019, 2023, 2018)
    add("WY-HANSON-RANDY", "Randy Hanson", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2023, 2027, 2022)
    add("WY-BETTOLO-BRENT", "Brent Bettolo", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2025, 2029, 2024)
    add("WY-HANSON-RANDY", "Randy Hanson", "municipal", "Rock Springs City Council Ward 4", "City of Rock Springs", 2027, 2031, 2026)

    add("WY-DAVIS-DUSTIN", "Dustin Davis", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2019, 2023, 2018)
    add("WY-DAVIS-DUSTIN", "Dustin Davis", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2023, 2027, 2022)
    add("WY-RAUCH-SETH-J", "Seth J. Rauch", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2023, 2027, 2022)
    add("WY-WOLFE-DAVID-C", "David C. Wolfe", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2025, 2029, 2024)
    add("WY-DAVEY-JOANNE", "Joanne Davey", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2025, 2029, 2024)
    add("WY-WALDNER-MARINDA", "Marinda Waldner", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2027, 2031, 2026)
    add("WY-DAVIS-DUSTIN", "Dustin Davis", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2027, 2031, 2026)
    add("WY-GOFF-JENNIFER", "Jennifer Goff", "municipal", "Wamsutter Town Council", "Town of Wamsutter", 2027, 2029, 2026,
        notes="Official 2026 general Town Council Wamsutter 2-year term.")

    add("WY-ANDREWS-GEORGE", "George Andrews", "municipal", "Granger Town Council", "Town of Granger", 2023, 2027, 2022)
    add("WY-PERRY-ROBERT-A", "Robert A. Perry", "municipal", "Granger Town Council", "Town of Granger", 2023, 2027, 2022)
    add("WY-HOWEY-VERN", "Vern Howey", "municipal", "Granger Town Council", "Town of Granger", 2025, 2029, 2024)
    add("WY-NYGAARD-KIMBERLY", "Kimberly G. Nygaard", "municipal", "Granger Town Council", "Town of Granger", 2025, 2029, 2024)
    add("WY-MANSIR-DAWN", "Dawn Mansir", "municipal", "Granger Town Council", "Town of Granger", 2027, 2031, 2026)
    add("WY-STYVAR-JOHN", "John Styvar", "municipal", "Granger Town Council", "Town of Granger", 2027, 2031, 2026)

    add("WY-MCCUNE-THOMAS", "Thomas McCune", "municipal", "Superior Town Council", "Town of Superior", 2025, 2029, 2024)
    add("WY-MERRITT-SANDRA-S", "Sandra S. Merritt", "municipal", "Superior Town Council", "Town of Superior", 2025, 2029, 2024)
    add("WY-FRITS-CHASE", "Chase Frits", "municipal", "Superior Town Council", "Town of Superior", 2027, 2031, 2026,
        notes="Official 2026 general Vote-For-2 printed one named winner (Chase Frits 72); the second seat is not filled from a named official winner.")
    add("WY-BARELA-BARBARA", "Barbara Barela", "municipal", "Superior Town Council", "Town of Superior", 2027, 2029, 2026,
        notes="Official 2026 general Town Council Superior 2-year term.")

    # Schools / college — official 2022, 2024, 2026 titles as printed (compacted).
    add("WY-SPICER-THOMAS-E", "Thomas E. Spicer", "schools", "Western Wyoming College Trustee", "Western Wyoming Community College", 2015, 2019, 2014,
        notes="Official 2014 clerk contest title: WESTERN WYOMING COLLEGE, vote for not more than 1 (Thomas E. Spicer). District/at-large was not printed on that line.")
    add("WY-BOETTCHER-DICK", "Dick Boettcher", "schools", "Western Wyoming College Trustee", "Western Wyoming Community College", 2015, 2019, 2014,
        notes="Official 2014 clerk contest title: WESTERN WYOMING COLLEGE, vote for not more than 1 (Dick Boettcher). District/at-large was not printed on that line.")
    add("WY-DONALDSON-VERONICA-K", "Veronica Donaldson", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2021, 2023, 2020,
        sources=[pg(2020)], notes="Official 2020 general: WWCC SD#1 2-year unexpired.")
    add("WY-JESSEN-JAMES", "James Jessen", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-HESTER-CARLA", "Carla Hester", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-CLARK-REGINA-M", "Regina M. Clark", "schools", "Western Wyoming College Trustee District #2", "Western Wyoming Community College", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-SUMMERS-ANDREA-R", "Andrea R. Summers", "schools", "SWSD #1 Trustee Farson Area", "Sweetwater County School District #1", 2021, 2025, 2020,
        sources=[pg(2020)], notes="Official 2020 general contest title: SD#1 TRUSTEE FARSON-EDEN.")
    add("WY-BURRIS-THOMAS-E", "Thomas E. Burris", "special-districts", "Sweetwater County Conservation District Supervisor", "Sweetwater County Conservation District", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-ANDERSON-STEPHANIE", "Stephanie Anderson", "special-districts", "Sweetwater County Conservation District Supervisor", "Sweetwater County Conservation District", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-ROBISON-LISA", "Lisa Robison", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-GORDON-ROBERT-L", 'Robert L. "Bob" Gordon', "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2021, 2025, 2020, sources=[pg(2020)])
    add("WY-ROBBINS-REED-W", "Reed W. Robbins", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2021, 2025, 2020, sources=[pg(2020)])

    add("WY-LORIMER-KENNETH", "Kenneth Lorimer", "schools", "Western Wyoming College Trustee At-Large", "Western Wyoming Community College", 2023, 2027, 2022)
    add("WY-TRAVIS-LINDSEY", "Lindsey Travis", "schools", "Western Wyoming College Trustee At-Large", "Western Wyoming Community College", 2027, 2031, 2026)
    add("WY-KOURBELAS-NEIL", "Neil Kourbelas", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2023, 2025, 2022,
        notes="Official 2022 general WWCC#1 2-year unexpired.")
    add("WY-ALLEN-STEPHEN-P", "Stephen P. Allen", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2023, 2027, 2022)
    add("WY-DONALDSON-VERONICA-K", "Veronica K. Donaldson", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2023, 2027, 2022)
    add("WY-MARSHALL-TIFFANY", "Tiffany Marshall", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2025, 2029, 2024)
    add("WY-KNEZOVICH-OZZIE", "Ozzie Knezovich", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2025, 2029, 2024)
    add("WY-FREEZE-JACKIE-L", "Jackie L. Freeze", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2027, 2031, 2026)
    add("WY-JESSEN-JAMES", "James Jessen", "schools", "Western Wyoming College Trustee District #1", "Western Wyoming Community College", 2027, 2031, 2026)
    add("WY-MEREDITH-JENISSA", "Jenissa Meredith", "schools", "Western Wyoming College Trustee District #2", "Western Wyoming Community College", 2023, 2027, 2022)
    add("WY-LEE-ROBBIE", "Robbie Lee", "schools", "Western Wyoming College Trustee District #2", "Western Wyoming Community College", 2025, 2029, 2024)
    add("WY-NELSON-STACEY", "Stacey Nelson", "schools", "Western Wyoming College Trustee District #2", "Western Wyoming Community College", 2027, 2031, 2026)
    add("WY-JESSEN-JAMES", "James Jessen", "schools", "Western Wyoming School District #1 Trustee", "Sweetwater County School District #1", 2025, 2029, 2024,
        notes="Official 2024 clerk contest title: WESTERN WYOMING SCHOOL DISTRICT #1, Vote For 1, James Jessen 12,467. This is a separate official contest from Western Wyoming College District #1 on the same summary.")

    add("WY-SEPPIE-COLE", "Cole Seppie", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2025, 2029, 2024)
    add("WY-FRANKS-CHAD", "Dr. Chad Franks", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2025, 2029, 2024)
    add("WY-WRIGHT-COLE", "Cole Wright", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2025, 2029, 2024)
    add("WY-SORENSEN-JOSHUA-P", "Joshua P. Sorensen", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2025, 2029, 2024)
    add("WY-GARDNER-MATTHEW", "Matthew Gardner", "schools", "SWSD #1 Trustee Farson Area", "Sweetwater County School District #1", 2025, 2029, 2024)
    add("WY-GRAY-LEO", "Leo Gray", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2027, 2031, 2026)
    add("WY-DEVRIES-DANELLA", "Danella DeVries", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2027, 2031, 2026)
    add("WY-HAGER-HEATHER", "Heather Hager", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2027, 2029, 2026,
        notes="Official 2026 general SW School Dist #1 2-year Rock Springs Area.")
    add("WY-ROSSETTI-KORI-L", "Kori L. Rossetti", "schools", "SWSD #1 Trustee Rock Springs Area", "Sweetwater County School District #1", 2027, 2029, 2026,
        notes="Official 2026 general SW School Dist #1 2-year Rock Springs Area.")
    add("WY-DRINKLE-MANDY", "Mandy Drinkle", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2025, 2029, 2024)
    add("WY-THOMAN-TOMMY", "Tommy Thoman", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2025, 2029, 2024)
    add("WY-DAVIS-TATE", "Tate Davis", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2025, 2029, 2024)
    add("WY-FOLEY-MICHELLE-J", "Michelle J. Foley", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2025, 2029, 2024)
    add("WY-WILSON-TOM", "Tom Wilson", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2027, 2031, 2026)
    add("WY-FLOM-DANIEL", "Daniel Flom", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2027, 2031, 2026)
    add("WY-SHONING-KENNY-JR", "Kenny Shoning Jr", "schools", "SWSD #2 Trustee", "Sweetwater County School District #2", 2027, 2031, 2026)

    add("WY-STANTON-DANIEL", "Daniel Stanton", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2023, 2027, 2022)
    add("WY-GUNTER-SANDEE", "Sandee Gunter", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2023, 2027, 2022)
    add("WY-SORENSEN-PATSY-A", "Patsy A. Sorensen", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2023, 2027, 2022)
    add("WY-GORDON-ROBERT-L", 'Robert L. "Bob" Gordon', "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2025, 2029, 2024)
    add("WY-ROBBINS-REED-W", "Reed W. Robbins", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2025, 2029, 2024)
    add("WY-STANTON-DANIEL", "Daniel Stanton", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2027, 2031, 2026)
    add("WY-GUNTER-SANDEE", "Sandee Gunter", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2027, 2031, 2026)
    add("WY-HARGROVE-ROSS-M", "Ross M. Hargrove", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2027, 2031, 2026)
    add("WY-EDWARDS-JACLYN", "Jaclyn Edwards", "special-districts", "Castle Rock Hospital District Trustee", "Castle Rock Hospital District", 2027, 2031, 2026)

    add("WY-THOMAN-MARY-E", "Mary E. Thoman", "special-districts", "Sweetwater County Conservation District Supervisor", "Sweetwater County Conservation District", 2015, 2019, 2014)
    add("WY-DICKINSON-JEAN-M", "Jean M. Dickinson", "special-districts", "Sweetwater County Conservation District Supervisor", "Sweetwater County Conservation District", 2015, 2019, 2014)
    add("WY-FOLKS-AARON", "Aaron Folks", "special-districts", "Sweetwater County Conservation District Supervisor At-Large", "Sweetwater County Conservation District", 2027, 2031, 2026)
    add("WY-FOLKS-LARRY-B", "Larry B. Folks", "special-districts", "Sweetwater County Conservation District Supervisor Rural", "Sweetwater County Conservation District", 2027, 2031, 2026)
    add("WY-DICKINSON-JEAN-M", "Jean M. Dickinson", "special-districts", "Sweetwater County Conservation District Supervisor Urban", "Sweetwater County Conservation District", 2027, 2031, 2026)
    add("WY-FLOYD-KEITH", "Keith Floyd", "special-districts", "Sweetwater County Fire District #1 Director", "Sweetwater County Fire District #1", 2027, 2031, 2026)

    SRC_BAIROIL = {"label": "Official Town of Bairoil city-government page, retrieved 2026-11-24",
                   "url": "https://townofbairoil.com/cityGovernment.php"}
    terms.append(T(person_id="WY-CLAWSON-LOWELL", name="Lowell Clawson", office_group="municipal",
        office="Bairoil Mayor", jurisdiction="Town of Bairoil",
        term_start="2026-01-09", term_end="2027-06-30", how_took_office="elected", confidence="high",
        sources=[SRC_BAIROIL],
        notes="Official Town of Bairoil city-government page, retrieved 2026-11-24: Mayor Lowell Clawson. The official page does not state a term end; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass. Bairoil does not appear on the official Sweetwater November general canvasses in this archive."))
    for pid, name in [
        ("WY-THORNTON-ALAN", "Alan Thornton"),
        ("WY-THORNTON-AUDRA", "Audra Thornton"),
        ("WY-MCFALL-BUTCH", "Butch McFall"),
        ("WY-CHAVEZ-MICHELLE", "Michelle Chavez"),
    ]:
        terms.append(T(person_id=pid, name=name, office_group="municipal",
            office="Bairoil Town Council", jurisdiction="Town of Bairoil",
            term_start="2026-01-09", term_end="2027-06-30", how_took_office="elected", confidence="high",
            sources=[SRC_BAIROIL],
            notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. The official page does not state a term end; encoded as current through the next ordinary May municipal cycle (June 2027) pending an official canvass."))
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


def build_sweetwater():
    people = {}
    P = H.person_factory(people)
    register_people(P)
    register_more_people(P)

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
        # Do not copy other judicial districts. Sweetwater is in the 3rd JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 11 (S11)", 1),
            ("Senate District 12 (S12)", 1),
            ("Senate District 13 (S13)", 1),
            ("Senate District 14 (S14)", 1),
        ],
        "state-house": [
            ("House District 17 (H17)", 1),
            ("House District 18 (H18)", 1),
            ("House District 39 (H39)", 1),
            ("House District 47 (H47)", 1),
            ("House District 48 (H48)", 1),
            ("House District 60 (H60)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Green River Mayor", 1),
            ("Green River City Council Ward 1", 2),
            ("Green River City Council Ward 2", 2),
            ("Green River City Council Ward 3", 2),
            ("Rock Springs Mayor", 1),
            ("Rock Springs City Council Ward 1", 2),
            ("Rock Springs City Council Ward 2", 2),
            ("Rock Springs City Council Ward 3", 2),
            ("Rock Springs City Council Ward 4", 2),
            ("Granger Mayor", 1),
            ("Wamsutter Mayor", 1),
            ("Bairoil Mayor", 1),
            ("Bairoil Town Council", 4),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "3rd Judicial District judges. Where an official Sweetwater clerk summary prints only a last name, or omits "
        "the name (official 2022 JUDGE A DISTRICT COURT; official 2026 FOR JUDGE C OF THE DISTRICT COURT; official "
        "2014 JUDGE JONES / JUDGE ZEBRE), the full name is taken from an official Wyoming Judicial Branch 3rd JD "
        "page or from a later official clerk ballot, and that source is cited. Sweetwater is in the 3rd Judicial "
        "District; judges of other districts are not copied here."
    )
    special_note = (
        "Municipal, school, and special-district names are keyed from official Sweetwater November general results "
        "in this archive. Green River, Rock Springs, Granger, Wamsutter, and (in 2026) Superior mayors appear on "
        "the official November ballot and are not council-selected. Current Town of Bairoil holders are taken from "
        "the official Town of Bairoil city-government page, retrieved 2026-11-24; Bairoil does not appear on those "
        "official November canvasses. Official 2016 general and official 2012 general "
        "are scanned precinct canvasses; 2016 county-commissioner Vote-For-2 winners and many 2012/2016 local "
        "offices were not filled from those scans and are Not yet collected rather than invented. The official "
        "county staff directory retrieved 2026-11-24 lists the Sheriff office as Vacant (Rich Fischer is listed as "
        "a Lieutenant, not as Sheriff). Official Clerk of District Court pages name Amanda L. Chetterbock as the "
        "current clerk, but no official appointment date was found, so January snapshots keep official 2022 winner "
        "Donnalee Bobak through January 2027."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Sweetwater primary PDFs "
        "are archived under /workspace/wyoleg/local-results/sweetwater/<year>/. The current (November 2026) precinct "
        "roster is in data/county_officials/sweetwater.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Sweetwater", county_number=4, slug="sweetwater", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Sweetwater", slug="sweetwater")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def update_sweetwater_json(people: dict):
    path = ROOT / "data" / "county_officials" / "sweetwater.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
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
        office("Senate District 11 (S11)", [
            _holder(people, "WY-HICKS-LARRY", "Larry Hicks", "REP", "January 2027"),
            _holder(people, "WY-DAVIS-BOB", "Bob Davis", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Bob Davis is the official 2026 general winner and takes office January 2027."),
        office("Senate District 12 (S12)", [
            _holder(people, "WY-KOLB-JOHN-K", "John K. Kolb", "REP", "January 2029"),
        ]),
        office("Senate District 13 (S13)", [
            _holder(people, "WY-JONES-STACY", "Stacy Jones", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Senate District 14 (S14)", [
            _holder(people, "WY-PEARSON-LAURA", "Laura Taliaferro (formerly Pearson)", "REP", "January 2029"),
        ], note="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Sweetwater portion: 1,351. Also covers Lincoln, Sublette, and Uinta. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA."),
    ]
    house_offices = [
        office("House District 15 (H15)", [
            _holder(people, "WY-THAYER-PAMELA", "Pamela Thayer", "REP", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ], note="Official 2026 SOS statewide House summary totals: Pamela Thayer 1,499, Cheryl Hulme 398. Official Sweetwater portion: Thayer 28, Hulme 6. Also covers Carbon County. Official SOS district-wide totals are used for this multi-county seat."),
        office("House District 17 (H17)", [
            _holder(people, "WY-LARSON-JT", "J.T. Larson", "REP", "January 2027"),
            _holder(people, "WY-BINGHAM-ELIZABETH", "Elizabeth Bingham", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Elizabeth Bingham is the official 2026 general winner and takes office January 2027."),
        office("House District 18 (H18)", [
            _holder(people, "WY-HEINER-SCOTT", "Scott Heiner", "REP", "January 2027"),
            _holder(people, "WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official 2026 SOS district-wide totals: Roberts 2,691. Official Sweetwater portion: 879."),
        ], note="Kenneth D. Roberts is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Roberts 2,691. Official Sweetwater portion: 879. Also covers Lincoln and Uinta. Official SOS district-wide totals are used for this multi-county seat."),
        office("House District 39 (H39)", [
            _holder(people, "WY-WYLIE-CODY", "Cody Wylie", "REP", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 47 (H47)", [
            _holder(people, "WY-DAVIS-BOB", "Bob Davis", "REP", "January 2027"),
            _holder(people, "WY-OTOOLE-EAMON", "Eamon O'Toole", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Eamon O'Toole is the official 2026 general winner and takes office January 2027."),
        office("House District 48 (H48)", [
            _holder(people, "WY-MCCANN-DARIN-M", "Darin M. McCann", "REP", "January 2027"),
            _holder(people, "WY-WAMSLEY-JAMES", "James Wamsley", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="James Wamsley is the official 2026 general winner and takes office January 2027."),
        office("House District 60 (H60)", [
            _holder(people, "WY-BRADY-MARLENE", "Marlene Brady", "REP", "January 2027"),
            _holder(people, "WY-NIEMIEC-TONY", "Tony Niemiec", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Tony Niemiec is the official 2026 general winner and takes office January 2027."),
    ]
    county = [
        office("County Commissioners", [
            _holder(people, "WY-SLAUGHTER-ROBB", "Robb Slaughter", "REP", "January 2027"),
            _holder(people, "WY-RICHARDS-ISLAND", "Island Richards", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-WEST-KEATON-D", "Keaton D. West", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-JONES-TAYLOR", "Taylor Jones", "REP", "January 2029"),
            _holder(people, "WY-THOMAN-MARY-E", "Mary E. Thoman", "REP", "January 2029"),
            _holder(people, "WY-BUSHMAN-SHERRY", "Sherry Bushman", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Sherry Bushman is the official 2026 general Vote-For-3 winner (with continuing members Keaton D. West and Island Richards) and takes office January 2027."),
        office("County Clerk", [
            _holder(people, "WY-LANE-CINDY", "Cindy Lane", "REP", "January 2027"),
            _holder(people, "WY-DAVIS-DALE", "Dale Davis", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Dale Davis is the official 2026 general winner and takes office January 2027."),
        office("County Treasurer", [
            _holder(people, "WY-COWAN-MARK", "S. Mark Cowan", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Assessor", [
            _holder(people, "WY-DIVIS-DAVE", "Dave Divis", "REP", "January 2027"),
            _holder(people, "WY-STACEY-MARIANNE", "Marianne Stacey", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Marianne Stacey is the official 2026 general winner and takes office January 2027."),
        office("County Sheriff", [
            _holder(people, "WY-KAUMO-RICHARD-F", "Richard F. Kaumo", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="The official Sweetwater County staff directory retrieved 2026-11-24 lists the Sheriff office as Vacant (Rich Fischer is listed there as a Lieutenant, not as Sheriff). No official appointment of an interim sheriff was found. Richard F. Kaumo is the official 2026 general winner and takes office January 2027."),
        office("County Attorney", [
            _holder(people, "WY-ERRAMOUSPE-DANIEL-E", "Daniel E. Erramouspe", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Clerk of District Court", [
            _holder(people, "WY-CHETTERBOCK-AMANDA-L", "Amanda L. Chetterbock", "REP", "January 2031",
                    notes="Named as the current clerk on the official county Clerk of District Court page and the official Wyoming Judicial Branch 3rd JD Sweetwater district page (retrieved 2026-11-24); official 2026 general winner, term begins January 2027."),
        ], note="Amanda L. Chetterbock is named as the current clerk on official county and Wyoming Judicial Branch pages and is the official 2026 general winner."),
        office("County Coroner", [
            _holder(people, "WY-MAJHANOVICH-DALE-S", "Dale S. Majhanovich", "DEM", "January 2027"),
            _holder(people, "WY-SANDERS-TRAVIS-R", "Travis R. Sanders", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Travis R. Sanders is the official 2026 general winner and takes office January 2027."),
    ]
    municipal = [
        office("Green River Mayor", [
            _holder(people, "WY-RUST-PETE", "Pete Rust", "", "January 2027"),
            _holder(people, "WY-BLAKE-STAN", "Stan Blake", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Stan Blake is the official 2026 general winner and takes office January 2027. The Green River mayor is elected on the November ballot."),
        office("Green River City Council Ward 1", [
            _holder(people, "WY-WILLIAMS-RONALD-L", "Ronald L. Williams", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-BUSHMAN-SHERRY", "Sherry Bushman", "", "January 2029"),
        ]),
        office("Green River City Council Ward 2", [
            _holder(people, "WY-SHUTRAN-MICHAEL-S", "Michael S. Shutran", "", "January 2027"),
            _holder(people, "WY-MASER-JESSICA", "Jessica Maser", "", "January 2029"),
            _holder(people, "WY-JOSEPH-JEAN", "Jean Joseph", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Jean Joseph is the official 2026 general winner and takes office January 2027."),
        office("Green River City Council Ward 3", [
            _holder(people, "WY-KILLPACK-GARY", "Gary Killpack", "", "January 2027"),
            _holder(people, "WY-BERG-ROBERT-V", "Robert V. Berg", "", "January 2029"),
            _holder(people, "WY-STEVENS-PAUL-D", "Paul D. Stevens", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Paul D. Stevens is the official 2026 general winner and takes office January 2027."),
        office("Rock Springs Mayor", [
            _holder(people, "WY-MICKELSON-MAX", "Max Mickelson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Rock Springs City Council Ward 1", [
            _holder(people, "WY-DEMAS-JEANNIE", "Jeannie Demas", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-MILONAS-RICK", "Rick Milonas", "", "January 2029"),
        ]),
        office("Rock Springs City Council Ward 2", [
            _holder(people, "WY-ALLEN-THOMAS", "Thomas Allen", "", "January 2027"),
            _holder(people, "WY-ZOTTI-ROBERT-B", "Robert B. Zotti", "", "January 2029"),
            _holder(people, "WY-THOMPSON-DAVID-A", "David A. Thompson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="David A. Thompson is the official 2026 general winner and takes office January 2027."),
        office("Rock Springs City Council Ward 3", [
            _holder(people, "WY-PEDRI-DANIEL-J", "Daniel J. Pedri", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-HICKERSON-LARRY", "Larry Hickerson", "", "January 2029"),
        ]),
        office("Rock Springs City Council Ward 4", [
            _holder(people, "WY-HANSON-RANDY", "Randy Hanson", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-BETTOLO-BRENT", "Brent Bettolo", "", "January 2029"),
        ]),
        office("Granger Mayor", [
            _holder(people, "WY-STYVAR-JOHN", "John Styvar", "", "January 2027"),
            _holder(people, "WY-VALERIO-ANSELMO", 'Anselmo "Hippy" Valerio', "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Anselmo \"Hippy\" Valerio is the official 2026 general winner and takes office January 2027."),
        office("Granger Town Council", [
            _holder(people, "WY-ANDREWS-GEORGE", "George Andrews", "", "January 2027"),
            _holder(people, "WY-PERRY-ROBERT-A", "Robert A. Perry", "", "January 2027"),
            _holder(people, "WY-HOWEY-VERN", "Vern Howey", "", "January 2029"),
            _holder(people, "WY-NYGAARD-KIMBERLY", "Kimberly G. Nygaard", "", "January 2029"),
            _holder(people, "WY-MANSIR-DAWN", "Dawn Mansir", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-STYVAR-JOHN", "John Styvar", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Wamsutter Mayor", [
            _holder(people, "WY-RONEY-LARRY-CHIP", 'Larry "Chip" Roney', "", "January 2027"),
            _holder(people, "WY-JERKE-KARLIN", "Karlin Jerke", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Karlin Jerke is the official 2026 general winner and takes office January 2027."),
        office("Wamsutter Town Council", [
            _holder(people, "WY-DAVIS-DUSTIN", "Dustin Davis", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-RAUCH-SETH-J", "Seth J. Rauch", "", "January 2027"),
            _holder(people, "WY-WOLFE-DAVID-C", "David C. Wolfe", "", "January 2029"),
            _holder(people, "WY-DAVEY-JOANNE", "Joanne Davey", "", "January 2029"),
            _holder(people, "WY-WALDNER-MARINDA", "Marinda Waldner", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-GOFF-JENNIFER", "Jennifer Goff", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general 2-year term."),
        ]),
        office("Superior Mayor", [
            _holder(people, "WY-NIEMIEC-RICK", "Rick Niemiec", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Rick Niemiec is the official 2026 general winner and takes office January 2027. No official Superior mayoral contest was found in this archive for 2014–2024."),
        office("Superior Town Council", [
            _holder(people, "WY-MCCUNE-THOMAS", "Thomas McCune", "", "January 2029"),
            _holder(people, "WY-MERRITT-SANDRA-S", "Sandra S. Merritt", "", "January 2029"),
            _holder(people, "WY-FRITS-CHASE", "Chase Frits", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-BARELA-BARBARA", "Barbara Barela", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general 2-year term."),
        ]),
        office("Bairoil Mayor", [
            _holder(people, "WY-CLAWSON-LOWELL", "Lowell Clawson", "", "",
                    notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. No term end stated on the official page."),
        ]),
        office("Bairoil Town Council", [
            _holder(people, "WY-THORNTON-ALAN", "Alan Thornton", "", "",
                    notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. No term end stated on the official page."),
            _holder(people, "WY-THORNTON-AUDRA", "Audra Thornton", "", "",
                    notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. No term end stated on the official page."),
            _holder(people, "WY-MCFALL-BUTCH", "Butch McFall", "", "",
                    notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. No term end stated on the official page."),
            _holder(people, "WY-CHAVEZ-MICHELLE", "Michelle Chavez", "", "",
                    notes="Official Town of Bairoil city-government page, retrieved 2026-11-24. No term end stated on the official page."),
        ]),
    ]
    schools = [
        office("Western Wyoming College Trustee At-Large", [
            _holder(people, "WY-LORIMER-KENNETH", "Kenneth Lorimer", "", "January 2027"),
            _holder(people, "WY-TRAVIS-LINDSEY", "Lindsey Travis", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Western Wyoming College Trustee District #1", [
            _holder(people, "WY-ALLEN-STEPHEN-P", "Stephen P. Allen", "", "January 2027"),
            _holder(people, "WY-DONALDSON-VERONICA-K", "Veronica K. Donaldson", "", "January 2027"),
            _holder(people, "WY-MARSHALL-TIFFANY", "Tiffany Marshall", "", "January 2029"),
            _holder(people, "WY-KNEZOVICH-OZZIE", "Ozzie Knezovich", "", "January 2029"),
            _holder(people, "WY-JESSEN-JAMES", "James Jessen", "", "January 2031",
                    notes="Official 2024 District #1 line, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-FREEZE-JACKIE-L", "Jackie L. Freeze", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Western Wyoming College Trustee District #2", [
            _holder(people, "WY-MEREDITH-JENISSA", "Jenissa Meredith", "", "January 2027"),
            _holder(people, "WY-LEE-ROBBIE", "Robbie Lee", "", "January 2029"),
            _holder(people, "WY-NELSON-STACEY", "Stacey Nelson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Western Wyoming School District #1 Trustee", [
            _holder(people, "WY-JESSEN-JAMES", "James Jessen", "", "January 2029",
                    notes="Official 2024 general WESTERN WYOMING SCHOOL DISTRICT #1 winner."),
        ]),
        office("SWSD #1 Trustee Rock Springs Area", [
            _holder(people, "WY-SEPPIE-COLE", "Cole Seppie", "", "January 2029"),
            _holder(people, "WY-FRANKS-CHAD", "Dr. Chad Franks", "", "January 2029"),
            _holder(people, "WY-WRIGHT-COLE", "Cole Wright", "", "January 2029"),
            _holder(people, "WY-SORENSEN-JOSHUA-P", "Joshua P. Sorensen", "", "January 2029"),
            _holder(people, "WY-GRAY-LEO", "Leo Gray", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-DEVRIES-DANELLA", "Danella DeVries", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-HAGER-HEATHER", "Heather Hager", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general 2-year term."),
            _holder(people, "WY-ROSSETTI-KORI-L", "Kori L. Rossetti", "", "January 2029",
                    notes="Takes office January 2027. Official 2026 general 2-year term."),
        ]),
        office("SWSD #1 Trustee Farson Area", [
            _holder(people, "WY-GARDNER-MATTHEW", "Matthew Gardner", "", "January 2029"),
        ]),
        office("SWSD #2 Trustee", [
            _holder(people, "WY-DRINKLE-MANDY", "Mandy Drinkle", "", "January 2029"),
            _holder(people, "WY-THOMAN-TOMMY", "Tommy Thoman", "", "January 2029"),
            _holder(people, "WY-DAVIS-TATE", "Tate Davis", "", "January 2029"),
            _holder(people, "WY-FOLEY-MICHELLE-J", "Michelle J. Foley", "", "January 2029"),
            _holder(people, "WY-WILSON-TOM", "Tom Wilson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-FLOM-DANIEL", "Daniel Flom", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-SHONING-KENNY-JR", "Kenny Shoning Jr", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
    ]
    special = [
        office("Castle Rock Hospital District Trustee", [
            _holder(people, "WY-STANTON-DANIEL", "Daniel Stanton", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-GUNTER-SANDEE", "Sandee Gunter", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-GORDON-ROBERT-L", 'Robert L. "Bob" Gordon', "", "January 2029"),
            _holder(people, "WY-ROBBINS-REED-W", "Reed W. Robbins", "", "January 2029"),
            _holder(people, "WY-HARGROVE-ROSS-M", "Ross M. Hargrove", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-EDWARDS-JACLYN", "Jaclyn Edwards", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Sweetwater County Conservation District Supervisor At-Large", [
            _holder(people, "WY-FOLKS-AARON", "Aaron Folks", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Sweetwater County Conservation District Supervisor Rural", [
            _holder(people, "WY-FOLKS-LARRY-B", "Larry B. Folks", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Sweetwater County Conservation District Supervisor Urban", [
            _holder(people, "WY-DICKINSON-JEAN-M", "Jean M. Dickinson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Sweetwater County Fire District #1 Director", [
            _holder(people, "WY-FLOYD-KEITH", "Keith Floyd", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
    ]
    judicial = [
        office("District Judge, 3rd Judicial District", [
            _holder(people, "WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "", "January 2033",
                    notes="Official 2020 term ends January 2027; official 2026 clerk Judge C retention (YES, unnamed on the clerk line). Identified from the official Wyoming Judicial Branch 3rd JD Sweetwater district page."),
            _holder(people, "WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "", "January 2029",
                    notes="Official 2022 clerk Judge A retention (YES, unnamed). Identified from the official 3rd JD Lincoln County district page."),
            _holder(people, "WY-KASTE-JAMES-C", "James C. Kaste", "", "January 2031",
                    notes="Official 2024 clerk Judge D JAMES KASTE. Full name from the official 3rd JD Uinta County district page."),
            _holder(people, "WY-STITH-CLARK", "Clark Stith", "", "January 2029",
                    notes="Official Wyoming Judicial Branch 3rd JD Sweetwater district page: appointed April 2026."),
        ]),
        office("Circuit Judge, 3rd Judicial District", [
            _holder(people, "WY-PROKOS-JOHN-R", "John R. Prokos", "", "January 2031",
                    notes="Official 2022 term ends January 2027; official 2026 clerk JOHN R. PROKOS, YES, continuing."),
            _holder(people, "WY-GREER-MICHAEL-L", "Michael L. Greer", "", "January 2029",
                    notes="Official 2024 clerk MICHAEL L. GREER FOR CIRCUIT COURT JUDGE, YES."),
            _holder(people, "WY-CORPENING-GREGORY-S", "Gregory S. Corpening", "", "January 2029",
                    notes="Official 2024 clerk GREGORY S. CORPENING FOR CIRCUIT COURT JUDGE, YES."),
            _holder(people, "WY-STOUT-E-DEAN", "E. Dean Stout", "", "January 2029",
                    notes="Official Wyoming Judicial Branch 3rd JD Rock Springs circuit page: appointed May 2026."),
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
    src["general_results"] = cms("Official Sweetwater Results.pdf")
    src["primary_results"] = cms("2026 Primary Official Election Summary.pdf")
    src["checked"] = RETRIEVED
    data["sources"] = src
    apply_to_groups(data["groups"], 'sweetwater')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
