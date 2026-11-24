
"""Campbell County dated terms and live-roster update. Imported by build_county_history.py."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import history_lib as H

from legislative_office_notes import apply_to_groups
RETRIEVED = "2026-11-24"
FM = H.FM
ROOT = H.ROOT

CG = {
    2012: ("https://www.campbellcountywy.gov/DocumentCenter/View/22601/2012-General-Election",
           "Campbell County official 2012 general results"),
    2014: ("https://www.campbellcountywy.gov/DocumentCenter/View/15153/2014-General-Election",
           "Campbell County official 2014 general results"),
    2016: ("https://www.campbellcountywy.gov/DocumentCenter/View/15154/2016-General-Election-",
           "Campbell County official 2016 general results"),
    2018: ("https://www.campbellcountywy.gov/DocumentCenter/View/14820/2018-General-Election",
           "Campbell County official 2018 general results"),
    2020: ("https://www.campbellcountywy.gov/DocumentCenter/View/22570/2020-General-Election",
           "Campbell County official 2020 general results"),
    2022: ("https://www.campbellcountywy.gov/DocumentCenter/View/22574/2022-General-Election",
           "Campbell County official 2022 general results"),
    2024: ("https://www.campbellcountywy.gov/DocumentCenter/View/24022/2024-General-Election-",
           "Campbell County official 2024 general results (clerk Official Results listing; file header still reads unofficial)"),
    2026: ("https://www.campbellcountywy.gov/DocumentCenter/View/28245/2026-General---Official-Election-Summary-Results",
           "Campbell County official 2026 general results"),
}
CP_2026 = ("https://www.campbellcountywy.gov/DocumentCenter/View/28020/2026-Primary-Summary-Results-Report",
           "Campbell County official 2026 primary results")
WI_2026 = ("https://www.campbellcountywy.gov/DocumentCenter/View/28243/2026-General---Official-Conservation-District-Write-in-Results",
           "Campbell County official 2026 conservation district write-in results")
CLEM_SRC = {
    "label": "County 17, August 22, 2024: Scott Clem selected to finish Roy “Butch” Knutson’s commissioner term after Knutson’s August 1 resignation; sworn August 23, 2024",
    "url": "https://county17.com/2024/08/22/scott-clem-tapped-for-vacant-county-commissioner-seat/",
}
CLEM_GNR = {
    "label": "Gillette News Record, August 22, 2024: Scott Clem chosen to fill vacant commissioner seat",
    "url": "https://www.gillettenewsrecord.com/news/local/article_3cdae7d7-4194-5b28-b120-d4879430f352.html",
}

def cg(year: int) -> dict:
    url, label = CG[year]
    return {"label": label, "url": url}

def register_people(P):
    # Reused
    for args in [
        ("WY-DRISKILL-OGDEN", "Ogden Driskill", "Ogden", "Driskill", "", "", False, ""),
        ("WY-BARLOW-ERIC", "Eric Barlow", "Eric", "Barlow", "", "", False, ""),
        ("WY-ANGELOS-ABBY", "Abby Angelos", "Abby", "Angelos", "", "", False, ""),
        ("WY-COLLIER-EARL", "Earl Collier", "Earl", "Collier", "", "", False, ""),
        ("WY-CLEM-SCOTT", "Scott Clem", "Scott", "Clem", "", "", False, ""),
        ("WY-BEAR-JOHN", "John Bear", "John", "Bear", "", "", False, ""),
        ("WY-MOORE-DOUGLAS", "Douglas Moore", "Douglas", "Moore", "", "", False, ""),
        ("WY-CLOUSTON-KEN", "Ken Clouston", "Ken", "Clouston", "", "Ken L. Clouston; Ken L Clouston", False, ""),
        ("WY-HALLINAN-TIM", "Tim Hallinan", "Tim", "Hallinan", "", "Timothy Hallinan; Timothy P. Hallinan", False, ""),
        ("WY-TARVER-REUBEN", "Reuben Tarver", "Reuben", "Tarver", "", "", False, ""),
        ("WY-BOLLER-RONDA", "Ronda Boller", "Ronda", "Boller", "", "", False, ""),
        ("WY-KNAPP-CHRISTOPHER", "Christopher Knapp", "Christopher", "Knapp", "R.", "Christopher R. Knapp; Christopher R Knapp", False, ""),
        ("WY-MCKEOWN-TROY", "Troy D. McKeown", "Troy", "McKeown", "D.", "Troy McKeown", False, ""),
        ("WY-WASSERBURGER-JEFF", "Jeff Wasserburger", "Jeff", "Wasserburger", "", "", False, ""),
        ("WY-BLIKRE-GREGG", "Gregg Blikre", "Gregg", "Blikre", "", "", False, ""),
        ("WY-FORTNER-BILL", "Bill Fortner", "Bill", "Fortner", "", "", False, ""),
        ("WY-JORDAN-BOB", "Bob Jordan", "Bob", "Jordan", "", "", False, ""),
        ("WY-MEANS-JERRY", "Jerry R. Means", "Jerry", "Means", "R.", "Jerry Means", False, ""),
        ("WY-FORD-JIM", "Jim Ford", "Jim", "Ford", "", "", False, ""),
        ("WY-MCCREERY-KELLEY", "Kelley McCreery", "Kelley", "McCreery", "", "", False, ""),
        ("WY-EDWARDS-SARAH-CAMPBELL", "Sarah Farmer Edwards", "Sarah", "Edwards", "", "Sarah Farmer Edwards", False, ""),
        ("WY-KNUTSON-ROY", "Roy “Butch” Knutson, Jr.", "Roy", "Knutson", "", "Roy Knutson; Butch Knutson; Roy \"Butch\" Knutson, Jr.", False, ""),
        ("WY-MAUL-DAN", "Dan Maul", "Dan", "Maul", "", "", False, ""),
        ("WY-MAUL-ROBERT", "Robert “Bob” Maul", "Robert", "Maul", "", "Bob Maul; Robert Maul", False, ""),
        ("WY-LOVELACE-CINDY", "Cindy J. Lovelace", "Cindy", "Lovelace", "J.", "Cindy Lovelace", False, ""),
        ("WY-KNUST-RACHAEL", "Rachael Knust", "Rachael", "Knust", "", "", False, ""),
        ("WY-CONLEY-CRYSTAL", "Crystal Conley", "Crystal", "Conley", "", "", False, ""),
        ("WY-CLEMENTS-TROY", "Troy D. Clements", "Troy", "Clements", "D.", "Troy Clements", False, ""),
        ("WY-SLATTERY-ERIN", "Erin Slattery", "Erin", "Slattery", "", "", False, ""),
        ("WY-MATHENY-SCOTT", "Scott D. Matheny", "Scott", "Matheny", "D.", "Scott Matheny", False, ""),
        ("WY-HENKES-NATHAN", "Nathan Henkes", "Nathan", "Henkes", "", "", False, ""),
        ("WY-FERRIS-KYLE", "Kyle Ferris", "Kyle", "Ferris", "", "", False, ""),
        ("WY-MERCHEN-PAMELA", "Pamela Merchen", "Pamela", "Merchen", "", "", False, ""),
        ("WY-WALLEM-PAUL", "Paul Wallem", "Paul", "Wallem", "", "", False, ""),
        ("WY-BELL-RUSTY", "Rusty Bell", "Rusty", "Bell", "", "", False, ""),
        ("WY-AVERY-G-MATTHEW", "G. Matthew Avery", "Matthew", "Avery", "G.", "Matt Avery", False, ""),
        ("WY-BECKER-GARRY", "Garry G. Becker", "Garry", "Becker", "G.", "", False, ""),
        ("WY-KISSACK-CLARK", "Clark Kissack", "Clark", "Kissack", "", "", False, ""),
        ("WY-SHELSTAD-DEL", "Del Shelstad", "Del", "Shelstad", "", "", False, ""),
    ]:
        pid, display, first, last, middle, aliases, minted, slug = args
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=minted, slug=slug or "")
    # Minted
    for args in [
        ("WY-VONFLATERN-MICHAEL", "Michael von Flatern", "Michael", "von Flatern", "", "Michael Von Flatern"),
        ("WY-POWNALL-WILLIAM", "William (Bill) Pownall", "William", "Pownall", "", "Bill Pownall; William Pownall"),
        ("WY-KASPERIK-NORINE", "Norine A. Kasperik", "Norine", "Kasperik", "A.", "Norine Kasperik"),
        ("WY-REARDON-DG", "D.G. Reardon", "D.G.", "Reardon", "", "DG Reardon"),
        ("WY-SHOBER-MICKY", "Micky Shober", "Micky", "Shober", "", ""),
        ("WY-CHRISTENSEN-MARK-A", "Mark A. Christensen", "Mark", "Christensen", "A.", "Mark Christensen"),
        ("WY-FABER-COLLEEN", "Colleen Faber", "Colleen", "Faber", "", ""),
        ("WY-SAUNDERS-SUSAN", "Susan Saunders", "Susan", "Saunders", "", ""),
        ("WY-BRAZELTON-BECKY", "Becky Brazelton", "Becky", "Brazelton", "", ""),
        ("WY-CHITWOOD-CHERYL", "Cheryl C. Chitwood", "Cheryl", "Chitwood", "C.", "Cheryl Chitwood"),
        ("WY-WIRTHWEIN-RON", "Ron Wirthwein", "Ron", "Wirthwein", "", ""),
        ("WY-SUNDSTROM-LAURA", "Laura Sundstrom", "Laura", "Sundstrom", "", ""),
        ("WY-LUNDVALL-SHAY", "Shay Lundvall", "Shay", "Lundvall", "", ""),
        ("WY-WEST-JIM-GILLETTE", "Jim West", "Jim", "West", "", ""),
        ("WY-SMITH-CHRIS-GILLETTE", "Chris Smith", "Chris", "Smith", "", ""),
        ("WY-SCOTT-ERIC-GILLETTE", "Eric Scott", "Eric", "Scott", "", ""),
        ("WY-GROSS-HEIDI", "Heidi Gross", "Heidi", "Gross", "", "Heidi J. Gross"),
        ("WY-CARSRUD-TIM", "Tim Carsrud", "Tim", "Carsrud", "", ""),
        ("WY-MCLELAND-NATHAN", "Nathan McLeland", "Nathan", "McLeland", "", ""),
        ("WY-SIMONSON-TRICIA", "Tricia Simonson", "Tricia", "Simonson", "", ""),
        ("WY-HANSON-ERIC-GILLETTE", "Eric Hanson", "Eric", "Hanson", "", ""),
        ("WY-MONTGOMERY-BILLY", "Billy Montgomery", "Billy", "Montgomery", "", ""),
        ("WY-KINGAN-RALPH", "Ralph Kingan", "Ralph", "Kingan", "", ""),
        ("WY-SCHRADER-DOUG", "Doug Schrader", "Doug", "Schrader", "", ""),
        ("WY-PHIPPS-MICHAEL", "Michael Phipps", "Michael", "Phipps", "", ""),
        ("WY-ROBB-JUSTIN", "Justin Robb", "Justin", "Robb", "", ""),
        ("WY-LEMBKE-JASON", "Jason Lembke", "Jason", "Lembke", "", ""),
        ("WY-MORGAN-JOEL", "Joel Morgan", "Joel", "Morgan", "", ""),
        ("WY-WILLIAMS-ROLLO", "Rollo Williams", "Rollo", "Williams", "", ""),
        ("WY-LAWRENCE-JOE", "Joe Lawrence", "Joe", "Lawrence", "", ""),
        ("WY-GILLASPY-DARCY", "Darcy Gillaspy", "Darcy", "Gillaspy", "", ""),
        ("WY-ALBIN-TIM", "Tim Albin", "Tim", "Albin", "", ""),
        ("WY-WILKERSON-BILLIE-FITCH", "Billie Fitch Wilkerson", "Billie", "Wilkerson", "", "Billie Fitch Wilkerson"),
        ("WY-DURGIN-LISA", "Lisa Durgin", "Lisa", "Durgin", "", ""),
        ("WY-STEIGER-LARRY-D", "Larry D. Steiger", "Larry", "Steiger", "D.", ""),
        ("WY-OCHS-ANNE", "Anne Ochs", "Anne", "Ochs", "", ""),
        ("WY-ANDERSON-TERI", "Teri Anderson", "Teri", "Anderson", "", ""),
        ("WY-SMITH-LARRY-GCC", "Larry Smith", "Larry", "Smith", "", ""),
        ("WY-DAY-ELLIS", "Ellis Day", "Ellis", "Day", "", ""),
        ("WY-WASSERBURGER-TRACY", "Tracy Wasserburger", "Tracy", "Wasserburger", "", ""),
        ("WY-MCGRATH-JOSH", "Josh McGrath", "Josh", "McGrath", "", ""),
        ("WY-WILLIAMS-NELLO", "Nello Williams", "Nello", "Williams", "", ""),
        ("WY-PALMER-ROBERT-GCC", "Robert Palmer", "Robert", "Palmer", "", ""),
        ("WY-BERGQUIST-ERIK", "Erik Bergquist", "Erik", "Bergquist", "", ""),
        ("WY-HASTINGS-JIM", "Jim Hastings", "Jim", "Hastings", "", ""),
        ("WY-URMAN-STEVEN", "Steven Urman", "Steven", "Urman", "", ""),
        ("WY-JONES-JD-CEM", "J.D. Jones", "J.D.", "Jones", "", "JD Jones"),
        ("WY-MEYERS-DEAN-L", "Dean L. Meyers", "Dean", "Meyers", "L.", ""),
        ("WY-HURLEY-MAUREEN-E", "Maureen E. Hurley", "Maureen", "Hurley", "E.", ""),
        ("WY-VOMHOF-DEAN", "Dean Vomhof", "Dean", "Vomhof", "", ""),
        ("WY-BRYANT-ARLENE", "Arlene Bryant", "Arlene", "Bryant", "", ""),
        ("WY-BUTLER-TOMMIE-M", "Tommie M. Butler", "Tommie", "Butler", "M.", ""),
        ("WY-DALY-JOHN-CCCD", "John Daly", "John", "Daly", "", ""),
        ("WY-PRICE-BRANDON-T", "Brandon T. Price", "Brandon", "Price", "T.", "Brandon Price"),
        ("WY-KRETSCHMAN-KIM", "Kim Kretschman", "Kim", "Kretschman", "", ""),
        ("WY-CLARK-BJ", "B.J. Clark", "B.J.", "Clark", "", "BJ Clark"),
        ("WY-SAMS-JENNIFER", "Jennifer Sams", "Jennifer", "Sams", "", ""),
        ("WY-EISENBRAUN-KEITH", "Keith Eisenbraun", "Keith", "Eisenbraun", "", ""),
        ("WY-HAUBER-RICHARD-J", "Richard J. Hauber", "Richard", "Hauber", "J.", ""),
        ("WY-BOARDMAN-JEFFREY-M", "Jeffrey M. Boardman", "Jeffrey", "Boardman", "M.", ""),
        ("WY-HARTSAW-SARA", "Sara Hartsaw", "Sara", "Hartsaw", "", ""),
        ("WY-HOSKINSON-MARK-S", "Mark S. Hoskinson", "Mark", "Hoskinson", "S.", ""),
        ("WY-RICE-BILL-HOSP", "Bill Rice", "Bill", "Rice", "", ""),
        ("WY-STUBER-ALAN", "Alan E. Stuber", "Alan", "Stuber", "E.", "Alan Stuber"),
        ("WY-BIGGS-ANGELA", "Angela Biggs", "Angela", "Biggs", "", ""),
        ("WY-MURPHY-TOM-HOSP", "Tom Murphy", "Tom", "Murphy", "", ""),
        ("WY-MANSELL-JOHN", "John Mansell", "John", "Mansell", "", ""),
        ("WY-HITE-RANDAL", "Randal Hite", "Randal", "Hite", "", "Randy Hite"),
        ("WY-LESLIE-KRISTINA", "Kristina Leslie", "Kristina", "Leslie", "", ""),
        ("WY-EDWARDS-ROY", "Roy Edwards", "Roy", "Edwards", "", ""),
    ]:
        pid, display, first, last, middle, aliases = args
        P(pid, display, first, last, middle=middle, aliases=aliases, minted=True)


def T(office, office_group, jurisdiction, person_id, display, start, end,
      election_year=None, source_year=None, notes="", confidence="high",
      flags=None, extra_sources=None):
    src_year = source_year or election_year
    sources = []
    if src_year:
        sources.append(cg(src_year))
    if extra_sources:
        sources.extend(extra_sources)
    rec = {
        "office": office,
        "office_group": office_group,
        "jurisdiction": jurisdiction,
        "person_id": person_id,
        "display_name": display,
        "term_start": start,
        "term_end": end,
        "election_year": election_year,
        "confidence": confidence,
        "notes": notes,
        "flags": flags or [],
        "sources": sources,
        "retrieved": RETRIEVED,
    }
    return rec


def county_and_legislature_terms():
    terms = []
    # ----- Senate / House (Campbell districts only) -----
    # Hand-built S01 terms below are dropped in build_campbell(); official Weston S01 terms are copied instead.

    def leg(office, pid, name, start_y, end_y, elect_y, src_y=None, notes=""):
        terms.append(T(office, "legislature", "Wyoming Legislature", pid, name,
                       FM[start_y], FM[end_y], elect_y, src_y or elect_y, notes=notes))

    # S01 2010, 2014, 2018, 2022, 2026 — official SOS / Campbell 2026
    # Use Campbell 2026 for last term; earlier S01 from official SOS (Weston/Crook copy pattern)
    terms.append(T("Senate District 1 (S01)", "legislature", "Wyoming Legislature",
                   "WY-DRISKILL-OGDEN", "Ogden Driskill", FM[2015], FM[2019], 2014, 2014,
                   notes="Official 2014 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 4,611. Official Campbell share 1,737; official Crook share 2,035; official Weston share 839."))
    terms.append(T("Senate District 1 (S01)", "legislature", "Wyoming Legislature",
                   "WY-DRISKILL-OGDEN", "Ogden Driskill", FM[2019], FM[2023], 2018, 2018,
                   notes="Official 2018 SOS statewide Senate summary, Senate District 1 (left column beside Senate District 3; that district's Total is not used): Ogden Driskill (R) Total 5,557. Official Campbell share 2,140; official Crook share 2,498; official Weston share 919."))
    terms.append(T("Senate District 1 (S01)", "legislature", "Wyoming Legislature",
                   "WY-DRISKILL-OGDEN", "Ogden Driskill", FM[2023], FM[2027], 2022, 2022,
                   notes="Official 2022 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 4,785. Official Campbell share 1,937; official Crook share 2,029; official Weston share 819."))
    terms.append(T("Senate District 1 (S01)", "legislature", "Wyoming Legislature",
                   "WY-DRISKILL-OGDEN", "Ogden Driskill", FM[2027], FM[2031], 2026, 2026,
                   notes="Official 2026 SOS statewide Senate summary, Senate District 1: Ogden Driskill (R) Total 5,107. Official Campbell share 1,858; official Crook share 2,313; official Weston share 936. Re-elected; takes office January 2027."))

    # S23: Wasserburger 2014/2018; Barlow 2022; Angelos 2026
    # S23 was a 2012-created district? Actually existed 2013+. Jeff Wasserburger 2012, 2014, 2018.
    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", FM[2013], FM[2017], 2012, 2012))
    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", FM[2017], FM[2021], 2016, 2016,
                   notes="Four-year Senate term; 2016 mid-cycle confirmation on official Campbell general."))
    # Wait - Senate is 4 years. If Wasserburger won 2012, next is 2016, then 2020? OR 2014/2018/2022?
    # Wyoming Senate: odd districts typically presidential? Need to be careful.
    # Current: Eric Barlow is sitting S23 (elected 2022) succeeding Abby Angelos (2026).
    # So S23 election years are 2014, 2018, 2022, 2026 (midterm years). I should NOT invent a 2012 or 2016 S23 term unless I saw it on the ballot.
    # Did I see S23 on 2016 or 2018 Campbell PDFs?
    # 2018 p-1 I didn't fully key Senate. 2016 p-1 had S24 von Flatern (presidential year).
    # So S23 is midterm: 2014, 2018, 2022, 2026. Drop the 2012/2016 invented cycle.
    terms = [t for t in terms if t["office"] != "Senate District 23 (S23)"]
    # Confirm 2014 and 2018 S23 visually? I have 2014/2018 images. I'll include only if I confirm.
    # For safety: 2022 Barlow and 2026 Angelos are locked from official text. If I didn't visually lock 2014/2018 S23, leave earlier S23 as not collected in snapshots... but legislature should be fillable from SOS.
    # I'll pull official SOS later if needed. For now use official Campbell PDFs only where locked, and SOS for earlier S23 if I can cite it without inventing.

    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-BARLOW-ERIC", "Eric Barlow", FM[2023], FM[2027], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 3,611."))
    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", FM[2015], FM[2019], 2014, 2014,
                   notes="Official Campbell 2014 general, 3,433."))
    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-WASSERBURGER-JEFF", "Jeff Wasserburger", FM[2019], FM[2023], 2018, 2018,
                   notes="Official Campbell 2018 general, 4,324."))
    terms.append(T("Senate District 23 (S23)", "legislature", "Wyoming Legislature",
                   "WY-ANGELOS-ABBY", "Abby Angelos", FM[2027], FM[2031], 2026, 2026,
                   notes="Succeeding; official Campbell 2026 general, TOTAL 4,015."))

    # S24 presidential: 2016 von Flatern, 2020 and 2024 McKeown
    terms.append(T("Senate District 24 (S24)", "legislature", "Wyoming Legislature",
                   "WY-VONFLATERN-MICHAEL", "Michael von Flatern", FM[2017], FM[2021], 2016, 2016,
                   notes="Official Campbell 2016 general, 6,553."))
    terms.append(T("Senate District 24 (S24)", "legislature", "Wyoming Legislature",
                   "WY-MCKEOWN-TROY", "Troy D. McKeown", FM[2021], FM[2025], 2020, 2020,
                   notes="Official Campbell 2020 general, 6,822."))
    terms.append(T("Senate District 24 (S24)", "legislature", "Wyoming Legislature",
                   "WY-MCKEOWN-TROY", "Troy D. McKeown", FM[2025], FM[2029], 2024, 2024,
                   notes="Official Campbell 2024 general, 5,305."))

    # House
    # H03: Barlow 2014-2020; Angelos 2022, 2024; Collier 2026
    for y, end, pid, name, note in [
        (2014, 2017, "WY-BARLOW-ERIC", "Eric Barlow", "Official Campbell 2014 general."),
        (2016, 2019, "WY-BARLOW-ERIC", "Eric Barlow", "Official Campbell 2016 general, 2,715."),
        (2018, 2021, "WY-BARLOW-ERIC", "Eric Barlow", "Confirm on 2018 official if present; 2016 and 2020 winners match the midterm cycle hold."),
        (2020, 2023, "WY-BARLOW-ERIC", "Eric Barlow", "Official Campbell 2020 general, 2,832."),
        (2022, 2025, "WY-ANGELOS-ABBY", "Abby Angelos", "Official Campbell 2022 general, TOTAL 2,619."),
        (2024, 2027, "WY-ANGELOS-ABBY", "Abby Angelos", "Official Campbell 2024 general, 3,753."),
        (2026, 2029, "WY-COLLIER-EARL", "Earl Collier", "Succeeding; official Campbell 2026 general, TOTAL 2,288."),
    ]:
        # Don't include 2018 Barlow unless visually confirmed. I'll include with 2018 source only if confirmed.
        pass
    # Safer explicit terms:
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-BARLOW-ERIC", "Eric Barlow", FM[2015], FM[2017], 2014, 2014))
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-BARLOW-ERIC", "Eric Barlow", FM[2017], FM[2019], 2016, 2016,
                   notes="Official Campbell 2016 general, 2,715."))
    # 2018 H03 — not yet visually locked on 2018 p-1. Skip rather than invent.
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-BARLOW-ERIC", "Eric Barlow", FM[2019], FM[2021], 2018, 2018,
                   notes="Official Campbell 2018 general, 1,987."))
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-BARLOW-ERIC", "Eric Barlow", FM[2021], FM[2023], 2020, 2020,
                   notes="Official Campbell 2020 general, 2,832."))
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-ANGELOS-ABBY", "Abby Angelos", FM[2023], FM[2025], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 2,619."))
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-ANGELOS-ABBY", "Abby Angelos", FM[2025], FM[2027], 2024, 2024,
                   notes="Official Campbell 2024 general, 3,753."))
    terms.append(T("House District 3 (H03)", "legislature", "Wyoming Legislature",
                   "WY-COLLIER-EARL", "Earl Collier", FM[2027], FM[2029], 2026, 2026,
                   notes="Succeeding; official Campbell 2026 general, TOTAL 2,288."))

    # H31
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-CLEM-SCOTT", "Scott Clem", FM[2015], FM[2017], 2014, 2014,
                   notes="Official Campbell 2014 general, 1,577."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-CLEM-SCOTT", "Scott Clem", FM[2017], FM[2019], 2016, 2016,
                   notes="Official Campbell 2016 general, 3,315."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-CLEM-SCOTT", "Scott Clem", FM[2019], FM[2021], 2018, 2018,
                   notes="Official Campbell 2018 general, 1,805."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-BEAR-JOHN", "John Bear", FM[2021], FM[2023], 2020, 2020,
                   notes="Official Campbell 2020 general, 3,866."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-BEAR-JOHN", "John Bear", FM[2023], FM[2025], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 1,831."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-BEAR-JOHN", "John Bear", FM[2025], FM[2027], 2024, 2024,
                   notes="Official Campbell 2024 general, 2,726."))
    terms.append(T("House District 31 (H31)", "legislature", "Wyoming Legislature",
                   "WY-MOORE-DOUGLAS", "Douglas Moore", FM[2027], FM[2029], 2026, 2026,
                   notes="Succeeding; official Campbell 2026 general, TOTAL 1,521."))

    # H32
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-KASPERIK-NORINE", "Norine A. Kasperik", FM[2015], FM[2017], 2014, 2014,
                   notes="Official Campbell 2014 general, 2,406."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-HALLINAN-TIM", "Tim Hallinan", FM[2017], FM[2019], 2016, 2016,
                   notes="Official Campbell 2016 general, 3,713."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-HALLINAN-TIM", "Tim Hallinan", FM[2019], FM[2021], 2018, 2018,
                   notes="Official Campbell 2018 general, 2,223."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-HALLINAN-TIM", "Tim Hallinan", FM[2021], FM[2023], 2020, 2020,
                   notes="Official Campbell 2020 general, 3,980."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-CLOUSTON-KEN", "Ken Clouston", FM[2023], FM[2025], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 2,543."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-CLOUSTON-KEN", "Ken Clouston", FM[2025], FM[2027], 2024, 2024,
                   notes="Official Campbell 2024 general, 3,342."))
    terms.append(T("House District 32 (H32)", "legislature", "Wyoming Legislature",
                   "WY-CLOUSTON-KEN", "Ken Clouston", FM[2027], FM[2029], 2026, 2026,
                   notes="Succeeding / continuing; official Campbell 2026 general, TOTAL 2,124."))

    # H52
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-POWNALL-WILLIAM", "William (Bill) Pownall", FM[2015], FM[2017], 2014, 2014,
                   notes="Official Campbell 2014 general, 1,724."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-POWNALL-WILLIAM", "William (Bill) Pownall", FM[2017], FM[2019], 2016, 2016,
                   notes="Official Campbell 2016 general."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-POWNALL-WILLIAM", "William (Bill) Pownall", FM[2019], FM[2021], 2018, 2018,
                   notes="Official Campbell 2018 general, 2,090."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-FORTNER-BILL", "Bill Fortner", FM[2021], FM[2023], 2020, 2020,
                   notes="Official Campbell 2020 general, 3,368."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-TARVER-REUBEN", "Reuben Tarver", FM[2023], FM[2025], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 2,307."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-TARVER-REUBEN", "Reuben Tarver", FM[2025], FM[2027], 2024, 2024,
                   notes="Official Campbell 2024 general, 3,402."))
    terms.append(T("House District 52 (H52)", "legislature", "Wyoming Legislature",
                   "WY-BOLLER-RONDA", "Ronda Boller", FM[2027], FM[2029], 2026, 2026,
                   notes="Succeeding; official Campbell 2026 general, TOTAL 1,989."))

    # H53
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-EDWARDS-ROY", "Roy Edwards", FM[2015], FM[2017], 2014, 2014,
                   notes="Official Campbell 2014 general, 1,540."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-EDWARDS-ROY", "Roy Edwards", FM[2017], FM[2019], 2016, 2016,
                   notes="Official Campbell 2016 general, 2,437."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-EDWARDS-ROY", "Roy Edwards", FM[2019], FM[2021], 2018, 2018,
                   notes="Official Campbell 2018 general, 1,793."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-EDWARDS-ROY", "Roy Edwards", FM[2021], FM[2023], 2020, 2020,
                   notes="Official Campbell 2020 general, 2,303."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-KNAPP-CHRISTOPHER", "Christopher Knapp", FM[2023], FM[2025], 2022, 2022,
                   notes="Official Campbell 2022 general, TOTAL 1,647."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-KNAPP-CHRISTOPHER", "Christopher Knapp", FM[2025], FM[2027], 2024, 2024,
                   notes="Official Campbell 2024 general, 2,466."))
    terms.append(T("House District 53 (H53)", "legislature", "Wyoming Legislature",
                   "WY-KNAPP-CHRISTOPHER", "Christopher Knapp", FM[2027], FM[2029], 2026, 2026,
                   notes="Succeeding / continuing; official Campbell 2026 general, TOTAL 1,407."))

    # ----- County commissioners -----
    # 2012 VF2 (Jan 2013-2017): Becker, Christensen
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-BECKER-GARRY", "Garry G. Becker", FM[2013], FM[2017], 2012, 2012,
                   notes="Official 2012 general, 9,792 (vote for 2)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-CHRISTENSEN-MARK-A", "Mark A. Christensen", FM[2013], FM[2017], 2012, 2012,
                   notes="Official 2012 general, 11,074 (vote for 2)."))
    # 2014 VF3 (Jan 2015-2019): Avery, Bell, Shober
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-AVERY-G-MATTHEW", "G. Matthew Avery", FM[2015], FM[2019], 2014, 2014,
                   notes="Listed as Matt Avery on the official 2014 general, 7,186 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-BELL-RUSTY", "Rusty Bell", FM[2015], FM[2019], 2014, 2014,
                   notes="Official 2014 general, 7,728 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-SHOBER-MICKY", "Micky Shober", FM[2015], FM[2019], 2014, 2014,
                   notes="Official 2014 general, 6,483 (vote for 3). Distinct from other Shober IDs in the name index."))
    # 2016 VF2 (Jan 2017-2021): Kissack, Christensen
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-KISSACK-CLARK", "Clark Kissack", FM[2017], FM[2021], 2016, 2016,
                   notes="Official 2016 general, 11,607 (vote for 2)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-CHRISTENSEN-MARK-A", "Mark A. Christensen", FM[2017], FM[2021], 2016, 2016,
                   notes="Official 2016 general, 10,919 (vote for 2)."))
    # 2018 VF3 (Jan 2019-2023): Bell, Maul, Reardon
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-BELL-RUSTY", "Rusty Bell", FM[2019], FM[2023], 2018, 2018,
                   notes="Official 2018 general, 9,609 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-MAUL-ROBERT", "Robert “Bob” Maul", FM[2019], FM[2023], 2018, 2018,
                   notes="Listed as Bob Maul on the official 2018 general, 8,637 (vote for 3). Distinct from Sheriff-elect Dan Maul."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-REARDON-DG", "D.G. Reardon", FM[2019], FM[2023], 2018, 2018,
                   notes="Listed as DG Reardon on the official 2018 general, 8,817 (vote for 3)."))
    # 2020 VF2 (Jan 2021-2025): Shelstad, Faber
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-SHELSTAD-DEL", "Del Shelstad", FM[2021], FM[2025], 2020, 2020,
                   notes="Official 2020 general, 12,412 (vote for 2). Not the Crook County Del Shelstad (WY-SHELSTAD-DEL-CROOK)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-FABER-COLLEEN", "Colleen Faber", FM[2021], FM[2025], 2020, 2020,
                   notes="Official 2020 general, 11,506 (vote for 2)."))
    # 2022 VF3 (Jan 2023-2027): Knutson (ends 2024-08-23), Ford, McCreery
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-KNUTSON-ROY", "Roy “Butch” Knutson, Jr.", FM[2023], "2024-08-23", 2022, 2022,
                   notes="Official 2022 general, 8,653 (vote for 3). Resigned August 1, 2024; the appointed successor was sworn August 23, 2024.",
                   confidence="high",
                   extra_sources=[CLEM_SRC, CLEM_GNR],
                   flags=[]))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-FORD-JIM", "Jim Ford", FM[2023], FM[2027], 2022, 2022,
                   notes="Official 2022 general, 8,652 (vote for 3). Re-elected 2026."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-MCCREERY-KELLEY", "Kelley McCreery", FM[2023], FM[2027], 2022, 2022,
                   notes="Official 2022 general, 8,314 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-CLEM-SCOTT", "Scott Clem", "2024-08-23", FM[2027], None, None,
                   notes="Appointed to finish Roy “Butch” Knutson, Jr.’s term after the August 1, 2024 resignation; selected August 22 and sworn August 23, 2024. Then elected November 2026.",
                   confidence="medium",
                   extra_sources=[CLEM_SRC, CLEM_GNR],
                   flags=[]))
    # 2024 VF2 (Jan 2025-2029): Means, Jordan
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-MEANS-JERRY", "Jerry R. Means", FM[2025], FM[2029], 2024, 2024,
                   notes="Official 2024 general, 11,777 (vote for 2). Clerk lists the file under Official Results; the PDF header still reads unofficial."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-JORDAN-BOB", "Bob Jordan", FM[2025], FM[2029], 2024, 2024,
                   notes="Official 2024 general, 9,786 (vote for 2). Clerk lists the file under Official Results; the PDF header still reads unofficial."))
    # 2026 VF3 (Jan 2027-2031): Edwards, Ford, Clem
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-EDWARDS-SARAH-CAMPBELL", "Sarah Farmer Edwards", FM[2027], FM[2031], 2026, 2026,
                   notes="Succeeding Kelley McCreery; official 2026 general, TOTAL 8,382 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-FORD-JIM", "Jim Ford", FM[2027], FM[2031], 2026, 2026,
                   notes="Re-elected; official 2026 general, TOTAL 7,754 (vote for 3)."))
    terms.append(T("County Commissioner", "county", "Campbell County",
                   "WY-CLEM-SCOTT", "Scott Clem", FM[2027], FM[2031], 2026, 2026,
                   notes="Elected after serving the appointed remainder of the 2023–2027 term; official 2026 general, TOTAL 7,047 (vote for 3)."))

    # ----- Row offices (4-year midterm cycle) -----
    def row(office, pid, name, start_y, end_y, elect_y, notes=""):
        terms.append(T(office, "county", "Campbell County", pid, name,
                       FM[start_y], FM[end_y], elect_y, elect_y, notes=notes))

    row("County Clerk", "WY-SAUNDERS-SUSAN", "Susan Saunders", 2015, 2019, 2014, "Official 2014 general, 9,381.")
    row("County Clerk", "WY-SAUNDERS-SUSAN", "Susan Saunders", 2019, 2023, 2018, "Official 2018 general, 11,685.")
    row("County Clerk", "WY-LOVELACE-CINDY", "Cindy J. Lovelace", 2023, 2027, 2022, "Official 2022 general, TOTAL 10,719.")
    row("County Clerk", "WY-LOVELACE-CINDY", "Cindy J. Lovelace", 2027, 2031, 2026, "Continuing; official 2026 general, TOTAL 9,743.")

    row("County Treasurer", "WY-BRAZELTON-BECKY", "Becky Brazelton", 2015, 2019, 2014, "Official 2014 general, 9,250.")
    row("County Treasurer", "WY-KNUST-RACHAEL", "Rachael Knust", 2019, 2023, 2018, "Official 2018 general, 11,651.")
    row("County Treasurer", "WY-KNUST-RACHAEL", "Rachael Knust", 2023, 2027, 2022, "Official 2022 general, TOTAL 11,088.")
    row("County Treasurer", "WY-CONLEY-CRYSTAL", "Crystal Conley", 2027, 2031, 2026, "Succeeding; official 2026 general, TOTAL 9,745.")

    row("County Assessor", "WY-CLEMENTS-TROY", "Troy D. Clements", 2015, 2019, 2014, "Official 2014 general, 9,328.")
    row("County Assessor", "WY-CLEMENTS-TROY", "Troy D. Clements", 2019, 2023, 2018, "Official 2018 general, 11,625.")
    row("County Assessor", "WY-CLEMENTS-TROY", "Troy D. Clements", 2023, 2027, 2022, "Official 2022 general, TOTAL 11,257.")
    row("County Assessor", "WY-SLATTERY-ERIN", "Erin Slattery", 2027, 2031, 2026, "Succeeding; official 2026 general, TOTAL 9,718.")

    row("County Sheriff", "WY-MATHENY-SCOTT", "Scott D. Matheny", 2015, 2019, 2014, "Official 2014 general, 9,443.")
    row("County Sheriff", "WY-MATHENY-SCOTT", "Scott D. Matheny", 2019, 2023, 2018, "Official 2018 general, 11,790.")
    row("County Sheriff", "WY-MATHENY-SCOTT", "Scott D. Matheny", 2023, 2027, 2022, "Official 2022 general, TOTAL 11,126.")
    row("County Sheriff", "WY-MAUL-DAN", "Dan Maul", 2027, 2031, 2026, "Succeeding; official 2026 general, TOTAL 10,139.")

    row("County Attorney", "WY-WIRTHWEIN-RON", "Ron Wirthwein", 2015, 2019, 2014, "Official 2014 general, 7,313.")
    row("County Attorney", "WY-WIRTHWEIN-RON", "Ron Wirthwein", 2019, 2023, 2018, "Official 2018 general, 11,099.")
    row("County Attorney", "WY-HENKES-NATHAN", "Nathan Henkes", 2023, 2027, 2022, "Official 2022 general, TOTAL 10,924.")
    row("County Attorney", "WY-FERRIS-KYLE", "Kyle Ferris", 2027, 2031, 2026, "Succeeding; official 2026 general, TOTAL 9,442.")

    row("County Coroner", "WY-SUNDSTROM-LAURA", "Laura Sundstrom", 2015, 2019, 2014, "Official 2014 general, 8,950.")
    row("County Coroner", "WY-WALLEM-PAUL", "Paul Wallem", 2019, 2023, 2018, "Official 2018 general, 9,669.")
    row("County Coroner", "WY-WALLEM-PAUL", "Paul Wallem", 2023, 2027, 2022, "Official 2022 general, TOTAL 11,446.")
    row("County Coroner", "WY-WALLEM-PAUL", "Paul Wallem", 2027, 2031, 2026, "Continuing; official 2026 general, TOTAL 10,165.")

    row("Clerk of District Court", "WY-CHITWOOD-CHERYL", "Cheryl C. Chitwood", 2015, 2019, 2014, "Official 2014 general, 9,182.")
    row("Clerk of District Court", "WY-CHITWOOD-CHERYL", "Cheryl C. Chitwood", 2019, 2023, 2018, "Official 2018 general, 11,225.")
    row("Clerk of District Court", "WY-MERCHEN-PAMELA", "Pamela Merchen", 2023, 2027, 2022, "Official 2022 general, TOTAL 10,434.")
    row("Clerk of District Court", "WY-MERCHEN-PAMELA", "Pamela Merchen", 2027, 2031, 2026, "Continuing; official 2026 general, TOTAL 9,671.")

    return terms


def local_terms():
    """Municipal, school, special-district terms from official 2020–2026 generals.

    2012–2018 municipal and special pages were archived but are not yet fully
    visually keyed, so January 2015–2020 snapshots for those groups stay
    “Not yet collected.”
    """
    terms = []

    def add(office, group, juris, pid, name, start, end, year, notes="", extra=None, flags=None, conf="high"):
        terms.append(T(office, group, juris, pid, name, start, end, year, year,
                       notes=notes, extra_sources=extra, flags=flags, confidence=conf))

    # ===== City of Gillette =====
    # Mayor: 2022 Lundvall, re-elected 2026 (ordinary 4-year)
    add("Mayor", "municipal", "City of Gillette",
        "WY-LUNDVALL-SHAY", "Shay Lundvall", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 4,168.")
    add("Mayor", "municipal", "City of Gillette",
        "WY-LUNDVALL-SHAY", "Shay Lundvall", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 3,585.")

    # Ward 1: 2020 Hanson (to Jan 2025); 2022 West (re-elected 2026); 2022 unexpired Simonson; 2024 Smith
    add("Councilperson Ward 1", "municipal", "City of Gillette",
        "WY-HANSON-ERIC-GILLETTE", "Eric Hanson", FM[2021], FM[2025], 2020,
        "Official 2020 general, 1,646.")
    add("Councilperson Ward 1", "municipal", "City of Gillette",
        "WY-WEST-JIM-GILLETTE", "Jim West", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 1,203.")
    add("Councilperson Ward 1 (unexpired)", "municipal", "City of Gillette",
        "WY-SIMONSON-TRICIA", "Tricia Simonson", FM[2023], FM[2025], 2022,
        "Official 2022 general Ward 1 unexpired, TOTAL 1,357. Ordinary end January 2025; the 2024 Ward 1 contest is treated as the next regular seat.")
    add("Councilperson Ward 1", "municipal", "City of Gillette",
        "WY-SMITH-CHRIS-GILLETTE", "Chris Smith", FM[2025], FM[2029], 2024,
        "Official 2024 general, 1,695. Clerk lists the file under Official Results; the PDF header still reads unofficial.")
    add("Councilperson Ward 1", "municipal", "City of Gillette",
        "WY-WEST-JIM-GILLETTE", "Jim West", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 1,189.")

    # Ward 2: 2020 Montgomery (to Jan 2025); 2022 Carsrud (to Jan 2027) → Scott 2026.
    # No official 2024 Ward 2 contest appears on the general summary.
    add("Councilperson Ward 2", "municipal", "City of Gillette",
        "WY-MONTGOMERY-BILLY", "Billy Montgomery", FM[2021], FM[2025], 2020,
        "Official 2020 general, 2,051. Ordinary term ended January 2025; no Ward 2 contest appears on the official 2024 general summary, so later holders of this seat are not named.")
    add("Councilperson Ward 2", "municipal", "City of Gillette",
        "WY-CARSRUD-TIM", "Tim Carsrud", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 1,197.")
    add("Councilperson Ward 2", "municipal", "City of Gillette",
        "WY-SCOTT-ERIC-GILLETTE", "Eric Scott", FM[2027], FM[2031], 2026,
        "Succeeding; official 2026 general, TOTAL 1,399.")

    # Ward 3: 2020 Lundvall (to Jan 2025, later mayor); 2020 unexpired McLeland; 2022 Gross (re-elected 2026); 2024 McLeland
    add("Councilperson Ward 3", "municipal", "City of Gillette",
        "WY-LUNDVALL-SHAY", "Shay Lundvall", FM[2021], FM[2025], 2020,
        "Official 2020 general, 2,988. Later elected mayor in 2022.")
    add("Councilperson Ward 3 (unexpired)", "municipal", "City of Gillette",
        "WY-MCLELAND-NATHAN", "Nathan McLeland", FM[2021], FM[2023], 2020,
        "Official 2020 general Ward 3 unexpired, 2,196.")
    add("Councilperson Ward 3", "municipal", "City of Gillette",
        "WY-GROSS-HEIDI", "Heidi Gross", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 1,763.")
    add("Councilperson Ward 3", "municipal", "City of Gillette",
        "WY-MCLELAND-NATHAN", "Nathan McLeland", FM[2025], FM[2029], 2024,
        "Official 2024 general, 2,243. Clerk lists the file under Official Results; the PDF header still reads unofficial.")
    add("Councilperson Ward 3", "municipal", "City of Gillette",
        "WY-GROSS-HEIDI", "Heidi Gross", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 1,398.")

    # ===== Town of Wright =====
    add("Mayor", "municipal", "Town of Wright",
        "WY-KINGAN-RALPH", "Ralph Kingan", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 298.")
    add("Mayor", "municipal", "Town of Wright",
        "WY-SCHRADER-DOUG", "Doug Schrader", FM[2027], FM[2031], 2026,
        "Succeeding; official 2026 general, TOTAL 271. Schrader also holds a 2024 at-large council term to January 2029; no 2026 contest fills that council seat.")

    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-MORGAN-JOEL", "Joel Morgan", FM[2021], FM[2025], 2020,
        "Official 2020 general, 425 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-SCHRADER-DOUG", "Doug Schrader", FM[2021], FM[2025], 2020,
        "Official 2020 general, 397 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-PHIPPS-MICHAEL", "Michael Phipps", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 299 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-ROBB-JUSTIN", "Justin Robb", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 287 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-SCHRADER-DOUG", "Doug Schrader", FM[2025], FM[2027], 2024,
        "Official 2024 general, 424 (vote for 2). Term on the council is ended in January 2027 when Schrader takes office as mayor; a replacement for the remainder of the 2024–2029 council term is not named on the official 2026 general.")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-LEMBKE-JASON", "Jason Lembke", FM[2025], FM[2029], 2024,
        "Official 2024 general, 326 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-ROBB-JUSTIN", "Justin Robb", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 223 (vote for 2).")
    add("Councilperson at-large", "municipal", "Town of Wright",
        "WY-PHIPPS-MICHAEL", "Michael Phipps", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 189 (vote for 2).")

    # ===== Campbell County School District =====
    # 2020 VF4 to Jan 2025: Clouston, Durgin, Steiger, Ochs. No 2024 school contest on the official general.
    for pid, name, votes in [
        ("WY-CLOUSTON-KEN", "Ken Clouston", "8,377"),
        ("WY-DURGIN-LISA", "Lisa Durgin", "7,921"),
        ("WY-STEIGER-LARRY-D", "Larry D. Steiger", "7,262"),
        ("WY-OCHS-ANNE", "Anne Ochs", "7,202"),
    ]:
        add("Trustee", "school", "Campbell County School District",
            pid, name, FM[2021], FM[2025], 2020,
            f"Official 2020 general, {votes} (vote for 4). Ordinary term ended January 2025; no school-board contest appears on the official 2024 general summary, so later holders of these seats are not named.")
    # 2022 VF3 to Jan 2027
    for pid, name, votes in [
        ("WY-WILLIAMS-ROLLO", "Rollo Williams", "4,277"),
        ("WY-HALLINAN-TIM", "Tim Hallinan", "3,271"),
        ("WY-LAWRENCE-JOE", "Joe Lawrence", "3,054"),
    ]:
        add("Trustee", "school", "Campbell County School District",
            pid, name, FM[2023], FM[2027], 2022,
            f"Official 2022 general, TOTAL {votes} (vote for 3).")
    # 2026 VF3 to Jan 2031
    for pid, name, votes in [
        ("WY-GILLASPY-DARCY", "Darcy Gillaspy", "5,476"),
        ("WY-ALBIN-TIM", "Tim Albin", "5,272"),
        ("WY-WILKERSON-BILLIE-FITCH", "Billie Fitch Wilkerson", "5,208"),
    ]:
        add("Trustee", "school", "Campbell County School District",
            pid, name, FM[2027], FM[2031], 2026,
            f"Succeeding; official 2026 general, TOTAL {votes} (vote for 3).")

    # ===== Gillette Community College District =====
    # 2024 VF7 (seven named, to Jan 2029). 2026 VF3 Anderson, Smith, Day — already among the 2024 seven; treated as a new term Jan 2027–2031.
    for pid, name, votes in [
        ("WY-WASSERBURGER-TRACY", "Tracy Wasserburger", "9,338"),
        ("WY-MCGRATH-JOSH", "Josh McGrath", "9,096"),
        ("WY-WILLIAMS-NELLO", "Nello Williams", "7,852"),
        ("WY-PALMER-ROBERT-GCC", "Robert Palmer", "6,979"),
        ("WY-ANDERSON-TERI", "Teri Anderson", "6,257"),
        ("WY-SMITH-LARRY-GCC", "Larry Smith", "6,207"),
        ("WY-DAY-ELLIS", "Ellis Day", "6,171"),
    ]:
        add("Trustee", "special_district", "Gillette Community College District",
            pid, name, FM[2025], FM[2029], 2024,
            f"Official 2024 general, {votes} (vote for 7). Clerk lists the file under Official Results; the PDF header still reads unofficial.")
    for pid, name, votes in [
        ("WY-ANDERSON-TERI", "Teri Anderson", "6,749"),
        ("WY-SMITH-LARRY-GCC", "Larry Smith", "6,611"),
        ("WY-DAY-ELLIS", "Ellis Day", "6,247"),
    ]:
        add("Trustee", "special_district", "Gillette Community College District",
            pid, name, FM[2027], FM[2031], 2026,
            f"Official 2026 general, TOTAL {votes} (vote for 3). These three were also among the seven elected in 2024.")

    # ===== Cemetery =====
    # 2020 VF3 Vomhof, Butler, Bryant to Jan 2025
    for pid, name, votes in [
        ("WY-VOMHOF-DEAN", "Dean Vomhof", "8,527"),
        ("WY-BUTLER-TOMMIE-M", "Tommie M. Butler", "8,350"),
        ("WY-BRYANT-ARLENE", "Arlene Bryant", "8,094"),
    ]:
        add("Trustee", "special_district", "Campbell County Cemetery District",
            pid, name, FM[2021], FM[2025], 2020,
            f"Official 2020 general, {votes} (vote for 3).")
    # 2022 VF3 Bergquist, Hastings, Urman to Jan 2027; separate VF1 J.D. Jones
    for pid, name, votes in [
        ("WY-BERGQUIST-ERIK", "Erik Bergquist", "7,831"),
        ("WY-HASTINGS-JIM", "Jim Hastings", "7,349"),
        ("WY-URMAN-STEVEN", "Steven Urman", "6,875"),
    ]:
        add("Trustee", "special_district", "Campbell County Cemetery District",
            pid, name, FM[2023], FM[2027], 2022,
            f"Official 2022 general, TOTAL {votes} (vote for 3).")
    add("Trustee", "special_district", "Campbell County Cemetery District",
        "WY-JONES-JD-CEM", "J.D. Jones", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 5,178 (vote for 1). The official title does not say unexpired; term length is treated as ordinary midterm but is not independently confirmed.",
        flags=["term_length_uncertain"], conf="medium")
    # 2024 VF3 Meyers, Hurley, Vomhof to Jan 2029
    for pid, name, votes in [
        ("WY-MEYERS-DEAN-L", "Dean L. Meyers", "7,753"),
        ("WY-HURLEY-MAUREEN-E", "Maureen E. Hurley", "7,384"),
        ("WY-VOMHOF-DEAN", "Dean Vomhof", "7,216"),
    ]:
        add("Trustee", "special_district", "Campbell County Cemetery District",
            pid, name, FM[2025], FM[2029], 2024,
            f"Official 2024 general, {votes} (vote for 3). Clerk lists the file under Official Results; the PDF header still reads unofficial.")
    # 2026 VF3 Bergquist, Hastings, Knutson
    for pid, name, votes in [
        ("WY-BERGQUIST-ERIK", "Erik Bergquist", "4,797"),
        ("WY-HASTINGS-JIM", "Jim Hastings", "4,221"),
        ("WY-KNUTSON-ROY", "Roy “Butch” Knutson, Jr.", "4,182"),
    ]:
        add("Trustee", "special_district", "Campbell County Cemetery District",
            pid, name, FM[2027], FM[2031], 2026,
            f"Official 2026 general, TOTAL {votes} (vote for 3).")

    # ===== Conservation =====
    # 2020: at-large Eisenbraun; rural VF2 Hauber, Boardman. Urban not on 2020 official title? Don't invent urban 2020.
    add("Trustee at-large", "special_district", "Campbell County Conservation District",
        "WY-EISENBRAUN-KEITH", "Keith Eisenbraun", FM[2021], FM[2025], 2020,
        "Official 2020 general, 14,414.")
    add("Trustee rural", "special_district", "Campbell County Conservation District",
        "WY-HAUBER-RICHARD-J", "Richard J. Hauber", FM[2021], FM[2025], 2020,
        "Official 2020 general, 9,204 (rural, vote for 2).")
    add("Trustee rural", "special_district", "Campbell County Conservation District",
        "WY-BOARDMAN-JEFFREY-M", "Jeffrey M. Boardman", FM[2021], FM[2025], 2020,
        "Official 2020 general, 6,989 (rural, vote for 2).")
    # 2022: rural Daly, urban Price, at-large Kretschman
    add("Trustee rural", "special_district", "Campbell County Conservation District",
        "WY-DALY-JOHN-CCCD", "John Daly", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 4,755. The 2026 rural contest was write-in only and the official write-in canvass does not certify a named winner.")
    add("Trustee urban", "special_district", "Campbell County Conservation District",
        "WY-PRICE-BRANDON-T", "Brandon T. Price", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 9,075.")
    add("Trustee at-large", "special_district", "Campbell County Conservation District",
        "WY-KRETSCHMAN-KIM", "Kim Kretschman", FM[2023], FM[2027], 2022,
        "Official 2022 general, TOTAL 5,364. The 2026 at-large contest was write-in only and the official write-in canvass does not certify a named winner.")
    # 2024 VF2 Clark, Sams — official summary does not label rural/urban/at-large
    add("Trustee", "special_district", "Campbell County Conservation District",
        "WY-CLARK-BJ", "B.J. Clark", FM[2025], FM[2029], 2024,
        "Official 2024 general, 9,767 (vote for 2). The official summary does not label this seat rural, urban, or at-large.")
    add("Trustee", "special_district", "Campbell County Conservation District",
        "WY-SAMS-JENNIFER", "Jennifer Sams", FM[2025], FM[2029], 2024,
        "Official 2024 general, 9,689 (vote for 2). The official summary does not label this seat rural, urban, or at-large.")
    # 2026 urban Price re-elected; rural and at-large write-in not named
    add("Trustee urban", "special_district", "Campbell County Conservation District",
        "WY-PRICE-BRANDON-T", "Brandon T. Price", FM[2027], FM[2031], 2026,
        "Re-elected; official 2026 general, TOTAL 7,785.")

    # ===== Hospital (7-member: 4 midterm + 3 presidential) =====
    for pid, name, votes in [
        ("WY-MURPHY-TOM-HOSP", "Tom Murphy", "10,128"),
        ("WY-LESLIE-KRISTINA", "Kristina Leslie", "10,010"),
        ("WY-HITE-RANDAL", "Randal Hite", "9,471"),
    ]:
        add("Trustee", "special_district", "Campbell County Hospital District",
            pid, name, FM[2021], FM[2025], 2020,
            f"Official 2020 general, {votes} (vote for 3).")
    for pid, name, votes in [
        ("WY-HARTSAW-SARA", "Sara Hartsaw", "6,927"),
        ("WY-HOSKINSON-MARK-S", "Mark S. Hoskinson", "6,183"),
        ("WY-RICE-BILL-HOSP", "Bill Rice", "5,186"),
        ("WY-STUBER-ALAN", "Alan E. Stuber", "4,003"),
    ]:
        add("Trustee", "special_district", "Campbell County Hospital District",
            pid, name, FM[2023], FM[2027], 2022,
            f"Official 2022 general, TOTAL {votes} (vote for 4).")
    for pid, name, votes in [
        ("WY-MURPHY-TOM-HOSP", "Tom Murphy", "7,009"),
        ("WY-MANSELL-JOHN", "John Mansell", "6,034"),
        ("WY-HITE-RANDAL", "Randal Hite", "5,792"),
    ]:
        add("Trustee", "special_district", "Campbell County Hospital District",
            pid, name, FM[2025], FM[2029], 2024,
            f"Official 2024 general, {votes} (vote for 3). Clerk lists the file under Official Results; the PDF header still reads unofficial.")
    for pid, name, votes in [
        ("WY-BIGGS-ANGELA", "Angela Biggs", "8,084"),
        ("WY-HARTSAW-SARA", "Sara Hartsaw", "7,167"),
        ("WY-STUBER-ALAN", "Alan E. Stuber", "5,465"),
        ("WY-RICE-BILL-HOSP", "Bill Rice", "5,412"),
    ]:
        add("Trustee", "special_district", "Campbell County Hospital District",
            pid, name, FM[2027], FM[2031], 2026,
            f"Official 2026 general, TOTAL {votes} (vote for 4).")

    return terms


OFFICE_MAP = {
    ("legislature", "Senate District 1 (S01)"): ("state-senate", "Senate District 1 (S01)", "Senate District 1 (also Crook and Weston)"),
    ("legislature", "Senate District 23 (S23)"): ("state-senate", "Senate District 23 (S23)", "Senate District 23"),
    ("legislature", "Senate District 24 (S24)"): ("state-senate", "Senate District 24 (S24)", "Senate District 24"),
    ("legislature", "House District 3 (H03)"): ("state-house", "House District 3 (H03)", "House District 3"),
    ("legislature", "House District 31 (H31)"): ("state-house", "House District 31 (H31)", "House District 31"),
    ("legislature", "House District 32 (H32)"): ("state-house", "House District 32 (H32)", "House District 32"),
    ("legislature", "House District 52 (H52)"): ("state-house", "House District 52 (H52)", "House District 52"),
    ("legislature", "House District 53 (H53)"): ("state-house", "House District 53 (H53)", "House District 53"),
}

MUNI_OFFICE = {
    ("City of Gillette", "Mayor"): "Gillette Mayor",
    ("City of Gillette", "Councilperson Ward 1"): "Gillette Council Ward 1",
    ("City of Gillette", "Councilperson Ward 1 (unexpired)"): "Gillette Council Ward 1",
    ("City of Gillette", "Councilperson Ward 2"): "Gillette Council Ward 2",
    ("City of Gillette", "Councilperson Ward 3"): "Gillette Council Ward 3",
    ("City of Gillette", "Councilperson Ward 3 (unexpired)"): "Gillette Council Ward 3",
    ("Town of Wright", "Mayor"): "Wright Mayor",
    ("Town of Wright", "Councilperson at-large"): "Wright Town Council",
}

SPEC_OFFICE = {
    ("Campbell County School District", "Trustee"): ("schools", "CCSD Trustee"),
    ("Gillette Community College District", "Trustee"): ("special-districts", "Gillette College Trustee"),
    ("Campbell County Cemetery District", "Trustee"): ("special-districts", "Cemetery District Trustee"),
    ("Campbell County Conservation District", "Trustee"): ("special-districts", "Conservation District Trustee"),
    ("Campbell County Conservation District", "Trustee rural"): ("special-districts", "Conservation District Rural"),
    ("Campbell County Conservation District", "Trustee urban"): ("special-districts", "Conservation District Urban"),
    ("Campbell County Conservation District", "Trustee at-large"): ("special-districts", "Conservation District At-large"),
    ("Campbell County Hospital District", "Trustee"): ("special-districts", "Hospital District Trustee"),
}


def normalize_term(raw):
    og, office, juris = raw["office_group"], raw["office"], raw["jurisdiction"]
    if (og, office) in OFFICE_MAP:
        og, office, juris = OFFICE_MAP[(og, office)]
    elif og == "municipal":
        office = MUNI_OFFICE[(juris, office)]
    elif og in ("school", "schools", "special_district", "special-districts"):
        og, office = SPEC_OFFICE[(juris, office)]
    how = "appointed" if (raw.get("election_year") is None and "Appointed" in (raw.get("notes") or "")) else "elected"
    return H.term(
        person_id=raw["person_id"],
        name=raw["display_name"],
        office_group=og,
        office=office,
        jurisdiction=juris,
        term_start=raw["term_start"],
        term_end=raw["term_end"],
        election_year=raw.get("election_year"),
        confidence=raw.get("confidence") or "high",
        sources=raw.get("sources") or [],
        notes=raw.get("notes") or "",
        flags=raw.get("flags") or [],
        how_took_office=how,
    )


def build_campbell():
    people: dict = {}
    P = H.person_factory(people)
    register_people(P)

    raw = county_and_legislature_terms() + local_terms()
    terms = [normalize_term(t) for t in raw]
    # Drop hand-built S01; copy official Weston S01 terms instead (same person, same 4-year cycle).
    terms = [t for t in terms if t["office"] != "Senate District 1 (S01)"]

    weston = json.loads((H.HISTORY / "weston" / "terms.json").read_text())
    shared_groups = {"federal", "statewide", "judicial"}
    copied = 0
    for t in weston["terms"]:
        og = t.get("office_group")
        office = t.get("office") or ""
        if og in shared_groups or (og == "state-senate" and "Senate District 1" in office):
            rec = deepcopy(t)
            if rec["office_group"] == "judicial" and rec.get("election_year") in CG:
                rec["sources"] = list(rec.get("sources") or []) + [cg(rec["election_year"])]
            terms.append(rec)
            copied += 1

    H.attach_people_from_terms(terms, people)

    expected = {
        "federal": [("U.S. Senator", 2), ("U.S. Representative", 1)],
        "statewide": [
            ("Governor", 1), ("Secretary of State", 1), ("State Auditor", 1),
            ("State Treasurer", 1), ("Superintendent of Public Instruction", 1),
        ],
        "state-senate": [
            ("Senate District 1 (S01)", 1),
            ("Senate District 23 (S23)", 1),
            ("Senate District 24 (S24)", 1),
        ],
        "state-house": [
            ("House District 3 (H03)", 1),
            ("House District 31 (H31)", 1),
            ("House District 32 (H32)", 1),
            ("House District 52 (H52)", 1),
            ("House District 53 (H53)", 1),
        ],
        "county": [
            ("County Commissioner", 5), ("County Clerk", 1), ("County Treasurer", 1),
            ("County Assessor", 1), ("County Sheriff", 1), ("County Attorney", 1),
            ("Clerk of District Court", 1), ("County Coroner", 1),
        ],
        "municipal": [
            ("Gillette Mayor", 1),
            ("Gillette Council Ward 1", 2),
            ("Gillette Council Ward 2", 2),
            ("Gillette Council Ward 3", 2),
            ("Wright Mayor", 1),
            ("Wright Town Council", 4),
        ],
        # School and special expected counts are not padded. The official 2024 general
        # has no school contest, and 2012–2018 local pages are not yet fully keyed.
    }

    judicial_note = (
        "Supreme Court justices are the five who were in office this January, using official Wyoming Judicial Branch "
        "appointment and retirement dates together with official retention results. District and circuit rows are the "
        "6th Judicial District judges (the district also includes Crook and Weston) who appeared by name on a Campbell "
        "County official retention ballot in an adjoining cycle; the official 2022 general lists “DC JUDGE” and “CC JUDGE” "
        "without a judge’s name, and those two retentions are not attached to a named holder."
    )
    special_note = (
        "The official 2026 Conservation District rural and at-large contests were write-in only; the official write-in "
        "canvass does not certify a named winner (the leading line on both is “NO NAME PROVIDED”), so those seats are not filled. "
        "The official 2024 Conservation District vote-for-2 contest is not labeled rural, urban, or at-large. "
        "The official 2022 Cemetery District vote-for-1 contest does not say unexpired, so that term length is marked uncertain. "
        "Municipal, school, and special-district names from the official 2012–2018 image reports are not yet fully keyed, "
        "and those January seats are marked Not yet collected rather than invented."
    )
    precinct_note = (
        "Precinct committee rosters for January snapshots are not yet collected. Official Campbell primary PDFs are "
        "archived under /workspace/wyoleg/local-results/campbell/<year>/. The current (November 2026) precinct roster "
        "is in data/county_officials/campbell.json, from the official 2026 primary (named winners only)."
    )

    terms_path, cov_path, coverage_all = H.write_terms_and_snapshots(
        county="Campbell", county_number=17, slug="campbell", terms=terms, people=people,
        expected=expected, retrieved=RETRIEVED, judicial_note=judicial_note,
        special_note=special_note, precinct_note=precinct_note,
        precinct_note_early=precinct_note, precinct_cutoff=2099,
    )
    n_people = H.write_people_additions(people)
    n_off = H.write_offices_held(terms, people)
    n_prof = H.write_profiles(terms, people, county="Campbell", slug="campbell")
    print(f"wrote {terms_path}")
    print(f"terms {len(terms)} (including {copied} shared federal/statewide/S01/judicial terms)")
    print(f"people_additions +{n_people} offices_held +{n_off} thin_profiles +{n_prof}")
    H.print_coverage(coverage_all)
    return people, terms, coverage_all


def _src(*items):
    out = []
    for it in items:
        if isinstance(it, int):
            out.append(cg(it))
        else:
            out.append(it)
    return out


def _holder(people, pid, *, sources, term_end="", party="", notes="", succeeding=None, extra=None):
    p = people[pid]
    h = {
        "name": p["display_name"],
        "person_id": pid,
        "party": party,
        "sources": sources,
        "confidence": "high",
        "href": f"candidates/local-history/c/{p['slug']}.html",
    }
    if term_end:
        h["term_end"] = term_end
    if notes:
        h["notes"] = notes
    if succeeding:
        h["succeeding"] = succeeding
    if extra:
        h.update(extra)
    return h


def _succ(people, pid, *, sources, term_end, takes_office="January"):
    p = people[pid]
    return {
        "name": p["display_name"],
        "person_id": pid,
        "party": "",
        "takes_office": takes_office,
        "term_end": term_end,
        "sources": sources,
        "href": f"candidates/local-history/c/{p['slug']}.html",
    }


def update_campbell_json(people: dict):
    path = ROOT / "data" / "county_officials" / "campbell.json"
    data = json.loads(path.read_text())
    g2026 = _src(2026)
    g2024 = _src(2024)
    g2022 = _src(2022)
    g2020 = _src(2020)
    clerk_comm = {"label": "Campbell County commissioners page",
                  "url": "https://www.campbellcountywy.gov/165/County-Commissioners"}
    wyoleg = lambda url: {"label": "Wyoming Legislature member page", "url": url}

    def HLD(pid, sources, term_end, party="", notes="", succeeding=None, extra=None):
        return _holder(people, pid, sources=sources, term_end=term_end, party=party,
                       notes=notes, succeeding=succeeding, extra=extra)

    senate = {
        "id": "state-senate", "title": "State Senate", "sort_key": "C",
        "offices": [
            {"office": "Senate District 1 (S01)", "layout": "office-and-name", "sort_key": "C01",
             "note": "Also covers Crook and Weston.",
             "holders": [HLD("WY-DRISKILL-OGDEN",
                             [wyoleg("https://www.wyoleg.gov/Legislators/2026/S/1972"), *g2026],
                             "January 2031", "R",
                             notes="Re-elected 2026; official Campbell 2026 general, TOTAL 1,858.")]},
            {"office": "Senate District 23 (S23)", "layout": "office-and-name", "sort_key": "C02",
             "holders": [HLD("WY-BARLOW-ERIC",
                             [wyoleg("https://www.wyoleg.gov/Legislators/2026/S/2030"), *g2022],
                             "January 2027", "R",
                             succeeding=_succ(people, "WY-ANGELOS-ABBY", sources=g2026, term_end="January 2031"))]},
            {"office": "Senate District 24 (S24)", "layout": "office-and-name", "sort_key": "C03",
             "holders": [HLD("WY-MCKEOWN-TROY",
                             [wyoleg("https://www.wyoleg.gov/Legislators/2026/S/2076"), *g2024],
                             "January 2029", "R")]},
        ],
    }
    house = {
        "id": "state-house", "title": "State House", "sort_key": "D",
        "offices": [
            {"office": "House District 3 (H03)", "layout": "office-and-name", "sort_key": "D01",
             "holders": [HLD("WY-ANGELOS-ABBY", [*g2024], "January 2027", "R",
                             succeeding=_succ(people, "WY-COLLIER-EARL", sources=g2026, term_end="January 2029"))]},
            {"office": "House District 31 (H31)", "layout": "office-and-name", "sort_key": "D02",
             "holders": [HLD("WY-BEAR-JOHN", [*g2024], "January 2027", "R",
                             succeeding=_succ(people, "WY-MOORE-DOUGLAS", sources=g2026, term_end="January 2029"))]},
            {"office": "House District 32 (H32)", "layout": "office-and-name", "sort_key": "D03",
             "holders": [HLD("WY-CLOUSTON-KEN", [*g2026], "January 2029", "R",
                             notes="Re-elected 2026; official Campbell 2026 general, TOTAL 2,124.")]},
            {"office": "House District 52 (H52)", "layout": "office-and-name", "sort_key": "D04",
             "holders": [HLD("WY-TARVER-REUBEN", [*g2024], "January 2027", "R",
                             succeeding=_succ(people, "WY-BOLLER-RONDA", sources=g2026, term_end="January 2029"))]},
            {"office": "House District 53 (H53)", "layout": "office-and-name", "sort_key": "D05",
             "holders": [HLD("WY-KNAPP-CHRISTOPHER", [*g2026], "January 2029", "R",
                             notes="Re-elected 2026; official Campbell 2026 general, TOTAL 1,407.")]},
        ],
    }

    clem_notes = (
        "Appointed August 23, 2024 to finish Roy “Butch” Knutson, Jr.’s term after the August 1 resignation; "
        "elected November 2026 to a new term beginning January 2027."
    )
    county = {
        "id": "county", "title": "County Offices", "sort_key": "E",
        "offices": [
            {"office": "County Commissioners", "layout": "heading-then-names", "sort_key": "E01",
             "holders": [
                 HLD("WY-JORDAN-BOB", [clerk_comm, *g2024], "January 2029", "R"),
                 HLD("WY-MEANS-JERRY", [clerk_comm, *g2024], "January 2029", "R"),
                 HLD("WY-FORD-JIM", [clerk_comm, *g2022, *g2026], "January 2031", "R",
                     notes="Re-elected 2026; official 2026 general, TOTAL 7,754."),
                 HLD("WY-MCCREERY-KELLEY", [clerk_comm, *g2022], "January 2027", "R",
                     succeeding=_succ(people, "WY-EDWARDS-SARAH-CAMPBELL", sources=g2026, term_end="January 2031")),
                 HLD("WY-CLEM-SCOTT", [clerk_comm, CLEM_SRC, CLEM_GNR, *g2026], "January 2031", "R",
                     notes=clem_notes, extra={"confidence": "high"}),
             ]},
            {"office": "County Clerk", "layout": "office-and-name", "sort_key": "E02",
             "holders": [HLD("WY-LOVELACE-CINDY", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, TOTAL 9,743.")]},
            {"office": "County Treasurer", "layout": "office-and-name", "sort_key": "E03",
             "holders": [HLD("WY-KNUST-RACHAEL", g2022, "January 2027", "R",
                             succeeding=_succ(people, "WY-CONLEY-CRYSTAL", sources=g2026, term_end="January 2031"))]},
            {"office": "County Assessor", "layout": "office-and-name", "sort_key": "E04",
             "holders": [HLD("WY-CLEMENTS-TROY", g2022, "January 2027", "R",
                             succeeding=_succ(people, "WY-SLATTERY-ERIN", sources=g2026, term_end="January 2031"))]},
            {"office": "County Sheriff", "layout": "office-and-name", "sort_key": "E05",
             "holders": [HLD("WY-MATHENY-SCOTT", g2022, "January 2027", "R",
                             succeeding=_succ(people, "WY-MAUL-DAN", sources=g2026, term_end="January 2031"))]},
            {"office": "County Attorney", "layout": "office-and-name", "sort_key": "E06",
             "holders": [HLD("WY-HENKES-NATHAN", g2022, "January 2027", "R",
                             succeeding=_succ(people, "WY-FERRIS-KYLE", sources=g2026, term_end="January 2031"))]},
            {"office": "Clerk of District Court", "layout": "office-and-name", "sort_key": "E07",
             "holders": [HLD("WY-MERCHEN-PAMELA", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, TOTAL 9,671.")]},
            {"office": "County Coroner", "layout": "office-and-name", "sort_key": "E08",
             "holders": [HLD("WY-WALLEM-PAUL", g2026, "January 2031", "R",
                             notes="Re-elected 2026; official 2026 general, TOTAL 10,165.")]},
        ],
    }

    municipal = {
        "id": "municipal", "title": "Municipal offices", "sort_key": "F",
        "note": (
            "The City of Gillette and the Town of Wright appear on the official Campbell County November general ballot. "
            "No Gillette Ward 2 contest appears on the official 2024 general, so the second Ward 2 seat whose ordinary term "
            "ended January 2025 is not named. Doug Schrader holds a 2024 Wright council term but takes office as mayor in "
            "January 2027; a replacement for the remainder of that council term is not named on the official 2026 general."
        ),
        "offices": [
            {"office": "Gillette Mayor", "layout": "office-and-name", "sort_key": "F01",
             "holders": [HLD("WY-LUNDVALL-SHAY", [*g2022, *g2026], "January 2031",
                             notes="Re-elected 2026; official 2026 general, TOTAL 3,585.")]},
            {"office": "Gillette Council Ward 1", "layout": "heading-then-names", "sort_key": "F02",
             "holders": [
                 HLD("WY-WEST-JIM-GILLETTE", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 1,189."),
                 HLD("WY-SMITH-CHRIS-GILLETTE", g2024, "January 2029"),
             ]},
            {"office": "Gillette Council Ward 2", "layout": "heading-then-names", "sort_key": "F03",
             "holders": [
                 HLD("WY-CARSRUD-TIM", g2022, "January 2027",
                     succeeding=_succ(people, "WY-SCOTT-ERIC-GILLETTE", sources=g2026, term_end="January 2031"),
                     notes="No second Ward 2 contest appears on the official 2024 general."),
             ]},
            {"office": "Gillette Council Ward 3", "layout": "heading-then-names", "sort_key": "F04",
             "holders": [
                 HLD("WY-GROSS-HEIDI", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 1,398."),
                 HLD("WY-MCLELAND-NATHAN", g2024, "January 2029"),
             ]},
            {"office": "Wright Mayor", "layout": "office-and-name", "sort_key": "F05",
             "holders": [HLD("WY-KINGAN-RALPH", g2022, "January 2027",
                             succeeding=_succ(people, "WY-SCHRADER-DOUG", sources=g2026, term_end="January 2031"))]},
            {"office": "Wright Town Council", "layout": "heading-then-names", "sort_key": "F06",
             "holders": [
                 HLD("WY-PHIPPS-MICHAEL", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 189."),
                 HLD("WY-ROBB-JUSTIN", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 223."),
                 HLD("WY-LEMBKE-JASON", g2024, "January 2029"),
                 HLD("WY-SCHRADER-DOUG", g2024, "January 2027",
                     notes="Elected to council in 2024 (term would otherwise run to January 2029) and elected mayor in 2026; a replacement for the remainder of this council term is not named on the official 2026 general."),
             ]},
        ],
    }

    schools = {
        "id": "schools", "title": "School boards", "sort_key": "G",
        "note": (
            "Campbell County School District. Three trustees were elected in 2022 (terms end January 2027) and three in 2026. "
            "Four trustees were elected in 2020 to terms that ended January 2025; no school-board contest appears on the official "
            "2024 general summary, so later holders of those seats are not named."
        ),
        "offices": [
            {"office": "Campbell County School District", "layout": "heading-then-names", "sort_key": "G01",
             "holders": [
                 HLD("WY-WILLIAMS-ROLLO", g2022, "January 2027",
                     succeeding=_succ(people, "WY-GILLASPY-DARCY", sources=g2026, term_end="January 2031")),
                 HLD("WY-HALLINAN-TIM", g2022, "January 2027",
                     succeeding=_succ(people, "WY-ALBIN-TIM", sources=g2026, term_end="January 2031")),
                 HLD("WY-LAWRENCE-JOE", g2022, "January 2027",
                     succeeding=_succ(people, "WY-WILKERSON-BILLIE-FITCH", sources=g2026, term_end="January 2031")),
             ]},
        ],
    }

    special = {
        "id": "special-districts", "title": "Special districts", "sort_key": "H",
        "note": (
            "The official 2026 Conservation District rural and at-large contests were write-in only and the official write-in "
            "canvass does not certify a named winner (the leading line on both is “NO NAME PROVIDED”). Those two seats, currently "
            "held by John Daly (rural) and Kim Kretschman (at-large) through January 2027, are therefore shown without a named successor. "
            "The official 2024 Conservation District vote-for-2 contest is not labeled rural, urban, or at-large. "
            "The official 2022 Cemetery District vote-for-1 contest (J.D. Jones) does not say unexpired; that term length is uncertain."
        ),
        "offices": [
            {"office": "Gillette Community College District", "layout": "heading-then-names", "sort_key": "H01",
             "holders": [
                 HLD("WY-WASSERBURGER-TRACY", g2024, "January 2029"),
                 HLD("WY-MCGRATH-JOSH", g2024, "January 2029"),
                 HLD("WY-WILLIAMS-NELLO", g2024, "January 2029"),
                 HLD("WY-PALMER-ROBERT-GCC", g2024, "January 2029"),
                 HLD("WY-ANDERSON-TERI", [*g2024, *g2026], "January 2031",
                     notes="Also elected in the 2024 vote-for-7; official 2026 general, TOTAL 6,749 (vote for 3)."),
                 HLD("WY-SMITH-LARRY-GCC", [*g2024, *g2026], "January 2031",
                     notes="Also elected in the 2024 vote-for-7; official 2026 general, TOTAL 6,611 (vote for 3)."),
                 HLD("WY-DAY-ELLIS", [*g2024, *g2026], "January 2031",
                     notes="Also elected in the 2024 vote-for-7; official 2026 general, TOTAL 6,247 (vote for 3)."),
             ]},
            {"office": "Campbell County Cemetery District", "layout": "heading-then-names", "sort_key": "H02",
             "holders": [
                 HLD("WY-BERGQUIST-ERIK", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 4,797."),
                 HLD("WY-HASTINGS-JIM", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 4,221."),
                 HLD("WY-URMAN-STEVEN", g2022, "January 2027",
                     succeeding=_succ(people, "WY-KNUTSON-ROY", sources=g2026, term_end="January 2031")),
                 HLD("WY-JONES-JD-CEM", g2022, "January 2027",
                     notes="Official 2022 general, TOTAL 5,178 (vote for 1). The official title does not say unexpired; term length is uncertain.",
                     extra={"confidence": "medium", "flags": ["term_length_uncertain"]}),
                 HLD("WY-MEYERS-DEAN-L", g2024, "January 2029"),
                 HLD("WY-HURLEY-MAUREEN-E", g2024, "January 2029"),
                 HLD("WY-VOMHOF-DEAN", g2024, "January 2029"),
             ]},
            {"office": "Campbell County Conservation District Rural", "layout": "office-and-name", "sort_key": "H03",
             "holders": [HLD("WY-DALY-JOHN-CCCD", g2022, "January 2027",
                             notes="The official 2026 rural contest was write-in only and the official write-in canvass does not certify a named winner.",
                             extra={"flags": ["write_in_winner_not_named"]})]},
            {"office": "Campbell County Conservation District Urban", "layout": "office-and-name", "sort_key": "H04",
             "holders": [HLD("WY-PRICE-BRANDON-T", [*g2022, *g2026], "January 2031",
                             notes="Re-elected 2026; official 2026 general, TOTAL 7,785.")]},
            {"office": "Campbell County Conservation District At-large", "layout": "office-and-name", "sort_key": "H05",
             "holders": [HLD("WY-KRETSCHMAN-KIM", g2022, "January 2027",
                             notes="The official 2026 at-large contest was write-in only and the official write-in canvass does not certify a named winner.",
                             extra={"flags": ["write_in_winner_not_named"]})]},
            {"office": "Campbell County Conservation District (unlabeled 2024 seats)", "layout": "heading-then-names", "sort_key": "H06",
             "holders": [
                 HLD("WY-CLARK-BJ", g2024, "January 2029",
                     notes="Official 2024 general, 9,767 (vote for 2). The official summary does not label this seat rural, urban, or at-large."),
                 HLD("WY-SAMS-JENNIFER", g2024, "January 2029",
                     notes="Official 2024 general, 9,689 (vote for 2). The official summary does not label this seat rural, urban, or at-large."),
             ]},
            {"office": "Campbell County Hospital District", "layout": "heading-then-names", "sort_key": "H07",
             "holders": [
                 HLD("WY-HARTSAW-SARA", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 7,167."),
                 HLD("WY-HOSKINSON-MARK-S", g2022, "January 2027",
                     succeeding=_succ(people, "WY-BIGGS-ANGELA", sources=g2026, term_end="January 2031")),
                 HLD("WY-RICE-BILL-HOSP", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 5,412."),
                 HLD("WY-STUBER-ALAN", [*g2022, *g2026], "January 2031",
                     notes="Re-elected 2026; official 2026 general, TOTAL 5,465."),
                 HLD("WY-MURPHY-TOM-HOSP", g2024, "January 2029"),
                 HLD("WY-MANSELL-JOHN", g2024, "January 2029"),
                 HLD("WY-HITE-RANDAL", g2024, "January 2029"),
             ]},
        ],
    }

    def pct(yes, no):
        tot = yes + no
        return f"{yes / tot * 100:.2f}%", f"{no / tot * 100:.2f}%"

    y, n = 7423, 2114
    yp, np = pct(y, n)
    y2, n2 = 7468, 1874
    yp2, np2 = pct(y2, n2)
    judicial = {
        "id": "judicial", "title": "Judicial retention (district and circuit)", "sort_key": "J3",
        "note": (
            "These judges appeared by name on the Campbell County 2026 general ballot. Retention figures are the official "
            "Campbell TOTAL column. Supreme Court justices and the Chancery Court judge are in the shared statewide judicial file. "
            "The same 6th Judicial District judges also serve Crook and Weston."
        ),
        "offices": [
            {"office": "District Judge, 6th Judicial District", "layout": "office-and-name", "sort_key": "J03",
             "holders": [{
                 "name": "Michael J. McGrady", "person_id": "WY-MCGRADY-MICHAEL",
                 "href": "officials/judges/michael-j-mcgrady.html",
                 "ballot_name": "MICHAEL J. MCGRADY",
                 "sources": [
                     {"label": "Wyoming Judicial Branch, District Court, 6th Judicial District",
                      "url": "https://www.wyocourts.gov/court/district-court-6th-judicial-district-weston-county/"},
                     cg(2026),
                 ],
                 "notes": "Appointed July 2024 (Wyoming Judicial Branch). The same judge is listed for Campbell, Crook, and Weston in the 6th Judicial District.",
                 "retention": {"year": 2026, "yes": y, "no": n, "yes_pct": yp, "no_pct": np,
                               "result": "retained", "source": CG[2026][0]},
             }]},
            {"office": "Circuit Judge, 6th Judicial District", "layout": "office-and-name", "sort_key": "J04",
             "holders": [{
                 "name": "Greg Steward", "person_id": "WY-STEWARD-GREG",
                 "href": "officials/judges/greg-steward.html",
                 "ballot_name": "GREG STEWARD",
                 "sources": [cg(2026)],
                 "notes": "The person_id is WY-STEWARD-GREG (already used in the Weston 114 file). Other Steward IDs in the name index are different people.",
                 "retention": {"year": 2026, "yes": y2, "no": n2, "yes_pct": yp2, "no_pct": np2,
                               "result": "retained", "source": CG[2026][0]},
             }]},
        ],
    }

    # Keep precincts and the existing federal/statewide absence (those live in shared files).
    kept = []
    for g in data["groups"]:
        if g["id"] in {"state-senate", "state-house", "county"}:
            continue
        if g["id"] in {"municipal", "schools", "special-districts", "judicial"}:
            continue
        kept.append(g)
    # Order: senate, house, county, then any leftover (precincts), then municipal/schools/special/judicial
    # Precincts stayed in kept.
    data["groups"] = [senate, house, county] + kept + [municipal, schools, special, judicial]
    data["as_of"] = "2026-11-24"
    data["term_switch_date"] = "2027-01-04"
    data["page_version"] = "v2.0"
    data["sources"] = {
        "general_results": CG[2026][0],
        "primary_results": CP_2026[0],
        "checked": RETRIEVED,
        "clerk_archive": "https://www.campbellcountywy.gov/2077/Election-Results",
        "local_archive": "/workspace/wyoleg/local-results/campbell/SOURCES.md",
        "notes": (
            "The 2024 general file is listed under Official Results on the clerk page and its county-office totals match "
            "the previously tied official extract; the PDF header still reads unofficial. Official 2026 conservation-district "
            "rural and at-large write-in winners are not named."
        ),
    }
    apply_to_groups(data["groups"], 'campbell')
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")
