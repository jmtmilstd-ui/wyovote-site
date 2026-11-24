#!/usr/bin/env python3
"""Johnson County officeholder history (preview). Official clerk, SOS, court,
and town sources only. Names are never invented.
"""
from __future__ import annotations

import json
from copy import deepcopy

import history_lib as H
from history_lib import FM, ROOT, src_dict, term

RETRIEVED = "2026-11-24"
CN = 16
SLUG = "johnson"

URL_COUNTY = "https://www.johnsoncowy.gov/"
URL_COMM = "https://www.johnsoncowy.gov/departments/commission-members"
URL_CLERK = "https://www.johnsoncowy.gov/departments/clerk"
URL_ELECTIONS = "https://www.johnsoncowy.gov/departments/elections"
URL_ASSESSOR = "https://www.johnsoncowy.gov/departments/assessor"
URL_TREASURER = "https://www.johnsoncowy.gov/departments/treasurer"
URL_SHERIFF = "https://www.johnsoncowy.gov/departments/sheriff"
URL_ATTORNEY = "https://www.johnsoncowy.gov/departments/attorney"
URL_CDC = "https://www.johnsoncowy.gov/departments/clerk-of-district-court"
URL_CORONER = "https://www.johnsoncowy.gov/departments/coroner"
URL_BUFFALO = "https://www.cityofbuffalowy.com/"
URL_BUF_MAYOR = "https://www.cityofbuffalowy.com/pview.aspx?id=24176&catid=509"
URL_BUF_COUNCIL = "https://www.cityofbuffalowy.com/pview.aspx?id=24173&catid=509"


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


SRC_COMM = S("Official Johnson County Commissioners page, retrieved 2026-11-24", URL_COMM)
SRC_CLERK = S("Official Johnson County Clerk page, retrieved 2026-11-24", URL_CLERK)
SRC_ELEC = S("Official Johnson County Clerk Elections page, retrieved 2026-11-24", URL_ELECTIONS)
SRC_ASSESSOR = S("Official Johnson County Assessor page, retrieved 2026-11-24", URL_ASSESSOR)
SRC_TREAS = S("Official Johnson County Treasurer page, retrieved 2026-11-24", URL_TREASURER)
SRC_SHERIFF = S("Official Johnson County Sheriff page, retrieved 2026-11-24", URL_SHERIFF)
SRC_ATTORNEY = S("Official Johnson County Attorney page, retrieved 2026-11-24", URL_ATTORNEY)
SRC_CDC = S("Official Johnson County Clerk of District Court page, retrieved 2026-11-24", URL_CDC)
SRC_CORONER = S("Official Johnson County Coroner page, retrieved 2026-11-24", URL_CORONER)
SRC_BUF_MAYOR = S("Official City of Buffalo Mayor's Office page, retrieved 2026-11-24", URL_BUF_MAYOR)
SRC_BUF_COUNCIL = S("Official City of Buffalo City Council page, retrieved 2026-11-24", URL_BUF_COUNCIL)


SRC_COURT = S(
    "Official 4th Judicial District names and retention dating already used in the Sheridan history, plus official Johnson clerk named-retention totals where an official certified Johnson canvass is now in hand.",
    "",
)
SRC_2026_SUM = S(
    "Official Johnson County General Election Detail Report, November 3, 2026 (header OFFICIAL RESULTS; footer GENERAL ELECTION DETAIL REPORT - 11/06/2026 12:19PM; Precincts Complete 16 of 16). Official file title: Johnson County General election OFFICIAL Results.pdf, linked from the official 2026 Results Drive folder on the official elections page.",
    "https://drive.google.com/file/d/1QrzYmvHr9euYlYbndXbkDZN5RlI0lcYf/view",
)
SRC_2026_PCT = S(
    "Official Johnson County General Election Precinct Report, November 3, 2026 (header OFFICIAL RESULTS; footer JOHNSON COUNTY General Election Precinct Report - 11/05/2026 04:31PM; 16 of 16 Precincts Reporting; 30 pages).",
    "https://drive.google.com/file/d/1vfmKkmawmREEplnTg3RVOoKKXscEWj2V/view",
)
SRC_2024_SUM = S(
    "Official Johnson County General Election Summary, November 5, 2024, from the official Election Archives December 2024 folder (header typo OFFICAL RESULTS; footer Election Summary - 12/04/2024 11:05AM; Precincts Complete 16 of 16). Official file title: General Election Summary-County Official Results.pdf.",
    "https://drive.google.com/file/d/1vsM1XgYlvb_7evTdhfp4jdOYYu2aDNtk/view",
)
SRC_2022_SUM = S(
    "Official Johnson County General Election Summary, November 8, 2022 (header OFFICIAL RESULTS; footer Election Summary - 11/10/2022 11:46 AM; Precincts Complete 16 of 16). Official Election Archives file 2022-General-Election-Results.pdf.",
    "https://drive.google.com/file/d/1nRAtKeLfiHTfB-v0V6G2Rp2ffV61hE-p/view",
)
SRC_KAYCEE = S(
    "Official Town of Kaycee Town Council page, retrieved 2026-11-24",
    "https://www.kayceewyo.com/government",
)
SRC_KAYCEE_HOME = S(
    "Official Town of Kaycee website (kayceewyo.com), retrieved 2026-11-24, which identifies itself as the official website of the Town of Kaycee.",
    "https://www.kayceewyo.com/",
)

def register_people(P):
    P("WY-SCHIFFER-JOHN-C", "John C. Schiffer", "John", "Schiffer", middle="C.")
    P("WY-KINSKEY-DAVE", "Dave Kinskey", "Dave", "Kinskey")
    P("WY-CRAGO-BARRY", "Barry Crago", "Barry", "Crago")
    P("WY-MADDEN-MICHAEL", "Michael Madden", "Michael", "Madden", aliases="Mike Madden")
    P("WY-TASS-RICHARD-L", "Richard L. Tass", "Richard", "Tass", middle="L.")
    P("WY-CONNOLLY-MARILYN", "Marilyn F Connolly", "Marilyn", "Connolly",
      aliases="Marilyn Connolly; Marilyn F. Connolly; Marilyn Connoly")
    P("WY-NOVOTNY-BILL-III", "Bill Novotny III", "Bill", "Novotny", aliases="Bill Novotny; REP BILL NOVOTNY")
    P("WY-SHELLEY-JEFF", "Jeff Shelley", "Jeff", "Shelley", aliases="REP JEFF SHELLEY")
    P("WY-KOZISEK-STEVE", "Steve Kozisek", "Steve", "Kozisek")
    P("WY-CAMINO-JACKIE", "Jackie Camino", "Jackie", "Camino")
    P("WY-HARRIET-KATE", "Kate Harriet", "Kate", "Harriet")
    P("WY-RODRIGUEZ-BECKY", "Becky Rodriguez", "Becky", "Rodriguez")
    P("WY-BISHOP-CARLA", "Carla Bishop", "Carla", "Bishop")
    P("WY-BORGIALLI-BRITTNEE", "Brittnee Borgialli", "Brittnee", "Borgialli")
    P("WY-ESPONDA-STEVE", "Steve Esponda", "Steve", "Esponda", aliases="Stephen Esponda; STEPHEN ESPONDA")
    P("WY-ODENBACH-ROD", "Rod Odenbach", "Rod", "Odenbach")
    P("WY-KEELER-ADRIAN", "Adrian Keeler", "Adrian", "Keeler")
    P("WY-RUBY-TUCKER", "Tucker Ruby", "Tucker", "Ruby", aliases="Tucker J. Ruby; TUCKER J. RUBY; TUCKER J RUBY")
    P("WY-RHOADS-PAIGE", "Paige Rhoads", "Paige", "Rhoads")
    P("WY-SULLIVAN-SHAWN", "Shawn Sullivan", "Shawn", "Sullivan", aliases="Shawn M. Sullivan; SHAWN M. SULLIVAN; SHAWN M SULLIVAN")
    P("WY-FENN-JOHN", "John G. Fenn", "John", "Fenn", middle="G.")
    P("WY-EDELMAN", "Edelman", "Edelman", "Edelman")
    P("WY-PHILLIPS-DARCI", "Darci A.V. Phillips", "Darci", "Phillips", aliases="Darci A. V. Phillips")
    P("WY-KIRVEN-BENJAMIN", "Benjamin Kirven", "Benjamin", "Kirven")
    P("WY-CUNDIFF-SHELLEY-A", "Shelley A. Cundiff", "Shelley", "Cundiff", middle="A.")
    P("WY-BURNINGHAM-BEN", "Ben Burningham", "Ben", "Burningham")
    P("WY-SCHRADER-SHANE-J", "Shane J. Schrader", "Shane", "Schrader", middle="J.",
      aliases="Shane J Schrader; Shane James Schrader; SHANE JAMES SCHRADER")
    P("WY-JOHNSON-MICHAEL-R-MAYOR", "Michael R. Johnson", "Michael", "Johnson", middle="R.",
      aliases="Mike Johnson", slug="michael-r-johnson-buffalo-mayor")
    P("WY-CAMINO-MYRA", "Myra Camino", "Myra", "Camino")
    P("WY-HASKINS-WES", "Wes Haskins", "Wes", "Haskins")
    P("WY-MADDEN-MIKE-COUNCIL", "Mike Madden", "Mike", "Madden", slug="mike-madden-buffalo-council")
    P("WY-MADSEN-SCOTT", "Scott Madsen", "Scott", "Madsen", aliases="Richard \"Scott\" Madsen")
    P("WY-RUCKI-CRAIG", "Craig Rucki", "Craig", "Rucki")
    P("WY-KNAPP-TOM", "Tom Knapp", "Tom", "Knapp")
    P("WY-FOSTER-PAT", "Pat Foster", "Pat", "Foster")
    P("WY-FURNIVAL-BOB", "Bob Furnival", "Bob", "Furnival")
    P("WY-DAVIS-ALVIS", "Alvis Davis", "Alvis", "Davis")
    P("WY-LOMPE-JENNIFER", "Jennifer Lompe", "Jennifer", "Lompe")
    # JCSD #1
    P("WY-BELUS-DAVE", "Dave Belus", "Dave", "Belus")
    P("WY-GODDARD-MARCIA", "Marcia Goddard", "Marcia", "Goddard")
    P("WY-PEARSON-TRAVIS-D", "Travis D. Pearson", "Travis", "Pearson", middle="D.")
    P("WY-RODRIGUEZ-CASEY", "Casey Rodriguez", "Casey", "Rodriguez")
    P("WY-ESCOZ-DANIEL", "Daniel \"Noodle\" Escoz", "Daniel", "Escoz", aliases="Daniel Escoz")
    P("WY-FOX-LYNETTE", "Lynette Fox", "Lynette", "Fox")
    P("WY-DAVIDSON-REED", "Reed Davidson", "Reed", "Davidson")
    P("WY-MAYA-BENITO-A", "Benito A Maya", "Benito", "Maya", middle="A")
    P("WY-WRIGHT-MCKENZI", "McKenzi Wright", "McKenzi", "Wright")
    P("WY-BERGSTRESSER-BRYAN", "Bryan Bergstresser", "Bryan", "Bergstresser")
    P("WY-CURTRIGHT-CASEY", "Casey Curtright", "Casey", "Curtright")
    P("WY-HAGGE-REGG", "Regg Hagge", "Regg", "Hagge")
    # specials
    P("WY-CAMINO-SHEILA", "Sheila Camino", "Sheila", "Camino")
    P("WY-GRAVES-ELIZABETH", "Liz Graves", "Liz", "Graves", aliases="Elizabeth Graves; ELIZABETH GRAVES; LIZ GRAVES")
    P("WY-GODDARD-LUKE", "Luke Goddard", "Luke", "Goddard")
    P("WY-MUELLER-BARBARA", "Barbara Mueller", "Barbara", "Mueller")
    P("WY-HANCOCK-BOB", "Bob Hancock", "Bob", "Hancock")
    P("WY-SPIERING-KATHLEEN", "Kathleen \"Kassie\" Spiering", "Kathleen", "Spiering", aliases="Kassie Spiering")
    P("WY-BURKE-BILL", "Bill Burke", "Bill", "Burke")
    P("WY-FIELDGROVE-RYAN", "Ryan Fieldgrove", "Ryan", "Fieldgrove")
    P("WY-WATT-VIRGINIA", "Virginia Watt", "Virginia", "Watt")
    P("WY-FOSS-JAY", "Jay Foss", "Jay", "Foss")
    P("WY-BAKER-TRAVIS", "Travis Baker", "Travis", "Baker")
    P("WY-SCHUMAN-LARA", "Lara Schuman", "Lara", "Schuman")
    P("WY-HARLAN-THOMAS", "Thomas Harlan", "Thomas", "Harlan", aliases="Thomas H Harlan; THOMAS H HARLAN")
    P("WY-LUND-KEVIN", "Kevin Lund", "Kevin", "Lund")
    P("WY-LUND-KEVIN-FIRE", "Kevin Lund", "Kevin", "Lund", slug="kevin-lund-powder-river-fire")
    P("WY-CURUCHET-WADE-C", "Wade C Curuchet", "Wade", "Curuchet", middle="C")
    P("WY-RENKERT-GEORGE", "George Renkert", "George", "Renkert")
    P("WY-JONES-WILLIAM", "William Jones", "William", "Jones")
    P("WY-KOZISEK-PAUL", "Paul Kozisek", "Paul", "Kozisek")
    P("WY-STROM-KIRK-A", "Kirk A. Strom", "Kirk", "Strom", middle="A.", aliases="Kirk Strom")
    P("WY-HULET-AMANDA", "Amanda Hulet", "Amanda", "Hulet")
    P("WY-LOHSE-TOM", "Tom Lohse", "Tom", "Lohse")
    P("WY-CARR-MATT", "Matt Carr", "Matt", "Carr")
    P("WY-HAINES-STEVE", "Steve Haines", "Steve", "Haines")
    P("WY-PERRY-BRYCE", "Bryce Perry", "Bryce", "Perry")
    P("WY-GRIFFITH-RICH", "Rich Griffith", "Rich", "Griffith")
    P("WY-HOLT-THOMAS", "Thomas Holt", "Thomas", "Holt", aliases="Thomas A Holt")
    P("WY-KOZISEK-ALECIA", "Alecia Kozisek", "Alecia", "Kozisek")
    P("WY-HEIN-MATTHEW", "Matthew Hein", "Matthew", "Hein")
    P("WY-SCHUELER-MARK", "Mark Schueler", "Mark", "Schueler")
    P("WY-HAGGE-DANIELLE", "Danielle Hagge", "Danielle", "Hagge")
    P("WY-WILSON-MARK-K", "Mark K. Wilson", "Mark", "Wilson", middle="K.")
    P("WY-MICHELENA-ADAM", "Adam Michelena", "Adam", "Michelena")
    P("WY-WAMPOLE-COURTNEE", "Courtnee Wampole", "Courtnee", "Wampole")
    P("WY-LITZEL-MARY", "Mary Litzel", "Mary", "Litzel")
    P("WY-REIMLER-TIM", "Tim Reimler", "Tim", "Reimler")
    P("WY-CAMINO-BRITNI", "Britni Camino", "Britni", "Camino")
    P("WY-BUFFINGTON-KAREN", "Karen Buffington", "Karen", "Buffington")
    P("WY-FRALEY-MARGARET-R", "Margaret R. Fraley", "Margaret", "Fraley", middle="R.", aliases="Margaret R Fraley")
    P("WY-WILSON-MARK-A", "Mark A. Wilson", "Mark", "Wilson", middle="A.", aliases="Mark Alan Wilson")
    P("WY-GAY-DAN", "Dan Gay", "Dan", "Gay")
    P("WY-EDELMAN-VICKI", "Vicki Edelman", "Vicki", "Edelman")
    P("WY-NATION-KAY", "Kay Nation", "Kay", "Nation")


def _add(terms, pid, name, office, group, start, end, year, sources, notes, party="", how="elected", conf="high", **extra):
    kw=dict(person_id=pid, name=name, party=party, office_group=group, office=office,
            term_start=start if isinstance(start, str) and "-" in str(start) else (start if isinstance(start, str) else FM[start]),
            term_end=end if isinstance(end, str) and "-" in str(end) else (end if isinstance(end, str) else FM[end]),
            election_year=year, sources=sources, notes=notes, confidence=conf, how_took_office=how)
    if isinstance(start, int):
        kw["term_start"]=FM[start]
    if isinstance(end, int):
        kw["term_end"]=FM[end]
    kw.update(extra)
    terms.append(T(**kw))


def county_terms():
    terms = []
    s26, s24, s22 = [SRC_2026_SUM, SRC_2026_PCT], [SRC_2024_SUM], [SRC_2022_SUM]
    # Commissioners: official bio 2014 for Novotny pre-2022; official 2022 (vote 2) and 2026 (vote 2); official 2024 Kozisek (vote 1).
    _add(terms, "WY-NOVOTNY-BILL-III", "Bill Novotny III", "County Commissioner", "county",
         2015, 2023, 2014, [SRC_COMM, SRC_2022_SUM],
         "Official commissioners page, retrieved 2026-11-24: Bill Novotny III, Chairman. Official bio: elected in 2014 and chairman since 2016. Official intervening canvasses before 2022 were not confirmed (medium). Official 2022 general then records a Novotny win, below.",
         how="elected", conf="medium")
    _add(terms, "WY-NOVOTNY-BILL-III", "Bill Novotny III", "County Commissioner", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Commissioners (vote for 2): Bill Novotny 2,550, Jeff Shelley 3,024.")
    _add(terms, "WY-SHELLEY-JEFF", "Jeff Shelley", "County Commissioner", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Commissioners (vote for 2): Jeff Shelley 3,024, Bill Novotny 2,550. Official commissioners page, retrieved 2026-11-24, lists Jeff Shelley as Vice Chair.")
    _add(terms, "WY-NOVOTNY-BILL-III", "Bill Novotny III", "County Commissioner", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, County Commissioners (vote for 2): Bill Novotny 2,616, Jeff Shelley 2,803.")
    _add(terms, "WY-SHELLEY-JEFF", "Jeff Shelley", "County Commissioner", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, County Commissioners (vote for 2): Jeff Shelley 2,803, Bill Novotny 2,616.")
    _add(terms, "WY-KOZISEK-STEVE", "Steve Kozisek", "County Commissioner", "county",
         2025, 2029, 2024, s24,
         "Official 2024 general, County Commissioner (vote for 1): Steve Kozisek 4,309. Official commissioners page, retrieved 2026-11-24, lists him as Commissioner.")

    _add(terms, "WY-HARRIET-KATE", "Kate Harriet", "County Clerk", "county",
         2023, 2025, 2022, s22,
         "Official 2022 general, County Clerk: Kate Harriet 3,494. Official 2024 general then names Jackie Camino as clerk; the official 2024 summary does not label that race as an unexpired term.")
    _add(terms, "WY-CAMINO-JACKIE", "Jackie Camino", "County Clerk", "county",
         2025, 2027, 2024, s24,
         "Official 2024 general, County Clerk: Jackie Camino 4,217. Official clerk page, retrieved 2026-11-24, still names Jackie Camino. Official 2026 general names Becky Rodriguez as the next clerk (takes office January 2027). Official 2022, 2024, and 2026 canvasses each have a clerk race; that unusual sequence is recorded as printed and is not resolved beyond the official totals.")
    _add(terms, "WY-RODRIGUEZ-BECKY", "Becky Rodriguez", "County Clerk", "county",
         2027, 2031, 2026, s26,
         "Succeeding; official 2026 general, County Clerk: Becky Rodriguez 3,185.")

    _add(terms, "WY-BISHOP-CARLA", "Carla Bishop", "County Treasurer", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Treasurer: Carla Bishop 3,451. Official treasurer page, retrieved 2026-11-24, still names Carla Bishop.")
    _add(terms, "WY-BORGIALLI-BRITTNEE", "Brittnee Borgialli", "County Treasurer", "county",
         2027, 2031, 2026, s26,
         "Succeeding; official 2026 general, County Treasurer: Brittnee Borgialli 3,249, Manna Dudley Case 306.")

    _add(terms, "WY-ESPONDA-STEVE", "Steve Esponda", "County Assessor", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Assessor: Stephen Esponda 3,456. Official assessor page, retrieved 2026-11-24, names Steve Esponda.")
    _add(terms, "WY-ESPONDA-STEVE", "Steve Esponda", "County Assessor", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, County Assessor: Stephen Esponda 3,165. Display name Steve Esponda follows the official assessor page.")

    _add(terms, "WY-ODENBACH-ROD", "Rod Odenbach", "County Sheriff", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Sheriff: Rod Odenbach 3,309. Official sheriff page, retrieved 2026-11-24, still names Sheriff Rod Odenbach.")
    _add(terms, "WY-KEELER-ADRIAN", "Adrian Keeler", "County Sheriff", "county",
         2027, 2031, 2026, s26,
         "Succeeding; official 2026 general, County Sheriff: Adrian Keeler 3,126.")

    _add(terms, "WY-RUBY-TUCKER", "Tucker Ruby", "County Attorney", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Attorney: Tucker J Ruby 3,432. Official attorney page, retrieved 2026-11-24, names Tucker Ruby.")
    _add(terms, "WY-RUBY-TUCKER", "Tucker Ruby", "County Attorney", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, County Attorney: Tucker J. Ruby 3,106. Display name Tucker Ruby follows the official attorney page.")

    _add(terms, "WY-RHOADS-PAIGE", "Paige Rhoads", "Clerk of District Court", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, Clerk of District Court: Paige Rhoads 3,594. Official CDC page, retrieved 2026-11-24, names Paige Rhoads.")
    _add(terms, "WY-RHOADS-PAIGE", "Paige Rhoads", "Clerk of District Court", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Clerk of District Court: Paige Rhoads 3,288.")

    _add(terms, "WY-SULLIVAN-SHAWN", "Shawn Sullivan", "County Coroner", "county",
         2023, 2027, 2022, s22,
         "Official 2022 general, County Coroner: Shawn M Sullivan 3,479. Official coroner page, retrieved 2026-11-24, names Shawn Sullivan.")
    _add(terms, "WY-SULLIVAN-SHAWN", "Shawn Sullivan", "County Coroner", "county",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, County Coroner: Shawn M. Sullivan 3,291. Display name Shawn Sullivan follows the official coroner page.")
    return terms


def judicial_terms():
    terms = []
    # Fenn / Edelman remain from official Sheridan-cited 2020 retentions (no official Johnson 2020 canvass found).
    terms.append(T(person_id="WY-FENN-JOHN", name="John G. Fenn", party="", office_group="judicial",
                   office="District Judge, 4th Judicial District", term_start=FM[2021], term_end=FM[2023],
                   election_year=2020, how_took_office="retained", confidence="medium", sources=[SRC_COURT],
                   notes="Official 4th JD district judge John G. Fenn, from official sources already used in the Sheridan history (official 2020 Sheridan named retention). Official Johnson 2020 YES/NO were not found in the official Election Archives folders available in this preview."))
    terms.append(T(person_id="WY-EDELMAN", name="Edelman", party="", office_group="judicial",
                   office="District Judge, 4th Judicial District", term_start=FM[2021], term_end=FM[2025],
                   election_year=2020, how_took_office="retained", confidence="medium", sources=[SRC_COURT],
                   notes="Official 2020 Sheridan general names this 4th JD retention as DIST CT - EDELMAN without a first name. Official Johnson 2020 YES/NO were not found in this preview."))
    # Official 2024 Johnson canvass
    yes, no = 3289, 680
    tot=yes+no
    terms.append(T(person_id="WY-PHILLIPS-DARCI", name="Darci A.V. Phillips", party="", office_group="judicial",
                   office="District Judge, 4th Judicial District", term_start=FM[2025], term_end=FM[2031],
                   election_year=2024, how_took_office="retained", confidence="high", sources=[SRC_2024_SUM],
                   notes="Official 2024 Johnson general, RETAIN JUDGE A DARCI A. V. PHILLIPS, YES 3,289 / NO 680.",
                   retention={"year": 2024, "yes": yes, "no": no, "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                              "result": "retained", "source": SRC_2024_SUM["url"]}))
    yes, no = 3519, 781
    tot=yes+no
    terms.append(T(person_id="WY-KIRVEN-BENJAMIN", name="Benjamin Kirven", party="", office_group="judicial",
                   office="District Judge, 4th Judicial District", term_start=FM[2025], term_end=FM[2031],
                   election_year=2024, how_took_office="retained", confidence="high", sources=[SRC_2024_SUM],
                   notes="Official 2024 Johnson general, RETAIN JUDGE B BENJAMIN KIRVEN, YES 3,519 / NO 781.",
                   retention={"year": 2024, "yes": yes, "no": no, "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                              "result": "retained", "source": SRC_2024_SUM["url"]}))
    # Official 2022 Johnson circuit retention of Cundiff
    yes, no = 2399, 976
    tot=yes+no
    terms.append(T(person_id="WY-CUNDIFF-SHELLEY-A", name="Shelley A. Cundiff", party="", office_group="judicial",
                   office="Circuit Judge, 4th Judicial District", term_start=FM[2023], term_end=FM[2027],
                   election_year=2022, how_took_office="retained", confidence="high", sources=[SRC_2022_SUM],
                   notes="Official 2022 Johnson general, FOURTH JUDICIAL DIST CIRCUIT COURT JUDGE CUNDIFF, YES 2,399 / NO 976. The official 2022 summary does not print a first name; Shelley A. Cundiff is the official name already used in the Sheridan history for this 2022 retention.",
                   retention={"year": 2022, "yes": yes, "no": no, "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                              "result": "retained", "source": SRC_2022_SUM["url"]}))
    # Official 2026 Johnson named retention: JUDGE BEN BURNINGHAM (title does not say district vs circuit)
    yes, no = 2398, 568
    tot=yes+no
    terms.append(T(person_id="WY-BURNINGHAM-BEN", name="Ben Burningham", party="", office_group="judicial",
                   office="Circuit Judge, 4th Judicial District", term_start=FM[2027], term_end=FM[2031],
                   election_year=2026, how_took_office="retained", confidence="medium", sources=[SRC_2026_SUM, SRC_2026_PCT],
                   notes="Official 2026 general, RETAIN JUDGE BEN BURNINGHAM, YES 2,398 / NO 568. The official 2026 line does not say district or circuit. This row is listed as the 4th JD circuit seat following the official 2022 Johnson circuit retention of Judge Cundiff, without inventing an appointment date (medium on the circuit title). The official 2026 summary image is dated 11/06/2026 12:19PM, Precincts Complete 16 of 16.",
                   retention={"year": 2026, "yes": yes, "no": no, "yes_pct": f"{yes/tot*100:.2f}%", "no_pct": f"{no/tot*100:.2f}%",
                              "result": "retained", "source": SRC_2026_SUM["url"]}))
    return terms


def municipal_terms():
    terms = []
    s26, s24, s22 = [SRC_2026_SUM, SRC_2026_PCT], [SRC_2024_SUM], [SRC_2022_SUM]
    terms.append(T(person_id="WY-JOHNSON-MICHAEL-R-MAYOR", name="Michael R. Johnson", party="", office_group="municipal",
                   office="City of Buffalo Mayor", term_start="2015-01-01", term_end="2019-01-01",
                   election_year=None, how_took_office="unknown", confidence="medium", sources=[SRC_BUF_MAYOR],
                   notes="Official City of Buffalo Mayor's Office page, Former Mayors: 01/2015 to 12.2018 Michael R. Johnson."))
    _add(terms, "WY-SCHRADER-SHANE-J", "Shane J. Schrader", "City of Buffalo Mayor", "municipal",
         2019, 2023, None, [SRC_BUF_MAYOR],
         "Official City of Buffalo Mayor's Office page, retrieved 2026-11-24, names Mayor Shane J. Schrader. Official former-mayor list ends 12/2018 (Michael R. Johnson); the official start day is taken as January 2019 following that official list (medium). Official 2022 general then records a Schrader mayoral win, below.",
         how="unknown", conf="medium")
    # fix election_year None - T() may need year. Use 0 or omit? term() probably ok with None. I passed None as year - need to use a year. Use 2018 medium without inventing.
    terms[-1]["election_year"] = None
    _add(terms, "WY-SCHRADER-SHANE-J", "Shane J. Schrader", "City of Buffalo Mayor", "municipal",
         2023, 2027, 2022, s22,
         "Official 2022 general, Mayor: Shane J Schrader 1,097. Official city Mayor's Office page, retrieved 2026-11-24, names Shane J. Schrader.")
    _add(terms, "WY-SCHRADER-SHANE-J", "Shane J. Schrader", "City of Buffalo Mayor", "municipal",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Mayor: Shane James Schrader 847, Bob Hancock 711. Display name Shane J. Schrader follows the official city page and the official 2022 ballot.")

    _add(terms, "WY-CAMINO-MYRA", "Myra Camino", "City of Buffalo Council", "municipal",
         2023, 2027, 2022, s22,
         "Official 2022 general, City Council Member (vote for 2): Myra Camino 1,135, Mike Madden 769.")
    _add(terms, "WY-MADDEN-MIKE-COUNCIL", "Mike Madden", "City of Buffalo Council", "municipal",
         2023, 2027, 2022, s22,
         "Official 2022 general, City Council Member (vote for 2): Mike Madden 769, Myra Camino 1,135. Distinct from historical House District 40 member Michael Madden unless an official source identifies them as the same person.")
    _add(terms, "WY-HASKINS-WES", "Wes Haskins", "City of Buffalo Council", "municipal",
         2025, 2029, 2024, s24,
         "Official 2024 general, City Council Member (vote for 2): Wes Haskins 1,339, Richard \"Scott\" Madsen 1,166.")
    _add(terms, "WY-MADSEN-SCOTT", "Scott Madsen", "City of Buffalo Council", "municipal",
         2025, 2029, 2024, s24,
         "Official 2024 general, City Council Member (vote for 2): Richard \"Scott\" Madsen 1,166, Wes Haskins 1,339. Display name Scott Madsen follows the official City of Buffalo council page.")
    _add(terms, "WY-CAMINO-MYRA", "Myra Camino", "City of Buffalo Council", "municipal",
         2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, City Council Member (vote for 2): Myra Camino 1,100, Craig Rucki 595.")
    _add(terms, "WY-RUCKI-CRAIG", "Craig Rucki", "City of Buffalo Council", "municipal",
         2027, 2031, 2026, s26,
         "Succeeding; official 2026 general, City Council Member (vote for 2): Craig Rucki 595, Myra Camino 1,100.")

    # Official Town of Kaycee roster. Terms printed as 2026-2030 or 2024-2028; exact start/end day not printed (medium on day).
    _add(terms, "WY-KNAPP-TOM", "Tom Knapp", "Town of Kaycee Mayor", "municipal",
         "2026-01-01", "2031-01-05", None, [SRC_KAYCEE, SRC_KAYCEE_HOME],
         "Official Town of Kaycee Town Council page, retrieved 2026-11-24: Tom Knapp, Mayor, Term: 2026–2030. Official page says term spans are the four-year terms each seat is elected for. Kaycee mayor/council were not on the official November 2026 Johnson County general canvass. Exact term-start day is not printed (medium).",
         how="unknown", conf="medium")
    _add(terms, "WY-FOSTER-PAT", "Pat Foster", "Town of Kaycee Council", "municipal",
         "2024-01-01", "2029-01-01", None, [SRC_KAYCEE],
         "Official Town of Kaycee Town Council page, retrieved 2026-11-24: Pat Foster, Vice Mayor, Term: 2024–2028. Exact term-start day is not printed (medium).",
         how="unknown", conf="medium")
    _add(terms, "WY-FURNIVAL-BOB", "Bob Furnival", "Town of Kaycee Council", "municipal",
         "2024-01-01", "2029-01-01", None, [SRC_KAYCEE],
         "Official Town of Kaycee Town Council page, retrieved 2026-11-24: Bob Furnival, Council, Term: 2024–2028. Exact term-start day is not printed (medium).",
         how="unknown", conf="medium")
    _add(terms, "WY-DAVIS-ALVIS", "Alvis Davis", "Town of Kaycee Council", "municipal",
         "2026-01-01", "2031-01-05", None, [SRC_KAYCEE],
         "Official Town of Kaycee Town Council page, retrieved 2026-11-24: Alvis Davis, Council, Term: 2026–2030. Exact term-start day is not printed (medium).",
         how="unknown", conf="medium")
    _add(terms, "WY-LOMPE-JENNIFER", "Jennifer Lompe", "Town of Kaycee Council", "municipal",
         "2026-01-01", "2031-01-05", None, [SRC_KAYCEE],
         "Official Town of Kaycee Town Council page, retrieved 2026-11-24: Jennifer Lompe, Council, Term: 2026–2030. Exact term-start day is not printed (medium).",
         how="unknown", conf="medium")
    return terms


def school_terms():
    terms = []
    s26, s24, s22 = [SRC_2026_SUM, SRC_2026_PCT], [SRC_2024_SUM], [SRC_2022_SUM]
    office = "Johnson County School District #1 Trustee"
    # Official 2022 vote for 4 (terms through January 2027)
    for pid, name, n in [
        ("WY-GODDARD-MARCIA", "Marcia Goddard", "2,100"),
        ("WY-BELUS-DAVE", "Dave Belus", "2,010"),
        ("WY-RODRIGUEZ-CASEY", "Casey Rodriguez", "1,890"),
        ("WY-PEARSON-TRAVIS-D", "Travis D. Pearson", "1,788"),
    ]:
        _add(terms, pid, name, office, "schools", 2023, 2027, 2022, s22,
             f"Official 2022 general, School Board Trustee at Large (vote for 4): {name} {n}. Distinct from any similarly named person unless an official source identifies them as the same.")
    # Official 2024 vote for 5 (terms through January 2029)
    for pid, name, n in [
        ("WY-FOX-LYNETTE", "Lynette Fox", "3,013"),
        ("WY-ESCOZ-DANIEL", "Daniel \"Noodle\" Escoz", "2,800"),
        ("WY-MAYA-BENITO-A", "Benito A Maya", "2,698"),
        ("WY-WRIGHT-MCKENZI", "McKenzi Wright", "2,358"),
        ("WY-DAVIDSON-REED", "Reed Davidson", "2,332"),
    ]:
        _add(terms, pid, name, office, "schools", 2025, 2029, 2024, s24,
             f"Official 2024 general, School Board Trustee at Large (vote for 5): {name} {n}.")
    # Official 2026 vote for 4 (terms January 2027-2031). Casey Curtright is not combined with 2022 Casey Rodriguez.
    for pid, name, n in [
        ("WY-PEARSON-TRAVIS-D", "Travis D. Pearson", "2,427"),
        ("WY-BERGSTRESSER-BRYAN", "Bryan Bergstresser", "2,144"),
        ("WY-CURTRIGHT-CASEY", "Casey Curtright", "2,133"),
        ("WY-HAGGE-REGG", "Regg Hagge", "2,048"),
    ]:
        note = f"Official 2026 general, School Board Trustee at Large (vote for 4): {name} {n}."
        if pid == "WY-PEARSON-TRAVIS-D":
            note = "Re-elected; " + note
        elif pid == "WY-CURTRIGHT-CASEY":
            note += " Not combined with 2022 official winner Casey Rodriguez without an official identification."
        _add(terms, pid, name, office, "schools", 2027, 2031, 2026, s26, note)
    return terms


def special_terms():
    terms = []
    s26, s24, s22 = [SRC_2026_SUM, SRC_2026_PCT], [SRC_2024_SUM], [SRC_2022_SUM]
    # Cemetery
    o="Cemetery District Trustee"
    for pid, name, n in [("WY-CAMINO-SHEILA","Sheila Camino","2,505"),("WY-GODDARD-LUKE","Luke Goddard","2,412"),("WY-GRAVES-ELIZABETH","Liz Graves","2,323")]:
        _add(terms, pid, name, o, "special-districts", 2023, 2027, 2022, s22,
             f"Official 2022 general, Cemetery District Trustee (vote for 3): official ballot Elizabeth Graves 2,323 / Sheila Camino 2,505 / Luke Goddard 2,412. Display Liz Graves follows the official 2026 ballot for the same seat class.")
    _add(terms, "WY-MUELLER-BARBARA", "Barbara Mueller", o, "special-districts", 2023, 2025, 2022, s22,
         "Official 2022 general, Cemetery District Trustee Unexpired: Barbara Mueller 3,123.")
    for pid, name, n in [("WY-SPIERING-KATHLEEN","Kathleen \"Kassie\" Spiering","3,032"),("WY-HANCOCK-BOB","Bob Hancock","2,988"),("WY-MUELLER-BARBARA","Barbara Mueller","2,920")]:
        _add(terms, pid, name, o, "special-districts", 2025, 2029, 2024, s24,
             f"Official 2024 general, Cemetery Dist Trustee (vote for 3): {name} {n}.")
    for pid, name, n in [("WY-GODDARD-LUKE","Luke Goddard","2,643"),("WY-CAMINO-SHEILA","Sheila Camino","2,608"),("WY-GRAVES-ELIZABETH","Liz Graves","2,552")]:
        _add(terms, pid, name, o, "special-districts", 2027, 2031, 2026, s26,
             f"Re-elected; official 2026 general, Cemetery Dist Trustee (vote for 3): {name} {n}.")

    # Clear Creek
    _add(terms, "WY-FIELDGROVE-RYAN", "Ryan Fieldgrove", "Clear Creek Conservation District Rural", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Clear Creek Conservation Dist Rural (vote for 2): Ryan Fieldgrove 2,739, Virginia Watt 2,433.")
    _add(terms, "WY-WATT-VIRGINIA", "Virginia Watt", "Clear Creek Conservation District Rural", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Clear Creek Conservation Dist Rural (vote for 2): Virginia Watt 2,433, Ryan Fieldgrove 2,739.")
    _add(terms, "WY-FOSS-JAY", "Jay Foss", "Clear Creek Conservation District At Large", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Clear Creek Conservation Dist At Large: Jay Foss 2,822.")
    _add(terms, "WY-BAKER-TRAVIS", "Travis Baker", "Clear Creek Conservation District Rural", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Clear Creek Conserv Dist Rural (vote for 1): Travis Baker 3,445.")
    _add(terms, "WY-SCHUMAN-LARA", "Lara Schuman", "Clear Creek Conservation District Urban", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Clear Creek Conserv Dist Urban (vote for 1): Lara Schuman 3,474.")
    _add(terms, "WY-FIELDGROVE-RYAN", "Ryan Fieldgrove", "Clear Creek Conservation District Rural", "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Clear Creek Conservation Dist Rural (vote for 2): Ryan Fieldgrove 2,575, Bill Burke 2,217.")
    _add(terms, "WY-BURKE-BILL", "Bill Burke", "Clear Creek Conservation District Rural", "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Clear Creek Conservation Dist Rural (vote for 2): Bill Burke 2,217, Ryan Fieldgrove 2,575.")
    _add(terms, "WY-FOSS-JAY", "Jay Foss", "Clear Creek Conservation District At Large", "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Clear Creek Conservation Dist At Large: Jay Foss 1,191, Rick Pallister 1,099, Kris Whitney 379.")

    # Powder River conservation
    _add(terms, "WY-HARLAN-THOMAS", "Thomas Harlan", "Powder River Conservation District Rural", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Powder River Conservation Dist Rural: Thomas H Harlan 375.")
    _add(terms, "WY-LUND-KEVIN", "Kevin Lund", "Powder River Conservation District At Large", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Powder River Conservation Dist At Large: Kevin Lund 375.")
    _add(terms, "WY-CURUCHET-WADE-C", "Wade C Curuchet", "Powder River Conservation District Rural", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Powder River Conserv Dist Rural (vote for 2): Wade C Curuchet 443, George Renkert 349.")
    _add(terms, "WY-RENKERT-GEORGE", "George Renkert", "Powder River Conservation District Rural", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Powder River Conserv Dist Rural (vote for 2): George Renkert 349, Wade C Curuchet 443.")
    _add(terms, "WY-JONES-WILLIAM", "William Jones", "Powder River Conservation District Urban", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Powder River Conserv Dist Urban: William Jones 443.")
    _add(terms, "WY-HARLAN-THOMAS", "Thomas Harlan", "Powder River Conservation District Rural", "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Powder River Conservation Dist Rural: Thomas Harlan 319.")
    _add(terms, "WY-LUND-KEVIN", "Kevin Lund", "Powder River Conservation District At Large", "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Powder River Conservation Dist At Large: Kevin Lund 317.")

    # Fire #1
    _add(terms, "WY-KOZISEK-PAUL", "Paul Kozisek", "Johnson County Fire District #1 Trustee", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Johnson County Fire Dist 1 Trustee (vote for 2): Paul Kozisek 1,353, Amanda Hulet 1,154.")
    _add(terms, "WY-HULET-AMANDA", "Amanda Hulet", "Johnson County Fire District #1 Trustee", "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Johnson County Fire Dist 1 Trustee (vote for 2): Amanda Hulet 1,154, Paul Kozisek 1,353.")
    _add(terms, "WY-LOHSE-TOM", "Tom Lohse", "Johnson County Fire District #1 Trustee", "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Johnson Co Fire Dist 1 Trustee 4yr: Tom Lohse 1,713.")
    _add(terms, "WY-STROM-KIRK-A", "Kirk A. Strom", "Johnson County Fire District #1 Trustee", "special-districts", 2025, 2027, 2024, s24,
         "Official 2024 general, Johnson Co Fire Dist 1 Trustee 2yr: Kirk Strom 1,583.")
    _add(terms, "WY-KOZISEK-PAUL", "Paul Kozisek", "Johnson County Fire District #1 Trustee", "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Johnson Co Fire Dist #1 Trustee (vote for 2): Paul Kozisek 1,302, Kirk A. Strom 1,058.")
    _add(terms, "WY-STROM-KIRK-A", "Kirk A. Strom", "Johnson County Fire District #1 Trustee", "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Johnson Co Fire Dist #1 Trustee (vote for 2): Kirk A. Strom 1,058, Paul Kozisek 1,302.")

    # Powder River Fire
    o="Powder River Fire District Trustee"
    _add(terms, "WY-CARR-MATT", "Matt Carr", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Powder River Fire Dist Trustee (vote for 2): Matt Carr 335, Steve Haines 321.")
    _add(terms, "WY-HAINES-STEVE", "Steve Haines", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Powder River Fire Dist Trustee (vote for 2): Steve Haines 321, Matt Carr 335.")
    _add(terms, "WY-LUND-KEVIN-FIRE", "Kevin Lund", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Powder River Fire Dist Trustee 4yr: Kevin Lund 464. Distinct person ID from the Powder River Conservation District Kevin Lund without an official identification.")
    _add(terms, "WY-PERRY-BRYCE", "Bryce Perry", o, "special-districts", 2025, 2027, 2024, s24,
         "Official 2024 general, Powder River Fire Dist Trustee 2yr: Bryce Perry 461.")
    _add(terms, "WY-CARR-MATT", "Matt Carr", o, "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Powder River Fire Dist Trustee (vote for 2): Matt Carr 207.")
    _add(terms, "WY-PERRY-BRYCE", "Bryce Perry", o, "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Powder River Fire Dist Trustee (vote for 2): official named write-in Bryce Perry 102 (Write-In Totals 109). Official certification names Bryce Perry on the official summary.")

    # Hospital
    o="Hospital District Trustee"
    for pid, name, n in [("WY-KOZISEK-ALECIA","Alecia Kozisek","2,907"),("WY-HOLT-THOMAS","Thomas Holt","2,699"),("WY-GRIFFITH-RICH","Rich Griffith","2,616")]:
        _add(terms, pid, name, o, "special-districts", 2023, 2027, 2022, s22,
             f"Official 2022 general, Hospital Dist Trustee (vote for 3): official ballot Thomas A Holt 2,699 / Alecia Kozisek 2,907 / Rich Griffith 2,616.")
    _add(terms, "WY-HEIN-MATTHEW", "Matthew Hein", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Hospital Dist Trustee (vote for 2): Matthew Hein 3,316, Mark Schueler 3,306.")
    _add(terms, "WY-SCHUELER-MARK", "Mark Schueler", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Hospital Dist Trustee (vote for 2): Mark Schueler 3,306, Matthew Hein 3,316.")
    for pid, name, n in [("WY-KOZISEK-ALECIA","Alecia Kozisek","2,297"),("WY-HOLT-THOMAS","Thomas Holt","1,813"),("WY-GRIFFITH-RICH","Rich Griffith","1,635")]:
        _add(terms, pid, name, o, "special-districts", 2027, 2031, 2026, s26,
             f"Re-elected; official 2026 general, Hospital Dist Trustee (vote for 3): Alecia Kozisek 2,297, Thomas Holt 1,813, Rich Griffith 1,635, Mark K. Wilson 1,619, Danielle Hagge 839.")

    # Rural health
    o="Rural Health Care District Trustee"
    for pid, name, n in [("WY-MICHELENA-ADAM","Adam Michelena","1,856"),("WY-CAMINO-BRITNI","Britni Camino","1,895")]:
        # 2022 vote 3 winners: Britni Camino 1,895, Mark Schueler 1,892, Adam Michelena 1,856 (Jim Hicks 1,181 OCR maybe 1,181)
        pass
    _add(terms, "WY-CAMINO-BRITNI", "Britni Camino", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Rural Health Care Dist Trustee (vote for 3): Britni Camino 1,895.")
    _add(terms, "WY-SCHUELER-MARK", "Mark Schueler", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Rural Health Care Dist Trustee (vote for 3): Mark Schueler 1,892.")
    _add(terms, "WY-MICHELENA-ADAM", "Adam Michelena", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Rural Health Care Dist Trustee (vote for 3): Adam Michelena 1,856.")
    _add(terms, "WY-LITZEL-MARY", "Mary Litzel", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Rural Health Care Dist Trustee (vote for 2): Mary Litzel 3,551, Tim Reimler 3,216.")
    _add(terms, "WY-REIMLER-TIM", "Tim Reimler", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Rural Health Care Dist Trustee (vote for 2): Tim Reimler 3,216, Mary Litzel 3,551.")
    _add(terms, "WY-SCHUELER-MARK", "Mark Schueler", o, "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Rural Health Care Dist Trustee (vote for 3): Mark Schueler 2,552, Adam Michelena 2,471, Courtnee Wampole 2,180.")
    _add(terms, "WY-MICHELENA-ADAM", "Adam Michelena", o, "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Rural Health Care Dist Trustee (vote for 3): Adam Michelena 2,471, Mark Schueler 2,552, Courtnee Wampole 2,180.")
    _add(terms, "WY-WAMPOLE-COURTNEE", "Courtnee Wampole", o, "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Rural Health Care Dist Trustee (vote for 3): Courtnee Wampole 2,180, Mark Schueler 2,552, Adam Michelena 2,471.")

    # Senior
    o="Senior Citizen Service District Trustee"
    _add(terms, "WY-GAY-DAN", "Dan Gay", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Senior Citizen Service Dist Trustee (vote for 3): Dan Gay 3,078, Margaret R Fraley 2,838, Mark Alan Wilson 2,557.")
    _add(terms, "WY-FRALEY-MARGARET-R", "Margaret R. Fraley", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Senior Citizen Service Dist Trustee (vote for 3): Margaret R Fraley 2,838.")
    _add(terms, "WY-WILSON-MARK-A", "Mark A. Wilson", o, "special-districts", 2023, 2027, 2022, s22,
         "Official 2022 general, Senior Citizen Service Dist Trustee (vote for 3): Mark Alan Wilson 2,557.")
    _add(terms, "WY-EDELMAN-VICKI", "Vicki Edelman", o, "special-districts", 2025, 2029, 2024, s24,
         "Official 2024 general, Snr Citizen Serv Dist Trustee 4yr (vote for 2): Vicki Edelman 3,943. The official 2024 summary lists only one named candidate in that vote-for-2 contest; a second named 4-year winner was not printed.")
    _add(terms, "WY-BUFFINGTON-KAREN", "Karen Buffington", o, "special-districts", 2025, 2027, 2024, s24,
         "Official 2024 general, Snr Citizen Serv Dist Trustee 2yr: Karen Buffington 3,865.")
    _add(terms, "WY-FRALEY-MARGARET-R", "Margaret R. Fraley", o, "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Senior Citizen Service Dist Trustee (vote for 3): Margaret R. Fraley 2,690, Karen Buffington 2,509, Mark A. Wilson 2,369.")
    _add(terms, "WY-BUFFINGTON-KAREN", "Karen Buffington", o, "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Senior Citizen Service Dist Trustee (vote for 3): Karen Buffington 2,509.")
    _add(terms, "WY-WILSON-MARK-A", "Mark A. Wilson", o, "special-districts", 2027, 2031, 2026, s26,
         "Re-elected; official 2026 general, Senior Citizen Service Dist Trustee (vote for 3): Mark A. Wilson 2,369.")
    _add(terms, "WY-NATION-KAY", "Kay Nation", o, "special-districts", 2027, 2031, 2026, s26,
         "Official 2026 general, Senior Citizen Service Dist Trustee Unexpired: Kay Nation 2,703. Term-end follows the ordinary next cycle for this 2026 unexpired race (medium on the exact end day).")
    return terms


def expected_offices():
    return {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
                      ("State Treasurer", 1), ("Superintendent of Public Instruction", 1)],
        "state-senate": [("Senate District 22 (S22)", 1)],
        "state-house": [("House District 40 (H40)", 1)],
        "county": [("County Commissioner", 3), ("County Clerk", 1), ("County Treasurer", 1),
                   ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
                   ("Clerk of District Court", 1), ("County Coroner", 1)],
        "municipal": [
            ("City of Buffalo Mayor", 1), ("City of Buffalo Council", 4),
            ("Town of Kaycee Mayor", 1), ("Town of Kaycee Council", 4),
        ],
        "schools": [("Johnson County School District #1 Trustee", 9)],
        "special-districts": [
            ("Cemetery District Trustee", 6),
            ("Clear Creek Conservation District Rural", 3),
            ("Clear Creek Conservation District At Large", 1),
            ("Clear Creek Conservation District Urban", 1),
            ("Powder River Conservation District Rural", 3),
            ("Powder River Conservation District At Large", 1),
            ("Powder River Conservation District Urban", 1),
            ("Johnson County Fire District #1 Trustee", 4),
            ("Powder River Fire District Trustee", 4),
            ("Hospital District Trustee", 5),
            ("Rural Health Care District Trustee", 5),
            ("Senior Citizen Service District Trustee", 6),
        ],
        "judicial": [
            ("District Judge, 4th Judicial District", 2),
            ("Circuit Judge, 4th Judicial District", 1),
        ],
    }


def legislature_terms():
    terms = []
    s22 = [
        (2012, "WY-SCHIFFER-JOHN-C", "John C. Schiffer",
         "Official 2012 SOS statewide Senate summary, Senate District 22: John C. Schiffer (R) Total 7,658. Official Johnson share 3,683; official Sheridan 3,975."),
        (2016, "WY-KINSKEY-DAVE", "Dave Kinskey",
         "Official 2016 SOS statewide Senate summary, Senate District 22 (left column beside Senate District 24; that district's Total is not used): Dave Kinskey (R) Total 7,603. Official Johnson share 3,857; official Sheridan 3,746."),
        (2020, "WY-KINSKEY-DAVE", "Dave Kinskey",
         "Official 2020 SOS statewide Senate summary, Senate District 22 (left column beside Senate District 24; that district's Total is not used): Dave Kinskey (R) Total 8,516. Official Johnson share 4,226; official Sheridan 4,290."),
        (2024, "WY-CRAGO-BARRY", "Barry Crago",
         "Official 2024 SOS statewide Senate summary, Senate District 22: Barry Crago (R) Total 8,599. Official Johnson share 4,135; official Sheridan 4,464."),
    ]
    for year, pid, name, note in s22:
        terms.append(T(person_id=pid, name=name, party="R", office_group="state-senate",
                       office="Senate District 22 (S22)", term_start=FM[year + 1], term_end=FM[year + 5],
                       election_year=year, sources=[sos_src(year, "Senate")], notes=note))
    h40 = [
        (2012, "WY-MADDEN-MICHAEL", "Michael Madden",
         "Official 2012 SOS statewide House summary, House District 40: Michael Madden (R) Total 3,806. Official Johnson share 3,609; official Sheridan 197."),
        (2014, "WY-MADDEN-MICHAEL", "Michael Madden",
         "Official 2014 SOS statewide House summary, House District 40: Mike Madden (R) Total 2,827. Official Johnson share 2,685; official Sheridan 142."),
        (2016, "WY-MADDEN-MICHAEL", "Michael Madden",
         "Official 2016 SOS statewide House summary, House District 40 (right column beside House District 39; that district's Total is not used): Michael Madden (R) 3,534, Greg Haas (D) 834. Official Johnson share Madden 3,365, Haas 796; official Sheridan 169-38."),
        (2018, "WY-TASS-RICHARD-L", "Richard L. Tass",
         "Official 2018 SOS statewide House summary, House District 40 (right column beside House District 39; that district's Total is not used): Richard L. Tass (R) 2,355, Chris Schock (I) 1,552. Official Johnson share Tass 2,284, Schock 1,444; official Sheridan Tass 71, Schock 108 (district-wide Tass is the official winner)."),
        (2020, "WY-CRAGO-BARRY", "Barry Crago",
         "Official 2020 SOS statewide House summary, House District 40 (right column beside House District 39; that district's Total is not used): Barry Crago (R) Total 4,489. Official Johnson share 4,277; official Sheridan 212."),
        (2022, "WY-CRAGO-BARRY", "Barry Crago",
         "Official 2022 SOS statewide House summary, House District 40: Barry Crago (R) Total 4,007. Official Johnson share 3,416; official Sheridan 591."),
        (2024, "WY-CONNOLLY-MARILYN", "Marilyn F Connolly",
         "Official 2024 SOS statewide House summary, House District 40: Marilyn Connoly (R) (official SOS spelling) Total 4,806. Official Johnson share 4,100; official Sheridan 706. Display name Marilyn F Connolly follows the existing official-history person already used in Sheridan."),
        (2026, "WY-CONNOLLY-MARILYN", "Marilyn F Connolly",
         "Official 2026 SOS statewide House summary, House District 40: Marilyn Connolly (R) Total 3,677. Official Johnson share 3,122; official Sheridan 555."),
    ]
    for year, pid, name, note in h40:
        terms.append(T(person_id=pid, name=name, party="R", office_group="state-house",
                       office="House District 40 (H40)", term_start=FM[year + 1], term_end=FM[year + 3],
                       election_year=year, sources=[sos_src(year, "House")], notes=note))
    return terms


def build_johnson():
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
        "4th Judicial District judges (serving Johnson with Sheridan and other 4th JD counties). Full names follow "
        "official sources already used in the Sheridan history. Official Johnson named-retention YES/NO totals were "
        "not confirmed from a certified official Johnson clerk canvass in this preview."
    )
    coverage = H.write_terms_and_snapshots(
        county="Johnson", county_number=CN, slug=SLUG, terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
    )
    H.write_people_additions(people)
    H.write_offices_held(terms, people)
    H.write_profiles(terms, people, county="Johnson", slug=SLUG)
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


def update_johnson_json(people, terms):
    path = ROOT / "data" / "county_officials" / "johnson.json"
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
        _office("Senate District 22 (S22)", holders("Senate District 22 (S22)"),
                note="Official 2024 SOS statewide Senate summary, Senate District 22: Barry Crago (R) Total 8,599. Official Johnson share 4,135; official Sheridan 4,464. Official 2024 Johnson clerk summary (OFFICAL typo on the header; Precincts Complete 16 of 16) records the official Johnson share as Barry Crago 4,135. Off-cycle in 2026."),
    ]
    house = [
        _office("House District 40 (H40)", holders("House District 40 (H40)"),
                note="Official 2026 SOS statewide House summary, House District 40: Marilyn Connolly (R) Total 3,677. Official Johnson share 3,122; official Sheridan 555. Official 2026 Johnson clerk canvass (OFFICIAL RESULTS, 16 of 16 precincts complete) records Marilyn Connolly 3,122 in Johnson County. Display name Marilyn F Connolly follows the existing official-history person already used in Sheridan."),
    ]
    county = [
        _office("County Commissioner", holders("County Commissioner"),
                layout="heading-then-names",
                note="Three-member board. Official 2026 general (vote for 2): Bill Novotny 2,616 and Jeff Shelley 2,803, taking office January 2027. Official 2024 general (vote for 1): Steve Kozisek 4,309, term through January 2029. Official commissioners page, retrieved 2026-11-24, lists Novotny as Chairman and Shelley as Vice Chair."),
        _office("County Clerk", holders("County Clerk"),
                note="Official clerk page, retrieved 2026-11-24, names Jackie Camino (official 2024 general, 4,217). Official 2026 general: Becky Rodriguez 3,185, taking office January 2027. Official 2022, 2024, and 2026 canvasses each include a clerk race; that sequence is recorded as printed."),
        _office("County Treasurer", holders("County Treasurer"),
                note="Official treasurer page, retrieved 2026-11-24, names Carla Bishop (official 2022 general, 3,451). Official 2026 general: Brittnee Borgialli 3,249, taking office January 2027."),
        _office("County Assessor", holders("County Assessor"),
                note="Official assessor page, retrieved 2026-11-24, names Steve Esponda. Official 2022 and 2026 general ballots use Stephen Esponda (3,456 and 3,165)."),
        _office("County Sheriff", holders("County Sheriff"),
                note="Official sheriff page, retrieved 2026-11-24, names Sheriff Rod Odenbach (official 2022 general, 3,309). Official 2026 general: Adrian Keeler 3,126, taking office January 2027."),
        _office("County Attorney", holders("County Attorney"),
                note="Official attorney page, retrieved 2026-11-24, names Tucker Ruby. Official 2022 and 2026 general ballots use Tucker J. Ruby (3,432 and 3,106)."),
        _office("Clerk of District Court", holders("Clerk of District Court"),
                note="Official CDC page, retrieved 2026-11-24, names Paige Rhoads. Official 2022 general 3,594; official 2026 general 3,288."),
        _office("County Coroner", holders("County Coroner"),
                note="Official coroner page, retrieved 2026-11-24, names Shawn Sullivan. Official 2022 and 2026 general ballots use Shawn M. Sullivan (3,479 and 3,291)."),
    ]
    municipal = [
        _office("City of Buffalo Mayor", holders("City of Buffalo Mayor"),
                note="Official City of Buffalo Mayor's Office page, retrieved 2026-11-24, names Mayor Shane J. Schrader. Official 2022 general: Shane J Schrader 1,097. Official 2026 general: Shane James Schrader 847, Bob Hancock 711."),
        _office("City of Buffalo Council", holders("City of Buffalo Council"),
                layout="heading-then-names",
                note="Official 2024 general (vote for 2): Wes Haskins 1,339 and Richard \"Scott\" Madsen 1,166, terms through January 2029. Official 2022 general (vote for 2): Myra Camino 1,135 and Mike Madden 769, terms through January 2027. Official 2026 general (vote for 2): Myra Camino 1,100 (re-elected) and Craig Rucki 595, taking office January 2027. Official city council page, retrieved 2026-11-24, lists Myra Camino, Wes Haskins, Mike Madden, and Scott Madsen."),
        _office("Town of Kaycee Mayor", holders("Town of Kaycee Mayor"),
                note="Official Town of Kaycee Town Council page, retrieved 2026-11-24: Tom Knapp, Mayor, Term: 2026–2030. Kaycee offices were not on the official November 2026 Johnson County general canvass."),
        _office("Town of Kaycee Council", holders("Town of Kaycee Council"),
                layout="heading-then-names",
                note="Official Town of Kaycee Town Council page, retrieved 2026-11-24: Pat Foster, Vice Mayor, Term: 2024–2028; Bob Furnival, Term: 2024–2028; Alvis Davis, Term: 2026–2030; Jennifer Lompe, Term: 2026–2030. Official page says those are four-year elective terms. Exact term-start days are not printed."),
    ]
    schools = [
        _office("Johnson County School District #1 Trustee", holders("Johnson County School District #1 Trustee"),
                layout="heading-then-names",
                note="Official ballot title School Board Trustee at Large. Official 2022 general (vote for 4, terms through January 2027): Marcia Goddard 2,100, Dave Belus 2,010, Casey Rodriguez 1,890, Travis D. Pearson 1,788. Official 2024 general (vote for 5, terms through January 2029): Lynette Fox 3,013, Daniel \"Noodle\" Escoz 2,800, Benito A Maya 2,698, McKenzi Wright 2,358, Reed Davidson 2,332. Official 2026 general (vote for 4, taking office January 2027): Travis D. Pearson 2,427, Bryan Bergstresser 2,144, Casey Curtright 2,133, Regg Hagge 2,048. Casey Curtright is not combined with Casey Rodriguez without an official identification. Official jcsd1.us board page is behind a JavaScript challenge and was not used."),
    ]
    specials = [
        _office("Cemetery District Trustee", holders("Cemetery District Trustee"),
                layout="heading-then-names",
                note="Official 2022, 2024, and 2026 Johnson general canvasses (vote for 3; plus a 2022 unexpired race)."),
        _office("Clear Creek Conservation District Rural", holders("Clear Creek Conservation District Rural"),
                layout="heading-then-names",
                note="Official 2022 (vote for 2), 2024 (vote for 1), and 2026 (vote for 2) Johnson general canvasses."),
        _office("Clear Creek Conservation District At Large", holders("Clear Creek Conservation District At Large"),
                note="Official 2022 general: Jay Foss 2,822. Official 2026 general: Jay Foss 1,191."),
        _office("Clear Creek Conservation District Urban", holders("Clear Creek Conservation District Urban"),
                note="Official 2024 general: Lara Schuman 3,474, term through January 2029."),
        _office("Powder River Conservation District Rural", holders("Powder River Conservation District Rural"),
                layout="heading-then-names",
                note="Official 2022, 2024, and 2026 Johnson general canvasses."),
        _office("Powder River Conservation District At Large", holders("Powder River Conservation District At Large"),
                note="Official 2022 and 2026 general canvasses name Kevin Lund."),
        _office("Powder River Conservation District Urban", holders("Powder River Conservation District Urban"),
                note="Official 2024 general: William Jones 443, term through January 2029."),
        _office("Johnson County Fire District #1 Trustee", holders("Johnson County Fire District #1 Trustee"),
                layout="heading-then-names",
                note="Official 2022 (vote for 2), official 2024 (4-year and 2-year seats), and official 2026 (vote for 2) Johnson general canvasses."),
        _office("Powder River Fire District Trustee", holders("Powder River Fire District Trustee"),
                layout="heading-then-names",
                note="Official 2022, 2024 (4-year and 2-year seats), and official 2026 canvasses. Official 2026 names Matt Carr 207 and certified write-in Bryce Perry 102."),
        _office("Hospital District Trustee", holders("Hospital District Trustee"),
                layout="heading-then-names",
                note="Official 2022 (vote for 3), 2024 (vote for 2), and 2026 (vote for 3) Johnson general canvasses."),
        _office("Rural Health Care District Trustee", holders("Rural Health Care District Trustee"),
                layout="heading-then-names",
                note="Official 2022 (vote for 3), 2024 (vote for 2), and 2026 (vote for 3) Johnson general canvasses."),
        _office("Senior Citizen Service District Trustee", holders("Senior Citizen Service District Trustee"),
                layout="heading-then-names",
                note="Official 2022 (vote for 3), official 2024 (4-year vote for 2, with only Vicki Edelman named, and a 2-year seat), official 2026 (vote for 3 plus an unexpired seat won by Kay Nation 2,703)."),
    ]
    judicial = [
        _office("District Judge, 4th Judicial District",
                holders("District Judge, 4th Judicial District"),
                layout="heading-then-names",
                note="Official 2024 Johnson general: RETAIN JUDGE A DARCI A. V. PHILLIPS, YES 3,289 / NO 680; RETAIN JUDGE B BENJAMIN KIRVEN, YES 3,519 / NO 781."),
        _office("Circuit Judge, 4th Judicial District",
                holders("Circuit Judge, 4th Judicial District"),
                note="Official 2022 Johnson general retained FOURTH JUDICIAL DIST CIRCUIT COURT JUDGE CUNDIFF, YES 2,399 / NO 976. Official 2026 general, RETAIN JUDGE BEN BURNINGHAM, YES 2,398 / NO 568 (the official 2026 line does not itself say circuit). Burningham takes the next ordinary cycle in January 2027."),
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
        "general_results": "https://drive.google.com/file/d/1QrzYmvHr9euYlYbndXbkDZN5RlI0lcYf/view",
        "clerk_archive": URL_ELECTIONS,
        "checked": RETRIEVED,
        "local_archive": "/workspace/wyoleg/local-results/johnson/SOURCES.md",
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("updated", path)
    return path
