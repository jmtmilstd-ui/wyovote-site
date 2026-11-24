"""Teton County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
ARCHIVE = "https://www.tetoncountywy.gov/271/Election-Results"
ARCHIVE_SUM = "https://www.tetoncountywy.gov/Archive.aspx?AMID=47"
ARCHIVE_PBP = "https://www.tetoncountywy.gov/Archive.aspx?AMID=46"
DC = "https://www.tetoncountywy.gov/DocumentCenter/View/"
AC = "https://www.tetoncountywy.gov/ArchiveCenter/ViewFile/Item/"

COURTS = {
    "teton-d": ("https://www.wyocourts.gov/court/district-court-9th-judicial-district-teton-county/",
                "Wyoming Judicial Branch official District Court, 9th Judicial District, Teton County page"),
    "teton-c": ("https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-teton-county-state-of-wyoming-jackson/",
                "Wyoming Judicial Branch official Circuit Court of the 9th Judicial District (Jackson) page"),
    "fremont-d": ("https://www.wyocourts.gov/court/district-court-9th-judicial-district-fremont-county/",
                  "Wyoming Judicial Branch official District Court, 9th Judicial District, Fremont County page"),
    "sublette-d": ("https://www.wyocourts.gov/court/district-court-9th-judicial-district-sublette-county/",
                   "Wyoming Judicial Branch official District Court, 9th Judicial District, Sublette County page"),
    "fremont-c": ("https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-fremont-county-state-of-wyoming-lander/",
                  "Wyoming Judicial Branch official Circuit Court of the 9th Judicial District (Lander) page"),
    "riverton-c": ("https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-fremont-county-state-of-wyoming-riverton/",
                   "Wyoming Judicial Branch official Circuit Court of the 9th Judicial District (Riverton) page"),
    "sublette-c": ("https://www.wyocourts.gov/court/circuit-court-of-the-9th-judicial-district-sublette-county-state-of-wyoming-pinedale/",
                   "Wyoming Judicial Branch official Circuit Court of the 9th Judicial District (Pinedale) page"),
}

def dc(num_name: str) -> str:
    return DC + num_name

def ac(item: str) -> str:
    return AC + item

def sos_url(year: int) -> str:
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Teton_County_General_PbP.pdf"

PG = {
    2010: (ac("89"), "Teton County official 2010 general election results by summary"),
    2012: (ac("91"), "Teton County official 2012 general election results by summary"),
    2014: (ac("93"), "Teton County official 2014 general election results by summary"),
    2016: (ac("95"), "Teton County official 2016 general election results by summary"),
    2018: (dc("8456/2018-General-Election---Official-Summary-Results"), "Teton County official 2018 general election summary"),
    2020: (dc("16000/2020-General-Election---Official-Summary-Results-"), "Teton County official 2020 general election summary"),
    2022: (dc("23954/2022-General-Election---Official-Summary-Results"), "Teton County official 2022 general election summary"),
    2024: (dc("32501/Teton-County-Official-General-Election-Summary"), "Teton County official 2024 general election summary"),
    2026: (dc("42627/2026-General-Election-Official-Results-Summary"), "Teton County official 2026 general election summary"),
}

def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}

def sos(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} Teton general precinct-by-precinct summary", "url": sos_url(year)}

def sos_house(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} statewide House candidates summary",
            "url": f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_General_Statewide_House_Candidates_Summary.pdf"}

def sos_senate(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} statewide Senate candidates summary",
            "url": f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_General_Statewide_Senate_Candidates_Summary.pdf"}

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
        ("WY-DOCKSTADER-DAN", "Dan Dockstader", "Dan", "Dockstader"),
        ("WY-GIERAU-MIKE", "Mike Gierau", "Mike", "Gierau", "", 'Michael F. "Mike" Gierau'),
        ("WY-CHRISTENSEN-LELAND", "Leland Christensen", "Leland", "Christensen"),
        ("WY-YIN-MIKE", "Mike Yin", "Mike", "Yin"),
        ("WY-BYRON-ANDREW", "Andrew Byron", "Andrew", "Byron", "", "Andrew P. Byron"),
        ("WY-STORER-LIZ", "Liz Storer", "Liz", "Storer", "", "Elizabeth Liz Storer"),
        ("WY-PETROFF-RUTH-ANN", "Ruth Ann Petroff", "Ruth Ann", "Petroff"),
        ("WY-SCHWARTZ-ANDY", "Andy Schwartz", "Andy", "Schwartz"),
        ("WY-GINGERY-KEITH", "Keith Gingery", "Keith", "Gingery"),
        ("WY-HALVERSON-MARTI", "Marti Halverson", "Marti", "Halverson"),
        ("WY-ROSCOE-JIM", "Jim Roscoe", "Jim", "Roscoe"),
        ("WY-NEWCOMB-MARK", "Mark Newcomb", "Mark", "Newcomb"),
        ("WY-PROPST-LUTHER", "Luther Propst", "Luther", "Propst"),
        ("WY-GARDNER-WES", "Wes Gardner", "Wes", "Gardner"),
        ("WY-CARLMAN-LEN", "Len Carlman", "Len", "Carlman"),
        ("WY-MACKER-NATALIA-D", "Natalia D. Macker", "Natalia", "Macker", "D."),
        ("WY-CHIN-KARYN", "Karyn Chin", "Karyn", "Chin"),
        ("WY-DUNFORD-ALI", "Ali Dunford", "Ali", "Dunford"),
        ("WY-EPSTEIN-GREGORY-W", "Gregory W. Epstein", "Gregory", "Epstein", "W.", "Greg Epstein"),
        ("WY-BARRON-MARK", "Mark Barron", "Mark", "Barron"),
        ("WY-VOGELHEIM-PAUL", "Paul Vogelheim", "Paul", "Vogelheim"),
        ("WY-RHEA-SMOKEY", "Smokey Rhea", "Smokey", "Rhea"),
        ("WY-ALLEN-BARBARA", "Barbara Allen", "Barbara", "Allen"),
        ("WY-TURLEY-MELISSA", "Melissa Turley", "Melissa", "Turley"),
        ("WY-MURPHY-MAUREEN", 'Maureen "Mo" Murphy', "Maureen", "Murphy", "", "Mo Murphy"),
        ("WY-DAIGLE-SHERRY-L", "Sherry L. Daigle", "Sherry", "Daigle", "L."),
        ("WY-SMITS-KATIE", "Katie Smits", "Katie", "Smits"),
        ("WY-BAUR-DONNA-M", "Donna M. Baur", "Donna", "Baur", "M."),
        ("WY-SHINKLE-MELISSA", 'Melissa "Mel" Shinkle', "Melissa", "Shinkle", "", "Mel Shinkle"),
        ("WY-NADER-ASHLEE", "Ashlee Nader", "Ashlee", "Nader"),
        ("WY-CAVALLARO-ANDY", "Andy Cavallaro", "Andy", "Cavallaro"),
        ("WY-CARR-MATT", "Matt Carr", "Matt", "Carr"),
        ("WY-WHALEN-JIM", "Jim Whalen", "Jim", "Whalen"),
        ("WY-STOUT-RICHARD", 'Richard "Dick" Stout', "Richard", "Stout", "", "Dick Stout"),
        ("WY-WEISMAN-ERIN-E", "Erin E. Weisman", "Erin", "Weisman", "E.", "Erin Weisman"),
        ("WY-WEICHMAN-STEVE", "Steve Weichman", "Steve", "Weichman"),
        ("WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux Sutton", "Anne", "Sutton", "", "Anne Comeaux; Anne C. Sutton"),
        ("WY-BLUE-BRENT", 'Brent "Doc" Blue', "Brent", "Blue", "", "Doc Blue"),
        ("WY-CLAUSON-KATRINA-L", "Katrina L. Clauson", "Katrina", "Clauson", "L.", 'Katrina "Kat" Clauson'),
        ("WY-JORGENSEN-ARNE-OLAUS", "Arne Olaus Jorgensen", "Arne", "Jorgensen", "Olaus", "Arne Jorgensen"),
        ("WY-LEVINSON-HAILEY-MORTON", "Hailey Morton Levinson", "Hailey", "Levinson", "", "Hailey Morton"),
        ("WY-MULDOON-PETE", "Pete Muldoon", "Pete", "Muldoon"),
        ("WY-FLITNER-SARA", "Sara Flitner", "Sara", "Flitner"),
        ("WY-SCHECHTER-JONATHAN", "Jonathan Schechter", "Jonathan", "Schechter"),
        ("WY-SPERY-ALYSON", "Alyson Spery", "Alyson", "Spery"),
        ("WY-REGAN-KEVIN", "Kevin Regan", "Kevin", "Regan"),
        ("WY-VIEHMAN-DEVON", "Devon Viehman", "Devon", "Viehman"),
        ("WY-CHAMBERS-JESSICA-SELL", "Jessica Sell Chambers", "Jessica", "Chambers", "", "Jessica Chambers"),
        ("WY-ROOKS-JIM", "Jim Rooks", "Jim", "Rooks"),
        ("WY-STANFORD-JIM", "Jim Stanford", "Jim", "Stanford"),
        ("WY-FRANK-DON", "Don Frank", "Don", "Frank"),
        ("WY-LENZ-BOB", "Bob Lenz", "Bob", "Lenz"),
        ("WY-OWENS-MELISSA-M", "Melissa M. Owens", "Melissa", "Owens", "M."),
        ("WY-CONDER-JASON-M", "Jason M. Conder", "Jason", "Conder", "M."),
        ("WY-MCKAY-KATHARINE-G", "Katharine G. McKay", "Katharine", "McKay", "G.", "Kate G. McKay"),
        ("WY-DAY-TIMOTHY-C", "Timothy C. Day", "Timothy", "Day", "C."),
        ("WY-TYLER-MARVIN-L", "Marvin L. Tyler", "Marvin", "Tyler", "L."),
        ("WY-YOUNG-NORMAN-E", "Norman E. Young", "Norman", "Young", "E."),
        ("WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "Jefferson", "Coombs", "", "Jefferson Coombs"),
        ("WY-STEBNER-DANIEL-M", "Daniel M. Stebner", "Daniel", "Stebner", "M."),
        ("WY-LABUDA-JOHN", "John LaBuda", "John", "LaBuda"),
        ("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", "Wesley", "Roberts", "A."),
        ("WY-DENHARDT-ROBERT-B", "Robert B. Denhardt", "Robert", "Denhardt", "B.", "Rob Denhardt"),
        ("WY-HAWS-CURT-A", "Curt A. Haws", "Curt", "Haws", "A.", "Curt Haws"),
        ("WY-RADDA-JAMES-L", "James L. Radda", "James", "Radda", "L."),
        ("WY-ABRAMS-STEPHAN", "Stephan Abrams", "Stephan", "Abrams"),
        ("WY-DORNAN-READE", "Reade W. Dornan", "Reade", "Dornan", "W.", "Reade Dornan"),
        ("WY-SINCLAIR-ASHLEY", "Ashley Sinclair", "Ashley", "Sinclair"),
        ("WY-CARLIN-BETSY", "Betsy Carlin", "Betsy", "Carlin"),
        ("WY-MEAD-KATE", "Kate Mead", "Kate", "Mead"),
        ("WY-SCARLETT-BILL", "Bill Scarlett", "Bill", "Scarlett"),
        ("WY-ZUNG-JENNIFER", "Jennifer Zung", "Jennifer", "Zung"),
        ("WY-BAND-ANNIE", "Annie Band", "Annie", "Band"),
        ("WY-BRUMSTED-ALAN", "Alan Brumsted", "Alan", "Brumsted"),
        ("WY-TESKE-JANINE-BAY", "Janine Bay Teske", "Janine", "Teske", "", "Janine Bay Teske"),
        ("WY-LARROW-JOE", "Joe Larrow", "Joe", "Larrow"),
        ("WY-ELLIOTT-SYD", "Syd Elliott", "Syd", "Elliott"),
        ("WY-FARROW-ROBBI", "Robbi Farrow", "Robbi", "Farrow"),
        ("WY-RUSSELL-PATRICIA-A", "Patricia A. Russell", "Patricia", "Russell", "A."),
        ("WY-BOSCH-JERRY", "Jerry Bosch", "Jerry", "Bosch"),
        ("WY-CUTLER-PAM", "Pam Cutler", "Pam", "Cutler"),
        ("WY-CONOVER-KELLER-KATHARINE", "Katharine Conover-Keller", "Katharine", "Conover-Keller"),
        ("WY-HAYSE-BRUCE", "Bruce Hayse", "Bruce", "Hayse"),
        ("WY-HUNT-JIM", "Jim Hunt", "Jim", "Hunt"),
        ("WY-HOGLUND-BILL", "Bill Hoglund", "Bill", "Hoglund"),
        ("WY-BRENNAN-SHANNON-A", "Shannon A. Brennan", "Shannon", "Brennan", "A."),
        ("WY-HOCHHEISER-LOU", "Lou Hochheiser", "Lou", "Hochheiser"),
        ("WY-HOGAN-CYNTHIA", "Cynthia Hogan", "Cynthia", "Hogan"),
        ("WY-GIBSON-C-SCOTT", "C. Scott Gibson", "Scott", "Gibson", "C.", "Scott Gibson"),
        ("WY-HALL-ZACH", "Zach Hall", "Zach", "Hall"),
        ("WY-HERZ-BARBARA", "Barbara Herz", "Barbara", "Herz"),
        ("WY-CRITZER-SUE", "Sue Critzer", "Sue", "Critzer"),
        ("WY-HOPKINS-DEBORAH-C", "Deborah C. Hopkins", "Deborah", "Hopkins", "C."),
        ("WY-ALBRIGHT-JOE", "Joe Albright", "Joe", "Albright"),
        ("WY-AURELIO-LINDA", "Linda Aurelio", "Linda", "Aurelio"),
        ("WY-MASEK-ELIZABETH-C", "Elizabeth C. Masek", "Elizabeth", "Masek", "C.", "Elizabeth Masek"),
        ("WY-TENNICAN-MICHAEL", "Michael Tennican", "Michael", "Tennican", "", "Michael L. Tennican"),
        ("WY-ADAMS-DAVID-C", "David C. Adams", "David", "Adams", "C."),
        ("WY-LUCAS-BOB", "Bob Lucas", "Bob", "Lucas"),
        ("WY-WATSABAUGH-CATE", "Cate Watsabaugh", "Cate", "Watsabaugh"),
        ("WY-MCDONALD-STEVE", "Steve McDonald", "Steve", "McDonald"),
        ("WY-SHUPTRINE-SANDY", "Sandy Shuptrine", "Sandy", "Shuptrine"),
        ("WY-HURLEY-ROBY", "Roby Hurley", "Roby", "Hurley"),
        ("WY-FARBOD-KATHY", "Kathy Farbod", "Kathy", "Farbod"),
        ("WY-FULLER-NATE", "Nate Fuller", "Nate", "Fuller"),
        ("WY-CAMPBELL-THOMAS-M", "Thomas M. Campbell", "Thomas", "Campbell", "M."),
        ("WY-SCHREIBER-BAILEY-K", "Bailey K. Schreiber", "Bailey", "Schreiber", "K."),
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
            sources=kw.pop("sources", [pg(ey)] if ey in PG else []), **kw,
        ))

    # Senate 16 (Teton + Lincoln). Use official SOS district-wide totals when the Teton portion loses.
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Teton County", 2013, 2017, 2012, "REP",
        notes="Official 2012 Teton clerk: Dan Dockstader 1,064 to 56 write-ins (Teton portion). Also covers Lincoln County.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Teton County", 2017, 2021, 2016, "REP",
        sources=[sos_senate(2016), pg(2016)],
        notes="Official 2016 SOS statewide Senate summary totals: Dan Dockstader 7,208, Richard Kusaba 1,989. Official 2016 Teton clerk portion: Kusaba 1,113, Dockstader 860.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Teton County", 2021, 2025, 2020, "REP",
        sources=[pg(2020), sos_senate(2020)],
        notes="Official 2020 Teton clerk: Dan Dockstader 1,258 to 137 write-ins (Teton portion). Official 2020 SOS statewide Senate summary also lists Dockstader in S16.")
    add("WY-DOCKSTADER-DAN", "Dan Dockstader", "state-senate", "Senate District 16 (S16)", "Teton County", 2025, 2029, 2024, "REP",
        notes="Official 2024 Teton clerk: Dan Dockstader 1,475 to 115 write-ins (Teton portion). Also covers Lincoln County.")

    # Senate 17
    add("WY-CHRISTENSEN-LELAND", "Leland Christensen", "state-senate", "Senate District 17 (S17)", "Teton County", 2011, 2015, 2010, "REP",
        sources=[sos(2010)], notes="Official 2010 SOS Teton general PbP names Christensen (R) and Frisbie (D) for S17. Official 2014 clerk continues Christensen.")
    add("WY-CHRISTENSEN-LELAND", "Leland Christensen", "state-senate", "Senate District 17 (S17)", "Teton County", 2015, 2019, 2014, "REP",
        notes="Official 2014 Teton clerk: Leland Christensen 4,926 to 88 write-ins.")
    add("WY-GIERAU-MIKE", "Mike Gierau", "state-senate", "Senate District 17 (S17)", "Teton County", 2019, 2023, 2018, "DEM",
        notes="Official 2018 Teton clerk (OCR of official scan): Mike Gierau 6,008, Kate Mead 3,631.")
    add("WY-GIERAU-MIKE", 'Michael F. "Mike" Gierau', "state-senate", "Senate District 17 (S17)", "Teton County", 2023, 2027, 2022, "DEM",
        notes="Official 2022 Teton clerk: Michael F. \"Mike\" Gierau 5,142, Steve Duerr 2,615, Amanda Padilla 421.")
    add("WY-GIERAU-MIKE", "Mike Gierau", "state-senate", "Senate District 17 (S17)", "Teton County", 2027, 2031, 2026, "DEM")

    # House 16
    add("WY-PETROFF-RUTH-ANN", "Ruth Ann Petroff", "state-house", "House District 16 (H16)", "Teton County", 2013, 2015, 2012, "REP")
    add("WY-PETROFF-RUTH-ANN", "Ruth Ann Petroff", "state-house", "House District 16 (H16)", "Teton County", 2015, 2017, 2014, "REP",
        notes="Official 2014 Teton clerk: Ruth Ann Petroff 1,947 to 63 write-ins.")
    add("WY-GIERAU-MIKE", "Mike Gierau", "state-house", "House District 16 (H16)", "Teton County", 2017, 2019, 2016, "DEM",
        notes="Official 2016 Teton clerk: Mike Gierau 3,740.")
    add("WY-YIN-MIKE", "Mike Yin", "state-house", "House District 16 (H16)", "Teton County", 2019, 2021, 2018, "DEM",
        sources=[sos_house(2018), pg(2018)],
        notes="Official 2018 SOS statewide House summary / official 2018 Teton clerk: Mike Yin 2,530, Barbara Allen 1,712.")
    add("WY-YIN-MIKE", "Mike Yin", "state-house", "House District 16 (H16)", "Teton County", 2021, 2023, 2020, "DEM")
    add("WY-YIN-MIKE", "Mike Yin", "state-house", "House District 16 (H16)", "Teton County", 2023, 2025, 2022, "DEM")
    add("WY-YIN-MIKE", "Mike Yin", "state-house", "House District 16 (H16)", "Teton County", 2025, 2027, 2024, "DEM")
    add("WY-YIN-MIKE", "Mike Yin", "state-house", "House District 16 (H16)", "Teton County", 2027, 2029, 2026, "DEM")

    # House 22 (Teton + Lincoln). Always prefer official SOS district-wide totals.
    add("WY-HALVERSON-MARTI", "Marti Halverson", "state-house", "House District 22 (H22)", "Teton County", 2015, 2017, 2014, "REP",
        sources=[pg(2014), {"label": "Wyoming Secretary of State official 2014 Lincoln general precinct-by-precinct summary", "url": "https://sos.wyo.gov/Elections/Docs/2014/Results/General/2014_Lincoln_County_General_PbP.pdf"}],
        notes="Official 2014 SOS statewide House summary totals: Marti Halverson 1,991, Natalia Macker 1,224 (Lincoln 1,192–377; Teton 570–749; Sublette 229–98). Official SOS district-wide totals are used for this multi-county seat.")
    add("WY-HALVERSON-MARTI", "Marti Halverson", "state-house", "House District 22 (H22)", "Teton County", 2017, 2019, 2016, "REP",
        sources=[sos_house(2016), pg(2016)],
        notes="Official 2016 SOS statewide House summary totals: Marti Halverson 2,942, Marylee White 2,157. Official 2016 Teton clerk portion: White 1,247, Halverson 782.")
    add("WY-ROSCOE-JIM", "Jim Roscoe", "state-house", "House District 22 (H22)", "Teton County", 2019, 2021, 2018, "IND",
        sources=[sos_house(2018), pg(2018)],
        notes="Official 2018 SOS statewide House summary totals: Jim Roscoe 2,495, Marti Halverson 1,983. Official 2018 Teton clerk portion: Roscoe 1,381, Halverson 510.")
    add("WY-ROSCOE-JIM", "Jim Roscoe", "state-house", "House District 22 (H22)", "Teton County", 2021, 2023, 2020, "IND",
        sources=[sos_house(2020), pg(2020)],
        notes="Official 2020 SOS statewide House summary totals: Jim Roscoe 3,191, Bill Winney 2,825. Official 2020 Teton clerk portion: Roscoe 1,679, Winney 635.")
    add("WY-BYRON-ANDREW", "Andrew Byron", "state-house", "House District 22 (H22)", "Teton County", 2023, 2025, 2022, "REP",
        sources=[sos_house(2022), pg(2022)],
        notes="Official 2022 SOS statewide House summary totals: Andrew Byron 2,235, Bob Strobel 1,681. Official 2022 Teton clerk portion: Strobel 938, Byron 873.")
    add("WY-BYRON-ANDREW", "Andrew Byron", "state-house", "House District 22 (H22)", "Teton County", 2025, 2027, 2024, "REP")
    add("WY-BYRON-ANDREW", "Andrew Byron", "state-house", "House District 22 (H22)", "Teton County", 2027, 2029, 2026, "REP")
    # Official 2012 Teton clerk H22 (Winney 993, Halverson 614) is the Teton portion only; district-wide official totals were not confirmed, so January 2013-2015 H22 is Not yet collected.

    # House 23
    add("WY-GINGERY-KEITH", "Keith Gingery", "state-house", "House District 23 (H23)", "Teton County", 2013, 2015, 2012, "REP")
    add("WY-SCHWARTZ-ANDY", "Andy Schwartz", "state-house", "House District 23 (H23)", "Teton County", 2015, 2017, 2014, "DEM",
        notes="Official 2014 Teton clerk: Andy Schwartz 2,133, Jim Darwiche 1,697.")
    add("WY-SCHWARTZ-ANDY", "Andy Schwartz", "state-house", "House District 23 (H23)", "Teton County", 2017, 2019, 2016, "DEM")
    add("WY-SCHWARTZ-ANDY", "Andy Schwartz", "state-house", "House District 23 (H23)", "Teton County", 2019, 2021, 2018, "DEM",
        notes="Official 2018 Teton clerk: Andy Schwartz 3,358, Alex Muromcew 1,979.")
    add("WY-SCHWARTZ-ANDY", "Andy Schwartz", "state-house", "House District 23 (H23)", "Teton County", 2021, 2023, 2020, "DEM")
    add("WY-STORER-LIZ", "Liz Storer", "state-house", "House District 23 (H23)", "Teton County", 2023, 2025, 2022, "DEM",
        notes="Official 2022 Teton clerk: Liz Storer 2,489, Paul Vogelheim 2,326.")
    add("WY-STORER-LIZ", "Liz Storer", "state-house", "House District 23 (H23)", "Teton County", 2025, 2027, 2024, "DEM")
    add("WY-STORER-LIZ", "Liz Storer", "state-house", "House District 23 (H23)", "Teton County", 2027, 2029, 2026, "DEM",
        notes="Official 2026 Teton clerk: Liz Storer 3,274, Shannon A. Brennan 1,598.")

    # Commissioners: midterm VF3, presidential VF2.
    add("WY-ALLEN-BARBARA", "Barbara Allen", "county", "County Commissioner", "Teton County", 2013, 2017, 2012, "REP")
    add("WY-TURLEY-MELISSA", "Melissa Turley", "county", "County Commissioner", "Teton County", 2013, 2017, 2012, "DEM")
    add("WY-NEWCOMB-MARK", "Mark Newcomb", "county", "County Commissioner", "Teton County", 2015, 2019, 2014, "DEM")
    add("WY-VOGELHEIM-PAUL", "Paul Vogelheim", "county", "County Commissioner", "Teton County", 2015, 2019, 2014, "REP")
    add("WY-RHEA-SMOKEY", "Smokey Rhea", "county", "County Commissioner", "Teton County", 2015, 2019, 2014, "DEM",
        notes="Official 2014 Teton clerk Vote-For-3: Mark Newcomb 3,914, Paul Vogelheim 3,372, Smokey Rhea 3,248.")
    add("WY-EPSTEIN-GREGORY-W", "Greg Epstein", "county", "County Commissioner", "Teton County", 2017, 2021, 2016, "DEM")
    add("WY-MACKER-NATALIA-D", "Natalia D. Macker", "county", "County Commissioner", "Teton County", 2017, 2021, 2016, "DEM",
        notes="Official 2016 Teton clerk Vote-For-2: Greg Epstein 6,242, Natalia D. Macker 5,811.")
    add("WY-NEWCOMB-MARK", "Mark Newcomb", "county", "County Commissioner", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-PROPST-LUTHER", "Luther Propst", "county", "County Commissioner", "Teton County", 2019, 2023, 2018, "DEM",
        notes="Official 2018 Teton clerk is an official scan. OCR of that official summary: Mark Newcomb 6,128, Luther Propst 5,090 (14.33%), Mark Barron 5,013.")
    add("WY-BARRON-MARK", "Mark Barron", "county", "County Commissioner", "Teton County", 2019, 2023, 2018, "REP")
    add("WY-MACKER-NATALIA-D", "Natalia D. Macker", "county", "County Commissioner", "Teton County", 2021, 2025, 2020, "DEM")
    add("WY-EPSTEIN-GREGORY-W", "Gregory W. Epstein", "county", "County Commissioner", "Teton County", 2021, 2025, 2020, "DEM",
        notes="Official 2020 Teton clerk Vote-For-2: Natalia D. Macker 6,647, Gregory W. Epstein 5,149.")
    add("WY-NEWCOMB-MARK", "Mark Newcomb", "county", "County Commissioner", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-PROPST-LUTHER", "Luther Propst", "county", "County Commissioner", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-GARDNER-WES", "Wes Gardner", "county", "County Commissioner", "Teton County", 2023, 2027, 2022, "DEM",
        notes="Official 2022 Teton clerk Vote-For-3: Mark Newcomb 5,440, Luther Propst 5,099, Wes Gardner 4,946.")
    add("WY-MACKER-NATALIA-D", "Natalia D. Macker", "county", "County Commissioner", "Teton County", 2025, 2029, 2024, "DEM")
    add("WY-CARLMAN-LEN", "Len Carlman", "county", "County Commissioner", "Teton County", 2025, 2029, 2024, "DEM")
    add("WY-PROPST-LUTHER", "Luther Propst", "county", "County Commissioner", "Teton County", 2027, 2031, 2026, "DEM")
    add("WY-DUNFORD-ALI", "Ali Dunford", "county", "County Commissioner", "Teton County", 2027, 2031, 2026, "DEM")
    add("WY-CHIN-KARYN", "Karyn Chin", "county", "County Commissioner", "Teton County", 2027, 2031, 2026, "DEM",
        notes="Official 2026 Teton clerk Vote-For-3: Ali Dunford 6,227, Luther Propst 6,077, Karyn Chin 5,329.")

    # Row offices, midterm 4-year.
    add("WY-DAIGLE-SHERRY-L", "Sherry L. Daigle", "county", "County Clerk", "Teton County", 2015, 2019, 2014, "REP")
    add("WY-DAIGLE-SHERRY-L", "Sherry L. Daigle", "county", "County Clerk", "Teton County", 2019, 2023, 2018, "REP")
    add("WY-MURPHY-MAUREEN", 'Maureen "Mo" Murphy', "county", "County Clerk", "Teton County", 2023, 2027, 2022, "REP")
    add("WY-MURPHY-MAUREEN", 'Maureen "Mo" Murphy', "county", "County Clerk", "Teton County", 2027, 2031, 2026, "REP")

    add("WY-BAUR-DONNA-M", "Donna M. Baur", "county", "County Treasurer", "Teton County", 2015, 2019, 2014, "DEM")
    add("WY-SMITS-KATIE", "Katie Smits", "county", "County Treasurer", "Teton County", 2019, 2023, 2018, "REP")
    add("WY-SMITS-KATIE", "Katie Smits", "county", "County Treasurer", "Teton County", 2023, 2027, 2022, "REP")
    add("WY-SMITS-KATIE", "Katie Smits", "county", "County Treasurer", "Teton County", 2027, 2031, 2026, "REP")

    add("WY-CAVALLARO-ANDY", "Andy Cavallaro", "county", "County Assessor", "Teton County", 2015, 2019, 2014, "DEM")
    add("WY-SHINKLE-MELISSA", 'Melissa "Mel" Shinkle', "county", "County Assessor", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-SHINKLE-MELISSA", 'Melissa "Mel" Shinkle', "county", "County Assessor", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-NADER-ASHLEE", "Ashlee Nader", "county", "County Assessor", "Teton County", 2027, 2031, 2026, "DEM")

    add("WY-WHALEN-JIM", "Jim Whalen", "county", "County Sheriff", "Teton County", 2015, 2019, 2014, "REP")
    add("WY-CARR-MATT", "Matt Carr", "county", "County Sheriff", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-CARR-MATT", "Matt Carr", "county", "County Sheriff", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-CARR-MATT", "Matt Carr", "county", "County Sheriff", "Teton County", 2027, 2031, 2026, "DEM")

    add("WY-WEICHMAN-STEVE", "Steve Weichman", "county", "County Attorney", "Teton County", 2015, 2019, 2014, "REP")
    add("WY-WEISMAN-ERIN-E", "Erin Weisman", "county", "County Attorney", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-WEISMAN-ERIN-E", "Erin Weisman", "county", "County Attorney", "Teton County", 2023, "2024-08-01", 2022, "DEM",
        confidence="medium",
        notes="Official 2022 Teton clerk winner. Official Wyoming Judicial Branch 9th JD Jackson circuit page: appointed circuit judge August 2024 (day unstated; term_end 2024-08-01, medium). No official appointment date for successor Richard Stout was found, so January 2025-2026 County Attorney is Not yet collected. Official 2026 general winner Richard \"Dick\" Stout takes office January 2027.")
    add("WY-STOUT-RICHARD", 'Richard "Dick" Stout', "county", "County Attorney", "Teton County", 2027, 2031, 2026, "DEM")

    add("WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux", "county", "Clerk of District Court", "Teton County", 2015, 2019, 2014, "DEM")
    add("WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux Sutton", "county", "Clerk of District Court", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux Sutton", "county", "Clerk of District Court", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux Sutton", "county", "Clerk of District Court", "Teton County", 2027, 2031, 2026, "DEM")

    add("WY-BLUE-BRENT", 'Brent "Doc" Blue', "county", "County Coroner", "Teton County", 2015, 2019, 2014, "DEM")
    add("WY-BLUE-BRENT", 'Brent "Doc" Blue', "county", "County Coroner", "Teton County", 2019, 2023, 2018, "DEM")
    add("WY-BLUE-BRENT", 'Brent "Doc" Blue', "county", "County Coroner", "Teton County", 2023, 2027, 2022, "DEM")
    add("WY-CLAUSON-KATRINA-L", "Katrina L. Clauson", "county", "County Coroner", "Teton County", 2027, 2031, 2026, "DEM")
    return terms
def judicial_terms():
    terms = []

    def jt(pid, name, office, start, end, ey=None, how="retained", conf="high", src=None, notes=""):
        terms.append(T(
            person_id=pid, name=name, party="",
            office_group="judicial", office=office, jurisdiction="9th Judicial District",
            term_start=start, term_end=end, how_took_office=how,
            election_year=ey, confidence=conf, sources=src or ([] if ey not in PG else [pg(ey)]),
            notes=notes,
        ))

    dist = "District Judge, 9th Judicial District"
    circ = "Circuit Judge, 9th Judicial District"

    # District — official wyocourts pages retrieved 2026-11-24 plus official clerk/SOS retentions.
    jt("WY-YOUNG-NORMAN-E", "Norman E. Young", dist, FM[2011], FM[2017], 2010, "retained", "high",
       [sos(2010)], "Official 2010 SOS Teton general PbP: retained Norman E. Young.")
    jt("WY-YOUNG-NORMAN-E", "Norman E. Young", dist, FM[2017], FM[2023], 2016, "retained", "high",
       [sos(2016), pg(2016)],
       "Official 2016 SOS / official 2016 Teton clerk: retained Norman E. Young. Official Sublette 9th JD district page: Katharine/Kate G. McKay appointed January 2023.")
    jt("WY-TYLER-MARVIN-L", "Marvin L. Tyler", dist, FM[2011], FM[2017], 2010, "retained", "high",
       [sos(2010)], "Official 2010 SOS Teton general PbP: retained Marvin L. Tyler.")
    jt("WY-TYLER-MARVIN-L", "Marvin L. Tyler", dist, FM[2017], FM[2023], 2016, "retained", "high",
       [sos(2016), pg(2016)], "Official 2016 SOS / official 2016 Teton clerk: retained Marvin L. Tyler. No official departure date after January 2023 was found; Conder was appointed July 2019.")
    jt("WY-DAY-TIMOTHY-C", "Timothy C. Day", dist, FM[2013], FM[2019], 2012, "retained", "high",
       [sos(2012), pg(2012)], "Official 2012 SOS / official 2012 Teton clerk: retained Timothy C. Day.")
    jt("WY-DAY-TIMOTHY-C", "Timothy C. Day", dist, FM[2019], "2022-01-01", 2018, "retained", "medium",
       [sos(2018), pg(2018), courts("teton-d")],
       "Official 2018 SOS / official 2018 Teton clerk: retained Timothy C. Day. Official Wyoming Judicial Branch Teton 9th JD district page: Melissa M. Owens appointed January 2022 (day unstated; Day term_end 2022-01-01, medium).")
    jt("WY-OWENS-MELISSA-M", "Melissa M. Owens", dist, "2022-01-01", FM[2031], 2024, "appointed", "medium",
       [courts("teton-d"), pg(2024), sos(2024)],
       "Official Wyoming Judicial Branch Teton 9th JD district page: appointed January 2022 (day unstated), retained November 2024, term expires January 2031, stands November 2030. Official 2024 Teton clerk and official 2024 SOS: Melissa M. Owens.")
    jt("WY-CONDER-JASON-M", "Jason M. Conder", dist, "2019-07-01", FM[2027], 2020, "appointed", "medium",
       [courts("fremont-d"), sos(2020), pg(2020)],
       "Official Wyoming Judicial Branch Fremont 9th JD district page: appointed July 2019 (day unstated; term_start 2019-07-01, medium), retained November 2020, term expires January 2027, stands November 2026. Official 2020 clerk last-name CONDER filled from official SOS and the court page.")
    jt("WY-CONDER-JASON-M", "Jason M. Conder", dist, FM[2027], FM[2031], 2026, "retained", "high",
       [sos(2026), courts("fremont-d"), pg(2026)],
       "Official 2026 SOS Teton general PbP and official Fremont 9th JD district page: Jason M. Conder, retained. Official 2026 Teton clerk line prints RETAIN JUDGE JAMES M. CONDER (a typo); encoded as Jason M. Conder from the official SOS and court page.")
    jt("WY-MCKAY-KATHARINE-G", "Katharine G. McKay", dist, "2023-01-01", FM[2031], 2024, "appointed", "medium",
       [courts("sublette-d"), pg(2024), sos(2024)],
       "Official Wyoming Judicial Branch Sublette 9th JD district page: Honorable Kate G. McKay, appointed January 2023 (day unstated), retained November 2024, term expires January 2031, stands November 2030. Official 2024 Teton clerk and official 2024 SOS print Katharine G. McKay; that official ballot/SOS name is used here, and the court-page short form is the same person.")

    # Circuit
    jt("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", circ, FM[2011], FM[2015], 2010, "retained", "high", [sos(2010)])
    jt("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", circ, FM[2015], FM[2019], 2014, "retained", "high", [sos(2014), pg(2014)])
    jt("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", circ, FM[2019], FM[2023], 2018, "retained", "high", [sos(2018), pg(2018)])
    jt("WY-ROBERTS-WESLEY-A", "Wesley A. Roberts", circ, FM[2023], "2024-08-01", 2022, "retained", "medium",
       [sos(2022), pg(2022), courts("teton-c")],
       "Official 2022 SOS: Wesley A. Roberts. Official 2022 Teton clerk last-name-only JUDGE ROBERTS filled from official SOS. Official Wyoming Judicial Branch Jackson circuit page: Erin E. Weisman appointed August 2024 (day unstated; Roberts term_end 2024-08-01, medium) as the Jackson circuit judge. The 2022 retain would otherwise have run through January 2027.")
    jt("WY-WEISMAN-ERIN-E", "Erin E. Weisman", circ, "2024-08-01", FM[2027], None, "appointed", "medium",
       [courts("teton-c")],
       "Official Wyoming Judicial Branch Jackson circuit page: appointed August 2024 (day unstated; term_start 2024-08-01, medium), term expires January 2027, stands November 2026. Same person as official 2018 and 2022 Teton County Attorney Erin Weisman.")
    jt("WY-WEISMAN-ERIN-E", "Erin E. Weisman", circ, FM[2027], FM[2031], 2026, "retained", "high",
       [pg(2026), sos(2026), courts("teton-c")],
       "Official 2026 Teton clerk: ERIN E. WEISMAN, YES, continuing January 2027–2031.")
    jt("WY-DENHARDT-ROBERT-B", "Robert B. Denhardt", circ, FM[2013], FM[2017], 2012, "retained", "high",
       [sos(2012)], "Official 2012 SOS prints Rob Denhardt; official later SOS lines use Robert B. Denhardt.")
    jt("WY-DENHARDT-ROBERT-B", "Robert B. Denhardt", circ, FM[2017], FM[2021], 2016, "retained", "high", [sos(2016), pg(2016)])
    jt("WY-DENHARDT-ROBERT-B", "Robert B. Denhardt", circ, FM[2021], FM[2025], 2020, "retained", "high",
       [sos(2020), pg(2020)], "Official 2020 Teton clerk last-name DENHARDT filled from official SOS: Robert B. Denhardt.")
    jt("WY-HAWS-CURT-A", "Curt A. Haws", circ, FM[2013], FM[2017], 2012, "retained", "high",
       [sos(2012)], "Official 2016 SOS prints Curt Haws; official later lines use Curt A. Haws.")
    jt("WY-HAWS-CURT-A", "Curt A. Haws", circ, FM[2017], FM[2021], 2016, "retained", "high", [sos(2016), pg(2016)])
    jt("WY-HAWS-CURT-A", "Curt A. Haws", circ, FM[2021], FM[2025], 2020, "retained", "high",
       [sos(2020), pg(2020)], "Official 2020 Teton clerk last-name HAWS filled from official SOS.")
    jt("WY-RADDA-JAMES-L", "James L. Radda", circ, FM[2013], FM[2017], 2012, "retained", "high", [sos(2012)])
    jt("WY-RADDA-JAMES-L", "James L. Radda", circ, FM[2017], FM[2021], 2016, "retained", "high", [sos(2016), pg(2016)])
    jt("WY-RADDA-JAMES-L", "James L. Radda", circ, FM[2021], FM[2025], 2020, "retained", "high",
       [sos(2020), pg(2020)], "Official 2020 Teton clerk last-name RADDA filled from official SOS: James L. Radda.")
    jt("WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", circ, "2021-10-01", FM[2027], 2022, "appointed", "medium",
       [courts("fremont-c"), sos(2022), pg(2022)],
       "Official Wyoming Judicial Branch Lander circuit page: Jefferson Coombs, appointed October 2021 (day unstated; term_start 2021-10-01, medium), term expires January 2027, stands November 2026. Official 2022 SOS: Jefferson Boone Coombs. Official 2022 Teton clerk last-name-only COOMBS filled from that SOS and court page.")
    jt("WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", circ, FM[2027], FM[2031], 2026, "retained", "high",
       [pg(2026), sos(2026), courts("fremont-c")],
       "Official 2026 Teton clerk: JEFFERSON BOONE COOMBS, YES, continuing January 2027–2031.")
    jt("WY-STEBNER-DANIEL-M", "Daniel M. Stebner", circ, "2023-02-01", FM[2029], 2024, "appointed", "medium",
       [courts("riverton-c"), pg(2024), sos(2024)],
       "Official Wyoming Judicial Branch Riverton circuit page: appointed February 2023 (day unstated; term_start 2023-02-01, medium), retained November 2024, term expires January 2029, stands November 2028. Official 2024 Teton clerk and official 2024 SOS: Daniel M. Stebner.")
    jt("WY-LABUDA-JOHN", "John LaBuda", circ, "2023-01-01", FM[2029], 2024, "appointed", "medium",
       [courts("sublette-c"), pg(2024), sos(2024)],
       "Official Wyoming Judicial Branch Pinedale circuit page: appointed January 2023 (day unstated; term_start 2023-01-01, medium), retained November 2024, term expires January 2029, stands November 2028. Official 2024 Teton clerk and official 2024 SOS: John LaBuda.")
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

    # Town of Jackson — official clerks put MAYOR on the November ballot. Official Town of Jackson
    # pages and the FY2024 ACFR: mayor and four council members elected at large; effective 2017
    # the mayor serves a four-year term. Not council-selected.
    add("WY-BARRON-MARK", "Mark Barron", "municipal", "Jackson Mayor", "Town of Jackson", 2013, 2015, 2012,
        notes="Official 2012 Teton clerk: Mark Barron 2,692, Jim Fulmer 1,274. Two-year mayoral term observed before the four-year term effective 2017.")
    add("WY-FLITNER-SARA", "Sara Flitner", "municipal", "Jackson Mayor", "Town of Jackson", 2015, 2017, 2014,
        notes="Official 2014 Teton clerk: Sara Flitner 1,455, Mark Nowlin 1,415.")
    add("WY-MULDOON-PETE", "Pete Muldoon", "municipal", "Jackson Mayor", "Town of Jackson", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk: Pete Muldoon 2,415, Sara Flitner 2,376. First four-year mayoral term after the 2017 change. No mayor contest on official 2018 or 2022 clerks.")
    add("WY-LEVINSON-HAILEY-MORTON", "Hailey Morton Levinson", "municipal", "Jackson Mayor", "Town of Jackson", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk: Hailey Morton Levinson 3,405, Michael Kudar 2,140.")
    add("WY-JORGENSEN-ARNE-OLAUS", "Arne Olaus Jorgensen", "municipal", "Jackson Mayor", "Town of Jackson", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk: Arne Olaus Jorgensen 3,133, Jessica Sell Chambers 1,542. No mayor contest on the official 2026 clerk, consistent with the four-year cycle.")

    # Council VF2 staggered four-year terms.
    add("WY-LEVINSON-HAILEY-MORTON", "Hailey Morton", "municipal", "Jackson Town Council", "Town of Jackson", 2013, 2017, 2012)
    add("WY-STANFORD-JIM", "Jim Stanford", "municipal", "Jackson Town Council", "Town of Jackson", 2013, 2017, 2012,
        notes="Official 2012 Teton clerk Vote-For-2: Hailey Morton 2,052, Jim Stanford 1,718.")
    add("WY-FRANK-DON", "Don Frank", "municipal", "Jackson Town Council", "Town of Jackson", 2015, 2019, 2014)
    add("WY-LENZ-BOB", "Bob Lenz", "municipal", "Jackson Town Council", "Town of Jackson", 2015, 2019, 2014,
        notes="Official 2014 Teton clerk Vote-For-2: Don Frank 1,636, Bob Lenz 1,463.")
    add("WY-STANFORD-JIM", "Jim Stanford", "municipal", "Jackson Town Council", "Town of Jackson", 2017, 2021, 2016)
    add("WY-LEVINSON-HAILEY-MORTON", "Hailey Morton Levinson", "municipal", "Jackson Town Council", "Town of Jackson", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk Vote-For-2: Jim Stanford 2,290, Hailey Morton Levinson 2,208.")
    add("WY-SCHECHTER-JONATHAN", "Jonathan Schechter", "municipal", "Jackson Town Council", "Town of Jackson", 2019, 2023, 2018)
    add("WY-JORGENSEN-ARNE-OLAUS", "Arne Olaus Jorgensen", "municipal", "Jackson Town Council", "Town of Jackson", 2019, 2023, 2018,
        notes="Official 2018 Teton clerk (OCR of official scan) Vote-For-2: Jonathan Schechter 2,178, Arne Olaus Jorgensen 2,040.")
    add("WY-ROOKS-JIM", "Jim Rooks", "municipal", "Jackson Town Council", "Town of Jackson", 2021, 2025, 2020)
    add("WY-CHAMBERS-JESSICA-SELL", "Jessica Chambers", "municipal", "Jackson Town Council", "Town of Jackson", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk Vote-For-2: Jim Rooks 2,797, Jessica Chambers 2,574.")
    add("WY-SCHECHTER-JONATHAN", "Jonathan Schechter", "municipal", "Jackson Town Council", "Town of Jackson", 2023, 2027, 2022)
    add("WY-JORGENSEN-ARNE-OLAUS", "Arne Olaus Jorgensen", "municipal", "Jackson Town Council", "Town of Jackson", 2023, 2025, 2022,
        notes="Official 2022 Teton clerk Vote-For-2: Arne Olaus Jorgensen 2,254, Jonathan Schechter 1,831. Jorgensen is the official 2024 mayor and takes office January 2025; this council term is ended at January 2025 so the same person is not shown in both offices. No official appointment filling that council seat was found, so January 2025–2026 has three named council members plus one Not yet collected seat. Official 2026 winner Alyson Spery takes office January 2027.")
    add("WY-REGAN-KEVIN", "Kevin Regan", "municipal", "Jackson Town Council", "Town of Jackson", 2025, 2029, 2024)
    add("WY-VIEHMAN-DEVON", "Devon Viehman", "municipal", "Jackson Town Council", "Town of Jackson", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk Vote-For-2: Kevin Regan 2,349, Devon Viehman 2,061.")
    add("WY-SCHECHTER-JONATHAN", "Jonathan Schechter", "municipal", "Jackson Town Council", "Town of Jackson", 2027, 2031, 2026)
    add("WY-SPERY-ALYSON", "Alyson Spery", "municipal", "Jackson Town Council", "Town of Jackson", 2027, 2031, 2026,
        notes="Official 2026 Teton clerk Vote-For-2: Jonathan Schechter 2,323, Alyson Spery 2,171.")

    # Teton County School District #1 — midterm VF3, presidential VF4, seven-member board.
    add("WY-MEAD-KATE", "Kate Mead", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2013, 2017, 2012)
    add("WY-ELLIOTT-SYD", "Syd Elliott", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2013, 2017, 2012)
    add("WY-RUSSELL-PATRICIA-A", "Patricia A. Russell", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2013, 2017, 2012)
    add("WY-FARROW-ROBBI", "Robbi Farrow", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2013, 2017, 2012,
        notes="Official 2012 Teton clerk Vote-For-4: Kate Mead 6,393, Syd Elliott 3,457, Patricia A. Russell 3,303, Robbi Farrow 3,141.")
    add("WY-GINGERY-KEITH", "Keith Gingery", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2015, 2019, 2014)
    add("WY-LARROW-JOE", "Joe Larrow", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2015, 2019, 2014)
    add("WY-TESKE-JANINE-BAY", "Janine Bay Teske", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2015, 2019, 2014,
        notes="Official 2014 Teton clerk Vote-For-3: Keith Gingery 4,931, Joe Larrow 4,034, Janine Bay Teske 3,863.")
    add("WY-MEAD-KATE", "Kate Mead", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2017, 2021, 2016)
    add("WY-CARLIN-BETSY", "Betsy Carlin", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2017, 2021, 2016)
    add("WY-SCARLETT-BILL", "Bill Scarlett", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2017, 2021, 2016)
    add("WY-BAND-ANNIE", "Annie Band", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk Vote-For-4: Kate Mead 5,540, Betsy Carlin 4,639, Bill Scarlett 4,616, Annie Band 3,759.")
    add("WY-BRUMSTED-ALAN", "Alan Brumsted", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2019, 2023, 2018)
    add("WY-GINGERY-KEITH", "Keith Gingery", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2019, 2023, 2018)
    add("WY-TESKE-JANINE-BAY", "Janine Bay Teske", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2019, 2023, 2018,
        notes="Official 2018 Teton clerk (OCR of official scan) Vote-For-3: Alan Brumsted 5,266, Keith Gingery 5,053, Janine Bay Teske 4,257.")
    add("WY-MEAD-KATE", "Kate Mead", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2021, 2025, 2020)
    add("WY-CARLIN-BETSY", "Betsy Carlin", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2021, 2025, 2020)
    add("WY-ZUNG-JENNIFER", "Jennifer Zung", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2021, 2025, 2020)
    add("WY-SCARLETT-BILL", "Bill Scarlett", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk Vote-For-4: Kate Mead 8,209, Betsy Carlin 7,230, Jennifer Zung 6,388, Bill Scarlett 5,928.")
    add("WY-GINGERY-KEITH", "Keith Gingery", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2023, 2027, 2022)
    add("WY-DORNAN-READE", "Reade Dornan", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2023, 2027, 2022)
    add("WY-ABRAMS-STEPHAN", "Stephan Abrams", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2023, 2027, 2022,
        notes="Official 2022 Teton clerk Vote-For-3: Keith Gingery 4,365, Reade Dornan 3,981, Stephan Abrams 3,608.")
    add("WY-MEAD-KATE", "Kate Mead", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2025, 2029, 2024)
    add("WY-CARLIN-BETSY", "Betsy Carlin", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2025, 2029, 2024)
    add("WY-SCARLETT-BILL", "Bill Scarlett", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2025, 2029, 2024)
    add("WY-BOSCH-JERRY", "Jerry Bosch", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk Vote-For-4: Kate Mead 7,616, Betsy Carlin 6,788, Bill Scarlett 6,003, Jerry Bosch 4,803.")
    rec = {"label": "Teton County official 2026 general recount, Teton County School District #1 Trustee",
           "url": "https://www.tetoncountywy.gov/DocumentCenter/View/42629/2026-General-Election-Official-Recount-Summary-TCSD-1-Trustee"}
    add("WY-GINGERY-KEITH", "Keith Gingery", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2027, 2031, 2026, sources=[rec, pg(2026)])
    add("WY-SINCLAIR-ASHLEY", "Ashley Sinclair", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2027, 2031, 2026, sources=[rec, pg(2026)])
    add("WY-ABRAMS-STEPHAN", "Stephan Abrams", "schools", "TCSD #1 Trustee", "Teton County School District #1", 2027, 2031, 2026,
        sources=[rec, pg(2026)],
        notes="Official 2026 Teton clerk recount (DocumentCenter 42629, footer 11/06/2026) is the official result, Vote-For-3: Keith Gingery 5,426, Ashley Sinclair 4,858, Stephan Abrams 4,818, over Reade W. Dornan 4,770. Same order as the first official general summary.")

    # St. John's Hospital District
    add("WY-HAYSE-BRUCE", "Bruce Hayse", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2013, 2017, 2012)
    add("WY-GIBSON-C-SCOTT", "Scott Gibson", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2013, 2017, 2012)
    add("WY-HALL-ZACH", "Zach Hall", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2013, 2017, 2012,
        notes="Official 2012 Teton clerk Vote-For-3: Bruce Hayse 6,981, Scott Gibson 4,604, Zach Hall 4,358.")
    add("WY-ALBRIGHT-JOE", "Joe Albright", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2015, 2019, 2014)
    add("WY-MASEK-ELIZABETH-C", "Elizabeth C. Masek", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2015, 2019, 2014)
    add("WY-TENNICAN-MICHAEL", "Michael Tennican", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2015, 2019, 2014,
        notes="Official 2014 Teton clerk Vote-For-4: Joe Albright 3,737, Elizabeth C. Masek 2,912, Barbara Herz 2,818, Michael Tennican 2,695.")
    add("WY-HERZ-BARBARA", "Barbara Herz", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2015, 2019, 2014)
    add("WY-HAYSE-BRUCE", "Bruce Hayse", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2017, 2021, 2016)
    add("WY-HOGAN-CYNTHIA", "Cynthia Hogan", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2017, 2021, 2016)
    add("WY-GIBSON-C-SCOTT", "C. Scott Gibson", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk Vote-For-3: Bruce Hayse 7,322, Cynthia Hogan 4,125, C. Scott Gibson 3,861.")
    add("WY-ALBRIGHT-JOE", "Joe Albright", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2019, 2023, 2018)
    add("WY-AURELIO-LINDA", "Linda Aurelio", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2019, 2023, 2018)
    add("WY-MASEK-ELIZABETH-C", "Elizabeth Masek", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2019, 2023, 2018)
    add("WY-TENNICAN-MICHAEL", "Michael Tennican", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2019, 2023, 2018,
        notes="Official 2018 Teton clerk (OCR of official scan) Vote-For-4: Joe Albright 5,724, Linda Aurelio 4,629, Elizabeth Masek 4,560, Michael Tennican 4,071.")
    add("WY-HAYSE-BRUCE", "Bruce Hayse", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2021, 2025, 2020)
    add("WY-HOGAN-CYNTHIA", "Cynthia Hogan", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2021, 2025, 2020)
    add("WY-GIBSON-C-SCOTT", "C. Scott Gibson", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk Vote-For-3 (4-year): Bruce Hayse 8,347, Cynthia Hogan 7,688, C. Scott Gibson 6,720.")
    add("WY-CRITZER-SUE", "Sue Critzer", "special-districts", "St. John's Hospital District Trustee (2-year unexpired)", "St. John's Hospital District", 2021, 2023, 2020,
        notes="Official 2020 Teton clerk: St. John's Hospital Dist Trustee 2YR UNEXPIRED, Sue Critzer 9,155. January 2021–2022 hospital snapshots may exceed a typical seven-member board because these official unexpired seats are encoded without inventing which 2018 seats they replaced.")
    add("WY-HOPKINS-DEBORAH-C", "Deborah C. Hopkins", "special-districts", "St. John's Hospital District Trustee (2-year unexpired)", "St. John's Hospital District", 2021, 2023, 2020,
        notes="Official 2020 Teton clerk: St. John's Hospital Dist Trustee 2YR UNEXPIRED TERM, Deborah C. Hopkins 9,159.")
    add("WY-CONOVER-KELLER-KATHARINE", "Katharine Conover-Keller", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2023, 2027, 2022)
    add("WY-BLUE-BRENT", 'Brent "Doc" Blue', "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2023, 2027, 2022)
    add("WY-HOCHHEISER-LOU", "Lou Hochheiser", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2023, 2027, 2022)
    add("WY-CUTLER-PAM", "Pam Cutler", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2023, 2027, 2022,
        notes="Official 2022 Teton clerk Vote-For-4: Katharine Conover-Keller 4,407, Brent \"Doc\" Blue 3,618, Lou Hochheiser 3,512, Pam Cutler 3,481.")
    add("WY-HAYSE-BRUCE", "Bruce Hayse", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2025, 2029, 2024)
    add("WY-HUNT-JIM", "Jim Hunt", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2025, 2029, 2024)
    add("WY-HOGLUND-BILL", "Bill Hoglund", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2025, 2029, 2024)
    add("WY-BRENNAN-SHANNON-A", "Shannon A. Brennan", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk Vote-For-4: Bruce Hayse 6,694, Jim Hunt 6,017, Bill Hoglund 4,993, Shannon A. Brennan 4,857. Official 2024 recount (SPET and hospital) did not change these candidate totals versus the official general summary dated 11/08/2024.")
    add("WY-CONOVER-KELLER-KATHARINE", "Katharine Conover-Keller", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2027, 2031, 2026)
    add("WY-CUTLER-PAM", "Pam Cutler", "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2027, 2031, 2026)
    add("WY-BLUE-BRENT", 'Brent "Doc" Blue', "special-districts", "St. John's Hospital District Trustee", "St. John's Hospital District", 2027, 2031, 2026,
        notes="Official 2026 Teton clerk Vote-For-3: Katharine Conover-Keller 6,292, Pam Cutler 5,553, Brent \"Doc\" Blue 5,219.")

    # Conservation — official titles as printed.
    add("WY-LUCAS-BOB", "Bob Lucas", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2015, 2019, 2014)
    add("WY-SHUPTRINE-SANDY", "Sandy Shuptrine", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2015, 2019, 2014)
    add("WY-ADAMS-DAVID-C", "David C. Adams", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2015, 2019, 2014,
        notes="Official 2014 Teton clerk Vote-For-3: Bob Lucas 4,621, Sandy Shuptrine 4,455, David C. Adams 3,513.")
    add("WY-CAMPBELL-THOMAS-M", "Thomas M. Campbell", "special-districts", "Teton Conservation District Supervisor", "Teton Conservation District", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk prints two Vote-For-1 contests both titled Teton Conservation District, without Urban/Rural/At-Large labels. Official winners are Thomas M. Campbell 4,478 and Bailey K. Schreiber 7,248. Titles are not invented.")
    add("WY-SCHREIBER-BAILEY-K", "Bailey K. Schreiber", "special-districts", "Teton Conservation District Supervisor", "Teton Conservation District", 2017, 2021, 2016,
        notes="Official 2016 Teton clerk Vote-For-1 Teton Conservation District: Bailey K. Schreiber 7,248.")
    add("WY-LUCAS-BOB", "Bob Lucas", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2019, 2023, 2018)
    add("WY-ADAMS-DAVID-C", "David C. Adams", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2019, 2023, 2018)
    add("WY-MCDONALD-STEVE", "Steve McDonald", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2019, 2023, 2018,
        notes="Official 2018 Teton clerk (OCR of official scan) Vote-For-3 rural: Bob Lucas 6,003, David C. Adams 4,325, Steve McDonald 4,060.")
    add("WY-FULLER-NATE", "Nate Fuller", "special-districts", "Teton Conservation District Supervisor At-Large", "Teton Conservation District", 2019, 2023, 2018,
        notes="Official 2018 Teton clerk (OCR of official scan) Vote-For-1 at-large: Nate Fuller 4,839, Pietro Castelli 1,778.")
    add("WY-HURLEY-ROBY", "Roby Hurley", "special-districts", "Teton Conservation District Supervisor Urban", "Teton Conservation District", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk Vote-For-1 urban: Roby Hurley 9,644.")
    add("WY-FULLER-NATE", "Nate Fuller", "special-districts", "Teton Conservation District Supervisor At-Large", "Teton Conservation District", 2021, 2025, 2020,
        notes="Official 2020 Teton clerk Vote-For-1 at-large: Nate Fuller 9,962.")
    add("WY-WATSABAUGH-CATE", "Cate Watsabaugh", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2023, 2027, 2022)
    add("WY-LUCAS-BOB", "Bob Lucas", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2023, 2027, 2022)
    add("WY-ADAMS-DAVID-C", "David C. Adams", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2023, 2027, 2022,
        notes="Official 2022 Teton clerk Vote-For-3 rural: Cate Watsabaugh 5,086, Bob Lucas 4,215, David C. Adams 3,336.")
    add("WY-FARBOD-KATHY", "Kathy Farbod", "special-districts", "Teton Conservation District Supervisor At-Large", "Teton Conservation District", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk Vote-For-1 at-large: Kathy Farbod 8,417.")
    add("WY-HURLEY-ROBY", "Roby Hurley", "special-districts", "Teton Conservation District Supervisor Urban", "Teton Conservation District", 2025, 2029, 2024,
        notes="Official 2024 Teton clerk Vote-For-1 urban: Roby Hurley 8,589.")
    add("WY-WATSABAUGH-CATE", "Cate Watsabaugh", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2027, 2031, 2026)
    add("WY-ADAMS-DAVID-C", "David C. Adams", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2027, 2031, 2026)
    add("WY-LUCAS-BOB", "Bob Lucas", "special-districts", "Teton Conservation District Supervisor Rural", "Teton Conservation District", 2027, 2031, 2026,
        notes="Official 2026 Teton clerk Vote-For-3 rural: Cate Watsabaugh 6,533, David C. Adams 4,225, Bob Lucas 4,052.")
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


def build_teton():
    people = {}
    P = H.person_factory(people)
    register_people(P)

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
        # Do not copy other judicial districts. Teton is in the 9th JD.

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 16 (S16)", 1),
            ("Senate District 17 (S17)", 1),
        ],
        "state-house": [
            ("House District 16 (H16)", 1),
            ("House District 22 (H22)", 1),
            ("House District 23 (H23)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Jackson Mayor", 1),
            ("Jackson Town Council", 4),
        ],
    }

    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "9th Judicial District judges (Teton, Fremont, and Sublette). Official 2026 Teton clerk prints RETAIN JUDGE "
        "JAMES M. CONDER; the official 2026 SOS Teton precinct-by-precinct summary and the official Wyoming Judicial "
        "Branch Fremont 9th JD district page print Jason M. Conder, which is the name used here. Official 2024 clerk "
        "and official 2024 SOS print Katharine G. McKay; the official Sublette 9th JD district page prints Kate G. "
        "McKay for the same person. Where an official Teton clerk summary prints only a last name (official 2022 "
        "JUDGE ROBERTS / COOMBS; official 2020 CONDER / DENHARDT / HAWS / RADDA), the full name is taken from an "
        "official SOS line or official Wyoming Judicial Branch 9th JD page, and that source is cited. Judges of other "
        "districts are not copied here."
    )
    special_note = (
        "Municipal, school, and special-district names are keyed from official Teton November general results in this "
        "archive. The Town of Jackson is the only incorporated municipality. Official Town of Jackson government pages "
        "and the FY2024 ACFR state that the mayor and four council members are elected at large; effective 2017 the "
        "mayor serves a four-year term. Official clerk generals put MAYOR contests on the November ballot (2012, 2014, "
        "2016, 2020, 2024). Official 2026 Teton County School District #1 Trustee totals are from the official recount "
        "(DocumentCenter 42629). Official 2018 and official 2024 Teton clerk generals are official scans; those totals "
        "are from OCR of the official pages. Arne Olaus Jorgensen's official 2022 council term is ended at January 2025 "
        "when he takes office as mayor from the official 2024 clerk; no official appointment filling that council seat "
        "was found. Official 2016 conservation contests are titled only Teton Conservation District on the official "
        "clerk, without Urban/Rural/At-Large labels. Official mid-term vacancies are not invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Teton primary PDFs are "
        "archived under /workspace/wyoleg/local-results/teton/<year>/. The current (November 2026) precinct roster is "
        "in data/county_officials/teton.json, from the official 2026 primary (named winners only; 17 precincts / 57 holders)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Teton", county_number=22, slug="teton", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Teton", slug="teton")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def update_teton_json(people: dict):
    path = ROOT / "data" / "county_officials" / "teton.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
    data["county_number"] = 22
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
        office("Senate District 16 (S16)", [
            _holder(people, "WY-DOCKSTADER-DAN", "Dan Dockstader", "REP", "January 2029",
                    notes="Official 2024 winner; not on the 2026 ballot. Also covers Lincoln County."),
        ]),
        office("Senate District 17 (S17)", [
            _holder(people, "WY-GIERAU-MIKE", "Mike Gierau", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
    ]
    house_offices = [
        office("House District 16 (H16)", [
            _holder(people, "WY-YIN-MIKE", "Mike Yin", "DEM", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("House District 22 (H22)", [
            _holder(people, "WY-BYRON-ANDREW", "Andrew Byron", "REP", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027. Also covers Lincoln County. Official SOS district-wide totals are used for this multi-county seat."),
        ]),
        office("House District 23 (H23)", [
            _holder(people, "WY-STORER-LIZ", "Liz Storer", "DEM", "January 2029",
                    notes="Official 2024 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
    ]
    county = [
        office("County Commissioner", [
            _holder(people, "WY-NEWCOMB-MARK", "Mark Newcomb", "DEM", "January 2027"),
            _holder(people, "WY-PROPST-LUTHER", "Luther Propst", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-GARDNER-WES", "Wes Gardner", "DEM", "January 2027"),
            _holder(people, "WY-MACKER-NATALIA-D", "Natalia D. Macker", "DEM", "January 2029"),
            _holder(people, "WY-CARLMAN-LEN", "Len Carlman", "DEM", "January 2029"),
            _holder(people, "WY-DUNFORD-ALI", "Ali Dunford", "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
            _holder(people, "WY-CHIN-KARYN", "Karyn Chin", "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Ali Dunford and Karyn Chin are official 2026 general winners and take office January 2027. Mark Newcomb and Wes Gardner's official 2022 terms end January 2027. Luther Propst continues."),
        office("County Clerk", [
            _holder(people, "WY-MURPHY-MAUREEN", 'Maureen "Mo" Murphy', "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Treasurer", [
            _holder(people, "WY-SMITS-KATIE", "Katie Smits", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Assessor", [
            _holder(people, "WY-SHINKLE-MELISSA", 'Melissa "Mel" Shinkle', "DEM", "January 2027"),
            _holder(people, "WY-NADER-ASHLEE", "Ashlee Nader", "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Ashlee Nader is the official 2026 general winner and takes office January 2027."),
        office("County Sheriff", [
            _holder(people, "WY-CARR-MATT", "Matt Carr", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Attorney", [
            _holder(people, "WY-STOUT-RICHARD", 'Richard "Dick" Stout', "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner. Official Wyoming Judicial Branch Jackson circuit page: Erin E. Weisman (official 2022 County Attorney) was appointed circuit judge August 2024. No official appointment date for Stout was found, so January 2025–2026 County Attorney is Not yet collected in the snapshots."),
        ], note="Richard \"Dick\" Stout is the official 2026 general winner and takes office January 2027. No official mid-term appointment date after Erin Weisman's August 2024 judicial appointment was found."),
        office("Clerk of District Court", [
            _holder(people, "WY-SUTTON-ANNE-COMEAUX", "Anne Comeaux Sutton", "DEM", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("County Coroner", [
            _holder(people, "WY-BLUE-BRENT", 'Brent "Doc" Blue', "DEM", "January 2027"),
            _holder(people, "WY-CLAUSON-KATRINA-L", "Katrina L. Clauson", "DEM", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Katrina L. Clauson is the official 2026 general winner and takes office January 2027."),
    ]
    municipal = [
        office("Jackson Mayor", [
            _holder(people, "WY-JORGENSEN-ARNE-OLAUS", "Arne Olaus Jorgensen", "", "January 2029",
                    notes="Official 2024 general winner. The Jackson mayor is elected on the official November ballot, not selected by the council."),
        ]),
        office("Jackson Town Council", [
            _holder(people, "WY-SCHECHTER-JONATHAN", "Jonathan Schechter", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-REGAN-KEVIN", "Kevin Regan", "", "January 2029"),
            _holder(people, "WY-VIEHMAN-DEVON", "Devon Viehman", "", "January 2029"),
            _holder(people, "WY-SPERY-ALYSON", "Alyson Spery", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ], note="Alyson Spery is the official 2026 general winner and takes office January 2027. Arne Olaus Jorgensen became mayor January 2025; no official appointment filling that council seat through January 2026 was found."),
    ]
    schools = [
        office("TCSD #1 Trustee", [
            _holder(people, "WY-GINGERY-KEITH", "Keith Gingery", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 recount winner, term begins January 2027."),
            _holder(people, "WY-DORNAN-READE", "Reade W. Dornan", "", "January 2027"),
            _holder(people, "WY-ABRAMS-STEPHAN", "Stephan Abrams", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 recount winner, term begins January 2027."),
            _holder(people, "WY-MEAD-KATE", "Kate Mead", "", "January 2029"),
            _holder(people, "WY-CARLIN-BETSY", "Betsy Carlin", "", "January 2029"),
            _holder(people, "WY-SCARLETT-BILL", "Bill Scarlett", "", "January 2029"),
            _holder(people, "WY-BOSCH-JERRY", "Jerry Bosch", "", "January 2029"),
            _holder(people, "WY-SINCLAIR-ASHLEY", "Ashley Sinclair", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 recount winner."),
        ], note="Official 2026 Teton County School District #1 Trustee result is the official recount (DocumentCenter 42629): Keith Gingery, Ashley Sinclair, and Stephan Abrams. Reade W. Dornan's official 2022 term ends January 2027."),
    ]
    special = [
        office("St. John's Hospital District Trustee", [
            _holder(people, "WY-CONOVER-KELLER-KATHARINE", "Katharine Conover-Keller", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-BLUE-BRENT", 'Brent "Doc" Blue', "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-HOCHHEISER-LOU", "Lou Hochheiser", "", "January 2027"),
            _holder(people, "WY-CUTLER-PAM", "Pam Cutler", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-HAYSE-BRUCE", "Bruce Hayse", "", "January 2029"),
            _holder(people, "WY-HUNT-JIM", "Jim Hunt", "", "January 2029"),
            _holder(people, "WY-HOGLUND-BILL", "Bill Hoglund", "", "January 2029"),
            _holder(people, "WY-BRENNAN-SHANNON-A", "Shannon A. Brennan", "", "January 2029"),
        ]),
        office("Teton Conservation District Supervisor Rural", [
            _holder(people, "WY-WATSABAUGH-CATE", "Cate Watsabaugh", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-ADAMS-DAVID-C", "David C. Adams", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
            _holder(people, "WY-LUCAS-BOB", "Bob Lucas", "", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027."),
        ]),
        office("Teton Conservation District Supervisor At-Large", [
            _holder(people, "WY-FARBOD-KATHY", "Kathy Farbod", "", "January 2029"),
        ]),
        office("Teton Conservation District Supervisor Urban", [
            _holder(people, "WY-HURLEY-ROBY", "Roby Hurley", "", "January 2029"),
        ]),
    ]
    judicial = [
        office("District Judge, 9th Judicial District", [
            _holder(people, "WY-OWENS-MELISSA-M", "Melissa M. Owens", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Teton 9th JD district page: appointed January 2022, retained November 2024, term expires January 2031."),
            _holder(people, "WY-CONDER-JASON-M", "Jason M. Conder", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Fremont 9th JD district page: appointed July 2019, retained November 2020; official 2026 SOS retained Jason M. Conder (official 2026 Teton clerk typo JAMES M. CONDER). Term after the 2026 retain begins January 2027 and expires January 2031."),
            _holder(people, "WY-MCKAY-KATHARINE-G", "Katharine G. McKay", "", "January 2031",
                    notes="Official 2024 clerk and official 2024 SOS: Katharine G. McKay. Official Sublette 9th JD district page prints Kate G. McKay for the same person, appointed January 2023, retained November 2024, term expires January 2031."),
        ]),
        office("Circuit Judge, 9th Judicial District", [
            _holder(people, "WY-WEISMAN-ERIN-E", "Erin E. Weisman", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Jackson circuit page: appointed August 2024; official 2026 Teton clerk ERIN E. WEISMAN, YES, continuing January 2027–2031."),
            _holder(people, "WY-COOMBS-JEFFERSON-BOONE", "Jefferson Boone Coombs", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Lander circuit page and official 2022 SOS: Jefferson Boone Coombs, appointed October 2021; official 2026 Teton clerk JEFFERSON BOONE COOMBS, YES, continuing January 2027–2031."),
            _holder(people, "WY-STEBNER-DANIEL-M", "Daniel M. Stebner", "", "January 2029",
                    notes="Official Wyoming Judicial Branch Riverton circuit page: appointed February 2023, retained November 2024."),
            _holder(people, "WY-LABUDA-JOHN", "John LaBuda", "", "January 2029",
                    notes="Official Wyoming Judicial Branch Pinedale circuit page: appointed January 2023, retained November 2024."),
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
    src["general_results"] = "https://www.tetoncountywy.gov/DocumentCenter/View/42627/2026-General-Election-Official-Results-Summary"
    src["primary_results"] = "https://www.tetoncountywy.gov/DocumentCenter/View/41853/2026-Primary-Election-Official-Results-Summary"
    src["checked"] = RETRIEVED
    data["sources"] = src
    apply_to_groups(data["groups"], 'teton')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
