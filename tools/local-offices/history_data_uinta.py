"""Uinta County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H

RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT
CLERK = "https://uintacountywy.gov/26/Elections"
BASE = "https://uintacountywy.gov/DocumentCenter/View"
DISPLAY_PEARSON = "Laura Taliaferro (formerly Pearson)"

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

PG = {
    2026: (f"{BASE}/8642/2026-General-Election-Results-Unofficial",
           "Uinta County official 2026 general election summary (official Elections page and PDF header: Official Results)"),
}

def pg(year: int) -> dict:
    url, label = PG[year]
    return {"label": label, "url": url}

def sos_url(year: int) -> str:
    return f"https://sos.wyo.gov/Elections/Docs/{year}/Results/General/{year}_Uinta_County_General_PbP.pdf"

def sos(year: int) -> dict:
    return {"label": f"Wyoming Secretary of State official {year} Uinta general precinct-by-precinct summary", "url": sos_url(year)}

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
        ("WY-PEARSON-LAURA", DISPLAY_PEARSON, "Laura", "Pearson", "", "Laura Taliaferro Pearson; Laura Pearson; Laura Taliaferro"),
        ("WY-BARNARD-PAUL-R", "Paul R. Barnard", "Paul", "Barnard", "R."),
        ("WY-SCHULER-WENDY-DAVIS", "Wendy Davis Schuler", "Wendy", "Schuler", "", "Wendy Schuler"),
        ("WY-CRANK-THOMAS-D", "Thomas D. Crank", "Thomas", "Crank", "D."),
        ("WY-HEINER-SCOTT", "Scott Heiner", "Scott", "Heiner"),
        ("WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "Kenneth", "Roberts", "D."),
        ("WY-DAVISON-KATHLEEN", "Kathleen Davison", "Kathleen", "Davison"),
        ("WY-JAGGI-ALLEN-M", "Allen M. Jaggi", "Allen", "Jaggi", "M.", "Allen Jaggi"),
        ("WY-EYRE-DANNY", "Danny Eyre", "Danny", "Eyre"),
        ("WY-CONRAD-JON-R", "Jon R. Conrad", "Jon", "Conrad", "R.", "Jon R Conrad"),
        ("WY-WEBB-JOE", "Joe Webb", "Joe", "Webb"),
        ("WY-STEPHENS-CHAD", "Chad Stephens", "Chad", "Stephens"),
        ("WY-PIIPARINEN-GARRY-C", "Garry C. Piiparinen", "Garry", "Piiparinen", "C."),
        ("WY-WHARFF-ROBERT-A", "Robert A. Wharff", "Robert", "Wharff", "A.", "Robert Wharff"),
        ("WY-BERGER-RYAN-C", "Ryan C. Berger", "Ryan", "Berger", "C."),
        ("WY-WALTON-DAVID", "David Walton", "David", "Walton"),
        ("WY-ANDERSON-D-MARK", "D. Mark Anderson", "Mark", "Anderson", "", "David Mark Anderson; D Mark Anderson"),
        ("WY-CRANDALL-GREG", "Greg Crandall", "Greg", "Crandall"),
        ("WY-KALLAS-LORETTA-HOWIESON", "Loretta Howieson Kallas", "Loretta", "Kallas"),
        ("WY-KOPP-ANDY", "Andy Kopp", "Andy", "Kopp"),
        ("WY-HUTCHINSON-AMANDA", "Amanda Hutchinson", "Amanda", "Hutchinson"),
        ("WY-BRIMHALL-TERRY", "Terry Brimhall", "Terry", "Brimhall"),
        ("WY-RICHINS-ASHLEE", "Ashlee Richins", "Ashlee", "Richins"),
        ("WY-WRIGHT-KERRI", "Kerri Wright", "Kerri", "Wright"),
        ("WY-LIND-JESSE", "Jesse Lind", "Jesse", "Lind"),
        ("WY-VOSS-MIKEL", "Mikel Voss", "Mikel", "Voss"),
        ("WY-RASNAKE-JOSHUA", "Joshua Rasnake", "Joshua", "Rasnake"),
        ("WY-BERGER-RYAN", "Ryan Berger", "Ryan", "Berger"),  # Evanston council; distinct from Ryan C. Berger H49
        ("WY-WELLING-DAVID-DON", "David Don Welling", "David", "Welling"),
        ("WY-STOKES-BRIAN-J", "Brian J. Stokes", "Brian", "Stokes", "J.", "Brian J Stokes"),
        ("WY-WHITE-NICOLAS", "Nicolas White", "Nicolas", "White"),
        ("WY-BRUNSKI-DECKERT-BRITTNEY", "Brittney Brunski-Deckert", "Brittney", "Brunski-Deckert"),
        ("WY-BENTLEY-SPENCER-J", "Spencer J. Bentley", "Spencer", "Bentley", "J.", "Spencer J Bentley"),
        ("WY-DICKERSON-L-SCOTT", "L. Scott Dickerson", "Scott", "Dickerson", "", "L Scott Dickerson"),
        ("WY-HUTCHINSON-GARY", "Gary Hutchinson", "Gary", "Hutchinson"),
        ("WY-GUILD-CALEB", "Caleb Guild", "Caleb", "Guild"),
        ("WY-WELLING-JENNY", "Jenny Welling", "Jenny", "Welling"),
        ("WY-BRUCE-DAUNA-D", "Dauna D. Bruce", "Dauna", "Bruce", "D."),
        ("WY-WOODWARD-MARDI", "Mardi Woodward", "Mardi", "Woodward"),
        ("WY-LESTER-MERLE", "Merle Lester", "Merle", "Lester"),
        ("WY-MADSEN-DALE", "Dale Madsen", "Dale", "Madsen"),
        ("WY-NIELSON-TRAVIS", "Travis Nielson", "Travis", "Nielson"),
        ("WY-EYRE-SPENCER-J", "Spencer J. Eyre", "Spencer", "Eyre", "J."),
        ("WY-FACKRELL-JOHN-E", "John E. Fackrell", "John", "Fackrell", "E.", "John E Fackrell"),
        ("WY-LESTER-TY", "Ty Lester", "Ty", "Lester"),
        ("WY-GUILD-KELLY", "Kelly Guild", "Kelly", "Guild"),
        ("WY-STODDARD-WADE", "Wade Stoddard", "Wade", "Stoddard"),
        ("WY-CONDOS-KEVIN", "Kevin Condos", "Kevin", "Condos"),
        ("WY-HOOTON-SHANE", "Shane Hooton", "Shane", "Hooton"),
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
    ]
    for row in rows:
        pid, display, first, last = row[0], row[1], row[2], row[3]
        middle = row[4] if len(row) > 4 else ""
        aliases = row[5] if len(row) > 5 else ""
        slug = "laura-taliaferro-pearson" if pid == "WY-PEARSON-LAURA" else ""
        P(pid, display, first, last, middle, aliases=aliases, minted=True, slug=slug)
    import history_data_uinta_holders as UH
    UH.register_extra(P)

def _add(terms, pid, name, group, office, jur, a, b, ey, party="", notes="", sources=None, how="elected", conf="high"):
    terms.append(T(
        person_id=pid, name=name, party=party,
        office_group=group, office=office, jurisdiction=jur,
        term_start=FM[a] if not isinstance(a, str) else a,
        term_end=FM[b] if not isinstance(b, str) else b,
        how_took_office=how, election_year=ey, confidence=conf,
        sources=sources, notes=notes,
    ))

def legislature_and_county_terms():
    terms = []
    # S14 multi-county: official SOS district-wide totals, Uinta share noted. 2012 statewide senate PDF was not posted (HTTP 404).
    _add(terms, "WY-COOPER-STAN", "Stan Cooper", "state-senate", "Senate District 14 (S14)", "Uinta County",
         2013, 2017, 2012, "REP",
         "Official 2012 statewide Senate summary was not posted (HTTP 404). Official 2012 SOS Uinta general PbP totals (Uinta portion): Stan Cooper 620, John Vincent Love 108. Encoded at medium confidence from official county SOS reports; official district-wide 2012 totals were not available in a statewide Senate PDF.",
         sources=[sos(2012)], conf="medium")
    _add(terms, "WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-senate", "Senate District 14 (S14)", "Uinta County",
         2017, 2021, 2016, "REP",
         "Official 2016 SOS statewide Senate summary totals: Fred Baldwin 6,939, Anselm Sedey 1,237. Official Uinta portion: Baldwin 606, Sedey 106.",
         sources=[sos_senate(2016), sos(2016)])
    _add(terms, "WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-senate", "Senate District 14 (S14)", "Uinta County",
         2021, 2025, 2020, "REP",
         "Official 2020 SOS statewide Senate summary totals: Fred Baldwin 7,779. Official Uinta portion: 690.",
         sources=[sos_senate(2020), sos(2020)])
    _add(terms, "WY-PEARSON-LAURA", DISPLAY_PEARSON, "state-senate", "Senate District 14 (S14)", "Uinta County",
         2025, 2029, 2024, "REP",
         "Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Uinta portion: 593. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA.",
         sources=[sos_senate(2024), sos(2024)])

    # S15 is Uinta-only on official statewide summaries (Total equals the Uinta row).
    _add(terms, "WY-BARNARD-PAUL-R", "Paul R. Barnard", "state-senate", "Senate District 15 (S15)", "Uinta County",
         2015, 2019, 2014, "REP",
         "Official 2014 SOS statewide Senate summary totals: Paul R. Barnard 3,329, Bret McCoy 1,702 (Uinta-only district).",
         sources=[sos_senate(2014), sos(2014)])
    _add(terms, "WY-SCHULER-WENDY-DAVIS", "Wendy Davis Schuler", "state-senate", "Senate District 15 (S15)", "Uinta County",
         2019, 2023, 2018, "REP",
         "Official 2018 SOS statewide Senate summary totals: Wendy Davis Schuler 4,903 (Uinta-only district).",
         sources=[sos_senate(2018), sos(2018)])
    _add(terms, "WY-SCHULER-WENDY-DAVIS", "Wendy Davis Schuler", "state-senate", "Senate District 15 (S15)", "Uinta County",
         2023, 2027, 2022, "REP",
         "Official 2022 SOS statewide Senate summary totals: Wendy Davis Schuler 5,243 (Uinta-only district).",
         sources=[sos_senate(2022), sos(2022)])
    _add(terms, "WY-SCHULER-WENDY-DAVIS", "Wendy Davis Schuler", "state-senate", "Senate District 15 (S15)", "Uinta County",
         2027, 2031, 2026, "REP",
         "Official 2026 SOS statewide Senate summary totals: Wendy Davis Schuler 4,835 (Uinta-only; official 2026 Uinta clerk: Wendy Davis Schuler 4,835). Official 2022 term ends January 2027; official 2026 term begins January 2027.",
         sources=[sos_senate(2026), pg(2026)])

    # H18 multi-county official SOS district-wide totals; Uinta share noted.
    _add(terms, "WY-DAVISON-KATHLEEN", "Kathleen Davison", "state-house", "House District 18 (H18)", "Uinta County",
         2013, 2015, 2012, "REP",
         "Official 2012 statewide House summary was not posted (HTTP 404). Official 2012 SOS Uinta general PbP totals (Uinta portion): Kathleen Davison 632. Encoded at medium confidence.",
         sources=[sos(2012)], conf="medium")
    _add(terms, "WY-BALDWIN-FRED-A", "Fred A. Baldwin", "state-house", "House District 18 (H18)", "Uinta County",
         2015, 2017, 2014, "REP",
         "Official 2014 SOS statewide House summary totals: Fred A. Baldwin 2,297, Michele Irwin 719. Official Uinta portion: Baldwin 383, Irwin 105.",
         sources=[sos_house(2014), sos(2014)])
    _add(terms, "WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Uinta County",
         2017, 2019, 2016, "REP",
         "Official 2016 SOS statewide House summary totals: Thomas D. Crank 3,595, Michele Irwin 880. Official Uinta portion: Crank 575, Irwin 144.",
         sources=[sos_house(2016), sos(2016)])
    _add(terms, "WY-CRANK-THOMAS-D", "Thomas D. Crank", "state-house", "House District 18 (H18)", "Uinta County",
         2019, 2021, 2018, "REP",
         "Official 2018 SOS statewide House summary totals: Thomas D. Crank 3,088. Official Uinta portion: 491.",
         sources=[sos_house(2018), sos(2018)])
    _add(terms, "WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Uinta County",
         2021, 2023, 2020, "REP",
         "Official 2020 SOS statewide House summary totals: Scott Heiner 3,981. Official Uinta portion: 698.",
         sources=[sos_house(2020), sos(2020)])
    _add(terms, "WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Uinta County",
         2023, 2025, 2022, "REP",
         "Official 2022 SOS statewide House summary totals: Scott Heiner 2,689, Dennis B. Laughlin 590. Official Uinta portion: Heiner 429, Laughlin 63.",
         sources=[sos_house(2022), sos(2022)])
    _add(terms, "WY-HEINER-SCOTT", "Scott Heiner", "state-house", "House District 18 (H18)", "Uinta County",
         2025, 2027, 2024, "REP",
         "Official 2024 SOS statewide House summary totals: Scott Heiner 3,781. Official Uinta portion: 586.",
         sources=[sos_house(2024), sos(2024)])
    _add(terms, "WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "state-house", "House District 18 (H18)", "Uinta County",
         2027, 2029, 2026, "REP",
         "Official 2026 SOS statewide House summary totals: Kenneth D. Roberts 2,691. Official 2026 Uinta clerk portion: 400. Also covers Lincoln and Sweetwater.",
         sources=[sos_house(2026), pg(2026)])

    # H19 Uinta-only on official statewide summaries.
    _add(terms, "WY-JAGGI-ALLEN-M", "Allen Jaggi", "state-house", "House District 19 (H19)", "Uinta County",
         2015, 2017, 2014, "REP",
         "Official 2014 SOS statewide House summary totals: Allen Jaggi 1,897, Pete Roitz 806 (Uinta-only district).",
         sources=[sos_house(2014), sos(2014)])
    _add(terms, "WY-EYRE-DANNY", "Danny Eyre", "state-house", "House District 19 (H19)", "Uinta County",
         2017, 2019, 2016, "REP",
         "Official 2016 SOS statewide House summary totals: Danny Eyre 3,286, Mel McCreary 592 (Uinta-only district).",
         sources=[sos_house(2016)])
    _add(terms, "WY-EYRE-DANNY", "Danny Eyre", "state-house", "House District 19 (H19)", "Uinta County",
         2019, 2021, 2018, "REP",
         "Official 2018 SOS statewide House summary totals: Danny Eyre 2,617 (Uinta-only district).",
         sources=[sos_house(2018)])
    _add(terms, "WY-EYRE-DANNY", "Danny Eyre", "state-house", "House District 19 (H19)", "Uinta County",
         2021, 2023, 2020, "REP",
         "Official 2020 SOS statewide House summary totals: Danny Eyre 3,915 (Uinta-only district).",
         sources=[sos_house(2020)])
    _add(terms, "WY-CONRAD-JON-R", "Jon R. Conrad", "state-house", "House District 19 (H19)", "Uinta County",
         2023, 2025, 2022, "REP",
         "Official 2022 SOS statewide House summary totals: Jon R. Conrad 1,748, Sarah Butters 374 (Uinta-only district). The same person is an official 2026 Uinta County commissioner elect.",
         sources=[sos_house(2022)])
    _add(terms, "WY-WEBB-JOE", "Joe Webb", "state-house", "House District 19 (H19)", "Uinta County",
         2025, 2027, 2024, "REP",
         "Official 2024 SOS statewide House summary totals: Joe Webb 3,012 (Uinta-only district).",
         sources=[sos_house(2024), sos(2024)])
    _add(terms, "WY-STEPHENS-CHAD", "Chad Stephens", "state-house", "House District 19 (H19)", "Uinta County",
         2027, 2029, 2026, "REP",
         "Official 2026 SOS statewide House summary totals: Chad Stephens 2,414 (Uinta-only; official 2026 Uinta clerk: 2,414).",
         sources=[sos_house(2026), pg(2026)])

    # H49 Uinta-only.
    _add(terms, "WY-PIIPARINEN-GARRY-C", "Garry C. Piiparinen", "state-house", "House District 49 (H49)", "Uinta County",
         2015, 2017, 2014, "REP",
         "Official 2014 SOS statewide House summary totals: Garry C. Piiparinen 1,333, Clarence Vranish 724, Larissa Sneider 417 (Uinta-only district).",
         sources=[sos_house(2014), sos(2014)])
    _add(terms, "WY-PIIPARINEN-GARRY-C", "Garry C. Piiparinen", "state-house", "House District 49 (H49)", "Uinta County",
         2017, 2019, 2016, "REP",
         "Official 2016 SOS statewide House summary totals: Garry C. Piiparinen 2,747, Larissa Sneider 829 (Uinta-only district).",
         sources=[sos_house(2016)])
    _add(terms, "WY-PIIPARINEN-GARRY-C", "Garry C. Piiparinen", "state-house", "House District 49 (H49)", "Uinta County",
         2019, 2021, 2018, "REP",
         "Official 2018 SOS statewide House summary totals: Garry C. Piiparinen 2,166 (Uinta-only district).",
         sources=[sos_house(2018)])
    _add(terms, "WY-WHARFF-ROBERT-A", "Robert A. Wharff", "state-house", "House District 49 (H49)", "Uinta County",
         2021, 2023, 2020, "REP",
         "Official 2020 SOS statewide House summary totals: Robert A. Wharff 3,269 (Uinta-only district).",
         sources=[sos_house(2020)])
    _add(terms, "WY-BERGER-RYAN-C", "Ryan C. Berger", "state-house", "House District 49 (H49)", "Uinta County",
         2023, 2025, 2022, "REP",
         "Official 2022 SOS statewide House summary totals: Ryan C. Berger 2,060, Tim Beppler 858 (Uinta-only district).",
         sources=[sos_house(2022)])
    _add(terms, "WY-WHARFF-ROBERT-A", "Robert A. Wharff", "state-house", "House District 49 (H49)", "Uinta County",
         2025, 2027, 2024, "REP",
         "Official 2024 SOS statewide House summary totals: Robert Wharff 3,046 (Uinta-only district).",
         sources=[sos_house(2024), sos(2024)])
    _add(terms, "WY-WALTON-DAVID", "David Walton", "state-house", "House District 49 (H49)", "Uinta County",
         2027, 2029, 2026, "REP",
         "Official 2026 SOS statewide House summary totals: David Walton 2,262 (Uinta-only; official 2026 Uinta clerk: 2,262).",
         sources=[sos_house(2026), pg(2026)])

    # County offices: official 2026 clerk only. Official 2022/2024 clerk generals were not posted on the current official elections page; official SOS Uinta PbPs omit county offices.
    _add(terms, "WY-ANDERSON-D-MARK", "D. Mark Anderson", "county", "County Commissioner", "Uinta County",
         2027, 2031, 2026, "REP",
         "Official 2026 Uinta clerk Vote-For-2: D. Mark Anderson 3,825, Jon R. Conrad 3,779. Term begins January 2027.")
    _add(terms, "WY-CONRAD-JON-R", "Jon R. Conrad", "county", "County Commissioner", "Uinta County",
         2027, 2031, 2026, "REP",
         "Official 2026 Uinta clerk Vote-For-2. The same person is the official 2022 H19 winner.")
    for pid, name, office, n in [
        ("WY-CRANDALL-GREG", "Greg Crandall", "County Coroner", "Official 2026 Uinta clerk: Greg Crandall 3,564."),
        ("WY-KALLAS-LORETTA-HOWIESON", "Loretta Howieson Kallas", "County Attorney", "Official 2026 Uinta clerk: Loretta Howieson Kallas 4,512."),
        ("WY-KOPP-ANDY", "Andy Kopp", "County Sheriff", "Official 2026 Uinta clerk: Andy Kopp 4,995."),
        ("WY-HUTCHINSON-AMANDA", "Amanda Hutchinson", "County Clerk", "Official 2026 Uinta clerk: Amanda Hutchinson 5,378."),
        ("WY-BRIMHALL-TERRY", "Terry Brimhall", "County Treasurer", "Official 2026 Uinta clerk: Terry Brimhall 5,258."),
        ("WY-RICHINS-ASHLEE", "Ashlee Richins", "County Assessor", "Official 2026 Uinta clerk: Ashlee Richins 5,163."),
        ("WY-WRIGHT-KERRI", "Kerri Wright", "Clerk of District Court", "Official 2026 Uinta clerk: Kerri Wright 5,187."),
    ]:
        _add(terms, pid, name, "county", office, "Uinta County", 2027, 2031, 2026, "REP", n)
    return terms

def judicial_terms():
    # Same official 3rd JD sources and dates as Lincoln/Sweetwater. Do not copy other districts.
    terms = []
    dist = "District Judge, 3rd Judicial District"
    circ = "Circuit Judge, 3rd Judicial District"
    def jt(pid, name, office, start, end, ey, how, conf, src, notes):
        terms.append(T(person_id=pid, name=name, party="", office_group="judicial", office=office,
                       jurisdiction="3rd Judicial District", term_start=start if isinstance(start, str) else FM[start],
                       term_end=FM[end], how_took_office=how, election_year=ey, confidence=conf, sources=src, notes=notes))
    jt("WY-JAMES-NENA", "Nena James", dist, 2015, 2021, 2014, "retained", "high", [sos(2014)],
       "Official 2014 SOS Uinta general PbP retention, 3rd Judicial District. Full name from official SOS.")
    jt("WY-LAVERY-RICHARD-L", "Richard L. Lavery", dist, 2015, 2021, 2014, "retained", "high", [sos(2014)],
       "Official 2014 SOS Uinta general PbP retention.")
    jt("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", dist, "2015-01-01", 2023, None, "appointed", "medium", [courts("lincoln-d")],
       "Official Wyoming Judicial Branch Lincoln 3rd JD district page: appointed January 2015 (day unstated; term_start 2015-01-01, medium), retained November 2022, term expires January 2029.")
    jt("WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", dist, 2023, 2029, 2022, "retained", "high", [courts("lincoln-d"), sos(2022)],
       "Official 2022 retention; official Lincoln 3rd JD district page term expires January 2029.")
    jt("WY-KASTE-JAMES-C", "James C. Kaste", dist, "2022-10-01", 2031, 2024, "appointed", "medium", [courts("uinta-d"), sos(2024)],
       "Official Wyoming Judicial Branch Uinta 3rd JD district page: appointed October 2022 (day unstated; term_start 2022-10-01, medium), retained November 2024, term expires January 2031.")
    jt("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", dist, "2019-10-01", 2027, 2020, "appointed", "medium", [courts("sweetwater-d"), sos(2020)],
       "Official Wyoming Judicial Branch Sweetwater 3rd JD district page: appointed October 2019 (day unstated; term_start 2019-10-01, medium), retained November 2020, term expires January 2027.")
    jt("WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", dist, 2027, 2031, 2026, "retained", "high", [pg(2026), courts("sweetwater-d")],
       "Official 2026 Uinta clerk: FOR JUDGE C OF THE DISTRICT COURT SUZANNAH G. ROBINSON, YES, continuing January 2027–2031.")
    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, 2015, 2019, 2014, "retained", "high", [sos(2014)], "Official 2014 SOS Uinta general PbP: retained Craig L. Jones.")
    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, 2019, 2023, 2018, "retained", "high", [sos(2018)], "Official 2018 SOS Uinta general PbP retention.")
    jt("WY-JONES-CRAIG-L", "Craig L. Jones", circ, 2023, 2027, 2022, "retained", "high", [sos(2022)], "Official 2022 SOS Uinta general PbP retention.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, 2015, 2019, 2014, "retained", "high", [sos(2014), courts("rs-c")], "Official 2014 SOS Uinta general PbP: retained John R. Prokos.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, 2019, 2023, 2018, "retained", "high", [sos(2018)], "Official 2018 SOS Uinta general PbP retention.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, 2023, 2027, 2022, "retained", "high", [sos(2022)], "Official 2022 SOS Uinta general PbP retention.")
    jt("WY-PROKOS-JOHN-R", "John R. Prokos", circ, 2027, 2031, 2026, "retained", "high", [pg(2026), courts("rs-c")],
       "Official 2026 Uinta clerk: FOR THIRD JUDICIAL DISTRICT, CIRCUIT COURT JUDGE JOHN R. PROKOS, YES, continuing January 2027–2031.")
    jt("WY-ZEBRE-FRANK-J", "Frank J. Zebre", circ, 2015, 2019, 2014, "retained", "high", [sos(2014)], "Official 2014 SOS Uinta general PbP: retained Frank J. Zebre.")
    jt("WY-GREER-MICHAEL-L", "Michael L. Greer", circ, 2025, 2029, 2024, "retained", "high", [sos(2024)], "Official 2024 SOS Uinta general PbP retention, 3rd JD circuit.")
    jt("WY-CORPENING-GREGORY-S", "Gregory S. Corpening", circ, 2025, 2029, 2024, "retained", "high", [sos(2024)], "Official 2024 SOS Uinta general PbP retention, 3rd JD circuit.")
    return terms

def local_terms():
    terms = []
    # Official 2026 clerk only for municipal/school/special. Mayors of Evanston and Lyman appear on the official 2026 November ballot (elected, not council-selected). Mountain View and Bear River mayors were not on the official 2026 general; official 2022/2024 clerk generals were not on the current official elections page, so those mayor rows are Not yet collected rather than invented.
    _add(terms, "WY-LIND-JESSE", "Jesse Lind", "municipal", "Evanston Mayor", "City of Evanston", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Jesse Lind 1,740, Joy Bell 1,292. The Evanston mayor is elected on the official November ballot, not selected by the council. Encoded as a four-year term from the official 2026 contest; official 2022/2024 clerk generals were not found on the current official elections page to confirm the cycle.")
    _add(terms, "WY-RASNAKE-JOSHUA", "Joshua Rasnake", "municipal", "Evanston City Council Ward 1", "City of Evanston", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-1: Joshua Rasnake 588, Mikal D. Welling 411.")
    _add(terms, "WY-BERGER-RYAN", "Ryan Berger", "municipal", "Evanston City Council Ward 2", "City of Evanston", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-1: Ryan Berger 720, Matt Windley 438. Distinct from Ryan C. Berger (official 2022 H49).")
    _add(terms, "WY-WELLING-DAVID-DON", "David Don Welling", "municipal", "Evanston City Council Ward 3", "City of Evanston", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-1: David Don Welling 358, Sarah Lambert 284.")
    _add(terms, "WY-VOSS-MIKEL", "Mikel Voss", "municipal", "Lyman Mayor", "Town of Lyman", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Mikel Voss 437, Jack Bluemel 119. The Lyman mayor is elected on the official November ballot.")
    _add(terms, "WY-DICKERSON-L-SCOTT", "L. Scott Dickerson", "municipal", "Lyman Town Council", "Town of Lyman", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-2: L. Scott Dickerson 402, Gary Hutchinson 305, over Seth Hamblin 273.")
    _add(terms, "WY-HUTCHINSON-GARY", "Gary Hutchinson", "municipal", "Lyman Town Council", "Town of Lyman", 2027, 2031, 2026, "")
    _add(terms, "WY-STOKES-BRIAN-J", "Brian J. Stokes", "municipal", "Bear River Town Council", "Town of Bear River", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-2: Brian J. Stokes 123, Nicolas White 104. No Bear River mayor contest was on the official 2026 general.")
    _add(terms, "WY-WHITE-NICOLAS", "Nicolas White", "municipal", "Bear River Town Council", "Town of Bear River", 2027, 2031, 2026, "")
    _add(terms, "WY-BRUNSKI-DECKERT-BRITTNEY", "Brittney Brunski-Deckert", "municipal", "Mountain View Town Council", "Town of Mountain View", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-2: Brittney Brunski-Deckert 295, Spencer J. Bentley 285. No Mountain View mayor contest was on the official 2026 general.")
    _add(terms, "WY-BENTLEY-SPENCER-J", "Spencer J. Bentley", "municipal", "Mountain View Town Council", "Town of Mountain View", 2027, 2031, 2026, "")

    for pid, name in [
        ("WY-GUILD-CALEB", "Caleb Guild"), ("WY-WELLING-JENNY", "Jenny Welling"), ("WY-BRUCE-DAUNA-D", "Dauna D. Bruce"),
        ("WY-WOODWARD-MARDI", "Mardi Woodward"), ("WY-LESTER-MERLE", "Merle Lester"),
    ]:
        _add(terms, pid, name, "schools", "UCSD #1 Trustee", "Uinta County School District #1", 2027, 2031, 2026, "",
             "Official 2026 Uinta clerk Vote-For-5: Caleb Guild 1,862, Jenny Welling 1,825, Dauna D. Bruce 1,790, Mardi Woodward 1,753, Merle Lester 1,581, over Janice Davis 1,481.")
    _add(terms, "WY-MADSEN-DALE", "Dale Madsen", "schools", "UCSD #4 Trustee", "Uinta County School District #4", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-2: Dale Madsen 863, Travis Nielson 836.")
    _add(terms, "WY-NIELSON-TRAVIS", "Travis Nielson", "schools", "UCSD #4 Trustee", "Uinta County School District #4", 2027, 2031, 2026, "")
    _add(terms, "WY-EYRE-SPENCER-J", "Spencer J. Eyre", "schools", "UCSD #6 Trustee", "Uinta County School District #6", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk Vote-For-2: Spencer J. Eyre 586, John E. Fackrell 472.")
    _add(terms, "WY-FACKRELL-JOHN-E", "John E. Fackrell", "schools", "UCSD #6 Trustee", "Uinta County School District #6", 2027, 2031, 2026, "")

    _add(terms, "WY-LESTER-TY", "Ty Lester", "special-districts", "Uinta Conservation District Rural Supervisor", "Uinta Conservation District", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Ty Lester 4,772 (one of two official rural supervisor contests).")
    _add(terms, "WY-GUILD-KELLY", "Kelly Guild", "special-districts", "Uinta Conservation District Rural Supervisor", "Uinta Conservation District", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Kelly Guild 4,894 (one of two official rural supervisor contests).")
    _add(terms, "WY-STODDARD-WADE", "Wade Stoddard", "special-districts", "Uinta Conservation District Urban Supervisor", "Uinta Conservation District", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Wade Stoddard 4,719.")
    _add(terms, "WY-CONDOS-KEVIN", "Kevin Condos", "special-districts", "Uinta Conservation District At-Large Supervisor", "Uinta Conservation District", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Kevin Condos 4,626.")
    _add(terms, "WY-HOOTON-SHANE", "Shane Hooton", "special-districts", "Uinta County Rural Fire District Director", "Uinta County Rural Fire District", 2027, 2031, 2026, "",
         "Official 2026 Uinta clerk: Shane Hooton 1,463.")
    import history_data_uinta_holders as UH
    UH.add_holder_terms(terms)
    return terms

def _holder(people, pid, name=None, party="", term_end="", notes="", href=None, role=""):
    p = people.get(pid) or {}
    h = {"name": name or p.get("display_name") or pid, "person_id": pid, "party": party,
         "term_end": term_end, "sources": [], "confidence": "high", "notes": notes}
    if href is None and p.get("slug"):
        h["href"] = f"candidates/local-history/c/{p['slug']}.html"
    elif href:
        h["href"] = href
    if role:
        h["role"] = role
    return h


def build_uinta():
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
    H.attach_people_from_terms(terms, people)
    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1), ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 14 (S14)", 1), ("Senate District 15 (S15)", 1)],
        "state-house": [("House District 18 (H18)", 1), ("House District 19 (H19)", 1), ("House District 49 (H49)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1), ("County Assessor", 1),
                   ("County Sheriff", 1), ("County Attorney", 1), ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [("Evanston Mayor", 1), ("Lyman Mayor", 1), ("Mountain View Mayor", 1), ("Bear River Mayor", 1)],
    }
    import history_data_uinta_holders as UH
    expected = UH.expand_expected(expected)
    judicial_note = (
        "Supreme Court justices and the Chancery Court judge are the people in office this January, from official "
        "Wyoming Judicial Branch dates and official retention results (shared with other counties). Local rows are "
        "3rd Judicial District judges (Lincoln, Sweetwater, and Uinta). Full names are taken from official SOS lines "
        "or official Wyoming Judicial Branch 3rd JD pages, and those sources are cited. Judges of other districts are not copied here."
    )
    special_note = (
        "Municipal, school, special-district, and county names for terms beginning January 2027 are keyed from the official "
        "Uinta clerk 2026 general summary (DocumentCenter slug still says Unofficial; the official Elections page and the PDF "
        "header label Official Results, dated 11/05/2026 12:58PM). Official 2022 and 2024 Uinta clerk general summaries were "
        "not posted on the current official elections page (https://uintacountywy.gov/26/Elections), and official SOS Uinta "
        "precinct-by-precinct summaries omit county, municipal, and school offices, so earlier January local rows are Not yet "
        "collected rather than invented. Evanston and Lyman mayors appear on the official 2026 November ballot and are not "
        "council-selected. Mountain View and Bear River mayors were not on the official 2026 general. Official mid-term vacancies are not invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. The current (November 2026) precinct roster "
        "is in data/county_officials/uinta.json, from the official 2026 primary (named winners only; 9 precincts / 53 holders)."
    )
    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Uinta", county_number=19, slug="uinta", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Uinta", slug="uinta")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/SC-chancery terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all

def update_uinta_json(people: dict):
    path = ROOT / "data" / "county_officials" / "uinta.json"
    data = json.loads(path.read_text())
    data["as_of"] = RETRIEVED
    data["term_switch_date"] = "2027-01-04"
    data["county_number"] = 19
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
    local_gap = ("Official 2022 and 2024 Uinta clerk general summaries were not posted on the current official elections page, "
                 "so officers whose terms end January 2027 are Not yet collected rather than invented. Official 2026 general winners take office January 2027.")
    senate = [
        office("Senate District 14 (S14)", [
            _holder(people, "WY-PEARSON-LAURA", DISPLAY_PEARSON, "REP", "January 2029",
                    notes="Official 2024 winner. Also covers Lincoln, Sublette, and Sweetwater. Official SOS district-wide totals are used for this multi-county seat."),
        ], note="Official 2024 SOS statewide Senate summary totals: Laura Taliaferro Pearson 8,025 (official ballot name). Official Uinta portion: 593. Also covers Lincoln, Sublette, and Sweetwater. Display name follows the site rule: Laura Taliaferro (formerly Pearson), person ID WY-PEARSON-LAURA."),
        office("Senate District 15 (S15)", [
            _holder(people, "WY-SCHULER-WENDY-DAVIS", "Wendy Davis Schuler", "REP", "January 2031",
                    notes="Official 2022 winner, continuing; official 2026 general winner, term begins January 2027. Uinta-only on official SOS statewide summaries."),
        ]),
    ]
    house_offices = [
        office("House District 18 (H18)", [
            _holder(people, "WY-HEINER-SCOTT", "Scott Heiner", "REP", "January 2027"),
            _holder(people, "WY-ROBERTS-KENNETH-D", "Kenneth D. Roberts", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official 2026 SOS district-wide totals: Roberts 2,691. Official 2026 Uinta clerk portion: 400."),
        ], note="Kenneth D. Roberts is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Roberts 2,691. Official Uinta portion: 400. Also covers Lincoln and Sweetwater. Official SOS district-wide totals are used for this multi-county seat."),
        office("House District 19 (H19)", [
            _holder(people, "WY-WEBB-JOE", "Joe Webb", "REP", "January 2027"),
            _holder(people, "WY-STEPHENS-CHAD", "Chad Stephens", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official 2026 SOS totals: 2,414 (Uinta-only)."),
        ], note="Chad Stephens is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Stephens 2,414 (Uinta-only district)."),
        office("House District 49 (H49)", [
            _holder(people, "WY-WHARFF-ROBERT-A", "Robert A. Wharff", "REP", "January 2027"),
            _holder(people, "WY-WALTON-DAVID", "David Walton", "REP", "January 2029",
                    notes="Takes office January 2027. Official 2026 general winner. Official 2026 SOS totals: 2,262 (Uinta-only)."),
        ], note="David Walton is the official 2026 general winner and takes office January 2027. Official 2026 SOS statewide House summary totals: Walton 2,262 (Uinta-only district)."),
    ]
    county = [
        office("County Commissioner", [
            _holder(people, "WY-ANDERSON-D-MARK", "D. Mark Anderson", "REP", "January 2031",
                    role="Chairman",
                    notes="Official current chairman (official commission page: Mark Anderson, term listed January 2027). Official 2022 general Vote-For-2 winner (David Mark Anderson 4,536). Official 2026 general Vote-For-2 winner, continues January 2027–2031."),
            _holder(people, "WY-SOUTH-ERIC", "Eric South", "REP", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner (Eric South 4,215). Official commission page term end January 2027."),
            _holder(people, "WY-HATCH-BRENT", "Brent Hatch", "REP", "January 2029",
                    notes="Official commission page term end January 2029. Official 2024 clerk general summary was not collected; term date is from the official current members table."),
            _holder(people, "WY-CONRAD-JON-R", "Jon R. Conrad", "REP", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 winner."),
        ], note="Commissioners and row officers through January 2027 are from the official 2022 Uinta clerk general (DocumentCenter/View/7940, OFFICIAL RESULTS, 11/10/2022 1:19 PM) and official county elected-official pages. Official 2024 clerk general results were not found on the current official elections page or in a Wayback capture of the 2024 results file (DocumentCenter 8642 later holds the official 2026 general)."),
        office("County Clerk", [_holder(people, "WY-HUTCHINSON-AMANDA", "Amanda Hutchinson", "REP", "January 2031",
                    notes="Official 2022 general winner (5,848). Official current clerk. Official 2026 general winner, continues January 2027–2031.")]),
        office("County Treasurer", [_holder(people, "WY-BRIMHALL-TERRY", "Terry Brimhall", "REP", "January 2031",
                    notes="Official 2022 general winner (5,795). Official current treasurer. Official 2026 general winner, continues January 2027–2031.")]),
        office("County Assessor", [_holder(people, "WY-RICHINS-ASHLEE", "Ashlee Richins", "REP", "January 2031",
                    notes="Official current assessor (official Assessor page and official List of All Elected Officials, term expires 2027). Mid-term successor to official 2022 winner Lori S. Perkins (5,640). Official 2026 general winner, continues January 2027–2031. The official appointment date was not in the official minutes collected here.")]),
        office("County Sheriff", [_holder(people, "WY-KOPP-ANDY", "Andy Kopp", "REP", "January 2031",
                    notes="Official 2022 general winner (Andy Kopp 3,922, Rowdy Dean 2,652). Official current sheriff. Official 2026 general winner, continues January 2027–2031.")]),
        office("County Attorney", [_holder(people, "WY-KALLAS-LORETTA-HOWIESON", "Loretta Howieson Kallas", "REP", "January 2031",
                    notes="Official 2022 general winner (5,015). Official current attorney (official list: Loretta Kallas). Official 2026 general winner, continues January 2027–2031.")]),
        office("Clerk of District Court", [_holder(people, "WY-WRIGHT-KERRI", "Kerri Wright", "REP", "January 2031",
                    notes="Official 2022 general winner (5,728). Official current clerk of district court. Official 2026 general winner, continues January 2027–2031.")]),
        office("County Coroner", [_holder(people, "WY-CRANDALL-GREG", "Greg Crandall", "REP", "January 2031",
                    notes="Official 2022 general winner (5,925). Official current coroner. Official 2026 general winner, continues January 2027–2031.")]),
    ]
    municipal = [
        office("Evanston Mayor", [
            _holder(people, "WY-WILLIAMS-KENT", "Kent Williams", "", "January 2027",
                    notes="Official 2022 general winner (Kent Williams 1,711, Tim Lynch 1,449). Official City of Evanston Government page lists Mayor Kent Williams."),
            _holder(people, "WY-LIND-JESSE", "Jesse Lind", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner (Jesse Lind 1,740, Joy Bell 1,292). Currently official Ward II council member."),
        ], note="The Evanston mayor is elected on the official November ballot."),
        office("Evanston City Council Ward 1", [
            _holder(people, "WY-HEGEMAN-JENNIE", "Jennie Hegeman", "", "January 2027",
                    notes="Official 2022 general winner (Jen Hegeman 475, Mikal D Welling 452). Official city directory: Jennie Hegeman."),
            _holder(people, "WY-SCHMIDT-HENRY", "Henry Schmidt", "", "January 2029",
                    notes="Official City of Evanston Government page and official directory, Ward I. Official 2024 clerk general results were not collected."),
            _holder(people, "WY-RASNAKE-JOSHUA", "Joshua Rasnake", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Evanston City Council Ward 2", [
            _holder(people, "WY-LIND-JESSE", "Jesse Lind", "", "January 2027",
                    notes="Official 2022 general winner (Jesse Lind 699, Tib Ottley 555). Official city directory, Ward II. Official 2026 mayor elect."),
            _holder(people, "WY-SELLERS-MIKE", "Mike Sellers", "", "January 2029",
                    notes="Official City of Evanston Government page and official directory, Ward II. Official 2024 clerk general results were not collected."),
            _holder(people, "WY-BERGER-RYAN", "Ryan Berger", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner."),
        ]),
        office("Evanston City Council Ward 3", [
            _holder(people, "WY-WELLING-DAVID-DON", "David Don Welling", "", "January 2031",
                    notes="Official 2022 general winner (David Don Welling 621). Official city directory: David Welling. Official 2026 Ward 3 winner, continues January 2027–2031."),
            _holder(people, "WY-PERKES-EVAN", "Evan Perkes", "", "January 2029",
                    notes="Official City of Evanston Government page and official directory, Ward III. Official 2024 clerk general results were not collected."),
        ]),
        office("Lyman Mayor", [
            _holder(people, "WY-HOOTON-SHANE", "Shane Hooton", "", "January 2027",
                    notes="Official 2022 general winner (Shane Hooton 392, Allen Wyatt 287). Official Town of Lyman page: term expires Dec 31, 2026."),
            _holder(people, "WY-VOSS-MIKEL", "Mikel Voss", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner (Mikel Voss 437, Jack Bluemel 119)."),
        ], note="The Lyman mayor is elected on the official November ballot."),
        office("Lyman Town Council", [
            _holder(people, "WY-BERG-BRONSON", "Bronson Berg", "", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner (Bronson Berg 376, Gregg Moretti 373). Official town page term expires Dec 31, 2026."),
            _holder(people, "WY-MORETTI-GREGG", "Gregg Moretti", "", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner. Official town page term expires Dec 31, 2026."),
            _holder(people, "WY-BRAMLETT-JAMES", "James Bramlett", "", "January 2029",
                    notes="Official Town of Lyman Mayor and Council page: term expires Dec 31, 2028. Official 2024 clerk general results were not collected."),
            _holder(people, "WY-WILBUR-DANIELLE", "Danielle Wilbur", "", "January 2029",
                    notes="Official Town of Lyman Mayor and Council page: term expires Dec 31, 2028. Official 2024 clerk general results were not collected."),
            _holder(people, "WY-DICKERSON-L-SCOTT", "L. Scott Dickerson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 winner."),
            _holder(people, "WY-HUTCHINSON-GARY", "Gary Hutchinson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 winner."),
        ]),
        office("Mountain View Mayor", [
            _holder(people, "WY-AYRES-BRYAN", "Bryan Ayres", "", "January 2029",
                    notes="Official Town of Mountain View staff directory and official Uinta County Mountain View page list Mayor Bryan Ayres. No mayor contest was on the official 2022 or 2026 clerk generals. Official 2024 clerk results were not collected."),
        ]),
        office("Mountain View Town Council", [
            _holder(people, "WY-FERRIN-JAMY-D", "Jamy D. Ferrin", "", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner (Jamy D. Ferrin 260). Official directory lists Jamy Ferrin, Council President."),
            _holder(people, "WY-BRUNSKI-DECKERT-BRITTNEY", "Brittney Brunski-Deckert", "", "January 2031",
                    notes="Official Town of Mountain View staff directory. Official 2026 general Vote-For-2 winner, continues January 2027–2031. Official 2024 clerk results were not collected."),
            _holder(people, "WY-CARTER-TORI", "Tori Carter", "", "January 2029",
                    notes="Official Town of Mountain View staff directory. Official 2024 clerk results were not collected."),
            _holder(people, "WY-TIMS-MICHAEL", "Michael Tims", "", "January 2029",
                    notes="Official Town of Mountain View staff directory. Official 2024 clerk results were not collected."),
            _holder(people, "WY-BENTLEY-SPENCER-J", "Spencer J. Bentley", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 winner."),
        ]),
        office("Bear River Mayor", [
            _holder(people, "WY-KOFOED-CLYDE", "Clyde Kofoed", "", "January 2029",
                    notes="Official Uinta County Bear River page lists Mayor Clyde Kofoed. No mayor contest was on the official 2022 or 2026 clerk generals. Official 2024 clerk results were not collected. Official 2022 general: Clyde Kofoed was a Bear River council winner."),
        ]),
        office("Bear River Town Council", [
            _holder(people, "WY-STOKES-BRIAN-J", "Brian J. Stokes", "", "January 2031",
                    notes="Official 2022 general Vote-For-2 winner (BJ Stokes 111). Official 2026 general Vote-For-2 winner, continues January 2027–2031."),
            _holder(people, "WY-WHITE-NICOLAS", "Nicolas White", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general Vote-For-2 winner. Not named as a current council member in an official town council list collected here."),
        ], note="Official 2022 general also elected Clyde Kofoed to the council (98 votes). Other current council seats besides Stokes are Not yet collected from an official town council roster; the official town home page does not list the council."),
    ]
    schools = [
        office("UCSD #1 Trustee", [
            _holder(people, "WY-WELLING-JENNY", "Jenny Welling", "", "January 2031",
                    notes="Official 2022 general Vote-For-5 winner (2,059). Official current board list. Official 2026 Vote-For-5 winner, continues January 2027–2031."),
            _holder(people, "WY-BENNETT-DAVID", "David Bennett", "", "January 2027",
                    notes="Official 2022 general Vote-For-5 winner (1,911). Official current board list."),
            _holder(people, "WY-GUILD-CALEB", "Caleb Guild", "", "January 2031",
                    notes="Official 2022 general Vote-For-5 winner (1,887). Official current board list. Official 2026 Vote-For-5 winner, continues January 2027–2031."),
            _holder(people, "WY-DAVIS-JANICE", "Janice Davis", "", "January 2027",
                    notes="Official 2022 general Vote-For-5 winner (1,619). Official current board list."),
            _holder(people, "WY-PETERSON-DAVID", "David Peterson", "", "January 2029",
                    notes="Official UCSD #1 School Board page lists David Peterson, Chairman. Official 2024 clerk results were not collected.", role="Chairman"),
            _holder(people, "WY-ARCH-JESSICA", "Jessica Arch", "", "January 2029",
                    notes="Official UCSD #1 School Board page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-WHEELER-DAN", "Dan Wheeler", "", "January 2029",
                    notes="Official UCSD #1 School Board page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-WOODWARD-BRIAN", "Brian Woodward", "", "January 2029",
                    notes="Official UCSD #1 School Board page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-DUBOIS-JOHN", "John DuBois", "", "January 2029",
                    notes="Official UCSD #1 School Board page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-BRUCE-DAUNA-D", "Dauna D. Bruce", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Vote-For-5 winner."),
            _holder(people, "WY-WOODWARD-MARDI", "Mardi Woodward", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Vote-For-5 winner."),
            _holder(people, "WY-LESTER-MERLE", "Merle Lester", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Vote-For-5 winner."),
        ], note="Official 2022 general Vote-For-5 winners included Jesse Lind (1,715), who is not on the official UCSD #1 School Board staff list retrieved 2026-11-24 and is omitted from the live roster. Official 2024 clerk general results were not collected; 2024-class names are from the official current board page."),
        office("UCSD #4 Trustee", [
            _holder(people, "WY-CARPENTER-KELLY-Q", "Kelly Q. Carpenter", "", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner (Kelly Q Carpenter 992, Dale Madsen 904)."),
            _holder(people, "WY-MADSEN-DALE", "Dale Madsen", "", "January 2031",
                    notes="Official 2022 general Vote-For-2 winner (904). Official 2026 Vote-For-2 winner, continues January 2027–2031."),
            _holder(people, "WY-RUDY-AARON", "Aaron Rudy", "", "January 2029",
                    notes="Official UCSD #4 FY2027 budget hearing notice (June 30, 2026) attested by Aaron Rudy, Chairman. Official 2024 clerk results were not collected.", role="Chairman"),
            _holder(people, "WY-TIMS-BRIAN", "Brian Tims", "", "January 2029",
                    notes="Official UCSD #4 FY2027 budget hearing notice (June 30, 2026) attested by Brian Tims, Clerk. Official 2024 clerk results were not collected."),
            _holder(people, "WY-NIELSON-TRAVIS", "Travis Nielson", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Vote-For-2 winner."),
        ], note="A fifth current UCSD #4 trustee was not named in the official sources collected here and is Not yet collected. Official 2024 clerk general results were not collected."),
        office("UCSD #6 Trustee", [
            _holder(people, "WY-EYRE-SPENCER-J", "Spencer J. Eyre", "", "January 2031",
                    notes="Official 2022 general Vote-For-2 winner (696). Official current board list. Official 2026 Vote-For-2 winner, continues January 2027–2031."),
            _holder(people, "WY-LAMBERTI-JASON", "Jason Lamberti", "", "January 2027",
                    notes="Official 2022 general Vote-For-2 winner (473). Official current board list."),
            _holder(people, "WY-HEATON-NATHAN", "Nathan Heaton", "", "January 2029",
                    notes="Official UCSD #6 School Board Information page lists Nathan Heaton, Chairman. Official 2024 clerk results were not collected.", role="Chairman"),
            _holder(people, "WY-DUNN-SUE", "Sue Dunn", "", "January 2029",
                    notes="Official UCSD #6 School Board Information page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-BLUEMEL-CHRISTI", "Christi Bluemel", "", "January 2029",
                    notes="Official UCSD #6 School Board Information page. Official 2024 clerk results were not collected."),
            _holder(people, "WY-FACKRELL-JOHN-E", "John E. Fackrell", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 Vote-For-2 winner."),
        ]),
    ]
    special = [
        office("Uinta Conservation District Rural Supervisor", [
            _holder(people, "WY-GUILD-KELLY", "Kelly Guild", "", "January 2031",
                    notes="Official 2022 general rural winner (5,482). Official CD January 2026 newsletter: Chairman. Official 2026 rural winner, continues January 2027–2031.", role="Chairman"),
            _holder(people, "WY-EYRE-SPENCER-J", "Spencer J. Eyre", "", "January 2029",
                    notes="Official CD January 2026 newsletter: Vice Chairman. Official county special-district boards page: Spencer J. Eyre (rural), term expiration 2028. Official 2024 clerk results were not collected.", role="Vice Chairman"),
            _holder(people, "WY-LESTER-TY", "Ty Lester", "", "January 2031",
                    notes="Official 2022 general urban winner (5,222); official 2026 clerk lists a Rural Vote-For-1 win and the official CD January 2026 newsletter lists Ty Lester, Secretary/Treasurer. Continues January 2027–2031.", role="Secretary/Treasurer"),
        ]),
        office("Uinta Conservation District Urban Supervisor", [
            _holder(people, "WY-STODDARD-WADE", "Wade Stoddard", "", "January 2031",
                    notes="Official CD January 2026 newsletter lists Wade Stoddard as a current supervisor. Official 2026 urban winner, continues January 2027–2031."),
        ]),
        office("Uinta Conservation District At-Large Supervisor", [
            _holder(people, "WY-CONDOS-KEVIN", "Kevin Condos", "", "January 2031",
                    notes="Official 2022 general at-large winner (5,167). Official CD January 2026 newsletter. Official 2026 at-large winner, continues January 2027–2031."),
        ]),
        office("Uinta County Rural Fire District Director", [
            _holder(people, "WY-STONE-DANA", "Dana Stone", "", "January 2027",
                    notes="Official 2022 general winner (1,721). Official county special-district boards page: Dana Stone, term expiration 2026."),
            _holder(people, "WY-LUNSFORD-DAN", "Dan Lunsford", "", "January 2029",
                    notes="Official county special-district boards page: Dan Lunsford, term expiration 2028. Official 2024 clerk results were not collected."),
            _holder(people, "WY-WELLING-CRAIG-B", "Craig B. Welling", "", "January 2029",
                    notes="Official county special-district boards page: Craig B. Welling, term expiration 2028. Official 2024 clerk results were not collected."),
            _holder(people, "WY-HOOTON-SHANE", "Shane Hooton", "", "January 2031",
                    notes="Takes office January 2027. Official 2026 general winner (1,463). Official Town of Lyman page also lists Shane Hooton as mayor through Dec 31, 2026."),
        ]),
    ]
    judicial = [

        office("District Judge, 3rd Judicial District", [
            _holder(people, "WY-BLUEMEL-JOSEPH-B", "Joseph B. Bluemel", "", "January 2029",
                    notes="Official Wyoming Judicial Branch Lincoln 3rd JD district page: appointed January 2015, retained November 2022, term expires January 2029."),
            _holder(people, "WY-KASTE-JAMES-C", "James C. Kaste", "", "January 2031",
                    notes="Official Wyoming Judicial Branch Uinta 3rd JD district page: appointed October 2022, retained November 2024, term expires January 2031."),
            _holder(people, "WY-ROBINSON-SUZANNAH-G", "Suzannah G. Robinson", "", "January 2031",
                    notes="Official 2026 Uinta clerk SUZANNAH G. ROBINSON, YES, continuing January 2027–2031."),
        ]),
        office("Circuit Judge, 3rd Judicial District", [
            _holder(people, "WY-JONES-CRAIG-L", "Craig L. Jones", "", "January 2027"),
            _holder(people, "WY-PROKOS-JOHN-R", "John R. Prokos", "", "January 2031",
                    notes="Official 2026 Uinta clerk JOHN R. PROKOS, YES, continuing January 2027–2031."),
            _holder(people, "WY-GREER-MICHAEL-L", "Michael L. Greer", "", "January 2029"),
            _holder(people, "WY-CORPENING-GREGORY-S", "Gregory S. Corpening", "", "January 2029"),
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
        by_name = {}
        for g in groups:
            for o in g.get("offices") or []:
                for h in o.get("holders") or []:
                    pid = h.get("person_id") or ""
                    nm = (h.get("name") or "").strip()
                    if pid and nm:
                        by_name.setdefault(nm, pid)
        for prec in precincts.get("precincts") or []:
            for o in prec.get("offices") or []:
                for h in o.get("holders") or []:
                    nm = (h.get("name") or "").strip()
                    if h.get("person_id") or nm not in by_name:
                        continue
                    h["person_id"] = by_name[nm]
                    slug = (people.get(by_name[nm]) or {}).get("slug")
                    if slug and not h.get("href"):
                        h["href"] = f"candidates/local-history/c/{slug}.html"
        groups.append(precincts)
    data["groups"] = groups
    src = data.get("sources") or {}
    src["general_results"] = f"{BASE}/8642/2026-General-Election-Results-Unofficial"
    src["primary_results"] = f"{BASE}/8645/2026-Primary-Results-UNOFFICIAL"
    src["checked"] = RETRIEVED
    data["sources"] = src
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
